import React, { createContext, useContext, useState, useCallback } from 'react';

export type ModelType = 'deepseek-reasoner' | 'deepseek-chat';

interface SettingsContextType {
  model: ModelType;
  setModel: (model: ModelType) => void;
}

const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

const MODEL_STORAGE_KEY = 'deepfind-model';

export const SettingsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [model, setModelState] = useState<ModelType>(() => {
    // 从 localStorage 恢复模型设置
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem(MODEL_STORAGE_KEY);
      if (saved === 'deepseek-reasoner' || saved === 'deepseek-chat') {
        return saved;
      }
    }
    return 'deepseek-reasoner'; // 默认使用 R1
  });

  const setModel = useCallback((newModel: ModelType) => {
    setModelState(newModel);
    localStorage.setItem(MODEL_STORAGE_KEY, newModel);
  }, []);

  return (
    <SettingsContext.Provider value={{ model, setModel }}>
      {children}
    </SettingsContext.Provider>
  );
};

export const useSettings = (): SettingsContextType => {
  const context = useContext(SettingsContext);
  if (!context) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return context;
};