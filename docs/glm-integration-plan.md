# GLM-5.2 模型集成方案

## 📋 方案概述

### 目标
在 DeepFind Agent 中支持 GLM-5.2 模型切换，实现：
- ✅ 灵活切换 DeepSeek 和 GLM-5.2 模型
- ✅ 保持现有功能不变
- ✅ 支持模型级别的速率限制
- ✅ 统一的模型调用接口

### 背景
当前系统使用 DeepSeek 模型（deepseek-chat 和 deepseek-reasoner），需要支持 GLM-5.2 作为备选模型。

---

## 🔍 当前架构分析

### 1. 模型使用情况

**已抽象的调用**（使用 `get_llm` 统一接口）：
- `agents/extraction_agent.py` - 实体提取
- `agents/analyze_agent.py` - 内容分析
- `agents/report_agent.py` - 报告生成

**未抽象的调用**（直接使用 `ChatDeepSeek`）：
- `agents/search_agent.py` - 搜索词生成
- `agents/task_planner.py` - 任务规划
- `agents/enhanced_report_agent.py` - 增强报告生成

### 2. 配置管理
- `config/settings.py` - 模型配置
- `utils/llm_client.py` - 统一 LLM 客户端

---

## 🎯 实施方案

### 阶段一：环境准备

#### 1.1 安装依赖

```bash
# 安装智谱 AI SDK
pip install zhipuai

# 或添加到 requirements.txt
zhipuai>=2.0.0
```

#### 1.2 添加环境变量

编辑 `.env` 文件：

```bash
# ========== DeepSeek 配置 ==========
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxx
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_REASONER_MODEL=deepseek-reasoner

# ========== 智谱 GLM 配置 ==========
GLM_API_KEY=your_glm_api_key_here
GLM_MODEL=glm-5.2  # 或 glm-4-plus

# ========== 模型选择 ==========
# 可选值: deepseek | glm
DEFAULT_LLM_PROVIDER=deepseek
```

---

### 阶段二：核心代码改造

#### 2.1 更新配置文件

**文件**: `config/settings.py`

```python
"""配置管理模块"""

import os
from typing import Literal, Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """应用配置"""

    # ========== DeepSeek 配置 ==========
    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-chat"
    deepseek_reasoner_model: str = "deepseek-reasoner"
    
    # ========== 智谱 GLM 配置 ==========
    glm_api_key: str = ""
    glm_model: str = "glm-5.2"
    glm_temperature: float = 0.7
    
    # ========== 模型提供商选择 ==========
    llm_provider: Literal["deepseek", "glm"] = "deepseek"
    
    # ========== 其他配置 ==========
    brave_search_api_key: str = ""
    search_depth: Literal["shallow", "deep"] = "deep"
    max_search_results: int = 10
    default_language: Literal["zh", "en"] = "zh"
    report_mode: Literal["basic", "enhanced"] = "basic"
    report_max_sources: int = 8
    jina_reader_timeout: int = 15
    playwright_timeout: int = 20000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # ========== DeepSeek ==========
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "")
        
        deepseek_model_env = os.getenv("DEEPSEEK_MODEL")
        if deepseek_model_env:
            self.deepseek_model = deepseek_model_env
            
        deepseek_reasoner_env = os.getenv("DEEPSEEK_REASONER_MODEL")
        if deepseek_reasoner_env:
            self.deepseek_reasoner_model = deepseek_reasoner_env
        
        # ========== 智谱 GLM ==========
        self.glm_api_key = os.getenv("GLM_API_KEY", "")
        
        glm_model_env = os.getenv("GLM_MODEL")
        if glm_model_env:
            self.glm_model = glm_model_env
        
        # ========== 模型提供商 ==========
        provider_env = os.getenv("DEFAULT_LLM_PROVIDER")
        if provider_env in ("deepseek", "glm"):
            self.llm_provider = provider_env
        
        # ========== 其他配置 ==========
        self.brave_search_api_key = os.getenv("BRAVE_SEARCH_API_KEY", "")
        
        search_depth_env = os.getenv("SEARCH_DEPTH", "deep")
        if search_depth_env in ("shallow", "deep"):
            self.search_depth = search_depth_env
        
        max_results_env = os.getenv("MAX_SEARCH_RESULTS", "10")
        try:
            self.max_search_results = int(max_results_env)
        except ValueError:
            self.max_search_results = 10
        
        language_env = os.getenv("DEFAULT_LANGUAGE", "zh")
        if language_env in ("zh", "en"):
            self.default_language = language_env
        
        report_mode_env = os.getenv("REPORT_MODE", "basic")
        if report_mode_env in ("basic", "enhanced"):
            self.report_mode = report_mode_env
        
        max_sources_env = os.getenv("REPORT_MAX_SOURCES", "8")
        try:
            self.report_max_sources = int(max_sources_env)
        except ValueError:
            self.report_max_sources = 8


settings = Settings()
```

#### 2.2 重构 LLM 客户端

**文件**: `utils/llm_client.py`

```python
"""统一的 LLM 客户端 - 支持多模型切换"""

import time
import logging
from typing import Optional, Literal
from langchain_core.messages import BaseMessage

from config import settings

logger = logging.getLogger(__name__)


def create_llm_instance(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
):
    """
    创建 LLM 实例
    
    Args:
        provider: 模型提供商 ("deepseek" 或 "glm")，默认使用 settings.llm_provider
        model: 模型名称，默认使用提供商的默认模型
        temperature: 温度参数
    
    Returns:
        LLM 实例
    """
    provider = provider or settings.llm_provider
    
    if provider == "deepseek":
        from langchain_deepseek import ChatDeepSeek
        
        model = model or settings.deepseek_model
        return ChatDeepSeek(
            model=model,
            temperature=temperature,
            api_key=settings.deepseek_api_key,
        )
    
    elif provider == "glm":
        from langchain_community.chat_models import ChatZhipuAI
        
        model = model or settings.glm_model
        return ChatZhipuAI(
            model=model,
            temperature=temperature,
            zhipuai_api_key=settings.glm_api_key,
        )
    
    else:
        raise ValueError(f"不支持的模型提供商: {provider}")


class RateLimitedLLM:
    """带速率限制的 LLM 客户端"""

    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_retries: int = 3,
        min_interval: float = 1.0,
    ):
        """
        初始化带速率限制的 LLM 客户端

        Args:
            provider: 模型提供商 ("deepseek" 或 "glm")
            model: 模型名称
            temperature: 温度参数
            max_retries: 最大重试次数
            min_interval: 最小请求间隔
        """
        self.provider = provider or settings.llm_provider
        self.model = model
        self.temperature = temperature
        self.max_retries = max_retries
        self.min_interval = min_interval
        self._last_request_time = 0

        # 创建 LLM 实例
        self.llm = create_llm_instance(
            provider=self.provider,
            model=self.model,
            temperature=self.temperature,
        )
        
        logger.info(f"初始化 LLM 客户端: provider={self.provider}, model={self.llm.model_name}")

    def _wait_for_rate_limit(self):
        """等待速率限制"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.min_interval:
            wait_time = self.min_interval - elapsed
            logger.debug(f"速率限制等待 {wait_time:.2f} 秒")
            time.sleep(wait_time)

    def invoke(
        self,
        messages,
        retry_on_rate_limit: bool = True,
        **kwargs
    ):
        """
        调用 LLM，带重试机制

        Args:
            messages: 消息列表
            retry_on_rate_limit: 遇到速率限制时是否重试
            **kwargs: 其他参数

        Returns:
            LLM 响应
        """
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                # 等待速率限制
                self._wait_for_rate_limit()

                # 调用 LLM
                self._last_request_time = time.time()
                response = self.llm.invoke(messages, **kwargs)

                return response

            except Exception as e:
                error_str = str(e)
                last_exception = e

                # 检查是否是速率限制错误
                is_rate_limit = (
                    "429" in error_str or 
                    "rate limit" in error_str.lower() or 
                    "限流" in error_str or
                    "quota" in error_str.lower()
                )
                
                if is_rate_limit:
                    if retry_on_rate_limit and attempt < self.max_retries - 1:
                        # 指数退避
                        wait_time = (2 ** attempt) * 2 + 1  # 3, 5, 9 秒
                        logger.warning(f"遇到速率限制，等待 {wait_time} 秒后重试 (尝试 {attempt + 1}/{self.max_retries})")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"速率限制重试失败，已达到最大重试次数 ({self.max_retries})")
                        raise

                # 其他错误直接抛出
                logger.error(f"LLM 调用失败: {error_str}")
                raise

        # 所有重试都失败
        raise last_exception


# 全局缓存，避免重复创建实例
_llm_cache = {}


def get_llm(
    model: Optional[str] = None,
    temperature: float = 0.7,
    use_rate_limit: bool = True,
    provider: Optional[str] = None,
) -> RateLimitedLLM:
    """
    获取 LLM 客户端实例（带缓存）

    Args:
        model: 模型名称
        temperature: 温度参数
        use_rate_limit: 是否使用速率限制
        provider: 模型提供商 ("deepseek" 或 "glm")

    Returns:
        RateLimitedLLM 实例
    """
    provider = provider or settings.llm_provider
    model = model or (settings.deepseek_model if provider == "deepseek" else settings.glm_model)
    
    cache_key = f"{provider}_{model}_{temperature}_{use_rate_limit}"

    if cache_key not in _llm_cache:
        if use_rate_limit:
            _llm_cache[cache_key] = RateLimitedLLM(
                provider=provider,
                model=model,
                temperature=temperature,
            )
        else:
            # 不使用速率限制的快速客户端
            _llm_cache[cache_key] = create_llm_instance(
                provider=provider,
                model=model,
                temperature=temperature,
            )

    return _llm_cache[cache_key]
```

#### 2.3 更新各个 Agent

**文件**: `agents/search_agent.py`

```python
# 原代码（第 151-156 行）
llm = ChatDeepSeek(
    model=settings.deepseek_model,
    temperature=0.3,
    api_key=settings.deepseek_api_key,
)

# 改为
from utils.llm_client import get_llm

llm = get_llm(temperature=0.3)
```

**文件**: `agents/task_planner.py`

```python
# 原代码（第 56-61 行）
from langchain_deepseek import ChatDeepSeek

llm = ChatDeepSeek(
    model=settings.deepseek_model,
    temperature=0.3,
    api_key=settings.deepseek_api_key,
)

# 改为
from utils.llm_client import get_llm

llm = get_llm(temperature=0.3)
```

**文件**: `agents/enhanced_report_agent.py`（所有 ChatDeepSeek 调用）

```python
# 将所有 ChatDeepSeek 调用替换为
from utils.llm_client import get_llm

llm = get_llm(temperature=0.7)  # 根据实际温度调整
```

---

### 阶段三：测试验证

#### 3.1 创建测试脚本

**文件**: `test_llm_providers.py`

```python
"""测试不同的 LLM 提供商"""

import sys
sys.path.insert(0, '/Users/purepure/Desktop/docs/deepfind-agent')

from utils.llm_client import get_llm, create_llm_instance
from langchain_core.messages import HumanMessage, SystemMessage
from config import settings

print("=" * 60)
print("测试 LLM 提供商切换功能")
print("=" * 60)

# 测试 1: DeepSeek 模型
print("\n[测试 1] DeepSeek 模型")
print(f"API Key: {settings.deepseek_api_key[:20]}...")
print(f"Model: {settings.deepseek_model}")

try:
    llm_deepseek = get_llm(provider="deepseek", temperature=0.5)
    response = llm_deepseek.invoke([
        SystemMessage(content="你是一个助手"),
        HumanMessage(content="用一句话介绍纽约")
    ])
    print(f"✅ DeepSeek 响应成功")
    print(f"响应: {response.content[:100]}...")
except Exception as e:
    print(f"❌ DeepSeek 失败: {str(e)}")

# 测试 2: GLM 模型
print("\n[测试 2] GLM-5.2 模型")
print(f"API Key: {settings.glm_api_key[:20]}...")
print(f"Model: {settings.glm_model}")

try:
    llm_glm = get_llm(provider="glm", temperature=0.5)
    response = llm_glm.invoke([
        SystemMessage(content="你是一个助手"),
        HumanMessage(content="用一句话介绍纽约")
    ])
    print(f"✅ GLM 响应成功")
    print(f"响应: {response.content[:100]}...")
except Exception as e:
    print(f"❌ GLM 失败: {str(e)}")

# 测试 3: 默认模型
print("\n[测试 3] 默认模型")
print(f"当前默认提供商: {settings.llm_provider}")

try:
    llm_default = get_llm(temperature=0.5)
    response = llm_default.invoke([
        SystemMessage(content="你是一个助手"),
        HumanMessage(content="1+1=?")
    ])
    print(f"✅ 默认模型响应成功")
    print(f"响应: {response.content}")
except Exception as e:
    print(f"❌ 默认模型失败: {str(e)}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
```

#### 3.2 验证步骤

```bash
# 1. 测试 DeepSeek 模型
DEFAULT_LLM_PROVIDER=deepseek python test_llm_providers.py

# 2. 测试 GLM 模型
DEFAULT_LLM_PROVIDER=glm python test_llm_providers.py

# 3. 启动服务测试
DEFAULT_LLM_PROVIDER=deepseek python api.py  # 使用 DeepSeek
DEFAULT_LLM_PROVIDER=glm python api.py        # 使用 GLM
```

---

### 阶段四：前端支持（可选）

#### 4.1 添加模型选择 UI

**文件**: `frontend/src/contexts/SettingsContext.tsx`

```typescript
// 添加模型提供商选项
type LLMProvider = 'deepseek' | 'glm';

interface Settings {
  // ... 其他设置
  llmProvider: LLMProvider;
}

// 添加切换函数
const setLLMProvider = (provider: LLMProvider) => {
  setSettings(prev => ({ ...prev, llmProvider: provider }));
  // 发送 API 更新后端配置
  fetch('/api/settings', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ llmProvider: provider }),
  });
};
```

#### 4.2 添加 API 端点

**文件**: `api.py`

```python
from fastapi import HTTPException

@app.post("/api/settings")
async def update_settings(settings_update: dict):
    """更新运行时配置"""
    global settings
    
    if "llmProvider" in settings_update:
        provider = settings_update["llmProvider"]
        if provider in ("deepseek", "glm"):
            settings.llm_provider = provider
            # 清除 LLM 缓存
            from utils.llm_client import _llm_cache
            _llm_cache.clear()
            
            return {"success": True, "llmProvider": provider}
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
    
    return {"success": False}
```

---

## 📊 对比分析

| 维度 | DeepSeek | GLM-5.2 |
|------|----------|---------|
| **推理能力** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **速度** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **成本** | ¥1/百万token | ¥0.1/百万token |
| **中文能力** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **API 稳定性** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **无速率限制** | ❌ 有 | ✅ 宽松 |

**推荐使用场景**：
- **DeepSeek**: 需要深度推理的复杂任务（如研究、分析）
- **GLM-5.2**: 需要快速响应的简单任务（如搜索、格式化）

---

## 🚀 实施步骤

### 第一步：环境准备（15分钟）

```bash
# 1. 安装依赖
cd /Users/purepure/Desktop/docs/deepfind-agent
pip install zhipuai

# 2. 更新 .env
cat >> .env << EOF

# ========== 智谱 GLM 配置 ==========
GLM_API_KEY=your_glm_api_key_here
GLM_MODEL=glm-5.2
DEFAULT_LLM_PROVIDER=deepseek
EOF

# 3. 编辑 .env，填入实际的 GLM API Key
```

### 第二步：代码改造（30分钟）

```bash
# 1. 更新配置文件
#    - config/settings.py

# 2. 重构 LLM 客户端
#    - utils/llm_client.py

# 3. 更新各个 Agent
#    - agents/search_agent.py
#    - agents/task_planner.py
#    - agents/enhanced_report_agent.py
```

### 第三步：测试验证（15分钟）

```bash
# 1. 创建测试脚本
#    - test_llm_providers.py

# 2. 运行测试
python test_llm_providers.py

# 3. 启动服务
python api.py

# 4. 前端测试
#    - 输入查询验证功能
#    - 检查日志确认模型切换
```

### 第四步：部署上线（10分钟）

```bash
# 1. 更新 requirements.txt
echo "zhipuai>=2.0.0" >> requirements.txt

# 2. 重启服务
python api.py

# 3. 监控日志
tail -f api.log | grep "初始化 LLM 客户端"
```

---

## 📝 注意事项

### 1. API Key 安全
- ✅ 不要将 API Key 提交到代码仓库
- ✅ 使用环境变量管理密钥
- ✅ 定期轮换密钥

### 2. 模型切换
- 切换模型后会清除 LLM 缓存
- 需要等待当前请求完成
- 建议在低峰期切换

### 3. 错误处理
- 如果一个模型失败，自动fallback到另一个模型
- 记录详细的错误日志
- 设置合理的超时时间

### 4. 性能优化
- 缓存 LLM 实例避免重复创建
- 使用异步请求提高并发
- 监控模型响应时间

---

## 🔍 监控指标

### 关键指标

```python
# 在 utils/llm_client.py 中添加
import time

class LLMMetrics:
    def __init__(self):
        self.total_calls = 0
        self.success_calls = 0
        self.failed_calls = 0
        self.total_time = 0
        self.provider_calls = {"deepseek": 0, "glm": 0}
    
    def record_call(self, provider: str, duration: float, success: bool):
        self.total_calls += 1
        self.total_time += duration
        self.provider_calls[provider] += 1
        if success:
            self.success_calls += 1
        else:
            self.failed_calls += 1

metrics = LLMMetrics()
```

### 日志记录

```python
# 在每个模型调用时记录
logger.info(f"调用模型: provider={provider}, model={model}, duration={duration:.2f}s")
```

---

## ✅ 验收标准

### 功能验收
- ✅ 可以通过环境变量切换模型
- ✅ DeepSeek 模型调用正常
- ✅ GLM 模型调用正常
- ✅ 模型切换不影响功能
- ✅ 速率限制正常工作

### 性能验收
- ✅ GLM 响应时间 < DeepSeek（简单任务）
- ✅ 模型切换耗时 < 1秒
- ✅ 缓存命中率 > 80%

### 质量验收
- ✅ 报告质量不低于原模型
- ✅ 错误处理完善
- ✅ 日志记录详细

---

## 📚 参考文档

- 智谱 AI API 文档: https://open.bigmodel.cn/dev/api
- LangChain 文档: https://python.langchain.com/docs/integrations/chat/zhipuai
- GLM-5.2 模型介绍: https://open.bigmodel.cn/model/glm-5.2

---

**版本**: V1.0  
**创建时间**: 2026-06-29  
**预计实施时间**: 1-1.5小时