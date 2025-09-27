"""
Medical Data Service - AI Nurse Florence
Provides comprehensive medical information lookup with caching and external API integration
Following Service Layer Architecture with Conditional Imports Pattern
"""

import logging
import httpx
from typing import Dict, Optional, Any, Tuple
from datetime import datetime

# Conditional imports following project patterns
try:
    from utils.redis_cache import cached
    _has_caching = True
except ImportError:
    _has_caching = False
    def cached(ttl_seconds: int):
        """Fallback decorator when Redis not available"""
        def decorator(func):
            return func
        return decorator

try:
    from src.utils.metrics import record_cache_hit, record_service_call
    _has_metrics = True
except ImportError:
    _has_metrics = False
    def record_cache_hit(cache_key: str) -> None:
        pass
    def record_service_call(service_name: str, success: bool = True) -> None:
        pass

try:
    from services.prompt_enhancement import enhance_prompt
    _has_prompt_enhancement = True
except ImportError:
    _has_prompt_enhancement = False
    def enhance_prompt(query: str, context: str) -> Tuple[str, bool, str]:
        return query, False, ""

try:
    from services.openai_client import get_openai_client
    _has_openai = True
except ImportError:
    _has_openai = False
    def get_openai_client():
        return None

# Add model selector import following Conditional Imports Pattern
try:
    from services.model_selector import select_model_for_context, get_enterprise_model
    _has_model_selector = True
except ImportError:
    _has_model_selector = False
    def select_model_for_context(context: str, complexity: str = "medium") -> str:
        return "gpt-4-turbo-preview"  # Fallback
    
    def get_enterprise_model(task_type: str) -> str:
        return "gpt-4"

from utils.exceptions import ExternalServiceException, ServiceException
from utils.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Educational disclaimer banner following API Design Standards
EDU_BANNER = "Draft for clinician review — not medical advice. No PHI stored."

# Configuration following Configuration Management patterns
LIVE = getattr(settings, 'USE_LIVE', False)
MYDISEASE_BASE_URL = "https://mydisease.info/v1"
TIMEOUT_SECONDS = 30

# Add enterprise configuration
try:
    from utils.config import get_settings
    settings = get_settings()
    ENTERPRISE_MODE = getattr(settings, 'ENTERPRISE_CHATGPT_MODE', False)
    CHATGPT_STORE_MODE = getattr(settings, 'CHATGPT_STORE_MODE', False)
except ImportError:
    ENTERPRISE_MODE = False
    CHATGPT_STORE_MODE = False

class MedicalDataService:
    """
    Medical data lookup service with external API integration
    Following Service Layer Architecture with caching and error handling
    """
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=TIMEOUT_SECONDS)
        self.openai_client = get_openai_client() if _has_openai else None
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    @cached(ttl_seconds=3600)
    async def lookup_disease_info(self, term: str) -> Dict[str, Any]:
        """
        Lookup comprehensive disease information with caching
        
        Args:
            term: Medical term or disease name to search
            
        Returns:
            Dict containing disease information with educational banner
            
        Raises:
            ExternalServiceException: When external API calls fail
            ServiceException: For service-level errors
        """
        logger.info(f"Looking up disease information for: {term}")
        
        # Enhance prompt for clarity following prompt enhancement pattern
        if _has_prompt_enhancement:
            effective_term, needs_clarification, clarification_question = enhance_prompt(
                term, "disease_lookup"
            )
        else:
            effective_term = term
            needs_clarification = False
            clarification_question = ""
        
        if needs_clarification:
            logger.info(f"Query needs clarification: {term}")
            return {
                "banner": EDU_BANNER,
                "query": term,
                "needs_clarification": True,
                "clarification_question": clarification_question,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Record metrics if available
        if _has_metrics:
            record_service_call("mydisease_api")
        
        # External API integration with conditional loading
        if LIVE:
            try:
                result = await self._fetch_from_mydisease(effective_term)
                
                # Enhance with AI-generated summary if OpenAI available
                if self.openai_client and result.get("data"):
                    enhanced_result = await self._enhance_with_ai_summary(result, effective_term)
                    return enhanced_result
                
                return result
                
            except Exception as e:
                logger.error(f"External service failed for {term}: {str(e)}")
                if _has_metrics:
                    record_service_call("mydisease_api", success=False)
                
                # Graceful degradation - return stub response
                return await self._create_stub_response(effective_term)
        
        # Development/fallback stub response
        logger.info(f"Using stub response for: {term}")
        return await self._create_stub_response(effective_term)

    @cached(ttl_seconds=7200)
    async def lookup_drug_info(self, drug_name: str) -> Dict[str, Any]:
        """
        Lookup comprehensive drug information with caching
        
        Args:
            drug_name: Drug name to search
            
        Returns:
            Dict containing drug information with safety warnings
        """
        logger.info(f"Looking up drug information for: {drug_name}")
        
        # Enhance query
        if _has_prompt_enhancement:
            effective_term, needs_clarification, clarification_question = enhance_prompt(
                drug_name, "drug_lookup"
            )
        else:
            effective_term = drug_name
            needs_clarification = False
            clarification_question = ""
            
        if needs_clarification:
            return {
                "banner": EDU_BANNER,
                "query": drug_name,
                "needs_clarification": True,
                "clarification_question": clarification_question,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        if _has_metrics:
            record_service_call("drug_lookup")
        
        if LIVE:
            try:
                # Use MyDisease.info drug endpoint
                result = await self._fetch_drug_from_mydisease(effective_term)
                return result
            except Exception as e:
                logger.error(f"Drug lookup failed for {drug_name}: {str(e)}")
                return await self._create_drug_stub_response(effective_term)
        
        return await self._create_drug_stub_response(effective_term)

    @cached(ttl_seconds=1800)
    async def lookup_symptoms(self, symptoms: str) -> Dict[str, Any]:
        """
        Lookup potential conditions based on symptoms
        
        Args:
            symptoms: Comma-separated symptom list
            
        Returns:
            Dict containing potential conditions with educational disclaimers
        """
        logger.info(f"Looking up conditions for symptoms: {symptoms}")
        
        # Critical: This is for educational purposes only
        educational_warning = (
            "EDUCATIONAL ONLY - This is not diagnostic advice. "
            "Always consult qualified healthcare professionals for medical diagnosis. "
            "No PHI stored."
        )
        
        if _has_metrics:
            record_service_call("symptoms_lookup")
        
        if LIVE and self.openai_client:
            try:
                result = await self._ai_symptom_analysis(symptoms)
                result["banner"] = educational_warning
                return result
            except Exception as e:
                logger.error(f"AI symptom analysis failed: {str(e)}")
                return await self._create_symptom_stub_response(symptoms, educational_warning)
        
        return await self._create_symptom_stub_response(symptoms, educational_warning)

    async def _fetch_from_mydisease(self, term: str) -> Dict[str, Any]:
        """Fetch disease information from MyDisease.info API"""
        try:
            # Search for disease
            search_url = f"{MYDISEASE_BASE_URL}/query"
            search_params = {
                "q": term,
                "size": 5,
                "fields": "mondo.definition,disgenet.gene_name,pharmgkb.id"
            }
            
            search_response = await self.client.get(search_url, params=search_params)
            search_response.raise_for_status()
            search_data = search_response.json()
            
            if not search_data.get("hits"):
                return await self._create_stub_response(term, no_results=True)
            
            # Get detailed info for top hit
            disease_id = search_data["hits"][0].get("_id")
            if disease_id:
                detail_url = f"{MYDISEASE_BASE_URL}/disease/{disease_id}"
                detail_response = await self.client.get(detail_url)
                detail_response.raise_for_status()
                detail_data = detail_response.json()
                
                return self._format_mydisease_response(detail_data, term)
            
            return await self._create_stub_response(term)
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching from MyDisease.info: {e}")
            raise ExternalServiceException(
                "MyDisease.info API request failed",
                "mydisease_api"
            )
        except Exception as e:
            logger.error(f"Unexpected error in MyDisease.info lookup: {e}")
            raise ServiceException(f"Disease lookup failed: {str(e)}")

    async def _fetch_drug_from_mydisease(self, drug_name: str) -> Dict[str, Any]:
        """Fetch drug information from MyDisease.info drug endpoint"""
        try:
            search_url = f"{MYDISEASE_BASE_URL}/query"
            search_params = {
                "q": f"pharmgkb.chemicals.name:{drug_name}",
                "size": 3,
                "fields": "pharmgkb.chemicals.name,pharmgkb.chemicals.external_vocabulary"
            }
            
            response = await self.client.get(search_url, params=search_params)
            response.raise_for_status()
            data = response.json()
            
            return self._format_drug_response(data, drug_name)
            
        except Exception as e:
            logger.error(f"Drug lookup error: {e}")
            raise ExternalServiceException(
                "Drug information lookup failed",
                "mydisease_drug_api"
            )

    async def _enhance_with_ai_summary(self, result: Dict[str, Any], term: str) -> Dict[str, Any]:
        """Enhance medical data with AI-generated summary"""
        if not self.openai_client:
            return result
            
        try:
            # Use Enterprise ChatGPT model selection
            if ENTERPRISE_MODE or CHATGPT_STORE_MODE:
                model = get_enterprise_model("medical_summary") if _has_model_selector else "gpt-4"
            else:
                model = select_model_for_context("medical_summary", "basic") if _has_model_selector else "gpt-4-turbo-preview"
            
            prompt = f"""
            Provide a concise clinical summary for healthcare professionals about: {term}
            
            Based on this data: {result.get('data', {})}
            
            Focus on:
            - Key clinical features
            - Common presentations  
            - Important considerations for nurses
            
            Keep response under 200 words. Include educational disclaimer.
            """
            
            response = await self.openai_client.chat.completions.acreate(
                model=model,  # Enterprise ChatGPT compatible
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.3
            )
            
            ai_summary = response.choices[0].message.content
            
            result["ai_summary"] = ai_summary
            result["enhanced_by_ai"] = True
            result["model_used"] = model
            result["enterprise_mode"] = ENTERPRISE_MODE
            
            return result
            
        except Exception as e:
            logger.error(f"AI enhancement failed: {e}")
            return result

    async def _ai_symptom_analysis(self, symptoms: str) -> Dict[str, Any]:
        """AI-powered symptom analysis for educational purposes"""
        if not self.openai_client:
            raise ServiceException("AI service not available")
        
        # Use Enterprise ChatGPT for advanced analysis
        if ENTERPRISE_MODE or CHATGPT_STORE_MODE:
            model = get_enterprise_model("symptom_analysis") if _has_model_selector else "gpt-4"
        else:
            model = select_model_for_context("symptom_analysis", "advanced") if _has_model_selector else "gpt-4-turbo-preview"
            
        prompt = f"""
        Educational symptom analysis for healthcare professionals:
        
        Symptoms: {symptoms}
        
        Provide comprehensive analysis with:
        1. Possible conditions to consider (3-5) with likelihood reasoning
        2. Red flag symptoms that require immediate attention
        3. Additional questions for systematic assessment
        4. Next steps for evaluation with clinical reasoning
        
        Use advanced clinical reasoning and pattern recognition.
        
        CRITICAL: This is educational only, not diagnostic advice.
        Include appropriate medical disclaimers.
        """
        
        try:
            response = await self.openai_client.chat.completions.acreate(
                model=model,  # Enterprise ChatGPT model
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.2
            )
            
            analysis = response.choices[0].message.content
            
            return {
                "query": symptoms,
                "analysis": analysis,
                "type": "symptom_analysis",
                "ai_generated": True,
                "model_used": model,
                "enterprise_mode": ENTERPRISE_MODE,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"AI symptom analysis failed: {e}")
            raise ServiceException("AI symptom analysis unavailable")

    def _format_mydisease_response(self, data: Dict[str, Any], original_query: str) -> Dict[str, Any]:
        """Format MyDisease.info API response following response standards"""
        formatted_data = {
            "query": original_query,
            "disease_id": data.get("_id"),
            "definition": data.get("mondo", {}).get("definition"),
            "associated_genes": data.get("disgenet", {}).get("gene_name", []),
            "pharmgkb_id": data.get("pharmgkb", {}).get("id"),
            "source": "MyDisease.info",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return {
            "banner": EDU_BANNER,
            "data": formatted_data,
            "success": True
        }

    def _format_drug_response(self, data: Dict[str, Any], drug_name: str) -> Dict[str, Any]:
        """Format drug information response"""
        hits = data.get("hits", [])
        
        if not hits:
            return {
                "banner": EDU_BANNER,
                "query": drug_name,
                "data": {"message": "No drug information found"},
                "success": True
            }
        
        formatted_drugs = []
        for hit in hits:
            chemicals = hit.get("pharmgkb", {}).get("chemicals", [])
            for chemical in chemicals:
                if chemical.get("name", "").lower() == drug_name.lower():
                    formatted_drugs.append({
                        "name": chemical.get("name"),
                        "external_vocabulary": chemical.get("external_vocabulary", [])
                    })
        
        return {
            "banner": EDU_BANNER,
            "query": drug_name,
            "data": {
                "drugs": formatted_drugs,
                "source": "MyDisease.info PharmGKB"
            },
            "success": True,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _create_stub_response(self, term: str, no_results: bool = False) -> Dict[str, Any]:
        """Create stub response for development/fallback"""
        if no_results:
            message = f"No results found for '{term}'"
            stub_data = {"message": message}
        else:
            stub_data = {
                "definition": f"Educational information about {term} would appear here in live mode.",
                "clinical_notes": "This is a development stub response.",
                "associated_genes": ["GENE1", "GENE2"],
                "source": "Development stub"
            }
        
        return {
            "banner": EDU_BANNER,
            "query": term,
            "data": stub_data,
            "success": True,
            "is_stub": True,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _create_drug_stub_response(self, drug_name: str) -> Dict[str, Any]:
        """Create stub response for drug information"""
        return {
            "banner": EDU_BANNER,
            "query": drug_name,
            "data": {
                "name": drug_name,
                "class": "Sample drug class",
                "indications": ["Sample indication 1", "Sample indication 2"],
                "contraindications": ["Sample contraindication"],
                "nursing_considerations": [
                    "Monitor vital signs",
                    "Assess for adverse reactions",
                    "Patient education required"
                ],
                "source": "Development stub"
            },
            "success": True,
            "is_stub": True,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _create_symptom_stub_response(self, symptoms: str, warning: str) -> Dict[str, Any]:
        """Create stub response for symptom analysis"""
        return {
            "banner": warning,
            "query": symptoms, 
            "data": {
                "analysis": f"Educational analysis of symptoms '{symptoms}' would appear here in live mode with AI.",
                "possible_conditions": [
                    "Condition A (educational example)",
                    "Condition B (educational example)",
                    "Condition C (educational example)"
                ],
                "red_flags": [
                    "Severe symptom X requires immediate attention",
                    "Symptom Y combined with Z needs urgent evaluation"
                ],
                "assessment_questions": [
                    "Duration of symptoms?",
                    "Associated factors?",
                    "Previous medical history?"
                ],
                "next_steps": [
                    "Complete physical assessment",
                    "Consider diagnostic tests",
                    "Consult with physician"
                ],
                "source": "Development stub"
            },
            "success": True,
            "is_stub": True,
            "timestamp": datetime.utcnow().isoformat()
        }

# Service factory following dependency injection pattern
_medical_service_instance: Optional[MedicalDataService] = None

async def get_medical_service() -> MedicalDataService:
    """
    Get medical service instance with dependency injection pattern
    Following Service Layer Architecture
    """
    global _medical_service_instance
    
    if _medical_service_instance is None:
        _medical_service_instance = MedicalDataService()
    
    return _medical_service_instance

# Convenience functions for direct usage
async def lookup_disease_info(term: str) -> Dict[str, Any]:
    """Convenience function for disease lookup"""
    async with MedicalDataService() as service:
        return await service.lookup_disease_info(term)

async def lookup_drug_info(drug_name: str) -> Dict[str, Any]:
    """Convenience function for drug lookup"""
    async with MedicalDataService() as service:
        return await service.lookup_drug_info(drug_name)

async def lookup_symptoms(symptoms: str) -> Dict[str, Any]:
    """Convenience function for symptom analysis"""
    async with MedicalDataService() as service:
        return await service.lookup_symptoms(symptoms)