"""
Content Settings Router
API endpoints for managing facility settings, work presets, and personal content libraries

Endpoints:
- Facility settings management
- Work setting presets (ED, ICU, etc.)
- Personal content library (favorites, templates)
- Diagnosis content search
- Medication content search
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Database imports
from src.database import get_db
from src.models.content_settings import (
    DiagnosisContentMap,
    FacilitySettings,
    MedicationContentMap,
    PersonalContentLibrary,
    WorkSettingPreset,
    search_diagnosis_by_icd10,
    search_diagnosis_by_name,
    search_medication_by_rxnorm,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/content-settings", tags=["Content Settings"])


# ============================================================================
# Pydantic Schemas
# ============================================================================


class FacilitySettingsCreate(BaseModel):
    """Create/update facility settings"""

    facility_id: str
    facility_name: str
    main_phone: Optional[str] = None
    after_hours_phone: Optional[str] = None
    patient_portal_url: Optional[str] = None
    address: Optional[str] = None
    standard_follow_up_instructions: List[str] = []
    standard_emergency_criteria: List[str] = []
    hipaa_disclaimer: Optional[str] = None
    logo_path: Optional[str] = None


class FacilitySettingsResponse(BaseModel):
    """Facility settings response"""

    facility_id: str
    facility_name: str
    main_phone: Optional[str]
    after_hours_phone: Optional[str]
    patient_portal_url: Optional[str]
    address: Optional[str]
    standard_follow_up_instructions: List[str]
    standard_emergency_criteria: List[str]
    hipaa_disclaimer: Optional[str]
    logo_path: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class WorkSettingPresetResponse(BaseModel):
    """Work setting preset response"""

    id: str
    work_setting: str
    common_warning_signs: List[str]
    common_medications: List[Dict[str, Any]]
    common_diagnoses: List[str]
    common_activity_restrictions: List[str]
    common_diet_instructions: List[str]
    default_follow_up_timeframe: Optional[str]
    default_reading_level: Optional[str]
    default_language: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class PersonalContentUpdate(BaseModel):
    """Update personal content library"""

    favorite_warning_signs: Optional[List[str]] = None
    favorite_medication_instructions: Optional[List[str]] = None
    favorite_follow_up_phrases: Optional[List[str]] = None
    favorite_activity_restrictions: Optional[List[str]] = None
    custom_discharge_templates: Optional[List[Dict[str, Any]]] = None
    custom_medication_templates: Optional[List[Dict[str, Any]]] = None


class PersonalContentResponse(BaseModel):
    """Personal content library response"""

    user_id: str
    favorite_warning_signs: List[str]
    favorite_medication_instructions: List[str]
    favorite_follow_up_phrases: List[str]
    favorite_activity_restrictions: List[str]
    custom_discharge_templates: List[Dict[str, Any]]
    custom_medication_templates: List[Dict[str, Any]]
    most_used_diagnoses: List[Dict[str, Any]]
    most_used_medications: List[Dict[str, Any]]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class DiagnosisSearchResponse(BaseModel):
    """Diagnosis search result"""

    id: str
    icd10_code: str
    snomed_code: Optional[str]
    diagnosis_display: str
    diagnosis_aliases: List[str]
    standard_warning_signs: List[str]
    standard_medications: List[Dict[str, Any]]
    is_chronic_condition: bool
    typical_followup_days: Optional[int]

    class Config:
        from_attributes = True


# ============================================================================
# Facility Settings Endpoints
# ============================================================================


@router.get("/facility/{facility_id}", response_model=FacilitySettingsResponse)
async def get_facility_settings(facility_id: str, db: Session = Depends(get_db)):
    """
    Get facility settings by ID

    Returns facility-wide settings including contact info, standard content, etc.
    """
    facility = db.query(FacilitySettings).filter_by(facility_id=facility_id).first()

    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Facility settings not found for ID: {facility_id}",
        )

    return facility


@router.put("/facility", response_model=FacilitySettingsResponse)
async def create_or_update_facility_settings(
    settings: FacilitySettingsCreate, db: Session = Depends(get_db)
):
    """
    Create or update facility settings

    If facility already exists, updates it. Otherwise creates new facility settings.
    """
    existing = (
        db.query(FacilitySettings).filter_by(facility_id=settings.facility_id).first()
    )

    if existing:
        # Update existing
        for key, value in settings.dict().items():
            setattr(existing, key, value)
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        logger.info(f"Updated facility settings for {settings.facility_id}")
        return existing
    else:
        # Create new
        new_facility = FacilitySettings(
            **settings.dict(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(new_facility)
        db.commit()
        db.refresh(new_facility)
        logger.info(f"Created facility settings for {settings.facility_id}")
        return new_facility


# ============================================================================
# Work Setting Presets Endpoints
# ============================================================================


@router.get("/work-preset/{work_setting}", response_model=WorkSettingPresetResponse)
async def get_work_setting_preset(work_setting: str, db: Session = Depends(get_db)):
    """
    Get work setting preset by name

    Examples: emergency_department, icu, community_clinic, etc.
    Returns pre-configured content for that work environment.
    """
    preset = db.query(WorkSettingPreset).filter_by(work_setting=work_setting).first()

    if not preset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work setting preset not found: {work_setting}",
        )

    return preset


@router.get("/work-presets", response_model=List[WorkSettingPresetResponse])
async def list_work_setting_presets(db: Session = Depends(get_db)):
    """
    List all available work setting presets

    Returns all pre-configured work environments (ED, ICU, etc.)
    """
    presets = db.query(WorkSettingPreset).all()
    return presets


# ============================================================================
# Personal Content Library Endpoints
# ============================================================================


@router.get("/personal/{user_id}", response_model=PersonalContentResponse)
async def get_personal_content_library(user_id: str, db: Session = Depends(get_db)):
    """
    Get user's personal content library

    Returns nurse's favorite phrases, templates, and usage patterns.
    NO PATIENT DATA - only nurse preferences.
    """
    library = db.query(PersonalContentLibrary).filter_by(user_id=user_id).first()

    if not library:
        # Create empty library if doesn't exist
        library = PersonalContentLibrary(
            user_id=user_id,
            favorite_warning_signs=[],
            favorite_medication_instructions=[],
            favorite_follow_up_phrases=[],
            favorite_activity_restrictions=[],
            custom_discharge_templates=[],
            custom_medication_templates=[],
            most_used_diagnoses=[],
            most_used_medications=[],
            updated_at=datetime.utcnow(),
        )
        db.add(library)
        db.commit()
        db.refresh(library)
        logger.info(f"Created personal library for user {user_id}")

    return library


@router.put("/personal/{user_id}", response_model=PersonalContentResponse)
async def update_personal_content_library(
    user_id: str, updates: PersonalContentUpdate, db: Session = Depends(get_db)
):
    """
    Update user's personal content library

    Updates favorite phrases, templates, etc.
    Only updates fields that are provided (partial update).
    """
    library = db.query(PersonalContentLibrary).filter_by(user_id=user_id).first()

    if not library:
        # Create new library
        library = PersonalContentLibrary(
            user_id=user_id,
            **updates.dict(exclude_none=True),
            updated_at=datetime.utcnow(),
        )
        db.add(library)
    else:
        # Update existing
        for key, value in updates.dict(exclude_none=True).items():
            setattr(library, key, value)
        library.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(library)
    logger.info(f"Updated personal library for user {user_id}")
    return library


@router.post("/personal/{user_id}/favorite")
async def add_to_favorites(
    user_id: str, category: str, content: str, db: Session = Depends(get_db)
):
    """
    Add item to user's favorites

    Categories: warning_signs, medication_instructions, follow_up_phrases, activity_restrictions
    """
    library = db.query(PersonalContentLibrary).filter_by(user_id=user_id).first()

    if not library:
        library = PersonalContentLibrary(user_id=user_id)
        db.add(library)

    # Map category to field
    category_map = {
        "warning_signs": "favorite_warning_signs",
        "medication_instructions": "favorite_medication_instructions",
        "follow_up_phrases": "favorite_follow_up_phrases",
        "activity_restrictions": "favorite_activity_restrictions",
    }

    if category not in category_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category: {category}",
        )

    field_name = category_map[category]
    current_list = getattr(library, field_name) or []

    if content not in current_list:
        current_list.append(content)
        setattr(library, field_name, current_list)
        library.updated_at = datetime.utcnow()
        db.commit()
        logger.info(f"Added to {category} favorites for user {user_id}")

    return {"success": True, "message": f"Added to {category} favorites"}


@router.delete("/personal/{user_id}/favorite")
async def remove_from_favorites(
    user_id: str, category: str, content: str, db: Session = Depends(get_db)
):
    """Remove item from user's favorites"""
    library = db.query(PersonalContentLibrary).filter_by(user_id=user_id).first()

    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Library not found"
        )

    category_map = {
        "warning_signs": "favorite_warning_signs",
        "medication_instructions": "favorite_medication_instructions",
        "follow_up_phrases": "favorite_follow_up_phrases",
        "activity_restrictions": "favorite_activity_restrictions",
    }

    if category not in category_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid category"
        )

    field_name = category_map[category]
    current_list = getattr(library, field_name) or []

    if content in current_list:
        current_list.remove(content)
        setattr(library, field_name, current_list)
        library.updated_at = datetime.utcnow()
        db.commit()
        logger.info(f"Removed from {category} favorites for user {user_id}")

    return {"success": True, "message": f"Removed from {category} favorites"}


# ============================================================================
# Diagnosis Content Search Endpoints
# ============================================================================


@router.get("/diagnosis/search", response_model=List[DiagnosisSearchResponse])
async def search_diagnoses(q: str, limit: int = 20, db: Session = Depends(get_db)):
    """
    Search diagnoses by name or alias

    Fuzzy search across diagnosis names and aliases.
    Returns up to `limit` results.
    """
    try:
        results = search_diagnosis_by_name(db, q)
        return results[:limit]
    except Exception as e:
        logger.error(f"Diagnosis search failed: {str(e)}")
        # Return empty list instead of 500 error - graceful degradation
        return []


@router.get("/diagnosis/icd10/{icd10_code}", response_model=DiagnosisSearchResponse)
async def get_diagnosis_by_icd10(icd10_code: str, db: Session = Depends(get_db)):
    """
    Get diagnosis by ICD-10 code

    Example: E11.9 for Type 2 Diabetes
    """
    diagnosis = search_diagnosis_by_icd10(db, icd10_code)

    if not diagnosis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Diagnosis not found for ICD-10 code: {icd10_code}",
        )

    return diagnosis


@router.get("/diagnosis/autocomplete")
async def autocomplete_diagnosis(q: str, limit: int = 10):
    """
    Autocomplete for diagnosis search using comprehensive ICD-10 2025 codes.

    Searches 74,000+ diagnosis codes from CDC ICD-10-CM 2025 data.
    Returns minimal data for autocomplete dropdowns.
    """
    from fastapi.responses import JSONResponse

    try:
        from src.services.icd10_autocomplete import search_icd10

        results = search_icd10(q, limit)
        logger.info(
            f"Diagnosis autocomplete: query='{q}', found {len(results)} results"
        )
        return JSONResponse(content=results)
    except Exception as e:
        logger.error(f"Diagnosis autocomplete failed: {e}", exc_info=True)
        # Return empty list on error - graceful degradation
        return JSONResponse(content=[])


@router.get("/diagnosis/autocomplete/debug")
async def debug_icd10_status():
    """Debug endpoint to check ICD-10 file status"""
    import os

    from fastapi.responses import JSONResponse

    try:
        from src.services import icd10_autocomplete

        # Match the path logic in icd10_autocomplete.py
        router_dir = os.path.dirname(os.path.abspath(__file__))  # /app/routers
        app_root = os.path.dirname(router_dir)  # /app
        data_path = os.path.join(
            app_root, "data", "icd10_raw", "icd10cm-codes-2025.txt"
        )

        # List files in expected directory
        data_dir = os.path.join(app_root, "data", "icd10_raw")
        files_in_dir = (
            os.listdir(data_dir) if os.path.exists(data_dir) else ["DIR_NOT_FOUND"]
        )

        return JSONResponse(
            content={
                "file_path": data_path,
                "file_exists": os.path.exists(data_path),
                "cwd": os.getcwd(),
                "__file__": __file__,
                "router_dir": router_dir,
                "app_root": app_root,
                "data_dir": data_dir,
                "data_dir_exists": os.path.exists(data_dir),
                "files_in_data_dir": files_in_dir,
                "codes_loaded": len(icd10_autocomplete._icd10_codes),
                "loaded_flag": icd10_autocomplete._loaded,
            }
        )
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/diagnosis/{diagnosis_id}", response_model=DiagnosisSearchResponse)
async def get_diagnosis_by_id(diagnosis_id: str, db: Session = Depends(get_db)):
    """Get diagnosis content by ID"""
    diagnosis = db.query(DiagnosisContentMap).filter_by(id=diagnosis_id).first()

    if not diagnosis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Diagnosis not found: {diagnosis_id}",
        )

    return diagnosis


# ============================================================================
# Medication Content Search Endpoints
# ============================================================================


@router.get("/medication/rxnorm/{rxnorm_code}")
async def get_medication_by_rxnorm(rxnorm_code: str, db: Session = Depends(get_db)):
    """Get medication by RxNorm code"""
    medication = search_medication_by_rxnorm(db, rxnorm_code)

    if not medication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medication not found for RxNorm code: {rxnorm_code}",
        )

    return medication


@router.get("/medication/search")
async def search_medications(q: str, limit: int = 20, db: Session = Depends(get_db)):
    """Search medications by name"""
    search_pattern = f"%{q.lower()}%"
    results = (
        db.query(MedicationContentMap)
        .filter(MedicationContentMap.medication_display.ilike(search_pattern))
        .limit(limit)
        .all()
    )

    return results


@router.get("/medication/autocomplete")
async def autocomplete_medication(
    q: str, limit: int = 10, db: Session = Depends(get_db)
):
    """
    Autocomplete for medication search

    Returns minimal data for autocomplete dropdowns.
    """
    search_pattern = f"%{q.lower()}%"
    results = (
        db.query(MedicationContentMap)
        .filter(MedicationContentMap.medication_display.ilike(search_pattern))
        .limit(limit)
        .all()
    )

    return [
        {
            "id": m.id,
            "label": m.medication_display,
            "value": m.id,
            "rxnorm_code": m.rxnorm_code,
            "generic_name": m.generic_name,
        }
        for m in results
    ]


# ============================================================================
# Usage Tracking (NO PHI)
# ============================================================================


@router.post("/track-usage/{user_id}")
async def track_content_usage(
    user_id: str,
    content_type: str,  # "diagnosis" or "medication"
    content_id: str,
    db: Session = Depends(get_db),
):
    """
    Track content usage for personalization

    Updates most_used_diagnoses or most_used_medications.
    NO PATIENT DATA - only tracks which content nurse uses frequently.
    """
    library = db.query(PersonalContentLibrary).filter_by(user_id=user_id).first()

    if not library:
        library = PersonalContentLibrary(user_id=user_id)
        db.add(library)

    if content_type == "diagnosis":
        usage_list = library.most_used_diagnoses or []
        # Find existing entry or create new
        found = False
        for item in usage_list:
            if item.get("id") == content_id:
                item["count"] = item.get("count", 0) + 1
                item["last_used"] = datetime.utcnow().isoformat()
                found = True
                break

        if not found:
            usage_list.append(
                {
                    "id": content_id,
                    "count": 1,
                    "last_used": datetime.utcnow().isoformat(),
                }
            )

        library.most_used_diagnoses = usage_list

    elif content_type == "medication":
        usage_list = library.most_used_medications or []
        found = False
        for item in usage_list:
            if item.get("id") == content_id:
                item["count"] = item.get("count", 0) + 1
                item["last_used"] = datetime.utcnow().isoformat()
                found = True
                break

        if not found:
            usage_list.append(
                {
                    "id": content_id,
                    "count": 1,
                    "last_used": datetime.utcnow().isoformat(),
                }
            )

        library.most_used_medications = usage_list

    library.updated_at = datetime.utcnow()
    db.commit()

    return {"success": True, "message": "Usage tracked"}
