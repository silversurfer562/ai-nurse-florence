"""
Chat router for AI Nurse Florence.

Provides a general chat endpoint for clinical conversations.
This router handles the main chat functionality for the frontend interface.
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from utils.logging import get_logger
from utils.api_responses import create_success_response, create_error_response

# Conditional imports pattern
try:
    from services.openai_client import get_openai_client
    _has_openai = True
except ImportError:
    _has_openai = False
    def get_openai_client():
        return None

try:
    from services.prompt_enhancement import enhance_prompt
    _has_prompt_enhancement = True
except ImportError:
    _has_prompt_enhancement = False
    def enhance_prompt(prompt: str, service_type: str = "general"):
        return prompt, False, None

logger = get_logger(__name__)

router = APIRouter(prefix="", tags=["chat"])  # No prefix so it's directly under /api/v1


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., description="The clinical query or message", min_length=1, max_length=2000)
    language: str = Field(default="en", description="Response language code")
    context: str = Field(default="clinical", description="Context for the conversation")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(description="The AI assistant's response")
    language: str = Field(description="Language of the response")
    timestamp: str = Field(description="Response timestamp")
    educational_banner: str = Field(default="Educational purposes only — not medical advice. No PHI stored.")


@router.post("/chat",
    summary="Clinical Chat",
    description="""
    Chat with AI Nurse Florence for clinical guidance and support.
    
    This endpoint provides clinical decision support through natural language conversation.
    Designed for healthcare professionals seeking evidence-based guidance.
    
    **Important**: Educational use only. Always follow institutional protocols.
    
    Example request:
    ```json
    {
        "message": "What are the key assessment points for sepsis recognition?",
        "language": "en"
    }
    ```
    """,
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK
)
async def clinical_chat(request: ChatRequest) -> ChatResponse:
    """
    Process clinical chat requests with AI assistance.
    
    Provides evidence-based responses for clinical queries while maintaining
    educational context and safety guidelines.
    """
    try:
        logger.info(f"Clinical chat request: {request.message[:100]}...")
        
        # Enhance prompt for clarity if available
        if _has_prompt_enhancement:
            enhanced_message, needs_clarification, clarification_question = enhance_prompt(
                request.message, request.context or "clinical"
            )
            
            if needs_clarification:
                return ChatResponse(
                    response=f"I need a bit more information to provide the best clinical guidance. {clarification_question}",
                    language=request.language,
                    timestamp=datetime.utcnow().isoformat()
                )
        else:
            enhanced_message = request.message
        
        # Try to get OpenAI response if available
        if _has_openai:
            client = get_openai_client()
            if client:
                try:
                    # Create clinical context prompt
                    system_prompt = """You are AI Nurse Florence, a clinical decision support assistant for healthcare professionals.

Provide evidence-based, educational responses that help with:
- Clinical assessment and care planning
- Medication safety and administration
- Emergency protocols and procedures  
- Patient education and communication
- Documentation and reporting

Always include:
- Clear, actionable guidance
- Evidence-based recommendations
- Appropriate safety considerations
- References to protocols when relevant

Remember: Educational purposes only. Healthcare professionals should always verify information and follow institutional guidelines."""

                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": enhanced_message}
                        ],
                        max_tokens=1000,
                        temperature=0.7
                    )
                    
                    ai_response = response.choices[0].message.content
                    
                    return ChatResponse(
                        response=ai_response,
                        language=request.language,
                        timestamp=datetime.utcnow().isoformat()
                    )
                    
                except Exception as e:
                    logger.warning(f"OpenAI API call failed: {e}")
                    # Fall through to fallback response
        
        # Fallback response for development/testing
        fallback_responses = {
            "sepsis": "**Sepsis Recognition Protocol:**\n\n1. **Quick SOFA (qSOFA) Assessment:**\n   - Altered mental status (GCS < 15)\n   - Systolic BP ≤ 100 mmHg\n   - Respiratory rate ≥ 22/min\n\n2. **SIRS Criteria:**\n   - Temperature >38°C or <36°C\n   - Heart rate >90 bpm\n   - Respiratory rate >20/min\n   - WBC >12,000 or <4,000\n\n3. **Immediate Actions:**\n   - Obtain blood cultures before antibiotics\n   - Start broad-spectrum antibiotics within 1 hour\n   - Fluid resuscitation 30ml/kg crystalloid\n   - Reassess vital signs frequently\n\n**Always follow your institution's sepsis protocol and notify physician immediately.**",
            
            "medication": "**Medication Safety Guidelines:**\n\n1. **Five Rights:**\n   - Right patient\n   - Right medication\n   - Right dose\n   - Right route\n   - Right time\n\n2. **Before Administration:**\n   - Verify orders and allergies\n   - Check drug interactions\n   - Calculate doses carefully\n   - Use two patient identifiers\n\n3. **High-Alert Medications:**\n   - Double-check calculations\n   - Use smart pumps when available\n   - Have second nurse verify\n\n**Always consult pharmacy for complex calculations or unfamiliar medications.**",
            
            "assessment": "**Clinical Assessment Framework:**\n\n1. **Primary Survey (ABCDE):**\n   - Airway\n   - Breathing\n   - Circulation\n   - Disability (neurologic)\n   - Exposure/Environmental\n\n2. **Vital Signs:**\n   - Blood pressure\n   - Heart rate and rhythm\n   - Respiratory rate and quality\n   - Temperature\n   - Oxygen saturation\n   - Pain level\n\n3. **System-Specific Assessment:**\n   - Cardiovascular\n   - Pulmonary\n   - Neurologic\n   - Gastrointestinal\n   - Genitourinary\n   - Musculoskeletal\n\n**Document thoroughly and report significant changes immediately.**"
        }
        
        # Simple keyword matching for fallback
        message_lower = request.message.lower()
        response_text = None
        
        for keyword, response in fallback_responses.items():
            if keyword in message_lower:
                response_text = response
                break
        
        if not response_text:
            response_text = f"""**Clinical Guidance for: "{request.message}"**

I'd be happy to help with your clinical question. For specific guidance, please provide more details about:

- Patient population or scenario
- Specific clinical concerns
- Type of guidance needed (assessment, intervention, education)

**Common Clinical Topics I Can Help With:**
- Emergency assessment protocols
- Medication safety and administration
- Care planning and documentation
- Patient education strategies
- Clinical decision-making frameworks

**Remember:** This is educational guidance only. Always follow your institution's protocols and consult with physicians for patient-specific decisions."""

        return ChatResponse(
            response=response_text,
            language=request.language,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error in clinical_chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error processing clinical chat request"
        )


@router.get("/chat/health",
    summary="Chat Health Check",
    description="Health check for chat functionality"
)
async def chat_health():
    """Health check for chat service."""
    return {
        "status": "operational",
        "service": "clinical-chat",
        "openai_available": _has_openai,
        "prompt_enhancement_available": _has_prompt_enhancement,
        "timestamp": datetime.utcnow().isoformat()
    }
