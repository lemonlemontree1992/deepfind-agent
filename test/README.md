# 🧪 本地调试文档

> 此目录用于记录本地调试相关的内容，与线上环境保持独立

## 📋 目录结构

```
test/
├── README.md                    # 本文档
├── local_config/               # 本地配置文件
│   ├── .env.local             # 本地环境变量（不提交到git）
│   └── settings_local.py      # 本地设置
├── test_scripts/               # 测试脚本
│   ├── test_api.py            # API测试脚本
│   ├── test_search.py         # 搜索功能测试
│   └── test_report.py         # 报告生成测试
├── test_data/                  # 测试数据
│   ├── sample_products.csv    # 示例商品数据
│   ├── sample_orders.csv      # 示例订单数据
│   └── sample_traffic.csv     # 示例流量数据
├── test_outputs/               # 测试输出
│   ├── reports/               # 生成的测试报告
│   └── logs/                  # 测试日志
└── notes/                      # 调试笔记
    ├── debugging_notes.md     # 调试笔记
    └── todo.md                # 待办事项
```

---

## 🚀 本地调试指南

### 1. 环境准备

#### 1.1 创建本地环境变量
```bash
# 复制环境变量模板
cp .env test/local_config/.env.local

# 编辑本地环境变量
vim test/local_config/.env.local
```

#### 1.2 安装依赖
```bash
# 激活虚拟环境
source venv/bin/activate

# 安装开发依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 如果有
```

---

### 2. 运行测试

#### 2.1 API测试
```bash
# 测试后端API
python test/test_scripts/test_api.py

# 测试搜索功能
python test/test_scripts/test_search.py

# 测试报告生成
python test/test_scripts/test_report.py
```

#### 2.2 前端测试
```bash
cd frontend
npm run dev  # 启动前端开发服务器
```

#### 2.3 完整流程测试
```bash
# 启动后端
python api.py

# 启动前端（另一个终端）
cd frontend && npm run dev

# 访问 http://localhost:3000
```

---

## 📝 调试笔记

### 2026-06-30 调试记录

#### 新增功能
- ✅ 创建test目录结构
- ✅ 规划本地调试文档

#### 待测试功能
- [ ] 测试Reddit API接入
- [ ] 测试Hacker News API接入
- [ ] 测试Google News RSS订阅
- [ ] 测试场景分类器
- [ ] 测试产品方案报告生成

#### 已知问题
- [ ] 暂无

---

## 🔧 本地配置

### 环境变量（test/local_config/.env.local）

```bash
# ========== 本地调试配置 ==========

# DeepSeek API Key
DEEPSEEK_API_KEY=sk-your-local-test-key

# Tavily API Key
TAVILY_API_KEY=tvly-your-local-test-key

# Reddit API（免费）
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret

# OpenWeatherMap API（免费）
OPENWEATHERMAP_API_KEY=your_weather_api_key

# ExchangeRate API（免费）
EXCHANGERATE_API_KEY=your_exchange_rate_api_key

# ========== 本地调试开关 ==========
DEBUG_MODE=true
LOG_LEVEL=DEBUG
ENABLE_LOCAL_DATA=true
```

---

## 📊 测试数据准备

### 测试场景1：产品方案分析
```bash
# 测试查询
query: "分析iPhone 15 Pro和华为Mate 60 Pro的竞品对比"

# 测试数据
test/test_data/sample_products.csv  # 商品数据
test/test_data/sample_orders.csv    # 订单数据
```

### 测试场景2：旅游攻略生成
```bash
# 测试查询
query: "纽约4天3晚旅行攻略"

# 测试数据
test/test_data/travel_preferences.json  # 用户偏好
```

### 测试场景3：行业洞察报告
```bash
# 测试查询
query: "Claude 3发布对AI行业的影响"

# 测试数据
test/test_data/industry_keywords.json  # 关注关键词
```

---

## 🐛 Bug记录

### Bug #1
- **日期**: YYYY-MM-DD
- **描述**: 
- **重现步骤**:
- **解决方案**: 
- **状态**: Open/Fixed/Closed

---

## 📝 TODO

### 本地调试任务
- [ ] 创建测试脚本
- [ ] 准备测试数据
- [ ] 测试场景分类器
- [ ] 测试多源搜索
- [ ] 测试报告生成
- [ ] 性能测试
- [ ] 集成测试

### 优化任务
- [ ] 优化搜索速度
- [ ] 优化报告质量
- [ ] 优化内存占用
- [ ] 优化错误处理

---

## 🔗 相关文档

- [优化方案](../docs/AGENT-OPTIMIZATION-PLAN.md)
- [免费数据源](../docs/FREE-DATA-SOURCES.md)
- [电商产品分析](../docs/ECOMMERCE-PRODUCT-ANALYSIS.md)
- [架构设计](../docs/DEEPFIND-AGENT-ARCHITECTURE.md)

---

**文档版本**: V1.0
**创建时间**: 2026-06-30
**维护者**: 本地开发环境