# DeepSeek API 速率限制修复说明

**修复时间**: 2026-06-29  
**问题**: API Error: 429 - 模型全局请求额度超限(并发限流)

---

## 问题原因

DeepSeek API 有并发限制，当短时间内发送多个请求时会触发 429 错误。之前的代码中，每个 Agent 调用都会创建新的 LLM 实例并发送请求，没有速率限制和重试机制。

---

## 修复方案

### 1. 创建统一的 LLM 客户端 (`utils/llm_client.py`)

新增 `RateLimitedLLM` 类，包含以下特性：

- **速率限制**: 最小请求间隔 1 秒
- **自动重试**: 遇到 429 错误时最多重试 3 次
- **指数退避**: 等待时间递增（3s → 5s → 9s）
- **实例缓存**: 避免重复创建相同的 LLM 实例

```python
# 使用示例
from utils.llm_client import get_llm

# 获取带速率限制的 LLM 客户端
llm = get_llm(model="deepseek-chat", temperature=0.7)

# 正常调用（自动处理速率限制）
response = llm.invoke(messages)
```

### 2. 更新的文件

已更新以下 Agent 文件使用新的客户端：

- ✅ `agents/report_agent.py` - 报告生成
- ✅ `agents/analyze_agent.py` - 搜索分析
- ✅ `agents/extraction_agent.py` - 实体提取

---

## 修复效果

### 修复前
```
❌ 短时间内多个并发请求
❌ 遇到 429 直接失败
❌ 无重试机制
❌ 无请求间隔控制
```

### 修复后
```
✅ 控制请求速率（最小 1 秒间隔）
✅ 自动重试（最多 3 次）
✅ 指数退避（避免频繁重试）
✅ 统一的 LLM 实例管理
```

---

## 启动服务

### 方式 1: Streamlit Web 界面

```bash
streamlit run app.py
```

访问: http://localhost:8501

### 方式 2: FastAPI 后端

如果需要 FastAPI 后端：

```bash
# 安装依赖
pip install fastapi uvicorn sse-starlette

# 启动服务
python api.py
```

访问: http://localhost:8000

---

## 测试修复

修复后，429 错误会被自动处理：

```python
# 遇到速率限制时的日志
2026-06-29 19:35:12 - WARNING - 遇到速率限制 (429)，等待 3 秒后重试 (尝试 1/3)
2026-06-29 19:35:15 - INFO - 重试成功
```

如果仍然遇到 429 错误，可以调整参数：

```python
# 增加最小间隔到 2 秒
get_llm(model="deepseek-chat", min_interval=2.0)

# 增加最大重试次数到 5 次
get_llm(model="deepseek-chat", max_retries=5)
```

---

## 双方案模板集成

同时完成了旅行攻略双方案模板的集成：

- ✅ `prompts/adaptive_prompts.py` - 新增 `TRAVEL_GUIDE_PERFECT_PROMPT`
- ✅ `agents/report_agent.py` - 自动检测旅行查询并使用新模板

新模板包含：
- 方案A：经典必游路线（适合第一次来访）
- 方案B：深度体验路线（适合二次来访）
- 详细章节：行前准备、住宿选择、预算参考、实用提示

---

*修复版本: V1.1*  
*修复日期: 2026-06-29*