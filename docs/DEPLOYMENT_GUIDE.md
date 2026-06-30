# 🚀 DeepFind Agent 部署指南

**部署方案**: 完全免费部署到云服务器
**预计时间**: 30分钟
**平台**: Railway (后端) + Vercel (前端)

---

## 📋 部署架构

```
┌─────────────────┐         ┌─────────────────┐
│   Vercel        │         │   Railway       │
│   (前端)        │ ──────> │   (后端API)     │
│   React应用     │  HTTPS  │   FastAPI应用   │
└─────────────────┘         └─────────────────┘
        │                            │
        │                            │
   用户访问                    调用LLM API
        ▼                            ▼
  https://xxx.vercel.app    https://xxx.railway.app
```

### 为什么选择这个方案？

| 平台 | 免费额度 | 优点 |
|------|---------|------|
| **Railway** | $5/月免费额度 | • 自动从GitHub部署<br>• 支持环境变量<br>• 自动SSL证书<br>• 支持Python |
| **Vercel** | 无限免费 | • 自动从GitHub部署<br>• 全球CDN<br>• 自动SSL证书<br>• 支持React |

---

## 第一步：部署后端到Railway

### 1.1 注册Railway账号
1. 访问：https://railway.app/
2. 点击 **"Start a New Project"**
3. 选择 **"Log in with GitHub"**
4. 授权Railway访问您的GitHub

### 1.2 创建新项目
1. 点击 **"New Project"**
2. 选择 **"Deploy from GitHub repo"**
3. 选择 `deepfind-agent` 仓库
4. 点击 **"Deploy Now"**

### 1.3 配置环境变量
在Railway项目设置中添加环境变量：

```bash
# 必需的环境变量
DEEPSEEK_API_KEY=your_deepseek_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

# 可选的环境变量
SEARCH_DEPTH=deep
DEFAULT_LANGUAGE=zh
MAX_SEARCH_RESULTS=10
```

**添加步骤：**
1. 在Railway项目页面点击 **"Variables"**
2. 点击 **"Raw Editor"**
3. 粘贴上面的环境变量（填入真实的API Key）
4. 点击 **"Update Variables"**

### 1.4 配置启动命令
Railway会自动检测FastAPI，但需要确认启动命令：

**方式A：创建Procfile（推荐）**
在项目根目录创建 `Procfile` 文件：
```
web: uvicorn api:app --host 0.0.0.0 --port $PORT
```

**方式B：在Railway设置中配置**
1. 点击 **"Settings"**
2. 找到 **"Start Command"**
3. 填入：`uvicorn api:app --host 0.0.0.0 --port $PORT`

### 1.5 部署后端
1. 点击 **"Deploy"**
2. 等待构建完成（约2-3分钟）
3. 部署成功后会看到一个URL，如：
   ```
   https://deepfind-agent-production-xxx.up.railway.app
   ```

### 1.6 测试后端
访问后端URL的健康检查端点：
```
https://your-backend-url.railway.app/health
```

应该返回：
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

## 第二步：部署前端到Vercel

### 2.1 注册Vercel账号
1. 访问：https://vercel.com/
2. 点击 **"Sign Up"**
3. 选择 **"Continue with GitHub"**
4. 授权Vercel访问您的GitHub

### 2.2 导入项目
1. 点击 **"Add New..."** → **"Project"**
2. 在Import Git Repository中找到 `deepfind-agent`
3. 点击 **"Import"**

### 2.3 配置项目
**重要配置项：**

1. **Framework Preset**: 选择 `Create React App` 或自动检测

2. **Root Directory**: 设置为 `frontend`
   - 点击 **"Edit"**
   - 选择 `frontend` 文件夹

3. **Build Command**: 使用默认或设置为
   ```
   npm run build
   ```

4. **Output Directory**: 设置为
   ```
   dist
   ```

### 2.4 配置环境变量
在Vercel项目设置中添加环境变量：

```bash
# 后端API地址（替换为您的Railway后端URL）
VITE_API_URL=https://your-backend-url.railway.app
```

**添加步骤：**
1. 展开 **"Environment Variables"**
2. Name: `VITE_API_URL`
3. Value: 填入您的Railway后端URL
4. 点击 **"Add"**

### 2.5 部署前端
1. 点击 **"Deploy"**
2. 等待构建完成（约1-2分钟）
3. 部署成功后会看到一个URL，如：
   ```
   https://deepfind-agent.vercel.app
   ```

### 2.6 测试前端
访问前端URL，应该能看到DeepFind Agent的界面。

---

## 第三步：配置前端连接后端

### 3.1 修改前端配置文件

检查 `frontend/src/config/api.ts` 或类似文件，确保API地址配置正确：

```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

### 3.2 在Vercel中更新后端URL
如果需要修改后端URL：
1. 进入Vercel项目 → **Settings** → **Environment Variables**
2. 修改 `VITE_API_URL` 的值
3. 点击 **"Save"**
4. 触发重新部署：**Deployments** → 最新部署 → **Redeploy**

---

## 第四步：验证部署

### 4.1 后端验证清单
- [ ] 访问 `https://your-backend-url/health` 返回正常
- [ ] 访问 `https://your-backend-url/docs` 能看到API文档
- [ ] 测试搜索接口返回数据

### 4.2 前端验证清单
- [ ] 访问前端URL能显示界面
- [ ] 输入搜索关键词能正常工作
- [ ] 能看到实时流式输出
- [ ] 能下载生成的报告

### 4.3 完整流程测试
1. 访问前端URL
2. 输入测试关键词：`分析iPhone 15 Pro竞品对比`
3. 点击开始调研
4. 查看是否能正常返回结果

---

## 第五步：绑定自定义域名（可选）

### 5.1 在Vercel绑定域名
1. 进入项目 → **Settings** → **Domains**
2. 添加您的域名：`deepfind-agent.com`
3. 在域名服务商处添加DNS记录：
   ```
   类型: A
   名称: @
   值: 76.76.21.21
   ```

### 5.2 在Railway绑定域名
1. 进入项目 → **Settings** → **Domains**
2. 添加自定义域名：`api.deepfind-agent.com`
3. 在域名服务商处添加CNAME记录

---

## 🔧 常见问题

### Q1: Railway部署失败
**检查项**：
- 确认 `requirements.txt` 在根目录
- 确认Python版本兼容（requirements.txt中指定）
- 查看Railway日志排查错误

**解决方案**：
在 `requirements.txt` 第一行添加：
```
python>=3.9,<3.12
```

### Q2: 前端无法连接后端
**检查项**：
- 确认Vercel环境变量 `VITE_API_URL` 正确
- 确认后端URL可访问
- 检查浏览器控制台的CORS错误

**解决方案**：
在后端 `api.py` 中添加CORS配置：
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Q3: 后端响应慢
**解决方案**：
- Railway免费套餐会休眠，首次访问需等待
- 升级到Railway Pro套餐（$5/月）可获得更稳定性能

### Q4: 如何查看日志
**Railway**：
- 进入项目 → **Deployments** → 点击部署 → **View Logs**

**Vercel**：
- 进入项目 → **Deployments** → 点击部署 → **Functions** → **Logs**

---

## 💰 费用说明

### 免费套餐限制
- **Railway**: $5/月免费额度，约500小时运行时间
- **Vercel**: 无限免费，但带宽有限制（100GB/月）

### 预计费用
- **个人使用**: 完全免费
- **小团队使用**: 基本免费
- **大量用户**: 可能需升级付费套餐

### 升级建议
如果免费额度不够：
- Railway Pro: $20/月
- Vercel Pro: $20/月

---

## 🎯 下一步

部署完成后：

1. **测试应用**：完整测试所有功能
2. **监控日志**：观察是否有错误
3. **优化配置**：根据使用情况调整
4. **添加域名**：绑定自定义域名
5. **开启监控**：设置错误告警

---

**部署时间**: 2026-06-30
**预计时长**: 30分钟
**费用**: 完全免费