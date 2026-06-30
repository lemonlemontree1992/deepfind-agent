"""信息验证 Agent - 多来源交叉验证信息准确性"""

import logging
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class ValidationState(TypedDict):
    """验证状态"""
    entities: Dict[str, Any]  # 从extraction_agent获取的结构化实体
    analyzed_content: List[Dict[str, Any]]  # 原始网页内容
    validated_entities: Dict[str, Any]  # 验证后的实体
    validation_report: Dict[str, Any]  # 验证报告
    current_step: str
    error: str
    model: Optional[str]


def extract_price_value(price_str: str) -> Optional[float]:
    """从价格字符串中提取数值"""
    if not price_str:
        return None

    # 匹配数字（可能包含逗号分隔）
    # 支持格式：2000韩元, 100元, 150-200元, ¥100, $50
    patterns = [
        r'([\d,]+)\s*(?:韩元|元|日元|美元|￥|\$|¥)',  # 中日韩货币
        r'(?:￥|\$|¥)\s*([\d,]+)',  # 符号在前的货币
        r'([\d,]+)\s*(?:万|千|百)',  # 中文数字单位
    ]

    for pattern in patterns:
        match = re.search(pattern, price_str)
        if match:
            value = match.group(1).replace(',', '')
            try:
                return float(value)
            except:
                continue

    # 最后尝试提取任何数字
    numbers = re.findall(r'(\d+(?:\.\d+)?)', price_str)
    if numbers:
        try:
            return float(numbers[0])
        except:
            pass

    return None


def extract_time_value(time_str: str) -> Optional[str]:
    """规范化时间字符串"""
    if not time_str:
        return None

    # 提取时间范围
    time_pattern = r'(\d{1,2}:\d{2})\s*[-~到]\s*(\d{1,2}:\d{2})'
    match = re.search(time_pattern, time_str)
    if match:
        return f"{match.group(1)}-{match.group(2)}"

    # 提取小时范围
    hour_pattern = r'(\d{1,2})\s*[-~到]\s*(\d{1,2})\s*小时?'
    match = re.search(hour_pattern, time_str)
    if match:
        return f"{match.group(1)}-{match.group(2)}小时"

    return time_str.strip()


def cross_validate_field(field_name: str, values: List[Dict[str, Any]]) -> Dict[str, Any]:
    """交叉验证单个字段

    Args:
        field_name: 字段名称
        values: [{'value': xx, 'source': xx, 'source_id': xx, 'source_type': xx}]

    Returns:
        {
            "verified": True/False,
            "verified_value": xx,
            "confidence": 0.0-1.0,
            "agreement_ratio": 0.0-1.0,
            "sources": [...],
            "conflicting_values": [...],
            "note": "..."
        }
    """
    if not values:
        return {
            "verified": False,
            "verified_value": None,
            "confidence": 0.0,
            "note": "无来源数据"
        }

    # 来源权重
    source_weights = {
        "官网": 1.0,
        "官方网站": 1.0,
        "政府网站": 0.95,
        "知名旅游平台": 0.85,
        "马蜂窝": 0.8,
        "携程": 0.8,
        "穷游": 0.75,
        "小红书": 0.65,
        "百度旅游": 0.7,
        "TripAdvisor": 0.8,
        "社交媒体": 0.6,
        "博客": 0.5,
        "论坛": 0.45,
        "用户评论": 0.4,
    }

    # 归一化值
    normalized_values = {}
    for item in values:
        value = item.get('value')
        if value is None:
            continue

        # 根据字段类型处理值
        if '价格' in field_name or '门票' in field_name or '费用' in field_name:
            numeric_val = extract_price_value(str(value))
            if numeric_val:
                # 取整到10的倍数（处理误差）
                normalized = round(numeric_val, -1)
                if normalized not in normalized_values:
                    normalized_values[normalized] = []
                normalized_values[normalized].append(item)
        else:
            # 文本值：直接使用
            normalized_val = str(value).strip().lower()
            if normalized_val not in normalized_values:
                normalized_values[normalized_val] = []
            normalized_values[normalized_val].append(item)

    if not normalized_values:
        return {
            "verified": False,
            "verified_value": None,
            "confidence": 0.0,
            "note": "无法解析有效值"
        }

    # 找出最常见的值
    most_common = max(normalized_values.items(),
                      key=lambda x: (len(x[1]), sum(source_weights.get(v.get('source_type', ''), 0.5) for v in x[1])))
    verified_normalized, matching_items = most_common

    # 找出原始值
    original_value = matching_items[0].get('value')

    # 计算一致性比例
    agreement_ratio = len(matching_items) / len(values)

    # 计算加权置信度
    total_weight = 0
    weighted_confidence = 0
    for item in matching_items:
        source_type = item.get('source_type', '博客')
        weight = source_weights.get(source_type, 0.5)
        total_weight += weight
        weighted_confidence += weight

    if total_weight > 0:
        weighted_confidence = weighted_confidence / len(values)
    else:
        weighted_confidence = agreement_ratio * 0.7

    # 综合置信度
    final_confidence = (agreement_ratio * 0.4 + weighted_confidence * 0.6)

    # 冲突值
    conflicting_values = []
    for norm_val, items in normalized_values.items():
        if norm_val != verified_normalized:
            for item in items:
                conflicting_values.append({
                    "value": item.get('value'),
                    "source": item.get('source'),
                    "source_id": item.get('source_id')
                })

    # 验证是否通过
    verified = final_confidence >= 0.6 and agreement_ratio >= 0.5

    # 生成说明
    if agreement_ratio == 1.0:
        note = f"{len(values)}个来源一致"
    elif agreement_ratio >= 0.7:
        note = f"{len(matching_items)}/{len(values)}个来源一致，可信"
    elif agreement_ratio >= 0.5:
        note = f"{len(matching_items)}/{len(values)}个来源一致，建议确认"
    else:
        note = f"多个来源不一致，请核实"

    return {
        "verified": verified,
        "verified_value": original_value,
        "confidence": round(final_confidence, 2),
        "agreement_ratio": round(agreement_ratio, 2),
        "sources": [
            {"source": item.get('source'), "source_id": item.get('source_id')}
            for item in matching_items
        ],
        "conflicting_values": conflicting_values[:3] if conflicting_values else [],  # 最多返回3个冲突值
        "note": note
    }


def validate_attraction(attraction: Dict[str, Any], sources: List[Dict[str, Any]]) -> Dict[str, Any]:
    """验证景点实体"""
    validated = attraction.copy()
    validation_details = {}

    # 验证门票价格
    if attraction.get('ticket'):
        price_values = []
        if isinstance(attraction['ticket'], dict):
            for price_type, price_val in attraction['ticket'].items():
                if price_val:
                    price_values.append({
                        'value': price_val,
                        'source': attraction.get('source_urls', ['未知'])[0],
                        'source_id': attraction.get('source_ids', [0])[0],
                        'source_type': '旅游平台'
                    })
        else:
            price_values.append({
                'value': attraction['ticket'],
                'source': attraction.get('source_urls', ['未知'])[0],
                'source_id': attraction.get('source_ids', [0])[0],
                'source_type': '旅游平台'
            })

        if price_values:
            validation_details['ticket'] = cross_validate_field('门票价格', price_values)

    # 验证开放时间
    if attraction.get('hours'):
        time_values = []
        if isinstance(attraction['hours'], dict):
            for time_type, time_val in attraction['hours'].items():
                if time_val:
                    time_values.append({
                        'value': time_val,
                        'source': attraction.get('source_urls', ['未知'])[0],
                        'source_id': attraction.get('source_ids', [0])[0],
                        'source_type': '旅游平台'
                    })
        else:
            time_values.append({
                'value': attraction['hours'],
                'source': attraction.get('source_urls', ['未知'])[0],
                'source_id': attraction.get('source_ids', [0])[0],
                'source_type': '旅游平台'
            })

        if time_values:
            validation_details['hours'] = cross_validate_field('开放时间', time_values)

    # 计算整体置信度
    field_confidences = [v['confidence'] for v in validation_details.values()]
    overall_confidence = sum(field_confidences) / len(field_confidences) if field_confidences else attraction.get('confidence', 0.5)

    validated['validation'] = {
        "details": validation_details,
        "overall_confidence": round(overall_confidence, 2),
        "validated": overall_confidence >= 0.6
    }

    # 更新置信度
    if field_confidences:
        validated['confidence'] = round(overall_confidence, 2)

    return validated


def validate_restaurant(restaurant: Dict[str, Any], sources: List[Dict[str, Any]]) -> Dict[str, Any]:
    """验证餐厅实体"""
    validated = restaurant.copy()
    validation_details = {}

    # 验证人均消费
    if restaurant.get('price_range'):
        price_values = [{
            'value': restaurant['price_range'],
            'source': restaurant.get('source_urls', ['未知'])[0],
            'source_id': restaurant.get('source_ids', [0])[0],
            'source_type': '美食平台'
        }]
        validation_details['price_range'] = cross_validate_field('人均消费', price_values)

    # 验证评分
    if restaurant.get('rating'):
        rating_values = [{
            'value': restaurant['rating'],
            'source': restaurant.get('source_urls', ['未知'])[0],
            'source_id': restaurant.get('source_ids', [0])[0],
            'source_type': '美食平台'
        }]
        validation_details['rating'] = cross_validate_field('评分', rating_values)

    # 计算整体置信度
    field_confidences = [v['confidence'] for v in validation_details.values()]
    overall_confidence = sum(field_confidences) / len(field_confidences) if field_confidences else restaurant.get('confidence', 0.5)

    validated['validation'] = {
        "details": validation_details,
        "overall_confidence": round(overall_confidence, 2),
        "validated": overall_confidence >= 0.6
    }

    if field_confidences:
        validated['confidence'] = round(overall_confidence, 2)

    return validated


def validate_hotel(hotel: Dict[str, Any], sources: List[Dict[str, Any]]) -> Dict[str, Any]:
    """验证酒店实体"""
    validated = hotel.copy()
    validation_details = {}

    # 验证价格
    if hotel.get('price_range'):
        price_values = [{
            'value': hotel['price_range'],
            'source': hotel.get('source_urls', ['未知'])[0],
            'source_id': hotel.get('source_ids', [0])[0],
            'source_type': '酒店预订平台'
        }]
        validation_details['price_range'] = cross_validate_field('价格', price_values)

    # 验证评分
    if hotel.get('rating'):
        rating_values = [{
            'value': hotel['rating'],
            'source': hotel.get('source_urls', ['未知'])[0],
            'source_id': hotel.get('source_ids', [0])[0],
            'source_type': '酒店预订平台'
        }]
        validation_details['rating'] = cross_validate_field('评分', rating_values)

    # 计算整体置信度
    field_confidences = [v['confidence'] for v in validation_details.values()]
    overall_confidence = sum(field_confidences) / len(field_confidences) if field_confidences else hotel.get('confidence', 0.5)

    validated['validation'] = {
        "details": validation_details,
        "overall_confidence": round(overall_confidence, 2),
        "validated": overall_confidence >= 0.6
    }

    if field_confidences:
        validated['confidence'] = round(overall_confidence, 2)

    return validated


def validate_all_entities(state: ValidationState) -> Dict[str, Any]:
    """验证所有实体"""
    entities = state.get("entities", {})
    analyzed_content = state.get("analyzed_content", [])

    if not entities:
        return {
            "validated_entities": {},
            "validation_report": {
                "total_entities": 0,
                "high_confidence": 0,
                "medium_confidence": 0,
                "low_confidence": 0,
                "validated_count": 0,
                "conflict_count": 0
            },
            "current_step": "completed",
        }

    validated_entities = {}
    validation_report = {
        "total_entities": 0,
        "high_confidence": 0,  # >= 0.8
        "medium_confidence": 0,  # 0.6-0.8
        "low_confidence": 0,  # < 0.6
        "validated_count": 0,  # 已验证通过的
        "conflict_count": 0,  # 有冲突的
        "conflicts": []  # 冲突详情
    }

    # 验证景点
    for attraction in entities.get('attractions', []):
        validated = validate_attraction(attraction, analyzed_content)
        validated_entities.setdefault('attractions', []).append(validated)

        validation_report['total_entities'] += 1
        confidence = validated.get('confidence', 0.5)
        if confidence >= 0.8:
            validation_report['high_confidence'] += 1
        elif confidence >= 0.6:
            validation_report['medium_confidence'] += 1
        else:
            validation_report['low_confidence'] += 1

        if validated.get('validation', {}).get('validated', False):
            validation_report['validated_count'] += 1

        # 检查冲突
        for detail in validated.get('validation', {}).get('details', {}).values():
            if detail.get('conflicting_values'):
                validation_report['conflict_count'] += 1
                validation_report['conflicts'].append({
                    "entity": attraction.get('name'),
                    "field": list(validated.get('validation', {}).get('details', {}).keys()),
                    "conflict": detail['conflicting_values'][:2]
                })

    # 验证餐厅
    for restaurant in entities.get('restaurants', []):
        validated = validate_restaurant(restaurant, analyzed_content)
        validated_entities.setdefault('restaurants', []).append(validated)

        validation_report['total_entities'] += 1
        confidence = validated.get('confidence', 0.5)
        if confidence >= 0.8:
            validation_report['high_confidence'] += 1
        elif confidence >= 0.6:
            validation_report['medium_confidence'] += 1
        else:
            validation_report['low_confidence'] += 1

        if validated.get('validation', {}).get('validated', False):
            validation_report['validated_count'] += 1

    # 验证酒店
    for hotel in entities.get('hotels', []):
        validated = validate_hotel(hotel, analyzed_content)
        validated_entities.setdefault('hotels', []).append(validated)

        validation_report['total_entities'] += 1
        confidence = validated.get('confidence', 0.5)
        if confidence >= 0.8:
            validation_report['high_confidence'] += 1
        elif confidence >= 0.6:
            validation_report['medium_confidence'] += 1
        else:
            validation_report['low_confidence'] += 1

        if validated.get('validation', {}).get('validated', False):
            validation_report['validated_count'] += 1

    # 复制其他不需要验证的实体
    for key in ['transportations', 'tips', 'weather', 'budget_estimate', 'best_time', 'extraction_metadata']:
        if key in entities:
            validated_entities[key] = entities[key]

    logger.info(f"验证完成: 总实体{validation_report['total_entities']}个，"
               f"高置信度{validation_report['high_confidence']}个，"
               f"中置信度{validation_report['medium_confidence']}个，"
               f"低置信度{validation_report['low_confidence']}个，"
               f"冲突{validation_report['conflict_count']}个")

    return {
        "validated_entities": validated_entities,
        "validation_report": validation_report,
        "current_step": "completed",
    }


def build_validation_agent():
    """构建验证 Agent"""
    from langgraph.graph import StateGraph, END

    workflow = StateGraph(ValidationState)

    workflow.add_node("validate_entities", validate_all_entities)

    workflow.set_entry_point("validate_entities")
    workflow.add_edge("validate_entities", END)

    return workflow.compile()


def run_validation(
    entities: Dict[str, Any],
    analyzed_content: List[Dict[str, Any]],
    model: str = None
) -> Dict[str, Any]:
    """运行信息验证

    Args:
        entities: 提取的结构化实体
        analyzed_content: 原始分析内容
        model: 使用的模型（当前验证不使用LLM）

    Returns:
        {
            "validated_entities": {...},
            "validation_report": {...}
        }
    """
    logger.info(f"开始信息验证，实体类型数量: {len(entities)}")

    agent = build_validation_agent()
    result = agent.invoke({
        "entities": entities,
        "analyzed_content": analyzed_content,
        "validated_entities": {},
        "validation_report": {},
        "current_step": "init",
        "error": "",
        "model": model,
    })

    return result