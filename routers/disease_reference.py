"""
Disease Reference API Endpoints

Two-tier diagnosis system API:
- Tier 1: Full diagnosis library (DiagnosisContentMap) -> /api/v1/content-settings/diagnoses
- Tier 2: Reference database (DiseaseReference) -> /api/v1/disease-reference (this file)

The reference API provides lightweight lookup for rare/uncommon diseases with
external resource links but without full clinical content.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.disease_reference import DiagnosisPromotionQueue, DiseaseReference

router = APIRouter(prefix="/disease-reference", tags=["Disease Reference"])


# Response models
class DiseaseReferenceResponse(BaseModel):
    """Lightweight disease reference data"""

    mondo_id: str
    disease_name: str
    disease_synonyms: List[str]
    icd10_codes: List[str]
    snomed_code: Optional[str]
    short_description: Optional[str]
    disease_category: Optional[str]
    is_rare_disease: bool
    external_resources: dict
    search_stats: dict
    promoted_to_full_library: bool

    class Config:
        from_attributes = True


class DiseaseSearchResponse(BaseModel):
    """Search results with metadata"""

    query: str
    total_results: int
    results: List[DiseaseReferenceResponse]
    search_time_ms: float


class PromotionRequest(BaseModel):
    """Request to promote disease to full library"""

    mondo_id: str
    reason: Optional[str] = None
    requested_by: Optional[str] = None


# Endpoints


@router.get("/search", response_model=DiseaseSearchResponse)
async def search_disease_reference(
    q: str = Query(
        ..., min_length=2, description="Search query (disease name or ICD-10 code)"
    ),
    category: Optional[str] = Query(None, description="Filter by disease category"),
    rare_only: bool = Query(False, description="Show only rare diseases"),
    limit: int = Query(10, ge=1, le=100, description="Maximum results"),
    db: Session = Depends(get_db),
):
    """
    Search disease reference database.

    This searches the lightweight reference database (Tier 2) for diseases
    not in the full clinical library. Returns basic info + external links.

    **Use cases:**
    - User searches for rare disease not in full library
    - Quick ICD-10 code lookup
    - Finding external resources for uncommon conditions

    **Example:**
    ```
    GET /api/v1/disease-reference/search?q=Fabry%20disease
    GET /api/v1/disease-reference/search?q=E75.21
    GET /api/v1/disease-reference/search?category=Rare%20Diseases&limit=20
    ```
    """
    start_time = datetime.now()

    # Build query
    query = db.query(DiseaseReference)

    # Filter by category
    if category:
        query = query.filter(DiseaseReference.disease_category == category)

    # Filter by rare disease flag
    if rare_only:
        query = query.filter(DiseaseReference.is_rare_disease)

    # Search by name or ICD-10 code
    search_filter = DiseaseReference.disease_name.ilike(
        f"%{q}%"
    ) | DiseaseReference.icd10_codes.like(f"%{q}%")
    query = query.filter(search_filter)

    # Get results
    total_results = query.count()
    results = query.limit(limit).all()

    # Track search count for each result (for promotion decisions)
    for disease in results:
        disease.increment_search_count()

    db.commit()

    # Calculate search time
    search_time_ms = (datetime.now() - start_time).total_seconds() * 1000

    return {
        "query": q,
        "total_results": total_results,
        "results": [disease.to_dict() for disease in results],
        "search_time_ms": round(search_time_ms, 2),
    }


@router.get("/by-icd10/{icd10_code}", response_model=DiseaseReferenceResponse)
async def get_disease_by_icd10(icd10_code: str, db: Session = Depends(get_db)):
    """
    Get disease info by exact ICD-10 code.

    **Example:**
    ```
    GET /api/v1/disease-reference/by-icd10/E75.21
    ```
    """
    disease = (
        db.query(DiseaseReference)
        .filter(DiseaseReference.icd10_codes.like(f"%{icd10_code}%"))
        .first()
    )

    if not disease:
        raise HTTPException(
            status_code=404, detail=f"No reference found for ICD-10 code: {icd10_code}"
        )

    # Track search
    disease.increment_search_count()
    db.commit()

    return disease.to_dict()


@router.get("/categories", response_model=List[str])
async def get_disease_categories(db: Session = Depends(get_db)):
    """
    Get list of all disease categories in reference database.

    **Example:**
    ```
    GET /api/v1/disease-reference/categories
    ```
    """
    categories = db.query(DiseaseReference.disease_category).distinct().all()
    return [cat[0] for cat in categories if cat[0]]


@router.get("/stats")
async def get_database_stats(db: Session = Depends(get_db)):
    """
    Get statistics about the reference database.

    **Returns:**
    - Total diseases
    - Rare vs common split
    - Most searched diseases
    - Coverage by category
    """
    total_diseases = db.query(DiseaseReference).count()
    rare_diseases = db.query(DiseaseReference).filter_by(is_rare_disease=True).count()
    common_diseases = total_diseases - rare_diseases

    # Category breakdown
    categories = (
        db.query(
            DiseaseReference.disease_category, db.func.count(DiseaseReference.mondo_id)
        )
        .group_by(DiseaseReference.disease_category)
        .all()
    )

    category_counts = {cat: count for cat, count in categories if cat}

    # Most searched diseases (top 10)
    all_diseases = db.query(DiseaseReference).all()
    top_searched = sorted(
        [(d.disease_name, d.get_total_searches()) for d in all_diseases],
        key=lambda x: x[1],
        reverse=True,
    )[:10]

    return {
        "total_diseases": total_diseases,
        "rare_diseases": rare_diseases,
        "common_diseases": common_diseases,
        "categories": category_counts,
        "most_searched": [
            {"disease": name, "searches": count}
            for name, count in top_searched
            if count > 0
        ],
    }


@router.post("/promote")
async def request_promotion_to_full_library(
    request: PromotionRequest, db: Session = Depends(get_db)
):
    """
    Request to promote a disease from reference DB to full clinical library.

    **Workflow:**
    1. User/admin requests promotion (disease searched frequently or clinically important)
    2. Request goes to promotion queue
    3. Clinical team reviews and adds full content
    4. Disease promoted to DiagnosisContentMap (Tier 1)

    **Example:**
    ```json
    POST /api/v1/disease-reference/promote
    {
        "mondo_id": "ICD10:E75.21",
        "reason": "Searched 50+ times in last month",
        "requested_by": "dr.smith@hospital.org"
    }
    ```
    """
    # Check if disease exists in reference DB
    disease = db.query(DiseaseReference).filter_by(mondo_id=request.mondo_id).first()

    if not disease:
        raise HTTPException(
            status_code=404, detail="Disease not found in reference database"
        )

    # Check if already promoted
    if disease.promoted_to_full_library:
        raise HTTPException(status_code=400, detail="Disease already in full library")

    # Check if already in promotion queue
    existing_request = (
        db.query(DiagnosisPromotionQueue)
        .filter_by(mondo_id=request.mondo_id, status__in=["pending", "in_review"])
        .first()
    )

    if existing_request:
        return {
            "message": "Promotion request already exists",
            "request_id": existing_request.id,
            "status": existing_request.status,
        }

    # Create promotion request
    import uuid

    promotion = DiagnosisPromotionQueue(
        id=str(uuid.uuid4()),
        mondo_id=request.mondo_id,
        disease_name=disease.disease_name,
        requested_by=request.requested_by,
        request_reason=request.reason,
        search_frequency=disease.search_count,
        status="pending",
    )

    db.add(promotion)
    db.commit()
    db.refresh(promotion)

    return {
        "message": "Promotion request created",
        "request_id": promotion.id,
        "disease_name": disease.disease_name,
        "status": "pending",
        "search_count": disease.get_total_searches(),
    }


@router.get("/promotion-queue")
async def get_promotion_queue(
    status: Optional[str] = Query(
        None, description="Filter by status (pending, in_review, approved, rejected)"
    ),
    db: Session = Depends(get_db),
):
    """
    Get diseases in promotion queue (admin endpoint).

    **Statuses:**
    - pending: Awaiting review
    - in_review: Clinical team reviewing
    - approved: Approved for promotion
    - rejected: Not suitable for full library
    - completed: Promoted to full library
    """
    query = db.query(DiagnosisPromotionQueue)

    if status:
        query = query.filter_by(status=status)

    requests = query.order_by(DiagnosisPromotionQueue.requested_at.desc()).all()

    return [
        {
            "id": req.id,
            "disease_name": req.disease_name,
            "mondo_id": req.mondo_id,
            "status": req.status,
            "requested_by": req.requested_by,
            "reason": req.request_reason,
            "search_frequency": req.search_frequency,
            "requested_at": req.requested_at.isoformat() if req.requested_at else None,
            "reviewed_at": req.reviewed_at.isoformat() if req.reviewed_at else None,
        }
        for req in requests
    ]


# Health check
@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check for disease reference API"""
    try:
        count = db.query(DiseaseReference).count()
        return {"status": "healthy", "database": "connected", "total_diseases": count}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
