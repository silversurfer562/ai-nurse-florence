"""
AI Nurse Florence - Clinical Document Generation API
Provides template-based document generation for nursing workflows
"""

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any

from services.clinical_templates import (
    clinical_template_engine, 
    TemplateContext
)

router = APIRouter(prefix="/api/v2/clinical/documents", tags=["Clinical Documents"])

class DocumentGenerationRequest(BaseModel):
    """Request model for document generation"""
    template_name: str = Field(..., description="Name of the template to use")
    nurse_name: Optional[str] = Field(None, description="Name of the nurse generating the document")
    nurse_unit: Optional[str] = Field(None, description="Hospital unit/department")
    patient_name: Optional[str] = Field(None, description="Patient's name")
    patient_id: Optional[str] = Field(None, description="Patient ID or medical record number")
    patient_age: Optional[int] = Field(None, description="Patient's age")
    primary_diagnosis: Optional[str] = Field(None, description="Primary medical diagnosis")
    clinical_data: Dict[str, Any] = Field(default_factory=dict, description="Clinical data (vitals, assessments, etc.)")
    evidence_sources: List[str] = Field(default_factory=list, description="Evidence sources to cite")
    custom_fields: Dict[str, Any] = Field(default_factory=dict, description="Additional template-specific data")

class DocumentResponse(BaseModel):
    """Response model for generated documents"""
    success: bool
    document_type: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    editable: bool = True
    ready_for_use: bool = False
    error: Optional[str] = None
    required_fields: Optional[List[str]] = None

class TemplateListResponse(BaseModel):
    """Response model for template listing"""
    templates: List[Dict[str, Any]]
    categories: List[str]

@router.get("/templates", response_model=TemplateListResponse)
def list_document_templates(
    category: Optional[str] = Query(None, description="Filter by category (communication, education, care_planning)")
):
    """
    List all available clinical document templates
    
    **Use Cases:**
    - SBAR reports for physician communication
    - Patient education handouts
    - Care plans and assessments
    - Emails to allied health professionals
    - Continuing education responses
    """
    try:
        templates = clinical_template_engine.list_templates(category)
        categories = list(set(t["category"] for t in templates))
        
        return TemplateListResponse(
            templates=templates,
            categories=categories
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list templates: {str(e)}")

@router.get("/templates/{template_name}/requirements")
def get_template_requirements(template_name: str):
    """
    Get requirements and field descriptions for a specific template
    
    **Purpose:** Helps nurses understand what information is needed before generating a document
    """
    try:
        requirements = clinical_template_engine.get_template_requirements(template_name)
        return {
            "success": True,
            "template": requirements,
            "example_usage": _get_template_example(template_name)
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get requirements: {str(e)}")

@router.post("/generate", response_model=DocumentResponse)
def generate_clinical_document(request: DocumentGenerationRequest):
    """
    Generate a clinical document from a template
    
    **Continuing Education Focus:**
    - Provides structured, evidence-based templates
    - Supports work-related documentation needs
    - Generates professional communication formats
    - Creates editable drafts for review before use
    
    **Document Types Available:**
    - **SBAR Reports:** Professional communication to physicians
    - **Patient Education:** Handouts and educational materials
    - **Care Plans:** Structured nursing care documentation
    - **Emails:** Professional communication to allied health
    - **Assessment Notes:** Clinical documentation
    """
    try:
        # Create template context
        context = TemplateContext(
            nurse_name=request.nurse_name,
            nurse_unit=request.nurse_unit,
            patient_id=request.patient_id,
            patient_name=request.patient_name,
            patient_age=request.patient_age,
            primary_diagnosis=request.primary_diagnosis,
            clinical_data=request.clinical_data,
            evidence_sources=request.evidence_sources,
            custom_fields=request.custom_fields
        )
        
        # Generate document
        result = clinical_template_engine.generate_document(
            template_name=request.template_name,
            context=context,
            custom_data=request.custom_fields
        )
        
        return DocumentResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document generation failed: {str(e)}")

@router.post("/sbar-report")
def generate_sbar_report(
    patient_name: str = Body(..., description="Patient's name"),
    situation_description: str = Body(..., description="Current clinical situation"),
    assessment_findings: str = Body(..., description="Your clinical assessment"),
    recommendations: str = Body(..., description="Recommended actions"),
    nurse_name: Optional[str] = Body(None, description="Your name"),
    nurse_unit: Optional[str] = Body(None, description="Your unit"),
    patient_id: Optional[str] = Body(None, description="Patient ID"),
    background_info: Optional[str] = Body(None, description="Relevant background"),
    vitals: Optional[Dict[str, Any]] = Body(None, description="Current vital signs"),
    urgent: bool = Body(False, description="Mark as urgent communication")
):
    """
    **Quick SBAR Report Generator**
    
    Generate a professional SBAR (Situation, Background, Assessment, Recommendation) 
    report for physician communication. This supports evidence-based nursing practice 
    and continuing education in professional communication.
    
    **Example Usage:**
    ```json
    {
        "patient_name": "John Smith",
        "situation_description": "Patient experiencing increased shortness of breath",
        "assessment_findings": "Oxygen saturation decreased to 88%, increased work of breathing",
        "recommendations": "Request chest X-ray and consider oxygen therapy"
    }
    ```
    """
    
    custom_data = {
        "situation_description": situation_description,
        "assessment_findings": assessment_findings,
        "recommendations": recommendations,
        "background_info": background_info,
        "urgent_actions": "**URGENT**" if urgent else "",
        "recipient": "Attending Physician"
    }
    
    if vitals:
        custom_data["clinical_data"] = {"vitals": vitals}
    
    request = DocumentGenerationRequest(
        template_name="sbar_standard",
        nurse_name=nurse_name,
        nurse_unit=nurse_unit,
        patient_name=patient_name,
        patient_id=patient_id,
        custom_fields=custom_data
    )
    
    return generate_clinical_document(request)

@router.post("/patient-education")
def generate_patient_education(
    education_topic: str = Body(..., description="Topic for patient education"),
    main_information: str = Body(..., description="Key information patient needs to know"),
    instructions: str = Body(..., description="Specific instructions for patient"),
    warning_signs: str = Body(..., description="Warning signs to watch for"),
    contact_criteria: str = Body(..., description="When to contact healthcare team"),
    nurse_name: Optional[str] = Body(None, description="Your name"),
    nurse_unit: Optional[str] = Body(None, description="Your unit"),
    additional_resources: Optional[str] = Body(None, description="Additional resources or websites")
):
    """
    **Patient Education Material Generator**
    
    Create professional patient education handouts that nurses can edit 
    before providing to patients or families. Supports continuing education 
    in patient teaching and health literacy.
    
    **Example Usage:**
    ```json
    {
        "education_topic": "Managing Diabetes at Home",
        "main_information": "Diabetes requires daily monitoring of blood sugar levels...",
        "instructions": "Check blood sugar twice daily, take medication as prescribed...",
        "warning_signs": "Blood sugar over 300, excessive thirst, confusion...",
        "contact_criteria": "Call immediately if blood sugar >300 or <70"
    }
    ```
    """
    
    custom_data = {
        "education_topic": education_topic,
        "main_information": main_information,
        "instructions": instructions,
        "warning_signs": warning_signs,
        "contact_criteria": contact_criteria,
        "additional_resources": additional_resources
    }
    
    request = DocumentGenerationRequest(
        template_name="patient_education_standard",
        nurse_name=nurse_name,
        nurse_unit=nurse_unit,
        custom_fields=custom_data
    )
    
    return generate_clinical_document(request)

@router.post("/physician-email")
def generate_physician_email(
    patient_name: str = Body(..., description="Patient's name"),
    clinical_update: str = Body(..., description="Clinical update to communicate"),
    current_assessment: str = Body(..., description="Current clinical assessment"),
    concerns_questions: str = Body(..., description="Specific concerns or questions"),
    nurse_name: Optional[str] = Body(None, description="Your name"),
    nurse_unit: Optional[str] = Body(None, description="Your unit"),
    physician_name: Optional[str] = Body(None, description="Physician's name"),
    patient_id: Optional[str] = Body(None, description="Patient ID"),
    actions_taken: Optional[str] = Body(None, description="Actions already taken"),
    vitals: Optional[Dict[str, Any]] = Body(None, description="Current vital signs")
):
    """
    **Professional Email to Physician**
    
    Generate professional email communication to physicians or other providers.
    Supports continuing education in interprofessional communication and 
    evidence-based collaborative care.
    
    **Example Usage:**
    ```json
    {
        "patient_name": "Mary Johnson",
        "clinical_update": "Patient developed new onset chest pain at 1400",
        "current_assessment": "Pain 7/10, radiating to left arm, diaphoretic",
        "concerns_questions": "Please evaluate for possible cardiac event"
    }
    ```
    """
    
    custom_data = {
        "clinical_update": clinical_update,
        "current_assessment": current_assessment,
        "concerns_questions": concerns_questions,
        "physician_name": physician_name,
        "actions_taken": actions_taken,
        "email_subject": f"Patient Update - {patient_name}"
    }
    
    if vitals:
        custom_data["clinical_data"] = {"vitals": vitals}
    
    request = DocumentGenerationRequest(
        template_name="physician_email",
        nurse_name=nurse_name,
        nurse_unit=nurse_unit,
        patient_name=patient_name,
        patient_id=patient_id,
        custom_fields=custom_data
    )
    
    return generate_clinical_document(request)

@router.post("/continuing-education/qa")
def generate_continuing_education_response(
    clinical_question: str = Body(..., description="Clinical question for continuing education"),
    evidence_answer: str = Body(..., description="Evidence-based answer"),
    key_points: str = Body(..., description="Key clinical points to remember"),
    practical_application: str = Body(..., description="How to apply in practice"),
    nurse_name: Optional[str] = Body(None, description="Your name"),
    evidence_sources: List[str] = Body(default_factory=list, description="Evidence sources"),
    related_considerations: Optional[str] = Body(None, description="Additional considerations")
):
    """
    **Continuing Education Q&A Response**
    
    Generate structured responses to clinical questions for continuing education.
    Supports evidence-based practice development and work-related learning.
    
    **Purpose:** 
    - Answer work-related clinical questions as they arise
    - Provide evidence-based information for decision-making
    - Support continuing education requirements
    - Create reference materials for future use
    
    **Example Usage:**
    ```json
    {
        "clinical_question": "What are the early signs of sepsis in elderly patients?",
        "evidence_answer": "Early sepsis signs in elderly include altered mental status...",
        "key_points": "Monitor for confusion, subtle vital sign changes...",
        "practical_application": "Use SIRS criteria modified for elderly population..."
    }
    ```
    """
    
    custom_data = {
        "clinical_question": clinical_question,
        "evidence_answer": evidence_answer,
        "key_points": key_points,
        "practical_application": practical_application,
        "related_considerations": related_considerations
    }
    
    request = DocumentGenerationRequest(
        template_name="continuing_ed_qa",
        nurse_name=nurse_name,
        evidence_sources=evidence_sources,
        custom_fields=custom_data
    )
    
    return generate_clinical_document(request)

def _get_template_example(template_name: str) -> Dict[str, Any]:
    """Get example usage for a template"""
    examples = {
        "sbar_standard": {
            "description": "Professional SBAR report for physician communication",
            "example_data": {
                "patient_name": "John Smith",
                "situation_description": "Patient experiencing increased shortness of breath post-surgery",
                "assessment_findings": "Oxygen saturation 88%, increased work of breathing, crackles in bilateral lower lobes",
                "recommendations": "Request chest X-ray, consider diuretic therapy, oxygen therapy initiated"
            }
        },
        "patient_education_standard": {
            "description": "Patient education handout",
            "example_data": {
                "education_topic": "Post-Surgical Wound Care",
                "main_information": "Proper wound care prevents infection and promotes healing",
                "instructions": "Keep wound clean and dry, change dressing daily as shown",
                "warning_signs": "Increased redness, warmth, swelling, or discharge from wound",
                "contact_criteria": "Call surgeon if temperature >101°F or wound shows signs of infection"
            }
        },
        "physician_email": {
            "description": "Professional email to physician",
            "example_data": {
                "clinical_update": "Patient developed new onset chest pain at 1400 hours",
                "current_assessment": "Pain 7/10, crushing quality, radiating to left arm, patient diaphoretic",
                "concerns_questions": "Please evaluate for possible acute coronary syndrome"
            }
        }
    }
    
    return examples.get(template_name, {"description": "Template example not available"})

# Add banner for continuing education focus
CONTINUING_EDUCATION_BANNER = """
**AI Nurse Florence - Continuing Education Assistant**
*Supporting evidence-based nursing practice and professional development*

This tool provides template-based document generation to support:
✓ Work-related clinical questions and scenarios
✓ Professional communication with healthcare team
✓ Patient education material development  
✓ Evidence-based nursing documentation
✓ Continuing education and skill development

**Important:** All generated documents are drafts for your review and editing before use.
Always follow your facility's policies and consult with your healthcare team as appropriate.
"""
