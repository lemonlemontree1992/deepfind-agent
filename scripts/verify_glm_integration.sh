#!/bin/bash

# GLM-5.2 集成验证脚本
# 用于快速检查代码修改是否正确

echo "========================================="
echo "  GLM-5.2 集成验证脚本"
echo "========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 计数器
PASS=0
FAIL=0

# 检查函数
check() {
    local description=$1
    local command=$2

    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $description${NC}"
        ((PASS++))
    else
        echo -e "${RED}❌ $description${NC}"
        ((FAIL++))
    fi
}

# 开始检查
echo "1. 检查依赖安装..."
check "zhipuai 已安装" "pip show zhipuai"
check "langchain_deepseek 已安装" "pip show langchain-deepseek"
echo ""

echo "2. 检查文件修改..."
check "requirements.txt 包含 zhipuai" "grep -q 'zhipuai' requirements.txt"
check ".env 包含 GLM_API_KEY" "grep -q 'GLM_API_KEY' .env"
check ".env 包含 GLM_MODEL" "grep -q 'GLM_MODEL' .env"
check ".env 包含 DEFAULT_LLM_PROVIDER" "grep -q 'DEFAULT_LLM_PROVIDER' .env"
echo ""

echo "3. 检查代码导入..."
check "utils/llm_client.py 存在" "test -f utils/llm_client.py"
check "config/settings.py 包含 glm_api_key" "grep -q 'glm_api_key' config/settings.py"
echo ""

echo "4. 检查未修改的 ChatDeepSeek 导入..."
remaining_imports=$(grep -r "from langchain_deepseek import ChatDeepSeek" agents/ 2>/dev/null | wc -l)
if [ "$remaining_imports" -eq 0 ]; then
    echo -e "${GREEN}✅ 所有 ChatDeepSeek 导入已替换${NC}"
    ((PASS++))
else
    echo -e "${YELLOW}⚠️  还有 $remaining_imports 处 ChatDeepSeek 导入未替换${NC}"
    ((FAIL++))
    echo -e "${YELLOW}   文件列表:${NC}"
    grep -r "from langchain_deepseek import ChatDeepSeek" agents/ 2>/dev/null
fi
echo ""

echo "5. 检查 get_llm 使用..."
check "agents/analyze_agent.py 使用 get_llm" "grep -q 'from utils.llm_client import get_llm' agents/analyze_agent.py"
check "agents/extraction_agent.py 使用 get_llm" "grep -q 'from utils.llm_client import get_llm' agents/extraction_agent.py"
check "agents/report_agent.py 使用 get_llm" "grep -q 'from utils.llm_client import get_llm' agents/report_agent.py"
echo ""

echo "6. 检查语法错误..."
check "config/settings.py 语法正确" "python -m py_compile config/settings.py"
check "utils/llm_client.py 语法正确" "python -m py_compile utils/llm_client.py"
echo ""

echo "7. 检查测试脚本..."
check "test_llm_providers.py 存在" "test -f test_llm_providers.py"
echo ""

# 汇总结果
echo "========================================="
echo "验证结果汇总"
echo "========================================="
echo -e "${GREEN}通过: $PASS 项${NC}"
echo -e "${RED}失败: $FAIL 项${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}🎉 所有检查通过！可以继续下一步测试。${NC}"
    echo ""
    echo "下一步:"
    echo "  1. 确保 .env 中的 GLM_API_KEY 已填写"
    echo "  2. 运行测试: python test_llm_providers.py"
    echo "  3. 启动服务: python api.py"
    exit 0
else
    echo -e "${RED}❌ 还有 $FAIL 项检查未通过，请修复后再继续。${NC}"
    echo ""
    echo "修复建议:"
    echo "  - 参考 docs/glm-code-checklist.md 修改代码"
    echo "  - 运行脚本的详细检查: bash scripts/integrate_glm.sh"
    exit 1
fi