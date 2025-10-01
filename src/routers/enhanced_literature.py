"""
Enhanced Literature Router - AI Nurse Florence
Phase 4.2: Additional Medical Services

Provides advanced literature search endpoints with smart caching,
evidence-based ranking, and specialty-specific filtering.
"""

import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Query, HTTPException, status, Depends
from pydantic import BaseModel, Field

# Import utilities following conditional imports pattern
try:
    from src.services.enhanced_literature_service import enhanced_literature_service
    from src.utils.api_responses import create_success_response, create_error_response
    from src.utils.auth_dependencies import get_current_user
    _has_dependencies = True
    _literature_service = enhanced_literature_service
except ImportError:
    _has_dependencies = False
    _literature_service = None  # type: ignore
    
    # Mock dependencies for testing
    async def get_current_user() -> Dict[str, Any]:  # type: ignore
        return {"user_id": "mock_user", "role": "user"}
    
    def create_success_response(data: Any) -> Dict[str, Any]:  # type: ignore
        return {"success": True, "data": data}
    
    def create_error_response(message: str, status_code: int = 500, details: Optional[Dict] = None) -> Dict[str, Any]:  # type: ignore
        return {"success": False, "message": message, "details": details}

logger = logging.getLogger(__name__)

# Pydantic models for request/response validation
class LiteratureSearchRequest(BaseModel):
    """Literature search request model."""
    query: str = Field(..., min_length=2, max_length=500, description="Literature search query")
    specialty: Optional[str] = Field(None, description="Medical specialty context")
    max_results: int = Field(10, ge=1, le=50, description="Maximum number of results")
    use_cache: bool = Field(True, description="Whether to use caching")

class EvidenceSummaryRequest(BaseModel):
    """Evidence summary request model."""
    topic: str = Field(..., min_length=2, max_length=200, description="Medical topic for evidence summary")
    specialty: Optional[str] = Field(None, description="Medical specialty context")

# Router setup
router = APIRouter(
    prefix="/literature-enhanced",
    tags=["enhanced-literature"],
    responses={
        401: {"description": "Authentication required"},
        500: {"description": "Internal server error"}
    }
)

@router.get(
    "/search",
    summary="Enhanced literature search",
    description="Search medical literature with intelligent caching, evidence-based ranking, and specialty filtering"
)
async def search_literature_enhanced(
    q: str = Query(..., min_length=2, max_length=500, description="Literature search query"),
    specialty: Optional[str] = Query(None, description="Medical specialty context"),
    max_results: int = Query(10, ge=1, le=50, description="Maximum number of results to return"),
    use_cache: bool = Query(True, description="Whether to use intelligent caching"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Enhanced literature search with smart caching and evidence-based ranking.
    
    Features:
    - Intelligent query processing and enhancement
    - Smart caching with literature-specific strategies
    - Evidence-based result ranking by quality and relevance
    - Medical specialty-aware filtering
    - Citation analysis and impact scoring
    """
    try:
        if not _has_dependencies:
            return create_error_response(
                message="Enhanced literature service not available",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Perform enhanced literature search
        if not _literature_service:
            return create_error_response(
                message="Enhanced literature service not available",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            )
            
        results = await _literature_service.search_literature(
            query=q,
            specialty=specialty,
            max_results=max_results,
            use_cache=use_cache
        )
        
        # Add user context to response
        results["requested_by"] = current_user.get("user_id")
        results["user_specialty"] = current_user.get("specialty")
        
        return create_success_response(results)
        
    except Exception as e:
        logger.error(f"Enhanced literature search failed: {e}")
        return create_error_response(
            message="Literature search failed",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )

@router.post(
    "/search",
    summary="Enhanced literature search (POST)",
    description="Search medical literature using POST request with detailed parameters"
)
async def search_literature_enhanced_post(
    request: LiteratureSearchRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Enhanced literature search using POST request for complex queries.
    Supports all the same features as the GET endpoint with structured input.
    """
    try:
        if not _has_dependencies:
            return create_error_response(
                message="Enhanced literature service not available",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        if not _literature_service:
            return create_error_response(
                message="Enhanced literature service not available",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            )
            
        results = await _literature_service.search_literature(
            query=request.query,
            specialty=request.specialty,
            max_results=request.max_results,
            use_cache=request.use_cache
        )
        
        results["requested_by"] = current_user.get("user_id")
        results["request_method"] = "POST"
        
        return create_success_response(results)
        
    except Exception as e:
        logger.error(f"Enhanced literature search (POST) failed: {e}")
        return create_error_response(
            message="Literature search failed",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )

@router.get(
    "/evidence-summary",
    summary="Get evidence summary for medical topic",
    description="Get comprehensive evidence summary with quality assessment for a medical topic"
)
async def get_evidence_summary(
    topic: str = Query(..., min_length=2, max_length=200, description="Medical topic for evidence summary"),
    specialty: Optional[str] = Query(None, description="Medical specialty context"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get evidence-based summary for a medical topic.
    
    Features:
    - Systematic review and meta-analysis prioritization
    - Evidence quality assessment (1A, 1B, 2A, 2B levels)
    - Clinical guideline integration
    - Evidence-based recommendations
    - Quality metrics and impact factors
    """
    try:
        if not _has_dependencies:
            return create_error_response(
                message="Enhanced literature service not available",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        if not _literature_service:
            return create_error_response(
                message="Enhanced literature service not available",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        summary = await _literature_service.get_evidence_summary(
            topic=topic,
            specialty=specialty
        )
        
        summary["requested_by"] = current_user.get("user_id")
        summary["user_specialty"] = current_user.get("specialty")
        
        return create_success_response(summary)
        
    except Exception as e:
        logger.error(f"Evidence summary failed: {e}")
        return create_error_response(
            message="Evidence summary generation failed",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )

@router.post(
    "/evidence-summary",
    summary="Get evidence summary (POST)",
    description="Get evidence summary using POST request with structured parameters"
)
async def get_evidence_summary_post(
    request: EvidenceSummaryRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get evidence summary using POST request for complex topic analysis.
    """
    try:
        if not _has_dependencies:
            return create_error_response(
                message="Enhanced literature service not available",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        if not _literature_service:
            return create_error_response(
                message="Enhanced literature service not available",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        summary = await _literature_service.get_evidence_summary(
            topic=request.topic,
            specialty=request.specialty
        )
        
        summary["requested_by"] = current_user.get("user_id")
        summary["request_method"] = "POST"
        
        return create_success_response(summary)
        
    except Exception as e:
        logger.error(f"Evidence summary (POST) failed: {e}")
        return create_error_response(
            message="Evidence summary generation failed",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )

@router.get(
    "/specialties",
    summary="Get supported medical specialties",
    description="Get list of supported medical specialties for enhanced filtering"
)
async def get_supported_specialties(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get list of medical specialties supported for enhanced literature filtering.
    """
    specialties = {
        "primary_care": {
            "name": "Primary Care",
            "description": "Family medicine, internal medicine, general practice",
            "keywords": ["primary care", "family medicine", "general practice"]
        },
        "cardiology": {
            "name": "Cardiology",
            "description": "Heart and cardiovascular conditions",
            "keywords": ["cardiac", "cardiovascular", "heart", "cardiology"]
        },
        "oncology": {
            "name": "Oncology", 
            "description": "Cancer care and treatment",
            "keywords": ["cancer", "oncology", "tumor", "malignancy"]
        },
        "neurology": {
            "name": "Neurology",
            "description": "Neurological and brain conditions", 
            "keywords": ["neurology", "neurological", "brain", "nervous system"]
        },
        "pediatrics": {
            "name": "Pediatrics",
            "description": "Children and infant care",
            "keywords": ["pediatric", "children", "infant", "pediatrics"]
        },
        "emergency": {
            "name": "Emergency Medicine",
            "description": "Emergency and critical care",
            "keywords": ["emergency", "critical care", "acute", "trauma"]
        },
        "nursing": {
            "name": "Nursing",
            "description": "Nursing practice and patient care",
            "keywords": ["nursing", "patient care", "clinical practice"]
        },
        "surgery": {
            "name": "Surgery",
            "description": "Surgical procedures and perioperative care",
            "keywords": ["surgery", "surgical", "operative", "perioperative"]
        },
        "psychiatry": {
            "name": "Psychiatry",
            "description": "Mental health and psychiatric conditions",
            "keywords": ["psychiatry", "mental health", "psychiatric"]
        },
        "obstetrics_gynecology": {
            "name": "Obstetrics & Gynecology",
            "description": "Women's health and reproductive medicine",
            "keywords": ["obstetrics", "gynecology", "women's health", "reproductive"]
        }
    }
    
    response = {
        "supported_specialties": specialties,
        "total_specialties": len(specialties),
        "requested_by": current_user.get("user_id"),
        "usage_note": "Use specialty parameter in search requests for enhanced filtering"
    }
    
    return create_success_response(response)

@router.get(
    "/test",
    summary="Test enhanced literature service",
    description="Test endpoint to verify enhanced literature service functionality"
)
async def test_enhanced_literature_service(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Test enhanced literature service functionality."""
    
    system_status: Dict[str, Any] = {
        "enhanced_literature_available": _has_dependencies,
        "dependencies_loaded": _has_dependencies,
        "smart_caching_enabled": bool(_literature_service.cache_enabled if _literature_service else False)
    }
    
    if _has_dependencies and _literature_service:
        # Test a simple search
        try:
            test_result = await _literature_service.search_literature(
                query="diabetes management",
                max_results=1,
                use_cache=False
            )
            system_status["test_search_successful"] = True
            system_status["test_result_count"] = test_result.get("total_results", 0)
        except Exception as e:
            system_status["test_search_successful"] = False
            system_status["test_search_error"] = str(e)
    
    return create_success_response({
        "message": "Enhanced literature service operational",
        "user": current_user.get("user_id"),
        "system_status": system_status,
        "service_features": [
            "Intelligent query processing",
            "Smart caching with similarity matching",
            "Evidence-based result ranking",
            "Medical specialty filtering",
            "Citation analysis and impact scoring",
            "Evidence quality assessment"
        ]
    })
