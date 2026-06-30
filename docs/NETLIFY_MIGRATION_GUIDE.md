# Netlify 部署指南

## 为什么选择 Netlify？

✅ **更好的全球访问** - 在亚洲地区访问速度通常优于 Vercel
✅ **完全免费** - 个人项目永久免费
✅ **自动部署** - GitHub 集成，推送自动部署
✅ **简单配置** - 无需复杂配置文件

---

## 📋 部署步骤

### 第一步：登录 Netlify

1. 访问：https://app.netlify.com
2. 点击 "Sign up" 或 "Log in"
3. 选择 "GitHub" 登录（推荐）

### 第二步：导入项目

1. 登录后，点击 "Add new site" → "Import an existing project"
2. 选择 "GitHub"
3. 找到并选择 `deepfind-agent` 仓库
4. 如果看不到仓库，点击 "Configure the Netlify app on GitHub"

### 第三步：配置构建设置

**关键配置：**

```
Base directory: frontend
Build command: npm run build
Publish directory: frontend/dist
```

**详细步骤：**

1. **Base directory**（基础目录）
   - 输入：`frontend`
   - 这是告诉 Netlify 前端代码在 frontend 文件夹

2. **Build command**（构建命令）
   - 输入：`npm run build`
   - 或使用默认的自动检测

3. **Publish directory**（发布目录）
   - 输入：`frontend/dist`
   - 这是构建输出的目录

### 第四步：环境变量配置

点击 "Advanced" → "Add environment variable"

```
Key: VITE_API_BASE_URL
Value: https://deepfind-agent.onrender.com
```

### 第五步：部署

1. 点击 "Deploy site"
2. 等待 1-3 分钟
3. 部署完成后会获得一个 URL（类似 `https://random-name.netlify.app`）

---

## 🧪 部署后测试

部署完成后，访问提供的 URL，应该能看到：

1. ✅ 前端界面正常显示
2. ✅ 可以输入查询
3. ✅ 后端 API 连接正常

---

## 🔄 自定义域名（可选）

如果需要自定义域名：

1. 在 Netlify 项目页面，点击 "Domain settings"
2. 点击 "Add custom domain"
3. 输入您的域名
4. 按照提示配置 DNS

---

## 📊 Netlify vs Vercel 对比

| 功能 | Netlify | Vercel |
|------|---------|--------|
| 免费额度 | ✅ 无限制 | ✅ 无限制 |
| 全球 CDN | ✅ 优秀 | ✅ 优秀 |
| 亚洲访问 | ✅ 更快 | ⚠️ 可能受限 |
| 部署速度 | ✅ 1-3 分钟 | ✅ 1-3 分钟 |
| 配置复杂度 | ✅ 简单 | ⚠️ 稍复杂 |
| GitHub 集成 | ✅ 支持 | ✅ 支持 |

---

## 🚨 常见问题

### Q1: 构建失败怎么办？

**检查清单：**
- [ ] Base directory 设置为 `frontend`
- [ ] Build command 是 `npm run build`
- [ ] Publish directory 是 `frontend/dist`
- [ ] Node.js 版本兼容（Netlify 默认使用最新稳定版）

### Q2: 页面空白怎么办？

**可能原因：**
1. JavaScript 文件路径错误
2. 环境变量未设置

**解决方案：**
- 检查环境变量 `VITE_API_BASE_URL` 是否设置
- 检查浏览器控制台错误信息

### Q3: 无法连接后端？

**检查：**
- 后端 URL 是否正确：`https://deepfind-agent.onrender.com`
- CORS 配置是否正确（已在后端配置）

---

## 📝 部署检查清单

在 Netlify 部署前确认：

- [ ] GitHub 仓库已更新（包含最新代码）
- [ ] `frontend/dist` 目录存在（本地构建测试）
- [ ] `vercel.json` 配置正确（或删除它）
- [ ] 准备好环境变量 `VITE_API_BASE_URL`

在 Netlify 部署时确认：

- [ ] Base directory: `frontend` ✅
- [ ] Build command: `npm run build` ✅
- [ ] Publish directory: `frontend/dist` ✅
- [ ] Environment variable 已添加 ✅

---

## 🎯 下一步

1. **立即部署到 Netlify**
2. 测试新 URL 是否可以访问
3. 如果成功，可以删除 Vercel 项目

---

**预计部署时间**: 5-10 分钟
**支持文档**: https://docs.netlify.com