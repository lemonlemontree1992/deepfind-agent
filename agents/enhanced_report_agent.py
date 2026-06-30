"""增强版报告撰写 Agent - 实现多阶段生成流程

核心改进：
1. 内容分类与组织
2. 报告大纲规划
3. 分章节撰写
4. 质量审阅与优化
5. 执行摘要生成
"""

import json
import logging
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_deepseek import ChatDeepSeek
from langgraph.graph import StateGraph, END

from config import settings
from prompts.report_prompts import (
    CONTENT_CLASSIFICATION_PROMPT,
    KEY_INSIGHTS_EXTRACTION_PROMPT,
    REPORT_PLANNING_PROMPT,
    SECTION_WRITING_PROMPT,
    REPORT_REVIEW_PROMPT,
    EXECUTIVE_SUMMARY_PROMPT,
    FINAL_REPORT_TEMPLATE,
)

logger = logging.getLogger(__name__)


class EnhancedReportState(TypedDict):
    """增强版报告状态"""
    query: str
    analyzed_content: List[Dict[str, Any]]

    # 分类和组织结果
    classified_content: Dict[str, Any]
    key_insights: str
    report_type: str

    # 大纲和规划
    outline: str
    outline_sections: List[Dict[str, Any]]

    # 生成的内容
    sections_content: Dict[str, str]
    draft_report: str

    # 审阅结果
    review_score: float
    review_issues: List[str]
    review_suggestions: str

    # 最终报告
    executive_summary: str
    final_report: str
    sources: List[Dict[str, str]]

    # 其他状态
    current_step: str
    error: str
    model: Optional[str]

    # 流式输出回调
    stream_callback: Optional[Any]


def classify_content(state: EnhancedReportState) -> Dict[str, Any]:
    """步骤1: 对搜索结果进行分类和组织"""
    analyzed_content = state.get("analyzed_content", [])
    query = state.get("query", "")
    model = state.get("model") or settings.deepseek_model
    stream_callback = state.get("stream_callback")

    if not analyzed_content:
        logger.warning("没有分析内容，跳过分类步骤")
        return {
            "classified_content": {"themes": [], "cross_theme_insights": [], "data_gaps": []},
            "current_step": "classifying",
        }

    try:
        if stream_callback:
            stream_callback("step", "正在对内容进行分类组织...")

        llm = ChatDeepSeek(
            model=model,
            temperature=0.3,  # 分类任务使用较低温度
            api_key=settings.deepseek_api_key,
        )

        # 准备搜索结果文本
        search_results_text = ""
        for i, item in enumerate(analyzed_content, 1):
            content_preview = item.get("content", "")[:1500]  # 限制长度
            search_results_text += f"\n[来源 {i}]\n"
            search_results_text += f"标题: {item.get('title', '未知标题')}\n"
            search_results_text += f"URL: {item.get('url', '')}\n"
            search_results_text += f"内容摘要: {content_preview}...\n"
            search_results_text += "-" * 50 + "\n"

        prompt = CONTENT_CLASSIFICATION_PROMPT.format(
            query=query,
            search_results=search_results_text[:8000]  # 限制总长度
        )

        messages = [
            SystemMessage(content="你是一位专业的信息分析师，擅长对复杂信息进行分类和组织。请严格按照 JSON 格式输出结果。"),
            HumanMessage(content=prompt),
        ]

        logger.info("开始内容分类...")
        response = llm.invoke(messages)

        # 解析 JSON 响应
        try:
            # 提取 JSON 内容
            content = response.content
            # 尝试找到 JSON 块
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_content = content[json_start:json_end].strip()
            elif "```" in content:
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                json_content = content[json_start:json_end].strip()
            else:
                json_content = content.strip()

            classified_content = json.loads(json_content)
        except json.JSONDecodeError:
            logger.warning("JSON 解析失败，使用默认分类")
            classified_content = {
                "themes": [{
                    "name": "综合分析",
                    "description": f"关于 {query} 的综合分析",
                    "sources": [
                        {"id": i+1, "title": item.get("title", ""), "url": item.get("url", ""),
                         "credibility": "medium", "key_data": [], "key_insights": [], "relevance_score": 0.8}
                        for i, item in enumerate(analyzed_content[:10])
                    ]
                }],
                "cross_theme_insights": [],
                "data_gaps": []
            }

        logger.info(f"内容分类完成，识别出 {len(classified_content.get('themes', []))} 个主题")

        return {
            "classified_content": classified_content,
            "current_step": "extracting_insights",
        }

    except Exception as e:
        logger.error(f"内容分类失败: {str(e)}")
        return {
            "classified_content": {"themes": [], "cross_theme_insights": [], "data_gaps": []},
            "current_step": "classifying",
            "error": str(e),
        }


def extract_key_insights(state: EnhancedReportState) -> Dict[str, Any]:
    """步骤2: 提取关键洞察"""
    query = state.get("query", "")
    classified_content = state.get("classified_content", {})
    model = state.get("model") or settings.deepseek_model
    stream_callback = state.get("stream_callback")

    try:
        if stream_callback:
            stream_callback("step", "正在提取关键洞察...")

        llm = ChatDeepSeek(
            model=model,
            temperature=0.5,
            api_key=settings.deepseek_api_key,
        )

        # 格式化分类内容
        classified_text = json.dumps(classified_content, ensure_ascii=False, indent=2)

        prompt = KEY_INSIGHTS_EXTRACTION_PROMPT.format(
            query=query,
            classified_content=classified_text[:10000]
        )

        messages = [
            SystemMessage(content="你是一位资深研究分析师，擅长从复杂信息中提取关键洞察和趋势。"),
            HumanMessage(content=prompt),
        ]

        logger.info("开始提取关键洞察...")
        response = llm.invoke(messages)
        key_insights = response.content

        logger.info(f"关键洞察提取完成，长度: {len(key_insights)}")

        return {
            "key_insights": key_insights,
            "current_step": "planning",
        }

    except Exception as e:
        logger.error(f"提取关键洞察失败: {str(e)}")
        return {
            "key_insights": "关键洞察提取失败",
            "current_step": "planning",
            "error": str(e),
        }


def plan_report_outline(state: EnhancedReportState) -> Dict[str, Any]:
    """步骤3: 规划报告大纲"""
    query = state.get("query", "")
    key_insights = state.get("key_insights", "")
    classified_content = state.get("classified_content", {})
    model = state.get("model") or settings.deepseek_model
    stream_callback = state.get("stream_callback")

    try:
        if stream_callback:
            stream_callback("step", "正在规划报告结构...")

        llm = ChatDeepSeek(
            model=model,
            temperature=0.5,
            api_key=settings.deepseek_api_key,
        )

        # 格式化主题信息
        themes_text = ""
        for theme in classified_content.get("themes", []):
            themes_text += f"- {theme.get('name', '')}: {theme.get('description', '')}\n"

        prompt = REPORT_PLANNING_PROMPT.format(
            query=query,
            key_insights=key_insights[:3000],
            themes=themes_text
        )

        messages = [
            SystemMessage(content="你是一位专业的研究报告架构师，擅长设计清晰的报告结构。"),
            HumanMessage(content=prompt),
        ]

        logger.info("开始规划报告大纲...")
        response = llm.invoke(messages)
        outline = response.content

        # 提取报告类型
        report_type = "综合研究"
        if "技术研究" in outline:
            report_type = "技术研究"
        elif "市场研究" in outline:
            report_type = "市场研究"
        elif "政策研究" in outline:
            report_type = "政策研究"

        # 解析大纲章节
        outline_sections = []
        current_section = None
        for line in outline.split("\n"):
            line = line.strip()
            if line.startswith("## ") and not line.startswith("## 执行摘要"):
                if current_section:
                    outline_sections.append(current_section)
                current_section = {
                    "title": line[3:].strip(),
                    "content": "",
                    "points": []
                }
            elif current_section and line.startswith("- "):
                current_section["points"].append(line[2:])
            elif current_section and line:
                current_section["content"] += line + "\n"

        if current_section:
            outline_sections.append(current_section)

        logger.info(f"报告大纲规划完成，共 {len(outline_sections)} 个章节，类型: {report_type}")

        return {
            "outline": outline,
            "outline_sections": outline_sections,
            "report_type": report_type,
            "current_step": "writing_sections",
        }

    except Exception as e:
        logger.error(f"规划报告大纲失败: {str(e)}")
        return {
            "outline": f"# 报告大纲\n\n## 1. 背景介绍\n## 2. 核心分析\n## 3. 结论建议",
            "outline_sections": [
                {"title": "背景介绍", "content": "", "points": []},
                {"title": "核心分析", "content": "", "points": []},
                {"title": "结论建议", "content": "", "points": []},
            ],
            "report_type": "综合研究",
            "current_step": "writing_sections",
            "error": str(e),
        }


def write_sections(state: EnhancedReportState) -> Dict[str, Any]:
    """步骤4: 逐章节撰写内容"""
    query = state.get("query", "")
    outline_sections = state.get("outline_sections", [])
    analyzed_content = state.get("analyzed_content", [])
    classified_content = state.get("classified_content", {})
    model = state.get("model") or settings.deepseek_model
    stream_callback = state.get("stream_callback")

    sections_content = {}
    previous_summary = ""

    try:
        llm = ChatDeepSeek(
            model=model,
            temperature=0.7,  # 创作任务使用中等温度
            api_key=settings.deepseek_api_key,
        )

        # 准备素材摘要
        sources_by_theme = {}
        for theme in classified_content.get("themes", []):
            theme_name = theme.get("name", "")
            sources_by_theme[theme_name] = theme.get("sources", [])

        for i, section in enumerate(outline_sections):
            section_title = section.get("title", f"章节 {i+1}")

            if stream_callback:
                stream_callback("step", f"正在撰写: {section_title}")

            logger.info(f"撰写章节: {section_title}")

            # 查找相关来源
            relevant_sources = ""
            added_ids = set()

            # 首先添加主题相关的来源
            for theme_name, sources in sources_by_theme.items():
                if any(keyword in section_title for keyword in theme_name.split()):
                    for source in sources[:5]:
                        source_id = source.get("id")
                        if source_id not in added_ids:
                            added_ids.add(source_id)
                            relevant_sources += f"\n[来源 {source_id}] {source.get('title', '')}\n"
                            relevant_sources += f"URL: {source.get('url', '')}\n"
                            # 查找完整内容
                            for item in analyzed_content:
                                if item.get("url") == source.get("url"):
                                    relevant_sources += f"内容: {item.get('content', '')[:1000]}...\n"
                                    break

            # 补充通用来源
            if len(added_ids) < 5:
                for item in analyzed_content[:10]:
                    source_id = analyzed_content.index(item) + 1
                    if source_id not in added_ids:
                        relevant_sources += f"\n[来源 {source_id}] {item.get('title', '')}\n"
                        relevant_sources += f"URL: {item.get('url', '')}\n"
                        relevant_sources += f"内容: {item.get('content', '')[:800]}...\n"
                        added_ids.add(source_id)
                        if len(added_ids) >= 8:
                            break

            # 格式化章节要点
            section_points = "\n".join([f"- {p}" for p in section.get("points", [])])

            prompt = SECTION_WRITING_PROMPT.format(
                query=query,
                section_title=section_title,
                section_overview=section.get("content", f"关于 {section_title} 的详细分析"),
                section_points=section_points or f"深入分析 {section_title}",
                relevant_sources=relevant_sources[:6000],
                previous_sections_summary=previous_summary[:2000]
            )

            messages = [
                SystemMessage(content="你是一位专业的研究报告撰写专家，擅长撰写结构清晰、论证严谨的研究报告章节。"),
                HumanMessage(content=prompt),
            ]

            response = llm.invoke(messages)
            section_content = response.content

            sections_content[section_title] = section_content

            # 更新摘要
            previous_summary += f"\n{section_title}: {section_content[:200]}..."

            logger.info(f"章节 '{section_title}' 撰写完成，长度: {len(section_content)}")

        return {
            "sections_content": sections_content,
            "current_step": "assembling",
        }

    except Exception as e:
        logger.error(f"撰写章节失败: {str(e)}")
        return {
            "sections_content": {},
            "current_step": "assembling",
            "error": str(e),
        }


def assemble_draft(state: EnhancedReportState) -> Dict[str, Any]:
    """步骤5: 组装报告草稿"""
    sections_content = state.get("sections_content", {})
    outline = state.get("outline", "")
    stream_callback = state.get("stream_callback")

    try:
        if stream_callback:
            stream_callback("step", "正在组装报告...")

        # 组装报告
        draft = ""
        for section_title, content in sections_content.items():
            draft += f"\n## {section_title}\n\n{content}\n\n"

        logger.info(f"报告草稿组装完成，总长度: {len(draft)}")

        return {
            "draft_report": draft,
            "current_step": "reviewing",
        }

    except Exception as e:
        logger.error(f"组装报告失败: {str(e)}")
        return {
            "draft_report": "",
            "current_step": "reviewing",
            "error": str(e),
        }


def review_report(state: EnhancedReportState) -> Dict[str, Any]:
    """步骤6: 质量审阅"""
    query = state.get("query", "")
    draft_report = state.get("draft_report", "")
    model = state.get("model") or settings.deepseek_model
    stream_callback = state.get("stream_callback")

    try:
        if stream_callback:
            stream_callback("step", "正在审阅报告质量...")

        llm = ChatDeepSeek(
            model=model,
            temperature=0.3,  # 审阅任务使用低温度
            api_key=settings.deepseek_api_key,
        )

        prompt = REPORT_REVIEW_PROMPT.format(
            query=query,
            report_content=draft_report[:15000]  # 限制长度
        )

        messages = [
            SystemMessage(content="你是一位资深的研究报告编辑，擅长评估报告质量并提出改进建议。"),
            HumanMessage(content=prompt),
        ]

        logger.info("开始审阅报告...")
        response = llm.invoke(messages)
        review_result = response.content

        # 解析评分
        review_score = 35.0  # 默认分数
        try:
            import re
            score_match = re.search(r'\*\*综合得分\*\*[：:]\s*(\d+(?:\.\d+)?)/50', review_result)
            if score_match:
                review_score = float(score_match.group(1))
        except:
            pass

        # 提取问题
        review_issues = []
        if "严重问题" in review_result:
            issues_start = review_result.find("严重问题")
            issues_end = review_result.find("####", issues_start) if "####" in review_result[issues_start:] else len(review_result)
            issues_section = review_result[issues_start:issues_end]
            for line in issues_section.split("\n"):
                if line.strip().startswith(("1.", "2.", "3.", "4.", "5.")):
                    review_issues.append(line.strip())

        logger.info(f"报告审阅完成，得分: {review_score}/50，发现 {len(review_issues)} 个问题")

        return {
            "review_score": review_score,
            "review_issues": review_issues,
            "review_suggestions": review_result,
            "current_step": "finalizing",
        }

    except Exception as e:
        logger.error(f"审阅报告失败: {str(e)}")
        return {
            "review_score": 40.0,
            "review_issues": [],
            "review_suggestions": "",
            "current_step": "finalizing",
            "error": str(e),
        }


def generate_executive_summary(state: EnhancedReportState) -> Dict[str, Any]:
    """步骤7: 生成执行摘要"""
    query = state.get("query", "")
    draft_report = state.get("draft_report", "")
    key_insights = state.get("key_insights", "")
    stream_callback = state.get("stream_callback")
    model = state.get("model") or settings.deepseek_model

    try:
        if stream_callback:
            stream_callback("step", "正在生成执行摘要...")

        llm = ChatDeepSeek(
            model=model,
            temperature=0.5,
            api_key=settings.deepseek_api_key,
        )

        # 提取关键数据
        key_data = ""
        if key_insights:
            # 从关键洞察中提取数据
            import re
            numbers = re.findall(r'[\d,]+(?:\.\d+)?(?:\s*[%亿美元万元]|\s*个|\s*次|\s*人)', key_insights)
            key_data = "\n".join(numbers[:10])

        prompt = EXECUTIVE_SUMMARY_PROMPT.format(
            query=query,
            report_content=draft_report[:12000],
            key_data=key_data
        )

        messages = [
            SystemMessage(content="你是一位专业的商业分析师，擅长撰写精炼有力的执行摘要。"),
            HumanMessage(content=prompt),
        ]

        logger.info("生成执行摘要...")
        response = llm.invoke(messages)
        executive_summary = response.content

        logger.info(f"执行摘要生成完成，长度: {len(executive_summary)}")

        return {
            "executive_summary": executive_summary,
            "current_step": "completed",
        }

    except Exception as e:
        logger.error(f"生成执行摘要失败: {str(e)}")
        return {
            "executive_summary": "执行摘要生成失败",
            "current_step": "completed",
            "error": str(e),
        }


def assemble_final_report(state: EnhancedReportState) -> Dict[str, Any]:
    """步骤8: 组装最终报告"""
    query = state.get("query", "")
    executive_summary = state.get("executive_summary", "")
    sections_content = state.get("sections_content", {})
    draft_report = state.get("draft_report", "")
    analyzed_content = state.get("analyzed_content", [])
    report_type = state.get("report_type", "综合研究")
    review_issues = state.get("review_issues", [])
    stream_callback = state.get("stream_callback")

    try:
        if stream_callback:
            stream_callback("step", "正在组装最终报告...")

        # 生成目录
        toc = "## 目录\n\n"
        section_num = 1
        for section_title in sections_content.keys():
            toc += f"{section_num}. {section_title}\n"
            section_num += 1

        # 生成建议
        conclusion = "\n基于以上分析，我们提出以下建议：\n\n"
        if review_issues:
            conclusion += "**需要注意的问题**：\n"
            for issue in review_issues[:3]:
                conclusion += f"- {issue}\n"
            conclusion += "\n"

        conclusion += "**进一步研究方向**：\n"
        conclusion += "- 建议持续关注该领域的发展动态\n"
        conclusion += "- 收集更多一手数据和用户反馈\n"
        conclusion += "- 进行深入的专家访谈以获得更深层次的洞察\n"

        # 生成局限性声明
        limitations = """
本报告基于公开可获得的信息进行分析，存在以下局限性：
1. **信息来源局限性**：报告依赖搜索引擎返回的信息，可能存在信息选择性偏差
2. **时效性限制**：信息截至报告生成时刻，后续发展可能改变部分结论
3. **AI 分析局限**：报告使用 AI 进行内容分析和组织，可能存在理解偏差
4. **不可抗因素**：某些领域可能受到数据可获得性、语言障碍等因素影响
"""

        # 生成参考资料（使用正确的Markdown链接格式）
        references = ""
        for i, item in enumerate(analyzed_content, 1):
            title = item.get("title", "未知标题")
            url = item.get("url", "")
            if url:
                references += f"{i}. [{title}]({url})\n"
            else:
                references += f"{i}. {title}\n"

        # 组装最终报告
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')

        final_report = FINAL_REPORT_TEMPLATE.format(
            query=query,
            timestamp=timestamp,
            source_count=len(analyzed_content),
            report_type=report_type,
            executive_summary=executive_summary,
            table_of_contents=toc,
            main_content=draft_report,
            conclusion=conclusion,
            limitations=limitations,
            references=references,
            analyzed_pages=len(analyzed_content),
        )

        # 准备来源列表
        sources = [
            {"id": i + 1, "title": item.get("title", "未知标题"), "url": item.get("url", "")}
            for i, item in enumerate(analyzed_content)
        ]

        logger.info(f"最终报告组装完成，总长度: {len(final_report)}")

        return {
            "final_report": final_report,
            "sources": sources,
            "current_step": "completed",
        }

    except Exception as e:
        logger.error(f"组装最终报告失败: {str(e)}")
        return {
            "final_report": f"# 报告生成失败\n\n错误信息: {str(e)}",
            "sources": [],
            "current_step": "completed",
            "error": str(e),
        }


# =============================================================================
# 构建增强版报告生成 Agent
# =============================================================================

def build_enhanced_report_agent():
    """构建增强版报告 Agent 工作流"""
    workflow = StateGraph(EnhancedReportState)

    # 添加节点
    workflow.add_node("classify", classify_content)
    workflow.add_node("extract_insights", extract_key_insights)
    workflow.add_node("plan_outline", plan_report_outline)
    workflow.add_node("write_sections", write_sections)
    workflow.add_node("assemble_draft", assemble_draft)
    workflow.add_node("review", review_report)
    workflow.add_node("generate_summary", generate_executive_summary)
    workflow.add_node("final_assemble", assemble_final_report)

    # 定义工作流
    workflow.set_entry_point("classify")
    workflow.add_edge("classify", "extract_insights")
    workflow.add_edge("extract_insights", "plan_outline")
    workflow.add_edge("plan_outline", "write_sections")
    workflow.add_edge("write_sections", "assemble_draft")
    workflow.add_edge("assemble_draft", "review")
    workflow.add_edge("review", "generate_summary")
    workflow.add_edge("generate_summary", "final_assemble")
    workflow.add_edge("final_assemble", END)

    return workflow.compile()


def run_enhanced_report(
    query: str,
    analyzed_content: List[Dict[str, Any]],
    key_findings: str = "",
    model: str = None,
    stream_callback=None
) -> Dict[str, Any]:
    """运行增强版报告生成流程

    Args:
        query: 调研主题
        analyzed_content: 分析后的内容列表
        key_findings: 预提取的关键发现（可选，增强版会重新提取）
        model: 使用的模型
        stream_callback: 流式输出回调函数

    Returns:
        包含最终报告和来源的字典
    """
    logger.info(f"开始增强版报告生成流程，主题: {query}")

    agent = build_enhanced_report_agent()
    result = agent.invoke({
        "query": query,
        "analyzed_content": analyzed_content,
        "classified_content": {},
        "key_insights": key_findings,
        "report_type": "",
        "outline": "",
        "outline_sections": [],
        "sections_content": {},
        "draft_report": "",
        "review_score": 0.0,
        "review_issues": [],
        "review_suggestions": "",
        "executive_summary": "",
        "final_report": "",
        "sources": [],
        "current_step": "init",
        "error": "",
        "model": model,
        "stream_callback": stream_callback,
    })

    return result