# 📋 DeepFind Agent 发布检查清单

## 🔴 发布前必做事项（高优先级）

### 1. 敏感信息处理 ✅ 最重要
**风险等级**: 🔴 极高（泄露API Key会导致费用损失）

#### 1.1 检查.env文件
```bash
# 查看当前.env文件
cat .env
```

**发现的问题**:
- ✅ `.env`文件包含真实的API Key
- ❌ `.env`文件不能提交到GitHub

**解决方案**:
```bash
# 1. 确保.env在.gitignore中
echo ".env" >> .gitignore

# 2. 检查是否有其他敏感文件
grep -r "sk-" . --include="*.py" --include="*.txt" --include="*.md"
grep -r "tvly-" . --include="*.py" --include="*.txt" --include="*.md"
```

#### 1.2 代码中的敏感信息检查
```bash
# 检查代码中是否硬编码了API Key
grep -r "api_key.*=" . --include="*.py" | grep -v ".env" | grep -v "settings.py"
grep -r "API_KEY.*=" . --include="*.py" | grep -v ".env" | grep -v "settings.py"
```

**需要修改的文件**:
- [ ] `test_glm_api.py` - 可能有硬编码的API Key
- [ ] `test_llm_providers.py` - 可能有硬编码的API Key
- [ ] 其他测试脚本

---

### 2. .gitignore配置 ✅ 必须配置

#### 2.1 创建完整的.gitignore
```bash
cat > .gitignore << 'EOF'
# ========== 敏感信息 ==========
.env
.env.local
.env.*.local
*.key
*.pem
secrets.json

# ========== Python ==========
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# ========== 虚拟环境 ==========
venv/
ENV/
env/
.venv

# ========== 日志文件 ==========
*.log
logs/
api.log
server.log
backend*.log
frontend*.log
streamlit.log

# ========== 输出文件 ==========
outputs/
test/test_outputs/

# ========== 系统文件 ==========
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# ========== IDE配置 ==========
.vscode/
.idea/
*.swp
*.swo
*~

# ========== 临时文件 ==========
*.tmp
*.bak
*.cache
.cache/

# ========== 测试文件 ==========
.pytest_cache/
.coverage
htmlcov/
.tox/

# ========== 编译文件 ==========
*.pyc
*.pyo
*.exe
*.dll
*.so
*.dylib

# ========== 压缩文件 ==========
*.zip
*.tar.gz
*.rar
muse.zip

# ========== 其他 ==========
node_modules/
.npm
.eslintcache
EOF
```

---

### 3. 代码清理 ✅ 必须清理

#### 3.1 删除不必要的文件
```bash
# 删除日志文件
rm -f *.log backend*.log frontend*.log streamlit.log

# 删除压缩文件
rm -f muse.zip

# 删除测试输出（保留测试脚本）
rm -rf outputs/*
mkdir -p outputs/.gitkeep

# 删除虚拟环境（用户可以自己创建）
# 不删除venv，但加入.gitignore
```

#### 3.2 移动测试脚本
```bash
# 将测试脚本移动到test目录
mv test_*.py test/test_scripts/

# 或者删除临时测试文件
# rm test_*.py
```

---

### 4. 文档完善 ✅ 必须完善

#### 4.1 创建README.md

```bash
cat > README.md << 'EOF'
# 🚀 DeepFind Agent

<div align="center">

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)

**一个强大的深度调研智能体，支持多场景专业报告生成**

[功能特性](#功能特性) • [快速开始](#快速开始) • [使用文档](#使用文档) • [贡献指南](#贡献指南)

</div>

---

## 📖 简介

DeepFind Agent 是一个**通用深度调研智能体**，具备强大的多源搜索和报告生成能力，专注于三大场景：

1. **产品方案设计** - 输出面向商家后台的产品经理可执行的产品方案
2. **旅游攻略生成** - 输出可直接执行的旅游攻略
3. **行业洞察报告** - 输出互联网/AI圈的最新动态和深度分析

## ✨ 功能特性

### 核心能力
- 🔍 **多源搜索** - Reddit、Hacker News、Google News、电商搜索等
- 🧠 **智能分析** - 趋势分析、竞品对比、情感分析
- 📊 **专业报告** - 产品方案、旅游攻略、行业洞察
- 🔒 **数据安全** - 本地部署，数据不上传

### 三大场景
| 场景 | 输入示例 | 输出价值 |
|------|---------|---------|
| 产品方案设计 | "分析iPhone 15 Pro竞品对比" | 可执行的产品决策建议 |
| 旅游攻略生成 | "纽约4天3晚攻略" | 可直接执行的旅游攻略 |
| 行业洞察报告 | "Claude 3发布对AI行业影响" | 深度行业洞察报告 |

## 🚀 快速开始

### 环境要求
- Python 3.9+
- Node.js 16+（前端）
- 8GB+ RAM

### 安装步骤

#### 1. 克隆项目
\`\`\`bash
git clone https://github.com/yourusername/deepfind-agent.git
cd deepfind-agent
\`\`\`

#### 2. 后端安装
\`\`\`bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
\`\`\`

#### 3. 前端安装
\`\`\`bash
cd frontend
npm install
cd ..
\`\`\`

#### 4. 配置环境变量
\`\`\`bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，填入API Key
vim .env
\`\`\`

#### 5. 启动服务
\`\`\`bash
# 启动后端
python api.py

# 启动前端（另一个终端）
cd frontend && npm run dev
\`\`\`

#### 6. 访问应用
打开浏览器访问: http://localhost:3000

## 📚 使用文档

- [完整文档](docs/)
- [快速开始](test/QUICK_START.md)
- [API文档](docs/API.md)
- [架构设计](docs/DEEPFIND-AGENT-ARCHITECTURE.md)

## 🔧 配置说明

### 必需的API Key
- **DeepSeek API Key** - LLM模型（必需）
- **Tavily API Key** - 搜索服务（必需）

### 可选的API Key（免费）
- **Reddit API Key** - 社区讨论（免费，无限制）
- **Hacker News API** - 技术讨论（免费，无限制）
- **OpenWeatherMap API** - 天气数据（免费，1000次/天）

## 🤝 贡献指南

欢迎贡献！请查看 [贡献指南](CONTRIBUTING.md)

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 后端框架
- [React](https://reactjs.org/) - 前端框架
- [DeepSeek](https://www.deepseek.com/) - LLM模型
- [Tavily](https://tavily.com/) - 搜索服务

## 📞 联系方式

- 作者: Your Name
- 邮箱: your.email@example.com
- GitHub: [@yourusername](https://github.com/yourusername)

---

<div align="center">
Made with ❤️ by DeepFind Team
</div>
EOF
```

#### 4.2 创建LICENSE
```bash
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2026 DeepFind Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
```

#### 4.3 创建CONTRIBUTING.md
```bash
cat > CONTRIBUTING.md << 'EOF'
# 🤝 贡献指南

感谢您考虑为 DeepFind Agent 做出贡献！

## 📋 贡献方式

### 报告Bug
如果您发现了bug，请创建一个issue并包含：
- 问题描述
- 复现步骤
- 预期行为
- 实际行为
- 环境信息（操作系统、Python版本等）

### 提出新功能
如果您有新功能建议，请创建一个issue并包含：
- 功能描述
- 使用场景
- 预期效果

### 提交代码
1. Fork本仓库
2. 创建特性分支 (\`git checkout -b feature/AmazingFeature\`)
3. 提交更改 (\`git commit -m 'Add some AmazingFeature'\`)
4. 推送到分支 (\`git push origin feature/AmazingFeature\`)
5. 创建Pull Request

## 🔧 开发环境设置

\`\`\`bash
# 克隆仓库
git clone https://github.com/yourusername/deepfind-agent.git
cd deepfind-agent

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装开发依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 运行测试
pytest tests/
\`\`\`

## 📝 代码规范

- 遵循PEP 8编码规范
- 使用有意义的变量名
- 添加必要的注释
- 编写单元测试

## 📄 许可证

通过贡献代码，您同意您的代码将在MIT许可证下发布。
EOF
```

---

### 5. 依赖管理 ✅ 必须完善

#### 5.1 检查并更新requirements.txt
```bash
# 生成当前环境的依赖
pip freeze > requirements.txt

# 或者手动编辑requirements.txt，只保留必要的依赖
cat > requirements.txt << 'EOF'
# Core dependencies
fastapi==0.100.0
uvicorn[standard]==0.22.0
python-dotenv==1.0.0
requests==2.31.0
httpx==0.24.1

# LangChain
langchain==0.1.0
langchain-community==0.0.10
langchain-deepseek==0.1.0

# Search
duckduckgo-search==3.9.0
tavily-python==0.3.0

# Data processing
feedparser==6.0.10
beautifulsoup4==4.12.2
lxml==4.9.3

# Optional: Reddit API
praw==7.7.1

# Optional: Weather API
pyowm==3.3.0

# Optional: Data visualization
matplotlib==3.7.2
plotly==5.15.0
EOF
```

#### 5.2 创建requirements-dev.txt（开发依赖）
```bash
cat > requirements-dev.txt << 'EOF'
# Testing
pytest==7.4.0
pytest-cov==4.1.0
pytest-asyncio==0.21.0

# Code quality
black==23.3.0
flake8==6.0.0
mypy==1.4.0

# Documentation
sphinx==7.0.1
sphinx-rtd-theme==1.2.2
EOF
```

---

## 🟡 发布前建议事项（中优先级）

### 6. 版本管理 ✅ 建议配置

#### 6.1 创建版本文件
```bash
cat > VERSION << 'EOF'
v1.0.0
EOF
```

#### 6.2 创建CHANGELOG.md
```bash
cat > CHANGELOG.md << 'EOF'
# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [1.0.0] - 2026-06-30

### Added
- 初始版本发布
- 多源搜索能力（Reddit, Hacker News, Google News）
- 三大场景支持（产品方案、旅游攻略、行业洞察）
- 智能场景分类
- 专业报告生成

### Changed

### Deprecated

### Removed

### Fixed

### Security
EOF
```

---

### 7. GitHub配置 ✅ 建议配置

#### 7.1 创建.github目录
```bash
mkdir -p .github
mkdir -p .github/ISSUE_TEMPLATE
mkdir -p .github/workflows
```

#### 7.2 创建Issue模板
```bash
cat > .github/ISSUE_TEMPLATE/bug_report.md << 'EOF'
---
name: Bug report
about: Create a report to help us improve
title: ''
labels: bug
assignees: ''
---

## 🐛 Bug描述
清晰简洁地描述这个bug。

## 📋 复现步骤
1. 进入 '...'
2. 点击 '....'
3. 滚动到 '....'
4. 看到错误

## ✅ 预期行为
清晰简洁地描述您期望发生的事情。

## ❌ 实际行为
清晰简洁地描述实际发生的事情。

## 📸 截图
如果适用，添加截图以帮助解释您的问题。

## 💻 环境信息
- 操作系统: [例如 macOS, Windows, Linux]
- Python版本: [例如 3.9.0]
- Node.js版本: [例如 16.0.0]
- 浏览器: [例如 Chrome, Safari]

## 📝 其他信息
添加关于此问题的任何其他上下文信息。
EOF

cat > .github/ISSUE_TEMPLATE/feature_request.md << 'EOF'
---
name: Feature request
about: Suggest an idea for this project
title: ''
labels: enhancement
assignees: ''
---

## 💡 功能描述
清晰简洁地描述您想要的功能。

## 🎯 使用场景
描述这个功能的使用场景，为什么需要这个功能。

## 📝 解决方案
描述您希望如何实现这个功能。

## 🔄 替代方案
描述您考虑过的任何替代解决方案或功能。

## 📸 示例
如果有相关的示例或截图，请添加在这里。

## 📝 其他信息
添加关于功能请求的任何其他上下文或截图。
EOF
```

#### 7.3 创建Pull Request模板
```bash
cat > .github/PULL_REQUEST_TEMPLATE.md << 'EOF'
## 📝 更改描述
请清晰简洁地描述所做的更改。

## 🔗 相关Issue
请链接相关的issue，例如：Fixes #123

## 📋 更改类型
请勾选适用的类型：
- [ ] 🐛 Bug修复
- [ ] ✨ 新功能
- [ ] 📝 文档更新
- [ ] 🎨 代码格式/风格调整
- [ ] ♻️ 代码重构
- [ ] ⚡️ 性能优化
- [ ] ✅ 测试相关

## 🧪 测试
请描述您如何测试这些更改：
- [ ] 本地测试通过
- [ ] 单元测试通过
- [ ] 集成测试通过

## 📸 截图（如果适用）
如果更改包含UI更新，请添加截图。

## ✅ 检查清单
- [ ] 我的代码遵循项目的代码规范
- [ ] 我已进行自我审查
- [ ] 我已对代码进行了必要的注释
- [ ] 我已更新相关文档
- [ ] 我的更改没有引入新的警告
- [ ] 我已添加证明修复有效或功能正常的测试
- [ ] 新旧测试均通过

## 📝 其他信息
添加任何其他有助于审核的信息。
EOF
```

---

## 🟢 可选事项（低优先级）

### 8. CI/CD配置（可选）
```bash
cat > .github/workflows/ci.yml << 'EOF'
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python 3.9
      uses: actions/setup-python@v4
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Lint with flake8
      run: |
        # stop the build if there are Python syntax errors or undefined names
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        # exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    
    - name: Test with pytest
      run: |
        pytest tests/ -v --cov=.
EOF
```

---

## ✅ 发布前最终检查清单

### 安全检查
- [ ] 确认`.env`文件已加入`.gitignore`
- [ ] 确认代码中无硬编码的API Key
- [ ] 确认日志文件已加入`.gitignore`
- [ ] 确认虚拟环境已加入`.gitignore`

### 代码检查
- [ ] 删除所有日志文件
- [ ] 删除所有临时文件
- [ ] 删除测试输出文件
- [ ] 移动测试脚本到test目录

### 文档检查
- [ ] README.md完整且准确
- [ ] LICENSE文件存在
- [ ] CONTRIBUTING.md文件存在
- [ ] CHANGELOG.md文件存在
- [ ] .env.example文件存在

### 依赖检查
- [ ] requirements.txt准确且完整
- [ ] requirements-dev.txt准确且完整（如果有）
- [ ] package.json准确且完整（前端）

### Git检查
- [ ] .gitignore配置正确
- [ ] 项目未初始化git（需要初始化）
- [ ] 准备好提交的消息

---

## 🚀 发布流程

### 步骤1: 初始化Git仓库
```bash
cd /Users/purepure/Desktop/docs/deepfind-agent
git init
git add .
git commit -m "🎉 Initial commit: DeepFind Agent v1.0.0"
```

### 步骤2: 创建GitHub仓库
1. 访问 https://github.com/new
2. 填写仓库信息：
   - Repository name: `deepfind-agent`
   - Description: `🚀 一个强大的深度调研智能体，支持多场景专业报告生成`
   - 选择Public
   - 不要勾选"Add a README file"（我们已经有了）
   - 不要勾选"Add .gitignore"（我们已经有了）
   - 选择MIT License（我们已经有了）
3. 点击"Create repository"

### 步骤3: 连接远程仓库并推送
```bash
# 添加远程仓库
git remote add origin https://github.com/yourusername/deepfind-agent.git

# 推送到GitHub
git branch -M main
git push -u origin main
```

### 步骤4: 创建发布标签
```bash
# 创建v1.0.0标签
git tag -a v1.0.0 -m "Release v1.0.0: Initial release"

# 推送标签
git push origin v1.0.0
```

### 步骤5: 在GitHub创建Release
1. 访问 https://github.com/yourusername/deepfind-agent/releases
2. 点击"Draft a new release"
3. 选择标签v1.0.0
4. 填写Release title: `v1.0.0 - Initial Release`
5. 填写Release notes（从CHANGELOG.md复制）
6. 点击"Publish release"

---

## 📊 发布后检查

### GitHub检查
- [ ] 所有文件已正确提交
- [ ] README.md显示正常
- [ ] .env文件未提交（重要！）
- [ ] Releases页面显示v1.0.0

### 功能检查
- [ ] 克隆仓库到新目录测试
- [ ] 按照README.md安装依赖成功
- [ ] 配置.env后能正常启动
- [ ] 所有功能正常运行

---

## 🆘 常见问题

### Q1: 如何撤销提交了敏感文件？
```bash
# 从Git历史中彻底删除文件
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# 强制推送
git push origin --force --all
```

### Q2: 如何处理大文件？
```bash
# 检查大文件
find . -type f -size +50M

# 使用Git LFS管理大文件
git lfs install
git lfs track "*.zip"
git lfs track "*.tar.gz"
```

### Q3: 如何更新GitHub仓库？
```bash
# 添加更改
git add .

# 提交更改
git commit -m "📝 Update: 描述更新内容"

# 推送到GitHub
git push origin main
```

---

**文档版本**: V1.0
**创建时间**: 2026-06-30
**最后更新**: 2026-06-30