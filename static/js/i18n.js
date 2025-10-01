/**
 * AI Nurse Florence - Internationalization (i18n) Utility
 * Provides multi-language support for the frontend
 */

class I18n {
    constructor() {
        this.currentLanguage = 'en';
        this.translations = {};
        this.fallbackLanguage = 'en';
        this.supportedLanguages = {
            'en': { name: 'English', native: 'English', flag: '🇬🇧' },
            'es': { name: 'Spanish', native: 'Español', flag: '🇪🇸' },
            'fr': { name: 'French', native: 'Français', flag: '🇫🇷' },
            'de': { name: 'German', native: 'Deutsch', flag: '🇩🇪' },
            'it': { name: 'Italian', native: 'Italiano', flag: '🇮🇹' },
            'pt': { name: 'Portuguese', native: 'Português', flag: '🇵🇹' },
            'zh-CN': { name: 'Chinese (Simplified)', native: '简体中文', flag: '🇨🇳' }
        };
    }

    /**
     * Initialize i18n with language preference
     */
    async init(language = null) {
        // Load language from: parameter > localStorage > browser > default
        this.currentLanguage = language ||
                               localStorage.getItem('florence_language') ||
                               this.detectBrowserLanguage() ||
                               'en';

        await this.loadTranslations(this.currentLanguage);

        // Also load fallback language if different
        if (this.currentLanguage !== this.fallbackLanguage) {
            await this.loadTranslations(this.fallbackLanguage);
        }

        // Update HTML lang attribute
        document.documentElement.lang = this.currentLanguage;

        return this.currentLanguage;
    }

    /**
     * Load translations for a specific language
     */
    async loadTranslations(lang) {
        if (this.translations[lang]) {
            return this.translations[lang];
        }

        try {
            const response = await fetch(`/static/translations/${lang}.json`);
            if (response.ok) {
                this.translations[lang] = await response.json();
                return this.translations[lang];
            } else {
                console.warn(`Translation file not found for language: ${lang}`);
                return null;
            }
        } catch (error) {
            console.error(`Failed to load translations for ${lang}:`, error);
            return null;
        }
    }

    /**
     * Get translated text for a key
     * @param {string} key - Dot notation key (e.g., 'common.loading')
     * @param {object} params - Optional parameters for string interpolation
     */
    t(key, params = {}) {
        const keys = key.split('.');
        let value = this.translations[this.currentLanguage];

        // Try to find in current language
        for (const k of keys) {
            if (value && typeof value === 'object') {
                value = value[k];
            } else {
                value = undefined;
                break;
            }
        }

        // Fallback to default language if not found
        if (value === undefined && this.currentLanguage !== this.fallbackLanguage) {
            value = this.translations[this.fallbackLanguage];
            for (const k of keys) {
                if (value && typeof value === 'object') {
                    value = value[k];
                } else {
                    value = undefined;
                    break;
                }
            }
        }

        // If still not found, return the key itself
        if (value === undefined) {
            console.warn(`Translation missing for key: ${key}`);
            return key;
        }

        // Interpolate parameters
        if (typeof value === 'string' && Object.keys(params).length > 0) {
            return value.replace(/\{(\w+)\}/g, (match, param) => {
                return params[param] !== undefined ? params[param] : match;
            });
        }

        return value;
    }

    /**
     * Change the current language
     */
    async changeLanguage(lang) {
        if (!this.supportedLanguages[lang]) {
            console.error(`Unsupported language: ${lang}`);
            return false;
        }

        await this.loadTranslations(lang);
        this.currentLanguage = lang;
        localStorage.setItem('florence_language', lang);
        document.documentElement.lang = lang;

        // Emit custom event for other components to react
        window.dispatchEvent(new CustomEvent('languageChanged', {
            detail: { language: lang }
        }));

        return true;
    }

    /**
     * Get current language
     */
    getCurrentLanguage() {
        return this.currentLanguage;
    }

    /**
     * Get list of supported languages
     */
    getSupportedLanguages() {
        return this.supportedLanguages;
    }

    /**
     * Detect browser language
     */
    detectBrowserLanguage() {
        const browserLang = navigator.language || navigator.userLanguage;

        // Try exact match first
        if (this.supportedLanguages[browserLang]) {
            return browserLang;
        }

        // Try language code only (e.g., 'en' from 'en-US')
        const langCode = browserLang.split('-')[0];
        if (this.supportedLanguages[langCode]) {
            return langCode;
        }

        // Check if browser language is Chinese
        if (langCode === 'zh') {
            // Default to Simplified Chinese
            return 'zh-CN';
        }

        return null;
    }

    /**
     * Translate all elements with data-i18n attribute
     */
    translatePage() {
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            const translation = this.t(key);

            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                element.placeholder = translation;
            } else {
                element.textContent = translation;
            }
        });

        document.querySelectorAll('[data-i18n-title]').forEach(element => {
            const key = element.getAttribute('data-i18n-title');
            element.title = this.t(key);
        });

        document.querySelectorAll('[data-i18n-aria-label]').forEach(element => {
            const key = element.getAttribute('data-i18n-aria-label');
            element.setAttribute('aria-label', this.t(key));
        });
    }
}

// Create global instance
window.i18n = new I18n();

// Auto-initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.i18n.init().then(() => {
            window.i18n.translatePage();
        });
    });
} else {
    window.i18n.init().then(() => {
        window.i18n.translatePage();
    });
}
