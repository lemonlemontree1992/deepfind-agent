# DeepFind Agent 深度调研报告 V2.0

**生成时间**: 2025-06-29  
**项目路径**: `/Users/purepure/Desktop/docs/deepfind-agent`  
**版本**: V2.0 (补充查漏版)

---

## 📋 报告更新说明

本版本在 V1.0 基础上，新增以下内容：
1. **项目功能补全** - 发现遗漏的关键功能模块
2. **架构深度分析** - LangGraph 高级特性使用评估
3. **业内深度对比** - 与 GPT-Researcher、Perplexity 具体实现对比
4. **搜索工具评测** - Tavily/Exa/Serper/Bing 详细对比
5. **具体实现方案** - 可落地的代码级优化建议
6. **性能评估体系** - 量化的优化效果评估方法

---

## 一、项目功能全景（补充）

### 1.1 完整 Agent 架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           DeepFind Agent 完整架构                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                      用户交互层                                   │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │    │
│  │  │  Streamlit   │  │   React UI   │  │  FastAPI REST + SSE  │  │    │
│  │  │   (app.py)   │  │  (frontend)  │  │      (api.py)        │  │    │
│  │  └──────────────┘  └──────────────┘  └──────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                     │
│                                    ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    工作流编排层 (LangGraph)                        │    │
│  │                                                                   │    │
│  │   workflow.py                                                     │    │
│  │   ├── write_todos()        任务拆解                               │    │
│  │   ├── save_research_request()  保存需求                           │    │
│  │   ├── run_search()         搜索 Agent                             │    │
│  │   ├── run_analyze()        分析 Agent                             │    │
│  │   ├── run_report()         报告 Agent                             │    │
│  │   └── verify_report()      验证报告                               │    │
│  │                                                                   │    │
│  │   task_planner.py + task_executor.py  (任务DAG规划与执行)         │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                     │
│                                    ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                        Agent 层                                   │    │
│  │                                                                   │    │
│  │  核心流程:                                                        │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │    │
│  │  │Search Agent │→ │Analyze Agent│→ │Report Agent │              │    │
│  │  │(分类搜索)    │  │(并行解析)    │  │(自适应生成) │              │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘              │    │
│  │                                                                   │    │
│  │  增强模块 (V1.0报告遗漏):                                          │    │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │    │
│  │  │Extraction Agent │  │Validation Agent │  │Enhanced Report  │  │    │
│  │  │(智能实体提取)    │  │(交叉验证)       │  │(8步增强生成)      │  │    │
│  │  │    ⭐ 新发现     │  │   ⭐ 新发现      │  └─────────────────┘  │    │
│  │  └─────────────────┘  └─────────────────┘                        │    │
│  │                                                                   │    │
│  │  ┌─────────────────┐  ┌─────────────────┐                        │    │
│  │  │  Task Planner   │  │  Task Executor  │                        │    │
│  │  │  (DAG任务规划)   │  │  (任务执行器)    │                        │    │
│  │  │   ⭐ 新发现      │  │   ⭐ 新发现      │                        │    │
│  │  └─────────────────┘  └─────────────────┘                        │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                     │
│                                    ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                        工具层 (Tools)                             │    │
│  │                                                                   │    │
│  │  搜索工具:                         网页解析:                       │    │
│  │  ┌───────────────┐               ┌───────────────┐               │    │
│  │  │ Tavily API    │               │ Jina Reader   │               │    │
│  │  │ (AI专用搜索)   │               │ (免费解析)    │               │    │
│  │  └───────────────┘               └───────────────┘               │    │
│  │  ┌───────────────┐               ┌───────────────┐               │    │
│  │  │ DuckDuckGo    │               │ Playwright    │               │    │
│  │  │ (国内可用)     │               │ (动态网页)    │               │    │
│  │  └───────────────┘               └───────────────┘               │    │
│  │  ┌───────────────┐               ┌───────────────┐               │    │
│  │  │ Brave Search  │               │ Parallel Scrap│               │    │
│  │  │ (备用源)       │               │ (并行解析5并发)│               │    │
│  │  └───────────────┘               └───────────────┘               │    │
│  │                                                                   │    │
│  │  智能搜索: smart_search.py - 自动fallback机制                      │    │
│  │  并行搜索: parallel_search.py - 多维度并行搜索                     │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                     │
│                                    ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                      数据模型层 (Schemas)                         │    │
│  │                                                                   │    │
│  │  entities.py - Pydantic 结构化实体定义                            │    │
│  │  ├── Attraction (景点)    ├── OpeningHours (营业时间)             │    │
│  │  ├── Restaurant (餐厅)    ├── Pricing (价格)                      │    │
│  │  ├── Hotel (酒店)         ├── Location (位置)                      │    │
│  │  ├── Transportation (交通) ├── Contact (联系方式)                  │    │
│  │  └── TravelTip (贴士)                                            │    │
│  │                                                                   │    │
│  │  tasks.py - 任务定义 (DAG规划)                                     │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 V1.0 报告遗漏的重要功能

#### ⭐ 1. Validation Agent (交叉验证机制)

**位置**: `agents/validation_agent.py`

**功能**: 多来源交叉验证信息准确性

```python
# 已实现的功能 (V1.0未记录)
def cross_validate_field(field_name: str, values: List[Dict]) -> Dict:
    """
    交叉验证单个字段
    - 来源权重: 官网(1.0) > 政府网站(0.95) > 知名平台(0.8) > 社交媒体(0.6)
    - 一致性计算: agreement_ratio = 一致来源数 / 总来源数
    - 置信度: weighted_confidence 综合来源权重和一致性
    """
    source_weights = {
        "官网": 1.0, "政府网站": 0.95, "马蜂窝": 0.8, 
        "携程": 0.8, "小红书": 0.65, "博客": 0.5
    }
    # 验证通过: confidence >= 0.6 && agreement_ratio >= 0.5
```

**评估**: 
- ✅ **已有的验证能力**: 价格、时间、评分等字段交叉验证
- ✅ **来源可信度权重**: 基于来源类型加权计算
- ❌ **缺失**: 未验证引用准确性、未检测幻觉

#### ⭐ 2. Extraction Agent (智能实体提取)

**位置**: `agents/extraction_agent.py`

**功能**: 自动识别内容类型并提取结构化信息

```python
# 已实现的功能 (V1.0未记录)
def extract_entities_intelligent(state: ExtractionState):
    """
    智能提取实体 - 支持多种内容类型
    - content_type: weather|product|travel|tech|news|qa|other
    - entities: 根据类型动态提取结构化信息
    - confidence_scores: 提取置信度评分
    """
```

**已有实体模式**:
- 旅行类: attractions, restaurants, hotels, transportations, tips
- 产品类: products, specs, pros, cons, rating
- 技术类: concepts, steps, code_examples

**评估**: 
- ✅ **已有**: 自动内容类型识别、动态实体提取、置信度评分
- ❌ **缺失**: 实体关系图构建、知识图谱

#### ⭐ 3. Task Planner & Executor (任务DAG规划)

**位置**: `agents/task_planner.py`, `agents/task_executor.py`

**功能**: 将复杂查询拆解为有向无环图(DAG)任务并行执行

```python
# 已实现的功能 (V1.0未记录)
def plan_tasks_for_query(query: str) -> TaskPlan:
    """
    任务DAG规划
    - tasks: Task列表 (每个Task包含id, description, dependencies)
    - dag: 有向无环图
    - execution_order: 拓扑排序后的执行顺序
    """
```

**评估**: 
- ✅ **已有**: 任务依赖分析、DAG构建、并行执行
- ❌ **缺失**: 任务失败重试、动态任务调整

#### ⭐ 4. 国际化与本地化

**位置**: 业务调研问卷支持中文

**评估**: 
- ✅ 已有中文问答生成
- ❌ 缺少多语言支持切换

#### ⭐ 5. 流式输出 (SSE)

**位置**: `api.py` - FastAPI + SSE

```python
# 已实现的流式输出 (V1.0未记录)
async def stream_research_progress(session_id: str):
    """SSE 实时推送研究进度"""
    yield f"data: {json.dumps(progress_data)}\n\n"
```

**评估**: 
- ✅ **已有**: 实时进度推送、阶段状态更新
- ❌ **缺失**: 报告内容流式生成(当前是整段输出)

---

## 二、架构深度分析（新增）

### 2.1 LangGraph 使用评估

#### 当前使用方式

```python
# workflow.py - 简单线性流程
workflow = StateGraph(SearchState)
workflow.add_node("generate_queries", generate_search_queries)
workflow.add_node("execute_search", execute_search)
workflow.set_entry_point("generate_queries")
workflow.add_edge("generate_queries", "execute_search")
workflow.add_edge("execute_search", END)
```

#### LangGraph 高级特性 (未使用)

| 特性 | 说明 | 当前状态 | 建议使用 |
|------|------|----------|----------|
| **Checkpointing** | 状态持久化，支持暂停/恢复 | ❌ 未使用 | 🔴 高优先级 |
| **Memory** | 跨会话记忆，上下文保持 | ❌ 未使用 | 🟡 中优先级 |
| **Human-in-the-loop** | 人工审核节点 | ❌ 未使用 | 🟢 低优先级 |
| **Conditional Edges** | 条件分支路由 | ❌ 未使用 | 🔴 高优先级 |
| **Parallel Nodes** | 并行节点执行 | ⚠️ 部分使用 | 可优化 |
| **Subgraphs** | 嵌套子图 | ❌ 未使用 | 🟢 低优先级 |
| **Error Boundaries** | 错误边界处理 | ❌ 未使用 | 🔴 高优先级 |

#### 建议优化：增强型工作流

```python
# 建议实现：带条件分支和错误处理的工作流
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END

def build_enhanced_workflow():
    workflow = StateGraph(ResearchState)
    
    # 添加节点
    workflow.add_node("classify_query", classify_query_node)
    workflow.add_node("search_shallow", search_shallow_node)
    workflow.add_node("search_deep", search_deep_node)
    workflow.add_node("analyze", analyze_node)
    workflow.add_node("validate", validate_node)
    workflow.add_node("generate_report", generate_report_node)
    workflow.add_node("quality_check", quality_check_node)
    workflow.add_node("retry_search", retry_search_node)
    workflow.add_node("human_review", human_review_node)
    
    # 条件分支
    def route_by_complexity(state):
        if state["complexity"] == "simple":
            return "search_shallow"
        return "search_deep"
    
    def check_quality(state):
        if state["quality_score"] >= 0.8:
            return "generate_report"
        elif state["retry_count"] < 3:
            return "retry_search"
        return "human_review"
    
    # 构建工作流
    workflow.set_entry_point("classify_query")
    workflow.add_conditional_edges("classify_query", route_by_complexity)
    workflow.add_edge("search_shallow", "analyze")
    workflow.add_edge("search_deep", "analyze")
    workflow.add_edge("analyze", "validate")
    workflow.add_conditional_edges("validate", check_quality)
    workflow.add_edge("retry_search", "analyze")
    workflow.add_edge("human_review", "generate_report")
    workflow.add_edge("generate_report", END)
    
    # 添加持久化
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)
```

### 2.2 错误处理与重试机制（缺失）

#### 当前问题

```python
# workflow.py - 简单错误处理
except Exception as e:
    logger.error(f"工作流执行失败: {str(e)}")
    result["errors"].append(str(e))
    # ❌ 无重试机制
    # ❌ 无降级策略
    # ❌ 无错误分类
```

#### 建议实现：分层重试机制

```python
# 建议实现：retry_handler.py
import tenacity
from functools import wraps

# 搜索重试配置
@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_exponential(multiplier=1, min=2, max=10),
    retry=tenacity.retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
    before_sleep=tenacity.before_sleep_log(logger, logging.WARNING)
)
def search_with_retry(query: str, search_func):
    """带重试的搜索"""
    return search_func(query)

# LLM调用重试配置
@tenacity.retry(
    stop=tenacity.stop_after_attempt(2),
    wait=tenacity.wait_fixed(5),
    retry=tenacity.retry_if_exception_type((RateLimitError, ServiceUnavailableError))
)
def llm_call_with_retry(prompt: str, llm):
    """带重试的LLM调用"""
    return llm.invoke(prompt)

# 降级策略
def search_with_fallback(query: str):
    """带降级的搜索"""
    sources = [
        ("Tavily", tavily_search_sync),
        ("DuckDuckGo", duckduckgo_search_sync),
        ("Brave", brave_search_sync),
    ]
    
    for source_name, search_func in sources:
        try:
            results = search_with_retry(query, search_func)
            if results:
                return results, source_name
        except Exception as e:
            logger.warning(f"{source_name} 搜索失败: {e}")
            continue
    
    return [], "failed"
```

### 2.3 Token 成本优化（新增分析）

#### 当前问题

```python
# analyze_agent.py - 内容未做Token优化
content_summary = ""
for i, item in enumerate(analyzed_content, 1):
    content_summary += f"\n[来源 {i}] {item['title']}\n"
    content_summary += f"URL: {item['url']}\n"
    # ❌ 直接截取前2000字符，可能截断重要信息
    content_text = item.get("content", "")
    content_summary += f"内容摘要: {content_text[:2000]}...\n"
```

#### 建议实现：智能Token管理

```python
# 建议实现：token_manager.py
import tiktoken

class TokenManager:
    """Token 管理"""
    
    def __init__(self, model: str = "gpt-4", max_tokens: int = 128000):
        self.encoding = tiktoken.encoding_for_model(model)
        self.max_tokens = max_tokens
        self.reserved_tokens = 4000  # 预留给输出
    
    def count_tokens(self, text: str) -> int:
        """计算Token数"""
        return len(self.encoding.encode(text))
    
    def smart_truncate(self, text: str, max_tokens: int) -> str:
        """智能截断 - 保留关键信息"""
        tokens = self.encoding.encode(text)
        if len(tokens) <= max_tokens:
            return text
        
        # 策略：优先保留开头和结尾
        head_tokens = max_tokens // 3
        tail_tokens = max_tokens // 3
        middle_tokens = max_tokens - head_tokens - tail_tokens
        
        truncated = (
            tokens[:head_tokens] +
            self.encoding.encode("\n...[内容已截断]...\n") +
            tokens[-tail_tokens:]
        )
        return self.encoding.decode(truncated)
    
    def optimize_content(self, items: List[Dict], query: str) -> str:
        """优化内容 - 按相关性排序和截断"""
        available_tokens = self.max_tokens - self.reserved_tokens
        budget_per_item = available_tokens // len(items)
        
        optimized = []
        for item in items:
            content = item.get("content", "")
            title = item.get("title", "")
            
            # 按预算截断
            truncated = self.smart_truncate(
                content, 
                budget_per_item - self.count_tokens(title) - 50
            )
            optimized.append(f"[来源] {title}\n{truncated}\n")
        
        return "\n---\n".join(optimized)
```

---

## 三、搜索工具深度评测（新增）

### 3.1 搜索工具对比分析

| 工具 | 定位 | 特点 | 价格 | 国内可用 | 推荐度 |
|------|------|------|------|----------|--------|
| **Tavily** | AI专用搜索 | 结果结构化、答案提取、深度搜索模式 | $0.004/次 | ❌ 需翻墙 | ⭐⭐⭐⭐⭐ |
| **Exa** | 神经搜索 | 语义相似性、内容质量高、无广告 | $1/1000次 | ❌ 需翻墙 | ⭐⭐⭐⭐⭐ |
| **Serper** | Google API | 原生Google结果、速度快 | $50/5000次 | ❌ 需翻墙 | ⭐⭐⭐⭐ |
| **Bing Search** | 通用搜索 | 微软生态、结果丰富 | 免费层有限 | ⚠️ 不稳定 | ⭐⭐⭐⭐ |
| **DuckDuckGo** | 隐私搜索 | 无追踪、API简单 | 免费 | ✅ 可用 | ⭐⭐⭐ |
| **Brave Search** | 独立搜索 | 独立索引、无偏见 | 免费 | ⚠️ 不稳定 | ⭐⭐⭐ |
| **SerpAPI** | 多引擎聚合 | Google/Bing/Yahoo等 | $50/5000次 | ❌ 需翻墙 | ⭐⭐⭐⭐ |

### 3.2 Tavily vs Exa 深度对比

```python
# Tavily 特点
{
    "search_depth": "basic|advanced",  # 深度搜索选项
    "include_answer": True,            # AI 摘要答案
    "include_raw_content": True,       # 原始HTML
    "include_domains": [],             # 域名过滤
    "max_results": 10,
}

# Exa 特点 (神经搜索)
{
    "use_autoprompt": True,            # 自动优化查询
    "type": "keyword|neural|auto",     # 搜索类型
    "category": "company|research|news|movie|song|book|paper",
    "numResults": 10,
    "contents": {
        "text": {"maxCharacters": 1000},
        "livepxincrawl": True          # 实时抓取
    }
}

# 对比结论
"""
Tavily 优势:
  - 专为 AI Agent 设计，结果直接可用
  - 深度搜索模式，信息更完整
  - 内置答案提取

Exa 优势:
  - 语义匹配更精准
  - 内容质量过滤
  - 分类搜索(论文、新闻等)

建议:
  - 综合调研: Tavily advanced 模式
  - 学术研究: Exa paper 类别
  - 实时新闻: 两者的 livecrawl 功能
"""
```

### 3.3 搜索源优化建议

```python
# 建议实现：multi_search_aggregator.py
class MultiSearchAggregator:
    """多搜索源聚合器"""
    
    def __init__(self):
        self.sources = {
            "tavily": {"priority": 1, "daily_budget": 1000, "cost": 0.004},
            "exa": {"priority": 2, "daily_budget": 500, "cost": 0.001},
            "duckduckgo": {"priority": 3, "daily_budget": float('inf'), "cost": 0},
            "brave": {"priority": 4, "daily_budget": float('inf'), "cost": 0},
        }
        self.usage = {k: 0 for k in self.sources}
    
    def search(self, query: str, search_type: str = "general"):
        """智能多源搜索"""
        results = []
        
        # 根据查询类型选择策略
        if search_type == "academic":
            prioritized = ["tavily", "exa", "duckduckgo"]
        elif search_type == "news":
            prioritized = ["tavily", "duckduckgo", "brave"]
        else:
            prioritized = ["tavily", "duckduckgo", "brave"]
        
        for source in prioritized:
            if self.check_budget(source):
                try:
                    source_results = self.execute_search(source, query)
                    results.extend(source_results)
                    self.usage[source] += 1
                    
                    if len(results) >= 10:
                        break
                except Exception as e:
                    logger.warning(f"{source} 搜索失败: {e}")
                    continue
        
        return self.deduplicate_and_rank(results)
```

---

## 四、业内深度对比（补充）

### 4.1 与 GPT-Researcher 架构对比

| 维度 | DeepFind Agent | GPT-Researcher | 差距分析 |
|------|----------------|----------------|----------|
| **搜索深度** | 1-2 层 | 2-3 层 | 需增强递归搜索 |
| **搜索源** | 3 个 | 10+ 个 | 需扩展源 |
| **报告模板** | 自适应 | 固定模板 | ✅ 更好 |
| **分类搜索** | ✅ 有 | ❌ 无 | ✅ 更好 |
| **并行解析** | ✅ 5并发 | ✅ 类似 | 相当 |
| **向量存储** | ❌ 无 | ✅ Chroma | 需增加 |
| **增量更新** | ❌ 无 | ⚠️ 部分 | 可增加 |
| **引用追踪** | ⚠️ 简单 | ✅ 完整 | 需增强 |
| **本地缓存** | ❌ 无 | ⚠️ 简单 | 可增加 |
| **流式输出** | ⚠️ 进度 | ✅ 内容 | 可增强 |

### 4.2 GPT-Researcher 核心实现借鉴

```python
# GPT-Researcher 核心流程 (可借鉴)
class GPTResearcher:
    def __init__(self):
        self.retriever = VectorRetriever()  # 向量检索
        self.context_manager = ContextManager()  # 上下文管理
    
    async def research(self, query: str):
        # 1. 生成子查询
        sub_queries = await self.generate_sub_queries(query)
        
        # 2. 并行搜索 + 向量存储
        for sub_query in sub_queries:
            results = await self.search(sub_query)
            await self.retriever.add_documents(results)
        
        # 3. 相关性检索
        relevant_docs = await self.retriever.get_relevant_documents(query)
        
        # 4. 报告生成
        report = await self.generate_report(query, relevant_docs)
        
        return report

# DeepFind Agent 可借鉴的实现
class EnhancedDeepFind:
    def __init__(self):
        self.vector_store = Chroma()  # 新增：向量存储
        self.cache = SearchCache()    # 新增：搜索缓存
        self.relevance_scorer = RelevanceScorer()  # 新增：相关性评分
    
    async def research_with_depth(self, query: str, max_depth: int = 3):
        """递归深度搜索"""
        visited = set()
        results = []
        
        # BFS 深度搜索
        queue = [(query, 0)]
        while queue:
            current_query, depth = queue.pop(0)
            
            if depth >= max_depth or current_query in visited:
                continue
            
            visited.add(current_query)
            search_results = await self.search_with_cache(current_query)
            
            # 向量存储
            await self.vector_store.add_documents(search_results)
            results.extend(search_results)
            
            # 提取相关链接，继续深搜
            if depth < max_depth - 1:
                links = self.extract_relevant_links(search_results, query)
                for link in links[:5]:  # 限制广度
                    queue.append((link, depth + 1))
        
        return results
```

### 4.3 ReAct vs Plan-and-Execute 架构分析

**当前 DeepFind 采用**: 线性 Plan-and-Execute 模式

```
Plan → Search → Analyze → Report → Verify
```

**ReAct 架构优势**: 思考-行动-观察循环

```
while not done:
    thought = think(current_state)
    action = decide_action(thought)
    observation = execute(action)
    state = update(state, observation)
```

**建议**: 混合架构

```python
# 建议实现：hybrid_agent.py
class HybridResearchAgent:
    """混合架构：Plan-and-Execute + ReAct"""
    
    def research(self, query: str):
        # Phase 1: 规划 (Plan-and-Execute)
        plan = self.plan(query)
        
        for task in plan.tasks:
            # Phase 2: 执行 (ReAct循环)
            max_iterations = 5
            iteration = 0
            
            while iteration < max_iterations:
                # 思考
                thought = self.think(task, self.state)
                
                # 判断是否完成
                if thought["action"] == "finish":
                    break
                
                # 执行行动
                observation = self.execute(thought["action"])
                
                # 观察结果，决定下一步
                if observation["quality"] < 0.6:
                    # 质量不够，调整策略
                    thought = self.reflect(observation)
                    thought["action"] = "retry_with_different_query"
                
                iteration += 1
        
        return self.generate_final_report()
```

---

## 五、具体实现方案（新增）

### 5.1 递归深度搜索实现方案

```python
# 新增文件：agents/recursive_search_agent.py
"""
递归深度搜索 Agent - 实现 3 层搜索深度

搜索流程:
Layer 1: 初始查询搜索
Layer 2: 提取关键链接深搜
Layer 3: 追踪引用和参考来源
"""

from typing import List, Dict, Any, Set, Tuple
from dataclasses import dataclass
import asyncio
from urllib.parse import urlparse, urljoin
import re

@dataclass
class SearchResult:
    url: str
    title: str
    content: str
    depth: int
    source_query: str
    relevance_score: float
    links_found: List[str]

class RecursiveSearchAgent:
    """递归深度搜索 Agent"""
    
    def __init__(
        self,
        max_depth: int = 3,
        max_links_per_page: int = 5,
        max_total_results: int = 50,
        relevance_threshold: float = 0.3
    ):
        self.max_depth = max_depth
        self.max_links_per_page = max_links_per_page
        self.max_total_results = max_total_results
        self.relevance_threshold = relevance_threshold
        self.visited_urls: Set[str] = set()
        self.results: List[SearchResult] = []
    
    async def search_with_depth(
        self, 
        query: str,
        search_func,
        scrape_func,
        relevance_scorer
    ) -> List[SearchResult]:
        """
        递归深度搜索
        
        Args:
            query: 初始查询
            search_func: 搜索函数
            scrape_func: 网页解析函数
            relevance_scorer: 相关性评分函数
        """
        # Layer 1: 初始搜索
        layer1_results = await self._search_layer(query, search_func, depth=1)
        
        # Layer 2: 从 Layer 1 结果中提取关键链接深搜
        layer2_results = []
        for result in layer1_results[:self.max_links_per_page]:
            relevant_links = await self._extract_relevant_links(
                result, query, relevance_scorer
            )
            for link in relevant_links[:2]:  # 每个页面最多深追2个链接
                layer2 = await self._deep_crawl(
                    link, scrape_func, depth=2, 
                    parent_query=result.title
                )
                layer2_results.extend(layer2)
        
        # Layer 3: 追踪引用和参考来源
        layer3_results = []
        for result in layer2_results[:self.max_links_per_page]:
            citations = await self._extract_citations(result, scrape_func)
            for citation in citations[:1]:
                if citation not in self.visited_urls:
                    layer3 = await self._deep_crawl(
                        citation, scrape_func, depth=3,
                        parent_query=result.title
                    )
                    layer3_results.extend(layer3)
        
        # 合并和排序
        all_results = layer1_results + layer2_results + layer3_results
        return self._rank_and_deduplicate(all_results, relevance_scorer, query)
    
    async def _search_layer(
        self, 
        query: str, 
        search_func, 
        depth: int
    ) -> List[SearchResult]:
        """搜索单层"""
        raw_results = await search_func(query)
        
        results = []
        for item in raw_results:
            url = item.get("url", "")
            if url in self.visited_urls:
                continue
            
            self.visited_urls.add(url)
            results.append(SearchResult(
                url=url,
                title=item.get("title", ""),
                content=item.get("content", item.get("description", "")),
                depth=depth,
                source_query=query,
                relevance_score=0.0,
                links_found=[]
            ))
        
        return results
    
    async def _extract_relevant_links(
        self,
        result: SearchResult,
        query: str,
        relevance_scorer
    ) -> List[str]:
        """提取相关链接"""
        content = result.content
        
        # 提取链接
        link_pattern = r'href=["\']([^"\']+)["\']|URL:\s*([^\s]+)'
        matches = re.findall(link_pattern, content)
        links = [m[0] or m[1] for m in matches if m[0] or m[1]]
        
        # 过滤无效链接
        valid_links = []
        for link in links:
            if self._is_valid_link(link, result.url):
                # 简单相关性判断
                score = await relevance_scorer(link, query)
                if score >= self.relevance_threshold:
                    valid_links.append((link, score))
        
        # 按相关性排序
        valid_links.sort(key=lambda x: x[1], reverse=True)
        return [link for link, _ in valid_links[:self.max_links_per_page]]
    
    def _is_valid_link(self, link: str, base_url: str) -> bool:
        """验证链接有效性"""
        if not link:
            return False
        
        # 转换相对链接为绝对链接
        if link.startswith('/'):
            parsed = urlparse(base_url)
            link = f"{parsed.scheme}://{parsed.netloc}{link}"
        
        # 过滤无效链接
        invalid_patterns = [
            r'javascript:', r'mailto:', r'tel:', r'#',
            r'\.pdf$', r'\.jpg$', r'\.png$', r'\.gif$',
            r'login', r'signup', r'register', r'cart'
        ]
        
        for pattern in invalid_patterns:
            if re.search(pattern, link, re.IGNORECASE):
                return False
        
        return True
    
    async def _deep_crawl(
        self,
        url: str,
        scrape_func,
        depth: int,
        parent_query: str
    ) -> List[SearchResult]:
        """深度爬取单个URL"""
        if url in self.visited_urls:
            return []
        
        self.visited_urls.add(url)
        
        try:
            content = await scrape_func(url)
            return [SearchResult(
                url=url,
                title=content.get("title", ""),
                content=content.get("content", ""),
                depth=depth,
                source_query=parent_query,
                relevance_score=0.0,
                links_found=[]
            )]
        except Exception as e:
            logger.warning(f"深度爬取失败 {url}: {e}")
            return []
    
    async def _extract_citations(
        self,
        result: SearchResult,
        scrape_func
    ) -> List[str]:
        """提取引用来源"""
        content = result.content
        
        # 提取引用链接模式
        patterns = [
            r'来源[：:]\s*([^\s]+)',
            r'参考[：:]\s*([^\s]+)',
            r'Reference[：:]\s*([^\s]+)',
            r'Source[：:]\s*([^\s]+)',
            r'\[\d+\]\s*([^\s]+)',
        ]
        
        citations = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            citations.extend(matches)
        
        return list(set(citations))[:5]
    
    def _rank_and_deduplicate(
        self,
        results: List[SearchResult],
        relevance_scorer,
        query: str
    ) -> List[SearchResult]:
        """排序和去重"""
        # 计算相关性分数
        for result in results:
            result.relevance_score = relevance_scorer(result.content, query)
        
        # 去重
        seen = set()
        unique_results = []
        for result in results:
            if result.url not in seen:
                seen.add(result.url)
                unique_results.append(result)
        
        # 按相关性 + 深度加权排序
        unique_results.sort(
            key=lambda x: x.relevance_score * 0.7 + (3 - x.depth) * 0.3,
            reverse=True
        )
        
        return unique_results[:self.max_total_results]


# 集成到现有 workflow.py
async def run_recursive_search(query: str, max_depth: int = 3):
    """运行递归深度搜索"""
    from tools import smart_search, scrape_url
    
    agent = RecursiveSearchAgent(
        max_depth=max_depth,
        max_links_per_page=5,
        max_total_results=50
    )
    
    results = await agent.search_with_depth(
        query=query,
        search_func=smart_search,
        scrape_func=scrape_url,
        relevance_scorer=lambda content, q: 0.5  # 简单实现
    )
    
    # 转换为现有格式
    return [
        {
            "url": r.url,
            "title": r.title,
            "content": r.content,
            "depth": r.depth,
            "source_query": r.source_query,
            "relevance_score": r.relevance_score,
        }
        for r in results
    ]
```

### 5.2 信息可信度评估实现

```python
# 新增文件：agents/credibility_scorer.py
"""
信息可信度评估器

评估维度:
1. 来源权威性 (Domain Authority)
2. 内容时效性 (Freshness)
3. 引用数量 (Citation Count)
4. 交叉验证 (Cross-Reference)
5. 作者可信度 (Author Credibility)
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import re
from urllib.parse import urlparse

@dataclass
class CredibilityScore:
    overall: float  # 综合分数 0-1
    domain_authority: float
    freshness: float
    citation_count: float
    cross_reference: float
    author_credibility: float
    factors: Dict[str, str]  # 评分因素说明

class CredibilityScorer:
    """信息可信度评分器"""
    
    # 权威域名权重
    DOMAIN_AUTHORITY = {
        # 政府和官方
        ".gov": 1.0, ".gov.cn": 1.0, ".edu": 0.95, ".edu.cn": 0.95,
        # 主流媒体
        "reuters.com": 0.9, "bbc.com": 0.9, "nytimes.com": 0.88,
        "wsj.com": 0.88, "economist.com": 0.9,
        # 科技媒体
        "techcrunch.com": 0.8, "theverge.com": 0.8, "wired.com": 0.85,
        # 学术
        "arxiv.org": 0.95, "scholar.google.com": 0.95, "nature.com": 0.98,
        "science.org": 0.98, "sciencedirect.com": 0.95,
        # 知名平台
        "wikipedia.org": 0.75, "zhihu.com": 0.6, "reddit.com": 0.5,
        # 博客和个人
        "medium.com": 0.5, "blogspot.com": 0.3, "wordpress.com": 0.3,
    }
    
    # 低可信度域名
    LOW_CREDIBILITY_DOMAINS = [
        "tabloid", "gossip", "clickbait", "fake-news",
        " conspiracy", "rumor"
    ]
    
    def __init__(self, llm=None):
        self.llm = llm
    
    def score_source(self, source: Dict[str, Any]) -> CredibilityScore:
        """评估单个来源的可信度"""
        url = source.get("url", "")
        content = source.get("content", "")
        title = source.get("title", "")
        publish_date = source.get("publish_date")
        author = source.get("author", "")
        
        # 1. 来源权威性
        domain_score = self._score_domain_authority(url)
        
        # 2. 内容时效性
        freshness_score = self._score_freshness(publish_date, content)
        
        # 3. 引用数量
        citation_score = self._score_citations(content)
        
        # 4. 作者可信度
        author_score = self._score_author(author, url)
        
        # 5. 交叉验证 (需要外部数据，暂用默认值)
        cross_ref_score = 0.5
        
        # 综合评分 (加权平均)
        overall = (
            domain_score * 0.3 +
            freshness_score * 0.2 +
            citation_score * 0.2 +
            cross_ref_score * 0.15 +
            author_score * 0.15
        )
        
        return CredibilityScore(
            overall=overall,
            domain_authority=domain_score,
            freshness=freshness_score,
            citation_count=citation_score,
            cross_reference=cross_ref_score,
            author_credibility=author_score,
            factors={
                "domain": f"域名权重: {domain_score:.2f}",
                "freshness": f"时效性: {freshness_score:.2f}",
                "citations": f"引用数: {citation_score:.2f}",
                "author": f"作者可信度: {author_score:.2f}",
            }
        )
    
    def _score_domain_authority(self, url: str) -> float:
        """评估域名权威性"""
        if not url:
            return 0.3
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # 完全匹配
            for auth_domain, score in self.DOMAIN_AUTHORITY.items():
                if auth_domain in domain:
                    return score
            
            # 后缀匹配
            if domain.endswith(".gov") or domain.endswith(".gov.cn"):
                return 1.0
            if domain.endswith(".edu") or domain.endswith(".edu.cn"):
                return 0.95
            if domain.endswith(".org"):
                return 0.7
            if domain.endswith(".com") or domain.endswith(".net"):
                return 0.5
            
            # 检查低可信度关键词
            for keyword in self.LOW_CREDIBILITY_DOMAINS:
                if keyword in domain:
                    return 0.2
            
            return 0.4  # 默认值
            
        except Exception:
            return 0.3
    
    def _score_freshness(self, publish_date: str, content: str) -> float:
        """评估内容时效性"""
        # 如果有发布日期
        if publish_date:
            try:
                # 尝试解析日期
                date = self._parse_date(publish_date)
                if date:
                    days_old = (datetime.now() - date).days
                    
                    if days_old < 7:
                        return 1.0
                    elif days_old < 30:
                        return 0.9
                    elif days_old < 90:
                        return 0.8
                    elif days_old < 365:
                        return 0.6
                    else:
                        return 0.4
            except Exception:
                pass
        
        # 从内容推断
        current_year = str(datetime.now().year)
        last_year = str(datetime.now().year - 1)
        
        if current_year in content:
            return 0.9
        elif last_year in content:
            return 0.7
        else:
            return 0.5
    
    def _parse_date(self, date_str: str) -> datetime:
        """解析日期字符串"""
        formats = [
            "%Y-%m-%d", "%Y/%m/%d", "%Y年%m月%d日",
            "%d/%m/%Y", "%m/%d/%Y", "%B %d, %Y"
        ]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None
    
    def _score_citations(self, content: str) -> float:
        """评估引用数量"""
        if not content:
            return 0.3
        
        # 计算引用标记
        citation_patterns = [
            r'\[\d+\]',  # [1], [2] 样式
            r'\(\d{4}\)',  # (2023) 样式
            r'来源[：:]',  # 中文来源
            r'Source:', r'Reference:',  # 英文来源
            r'according to',  # According to ...
        ]
        
        citation_count = 0
        for pattern in citation_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            citation_count += len(matches)
        
        # 归一化
        if citation_count >= 10:
            return 1.0
        elif citation_count >= 5:
            return 0.8
        elif citation_count >= 3:
            return 0.6
        elif citation_count >= 1:
            return 0.4
        else:
            return 0.2
    
    def _score_author(self, author: str, url: str) -> float:
        """评估作者可信度"""
        if not author:
            return 0.4
        
        # 简单规则
        if "博士" in author or "Dr." in author or "PhD" in author:
            return 0.9
        if "教授" in author or "Prof." in author:
            return 0.95
        if "记者" in author or "记者" in author:
            return 0.7
        
        return 0.5
    
    async def detect_bias(self, content: str) -> Dict[str, Any]:
        """检测内容偏见 (使用 LLM)"""
        if not self.llm:
            return {"bias_detected": False, "bias_type": "unknown"}
        
        bias_prompt = """分析以下内容是否存在偏见或主观倾向：

        {content}

        请从以下维度分析：
        1. 立场偏见（是否偏向某一方）
        2. 选择性报道（是否忽略重要事实）
        3. 情感倾向（是否使用煽动性语言）
        4. 商业利益（是否涉及推广）

        以JSON格式返回：
        {{
            "bias_detected": true/false,
            "bias_type": "立场|选择性|情感|商业|无",
            "confidence": 0.0-1.0,
            "explanation": "简短说明"
        }}
        """
        
        # 调用 LLM
        response = await self.llm.ainvoke(bias_prompt.format(content=content[:2000]))
        return self._parse_json_response(response)
    
    def _parse_json_response(self, response: str) -> Dict:
        """解析JSON响应"""
        try:
            import json
            # 提取JSON部分
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
            else:
                json_str = response.strip()
            return json.loads(json_str)
        except Exception:
            return {"bias_detected": False, "bias_type": "unknown"}


# 集成使用
def score_search_results(results: List[Dict]) -> List[Dict]:
    """为搜索结果添加可信度评分"""
    scorer = CredibilityScorer()
    
    for result in results:
        score = scorer.score_source(result)
        result["credibility"] = {
            "overall": score.overall,
            "domain_authority": score.domain_authority,
            "freshness": score.freshness,
            "factors": score.factors,
        }
    
    # 按可信度排序
    results.sort(key=lambda x: x["credibility"]["overall"], reverse=True)
    
    return results
```

### 5.3 向量存储与语义检索实现

```python
# 新增文件：tools/vector_store.py
"""
向量存储与语义检索

功能:
1. 搜索结果向量化存储
2. 语义相似度检索
3. 增量更新支持
"""

from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import hashlib

class VectorDocumentStore:
    """向量文档存储"""
    
    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="research_documents",
            metadata={"hnsw:space": "cosine"}
        )
        self.embedder = SentenceTransformer(embedding_model)
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """添加文档"""
        for doc in documents:
            doc_id = self._generate_id(doc["url"])
            
            # 生成嵌入
            embedding = self.embedder.encode(doc["content"])
            
            # 添加到集合
            self.collection.add(
                ids=[doc_id],
                embeddings=[embedding.tolist()],
                documents=[doc["content"]],
                metadatas=[{
                    "url": doc["url"],
                    "title": doc["title"],
                    "source_query": doc.get("source_query", ""),
                    "depth": doc.get("depth", 1),
                    "timestamp": doc.get("timestamp", ""),
                }]
            )
    
    def search_similar(
        self, 
        query: str, 
        n_results: int = 10,
        where_filter: Optional[Dict] = None
    ) -> List[Dict]:
        """语义相似度搜索"""
        query_embedding = self.embedder.encode(query)
        
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )
        
        return [
            {
                "content": doc,
                "metadata": meta,
                "distance": dist,
            }
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )
        ]
    
    def delete_by_query(self, source_query: str):
        """删除指定查询的文档"""
        self.collection.delete(
            where={"source_query": source_query}
        )
    
    def _generate_id(self, url: str) -> str:
        """生成唯一ID"""
        return hashlib.md5(url.encode()).hexdigest()


# 集成到搜索流程
class EnhancedSearchWithVectorStore:
    """带向量存储的增强搜索"""
    
    def __init__(self):
        self.vector_store = VectorDocumentStore()
        self.cache = {}
    
    async def search_and_store(self, query: str):
        """搜索并存储"""
        # 1. 先检查向量存储
        cached = self.vector_store.search_similar(query, n_results=5)
        if cached and cached[0]["distance"] < 0.1:  # 高度相似
            return [c["metadata"] for c in cached]
        
        # 2. 执行搜索
        results = await self.execute_search(query)
        
        # 3. 存储到向量库
        self.vector_store.add_documents(results)
        
        return results
    
    async def get_related_documents(self, query: str):
        """获取相关文档"""
        return self.vector_store.search_similar(query, n_results=20)
```

---

## 六、性能评估体系（新增）

### 6.1 评估指标定义

```python
# 新增文件：evaluation/metrics.py
"""
评估指标定义

指标分类:
1. 搜索质量指标
2. 报告质量指标  
3. 系统性能指标
"""

from dataclasses import dataclass
from typing import List, Dict

@dataclass
class SearchQualityMetrics:
    """搜索质量指标"""
    precision: float  # 精确率: 相关结果 / 总结果
    recall: float     # 召回率: 相关结果 / 总相关
    ndcg: float       # 归一化折损累积增益
    mrr: float        # 平均倒数排名
    coverage: float   # 覆盖率: 唯一来源数 / 理想来源数
    
@dataclass
class ReportQualityMetrics:
    """报告质量指标"""
    completeness: float      # 完整性: 覆盖的关键点比例
    accuracy: float          # 准确性: 正确陈述的比例
    citation_quality: float  # 引用质量: 有效引用比例
    structure_score: float   # 结构评分: 组织清晰度
    readability: float       # 可读性: Flesch-Kincaid 分数
    
@dataclass
class SystemPerformanceMetrics:
    """系统性能指标"""
    total_time: float        # 总耗时 (秒)
    search_time: float       # 搜索耗时
    analysis_time: float     # 分析耗时
    generation_time: float   # 生成耗时
    token_usage: int         # Token 使用量
    api_calls: int           # API 调用次数
    cost: float              # 成本 (美元)

class EvaluationFramework:
    """评估框架"""
    
    def evaluate_search(self, results: List[Dict], ground_truth: List[str]) -> SearchQualityMetrics:
        """评估搜索质量"""
        # 精确率
        relevant = sum(1 for r in results if self._is_relevant(r, ground_truth))
        precision = relevant / len(results) if results else 0
        
        # 召回率
        recall = relevant / len(ground_truth) if ground_truth else 0
        
        # MRR
        mrr = self._calculate_mrr(results, ground_truth)
        
        # NDCG
        ndcg = self._calculate_ndcg(results, ground_truth)
        
        return SearchQualityMetrics(
            precision=precision,
            recall=recall,
            ndcg=ndcg,
            mrr=mrr,
            coverage=len(set(r["url"] for r in results)) / 10  # 假设理想10个来源
        )
    
    def evaluate_report(self, report: str, sources: List[Dict], facts: List[str]) -> ReportQualityMetrics:
        """评估报告质量"""
        # 完整性
        covered_facts = sum(1 for fact in facts if fact in report)
        completeness = covered_facts / len(facts) if facts else 0
        
        # 引用质量
        citations = self._extract_citations(report)
        valid_citations = sum(1 for c in citations if self._validate_citation(c, sources))
        citation_quality = valid_citations / len(citations) if citations else 0
        
        # 结构评分
        structure_score = self._evaluate_structure(report)
        
        # 可读性
        readability = self._calculate_readability(report)
        
        return ReportQualityMetrics(
            completeness=completeness,
            accuracy=0.0,  # 需要人工评估
            citation_quality=citation_quality,
            structure_score=structure_score,
            readability=readability
        )
    
    def _is_relevant(self, result: Dict, ground_truth: List[str]) -> bool:
        """判断结果是否相关"""
        url = result.get("url", "")
        title = result.get("title", "")
        return any(gt in url or gt in title for gt in ground_truth)
    
    def _calculate_mrr(self, results: List[Dict], ground_truth: List[str]) -> float:
        """计算 MRR"""
        for i, result in enumerate(results, 1):
            if self._is_relevant(result, ground_truth):
                return 1.0 / i
        return 0.0
    
    def _calculate_ndcg(self, results: List[Dict], ground_truth: List[str]) -> float:
        """计算 NDCG"""
        import math
        
        dcg = 0.0
        for i, result in enumerate(results, 1):
            relevance = 1.0 if self._is_relevant(result, ground_truth) else 0.0
            dcg += relevance / math.log2(i + 1)
        
        # Ideal DCG
        idcg = sum(1.0 / math.log2(i + 1) for i in range(1, len(ground_truth) + 1))
        
        return dcg / idcg if idcg > 0 else 0.0
    
    def _extract_citations(self, report: str) -> List[str]:
        """提取引用"""
        import re
        return re.findall(r'\[(\d+)\]', report)
    
    def _validate_citation(self, citation: str, sources: List[Dict]) -> bool:
        """验证引用有效性"""
        try:
            idx = int(citation) - 1
            return 0 <= idx < len(sources)
        except ValueError:
            return False
    
    def _evaluate_structure(self, report: str) -> float:
        """评估报告结构"""
        # 检查必要章节
        required_sections = ["摘要", "背景", "分析", "结论", "参考"]
        found = sum(1 for section in required_sections if section in report)
        return found / len(required_sections)
    
    def _calculate_readability(self, report: str) -> float:
        """计算可读性分数"""
        # 简化版 Flesch-Kincaid
        sentences = report.split("。")
        words = report.split()
        
        if not sentences or not words:
            return 0.0
        
        avg_sentence_length = len(words) / len(sentences)
        
        # 越短越易读
        if avg_sentence_length <= 15:
            return 1.0
        elif avg_sentence_length <= 25:
            return 0.8
        elif avg_sentence_length <= 35:
            return 0.6
        else:
            return 0.4
```

### 6.2 Benchmark 测试集

```yaml
# evaluation/benchmark.yaml
# 用于评估的测试集

test_cases:
  - id: travel_001
    query: "济州岛5天4晚旅游攻略"
    type: travel
    expected:
      key_entities:
        - "牛岛"
        - "城山日出峰"
        - "汉拿山"
        - "黑猪肉"
      min_sources: 8
      min_length: 3000
      must_cover:
        - "景点"
        - "美食"
        - "住宿"
        - "交通"
  
  - id: tech_001
    query: "LangGraph 和 LangChain 的区别"
    type: technical
    expected:
      key_entities:
        - "状态管理"
        - "工作流"
        - "Agent"
      min_sources: 5
      min_length: 2000
      must_cover:
        - "架构对比"
        - "使用场景"
        - "代码示例"
  
  - id: news_001
    query: "2025年AI发展趋势"
    type: news
    expected:
      min_sources: 10
      max_age_days: 30
      must_cover:
        - "大模型"
        - "应用落地"
        - "行业影响"
        
metrics_thresholds:
  search:
    precision: 0.7
    recall: 0.6
    ndcg: 0.65
  report:
    completeness: 0.8
    citation_quality: 0.9
    structure_score: 0.7
  performance:
    total_time_max: 120  # 秒
    cost_max: 0.5  # 美元
```

### 6.3 持续监控仪表板

```python
# evaluation/monitor.py
"""
持续监控仪表板

监控内容:
1. 搜索成功率
2. 报告生成质量
3. API 调用延迟
4. 成本追踪
"""

import time
import json
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass, asdict

@dataclass
class MetricRecord:
    timestamp: str
    query_type: str
    search_results: int
    search_time: float
    analysis_time: float
    generation_time: float
    total_time: float
    token_usage: int
    cost: float
    quality_score: float
    errors: List[str]

class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, storage_path: str = "./metrics.jsonl"):
        self.storage_path = storage_path
        self.current_record = None
    
    def start_request(self, query_type: str):
        """开始请求"""
        self.current_record = {
            "timestamp": datetime.now().isoformat(),
            "query_type": query_type,
            "start_time": time.time(),
            "phases": {},
            "errors": []
        }
    
    def record_phase(self, phase: str, duration: float, **kwargs):
        """记录阶段"""
        self.current_record["phases"][phase] = {
            "duration": duration,
            **kwargs
        }
    
    def record_error(self, error: str):
        """记录错误"""
        self.current_record["errors"].append(error)
    
    def end_request(self, token_usage: int, cost: float, quality_score: float):
        """结束请求"""
        record = self.current_record
        record["total_time"] = time.time() - record["start_time"]
        record["token_usage"] = token_usage
        record["cost"] = cost
        record["quality_score"] = quality_score
        
        # 保存
        with open(self.storage_path, "a") as f:
            f.write(json.dumps(record) + "\n")
        
        return record
    
    def get_statistics(self, days: int = 7) -> Dict:
        """获取统计"""
        # 读取最近N天的数据
        records = []
        cutoff = datetime.now().timestamp() - days * 86400
        
        with open(self.storage_path, "r") as f:
            for line in f:
                try:
                    record = json.loads(line)
                    ts = datetime.fromisoformat(record["timestamp"]).timestamp()
                    if ts >= cutoff:
                        records.append(record)
                except Exception:
                    continue
        
        if not records:
            return {}
        
        return {
            "total_requests": len(records),
            "avg_total_time": sum(r["total_time"] for r in records) / len(records),
            "avg_quality_score": sum(r.get("quality_score", 0) for r in records) / len(records),
            "total_cost": sum(r.get("cost", 0) for r in records),
            "total_tokens": sum(r.get("token_usage", 0) for r in records),
            "error_rate": sum(1 for r in records if r.get("errors")) / len(records),
            "by_query_type": self._group_by_type(records)
        }
    
    def _group_by_type(self, records: List[Dict]) -> Dict:
        """按查询类型分组"""
        groups = {}
        for r in records:
            t = r.get("query_type", "unknown")
            if t not in groups:
                groups[t] = []
            groups[t].append(r)
        
        return {
            t: {
                "count": len(rs),
                "avg_time": sum(r["total_time"] for r in rs) / len(rs),
                "avg_quality": sum(r.get("quality_score", 0) for r in rs) / len(rs)
            }
            for t, rs in groups.items()
        }
```

---

## 七、优化优先级（修订版）

### 7.1 优先级矩阵

| 优化项 | 影响 | 工作量 | 依赖 | 优先级 |
|--------|------|--------|------|--------|
| **递归深度搜索** | ⭐⭐⭐⭐⭐ | 高 | 无 | P0 |
| **信息可信度评估** | ⭐⭐⭐⭐⭐ | 中 | 无 | P0 |
| **向量存储与语义检索** | ⭐⭐⭐⭐ | 中 | 无 | P0 |
| **LangGraph 高级特性** | ⭐⭐⭐⭐ | 中 | 无 | P1 |
| **错误处理与重试** | ⭐⭐⭐⭐ | 低 | 无 | P1 |
| **Token 成本优化** | ⭐⭐⭐ | 低 | 无 | P1 |
| **学术搜索集成** | ⭐⭐⭐ | 中 | 无 | P2 |
| **流式内容输出** | ⭐⭐⭐ | 中 | 无 | P2 |
| **ReAct 混合架构** | ⭐⭐⭐⭐ | 高 | P0 | P2 |
| **交互式追问** | ⭐⭐ | 中 | P2 | P3 |

### 7.2 实施路线图（修订）

```
Phase 0: 基础增强 (1周)
├── 错误处理与重试机制
├── Token 成本优化
└── 性能监控仪表板

Phase 1: 核心能力 (2-3周)
├── 递归深度搜索 (P0)
├── 信息可信度评估 (P0)
├── 向量存储集成 (P0)
└── LangGraph 条件分支与Checkpointing

Phase 2: 功能扩展 (2周)
├── 学术搜索集成 (Exa/arXiv)
├── 流式内容输出
├── 搜索源优先级管理
└── Validation Agent 增强

Phase 3: 架构升级 (2周)
├── ReAct 混合架构
├── 反思与自我纠正
├── 多模型协作
└── 知识图谱构建

Phase 4: 体验优化 (1周)
├── 交互式追问
├── 搜索进度可视化
├── 导出格式增强
└── 多语言支持
```

---

## 八、总结与行动清单

### 8.1 项目现状评估

| 维度 | 评分 | 说明 |
|------|------|------|
| **搜索能力** | ⭐⭐⭐☆☆ | 有分类搜索，但深度不足 |
| **分析能力** | ⭐⭐⭐☆☆ | 有并行解析，但无向量化 |
| **报告质量** | ⭐⭐⭐⭐☆ | 自适应输出较好，验证需增强 |
| **架构设计** | ⭐⭐⭐☆☆ | LangGraph 基础使用，高级特性未用 |
| **错误处理** | ⭐⭐☆☆☆ | 简单捕获，无重试和降级 |
| **性能优化** | ⭐⭐⭐☆☆ | 有并行，但无缓存和Token优化 |
| **扩展性** | ⭐⭐⭐⭐☆ | 模块化好，易于扩展 |
| **国内可用** | ⭐⭐⭐⭐⭐ | DuckDuckGo 无需翻墙 |

### 8.2 立即可行动项

#### 本周可完成 (低工作量高影响)

1. **添加错误重试机制** - 1天
2. **实现 Token 计数和优化** - 0.5天
3. **添加性能监控日志** - 0.5天
4. **优化搜索降级策略** - 1天

#### 下周可完成 (中等工作量)

1. **实现递归深度搜索** - 3天
2. **添加信息可信度评分** - 2天
3. **集成 Chroma 向量存储** - 2天
4. **LangGraph 条件分支** - 1天

#### 长期规划 (高工作量)

1. **ReAct 混合架构重构** - 1周
2. **知识图谱构建** - 2周
3. **多模型协作系统** - 2周

---

## 附录

### A. 参考资源

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [GPT-Researcher GitHub](https://github.com/assafelovic/gpt-researcher)
- [Tavily API Documentation](https://docs.tavily.com/)
- [Exa AI Documentation](https://docs.exa.ai/)
- [Chroma Documentation](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)

### B. 测试 Benchmark

见 `evaluation/benchmark.yaml`

### C. 监控仪表板

见 `evaluation/monitor.py`

---

*报告版本: V2.0*  
*生成时间: 2025-06-29*  
*项目版本: DeepFind Agent v1.0*