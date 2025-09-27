"""
Medical Literature Router - AI Nurse Florence
Following Router Organization pattern with PubMed integration
"""

from fastapi import APIRouter, Query, Path, HTTPException, status
from typing import Optional, List
from pydantic import BaseModel, Field

from src.services import get_service
from src.models.schemas import BaseResponse

# Educational banner following coding instructions
EDU_BANNER = "Draft for clinician review — not medical advice. No PHI stored."

router = APIRouter(
    prefix="/api/v1/literature",
    tags=["medical-literature"],
    responses={
        404: {"description": "No literature found"},
        500: {"description": "PubMed service error"}
    }
)

class LiteratureResponse(BaseResponse):
    """Medical literature response following API Design Standards."""
    banner: str = Field(default=EDU_BANNER)
    query: str = Field(..., description="Search query")
    articles: List[dict] = Field(default_factory=list, description="PubMed articles")
    total_results: int = Field(default=0, description="Total articles available")

@router.get(
    "/search",
    response_model=LiteratureResponse,
    summary="Search medical literature",
    description="Search PubMed for relevant medical literature. Educational use only.",
    responses={
        200: {
            "description": "Literature search completed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "banner": EDU_BANNER,
                            "query": "diabetes management",
                            "articles": [
                                {
                                    "title": "Diabetes Management Guidelines",
                                    "authors": ["Smith J", "Johnson A"],
                                    "journal": "Diabetes Care",
                                    "year": "2024",
                                    "pmid": "12345678"
                                }
                            ],
                            "total_results": 150
                        }
                    }
                }
            }
        }
    }
)
async def search_literature(
    q: str = Query(
        ...,
        description="Medical search terms",
        min_length=2,
        max_length=200,
        examples={
            "diabetes management": {"summary": "Search diabetes care literature"},
            "hypertension treatment": {"summary": "Search blood pressure treatment studies"},
            "nursing interventions": {"summary": "Search nursing care research"}
        }
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of articles to return"
    )
):
    """
    Search medical literature through PubMed.
    
    Following Service Layer Architecture:
    - Uses service registry for PubMed integration
    - Implements educational disclaimers
    - Standardized error handling
    """
    try:
        # Get service through registry (Conditional Imports Pattern)
        pubmed_service = get_service('pubmed')
        if not pubmed_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Literature search service temporarily unavailable"
            )
        
        # Call service layer
        result = await pubmed_service.search_literature(q, limit=limit)
        
        return {
            "success": True,
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching literature: {str(e)}"
        )

@router.get(
    "/article/{pmid}",
    response_model=dict,
    summary="Get article details",
    description="Retrieve detailed information for a specific PubMed article."
)
async def get_article_details(
    pmid: str = Path(
        ...,
        description="PubMed ID of the article",
        pattern="^[0-9]+$",
        examples=["12345678", "34567890"]
    )
):
    """Get detailed article information by PMID following API Design Standards."""
    try:
        pubmed_service = get_service('pubmed')
        if not pubmed_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Article service temporarily unavailable"
            )
        
        result = await pubmed_service.get_article_details(pmid)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Article not found: {pmid}"
            )
        
        return {
            "success": True,
            "data": {
                "banner": EDU_BANNER,
                **result
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving article: {str(e)}"
        )
