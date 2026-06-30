# 🚀 方案A部署完整指南：Vercel + Render（完全免费）

**部署方案**: Vercel（前端）+ Render（后端）
**总费用**: $0/月
**需要信用卡**: ❌ 不需要
**预计时间**: 20-30分钟

---

## 📦 部署架构

```
用户访问
    ↓
Vercel (前端React应用)
https://your-app.vercel.app
    ↓
Render (后端FastAPI应用)
https://your-app.onrender.com
    ↓
DeepSeek API / Tavily API
```

---

## ✅ 部署前准备

### 需要准备的材料
- ✅ GitHub账号（已有：lemonlemontree1992）
- ✅ GitHub仓库：https://github.com/lemonlemontree1992/deepfind-agent
- ✅ DeepSeek API Key
- ✅ Tavily API Key
- ✅ 一个邮箱（用于注册Render和Vercel）

### API Key获取链接
- DeepSeek: https://platform.deepseek.com/
- Tavily: https://tavily.com/

---

## 第一步：部署后端到Render（15分钟）

### 1.1 注册Render账号

1. **访问Render官网**
   ```
   https://render.com/
   ```

2. **点击注册**
   - 点击右上角 **"Get Started"** 或 **"Sign Up"**
   - 选择 **"Sign up with GitHub"**
   - 授权Render访问您的GitHub账号

3. **完成注册**
   - 填写必要信息（姓名、邮箱）
   - 不需要信用卡！

### 1.2 创建新的Web Service

1. **进入控制台**
   登录后进入Render控制台

2. **创建新服务**
   - 点击右上角 **"New +"** 按钮
   - 选择 **"Web Service"**

3. **连接GitHub仓库**
   - 如果是首次使用，需要授权GitHub
   - 在仓库列表中找到 `deepfind-agent`
   - 点击 **"Connect"**

### 1.3 配置Web Service

**基本配置**：

| 配置项 | 值 |
|--------|-----|
| **Name** | `deepfind-agent-api`（或您喜欢的名字） |
| **Region** | `Oregon (US West)` 或 `Frankfurt (EU Central)` |
| **Branch** | `main` |
| **Root Directory** | 留空（或 `.`） |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn api:app --host 0.0.0.0 --port $PORT` |

**重要**：
- Runtime会自动检测为Python 3
- Build Command和Start Command必须正确
- Root Directory留空表示根目录

**选择免费套餐**：

| 配置项 | 选择 |
|--------|-----|
| **Instance Type** | 选择 **"Free"** |

### 1.4 添加环境变量

**在同一个配置页面**：

1. 找到 **"Environment Variables"** 部分
2. 点击 **"Add Environment Variable"**
3. 逐个添加以下变量：

**变量1**：
```
Key: DEEPSEEK_API_KEY
Value: sk-您的DeepSeek API Key
```

**变量2**：
```
Key: TAVILY_API_KEY
Value: tvly-dev-您的Tavily API Key
```

**变量3**：
```
Key: ENV
Value: production
```

**变量4**：
```
Key: ALLOWED_ORIGINS
Value: *（暂时设为星号，部署前端后再更新）
```

**变量5**：
```
Key: PYTHON_VERSION
Value: 3.11.4
```

### 1.5 创建Web Service

1. 确认所有配置正确
2. 点击页面底部的 **"Deploy Web Service"** 按钮

### 1.6 等待部署

**部署过程**（约3-5分钟）：

```
1. Cloning from GitHub... ✅
2. Installing Python 3.11.4... ✅
3. Installing dependencies from requirements.txt... ✅
4. Starting deployment... ✅
5. Health check... ✅
6. Live! ✅
```

**您会看到**：
- 实时构建日志
- 每个步骤的进度
- 最后显示 "Your service is live"

### 1.7 获取后端URL

**部署成功后**：

1. 在服务页面顶部，找到您的服务URL
2. URL格式类似：
   ```
   https://deepfind-agent-api.onrender.com
   ```
3. **复制这个URL**，下一步部署前端时需要用到

### 1.8 验证后端部署

**在浏览器中测试**：

1. **访问根路径**：
   ```
   https://your-app.onrender.com/
   ```
   应该看到：
   ```json
   {
     "name": "DeepFind Agent API",
     "version": "1.0.0",
     "status": "running"
   }
   ```

2. **访问健康检查**：
   ```
   https://your-app.onrender.com/health
   ```
   应该看到：
   ```json
   {
     "status": "healthy",
     "api_keys": {
       "deepseek": true,
       "tavily": true
     }
   }
   ```

3. **访问API文档**：
   ```
   https://your-app.onrender.com/docs
   ```
   应该看到FastAPI自动生成的API文档

**如果看到以上内容，说明后端部署成功！** ✅

---

## 第二步：部署前端到Vercel（10分钟）

### 2.1 注册Vercel账号

1. **访问Vercel官网**
   ```
   https://vercel.com/
   ```

2. **点击注册**
   - 点击右上角 **"Sign Up"**
   - 选择 **"Continue with GitHub"**
   - 授权Vercel访问您的GitHub账号

3. **完成注册**
   - 不需要信用卡！
   - 自动跳转到Vercel控制台

### 2.2 导入项目

1. **创建新项目**
   - 点击右上角 **"Add New..."**
   - 选择 **"Project"**

2. **导入GitHub仓库**
   - 在 **"Import Git Repository"** 部分
   - 找到 `deepfind-agent` 仓库
   - 点击 **"Import"**

### 2.3 配置项目

**重要配置**：

#### Root Directory设置
1. 找到 **"Root Directory"** 部分
2. 点击 **"Edit"**
3. 选择 **`frontend`** 文件夹
4. 点击 **"Continue"**

#### Framework Preset
- Vercel会自动检测为 `Vite` 或 `React`
- 如果没有自动检测，选择 **"Other"**

#### Build & Development Settings
| 配置项 | 值 |
|--------|-----|
| **Framework Preset** | `Vite` 或自动检测 |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |
| **Install Command** | `npm install` （自动设置） |

### 2.4 添加环境变量

**在同一个配置页面**：

1. 展开 **"Environment Variables"** 部分

2. 添加环境变量：

**变量1**：
```
Name: VITE_API_BASE_URL
Value: https://your-app.onrender.com
```

**重要**：
- 将 `https://your-app.onrender.com` 替换为第一步获取的Render后端URL
- 不要在URL末尾加 `/`
- 确保URL正确，否则前端无法连接后端

### 2.5 部署前端

1. 确认所有配置正确
2. 点击 **"Deploy"** 按钮

3. 等待部署（约1-2分钟）：
   ```
   Installing dependencies... ✅
   Building... ✅
   Optimizing... ✅
   Deploying... ✅
   Congratulations! 🎉
   ```

### 2.6 获取前端URL

**部署成功后**：

1. Vercel会显示一个庆祝界面 🎉
2. 您会看到前端URL，格式如：
   ```
   https://deepfind-agent.vercel.app
   ```
   或
   ```
   https://deepfind-agent-xyz.vercel.app
   ```

3. **复制这个URL**，下一步需要用到

### 2.7 验证前端部署

**在浏览器中测试**：

1. 访问您的前端URL
2. 应该能看到DeepFind Agent的界面
3. 尝试输入测试关键词并提交

---

## 第三步：更新跨域配置（2分钟）

### 3.1 回到Render

1. 登录 https://dashboard.render.com/
2. 进入您的 `deepfind-agent-api` 服务
3. 点击左侧的 **"Environment"** 标签

### 3.2 更新ALLOWED_ORIGINS变量

1. 找到 `ALLOWED_ORIGINS` 变量
2. 点击右侧的 **"Edit"** 按钮
3. 将值从 `*` 改为您的前端URL：
   ```
   https://your-app.vercel.app
   ```
4. 点击 **"Save Changes"**

### 3.3 自动重新部署

- Render会自动检测环境变量变化
- 等待约30秒-1分钟
- 服务会自动重新部署

**或者手动触发**：
- 点击 **"Manual Deploy"**
- 选择 **"Deploy latest commit"**

---

## 第四步：完整功能测试（5分钟）

### 4.1 测试后端API

**在浏览器中访问**：

1. **根路径测试**：
   ```
   https://your-app.onrender.com/
   ```
   期望结果：
   ```json
   {"name": "DeepFind Agent API", "version": "1.0.0", "status": "running"}
   ```

2. **健康检查**：
   ```
   https://your-app.onrender.com/health
   ```
   期望结果：
   ```json
   {"status": "healthy", "api_keys": {"deepseek": true, "tavily": true}}
   ```

3. **API文档**：
   ```
   https://your-app.onrender.com/docs
   ```
   应该看到Swagger UI文档界面

### 4.2 测试前端界面

**在浏览器中访问**：
```
https://your-app.vercel.app
```

**测试步骤**：

1. **访问前端**
   - 应该看到DeepFind Agent界面
   - 界面正常加载，无错误

2. **输入测试关键词**
   ```
   分析iPhone 15 Pro竞品对比
   ```

3. **提交查询**
   - 点击"开始调研"或类似的提交按钮
   - 观察是否有实时流式输出

4. **检查功能**
   - ✅ 搜索开始
   - ✅ 实时进度显示
   - ✅ 结果生成
   - ✅ 报告下载

### 4.3 测试完整流程

**完整测试案例**：

1. **测试用例1：产品分析**
   ```
   输入：分析iPhone 15 Pro和华为Mate 60 Pro的竞品对比
   期望：生成产品对比报告
   ```

2. **测试用例2：旅游攻略**
   ```
   输入：纽约4天3晚旅游攻略
   期望：生成旅游攻略
   ```

3. **测试用例3：行业洞察**
   ```
   输入：Claude 3发布对AI行业的影响
   期望：生成行业洞察报告
   ```

**检查要点**：
- ✅ 前端能正常访问
- ✅ 后端API响应正常
- ✅ 搜索功能工作正常
- ✅ 流式输出正常
- ✅ 报告生成正常

---

## 🎉 部署成功！

### 您的应用地址

**前端**：
```
https://your-app.vercel.app
```

**后端**：
```
https://your-app.onrender.com
```

**API文档**：
```
https://your-app.onrender.com/docs
```

### 分享给用户

现在您可以：
1. 分享前端URL给用户使用
2. 在GitHub仓库首页添加部署链接
3. 开始分享您的项目！

---

## ⚠️ 重要注意事项

### Render的休眠机制

**免费层限制**：
- ⚠️ **15分钟无请求后自动休眠**
- ⚠️ **休眠后首次访问需等待约30秒启动**

**影响**：
- 用户首次访问可能需要等待30秒
- 之后15分钟内的访问都是秒开

**解决方案**（如果需要）：
- 使用第三方服务定期ping您的应用
- 或升级到Render付费计划（$7/月）

### 监控和维护

**Render监控**：
1. 访问 https://dashboard.render.com/
2. 进入您的服务
3. 查看：
   - **Logs**: 实时日志
   - **Metrics**: CPU、内存、网络
   - **Events**: 部署历史

**Vercel监控**：
1. 访问 https://vercel.com/dashboard
2. 进入您的项目
3. 查看：
   - **Deployments**: 部署历史
   - **Analytics**: 访问统计
   - **Logs**: 函数日志

---

## 🔄 更新部署

### 代码更新流程

**当您修改代码后**：

1. **提交到GitHub**：
   ```bash
   git add .
   git commit -m "更新说明"
   git push origin main
   ```

2. **自动部署**：
   - Render会自动检测并重新部署后端（约3-5分钟）
   - Vercel会自动检测并重新部署前端（约1-2分钟）

3. **手动触发**（如果自动部署失败）：
   - Render: 点击 "Manual Deploy"
   - Vercel: 点击 "Redeploy"

### 环境变量更新

**更新Render环境变量**：
1. 进入服务 → Environment
2. 编辑对应的变量
3. 点击 Save Changes
4. 自动重新部署

**更新Vercel环境变量**：
1. 进入项目 → Settings → Environment Variables
2. 编辑对应的变量
3. 需要手动Redeploy

---

## ❓ 常见问题

### Q1: 后端部署失败怎么办？

**检查步骤**：
1. 查看Build Logs具体错误
2. 确认 `requirements.txt` 在根目录
3. 确认 `Procfile` 存在且内容正确
4. 确认Python版本兼容（runtime.txt）
5. 确认环境变量是否正确设置

**常见错误**：
```
错误: Module not found
解决: 检查requirements.txt中的依赖是否完整
```

```
错误: Port not specified
解决: 确认Start Command使用 $PORT 变量
```

### Q2: 前端无法连接后端？

**检查步骤**：
1. 确认后端URL是否正确
2. 确认Vercel环境变量 `VITE_API_BASE_URL` 设置正确
3. 确认Render的 `ALLOWED_ORIGINS` 包含前端URL
4. 查看浏览器控制台的CORS错误

**调试方法**：
- 在浏览器中直接访问后端URL测试
- 查看Network面板的请求详情
- 检查Render日志

### Q3: 首次访问很慢？

**原因**：
- Render免费层会休眠
- 首次访问需要启动服务（约30秒）

**解决**：
- 正常现象，等待即可
- 之后15分钟内访问都是秒开

### Q4: 如何绑定自定义域名？

**Vercel绑定域名**：
1. 项目 → Settings → Domains
2. 添加您的域名
3. 在域名服务商处添加DNS记录

**Render绑定域名**：
1. 服务 → Settings → Custom Domains
2. 添加您的域名
3. 添加DNS记录

---

## 📊 部署检查清单

完成后端部署：
- [ ] Render账号已注册
- [ ] Web Service已创建
- [ ] GitHub仓库已连接
- [ ] 环境变量已配置（5个）
  - [ ] DEEPSEEK_API_KEY
  - [ ] TAVILY_API_KEY
  - [ ] ENV
  - [ ] ALLOWED_ORIGINS
  - [ ] PYTHON_VERSION
- [ ] 部署成功（绿色状态）
- [ ] 后端URL已复制
- [ ] 后端API测试通过

完成前端部署：
- [ ] Vercel账号已注册
- [ ] 项目已导入
- [ ] Root Directory设置为 frontend
- [ ] 环境变量已配置
  - [ ] VITE_API_BASE_URL
- [ ] 部署成功（🎉界面）
- [ ] 前端URL已复制
- [ ] 前端界面测试通过

完成跨域配置：
- [ ] Render的ALLOWED_ORIGINS已更新
- [ ] 服务已重新部署

完整功能测试：
- [ ] 后端健康检查正常
- [ ] 前端界面正常加载
- [ ] 搜索功能正常工作
- [ ] 流式输出正常
- [ ] 报告生成正常

---

## 📞 需要帮助？

**部署过程中遇到问题**：
1. 查看Render Logs
2. 查看Vercel Deployments
3. 检查浏览器控制台错误
4. 参考 `docs/FREE_PLATFORMS_SUPABASE.md`

**文档位置**：
- 本指南：`docs/DEPLOYMENT_PLAN_A.md`
- Render 详细步骤：`docs/RENDER_BACKEND_DEPLOYMENT.md`
- 平台对比：`docs/FREE_PLATFORMS_SUPABASE.md`

---

## 🎊 恭喜！

您已成功部署DeepFind Agent到完全免费的平台：
- ✅ 前端：Vercel（永久免费）
- ✅ 后端：Render（永久免费）
- ✅ 总费用：$0/月
- ✅ 不需要信用卡

现在可以开始使用和分享您的项目了！🚀

---

**部署时间**: 2026-06-30
**方案**: 方案A（Vercel + Render）
**费用**: $0/月