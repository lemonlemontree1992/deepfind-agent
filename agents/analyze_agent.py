"""分析 Agent - 负责分析搜索结果和网页内容"""

import logging
from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

from config import settings
from tools import scrape_url, scrape_urls_parallel
from utils.llm_client import get_llm
from tools.result_aggregator import get_consensus_info

logger = logging.getLogger(__name__)


class AnalyzeState(TypedDict):
    """分析状态"""
    search_results: List[Dict[str, Any]]
    analyzed_content: List[Dict[str, Any]]
    key_findings: str  # 修正：应该是 str 而不是 List[str]
    current_step: str
    error: str
    model: Optional[str]  # 添加模型参数到状态


def analyze_search_results(state: AnalyzeState) -> Dict[str, Any]:
    """分析搜索结果，提取关键信息（并行解析优化版）"""
    analyzed = []
    search_results = state.get("search_results", [])

    # 根据搜索深度决定解析多少页面
    max_pages = 10 if settings.search_depth == "deep" else 5

    logger.info(f"开始分析搜索结果，解析 {min(len(search_results), max_pages)} 个页面（并行）")

    # 提取 URL 列表
    urls = []
    for result in search_results[:max_pages]:
        url = result.get("url", "")
        if url:
            urls.append(url)

    # 并行解析所有 URL
    if urls:
        parsed_results = scrape_urls_parallel(urls, max_workers=5)

        # 匹配解析结果和原始搜索结果
        for i, result in enumerate(search_results[:max_pages]):
            url = result.get("url", "")
            if i < len(parsed_results):
                parsed = parsed_results[i]
                if "error" not in parsed:
                    analyzed.append({
                        "url": url,
                        "title": result.get("title", "") or parsed.get("title", ""),
                        "content": parsed.get("content", ""),
                        "source": parsed.get("source", ""),
                    })
                    logger.info(f"解析成功: {parsed.get('title', url[:50])}")
                else:
                    logger.warning(f"解析失败 {url}: {parsed.get('error', '未知错误')}")

    logger.info(f"成功解析 {len(analyzed)} 个页面")

    return {
        "analyzed_content": analyzed,
        "current_step": "extracting",
    }


def extract_key_findings(state: AnalyzeState) -> Dict[str, Any]:
    """提取关键发现（综合多方信息）"""
    analyzed_content = state.get("analyzed_content", [])
    model = state.get("model")  # 从状态中获取模型参数

    if not analyzed_content:
        logger.warning("没有分析内容，无法提取关键发现")
        return {
            "key_findings": "未能获取有效的分析内容，请检查搜索结果。",
            "current_step": "completed",
        }

    try:
        # 分析阶段使用快速模型（信息整合不需要深度推理）
        llm = get_llm(model="deepseek-chat", temperature=0.5)

        # 准备内容摘要（优先使用高权威性来源）
        content_summary = ""
        for i, item in enumerate(analyzed_content, 1):
            # 显示评分和权威性
            score = item.get('_score', 0)
            authority = item.get('_authority', 6.0)
            mentions = item.get('_mentions', 0)

            content_summary += f"\n[来源 {i}] {item['title']}\n"
            content_summary += f"URL: {item['url']}\n"
            content_summary += f"权威性: {authority}/10 | 评分: {score:.1f} | 提及次数: {mentions}\n"

            # 截取前2000字符避免超长
            content_text = item.get("content", "")
            content_summary += f"内容摘要: {content_text[:2000]}...\n"
            content_summary += "-" * 50 + "\n"

        # 获取共识信息
        consensus = get_consensus_info(analyzed_content, top_n=5)

        system_prompt = """你是一个专业的信息分析师。请从提供的搜索结果中提取关键发现和重要信息。

**重要原则**：
1. **优先采用高权威性来源**的信息（权威性评分高的来源更可信）
2. **重点关注多次提及的信息**（多个来源都提到的事项更具参考价值）
3. **综合多方观点**：如果一个信息被多个来源提及，要在发现中标注"多个来源一致"
4. **标注信息来源和置信度**：使用 [来源编号] 标注，并说明信息的可信程度

**输出格式**：
- 发现1：具体内容 [来源编号] ⭐⭐⭐（权威性高/多次提及）
- 发现2：具体内容 [来源编号] ⭐⭐（中等可信度）
..."""

        if consensus:
            system_prompt += f"""

**已识别的共识信息**（多个来源一致提到）：
- 最常提及的景点：{', '.join(consensus.get('top_attractions', [])) if consensus.get('top_attractions') else '无'}
- 最常提及的餐厅：{', '.join(consensus.get('top_restaurants', [])) if consensus.get('top_restaurants') else '无'}
- 最常提及的酒店：{', '.join(consensus.get('top_hotels', [])) if consensus.get('top_hotels') else '无'}

请优先关注这些共识信息，它们更可能准确可靠。"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=content_summary),
        ]

        logger.info("调用 LLM 提取关键发现...")
        response = llm.invoke(messages)
        findings = response.content

        logger.info(f"成功提取关键发现，长度: {len(findings)}")

        return {
            "key_findings": findings,
            "current_step": "completed",
        }

    except Exception as e:
        logger.error(f"提取关键发现失败: {str(e)}")
        return {
            "key_findings": f"提取关键信息时出错: {str(e)}",
            "current_step": "completed",
            "error": str(e),
        }


def build_analyze_agent():
    """构建分析 Agent"""
    workflow = StateGraph(AnalyzeState)

    workflow.add_node("analyze_results", analyze_search_results)
    workflow.add_node("extract_findings", extract_key_findings)

    workflow.set_entry_point("analyze_results")
    workflow.add_edge("analyze_results", "extract_findings")
    workflow.add_edge("extract_findings", END)

    return workflow.compile()


def run_analyze(search_results: List[Dict[str, Any]], model: str = None) -> Dict[str, Any]:
    """运行分析 Agent"""
    logger.info(f"开始分析流程，搜索结果数量: {len(search_results)}")

    agent = build_analyze_agent()
    result = agent.invoke({
        "search_results": search_results,
        "analyzed_content": [],
        "key_findings": "",
        "current_step": "init",
        "error": "",
        "model": model,  # 通过状态传递模型参数
    })

    return result