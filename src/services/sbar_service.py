"""
SBAR Service - AI Nurse Florence
Following Service Layer Architecture for clinical documentation
"""

import logging
from typing import Dict, Any, Optional
from src.utils.config import get_settings
from src.services.base_service import BaseService

# Conditional imports following copilot-instructions.md pattern
try:
    from src.utils.redis_cache import cached
    _has_cache = True
except ImportError:
    _has_cache = False
    def cached(ttl_seconds: int):
        def decorator(func):
            return func
        return decorator

logger = logging.getLogger(__name__)

class SBARService(BaseService):
    """
    SBAR documentation service following Service Layer Architecture.
    Provides clinical documentation support and AI enhancement.
    """
    
    def __init__(self):
        super().__init__()
        self.settings = get_settings()
    
    @cached(ttl_seconds=300) if _has_cache else lambda: lambda f: f
    async def validate_sbar_step(self, step_number: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate SBAR step data following clinical documentation standards.
        
        Args:
            step_number: SBAR step (1-4)
            data: Step data to validate
            
        Returns:
            Validation result with suggestions
        """
        try:
            validation_result = {
                "valid": True,
                "suggestions": [],
                "completeness_score": 0.0,
                "clinical_flags": []
            }
            
            # Step-specific validation
            if step_number == 1:  # Situation
                validation_result = await self._validate_situation_step(data)
            elif step_number == 2:  # Background
                validation_result = await self._validate_background_step(data)
            elif step_number == 3:  # Assessment
                validation_result = await self._validate_assessment_step(data)
            elif step_number == 4:  # Recommendation
                validation_result = await self._validate_recommendation_step(data)
            
            return validation_result
            
        except Exception as e:
            logger.error(f"SBAR validation error: {e}")
            return {"valid": False, "error": str(e)}
    
    async def enhance_sbar_report(self, sbar_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance SBAR report with clinical insights and evidence-based suggestions.
        
        Args:
            sbar_data: Complete SBAR data
            
        Returns:
            Enhanced report with clinical insights
        """
        try:
            enhanced_report = {
                "original_report": sbar_data,
                "clinical_insights": [],
                "evidence_links": [],
                "care_plan_suggestions": [],
                "risk_assessment": {}
            }
            
            # Get OpenAI service for enhancement following Conditional Imports Pattern
            from src.services import get_service
            openai_service = get_service("openai")
            
            if openai_service:
                # AI-powered enhancement
                enhanced_report = await self._ai_enhance_sbar(sbar_data, openai_service)
            else:
                # Rule-based enhancement
                enhanced_report = await self._rule_based_enhance_sbar(sbar_data)
            
            return enhanced_report
            
        except Exception as e:
            logger.error(f"SBAR enhancement error: {e}")
            return {"error": str(e)}
    
    async def _validate_situation_step(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Situation step data."""
        score = 0.0
        suggestions = []
        clinical_flags = []
        
        # Check required fields
        if data.get("patient_condition"):
            score += 0.4
            # Check for urgency indicators
            condition = data["patient_condition"].lower()
            urgent_terms = ["chest pain", "shortness of breath", "altered consciousness", "severe pain"]
            for term in urgent_terms:
                if term in condition:
                    clinical_flags.append(f"Urgent indicator detected: {term}")
        else:
            suggestions.append("Patient condition description is required")
        
        if data.get("immediate_concerns"):
            score += 0.4
        else:
            suggestions.append("Immediate concerns should be specified")
        
        if data.get("vital_signs"):
            score += 0.2
        else:
            suggestions.append("Vital signs would strengthen the situation description")
        
        return {
            "valid": score >= 0.6,
            "completeness_score": score,
            "suggestions": suggestions,
            "clinical_flags": clinical_flags
        }
    
    async def _validate_background_step(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Background step data."""
        score = 0.0
        suggestions = []
        
        if data.get("medical_history"):
            score += 0.5
        else:
            suggestions.append("Medical history is essential for clinical context")
        
        if data.get("current_treatments"):
            score += 0.5
        else:
            suggestions.append("Current treatments/interventions should be documented")
        
        return {
            "valid": score >= 0.5,
            "completeness_score": score,
            "suggestions": suggestions,
            "clinical_flags": []
        }
    
    async def _validate_assessment_step(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Assessment step data."""
        score = 0.0
        suggestions = []
        clinical_flags = []
        
        if data.get("clinical_assessment"):
            score += 0.6
            # Check for clinical red flags
            assessment = data["clinical_assessment"].lower()
            red_flag_terms = ["chest pain", "shortness of breath", "altered mental status", "severe pain"]
            for term in red_flag_terms:
                if term in assessment:
                    clinical_flags.append(f"Clinical attention flag: {term}")
        else:
            suggestions.append("Clinical assessment is critical for SBAR communication")
        
        if data.get("primary_concerns"):
            score += 0.4
        else:
            suggestions.append("Primary concerns help prioritize care needs")
        
        return {
            "valid": score >= 0.6,
            "completeness_score": score,
            "suggestions": suggestions,
            "clinical_flags": clinical_flags
        }
    
    async def _validate_recommendation_step(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Recommendation step data."""
        score = 0.0
        suggestions = []
        clinical_flags = []
        
        if data.get("recommendations"):
            score += 0.5
        else:
            suggestions.append("Specific recommendations are essential for actionable communication")
        
        if data.get("requested_actions"):
            score += 0.3
        else:
            suggestions.append("Clearly state what actions you need from the physician")
        
        if data.get("timeline"):
            score += 0.2
            timeline = data["timeline"]
            if timeline == "Immediate":
                clinical_flags.append("Immediate attention requested - ensure rapid communication path")
        else:
            suggestions.append("Timeline helps prioritize the urgency of response")
        
        return {
            "valid": score >= 0.5,
            "completeness_score": score,
            "suggestions": suggestions,
            "clinical_flags": clinical_flags
        }
    
    async def _ai_enhance_sbar(self, sbar_data: Dict[str, Any], openai_service) -> Dict[str, Any]:
        """AI-powered SBAR enhancement using OpenAI service."""
        # This would integrate with your OpenAI service
        # For now, return rule-based enhancement
        return await self._rule_based_enhance_sbar(sbar_data)
    
    async def _rule_based_enhance_sbar(self, sbar_data: Dict[str, Any]) -> Dict[str, Any]:
        """Rule-based SBAR enhancement for when AI is unavailable."""
        enhanced = {
            "clinical_insights": [
                "SBAR framework ensures structured clinical communication",
                "Complete documentation supports continuity of care",
                "Timely communication improves patient outcomes"
            ],
            "evidence_links": [],
            "care_plan_suggestions": [],
            "risk_assessment": {"overall_risk": "Assessment pending clinical review"}
        }
        
        # Add context-specific insights based on content
        sections = sbar_data.get("sections", {})
        
        if "situation" in sections:
            situation = sections["situation"]
            if any(term in str(situation).lower() for term in ["chest pain", "shortness of breath"]):
                enhanced["clinical_insights"].append(
                    "Cardiac symptoms require immediate assessment and continuous monitoring"
                )
                enhanced["risk_assessment"]["cardiac_risk"] = "Elevated - requires immediate evaluation"
        
        return enhanced

def create_sbar_service() -> Optional[SBARService]:
    """
    Create SBAR service with graceful degradation following Conditional Imports Pattern.
    Returns None if service cannot be initialized.
    """
    try:
        return SBARService()
    except Exception as e:
        logger.warning(f"SBAR service unavailable: {e}")
        return None