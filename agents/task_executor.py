"""任务执行器 - DAG依赖管理与并行执行"""

import logging
import asyncio
import time
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import threading

from schemas.tasks import Task, TaskPlan, TaskStatus, TaskResult, TaskType

logger = logging.getLogger(__name__)


class TaskExecutor:
    """任务执行器

    支持特性:
    - DAG依赖解析与拓扑排序
    - 并行执行无依赖任务
    - 进度追踪与回调
    - 失败重试机制
    """

    def __init__(
        self,
        max_workers: int = 4,
        on_task_start: Optional[Callable] = None,
        on_task_complete: Optional[Callable] = None,
        on_task_error: Optional[Callable] = None,
        on_progress: Optional[Callable] = None,
    ):
        """
        Args:
            max_workers: 最大并行任务数
            on_task_start: 任务开始回调
            on_task_complete: 任务完成回调
            on_task_error: 任务错误回调
            on_progress: 进度更新回调
        """
        self.max_workers = max_workers
        self.on_task_start = on_task_start
        self.on_task_complete = on_task_complete
        self.on_task_error = on_task_error
        self.on_progress = on_progress
        self._lock = threading.Lock()

    def resolve_dag(self, tasks: List[Task]) -> List[List[str]]:
        """解析任务DAG，返回可并行执行的任务层级

        Returns:
            List[List[str]]: 每层可并行执行的任务ID列表
        """
        # 构建依赖图
        task_map = {task.id: task for task in tasks}
        in_degree = {task.id: 0 for task in tasks}
        graph = {task.id: [] for task in tasks}

        # 构建邻接表和入度计数
        for task in tasks:
            for dep_id in task.dependencies:
                if dep_id in task_map:
                    graph[dep_id].append(task.id)
                    in_degree[task.id] += 1

        # Kahn算法 - 拓扑排序并分层
        levels = []
        current_level = [tid for tid, deg in in_degree.items() if deg == 0]

        while current_level:
            # 当前层可并行执行
            levels.append(sorted(current_level))

            # 更新入度
            next_level = []
            for tid in current_level:
                for child_id in graph[tid]:
                    in_degree[child_id] -= 1
                    if in_degree[child_id] == 0:
                        next_level.append(child_id)

            current_level = sorted(list(set(next_level)))

        # 检查是否有环
        total_tasks = sum(len(level) for level in levels)
        if total_tasks != len(tasks):
            raise ValueError("任务依赖存在循环引用，无法执行")

        return levels

    def execute_task(
        self,
        task: Task,
        context: Dict[str, Any],
        task_handlers: Dict[str, Callable]
    ) -> TaskResult:
        """执行单个任务"""
        start_time = time.time()

        try:
            logger.info(f"开始执行任务: {task.id} - {task.name}")

            # 更新状态
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()

            if self.on_task_start:
                self.on_task_start(task)

            # 获取任务处理器
            handler = task_handlers.get(task.task_type)
            if not handler:
                raise ValueError(f"未知的任务类型: {task.task_type}")

            # 准备输入数据（合并上游输出）
            input_data = {**task.input_data, **context.get("upstream_outputs", {})}

            # 执行任务
            output = handler(task, input_data, context)

            # 更新状态
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.output_data = output if isinstance(output, dict) else {"result": output}

            execution_time = time.time() - start_time
            logger.info(f"任务完成: {task.id}, 耗时: {execution_time:.2f}s")

            result = TaskResult(
                task_id=task.id,
                task_name=task.name,
                success=True,
                output_data=task.output_data,
                execution_time=execution_time
            )

            if self.on_task_complete:
                self.on_task_complete(task, result)

            return result

        except Exception as e:
            # 任务失败
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()
            task.error_message = str(e)
            task.retry_count += 1

            execution_time = time.time() - start_time

            result = TaskResult(
                task_id=task.id,
                task_name=task.name,
                success=False,
                error_message=str(e),
                execution_time=execution_time
            )

            if self.on_task_error:
                self.on_task_error(task, result)

            return result

    def execute_plan(
        self,
        plan: TaskPlan,
        task_handlers: Dict[str, Callable],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """执行完整任务计划

        Args:
            plan: 任务计划
            task_handlers: 任务类型到处理函数的映射
            context: 执行上下文

        Returns:
            执行结果，包含所有任务输出和汇总数据
        """
        start_time = time.time()
        context = context or {}
        results = {}

        try:
            # 解析 DAG 层级
            levels = self.resolve_dag(plan.tasks)
            plan.execution_order = [tid for level in levels for tid in level]
            plan.parallel_groups = levels

            logger.info(f"任务计划分解为 {len(levels)} 层，共 {len(plan.tasks)} 个任务")
            logger.info(f"并行层级: {levels}")

            # 逐层执行
            for level_idx, level_tasks in enumerate(levels):
                logger.info(f"执行第 {level_idx + 1}/{len(levels)} 层任务: {level_tasks}")

                # 检查依赖失败
                failed_deps = [
                    tid for tid in level_tasks
                    if plan.get_task(tid) and plan.get_task(tid).status == TaskStatus.FAILED
                ]
                if failed_deps:
                    logger.error(f"层内有失败任务，跳过后续执行: {failed_deps}")
                    break

                # 该层可并行执行的任务
                tasks_to_run = [
                    plan.get_task(tid) for tid in level_tasks
                    if plan.get_task(tid) and plan.get_task(tid).status == TaskStatus.PENDING
                ]

                if not tasks_to_run:
                    continue

                # 准备上游输出
                upstream_outputs = {}
                for task in tasks_to_run:
                    for dep_id in task.dependencies:
                        dep_task = plan.get_task(dep_id)
                        if dep_task and dep_task.output_data:
                            upstream_outputs[dep_id] = dep_task.output_data

                context["upstream_outputs"] = upstream_outputs

                # 并行执行（使用线程池）
                with ThreadPoolExecutor(max_workers=min(len(tasks_to_run), self.max_workers)) as executor:
                    futures = {
                        executor.submit(self.execute_task, task, context, task_handlers): task
                        for task in tasks_to_run
                    }

                    for future in futures:
                        try:
                            result = future.result()
                            results[result.task_id] = result
                        except Exception as e:
                            logger.error(f"任务执行异常: {e}")

                # 更新进度
                progress = plan.get_execution_progress()
                if self.on_progress:
                    self.on_progress(progress)

                # 检查是否有失败
                failed_tasks = [t for t in tasks_to_run if t.status == TaskStatus.FAILED]
                if failed_tasks:
                    logger.error(f"第 {level_idx + 1} 层有 {len(failed_tasks)} 个任务失败")
                    # 继续执行，但记录失败

        except Exception as e:
            logger.error(f"任务计划执行失败: {e}")
            raise

        # 汇总结果
        total_time = time.time() - start_time
        final_progress = plan.get_execution_progress()

        return {
            "plan_id": plan.plan_id,
            "query": plan.query,
            "progress": final_progress,
            "results": results,
            "task_outputs": {
                task.id: task.output_data
                for task in plan.tasks
                if task.output_data
            },
            "total_time": total_time,
        }

    async def execute_plan_async(
        self,
        plan: TaskPlan,
        task_handlers: Dict[str, Callable],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """异步执行任务计划（用于SSE流式输出）"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.execute_plan,
            plan,
            task_handlers,
            context
        )


def create_task_handlers(api_context: Dict[str, Any]) -> Dict[str, Callable]:
    """创建任务处理器映射

    Args:
        api_context: API上下文（包含session_id, model等）

    Returns:
        任务类型到处理函数的映射
    """
    from agents.search_agent import run_search
    from agents.analyze_agent import run_analyze
    from agents.extraction_agent import run_extraction
    from agents.validation_agent import run_validation
    from agents.report_agent import run_report, generate_guide_from_entities
    from tools.parallel_search import parallel_search, merge_parallel_search_results, get_dimensional_search_queries

    def handle_search(task: Task, input_data: Dict, context: Dict) -> Dict:
        """处理搜索任务（支持并行多维度搜索）"""
        dimension = input_data.get("dimension", "general")
        queries = input_data.get("queries", [context.get("query", "")])

        # 合并上游搜索结果
        upstream_outputs = context.get("upstream_outputs", {})
        accumulated_results = []
        for dep_output in upstream_outputs.values():
            if "results" in dep_output:
                accumulated_results.extend(dep_output["results"])

        # 执行搜索
        results = []
        for query in queries[:3]:
            result = run_search(query)
            if result.get("search_results"):
                for r in result["search_results"]:
                    r["dimension"] = dimension
                results.extend(result["search_results"])

        return {"results": results, "queries": queries}

    def handle_parallel_search(task: Task, input_data: Dict, context: Dict) -> Dict:
        """处理并行多维度搜索任务"""
        destination = input_data.get("destination", context.get("query", ""))

        # 生成分维度查询
        queries_by_dimension = get_dimensional_search_queries(destination)

        # 执行并行搜索
        results_by_dimension = parallel_search(
            queries_by_dimension,
            max_results_per_query=5,
            max_workers=4
        )

        # 合并结果
        all_results = merge_parallel_search_results(results_by_dimension)

        return {
            "results": all_results,
            "results_by_dimension": results_by_dimension,
            "queries_by_dimension": queries_by_dimension
        }

    def handle_analyze(task: Task, input_data: Dict, context: Dict) -> Dict:
        """处理分析任务"""
        # 收集所有搜索结果
        upstream_outputs = context.get("upstream_outputs", {})
        all_results = []
        for dep_output in upstream_outputs.values():
            if "results" in dep_output:
                all_results.extend(dep_output["results"])

        if not all_results:
            return {"analyzed_content": []}

        # 执行分析
        result = run_analyze(all_results, context.get("query", ""))
        return {"analyzed_content": result.get("analyzed_content", [])}

    def handle_extract(task: Task, input_data: Dict, context: Dict) -> Dict:
        """处理提取任务"""
        upstream_outputs = context.get("upstream_outputs", {})
        analyzed_content = []
        for dep_output in upstream_outputs.values():
            if "analyzed_content" in dep_output:
                analyzed_content.extend(dep_output["analyzed_content"])

        if not analyzed_content:
            # 尝试直接从搜索结果获取
            for dep_output in upstream_outputs.values():
                if "results" in dep_output:
                    analyzed_content.extend(dep_output["results"])

        result = run_extraction(
            analyzed_content,
            context.get("query", ""),
            context.get("model")
        )
        return {"entities": result.get("entities", {})}

    def handle_validate(task: Task, input_data: Dict, context: Dict) -> Dict:
        """处理验证任务"""
        upstream_outputs = context.get("upstream_outputs", {})
        entities = {}
        analyzed_content = []

        for dep_output in upstream_outputs.values():
            if "entities" in dep_output:
                entities = dep_output["entities"]
            if "analyzed_content" in dep_output:
                analyzed_content.extend(dep_output["analyzed_content"])

        result = run_validation(entities, analyzed_content, context.get("model"))
        return {
            "validated_entities": result.get("validated_entities", {}),
            "validation_report": result.get("validation_report", {})
        }

    def handle_report(task: Task, input_data: Dict, context: Dict) -> Dict:
        """处理报告生成任务"""
        query = context.get("query", "")
        model = context.get("model")
        query_type = context.get("query_type", "research")

        upstream_outputs = context.get("upstream_outputs", {})
        analyzed_content = []
        entities = {}
        validated_entities = {}
        key_findings = ""

        # 收集上游数据
        for dep_output in upstream_outputs.values():
            if "analyzed_content" in dep_output:
                analyzed_content.extend(dep_output["analyzed_content"])
            if "entities" in dep_output:
                entities = dep_output["entities"]
            if "validated_entities" in dep_output:
                validated_entities = dep_output["validated_entities"]
            if "key_findings" in dep_output:
                key_findings = dep_output["key_findings"]

        # 根据查询类型选择生成方式
        if query_type == "travel_guide" and validated_entities:
            report = generate_guide_from_entities(
                validated_entities,
                query,
                analyzed_content,
                model
            )
        else:
            result = run_report(query, analyzed_content, key_findings, model)
            report = result.get("report", "")

        return {"report": report}

    return {
        TaskType.SEARCH.value: handle_search,
        TaskType.ANALYZE.value: handle_analyze,
        TaskType.EXTRACT.value: handle_extract,
        TaskType.VALIDATE.value: handle_validate,
        TaskType.REPORT.value: handle_report,
    }