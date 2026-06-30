"""搜索结果聚合与排序 - 综合多方信息，提高结果稳定性"""

import logging
from typing import List, Dict, Any
from collections import Counter
import hashlib
import re

logger = logging.getLogger(__name__)


class SearchResultAggregator:
    """搜索结果聚合器 - 综合多方信息并排序"""

    def __init__(self):
        self.result_cache = {}  # URL -> 结果缓存
        self.mention_count = Counter()  # 提及次数统计
        self.source_scores = {}  # 来源评分

    def calculate_source_authority(self, url: str) -> float:
        """计算来源权威性评分（0-10分）

        高权威性来源：
        - 政府网站 (.gov.cn) : 10分
        - 知名媒体 (人民网、新华网等) : 9分
        - 专业平台 (马蜂窝、携程、小红书等) : 8分
        - 知名社区 (知乎、豆瓣等) : 7分
        - 个人博客 : 5分
        - 其他 : 6分
        """
        url_lower = url.lower()

        # 政府网站
        if '.gov.' in url_lower:
            return 10.0

        # 知名媒体
        media_sites = [
            'people.com.cn', 'xinhuanet.com', 'cctv.com', 'chinadaily.com.cn',
            'thepaper.cn', 'bjnews.com.cn', 'caixin.com', 'yicai.com'
        ]
        if any(site in url_lower for site in media_sites):
            return 9.0

        # 专业旅行平台
        travel_platforms = [
            'mafengwo.cn', 'ctrip.com', 'qunar.com', 'tuniu.com',
            'xiaohongshu.com', 'mafengwo.com', 'tripadvisor.cn'
        ]
        if any(platform in url_lower for platform in travel_platforms):
            return 8.5

        # 知名社区平台
        community_sites = [
            'zhihu.com', 'douban.com', 'weibo.com', 'bilibili.com',
            'tieba.baidu.com', 'jingyan.baidu.com'
        ]
        if any(site in url_lower for site in community_sites):
            return 7.5

        # 个人博客/小众网站
        blog_indicators = ['blog', 'wordpress', 'github.io', 'medium.com']
        if any(indicator in url_lower for indicator in blog_indicators):
            return 5.0

        # 默认
        return 6.0

    def extract_keywords(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        if not text:
            return []

        # 提取中文关键词（2-4字）
        chinese_keywords = re.findall(r'[\u4e00-\u9fa5]{2,4}', text)
        # 提取英文关键词
        english_keywords = re.findall(r'[a-zA-Z]{3,}', text)

        keywords = chinese_keywords + english_keywords
        # 转小写并去重
        keywords = list(set(k.lower() for k in keywords))

        return keywords

    def calculate_relevance_score(self, result: Dict[str, Any], query: str) -> float:
        """计算结果与查询的相关性评分（0-10分）

        评分因素：
        1. 标题匹配度（最重要）
        2. 内容关键词匹配
        3. 来源权威性
        """
        title = result.get('title', '').lower()
        description = result.get('description', '').lower()
        query_lower = query.lower()

        score = 0.0

        # 1. 标题匹配（权重6分）
        # 完全匹配
        if query_lower in title:
            score += 6.0
        # 部分匹配
        else:
            query_keywords = self.extract_keywords(query)
            title_keywords = self.extract_keywords(title)
            if query_keywords and title_keywords:
                match_ratio = len(set(query_keywords) & set(title_keywords)) / len(query_keywords)
                score += match_ratio * 6.0

        # 2. 内容相关性（权重2分）
        query_keywords = set(self.extract_keywords(query))
        content_keywords = set(self.extract_keywords(description))
        if query_keywords and content_keywords:
            relevance = len(query_keywords & content_keywords) / len(query_keywords)
            score += relevance * 2.0

        # 3. 来源权威性（权重2分）
        url = result.get('url', '')
        authority_score = self.calculate_source_authority(url)
        score += (authority_score / 10.0) * 2.0

        return min(score, 10.0)

    def aggregate_and_rank(
        self,
        results: List[Dict[str, Any]],
        query: str,
        min_score: float = 3.0
    ) -> List[Dict[str, Any]]:
        """聚合和排序搜索结果

        Args:
            results: 搜索结果列表
            query: 用户查询
            min_score: 最低评分阈值

        Returns:
            排序后的结果列表
        """
        if not results:
            return []

        logger.info(f"开始聚合 {len(results)} 条搜索结果，查询: {query[:50]}...")

        # 1. 去重（基于URL）
        seen_urls = {}
        for result in results:
            url = result.get('url', '')
            if url:
                if url not in seen_urls:
                    seen_urls[url] = result
                else:
                    # 如果出现重复，增加提及次数
                    self.mention_count[url] += 1

        unique_results = list(seen_urls.values())
        logger.info(f"去重后剩余 {len(unique_results)} 条结果")

        # 2. 计算综合评分
        scored_results = []
        for result in unique_results:
            # 相关性评分
            relevance_score = self.calculate_relevance_score(result, query)

            # 来源权威性
            url = result.get('url', '')
            authority_score = self.calculate_source_authority(url)

            # 提及次数加成（重复出现的更可信）
            mention_bonus = min(self.mention_count[url] * 0.5, 2.0)

            # 综合评分
            total_score = relevance_score + (authority_score / 10.0) + mention_bonus

            result['_score'] = total_score
            result['_relevance'] = relevance_score
            result['_authority'] = authority_score
            result['_mentions'] = self.mention_count[url]

            scored_results.append(result)

        # 3. 按评分排序
        scored_results.sort(key=lambda x: x.get('_score', 0), reverse=True)

        # 4. 过滤低分结果
        filtered_results = [r for r in scored_results if r.get('_score', 0) >= min_score]

        logger.info(f"评分排序完成，保留 {len(filtered_results)} 条高分结果")

        # 5. 记录Top结果
        if filtered_results:
            logger.info(f"Top 3 结果:")
            for i, result in enumerate(filtered_results[:3], 1):
                logger.info(
                    f"  {i}. [{result.get('_score', 0):.1f}分] {result.get('title', '')[:50]} "
                    f"(权威性:{result.get('_authority', 0):.1f}, 提及:{result.get('_mentions', 0)}次)"
                )

        return filtered_results

    def get_most_mentioned_info(self, results: List[Dict[str, Any]], keyword: str) -> List[str]:
        """提取最常被提及的信息

        Args:
            results: 搜索结果列表
            keyword: 要提取的关键词（如"景点"、"美食"等）

        Returns:
            最常被提及的信息列表（按提及次数排序）
        """
        info_counter = Counter()

        for result in results:
            title = result.get('title', '')
            description = result.get('description', '')

            # 提取包含关键词的信息
            text = f"{title} {description}"

            # 使用正则提取相关信息（简化版）
            # 这里可以根据实际需求优化提取逻辑
            if keyword in text:
                # 提取关键词附近的文本
                patterns = [
                    rf'{keyword}[:：]?\s*([^\n。！？]+)',
                    rf'推荐[:：]?\s*([^\n。！？]+{keyword}[^\n。！？]+)',
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, text)
                    for match in matches:
                        info_counter[match.strip()] += 1

        # 返回提及次数最多的信息
        return [item for item, count in info_counter.most_common(10)]

    def get_consensus_info(self, results: List[Dict[str, Any]], top_n: int = 5) -> Dict[str, Any]:
        """获取共识信息（多个来源都提及的信息）

        Returns:
            {
                'top_attractions': [...],  # 最常提及的景点
                'top_restaurants': [...],  # 最常提及的餐厅
                'top_hotels': [...],       # 最常提及的酒店
                'common_tips': [...],      # 常见建议
            }
        """
        consensus = {
            'top_attractions': self.get_most_mentioned_info(results, '景点')[:top_n],
            'top_restaurants': self.get_most_mentioned_info(results, '餐厅')[:top_n],
            'top_hotels': self.get_most_mentioned_info(results, '酒店')[:top_n],
            'common_tips': self.get_most_mentioned_info(results, '建议')[:top_n],
        }

        return consensus


# 全局聚合器实例
_aggregator = SearchResultAggregator()


def aggregate_search_results(
    results: List[Dict[str, Any]],
    query: str,
    min_score: float = 3.0
) -> List[Dict[str, Any]]:
    """聚合和排序搜索结果（便捷函数）"""
    return _aggregator.aggregate_and_rank(results, query, min_score)


def get_consensus_info(results: List[Dict[str, Any]], top_n: int = 5) -> Dict[str, Any]:
    """获取共识信息（便捷函数）"""
    return _aggregator.get_consensus_info(results, top_n)