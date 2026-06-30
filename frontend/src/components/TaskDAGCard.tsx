import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, Loader2, Circle, AlertCircle, ChevronDown, ChevronRight, Zap, ArrowDown } from 'lucide-react';
import { cn } from '@/lib/utils';

// 任务状态类型
type TaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'skipped';

// 任务接口
interface Task {
  id: string;
  name: string;
  type: string;
  description: string;
  dependencies: string[];
  priority: number;
  status: TaskStatus;
}

// 任务计划接口
interface TaskPlan {
  plan_id: string;
  query_type: string;
  tasks: Task[];
  parallel_groups: string[][];
  summary: {
    total_tasks: number;
    parallel_levels: number;
    estimated_time: number;
    progress: {
      total: number;
      completed: number;
      running: number;
      failed: number;
      progress: number;
      is_complete: boolean;
    };
  };
}

interface TaskDAGCardProps {
  taskPlan: TaskPlan;
  taskStatuses?: Record<string, TaskStatus>;
  contentType?: string; // 自动识别的内容类型
}

// 任务状态图标
const TaskStatusIcon: React.FC<{ status: TaskStatus }> = ({ status }) => {
  switch (status) {
    case 'completed':
      return <CheckCircle2 className="h-4 w-4 text-green-500" />;
    case 'running':
      return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />;
    case 'failed':
      return <AlertCircle className="h-4 w-4 text-red-500" />;
    case 'skipped':
      return <Circle className="h-4 w-4 text-gray-400" />;
    default:
      return <Circle className="h-4 w-4 text-gray-300" />;
  }
};

// 任务类型颜色和图标
const taskTypeConfig: Record<string, { color: string; bgColor: string; borderColor: string; label: string }> = {
  search: { color: 'text-amber-600', bgColor: 'bg-amber-50', borderColor: 'border-amber-200', label: '搜索' },
  analyze: { color: 'text-blue-600', bgColor: 'bg-blue-50', borderColor: 'border-blue-200', label: '分析' },
  extract: { color: 'text-purple-600', bgColor: 'bg-purple-50', borderColor: 'border-purple-200', label: '提取' },
  validate: { color: 'text-orange-600', bgColor: 'bg-orange-50', borderColor: 'border-orange-200', label: '验证' },
  report: { color: 'text-green-600', bgColor: 'bg-green-50', borderColor: 'border-green-200', label: '生成' },
};

// 内容类型标签
const contentTypeLabels: Record<string, { label: string; icon: string; color: string }> = {
  weather: { label: '天气预报', icon: '🌤️', color: 'bg-blue-100 text-blue-700' },
  product: { label: '产品评测', icon: '📱', color: 'bg-purple-100 text-purple-700' },
  travel: { label: '旅行攻略', icon: '✈️', color: 'bg-green-100 text-green-700' },
  tech: { label: '技术指南', icon: '💻', color: 'bg-orange-100 text-orange-700' },
  news: { label: '新闻资讯', icon: '📰', color: 'bg-red-100 text-red-700' },
  qa: { label: '问答', icon: '❓', color: 'bg-yellow-100 text-yellow-700' },
  other: { label: '综合信息', icon: '📋', color: 'bg-gray-100 text-gray-700' },
};

// 任务节点组件
const TaskNode: React.FC<{
  task: Task;
  isRunning: boolean;
}> = ({ task, isRunning }) => {
  const config = taskTypeConfig[task.type] || { color: 'text-gray-600', bgColor: 'bg-gray-50', borderColor: 'border-gray-200', label: task.type };

  return (
    <motion.div
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      className={cn(
        "relative flex items-center gap-2 px-3 py-2 rounded-lg border-2 transition-all duration-300",
        config.bgColor,
        config.borderColor,
        task.status === 'completed' && "border-green-400 bg-green-50/80",
        task.status === 'running' && "border-blue-400 bg-blue-50/80 shadow-md",
        task.status === 'failed' && "border-red-400 bg-red-50/80",
        isRunning && "ring-2 ring-blue-400 ring-offset-1"
      )}
    >
      {/* 状态指示器 */}
      <div className="flex-shrink-0">
        <TaskStatusIcon status={task.status} />
      </div>

      {/* 任务类型标签 */}
      <span className={cn(
        "text-xs px-1.5 py-0.5 rounded font-medium",
        config.color,
        "bg-white/60"
      )}>
        {config.label}
      </span>

      {/* 任务名称 */}
      <span className="text-xs font-medium text-gray-700 truncate max-w-[120px]">
        {task.name}
      </span>

      {/* 运行中的脉冲动画 */}
      {isRunning && (
        <motion.div
          className="absolute inset-0 rounded-lg border-2 border-blue-400"
          animate={{ opacity: [0.5, 0, 0.5], scale: [1, 1.02, 1] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        />
      )}
    </motion.div>
  );
};

// DAG 连接线组件
const DAGConnector: React.FC<{ isHighlight?: boolean }> = ({ isHighlight }) => (
  <div className="flex flex-col items-center py-1">
    <motion.div
      initial={{ height: 0, opacity: 0 }}
      animate={{ height: 'auto', opacity: 1 }}
      className={cn(
        "w-0.5 h-4 rounded-full",
        isHighlight ? "bg-blue-400" : "bg-gray-300"
      )}
    />
    <ArrowDown className={cn(
      "h-3 w-3 -mt-1",
      isHighlight ? "text-blue-400" : "text-gray-300"
    )} />
  </div>
);

// 并行指示器
const ParallelIndicator: React.FC<{ count: number }> = ({ count }) => (
  <div className="flex items-center gap-1 text-xs text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full">
    <Zap className="h-3 w-3" />
    <span>并行 x{count}</span>
  </div>
);

export const TaskDAGCard: React.FC<TaskDAGCardProps> = ({ taskPlan, taskStatuses = {}, contentType }) => {
  const [expanded, setExpanded] = React.useState(true); // 默认展开
  const cardId = React.useId();

  const { tasks, parallel_groups, summary } = taskPlan;

  // 合并任务状态
  const enrichedTasks = tasks.map(task => ({
    ...task,
    status: taskStatuses[task.id] || task.status,
  }));

  // 动态计算进度（基于实时任务状态）
  const progress = React.useMemo(() => {
    const total = enrichedTasks.length;
    const completed = enrichedTasks.filter(t => t.status === 'completed').length;
    const running = enrichedTasks.filter(t => t.status === 'running').length;
    const failed = enrichedTasks.filter(t => t.status === 'failed').length;
    return {
      total,
      completed,
      running,
      failed,
      progress: total > 0 ? completed / total : 0,
      is_complete: completed === total,
    };
  }, [enrichedTasks]);

  // 检查是否有正在运行的任务
  const hasRunningTasks = progress.running > 0;

  // 获取当前运行的层级
  const runningLevel = React.useMemo(() => {
    for (let i = 0; i < parallel_groups.length; i++) {
      const levelTasks = parallel_groups[i].map(id => enrichedTasks.find(t => t.id === id)).filter(Boolean);
      if (levelTasks.some(t => t?.status === 'running')) {
        return i;
      }
    }
    return -1;
  }, [parallel_groups, enrichedTasks]);

  return (
    <div className="my-3 rounded-lg border border-border bg-gradient-to-br from-slate-50/50 to-blue-50/30 overflow-hidden shadow-sm">
      {/* 头部 */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-muted/30 transition-colors"
        aria-expanded={expanded}
        aria-controls={`${cardId}-content`}
      >
        <div className="flex items-center gap-3">
          <div className={cn(
            "p-1.5 rounded-lg",
            hasRunningTasks ? "bg-blue-100" : progress.is_complete ? "bg-green-100" : "bg-gray-100"
          )}>
            <Zap className={cn(
              "h-4 w-4",
              hasRunningTasks ? "text-blue-500 animate-pulse" : progress.is_complete ? "text-green-500" : "text-gray-400"
            )} />
          </div>
          <div className="text-left">
            <div className="flex items-center gap-2">
              <span className="font-medium text-sm">任务规划</span>
              {contentType && contentTypeLabels[contentType] && (
                <span className={`text-xs px-2 py-0.5 rounded-full ${contentTypeLabels[contentType].color}`}>
                  {contentTypeLabels[contentType].icon} {contentTypeLabels[contentType].label}
                </span>
              )}
            </div>
            <div className="text-xs text-muted-foreground flex items-center gap-2">
              <span>{progress.completed}/{progress.total} 完成</span>
              <span className="text-gray-300">|</span>
              <span>{summary.parallel_levels} 层级</span>
              <span className="text-gray-300">|</span>
              <span>~{summary.estimated_time}秒</span>
              {hasRunningTasks && (
                <>
                  <span className="text-gray-300">|</span>
                  <span className="text-blue-500 font-medium animate-pulse">执行中...</span>
                </>
              )}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {progress.is_complete && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="flex items-center gap-1 text-green-600 text-xs"
            >
              <CheckCircle2 className="h-4 w-4" />
              <span>完成</span>
            </motion.div>
          )}
          {expanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
        </div>
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            id={`${cardId}-content`}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="border-t border-border"
          >
            {/* 进度条 */}
            <div className="px-4 py-2 bg-muted/30">
              <div className="flex items-center justify-between text-xs text-muted-foreground mb-1.5">
                <span>执行进度</span>
                <span className="font-medium">{Math.round(progress.progress * 100)}%</span>
              </div>
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-blue-500 to-green-500 rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${progress.progress * 100}%` }}
                  transition={{ duration: 0.5, ease: "easeOut" }}
                />
              </div>
              {/* 任务状态统计 */}
              <div className="flex items-center gap-3 mt-2 text-xs">
                {progress.completed > 0 && (
                  <span className="flex items-center gap-1 text-green-600">
                    <CheckCircle2 className="h-3 w-3" />
                    {progress.completed} 完成
                  </span>
                )}
                {progress.running > 0 && (
                  <span className="flex items-center gap-1 text-blue-600">
                    <Loader2 className="h-3 w-3 animate-spin" />
                    {progress.running} 执行中
                  </span>
                )}
                {progress.failed > 0 && (
                  <span className="flex items-center gap-1 text-red-600">
                    <AlertCircle className="h-3 w-3" />
                    {progress.failed} 失败
                  </span>
                )}
              </div>
            </div>

            {/*图形化 DAG 视图 */}
            <div className="px-4 py-4 bg-gradient-to-b from-transparent to-slate-50/50">
              <div className="text-xs text-muted-foreground font-medium mb-3 flex items-center gap-2">
                <span>执行流程</span>
                {parallel_groups.some(g => g.length > 1) && (
                  <span className="text-amber-600 bg-amber-50 px-1.5 py-0.5 rounded text-[10px]">
                    支持并行执行
                  </span>
                )}
              </div>

              <div className="space-y-1">
                {parallel_groups.map((level, levelIdx) => {
                  const levelTasks = level.map(taskId => enrichedTasks.find(t => t.id === taskId)).filter(Boolean) as Task[];
                  const isCurrentLevel = levelIdx === runningLevel;
                  const allCompleted = levelTasks.every(t => t.status === 'completed');
                  const hasFailed = levelTasks.some(t => t.status === 'failed');

                  return (
                    <React.Fragment key={levelIdx}>
                      {/* 层级标签 */}
                      <div className="flex items-center gap-2 mb-2">
                        <span className={cn(
                          "text-[10px] font-medium px-2 py-0.5 rounded-full",
                          isCurrentLevel ? "bg-blue-100 text-blue-700" :
                          allCompleted ? "bg-green-100 text-green-700" :
                          hasFailed ? "bg-red-100 text-red-700" :
                          "bg-gray-100 text-gray-500"
                        )}>
                          Level {levelIdx}
                        </span>
                        {level.length > 1 && (
                          <ParallelIndicator count={level.length} />
                        )}
                      </div>

                      {/* 任务节点 */}
                      <div className={cn(
                        "flex flex-wrap gap-2 pl-4",
                        level.length > 1 && "justify-center"
                      )}>
                        {levelTasks.map(task => (
                          <TaskNode
                            key={task.id}
                            task={task}
                            isRunning={task.status === 'running'}
                          />
                        ))}
                      </div>

                      {/* 层级间连接线 */}
                      {levelIdx < parallel_groups.length - 1 && (
                        <div className="flex justify-center py-2">
                          <div className={cn(
                            "flex flex-col items-center",
                            isCurrentLevel && "text-blue-400"
                          )}>
                            <div className={cn(
                              "w-px h-4 rounded-full",
                              isCurrentLevel ? "bg-blue-400" : "bg-gray-300"
                            )} />
                            <ArrowDown className={cn(
                              "h-3 w-3 -mt-1",
                              isCurrentLevel ? "text-blue-400" : "text-gray-300"
                            )} />
                          </div>
                        </div>
                      )}
                    </React.Fragment>
                  );
                })}
              </div>
            </div>

            {/* 任务详情列表 */}
            <details className="group border-t border-border">
              <summary className="px-4 py-2 text-xs text-muted-foreground cursor-pointer hover:bg-muted/30 flex items-center gap-2">
                <ChevronRight className="h-3 w-3 transition-transform group-open:rotate-90" />
                <span>查看任务详情 ({tasks.length} 个任务)</span>
              </summary>
              <div className="px-4 pb-3 space-y-1 max-h-48 overflow-y-auto">
                {enrichedTasks.map(task => (
                  <div
                    key={task.id}
                    className="flex items-center justify-between text-xs py-1.5 px-2 rounded hover:bg-muted/50"
                  >
                    <div className="flex items-center gap-2">
                      <TaskStatusIcon status={task.status} />
                      <span className="font-mono text-muted-foreground text-[10px]">{task.id}</span>
                      <span className="font-medium">{task.name}</span>
                    </div>
                    <div className="flex items-center gap-2 text-muted-foreground">
                      {task.dependencies.length > 0 && (
                        <span className="text-[10px] bg-gray-100 px-1 rounded">
                          依赖: {task.dependencies.length}
                        </span>
                      )}
                      <span className={cn(
                        "px-1.5 py-0.5 rounded text-[10px] font-medium",
                        taskTypeConfig[task.type]?.bgColor || 'bg-gray-50',
                        taskTypeConfig[task.type]?.color || 'text-gray-500'
                      )}>
                        {taskTypeConfig[task.type]?.label || task.type}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </details>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default TaskDAGCard;