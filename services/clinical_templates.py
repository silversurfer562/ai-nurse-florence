from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel

class TemplateContext(BaseModel):
    nurse_name: Optional[str] = None
    nurse_unit: Optional[str] = None
    patient_name: Optional[str] = None
    patient_id: Optional[str] = None
    patient_age: Optional[int] = None
    primary_diagnosis: Optional[str] = None
    clinical_data: Dict[str, Any] = {}
    evidence_sources: List[str] = []
    custom_fields: Dict[str, Any] = {}

class DocumentType:
    SBAR = "sbar_standard"
    PATIENT_ED = "patient_education_standard"
    EMAIL = "physician_email"
    CE_QA = "continuing_ed_qa"

class ClinicalTemplateEngine:
    def list_templates(self, category: Optional[str] = None):
        templates = [
            {"name": "sbar_standard", "category": "communication", "description": "SBAR Report"},
            {"name": "patient_education_standard", "category": "education", "description": "Patient Education"},
            {"name": "physician_email", "category": "communication", "description": "Physician Email"},
            {"name": "continuing_ed_qa", "category": "education", "description": "CE Q&A"}
        ]
        if category:
            templates = [t for t in templates if t["category"] == category]
        return templates
    
    def get_template_requirements(self, template_name: str):
        requirements = {
            "sbar_standard": {
                "required": ["situation_description", "assessment_findings", "recommendations"],
                "optional": ["background_info", "vital_signs"]
            }
        }
        if template_name not in [t["name"] for t in self.list_templates()]:
            raise ValueError(f"Template {template_name} not found")
        return requirements.get(template_name, {})
    
    def generate_document(self, template_name: str, context: TemplateContext, custom_data: Dict = None):
        # Basic template generation
        content = f"""
# Clinical Document
**Type**: {template_name}
**Generated**: {datetime.utcnow().isoformat()}
**Patient**: {context.patient_name or 'N/A'}

## Content
{custom_data.get('situation_description', '')}
{custom_data.get('assessment_findings', '')}
{custom_data.get('recommendations', '')}
        """
        
        return {
            "success": True,
            "document_type": template_name,
            "title": f"Clinical Document - {template_name}",
            "content": content,
            "metadata": {"generated_at": datetime.utcnow().isoformat()},
            "editable": True,
            "ready_for_use": False
        }

clinical_template_engine = ClinicalTemplateEngine()
