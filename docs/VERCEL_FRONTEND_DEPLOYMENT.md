# 🚀 Vercel前端部署详细步骤

**后端URL**: https://deepfind-agent.onrender.com ✅
**下一步**: 部署前端到Vercel
**预计时间**: 10分钟

---

## 📦 部署架构回顾

```
用户访问
    ↓
Vercel (前端React)
https://xxx.vercel.app
    ↓
Render (后端API)
https://deepfind-agent.onrender.com
    ↓
DeepSeek API / Tavily API
```

---

## 第一步：访问Vercel（2分钟）

### 1.1 打开Vercel官网
```
https://vercel.com/
```

### 1.2 注册/登录
- 点击右上角 **"Sign Up"**
- 选择 **"Continue with GitHub"**
- 授权Vercel访问您的GitHub账号
- **不需要信用卡！**

### 1.3 完成注册
- 自动跳转到Vercel控制台
- 您会看到欢迎界面

---

## 第二步：导入项目（3分钟）

### 2.1 创建新项目
- 登录后，点击右上角 **"Add New..."**
- 选择 **"Project"**

### 2.2 导入GitHub仓库
- 在 **"Import Git Repository"** 部分
- 您会看到GitHub仓库列表
- 找到 `deepfind-agent` 仓库
- 仓库所有者：`lemonlemontree1992`
- 点击 **"Import"** 按钮

### 2.3 确认仓库信息
**确认页面显示**：
```
Repository: lemonlemontree1992/deepfind-agent
Branch: main
```

---

## 第三步：配置项目（重要！）（3分钟）

### 3.1 设置Root Directory（关键步骤！）

**⚠️ 非常重要！必须设置正确的Root Directory！**

1. 找到 **"Root Directory"** 部分
2. 点击右侧的 **"Edit"** 按钮
3. 在弹出的文件夹选择器中：
   - 您会看到项目根目录的内容
   - 找到并点击 **`frontend`** 文件夹
   - 确认选中（文件夹会有高亮显示）
4. 点击 **"Continue"** 或 **"Confirm"**

**为什么必须选择frontend？**
```
项目结构：
deepfind-agent/
├── backend/          后端代码
├── frontend/         ← 前端代码在这里！
├── agents/
├── tools/
└── ...
```

**如果忘记选择frontend会怎样？**
- ❌ Vercel会尝试构建整个项目
- ❌ 构建会失败（找不到package.json）
- ❌ 前端无法正常运行

### 3.2 确认Framework设置

**Vercel会自动检测**：
- Framework Preset: `Vite` 或 `React`
- 如果没有自动检测，手动选择 `Vite`

**Build & Development Settings**：
| 设置项 | 值 |
|--------|-----|
| **Framework Preset** | `Vite` 或自动检测 |
| **Build Command** | `npm run build`（自动填充） |
| **Output Directory** | `dist`（自动填充） |
| **Install Command** | `npm install`（自动填充） |

**⚠️ 如果Output Directory不是dist**：
- 手动改为 `dist`

### 3.3 添加环境变量（关键步骤！）

**在同一个配置页面**：

1. 找到 **"Environment Variables"** 部分
2. 点击展开

3. **添加变量**：
   ```
   Name: VITE_API_BASE_URL
   Value: https://deepfind-agent.onrender.com
   ```

**⚠️ 重要注意事项**：
```
✅ 正确：https://deepfind-agent.onrender.com
❌ 错误：https://deepfind-agent.onrender.com/（末尾不要加斜杠）
❌ 错误：http://deepfind-agent.onrender.com（要用https）
❌ 错误：deepfind-agent.onrender.com（要加https://）
```

4. 点击 **"Add"** 按钮确认添加

**确认环境变量已添加**：
- 您应该能在环境变量列表中看到：
  ```
  VITE_API_BASE_URL = https://deepfind-agent.onrender.com
  ```

---

## 第四步：部署前端（2分钟）

### 4.1 检查所有配置

**部署前最后检查**：
- [ ] Root Directory 设置为 `frontend`
- [ ] Framework Preset 显示为 `Vite` 或 `React`
- [ ] Build Command 为 `npm run build`
- [ ] Output Directory 为 `dist`
- [ ] 环境变量已添加：
  - [ ] `VITE_API_BASE_URL` = `https://deepfind-agent.onrender.com`

### 4.2 点击部署
- 确认所有配置正确
- 点击页面底部的 **"Deploy"** 按钮

### 4.3 等待构建

**构建过程**（约1-2分钟）：
```
✅ Installing dependencies...
✅ npm install
✅ Building...
✅ npm run build
✅ Optimizing...
✅ Generating static pages...
✅ Collecting page data...
✅ Finalizing page optimization...
✅ Deployment completed
```

### 4.4 部署成功

**看到庆祝界面** 🎉：
- Vercel会显示一个庆祝动画
- 显示 "Congratulations!"
- 显示您的部署URL

---

## 第五步：获取前端URL（1分钟）

### 5.1 查看部署URL

**部署成功后，您会看到**：
```
🎉 Congratulations! Your project has been deployed.

Production: https://deepfind-agent.vercel.app
```

**或类似格式**：
```
https://deepfind-agent-xyz.vercel.app
```

### 5.2 复制URL

**您的前端URL可能是**：
```
https://deepfind-agent.vercel.app
```
或
```
https://deepfind-agent-[随机字符].vercel.app
```

**复制这个URL**，下一步需要用到！

---

## 第六步：测试前端（2分钟）

### 6.1 访问前端

**在浏览器中访问您的前端URL**：
```
https://your-frontend-url.vercel.app
```

### 6.2 检查界面

**应该能看到**：
- ✅ DeepFind Agent 的界面正常显示
- ✅ 没有错误信息
- ✅ 界面布局正常
- ✅ 可以输入查询

### 6.3 测试功能

**尝试输入测试关键词**：
```
分析iPhone 15 Pro竞品对比
```

**检查**：
- ✅ 能否提交查询
- ✅ 是否显示加载状态
- ✅ 是否有实时进度显示
- ✅ 是否生成报告
- ✅ 是否可以下载报告

---

## ⚠️ 如果遇到问题

### 问题1：构建失败

**可能原因**：
- Root Directory 没有设置为 `frontend`
- Build Command 不正确
- package.json 文件缺失

**解决方法**：
1. 进入Vercel项目 → Settings
2. 检查 Root Directory 是否为 `frontend`
3. 检查 Build Command 是否为 `npm run build`
4. 重新部署

---

### 问题2：页面空白或报错

**可能原因**：
- 环境变量未设置或设置错误
- 后端URL不正确

**解决方法**：
1. 检查环境变量：
   - 项目 → Settings → Environment Variables
   - 确认 `VITE_API_BASE_URL` 设置正确
2. 检查URL格式：
   - ✅ 正确：`https://deepfind-agent.onrender.com`
   - ❌ 错误：`https://deepfind-agent.onrender.com/`

3. 更新环境变量后需要重新部署：
   - Deployments → 最新部署 → Redeploy

---

### 问题3：无法连接后端

**可能原因**：
- 后端未运行
- 跨域配置错误
- 环境变量错误

**解决方法**：
1. 测试后端是否正常：
   - 访问 `https://deepfind-agent.onrender.com/health`
   - 应该返回正常JSON

2. 检查跨域配置：
   - 回到Render
   - 检查 `ALLOWED_ORIGINS` 环境变量
   - 应该包含您的前端URL

---

### 问题4：API请求失败

**检查浏览器控制台**：
1. 打开浏览器开发者工具（F12）
2. 查看 Console 标签
3. 查看 Network 标签
4. 检查API请求是否发送
5. 检查响应内容

---

## 📝 部署完成检查清单

完成以下检查，确认前端部署成功：

- [ ] 已访问Vercel并注册
- [ ] 已导入GitHub仓库
- [ ] Root Directory 设置为 `frontend` ✅ 重要！
- [ ] Framework 自动检测为 Vite/React
- [ ] Build Command 为 `npm run build`
- [ ] Output Directory 为 `dist`
- [ ] 环境变量已添加
  - [ ] `VITE_API_BASE_URL` = `https://deepfind-agent.onrender.com`
- [ ] 已点击 Deploy
- [ ] 构建成功（看到🎉）
- [ ] 已获取前端URL
- [ ] 前端界面可以访问
- [ ] 可以提交查询
- [ ] 可以生成报告

---

## 🔄 下一步：更新跨域配置

**前端部署成功后，需要更新Render的跨域设置**：

### 步骤：

1. 回到Render控制台
   ```
   https://dashboard.render.com/
   ```

2. 进入您的服务 → Environment

3. 编辑 `ALLOWED_ORIGINS` 变量
   - 当前值：`*`
   - 改为您的前端URL：`https://your-frontend.vercel.app`

4. 点击 Save Changes

5. 等待自动重新部署（约30秒）

---

## 📊 当前部署状态

| 组件 | 平台 | URL | 状态 |
|------|------|-----|------|
| 后端 | Render | https://deepfind-agent.onrender.com | ✅ 已部署 |
| 前端 | Vercel | https://xxx.vercel.app | 🚀 正在部署 |

---

## 📞 需要帮助？

**部署过程中遇到问题**：
- 查看 Vercel Deployments 日志
- 查看浏览器控制台错误
- 告诉我具体的错误信息

**我会帮您解决问题！**

---

**部署时间**: 2026-06-30
**后端URL**: https://deepfind-agent.onrender.com
**预计完成**: 10分钟