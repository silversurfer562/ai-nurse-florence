"""
Disease Information Router - AI Nurse Florence
Following External Service Integration and API Design Standards from coding instructions
"""

from fastapi import APIRouter, Query, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List

from ..services.disease_service import lookup_disease_info
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


@router.get("/lookup", response_model=DiseaseResponse)
async def lookup_disease(
    q: str = Query(
        ...,
        description="Disease name or condition to look up",
        examples=["hypertension", "diabetes mellitus", "pneumonia"],
    )
):
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
