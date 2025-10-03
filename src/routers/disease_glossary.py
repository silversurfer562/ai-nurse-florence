"""
Disease Glossary Router - AI Nurse Florence
Comprehensive disease reference and export functionality

Provides access to 12,000+ diseases with:
- MONDO IDs, ICD-10, SNOMED, UMLS codes
- Disease synonyms and descriptions
- Categorization and search
- JSON export for open data access
"""

from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from src.models.disease_reference import DiseaseReference
    from src.database import get_db
    _has_models = True
    logger.info("✅ Disease glossary models loaded successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import disease glossary models: {e}")
    _has_models = False
    DiseaseReference = None  # type: ignore
    def get_db():  # type: ignore
        return None
except Exception as e:
    logger.error(f"❌ Unexpected error loading disease glossary models: {e}")
    _has_models = False
    DiseaseReference = None  # type: ignore
    def get_db():  # type: ignore
        return None

router = APIRouter(prefix="/disease-glossary", tags=["Disease Glossary"])


class GlossaryEntry(BaseModel):
    """Disease glossary entry with comprehensive metadata."""
    mondo_id: str = Field(..., description="MONDO ontology ID")
    disease_name: str = Field(..., description="Primary disease name")
    synonyms: List[str] = Field(default_factory=list, description="Alternative names")
    icd10_codes: List[str] = Field(default_factory=list, description="ICD-10 diagnostic codes")
    snomed_code: Optional[str] = Field(None, description="SNOMED CT code")
    umls_code: Optional[str] = Field(None, description="UMLS concept code")
    description: Optional[str] = Field(None, description="Short description")
    category: Optional[str] = Field(None, description="Disease category")
    is_rare: bool = Field(default=False, description="Rare disease flag")
    prevalence: Optional[str] = Field(None, description="Estimated prevalence")


class GlossaryResponse(BaseModel):
    """Response for glossary queries."""
    total: int = Field(..., description="Total matching diseases")
    returned: int = Field(..., description="Number returned in this response")
    offset: int = Field(..., description="Pagination offset")
    diseases: List[GlossaryEntry] = Field(..., description="Disease entries")
    categories: Optional[List[str]] = Field(None, description="Available categories")


@router.get("/", response_model=GlossaryResponse)
async def get_disease_glossary(
    search: Optional[str] = Query(None, description="Search term for disease name or synonym"),
    category: Optional[str] = Query(None, description="Filter by disease category"),
    rare_only: bool = Query(False, description="Show only rare diseases"),
    limit: int = Query(100, ge=1, le=1000, description="Number of results (max 1000)"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    include_categories: bool = Query(False, description="Include list of all categories")
):
    """
    Get disease glossary with optional filtering and pagination.

    - **search**: Find diseases by name or synonym (case-insensitive)
    - **category**: Filter by specific category
    - **rare_only**: Show only rare diseases
    - **limit**: Maximum results to return (default 100, max 1000)
    - **offset**: Skip first N results for pagination
    - **include_categories**: Return list of all available categories
    """
    if not _has_models:
        raise HTTPException(status_code=503, detail="Database models not available")

    db = next(get_db())
    try:
        # Build query
        query = db.query(DiseaseReference)

        # Apply filters
        if search:
            search_term = f"%{search.lower()}%"
            query = query.filter(
                (DiseaseReference.disease_name.ilike(search_term)) |
                (DiseaseReference.disease_synonyms.ilike(search_term))
            )

        if category:
            query = query.filter(DiseaseReference.disease_category == category)

        if rare_only:
            query = query.filter(DiseaseReference.is_rare_disease == True)

        # Get total count
        total = query.count()

        # Apply pagination and fetch
        diseases_db = query.order_by(DiseaseReference.disease_name).offset(offset).limit(limit).all()

        # Convert to response format
        diseases = []
        for disease in diseases_db:
            synonyms = json.loads(disease.disease_synonyms) if disease.disease_synonyms else []
            icd10 = json.loads(disease.icd10_codes) if disease.icd10_codes else []

            diseases.append(GlossaryEntry(
                mondo_id=disease.mondo_id,
                disease_name=disease.disease_name,
                synonyms=synonyms if isinstance(synonyms, list) else [],
                icd10_codes=icd10 if isinstance(icd10, list) else [],
                snomed_code=disease.snomed_code,
                umls_code=disease.umls_code,
                description=disease.short_description,
                category=disease.disease_category,
                is_rare=disease.is_rare_disease or False,
                prevalence=disease.estimated_prevalence
            ))

        # Get categories if requested
        categories_list = None
        if include_categories:
            categories_result = db.query(DiseaseReference.disease_category)\
                .distinct()\
                .filter(DiseaseReference.disease_category.isnot(None))\
                .all()
            categories_list = sorted([cat[0] for cat in categories_result if cat[0]])

        return GlossaryResponse(
            total=total,
            returned=len(diseases),
            offset=offset,
            diseases=diseases,
            categories=categories_list
        )

    finally:
        db.close()


@router.get("/export")
async def export_disease_glossary(
    format: str = Query("json", regex="^(json|csv)$", description="Export format: json or csv"),
    category: Optional[str] = Query(None, description="Filter by category"),
    rare_only: bool = Query(False, description="Export only rare diseases")
):
    """
    Export the complete disease glossary as JSON or CSV.

    Returns a downloadable file with all diseases matching the filters.
    - **format**: 'json' or 'csv'
    - **category**: Optional category filter
    - **rare_only**: Export only rare diseases
    """
    if not _has_models:
        raise HTTPException(status_code=503, detail="Database models not available")

    db = next(get_db())
    try:
        # Build query
        query = db.query(DiseaseReference)

        if category:
            query = query.filter(DiseaseReference.disease_category == category)

        if rare_only:
            query = query.filter(DiseaseReference.is_rare_disease == True)

        diseases_db = query.order_by(DiseaseReference.disease_name).all()

        # Convert to export format
        export_data = []
        for disease in diseases_db:
            synonyms = json.loads(disease.disease_synonyms) if disease.disease_synonyms else []
            icd10 = json.loads(disease.icd10_codes) if disease.icd10_codes else []

            export_data.append({
                "mondo_id": disease.mondo_id,
                "disease_name": disease.disease_name,
                "synonyms": synonyms,
                "icd10_codes": icd10,
                "snomed_code": disease.snomed_code,
                "umls_code": disease.umls_code,
                "description": disease.short_description,
                "category": disease.disease_category,
                "is_rare_disease": disease.is_rare_disease,
                "prevalence": disease.estimated_prevalence,
                "medlineplus_url": disease.medlineplus_url,
                "mondo_url": disease.mondo_url
            })

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d")
        filter_suffix = f"_{category}" if category else ""
        filter_suffix += "_rare" if rare_only else ""
        filename = f"ai_nurse_florence_disease_glossary{filter_suffix}_{timestamp}.{format}"

        if format == "json":
            # JSON export with metadata
            json_output = {
                "metadata": {
                    "title": "AI Nurse Florence Disease Glossary",
                    "version": "1.0",
                    "exported_at": datetime.now().isoformat(),
                    "total_diseases": len(export_data),
                    "filters": {
                        "category": category,
                        "rare_only": rare_only
                    },
                    "license": "CC-BY-4.0",
                    "attribution": "AI Nurse Florence - https://ainurseflorence.com"
                },
                "diseases": export_data
            }

            content = json.dumps(json_output, indent=2, ensure_ascii=False)

            return Response(
                content=content,
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}",
                    "Content-Type": "application/json; charset=utf-8"
                }
            )

        else:  # CSV format
            import csv
            import io

            output = io.StringIO()
            if export_data:
                # Flatten nested fields for CSV
                fieldnames = ["mondo_id", "disease_name", "synonyms_list", "icd10_codes_list",
                             "snomed_code", "umls_code", "description", "category",
                             "is_rare_disease", "prevalence", "medlineplus_url", "mondo_url"]

                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()

                for disease in export_data:
                    writer.writerow({
                        "mondo_id": disease["mondo_id"],
                        "disease_name": disease["disease_name"],
                        "synonyms_list": "; ".join(disease["synonyms"]) if disease["synonyms"] else "",
                        "icd10_codes_list": "; ".join(disease["icd10_codes"]) if disease["icd10_codes"] else "",
                        "snomed_code": disease["snomed_code"] or "",
                        "umls_code": disease["umls_code"] or "",
                        "description": disease["description"] or "",
                        "category": disease["category"] or "",
                        "is_rare_disease": disease["is_rare_disease"],
                        "prevalence": disease["prevalence"] or "",
                        "medlineplus_url": disease["medlineplus_url"] or "",
                        "mondo_url": disease["mondo_url"] or ""
                    })

            return Response(
                content=output.getvalue(),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}",
                    "Content-Type": "text/csv; charset=utf-8"
                }
            )

    finally:
        db.close()


@router.get("/stats")
async def get_glossary_stats():
    """
    Get statistics about the disease glossary.

    Returns counts by category, rare disease counts, and coverage metrics.
    """
    if not _has_models:
        raise HTTPException(status_code=503, detail="Database models not available")

    db = next(get_db())
    try:
        # Test database connection and table existence
        logger.info("Testing disease_reference table access...")
        # Total count
        total_diseases = db.query(DiseaseReference).count()

        # Rare diseases count
        rare_count = db.query(DiseaseReference).filter(DiseaseReference.is_rare_disease == True).count()

        # Count by category
        categories = db.query(
            DiseaseReference.disease_category,
            db.func.count(DiseaseReference.mondo_id)
        ).filter(
            DiseaseReference.disease_category.isnot(None)
        ).group_by(
            DiseaseReference.disease_category
        ).all()

        category_counts = {cat: count for cat, count in categories}

        # Coding coverage
        with_icd10 = db.query(DiseaseReference).filter(
            DiseaseReference.icd10_codes.isnot(None),
            DiseaseReference.icd10_codes != '[]'
        ).count()

        with_snomed = db.query(DiseaseReference).filter(
            DiseaseReference.snomed_code.isnot(None)
        ).count()

        return {
            "total_diseases": total_diseases,
            "rare_diseases": rare_count,
            "common_diseases": total_diseases - rare_count,
            "categories": category_counts,
            "coding_coverage": {
                "icd10": {
                    "count": with_icd10,
                    "percentage": round(with_icd10 / total_diseases * 100, 1) if total_diseases > 0 else 0
                },
                "snomed": {
                    "count": with_snomed,
                    "percentage": round(with_snomed / total_diseases * 100, 1) if total_diseases > 0 else 0
                }
            },
            "last_updated": datetime.now().isoformat()
        }

    finally:
        db.close()
# Force redeploy
