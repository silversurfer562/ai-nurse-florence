"""
MedlinePlus Integration API Endpoints

Provides MedlinePlus patient education content for diagnoses.
Includes caching, multi-language support, and fallback URLs.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database import get_db
from src.integrations.medlineplus import MedlinePlusClient, MedlinePlusContentEnricher
from src.models.content_settings import DiagnosisContentMap, MedlinePlusCache

router = APIRouter(prefix="/medlineplus", tags=["MedlinePlus"])


# Response models
class MedlinePlusContentResponse(BaseModel):
    """MedlinePlus patient education content"""

    icd10_code: str
    disease_name: str
    title: str
    url: str
    summary: Optional[str]
    language: str
    source: str
    cached: bool


@router.get("/by-icd10/{icd10_code}", response_model=MedlinePlusContentResponse)
async def get_medlineplus_by_icd10(
    icd10_code: str,
    language: str = Query("en", regex="^(en|es)$", description="Language: en or es"),
    force_refresh: bool = Query(False, description="Force refresh from API"),
    db: Session = Depends(get_db),
):
    """
    Get MedlinePlus patient education content for an ICD-10 code.

    **Example:** GET /api/v1/medlineplus/by-icd10/E11.9?language=en
    """
    # Find diagnosis in Tier 1
    diagnosis = db.query(DiagnosisContentMap).filter_by(icd10_code=icd10_code).first()
    disease_name = diagnosis.diagnosis_display if diagnosis else "Unknown condition"

    # Create enricher
    enricher = MedlinePlusContentEnricher(db)

    # Fetch content
    content = enricher.enrich_diagnosis(
        diagnosis_id=icd10_code,
        icd10_code=icd10_code,
        disease_name=disease_name,
        language=language,
        force_refresh=force_refresh,
    )

    if not content:
        raise HTTPException(
            status_code=404, detail=f"No content found for {icd10_code}"
        )

    return {
        "icd10_code": icd10_code,
        "disease_name": disease_name,
        "title": content.get("title", ""),
        "url": content.get("url", ""),
        "summary": content.get("summary", ""),
        "language": language,
        "source": content.get("source", "MedlinePlus"),
        "cached": "cached" in content.get("source", "").lower(),
    }


@router.get("/cache/stats")
async def get_cache_stats(db: Session = Depends(get_db)):
    """Get MedlinePlus cache statistics"""
    from sqlalchemy import func

    total = db.query(MedlinePlusCache).count()
    by_language = (
        db.query(MedlinePlusCache.language, func.count(MedlinePlusCache.icd10_code))
        .group_by(MedlinePlusCache.language)
        .all()
    )

    return {
        "total_cached": total,
        "by_language": {lang: count for lang, count in by_language},
    }


@router.get("/health")
async def health_check():
    """Health check for MedlinePlus API"""
    client = MedlinePlusClient()
    try:
        test_content = client.fetch_content("E11.9", "en")
        api_status = "operational" if test_content else "degraded"
    except Exception:
        api_status = "unavailable"

    return {"status": "healthy", "medlineplus_api": api_status, "cache_enabled": True}
