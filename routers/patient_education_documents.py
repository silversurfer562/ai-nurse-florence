"""
Patient Education Document Generation API

Generate patient-friendly education materials with:
- Grade 6-8 reading level content
- Multi-language support (English, Spanish, Chinese)
- MedlinePlus resource integration
- FHIR-compliant coding
- PDF generation
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from pathlib import Path
import json

from sqlalchemy.orm import Session
from database import get_db
from src.models.content_settings import DiagnosisContentMap
from src.integrations.medlineplus import MedlinePlusClient
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors

router = APIRouter(prefix="/api/documents", tags=["Patient Education Documents"])


class PatientEducationRequest(BaseModel):
    """Request model for patient education document generation"""

    # Patient info (for personalization only - not stored)
    patient_name: str = Field(..., description="Patient name for document header")
    preferred_language: str = Field(default="en", description="Language code: en, es, zh")
    reading_level: str = Field(default="intermediate", description="basic, intermediate, or advanced")

    # Diagnosis
    diagnosis_id: str = Field(..., description="Diagnosis ID from content library")
    icd10_code: str = Field(..., description="ICD-10 code")
    snomed_code: Optional[str] = Field(None, description="SNOMED CT code (if available)")

    # Content selection
    include_description: bool = Field(default=True, description="Include condition description")
    include_warning_signs: bool = Field(default=True, description="Include warning signs")
    include_medications: bool = Field(default=True, description="Include medication info")
    include_diet: bool = Field(default=True, description="Include diet/lifestyle")
    include_medlineplus: bool = Field(default=True, description="Include MedlinePlus resources")
    include_follow_up: bool = Field(default=True, description="Include follow-up instructions")

    # Custom content
    custom_instructions: Optional[str] = Field(None, description="Provider's custom instructions")
    follow_up_date: Optional[str] = Field(None, description="Follow-up appointment info")


class PatientEducationResponse(BaseModel):
    """Response model for generated document"""

    document_id: str
    pdf_url: str
    html_preview_url: Optional[str]
    language: str
    reading_level: str
    generated_at: datetime


@router.post("/patient-education", response_model=PatientEducationResponse)
async def generate_patient_education_document(
    request: PatientEducationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate a patient education document with selected content.

    Features:
    - Patient-friendly language (Grade 6-8 reading level)
    - Multi-language support
    - MedlinePlus integration
    - FHIR-compliant coding
    - PDF generation
    """

    # Get diagnosis from database
    diagnosis = db.query(DiagnosisContentMap).filter_by(
        id=request.diagnosis_id
    ).first()

    if not diagnosis:
        raise HTTPException(
            status_code=404,
            detail=f"Diagnosis '{request.diagnosis_id}' not found"
        )

    # Get MedlinePlus content if requested
    medlineplus_content = None
    if request.include_medlineplus:
        medlineplus_client = MedlinePlusClient()
        medlineplus_content = medlineplus_client.fetch_content(
            icd10_code=request.icd10_code,
            language=request.preferred_language
        )

    # Build document content
    document_content = _build_document_content(
        request=request,
        diagnosis=diagnosis,
        medlineplus_content=medlineplus_content
    )

    # Generate PDF
    pdf_path = _generate_pdf(
        content=document_content,
        patient_name=request.patient_name,
        language=request.preferred_language
    )

    # Generate document ID
    document_id = f"PE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    return PatientEducationResponse(
        document_id=document_id,
        pdf_url=f"/api/documents/download/{pdf_path.name}",
        html_preview_url=None,  # TODO: Implement HTML preview
        language=request.preferred_language,
        reading_level=request.reading_level,
        generated_at=datetime.now()
    )


def _build_document_content(
    request: PatientEducationRequest,
    diagnosis: DiagnosisContentMap,
    medlineplus_content: Optional[dict]
) -> dict:
    """Build structured content for the document"""

    content = {
        "title": _translate("Patient Education", request.preferred_language),
        "patient_name": request.patient_name,
        "diagnosis_name": diagnosis.diagnosis_display,
        "sections": []
    }

    # Condition description (patient-friendly)
    if request.include_description:
        description = diagnosis.patient_friendly_description or diagnosis.diagnosis_display

        content["sections"].append({
            "title": _translate("What is this condition?", request.preferred_language),
            "content": description,
            "icon": "info-circle"
        })

    # Warning signs
    if request.include_warning_signs and diagnosis.standard_warning_signs:
        content["sections"].append({
            "title": _translate("When to seek immediate help", request.preferred_language),
            "content": _translate(
                "Call 911 or go to the emergency room if you have:",
                request.preferred_language
            ),
            "bullet_points": diagnosis.standard_warning_signs,
            "icon": "exclamation-triangle",
            "style": "warning"
        })

    # Medications
    if request.include_medications and diagnosis.standard_medications:
        med_content = _format_medications(
            diagnosis.standard_medications,
            request.preferred_language
        )
        content["sections"].append({
            "title": _translate("Your Medications", request.preferred_language),
            "content": med_content,
            "icon": "pills"
        })

    # Diet and lifestyle
    if request.include_diet and diagnosis.standard_diet_instructions:
        content["sections"].append({
            "title": _translate("Diet and Lifestyle", request.preferred_language),
            "content": diagnosis.standard_diet_instructions,
            "icon": "utensils"
        })

    # MedlinePlus resources
    if request.include_medlineplus and medlineplus_content:
        content["sections"].append({
            "title": _translate("Learn More", request.preferred_language),
            "content": _translate(
                "For more information, visit these trusted resources:",
                request.preferred_language
            ),
            "resources": [
                {
                    "title": medlineplus_content.get("title"),
                    "url": medlineplus_content.get("url"),
                    "source": "MedlinePlus"
                }
            ],
            "icon": "book"
        })

    # Follow-up instructions
    if request.include_follow_up:
        follow_up_text = diagnosis.standard_follow_up_instructions or \
                        _translate("Follow up with your healthcare provider as directed.", request.preferred_language)

        if request.follow_up_date:
            follow_up_text += f"\n\n{_translate('Your follow-up appointment:', request.preferred_language)} {request.follow_up_date}"

        content["sections"].append({
            "title": _translate("Follow-up Care", request.preferred_language),
            "content": follow_up_text,
            "icon": "calendar-check"
        })

    # Custom instructions
    if request.custom_instructions:
        content["sections"].append({
            "title": _translate("Special Instructions for You", request.preferred_language),
            "content": request.custom_instructions,
            "icon": "user-md",
            "style": "highlight"
        })

    return content


def _generate_pdf(content: dict, patient_name: str, language: str) -> Path:
    """Generate PDF from document content"""

    # Create output directory if it doesn't exist
    output_dir = Path("generated_documents")
    output_dir.mkdir(exist_ok=True)

    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"patient_education_{timestamp}.pdf"
    filepath = output_dir / filename

    # Create PDF
    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1E40AF'),
        spaceAfter=30
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2563EB'),
        spaceAfter=12,
        spaceBefore=20
    )
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=12,
        leading=18,
        spaceAfter=12
    )
    warning_style = ParagraphStyle(
        'Warning',
        parent=styles['BodyText'],
        fontSize=12,
        leading=18,
        textColor=colors.HexColor('#DC2626'),
        leftIndent=20,
        spaceAfter=12
    )

    # Build PDF content
    story = []

    # Header
    story.append(Paragraph(content["title"], title_style))
    story.append(Paragraph(f"<b>Patient:</b> {patient_name}", body_style))
    story.append(Paragraph(f"<b>Diagnosis:</b> {content['diagnosis_name']}", body_style))
    story.append(Spacer(1, 0.3 * inch))

    # Sections
    for section in content["sections"]:
        # Section title
        story.append(Paragraph(section["title"], heading_style))

        # Section content
        if section.get("content"):
            style = warning_style if section.get("style") == "warning" else body_style
            story.append(Paragraph(section["content"], style))

        # Bullet points
        if section.get("bullet_points"):
            for point in section["bullet_points"]:
                story.append(Paragraph(f"• {point}", body_style))

        # Resources
        if section.get("resources"):
            for resource in section["resources"]:
                story.append(Paragraph(
                    f"• <b>{resource['title']}</b><br/>"
                    f"  {resource['url']}<br/>"
                    f"  <i>Source: {resource['source']}</i>",
                    body_style
                ))

        story.append(Spacer(1, 0.2 * inch))

    # Footer
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph(
        f"<i>Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</i>",
        styles['Normal']
    ))

    # Build PDF
    doc.build(story)

    return filepath


def _format_medications(medications: List[dict], language: str) -> str:
    """Format medication list for document"""

    if not medications:
        return _translate("No medications prescribed.", language)

    formatted = []
    for med in medications:
        med_name = med.get("medication_display", "Unknown")
        dosage = f"{med.get('dosage_value', '')} {med.get('dosage_unit', '')}"
        frequency = med.get("frequency_display", "")

        formatted.append(
            f"<b>{med_name}</b><br/>"
            f"Take {dosage} {frequency}"
        )

    return "<br/><br/>".join(formatted)


def _translate(text: str, language: str) -> str:
    """Translate text to specified language (stub - implement with translation API)"""

    # Translation dictionary (Spanish)
    translations_es = {
        "Patient Education": "Educación del Paciente",
        "What is this condition?": "¿Qué es esta condición?",
        "When to seek immediate help": "Cuándo buscar ayuda inmediata",
        "Call 911 or go to the emergency room if you have:": "Llame al 911 o vaya a la sala de emergencias si tiene:",
        "Your Medications": "Sus Medicamentos",
        "Diet and Lifestyle": "Dieta y Estilo de Vida",
        "Learn More": "Aprenda Más",
        "For more information, visit these trusted resources:": "Para más información, visite estos recursos confiables:",
        "Follow-up Care": "Cuidado de Seguimiento",
        "Follow up with your healthcare provider as directed.": "Haga seguimiento con su proveedor de salud según las indicaciones.",
        "Your follow-up appointment:": "Su cita de seguimiento:",
        "Special Instructions for You": "Instrucciones Especiales Para Usted",
        "No medications prescribed.": "No se recetaron medicamentos.",
        "Take": "Tome"
    }

    # Translation dictionary (Chinese)
    translations_zh = {
        "Patient Education": "患者教育",
        "What is this condition?": "这是什么病症?",
        "When to seek immediate help": "何时寻求紧急帮助",
        "Call 911 or go to the emergency room if you have:": "如果您有以下情况，请拨打911或去急诊室:",
        "Your Medications": "您的药物",
        "Diet and Lifestyle": "饮食和生活方式",
        "Learn More": "了解更多",
        "For more information, visit these trusted resources:": "欲了解更多信息，请访问这些可信资源:",
        "Follow-up Care": "后续护理",
        "Follow up with your healthcare provider as directed.": "按照指示与您的医疗保健提供者进行随访。",
        "Your follow-up appointment:": "您的随访预约:",
        "Special Instructions for You": "为您的特别说明",
        "No medications prescribed.": "未开处方药。",
        "Take": "服用"
    }

    if language == "es":
        return translations_es.get(text, text)
    elif language == "zh":
        return translations_zh.get(text, text)
    else:
        return text


@router.get("/download/{filename}")
async def download_document(filename: str):
    """Download generated document"""

    filepath = Path("generated_documents") / filename

    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Document not found")

    return FileResponse(
        path=str(filepath),
        media_type="application/pdf",
        filename=filename
    )
