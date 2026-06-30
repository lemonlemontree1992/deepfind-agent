# 🤝 贡献指南

感谢您考虑为 DeepFind Agent 做出贡献！

---

## 📋 目录

- [行为准则](#行为准则)
- [我能贡献什么](#我能贡献什么)
- [开发环境设置](#开发环境设置)
- [提交代码](#提交代码)
- [代码规范](#代码规范)
- [问题反馈](#问题反馈)

---

## 行为准则

本项目采用贡献者公约作为行为准则。参与此项目即表示您同意遵守其条款。请阅读 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) 了解详情。

---

## 我能贡献什么

### 🐛 报告Bug

如果您发现了bug，请创建一个issue并包含：

- **问题描述**: 清晰简洁地描述bug
- **复现步骤**: 详细的步骤让我们重现问题
- **预期行为**: 您期望发生什么
- **实际行为**: 实际发生了什么
- **环境信息**: 操作系统、Python版本、Node.js版本等
- **截图**: 如果适用，添加截图帮助解释问题

**Bug报告模板**:
\`\`\`markdown
## 🐛 Bug描述
[清晰简洁地描述bug]

## 📋 复现步骤
1. 进入 '...'
2. 点击 '....'
3. 滚动到 '....'
4. 看到错误

## ✅ 预期行为
[描述您期望发生的事情]

## ❌ 实际行为
[描述实际发生的事情]

## 💻 环境信息
- 操作系统: [例如 macOS, Windows, Linux]
- Python版本: [例如 3.9.0]
- Node.js版本: [例如 16.0.0]
- 浏览器: [例如 Chrome, Safari]

## 📸 截图
[如果适用，添加截图]

## 📝 其他信息
[添加关于此问题的任何其他上下文]
\`\`\`

---

### 💡 提出新功能

如果您有新功能建议，请创建一个issue并包含：

- **功能描述**: 清晰简洁地描述功能
- **使用场景**: 描述这个功能的使用场景
- **预期效果**: 描述您希望如何工作
- **替代方案**: 描述您考虑过的任何替代解决方案

**功能建议模板**:
\`\`\`markdown
## 💡 功能描述
[清晰简洁地描述您想要的功能]

## 🎯 使用场景
[描述这个功能的使用场景]

## 📝 解决方案
[描述您希望如何实现这个功能]

## 🔄 替代方案
[描述您考虑过的任何替代解决方案]

## 📸 示例
[如果有相关的示例或截图，请添加]

## 📝 其他信息
[添加关于功能请求的任何其他上下文]
\`\`\`

---

### 📝 完善文档

文档改进包括：

- 修正拼写或语法错误
- 添加缺失的文档
- 改进现有文档的清晰度
- 翻译文档到其他语言

---

### 💻 提交代码

#### 开发环境设置

\`\`\`bash
# 1. Fork本仓库
# 点击GitHub页面右上角的"Fork"按钮

# 2. 克隆您的Fork
git clone https://github.com/yourusername/deepfind-agent.git
cd deepfind-agent

# 3. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

# 4. 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 5. 安装前端依赖
cd frontend
npm install
cd ..

# 6. 配置环境变量
cp .env.example .env
# 编辑.env文件，填入API Key

# 7. 运行测试
pytest tests/

# 8. 启动开发服务器
python api.py
\`\`\`

#### 代码规范

##### Python代码规范
- 遵循 [PEP 8](https://pep8.org/) 编码规范
- 使用有意义的变量名和函数名
- 添加必要的注释和文档字符串
- 编写单元测试

**示例**:
\`\`\`python
def get_llm(model: str, temperature: float = 0.7) -> ChatDeepSeek:
    """
    获取LLM实例
    
    Args:
        model: 模型名称
        temperature: 温度参数 (0.0-1.0)
    
    Returns:
        ChatDeepSeek: LLM实例
    
    Raises:
        ValueError: 如果model为空
    """
    if not model:
        raise ValueError("model不能为空")
    
    return ChatDeepSeek(
        model=model,
        temperature=temperature,
        api_key=settings.deepseek_api_key
    )
\`\`\`

##### JavaScript/TypeScript代码规范
- 使用ESLint和Prettier
- 使用TypeScript类型注解
- 遵循React Hooks规范
- 编写组件测试

**示例**:
\`\`\`typescript
interface SearchBarProps {
  onSearch: (query: string) => void;
  placeholder?: string;
}

export const SearchBar: React.FC<SearchBarProps> = ({ 
  onSearch, 
  placeholder = "搜索..." 
}) => {
  const [query, setQuery] = useState<string>('');
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={placeholder}
      />
    </form>
  );
};
\`\`\`

---

## 提交代码

### Git提交规范

我们使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

\`\`\`
<type>(<scope>): <subject>

<body>

<footer>
\`\`\`

#### Type类型
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式（不影响代码运行的变动）
- `refactor`: 重构（既不是新增功能，也不是修改bug的代码变动）
- `perf`: 性能优化
- `test`: 增加测试
- `chore`: 构建过程或辅助工具的变动

#### 示例

\`\`\`bash
# 新功能
git commit -m "feat(search): 添加DuckDuckGo搜索支持"

# Bug修复
git commit -m "fix(api): 修复流式输出中断问题"

# 文档更新
git commit -m "docs(readme): 更新安装说明"

# 重构
git commit -m "refactor(agent): 重构搜索Agent逻辑"
\`\`\`

---

### Pull Request流程

1. **Fork仓库** 并创建特性分支
   \`\`\`bash
   git checkout -b feature/amazing-feature
   \`\`\`

2. **提交更改**
   \`\`\`bash
   git add .
   git commit -m "feat: 添加某个新功能"
   \`\`\`

3. **推送到您的Fork**
   \`\`\`bash
   git push origin feature/amazing-feature
   \`\`\`

4. **创建Pull Request**
   - 访问您的Fork页面
   - 点击"New Pull Request"
   - 填写PR标题和描述
   - 提交PR

#### Pull Request模板

\`\`\`markdown
## 📝 更改描述
请清晰简洁地描述所做的更改。

## 🔗 相关Issue
Fixes #(issue number)

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
\`\`\`

---

## 问题反馈

### 创建Issue

在创建Issue之前，请：

1. **搜索现有Issue** - 确保问题尚未被报告
2. **使用Issue模板** - 选择合适的模板（Bug报告或功能请求）
3. **提供详细信息** - 包括环境信息、复现步骤等

### Issue标签

我们使用以下标签：

- `bug` - Bug报告
- `enhancement` - 新功能请求
- `documentation` - 文档相关
- `good first issue` - 适合新贡献者
- `help wanted` - 需要帮助
- `question` - 问题咨询

---

## 开发提示

### 运行测试

\`\`\`bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_search.py

# 运行测试并生成覆盖率报告
pytest --cov=. tests/
\`\`\`

### 代码格式化

\`\`\`bash
# Python代码格式化
black .
isort .

# JavaScript/TypeScript代码格式化
cd frontend
npm run format
\`\`\`

### 类型检查

\`\`\`bash
# Python类型检查
mypy .

# TypeScript类型检查
cd frontend
npm run type-check
\`\`\`

---

## 许可证

通过贡献代码，您同意您的代码将在MIT许可证下发布。

---

## 🙏 感谢

感谢所有贡献者的付出！您的每一个贡献都让这个项目变得更好。

---

**问题？**

如果您有任何问题，请：
- 查看 [文档](docs/)
- 搜索 [Issues](https://github.com/yourusername/deepfind-agent/issues)
- 创建新的 [Issue](https://github.com/yourusername/deepfind-agent/issues/new)