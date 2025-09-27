"""
OpenAI client with conditional loading
Following AI Nurse Florence integration patterns
"""

import logging
from typing import Optional, Dict, Any, List
import asyncio

# Conditional OpenAI import - graceful degradation
try:
    from openai import AsyncOpenAI
    _openai_available = True
except ImportError:
    _openai_available = False
    AsyncOpenAI = None

from ..utils.config import get_openai_config, is_feature_enabled
from ..utils.exceptions import ExternalServiceException

# Global client instance
_openai_client: Optional[AsyncOpenAI] = None

async def get_openai_client() -> Optional[AsyncOpenAI]:
    """Get OpenAI client with graceful fallback"""
    global _openai_client
    
    if not _openai_available:
        logging.warning("OpenAI library not available - install with: pip install openai")
        return None
    
    if not is_feature_enabled('openai'):
        logging.info("OpenAI not configured - clinical AI features disabled")
        return None
    
    if _openai_client is None:
        openai_config = get_openai_config()
        if not openai_config:
            return None
        
        try:
            _openai_client = AsyncOpenAI(
                api_key=openai_config["api_key"],
                timeout=30.0,
                max_retries=2
            )
            logging.info("OpenAI client initialized successfully")
        except Exception as e:
            logging.error(f"OpenAI client initialization failed: {e}")
            return None
    
    return _openai_client

async def chat_completion(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    **kwargs
) -> Optional[str]:
    """
    Chat completion with clinical context
    Returns None if OpenAI unavailable (graceful degradation)
    """
    client = await get_openai_client()
    if not client:
        return None
    
    try:
        # Get default config
        openai_config = get_openai_config()
        if not openai_config:
            return None
        
        # Use provided parameters or defaults
        model = model or openai_config["model"]
        temperature = temperature if temperature is not None else openai_config["temperature"]
        max_tokens = max_tokens or openai_config["max_tokens"]
        
        # Add clinical safety context to system message
        if messages and messages[0].get("role") == "system":
            messages[0]["content"] += "\n\nIMPORTANT: This is for educational purposes only. Always emphasize clinical judgment and evidence-based practice."
        else:
            messages.insert(0, {
                "role": "system",
                "content": "You are an AI assistant providing educational healthcare information. Always emphasize that this is for educational purposes only and clinical judgment is required."
            })
        
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logging.error(f"OpenAI chat completion failed: {e}")
        raise ExternalServiceException("OpenAI", str(e), e)

async def clinical_decision_support(
    patient_condition: str,
    severity: str = "moderate",
    care_setting: str = "med-surg",
    additional_context: Optional[str] = None
) -> Optional[str]:
    """
    Generate clinical decision support content
    Returns None if OpenAI unavailable
    """
    client = await get_openai_client()
    if not client:
        return None
    
    # Construct clinical prompt
    prompt = f"""
As a nursing education expert, provide evidence-based nursing interventions for:

Patient Condition: {patient_condition}
Severity: {severity}
Care Setting: {care_setting}
{f"Additional Context: {additional_context}" if additional_context else ""}

Please provide:
1. Primary nursing interventions (3-5 evidence-based interventions)
2. Monitoring parameters
3. Patient education points
4. Safety considerations

Format as structured text with clear headings. Include evidence levels where possible.
Remember: This is educational content for nursing professionals.
"""

    messages = [
        {
            "role": "system",
            "content": "You are a nursing education expert providing evidence-based clinical guidance. Always emphasize clinical judgment and evidence-based practice."
        },
        {
            "role": "user", 
            "content": prompt
        }
    ]
    
    return await chat_completion(messages, temperature=0.1)

async def generate_sbar_report(
    situation: str,
    background: str, 
    assessment: str,
    recommendation: str
) -> Optional[str]:
    """
    Generate formatted SBAR report
    Returns None if OpenAI unavailable
    """
    client = await get_openai_client()
    if not client:
        return None
    
    prompt = f"""
Format the following information into a professional SBAR report:

SITUATION: {situation}
BACKGROUND: {background}  
ASSESSMENT: {assessment}
RECOMMENDATION: {recommendation}

Please format this as a clear, professional SBAR report suitable for healthcare communication.
Include appropriate clinical terminology and ensure clarity for handoff communication.
"""

    messages = [
        {
            "role": "system",
            "content": "You are a clinical documentation expert. Format healthcare communications clearly and professionally."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    
    return await chat_completion(messages, temperature=0.2)

async def enhance_patient_education(
    topic: str,
    reading_level: str = "6th grade",
    language: str = "en"
) -> Optional[str]:
    """
    Generate patient education content
    Returns None if OpenAI unavailable
    """
    client = await get_openai_client()
    if not client:
        return None
    
    prompt = f"""
Create patient education content for: {topic}

Requirements:
- Reading level: {reading_level}
- Language: {language}
- Include key points, lifestyle modifications, when to call healthcare provider
- Use simple, clear language appropriate for patients
- Include encouragement and practical tips

Format as structured patient education material.
"""

    messages = [
        {
            "role": "system", 
            "content": "You are a patient education specialist. Create clear, empowering educational content for patients and families."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    
    return await chat_completion(messages, temperature=0.3)

# Legacy compatibility function for existing routers
async def chat(messages: List[Dict[str, str]], model: str = "gpt-4o-mini", **kwargs) -> str:
    """
    Legacy chat function for backward compatibility
    Used by education router and other existing components
    """
    result = await chat_completion(messages, model=model, **kwargs)
    if result is None:
        raise ExternalServiceException("OpenAI", "OpenAI service not available", None)
    return result

# Client availability check
async def is_openai_available() -> bool:
    """Check if OpenAI client is available and working"""
    client = await get_openai_client()
    return client is not None

# Cleanup function
async def cleanup_openai_client():
    """Cleanup OpenAI client on shutdown"""
    global _openai_client
    if _openai_client:
        await _openai_client.close()
        _openai_client = None
        logging.info("OpenAI client cleaned up")

# Service factory function following Conditional Imports Pattern
def create_openai_service() -> Optional[OpenAIService]:
    """
    Create OpenAI service with graceful degradation.
    Returns None if service cannot be initialized.
    """
    try:
        return OpenAIService()
    except Exception as e:
        logger.warning(f"OpenAI service unavailable: {e}")
        return None

# Export public interface
__all__ = [
    "get_openai_client",
    "chat_completion", 
    "clinical_decision_support",
    "generate_sbar_report",
    "enhance_patient_education",
    "chat",  # Legacy compatibility
    "is_openai_available",
    "cleanup_openai_client"
]
