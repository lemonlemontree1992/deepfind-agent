"""Tavily Search API - 专为 AI Agent 设计的搜索工具"""

import logging
import os
from typing import List, Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)

# Tavily API 配置
TAVILY_API_URL = "https://api.tavily.com/search"


def tavily_search(
    query: str,
    max_results: int = 10,
    search_depth: str = "advanced",
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    使用 Tavily API 进行搜索

    Args:
        query: 搜索查询词
        max_results: 返回结果数量（最大 10）
        search_depth: 搜索深度 "basic" 或 "advanced"
        include_domains: 只包含这些域名
        exclude_domains: 排除这些域名

    Returns:
        搜索结果列表
    """
    api_key = os.getenv("TAVILY_API_KEY", "")

    if not api_key:
        logger.warning("Tavily API Key 未配置")
        return []

    try:
        logger.info(f"Tavily 搜索: {query}")

        payload = {
            "api_key": api_key,
            "query": query,
            "max_results": min(max_results, 10),
            "search_depth": search_depth,
            "include_answer": True,
            "include_raw_content": False,
        }

        if include_domains:
            payload["include_domains"] = include_domains
        if exclude_domains:
            payload["exclude_domains"] = exclude_domains

        with httpx.Client(timeout=30.0) as client:
            response = client.post(TAVILY_API_URL, json=payload)
            response.raise_for_status()
            data = response.json()

        results = []

        # 提取答案（如果有）
        if data.get("answer"):
            results.append({
                "title": "Tavily AI 摘要",
                "url": "",
                "description": data["answer"],
            })

        # 提取搜索结果
        for item in data.get("results", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "description": item.get("content", "") or item.get("snippet", ""),
            })

        logger.info(f"Tavily 找到 {len(results)} 条结果")
        return results

    except httpx.HTTPStatusError as e:
        logger.error(f"Tavily API HTTP 错误: {e.response.status_code}")
        if e.response.status_code == 401:
            logger.error("Tavily API Key 无效")
        elif e.response.status_code == 429:
            logger.error("Tavily API 请求次数超限")
        return []
    except httpx.TimeoutException:
        logger.error("Tavily API 请求超时")
        return []
    except Exception as e:
        logger.error(f"Tavily 搜索出错: {str(e)}")
        return []


def tavily_search_sync(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    同步版本的 Tavily 搜索（兼容接口）

    Args:
        query: 搜索查询词
        max_results: 返回结果数量

    Returns:
        搜索结果列表
    """
    return tavily_search(query, max_results=max_results)