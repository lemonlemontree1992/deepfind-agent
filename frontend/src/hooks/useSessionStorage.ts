import { useState, useEffect, useCallback } from 'react';

const SESSION_STORAGE_KEY = 'deepfind-sessions';
const MAX_SESSIONS = 20; // 最大保存会话数
const STORAGE_QUOTA_WARNING = 0.8; // 存储空间使用警告阈值

// 工具调用状态
interface ToolCall {
  tool: string;
  status: 'running' | 'completed' | 'error';
  input?: string;
  output?: string;
  message?: string;
  urls?: Array<{ url: string; title: string; status: string }>;
}

// 每个问题批次的中间状态
interface MessageBatch {
  toolCalls: ToolCall[];
  searchResults: Array<{ title: string; url: string }>;
  todos: string[];
  streamingContent: string;
  outputFiles?: Record<string, string>;
}

interface SessionData {
  id: string;
  title: string;
  messages: Array<{ role: 'user' | 'assistant'; content: string }>;
  timestamp: number;
  status: 'idle' | 'running' | 'completed' | 'error' | 'cancelled';
  progress: number;
  currentStep: string;
  lastQuery?: string;
  batches: MessageBatch[]; // 每个问题的中间状态，索引与用户消息索引对应
}

/**
 * 检查 localStorage 存储空间使用情况
 */
function checkStorageQuota(): { used: number; available: boolean } {
  try {
    let totalSize = 0;
    for (const key in localStorage) {
      if (localStorage.hasOwnProperty(key)) {
        totalSize += localStorage.getItem(key)?.length || 0;
      }
    }
    // localStorage 通常限制为 5MB
    const quotaMB = 5;
    const usedMB = totalSize / (1024 * 1024);
    return {
      used: usedMB,
      available: usedMB < quotaMB * STORAGE_QUOTA_WARNING
    };
  } catch {
    return { used: 0, available: true };
  }
}

/**
 * 自定义 Hook：会话持久化
 *
 * 功能：
 * - 自动保存会话到 localStorage
 * - 页面加载时恢复会话
 * - 限制最大存储数量
 * - 异常处理和存储空间检查
 */
export function useSessionStorage<T extends SessionData>(
  initialValue: T[]
): [T[], (value: T[] | ((prev: T[]) => T[])) => void, () => void] {
  // 从 localStorage 初始化
  const [sessions, setSessionsState] = useState<T[]>(() => {
    if (typeof window === 'undefined') {
      return initialValue;
    }
    try {
      const saved = localStorage.getItem(SESSION_STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        // 验证数据格式
        if (Array.isArray(parsed)) {
          // 恢复有效会话，将 running 状态改为 interrupted（保留数据）
          const validSessions = parsed
            .filter((s: T) => s.id && s.messages)
            .map((s: T) => {
              // 数据迁移：确保 batches 字段存在
              // 兼容旧格式：如果没有 batches 字段，从旧字段迁移数据
              if (!s.batches) {
                return {
                  ...s,
                  // 删除旧的字段
                  todos: undefined,
                  searchResults: undefined,
                  outputFiles: undefined,
                  toolCalls: undefined,
                  streamingContent: undefined,
                  batches: [],
                } as T;
              }
              return {
                ...s,
                // 如果是运行中状态，标记为已中断（保留已收集的数据）
                status: s.status === 'running' ? 'error' as const : s.status,
                currentStep: s.status === 'running' ? '会话已中断' : s.currentStep,
              };
            });
          return validSessions as T[];
        }
      }
    } catch (error) {
      console.error('Failed to load sessions from storage:', error);
      // 如果解析失败，清除损坏的数据
      try {
        localStorage.removeItem(SESSION_STORAGE_KEY);
      } catch {
        // 忽略清除错误
      }
    }
    return initialValue;
  });

  // 保存到 localStorage（带异常处理）
  const saveToStorage = useCallback((data: T[]) => {
    try {
      // 检查存储空间
      const quota = checkStorageQuota();
      if (!quota.available) {
        console.warn('localStorage storage quota warning: using', quota.used.toFixed(2), 'MB');
      }

      // 只保存有效的会话，限制数量
      const validSessions = data
        .filter(s => s.messages && s.messages.length > 0 && s.id)
        .slice(0, MAX_SESSIONS);

      const serialized = JSON.stringify(validSessions);
      localStorage.setItem(SESSION_STORAGE_KEY, serialized);
    } catch (error) {
      if (error instanceof DOMException && error.name === 'QuotaExceededError') {
        console.error('localStorage quota exceeded, clearing old sessions');
        // 存储空间不足时，清除一半的旧会话
        try {
          const halfSessions = data.slice(0, Math.ceil(data.length / 2));
          localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(halfSessions));
        } catch {
          console.error('Failed to recover from quota exceeded');
        }
      } else {
        console.error('Failed to save sessions to storage:', error);
      }
    }
  }, []);

  // 包装 setSessions，自动保存
  const setSessions = useCallback(
    (value: T[] | ((prev: T[]) => T[])) => {
      setSessionsState(prev => {
        const newValue = typeof value === 'function' ? value(prev) : value;
        saveToStorage(newValue);
        return newValue;
      });
    },
    [saveToStorage]
  );

  // 清除所有会话
  const clearSessions = useCallback(() => {
    try {
      localStorage.removeItem(SESSION_STORAGE_KEY);
    } catch (error) {
      console.error('Failed to clear sessions from storage:', error);
    }
    setSessionsState([]);
  }, []);

  // 监听其他标签页的变化（带验证）
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === SESSION_STORAGE_KEY && e.newValue) {
        try {
          const newSessions = JSON.parse(e.newValue);
          // 验证数据格式
          if (Array.isArray(newSessions)) {
            const validSessions = newSessions.filter((s: T) => s.id && s.messages);
            setSessionsState(validSessions as T[]);
          }
        } catch (error) {
          console.error('Failed to sync sessions from storage:', error);
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  return [sessions, setSessions, clearSessions];
}