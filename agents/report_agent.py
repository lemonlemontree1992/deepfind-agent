"""自适应报告生成 Agent - 根据内容类型自动选择最佳输出格式"""

import json
import logging
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

from config import settings
from prompts.adaptive_prompts import ADAPTIVE_REPORT_PROMPT, CONCISE_OUTPUT_PROMPT, TRAVEL_GUIDE_PERFECT_PROMPT
from utils.llm_client import get_llm

logger = logging.getLogger(__name__)


class ReportState(TypedDict):
    """报告状态"""
    query: str
    analyzed_content: List[Dict[str, Any]]
    entities: Dict[str, Any]  # 提取的结构化实体
    content_type: str  # 内容类型
    key_findings: str
    report: str
    sources: List[Dict[str, str]]
    current_step: str
    error: str
    model: Optional[str]


def prepare_sources_summary(analyzed_content: List[Dict[str, Any]], max_sources: int = 8) -> str:
    """准备来源摘要"""
    sources_parts = []
    for i, item in enumerate(analyzed_content[:max_sources], 1):
        title = item.get('title', '未知标题')
        url = item.get('url', '')
        content = item.get('content', '')[:500]
        sources_parts.append(f"[来源 {i}] {title}\n{content}\n")
    return "\n---\n".join(sources_parts)


def generate_adaptive_report(state: ReportState) -> Dict[str, Any]:
    """生成自适应报告 - 根据内容类型选择最佳输出格式"""
    query = state.get("query", "")
    analyzed_content = state.get("analyzed_content", [])
    entities = state.get("entities", {})
    content_type = state.get("content_type", "other")
    key_findings = state.get("key_findings", "")
    model = state.get("model") or settings.deepseek_model

    if not analyzed_content:
        logger.warning("没有分析内容，生成简化报告")
        return {
            "report": f"# {query}\n\n很抱歉，未能获取有效的搜索结果，无法生成报告。",
            "sources": [],
            "current_step": "completed",
        }

    try:
        # 报告生成使用快速模型（格式化输出不需要深度推理）
        llm = get_llm(model="deepseek-chat", temperature=0.7)

        # 准备来源摘要
        sources_summary = prepare_sources_summary(analyzed_content)

        # 准备实体信息
        entities_str = json.dumps(entities, ensure_ascii=False, indent=2) if entities else "{}"

        # 根据内容类型选择不同的 Prompt 模板
        if content_type == "travel":
            # 旅行攻略使用完美模板（双方案模式 + 细节丰富度）
            report_prompt = TRAVEL_GUIDE_PERFECT_PROMPT.format(
                query=query,
                entities=entities_str,
                sources=sources_summary
            )
            logger.info(f"使用旅行攻略完美模板（双方案模式）")
        else:
            # 其他内容类型使用通用自适应模板
            report_prompt = ADAPTIVE_REPORT_PROMPT.format(
                query=query,
                entities=entities_str,
                sources=sources_summary
            )

        logger.info(f"生成自适应报告，内容类型: {content_type}")

        # 流式生成报告
        response = llm.invoke(messages=[
            SystemMessage(content=report_prompt),
            HumanMessage(content="请根据提取的信息生成报告，选择最适合的输出格式。")
        ])
        report_content = response.content

        # 添加报告头部信息
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')

        # 根据内容类型添加不同的标题
        type_labels = {
            "weather": "天气预报",
            "product": "产品评测",
            "travel": "旅行攻略",
            "tech": "技术指南",
            "news": "新闻资讯",
            "qa": "问答",
            "other": "信息汇总"
        }
        type_label = type_labels.get(content_type, "信息汇总")

        # 准备来源列表
        sources = [
            {"id": i + 1, "title": item.get("title", "未知标题"), "url": item.get("url", "")}
            for i, item in enumerate(analyzed_content)
        ]

        # 生成参考资料章节
        references_section = "\n## 参考资料\n\n"
        for source in sources:
            title = source.get("title", "未知标题")
            url = source.get("url", "")
            if url:
                references_section += f"{source['id']}. [{title}]({url})\n"
            else:
                references_section += f"{source['id']}. {title}\n"

        report = f"""# {query}

**类型**：{type_label}
**生成时间**：{timestamp}
**数据来源**：{len(analyzed_content)} 个来源

---

{report_content}
{references_section}
---

*本报告由 DeepFind Agent 自动生成，信息来源于公开网络，仅供参考。*
"""

        logger.info(f"报告生成完成，长度: {len(report)}")

        return {
            "report": report,
            "sources": sources,
            "current_step": "completed",
        }

    except Exception as e:
        logger.error(f"生成报告失败: {str(e)}")
        return {
            "report": f"# {query}\n\n报告生成失败: {str(e)}",
            "sources": [],
            "current_step": "completed",
            "error": str(e),
        }


def generate_concise_report(state: ReportState) -> Dict[str, Any]:
    """生成简洁报告 - 用于简单查询"""
    query = state.get("query", "")
    analyzed_content = state.get("analyzed_content", [])
    model = state.get("model") or settings.deepseek_model

    if not analyzed_content:
        return {
            "report": f"# {query}\n\n未能找到相关信息。",
            "sources": [],
            "current_step": "completed",
        }

    try:
        # 简洁报告使用快速模型
        llm = get_llm(model="deepseek-chat", temperature=0.3)

        # 准备内容
        content = prepare_sources_summary(analyzed_content[:5])

        # 使用简洁输出 Prompt
        concise_prompt = CONCISE_OUTPUT_PROMPT.format(
            query=query,
            content=content
        )

        logger.info(f"生成简洁报告，查询: {query[:50]}...")

        response = llm.invoke([
            SystemMessage(content=concise_prompt),
            HumanMessage(content="请直接回答问题，简洁明了。")
        ])

        report_content = response.content

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')

        report = f"""# {query}

**生成时间**：{timestamp}

---

{report_content}

---

*信息来源：{len(analyzed_content)} 个来源*
"""

        sources = [
            {"id": i + 1, "title": item.get("title", "未知标题"), "url": item.get("url", "")}
            for i, item in enumerate(analyzed_content[:5])
        ]

        return {
            "report": report,
            "sources": sources,
            "current_step": "completed",
        }

    except Exception as e:
        logger.error(f"生成简洁报告失败: {str(e)}")
        return {
            "report": f"# {query}\n\n回答生成失败: {str(e)}",
            "sources": [],
            "current_step": "completed",
            "error": str(e),
        }


def build_report_agent():
    """构建自适应报告 Agent"""
    workflow = StateGraph(ReportState)

    workflow.add_node("generate", generate_adaptive_report)

    workflow.set_entry_point("generate")
    workflow.add_edge("generate", END)

    return workflow.compile()


def run_report(
    query: str,
    analyzed_content: List[Dict[str, Any]],
    entities: Dict[str, Any] = None,
    content_type: str = "other",
    key_findings: str = "",
    model: str = None
) -> Dict[str, Any]:
    """运行自适应报告生成

    Args:
        query: 用户查询
        analyzed_content: 分析后的内容
        entities: 提取的结构化实体
        content_type: 内容类型
        key_findings: 关键发现
        model: 使用的模型

    Returns:
        {"report": "...", "sources": [...]}
    """
    logger.info(f"开始生成报告，内容类型: {content_type}")

    agent = build_report_agent()
    result = agent.invoke({
        "query": query,
        "analyzed_content": analyzed_content,
        "entities": entities or {},
        "content_type": content_type,
        "key_findings": key_findings,
        "report": "",
        "sources": [],
        "current_step": "init",
        "error": "",
        "model": model,
    })

    return result


# 保留旧接口兼容性
def run_report_legacy(
    query: str,
    analyzed_content: List[Dict[str, Any]],
    key_findings: str = "",
    model: str = None
) -> Dict[str, Any]:
    """旧接口 - 兼容性保留"""
    return run_report(query, analyzed_content, {}, "other", key_findings, model)