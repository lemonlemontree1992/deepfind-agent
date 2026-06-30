"""Brave Search API 搜索工具"""

import logging
import httpx
from typing import List, Dict, Any, Optional
from config import settings

logger = logging.getLogger(__name__)


def brave_search_sync(query: str, count: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    使用 Brave Search API 进行搜索

    Args:
        query: 搜索查询词
        count: 返回结果数量，默认使用配置中的 max_search_results

    Returns:
        搜索结果列表，每个结果包含 title, url, description
        如果搜索失败返回空列表
    """
    # 检查 API Key
    if not settings.brave_search_api_key:
        logger.warning("Brave Search API Key 未配置，将使用 DuckDuckGo")
        return []

    count = count or settings.max_search_results
    url = "https://api.search.brave.com/res/v1/web/search"

    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": settings.brave_search_api_key,
    }

    params = {
        "q": query,
        "count": count,
        "search_lang": "zh-hans" if settings.default_language == "zh" else "en",
    }

    try:
        logger.info(f"Brave Search 搜索: {query}")

        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

        results = []
        for item in data.get("web", {}).get("results", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "description": item.get("description", ""),
            })

        logger.info(f"Brave Search 找到 {len(results)} 条结果")
        return results

    except httpx.HTTPStatusError as e:
        logger.error(f"Brave Search API HTTP 错误: {e.response.status_code}")
        return []
    except httpx.HTTPError as e:
        logger.error(f"Brave Search API 请求失败: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Brave Search 搜索出错: {str(e)}")
        return []