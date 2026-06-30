#!/bin/bash

# DeepFind Agent 启动脚本

echo "🔍 DeepFind Agent 启动中..."
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 检查依赖
if [ ! -f "venv/lib/python3.*/site-packages/streamlit/__init__.py" ]; then
    echo "📥 安装依赖..."
    pip install -r requirements.txt
    playwright install
fi

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️  .env 文件不存在，正在创建..."
    cp .env.example .env
    echo "请编辑 .env 文件，填入你的 DeepSeek API Key"
    exit 1
fi

# 启动 Streamlit
echo "🚀 启动 Web 界面..."
streamlit run app.py