import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';

/**
 * Hook for managing document generation language preference
 *
 * Separate from UI language (i18n) - this controls the language
 * for generated patient documents (education materials, discharge instructions, etc.)
 *
 * Defaults to user's detected browser language
 */

const STORAGE_KEY = 'documentLanguage';

export function useDocumentLanguage() {
  const { i18n } = useTranslation();

  // Initialize with stored preference or fallback to UI language
  const [documentLanguage, setDocumentLanguageState] = useState<string>(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored || i18n.language || 'en';
  });

  // Sync with localStorage
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, documentLanguage);
  }, [documentLanguage]);

  const setDocumentLanguage = (language: string) => {
    setDocumentLanguageState(language);
  };

  const resetToUILanguage = () => {
    setDocumentLanguageState(i18n.language);
  };

  const clearDocumentLanguage = () => {
    localStorage.removeItem(STORAGE_KEY);
    setDocumentLanguageState(i18n.language);
  };

  return {
    documentLanguage,
    setDocumentLanguage,
    resetToUILanguage,
    clearDocumentLanguage,
  };
}
