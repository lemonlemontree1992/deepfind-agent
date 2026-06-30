# 🚀 DeepFind Agent

<div align="center">

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)

**一个强大的深度调研智能体，支持多场景专业报告生成**

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [使用场景](#-使用场景) • [文档](#-文档)

</div>

---

## 📖 简介

DeepFind Agent 是一个**通用深度调研智能体**，具备强大的多源搜索和报告生成能力，专注于三大场景：

1. **📊 产品方案设计** - 输出面向商家后台的产品经理可执行的产品方案
2. **🌍 旅游攻略生成** - 输出可直接执行的旅游攻略（双方案模式）
3. **📈 行业洞察报告** - 输出互联网/AI圈的最新动态和深度分析

### 核心亮点

- 🔍 **多源搜索** - Tavily/DuckDuckGo/Serper/Brave，智能聚合
- 🧠 **智能分析** - 趋势分析、竞品对比、情感分析
- 📊 **专业报告** - 产品方案、旅游攻略、行业洞察
- 🔄 **自适应输出** - 根据内容类型自动选择最佳格式
- 🔒 **数据安全** - 本地部署，数据不上传

---

## ✨ 功能特性

### 🔍 搜索能力
- **多源搜索**: Tavily、DuckDuckGo、Serper、Brave、SerpApi
- **智能聚合**: 权威度评分、相关性排序、去重去噪
- **并行搜索**: 多维度搜索词并行执行，速度提升85%
- **智能降级**: 主搜索源失败自动切换备用源

### 🧠 分析能力
- **智能提取**: 自动识别内容类型（产品、旅游、新闻等）
- **实体识别**: 提取产品、地点、公司、技术等关键信息
- **情感分析**: 分析用户评价情感分布
- **趋势分析**: 价格走势、热度变化、市场趋势

### 📊 报告生成
- **产品方案**: 竞品对比、用户评价、定价策略、行动清单
- **旅游攻略**: 双方案模式（经典+深度）、实时天气、预算明细
- **行业洞察**: 时间线、影响分析、趋势预测、行动建议
- **自适应输出**: 根据内容自动选择表格、列表、时间线等格式

### 🎯 三大场景

| 场景 | 输入示例 | 输出价值 |
|------|---------|---------|
| 产品方案设计 | "分析iPhone 15 Pro竞品对比" | 可执行的产品决策建议 |
| 旅游攻略生成 | "纽约4天3晚攻略" | 可直接执行的旅游攻略 |
| 行业洞察报告 | "Claude 3发布对AI行业影响" | 深度行业洞察报告 |

---

## 🚀 快速开始

### 环境要求
- Python 3.9+
- Node.js 16+（前端）
- 8GB+ RAM

### 安装步骤

#### 1. 克隆项目
```bash
git clone https://github.com/yourusername/deepfind-agent.git
cd deepfind-agent
```

#### 2. 后端安装
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

# 安装依赖
pip install -r requirements.txt
```

#### 3. 前端安装
```bash
cd frontend
npm install
cd ..
```

#### 4. 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，填入API Key
vim .env
```

**必需的API Key**:
- `DEEPSEEK_API_KEY` - DeepSeek LLM API（[获取地址](https://platform.deepseek.com/)）
- `TAVILY_API_KEY` - Tavily搜索API（[获取地址](https://tavily.com/)）

#### 5. 启动服务
```bash
# 启动后端
python api.py

# 启动前端（另一个终端）
cd frontend && npm run dev
```

#### 6. 访问应用
打开浏览器访问: http://localhost:3000

---

## 📖 使用场景

### 场景一：产品方案设计

**输入示例**:
```
分析iPhone 15 Pro和华为Mate 60 Pro的竞品对比，给出产品方案建议
```

**输出内容**:
- 产品概览（基础信息、市场表现、用户反馈）
- 竞品对比分析（参数对比、价格对比、用户评分对比）
- 用户评价分析（评价分布、正向/负向关键词、用户画像）
- 价格策略分析（价格历史、促销节点、定价建议）
- 流量与转化分析（流量来源、转化漏斗、优化建议）
- 产品方案建议（定价策略、流量策略、转化优化、行动清单）

---

### 场景二：旅游攻略生成

**输入示例**:
```
纽约4天3晚旅行攻略
```

**输出内容**:
- 整体概览与行前准备（最佳时间、签证、货币、通讯）
- 区域住宿选择指南（推荐区域、适合人群、价格参考）
- 行程规划方案（方案A：经典必游 + 方案B：深度体验）
- 核心美食推荐（必吃美食、美食街区、餐厅预订）
- 预算参考（经济型/舒适型/豪华型，三档预算明细）
- 实用小贴士（交通、地图、语言、购物、安全）

---

### 场景三：行业洞察报告

**输入示例**:
```
Claude 3发布对AI行业的影响
```

**输出内容**:
- 核心要点（3-5条关键发现）
- 产品概览（时间线、核心特性、技术创新）
- 性能基准对比（与竞品对比表、技术优势劣势）
- 社区讨论热度（Reddit、Hacker News、Twitter讨论）
- 影响分析（对开发者、产品经理、投资人的影响）
- 未来趋势预测（短期、中期、长期）
- 行动建议（针对不同角色）

---

## 📚 文档

### 用户文档
- [快速开始指南](test/QUICK_START.md) - 5分钟快速上手
- [使用场景](docs/DEEPFIND-AGENT-ARCHITECTURE.md) - 详细场景说明

### 开发文档
- [架构设计](docs/DEEPFIND-AGENT-ARCHITECTURE.md) - 整体架构设计
- [优化方案](docs/AGENT-OPTIMIZATION-PLAN.md) - 未来优化计划
- [免费数据源](docs/FREE-DATA-SOURCES.md) - 免费API接入指南
- [发布检查清单](docs/RELEASE_CHECKLIST.md) - 发布前检查事项

### API文档
- 后端API运行后访问: http://localhost:8000/docs
- 主要端点:
  - `GET /health` - 健康检查
  - `GET /api/research/stream` - 调研流式接口

---

## 🔧 配置说明

### 必需的API Key

| API Key | 用途 | 获取地址 | 价格 |
|---------|------|---------|------|
| DeepSeek API Key | LLM模型 | [获取](https://platform.deepseek.com/) | ¥1/百万token |
| Tavily API Key | 搜索服务 | [获取](https://tavily.com/) | 免费额度 |

### 可选的API Key（免费）

| API Key | 用途 | 免费额度 | 获取地址 |
|---------|------|---------|---------|
| Reddit API | 社区讨论 | 无限制 | [获取](https://www.reddit.com/prefs/apps) |
| Hacker News API | 技术讨论 | 无限制 | 无需申请 |
| OpenWeatherMap API | 天气数据 | 1000次/天 | [获取](https://openweathermap.org/api) |
| ExchangeRate API | 汇率换算 | 1500次/月 | [获取](https://www.exchangerate-api.com/) |

---

## 🛠️ 技术栈

### 后端
- **框架**: FastAPI 0.100+
- **LLM**: DeepSeek、GLM
- **搜索**: Tavily、DuckDuckGo、Serper、Brave
- **异步**: asyncio、httpx

### 前端
- **框架**: React 18、TypeScript
- **UI**: Tailwind CSS、Shadcn UI
- **状态管理**: React Query
- **构建工具**: Vite

---

## 📊 项目结构

```
deepfind-agent/
├── agents/                 # Agent模块
│   ├── search_agent.py    # 搜索Agent
│   ├── analyze_agent.py   # 分析Agent
│   ├── report_agent.py    # 报告Agent
│   └── ...
├── tools/                  # 工具模块
│   ├── search.py          # 搜索工具
│   ├── result_aggregator.py # 结果聚合
│   └── ...
├── prompts/                # Prompt模板
│   ├── adaptive_prompts.py   # 自适应Prompt
│   ├── business_research_prompts.py # 商业调研
│   └── ...
├── utils/                  # 工具函数
│   ├── llm_client.py      # LLM客户端
│   └── ...
├── config/                 # 配置文件
│   └── settings.py        # 配置管理
├── frontend/               # 前端代码
│   ├── src/
│   ├── package.json
│   └── ...
├── docs/                   # 文档
│   └── ...
├── test/                   # 测试
│   └── ...
├── api.py                  # 主API入口
├── requirements.txt        # Python依赖
├── .env.example            # 环境变量模板
└── README.md               # 项目说明
```

---

## 🤝 贡献指南

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md)

### 贡献方式
- 报告Bug
- 提出新功能
- 提交代码
- 完善文档

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

## 🙏 致谢

### 核心依赖
- [FastAPI](https://fastapi.tiangolo.com/) - 现代高性能Web框架
- [LangChain](https://www.langchain.com/) - LLM应用开发框架
- [DeepSeek](https://www.deepseek.com/) - 强大的LLM模型
- [Tavily](https://tavily.com/) - AI专用搜索引擎
- [React](https://reactjs.org/) - 用户界面库
- [Tailwind CSS](https://tailwindcss.com/) - 实用优先的CSS框架

### 灵感来源
- [AutoGPT](https://github.com/Significant-Gravitas/Auto-GPT) - 自主AI代理
- [GPT-Researcher](https://github.com/assafelovic/gpt-researcher) - AI研究助手

---

## 📞 联系方式

- **问题反馈**: [GitHub Issues](https://github.com/yourusername/deepfind-agent/issues)
- **功能建议**: [GitHub Discussions](https://github.com/yourusername/deepfind-agent/discussions)

---

<div align="center">

**Made with ❤️ by DeepFind Team**

**⭐ 如果这个项目对你有帮助，请给一个Star！⭐**

</div>