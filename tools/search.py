"""修复后的搜索工具 - 多搜索源支持"""

import logging
import os
from typing import List, Dict, Any
import httpx
import time

logger = logging.getLogger(__name__)


def search_with_tavily(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """使用 Tavily 搜索（首选，专为 AI 设计）"""
    from .tavily_search import tavily_search_sync
    return tavily_search_sync(query, max_results)


def search_with_serper(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """使用 Serper (Google Search API) - 有免费额度"""
    api_key = os.getenv("SERPER_API_KEY", "")
    if not api_key:
        logger.debug("Serper API Key 未配置")
        return []

    try:
        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "q": query,
            "num": max_results
        }

        with httpx.Client(timeout=15.0) as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        results = []
        # Organic results
        for item in data.get("organic", [])[:max_results]:
            results.append({
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "description": item.get("snippet", ""),
            })

        logger.info(f"Serper 找到 {len(results)} 条结果")
        return results

    except Exception as e:
        logger.warning(f"Serper 搜索失败: {str(e)}")
        return []


def search_with_brave(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """使用 Brave Search API - 有免费额度"""
    api_key = os.getenv("BRAVE_API_KEY", "")
    if not api_key:
        logger.debug("Brave API Key 未配置")
        return []

    try:
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": api_key
        }
        params = {
            "q": query,
            "count": max_results
        }

        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

        results = []
        for item in data.get("web", {}).get("results", [])[:max_results]:
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "description": item.get("description", ""),
            })

        logger.info(f"Brave Search 找到 {len(results)} 条结果")
        return results

    except Exception as e:
        logger.warning(f"Brave Search 失败: {str(e)}")
        return []


def search_with_duckduckgo(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """使用 DuckDuckGo 搜索 - 免费，无需 API Key"""
    try:
        # 使用 ddgs 包（新版本）
        from ddgs import DDGS

        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

        formatted = []
        for item in results:
            formatted.append({
                "title": item.get("title", ""),
                "url": item.get("href", "") or item.get("url", ""),
                "description": item.get("body", "") or item.get("description", ""),
            })

        logger.info(f"DuckDuckGo 找到 {len(formatted)} 条结果")
        return formatted

    except Exception as e:
        logger.warning(f"DuckDuckGo 搜索失败: {str(e)}")
        return []


def search_with_serpapi(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """使用 SerpApi - 有免费额度"""
    api_key = os.getenv("SERPAPI_KEY", "")
    if not api_key:
        logger.debug("SerpApi Key 未配置")
        return []

    try:
        url = "https://serpapi.com/search"
        params = {
            "q": query,
            "api_key": api_key,
            "num": max_results,
        }

        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        results = []
        for item in data.get("organic_results", [])[:max_results]:
            results.append({
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "description": item.get("snippet", ""),
            })

        logger.info(f"SerpApi 找到 {len(results)} 条结果")
        return results

    except Exception as e:
        logger.warning(f"SerpApi 搜索失败: {str(e)}")
        return []


def smart_search(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    智能搜索：依次尝试多个搜索源

    优先级：
    1. Serper (Google Search API，速度快，质量高)
    2. Brave Search (免费额度，质量好)
    3. DuckDuckGo (完全免费，无需 API Key)
    4. SerpApi (免费额度)
    5. Tavily (需付费，额度受限)
    """
    logger.info(f"开始智能搜索: {query}")

    # 1. 优先尝试 Serper (如果能用)
    if os.getenv("SERPER_API_KEY"):
        results = search_with_serper(query, max_results)
        if results:
            return results
        logger.info("Serper 无结果，尝试下一个搜索源...")

    # 2. 尝试 Brave Search
    if os.getenv("BRAVE_API_KEY"):
        results = search_with_brave(query, max_results)
        if results:
            return results
        logger.info("Brave Search 无结果，尝试下一个搜索源...")

    # 3. 尝试 DuckDuckGo (完全免费)
    results = search_with_duckduckgo(query, max_results)
    if results:
        return results
    logger.info("DuckDuckGo 无结果，尝试下一个搜索源...")

    # 4. 尝试 SerpApi
    if os.getenv("SERPAPI_KEY"):
        results = search_with_serpapi(query, max_results)
        if results:
            return results
        logger.info("SerpApi 无结果，尝试下一个搜索源...")

    # 5. 最后尝试 Tavily (如果还有额度)
    if os.getenv("TAVILY_API_KEY"):
        results = search_with_tavily(query, max_results)
        if results:
            return results

    logger.warning("所有搜索源均无结果")
    return []


# 导出统一接口
def search(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """统一的搜索接口"""
    return smart_search(query, max_results)