# 🚀 快速发布指南

## ⚡ 快速开始（5分钟）

### 1. 运行发布准备脚本
```bash
cd /Users/purepure/Desktop/docs/deepfind-agent
./scripts/prepare_release.sh
```

这个脚本会自动：
- ✅ 检查敏感信息
- ✅ 清理不必要的文件
- ✅ 创建必要的目录
- ✅ 统计项目信息
- ✅ 最终检查

### 2. 手动检查（重要！）
完成自动检查后，手动检查以下内容：

#### 2.1 检查.env文件
```bash
# 确认.env存在且包含API Key
cat .env | grep API_KEY

# 确认.env在.gitignore中
grep "\.env" .gitignore
```

**⚠️ 重要**: `.env`文件**绝对不能**提交到GitHub！

#### 2.2 检查代码中是否有硬编码API Key
```bash
# 搜索代码中是否包含真实的API Key
grep -r "sk-" . --include="*.py" | grep -v ".env"
grep -r "tvly-" . --include="*.py" | grep -v ".env"
```

如果发现硬编码的API Key，**立即删除**！

### 3. 初始化Git仓库并推送
```bash
# 初始化Git仓库
git init

# 添加所有文件
git add .

# 提交
git commit -m "🎉 Initial commit: DeepFind Agent v1.0.0"

# 连接GitHub仓库（替换yourusername为你的GitHub用户名）
git remote add origin https://github.com/yourusername/deepfind-agent.git

# 推送到GitHub
git branch -M main
git push -u origin main

# 创建v1.0.0标签
git tag -a v1.0.0 -m "Release v1.0.0: Initial release"
git push origin v1.0.0
```

---

## 📋 完整检查清单

### ✅ 安全检查（必须）
- [ ] `.env`已在`.gitignore`中
- [ ] 代码中无硬编码API Key
- [ ] 日志文件已在`.gitignore`中
- [ ] 虚拟环境已在`.gitignore`中
- [ ] `.DS_Store`已在`.gitignore`中
- [ ] `outputs/`已在`.gitignore`中

### ✅ 文件检查（必须）
- [ ] `README.md`存在且完整
- [ ] `LICENSE`存在（MIT）
- [ ] `.gitignore`存在且配置正确
- [ ] `.env.example`存在
- [ ] `requirements.txt`存在且准确

### ✅ 清理检查（必须）
- [ ] 所有`.log`文件已删除
- [ ] 所有`.zip`文件已删除
- [ ] `__pycache__/`已删除
- [ ] `.DS_Store`已删除
- [ ] `outputs/`目录已清空

### ✅ 文档检查（推荐）
- [ ] `CONTRIBUTING.md`存在
- [ ] `CHANGELOG.md`存在
- [ ] `docs/RELEASE_CHECKLIST.md`存在
- [ ] `test/`目录结构完整

---

## 🔧 常见问题

### Q1: 运行脚本时提示"Permission denied"
```bash
# 给脚本添加执行权限
chmod +x scripts/prepare_release.sh
```

### Q2: Git提示"fatal: not a git repository"
```bash
# 初始化Git仓库
git init
```

### Q3: 推送时提示"fatal: remote origin already exists"
```bash
# 删除旧的远程仓库
git remote remove origin

# 重新添加
git remote add origin https://github.com/yourusername/deepfind-agent.git
```

### Q4: 不小心提交了.env文件怎么办？
```bash
# 从Git历史中彻底删除.env文件
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# 强制推送
git push origin --force --all

# 重要：立即更换所有API Key！
```

---

## 📚 详细文档

- [完整发布检查清单](RELEASE_CHECKLIST.md)
- [快速开始指南](../test/QUICK_START.md)
- [架构设计](DEEPFIND-AGENT-ARCHITECTURE.md)

---

**文档版本**: V1.0
**创建时间**: 2026-06-30