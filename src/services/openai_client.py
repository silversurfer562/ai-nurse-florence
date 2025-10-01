"""
OpenAI Client Service - AI Nurse Florence
Following OpenAI Integration pattern with environment-based API key loading
"""

import logging
from typing import Optional, Dict, Any
from src.utils.config import get_settings, get_openai_config

logger = logging.getLogger(__name__)

class OpenAIService:
    """
    OpenAI service following OpenAI Integration pattern.
    Implements Conditional Imports Pattern for graceful degradation.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.config = get_openai_config()

        # Try to initialize OpenAI client following lazy client pattern
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client if API key is available."""
        if self.config["available"]:
            try:
                # Try to import OpenAI following Conditional Imports Pattern
                try:
                    import openai
                    # Use AsyncOpenAI for async/await compatibility
                    self._client = openai.AsyncOpenAI(api_key=self.config["api_key"])
                    logger.info("OpenAI service: Client initialized successfully")
                except ImportError:
                    logger.info("OpenAI service: openai library not available, using educational stubs")
                    self._client = None
                except Exception as e:
                    logger.warning(f"OpenAI service: Failed to initialize client: {e}")
                    self._client = None
            except Exception as e:
                logger.warning(f"OpenAI service: Configuration error: {e}")
        else:
            logger.info("OpenAI service: No API key configured, using educational stubs")
    
    async def generate_response(self, prompt: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate AI response following OpenAI Integration pattern.
        
        Args:
            prompt: User prompt for AI generation
            context: Optional context for better responses
        
        Returns:
            Dict with AI response and educational disclaimers
        """
        try:
            if self._client and self.config["available"]:
                # Use live OpenAI API
                return await self._generate_live_response(prompt, context)
            else:
                # Fallback: Educational stub response
                return self._create_stub_response(prompt, context)
                
        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            return self._create_error_response(prompt, str(e))
    
    async def _generate_live_response(self, prompt: str, context: Optional[str]) -> Dict[str, Any]:
        """Generate live OpenAI response using actual API."""
        try:
            # Construct messages following OpenAI best practices
            messages = []
            
            if context:
                messages.append({
                    "role": "system",
                    "content": f"You are a healthcare AI assistant. Context: {context}."
                })
            else:
                messages.append({
                    "role": "system",
                    "content": "You are a healthcare AI assistant providing information."
                })
            
            messages.append({"role": "user", "content": prompt})
            
            # Make API call
            response = await self._client.chat.completions.create(
                model=self.config["model"],
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            return {
                "prompt": prompt,
                "context": context,
                "response": ai_response,
                "model": self.config["model"],
                "service_note": "OpenAI service: Live API response",
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
        except Exception as e:
            logger.error(f"Live OpenAI API error: {e}")
            # Fall back to stub response on API error
            return self._create_stub_response(prompt, context, api_error=str(e))
    
    def _create_stub_response(self, prompt: str, context: Optional[str], api_error: Optional[str] = None) -> Dict[str, Any]:
        """Create educational stub response following API Design Standards."""
        
        if api_error:
            service_note = f"OpenAI service: API error, using educational stub - {api_error}"
        else:
            service_note = "OpenAI service: Educational stub mode (no API key configured)"
        
        # Create contextual response based on prompt content
        if any(term in prompt.lower() for term in ['nursing', 'patient', 'care', 'assessment']):
            response = f"Educational AI response for nursing query: '{prompt}'. This is a simulated response demonstrating the AI assistant's capability to provide contextual healthcare information. In a live system, this would provide evidence-based nursing guidance with proper citations and safety considerations."
        elif any(term in prompt.lower() for term in ['medication', 'drug', 'treatment']):
            response = f"Educational AI response for medication query: '{prompt}'. This simulated response shows how the AI would provide drug information with appropriate safety disclaimers, contraindications, and dosing considerations based on current clinical guidelines."
        elif any(term in prompt.lower() for term in ['diagnosis', 'symptom', 'condition']):
            response = f"Educational AI response for diagnostic query: '{prompt}'. This demonstrates how the AI would provide differential diagnosis considerations, clinical decision support, and evidence-based recommendations while emphasizing the need for professional clinical judgment."
        else:
            response = f"Educational AI response: This is a simulated response to '{prompt}' for demonstration purposes. A live system would provide comprehensive, evidence-based healthcare information with appropriate clinical context and safety considerations."
        
        return {
            "prompt": prompt,
            "context": context,
            "response": response,
            "model": self.config["model"],
            "service_note": service_note
        }
    
    def _create_error_response(self, prompt: str, error: str) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            "prompt": prompt,
            "error": f"OpenAI service temporarily unavailable: {error}",
            "fallback_note": "AI service experiencing issues. Content may be limited.",
            "service_status": "degraded"
        }


async def clinical_decision_support(
    patient_data: dict,
    clinical_question: str,
    context: str = "general"
) -> dict:
    """
    Clinical decision support using OpenAI following OpenAI Integration pattern.
    
    Args:
        patient_data: Patient information (de-identified)
        clinical_question: Clinical question requiring decision support
        context: Clinical context (general, critical, emergency)
    
    Returns:
        Dict with clinical recommendations and educational disclaimers
    """
    service = create_openai_service()

    if not service:
        return {
            "clinical_question": clinical_question,
            "error": "Clinical decision support temporarily unavailable",
            "fallback_note": "Please consult clinical protocols and healthcare team for decision support",
            "service_status": "degraded"
        }
    
    # Create clinical decision prompt
    clinical_prompt = f"""
    Clinical Decision Support Request:

    Clinical Question: {clinical_question}
    Context: {context}
    Patient Data: {patient_data}

    Please provide evidence-based clinical guidance including:
    1. Assessment considerations
    2. Recommended interventions
    3. Monitoring parameters
    4. When to escalate care
    """
    
    try:
        result = await service.generate_response(
            prompt=clinical_prompt,
            context="clinical_decision_support"
        )
        
        # Add clinical-specific fields
        result.update({
            "clinical_question": clinical_question,
            "decision_support_type": context,
            "escalation_note": "Escalate to attending physician or specialist for complex cases or when patient condition changes."
        })
        
        return result
        
    except Exception as e:
        return {
            "clinical_question": clinical_question,
            "error": f"Clinical decision support failed: {str(e)}",
            "fallback_note": "AI decision support temporarily unavailable - rely on clinical protocols",
            "service_status": "error"
        }

def is_openai_available() -> bool:
    """
    Check if OpenAI service is available following OpenAI Integration pattern.
    
    Returns:
        bool: True if OpenAI service can be created and used
    """
    try:
        config = get_openai_config()
        return config["available"]
    except Exception:
        return False

# Update factory function to include clinical decision support
def create_openai_service() -> Optional[OpenAIService]:
    """
    Create OpenAI service with clinical decision support capabilities.
    Returns None if service cannot be initialized following Conditional Imports Pattern.
    """
    try:
        service = OpenAIService()
        
        # Verify clinical decision support is available
        if service.config["available"]:
            logger.info("OpenAI service: Clinical decision support enabled")
        else:
            logger.info("OpenAI service: Using educational stubs for clinical decision support")
            
        return service
    except Exception as e:
        logger.warning(f"OpenAI service unavailable: {e}")
        return None
