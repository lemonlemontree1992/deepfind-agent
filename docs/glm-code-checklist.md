# GLM-5.2 集成代码修改清单

## ✅ 修改概览

| 文件 | 状态 | 说明 |
|------|------|------|
| `requirements.txt` | 待修改 | 添加 zhipuai 依赖 |
| `.env` | 待修改 | 添加 GLM 配置 |
| `config/settings.py` | 待修改 | 添加 GLM 配置项 |
| `utils/llm_client.py` | 待修改 | 重构为多模型支持 |
| `agents/search_agent.py` | 部分完成 | 已使用 get_llm |
| `agents/analyze_agent.py` | ✅ 完成 | 已使用 get_llm |
| `agents/extraction_agent.py` | ✅ 完成 | 已使用 get_llm |
| `agents/report_agent.py` | ✅ 完成 | 已使用 get_llm |
| `agents/task_planner.py` | 待修改 | 需替换 ChatDeepSeek |
| `agents/enhanced_report_agent.py` | 待修改 | 需替换 ChatDeepSeek |

---

## 📝 详细修改清单

### 1. requirements.txt

**位置**: 项目根目录

**添加内容**:
```txt
zhipuai>=2.0.0
```

**修改方式**: 在文件末尾添加

---

### 2. .env

**位置**: 项目根目录

**添加内容**:
```bash
# ========== 智谱 GLM 配置 ==========
GLM_API_KEY=your_glm_api_key_here
GLM_MODEL=glm-5.2

# ========== 模型选择 ==========
DEFAULT_LLM_PROVIDER=deepseek  # 可选: deepseek | glm
```

**修改方式**: 在文件末尾追加

**注意**: 需要替换 `your_glm_api_key_here` 为实际的 GLM API Key

---

### 3. config/settings.py

**位置**: `config/settings.py`

**修改内容**: 见 `docs/glm-integration-plan.md` 第 2.1 节

**关键修改点**:
- 添加 GLM 相关配置项
- 添加 llm_provider 配置项
- 更新 `__init__` 方法读取 GLM 环境变量

---

### 4. utils/llm_client.py

**位置**: `utils/llm_client.py`

**修改内容**: 完全重写，见 `docs/glm-integration-plan.md` 第 2.2 节

**关键修改点**:
- 添加 `create_llm_instance()` 函数支持多模型
- 更新 `RateLimitedLLM` 类支持 provider 参数
- 更新 `get_llm()` 函数支持 provider 参数
- 添加 GLM 模型支持

---

### 5. agents/search_agent.py

**位置**: `agents/search_agent.py`

**第 8 行**: 导入修改
```python
# 原代码
from langchain_deepseek import ChatDeepSeek

# 改为
from utils.llm_client import get_llm
```

**第 151-156 行**: 模型调用修改
```python
# 原代码
llm = ChatDeepSeek(
    model=settings.deepseek_model,
    temperature=0.3,
    api_key=settings.deepseek_api_key,
)

# 改为
llm = get_llm(temperature=0.3)
```

---

### 6. agents/task_planner.py

**位置**: `agents/task_planner.py`

**第 56 行**: 导入修改
```python
# 原代码
from langchain_deepseek import ChatDeepSeek

# 改为
from utils.llm_client import get_llm
```

**第 57-62 行**: 模型调用修改
```python
# 原代码
llm = ChatDeepSeek(
    model=settings.deepseek_model,
    temperature=0.3,
    api_key=settings.deepseek_api_key,
)

# 改为
llm = get_llm(temperature=0.3)
```

---

### 7. agents/enhanced_report_agent.py

**位置**: `agents/enhanced_report_agent.py`

**第 16 行**: 导入修改
```python
# 原代码
from langchain_deepseek import ChatDeepSeek

# 改为
from utils.llm_client import get_llm
```

**所有 ChatDeepSeek 调用**（共 6 处）: 替换为 get_llm

```python
# 原代码（示例）
llm = ChatDeepSeek(
    model=settings.deepseek_model,
    temperature=0.7,
    api_key=settings.deepseek_api_key,
)

# 改为
llm = get_llm(temperature=0.7)
```

**具体修改位置**:
- 第 88 行
- 第 177 行
- 第 228 行
- 第 321 行
- 第 455 行
- 第 527 行

---

## 🔍 快速搜索和替换

### 使用 grep 查找所有 ChatDeepSeek 引用

```bash
# 搜索所有导入 ChatDeepSeek 的文件
grep -r "from langchain_deepseek import ChatDeepSeek" agents/

# 搜索所有 ChatDeepSeek 实例化
grep -r "ChatDeepSeek(" agents/
```

### 批量替换示例

```bash
# 替换导入语句
find agents/ -type f -name "*.py" -exec sed -i '' 's/from langchain_deepseek import ChatDeepSeek/from utils.llm_client import get_llm/g' {} +

# 注意: ChatDeepSeek 实例化需要手动修改，因为参数不同
```

---

## ✅ 验证清单

完成修改后，执行以下验证：

### 1. 语法检查
```bash
python -m py_compile config/settings.py
python -m py_compile utils/llm_client.py
python -m py_compile agents/search_agent.py
python -m py_compile agents/task_planner.py
python -m py_compile agents/enhanced_report_agent.py
```

### 2. 导入测试
```bash
python -c "from utils.llm_client import get_llm; print('✅ 导入成功')"
```

### 3. 功能测试
```bash
# 运行测试脚本
python test_llm_providers.py
```

### 4. 服务启动测试
```bash
python api.py
# 访问 http://localhost:8000/health
```

---

## 📊 修改统计

- **需要修改的文件**: 7 个
- **需要添加的文件**: 1 个 (test_llm_providers.py)
- **新增代码行数**: ~200 行
- **修改代码行数**: ~50 行
- **预计修改时间**: 30-40 分钟

---

## 🚨 注意事项

1. **备份文件**: 修改前请备份原始文件
2. **API Key**: 确保 .env 中的 GLM_API_KEY 有效
3. **测试**: 修改后务必运行测试脚本
4. **日志**: 注意查看日志中的模型初始化信息
5. **缓存**: 切换模型后需要重启服务清除缓存

---

## 📞 问题排查

### 问题 1: ModuleNotFoundError: No module named 'zhipuai'
**解决**: `pip install zhipuai>=2.0.0`

### 问题 2: Invalid API key
**解决**: 检查 .env 中的 GLM_API_KEY 是否正确

### 问题 3: 模型调用失败
**解决**: 
1. 检查网络连接
2. 查看日志 `tail -f api.log`
3. 验证 API 调用配额

### 问题 4: 找不到 get_llm
**解决**: 确保 `from utils.llm_client import get_llm` 导入正确

---

**创建时间**: 2026-06-29  
**适用版本**: DeepFind Agent V2.0+