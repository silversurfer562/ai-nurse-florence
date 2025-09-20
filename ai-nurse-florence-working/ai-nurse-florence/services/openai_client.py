# filepath: /Users/patrickroebuck/Documents/pycharm-projects/nurses_api/services/openai_client.py
import os
import re
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

_client = None

def _is_valid_api_key(api_key: str) -> bool:
    """
    Validate that the API key is not a placeholder or obviously invalid.
    
    Args:
        api_key: The API key to validate
        
    Returns:
        True if the key appears to be valid, False otherwise
    """
    if not api_key:
        return False
    
    # Check for common placeholder patterns
    placeholder_patterns = [
        r"your[_-]?api[_-]?key",
        r"your[_-]?openai[_-]?key", 
        r"sk-NEW_Y",  # The specific placeholder from the error
        r"\*+",  # Keys with asterisks
        r"here",  # Keys ending with "here"
        r"placeholder",
        r"example",
        r"test[_-]?key",
        r"dummy",
        r"fake"
    ]
    
    api_key_lower = api_key.lower()
    for pattern in placeholder_patterns:
        if re.search(pattern, api_key_lower):
            return False
    
    # OpenAI API keys should start with "sk-" and be reasonably long
    if not api_key.startswith("sk-"):
        return False
    
    # Real OpenAI keys are typically 51 characters long
    if len(api_key) < 20:  # Allow some flexibility but catch obvious fakes
        return False
    
    return True

def get_client():
    """
    Return a configured OpenAI client or None.
    Lazy-imports the OpenAI package so the app can run even when the package
    is not installed. Caller should raise or handle the None case.
    """
    global _client
    if _client is not None:
        return _client
    if not OPENAI_API_KEY:
        return None
    
    # Validate the API key before attempting to use it
    if not _is_valid_api_key(OPENAI_API_KEY):
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(
            f"Invalid or placeholder OpenAI API key detected: {OPENAI_API_KEY[:10]}..."
            + " Please set a valid OPENAI_API_KEY environment variable."
        )
        return None
    
    try:
        from openai import OpenAI as OpenAIClient
    except Exception:
        return None
    try:
        _client = OpenAIClient(api_key=OPENAI_API_KEY)
    except Exception:
        _client = None
    return _client
