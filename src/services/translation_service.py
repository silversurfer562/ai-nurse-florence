"""
Translation Service for AI Nurse Florence
Provides multi-language support with fallback strategies.

Supports: English, Spanish, French, German, Italian, Portuguese, Chinese (Simplified)
"""

import logging
from typing import Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class SupportedLanguage(str, Enum):
    """Supported languages for translation."""
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    CHINESE_SIMPLIFIED = "zh-CN"
    CHINESE_TRADITIONAL = "zh-TW"


# Language metadata
LANGUAGE_INFO = {
    "en": {"name": "English", "native": "English", "flag": "🇬🇧"},
    "es": {"name": "Spanish", "native": "Español", "flag": "🇪🇸"},
    "fr": {"name": "French", "native": "Français", "flag": "🇫🇷"},
    "de": {"name": "German", "native": "Deutsch", "flag": "🇩🇪"},
    "it": {"name": "Italian", "native": "Italiano", "flag": "🇮🇹"},
    "pt": {"name": "Portuguese", "native": "Português", "flag": "🇵🇹"},
    "zh-CN": {"name": "Chinese (Simplified)", "native": "简体中文", "flag": "🇨🇳"},
    "zh-TW": {"name": "Chinese (Traditional)", "native": "繁體中文", "flag": "🇹🇼"},
}


class TranslationService:
    """
    Translation service with multiple backend support.

    Supports:
    1. DeepL API (best quality, requires API key)
    2. Google Translate API (good quality, requires API key)
    3. googletrans (free fallback, no API key needed)
    """

    def __init__(self):
        """Initialize translation service with fallback strategy."""
        self.deepl_client = None
        self.google_client = None
        self.free_translator = None

        # Try to initialize translation backends
        self._init_deepl()
        self._init_google()
        self._init_free()

    def _init_deepl(self):
        """Initialize DeepL translator if API key is available."""
        try:
            import os
            deepl_key = os.getenv("DEEPL_API_KEY")
            if deepl_key:
                import deepl
                self.deepl_client = deepl.Translator(deepl_key)
                logger.info("✅ DeepL translator initialized")
        except ImportError:
            logger.debug("DeepL library not installed (pip install deepl)")
        except Exception as e:
            logger.debug(f"DeepL initialization failed: {e}")

    def _init_google(self):
        """Initialize Google Translate if credentials are available."""
        try:
            import os
            google_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if google_creds:
                from google.cloud import translate_v2 as translate
                self.google_client = translate.Client()
                logger.info("✅ Google Translate initialized")
        except ImportError:
            logger.debug("Google Translate library not installed")
        except Exception as e:
            logger.debug(f"Google Translate initialization failed: {e}")

    def _init_free(self):
        """Initialize free translation fallback."""
        # googletrans has dependency conflicts with OpenAI library
        # Skipping free translator initialization
        # Translation will rely on DeepL or Google Translate API with API keys
        logger.info("⚠️ Free translation not available (requires API key for DeepL or Google)")
        self.free_translator = None

    async def translate(
        self,
        text: str,
        target_language: str,
        source_language: str = "en",
        context: str = "medical"
    ) -> Dict[str, Any]:
        """
        Translate text to target language.

        Args:
            text: Text to translate
            target_language: Target language code (e.g., 'es', 'zh-CN')
            source_language: Source language code (default: 'en')
            context: Context for translation (e.g., 'medical', 'clinical')

        Returns:
            Dict with translated_text, detected_language, method, success
        """
        # Normalize language codes
        target_language = self._normalize_language_code(target_language)
        source_language = self._normalize_language_code(source_language)

        # If target is same as source, no translation needed
        if target_language == source_language or target_language == "en":
            return {
                "translated_text": text,
                "detected_language": source_language,
                "target_language": target_language,
                "method": "no_translation_needed",
                "success": True
            }

        # Try translation methods in order of quality
        methods = [
            ("deepl", self._translate_with_deepl),
            ("google", self._translate_with_google),
        ]

        for method_name, method_func in methods:
            try:
                result = await method_func(text, target_language, source_language)
                if result:
                    return {
                        "translated_text": result,
                        "detected_language": source_language,
                        "target_language": target_language,
                        "method": method_name,
                        "success": True
                    }
            except Exception as e:
                logger.debug(f"{method_name} translation failed: {e}")
                continue

        # All methods failed, return original text with note
        logger.warning(f"Translation unavailable for {source_language} -> {target_language}")
        logger.warning("To enable translation, set DEEPL_API_KEY or GOOGLE_APPLICATION_CREDENTIALS")
        return {
            "translated_text": text,
            "detected_language": source_language,
            "target_language": target_language,
            "method": "none",
            "success": False,
            "error": "Translation requires API key (DeepL or Google Translate)"
        }

    async def _translate_with_deepl(
        self, text: str, target: str, source: str
    ) -> Optional[str]:
        """Translate using DeepL API."""
        if not self.deepl_client:
            return None

        # DeepL uses different language codes
        target_deepl = self._to_deepl_code(target)
        source_deepl = self._to_deepl_code(source)

        result = self.deepl_client.translate_text(
            text,
            target_lang=target_deepl,
            source_lang=source_deepl
        )
        return result.text

    async def _translate_with_google(
        self, text: str, target: str, source: str
    ) -> Optional[str]:
        """Translate using Google Translate API."""
        if not self.google_client:
            return None

        result = self.google_client.translate(
            text,
            target_language=target,
            source_language=source
        )
        return result["translatedText"]


    def _normalize_language_code(self, code: str) -> str:
        """Normalize language code to standard format."""
        code = code.lower().strip()

        # Handle common variations
        code_map = {
            "zh": "zh-CN",  # Default Chinese to Simplified
            "zh-cn": "zh-CN",
            "zh-tw": "zh-TW",
            "pt": "pt",
            "pt-br": "pt",
            "en": "en",
            "en-us": "en",
            "en-gb": "en",
        }

        return code_map.get(code, code)

    def _to_deepl_code(self, code: str) -> str:
        """Convert language code to DeepL format."""
        deepl_map = {
            "en": "EN",
            "es": "ES",
            "fr": "FR",
            "de": "DE",
            "it": "IT",
            "pt": "PT",
            "zh-CN": "ZH",
            "zh-TW": "ZH",
        }
        return deepl_map.get(code, code.upper())

    def get_supported_languages(self) -> Dict[str, Dict[str, str]]:
        """Get list of supported languages with metadata."""
        return LANGUAGE_INFO

    def is_language_supported(self, language_code: str) -> bool:
        """Check if a language is supported."""
        normalized = self._normalize_language_code(language_code)
        return normalized in LANGUAGE_INFO


# Global translation service instance
_translation_service: Optional[TranslationService] = None


def get_translation_service() -> TranslationService:
    """Get or create the global translation service instance."""
    global _translation_service
    if _translation_service is None:
        _translation_service = TranslationService()
    return _translation_service


async def translate_text(
    text: str,
    target_language: str,
    source_language: str = "en",
    context: str = "medical"
) -> Dict[str, Any]:
    """
    Convenience function to translate text.

    Args:
        text: Text to translate
        target_language: Target language code
        source_language: Source language code (default: 'en')
        context: Context for translation (default: 'medical')

    Returns:
        Translation result dictionary
    """
    service = get_translation_service()
    return await service.translate(text, target_language, source_language, context)
