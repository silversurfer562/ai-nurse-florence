from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Nurse Florence",
    description="Clinical Decision Support System API",
    version="2.0.1"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
# This serves your frontend at /static/
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
    logger.info("Static files mounted at /static/")
else:
    logger.warning("Static directory not found. Create 'static' folder for frontend files.")

# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str
    language: str = "en"

class ChatResponse(BaseModel):
    response: str
    language: str
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    message: str
    version: str
    timestamp: str

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "AI Nurse Florence - Healthcare AI Assistant",
        "status": "operational", 
        "version": "2.0.1",
        "banner": "Educational purposes only — verify with healthcare providers. No PHI stored.",
        "docs": "/docs",
        "health": "/health",
        "api_health": "/api/v1/health",
        "frontend": "/static/index.html"
    }

# Health check endpoint
@app.get("/health")
@app.get("/api/v1/health")
async def health_check():
    return HealthResponse(
        status="operational",
        message="AI Nurse Florence API is running",
        version="2.0.1",
        timestamp=datetime.utcnow().isoformat()
    )

# Chat endpoint for clinical consultations
@app.post("/api/v1/chat")
async def clinical_chat(chat_request: ChatRequest):
    try:
        # Log the incoming request
        logger.info(f"Clinical chat request: {chat_request.message[:100]}...")
        
        # For now, return a standard response
        # In production, this would call your AI model
        response_text = generate_clinical_response(chat_request.message)
        
        return ChatResponse(
            response=response_text,
            language=chat_request.language,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error in clinical_chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Additional API endpoints for clinical features
@app.get("/api/v1/protocols/{protocol_type}")
async def get_protocol(protocol_type: str):
    """Get clinical protocols by type"""
    protocols = {
        "sepsis": "Sepsis recognition and management protocols...",
        "medication": "Medication safety and administration protocols...",
        "assessment": "Patient assessment protocols and tools...",
        "documentation": "Clinical documentation standards..."
    }
    
    if protocol_type.lower() in protocols:
        return {
            "protocol_type": protocol_type,
            "content": protocols[protocol_type.lower()],
            "timestamp": datetime.utcnow().isoformat()
        }
    else:
        raise HTTPException(status_code=404, detail="Protocol not found")

@app.get("/api/v1/calculations/dosage")
async def dosage_calculator(
    desired_dose: float,
    stock_strength: float, 
    stock_volume: float = 1.0
):
    """Calculate medication dosage"""
    try:
        if stock_strength <= 0:
            raise HTTPException(status_code=400, detail="Stock strength must be greater than 0")
        
        volume_to_give = (desired_dose / stock_strength) * stock_volume
        
        return {
            "desired_dose": desired_dose,
            "stock_strength": stock_strength,
            "stock_volume": stock_volume,
            "volume_to_give": round(volume_to_give, 2),
            "calculation": f"({desired_dose} ÷ {stock_strength}) × {stock_volume} = {volume_to_give:.2f}",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in dosage calculation: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid calculation parameters")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Resource not found",
            "path": str(request.url.path),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

def generate_clinical_response(message: str) -> str:
    """
    Generate clinical response based on message content.
    In production, this would interface with your AI model.
    """
    message_lower = message.lower()
    
    if "sepsis" in message_lower:
        return """**Sepsis Recognition & Management Protocol:**

**qSOFA Screening (≥2 points suggests sepsis):**
• Altered mental status (GCS <15)
• Systolic BP ≤100 mmHg  
• Respiratory rate ≥22/min

**SIRS Criteria (≥2 suggests infection):**
• Temperature >38°C or <36°C
• Heart rate >90 bpm
• Respiratory rate >20/min
• WBC >12,000 or <4,000

**Sepsis Bundle - Hour-1:**
1. Measure lactate level
2. Obtain blood cultures before antibiotics
3. Administer broad-spectrum antibiotics within 1 hour
4. Begin rapid IV fluid resuscitation 30mL/kg

**Nursing Priorities:**
• Continuous vital sign monitoring
• Strict I&O measurement
• Early mobility as tolerated
• DVT prophylaxis
• Family communication"""

    elif any(word in message_lower for word in ["medication", "dosage", "drug"]):
        return """**Medication Safety Protocol:**

**Five Rights of Administration:**
• Right Patient (2 identifiers)
• Right Drug (generic & brand names)  
• Right Dose (calculate and verify)
• Right Route (PO, IV, IM, SQ, etc.)
• Right Time (scheduled vs PRN)

**Dosage Calculation:**
**Formula:** (Desired dose ÷ Stock strength) × Stock volume = Volume to give

**Critical Safety Checks:**
1. Verify allergies and contraindications
2. Check drug interactions
3. Assess patient's current condition
4. Double-check high-risk medications
5. Monitor for adverse effects
6. Document immediately

**High-Alert Medications:** Insulin, heparin, chemotherapy, vasoactive drugs require independent double-checks."""

    elif "pain" in message_lower:
        return """**Pain Assessment & Management:**

**Assessment Scales:**
• **Numeric Rating (0-10):** Adults, cognitively intact
• **Wong-Baker FACES:** Children 3+, language barriers  
• **FLACC Scale:** Non-verbal patients
• **CPOT:** Critical care/ventilated patients

**PQRST Assessment:**
• **P**rovocation: What makes it better/worse?
• **Q**uality: Sharp, dull, burning, cramping?
• **R**egion: Where? Does it radiate?
• **S**everity: 0-10 scale rating
• **T**iming: When started? Constant/intermittent?

**Non-Pharmacological Interventions:**
• Positioning and support
• Heat/cold therapy
• Massage and distraction
• Relaxation techniques
• Music therapy

**Documentation:** Pain scores before/after interventions, effectiveness, side effects."""

    elif "sbar" in message_lower:
        return """**SBAR Communication Framework:**

**S - SITUATION:**
"Hi Dr. [Name], this is [Your name] calling about [Patient] in room [#]. I'm calling because [specific reason]."

**B - BACKGROUND:**
• Patient age, sex, diagnosis
• Admission date and reason
• Relevant medical history
• Current medications
• Recent procedures

**A - ASSESSMENT:**
• Current vital signs with trends
• Physical assessment findings
• Laboratory/diagnostic results
• Pain level and mental status

**R - RECOMMENDATION:**
• What you think the patient needs
• Specific orders you're requesting
• Timeline for response
• Questions for provider

**Example:** "Dr. Smith, this is Sarah calling about Mrs. Johnson in 302. She's having increased SOB. She's 68 with CHF, admitted yesterday. Her O2 sat dropped to 88%, RR 28, new crackles bilaterally. I think she needs a chest X-ray and increased diuretics. Can you assess within 30 minutes?"."""

    else:
        return f"""**Clinical Consultation Response:**

Thank you for your question about: "{message}"

As your clinical decision support assistant, I can provide evidence-based guidance on:

• **Patient Assessment** - Systematic evaluation and monitoring
• **Medication Safety** - Dosing, interactions, administration  
• **Emergency Protocols** - Recognition and response procedures
• **Documentation** - SBAR, care plans, nursing notes
• **Specialized Care** - Wound management, IV therapy

**For more specific guidance, please provide:**
• Clinical context or patient scenario
• Specific symptoms or conditions
• Particular protocols needed
• Your primary concerns

**Remember:** This is educational support. Always follow institutional protocols and consult healthcare team members for patient care decisions."""

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment variable (Railway sets this automatically)
    port = int(os.environ.get("PORT", 8080))
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Set to True for development
        log_level="info"
    )