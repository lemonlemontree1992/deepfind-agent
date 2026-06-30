import React, { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Plus, Download, Trash2, MessageSquare, PanelLeftClose, PanelLeftOpen, Loader2, CheckCircle2, AlertCircle, FileText, X, RotateCcw, Globe, Search, Cpu, Zap, Globe2, FileSearch, BookOpen, Copy, Check } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Progress } from '@/components/ui/progress';
import { exportToPDF, Message } from '@/lib/pdfUtils';
import { cn } from '@/lib/utils';
import { useLanguage } from '@/contexts/LanguageContext';
import { useSessionStorage } from '@/hooks/useSessionStorage';
import { useSettings, ModelType } from '@/contexts/SettingsContext';
import { TodosCard, SourcesCard, ToolCallCard } from '@/components/AgentCards';
import { CopyButton } from '@/components/CopyButton';
import TaskDAGCard from '@/components/TaskDAGCard';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

// API 基础地址 - 从环境变量读取
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://deepfind-agent.onrender.com';

// 用于追踪活跃的 EventSource 连接
const activeEventSources = new Map<string, EventSource>();

// 工具调用状态
interface ToolCall {
  tool: string;
  status: 'running' | 'completed' | 'error';
  input?: string;
  output?: string;
  message?: string;
  urls?: Array<{ url: string; title: string; status: string }>;
}

// 每个问题批次的中间状态（通过索引与用户消息关联）
interface MessageBatch {
  toolCalls: ToolCall[];
  searchResults: Array<{ title: string; url: string }>;
  todos: string[];
  streamingContent: string;
  outputFiles?: Record<string, string>;
  // 内容类型：weather/product/travel/tech/news/qa/other
  contentType?: string;
  // 任务计划
  taskPlan?: {
    plan_id: string;
    query_type: string;
    tasks: Array<{
      id: string;
      name: string;
      type: string;
      description: string;
      dependencies: string[];
      priority: number;
      status: string;
    }>;
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
  };
  taskStatuses?: Record<string, 'pending' | 'running' | 'completed' | 'failed' | 'skipped'>;
}

interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  timestamp: number;
  status: 'idle' | 'running' | 'completed' | 'error' | 'cancelled';
  progress: number;
  currentStep: string;
  lastQuery?: string; // 用于重试
  batches: MessageBatch[]; // 每个问题的中间状态，索引与用户消息索引对应
}

const ChatPage: React.FC = () => {
  const { t, language, setLanguage } = useLanguage();
  const { model, setModel } = useSettings();
  const [sessions, setSessions, clearSessions] = useSessionStorage<ChatSession>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [inputValue, setInputValue] = useState('');
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [apiStatus, setApiStatus] = useState<'checking' | 'ok' | 'error'>('checking');
  const [searchQuery, setSearchQuery] = useState('');
  const initRef = useRef(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewContent, setPreviewContent] = useState('');
  const [previewFormat, setPreviewFormat] = useState<'markdown' | 'html'>('markdown');

  const currentSession = sessions.find(s => s.id === currentSessionId);

  // 过滤会话列表
  const filteredSessions = useMemo(() => {
    if (!searchQuery.trim()) return sessions;
    const query = searchQuery.toLowerCase();
    return sessions.filter(session =>
      session.title.toLowerCase().includes(query) ||
      session.messages.some(msg => msg.content.toLowerCase().includes(query))
    );
  }, [sessions, searchQuery]);

  // 检查 API 状态
  useEffect(() => {
    const checkApi = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
          setApiStatus('ok');
        } else {
          setApiStatus('error');
        }
      } catch {
        setApiStatus('error');
      }
    };

    checkApi();

    // 每 30 秒检查一次 API 状态
    const interval = setInterval(checkApi, 30000);

    return () => clearInterval(interval);
  }, []);

  // 初始化会话 - 使用 ref 防止重复初始化
  useEffect(() => {
    if (initRef.current) return;
    initRef.current = true;

    if (sessions.length === 0) {
      // 没有保存的会话，创建新会话
      createNewSession();
    } else if (!currentSessionId) {
      // 有保存的会话但没有选中的会话，选择第一个
      setCurrentSessionId(sessions[0].id);
    }
  // 只在组件挂载时执行一次
  // createNewSession 和 sessions 是初始化逻辑，不需要作为依赖
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentSessionId]);

  // 自动滚动到底部
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [currentSession?.messages]);

  // 组件卸载时清理所有 EventSource 连接
  useEffect(() => {
    return () => {
      activeEventSources.forEach((es) => es.close());
      activeEventSources.clear();
    };
  }, []);

  const createNewSession = useCallback(() => {
    const newSession: ChatSession = {
      id: Date.now().toString(),
      title: t.sidebar.newChat,
      messages: [
        {
          role: 'assistant',
          content: t.message.welcome
        }
      ],
      timestamp: Date.now(),
      status: 'idle',
      progress: 0,
      currentStep: '',
      lastQuery: undefined,
      batches: [], // 初始化为空数组
    };
    setSessions(prev => [newSession, ...prev]);
    setCurrentSessionId(newSession.id);
  }, [t, setSessions]);

  const deleteSession = useCallback(async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    e.preventDefault();

    // 关闭该 session 的 EventSource 连接（如果存在）
    const es = activeEventSources.get(id);
    if (es) {
      es.close();
      activeEventSources.delete(id);
    }

    // 调用后端删除 API
    try {
      await fetch(`${API_BASE_URL}/api/sessions/${id}`, { method: 'DELETE' });
    } catch (error) {
      console.error('Failed to delete session from backend:', error);
    }

    // 获取当前会话列表，计算删除后的列表
    setSessions(prev => {
      const filtered = prev.filter(s => s.id !== id);

      // 如果删除的是当前选中的会话
      if (currentSessionId === id) {
        if (filtered.length > 0) {
          // 切换到第一个可用会话
          setCurrentSessionId(filtered[0].id);
        } else {
          // 没有会话了，需要创建新会话
          setCurrentSessionId(null);
        }
      }

      return filtered;
    });

    // 如果删除后没有会话，延迟创建新会话
    setTimeout(() => {
      setSessions(prev => {
        if (prev.length === 0) {
          createNewSession();
        }
        return prev;
      });
    }, 50);
  }, [currentSessionId, setSessions, createNewSession]);

  const cancelResearch = async (sessionId: string) => {
    // 关闭 EventSource
    const es = activeEventSources.get(sessionId);
    if (es) {
      es.close();
      activeEventSources.delete(sessionId);
    }
    // 调用后端取消 API
    try {
      await fetch(`${API_BASE_URL}/api/research/${sessionId}/cancel`, { method: 'POST' });
    } catch (error) {
      console.error('Failed to cancel research:', error);
    }
    // 更新状态
    setSessions(prev => prev.map(session =>
      session.id === sessionId
        ? { ...session, status: 'cancelled' as const, currentStep: t.progress.cancelled }
        : session
    ));
  };

  const startResearch = async (query: string, sessionId: string, isRetry: boolean = false) => {
    // 添加用户消息并创建新批次（重试时不重复添加）
    if (!isRetry) {
      const userMessage: Message = { role: 'user', content: query };
      setSessions(prev => prev.map(session =>
        session.id === sessionId
          ? {
              ...session,
              messages: [...session.messages, userMessage],
              status: 'running' as const,
              progress: 0,
              currentStep: t.progress.initializing,
              title: query.slice(0, 20) + (query.length > 20 ? '...' : ''),
              lastQuery: query,
              // 添加新批次（索引将与用户消息在 filtered 数组中的索引对应）
              batches: [
                ...session.batches,
                {
                  toolCalls: [],
                  searchResults: [],
                  todos: [],
                  streamingContent: '',
                }
              ],
            }
          : session
      ));
    } else {
      // 重试时找到最后一个批次并重置其状态
      setSessions(prev => prev.map(session =>
        session.id === sessionId
          ? {
              ...session,
              status: 'running' as const,
              progress: 0,
              currentStep: t.progress.initializing,
              batches: session.batches.map((batch, idx) =>
                idx === session.batches.length - 1
                  ? { ...batch, toolCalls: [], searchResults: [], todos: [], streamingContent: '' }
                  : batch
              ),
            }
          : session
      ));
    }
    setInputValue('');

    // 关闭该 session 已有的 EventSource 连接
    const existingES = activeEventSources.get(sessionId);
    if (existingES) {
      existingES.close();
      activeEventSources.delete(sessionId);
    }

    try {
      // 使用 SSE 流式获取进度，传递模型参数
      const eventSource = new EventSource(`${API_BASE_URL}/api/research/stream?query=${encodeURIComponent(query)}&model=${model}`);
      activeEventSources.set(sessionId, eventSource);

      // 辅助函数：添加助手消息
      const addAssistantMessage = (content: string) => {
        setSessions(prev => prev.map(session =>
          session.id === sessionId
            ? { ...session, messages: [...session.messages, { role: 'assistant' as const, content }] }
            : session
        ));
      };

      // 辅助函数：更新 session 状态
      const updateSessionState = (updates: Partial<ChatSession>) => {
        setSessions(prev => prev.map(session =>
          session.id === sessionId ? { ...session, ...updates } : session
        ));
      };

      // 辅助函数：更新最后一个批次的状态
      const updateLastBatch = (updates: Partial<MessageBatch>) => {
        setSessions(prev => prev.map(session => {
          if (session.id !== sessionId) return session;
          if (session.batches.length === 0) return session;
          const updatedBatches = [...session.batches];
          updatedBatches[session.batches.length - 1] = {
            ...updatedBatches[session.batches.length - 1],
            ...updates
          };
          return { ...session, batches: updatedBatches };
        }));
      };

      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        updateSessionState({
          progress: data.progress,
          currentStep: data.step,
        });
      };

      eventSource.addEventListener('progress', (event) => {
        const data = JSON.parse(event.data);
        updateSessionState({
          progress: data.progress,
          currentStep: data.step,
        });
      });

      eventSource.addEventListener('warning', (event) => {
        const data = JSON.parse(event.data);
        console.warn('Server warning:', data.message);
      });

      // 工具开始执行 - 更新最后一个批次
      eventSource.addEventListener('tool_start', (event) => {
        const data = JSON.parse(event.data);
        setSessions(prev => prev.map(session => {
          if (session.id !== sessionId) return session;
          if (session.batches.length === 0) return session;
          const updatedBatches = [...session.batches];
          updatedBatches[session.batches.length - 1].toolCalls.push({
            tool: data.tool,
            status: 'running' as const,
            input: data.input,
            message: data.message,
          });
          return { ...session, batches: updatedBatches };
        }));
      });

      // 工具进度更新 - 更新最后一个批次
      eventSource.addEventListener('tool_progress', (event) => {
        const data = JSON.parse(event.data);
        setSessions(prev => prev.map(session => {
          if (session.id !== sessionId) return session;
          if (session.batches.length === 0) return session;
          const updatedBatches = [...session.batches];
          const toolCalls = updatedBatches[session.batches.length - 1].toolCalls;
          const lastTool = toolCalls[toolCalls.length - 1];
          if (lastTool && lastTool.status === 'running') {
            lastTool.message = data.message;
            if (data.url) {
              lastTool.urls = lastTool.urls || [];
              lastTool.urls.push({ url: data.url, title: '', status: 'loading' });
            }
          }
          return { ...session, batches: updatedBatches };
        }));
      });

      // 工具执行完成 - 更新最后一个批次
      eventSource.addEventListener('tool_end', (event) => {
        const data = JSON.parse(event.data);
        setSessions(prev => prev.map(session => {
          if (session.id !== sessionId) return session;
          if (session.batches.length === 0) return session;
          const updatedBatches = [...session.batches];
          const toolCalls = updatedBatches[session.batches.length - 1].toolCalls;
          const lastTool = toolCalls[toolCalls.length - 1];
          if (lastTool) {
            lastTool.status = 'completed';
            lastTool.output = data.output_summary;
          }
          return { ...session, batches: updatedBatches };
        }));
      });

      // 页面加载进度 - 更新最后一个批次
      eventSource.addEventListener('page_progress', (event) => {
        const data = JSON.parse(event.data);
        setSessions(prev => prev.map(session => {
          if (session.id !== sessionId) return session;
          if (session.batches.length === 0) return session;
          const updatedBatches = [...session.batches];
          const toolCalls = updatedBatches[session.batches.length - 1].toolCalls;
          const lastTool = toolCalls[toolCalls.length - 1];
          if (lastTool && lastTool.status === 'running') {
            lastTool.urls = lastTool.urls || [];
            lastTool.urls.push({ url: data.url, title: data.title, status: 'pending' });
          }
          return { ...session, batches: updatedBatches };
        }));
      });

      // 页面加载完成 - 更新最后一个批次
      eventSource.addEventListener('page_loaded', (event) => {
        const data = JSON.parse(event.data);
        setSessions(prev => prev.map(session => {
          if (session.id !== sessionId) return session;
          if (session.batches.length === 0) return session;
          const updatedBatches = [...session.batches];
          const toolCalls = updatedBatches[session.batches.length - 1].toolCalls;
          const lastTool = toolCalls[toolCalls.length - 1];
          if (lastTool && lastTool.urls) {
            const urlIndex = lastTool.urls.findIndex(u => u.url === data.url);
            if (urlIndex >= 0) {
              lastTool.urls[urlIndex].status = data.status;
              lastTool.urls[urlIndex].title = data.title;
            }
          }
          return { ...session, batches: updatedBatches };
        }));
      });

      // LLM 流式输出 - 更新最后一个批次
      eventSource.addEventListener('llm_chunk', (event) => {
        const data = JSON.parse(event.data);
        setSessions(prev => prev.map(session => {
          if (session.id !== sessionId) return session;
          if (session.batches.length === 0) return session;
          const updatedBatches = [...session.batches];
          updatedBatches[session.batches.length - 1].streamingContent += data.content;
          return { ...session, batches: updatedBatches };
        }));
      });

      // todos 更新最后一个批次
      eventSource.addEventListener('todos', (event) => {
        const data = JSON.parse(event.data);
        updateLastBatch({ todos: data.todos });
      });

      // task_plan 任务计划事件
      eventSource.addEventListener('task_plan', (event) => {
        const data = JSON.parse(event.data);
        updateLastBatch({
          taskPlan: {
            plan_id: data.plan_id,
            query_type: data.query_type,
            tasks: data.tasks,
            parallel_groups: data.parallel_groups,
            summary: data.summary,
          },
          taskStatuses: {}
        });
        updateSessionState({
          currentStep: `任务规划: ${data.summary?.total_tasks || 0} 个任务`
        });
      });

      // task_status 任务状态更新事件
      eventSource.addEventListener('task_status', (event) => {
        const data = JSON.parse(event.data);
        setSessions(prev => prev.map(session => {
          if (session.id !== sessionId) return session;
          if (session.batches.length === 0) return session;
          const lastBatchIndex = session.batches.length - 1;
          const currentStatuses = session.batches[lastBatchIndex].taskStatuses || {};
          const updatedBatches = [...session.batches];
          updatedBatches[lastBatchIndex] = {
            ...updatedBatches[lastBatchIndex],
            taskStatuses: {
              ...currentStatuses,
              [data.task_id]: data.status
            }
          };
          return {
            ...session,
            batches: updatedBatches,
            currentStep: data.message || `${data.task_id}: ${data.status}`
          };
        }));
      });

      // extraction 内容类型识别事件
      eventSource.addEventListener('extraction', (event) => {
        const data = JSON.parse(event.data);
        const contentType = data.content_type || 'unknown';
        const typeLabels: Record<string, string> = {
          'weather': '天气预报',
          'product': '产品评测',
          'travel': '旅行攻略',
          'tech': '技术指南',
          'news': '新闻资讯',
          'qa': '问答',
          'other': '综合信息'
        };
        updateLastBatch({
          contentType: contentType,
        });
        updateSessionState({
          currentStep: `识别为${typeLabels[contentType] || contentType}类型`
        });
      });

      // search 更新最后一个批次
      eventSource.addEventListener('search', (event) => {
        const data = JSON.parse(event.data);
        updateLastBatch({ searchResults: data.results });
        updateSessionState({
          progress: 30,
          currentStep: t.progress.searchComplete
        });
      });

      eventSource.addEventListener('analyze', (event) => {
        updateSessionState({
          progress: 60,
          currentStep: t.progress.analyzeComplete
        });
      });

      // complete 更新最后一个批次
      eventSource.addEventListener('complete', (event) => {
        const data = JSON.parse(event.data);
        setSessions(prev => prev.map(session => {
          if (session.id !== sessionId) return session;
          if (session.batches.length === 0) return session;
          const lastBatchIndex = session.batches.length - 1;
          // 优先使用后端返回的完整报告（包含参考资料），而不是流式累积的内容
          const reportContent = data.report || session.batches[lastBatchIndex].streamingContent;
          const updatedBatches = [...session.batches];
          updatedBatches[lastBatchIndex].outputFiles = data.output_files;
          updatedBatches[lastBatchIndex].streamingContent = '';
          return {
            ...session,
            status: 'completed' as const,
            progress: 100,
            currentStep: t.progress.completed,
            messages: [...session.messages, { role: 'assistant' as const, content: reportContent }],
            batches: updatedBatches,
          };
        }));
        eventSource.close();
        activeEventSources.delete(sessionId);
      });

      eventSource.addEventListener('cancelled', (event) => {
        const data = JSON.parse(event.data);
        addAssistantMessage(`⏹️ **${t.progress.cancelled}**\n\n${data.message}`);
        updateSessionState({ status: 'cancelled', currentStep: t.progress.cancelled });
        eventSource.close();
        activeEventSources.delete(sessionId);
      });

      eventSource.addEventListener('error', (event) => {
        const data = JSON.parse(event.data);
        addAssistantMessage(`${t.message.error}${data.message}`);
        updateSessionState({ status: 'error' });
        eventSource.close();
        activeEventSources.delete(sessionId);
      });

      eventSource.onerror = () => {
        addAssistantMessage(t.message.connectionLost);
        updateSessionState({ status: 'error' });
        eventSource.close();
        activeEventSources.delete(sessionId);
      };

    } catch (error) {
      setSessions(prev => prev.map(session =>
        session.id === sessionId
          ? {
              ...session,
              status: 'error' as const,
              messages: [...session.messages, {
                role: 'assistant' as const,
                content: t.message.networkError
              }]
            }
          : session
      ));
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || !currentSessionId || apiStatus !== 'ok') return;
    await startResearch(inputValue, currentSessionId);
  };

  const handleRetry = async (sessionId: string) => {
    const session = sessions.find(s => s.id === sessionId);
    if (!session?.lastQuery) return;
    // 移除最后一条错误消息
    setSessions(prev => prev.map(s =>
      s.id === sessionId
        ? { ...s, messages: s.messages.slice(0, -1) }
        : s
    ));
    await startResearch(session.lastQuery, sessionId, true);
  };

  const handleExportPDF = () => {
    // PDF 导出功能已移除
    toast.info("PDF 导出功能已停用，请使用 Markdown 或 HTML 格式");
  };

  const handleDownloadReport = async (format: 'markdown' | 'html') => {
    // 从最后一个批次获取 outputFile
    const lastBatch = currentSession?.batches?.[currentSession.batches.length - 1];
    const filePath = lastBatch?.outputFiles?.[format];
    if (!filePath) return;

    try {
      // 从后端下载文件
      const response = await fetch(`${API_BASE_URL}/api/download?path=${encodeURIComponent(filePath)}&format=${format}`);
      if (!response.ok) throw new Error('下载失败');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filePath.split('/').pop() || `report.${format === 'markdown' ? 'md' : 'html'}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      toast.success(`已下载 ${format === 'markdown' ? 'Markdown' : 'HTML'} 文件`);
    } catch (error) {
      console.error('下载失败:', error);
      toast.error('下载失败，请重试');
    }
  };

  const handlePreviewReport = async (format: 'markdown' | 'html') => {
    // 从最后一个批次获取 outputFile
    const lastBatch = currentSession?.batches?.[currentSession.batches.length - 1];
    const filePath = lastBatch?.outputFiles?.[format];
    if (!filePath) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/download?path=${encodeURIComponent(filePath)}&format=${format}`);
      if (!response.ok) throw new Error('获取预览失败');

      const content = await response.text();
      setPreviewContent(content);
      setPreviewFormat(format);
      setPreviewOpen(true);
    } catch (error) {
      console.error('预览失败:', error);
      toast.error('预览失败，请重试');
    }
  };

  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden">
      {/* Sidebar */}
      <AnimatePresence mode="wait">
        {isSidebarOpen && (
          <motion.div
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 280, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            className="border-r border-border bg-paper flex flex-col"
          >
            <div className="p-4 border-b border-border flex justify-between items-center">
              <div className="flex items-center gap-2">
                <svg className="h-5 w-5 text-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M11 12c.5 0 1-.5 1-1V5l-2 2-2-2v6c0 .5.5 1 1 1h2z" />
                  <path d="M18 12c.5 0 1-.5 1-1V5l-2 2-2-2v6c0 .5.5 1 1 1h2z" />
                  <path d="M12 21c-2.5 0-4.5-2-4.5-4.5 0-1.5 1-3 2.5-3.5h4c1.5.5 2.5 2 2.5 3.5 0 2.5-2 4.5-4.5 4.5z" />
                  <path d="M10 17h4" />
                </svg>
                <h2 className="text-xl font-serif">{t.sidebar.title}</h2>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setIsSidebarOpen(false)}>
                <PanelLeftClose className="h-4 w-4" />
              </Button>
            </div>

            {/* API 状态 */}
            <div className="px-4 py-2 border-b border-border">
              <div className={cn(
                "flex items-center gap-2 text-xs",
                apiStatus === 'ok' && "text-green-600",
                apiStatus === 'error' && "text-red-600",
                apiStatus === 'checking' && "text-yellow-600"
              )}>
                {apiStatus === 'ok' && <><CheckCircle2 className="h-3 w-3" /> {t.sidebar.apiConnected}</>}
                {apiStatus === 'error' && <><AlertCircle className="h-3 w-3" /> {t.sidebar.apiDisconnected}</>}
                {apiStatus === 'checking' && <><Loader2 className="h-3 w-3 animate-spin" /> {t.sidebar.apiChecking}</>}
              </div>
            </div>

            {/* 语言切换 */}
            <div className="px-4 py-2 border-b border-border">
              <div className="flex items-center gap-2 text-xs">
                <Globe className="h-3 w-3" />
                <button
                  onClick={() => setLanguage('zh')}
                  className={cn(
                    "px-2 py-1 rounded transition-colors",
                    language === 'zh' ? "bg-primary text-white" : "hover:bg-secondary"
                  )}
                >
                  中文
                </button>
                <button
                  onClick={() => setLanguage('en')}
                  className={cn(
                    "px-2 py-1 rounded transition-colors",
                    language === 'en' ? "bg-primary text-white" : "hover:bg-secondary"
                  )}
                >
                  EN
                </button>
              </div>
            </div>

            {/* 模型选择 */}
            <div className="px-4 py-2 border-b border-border">
              <div className="flex items-center gap-2 text-xs">
                <Cpu className="h-3 w-3" />
                <select
                  value={model}
                  onChange={(e) => setModel(e.target.value as ModelType)}
                  className="flex-1 text-xs bg-transparent border border-border rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-primary"
                >
                  <option value="deepseek-reasoner">DeepSeek R1</option>
                  <option value="deepseek-chat">DeepSeek V3</option>
                </select>
              </div>
              <p className="text-[10px] text-muted-foreground mt-1 ml-5">
                {model === 'deepseek-reasoner' ? t.settings.modelDesc.deepseek_reasoner : t.settings.modelDesc.deepseek_chat}
              </p>
            </div>

            {/* 搜索历史 */}
            <div className="px-4 py-2">
              <div className="relative">
                <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-3 w-3 text-muted-foreground" />
                <Input
                  placeholder={t.sidebar.searchPlaceholder}
                  className="pl-7 h-8 text-xs"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
            </div>

            <div className="p-4">
              <Button
                onClick={createNewSession}
                className="w-full justify-start gap-2 font-sans"
                variant="outline"
              >
                <Plus className="h-4 w-4" /> {t.sidebar.newChat}
              </Button>
            </div>

            <ScrollArea className="flex-1 px-2">
              <div className="space-y-1">
                {filteredSessions.length === 0 && searchQuery.trim() ? (
                  <p className="text-xs text-muted-foreground text-center py-4">{t.sidebar.noResults}</p>
                ) : filteredSessions.length === 0 ? (
                  <p className="text-xs text-muted-foreground text-center py-4">暂无会话</p>
                ) : (
                  filteredSessions.map(session => (
                    <div
                      key={session.id}
                      className={cn(
                        "group flex items-center gap-2 px-3 py-2 rounded-md cursor-pointer transition-colors",
                        currentSessionId === session.id ? "bg-secondary" : "hover:bg-secondary/50"
                      )}
                      onClick={() => setCurrentSessionId(session.id)}
                    >
                      <MessageSquare className="h-4 w-4 shrink-0 text-muted-foreground" />
                      <span className="flex-1 text-sm truncate font-sans min-w-0">
                        {session.title}
                      </span>
                      {session.status === 'running' && (
                        <Loader2 className="h-4 w-4 animate-spin text-primary shrink-0" />
                      )}
                      {/* 删除按钮 */}
                      <button
                        type="button"
                        onClick={(e) => deleteSession(session.id, e)}
                        className="shrink-0 p-1 rounded text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors"
                        aria-label="删除会话"
                        title="删除此会话"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  ))
                )}
              </div>
            </ScrollArea>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <main className="flex-1 flex flex-col relative bg-white">
        {/* Header */}
        <header className="h-14 border-b border-border flex items-center justify-between px-6 bg-white/80 backdrop-blur-sm sticky top-0 z-10">
          <div className="flex items-center gap-4">
            {!isSidebarOpen && (
              <Button variant="ghost" size="icon" onClick={() => setIsSidebarOpen(true)}>
                <PanelLeftOpen className="h-4 w-4" />
              </Button>
            )}
            <h1 className="text-lg font-serif">
              {currentSession?.title || t.main.defaultTitle}
            </h1>
          </div>

          <div className="flex items-center gap-2">
            {/* 从最后一个批次获取 outputFile */}
            {(() => {
              const lastBatch = currentSession?.batches?.[currentSession.batches.length - 1];
              return lastBatch?.outputFiles?.markdown ? (
                <>
                  <Button
                    variant="outline"
                    size="sm"
                    className="gap-2"
                    onClick={() => handlePreviewReport('markdown')}
                    title="预览 Markdown"
                  >
                    <BookOpen className="h-4 w-4" /> 预览
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="gap-2"
                    onClick={() => handleDownloadReport('markdown')}
                    title="下载 Markdown"
                  >
                    <Download className="h-4 w-4" /> MD
                  </Button>
                </>
              ) : null;
            })()}
            {(() => {
              const lastBatch = currentSession?.batches?.[currentSession.batches.length - 1];
              return lastBatch?.outputFiles?.html ? (
                <Button
                  variant="outline"
                  size="sm"
                  className="gap-2"
                  onClick={() => handleDownloadReport('html')}
                  title="下载 HTML"
                >
                  <FileText className="h-4 w-4" /> HTML
                </Button>
              ) : null;
            })()}
          </div>
        </header>

        {/* Progress Bar */}
        {currentSession?.status === 'running' && (
          <div className="px-6 py-2 bg-secondary/30 border-b border-border">
            <div className="flex items-center gap-3">
              <Loader2 className="h-4 w-4 animate-spin text-primary" />
              <span className="text-sm text-muted-foreground">{currentSession.currentStep}</span>
              <Progress value={currentSession.progress} className="flex-1 h-2" />
              <span className="text-sm font-mono">{currentSession.progress}%</span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => cancelResearch(currentSession.id)}
                className="text-destructive hover:text-destructive"
              >
                <X className="h-4 w-4 mr-1" /> {t.common.cancel}
              </Button>
            </div>
          </div>
        )}

        
        {/* Messages */}
        <div id="chat-messages" className="flex-1 overflow-y-auto p-6 md:p-12 scroll-smooth" ref={scrollRef}>
          <div className="max-w-3xl mx-auto space-y-6">
            {(() => {
              if (!currentSession) return null;

              const messages = currentSession.messages;
              const batches = currentSession.batches;

              // 判断是否显示欢迎消息（仅当会话刚创建时）
              const showWelcome = messages.length === 1 &&
                                  messages[0].role === 'assistant' &&
                                  currentSession.status === 'idle';

              // 获取用户消息（跳过可能的欢迎消息）
              const userMessages = messages.filter(msg => msg.role === 'user');

              // 当前批次是否正在运行
              const isRunning = currentSession.status === 'running';

              return (
                <>
                  {/* 1. 欢迎消息 */}
                  {showWelcome && messages[0] && (
                    <motion.div
                      key="welcome"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="flex flex-col gap-2 items-start"
                    >
                      <div className="max-w-[85%] px-6 py-4 shadow-sm bg-paper border border-border rounded-2xl rounded-tl-none">
                        <div className="prose prose-sm max-w-none dark:prose-invert prose-p:my-2 prose-headings:mt-4 prose-headings:mb-2">
                          <ReactMarkdown remarkPlugins={[remarkGfm]}>{messages[0].content}</ReactMarkdown>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <CopyButton text={messages[0].content} />
                        <span className="text-[10px] uppercase tracking-widest text-muted-foreground px-2">
                          {t.message.agent}
                        </span>
                      </div>
                    </motion.div>
                  )}

                  {/* 2. 遍历每个用户消息和对应批次 */}
                  {userMessages.map((msg, idx) => {
                    // 获取对应批次（使用索引关联）
                    const batch = batches[idx];
                    // 判断是否是最后一个批次
                    const isLastBatch = idx === batches.length - 1;
                    // 当前批次是否活跃（正在运行且是最后一个批次）
                    const isCurrentBatch = isLastBatch && isRunning;

                    // 获取该批次的工具状态
                    const searchTool = batch?.toolCalls?.find(t => t.tool === 'search');
                    const analyzeTool = batch?.toolCalls?.find(t => t.tool === 'analyze');
                    const reportTool = batch?.toolCalls?.find(t => t.tool === 'report');

                    // 找到这个用户消息后面对应的 assistant 响应
                    const msgIndex = messages.indexOf(msg);
                    const assistantMsg = messages
                      .slice(msgIndex + 1)
                      .find(m => m.role === 'assistant');

                    return (
                      <React.Fragment key={`batch-${idx}`}>
                        {/* 用户问题 */}
                        <motion.div
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="flex flex-col gap-2 items-end"
                        >
                          <div className="max-w-[85%] px-6 py-4 shadow-sm bg-ink text-white rounded-2xl rounded-tr-none font-sans">
                            <div className="whitespace-pre-wrap">{msg.content}</div>
                          </div>
                          <div className="flex items-center gap-2">
                            <CopyButton text={msg.content} className="text-white hover:text-white" />
                            <span className="text-[10px] uppercase tracking-widest text-muted-foreground px-2">
                              {t.message.user}
                            </span>
                          </div>
                        </motion.div>

                        {/* 批次的中间状态 - 仅当是当前活跃批次且有数据时显示 */}
                        {batch && isCurrentBatch && (
                          <>
                            {/* 任务DAG卡片 */}
                            {batch.taskPlan && (
                              <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="w-full"
                              >
                                <TaskDAGCard
                                  taskPlan={batch.taskPlan}
                                  taskStatuses={batch.taskStatuses || {}}
                                  contentType={batch.contentType}
                                />
                              </motion.div>
                            )}

                            {/* 任务列表卡片 */}
                            {batch.todos && batch.todos.length > 0 && !batch.taskPlan && (
                              <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="w-full"
                              >
                                <TodosCard
                                  todos={batch.todos}
                                  completedCount={
                                    !isRunning ? batch.todos.length :
                                    currentSession.progress >= 70 ? 4 :
                                    currentSession.progress >= 60 ? 3 :
                                    currentSession.progress >= 30 ? 2 :
                                    currentSession.progress >= 15 ? 1 : 0
                                  }
                                />
                              </motion.div>
                            )}

                            {/* 4. 搜索工具卡片 */}
                            {searchTool && (
                              <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="w-full"
                              >
                                <ToolCallCard data={searchTool} />
                              </motion.div>
                            )}

                            {/* 5. 搜索结果卡片 */}
                            {batch.searchResults && batch.searchResults.length > 0 && (
                              <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="w-full"
                              >
                                <SourcesCard
                                  sources={batch.searchResults.map(r => ({
                                    title: r.title,
                                    url: r.url,
                                    status: 'success' as const
                                  }))}
                                  title={t.message.searchResults}
                                  toolName="search"
                                  status="completed"
                                />
                              </motion.div>
                            )}

                            {/* 6. 分析工具卡片 */}
                            {analyzeTool && (
                              <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="w-full"
                              >
                                <ToolCallCard data={analyzeTool} />
                              </motion.div>
                            )}

                            {/* 7. 报告生成工具卡片 */}
                            {reportTool && (
                              <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="w-full"
                              >
                                <ToolCallCard data={reportTool} />
                              </motion.div>
                            )}

                            {/* 8. 流式输出内容 */}
                            {reportTool && (
                              <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="w-full"
                              >
                                <div className="bg-paper border border-border rounded-lg px-6 py-4 shadow-sm">
                                  <div className="flex items-center gap-2 mb-3 text-sm font-medium text-primary">
                                    <BookOpen className="h-4 w-4" />
                                    <span>{t.progress.writing}</span>
                                    <Loader2 className="h-3 w-3 animate-spin" />
                                  </div>
                                  {batch.streamingContent ? (
                                    <div>
                                      <div className="prose prose-sm max-w-none dark:prose-invert prose-p:my-2 prose-headings:mt-4 prose-headings:mb-2">
                                        <ReactMarkdown remarkPlugins={[remarkGfm]}>{batch.streamingContent}</ReactMarkdown>
                                        <span className="inline-block w-2 h-4 bg-primary animate-pulse"></span>
                                      </div>
                                      <div className="mt-3 pt-3 border-t border-border flex items-center gap-2">
                                        <CopyButton text={batch.streamingContent} />
                                        <span className="text-xs text-muted-foreground">实时生成中...</span>
                                      </div>
                                    </div>
                                  ) : (
                                    <div className="text-muted-foreground text-sm">
                                      正在准备报告内容，请稍候...
                                      <span className="inline-block w-2 h-4 bg-muted animate-pulse ml-1"></span>
                                    </div>
                                  )}
                                </div>
                              </motion.div>
                            )}
                          </>
                        )}

                        {/* 9. 已完成的批次 - 显示 assistant 响应 */}
                        {batch && !isRunning && isLastBatch && assistantMsg && (
                          <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="flex flex-col gap-2 items-start"
                          >
                            <div className="max-w-[85%] px-6 py-4 shadow-sm bg-paper border border-border rounded-2xl rounded-tl-none">
                              <div className="prose prose-sm max-w-none dark:prose-invert prose-p:my-2 prose-headings:mt-4 prose-headings:mb-2">
                                <ReactMarkdown remarkPlugins={[remarkGfm]}>{assistantMsg.content}</ReactMarkdown>
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              <CopyButton text={assistantMsg.content} />
                              <span className="text-[10px] uppercase tracking-widest text-muted-foreground px-2">
                                {t.message.agent}
                              </span>
                            </div>
                          </motion.div>
                        )}

                        {/* 10. 显示已完成的历史批次的 assistant 响应 */}
                        {batch && !isLastBatch && assistantMsg && (
                          <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="flex flex-col gap-2 items-start"
                          >
                            <div className="max-w-[85%] px-6 py-4 shadow-sm bg-paper border border-border rounded-2xl rounded-tl-none">
                              <div className="prose prose-sm max-w-none dark:prose-invert prose-p:my-2 prose-headings:mt-4 prose-headings:mb-2">
                                <ReactMarkdown remarkPlugins={[remarkGfm]}>{assistantMsg.content}</ReactMarkdown>
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              <CopyButton text={assistantMsg.content} />
                              <span className="text-[10px] uppercase tracking-widest text-muted-foreground px-2">
                                {t.message.agent}
                              </span>
                            </div>
                          </motion.div>
                        )}
                      </React.Fragment>
                    );
                  })}

                  {/* 11. 错误/取消状态显示 */}
                  {(currentSession.status === 'error' || currentSession.status === 'cancelled') && batches.length > 0 && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="flex flex-col gap-2 items-start"
                    >
                      <div className="max-w-[85%] px-6 py-4 shadow-sm bg-paper border border-border rounded-2xl rounded-tl-none">
                        <div className="prose prose-sm max-w-none dark:prose-invert prose-p:my-2 prose-headings:mt-4 prose-headings:mb-2">
                          <p>操作已取消或出错。请重试。</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] uppercase tracking-widest text-muted-foreground px-2">
                          {t.message.agent}
                        </span>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleRetry(currentSession.id)}
                          className="h-6 text-xs gap-1"
                        >
                          <RotateCcw className="h-3 w-3" /> {t.common.retry}
                        </Button>
                      </div>
                    </motion.div>
                  )}
                </>
              );
            })()}
          </div>
        </div>

        {/* Input */}
        <div className="p-6 md:p-12 max-w-3xl mx-auto w-full">
          <div className="relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-border/50 to-border/50 rounded-2xl blur opacity-25 group-hover:opacity-100 transition duration-1000 group-hover:duration-200"></div>
            <div className="relative flex items-center bg-white border border-border rounded-2xl shadow-lg focus-within:ring-1 focus-within:ring-primary/20 transition-all">
              <Input
                placeholder={t.input.placeholder}
                className="flex-1 border-0 focus-visible:ring-0 focus-visible:ring-offset-0 bg-transparent h-14 px-6 text-lg font-sans"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}
                disabled={currentSession?.status === 'running'}
              />
              <Button
                size="icon"
                className="mr-2 h-10 w-10 rounded-xl"
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || currentSession?.status === 'running' || apiStatus !== 'ok'}
              >
                {currentSession?.status === 'running' ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>
          <p className="text-center text-[10px] text-muted-foreground mt-4 uppercase tracking-[0.2em]">
            {t.input.tagline}
          </p>
        </div>
      </main>

      {/* 预览对话框 */}
      <Dialog open={previewOpen} onOpenChange={setPreviewOpen}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-hidden">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <BookOpen className="h-5 w-5" />
              报告预览
            </DialogTitle>
          </DialogHeader>
          <ScrollArea className="flex-1 h-[calc(80vh-100px)]">
            {previewFormat === 'markdown' ? (
              <div className="prose prose-sm max-w-none dark:prose-invert p-4">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{previewContent}</ReactMarkdown>
              </div>
            ) : (
              <div
                className="p-4"
                dangerouslySetInnerHTML={{ __html: previewContent }}
              />
            )}
          </ScrollArea>
          <div className="flex justify-end gap-2 pt-4 border-t">
            <Button
              variant="outline"
              onClick={() => setPreviewOpen(false)}
            >
              关闭
            </Button>
            <Button
              onClick={() => {
                handleDownloadReport(previewFormat);
                setPreviewOpen(false);
              }}
            >
              <Download className="h-4 w-4 mr-2" />
              下载
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ChatPage;