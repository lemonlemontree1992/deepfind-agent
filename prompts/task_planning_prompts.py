"""任务规划 Prompt - 不同类型任务的任务模板"""

from typing import List, Dict, Any
from schemas.tasks import Task, TaskType, TaskPriority

# ============ 任务模板定义 ============

TRAVEL_GUIDE_TEMPLATE = """
## 旅行攻略任务模板

针对查询: "{query}"

### 任务分解

```json
{
  "tasks": [
    {
      "id": "search_attractions",
      "name": "搜索景点信息",
      "task_type": "search",
      "description": "搜索目的地景点、门票、开放时间",
      "dependencies": [],
      "priority": 1,
      "input_data": {
        "dimension": "attractions",
        "queries": ["{destination}必去景点", "{destination}门票价格", "{destination}景点交通"]
      }
    },
    {
      "id": "search_restaurants",
      "name": "搜索美食信息",
      "task_type": "search",
      "description": "搜索当地美食和餐厅推荐",
      "dependencies": [],
      "priority": 2,
      "input_data": {
        "dimension": "restaurants",
        "queries": ["{destination}美食推荐", "{destination}餐厅 地址 人均"]
      }
    },
    {
      "id": "search_hotels",
      "name": "搜索住宿信息",
      "task_type": "search",
      "description": "搜索酒店和住宿推荐",
      "dependencies": [],
      "priority": 2,
      "input_data": {
        "dimension": "hotels",
        "queries": ["{destination}住宿推荐", "{destination}酒店 价格"]
      }
    },
    {
      "id": "search_transport",
      "name": "搜索交通信息",
      "task_type": "search",
      "description": "搜索交通攻略",
      "dependencies": [],
      "priority": 3,
      "input_data": {
        "dimension": "transport",
        "queries": ["{destination}机场交通", "{destination}市内交通"]
      }
    },
    {
      "id": "extract_entities",
      "name": "提取结构化实体",
      "task_type": "extract",
      "description": "从搜索结果中提取景点、餐厅、酒店等实体",
      "dependencies": ["search_attractions", "search_restaurants", "search_hotels", "search_transport"],
      "priority": 1
    },
    {
      "id": "validate_entities",
      "name": "验证实体信息",
      "task_type": "validate",
      "description": "多来源交叉验证实体信息准确性",
      "dependencies": ["extract_entities"],
      "priority": 2
    },
    {
      "id": "generate_report",
      "name": "生成攻略报告",
      "task_type": "report",
      "description": "基于结构化数据生成详细攻略",
      "dependencies": ["validate_entities"],
      "priority": 1
    }
  ]
}
```

### DAG表示
```
search_attractions ----\\
search_restaurants -------> extract_entities -> validate_entities -> generate_report
search_hotels ----------/
search_transport -------/
```
"""

COMPETITIVE_ANALYSIS_TEMPLATE = """
## 竞品分析任务模板

针对查询: "{query}"

### 任务分解

```json
{
  "tasks": [
    {
      "id": "search_product_a",
      "name": "搜索产品A信息",
      "task_type": "search",
      "description": "搜索竞品A的功能特性、价格、用户评价",
      "dependencies": [],
      "priority": 1
    },
    {
      "id": "search_product_b",
      "name": "搜索产品B信息",
      "task_type": "search",
      "description": "搜索竞品B的功能特性、价格、用户评价",
      "dependencies": [],
      "priority": 1
    },
    {
      "id": "search_market",
      "name": "搜索市场信息",
      "task_type": "search",
      "description": "搜索市场格局、行业趋势",
      "dependencies": [],
      "priority": 2
    },
    {
      "id": "extract_features",
      "name": "提取功能特性",
      "task_type": "extract",
      "description": "提取竞品的功能特性列表",
      "dependencies": ["search_product_a", "search_product_b"],
      "priority": 1
    },
    {
      "id": "build_comparison",
      "name": "构建对比表格",
      "task_type": "analyze",
      "description": "构建竞品对比分析表格",
      "dependencies": ["extract_features"],
      "priority": 2
    },
    {
      "id": "generate_report",
      "name": "生成分析报告",
      "task_type": "report",
      "description": "生成竞品分析报告",
      "dependencies": ["build_comparison", "search_market"],
      "priority": 1
    }
  ]
}
```
"""

SIMPLE_QA_TEMPLATE = """
## 简单问答任务模板

针对查询: "{query}"

### 任务分解

```json
{
  "tasks": [
    {
      "id": "quick_search",
      "name": "快速搜索",
      "task_type": "search",
      "description": "搜索问题的直接答案",
      "dependencies": [],
      "priority": 1,
      "input_data": {
        "max_results": 3
      }
    },
    {
      "id": "generate_answer",
      "name": "生成答案",
      "task_type": "report",
      "description": "直接生成简洁答案",
      "dependencies": ["quick_search"],
      "priority": 1
    }
  ]
}
```
"""

DEEP_RESEARCH_TEMPLATE = """
## 深度调研任务模板

针对查询: "{query}"

### 任务分解

```json
{
  "tasks": [
    {
      "id": "search_general",
      "name": "通用搜索",
      "task_type": "search",
      "description": "搜索基本背景信息",
      "dependencies": [],
      "priority": 1
    },
    {
      "id": "search_deep_1",
      "name": "深度搜索1",
      "task_type": "search",
      "description": "搜索技术细节/实现方案",
      "dependencies": [],
      "priority": 2
    },
    {
      "id": "search_deep_2",
      "name": "深度搜索2",
      "task_type": "search",
      "description": "搜索案例分析/最佳实践",
      "dependencies": [],
      "priority": 2
    },
    {
      "id": "analyze_content",
      "name": "内容分析",
      "task_type": "analyze",
      "description": "深度分析所有搜索结果",
      "dependencies": ["search_general", "search_deep_1", "search_deep_2"],
      "priority": 1
    },
    {
      "id": "generate_report",
      "name": "生成报告",
      "task_type": "report",
      "description": "生成详细调研报告",
      "dependencies": ["analyze_content"],
      "priority": 1
    }
  ]
}
```
"""


# ============ 任务规划 Prompt ============

TASK_PLANNING_PROMPT = """你是一个任务规划专家，需要根据用户的查询制定最优的任务执行计划。

## 任务规划原则

1. **最小化依赖**: 尽量并行执行不相互依赖的任务
2. **最大化效率**: 按优先级排序，关键路径优先执行
3. **合理分解**: 任务粒度适中，不要过度拆分
4. **数据驱动**: 下游任务依赖上游任务的输出数据

## 任务类型说明

- **search**: 执行搜索，获取网页内容
- **analyze**: 分析内容，提取关键信息
- **extract**: 结构化提取，输出JSON实体
- **validate**: 交叉验证，检查信息准确性
- **report**: 生成最终报告

## 示例模板

{template}

## 当前任务

请为以下查询生成任务计划，输出JSON格式的任务列表：

**查询**: {query}
**查询类型**: {query_type}

**要求**:
1. 输出合法JSON格式
2. 任务ID简短唯一（如 search_1, extract_attractions）
3. 依赖关系明确且合理
4. 优先级1-4，1为最高
5. 只输出JSON，不要其他文字

输出格式:
```json
{{
  "tasks": [
    {{
      "id": "任务ID",
      "name": "任务名称",
      "task_type": "任务类型",
      "description": "任务描述",
      "dependencies": ["依赖的任务ID"],
      "priority": 1-4
    }}
  ]
}}
```
"""


def get_template_for_query_type(query_type: str) -> str:
    """根据查询类型获取任务模板"""
    templates = {
        "travel_guide": TRAVEL_GUIDE_TEMPLATE,
        "competitive": COMPETITIVE_ANALYSIS_TEMPLATE,
        "simple_qa": SIMPLE_QA_TEMPLATE,
        "research": DEEP_RESEARCH_TEMPLATE,
    }
    return templates.get(query_type, DEEP_RESEARCH_TEMPLATE)


def build_task_planning_prompt(query: str, query_type: str) -> str:
    """构建任务规划Prompt"""
    template = get_template_for_query_type(query_type)
    return TASK_PLANNING_PROMPT.format(
        template=template,
        query=query,
        query_type=query_type
    )


def create_default_travel_plan(destination: str) -> List[Dict[str, Any]]:
    """创建默认旅行攻略任务计划（不调用LLM）"""
    return [
        {
            "id": "search_attractions",
            "name": "搜索景点信息",
            "task_type": TaskType.SEARCH.value,
            "description": f"搜索{destination}景点、门票、开放时间",
            "dependencies": [],
            "priority": TaskPriority.CRITICAL.value,
            "input_data": {
                "dimension": "attractions",
                "queries": [f"{destination}必去景点", f"{destination}门票价格", f"{destination}景点交通"]
            }
        },
        {
            "id": "search_restaurants",
            "name": "搜索美食信息",
            "task_type": TaskType.SEARCH.value,
            "description": f"搜索{destination}美食和餐厅推荐",
            "dependencies": [],
            "priority": TaskPriority.HIGH.value,
            "input_data": {
                "dimension": "restaurants",
                "queries": [f"{destination}美食推荐", f"{destination}餐厅 地址 人均"]
            }
        },
        {
            "id": "search_hotels",
            "name": "搜索住宿信息",
            "task_type": TaskType.SEARCH.value,
            "description": f"搜索{destination}酒店和住宿推荐",
            "dependencies": [],
            "priority": TaskPriority.HIGH.value,
            "input_data": {
                "dimension": "hotels",
                "queries": [f"{destination}住宿推荐", f"{destination}酒店 价格"]
            }
        },
        {
            "id": "search_transport",
            "name": "搜索交通信息",
            "task_type": TaskType.SEARCH.value,
            "description": f"搜索{destination}交通攻略",
            "dependencies": [],
            "priority": TaskPriority.NORMAL.value,
            "input_data": {
                "dimension": "transport",
                "queries": [f"{destination}机场交通", f"{destination}市内交通"]
            }
        },
        {
            "id": "search_tips",
            "name": "搜索避坑指南",
            "task_type": TaskType.SEARCH.value,
            "description": f"搜索{destination}旅游贴士和避坑指南",
            "dependencies": [],
            "priority": TaskPriority.NORMAL.value,
            "input_data": {
                "dimension": "tips",
                "queries": [f"{destination}旅游避坑", f"{destination}注意事项 2024"]
            }
        },
        {
            "id": "extract_entities",
            "name": "提取结构化实体",
            "task_type": TaskType.EXTRACT.value,
            "description": "从搜索结果中提取景点、餐厅、酒店等实体",
            "dependencies": ["search_attractions", "search_restaurants", "search_hotels", "search_transport", "search_tips"],
            "priority": TaskPriority.CRITICAL.value,
            "input_data": {}
        },
        {
            "id": "validate_entities",
            "name": "验证实体信息",
            "task_type": TaskType.VALIDATE.value,
            "description": "多来源交叉验证实体信息准确性",
            "dependencies": ["extract_entities"],
            "priority": TaskPriority.HIGH.value,
            "input_data": {}
        },
        {
            "id": "generate_report",
            "name": "生成攻略报告",
            "task_type": TaskType.REPORT.value,
            "description": "基于结构化数据生成详细攻略",
            "dependencies": ["validate_entities"],
            "priority": TaskPriority.CRITICAL.value,
            "input_data": {}
        }
    ]


def create_default_simple_plan() -> List[Dict[str, Any]]:
    """创建默认简单问答任务计划"""
    return [
        {
            "id": "quick_search",
            "name": "快速搜索",
            "task_type": TaskType.SEARCH.value,
            "description": "搜索问题的直接答案",
            "dependencies": [],
            "priority": TaskPriority.CRITICAL.value,
            "input_data": {"max_results": 3}
        },
        {
            "id": "generate_answer",
            "name": "生成答案",
            "task_type": TaskType.REPORT.value,
            "description": "直接生成简洁答案",
            "dependencies": ["quick_search"],
            "priority": TaskPriority.CRITICAL.value,
            "input_data": {}
        }
    ]


def create_default_research_plan() -> List[Dict[str, Any]]:
    """创建默认深度调研任务计划"""
    return [
        {
            "id": "search_general",
            "name": "通用搜索",
            "task_type": TaskType.SEARCH.value,
            "description": "搜索基本背景信息",
            "dependencies": [],
            "priority": TaskPriority.CRITICAL.value,
            "input_data": {}
        },
        {
            "id": "search_deep_1",
            "name": "深度搜索1",
            "task_type": TaskType.SEARCH.value,
            "description": "搜索技术细节/实现方案",
            "dependencies": [],
            "priority": TaskPriority.HIGH.value,
            "input_data": {}
        },
        {
            "id": "search_deep_2",
            "name": "深度搜索2",
            "task_type": TaskType.SEARCH.value,
            "description": "搜索案例分析/最佳实践",
            "dependencies": [],
            "priority": TaskPriority.HIGH.value,
            "input_data": {}
        },
        {
            "id": "analyze_content",
            "name": "内容分析",
            "task_type": TaskType.ANALYZE.value,
            "description": "深度分析所有搜索结果",
            "dependencies": ["search_general", "search_deep_1", "search_deep_2"],
            "priority": TaskPriority.CRITICAL.value,
            "input_data": {}
        },
        {
            "id": "generate_report",
            "name": "生成报告",
            "task_type": TaskType.REPORT.value,
            "description": "生成详细调研报告",
            "dependencies": ["analyze_content"],
            "priority": TaskPriority.CRITICAL.value,
            "input_data": {}
        }
    ]