"""DuckDuckGo 搜索工具（国内可用，无需 API Key）"""

import logging
from typing import List, Dict, Any, Optional
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)


def duckduckgo_search_sync(query: str, max_results: Optional[int] = 10) -> List[Dict[str, Any]]:
    """
    使用 DuckDuckGo 进行搜索（国内可用，无需 API Key）

    Args:
        query: 搜索查询词
        max_results: 返回结果数量，默认10条

    Returns:
        搜索结果列表，每个结果包含 title, url, description
    """
    try:
        logger.info(f"DuckDuckGo 搜索: {query}")

        with DDGS() as ddgs:
            # 使用 text 方法搜索
            results = list(ddgs.text(query, max_results=max_results or 10))

        if not results:
            logger.warning(f"DuckDuckGo 搜索无结果: {query}")
            return []

        formatted_results = []
        for item in results:
            formatted_results.append({
                "title": item.get("title", ""),
                "url": item.get("href", "") or item.get("url", ""),
                "description": item.get("body", "") or item.get("description", ""),
            })

        logger.info(f"DuckDuckGo 找到 {len(formatted_results)} 条结果")
        return formatted_results

    except Exception as e:
        logger.error(f"DuckDuckGo 搜索出错: {str(e)}")
        return []  # 返回空列表而不是错误字典，统一处理