"""
DeepFind Agent - 主工作流

流程：
1. Write TODOs - 拆解任务
2. Save Context - 保存用户问题到 research_request.md
3. Search - 调用搜索工具深度调研
4. Analyze - 分析网页内容
5. Report - 撰写报告到 research_request.md
6. Verify - 验证报告完整性
"""

import os
import logging
import re
from datetime import datetime
from typing import Dict, Any, List

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_deepseek import ChatDeepSeek

from config import settings
from agents import run_search, run_analyze, run_report
from utils import generate_pdf, generate_html, generate_markdown_file

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def write_todos(query: str) -> List[str]:
    """
    拆解任务为具体步骤（优化版：使用快速模型）

    Args:
        query: 用户调研问题

    Returns:
        任务列表
    """
    try:
        llm = ChatDeepSeek(
            model="deepseek-chat",  # 使用快速模型
            temperature=0.3,
            api_key=settings.deepseek_api_key,
        )

        system_prompt = """你是一个任务规划专家。根据用户的调研需求，拆解为具体的执行步骤。

要求：
1. 拆解为 3-5 个具体步骤
2. 每个步骤要可执行、可验证
3. 步骤之间要有逻辑顺序
4. 使用中文输出

输出格式（纯文本，每行一个步骤）：
步骤1：具体描述
步骤2：具体描述
..."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query),
        ]

        response = llm.invoke(messages)
        todos = []

        for line in response.content.split("\n"):
            line = line.strip()
            if line:
                # 移除可能的编号前缀
                if line[0].isdigit() and "." in line[:3]:
                    line = line.split(".", 1)[1].strip()
                if line:
                    todos.append(line)

        logger.info(f"生成 {len(todos)} 个任务步骤")
        return todos

    except Exception as e:
        logger.error(f"拆解任务失败: {str(e)}")
        return [f"调研主题: {query}", "执行多维度搜索", "分析搜索结果", "撰写调研报告"]


def save_research_request(query: str, output_dir: str) -> str:
    """
    保存用户问题到 research_request.md

    Args:
        query: 用户调研问题
        output_dir: 输出目录

    Returns:
        文件路径
    """
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, "research_request.md")

    content = f"""# 调研需求

## 原始问题
{query}

## 创建时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 状态
进行中...

---
"""

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info(f"保存调研需求到: {file_path}")
    return file_path


def update_research_request(file_path: str, report: str, sources: List[Dict[str, str]]):
    """
    更新 research_request.md，添加完整报告

    Args:
        file_path: 文件路径
        report: 调研报告内容
        sources: 参考来源列表
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 更新状态
        content = content.replace("进行中...", "已完成 ✓")

        # 添加报告内容
        content += f"\n\n## 调研报告\n\n{report}\n"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"更新调研报告到: {file_path}")
    except Exception as e:
        logger.error(f"更新文件失败: {str(e)}")


def verify_report(report: str) -> Dict[str, Any]:
    """
    验证报告完整性

    Args:
        report: 报告内容

    Returns:
        验证结果
    """
    issues = []
    score = 100

    # 检查引用
    refs = re.findall(r'\[(\d+)\]', report)
    if not refs:
        issues.append("报告缺少引用标注 [-10分]")
        score -= 10

    # 检查结构
    required_sections = ["摘要", "背景", "分析", "参考资料"]
    for section in required_sections:
        if section not in report:
            issues.append(f"报告缺少「{section}」部分 [-10分]")
            score -= 10

    # 检查内容长度
    if len(report) < 2000:
        issues.append("报告内容较短，建议补充更多细节 [-10分]")
        score -= 10

    logger.info(f"报告验证得分: {score}/100")

    return {
        "score": max(score, 0),
        "issues": issues,
        "passed": score >= 60,
    }


def run_deepfind_workflow(query: str, output_dir: str = None) -> Dict[str, Any]:
    """
    运行完整调研工作流

    Args:
        query: 用户调研问题
        output_dir: 输出目录

    Returns:
        包含报告和元数据的结果字典
    """
    logger.info(f"开始调研工作流: {query}")

    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), "outputs")

    os.makedirs(output_dir, exist_ok=True)

    result = {
        "query": query,
        "todos": [],
        "request_file": "",
        "search_results": [],
        "analyzed_content": [],
        "report": "",
        "sources": [],
        "verification": {},
        "output_files": {},
        "errors": [],
    }

    try:
        # Step 1: Write TODOs
        logger.info("📋 Step 1: 拆解任务...")
        result["todos"] = write_todos(query)
        for i, todo in enumerate(result["todos"], 1):
            logger.info(f"   {i}. {todo}")

        # Step 2: Save Context
        logger.info("📝 Step 2: 保存调研需求...")
        result["request_file"] = save_research_request(query, output_dir)

        # Step 3: Search
        logger.info("🔍 Step 3: 执行搜索...")
        search_result = run_search(query)
        result["search_results"] = search_result.get("search_results", [])
        logger.info(f"   找到 {len(result['search_results'])} 个结果")

        if not result["search_results"]:
            logger.warning("搜索无结果，生成提示报告")
            result["errors"].append("搜索无结果")

        # Step 4: Analyze
        logger.info("🔬 Step 4: 分析内容...")
        analyze_result = run_analyze(result["search_results"])
        result["analyzed_content"] = analyze_result.get("analyzed_content", [])
        result["key_findings"] = analyze_result.get("key_findings", "")
        logger.info(f"   分析了 {len(result['analyzed_content'])} 个网页")

        # Step 5: Report
        logger.info("📊 Step 5: 撰写报告...")
        report_result = run_report(
            query,
            result["analyzed_content"],
            result.get("key_findings", "")
        )
        result["report"] = report_result.get("report", "")
        result["sources"] = report_result.get("sources", [])

        # 更新 research_request.md
        if result["report"]:
            update_research_request(result["request_file"], result["report"], result["sources"])

        # Step 6: Verify
        logger.info("✅ Step 6: 验证报告...")
        if result["report"]:
            result["verification"] = verify_report(result["report"])
            if result["verification"]["issues"]:
                for issue in result["verification"]["issues"]:
                    logger.warning(f"   {issue}")

        # 生成输出文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 清理文件名中的特殊字符
        safe_query = "".join(c for c in query[:20] if c.isalnum() or c in " -_").strip()
        safe_query = safe_query.replace(" ", "_")

        # Markdown 文件
        md_path = os.path.join(output_dir, f"report_{timestamp}_{safe_query}.md")
        if generate_markdown_file(result["report"], md_path):
            result["output_files"]["markdown"] = md_path

        # HTML 文件
        html_path = os.path.join(output_dir, f"report_{timestamp}_{safe_query}.html")
        if generate_html(result["report"], html_path, query):
            result["output_files"]["html"] = html_path

        # PDF 文件
        pdf_path = os.path.join(output_dir, f"report_{timestamp}_{safe_query}.pdf")
        if generate_pdf(result["report"], pdf_path, query):
            result["output_files"]["pdf"] = pdf_path

        logger.info("🎉 调研完成！")
        logger.info(f"   Markdown: {result['output_files'].get('markdown', '生成失败')}")
        logger.info(f"   HTML: {result['output_files'].get('html', '生成失败')}")

    except Exception as e:
        error_msg = str(e)
        logger.error(f"工作流执行失败: {error_msg}")

        # 解析错误类型，给出友好提示
        if "402" in error_msg or "Insufficient Balance" in error_msg:
            result["errors"].append("⚠️ DeepSeek API 余额不足，请充值后重试")
            result["errors"].append("充值地址: https://platform.deepseek.com/")
        else:
            result["errors"].append(str(e))

        if not result["report"]:
            error_report = f"""# 调研报告

**主题**: {query}

## ⚠️ 生成失败

抱歉，调研报告生成过程中遇到问题。

### 错误信息
{error_msg}

### 可能的原因
1. **DeepSeek API 余额不足** - 请前往 https://platform.deepseek.com/ 充值
2. **网络连接问题** - 请检查网络连接
3. **搜索源不可用** - 请稍后重试

### 建议
- 检查 API Key 是否有效
- 确认 API 账户余额
- 尝试使用不同的关键词
"""
            result["report"] = error_report

    return result


if __name__ == "__main__":
    # 测试
    test_query = "2024年中国新能源汽车市场格局分析"
    result = run_deepfind_workflow(test_query)
    print(result["report"])