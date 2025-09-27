# services/openai_client.py
"""
OpenAI client configuration and management.
Provides a lazy-loaded OpenAI client that gracefully handles missing configurations.
"""
import logging
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
    
    # Check if OpenAI package is available
    if not _has_openai or OpenAIClient is None:
        logger.warning("OpenAI package not available - AI features disabled")
        return None
    
    # Check if API key is configured
    api_key = getattr(settings, 'OPENAI_API_KEY', None)
    if not api_key:
        logger.info("OpenAI API key not configured - AI features disabled")
        return None
    # Avoid initializing client when API key is a placeholder (common in example .env)
    if isinstance(api_key, str) and any(tag in api_key.upper() for tag in ("NEW_", "REPLACE", "YOUR")):
        logger.warning("OpenAI API key appears to be a placeholder; skipping client initialization")
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

# Added for education router compatibility
async def chat(messages, model="gpt-4o-mini", **kwargs):
    """
    Chat completion wrapper for education router
    Compatible with OpenAI API v1.0+
    """
    client = get_client()
    if not client:
        raise Exception("OpenAI client not configured - check OPENAI_API_KEY")

    try:
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI chat error: {e}")
        raise Exception(f"OpenAI chat failed: {str(e)}")
