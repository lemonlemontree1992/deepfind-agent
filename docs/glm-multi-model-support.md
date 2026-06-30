# GLM-5.2 多模型支持方案（扩展版）

## 📋 方案说明

**目标**：在现有 DeepSeek 模型基础上，增加 GLM-5.2 作为可选模型，让用户可以灵活选择。

**核心原则**：
- ✅ 保留 DeepSeek 作为默认模型
- ✅ 增加 GLM-5.2 作为备选模型
- ✅ 用户可以自由切换模型
- ✅ 不破坏现有功能

---

## 🎯 用户选择模型的方式

### 方式 1：环境变量切换（后端配置）

```bash
# .env 文件
DEFAULT_LLM_PROVIDER=deepseek  # 默认使用 DeepSeek
# DEFAULT_LLM_PROVIDER=glm     # 或切换为 GLM
```

### 方式 2：前端界面选择（推荐）

```
┌─────────────────────────────────────┐
│  🔍 DeepFind Agent                  │
│                                     │
│  [对话界面]                         │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ 请输入您的调研主题...        │   │
│  └─────────────────────────────┘   │
│                                     │
│  ⚙️ 模型设置                        │
│  ┌──────────────────────────────┐  │
│  │ ○ DeepSeek（推荐，推理强）   │  │
│  │ ● GLM-5.2（速度快，成本低）  │  │
│  └──────────────────────────────┘  │
│                                     │
│  [发送]                            │
└─────────────────────────────────────┘
```

### 方式 3：API 参数传递

```python
# 通过 API 请求参数指定模型
POST /api/chat
{
  "query": "纽约4天3晚旅行攻略",
  "model": "glm"  # 或 "deepseek"
}
```

---

## 🏗️ 技术架构设计

### 1. 配置层：支持双模型配置

**`.env` 配置文件**
```bash
# ========== DeepSeek 配置（默认） ==========
DEEPSEEK_API_KEY=sk-xxxxx
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_REASONER_MODEL=deepseek-reasoner

# ========== 智谱 GLM 配置 ==========
GLM_API_KEY=your_glm_api_key_here
GLM_MODEL=glm-5.2

# ========== 默认模型选择 ==========
DEFAULT_LLM_PROVIDER=deepseek
```

**`config/settings.py` 配置类**
```python
class Settings(BaseSettings):
    # DeepSeek 配置
    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-chat"
    
    # GLM 配置
    glm_api_key: str = ""
    glm_model: str = "glm-5.2"
    
    # 默认提供商
    llm_provider: Literal["deepseek", "glm"] = "deepseek"
```

---

### 2. 核心层：模型选择器

**`utils/llm_client.py` 核心逻辑**

```python
def get_llm(
    model: Optional[str] = None,
    provider: Optional[str] = None,  # 新增：提供商参数
    temperature: float = 0.7,
    use_rate_limit: bool = True,
) -> RateLimitedLLM:
    """
    获取 LLM 客户端实例（支持多模型选择）
    
    Args:
        model: 指定模型名称（可选）
        provider: 指定提供商 "deepseek" 或 "glm"（可选，默认使用配置）
        temperature: 温度参数
        use_rate_limit: 是否使用速率限制
    
    Returns:
        LLM 客户端实例
    """
    # 优先级：provider参数 > 配置文件的llm_provider
    provider = provider or settings.llm_provider
    
    # 根据提供商选择默认模型
    if not model:
        if provider == "glm":
            model = settings.glm_model
        else:
            model = settings.deepseek_model
    
    cache_key = f"{provider}_{model}_{temperature}_{use_rate_limit}"
    
    if cache_key not in _llm_cache:
        # 根据提供商创建对应的 LLM 实例
        if provider == "glm":
            from langchain_community.chat_models import ChatZhipuAI
            llm_instance = ChatZhipuAI(
                model=model,
                temperature=temperature,
                zhipuai_api_key=settings.glm_api_key,
            )
        else:  # deepseek
            from langchain_deepseek import ChatDeepSeek
            llm_instance = ChatDeepSeek(
                model=model,
                temperature=temperature,
                api_key=settings.deepseek_api_key,
            )
        
        # 包装为速率限制客户端
        if use_rate_limit:
            _llm_cache[cache_key] = RateLimitedLLM(
                llm_instance=llm_instance,
                provider=provider,
                model=model,
            )
        else:
            _llm_cache[cache_key] = llm_instance
    
    return _llm_cache[cache_key]


class RateLimitedLLM:
    """带速率限制的 LLM 客户端（支持多模型）"""
    
    def __init__(
        self,
        llm_instance,  # LLM 实例
        provider: str,
        model: str,
        max_retries: int = 3,
        min_interval: float = 1.0,
    ):
        self.llm = llm_instance
        self.provider = provider
        self.model = model
        self.max_retries = max_retries
        self.min_interval = min_interval
        self._last_request_time = 0
        
        logger.info(f"初始化 LLM 客户端: {provider}/{model}")
```

---

### 3. API 层：支持动态切换

**`api.py` 新增端点**

```python
from pydantic import BaseModel
from typing import Literal

class ChatRequest(BaseModel):
    query: str
    model: Optional[Literal["deepseek", "glm"]] = None  # 可选模型参数

class SettingsUpdate(BaseModel):
    llmProvider: Optional[Literal["deepseek", "glm"]] = None

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """处理聊天请求（支持模型选择）"""
    # 使用请求中的模型参数，或使用默认配置
    provider = request.model or settings.llm_provider
    
    # 传递给下游 agent
    result = await run_agent(
        query=request.query,
        llm_provider=provider  # 传递模型提供商
    )
    return result

@app.post("/api/settings")
async def update_settings(settings_update: SettingsUpdate):
    """更新运行时设置"""
    global settings
    
    if settings_update.llmProvider:
        provider = settings_update.llmProvider
        if provider in ("deepseek", "glm"):
            # 检查对应模型的 API Key 是否配置
            if provider == "glm" and not settings.glm_api_key:
                raise HTTPException(
                    status_code=400,
                    detail="GLM API Key 未配置，请先在 .env 中设置 GLM_API_KEY"
                )
            
            settings.llm_provider = provider
            
            # 清除 LLM 缓存，使用新模型
            from utils.llm_client import _llm_cache
            _llm_cache.clear()
            
            logger.info(f"模型切换为: {provider}")
            return {
                "success": True,
                "llmProvider": provider,
                "message": f"已切换到 {provider.upper()} 模型"
            }
    
    return {"success": False}

@app.get("/api/settings")
async def get_settings():
    """获取当前设置"""
    return {
        "llmProvider": settings.llm_provider,
        "availableProviders": {
            "deepseek": {
                "name": "DeepSeek",
                "model": settings.deepseek_model,
                "configured": bool(settings.deepseek_api_key),
                "description": "推理能力强，适合复杂任务"
            },
            "glm": {
                "name": "GLM-5.2",
                "model": settings.glm_model,
                "configured": bool(settings.glm_api_key),
                "description": "速度快，成本低，适合快速响应"
            }
        }
    }
```

---

### 4. Agent 层：支持模型参数传递

**修改所有 Agent，增加 llm_provider 参数**

**`agents/search_agent.py`**
```python
def generate_search_queries(state: SearchState) -> Dict[str, Any]:
    """生成搜索查询词"""
    query = state["query"]
    llm_provider = state.get("llm_provider")  # 从状态中获取
    
    try:
        # 使用指定的模型提供商
        llm = get_llm(
            provider=llm_provider,  # 传递提供商参数
            temperature=0.3
        )
        
        # ... 后续逻辑
```

**主入口修改**
```python
async def run_agent(
    query: str,
    llm_provider: Optional[str] = None  # 新增参数
):
    """运行 Agent（支持模型选择）"""
    # 初始化状态时传递 llm_provider
    initial_state = {
        "query": query,
        "llm_provider": llm_provider or settings.llm_provider,
        # ... 其他状态
    }
    
    # 运行 workflow
    result = await workflow.ainvoke(initial_state)
    return result
```

---

### 5. 前端层：模型选择 UI

**`frontend/src/contexts/SettingsContext.tsx`**

```typescript
export interface Settings {
  llmProvider: 'deepseek' | 'glm';
  // ... 其他设置
}

export function SettingsProvider({ children }: { children: React.ReactNode }) {
  const [settings, setSettings] = useState<Settings>({
    llmProvider: 'deepseek',
    // ...
  });

  // 初始化时获取设置
  useEffect(() => {
    fetch('/api/settings')
      .then(res => res.json())
      .then(data => {
        setSettings(prev => ({
          ...prev,
          llmProvider: data.llmProvider
        }));
      });
  }, []);

  // 切换模型
  const setLLMProvider = async (provider: 'deepseek' | 'glm') => {
    try {
      const response = await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ llmProvider: provider }),
      });
      
      if (response.ok) {
        setSettings(prev => ({ ...prev, llmProvider: provider }));
        toast.success(`已切换到 ${provider.toUpperCase()} 模型`);
      }
    } catch (error) {
      toast.error('模型切换失败');
    }
  };

  return (
    <SettingsContext.Provider value={{ settings, setLLMProvider }}>
      {children}
    </SettingsContext.Provider>
  );
}
```

**前端界面组件**

```tsx
// frontend/src/components/ModelSelector.tsx
import { useState } from 'react';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { useSettings } from '@/contexts/SettingsContext';
import { Sparkles, Zap } from 'lucide-react';

export function ModelSelector() {
  const { settings, setLLMProvider } = useSettings();
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = async (value: 'deepseek' | 'glm') => {
    setIsLoading(true);
    await setLLMProvider(value);
    setIsLoading(false);
  };

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-medium">AI 模型选择</h3>
      
      <RadioGroup
        value={settings.llmProvider}
        onValueChange={handleChange}
        disabled={isLoading}
      >
        <div className="flex items-start space-x-3 p-3 rounded-lg border hover:bg-accent cursor-pointer">
          <RadioGroupItem value="deepseek" id="deepseek" />
          <div className="flex-1">
            <Label htmlFor="deepseek" className="flex items-center gap-2 cursor-pointer">
              <Sparkles className="h-4 w-4" />
              <span className="font-medium">DeepSeek</span>
              <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">
                推荐
              </span>
            </Label>
            <p className="text-xs text-muted-foreground mt-1">
              推理能力强，适合复杂研究和深度分析
            </p>
          </div>
        </div>

        <div className="flex items-start space-x-3 p-3 rounded-lg border hover:bg-accent cursor-pointer">
          <RadioGroupItem value="glm" id="glm" />
          <div className="flex-1">
            <Label htmlFor="glm" className="flex items-center gap-2 cursor-pointer">
              <Zap className="h-4 w-4" />
              <span className="font-medium">GLM-5.2</span>
              <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded">
                快速
              </span>
            </Label>
            <p className="text-xs text-muted-foreground mt-1">
              响应速度快，成本低，适合日常查询
            </p>
          </div>
        </div>
      </RadioGroup>
      
      {isLoading && (
        <p className="text-xs text-muted-foreground">切换中...</p>
      )}
    </div>
  );
}
```

---

## 📊 对比优势

| 特性 | DeepSeek | GLM-5.2 |
|------|----------|---------|
| **推理能力** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **响应速度** | 2-5秒 | 0.5-2秒 ⚡ |
| **成本** | ¥1/百万token | ¥0.1/百万token 💰 |
| **复杂任务** | ✅ 更优 | ✅ 良好 |
| **简单查询** | ✅ 可用 | ✅ 更优 |
| **中文能力** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**推荐使用场景**：
- **DeepSeek**：深度研究、复杂分析、学术调研
- **GLM-5.2**：日常查询、快速问答、大量并发请求

---

## 🔄 使用流程

### 用户视角

1. **打开界面** → 看到"模型设置"
2. **选择模型** → DeepSeek 或 GLM-5.2
3. **输入查询** → 系统使用选定模型处理
4. **实时切换** → 可随时更换模型

### 系统视角

```
用户请求 → 检查模型选择 → 调用对应模型 API → 返回结果
    ↓            ↓                ↓
  前端     API/settings      LLM Client
           ↓                ↓
      更新配置          清除缓存
```

---

## 📝 实施步骤

### 第一步：准备工作（5分钟）

```bash
# 1. 安装依赖
pip install zhipuai>=2.0.0

# 2. 配置 API Key
echo "
# 智谱 GLM 配置
GLM_API_KEY=your_glm_api_key_here
GLM_MODEL=glm-5.2
" >> .env

# 3. 验证配置
python -c "from config import settings; print(f'GLM configured: {bool(settings.glm_api_key)}')"
```

### 第二步：修改代码（30分钟）

按照以下顺序修改：

1. **config/settings.py** - 添加 GLM 配置项（5分钟）
2. **utils/llm_client.py** - 重构支持多模型（10分钟）
3. **api.py** - 添加模型切换接口（5分钟）
4. **agents/*.py** - 支持 llm_provider 参数（10分钟）
5. **前端** - 添加模型选择 UI（可选，10分钟）

### 第三步：测试验证（10分钟）

```bash
# 1. 测试 DeepSeek
curl -X POST http://localhost:8000/api/settings \
  -H "Content-Type: application/json" \
  -d '{"llmProvider": "deepseek"}'

# 2. 测试 GLM
curl -X POST http://localhost:8000/api/settings \
  -H "Content-Type: application/json" \
  -d '{"llmProvider": "glm"}'

# 3. 验证查询
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "纽约旅行攻略", "model": "glm"}'
```

---

## 🎉 优势总结

### 对用户

- ✅ 可以根据需求选择合适的模型
- ✅ DeepSeek 处理复杂任务，GLM 快速响应简单问题
- ✅ 可以根据成本和速度灵活调整
- ✅ 无需修改代码，界面一键切换

### 对系统

- ✅ 保持 DeepSeek 的强大能力
- ✅ 增加 GLM 的成本优势
- ✅ 提供备用方案，提高可用性
- ✅ 架构灵活，易于扩展更多模型

---

**版本**: V2.0（多模型支持版）
**创建时间**: 2026-06-29
**预计实施时间**: 45-60 分钟