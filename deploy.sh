#!/bin/bash

# DeepFind Agent 快速部署脚本
# 用法: ./deploy.sh

echo "🚀 DeepFind Agent 部署助手"
echo "============================"
echo ""

echo "📋 部署步骤："
echo ""
echo "第一步：部署后端到 Railway"
echo "1. 访问: https://railway.app/"
echo "2. 使用 GitHub 登录"
echo "3. 点击 'New Project'"
echo "4. 选择 'Deploy from GitHub repo'"
echo "5. 选择 'deepfind-agent' 仓库"
echo "6. 添加环境变量:"
echo "   - DEEPSEEK_API_KEY=your_key"
echo "   - TAVILY_API_KEY=your_key"
echo "   - ENV=production"
echo "   - ALLOWED_ORIGINS=https://your-frontend.vercel.app"
echo ""
echo "按回车继续查看前端部署步骤..."
read -r

echo ""
echo "第二步：部署前端到 Vercel"
echo "1. 访问: https://vercel.com/"
echo "2. 使用 GitHub 登录"
echo "3. 点击 'Add New Project'"
echo "4. 导入 'deepfind-agent' 仓库"
echo "5. 设置 Root Directory: frontend"
echo "6. 添加环境变量:"
echo "   - VITE_API_BASE_URL=https://your-backend.railway.app"
echo "7. 点击 Deploy"
echo ""
echo "按回车查看部署验证步骤..."
read -r

echo ""
echo "第三步：验证部署"
echo "后端健康检查:"
echo "  curl https://your-backend.railway.app/health"
echo ""
echo "前端访问:"
echo "  打开浏览器访问: https://your-frontend.vercel.app"
echo ""
echo "📖 完整部署文档: docs/DEPLOYMENT_GUIDE.md"
echo ""
echo "✅ 部署完成！"