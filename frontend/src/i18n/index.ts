import { zh } from './zh';
import { en } from './en';

export type Language = 'zh' | 'en';
export type Translations = typeof zh;

export const translations: Record<Language, Translations> = {
  zh,
  en,
};

export const getTranslations = (lang: Language): Translations => {
  return translations[lang] || translations.zh;
};

export { zh, en };