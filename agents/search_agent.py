"""搜索 Agent - 负责执行搜索任务（增强版：支持分类搜索）"""

import logging
import os
import re
from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_deepseek import ChatDeepSeek
from langgraph.graph import StateGraph, END

from config import settings
from tools import tavily_search_sync, smart_search
from tools.result_aggregator import aggregate_search_results, get_consensus_info

logger = logging.getLogger(__name__)


class SearchState(TypedDict):
    """搜索状态"""
    query: str
    search_results: List[Dict[str, Any]]
    search_queries: List[str]
    dimensional_queries: Dict[str, List[str]]  # 新增：分类搜索词
    dimensional_results: Dict[str, List[Dict]]  # 新增：分类搜索结果
    current_step: str
    error: str


def extract_destination(query: str) -> str:
    """从查询中提取目的地"""
    # 常见目的地关键词
    destinations = [
        '济州岛', '日本', '韩国', '泰国', '新加坡', '香港', '澳门', '台湾',
        '马来西亚', '印尼', '巴厘岛', '普吉岛', '马尔代夫', '塞班',
        '云南', '四川', '成都', '重庆', '西安', '北京', '上海', '杭州',
        '广州', '深圳', '厦门', '三亚', '海口', '大理', '丽江', '香格里拉',
        '西藏', '拉萨', '新疆', '敦煌', '青岛', '大连', '苏州', '南京',
        '东京', '大阪', '京都', '北海道', '冲绳', '首尔', '釜山',
        '曼谷', '清迈', '芭提雅', '普吉'
    ]
    query_lower = query.lower()
    for dest in destinations:
        if dest in query:
            return dest

    # 尝试提取"去+地点"模式
    match = re.search(r'去(.+?)(?:玩|旅游|旅行|攻略)', query)
    if match:
        return match.group(1)

    return "目的地"


def generate_dimensional_queries(destination: str) -> Dict[str, List[str]]:
    """根据目的地生成分维度的搜索词（优化版：保留关键维度，减少查询词数量）

    优化说明：
    - 原版：6个维度 × 3个查询 = 18个查询词，串行耗时约36秒
    - 优化：6个维度 × 1个核心查询 = 6个查询词，并行耗时约3-5秒
    - 保留维度：景点、美食、住宿、交通、贴士、预算
    - 效果：减少查询数量，但通过并行执行保证速度，并保留关键信息
    """
    current_year = "2024"

    return {
        "attractions": [
            f"{destination}必去景点推荐 门票价格 {current_year}",
        ],
        "restaurants": [
            f"{destination}美食推荐 餐厅地址",
        ],
        "hotels": [
            f"{destination}住宿推荐 哪个区域方便",
        ],
        "transport": [
            f"{destination}交通攻略 机场到市区 交通卡",
        ],
        "tips": [
            f"{destination}旅游注意事项 天气 穿衣 {current_year}",
        ],
        "budget": [
            f"{destination}旅游费用预算 人均",
        ],
    }


def classify_search_queries(query: str) -> Dict[str, List[str]]:
    """根据查询类型分类搜索词"""
    query_lower = query.lower()

    # 旅行攻略类查询
    travel_keywords = ['攻略', '旅游', '旅行', '行程', '怎么玩', '去哪里', '几天',
                      '景点', '美食', '酒店', '机票', '自由行', '跟团', '自驾', '路线']

    if any(kw in query_lower for kw in travel_keywords):
        # 提取目的地
        destination = extract_destination(query)
        logger.info(f"检测到旅行攻略查询，目的地: {destination}")

        # 生成分维度搜索词
        dimensional_queries = generate_dimensional_queries(destination)

        # 添加原查询
        dimensional_queries["general"] = [query, f"{destination}旅游攻略 2024"]

        return dimensional_queries

    # 竞品分析类查询
    elif any(kw in query_lower for kw in ['竞品', '对比', '比较', 'versus', '竞争']):
        # 提取产品名
        return {"competitive": [query]}

    # 产品能力调研类查询
    elif any(kw in query_lower for kw in ['功能', '能力', '产品评测', '测评', '体验']):
        return {"product": [query]}

    # 默认：通用搜索
    else:
        return {"general": [query]}


def generate_search_queries(state: SearchState) -> Dict[str, Any]:
    """生成多个搜索查询词（增强版：支持分类搜索）"""
    logger.info(f"生成搜索查询词: {state['query']}")

    # 检查是否启用分类搜索
    query = state["query"]
    query_lower = query.lower()

    # 先尝试分类搜索
    dimensional_queries = classify_search_queries(query)

    # 如果有多个维度，使用分类搜索
    if len(dimensional_queries) > 1:
        logger.info(f"使用分类搜索，维度: {list(dimensional_queries.keys())}")
        return {
            "search_queries": [q for queries in dimensional_queries.values() for q in queries],
            "dimensional_queries": dimensional_queries,
            "current_step": "searching",
        }

    # 回退到原有逻辑
    if not settings.deepseek_api_key:
        logger.warning("DeepSeek API Key 未配置，使用原始查询")
        return {
            "search_queries": [state["query"]],
            "dimensional_queries": dimensional_queries,
            "current_step": "searching",
        }

    try:
        llm = ChatDeepSeek(
            model=settings.deepseek_model,
            temperature=0.3,
            api_key=settings.deepseek_api_key,
        )

        # 检测查询类型，生成针对性的搜索词
        query = state["query"]
        query_lower = query.lower()

        # 旅行攻略类查询
        travel_keywords = ['攻略', '旅游', '旅行', '行程', '怎么玩', '去哪里', '几天',
                          '景点', '美食', '酒店', '机票', '自由行', '跟团', '自驾', '路线']

        if any(kw in query_lower for kw in travel_keywords):
            system_prompt = """你是一个专业的旅行搜索助手。用户需要制定详细的旅行攻略，请生成6-8个具体的搜索查询词，覆盖以下维度：

**必须包含的搜索维度**：
1. 【基础攻略】目的地整体攻略/玩法
2. 【景点详情】具体景点名称+门票/开放时间/交通
3. 【美食推荐】当地必吃美食+具体餐厅名称+地址
4. 【住宿攻略】推荐住宿区域+酒店推荐
5. 【交通攻略】机场到市区交通+市内交通方式+交通卡
6. 【费用预算】人均费用+各项花费明细
7. 【避坑指南】旅游陷阱+注意事项
8. 【行程参考】具体天数行程安排

**格式要求**：
- 每行一个搜索查询词
- 不要添加编号或额外符号
- 查询词要具体，包含"小红书"、"马蜂窝"、"携程"等平台关键词有助于找到实用攻略
- 优先搜索最新信息（加上2024/2025年份）

**示例输出**（济州岛5天攻略）：
济州岛5天4晚详细攻略 小红书 2024
济州岛必去景点门票交通攻略 马蜂窝
济州岛美食推荐 黑猪肉餐厅地址
济州岛住宿推荐 哪个区域方便
济州岛交通攻略 公交车 T-money卡
济州岛旅游费用预算 人均多少钱
济州岛旅游避坑指南 注意事项
济州岛牛岛城山日出峰一日游路线"""
        else:
            system_prompt = """你是一个专业的搜索助手。根据用户的调研需求，生成3-5个不同角度的搜索查询词。

要求：
1. 查询词要具体、有针对性
2. 覆盖不同维度（现状、趋势、对比、问题等）
3. 使用用户原始语言（中文或英文）
4. 每行一个查询词，不要添加编号或额外符号"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query),
        ]

        response = llm.invoke(messages)
        content = response.content.strip()

        # 解析查询词
        queries = []
        for line in content.split("\n"):
            line = line.strip()
            # 移除可能的编号前缀
            if line and not line.startswith("#"):
                # 移除 "1." "2." 等编号
                if line[0].isdigit() and "." in line[:3]:
                    line = line.split(".", 1)[1].strip()
                if line:
                    queries.append(line)

        if not queries:
            queries = [state["query"]]

        logger.info(f"生成 {len(queries)} 个搜索查询词")

        return {
            "search_queries": queries,
            "dimensional_queries": dimensional_queries,
            "current_step": "searching",
        }

    except Exception as e:
        logger.error(f"生成搜索查询词失败: {str(e)}")
        # 失败时使用原始查询
        return {
            "search_queries": [state["query"]],
            "dimensional_queries": dimensional_queries,
            "current_step": "searching",
            "error": str(e),
        }


def execute_search(state: SearchState) -> Dict[str, Any]:
    """执行搜索（优化版：并行搜索，大幅减少耗时）

    优化说明：
    - 原版：串行搜索，18个查询 × 2秒 = 36秒
    - 优化：并行搜索，max(所有查询) = 约3-5秒
    - 效果：耗时减少85%
    """
    import concurrent.futures
    from functools import partial

    all_results = []
    queries = state.get("search_queries", [state["query"]])
    dimensional_queries = state.get("dimensional_queries", {})
    dimensional_results = {}

    logger.info(f"执行搜索，查询数量: {len(queries)}")
    if dimensional_queries:
        logger.info(f"分类搜索维度: {list(dimensional_queries.keys())}")

    # 检查 Tavily API Key
    tavily_key = os.getenv("TAVILY_API_KEY", "")
    use_tavily = tavily_key and tavily_key != "your_tavily_api_key_here"

    def execute_single_search(query: str, dimension: str = 'general', max_results: int = 5):
        """执行单个搜索（线程安全）"""
        try:
            if use_tavily:
                results = tavily_search_sync(query, max_results=max_results)
                if results:
                    for r in results:
                        r['dimension'] = dimension
                        r['search_query'] = query
                    logger.info(f"Tavily 搜索维度[{dimension}] '{query}' 获取 {len(results)} 条结果")
                    return results
                else:
                    logger.warning(f"Tavily 搜索 '{query}' 无结果，尝试备用搜索源")

            # 使用智能搜索（DuckDuckGo）
            results = smart_search(query, max_results=max_results)
            if results:
                for r in results:
                    r['dimension'] = dimension
                    r['search_query'] = query
                logger.info(f"智能搜索维度[{dimension}] '{query}' 获取 {len(results)} 条结果")
                return results
            else:
                logger.warning(f"搜索 '{query}' 无结果")
                return []
        except Exception as e:
            logger.error(f"搜索失败 '{query}': {e}")
            return []

    # 收集所有搜索任务
    search_tasks = []

    # 分类搜索任务
    if dimensional_queries:
        for dimension, dim_queries in dimensional_queries.items():
            for query in dim_queries[:3]:  # 每个维度最多3个查询
                search_tasks.append((query, dimension, 5))

    # 常规搜索任务
    for query in queries:
        search_tasks.append((query, 'general', settings.max_search_results))

    # 并行执行所有搜索任务
    logger.info(f"并行搜索 {len(search_tasks)} 个查询词...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # 提交所有搜索任务
        future_to_task = {
            executor.submit(execute_single_search, query, dimension, max_results): (query, dimension)
            for query, dimension, max_results in search_tasks
        }

        # 收集结果
        for future in concurrent.futures.as_completed(future_to_task):
            query, dimension = future_to_task[future]
            try:
                results = future.result()
                if results:
                    all_results.extend(results)
                    # 维度结果收集
                    if dimension not in dimensional_results:
                        dimensional_results[dimension] = []
                    dimensional_results[dimension].extend(results)
            except Exception as e:
                logger.error(f"搜索任务执行失败 '{query}': {e}")

    # 去重（基于URL）
    seen_urls = set()
    unique_results = []
    for result in all_results:
        url = result.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_results.append(result)

    # 聚合和排序结果（综合多方信息）
    logger.info("开始聚合和排序搜索结果...")

    # 降低最低评分阈值，确保保留足够的信息量
    # 如果过滤后结果太少，则放宽标准
    ranked_results = aggregate_search_results(unique_results, state["query"], min_score=1.5)

    # 如果过滤后结果少于5条，返回所有结果（保证信息量）
    if len(ranked_results) < 5 and len(unique_results) > 0:
        logger.warning(f"过滤后结果过少({len(ranked_results)}条)，保留所有结果")
        ranked_results = unique_results[:20]  # 最多返回20条

    # 统计各维度结果数量
    dimension_counts = {}
    for result in ranked_results:
        dim = result.get('dimension', 'general')
        dimension_counts[dim] = dimension_counts.get(dim, 0) + 1

    logger.info(f"搜索完成，去重排序后共 {len(ranked_results)} 条结果（原始{len(unique_results)}条）")
    logger.info(f"各维度结果数量: {dimension_counts}")

    # 详细输出结果质量分布
    if ranked_results:
        high_quality = len([r for r in ranked_results if r.get('_score', 0) >= 8])
        medium_quality = len([r for r in ranked_results if 5 <= r.get('_score', 0) < 8])
        low_quality = len([r for r in ranked_results if r.get('_score', 0) < 5])
        logger.info(f"结果质量分布: 高质量{high_quality}条 | 中等质量{medium_quality}条 | 一般质量{low_quality}条")

    # 获取共识信息
    if ranked_results:
        consensus = get_consensus_info(ranked_results, top_n=3)
        if any(consensus.values()):
            logger.info(f"发现共识信息: {', '.join([f'{k}:{len(v)}项' for k, v in consensus.items() if v])}")

    if not ranked_results:
        logger.warning("所有搜索均无结果")

    return {
        "search_results": ranked_results,
        "dimensional_results": dimensional_results,
        "current_step": "completed",
    }


def build_search_agent():
    """构建搜索 Agent"""
    workflow = StateGraph(SearchState)

    workflow.add_node("generate_queries", generate_search_queries)
    workflow.add_node("execute_search", execute_search)

    workflow.set_entry_point("generate_queries")
    workflow.add_edge("generate_queries", "execute_search")
    workflow.add_edge("execute_search", END)

    return workflow.compile()


def run_search(query: str) -> Dict[str, Any]:
    """运行搜索 Agent"""
    logger.info(f"开始搜索流程: {query}")

    agent = build_search_agent()
    result = agent.invoke({
        "query": query,
        "search_results": [],
        "search_queries": [],
        "current_step": "init",
        "error": "",
    })

    return result