"""任务规划 Schema - 结构化任务定义与DAG依赖"""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TaskType(str, Enum):
    """任务类型"""
    SEARCH = "search"
    ANALYZE = "analyze"
    EXTRACT = "extract"
    VALIDATE = "validate"
    REPORT = "report"


class TaskPriority(int, Enum):
    """任务优先级"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


class Task(BaseModel):
    """任务模型"""
    id: str = Field(..., description="任务唯一标识")
    name: str = Field(..., description="任务名称")
    task_type: TaskType = Field(..., description="任务类型")
    description: str = Field(default="", description="任务描述")

    # 依赖关系
    dependencies: List[str] = Field(default_factory=list, description="依赖的任务ID列表")

    # 优先级与状态
    priority: TaskPriority = Field(default=TaskPriority.NORMAL, description="任务优先级")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="任务状态")

    # 输入输出
    input_data: Dict[str, Any] = Field(default_factory=dict, description="任务输入数据")
    output_data: Dict[str, Any] = Field(default_factory=dict, description="任务输出数据")

    # 执行信息
    started_at: Optional[datetime] = Field(default=None, description="开始时间")
    completed_at: Optional[datetime] = Field(default=None, description="完成时间")
    error_message: Optional[str] = Field(default=None, description="错误信息")

    # 重试配置
    max_retries: int = Field(default=3, description="最大重试次数")
    retry_count: int = Field(default=0, description="当前重试次数")

    class Config:
        use_enum_values = True


class TaskPlan(BaseModel):
    """任务计划"""
    plan_id: str = Field(..., description="计划ID")
    query: str = Field(..., description="原始查询")
    query_type: str = Field(..., description="查询类型: simple/travel_guide/research")

    # 任务列表
    tasks: List[Task] = Field(default_factory=list, description="任务列表")

    # 执行顺序（拓扑排序后的任务ID列表）
    execution_order: List[str] = Field(default_factory=list, description="执行顺序")

    # 并行分组
    parallel_groups: List[List[str]] = Field(default_factory=list, description="可并行执行的任务组")

    # 元数据
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    estimated_time: int = Field(default=0, description="预计执行时间(秒)")

    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def get_ready_tasks(self) -> List[Task]:
        """获取可以执行的任务（依赖已完成）"""
        ready_tasks = []
        for task in self.tasks:
            if task.status != TaskStatus.PENDING:
                continue

            # 检查依赖是否全部完成
            all_deps_completed = True
            for dep_id in task.dependencies:
                dep_task = self.get_task(dep_id)
                if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                    all_deps_completed = False
                    break

            if all_deps_completed:
                ready_tasks.append(task)

        # 按优先级排序
        ready_tasks.sort(key=lambda t: t["priority"] if isinstance(t, dict) else t.priority)
        return ready_tasks

    def get_execution_progress(self) -> Dict[str, Any]:
        """获取执行进度"""
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED)
        running = sum(1 for t in self.tasks if t.status == TaskStatus.RUNNING)
        failed = sum(1 for t in self.tasks if t.status == TaskStatus.FAILED)

        return {
            "total": total,
            "completed": completed,
            "running": running,
            "failed": failed,
            "progress": completed / total if total > 0 else 0,
            "is_complete": completed == total,
        }


class TaskResult(BaseModel):
    """任务执行结果"""
    task_id: str
    task_name: str
    success: bool
    output_data: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    execution_time: float = 0.0  # 秒

    class Config:
        use_enum_values = True