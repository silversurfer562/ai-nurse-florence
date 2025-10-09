"""
Epic EHR Integration API Endpoints

Provides REST API endpoints for Epic FHIR integration including:
- Patient lookup by MRN or barcode
- Connection status checking
- Patient demographics and clinical data retrieval

Author: AI Nurse Florence
Created: 2025-01-07
"""

import logging
from datetime import datetime
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

# Lazy imports - don't import at module level to avoid config errors
logger = logging.getLogger(__name__)

# Will be set to True if imports succeed
EPIC_AVAILABLE = None


def get_epic_imports():
    """Lazy import of Epic modules to avoid config errors on module load"""
    global EPIC_AVAILABLE
    if EPIC_AVAILABLE is None:
        try:
            from src.integrations.epic_fhir_client import EpicFHIRClient
            from src.services.ehr_integration_service import EHRIntegrationService

            EPIC_AVAILABLE = True
            return EpicFHIRClient, EHRIntegrationService
        except Exception as e:
            logger.warning(f"Epic FHIR integration not available: {e}")
            EPIC_AVAILABLE = False
            return None, None
    elif EPIC_AVAILABLE:
        from src.integrations.epic_fhir_client import EpicFHIRClient
        from src.services.ehr_integration_service import EHRIntegrationService

        return EpicFHIRClient, EHRIntegrationService
    else:
        return None, None


# Create router
router = APIRouter(
    prefix="/ehr",
    tags=["Epic EHR Integration"],
    responses={404: {"description": "Not found"}},
)


# Request/Response Models
class PatientLookupRequest(BaseModel):
    """Request model for patient lookup"""

    identifier: str = Field(..., description="Patient identifier (MRN or barcode data)")
    identifier_type: str = Field(
        default="mrn", description="Type of identifier: mrn, barcode, fhir_id"
    )


class PatientDemographics(BaseModel):
    """Patient demographic information"""

    fhir_id: str
    mrn: str
    given_name: str
    family_name: str
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None


class Condition(BaseModel):
    """Active medical condition"""

    description: str
    icd10_code: Optional[str] = None
    snomed_code: Optional[str] = None
    clinical_status: str = "active"
    onset_date: Optional[str] = None


class Medication(BaseModel):
    """Active medication"""

    medication_name: str
    dosage: Optional[str] = None
    route: Optional[str] = None
    frequency: Optional[str] = None
    status: str = "active"
    prescribed_date: Optional[str] = None


class PatientDataResponse(BaseModel):
    """Complete patient data response"""

    patient: PatientDemographics
    conditions: List[Condition] = []
    medications: List[Medication] = []
    retrieved_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ConnectionStatusResponse(BaseModel):
    """Epic connection status"""

    status: str = Field(
        ..., description="Connection status: connected, disconnected, error"
    )
    environment: str = Field(
        ..., description="Epic environment: production, sandbox, mock"
    )
    endpoint: str = Field(..., description="Epic FHIR base URL")
    fhir_version: str = "R4"
    last_check: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# Dependency: Get Epic client
def get_epic_client() -> Optional[Any]:
    """
    Dependency to get Epic FHIR client instance.
    Returns None if Epic integration is not available.
    """
    import os

    EpicFHIRClient, _ = get_epic_imports()

    if EpicFHIRClient is None:
        return None

    try:
        # Import OAuthManager
        from src.integrations.epic_fhir_client import OAuthManager

        # Get configuration from environment
        base_url = os.getenv("EPIC_FHIR_BASE_URL", "http://localhost:8888")
        client_id = os.getenv("EPIC_CLIENT_ID", "test_client_id")
        client_secret = os.getenv("EPIC_CLIENT_SECRET", "test_client_secret")

        # For mock server, use a mock token URL
        token_url = base_url + "/oauth2/token"

        # Initialize OAuth manager
        oauth_manager = OAuthManager(
            token_url=token_url,
            client_id=client_id,
            client_secret=client_secret,
        )

        # Initialize Epic client with OAuth manager
        client = EpicFHIRClient(
            base_url=base_url,
            oauth_manager=oauth_manager,
        )
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Epic client: {e}")
        return None


# Dependency: Get EHR service
def get_ehr_service() -> Optional[Any]:
    """
    Dependency to get EHR integration service instance.
    """
    _, EHRIntegrationService = get_epic_imports()

    if EHRIntegrationService is None:
        return None

    return EHRIntegrationService()


# ============================================================================
# API Endpoints
# ============================================================================


@router.get("/epic/status", response_model=ConnectionStatusResponse)
async def get_epic_status(epic_client: Optional[Any] = Depends(get_epic_client)):
    """
    Check Epic FHIR connection status.

    Returns:
        ConnectionStatusResponse with current connection status
    """
    if not EPIC_AVAILABLE or epic_client is None:
        return ConnectionStatusResponse(
            status="disconnected",
            environment="unavailable",
            endpoint="Not configured",
            last_check=datetime.utcnow().isoformat(),
        )

    try:
        # Try to fetch metadata to verify connection
        await epic_client.get_metadata()

        return ConnectionStatusResponse(
            status="connected",
            environment="mock" if "localhost" in epic_client.base_url else "production",
            endpoint=epic_client.base_url,
            fhir_version="R4",
            last_check=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        logger.error(f"Epic status check failed: {e}")
        return ConnectionStatusResponse(
            status="error",
            environment="unknown",
            endpoint=epic_client.base_url if epic_client else "Unknown",
            last_check=datetime.utcnow().isoformat(),
        )


@router.post("/patient/lookup", response_model=PatientDataResponse)
async def lookup_patient(
    request: PatientLookupRequest,
    ehr_service: Optional[Any] = Depends(get_ehr_service),
    epic_client: Optional[Any] = Depends(get_epic_client),
):
    """
    Lookup patient by MRN, barcode, or FHIR ID.

    Retrieves:
    - Patient demographics (name, MRN, DOB, gender)
    - Active conditions (diagnoses with ICD-10/SNOMED codes)
    - Active medications (current prescriptions)

    Args:
        request: PatientLookupRequest with identifier and type

    Returns:
        PatientDataResponse with complete patient information

    Raises:
        HTTPException 404: Patient not found
        HTTPException 503: Epic service unavailable
    """
    if not EPIC_AVAILABLE or epic_client is None:
        raise HTTPException(
            status_code=503,
            detail="Epic FHIR integration is not available. Please check system configuration.",
        )

    try:
        # Parse identifier based on type
        if request.identifier_type == "barcode":
            # Extract MRN from barcode data
            mrn = ehr_service._parse_barcode(request.identifier)
            identifier_value = mrn
            search_type = "mrn"
        elif request.identifier_type == "fhir_id":
            identifier_value = request.identifier
            search_type = "fhir_id"
        else:  # mrn
            identifier_value = request.identifier
            search_type = "mrn"

        logger.info(f"Looking up patient: {search_type}={identifier_value}")

        # Search for patient
        if search_type == "fhir_id":
            patient_fhir = await epic_client.get_patient(identifier_value)
            if not patient_fhir:
                raise HTTPException(status_code=404, detail="Patient not found")
        else:
            # Search by MRN
            patients = await epic_client.search_patients(
                identifier=f"mrn|{identifier_value}"
            )
            if not patients or len(patients) == 0:
                raise HTTPException(
                    status_code=404,
                    detail=f"No patient found with MRN: {identifier_value}",
                )
            patient_fhir = patients[0]

        # Parse patient demographics
        patient_id = ehr_service._parse_patient_resource(patient_fhir)

        # Get active conditions
        conditions_raw = await epic_client.search_conditions(
            patient=patient_id.patient_fhir_id, clinical_status="active"
        )
        conditions = [
            ehr_service._parse_condition_resource(cond) for cond in conditions_raw
        ]

        # Get active medications
        medications_raw = await epic_client.search_medications(
            patient=patient_id.patient_fhir_id, status="active"
        )
        medications = [
            ehr_service._parse_medication_resource(med) for med in medications_raw
        ]

        # Build response
        response = PatientDataResponse(
            patient=PatientDemographics(
                fhir_id=patient_id.patient_fhir_id,
                mrn=patient_id.patient_mrn,
                given_name=patient_id.patient_given_name,
                family_name=patient_id.patient_family_name,
                date_of_birth=patient_fhir.get("birthDate"),
                gender=patient_fhir.get("gender", "").capitalize(),
            ),
            conditions=[
                Condition(
                    description=c.diagnosis_description,
                    icd10_code=c.diagnosis_icd10_code,
                    snomed_code=c.diagnosis_snomed_code,
                    clinical_status=c.diagnosis_clinical_status or "active",
                )
                for c in conditions
            ],
            medications=[
                Medication(
                    medication_name=m.medication_name,
                    dosage=m.medication_dosage,
                    route=m.medication_route,
                    frequency=m.medication_frequency,
                    status=m.medication_status or "active",
                )
                for m in medications
            ],
        )

        logger.info(f"Successfully retrieved patient data: {patient_id.patient_mrn}")
        return response

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Patient lookup failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve patient data: {str(e)}"
        )


@router.get("/patient/{fhir_id}", response_model=PatientDataResponse)
async def get_patient_by_id(
    fhir_id: str,
    ehr_service: Optional[Any] = Depends(get_ehr_service),
    epic_client: Optional[Any] = Depends(get_epic_client),
):
    """
    Get patient data by FHIR ID.

    Alternative endpoint that takes FHIR ID as path parameter.

    Args:
        fhir_id: Patient FHIR resource ID

    Returns:
        PatientDataResponse with complete patient information
    """
    request = PatientLookupRequest(identifier=fhir_id, identifier_type="fhir_id")
    return await lookup_patient(request, ehr_service, epic_client)


@router.post("/test-connection")
async def test_epic_connection(epic_client: Optional[Any] = Depends(get_epic_client)):
    """
    Test Epic FHIR connection with detailed diagnostics.

    Performs:
    - OAuth token acquisition test
    - Metadata endpoint test
    - Patient search test (if available)

    Returns:
        Detailed connection test results
    """
    if not EPIC_AVAILABLE or epic_client is None:
        return {
            "status": "failed",
            "error": "Epic FHIR integration not available",
            "tests": {
                "module_import": False,
                "client_initialization": False,
                "oauth": False,
                "metadata": False,
                "patient_search": False,
            },
        }

    test_results = {
        "status": "running",
        "tests": {},
        "timestamp": datetime.utcnow().isoformat(),
    }

    try:
        # Test 1: OAuth token
        test_results["tests"]["oauth"] = {
            "status": "testing",
            "message": "Requesting OAuth token...",
        }

        try:
            await epic_client.oauth_manager.get_access_token()
            test_results["tests"]["oauth"] = {
                "status": "passed",
                "message": "OAuth token acquired successfully",
            }
        except Exception as e:
            test_results["tests"]["oauth"] = {"status": "failed", "error": str(e)}
            test_results["status"] = "failed"
            return test_results

        # Test 2: Metadata endpoint
        test_results["tests"]["metadata"] = {
            "status": "testing",
            "message": "Fetching FHIR metadata...",
        }

        try:
            metadata = await epic_client.get_metadata()
            test_results["tests"]["metadata"] = {
                "status": "passed",
                "message": f"FHIR version: {metadata.get('fhirVersion', 'unknown')}",
            }
        except Exception as e:
            test_results["tests"]["metadata"] = {"status": "failed", "error": str(e)}

        # Test 3: Patient search (with known test MRN)
        test_results["tests"]["patient_search"] = {
            "status": "testing",
            "message": "Searching for test patient...",
        }

        try:
            patients = await epic_client.search_patients(identifier="mrn|12345678")
            if patients and len(patients) > 0:
                test_results["tests"]["patient_search"] = {
                    "status": "passed",
                    "message": f"Found {len(patients)} patient(s)",
                }
            else:
                test_results["tests"]["patient_search"] = {
                    "status": "warning",
                    "message": "No test patients found (this is okay for production)",
                }
        except Exception as e:
            test_results["tests"]["patient_search"] = {
                "status": "failed",
                "error": str(e),
            }

        # Overall status
        failed_tests = [
            name
            for name, result in test_results["tests"].items()
            if result.get("status") == "failed"
        ]

        if len(failed_tests) == 0:
            test_results["status"] = "passed"
            test_results["message"] = "All connection tests passed"
        else:
            test_results["status"] = "partial"
            test_results["message"] = f"Some tests failed: {', '.join(failed_tests)}"

        return test_results

    except Exception as e:
        logger.error(f"Connection test failed: {e}", exc_info=True)
        test_results["status"] = "error"
        test_results["error"] = str(e)
        return test_results


# ============================================================================
# Health Check Endpoint
# ============================================================================


@router.get("/health")
async def ehr_health_check():
    """
    Health check endpoint for EHR integration service.

    Returns basic status without making external API calls.
    """
    return {
        "service": "Epic EHR Integration",
        "status": "operational" if EPIC_AVAILABLE else "unavailable",
        "epic_available": EPIC_AVAILABLE,
        "timestamp": datetime.utcnow().isoformat(),
    }
