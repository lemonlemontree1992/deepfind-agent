# 🎯 GLM-5.2 多模型支持 - 完整实施方案

## 📋 需求确认

✅ **保留 DeepSeek 模型**（不变）
✅ **增加 GLM-5.2 模型**（新增）  
✅ **用户可选择模型**（前端下拉选择）  
✅ **动态切换模型**（无需重启服务）

---

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────┐
│                   前端界面                       │
│  ┌───────────────────────────────────────────┐  │
│  │  AI 模型: [ DeepSeek ▼ ]                 │  │
│  │  - DeepSeek (推理强，推荐)               │  │
│  │  - GLM-5.2  (速度快，便宜)               │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
                      ↓ API 调用
┌─────────────────────────────────────────────────┐
│                  后端 API                        │
│  POST /api/settings { llmProvider: "glm" }     │
│  POST /api/chat    { query: "...", model: "glm"}│
└─────────────────────────────────────────────────┘
                      ↓ 
┌─────────────────────────────────────────────────┐
│              统一 LLM 客户端                     │
│  get_llm(provider="deepseek") → DeepSeek        │
│  get_llm(provider="glm")       → ChatZhipuAI    │
└─────────────────────────────────────────────────┘
```

---

## 📦 交付清单

### 📄 完整文档（5份）

| 文档 | 用途 | 阅读时间 |
|------|------|---------|
| `glm-multi-model-support.md` | 完整技术方案 | 10分钟 |
| `frontend-model-selector.md` | 前端集成指南 | 5分钟 |
| `glm-code-checklist.md` | 代码修改清单 | 5分钟 |
| `glm-integration-plan.md` | 详细实施步骤 | 15分钟 |
| **本文档** | 快速实施指南 | 3分钟 |

### 🔧 脚本工具（3个）

| 脚本 | 用途 |
|------|------|
| `scripts/integrate_glm.sh` | 环境准备脚本 |
| `scripts/verify_glm_integration.sh` | 验证检查脚本 |
| `test_llm_providers.py` | 模型测试脚本 |

---

## 🚀 快速实施（3步骤）

### 步骤 1: 准备环境（5分钟）

```bash
# 1. 安装依赖
pip install zhipuai>=2.0.0

# 2. 配置 GLM API Key
cat >> .env << 'EOF'
# 智谱 GLM 配置
GLM_API_KEY=your_actual_api_key_here
GLM_MODEL=glm-5.2
EOF

# 3. 验证配置
python -c "from config import settings; print(f'GLM API Key: {settings.glm_api_key[:20]}...')"
```

### 步骤 2: 修改代码（按优先级）

#### 2.1 配置文件（5分钟）

**`config/settings.py`** - 添加 GLM 配置项

```python
# 在 Settings 类中添加
glm_api_key: str = ""
glm_model: str = "glm-5.2"
llm_provider: Literal["deepseek", "glm"] = "deepseek"

# 在 __init__ 方法中添加
self.glm_api_key = os.getenv("GLM_API_KEY", "")
glm_model_env = os.getenv("GLM_MODEL")
if glm_model_env:
    self.glm_model = glm_model_env

provider_env = os.getenv("DEFAULT_LLM_PROVIDER")
if provider_env in ("deepseek", "glm"):
    self.llm_provider = provider_env
```

#### 2.2 LLM 客户端（15分钟）

**`utils/llm_client.py`** - 支持双模型

```python
def create_llm_instance(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
):
    """创建 LLM 实例（支持多模型）"""
    provider = provider or settings.llm_provider
    
    if provider == "glm":
        from langchain_community.chat_models import ChatZhipuAI
        model = model or settings.glm_model
        return ChatZhipuAI(
            model=model,
            temperature=temperature,
            zhipuai_api_key=settings.glm_api_key,
        )
    else:  # deepseek
        from langchain_deepseek import ChatDeepSeek
        model = model or settings.deepseek_model
        return ChatDeepSeek(
            model=model,
            temperature=temperature,
            api_key=settings.deepseek_api_key,
        )


def get_llm(
    model: Optional[str] = None,
    temperature: float = 0.7,
    use_rate_limit: bool = True,
    provider: Optional[str] = None,  # 新增：提供商参数
) -> RateLimitedLLM:
    """获取 LLM 客户端（支持模型选择）"""
    provider = provider or settings.llm_provider
    model = model or (settings.glm_model if provider == "glm" else settings.deepseek_model)
    
    cache_key = f"{provider}_{model}_{temperature}_{use_rate_limit}"
    
    if cache_key not in _llm_cache:
        llm_instance = create_llm_instance(provider, model, temperature)
        
        if use_rate_limit:
            _llm_cache[cache_key] = RateLimitedLLM(
                llm_instance=llm_instance,
                provider=provider,
                model=model,
            )
        else:
            _llm_cache[cache_key] = llm_instance
    
    return _llm_cache[cache_key]
```

#### 2.3 API 接口（10分钟）

**`api.py`** - 添加模型切换接口

```python
from pydantic import BaseModel
from typing import Literal, Optional

class SettingsUpdate(BaseModel):
    llmProvider: Optional[Literal["deepseek", "glm"]] = None

class ChatRequest(BaseModel):
    query: str
    model: Optional[Literal["deepseek", "glm"]] = None

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
                "description": "推理能力强，适合复杂研究和深度分析"
            },
            "glm": {
                "name": "GLM-5.2",
                "model": settings.glm_model,
                "configured": bool(settings.glm_api_key),
                "description": "响应速度快，成本低，适合日常查询"
            }
        }
    }

@app.post("/api/settings")
async def update_settings(settings_update: SettingsUpdate):
    """更新运行时设置"""
    if settings_update.llmProvider:
        provider = settings_update.llmProvider
        if provider in ("deepseek", "glm"):
            # 检查 API Key
            if provider == "glm" and not settings.glm_api_key:
                raise HTTPException(
                    status_code=400,
                    detail="GLM API Key 未配置"
                )
            
            settings.llm_provider = provider
            
            # 清除缓存
            from utils.llm_client import _llm_cache
            _llm_cache.clear()
            
            return {
                "success": True,
                "llmProvider": provider,
                "message": f"已切换到 {provider.upper()} 模型"
            }
    
    return {"success": False}

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """处理聊天请求（支持模型选择）"""
    provider = request.model or settings.llm_provider
    
    result = await run_agent(
        query=request.query,
        llm_provider=provider
    )
    return result
```

#### 2.4 Agent 修改（15分钟）

**所有 Agent 文件** - 支持 provider 参数

```python
# agents/search_agent.py
# agents/analyze_agent.py
# agents/extraction_agent.py
# agents/report_agent.py
# agents/task_planner.py
# agents/enhanced_report_agent.py

# 在 State 中添加
class SearchState(TypedDict):
    query: str
    llm_provider: Optional[str]  # 新增
    # ... 其他字段

# 在调用 get_llm 时传递 provider
def some_function(state: SearchState):
    llm_provider = state.get("llm_provider")
    llm = get_llm(provider=llm_provider, temperature=0.3)
    # ...
```

### 步骤 3: 前端集成（20分钟）

#### 3.1 创建模型选择组件

**`frontend/src/components/ModelSelector.tsx`**

```tsx
import { useState, useEffect } from 'react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Sparkles, Zap, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

export function ModelSelector({ className = '' }) {
  const [currentModel, setCurrentModel] = useState('deepseek');
  const [models, setModels] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetch('/api/settings')
      .then(res => res.json())
      .then(data => {
        setCurrentModel(data.llmProvider);
        setModels(data.availableProviders);
      });
  }, []);

  const handleChange = async (value) => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ llmProvider: value }),
      });
      
      const data = await response.json();
      if (data.success) {
        setCurrentModel(value);
        toast.success(data.message);
      }
    } catch (error) {
      toast.error('切换失败');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <label className="text-sm">AI 模型:</label>
      <Select value={currentModel} onValueChange={handleChange} disabled={isLoading}>
        <SelectTrigger className="w-[180px]">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="deepseek">
            <div className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-blue-500" />
              <span>DeepSeek</span>
            </div>
          </SelectItem>
          <SelectItem value="glm" disabled={!models.glm?.configured}>
            <div className="flex items-center gap-2">
              <Zap className="h-4 w-4 text-green-500" />
              <span>GLM-5.2</span>
            </div>
          </SelectItem>
        </SelectContent>
      </Select>
      {isLoading && <Loader2 className="h-4 w-4 animate-spin" />}
    </div>
  );
}
```

#### 3.2 集成到主界面

**`frontend/src/pages/Index.tsx`**

```tsx
import { ModelSelector } from '@/components/ModelSelector';

// 在页面顶部工具栏添加
<div className="flex items-center justify-between mb-4">
  <h1 className="text-2xl font-bold">🔍 DeepFind Agent</h1>
  <ModelSelector />
</div>
```

---

## ✅ 测试验证

### 测试 1: 后端 API

```bash
# 获取当前设置
curl http://localhost:8000/api/settings

# 切换到 GLM
curl -X POST http://localhost:8000/api/settings \
  -H "Content-Type: application/json" \
  -d '{"llmProvider": "glm"}'

# 切换回 DeepSeek
curl -X POST http://localhost:8000/api/settings \
  -H "Content-Type: application/json" \
  -d '{"llmProvider": "deepseek"}'
```

### 测试 2: 前端界面

1. 访问 http://localhost:3000
2. 查看模型选择下拉框
3. 切换模型并验证提示
4. 发送查询验证使用正确模型

### 测试 3: 模型调用

```bash
# 运行测试脚本
python test_llm_providers.py

# 预期输出
✅ DeepSeek 响应成功
✅ GLM 响应成功
```

---

## 📊 完整文件清单

### 需要修改的文件

| 文件 | 修改量 | 说明 |
|------|--------|------|
| `config/settings.py` | +30行 | 添加 GLM 配置 |
| `utils/llm_client.py` | 重构 | 支持双模型 |
| `api.py` | +50行 | 添加 API 接口 |
| `agents/search_agent.py` | +5行 | 支持 provider |
| `agents/analyze_agent.py` | +5行 | 支持 provider |
| `agents/extraction_agent.py` | +5行 | 支持 provider |
| `agents/report_agent.py` | +5行 | 支持 provider |
| `agents/task_planner.py` | +5行 | 支持 provider |
| `frontend/src/components/ModelSelector.tsx` | 新建 | 模型选择组件 |
| `frontend/src/pages/Index.tsx` | +10行 | 集成组件 |

### 需要添加的文件

| 文件 | 说明 |
|------|------|
| `test_llm_providers.py` | 模型测试脚本 |

### 需要修改的配置

| 文件 | 修改内容 |
|------|----------|
| `.env` | 添加 GLM_API_KEY 等 |
| `requirements.txt` | 添加 zhipuai |

---

## 🎯 预期效果

### 用户视角

```
┌──────────────────────────────────────────┐
│  🔍 DeepFind Agent                       │
│                                          │
│  AI 模型: [ DeepSeek (推荐) ▼ ]         │
│           ┌─────────────────────────┐    │
│           │ DeepSeek (推荐)         │    │
│           │ GLM-5.2 (快速)          │    │
│           └─────────────────────────┘    │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │ 请输入您的调研主题...               │ │
│  └────────────────────────────────────┘ │
│                                          │
│  [发送]                                  │
└──────────────────────────────────────────┘
```

### 实现功能

✅ **前端下拉选择**：清晰展示两个模型选项  
✅ **动态切换**：无需重启服务，立即生效  
✅ **状态反馈**：显示当前模型，切换成功提示  
✅ **未配置提示**：未配置 API Key 的模型显示禁用  
✅ **后端支持**：完整 API 接口支持模型选择  

---

## ⏱️ 时间估算

| 步骤 | 时间 |
|------|------|
| 环境准备 | 5分钟 |
| 配置文件修改 | 5分钟 |
| 核心代码修改 | 30分钟 |
| 前端组件开发 | 20分钟 |
| 测试验证 | 10分钟 |
| **总计** | **70分钟** |

---

## 📞 后续支持

如遇到问题，请查看：

1. **完整方案**: `docs/glm-multi-model-support.md`
2. **前端集成**: `docs/frontend-model-selector.md`
3. **代码清单**: `docs/glm-code-checklist.md`
4. **测试脚本**: `python test_llm_providers.py`
5. **验证脚本**: `./scripts/verify_glm_integration.sh`

---

**版本**: V1.0  
**创建时间**: 2026-06-29  
**适用版本**: DeepFind Agent V2.0+