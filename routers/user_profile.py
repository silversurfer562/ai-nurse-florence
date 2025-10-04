"""
User Profile API Router
Manages nurse user profiles, work settings, and document preferences
"""

import base64
from pathlib import Path

from fastapi import APIRouter, HTTPException

from src.models.user_profile_schemas import (
    DocumentPermissions,
    NurseCredential,
    SignatureUploadRequest,
    UserProfileCreate,
    UserProfileResponse,
    UserProfileUpdate,
    WorkSetting,
    get_document_permissions,
    get_permission_level,
    get_smart_defaults,
)

router = APIRouter(prefix="/user-profile", tags=["User Profile"])


# Mock database for now - replace with actual database
_user_profiles = {}
_current_user_id = "test_user_123"  # Replace with actual auth


@router.post("", response_model=UserProfileResponse)
async def create_or_update_profile(profile: UserProfileCreate):
    """
    Create or update user profile with work settings

    **Smart Defaults:**
    - Reading level is automatically set based on work setting
    - Common languages are suggested based on facility type
    - Document permissions are set based on credentials

    **Example:**
    ```json
    {
        "full_name": "Jane Smith",
        "credentials": ["RN", "BSN"],
        "primary_credential": "RN",
        "license_number": "RN123456",
        "license_state": "CA",
        "facility_name": "City General Hospital",
        "work_setting": "emergency_department",
        "patient_population": "mixed_literacy"
    }
    ```
    """

    # Get smart defaults based on work setting
    smart_defaults = get_smart_defaults(profile.work_setting)

    # If user didn't explicitly set reading level, use smart default
    if profile.default_patient_reading_level is None:
        profile.default_patient_reading_level = smart_defaults.get(
            "recommended_reading_level", "intermediate"
        )

    # Determine permission level
    permission_level = get_permission_level(profile.primary_credential)

    # Check license expiry status
    license_status = "active"
    if profile.license_expiry:
        from datetime import datetime

        if profile.license_expiry < datetime.now():
            license_status = "expired"
        elif (profile.license_expiry - datetime.now()).days < 30:
            license_status = "expiring_soon"

    # Create profile response
    user_profile = {
        "user_id": _current_user_id,
        "full_name": profile.full_name,
        "credentials": profile.credentials,
        "primary_credential": profile.primary_credential,
        "permission_level": permission_level,
        "license_number": profile.license_number,
        "license_state": profile.license_state,
        "license_expiry": profile.license_expiry,
        "license_status": license_status,
        "facility_name": profile.facility_name,
        "work_setting": profile.work_setting,
        "department": profile.department,
        "patient_population": profile.patient_population,
        "work_phone": profile.work_phone,
        "work_email": profile.work_email,
        "default_patient_language": profile.default_patient_language,
        "default_patient_reading_level": profile.default_patient_reading_level,
        "secondary_languages": profile.secondary_languages,
        "has_signature": False,
        "signature_url": None,
        "documents_generated": 0,
        "last_document_at": None,
        "created_at": None,
        "updated_at": None,
    }

    # Store in mock database
    _user_profiles[_current_user_id] = user_profile

    return UserProfileResponse(**user_profile)


@router.get("", response_model=UserProfileResponse)
async def get_profile():
    """
    Get current user's profile

    **Returns:**
    - Complete user profile with work settings
    - Smart defaults applied for their work setting
    - Document permissions based on credentials
    """

    if _current_user_id not in _user_profiles:
        raise HTTPException(
            status_code=404, detail="Profile not found. Please create a profile first."
        )

    return UserProfileResponse(**_user_profiles[_current_user_id])


@router.patch("", response_model=UserProfileResponse)
async def update_profile(updates: UserProfileUpdate):
    """
    Update specific fields in user profile

    **Flexible Updates:**
    - Update only the fields you want to change
    - Smart defaults are re-applied if work_setting changes
    - Permissions are updated if credentials change
    """

    if _current_user_id not in _user_profiles:
        raise HTTPException(
            status_code=404, detail="Profile not found. Please create a profile first."
        )

    profile = _user_profiles[_current_user_id]

    # Update fields
    update_data = updates.dict(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            profile[field] = value

    # Re-calculate smart defaults if work setting changed
    if "work_setting" in update_data:
        smart_defaults = get_smart_defaults(profile["work_setting"])
        profile["default_patient_reading_level"] = smart_defaults.get(
            "recommended_reading_level", "intermediate"
        )

    # Re-calculate permissions if credentials changed
    if "primary_credential" in update_data:
        profile["permission_level"] = get_permission_level(
            profile["primary_credential"]
        )

    return UserProfileResponse(**profile)


@router.post("/signature")
async def upload_signature(signature: SignatureUploadRequest):
    """
    Upload digital signature for legal documents

    **Signature Requirements:**
    - Base64-encoded image
    - PNG or JPG format
    - Recommended size: 400x150 pixels
    - Will be used on legal documents and incident reports

    **Example:**
    ```json
    {
        "signature_data": "data:image/png;base64,iVBORw0KG...",
        "format": "png"
    }
    ```
    """

    if _current_user_id not in _user_profiles:
        raise HTTPException(
            status_code=404, detail="Profile not found. Please create a profile first."
        )

    # Decode base64 signature
    try:
        # Remove data URL prefix if present
        if signature.signature_data.startswith("data:image"):
            signature_data = signature.signature_data.split(",")[1]
        else:
            signature_data = signature.signature_data

        signature_bytes = base64.b64decode(signature_data)

        # Save signature to file
        signatures_dir = Path("static/signatures")
        signatures_dir.mkdir(parents=True, exist_ok=True)

        signature_filename = f"{_current_user_id}_signature.{signature.format}"
        signature_path = signatures_dir / signature_filename

        with open(signature_path, "wb") as f:
            f.write(signature_bytes)

        # Update profile
        profile = _user_profiles[_current_user_id]
        profile["has_signature"] = True
        profile["signature_url"] = f"/static/signatures/{signature_filename}"

        return {
            "success": True,
            "message": "Signature uploaded successfully",
            "signature_url": profile["signature_url"],
        }

    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to upload signature: {str(e)}"
        )


@router.get("/permissions", response_model=DocumentPermissions)
async def get_my_permissions():
    """
    Get document generation permissions based on credentials

    **Permission Levels:**
    - **BASIC** (CNA): Basic care instructions only
    - **STANDARD** (LPN/LVN): Most patient education, basic legal docs
    - **FULL** (RN+): All documents including full legal documentation
    - **ADVANCED** (NP/CNS/CRNA): Provider-level documents, prescriptions

    **Returns:**
    - What documents you can generate
    - Whether co-signature is required
    - Whether you can co-sign for others
    - Template creation permissions
    """

    if _current_user_id not in _user_profiles:
        raise HTTPException(
            status_code=404, detail="Profile not found. Please create a profile first."
        )

    profile = _user_profiles[_current_user_id]
    permissions = get_document_permissions(profile["permission_level"])

    return permissions


@router.get("/work-settings")
async def get_work_settings_info():
    """
    Get information about all available work settings

    **Returns:**
    - List of all work settings
    - Smart defaults for each setting
    - Recommended reading levels
    - Common document types for each setting

    **Use Case:**
    - Help users choose appropriate work setting during profile creation
    - Understand why certain defaults are recommended
    """

    settings_info = []

    for setting in WorkSetting:
        defaults = get_smart_defaults(setting)
        settings_info.append(
            {
                "value": setting.value,
                "name": setting.value.replace("_", " ").title(),
                "recommended_reading_level": defaults.get("recommended_reading_level"),
                "reason": defaults.get("reason"),
                "recommended_languages": defaults.get("recommended_languages"),
                "common_documents": defaults.get("common_documents"),
            }
        )

    return {"work_settings": settings_info, "total": len(settings_info)}


@router.get("/credentials")
async def get_available_credentials():
    """
    Get list of available nursing credentials

    **Returns:**
    - All available credentials
    - Permission level for each
    - Description of what each credential allows
    """

    credentials_info = []

    for credential in NurseCredential:
        permission_level = get_permission_level(credential)

        credentials_info.append(
            {
                "value": credential.value,
                "name": credential.value,
                "permission_level": permission_level.value,
                "description": _get_credential_description(credential),
            }
        )

    return {"credentials": credentials_info, "total": len(credentials_info)}


def _get_credential_description(credential: NurseCredential) -> str:
    """Get human-readable description of credential"""
    descriptions = {
        NurseCredential.CNA: "Certified Nursing Assistant - Basic care documentation",
        NurseCredential.LPN: "Licensed Practical Nurse - Standard patient education",
        NurseCredential.LVN: "Licensed Vocational Nurse - Standard patient education",
        NurseCredential.RN: "Registered Nurse - Full documentation including legal",
        NurseCredential.BSN: "Bachelor of Science in Nursing - Full documentation + templates",
        NurseCredential.MSN: "Master of Science in Nursing - Full documentation + templates",
        NurseCredential.NP: "Nurse Practitioner - All documents + prescriptions",
        NurseCredential.CNS: "Clinical Nurse Specialist - All documents + advanced care plans",
        NurseCredential.CRNA: "Certified Registered Nurse Anesthetist - All documents + anesthesia",
        NurseCredential.CNM: "Certified Nurse Midwife - All documents + obstetric care",
        NurseCredential.DNP: "Doctor of Nursing Practice - All documents + research",
        NurseCredential.PhD: "PhD in Nursing - All documents + research",
    }
    return descriptions.get(credential, "Nursing credential")


@router.get("/smart-defaults/{work_setting}")
async def get_smart_defaults_for_setting(work_setting: WorkSetting):
    """
    Get smart defaults for a specific work setting

    **Use Case:**
    - Preview what defaults will be applied before selecting work setting
    - Understand recommendations for your specific care environment

    **Example:**
    `/smart-defaults/emergency_department` returns:
    - Recommended reading level: basic
    - Reason: High stress, diverse literacy
    - Common languages needed
    """

    defaults = get_smart_defaults(work_setting)

    return {"work_setting": work_setting.value, "smart_defaults": defaults}


@router.get("/statistics")
async def get_user_statistics():
    """
    Get user's document generation statistics

    **Returns:**
    - Total documents generated
    - Documents by type
    - Most used languages
    - Most used reading levels
    - Recent activity
    """

    if _current_user_id not in _user_profiles:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile = _user_profiles[_current_user_id]

    return {
        "user_id": _current_user_id,
        "total_documents": profile.get("documents_generated", 0),
        "last_document_at": profile.get("last_document_at"),
        "work_setting": profile.get("work_setting"),
        "most_used_reading_level": profile.get("default_patient_reading_level"),
        "most_used_language": profile.get("default_patient_language"),
    }
