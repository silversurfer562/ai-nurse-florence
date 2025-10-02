import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import HttpBackend from 'i18next-http-backend';

i18n
  // Load translation files from public folder
  .use(HttpBackend)
  // Detect user language
  .use(LanguageDetector)
  // Pass the i18n instance to react-i18next
  .use(initReactI18next)
  // Initialize i18next
  .init({
    fallbackLng: 'en',
    debug: false,

    // Supported languages
    supportedLngs: [
      'en', // English
      'es', // Spanish
      'zh', // Chinese (Mandarin)
      'hi', // Hindi
      'ar', // Arabic
      'pt', // Portuguese
      'bn', // Bengali
      'ru', // Russian
      'ja', // Japanese
      'pa', // Punjabi
      'de', // German
      'ko', // Korean
      'fr', // French
      'vi', // Vietnamese
      'it', // Italian
      'tl', // Tagalog
    ],

    interpolation: {
      escapeValue: false, // React already escapes values
    },

    backend: {
      loadPath: '/locales/{{lng}}/translation.json',
    },

    detection: {
      // Order of language detection
      order: ['localStorage', 'navigator', 'htmlTag'],
      // Cache user language selection
      caches: ['localStorage'],
      lookupLocalStorage: 'i18nextLng',
    },

    react: {
      useSuspense: true,
    },
  });

export default i18n;
