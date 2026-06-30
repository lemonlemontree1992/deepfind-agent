# GLM-5.2 集成指南

## 📚 文档导航

### 1️⃣ 快速开始
阅读 **[glm-integration-summary.md](glm-integration-summary.md)** - 5分钟了解全貌

### 2️⃣ 完整方案
参考 **[glm-integration-plan.md](glm-integration-plan.md)** - 详细技术方案（60+页）

### 3️⃣ 代码修改
对照 **[glm-code-checklist.md](glm-code-checklist.md)** - 逐文件修改清单

---

## 🚀 快速实施（3步）

### 步骤 1: 准备环境（2分钟）

```bash
# 安装依赖
pip install zhipuai>=2.0.0

# 配置 API Key
echo "
# 智谱 GLM 配置
GLM_API_KEY=你的GLM_API_Key
GLM_MODEL=glm-5.2
DEFAULT_LLM_PROVIDER=deepseek
" >> .env
```

### 步骤 2: 修改代码（25分钟）

按照 `glm-code-checklist.md` 修改以下文件：

1. `config/settings.py` - 添加 GLM 配置
2. `utils/llm_client.py` - 支持双模型
3. `agents/search_agent.py` - 替换 ChatDeepSeek
4. `agents/task_planner.py` - 替换 ChatDeepSeek  
5. `agents/enhanced_report_agent.py` - 替换 ChatDeepSeek

### 步骤 3: 测试验证（5分钟）

```bash
# 运行验证脚本
./scripts/verify_glm_integration.sh

# 测试模型
python test_llm_providers.py

# 启动服务
python api.py
```

---

## 🎯 核心变更

### Before（只支持 DeepSeek）
```python
from langchain_deepseek import ChatDeepSeek

llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key=settings.deepseek_api_key
)
```

### After（支持 DeepSeek + GLM）
```python
from utils.llm_client import get_llm

# 默认使用 settings.llm_provider
llm = get_llm()

# 或指定模型
llm_deepseek = get_llm(provider="deepseek")
llm_glm = get_llm(provider="glm")
```

---

## 📊 模型对比

| 特性 | DeepSeek | GLM-5.2 |
|------|----------|---------|
| 推理能力 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 速度 | 较慢(2-5s) | 快(0.5-2s) |
| 成本 | ¥1/百万token | ¥0.1/百万token |
| 适用场景 | 复杂推理 | 快速响应 |

**推荐用法**：
- 搜索词生成 → GLM（快）
- 内容分析 → DeepSeek（准）
- 报告生成 → GLM（便宜）

---

## 🔧 使用方式

### 方式 1: 环境变量切换

```bash
# 使用 DeepSeek（默认）
DEFAULT_LLM_PROVIDER=deepseek python api.py

# 使用 GLM
DEFAULT_LLM_PROVIDER=glm python api.py
```

### 方式 2: 代码中指定

```python
from utils.llm_client import get_llm

# 快速任务用 GLM
fast_llm = get_llm(provider="glm", temperature=0.3)

# 深度分析用 DeepSeek  
deep_llm = get_llm(provider="deepseek", temperature=0.5)
```

---

## ✅ 验收清单

- [ ] 已安装 zhipuai 包
- [ ] .env 包含 GLM_API_KEY
- [ ] 已修改 5 个代码文件
- [ ] `python test_llm_providers.py` 测试通过
- [ ] `./scripts/verify_glm_integration.sh` 检查通过
- [ ] 服务启动成功，日志显示正确的模型

---

## 📞 问题排查

### Q1: ModuleNotFoundError: No module named 'zhipuai'
**A**: `pip install zhipuai>=2.0.0`

### Q2: Invalid API key
**A**: 检查 .env 中的 GLM_API_KEY 是否正确

### Q3: 找不到 get_llm
**A**: 确保导入语句正确：`from utils.llm_client import get_llm`

### Q4: 模型调用失败
**A**: 
1. 检查网络连接
2. 查看日志 `tail -f api.log`
3. 验证 API 配额

---

## 📦 脚本说明

| 脚本 | 用途 | 使用方式 |
|------|------|----------|
| `scripts/integrate_glm.sh` | 快速部署脚本 | `./scripts/integrate_glm.sh` |
| `scripts/verify_glm_integration.sh` | 验证检查脚本 | `./scripts/verify_glm_integration.sh` |
| `test_llm_providers.py` | 模型测试脚本 | `python test_llm_providers.py` |

---

## 🎓 相关资源

- **智谱 AI 官网**: https://open.bigmodel.cn
- **GLM-5.2 文档**: https://open.bigmodel.cn/model/glm-5.2
- **LangChain 文档**: https://python.langchain.com/docs/integrations/chat/zhipuai

---

**预计实施时间**: 30-60 分钟  
**难度等级**: ⭐⭐☆☆☆（中等）

如有问题，请查阅详细文档：
- 完整方案 → `glm-integration-plan.md`
- 代码清单 → `glm-code-checklist.md`  
- 总结文档 → `glm-integration-summary.md`