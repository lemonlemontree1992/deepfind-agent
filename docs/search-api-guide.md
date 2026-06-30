# DeepFind Agent 搜索源配置指南

## 问题诊断

当前 Tavily API 额度已用完（432 错误），导致搜索无结果。

## 解决方案

DeepFind Agent 现已支持多个搜索源，您可以配置以下任一搜索 API（按推荐顺序）：

---

### 方案 1: Serper API（推荐）🌟

**优势**：
- ✅ 免费额度：2500 次/月
- ✅ 质量高：Google 搜索结果
- ✅ 速度快：响应时间 < 500ms
- ✅ 无需信用卡

**获取步骤**：
1. 访问 https://serper.dev/
2. 点击 "Sign Up" 注册账号
3. 登录后在 Dashboard 获取 API Key
4. 配置到 `.env` 文件：

```bash
SERPER_API_KEY=your_serper_api_key_here
```

---

### 方案 2: Brave Search API

**优势**：
- ✅ 免费额度：2000 次/月
- ✅ 注重隐私
- ✅ 独立搜索引擎

**获取步骤**：
1. 访问 https://brave.com/search/api/
2. 点击 "Get Started" 注册
3. 创建 API Key
4. 配置到 `.env` 文件：

```bash
BRAVE_API_KEY=your_brave_api_key_here
```

---

### 方案 3: DuckDuckGo（已内置）✅

**优势**：
- ✅ 完全免费，无需 API Key
- ✅ 无使用限制
- ✅ 已经自动启用

**说明**：无需任何配置，系统会自动使用 DuckDuckGo 作为备选搜索源。

---

### 方案 4: SerpApi

**优势**：
- ✅ 免费额度：100 次/月
- ✅ 支持多种搜索引擎

**获取步骤**：
1. 访问 https://serpapi.com/
2. 注册账号
3. 获取 API Key
4. 配置到 `.env` 文件：

```bash
SERPAPI_KEY=your_serpapi_key_here
```

---

## 推荐配置

### 最简单（推荐新手）
无需任何配置，直接使用 DuckDuckGo（已自动启用）

### 最佳性能（推荐）
配置 Serper API + DuckDuckGo 作为备选

```bash
# .env 文件
SERPER_API_KEY=your_serper_api_key_here
# DuckDuckGo 已自动启用，无需配置
```

### 最大可靠性
配置多个搜索源，自动故障转移

```bash
# .env 文件
SERPER_API_KEY=your_serper_api_key_here
BRAVE_API_KEY=your_brave_api_key_here
SERPAPI_KEY=your_serpapi_key_here
# Tavily API Key (如果还有额度)
TAVILY_API_KEY=your_tavily_api_key_here
```

---

## 当前状态

```
❌ Tavily API: 额度已用完 (432 错误)
✅ DuckDuckGo: 已启用（自动）
⏸️  Serper API: 未配置
⏸️  Brave Search: 未配置
⏸️  SerpApi: 未配置
```

---

## 快速修复

### 立即可用（无需注册）
DuckDuckGo 已经自动启用，重启服务即可使用：

```bash
# 重启后端
lsof -ti:8000 | xargs kill -9
python3 api.py
```

### 推荐升级（5分钟）
1. 注册 Serper API（免费 2500 次/月）：https://serper.dev/
2. 获取 API Key
3. 添加到 `.env` 文件：
   ```bash
   SERPER_API_KEY=你的key
   ```
4. 重启服务

---

*更新时间: 2026-06-29*