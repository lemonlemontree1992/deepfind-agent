# 🚀 快速部署指南

**项目**: DeepFind Agent
**部署方式**: Railway（后端）+ Vercel（前端）
**费用**: 完全免费
**预计时间**: 30分钟

---

## ✅ 前置准备

在开始部署前，请确保：
- ✅ GitHub仓库已创建：https://github.com/lemonlemontree1992/deepfind-agent
- ✅ API Key已准备好：
  - DeepSeek API Key（必需）
  - Tavily API Key（必需）

---

## 📦 第一步：部署后端到Railway（后端API）

### 1.1 注册Railway账号

1. 访问：**https://railway.app/**
2. 点击 **"Start a New Project"**
3. 选择 **"Log in with GitHub"**
4. 授权Railway访问您的GitHub账号

### 1.2 创建新项目

1. 点击 **"New Project"** 按钮
2. 选择 **"Deploy from GitHub repo"**
3. 在列表中找到 **`deepfind-agent`**
4. 点击 **"Deploy Now"**

### 1.3 添加环境变量（关键步骤）

在Railway项目页面：

1. 点击 **"Variables"** 标签
2. 点击 **"Raw Editor"**（原文编辑器）
3. 粘贴以下内容（**替换为您的真实API Key**）：

```bash
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
TAVILY_API_KEY=tvly-dev-xxxxxxxxxxxxxxxxxxxxxxxx
ENV=production
ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

**重要**：
- `DEEPSEEK_API_KEY` 和 `TAVILY_API_KEY` 必须是真实的API Key
- `ALLOWED_ORIGINS` 先填 `*`（稍后更新为前端URL）

4. 点击 **"Update Variables"**

### 1.4 部署后端

1. Railway会自动检测到 `Procfile` 和 `runtime.txt`
2. 点击 **"Deploy"** 或等待自动部署
3. 等待构建完成（约2-3分钟）
4. 看到 ✅ 表示部署成功

### 1.5 获取后端URL

1. 在项目页面点击 **"Settings"**
2. 找到 **"Domains"** 部分
3. 点击 **"Generate Domain"**
4. 您会得到一个URL，格式如：
   ```
   https://deepfind-agent-production-abc123.up.railway.app
   ```
5. **复制这个URL**，后面需要用到

### 1.6 测试后端

在浏览器中访问：
```
https://your-backend-url.railway.app/health
```

应该看到类似：
```json
{
  "status": "healthy",
  "api_keys": {
    "deepseek": true,
    "tavily": true
  }
}
```

---

## 🌐 第二步：部署前端到Vercel（React应用）

### 2.1 注册Vercel账号

1. 访问：**https://vercel.com/**
2. 点击 **"Sign Up"**
3. 选择 **"Continue with GitHub"**
4. 授权Vercel访问您的GitHub账号

### 2.2 导入项目

1. 登录后点击 **"Add New..."** → **"Project"**
2. 在 **"Import Git Repository"** 中找到 `deepfind-agent`
3. 点击 **"Import"**

### 2.3 配置项目（重要步骤）

在 **"Configure Project"** 页面：

#### 基本配置
- **Framework Preset**: 自动检测（`Create React App` 或 `Other`）
- **Root Directory**: 点击 **"Edit"**，选择 **`frontend`** 文件夹

#### 构建配置
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Install Command**: `npm install`

#### 环境变量配置
1. 展开 **"Environment Variables"** 部分
2. 添加以下环境变量：

```
Name: VITE_API_BASE_URL
Value: https://your-backend-url.railway.app
```

**重要**：
- 将 `https://your-backend-url.railway.app` 替换为第一步获取的后端URL
- 不要在URL末尾加 `/`

### 2.4 部署前端

1. 确认所有配置正确
2. 点击 **"Deploy"** 按钮
3. 等待构建完成（约1-2分钟）
4. 看到 🎉 表示部署成功

### 2.5 获取前端URL

部署成功后，Vercel会显示一个URL，格式如：
```
https://deepfind-agent-xyz.vercel.app
```

**复制这个URL**，下一步需要用到。

---

## 🔗 第三步：配置跨域访问（重要）

### 3.1 更新Railway环境变量

回到Railway项目页面：

1. 点击 **"Variables"** 标签
2. 编辑 `ALLOWED_ORIGINS` 变量
3. 将值改为您的前端URL：
   ```
   https://your-frontend.vercel.app
   ```
4. 点击 **"Update Variables"**
5. Railway会自动重新部署

### 3.2 验证配置

等待Railway重新部署完成后（约1分钟），前端应该能正常访问后端API。

---

## ✅ 第四步：验证部署

### 4.1 测试后端API

在浏览器访问：
```
https://your-backend-url.railway.app/
```

应该看到：
```json
{
  "name": "DeepFind Agent API",
  "version": "1.0.0",
  "status": "running"
}
```

访问API文档：
```
https://your-backend-url.railway.app/docs
```

### 4.2 测试前端界面

在浏览器访问您的前端URL：
```
https://your-frontend.vercel.app
```

应该能看到DeepFind Agent的界面。

### 4.3 完整功能测试

1. 在前端界面输入测试关键词：
   ```
   分析iPhone 15 Pro竞品对比
   ```
2. 点击 **"开始调研"**
3. 观察是否能正常搜索和生成报告
4. 检查是否能正常下载报告

---

## 🎉 部署成功！

### 您的应用地址

- **前端**：https://your-frontend.vercel.app
- **后端**：https://your-backend-url.railway.app
- **API文档**：https://your-backend-url.railway.app/docs

### 分享给用户

现在您可以：
1. 分享前端URL给用户使用
2. 在GitHub仓库首页添加链接
3. 绑定自定义域名（可选）

---

## 📊 监控和维护

### 查看日志

**Railway日志**：
1. 进入项目页面
2. 点击 **"Deployments"**
3. 点击最新的部署
4. 点击 **"View Logs"**

**Vercel日志**：
1. 进入项目页面
2. 点击 **"Deployments"**
3. 点击最新的部署
4. 点击 **"Functions"** → **"Logs"**

### 环境变量管理

**更新API Key**：
- Railway → Variables → 编辑对应的变量

**更新前端配置**：
- Vercel → Settings → Environment Variables → 编辑并重新部署

---

## ❓ 常见问题

### Q1: 后端部署失败
**检查**：
- 确认 `requirements.txt` 在根目录
- 确认 `Procfile` 存在且有正确内容
- 查看Railway日志排查错误

### Q2: 前端无法连接后端
**检查**：
- Vercel环境变量 `VITE_API_BASE_URL` 是否正确
- Railway环境变量 `ALLOWED_ORIGINS` 是否包含前端URL
- 后端URL是否可以访问（尝试在浏览器打开）

### Q3: API Key无效
**检查**：
- 确认DeepSeek和Tavily的API Key有效
- 确认API Key没有过期
- 检查Railway环境变量是否正确设置

### Q4: 前端页面空白
**检查**：
- 浏览器控制台是否有错误
- 前端是否正确构建（Vercel日志）
- API地址是否配置正确

---

## 💰 费用说明

### 免费套餐
- **Railway**: $5/月免费额度，约500小时
- **Vercel**: 无限免费，100GB带宽/月

### 预估费用
- **个人使用**: 完全免费
- **小团队**: 基本免费
- **大量用户**: 可能需要升级付费套餐

---

## 🔄 更新部署

当代码更新后，部署流程：

1. **推送代码到GitHub**：
   ```bash
   git add .
   git commit -m "更新说明"
   git push origin main
   ```

2. **自动部署**：
   - Railway会自动检测并重新部署后端
   - Vercel会自动检测并重新部署前端

3. **手动触发**（如果自动部署失败）：
   - Railway: Deployments → 点击 "Redeploy"
   - Vercel: Deployments → 点击 "Redeploy"

---

## 📞 需要帮助？

如果遇到问题：
1. 查看完整部署文档：`docs/DEPLOYMENT_GUIDE.md`
2. 检查Railway和Vercel的日志
3. 在GitHub创建Issue

---

**祝您部署顺利！🎉**