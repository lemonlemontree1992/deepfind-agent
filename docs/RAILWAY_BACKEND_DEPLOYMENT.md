# 🚀 Railway后端部署详细步骤

**部署平台**: Railway
**部署内容**: DeepFind Agent后端API
**预计时间**: 10-15分钟
**费用**: 免费（$5/月额度）

---

## 📋 部署前准备

### 需要准备的材料
- ✅ GitHub账号（已有：lemonlemontree1992）
- ✅ GitHub仓库：https://github.com/lemonlemontree1992/deepfind-agent
- ✅ DeepSeek API Key（如果没有，访问：https://platform.deepseek.com/）
- ✅ Tavily API Key（如果没有，访问：https://tavily.com/）

### 确认文件存在
在您的GitHub仓库中确认以下文件存在：
- ✅ `Procfile` - Railway启动配置
- ✅ `runtime.txt` - Python版本指定
- ✅ `railway.json` - Railway配置
- ✅ `requirements.txt` - Python依赖

---

## 第一步：注册Railway账号

### 1.1 访问Railway官网
在浏览器中打开：
```
https://railway.app/
```

### 1.2 开始注册
点击页面上的 **"Start a New Project"** 或 **"Login"** 按钮

### 1.3 选择GitHub登录
1. 在登录页面选择 **"Log in with GitHub"**
2. 如果是首次使用，会跳转到GitHub授权页面
3. 点击 **"Authorize Railway"** 授权Railway访问您的GitHub

### 1.4 完成注册
授权后会自动跳回Railway，您会看到Railway的控制面板

---

## 第二步：创建新项目

### 2.1 点击创建项目
在Railway控制面板中：
1. 点击右上角的 **"New Project"** 按钮
2. 或者点击页面中央的 **"+ New Project"**

### 2.2 选择部署方式
在弹出的选项中选择：
```
✅ Deploy from GitHub repo
```

### 2.3 授权访问仓库（首次使用）
如果是第一次使用，可能需要：
1. 点击 **"Configure GitHub App"**
2. 选择 **"Only select repositories"**
3. 勾选 `deepfind-agent` 仓库
4. 点击 **"Save"**

### 2.4 选择仓库
在仓库列表中：
1. 找到 `deepfind-agent` 仓库
2. 确认所有者是 `lemonlemontree1992`
3. 点击 **"Deploy Now"** 按钮

---

## 第三步：配置环境变量（关键步骤）

### 3.1 等待初始化
点击Deploy后，Railway会开始初始化项目：
- 您会看到一个构建日志窗口
- 等待约30秒-1分钟
- 看到提示要求配置环境变量

### 3.2 进入变量设置
在项目页面：
1. 点击顶部的 **"Variables"** 标签
2. 或者点击 **"Add Variables"** 按钮

### 3.3 添加环境变量（两种方式）

#### 方式A：可视化添加（推荐新手）
点击 **"Add Variable"**，逐个添加：

**变量1：DeepSeek API Key**
- Name: `DEEPSEEK_API_KEY`
- Value: `sk-xxxxxxxxxxxxxxxxxxxxxxxx`
（替换为您的真实DeepSeek API Key）

**变量2：Tavily API Key**
- Name: `TAVILY_API_KEY`
- Value: `tvly-dev-xxxxxxxxxxxxxxxxxxxxxxxx`
（替换为您的真实Tavily API Key）

**变量3：环境标识**
- Name: `ENV`
- Value: `production`

**变量4：跨域配置（暂时设为*）**
- Name: `ALLOWED_ORIGINS`
- Value: `*`

#### 方式B：Raw Editor（快速）
1. 点击 **"Raw Editor"** 按钮
2. 粘贴以下内容（**替换为您的真实API Key**）：

```bash
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TAVILY_API_KEY=tvly-dev-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ENV=production
ALLOWED_ORIGINS=*
```

3. 点击 **"Update Variables"**

### 3.4 确认变量已添加
在Variables页面应该看到4个变量：
```
✅ DEEPSEEK_API_KEY
✅ TAVILY_API_KEY
✅ ENV
✅ ALLOWED_ORIGINS
```

---

## 第四步：启动部署

### 4.1 开始部署
添加环境变量后，Railway会自动开始部署：
- 如果没有自动部署，点击 **"Deployments"** 标签
- 点击 **"Redeploy"** 或 **"Deploy"** 按钮

### 4.2 查看构建日志
在部署过程中，您会看到构建日志：
```
Installing dependencies from Pipfile.lock...
...
Successfully installed...
...
Starting deployment...
...
✅ Deployment successful
```

**预计时间**: 2-3分钟

### 4.3 等待部署完成
部署过程包含以下步骤：
1. ✅ 检测运行环境（自动识别Python）
2. ✅ 安装Python 3.11.4（由runtime.txt指定）
3. ✅ 安装依赖包（从requirements.txt）
4. ✅ 启动应用（执行Procfile中的命令）
5. ✅ 健康检查

**成功标志**：
- 看到 ✅ 绿色对勾
- Status显示为 **"SUCCESS"**
- 日志最后显示：`Application startup complete`

### 4.4 如果部署失败
**常见错误**：

**错误1：找不到requirements.txt**
```
解决方案：确认requirements.txt在仓库根目录
```

**错误2：Python版本不兼容**
```
解决方案：检查runtime.txt内容是否为：python-3.11.4
```

**错误3：依赖安装失败**
```
解决方案：查看具体错误日志
可能是某个包版本问题，需要在requirements.txt中调整
```

**错误4：启动命令失败**
```
解决方案：确认Procfile内容为：
web: uvicorn api:app --host 0.0.0.0 --port $PORT
```

---

## 第五步：生成域名

### 5.1 进入设置
部署成功后：
1. 在项目页面点击 **"Settings"** 标签
2. 向下滚动找到 **"Domains"** 部分

### 5.2 生成域名
在Domains部分：
1. 点击 **"Generate Domain"** 按钮
2. Railway会自动生成一个域名，格式如：
   ```
   deepfind-agent-production-abc123.up.railway.app
   ```

**或者使用自定义域名**：
1. 点击 **"Add Custom Domain"**
2. 输入您的域名，如：`api.deepfind-agent.com`
3. 按照提示配置DNS记录

### 5.3 复制域名URL
**重要！复制您的域名URL**
```
https://deepfind-agent-production-xxxxxxxx.up.railway.app
```
这个URL就是您的后端API地址，前端部署时需要用到。

---

## 第六步：验证部署

### 6.1 测试根路径
在浏览器中访问您的域名：
```
https://your-url.up.railway.app/
```

**期望结果**：
```json
{
  "name": "DeepFind Agent API",
  "version": "1.0.0",
  "status": "running"
}
```

### 6.2 测试健康检查
访问健康检查端点：
```
https://your-url.up.railway.app/health
```

**期望结果**：
```json
{
  "status": "healthy",
  "api_keys": {
    "deepseek": true,
    "tavily": true
  }
}
```

**如果看到**：
```json
{
  "status": "degraded",
  "issues": ["DeepSeek API Key 未配置"]
}
```
表示环境变量配置有误，请检查：
- Variables中的API Key是否正确
- 是否有多余的空格或引号

### 6.3 测试API文档
访问FastAPI自动生成的API文档：
```
https://your-url.up.railway.app/docs
```

您应该能看到完整的API文档界面，包括：
- `/health` - 健康检查
- `/` - 根路径
- `/api/research/stream` - 流式调研接口
- `/api/sessions/{id}` - 会话管理
- 等等...

---

## 第七步：配置监控（可选）

### 7.1 查看日志
在项目页面：
1. 点击 **"Deployments"** 标签
2. 点击最新的部署记录
3. 点击 **"View Logs"**

您可以看到：
- 实时请求日志
- 错误日志
- 应用启动日志

### 7.2 设置告警（可选）
Railway支持设置部署告警：
1. Settings → Notifications
2. 添加Slack或Email通知
3. 设置告警触发条件

### 7.3 查看指标
在 **"Metrics"** 标签可以看到：
- CPU使用率
- 内存使用率
- 网络流量
- 请求次数

---

## 🎉 部署成功！

### 您的后端URL
```
https://deepfind-agent-production-xxxxxxxx.up.railway.app
```

### 可用的端点
- 根路径: `https://your-url/`
- 健康检查: `https://your-url/health`
- API文档: `https://your-url/docs`
- 流式调研: `https://your-url/api/research/stream`

### 下一步
现在您可以：
1. ✅ 记录您的后端URL
2. 🚀 部署前端到Vercel（使用这个URL）
3. 🔗 更新跨域配置（ALLOWED_ORIGINS）

---

## ❓ 常见问题

### Q1: 部署一直失败怎么办？
**检查步骤**：
1. 查看构建日志具体错误信息
2. 确认requirements.txt在根目录
3. 确认Procfile内容正确
4. 确认runtime.txt指定Python版本
5. 检查Python依赖版本兼容性

### Q2: 部署成功但无法访问？
**可能原因**：
1. 端口配置错误（应使用$PORT变量）
2. 健康检查失败（查看日志）
3. 应用启动报错
4. 环境变量未正确设置

### Q3: 如何更新代码？
**更新流程**：
1. 修改代码并提交到GitHub
2. Railway会自动检测并重新部署
3. 或者手动点击"Redeploy"

### Q4: 如何查看实时日志？
**查看方法**：
1. 进入项目页面
2. 点击"Deployments"
3. 点击最新部署
4. 点击"View Logs"

### Q5: 如何重启服务？
**重启方法**：
1. 进入项目页面
2. 点击"Deployments"
3. 点击"Redeploy"

### Q6: 免费额度够用吗？
**免费额度**：
- Railway提供$5/月免费额度
- 约等于500小时运行时间
- 个人使用完全够用
- 可以设置额度告警避免超支

### Q7: 如何绑定自定义域名？
**绑定步骤**：
1. Settings → Domains
2. 点击"Add Custom Domain"
3. 输入域名（如：api.deepfind-agent.com）
4. 按照提示添加DNS记录
5. 等待DNS生效（几分钟到几小时）

---

## 📊 部署状态检查清单

完成以下检查确认部署成功：

- [ ] Railway账号已注册
- [ ] 项目已创建
- [ ] GitHub仓库已连接
- [ ] 环境变量已配置（4个）
  - [ ] DEEPSEEK_API_KEY
  - [ ] TAVILY_API_KEY
  - [ ] ENV=production
  - [ ] ALLOWED_ORIGINS=*
- [ ] 构建成功（绿色对勾）
- [ ] 域名已生成
- [ ] 根路径访问正常
- [ ] 健康检查正常
- [ ] API文档可以访问
- [ ] 已复制后端URL

---

## 🔗 相关链接

- **Railway官网**: https://railway.app/
- **Railway文档**: https://docs.railway.app/
- **您的GitHub仓库**: https://github.com/lemonlemontree1992/deepfind-agent
- **DeepSeek API**: https://platform.deepseek.com/
- **Tavily API**: https://tavily.com/

---

## 📞 需要帮助？

部署过程中遇到问题：
1. 查看Railway构建日志
2. 检查环境变量是否正确
3. 参考 `docs/DEPLOYMENT_GUIDE.md`
4. 或者告诉我具体错误信息，我会帮您解决

---

**祝您部署顺利！🎉**

下一步：部署前端到Vercel（使用您刚刚获得的后端URL）