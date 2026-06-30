import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { Language, Translations, getTranslations } from '@/i18n';

interface LanguageContextType {
  language: Language;
  t: Translations;
  setLanguage: (lang: Language) => void;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

const LANGUAGE_STORAGE_KEY = 'deepfind-language';

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<Language>(() => {
    // 从 localStorage 恢复语言设置
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem(LANGUAGE_STORAGE_KEY);
      if (saved === 'zh' || saved === 'en') {
        return saved;
      }
      // 根据浏览器语言自动选择
      const browserLang = navigator.language.toLowerCase();
      if (browserLang.startsWith('zh')) {
        return 'zh';
      }
    }
    return 'en';
  });

  const setLanguage = useCallback((lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem(LANGUAGE_STORAGE_KEY, lang);
  }, []);

  const t = getTranslations(language);

  return (
    <LanguageContext.Provider value={{ language, t, setLanguage }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = (): LanguageContextType => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};