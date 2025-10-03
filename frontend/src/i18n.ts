import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Import translations directly (bundled approach - more reliable than HTTP)
import enTranslations from '../public/locales/en/translation.json';
import esTranslations from '../public/locales/es/translation.json';
import zhTranslations from '../public/locales/zh/translation.json';
import hiTranslations from '../public/locales/hi/translation.json';
import arTranslations from '../public/locales/ar/translation.json';
import ptTranslations from '../public/locales/pt/translation.json';
import bnTranslations from '../public/locales/bn/translation.json';
import ruTranslations from '../public/locales/ru/translation.json';
import jaTranslations from '../public/locales/ja/translation.json';
import paTranslations from '../public/locales/pa/translation.json';
import deTranslations from '../public/locales/de/translation.json';
import koTranslations from '../public/locales/ko/translation.json';
import frTranslations from '../public/locales/fr/translation.json';
import viTranslations from '../public/locales/vi/translation.json';
import itTranslations from '../public/locales/it/translation.json';
import tlTranslations from '../public/locales/tl/translation.json';

// Define resources
const resources = {
  en: { translation: enTranslations },
  es: { translation: esTranslations },
  zh: { translation: zhTranslations },
  hi: { translation: hiTranslations },
  ar: { translation: arTranslations },
  pt: { translation: ptTranslations },
  bn: { translation: bnTranslations },
  ru: { translation: ruTranslations },
  ja: { translation: jaTranslations },
  pa: { translation: paTranslations },
  de: { translation: deTranslations },
  ko: { translation: koTranslations },
  fr: { translation: frTranslations },
  vi: { translation: viTranslations },
  it: { translation: itTranslations },
  tl: { translation: tlTranslations },
};

i18n
  // Detect user language
  .use(LanguageDetector)
  // Pass the i18n instance to react-i18next
  .use(initReactI18next)
  // Initialize i18next
  .init({
    resources,
    fallbackLng: 'en',
    debug: false,

    // Supported languages
    supportedLngs: [
      'en', 'es', 'zh', 'hi', 'ar', 'pt', 'bn', 'ru',
      'ja', 'pa', 'de', 'ko', 'fr', 'vi', 'it', 'tl',
    ],

    interpolation: {
      escapeValue: false, // React already escapes values
    },

    detection: {
      // Order of language detection
      order: ['localStorage', 'navigator', 'htmlTag'],
      // Cache user language selection
      caches: ['localStorage'],
      lookupLocalStorage: 'i18nextLng',
    },

    react: {
      useSuspense: false, // Changed to false to avoid suspense issues
    },
  });

export default i18n;
