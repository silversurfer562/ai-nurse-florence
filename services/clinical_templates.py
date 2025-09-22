"""
AI Nurse Florence - Clinical Document Template Engine
Provides template-based responses for nursing documentation, continuing education, and professional communication.
"""

from typing import Dict, List, Optional, Any, Literal
from enum import Enum
from pydantic import BaseModel, Field
from jinja2 import Template, Environment, DictLoader
import json
from datetime import datetime
import re

class DocumentType(str, Enum):
    """Types of clinical documents that can be generated"""
    SBAR_REPORT = "sbar_report"
    PATIENT_EDUCATION = "patient_education" 
    PHYSICIAN_EMAIL = "physician_email"
    CARE_PLAN = "care_plan"
    INCIDENT_REPORT = "incident_report"
    DISCHARGE_SUMMARY = "discharge_summary"
    MEDICATION_ADMINISTRATION = "medication_admin"
    ASSESSMENT_NOTE = "assessment_note"
    CONTINUING_ED_RESPONSE = "continuing_ed"
    TEAM_COMMUNICATION = "team_communication"

class TemplateContext(BaseModel):
    """Context data for document generation"""
    nurse_name: Optional[str] = None
    nurse_unit: Optional[str] = None
    patient_id: Optional[str] = None
    patient_name: Optional[str] = None
    patient_age: Optional[int] = None
    primary_diagnosis: Optional[str] = None
    clinical_data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    evidence_sources: List[str] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)

class ClinicalTemplate(BaseModel):
    """Structured clinical document template"""
    name: str
    document_type: DocumentType
    title: str
    template_content: str
    required_fields: List[str]
    optional_fields: List[str] = Field(default_factory=list)
    evidence_based: bool = True
    professional_tone: bool = True
    includes_disclaimer: bool = True
    category: str = "general"

class TemplateEngine:
    """Clinical document template engine with evidence-based content generation"""
    
    def __init__(self):
        self.templates = self._load_clinical_templates()
        self.jinja_env = Environment(loader=DictLoader({}))
        self._setup_filters()
    
    def _setup_filters(self):
        """Custom Jinja2 filters for clinical content"""
        
        def format_vital_signs(vitals: Dict[str, Any]) -> str:
            """Format vital signs professionally"""
            if not vitals:
                return "Vital signs: Not recorded"
            
            formatted = []
            if 'bp_systolic' in vitals and 'bp_diastolic' in vitals:
                formatted.append(f"BP: {vitals['bp_systolic']}/{vitals['bp_diastolic']} mmHg")
            if 'heart_rate' in vitals:
                formatted.append(f"HR: {vitals['heart_rate']} bpm")
            if 'respiratory_rate' in vitals:
                formatted.append(f"RR: {vitals['respiratory_rate']} rpm")
            if 'temperature' in vitals:
                formatted.append(f"Temp: {vitals['temperature']}°F")
            if 'oxygen_saturation' in vitals:
                formatted.append(f"O2 Sat: {vitals['oxygen_saturation']}%")
                
            return ", ".join(formatted)
        
        def format_timestamp(dt: datetime) -> str:
            """Format timestamp for clinical documentation"""
            return dt.strftime("%Y-%m-%d %H:%M")
        
        def evidence_citation(sources: List[str]) -> str:
            """Format evidence sources as citations"""
            if not sources:
                return ""
            citations = [f"[{i+1}] {source}" for i, source in enumerate(sources)]
            return "\n\nEvidence Sources:\n" + "\n".join(citations)
        
        self.jinja_env.filters['vital_signs'] = format_vital_signs
        self.jinja_env.filters['timestamp'] = format_timestamp
        self.jinja_env.filters['evidence'] = evidence_citation

    def _load_clinical_templates(self) -> Dict[str, ClinicalTemplate]:
        """Load all clinical document templates"""
        templates = {}
        
        # SBAR Report Template
        templates['sbar_standard'] = ClinicalTemplate(
            name="sbar_standard",
            document_type=DocumentType.SBAR_REPORT,
            title="SBAR Communication Report",
            template_content="""
**SBAR REPORT**
Date/Time: {{ timestamp | timestamp }}
From: {{ nurse_name }}, {{ nurse_unit }}
To: {{ recipient | default('Attending Physician') }}

**SITUATION:**
Patient: {{ patient_name }} ({{ patient_id }})
Age: {{ patient_age }} years
Primary Diagnosis: {{ primary_diagnosis }}
Current concern: {{ situation_description }}

**BACKGROUND:**
{{ background_info }}
Relevant history: {{ relevant_history | default('See chart for complete history') }}
Current medications: {{ current_medications | default('See MAR') }}

**ASSESSMENT:**
Vital Signs: {{ clinical_data.vitals | vital_signs }}
Current status: {{ assessment_findings }}
Clinical concerns: {{ clinical_concerns }}

**RECOMMENDATION:**
{{ recommendations }}
{{ urgent_actions | default('') }}

---
*This communication supports continuing education and evidence-based nursing practice.*
{{ evidence_sources | evidence }}
            """.strip(),
            required_fields=["patient_name", "situation_description", "assessment_findings", "recommendations"],
            optional_fields=["patient_id", "patient_age", "primary_diagnosis", "background_info", "relevant_history"],
            category="communication"
        )
        
        # Patient Education Template
        templates['patient_education_standard'] = ClinicalTemplate(
            name="patient_education_standard", 
            document_type=DocumentType.PATIENT_EDUCATION,
            title="Patient Education Material",
            template_content="""
**{{ education_topic | upper }}**
*Patient Education Handout*

**What You Need to Know:**
{{ main_information }}

**Important Instructions:**
{{ instructions }}

**Warning Signs to Watch For:**
{{ warning_signs }}

**When to Contact Your Healthcare Team:**
{{ contact_criteria }}

**Additional Resources:**
{{ additional_resources | default('Ask your nurse or healthcare provider for more information.') }}

---
*Prepared by: {{ nurse_name }}, {{ nurse_unit }}*
*Date: {{ timestamp | timestamp }}*

**IMPORTANT:** This information is for educational purposes as part of your continuing care. Always follow your specific treatment plan and contact your healthcare provider with questions.

{{ evidence_sources | evidence }}
            """.strip(),
            required_fields=["education_topic", "main_information", "instructions", "warning_signs", "contact_criteria"],
            optional_fields=["additional_resources"],
            category="education"
        )
        
        # Physician Email Template
        templates['physician_email'] = ClinicalTemplate(
            name="physician_email",
            document_type=DocumentType.PHYSICIAN_EMAIL,
            title="Professional Communication to Physician",
            template_content="""
Subject: {{ email_subject | default('Patient Update - ' + patient_name) }}

Dear Dr. {{ physician_name | default('[Physician Name]') }},

I am writing to update you regarding {{ patient_name }} ({{ patient_id }}) in {{ nurse_unit }}.

**Clinical Update:**
{{ clinical_update }}

**Current Assessment:**
Vital Signs: {{ clinical_data.vitals | vital_signs }}
{{ current_assessment }}

**Concerns/Questions:**
{{ concerns_questions }}

**Actions Taken:**
{{ actions_taken | default('Per standing orders and unit protocols') }}

Please advise on next steps or if you would like to evaluate the patient.

Thank you for your collaboration in this patient's care.

Best regards,
{{ nurse_name }}
Registered Nurse, {{ nurse_unit }}
{{ contact_info | default('Available via secure messaging or unit phone') }}

---
*This communication supports evidence-based collaborative care.*
{{ evidence_sources | evidence }}
            """.strip(),
            required_fields=["patient_name", "clinical_update", "current_assessment", "concerns_questions"],
            optional_fields=["patient_id", "physician_name", "actions_taken", "contact_info"],
            category="communication"
        )
        
        # Continuing Education Response Template
        templates['continuing_ed_qa'] = ClinicalTemplate(
            name="continuing_ed_qa",
            document_type=DocumentType.CONTINUING_ED_RESPONSE,
            title="Continuing Education Response",
            template_content="""
**CLINICAL QUESTION:** {{ clinical_question }}

**EVIDENCE-BASED ANSWER:**
{{ evidence_answer }}

**KEY CLINICAL POINTS:**
{{ key_points }}

**PRACTICAL APPLICATION:**
{{ practical_application }}

**RELATED CONSIDERATIONS:**
{{ related_considerations | default('Always follow your facility protocols and consult with your healthcare team as appropriate.') }}

**PROFESSIONAL DEVELOPMENT:**
This response supports your continuing education and evidence-based practice development.

{{ evidence_sources | evidence }}

---
*Generated: {{ timestamp | timestamp }}*
*For: {{ nurse_name | default('Healthcare Professional') }}*
            """.strip(),
            required_fields=["clinical_question", "evidence_answer", "key_points", "practical_application"],
            optional_fields=["related_considerations"],
            category="education"
        )
        
        # Care Plan Template
        templates['care_plan'] = ClinicalTemplate(
            name="care_plan",
            document_type=DocumentType.CARE_PLAN,
            title="Nursing Care Plan",
            template_content="""
**NURSING CARE PLAN**
Patient: {{ patient_name }} ({{ patient_id }})
Primary Diagnosis: {{ primary_diagnosis }}
Date: {{ timestamp | timestamp }}
Nurse: {{ nurse_name }}

**PRIORITY NURSING DIAGNOSES:**
{{ nursing_diagnoses }}

**GOALS:**
{{ patient_goals }}

**INTERVENTIONS:**
{{ nursing_interventions }}

**EVALUATION CRITERIA:**
{{ evaluation_criteria }}

**PATIENT/FAMILY EDUCATION:**
{{ patient_education_plan }}

**DISCHARGE PLANNING:**
{{ discharge_planning | default('To be assessed closer to discharge') }}

---
*This care plan supports evidence-based nursing practice and continuing professional development.*
{{ evidence_sources | evidence }}
            """.strip(),
            required_fields=["patient_name", "primary_diagnosis", "nursing_diagnoses", "patient_goals", "nursing_interventions", "evaluation_criteria"],
            optional_fields=["patient_id", "patient_education_plan", "discharge_planning"],
            category="care_planning"
        )
        
        return templates
    
    def generate_document(
        self, 
        template_name: str, 
        context: TemplateContext,
        custom_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate a clinical document from template"""
        
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        template_config = self.templates[template_name]
        
        # Prepare template context
        template_data = context.dict()
        if custom_data:
            template_data.update(custom_data)
        
        # Check required fields
        missing_fields = []
        for field in template_config.required_fields:
            if field not in template_data or not template_data[field]:
                missing_fields.append(field)
        
        if missing_fields:
            return {
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}",
                "required_fields": template_config.required_fields,
                "template_name": template_name
            }
        
        # Generate document
        try:
            jinja_template = Template(template_config.template_content)
            jinja_template.environment = self.jinja_env
            generated_content = jinja_template.render(**template_data)
            
            return {
                "success": True,
                "document_type": template_config.document_type.value,
                "title": template_config.title,
                "content": generated_content,
                "metadata": {
                    "template_name": template_name,
                    "generated_at": datetime.now().isoformat(),
                    "nurse_name": context.nurse_name,
                    "patient_id": context.patient_id,
                    "evidence_based": template_config.evidence_based,
                    "category": template_config.category
                },
                "editable": True,
                "ready_for_use": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Template generation failed: {str(e)}",
                "template_name": template_name
            }
    
    def list_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available templates, optionally filtered by category"""
        templates_list = []
        
        for name, template in self.templates.items():
            if category and template.category != category:
                continue
                
            templates_list.append({
                "name": name,
                "title": template.title,
                "document_type": template.document_type.value,
                "category": template.category,
                "required_fields": template.required_fields,
                "optional_fields": template.optional_fields,
                "evidence_based": template.evidence_based
            })
        
        return templates_list
    
    def get_template_requirements(self, template_name: str) -> Dict[str, Any]:
        """Get requirements for a specific template"""
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        template = self.templates[template_name]
        return {
            "name": template_name,
            "title": template.title,
            "document_type": template.document_type.value,
            "required_fields": template.required_fields,
            "optional_fields": template.optional_fields,
            "category": template.category,
            "field_descriptions": self._get_field_descriptions(template_name)
        }
    
    def _get_field_descriptions(self, template_name: str) -> Dict[str, str]:
        """Get user-friendly descriptions for template fields"""
        field_descriptions = {
            # Common fields
            "patient_name": "Patient's full name",
            "patient_id": "Patient ID or medical record number",
            "patient_age": "Patient's age in years",
            "primary_diagnosis": "Primary medical diagnosis",
            "clinical_question": "The clinical question you want answered",
            "evidence_answer": "Evidence-based answer to the clinical question",
            "key_points": "Key clinical points to remember",
            "practical_application": "How to apply this in practice",
            
            # SBAR specific
            "situation_description": "Brief description of the current situation",
            "background_info": "Relevant background information",
            "assessment_findings": "Your clinical assessment findings",
            "recommendations": "Your recommendations for action",
            
            # Patient education specific
            "education_topic": "Main topic of the patient education",
            "main_information": "Key information the patient needs to know",
            "instructions": "Specific instructions for the patient",
            "warning_signs": "Signs that warrant immediate attention",
            "contact_criteria": "When to contact healthcare providers",
            
            # Communication specific
            "clinical_update": "Summary of clinical changes or updates",
            "current_assessment": "Current clinical assessment",
            "concerns_questions": "Specific concerns or questions for the physician",
            "physician_name": "Name of the receiving physician"
        }
        
        template = self.templates[template_name]
        relevant_descriptions = {}
        
        for field in template.required_fields + template.optional_fields:
            if field in field_descriptions:
                relevant_descriptions[field] = field_descriptions[field]
            else:
                relevant_descriptions[field] = f"Please provide {field.replace('_', ' ')}"
        
        return relevant_descriptions

# Initialize global template engine
clinical_template_engine = TemplateEngine()
