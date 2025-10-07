"""
Patient Education Document Generation API

Generate patient-friendly education materials with:
- Grade 6-8 reading level content
- Multi-language support (English, Spanish, Chinese)
- MedlinePlus resource integration
- FHIR-compliant coding
- PDF generation
"""

from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from sqlalchemy.orm import Session

from src.database import get_db
from src.integrations.medlineplus import MedlinePlusClient
from src.models.content_settings import DiagnosisContentMap
from src.services.claude_service import claude_service
from src.utils.html_generator import generate_patient_education_html

router = APIRouter(prefix="/documents", tags=["Patient Education Documents"])


class PatientEducationRequest(BaseModel):
    """Request model for patient education document generation"""

    # Patient info (for personalization only - not stored)
    patient_name: str = Field(..., description="Patient name for document header")
    preferred_language: str = Field(
        default="en", description="Language code: en, es, zh"
    )
    reading_level: str = Field(
        default="intermediate", description="basic, intermediate, or advanced"
    )

    # Care setting context (Care Setting Framework)
    care_setting: Optional[str] = Field(
        default="med-surg",
        description="Care setting: icu, med-surg, emergency, outpatient, home-health, skilled-nursing",
    )

    # Diagnosis - must come from content library for evidence-based content
    diagnosis_id: str = Field(..., description="Diagnosis ID from content library")
    icd10_code: str = Field(..., description="ICD-10 code")
    snomed_code: Optional[str] = Field(
        None, description="SNOMED CT code (if available)"
    )

    # Content selection
    include_description: bool = Field(
        default=True, description="Include condition description"
    )
    include_warning_signs: bool = Field(
        default=True, description="Include warning signs"
    )
    include_medications: bool = Field(
        default=True, description="Include medication info"
    )
    include_diet: bool = Field(default=True, description="Include diet/lifestyle")
    include_medlineplus: bool = Field(
        default=True, description="Include MedlinePlus resources"
    )
    include_follow_up: bool = Field(
        default=True, description="Include follow-up instructions"
    )

    # Custom content
    custom_instructions: Optional[str] = Field(
        None, description="Provider's custom instructions"
    )
    follow_up_date: Optional[str] = Field(
        None, description="Follow-up appointment info"
    )


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
    request: PatientEducationRequest, db: Session = Depends(get_db)
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
    import logging

    logger = logging.getLogger(__name__)

    try:
        logger.info(
            f"Starting patient education document generation for diagnosis_id: {request.diagnosis_id}"
        )

        # Get diagnosis from content library (required for evidence-based content)
        diagnosis = (
            db.query(DiagnosisContentMap).filter_by(id=request.diagnosis_id).first()
        )

        if not diagnosis:
            logger.error(
                f"Diagnosis not found in content library: {request.diagnosis_id}"
            )
            raise HTTPException(
                status_code=404,
                detail=f"Diagnosis '{request.diagnosis_id}' not found in content library. Please select a diagnosis from the available options.",
            )

        logger.info(f"Found diagnosis: {diagnosis.diagnosis_display}")

        # Get MedlinePlus content if requested
        medlineplus_content = None
        if request.include_medlineplus:
            try:
                medlineplus_client = MedlinePlusClient()
                medlineplus_content = medlineplus_client.fetch_content(
                    icd10_code=request.icd10_code, language=request.preferred_language
                )
                logger.info("MedlinePlus content fetched successfully")
            except Exception as e:
                logger.warning(f"Failed to fetch MedlinePlus content: {e}")
                # Continue without MedlinePlus content

        # Build document content with AI enhancement
        logger.info("Building document content...")
        document_content = await _build_document_content(
            request=request,
            diagnosis=diagnosis,
            medlineplus_content=medlineplus_content,
        )
        logger.info(
            f"Document content built with {len(document_content.get('sections', []))} sections"
        )

        # Generate PDF
        logger.info("Generating PDF...")
        pdf_path = _generate_pdf(
            content=document_content,
            patient_name=request.patient_name,
            language=request.preferred_language,
        )
        logger.info(f"PDF generated: {pdf_path}")

        # Generate HTML preview
        logger.info("Generating HTML preview...")
        html_path = _generate_html(
            content=document_content,
            patient_name=request.patient_name,
            language=request.preferred_language,
        )
        logger.info(f"HTML generated: {html_path}")

        # Generate document ID
        document_id = f"PE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        return PatientEducationResponse(
            document_id=document_id,
            pdf_url=f"/api/v1/documents/download/{pdf_path.name}",
            html_preview_url=f"/api/v1/documents/preview/{html_path.name}",
            language=request.preferred_language,
            reading_level=request.reading_level,
            generated_at=datetime.now(),
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(
            f"Error generating patient education document: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to generate document: {str(e)}"
        )


async def _build_document_content(
    request: PatientEducationRequest,
    diagnosis: DiagnosisContentMap,
    medlineplus_content: Optional[dict],
) -> dict:
    """Build structured content for the document with AI-enhanced content generation"""

    content = {
        "title": _translate("Patient Education", request.preferred_language),
        "patient_name": request.patient_name,
        "diagnosis_name": diagnosis.diagnosis_display,
        "sections": [],
    }

    # Condition description (patient-friendly) - Use Claude AI if database content is missing
    if request.include_description:
        description = diagnosis.patient_friendly_description

        # If no patient-friendly description, generate one with Claude AI
        if not description:
            try:
                ai_content = await claude_service.generate_patient_education(
                    condition=diagnosis.diagnosis_display,
                    patient_context={
                        "reading_level": request.reading_level,
                        "care_setting": request.care_setting,
                        "patient_name": request.patient_name,
                    },
                    language=request.preferred_language,
                )
                # Use AI response if available and not empty, otherwise fallback
                ai_response = ai_content.get("response", "")
                description = (
                    ai_response if ai_response else diagnosis.diagnosis_display
                )
            except Exception:
                # Fallback to diagnosis display name if AI fails
                description = diagnosis.diagnosis_display

        content["sections"].append(
            {
                "title": _translate(
                    "What is this condition?", request.preferred_language
                ),
                "content": description,
                "icon": "info-circle",
            }
        )

    # Warning signs
    if request.include_warning_signs and diagnosis.standard_warning_signs:
        content["sections"].append(
            {
                "title": _translate(
                    "When to seek immediate help", request.preferred_language
                ),
                "content": _translate(
                    "Call 911 or go to the emergency room if you have:",
                    request.preferred_language,
                ),
                "bullet_points": diagnosis.standard_warning_signs,
                "icon": "exclamation-triangle",
                "style": "warning",
            }
        )

    # Medications
    if request.include_medications and diagnosis.standard_medications:
        med_content = _format_medications(
            diagnosis.standard_medications, request.preferred_language
        )
        content["sections"].append(
            {
                "title": _translate("Your Medications", request.preferred_language),
                "content": med_content,
                "icon": "pills",
            }
        )

    # Diet and lifestyle
    if request.include_diet and diagnosis.standard_diet_instructions:
        content["sections"].append(
            {
                "title": _translate("Diet and Lifestyle", request.preferred_language),
                "content": diagnosis.standard_diet_instructions,
                "icon": "utensils",
            }
        )

    # MedlinePlus resources
    if request.include_medlineplus and medlineplus_content:
        content["sections"].append(
            {
                "title": _translate("Learn More", request.preferred_language),
                "content": _translate(
                    "For more information, visit these trusted resources:",
                    request.preferred_language,
                ),
                "resources": [
                    {
                        "title": medlineplus_content.get("title"),
                        "url": medlineplus_content.get("url"),
                        "source": "MedlinePlus",
                    }
                ],
                "icon": "book",
            }
        )

    # Follow-up instructions - Use AI for personalized guidance if database content is generic
    if request.include_follow_up:
        follow_up_text = diagnosis.standard_follow_up_instructions

        # If no specific follow-up instructions, generate personalized ones with AI
        if not follow_up_text:
            try:
                ai_followup = await claude_service.generate_patient_education(
                    condition=diagnosis.diagnosis_display,
                    patient_context={
                        "reading_level": request.reading_level,
                        "care_setting": request.care_setting,
                        "patient_name": request.patient_name,
                        "context": "follow-up care instructions",
                    },
                    language=request.preferred_language,
                )
                follow_up_text = ai_followup.get(
                    "response",
                    _translate(
                        "Follow up with your healthcare provider as directed.",
                        request.preferred_language,
                    ),
                )
            except Exception:
                # Fallback to generic instruction
                follow_up_text = _translate(
                    "Follow up with your healthcare provider as directed.",
                    request.preferred_language,
                )

        if request.follow_up_date:
            follow_up_text += f"\n\n{_translate('Your follow-up appointment:', request.preferred_language)} {request.follow_up_date}"

        content["sections"].append(
            {
                "title": _translate("Follow-up Care", request.preferred_language),
                "content": follow_up_text,
                "icon": "calendar-check",
            }
        )

    # Custom instructions
    if request.custom_instructions:
        content["sections"].append(
            {
                "title": _translate(
                    "Special Instructions for You", request.preferred_language
                ),
                "content": request.custom_instructions,
                "icon": "user-md",
                "style": "highlight",
            }
        )

    return content


def _generate_pdf(content: dict, patient_name: str, language: str) -> Path:
    """Generate PDF from document content"""

    # Create output directory if it doesn't exist
    # Use /app/data for persistence on Railway, or local data/ directory for development
    import logging
    import os

    logger = logging.getLogger(__name__)

    # Detect Railway environment by checking for RAILWAY_ENVIRONMENT variable
    is_railway = (
        os.getenv("RAILWAY_ENVIRONMENT") is not None
        or os.getenv("RAILWAY_SERVICE_ID") is not None
    )

    if is_railway:
        # Railway environment with persistent volume
        output_dir = Path("/app/data/generated_documents")
        logger.info(
            f"Railway environment detected, using persistent volume: {output_dir}"
        )
    else:
        # Local development environment
        output_dir = Path("data/generated_documents")
        logger.info(f"Local environment detected, using local directory: {output_dir}")

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory ready: {output_dir}")
    except Exception as e:
        logger.error(f"Failed to create output directory {output_dir}: {e}")
        raise

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
        bottomMargin=72,
    )

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        textColor=colors.HexColor("#1E40AF"),
        spaceAfter=30,
    )
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=16,
        textColor=colors.HexColor("#2563EB"),
        spaceAfter=12,
        spaceBefore=20,
    )
    body_style = ParagraphStyle(
        "CustomBody", parent=styles["BodyText"], fontSize=12, leading=18, spaceAfter=12
    )
    warning_style = ParagraphStyle(
        "Warning",
        parent=styles["BodyText"],
        fontSize=12,
        leading=18,
        textColor=colors.HexColor("#DC2626"),
        leftIndent=20,
        spaceAfter=12,
    )

    # Build PDF content
    story = []

    # Header
    story.append(Paragraph(content["title"], title_style))
    story.append(Paragraph(f"<b>Patient:</b> {patient_name}", body_style))
    story.append(
        Paragraph(f"<b>Diagnosis:</b> {content['diagnosis_name']}", body_style)
    )
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
                story.append(
                    Paragraph(
                        f"• <b>{resource['title']}</b><br/>"
                        f"  {resource['url']}<br/>"
                        f"  <i>Source: {resource['source']}</i>",
                        body_style,
                    )
                )

        story.append(Spacer(1, 0.2 * inch))

    # Footer
    story.append(Spacer(1, 0.5 * inch))
    story.append(
        Paragraph(
            f"<i>Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</i>",
            styles["Normal"],
        )
    )

    # Build PDF
    doc.build(story)

    return filepath


def _generate_html(content: dict, patient_name: str, language: str) -> Path:
    """Generate HTML preview from document content"""
    import logging
    import os

    logger = logging.getLogger(__name__)

    # Detect Railway environment
    is_railway = (
        os.getenv("RAILWAY_ENVIRONMENT") is not None
        or os.getenv("RAILWAY_SERVICE_ID") is not None
    )

    if is_railway:
        output_dir = Path("/app/data/generated_documents")
        logger.info(
            f"Railway environment detected, using persistent volume: {output_dir}"
        )
    else:
        output_dir = Path("data/generated_documents")
        logger.info(f"Local environment detected, using local directory: {output_dir}")

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory ready: {output_dir}")
    except Exception as e:
        logger.error(f"Failed to create output directory {output_dir}: {e}")
        raise

    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"patient_education_{timestamp}.html"
    filepath = output_dir / filename

    # Extract sections into dict for HTML generator
    sections = {}
    for section in content.get("sections", []):
        section_title = section.get("title", "")
        section_content = section.get("content", "")

        # Add bullet points if present
        if "bullet_points" in section and section["bullet_points"]:
            bullet_list = "\n".join(
                [f"• {point}" for point in section["bullet_points"]]
            )
            section_content = f"{section_content}\n\n{bullet_list}"

        sections[section_title] = section_content

    # Generate HTML using our utility
    html_content = generate_patient_education_html(
        patient_name=patient_name,
        diagnosis=content.get("diagnosis_name", ""),
        language=language,
        sections=sections,
        custom_instructions=None,  # Already in sections if present
        follow_up_date=None,  # Already in sections if present
    )

    # Write HTML to file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)

    logger.info(f"HTML preview generated: {filepath}")
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

        formatted.append(f"<b>{med_name}</b><br/>" f"Take {dosage} {frequency}")

    return "<br/><br/>".join(formatted)


def _translate(text: str, language: str) -> str:
    """
    Translate text to specified language.

    Note: For production, integrate with Google Translate API or similar service.
    This provides basic common medical phrases for 15 languages.
    """

    # Common translations for medical education materials
    translations = {
        "es": {  # Spanish
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
            "Take": "Tome",
        },
        "zh": {  # Chinese
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
            "Take": "服用",
        },
        "fr": {  # French
            "Patient Education": "Éducation du Patient",
            "What is this condition?": "Qu'est-ce que cette condition?",
            "When to seek immediate help": "Quand chercher une aide immédiate",
            "Call 911 or go to the emergency room if you have:": "Appelez le 911 ou allez aux urgences si vous avez:",
            "Your Medications": "Vos Médicaments",
            "Diet and Lifestyle": "Régime et Mode de Vie",
            "Learn More": "En Savoir Plus",
            "For more information, visit these trusted resources:": "Pour plus d'informations, visitez ces ressources fiables:",
            "Follow-up Care": "Suivi des Soins",
            "Follow up with your healthcare provider as directed.": "Suivez avec votre fournisseur de soins comme indiqué.",
            "Your follow-up appointment:": "Votre rendez-vous de suivi:",
            "Special Instructions for You": "Instructions Spéciales Pour Vous",
            "No medications prescribed.": "Aucun médicament prescrit.",
            "Take": "Prendre",
        },
        "de": {  # German
            "Patient Education": "Patientenaufklärung",
            "What is this condition?": "Was ist diese Erkrankung?",
            "When to seek immediate help": "Wann sofortige Hilfe suchen",
            "Call 911 or go to the emergency room if you have:": "Rufen Sie 911 an oder gehen Sie zur Notaufnahme, wenn Sie haben:",
            "Your Medications": "Ihre Medikamente",
            "Diet and Lifestyle": "Ernährung und Lebensstil",
            "Learn More": "Mehr Erfahren",
            "For more information, visit these trusted resources:": "Für weitere Informationen besuchen Sie diese vertrauenswürdigen Ressourcen:",
            "Follow-up Care": "Nachsorge",
            "Follow up with your healthcare provider as directed.": "Folgen Sie den Anweisungen Ihres Gesundheitsdienstleisters.",
            "Your follow-up appointment:": "Ihr Folgetermin:",
            "Special Instructions for You": "Spezielle Anweisungen Für Sie",
            "No medications prescribed.": "Keine Medikamente verschrieben.",
            "Take": "Nehmen",
        },
        "pt": {  # Portuguese
            "Patient Education": "Educação do Paciente",
            "What is this condition?": "O que é esta condição?",
            "When to seek immediate help": "Quando procurar ajuda imediata",
            "Call 911 or go to the emergency room if you have:": "Ligue para o 911 ou vá ao pronto-socorro se tiver:",
            "Your Medications": "Seus Medicamentos",
            "Diet and Lifestyle": "Dieta e Estilo de Vida",
            "Learn More": "Saiba Mais",
            "For more information, visit these trusted resources:": "Para mais informações, visite estes recursos confiáveis:",
            "Follow-up Care": "Cuidados de Acompanhamento",
            "Follow up with your healthcare provider as directed.": "Acompanhe com seu profissional de saúde conforme orientado.",
            "Your follow-up appointment:": "Sua consulta de acompanhamento:",
            "Special Instructions for You": "Instruções Especiais Para Você",
            "No medications prescribed.": "Nenhum medicamento prescrito.",
            "Take": "Tomar",
        },
        "ar": {  # Arabic
            "Patient Education": "تثقيف المريض",
            "What is this condition?": "ما هي هذه الحالة؟",
            "When to seek immediate help": "متى تطلب المساعدة الفورية",
            "Call 911 or go to the emergency room if you have:": "اتصل بالرقم 911 أو اذهب إلى غرفة الطوارئ إذا كان لديك:",
            "Your Medications": "أدويتك",
            "Diet and Lifestyle": "النظام الغذائي ونمط الحياة",
            "Learn More": "تعلم المزيد",
            "For more information, visit these trusted resources:": "لمزيد من المعلومات، قم بزيارة هذه الموارد الموثوقة:",
            "Follow-up Care": "الرعاية المتابعة",
            "Follow up with your healthcare provider as directed.": "تابع مع مقدم الرعاية الصحية الخاص بك حسب التوجيهات.",
            "Your follow-up appointment:": "موعد المتابعة الخاص بك:",
            "Special Instructions for You": "تعليمات خاصة لك",
            "No medications prescribed.": "لا توجد أدوية موصوفة.",
            "Take": "خذ",
        },
        "ru": {  # Russian
            "Patient Education": "Обучение Пациентов",
            "What is this condition?": "Что это за состояние?",
            "When to seek immediate help": "Когда обращаться за немедленной помощью",
            "Call 911 or go to the emergency room if you have:": "Звоните 911 или обратитесь в отделение неотложной помощи, если у вас:",
            "Your Medications": "Ваши Лекарства",
            "Diet and Lifestyle": "Диета и Образ Жизни",
            "Learn More": "Узнать Больше",
            "For more information, visit these trusted resources:": "Для получения дополнительной информации посетите эти надежные ресурсы:",
            "Follow-up Care": "Последующий Уход",
            "Follow up with your healthcare provider as directed.": "Наблюдайтесь у своего врача согласно указаниям.",
            "Your follow-up appointment:": "Ваш повторный прием:",
            "Special Instructions for You": "Специальные Инструкции Для Вас",
            "No medications prescribed.": "Лекарства не назначены.",
            "Take": "Принимать",
        },
        "hi": {  # Hindi
            "Patient Education": "रोगी शिक्षा",
            "What is this condition?": "यह स्थिति क्या है?",
            "When to seek immediate help": "तत्काल मदद कब लेनी है",
            "Call 911 or go to the emergency room if you have:": "यदि आपके पास है तो 911 पर कॉल करें या आपातकालीन कक्ष में जाएं:",
            "Your Medications": "आपकी दवाएं",
            "Diet and Lifestyle": "आहार और जीवनशैली",
            "Learn More": "और जानें",
            "For more information, visit these trusted resources:": "अधिक जानकारी के लिए, इन विश्वसनीय संसाधनों पर जाएं:",
            "Follow-up Care": "अनुवर्ती देखभाल",
            "Follow up with your healthcare provider as directed.": "निर्देशानुसार अपने स्वास्थ्य सेवा प्रदाता के साथ फॉलो-अप करें।",
            "Your follow-up appointment:": "आपकी फॉलो-अप अपॉइंटमेंट:",
            "Special Instructions for You": "आपके लिए विशेष निर्देश",
            "No medications prescribed.": "कोई दवा निर्धारित नहीं।",
            "Take": "लें",
        },
        "ja": {  # Japanese
            "Patient Education": "患者教育",
            "What is this condition?": "この状態は何ですか？",
            "When to seek immediate help": "緊急の助けを求めるべき時",
            "Call 911 or go to the emergency room if you have:": "次の症状がある場合は911に電話するか救急室に行ってください：",
            "Your Medications": "あなたの薬",
            "Diet and Lifestyle": "食事とライフスタイル",
            "Learn More": "詳しく学ぶ",
            "For more information, visit these trusted resources:": "詳細については、これらの信頼できるリソースをご覧ください：",
            "Follow-up Care": "フォローアップケア",
            "Follow up with your healthcare provider as directed.": "指示に従って医療提供者とフォローアップしてください。",
            "Your follow-up appointment:": "あなたのフォローアップ予約：",
            "Special Instructions for You": "あなたのための特別な指示",
            "No medications prescribed.": "処方された薬はありません。",
            "Take": "服用",
        },
        "ko": {  # Korean
            "Patient Education": "환자 교육",
            "What is this condition?": "이 상태는 무엇입니까?",
            "When to seek immediate help": "즉시 도움을 구해야 할 때",
            "Call 911 or go to the emergency room if you have:": "다음 증상이 있으면 911에 전화하거나 응급실로 가십시오:",
            "Your Medications": "귀하의 약물",
            "Diet and Lifestyle": "식단 및 생활 방식",
            "Learn More": "더 알아보기",
            "For more information, visit these trusted resources:": "자세한 내용은 다음 신뢰할 수 있는 리소스를 방문하십시오:",
            "Follow-up Care": "후속 관리",
            "Follow up with your healthcare provider as directed.": "지시에 따라 의료 서비스 제공자와 후속 조치를 취하십시오.",
            "Your follow-up appointment:": "귀하의 후속 예약:",
            "Special Instructions for You": "귀하를 위한 특별 지침",
            "No medications prescribed.": "처방된 약이 없습니다.",
            "Take": "복용",
        },
        "vi": {  # Vietnamese
            "Patient Education": "Giáo Dục Bệnh Nhân",
            "What is this condition?": "Tình trạng này là gì?",
            "When to seek immediate help": "Khi nào cần tìm kiếm sự giúp đỡ ngay lập tức",
            "Call 911 or go to the emergency room if you have:": "Gọi 911 hoặc đến phòng cấp cứu nếu bạn có:",
            "Your Medications": "Thuốc Của Bạn",
            "Diet and Lifestyle": "Chế Độ Ăn Uống và Lối Sống",
            "Learn More": "Tìm Hiểu Thêm",
            "For more information, visit these trusted resources:": "Để biết thêm thông tin, hãy truy cập các nguồn đáng tin cậy này:",
            "Follow-up Care": "Chăm Sóc Tiếp Theo",
            "Follow up with your healthcare provider as directed.": "Theo dõi với nhà cung cấp dịch vụ chăm sóc sức khỏe của bạn theo hướng dẫn.",
            "Your follow-up appointment:": "Cuộc hẹn theo dõi của bạn:",
            "Special Instructions for You": "Hướng Dẫn Đặc Biệt Cho Bạn",
            "No medications prescribed.": "Không có thuốc được kê đơn.",
            "Take": "Uống",
        },
        "tl": {  # Tagalog
            "Patient Education": "Edukasyon ng Pasyente",
            "What is this condition?": "Ano ang kondisyon na ito?",
            "When to seek immediate help": "Kailan humingi ng agarang tulong",
            "Call 911 or go to the emergency room if you have:": "Tumawag sa 911 o pumunta sa emergency room kung mayroon ka:",
            "Your Medications": "Ang Iyong mga Gamot",
            "Diet and Lifestyle": "Diyeta at Pamumuhay",
            "Learn More": "Matuto Pa",
            "For more information, visit these trusted resources:": "Para sa higit pang impormasyon, bisitahin ang mga pinagkakatiwalaang mapagkukunan na ito:",
            "Follow-up Care": "Subaybayan ang Pag-aalaga",
            "Follow up with your healthcare provider as directed.": "Subaybayan ang iyong tagapagbigay ng pangangalagang pangkalusugan ayon sa itinuro.",
            "Your follow-up appointment:": "Ang iyong follow-up na appointment:",
            "Special Instructions for You": "Mga Espesyal na Tagubilin Para sa Iyo",
            "No medications prescribed.": "Walang inireresetang gamot.",
            "Take": "Uminom",
        },
        "it": {  # Italian
            "Patient Education": "Educazione del Paziente",
            "What is this condition?": "Cos'è questa condizione?",
            "When to seek immediate help": "Quando cercare aiuto immediato",
            "Call 911 or go to the emergency room if you have:": "Chiama il 911 o vai al pronto soccorso se hai:",
            "Your Medications": "I Tuoi Farmaci",
            "Diet and Lifestyle": "Dieta e Stile di Vita",
            "Learn More": "Scopri di Più",
            "For more information, visit these trusted resources:": "Per ulteriori informazioni, visita queste risorse affidabili:",
            "Follow-up Care": "Assistenza di Follow-up",
            "Follow up with your healthcare provider as directed.": "Fai il follow-up con il tuo operatore sanitario come indicato.",
            "Your follow-up appointment:": "Il tuo appuntamento di follow-up:",
            "Special Instructions for You": "Istruzioni Speciali Per Te",
            "No medications prescribed.": "Nessun farmaco prescritto.",
            "Take": "Prendere",
        },
        "pl": {  # Polish
            "Patient Education": "Edukacja Pacjenta",
            "What is this condition?": "Co to za schorzenie?",
            "When to seek immediate help": "Kiedy szukać natychmiastowej pomocy",
            "Call 911 or go to the emergency room if you have:": "Zadzwoń pod 911 lub udaj się na izbę przyjęć, jeśli masz:",
            "Your Medications": "Twoje Leki",
            "Diet and Lifestyle": "Dieta i Styl Życia",
            "Learn More": "Dowiedz Się Więcej",
            "For more information, visit these trusted resources:": "Aby uzyskać więcej informacji, odwiedź te zaufane zasoby:",
            "Follow-up Care": "Opieka Kontynuacyjna",
            "Follow up with your healthcare provider as directed.": "Skontaktuj się z lekarzem zgodnie z zaleceniami.",
            "Your follow-up appointment:": "Twoja wizyta kontrolna:",
            "Special Instructions for You": "Specjalne Instrukcje Dla Ciebie",
            "No medications prescribed.": "Nie przepisano leków.",
            "Take": "Przyjmować",
        },
    }

    # Get translation for the specified language, fallback to English
    lang_dict = translations.get(language, {})
    return lang_dict.get(text, text)


@router.get("/download/{filename}")
async def download_document(filename: str):
    """Download generated document"""

    import os

    # Use same environment detection as _generate_pdf
    is_railway = (
        os.getenv("RAILWAY_ENVIRONMENT") is not None
        or os.getenv("RAILWAY_SERVICE_ID") is not None
    )

    if is_railway:
        base_dir = Path("/app/data/generated_documents")
    else:
        base_dir = Path("data/generated_documents")

    filepath = base_dir / filename

    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Document not found")

    return FileResponse(
        path=str(filepath), media_type="application/pdf", filename=filename
    )


@router.get("/preview/{filename}")
async def preview_document(filename: str):
    """Preview generated document as HTML"""
    import os

    # Use same environment detection as _generate_pdf
    is_railway = (
        os.getenv("RAILWAY_ENVIRONMENT") is not None
        or os.getenv("RAILWAY_SERVICE_ID") is not None
    )

    if is_railway:
        base_dir = Path("/app/data/generated_documents")
    else:
        base_dir = Path("data/generated_documents")

    filepath = base_dir / filename

    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Document preview not found")

    # Verify it's an HTML file
    if not filename.endswith(".html"):
        raise HTTPException(status_code=400, detail="Invalid preview file format")

    return FileResponse(path=str(filepath), media_type="text/html", filename=filename)
