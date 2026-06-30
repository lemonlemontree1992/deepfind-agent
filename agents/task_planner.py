"""任务规划器 - 自动生成任务执行计划"""

import json
import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

from langchain_core.messages import HumanMessage, SystemMessage

from schemas.tasks import Task, TaskPlan, TaskStatus, TaskType, TaskPriority
from prompts.task_planning_prompts import (
    build_task_planning_prompt,
    create_default_travel_plan,
    create_default_simple_plan,
    create_default_research_plan,
)

logger = logging.getLogger(__name__)


def extract_destination_from_query(query: str) -> str:
    """从查询中提取目的地"""
    destinations = [
        '济州岛', '日本', '韩国', '泰国', '新加坡', '香港', '澳门', '台湾',
        '马来西亚', '印尼', '巴厘岛', '普吉岛', '马尔代夫', '塞班',
        '云南', '四川', '成都', '重庆', '西安', '北京', '上海', '杭州',
        '广州', '深圳', '厦门', '三亚', '海口', '大理', '丽江', '香格里拉',
        '西藏', '拉萨', '新疆', '敦煌', '青岛', '大连', '苏州', '南京',
        '东京', '大阪', '京都', '北海道', '冲绳', '首尔', '釜山',
        '曼谷', '清迈', '芭提雅', '普吉'
    ]
    for dest in destinations:
        if dest in query:
            return dest
    return "目的地"


def plan_tasks_for_query(
    query: str,
    query_type: str,
    model: str = None
) -> TaskPlan:
    """根据查询类型规划任务

    Args:
        query: 用户查询
        query_type: 查询类型 (simple/travel_guide/research)
        model: 模型名称

    Returns:
        TaskPlan: 任务计划
    """
    from config import settings
    from langchain_deepseek import ChatDeepSeek

    # 生成计划ID
    plan_id = str(uuid.uuid4())[:8]

    # 根据查询类型选择默认任务模板（不调用LLM，快速响应）
    if query_type == "travel_guide":
        destination = extract_destination_from_query(query)
        tasks_data = create_default_travel_plan(destination)
    elif query_type == "simple":
        tasks_data = create_default_simple_plan()
    else:
        tasks_data = create_default_research_plan()

    # 创建任务对象
    tasks = []
    for task_data in tasks_data:
        task = Task(
            id=task_data["id"],
            name=task_data["name"],
            task_type=task_data["task_type"],
            description=task_data.get("description", ""),
            dependencies=task_data.get("dependencies", []),
            priority=task_data.get("priority", TaskPriority.NORMAL.value),
            input_data=task_data.get("input_data", {}),
        )
        tasks.append(task)

    # 创建任务计划
    plan = TaskPlan(
        plan_id=plan_id,
        query=query,
        query_type=query_type,
        tasks=tasks,
        created_at=datetime.now(),
    )

    # 解析DAG并行层级
    from agents.task_executor import TaskExecutor
    executor = TaskExecutor()
    try:
        levels = executor.resolve_dag(tasks)
        plan.parallel_groups = levels
        plan.execution_order = [tid for level in levels for tid in level]
    except Exception as e:
        logger.warning(f"DAG解析失败: {e}")
        # 降级：按依赖顺序排列
        plan.parallel_groups = [[t.id for t in tasks if not t.dependencies]]
        plan.execution_order = [t.id for t in tasks]

    # 计算预计时间（基于任务数量和并行度）
    plan.estimated_time = len(plan.parallel_groups) * 5  # 每层约5秒

    logger.info(f"为查询 '{query[:30]}...' 创建了 {len(tasks)} 个任务, {len(plan.parallel_groups)} 个并行层级")

    return plan


def visualize_dag(plan: TaskPlan) -> str:
    """生成DAG可视化字符串

    Args:
        plan: 任务计划

    Returns:
        DAG可视化字符串
    """
    lines = []
    lines.append("```")
    lines.append("任务执行DAG:")
    lines.append("")

    # 按层级显示
    for level_idx, level in enumerate(plan.parallel_groups):
        if len(level) > 1:
            lines.append(f"Level {level_idx}: {' || '.join(level)} (并行)")
        else:
            lines.append(f"Level {level_idx}: {level[0]}")

        # 显示依赖关系
        if level_idx < len(plan.parallel_groups) - 1:
            next_level = plan.parallel_groups[level_idx + 1]
            for task_id in level:
                task = plan.get_task(task_id)
                if task:
                    # 找依赖此任务的下级任务
                    for next_task_id in next_level:
                        next_task = plan.get_task(next_task_id)
                        if next_task and task_id in next_task.dependencies:
                            lines.append(f"  {task_id} -> {next_task_id}")

    lines.append("```")
    return "\n".join(lines)


def get_task_summary(plan: TaskPlan) -> Dict[str, Any]:
    """获取任务计划摘要

    Args:
        plan: 任务计划

    Returns:
        摘要信息
    """
    progress = plan.get_execution_progress()

    task_by_type = {}
    for task in plan.tasks:
        task_by_type.setdefault(task.task_type, []).append(task.id)

    return {
        "plan_id": plan.plan_id,
        "query": plan.query,
        "query_type": plan.query_type,
        "total_tasks": len(plan.tasks),
        "tasks_by_type": {k: len(v) for k, v in task_by_type.items()},
        "parallel_levels": len(plan.parallel_groups),
        "estimated_time": plan.estimated_time,
        "progress": progress,
    }