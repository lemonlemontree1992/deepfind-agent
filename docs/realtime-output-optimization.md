# DeepFind Agent 实时输出优化方案

## 问题现状

### 当前状态
```
用户输入 → 等待30-60秒 → 一次性显示报告
```

### 问题列表
1. **黑盒等待**: LLM 调用是同步的，用户看不到进度
2. **工具不可见**: 不知道 Agent 在执行什么操作
3. **一次性输出**: 报告生成后一次性显示，用户体验差
4. **思考过程缺失**: DeepSeek R1 的推理能力没利用

---

## 目标状态

```
用户输入
    ↓
[拆解任务] → ✅ 显示任务列表
    ↓
[搜索中...] → 🔍 显示搜索词 + 结果数量
    ↓
[访问网页] → 📋 实时显示正在访问的 URL
    ↓
[分析中...] → 📊 显示处理的网页数量
    ↓
[生成报告] → ✍️ 逐字打印报告内容
    ↓
[完成] → 📄 完整报告 + 下载选项
```

---

## 详细设计

### 1. 后端改造 (`api.py`)

#### 新增 SSE 事件类型

| 事件名 | 触发时机 | 数据结构 |
|--------|----------|----------|
| `tool_start` | 工具开始执行 | `{tool: string, input: string}` |
| `tool_progress` | 工具执行中 | `{message: string, url?: string}` |
| `tool_end` | 工具执行完成 | `{tool: string, output_summary: string}` |
| `llm_chunk` | LLM 输出 token | `{content: string, is_thinking?: bool}` |
| `page_loaded` | 网页加载完成 | `{url: string, title: string, status: string}` |

#### 代码改造点

```python
# 改造点 1: LLM 流式调用
# 改造前
response = await asyncio.to_thread(llm.invoke, messages)

# 改造后
async for chunk in llm.astream(messages):
    # DeepSeek R1 的 reasoning_content
    if hasattr(chunk, 'reasoning_content') and chunk.reasoning_content:
        yield send_event("llm_chunk", {
            "content": chunk.reasoning_content,
            "is_thinking": True
        })
    # 正常内容
    if chunk.content:
        yield send_event("llm_chunk", {
            "content": chunk.content,
            "is_thinking": False
        })
```

```python
# 改造点 2: 搜索进度
yield send_event("tool_start", {
    "tool": "search",
    "input": query
})

for i, search_query in enumerate(search_queries):
    yield send_event("tool_progress", {
        "message": f"正在搜索: {search_query}",
        "progress": f"{i+1}/{len(search_queries)}"
    })
    results = await asyncio.to_thread(tavily_search, search_query)
    
yield send_event("tool_end", {
    "tool": "search",
    "output_summary": f"找到 {len(all_results)} 条结果"
})
```

```python
# 改造点 3: 网页解析进度
yield send_event("tool_start", {
    "tool": "scrape",
    "input": f"解析 {len(urls)} 个网页"
})

for i, url in enumerate(urls):
    yield send_event("tool_progress", {
        "message": f"正在解析网页 {i+1}/{len(urls)}",
        "url": url
    })
    result = await asyncio.to_thread(scrape_url, url)
    yield send_event("page_loaded", {
        "url": url,
        "title": result.get("title", ""),
        "status": "success" if "error" not in result else "error"
    })
```

---

### 2. 前端改造 (`Index.tsx`)

#### 新增消息类型

```typescript
interface ToolCallCard {
  type: 'tool_call';
  tool: string;
  status: 'running' | 'completed' | 'error';
  input?: string;
  output?: string;
  progress?: string;
  urls?: { url: string; status: string; title?: string }[];
}

interface StreamingMessage {
  type: 'streaming';
  content: string;
  isThinking?: boolean;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  parts?: (ToolCallCard | StreamingMessage | { type: 'text'; content: string })[];
}
```

#### 事件处理器

```typescript
// 处理工具开始事件
eventSource.addEventListener('tool_start', (event) => {
  const data = JSON.parse(event.data);
  // 添加工具调用卡片
  addToolCallCard(data.tool, 'running', data.input);
});

// 处理工具进度事件
eventSource.addEventListener('tool_progress', (event) => {
  const data = JSON.parse(event.data);
  // 更新工具卡片状态
  updateToolCallProgress(data.message, data.url);
});

// 处理 LLM 流式输出
eventSource.addEventListener('llm_chunk', (event) => {
  const data = JSON.parse(event.data);
  if (data.is_thinking) {
    // 添加到思考区域
    appendThinkingContent(data.content);
  } else {
    // 添加到答案区域
    appendStreamContent(data.content);
  }
});
```

#### UI 组件

```tsx
// 工具调用卡片组件
const ToolCallCard: React.FC<{
  tool: string;
  status: 'running' | 'completed' | 'error';
  input?: string;
  output?: string;
  urls?: { url: string; status: string }[];
}> = ({ tool, status, input, output, urls }) => {
  return (
    <div className="tool-call-card">
      <div className="tool-header">
        {status === 'running' && <Loader2 className="animate-spin" />}
        {status === 'completed' && <CheckCircle2 className="text-green-500" />}
        <span>{tool}</span>
      </div>
      {input && <div className="tool-input">输入: {input}</div>}
      {urls && (
        <div className="tool-urls">
          {urls.map((u, i) => (
            <div key={i} className={u.status}>
              {u.url}
            </div>
          ))}
        </div>
      )}
      {output && <div className="tool-output">{output}</div>}
    </div>
  );
};
```

```tsx
// 思考过程区域
const ThinkingPanel: React.FC<{ content: string }> = ({ content }) => {
  const [expanded, setExpanded] = useState(false);
  return (
    <Collapsible open={expanded} onOpenChange={setExpanded}>
      <CollapsibleTrigger>
        🧠 思考过程 (点击展开)
      </CollapsibleTrigger>
      <CollapsibleContent>
        <div className="thinking-content prose">
          {content}
        </div>
      </CollapsibleContent>
    </Collapsible>
  );
};
```

---

### 3. 消息渲染改造

#### 当前渲染方式
```tsx
<div className="prose">
  {msg.content}  {/* 纯文本渲染 */}
</div>
```

#### 改造后渲染方式
```tsx
<div className="message-content">
  {msg.parts?.map((part, idx) => {
    switch (part.type) {
      case 'tool_call':
        return <ToolCallCard key={idx} {...part} />;
      case 'streaming':
        return (
          <div key={idx} className="prose">
            {part.content}
            <span className="cursor-blink">█</span>
          </div>
        );
      case 'text':
      default:
        return <div key={idx} className="prose">{part.content}</div>;
    }
  })}
</div>
```

---

### 4. 动画效果

#### 打字机光标
```css
.cursor-blink {
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}
```

#### 工具卡片动画
```tsx
<motion.div
  initial={{ opacity: 0, y: 10 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3 }}
>
  <ToolCallCard {...} />
</motion.div>
```

---

## 实施计划

### Phase 1: 后端流式输出 (高优先级)
- [ ] 改造 `api.py` 支持 LLM 流式调用
- [ ] 新增 `llm_chunk` 事件
- [ ] 新增 `tool_start/tool_end` 事件

### Phase 2: 前端消息渲染 (高优先级)
- [ ] 重构消息数据结构
- [ ] 实现流式文本渲染
- [ ] 添加打字机效果

### Phase 3: 工具调用卡片 (中优先级)
- [ ] 创建 `ToolCallCard` 组件
- [ ] 实现 URL 列表显示
- [ ] 添加状态图标

### Phase 4: 思考过程展示 (低优先级)
- [ ] 解析 DeepSeek R1 reasoning_content
- [ ] 创建折叠面板组件
- [ ] 添加思考时长显示

---

## 参考资料

### 竞品分析
- **ChatGPT**: 工具调用卡片 + 来源列表 + 流式输出
- **Perplexity**: 步骤进度 + URL 状态 + 逐字输出
- **DeepSeek R1**: 思考过程独立显示 + 最终答案
- **Manus AI**: 详细行动日志 + 实时截图

### 技术文档
- LangChain Streaming: `astream()` 方法
- DeepSeek R1 API: `reasoning_content` 字段
- SSE 事件格式: `event: {type}\ndata: {json}\n\n`