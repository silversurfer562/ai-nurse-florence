"""
Clinical decision support service
Evidence-based nursing interventions and risk assessment
"""

import logging
from typing import Dict, Any, List, Optional
from ..models.schemas import (
    ClinicalDecisionRequest, 
    ClinicalDecisionResponse,
    SeverityLevel,
    CareSetting,
    EvidenceLevel
)
from ..utils.redis_cache import cached
from ..utils.exceptions import ServiceException, ValidationException
from .openai_client import clinical_decision_support, is_openai_available

class ClinicalDecisionService:
    """Core clinical decision support service"""
    
    def __init__(self):
        self.evidence_database = self._load_evidence_database()
    
    @cached(ttl_seconds=3600, key_prefix="clinical_decision")
    async def get_nursing_interventions(
        self, 
        request: ClinicalDecisionRequest
    ) -> ClinicalDecisionResponse:
        """
        Generate evidence-based nursing interventions
        Combines rule-based logic with AI enhancement
        """
        try:
            # Validate input
            if not request.patient_condition.strip():
                raise ValidationException(
                    "patient_condition", 
                    request.patient_condition, 
                    "Patient condition cannot be empty"
                )
            
            # Get base interventions from evidence database
            base_interventions = self._get_base_interventions(request)
            
            # Enhance with AI if available
            ai_enhanced = await self._enhance_with_ai(request)
            
            # Combine and format interventions
            interventions = self._combine_interventions(base_interventions, ai_enhanced)
            
            # Get safety considerations
            safety_considerations = self._get_safety_considerations(request)
            
            # Determine evidence level
            evidence_level = self._determine_evidence_level(request.patient_condition)
            
            return ClinicalDecisionResponse(
                nursing_interventions=interventions,
                evidence_level=evidence_level,
                safety_considerations=safety_considerations,
                clinical_context={
                    "condition": request.patient_condition,
                    "severity": request.severity,
                    "care_setting": request.care_setting,
                    "ai_enhanced": ai_enhanced is not None
                }
            )
            
        except Exception as e:
            logging.error(f"Clinical decision service error: {e}")
            if isinstance(e, (ValidationException, ServiceException)):
                raise
            raise ServiceException(f"Failed to generate clinical decision: {str(e)}")
    
    def _load_evidence_database(self) -> Dict[str, Any]:
        """Load evidence-based intervention database"""
        return {
            "heart_failure": {
                "interventions": [
                    "Monitor daily weights and I&O",
                    "Assess for signs of fluid overload",
                    "Position patient in semi-Fowler's position",
                    "Monitor oxygen saturation and respiratory status",
                    "Administer medications as ordered (ACE inhibitors, diuretics)",
                    "Provide low-sodium diet education"
                ],
                "evidence_level": EvidenceLevel.LEVEL_II,
                "monitoring": ["Daily weight", "Vital signs q4h", "Lung sounds", "Edema assessment"]
            },
            "diabetes": {
                "interventions": [
                    "Monitor blood glucose levels as ordered",
                    "Assess feet for wounds or circulation issues",
                    "Provide diabetes education and self-management support",
                    "Monitor for signs of hypo/hyperglycemia",
                    "Coordinate with dietitian for meal planning",
                    "Encourage regular physical activity as appropriate"
                ],
                "evidence_level": EvidenceLevel.LEVEL_I,
                "monitoring": ["Blood glucose", "HbA1c", "Foot inspection", "Weight"]
            },
            "copd": {
                "interventions": [
                    "Monitor respiratory status and oxygen saturation",
                    "Encourage pursed-lip breathing techniques",
                    "Position for optimal lung expansion",
                    "Assess for signs of respiratory distress",
                    "Provide bronchodilator therapy as ordered",
                    "Educate on smoking cessation if applicable"
                ],
                "evidence_level": EvidenceLevel.LEVEL_II,
                "monitoring": ["O2 saturation", "Respiratory rate", "Breath sounds", "Peak flow"]
            },
            "pain": {
                "interventions": [
                    "Assess pain using appropriate pain scale",
                    "Implement non-pharmacological pain management",
                    "Administer analgesics as ordered",
                    "Monitor for side effects of pain medications",
                    "Position for comfort and support",
                    "Provide patient education on pain management"
                ],
                "evidence_level": EvidenceLevel.LEVEL_III,
                "monitoring": ["Pain scores", "Functional status", "Sleep quality", "Medication effects"]
            }
        }
    
    def _get_base_interventions(self, request: ClinicalDecisionRequest) -> Dict[str, Any]:
        """Get base interventions from evidence database"""
        condition_key = self._normalize_condition(request.patient_condition)
        
        # Look for matching condition in evidence database
        for key, data in self.evidence_database.items():
            if key in condition_key or condition_key in key:
                return data
        
        # Default interventions for unknown conditions
        return {
            "interventions": [
                "Complete comprehensive assessment",
                "Monitor vital signs per protocol", 
                "Assess pain and comfort level",
                "Provide patient and family education",
                "Coordinate with interdisciplinary team",
                "Document findings and interventions"
            ],
            "evidence_level": EvidenceLevel.LEVEL_VII,
            "monitoring": ["Vital signs", "General assessment", "Patient response"]
        }
    
    async def _enhance_with_ai(self, request: ClinicalDecisionRequest) -> Optional[str]:
        """Enhance interventions with AI if available"""
        if not await is_openai_available():
            return None
        
        try:
            return await clinical_decision_support(
                patient_condition=request.patient_condition,
                severity=request.severity.value,
                care_setting=request.care_setting.value,
                additional_context=request.additional_context
            )
        except Exception as e:
            logging.warning(f"AI enhancement failed: {e}")
            return None
    
    def _combine_interventions(
        self, 
        base_interventions: Dict[str, Any], 
        ai_enhanced: Optional[str]
    ) -> str:
        """Combine base and AI-enhanced interventions"""
        interventions = base_interventions["interventions"]
        
        # Format base interventions
        formatted = "**Evidence-Based Nursing Interventions:**\n\n"
        for i, intervention in enumerate(interventions, 1):
            formatted += f"{i}. {intervention}\n"
        
        # Add monitoring parameters
        if "monitoring" in base_interventions:
            formatted += "\n**Monitoring Parameters:**\n"
            for param in base_interventions["monitoring"]:
                formatted += f"• {param}\n"
        
        # Add AI enhancement if available
        if ai_enhanced:
            formatted += f"\n**Additional Clinical Guidance:**\n{ai_enhanced}"
        
        return formatted
    
    def _get_safety_considerations(self, request: ClinicalDecisionRequest) -> List[str]:
        """Get safety considerations based on condition and severity"""
        base_safety = [
            "Verify patient allergies and contraindications",
            "Consider individual patient factors and comorbidities",
            "Follow institutional protocols and guidelines",
            "Document all assessments and interventions"
        ]
        
        # Add severity-specific considerations
        if request.severity == SeverityLevel.CRITICAL:
            base_safety.extend([
                "Monitor continuously for deterioration",
                "Ensure rapid response team availability",
                "Consider ICU-level monitoring"
            ])
        elif request.severity == SeverityLevel.SEVERE:
            base_safety.extend([
                "Increase monitoring frequency",
                "Have emergency medications readily available"
            ])
        
        # Add care setting considerations
        if request.care_setting == CareSetting.HOME_HEALTH:
            base_safety.extend([
                "Ensure caregiver competency",
                "Verify emergency contact information",
                "Assess home environment safety"
            ])
        
        return base_safety
    
    def _determine_evidence_level(self, condition: str) -> EvidenceLevel:
        """Determine evidence level for condition"""
        condition_key = self._normalize_condition(condition)
        
        for key, data in self.evidence_database.items():
            if key in condition_key or condition_key in key:
                return data.get("evidence_level", EvidenceLevel.LEVEL_VII)
        
        return EvidenceLevel.LEVEL_VII
    
    def _normalize_condition(self, condition: str) -> str:
        """Normalize condition name for matching"""
        return condition.lower().replace(" ", "_").replace("-", "_")

# Global service instance
_clinical_service = None

def get_clinical_decision_service() -> ClinicalDecisionService:
    """Get clinical decision service singleton"""
    global _clinical_service
    if _clinical_service is None:
        _clinical_service = ClinicalDecisionService()
    return _clinical_service
