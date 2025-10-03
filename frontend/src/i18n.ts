import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Only bundle English and Spanish - most common languages
// Other languages will lazy load on demand
import enTranslations from '../public/locales/en/translation.json';
import esTranslations from '../public/locales/es/translation.json';

// Define initial resources (en, es bundled)
const resources = {
  en: { translation: enTranslations },
  es: { translation: esTranslations },
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

    // Supported languages (en/es bundled, others lazy loaded)
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
      useSuspense: true, // Enable suspense so translations load before render
    },
  });

// Lazy load other languages on demand
const languageLoader: Record<string, () => Promise<any>> = {
  zh: () => import('../public/locales/zh/translation.json'),
  hi: () => import('../public/locales/hi/translation.json'),
  ar: () => import('../public/locales/ar/translation.json'),
  pt: () => import('../public/locales/pt/translation.json'),
  bn: () => import('../public/locales/bn/translation.json'),
  ru: () => import('../public/locales/ru/translation.json'),
  ja: () => import('../public/locales/ja/translation.json'),
  pa: () => import('../public/locales/pa/translation.json'),
  de: () => import('../public/locales/de/translation.json'),
  ko: () => import('../public/locales/ko/translation.json'),
  fr: () => import('../public/locales/fr/translation.json'),
  vi: () => import('../public/locales/vi/translation.json'),
  it: () => import('../public/locales/it/translation.json'),
  tl: () => import('../public/locales/tl/translation.json'),
};

// Load language on demand when user switches
i18n.on('languageChanged', async (lng) => {
  if (!i18n.hasResourceBundle(lng, 'translation') && languageLoader[lng]) {
    const translations = await languageLoader[lng]();
    i18n.addResourceBundle(lng, 'translation', translations.default || translations);
  }
});

export default i18n;
