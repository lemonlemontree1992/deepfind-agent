import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, Loader2, ChevronDown, ChevronRight, Zap, Globe2, BookOpen, ExternalLink } from 'lucide-react';
import { cn } from '@/lib/utils';

interface TodoItem {
  text: string;
  completed: boolean;
}

interface TodosCardProps {
  todos: string[];
  completedCount?: number;
}

export const TodosCard: React.FC<TodosCardProps> = ({ todos, completedCount = 0 }) => {
  const [expanded, setExpanded] = React.useState(true);
  const cardId = React.useId();

  return (
    <div className="my-3 rounded-lg border border-border bg-muted/30 overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-muted/50 transition-colors"
        aria-expanded={expanded}
        aria-controls={`${cardId}-content`}
        aria-label={`任务拆解，已完成 ${completedCount}/${todos.length} 项`}
      >
        <div className="flex items-center gap-2">
          <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/10 text-primary text-sm font-medium">
            {completedCount}/{todos.length}
          </div>
          <span className="font-medium text-sm">任务拆解</span>
          {completedCount === todos.length && (
            <CheckCircle2 className="h-4 w-4 text-green-500" aria-label="已完成全部任务" />
          )}
        </div>
        {expanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
      </button>
      <AnimatePresence>
        {expanded && (
          <motion.div
            id={`${cardId}-content`}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="border-t border-border"
            role="region"
            aria-label="任务列表"
          >
            <ul className="px-4 py-2 space-y-1" role="list">
              {todos.map((todo, idx) => (
                <li key={idx} className="flex items-start gap-2 text-sm py-1">
                  <span className={cn(
                    "flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center text-xs",
                    idx < completedCount
                      ? "bg-green-100 text-green-600"
                      : "bg-muted text-muted-foreground"
                  )} aria-hidden="true">
                    {idx < completedCount ? '✓' : idx + 1}
                  </span>
                  <span className={cn(
                    "text-gray-700",
                    idx < completedCount && "line-through text-muted-foreground"
                  )}>
                    {todo}
                    {idx < completedCount && <span className="sr-only">（已完成）</span>}
                  </span>
                </li>
              ))}
            </ul>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

interface SourceItem {
  title: string;
  url: string;
  status?: 'loading' | 'success' | 'error';
}

interface SourcesCardProps {
  sources: SourceItem[];
  title?: string;
  toolName?: string;
  status?: 'running' | 'completed';
}

export const SourcesCard: React.FC<SourcesCardProps> = ({
  sources,
  title = '搜索结果',
  toolName = 'search',
  status = 'completed'
}) => {
  const [expanded, setExpanded] = React.useState(true);
  const [showAll, setShowAll] = React.useState(false);
  const displaySources = showAll ? sources : sources.slice(0, 5);
  const cardId = React.useId();

  return (
    <div className="my-3 rounded-lg border border-border bg-muted/30 overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-muted/50 transition-colors"
        aria-expanded={expanded}
        aria-controls={`${cardId}-content`}
        aria-label={`${title}，共 ${sources.length} 条结果`}
      >
        <div className="flex items-center gap-2">
          {toolName === 'search' && <Zap className="h-4 w-4 text-amber-500" aria-hidden="true" />}
          {toolName === 'analyze' && <Globe2 className="h-4 w-4 text-blue-500" aria-hidden="true" />}
          <span className="font-medium text-sm">{title}</span>
          <span className="text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded-full">
            {sources.length} 条
          </span>
          {status === 'completed' && <CheckCircle2 className="h-4 w-4 text-green-500" aria-label="已完成" />}
          {status === 'running' && <Loader2 className="h-4 w-4 animate-spin text-primary" aria-label="加载中" />}
        </div>
        {expanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
      </button>
      <AnimatePresence>
        {expanded && (
          <motion.div
            id={`${cardId}-content`}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="border-t border-border"
            role="region"
            aria-label="来源列表"
          >
            <ul className="px-4 py-2 space-y-1 max-h-60 overflow-y-auto" role="list">
              {displaySources.map((source, idx) => (
                <li key={idx} className="flex items-center gap-2 text-sm py-1">
                  <span className="flex-shrink-0 w-5 h-5 rounded bg-muted text-muted-foreground text-xs flex items-center justify-center" aria-hidden="true">
                    {idx + 1}
                  </span>
                  <a
                    href={source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 text-blue-600 hover:underline truncate flex items-center gap-1"
                    aria-label={`${source.title || source.url}（在新窗口打开）`}
                  >
                    <span className="truncate">{source.title || source.url}</span>
                    <ExternalLink className="h-3 w-3 flex-shrink-0" aria-hidden="true" />
                  </a>
                  {source.status === 'loading' && <Loader2 className="h-3 w-3 animate-spin text-muted-foreground" aria-label="加载中" />}
                  {source.status === 'success' && <CheckCircle2 className="h-3 w-3 text-green-500" aria-label="加载成功" />}
                </li>
              ))}
            </ul>
            {sources.length > 5 && (
              <button
                onClick={() => setShowAll(!showAll)}
                className="w-full py-2 text-sm text-primary hover:bg-muted/50 transition-colors"
                aria-expanded={showAll}
              >
                {showAll ? `收起` : `+${sources.length - 5} 更多来源`}
              </button>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

interface ToolCallData {
  tool: string;
  status: 'running' | 'completed' | 'error';
  input?: string;
  output?: string;
  message?: string;
}

interface ToolCallCardProps {
  data: ToolCallData;
}

export const ToolCallCard: React.FC<ToolCallCardProps> = ({ data }) => {
  const toolIcons: Record<string, React.ReactNode> = {
    search: <Zap className="h-4 w-4 text-amber-500" aria-hidden="true" />,
    analyze: <Globe2 className="h-4 w-4 text-blue-500" aria-hidden="true" />,
    report: <BookOpen className="h-4 w-4 text-purple-500" aria-hidden="true" />,
  };

  const toolNames: Record<string, string> = {
    search: '搜索',
    analyze: '分析',
    report: '生成报告',
  };

  const statusText = {
    running: '进行中',
    completed: '已完成',
    error: '出错了'
  };

  return (
    <div
      className={cn(
        "my-2 px-4 py-3 rounded-lg border flex items-center gap-3",
        data.status === 'running' && "bg-blue-50/50 border-blue-200",
        data.status === 'completed' && "bg-green-50/50 border-green-200",
        data.status === 'error' && "bg-red-50/50 border-red-200"
      )}
      role="status"
      aria-live="polite"
      aria-label={`${toolNames[data.tool] || data.tool} - ${statusText[data.status]}`}
    >
      {toolIcons[data.tool] || <Zap className="h-4 w-4" aria-hidden="true" />}
      <div className="flex-1">
        <div className="font-medium text-sm">{toolNames[data.tool] || data.tool}</div>
        {data.message && <div className="text-xs text-muted-foreground">{data.message}</div>}
        {data.output && (
          <div className="text-xs text-green-600 mt-1">
            <span aria-hidden="true">✓</span> {data.output}
          </div>
        )}
      </div>
      {data.status === 'running' && (
        <Loader2 className="h-4 w-4 animate-spin text-primary" aria-label="加载中" />
      )}
      {data.status === 'completed' && (
        <CheckCircle2 className="h-4 w-4 text-green-500" aria-label="已完成" />
      )}
    </div>
  );
};