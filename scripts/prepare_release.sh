#!/bin/bash

# ==========================================
# DeepFind Agent 发布准备脚本
# 用途: 自动化完成发布前的准备工作
# 使用: chmod +x scripts/prepare_release.sh && ./scripts/prepare_release.sh
# ==========================================

set -e  # 遇到错误立即退出

echo "🚀 DeepFind Agent 发布准备脚本"
echo "================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 步骤计数器
STEP=0

# ========== 步骤1: 检查敏感信息 ==========
echo -e "${YELLOW}步骤 $((STEP+=1)): 检查敏感信息...${NC}"

# 检查.env文件是否在.gitignore中
if grep -q "^\.env$" .gitignore 2>/dev/null; then
    echo -e "${GREEN}✅ .env已在.gitignore中${NC}"
else
    echo -e "${RED}⚠️  .env未在.gitignore中，正在添加...${NC}"
    echo ".env" >> .gitignore
    echo -e "${GREEN}✅ 已添加.env到.gitignore${NC}"
fi

# 检查代码中是否有硬编码的API Key
echo "检查代码中是否有硬编码的API Key..."
if grep -r "sk-[a-zA-Z0-9]" . --include="*.py" --exclude-dir=venv --exclude-dir=.git 2>/dev/null; then
    echo -e "${RED}❌ 发现硬编码的API Key，请手动删除！${NC}"
    echo "   请检查上述文件并删除硬编码的API Key"
else
    echo -e "${GREEN}✅ 未发现硬编码的API Key${NC}"
fi

echo ""

# ========== 步骤2: 清理不必要的文件 ==========
echo -e "${YELLOW}步骤 $((STEP+=1)): 清理不必要的文件...${NC}"

# 删除日志文件
echo "删除日志文件..."
find . -name "*.log" -type f -not -path "./venv/*" -not -path "./.git/*" -delete 2>/dev/null || true
echo -e "${GREEN}✅ 已删除日志文件${NC}"

# 删除压缩文件
echo "删除压缩文件..."
find . -name "*.zip" -type f -not -path "./venv/*" -not -path "./.git/*" -delete 2>/dev/null || true
echo -e "${GREEN}✅ 已删除压缩文件${NC}"

# 删除__pycache__目录
echo "删除__pycache__目录..."
find . -name "__pycache__" -type d -not -path "./venv/*" -not -path "./.git/*" -exec rm -rf {} + 2>/dev/null || true
echo -e "${GREEN}✅ 已删除__pycache__目录${NC}"

# 清空outputs目录（保留.gitkeep）
echo "清空outputs目录..."
if [ -d "outputs" ]; then
    find outputs -type f -not -name ".gitkeep" -delete 2>/dev/null || true
    echo -e "${GREEN}✅ 已清空outputs目录${NC}"
fi

# 删除.DS_Store文件
echo "删除.DS_Store文件..."
find . -name ".DS_Store" -type f -delete 2>/dev/null || true
echo -e "${GREEN}✅ 已删除.DS_Store文件${NC}"

echo ""

# ========== 步骤3: 创建必要的文件 ==========
echo -e "${YELLOW}步骤 $((STEP+=1)): 创建必要的文件...${NC}"

# 创建.gitkeep文件（如果不存在）
if [ -d "outputs" ]; then
    touch outputs/.gitkeep
    echo -e "${GREEN}✅ 已创建outputs/.gitkeep${NC}"
fi

if [ -d "test/test_outputs/reports" ]; then
    touch test/test_outputs/reports/.gitkeep
    echo -e "${GREEN}✅ 已创建test/test_outputs/reports/.gitkeep${NC}"
fi

if [ -d "test/test_outputs/logs" ]; then
    touch test/test_outputs/logs/.gitkeep
    echo -e "${GREEN}✅ 已创建test/test_outputs/logs/.gitkeep${NC}"
fi

# 创建目录（如果不存在）
mkdir -p .github/ISSUE_TEMPLATE
mkdir -p .github/workflows
echo -e "${GREEN}✅ 已创建.github目录${NC}"

echo ""

# ========== 步骤4: 检查必要文件是否存在 ==========
echo -e "${YELLOW}步骤 $((STEP+=1)): 检查必要文件是否存在...${NC}"

required_files=("README.md" "LICENSE" "CONTRIBUTING.md" "CHANGELOG.md" ".gitignore" ".env.example" "requirements.txt")

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file 存在${NC}"
    else
        echo -e "${RED}❌ $file 不存在${NC}"
    fi
done

echo ""

# ========== 步骤5: 统计项目信息 ==========
echo -e "${YELLOW}步骤 $((STEP+=1)): 统计项目信息...${NC}"

# 统计代码行数（排除venv）
echo "代码行数统计:"
python_lines=$(find . -name "*.py" -not -path "./venv/*" -not -path "./.git/*" | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}')
echo "  Python代码: $python_lines 行"

if [ -d "frontend/src" ]; then
    js_lines=$(find frontend/src -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}')
    echo "  JavaScript/TypeScript代码: $js_lines 行"
fi

# 统计文件数量
echo "文件数量统计:"
python_files=$(find . -name "*.py" -not -path "./venv/*" -not -path "./.git/*" | wc -l | awk '{print $1}')
echo "  Python文件: $python_files 个"

if [ -d "frontend/src" ]; then
    js_files=$(find frontend/src -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" | wc -l | awk '{print $1}')
    echo "  JavaScript/TypeScript文件: $js_files 个"
fi

echo ""

# ========== 步骤6: 显示文件大小 ==========
echo -e "${YELLOW}步骤 $((STEP+=1)): 显示项目大小...${NC}"

# 计算项目总大小（排除venv）
project_size=$(du -sh --exclude=venv --exclude=.git . 2>/dev/null | awk '{print $1}')
echo "项目总大小（排除venv）: $project_size"

# 计算venv大小
if [ -d "venv" ]; then
    venv_size=$(du -sh venv 2>/dev/null | awk '{print $1}')
    echo "虚拟环境大小: $venv_size"
fi

echo ""

# ========== 步骤7: 最终检查 ==========
echo -e "${YELLOW}步骤 $((STEP+=1)): 最终检查...${NC}"

# 检查是否有未提交的重要文件
echo "检查是否有未添加的重要文件..."
important_files=("api.py" "README.md" "requirements.txt" ".gitignore")

for file in "${important_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file 存在${NC}"
    else
        echo -e "${RED}❌ $file 不存在${NC}"
    fi
done

echo ""

# ========== 完成 ==========
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}✅ 发布准备完成！${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "📋 下一步操作:"
echo "1. 检查上述输出，确保所有检查项都通过"
echo "2. 如果发现硬编码的API Key，请手动删除"
echo "3. 如果缺失必要文件，请参考 docs/RELEASE_CHECKLIST.md 创建"
echo "4. 准备好后，运行以下命令:"
echo ""
echo "   # 初始化Git仓库"
echo "   git init"
echo ""
echo "   # 添加所有文件"
echo "   git add ."
echo ""
echo "   # 提交"
echo "   git commit -m '🎉 Initial commit: DeepFind Agent v1.0.0'"
echo ""
echo "   # 连接GitHub仓库（替换yourusername）"
echo "   git remote add origin https://github.com/yourusername/deepfind-agent.git"
echo ""
echo "   # 推送到GitHub"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "📚 详细说明请查看: docs/RELEASE_CHECKLIST.md"
echo ""