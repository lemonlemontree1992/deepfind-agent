#!/bin/bash

echo "🧪 测试 Vercel 部署访问..."
echo ""

# 测试主域名
echo "1️⃣ 测试主域名："
echo "   URL: https://deepfind-agent.vercel.app"
curl -I https://deepfind-agent.vercel.app 2>&1 | head -5
echo ""

# 测试备用域名 1
echo "2️⃣ 测试备用域名 1："
echo "   URL: https://deepfind-agent-yangs-projects-dd98a4ae.vercel.app"
curl -I https://deepfind-agent-yangs-projects-dd98a4ae.vercel.app 2>&1 | head -5
echo ""

# 测试备用域名 2
echo "3️⃣ 测试备用域名 2："
echo "   URL: https://deepfind-agent-git-main-yangs-projects-dd98a4ae.vercel.app"
curl -I https://deepfind-agent-git-main-yangs-projects-dd98a4ae.vercel.app 2>&1 | head -5
echo ""

# DNS 解析测试
echo "4️⃣ DNS 解析测试："
nslookup deepfind-agent.vercel.app 2>&1 | grep -A 2 "Name:"
echo ""

echo "✅ 测试完成！"
echo ""
echo "📝 如果以上测试都返回 'HTTP/2 200' 或 'HTTP/2 301'，说明部署成功。"
echo "💡 如果仍然无法在浏览器访问，可能是本地网络问题。"