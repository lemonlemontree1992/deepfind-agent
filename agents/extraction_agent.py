"""智能实体提取 Agent - 自动识别内容类型并提取结构化信息"""

import json
import logging
from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

from config import settings
from prompts.adaptive_prompts import INTELLIGENT_EXTRACTION_PROMPT
from utils.llm_client import get_llm

logger = logging.getLogger(__name__)


class ExtractionState(TypedDict):
    """提取状态"""
    analyzed_content: List[Dict[str, Any]]
    query: str
    content_type: str  # 自动识别的内容类型
    entities: Dict[str, Any]
    confidence_scores: Dict[str, float]
    extraction_metadata: Dict[str, Any]
    current_step: str
    error: str
    model: Optional[str]


def prepare_content_for_extraction(analyzed_content: List[Dict[str, Any]], max_sources: int = 10) -> str:
    """准备用于提取的内容"""
    content_parts = []
    for i, item in enumerate(analyzed_content[:max_sources], 1):
        title = item.get('title', '未知标题')
        url = item.get('url', '')
        content = item.get('content', '')[:2000]  # 限制每条内容的长度
        content_parts.append(f"""[来源 {i}] {title}
URL: {url}
内容:
{content}
---
""")
    return "\n".join(content_parts)


def extract_entities_intelligent(state: ExtractionState) -> Dict[str, Any]:
    """智能提取实体 - 自动识别内容类型"""
    analyzed_content = state.get("analyzed_content", [])
    query = state.get("query", "")
    model = state.get("model") or settings.deepseek_model

    if not analyzed_content:
        return {
            "content_type": "unknown",
            "entities": {},
            "confidence_scores": {},
            "extraction_metadata": {"error": "无内容可提取"},
            "current_step": "completed",
        }

    try:
        # 准备内容
        content = prepare_content_for_extraction(analyzed_content)

        # 构建提取 Prompt
        extraction_prompt = INTELLIGENT_EXTRACTION_PROMPT.format(content=content)

        # 调用 LLM
        llm = get_llm(model=model, temperature=0.3)

        logger.info(f"智能提取实体，查询: {query[:50]}...")

        response = llm.invoke([
            SystemMessage(content=extraction_prompt),
            HumanMessage(content=f"用户查询: {query}\n\n请提取结构化信息，输出JSON格式。")
        ])

        # 解析响应
        response_text = response.content.strip()

        # 移除可能的 markdown 代码块标记
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            # 移除第一行和最后一行
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            response_text = "\n".join(lines)

        # 解析 JSON
        result = json.loads(response_text)

        # 提取字段
        content_type = result.get("content_type", "unknown")
        entities = result.get("entities", {})
        summary = result.get("summary", "")
        key_facts = result.get("key_facts", [])
        metadata = result.get("extraction_metadata", {})

        # 计算置信度
        confidence_scores = {
            "overall": metadata.get("extraction_confidence", 0.7),
            "content_type": result.get("content_type_confidence", 0.8),
        }

        logger.info(f"提取完成，内容类型: {content_type}, 实体类型: {list(entities.keys())}")

        return {
            "content_type": content_type,
            "entities": entities,
            "confidence_scores": confidence_scores,
            "extraction_metadata": {
                **metadata,
                "summary": summary,
                "key_facts": key_facts,
                "total_sources": len(analyzed_content),
            },
            "current_step": "completed",
        }

    except json.JSONDecodeError as e:
        logger.error(f"JSON 解析失败: {str(e)}")
        return {
            "content_type": "unknown",
            "entities": {},
            "confidence_scores": {"overall": 0.0},
            "extraction_metadata": {"error": f"JSON解析失败: {str(e)}"},
            "current_step": "completed",
            "error": str(e),
        }
    except Exception as e:
        logger.error(f"实体提取失败: {str(e)}")
        return {
            "content_type": "unknown",
            "entities": {},
            "confidence_scores": {"overall": 0.0},
            "extraction_metadata": {"error": str(e)},
            "current_step": "completed",
            "error": str(e),
        }


def build_extraction_agent():
    """构建智能提取 Agent"""
    workflow = StateGraph(ExtractionState)

    workflow.add_node("extract", extract_entities_intelligent)

    workflow.set_entry_point("extract")
    workflow.add_edge("extract", END)

    return workflow.compile()


def run_extraction(
    analyzed_content: List[Dict[str, Any]],
    query: str,
    model: str = None
) -> Dict[str, Any]:
    """运行智能实体提取

    Args:
        analyzed_content: 分析后的内容列表
        query: 用户查询
        model: 使用的模型

    Returns:
        {
            "content_type": "weather|product|travel|tech|news|qa|other",
            "entities": {...},# 根据内容类型动态提取
            "confidence_scores": {...},
            "extraction_metadata": {...}
        }
    """
    logger.info(f"开始智能实体提取，内容数量: {len(analyzed_content)}")

    agent = build_extraction_agent()
    result = agent.invoke({
        "analyzed_content": analyzed_content,
        "query": query,
        "content_type": "",
        "entities": {},
        "confidence_scores": {},
        "extraction_metadata": {},
        "current_step": "init",
        "error": "",
        "model": model,
    })

    return result