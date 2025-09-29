"""
Disease Information Router - AI Nurse Florence
Following External Service Integration and API Design Standards from coding instructions
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Path, Query, status
from pydantic import BaseModel, Field

from ..services.disease_service import lookup_disease_info, search_disease_conditions
from ..utils.config import get_educational_banner

router = APIRouter(
    prefix="/disease",
    tags=["medical-information", "disease"],
    responses={
        200: {"description": "Disease information retrieved successfully"},
        422: {"description": "Query needs clarification"},
        500: {"description": "External service error"},
    },
)


class DiseaseResponse(BaseModel):
    banner: str = Field(default_factory=get_educational_banner)
    query: str
    summary: Optional[str] = None
    description: Optional[str] = None
    symptoms: Optional[List[str]] = None
    sources: Optional[List[str]] = None
    needs_clarification: Optional[bool] = False


class ConditionSuggestion(BaseModel):
    name: str
    mondo_id: str
    description: Optional[str] = None
    synonyms: Optional[List[str]] = None


class ConditionSearchResponse(BaseModel):
    suggestions: List[ConditionSuggestion]
    total_results: int


@router.get("/lookup", response_model=DiseaseResponse)
async def lookup_disease(
    q: str = Query(
        ...,
        description="Disease name or condition to look up",
        examples=["hypertension", "diabetes mellitus", "pneumonia"],
    ),
) -> DiseaseResponse:
    """
    Look up disease information following External Service Integration pattern.

    Provides evidence-based medical information for healthcare professionals.
    All responses include educational disclaimers per API Design Standards.
    """
    try:
        result = await lookup_disease_info(q)

        if result.get("needs_clarification"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": "Query needs clarification",
                    "clarification_question": result.get("clarification_question"),
                    "banner": get_educational_banner(),
                },
            )

        return DiseaseResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Disease lookup failed: {str(e)}",
        )


@router.get("/search", response_model=ConditionSearchResponse)
async def search_conditions(
    q: str = Query(
        ...,
        min_length=2,
        description="Search term for medical conditions (minimum 2 characters)",
        examples=["diab", "hyper", "cancer"],
    ),
    limit: int = Query(
        10,
        ge=1,
        le=50,
        description="Maximum number of suggestions to return"
    )
) -> ConditionSearchResponse:
    """
    Search for medical conditions with autocomplete suggestions.

    Provides real-time search suggestions for guided data entry.
    Returns MONDO disease ontology terms with descriptions and synonyms.
    """
    try:
        results = await search_disease_conditions(q, limit=limit)
        return ConditionSearchResponse(**results)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Condition search failed: {str(e)}",
        )


@router.get("/genes/{condition_id}")
async def get_condition_genes(
    condition_id: str = Path(
        ...,
        description="MONDO ID for the medical condition",
        examples=["MONDO:0005015", "MONDO:0005044"]
    )
):
    """
    Get gene information associated with a medical condition.

    Integrates with MyGene.info to provide genetic information
    related to the specified medical condition.
    """
    try:
        # This would integrate with MyGene.info API
        # For now, return a structured response indicating future integration
        return {
            "condition_id": condition_id,
            "message": "Gene information integration with MyGene.info coming soon",
            "placeholder_genes": [
                {
                    "gene_symbol": "INS",
                    "gene_name": "insulin",
                    "description": "Example gene associated with diabetes",
                    "mygene_url": "https://mygene.info/v3/gene/3630"
                }
            ],
            "integration_note": "Future integration will provide real gene data from MyGene.info API"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gene lookup failed: {str(e)}",
        )
