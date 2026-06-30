# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- 待添加的新功能

### Changed
- 待更改的功能

### Deprecated
- 待弃用的功能

### Removed
- 待移除的功能

### Fixed
- 待修复的bug

### Security
- 待修复的安全问题

---

## [1.0.0] - 2026-06-30

### Added
#### 核心功能
- ✨ 多源搜索引擎（Tavily、DuckDuckGo、Serper、Brave）
- ✨ 智能搜索结果聚合与排序
- ✨ 自适应报告生成（根据内容类型自动选择格式）
- ✨ 多场景支持（产品方案、旅游攻略、行业洞察）
- ✨ 流式输出支持（SSE）
- ✨ 任务规划与进度展示

#### 搜索能力
- ✨ 并行搜索（速度提升85%）
- ✨ 智能降级（主搜索源失败自动切换）
- ✨ 权威度评分系统
- ✨ 结果去重去噪

#### 分析能力
- ✨ 智能内容分类（天气、产品、旅游、技术、新闻等）
- ✨ 结构化信息提取
- ✨ 来源可信度评估
- ✨ 情感分析

#### 报告生成
- ✨ 产品方案报告（竞品对比、用户评价、定价策略）
- ✨ 旅游攻略报告（双方案模式、实时天气、预算明细）
- ✨ 行业洞察报告（时间线、影响分析、趋势预测）
- ✨ 来源标注与可信度评分

#### 用户界面
- ✨ 响应式前端界面（React + TypeScript + Tailwind CSS）
- ✨ 实时进度展示
- ✅ 任务DAG可视化
- ✨ Markdown渲染
- ✨ 复制功能
- ✨ 深色/浅色主题

#### API接口
- ✨ RESTful API（FastAPI）
- ✨ 流式接口（SSE）
- ✨ 健康检查接口
- ✨ 任务状态查询
- ✨ 任务取消

### Changed
- 🔄 优化搜索速度（并行搜索、智能缓存）
- 🔄 优化报告质量（来源标注、可信度评分）
- 🔄 优化用户体验（实时进度、错误处理）

### Fixed
- 🐛 修复Tavily API 432错误（配额超限）
- 🐛 修复DeepSeek API 429错误（速率限制）
- 🐛 修复搜索结果不一致问题（结果聚合与排序）
- 🐛 修复前端复制功能（支持文本选择）
- 🐛 修复前端图标显示（颜色加深）

### Security
- 🔒 添加.env到.gitignore（防止API Key泄露）
- 🔒 添加API Key验证
- 🔒 添加输入验证（查询长度限制）

---

## Version History

### v1.0.0 (2026-06-30)
- 🎉 初始版本发布
- ✨ 核心功能完整
- ✨ 三大场景支持
- ✨ 多源搜索引擎
- ✨ 自适应报告生成

---

## Roadmap

### v1.1.0 (Plan)
- 🔄 添加GLM-5.2模型支持
- 🔄 添加Reddit API集成
- 🔄 添加Hacker News API集成
- 🔄 添加用户上传CSV数据分析

### v1.2.0 (Plan)
- 🔄 添加数据可视化（图表生成）
- 🔄 添加报告导出PDF功能
- 🔄 添加多语言支持

### v2.0.0 (Plan)
- 🔄 重构为多Agent架构
- 🔄 添加记忆机制（支持连续对话）
- 🔄 添加流式搜索结果展示

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.