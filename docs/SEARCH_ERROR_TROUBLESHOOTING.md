# 搜索错误故障排查指南

**问题**: 前端显示"搜索错误"
**状态**: 正在排查
**更新时间**: 2026-06-30

---

## 🔍 已确认的事实

### ✅ 后端工作正常
- API 健康检查: ✅ 正常
- DeepSeek API Key: ✅ 已配置
- Tavily API Key: ✅ 已配置
- CORS 配置: ✅ 正确
- SSE 流式响应: ✅ 可以返回事件

### ❓ 需要确认的问题
1. **具体的错误消息**是什么？
2. **浏览器控制台**有什么错误？
3. **网络请求**是否成功？
4. **SSE 连接**是否保持打开？

---

## 🧪 诊断步骤

### 步骤 1: 检查浏览器控制台

请在浏览器中：
1. 按 `F12` 或 `Cmd+Option+I` 打开开发者工具
2. 切换到 **Console（控制台）** 标签
3. 重新执行一次搜索
4. **截图或复制所有错误消息**发送给我

### 步骤 2: 检查网络请求

在开发者工具中：
1. 切换到 **Network（网络）** 标签
2. 勾选 **"Preserve log"（保留日志）**
3. 重新执行一次搜索
4. 找到 `stream?query=...` 请求
5. **检查**：
   - 状态码是什么？（应该是 200）
   - Response（响应）标签显示什么？
   - 是否有 EventStream 内容？

### 步骤 3: 测试简单的 API 调用

在浏览器新标签页中，直接访问：
```
https://deepfind-agent.onrender.com/api/research/stream?query=test&model=deepseek-chat
```

观察：
- 是否开始流式返回数据？
- 是否有错误？

---

## 🚨 可能的原因

### 原因 1: Render 冷启动超时
**症状**: 首次请求需要 30-60 秒
**解决**:
- 等待更长时间（最多 2 分钟）
- 或者付费升级 Render（$7/月，无冷启动）

### 原因 2: 模型参数错误
**症状**: 前端发送了错误的 model 参数
**检查**:
```typescript
// 前端应该发送:
model=deepseek-reasoner  // 或
model=deepseek-chat
```

### 原因 3: EventSource 超时
**症状**: 连接在得到响应前关闭
**解决**:
- 增加前端超时时间
- 添加错误重试逻辑

### 原因 4: DeepSeek API 问题
**症状**: API Key 有效但请求失败
**检查**:
- DeepSeek API 额度是否用完？
- 是否有速率限制？

---

## 🔧 临时解决方案

### 方案 A: 添加详细日志

在前端代码中添加日志：

```typescript
// 找到 handleSendMessage 函数中的 EventSource 创建部分
const eventSource = new EventSource(`${API_BASE_URL}/api/research/stream?query=${encodeURIComponent(query)}&model=${model}`);

// 添加日志
console.log('Creating EventSource with URL:', `${API_BASE_URL}/api/research/stream?query=${encodeURIComponent(query)}&model=${model}`);

eventSource.onopen = () => {
  console.log('EventSource connection opened');
};

eventSource.onerror = (error) => {
  console.error('EventSource error:', error);
  console.error('EventSource readyState:', eventSource.readyState);
  // ... 原有错误处理
};
```

### 方案 B: 测试不同的模型

尝试使用 `deepseek-chat` 而不是 `deepseek-reasoner`：
- `deepseek-chat`: 更快，更适合简单查询
- `deepseek-reasoner`: 更深度的分析，但更慢

### 方案 C: 检查 Render 日志

1. 打开 Render Dashboard: https://dashboard.render.com
2. 选择 `deepfind-agent` 服务
3. 点击 **Logs** 标签
4. 执行一次搜索
5. 查看后端日志输出

---

## 📊 需要您提供的信息

为了准确定位问题，请提供：

1. **浏览器控制台的完整错误信息**
   - 截图或复制文本

2. **网络请求详情**
   - `stream` 请求的状态码
   - 响应内容的前几行

3. **测试结果**
   - 直接访问 API URL 的结果
   - 是否能看到流式数据？

4. **之前本地遇到的问题**
   - 具体是什么错误？
   - 当时如何解决的？

---

## 🎯 快速测试命令

打开浏览器开发者工具的 Console，粘贴并运行：

```javascript
// 测试 1: 检查 API 连接
fetch('https://deepfind-agent.onrender.com/health')
  .then(r => r.json())
  .then(d => console.log('✅ API 连接成功:', d))
  .catch(e => console.error('❌ API 连接失败:', e));

// 测试 2: 简单的 SSE 测试
const testES = new EventSource('https://deepfind-agent.onrender.com/api/research/stream?query=test&model=deepseek-chat');
testES.onopen = () => console.log('✅ SSE 连接已打开');
testES.onmessage = (e) => console.log('📨 收到消息:', e.data.substring(0, 100));
testES.onerror = (e) => {
  console.error('❌ SSE 错误:', e);
  console.log('ReadyState:', testES.readyState);
  testES.close();
};
```

运行后，将控制台输出发送给我。

---

## 🔍 代码检查点

### 前端代码位置
- 文件: `frontend/src/pages/Index.tsx`
- 函数: `handleSendMessage`
- 行号: ~321 (EventSource 创建)

### 后端代码位置
- 文件: `api.py`
- 端点: `/api/research/stream`
- 行号: ~464

---

## ⏭️ 下一步

**请立即执行：**

1. ✅ 打开浏览器开发者工具（F12 或 Cmd+Option+I）
2. ✅ 切换到 Console 标签
3. ✅ 执行一次搜索
4. ✅ 复制所有错误信息发给我

**或者执行快速测试：**
5. ✅ 在开发者工具 Console 中运行上面的测试代码
6. ✅ 复制输出结果发给我

**有了这些信息，我就能精确定位问题！** 🎯