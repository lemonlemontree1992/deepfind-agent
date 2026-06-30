#!/bin/bash

# GLM-5.2 模型集成快速部署脚本
# 使用方法: chmod +x scripts/integrate_glm.sh && ./scripts/integrate_glm.sh

set -e

echo "========================================="
echo "  GLM-5.2 模型集成部署脚本"
echo "========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查当前目录
if [ ! -f "config/settings.py" ]; then
    echo -e "${RED}错误: 请在项目根目录运行此脚本${NC}"
    exit 1
fi

# 步骤 1: 安装依赖
echo -e "${YELLOW}[步骤 1/6] 安装 zhipuai SDK...${NC}"
pip install zhipuai>=2.0.0
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ zhipuai 安装成功${NC}"
else
    echo -e "${RED}❌ zhipuai 安装失败${NC}"
    exit 1
fi
echo ""

# 步骤 2: 备份关键文件
echo -e "${YELLOW}[步骤 2/6] 备份关键文件...${NC}"
mkdir -p backups/$(date +%Y%m%d_%H%M%S)
cp config/settings.py backups/$(date +%Y%m%d_%H%M%S)/settings.py.bak
cp utils/llm_client.py backups/$(date +%Y%m%d_%H%M%S)/llm_client.py.bak
cp agents/search_agent.py backups/$(date +%Y%m%d_%H%M%S)/search_agent.py.bak
echo -e "${GREEN}✅ 文件备份完成${NC}"
echo ""

# 步骤 3: 更新 .env 文件
echo -e "${YELLOW}[步骤 3/6] 检查 .env 配置...${NC}"
if grep -q "GLM_API_KEY" .env; then
    echo -e "${GREEN}✅ .env 已包含 GLM 配置${NC}"
else
    echo -e "${YELLOW}添加 GLM 配置到 .env...${NC}"
    cat >> .env << 'EOF'

# ========== 智谱 GLM 配置 ==========
GLM_API_KEY=your_glm_api_key_here
GLM_MODEL=glm-5.2
DEFAULT_LLM_PROVIDER=deepseek
EOF
    echo -e "${GREEN}✅ GLM 配置已添加到 .env${NC}"
    echo -e "${YELLOW}⚠️  请手动编辑 .env 文件，填入有效的 GLM_API_KEY${NC}"
fi
echo ""

# 步骤 4: 更新 requirements.txt
echo -e "${YELLOW}[步骤 4/6] 更新 requirements.txt...${NC}"
if grep -q "zhipuai" requirements.txt; then
    echo -e "${GREEN}✅ requirements.txt 已包含 zhipuai${NC}"
else
    echo "zhipuai>=2.0.0" >> requirements.txt
    echo -e "${GREEN}✅ zhipuai 已添加到 requirements.txt${NC}"
fi
echo ""

# 步骤 5: 创建测试脚本
echo -e "${YELLOW}[步骤 5/6] 创建测试脚本...${NC}"
cat > test_llm_providers.py << 'EOF'
"""测试不同的 LLM 提供商"""

import sys
sys.path.insert(0, '.')

from utils.llm_client import get_llm
from langchain_core.messages import HumanMessage, SystemMessage
from config import settings

print("=" * 60)
print("测试 LLM 提供商切换功能")
print("=" * 60)

# 测试 DeepSeek
print("\n[测试 1] DeepSeek 模型")
try:
    llm = get_llm(provider="deepseek", temperature=0.5)
    response = llm.invoke([
        SystemMessage(content="你是一个助手"),
        HumanMessage(content="用一句话介绍纽约")
    ])
    print(f"✅ DeepSeek 响应: {response.content[:80]}...")
except Exception as e:
    print(f"❌ DeepSeek 失败: {str(e)}")

# 测试 GLM
print("\n[测试 2] GLM-5.2 模型")
try:
    llm = get_llm(provider="glm", temperature=0.5)
    response = llm.invoke([
        SystemMessage(content="你是一个助手"),
        HumanMessage(content="用一句话介绍纽约")
    ])
    print(f"✅ GLM 响应: {response.content[:80]}...")
except Exception as e:
    print(f"❌ GLM 失败: {str(e)}")

print("\n" + "=" * 60)
EOF
echo -e "${GREEN}✅ 测试脚本已创建: test_llm_providers.py${NC}"
echo ""

# 步骤 6: 完成
echo "========================================="
echo -e "${GREEN}部署准备完成！${NC}"
echo "========================================="
echo ""
echo "📋 后续步骤："
echo ""
echo "1. 编辑 .env 文件，填入您的 GLM API Key："
echo "   ${YELLOW}vim .env${NC}"
echo "   找到 GLM_API_KEY=your_glm_api_key_here，替换为实际密钥"
echo ""
echo "2. 更新代码文件（参考 docs/glm-integration-plan.md）："
echo "   - config/settings.py"
echo "   - utils/llm_client.py"
echo "   - agents/search_agent.py"
echo "   - agents/task_planner.py"
echo "   - agents/enhanced_report_agent.py"
echo ""
echo "3. 运行测试："
echo "   ${YELLOW}python test_llm_providers.py${NC}"
echo ""
echo "4. 重启服务："
echo "   ${YELLOW}python api.py${NC}"
echo ""
echo "5. 切换模型（在 .env 中修改）："
echo "   ${YELLOW}DEFAULT_LLM_PROVIDER=glm${NC}  # 使用 GLM"
echo "   ${YELLOW}DEFAULT_LLM_PROVIDER=deepseek${NC}  # 使用 DeepSeek"
echo ""
echo "📚 详细文档: docs/glm-integration-plan.md"
echo ""

# 检查是否需要填入 API Key
if grep -q "your_glm_api_key_here" .env; then
    echo -e "${YELLOW}⚠️  警告: 请先在 .env 文件中填入有效的 GLM_API_KEY${NC}"
    echo ""
fi