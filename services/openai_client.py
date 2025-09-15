# filepath: /Users/patrickroebuck/Documents/pycharm-projects/nurses_api/services/openai_client.py
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

_client = None

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
    try:
        from openai import OpenAI as OpenAIClient
    except Exception:
        return None
    try:
        _client = OpenAIClient(api_key=OPENAI_API_KEY)
    except Exception:
        _client = None
    return _client
