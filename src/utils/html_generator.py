"""
HTML Generation Utility for Patient Education Documents
Generates clean, accessible HTML previews
Following Service Layer Architecture
"""

from typing import Dict, List, Optional


def generate_patient_education_html(
    patient_name: str,
    diagnosis: str,
    language: str = "en",
    sections: Optional[Dict[str, str]] = None,
    custom_instructions: Optional[str] = None,
    follow_up_date: Optional[str] = None,
) -> str:
    """
    Generate HTML preview for patient education document

    Args:
        patient_name: Patient name for header
        diagnosis: Primary diagnosis
        language: Language code (en, es, zh)
        sections: Dict of section titles and content
        custom_instructions: Provider's custom instructions
        follow_up_date: Follow-up appointment date

    Returns:
        Complete HTML document string
    """
    sections = sections or {}

    # Language-specific labels
    labels = _get_language_labels(language)

    html = f"""
<!DOCTYPE html>
<html lang="{language}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{labels['title']}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header {{
            border-bottom: 3px solid #2563eb;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        h1 {{
            color: #1e40af;
            font-size: 28px;
            margin-bottom: 10px;
        }}
        .patient-info {{
            color: #64748b;
            font-size: 14px;
        }}
        h2 {{
            color: #2563eb;
            font-size: 22px;
            margin-top: 30px;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid #e5e7eb;
        }}
        h3 {{
            color: #1e40af;
            font-size: 18px;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        .section {{
            margin-bottom: 25px;
        }}
        .warning {{
            background-color: #fef2f2;
            border-left: 4px solid #dc2626;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .warning h3 {{
            color: #dc2626;
            margin-top: 0;
        }}
        .info {{
            background-color: #eff6ff;
            border-left: 4px solid #2563eb;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .info h3 {{
            color: #2563eb;
            margin-top: 0;
        }}
        ul {{
            padding-left: 25px;
        }}
        li {{
            margin-bottom: 8px;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e5e7eb;
            font-size: 12px;
            color: #64748b;
            text-align: center;
        }}
        .disclaimer {{
            background-color: #fefce8;
            border: 1px solid #eab308;
            padding: 15px;
            margin-top: 20px;
            border-radius: 4px;
            font-size: 13px;
        }}
        @media print {{
            body {{
                background-color: white;
            }}
            .container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{labels['title']}</h1>
            <div class="patient-info">
                <strong>{labels['patient']}:</strong> {patient_name}<br>
                <strong>{labels['diagnosis']}:</strong> {diagnosis}<br>
                <strong>{labels['date']}:</strong> {_get_current_date()}
            </div>
        </div>
"""

    # Add sections
    for section_title, section_content in sections.items():
        is_warning = (
            "warning" in section_title.lower() or "emergency" in section_title.lower()
        )
        section_class = "warning" if is_warning else "section"

        html += f"""
        <div class="{section_class}">
            <h2>{section_title}</h2>
            {_format_content(section_content)}
        </div>
"""

    # Add custom instructions if provided
    if custom_instructions:
        html += f"""
        <div class="info">
            <h3>{labels['custom_instructions']}</h3>
            <p>{custom_instructions}</p>
        </div>
"""

    # Add follow-up information if provided
    if follow_up_date:
        html += f"""
        <div class="info">
            <h3>{labels['follow_up']}</h3>
            <p>{follow_up_date}</p>
        </div>
"""

    # Add disclaimer
    html += f"""
        <div class="disclaimer">
            <strong>{labels['disclaimer_title']}:</strong> {labels['disclaimer_text']}
        </div>

        <div class="footer">
            <p>{labels['footer']}</p>
            <p>🤖 {labels['generated']} AI Nurse Florence</p>
        </div>
    </div>
</body>
</html>
"""

    return html


def _get_language_labels(language: str) -> Dict[str, str]:
    """Get language-specific labels"""
    labels = {
        "en": {
            "title": "Patient Education Document",
            "patient": "Patient",
            "diagnosis": "Diagnosis",
            "date": "Date",
            "custom_instructions": "Your Provider's Instructions",
            "follow_up": "Follow-Up Appointment",
            "disclaimer_title": "Important",
            "disclaimer_text": "This document is for educational purposes only. Always follow your healthcare provider's specific instructions. If you have questions or concerns, contact your doctor or nurse.",
            "footer": "Educational use only — not medical advice. No PHI stored.",
            "generated": "Generated with",
        },
        "es": {
            "title": "Documento de Educación del Paciente",
            "patient": "Paciente",
            "diagnosis": "Diagnóstico",
            "date": "Fecha",
            "custom_instructions": "Instrucciones de su Proveedor",
            "follow_up": "Cita de Seguimiento",
            "disclaimer_title": "Importante",
            "disclaimer_text": "Este documento es solo para fines educativos. Siempre siga las instrucciones específicas de su proveedor de atención médica. Si tiene preguntas o inquietudes, comuníquese con su médico o enfermera.",
            "footer": "Solo para uso educativo — no es consejo médico. No se almacena PHI.",
            "generated": "Generado con",
        },
        "zh": {
            "title": "患者教育文档",
            "patient": "患者",
            "diagnosis": "诊断",
            "date": "日期",
            "custom_instructions": "您的医疗服务提供者的指示",
            "follow_up": "随访预约",
            "disclaimer_title": "重要提示",
            "disclaimer_text": "本文件仅用于教育目的。请始终遵循您的医疗保健提供者的具体指示。如有疑问或担忧，请联系您的医生或护士。",
            "footer": "仅供教育使用 — 不是医疗建议。不存储PHI。",
            "generated": "生成工具",
        },
    }

    return labels.get(language, labels["en"])


def _format_content(content: str) -> str:
    """Format content with HTML paragraphs and lists"""
    # Split into lines
    lines = content.strip().split("\n")

    formatted = []
    in_list = False

    for line in lines:
        line = line.strip()
        if not line:
            if in_list:
                formatted.append("</ul>")
                in_list = False
            continue

        # Check if line is a list item
        if line.startswith("•") or line.startswith("-") or line.startswith("*"):
            if not in_list:
                formatted.append("<ul>")
                in_list = True
            # Remove bullet and format
            item = line[1:].strip()
            formatted.append(f"<li>{item}</li>")
        else:
            if in_list:
                formatted.append("</ul>")
                in_list = False
            formatted.append(f"<p>{line}</p>")

    if in_list:
        formatted.append("</ul>")

    return "\n".join(formatted)


def _get_current_date() -> str:
    """Get current date in readable format"""
    from datetime import datetime

    return datetime.now().strftime("%B %d, %Y")


def generate_medication_guide_html(
    medication_name: str,
    dosage: str,
    purpose: Optional[str] = None,
    side_effects: Optional[List[str]] = None,
    warnings: Optional[List[str]] = None,
    instructions: Optional[str] = None,
) -> str:
    """
    Generate HTML preview for medication guide

    Args:
        medication_name: Name of medication
        dosage: Dosage information
        purpose: What the medication is for
        side_effects: List of possible side effects
        warnings: List of warnings
        instructions: Special instructions

    Returns:
        Complete HTML document string
    """
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Medication Guide - {medication_name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
            color: white;
            padding: 25px;
            border-radius: 8px 8px 0 0;
            margin: -30px -30px 30px -30px;
        }}
        h1 {{
            margin: 0;
            font-size: 32px;
        }}
        .dosage {{
            font-size: 18px;
            margin-top: 10px;
            opacity: 0.9;
        }}
        h2 {{
            color: #2563eb;
            font-size: 22px;
            margin-top: 30px;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid #e5e7eb;
        }}
        .warning-box {{
            background-color: #fef2f2;
            border-left: 4px solid #dc2626;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        ul {{
            padding-left: 25px;
        }}
        li {{
            margin-bottom: 8px;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e5e7eb;
            font-size: 12px;
            color: #64748b;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{medication_name}</h1>
            <div class="dosage"><strong>Dosage:</strong> {dosage}</div>
        </div>
"""

    if purpose:
        html += f"""
        <div>
            <h2>What This Medication Is For</h2>
            <p>{purpose}</p>
        </div>
"""

    if instructions:
        html += f"""
        <div>
            <h2>How to Take This Medication</h2>
            <p>{instructions}</p>
        </div>
"""

    if warnings:
        html += """
        <div class="warning-box">
            <h2 style="margin-top: 0; color: #dc2626;">Important Warnings</h2>
            <ul>
"""
        for warning in warnings:
            html += f"                <li>{warning}</li>\n"
        html += """
            </ul>
        </div>
"""

    if side_effects:
        html += """
        <div>
            <h2>Possible Side Effects</h2>
            <ul>
"""
        for effect in side_effects:
            html += f"                <li>{effect}</li>\n"
        html += """
            </ul>
        </div>
"""

    html += """
        <div class="footer">
            <p>Educational use only — not medical advice. No PHI stored.</p>
            <p>🤖 Generated with AI Nurse Florence</p>
        </div>
    </div>
</body>
</html>
"""

    return html
