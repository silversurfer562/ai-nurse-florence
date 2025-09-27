"""
Literature Search Router - AI Nurse Florence
Following External Service Integration and API Design Standards from coding instructions
"""

from fastapi import APIRouter, Query, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from ..services.literature_service import search_pubmed
from ..utils.config import get_educational_banner

router = APIRouter(
    prefix="/literature",
    tags=["medical-information", "literature"],
    responses={
        200: {"description": "Literature search completed successfully"},
        422: {"description": "Query needs clarification"},
        500: {"description": "External service error"}
    }
)

class LiteratureResponse(BaseModel):
    banner: str = Field(default_factory=get_educational_banner)
    query: str
    total_results: Optional[int] = None
    results_summary: Optional[str] = None
    articles: Optional[List[Dict[str, Any]]] = None
    sources: Optional[List[str]] = None
    needs_clarification: Optional[bool] = False

@router.get("/search", response_model=LiteratureResponse)
async def search_literature(
    q: str = Query(..., 
                   description="Medical literature search query",
                   examples=["nursing assessment", "medication safety", "patient care protocols"]),
    max_results: int = Query(10, ge=1, le=50, description="Maximum number of results to return")
):
    """
    Search medical literature following External Service Integration pattern.
    
    Searches PubMed for evidence-based research and clinical studies.
    All responses include educational disclaimers per API Design Standards.
    """
    try:
        result = await search_pubmed(q, max_results=max_results)
        
        if result.get("needs_clarification"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": "Query needs clarification", 
                    "clarification_question": result.get("clarification_question"),
                    "banner": get_educational_banner()
                }
            )
        
        return LiteratureResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Literature search failed: {str(e)}"
        )
