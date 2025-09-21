# services/openai_client.py
"""
OpenAI client configuration and management.
Provides a lazy-loaded OpenAI client that gracefully handles missing configurations.
"""
import logging
import os
from typing import Optional, Any, TYPE_CHECKING

# Conditional imports - graceful degradation pattern
try:
    from openai import OpenAI as OpenAIClient
    _has_openai = True
except ImportError:
    _has_openai = False
    OpenAIClient = None

if TYPE_CHECKING and not _has_openai:
    from openai import OpenAI as OpenAIClient

try:
    from utils.config import settings
    _has_config = True
except ImportError:
    # Fallback for environments where config is not available
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    class _FallbackSettings:
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
    
    settings = _FallbackSettings()
    _has_config = False

logger = logging.getLogger(__name__)

# Global client instance (lazy-loaded)
_client: Optional[Any] = None
_client_initialized = False

def get_client() -> Optional[Any]:
    """
    Return a configured OpenAI client or None.
    
    Uses lazy initialization to avoid import errors when OpenAI package
    is not installed. Returns None if:
    - OpenAI package is not available
    - API key is not configured
    - Client initialization fails
    
    Returns:
        Configured OpenAI client or None
    """
    global _client, _client_initialized
    
    # Return cached client if already initialized
    if _client_initialized:
        return _client
    
    # Mark as initialized to avoid re-attempting
    _client_initialized = True

    # No automatic pytest detection here; tests should mock services.openai_client.get_client
    # when they need to control the client. Returning None here only when config absent.
    
    # Check if OpenAI package is available
    if not _has_openai or OpenAIClient is None:
        logger.warning("OpenAI package not available - AI features disabled")
        return None
    
    # Check if API key is configured
    api_key = getattr(settings, 'OPENAI_API_KEY', None)
    
    # Common placeholder values that should be treated as "not configured"
    placeholders = {
        'your-openai-api-key-here',
        'sk-placeholder',
        'sk-NEW_YOUR_KEY_HERE',
        'change-me',
        'your-key-here',
        'set-your-key-here'
    }
    
    if not api_key or api_key.strip() in placeholders:
        logger.info("OpenAI API key not configured - AI features disabled")
        return None
    
    # Initialize client
    try:
        _client = OpenAIClient(api_key=api_key)
        logger.info("OpenAI client initialized successfully")
        return _client
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {e}")
        _client = None
        return None

def is_available() -> bool:
    """
    Check if OpenAI client is available and properly configured.
    
    Returns:
        True if client is available, False otherwise
    """
    return get_client() is not None

def reset_client() -> None:
    """
    Reset the client instance (useful for testing).
    """
    global _client, _client_initialized
    _client = None
    _client_initialized = False
