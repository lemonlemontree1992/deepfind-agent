"""并行搜索工具 - 支持多维度并行搜索"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

logger = logging.getLogger(__name__)


def parallel_search(
    queries_by_dimension: Dict[str, List[str]],
    max_results_per_query: int = 5,
    max_workers: int = 4
) -> Dict[str, List[Dict[str, Any]]]:
    """并行执行多维度搜索

    Args:
        queries_by_dimension: 按维度分组的查询词
            {
                "attractions": ["济州岛必去景点", "济州岛门票价格"],
                "restaurants": ["济州岛美食推荐", "济州岛餐厅地址"],
                ...
            }
        max_results_per_query: 每个查询的最大结果数
        max_workers: 最大并行数

    Returns:
        按维度分组的搜索结果
            {
                "attractions": [结果列表],
                "restaurants": [结果列表],
                ...
            }
    """
    from . import tavily_search_sync, smart_search
    import os

    results_by_dimension: Dict[str, List[Dict[str, Any]]] = {}
    all_urls = set()  # 用于去重

    # 检查 Tavily API Key
    tavily_key = os.getenv("TAVILY_API_KEY", "")
    use_tavily = tavily_key and tavily_key != "your_tavily_api_key_here"

    def search_single_query(query: str, dimension: str) -> tuple:
        """搜索单个查询"""
        try:
            if use_tavily:
                results = tavily_search_sync(query, max_results=max_results_per_query)
            else:
                results = smart_search(query, max_results=max_results_per_query)

            # 为结果添加维度标签
            for r in results:
                r['dimension'] = dimension
                r['search_query'] = query

            return dimension, query, results, None
        except Exception as e:
            return dimension, query, [], str(e)

    # 统计总查询数
    total_queries = sum(len(queries) for queries in queries_by_dimension.values())
    logger.info(f"开始并行搜索，共 {len(queries_by_dimension)} 个维度，{total_queries} 个查询")

    # 使用线程池并行执行
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []

        for dimension, queries in queries_by_dimension.items():
            # 每个维度最多取前3个查询
            for query in queries[:3]:
                future = executor.submit(search_single_query, query, dimension)
                futures.append(future)

        # 收集结果
        for future in as_completed(futures):
            dimension, query, results, error = future.result()

            if error:
                logger.warning(f"搜索失败: [{dimension}] {query} - {error}")
                continue

            if results:
                # 去重并添加结果
                for result in results:
                    url = result.get('url', '')
                    if url and url not in all_urls:
                        all_urls.add(url)
                        results_by_dimension.setdefault(dimension, []).append(result)

                logger.info(f"搜索完成: [{dimension}] {query} -> {len(results)} 条结果")

    # 统计
    for dimension, results in results_by_dimension.items():
        logger.info(f"维度 [{dimension}]: {len(results)} 条结果")

    logger.info(f"并行搜索完成，共获取 {sum(len(r) for r in results_by_dimension.values())} 条结果")

    return results_by_dimension


def merge_parallel_search_results(
    results_by_dimension: Dict[str, List[Dict[str, Any]]]
) -> List[Dict[str, Any]]:
    """合并并行搜索结果为单一列表

    Args:
        results_by_dimension: 按维度分组的结果

    Returns:
        合并后的结果列表
    """
    all_results = []

    for dimension, results in results_by_dimension.items():
        for result in results:
            all_results.append(result)

    return all_results


def get_dimensional_search_queries(destination: str) -> Dict[str, List[str]]:
    """根据目的地生成分维度搜索查询

    Args:
        destination: 目的地名称

    Returns:
        分维度的搜索查询
    """
    current_year = "2024"

    return {
        "attractions": [
            f"{destination}必去景点推荐 {current_year}",
            f"{destination}景点门票价格 开放时间",
            f"{destination}旅游路线规划 最佳路线",
        ],
        "restaurants": [
            f"{destination}美食推荐 必吃榜单",
            f"{destination}餐厅推荐 人均消费 地址",
            f"{destination}当地特色美食 小吃",
        ],
        "hotels": [
            f"{destination}住宿推荐 哪个区域方便",
            f"{destination}酒店评测 性价比",
            f"{destination}民宿推荐 亲子酒店",
        ],
        "transport": [
            f"{destination}交通攻略 机场到市区",
            f"{destination}市内交通 公交 地铁 打车",
            f"{destination}交通卡 租车攻略",
        ],
        "tips": [
            f"{destination}旅游避坑指南 {current_year}",
            f"{destination}注意事项 天气 穿衣",
            f"{destination}最佳旅游时间 季节",
        ],
        "budget": [
            f"{destination}旅游费用预算 人均多少钱",
            f"{destination}自由行费用明细",
        ],
    }