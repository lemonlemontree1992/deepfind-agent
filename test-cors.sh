#!/bin/bash

echo "🧪 测试 CORS 配置..."
echo ""

# 测试后端健康检查
echo "1️⃣ 测试后端健康检查："
curl -s https://deepfind-agent.onrender.com/health | head -20
echo ""
echo ""

# 测试 CORS 预检请求
echo "2️⃣ 测试 CORS 预检请求 (OPTIONS)："
curl -I -X OPTIONS https://deepfind-agent.onrender.com/health \
  -H "Origin: https://deepfind-agent.vercel.app" \
  -H "Access-Control-Request-Method: GET" \
  2>/dev/null | grep -i "access-control"
echo ""

echo "✅ 如果看到 'access-control-allow-origin' 包含您的 Vercel URL，配置成功！"