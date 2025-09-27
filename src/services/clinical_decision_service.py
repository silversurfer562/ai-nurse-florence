"""
Clinical Decision Service - AI Nurse Florence
Following Service Layer Architecture from coding instructions
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from ..utils.config import get_settings, get_educational_banner
from .openai_client import clinical_decision_support, is_openai_available

logger = logging.getLogger(__name__)

class ClinicalDecisionService:
    """
    Clinical decision support service following Service Layer Architecture.
    Provides AI-assisted clinical guidance with educational disclaimers.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.banner = get_educational_banner()
        self.openai_available = is_openai_available()

    async def get_nursing_interventions(
        self,
        patient_condition: str,
        severity: str = "moderate",
        comorbidities: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Compatibility wrapper used by the router.

        Maps the older `get_nursing_interventions` call to the newer
        `get_nursing_recommendations` implementation so both interfaces work.
        """
        # Use comorbidities as nursing concerns if provided
        nursing_concerns = comorbidities or []
        # Map severity to a priority level
        priority = "routine"
        if severity and severity.lower() in ("urgent", "severe", "critical"):
            priority = "urgent" if severity.lower() == "severe" else "critical"

        result = await self.get_nursing_recommendations(
            patient_condition=patient_condition,
            nursing_concerns=nursing_concerns,
            priority_level=priority
        )

        # Normalize result to expected router response shape
        # Normalize nursing_interventions to a single string (router expects a string)
        nursing = result.get("nursing_interventions", [])
        if isinstance(nursing, list):
            nursing_str = "; ".join(nursing)
        elif isinstance(nursing, str):
            nursing_str = nursing
        else:
            nursing_str = str(nursing)

        normalized = {
            "nursing_interventions": nursing_str,
            "evidence_level": result.get("evidence_level", "Level VII - Expert Opinion"),
            "safety_considerations": result.get("safety_considerations", []),
            "clinical_context": result.get("clinical_context") or {"concerns": nursing_concerns}
        }

        return normalized
        
    async def get_nursing_recommendations(
        self,
        patient_condition: str,
        nursing_concerns: List[str],
        priority_level: str = "routine"
    ) -> Dict[str, Any]:
        """
        Get nursing care recommendations following Clinical Decision Support pattern.
        
        Args:
            patient_condition: Current patient condition/diagnosis
            nursing_concerns: List of nursing concerns or observations
            priority_level: Priority level (routine, urgent, critical)
        
        Returns:
            Dict with nursing recommendations and care priorities
        """
        
        # Prepare clinical context
        patient_data = {
            "condition": patient_condition,
            "nursing_concerns": nursing_concerns,
            "priority": priority_level,
            "timestamp": datetime.now().isoformat()
        }
        
        clinical_question = f"What are the priority nursing interventions for a patient with {patient_condition}? Nursing concerns include: {', '.join(nursing_concerns)}"
        
        if self.openai_available:
            # Use AI-powered clinical decision support
            result = await clinical_decision_support(
                patient_data=patient_data,
                clinical_question=clinical_question,
                context="nursing_care"
            )
            
            # Add nursing-specific structure
            if "error" not in result:
                result.update({
                    "nursing_interventions": self._extract_interventions(result.get("response", "")),
                    "monitoring_parameters": self._extract_monitoring(result.get("response", "")),
                    "care_priority": priority_level,
                    "nursing_note": "AI-assisted nursing guidance - verify with nursing protocols and patient assessment"
                })
                # Ensure expected fields exist for downstream callers/tests
                result.setdefault("patient_condition", patient_condition)
                result.setdefault("nursing_concerns", nursing_concerns)
                result.setdefault("evidence_level", result.get("evidence_level", "Level VII - Expert Opinion"))
                result.setdefault("safety_considerations", result.get("safety_considerations", []))
            
            return result
        else:
            # Fallback to educational nursing guidance
            return self._create_nursing_stub(patient_condition, nursing_concerns, priority_level)
    
    async def assess_care_escalation(
        self,
        patient_data: Dict[str, Any],
        current_interventions: List[str],
        clinical_indicators: List[str]
    ) -> Dict[str, Any]:
        """
        Assess need for care escalation following Clinical Decision Support pattern.
        
        Args:
            patient_data: Current patient status and vital signs
            current_interventions: Interventions currently in place
            clinical_indicators: Clinical indicators suggesting escalation
        
        Returns:
            Dict with escalation recommendations and urgency level
        """
        
        clinical_question = f"Based on clinical indicators: {', '.join(clinical_indicators)}, should care be escalated? Current interventions: {', '.join(current_interventions)}"
        
        if self.openai_available:
            result = await clinical_decision_support(
                patient_data=patient_data,
                clinical_question=clinical_question,
                context="care_escalation"
            )
            
            # Add escalation-specific fields
            if "error" not in result:
                result.update({
                    "escalation_recommended": self._assess_escalation_need(clinical_indicators),
                    "urgency_level": self._determine_urgency(clinical_indicators),
                    "escalation_timeline": self._get_escalation_timeline(clinical_indicators),
                    "escalation_note": "Escalation assessment based on clinical indicators - final decision requires bedside evaluation"
                })
            
            return result
        else:
            # Fallback escalation guidance
            return self._create_escalation_stub(patient_data, clinical_indicators)
    
    def _extract_interventions(self, ai_response: str) -> List[str]:
        """Extract nursing interventions from AI response."""
        # Simple extraction logic - in production would use more sophisticated NLP
        interventions = []
        lines = ai_response.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['monitor', 'assess', 'administer', 'provide', 'ensure']):
                if len(line) > 10 and len(line) < 200:  # Reasonable intervention length
                    interventions.append(line)
        
        return interventions[:5]  # Return top 5 interventions
    
    def _extract_monitoring(self, ai_response: str) -> List[str]:
        """Extract monitoring parameters from AI response."""
        monitoring = []
        lines = ai_response.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['vital signs', 'blood pressure', 'temperature', 'oxygen', 'pain', 'mental status']):
                if len(line) > 5 and len(line) < 150:
                    monitoring.append(line)
        
        return monitoring[:3]  # Return top 3 monitoring parameters
    
    def _assess_escalation_need(self, clinical_indicators: List[str]) -> bool:
        """Simple rule-based escalation assessment."""
        critical_indicators = ['chest pain', 'difficulty breathing', 'altered mental status', 'severe pain', 'bleeding']
        
        for indicator in clinical_indicators:
            if any(critical in indicator.lower() for critical in critical_indicators):
                return True
        
        return len(clinical_indicators) >= 3  # Multiple concerns may warrant escalation
    
    def _determine_urgency(self, clinical_indicators: List[str]) -> str:
        """Determine urgency level based on clinical indicators."""
        emergency_indicators = ['chest pain', 'difficulty breathing', 'unresponsive', 'severe bleeding']
        urgent_indicators = ['altered mental status', 'severe pain', 'fever >101.5', 'low blood pressure']
        
        for indicator in clinical_indicators:
            indicator_lower = indicator.lower()
            if any(emergency in indicator_lower for emergency in emergency_indicators):
                return "emergency"
            elif any(urgent in indicator_lower for urgent in urgent_indicators):
                return "urgent"
        
        return "routine"
    
    def _get_escalation_timeline(self, clinical_indicators: List[str]) -> str:
        """Get recommended escalation timeline."""
        urgency = self._determine_urgency(clinical_indicators)
        
        if urgency == "emergency":
            return "Immediate - call physician now"
        elif urgency == "urgent":
            return "Within 15-30 minutes"
        else:
            return "Within 1-2 hours or per facility protocol"
    
    def _create_nursing_stub(self, condition: str, concerns: List[str], priority: str) -> Dict[str, Any]:
        """Create educational nursing guidance stub."""
        return {
            "banner": self.banner,
            "patient_condition": condition,
            "nursing_concerns": concerns,
            "priority_level": priority,
            "nursing_interventions": [
                "Assess patient condition and vital signs",
                "Review nursing care plan and protocols",
                "Document findings and interventions",
                "Monitor for changes in patient status",
                "Communicate with healthcare team as needed"
            ],
            "monitoring_parameters": [
                "Vital signs per protocol",
                "Pain assessment",
                "Mental status and level of consciousness"
            ],
            "service_note": "Educational nursing guidance - OpenAI service unavailable",
            "nursing_note": "This is educational content - always follow facility protocols and nursing standards"
        }
    
    def _create_escalation_stub(self, patient_data: Dict[str, Any], indicators: List[str]) -> Dict[str, Any]:
        """Create educational escalation guidance stub."""
        return {
            "banner": self.banner,
            "clinical_indicators": indicators,
            "escalation_recommended": len(indicators) >= 2,
            "urgency_level": "routine",
            "escalation_timeline": "Per facility protocol",
            "service_note": "Educational escalation guidance - AI decision support unavailable",
            "escalation_note": "Always follow facility escalation protocols and use clinical judgment"
        }

# Factory function following Conditional Imports Pattern
def get_clinical_decision_service() -> Optional[ClinicalDecisionService]:
    """
    Get clinical decision service with graceful degradation.
    Returns None if service cannot be initialized.
    """
    try:
        return ClinicalDecisionService()
    except Exception as e:
        logger.warning(f"Clinical decision service unavailable: {e}")
        return None

# Service instance for dependency injection
_clinical_decision_service: Optional[ClinicalDecisionService] = None

def create_clinical_decision_service() -> Optional[ClinicalDecisionService]:
    """Create clinical decision service instance following Service Layer Architecture."""
    global _clinical_decision_service
    
    if _clinical_decision_service is None:
        _clinical_decision_service = get_clinical_decision_service()
    
    return _clinical_decision_service
