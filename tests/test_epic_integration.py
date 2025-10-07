"""
Integration Tests for Epic FHIR Integration
Tests EpicFHIRClient, FHIR parsers, and mock server together
"""

import pytest

from services.ehr_integration_service import EHRIntegrationService
from src.integrations.epic_fhir_client import (
    EpicFHIRClient,
    OAuthManager,
    create_epic_client,
)
from src.models.patient_document_schemas import (
    FHIRCondition,
    FHIRMedicationRequest,
    FHIRPatientIdentifier,
)

# Test configuration for mock server
MOCK_BASE_URL = "http://localhost:8888"
MOCK_TOKEN_URL = "http://localhost:8888/oauth2/token"
MOCK_CLIENT_ID = "test_client"
MOCK_CLIENT_SECRET = "test_secret"

# Test patient MRNs
TEST_MRN_JOHN = "12345678"  # John Smith
TEST_MRN_SARAH = "87654321"  # Sarah Johnson


@pytest.fixture
def oauth_manager():
    """Create OAuth manager for tests"""
    return OAuthManager(
        token_url=MOCK_TOKEN_URL,
        client_id=MOCK_CLIENT_ID,
        client_secret=MOCK_CLIENT_SECRET,
    )


@pytest.fixture
def epic_client(oauth_manager):
    """Create Epic FHIR client for tests"""
    return EpicFHIRClient(
        base_url=MOCK_BASE_URL,
        oauth_manager=oauth_manager,
        timeout=10.0,
    )


@pytest.fixture
def ehr_service():
    """Create EHR integration service for tests"""
    return EHRIntegrationService()


# ============================================================================
# OAuth 2.0 Tests
# ============================================================================


@pytest.mark.asyncio
async def test_oauth_token_request(oauth_manager):
    """Test OAuth token request succeeds"""
    token = await oauth_manager.get_access_token()

    assert token is not None
    assert len(token) > 0
    assert oauth_manager.is_token_valid()
    assert oauth_manager.token_expiry is not None


@pytest.mark.asyncio
async def test_oauth_token_caching(oauth_manager):
    """Test OAuth token is cached and reused"""
    # First request
    token1 = await oauth_manager.get_access_token()
    expiry1 = oauth_manager.token_expiry

    # Second request should use cached token
    token2 = await oauth_manager.get_access_token()
    expiry2 = oauth_manager.token_expiry

    assert token1 == token2
    assert expiry1 == expiry2


# ============================================================================
# Patient Lookup Tests
# ============================================================================


@pytest.mark.asyncio
async def test_patient_search_by_mrn(epic_client):
    """Test patient lookup by MRN"""
    result = await epic_client.get(
        "/Patient", params={"identifier": f"mrn|{TEST_MRN_JOHN}"}
    )

    assert result["resourceType"] == "Bundle"
    assert result["total"] == 1
    assert len(result["entry"]) == 1

    patient = result["entry"][0]["resource"]
    assert patient["resourceType"] == "Patient"
    assert patient["id"] == "eXYZ123"


@pytest.mark.asyncio
async def test_patient_not_found(epic_client):
    """Test patient lookup with invalid MRN"""
    result = await epic_client.get("/Patient", params={"identifier": "mrn|99999999"})

    assert result["resourceType"] == "Bundle"
    assert result["total"] == 0
    assert len(result["entry"]) == 0


@pytest.mark.asyncio
async def test_patient_get_by_id(epic_client):
    """Test patient retrieval by FHIR ID"""
    patient = await epic_client.get("/Patient/eXYZ123")

    assert patient["resourceType"] == "Patient"
    assert patient["id"] == "eXYZ123"
    assert patient["name"][0]["family"] == "Smith"
    assert patient["name"][0]["given"][0] == "John"


# ============================================================================
# Condition (Diagnosis) Tests
# ============================================================================


@pytest.mark.asyncio
async def test_condition_search(epic_client):
    """Test active condition search by patient"""
    result = await epic_client.get(
        "/Condition", params={"patient": "eXYZ123", "clinical-status": "active"}
    )

    assert result["resourceType"] == "Bundle"
    assert result["total"] == 2  # John has 2 conditions

    conditions = [entry["resource"] for entry in result["entry"]]

    # Check first condition (Diabetes)
    diabetes = conditions[0]
    assert diabetes["resourceType"] == "Condition"
    assert any("E11.9" in c.get("code", "") for c in diabetes["code"]["coding"])
    assert "Diabetes" in diabetes["code"]["text"]


@pytest.mark.asyncio
async def test_condition_patient_without_conditions(epic_client):
    """Test condition search for patient with no active conditions"""
    result = await epic_client.get(
        "/Condition", params={"patient": "NONEXISTENT", "clinical-status": "active"}
    )

    assert result["resourceType"] == "Bundle"
    assert result["total"] == 0


# ============================================================================
# Medication Tests
# ============================================================================


@pytest.mark.asyncio
async def test_medication_search(epic_client):
    """Test active medication search by patient"""
    result = await epic_client.get(
        "/MedicationRequest", params={"patient": "eXYZ123", "status": "active"}
    )

    assert result["resourceType"] == "Bundle"
    assert result["total"] == 2  # John has 2 medications

    medications = [entry["resource"] for entry in result["entry"]]

    # Check first medication (Metformin)
    metformin = medications[0]
    assert metformin["resourceType"] == "MedicationRequest"
    assert "Metformin" in metformin["medicationCodeableConcept"]["text"]
    assert metformin["status"] == "active"


# ============================================================================
# Encounter Tests
# ============================================================================


@pytest.mark.asyncio
async def test_encounter_get_by_id(epic_client):
    """Test encounter retrieval by FHIR ID"""
    encounter = await epic_client.get("/Encounter/eXYZ999")

    assert encounter["resourceType"] == "Encounter"
    assert encounter["id"] == "eXYZ999"
    assert encounter["status"] == "in-progress"
    assert encounter["class"]["code"] == "EMER"


# ============================================================================
# FHIR Parser Tests
# ============================================================================


def test_parse_patient_resource(ehr_service):
    """Test Patient FHIR resource parsing"""
    patient_resource = {
        "resourceType": "Patient",
        "id": "eXYZ123",
        "identifier": [
            {
                "system": "urn:oid:1.2.840.114350",
                "value": "12345678",
                "type": {"text": "MRN"},
            }
        ],
        "name": [{"family": "Smith", "given": ["John", "Michael"], "use": "official"}],
    }

    parsed = ehr_service._parse_patient_resource(patient_resource)

    assert isinstance(parsed, FHIRPatientIdentifier)
    assert parsed.patient_fhir_id == "eXYZ123"
    assert parsed.patient_mrn == "12345678"
    assert parsed.patient_family_name == "Smith"
    assert parsed.patient_given_name == "John"
    assert parsed.full_name == "John Smith"


def test_parse_condition_resource(ehr_service):
    """Test Condition FHIR resource parsing"""
    condition_resource = {
        "resourceType": "Condition",
        "id": "cXYZ789",
        "clinicalStatus": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                    "code": "active",
                }
            ]
        },
        "code": {
            "coding": [
                {"system": "http://hl7.org/fhir/sid/icd-10", "code": "E11.9"},
                {"system": "http://snomed.info/sct", "code": "44054006"},
            ],
            "text": "Type 2 Diabetes Mellitus",
        },
    }

    parsed = ehr_service._parse_condition_resource(condition_resource)

    assert isinstance(parsed, FHIRCondition)
    assert parsed.condition_fhir_id == "cXYZ789"
    assert parsed.condition_code_icd10 == "E11.9"
    assert parsed.condition_code_snomed == "44054006"
    assert parsed.condition_display == "Type 2 Diabetes Mellitus"
    assert parsed.condition_clinical_status == "active"


def test_parse_medication_resource(ehr_service):
    """Test MedicationRequest FHIR resource parsing"""
    medication_resource = {
        "resourceType": "MedicationRequest",
        "id": "mXYZ456",
        "status": "active",
        "medicationCodeableConcept": {
            "coding": [
                {
                    "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                    "code": "860975",
                }
            ],
            "text": "Metformin 500 MG Oral Tablet",
        },
        "dosageInstruction": [
            {"text": "Take 1 tablet by mouth twice daily with meals"}
        ],
    }

    parsed = ehr_service._parse_medication_resource(medication_resource)

    assert isinstance(parsed, FHIRMedicationRequest)
    assert parsed.medication_fhir_id == "mXYZ456"
    assert parsed.medication_code_rxnorm == "860975"
    assert parsed.medication_display == "Metformin 500 MG Oral Tablet"
    assert (
        parsed.medication_dosage_instruction
        == "Take 1 tablet by mouth twice daily with meals"
    )
    assert parsed.medication_status == "active"


# ============================================================================
# Barcode Parsing Tests
# ============================================================================


def test_parse_barcode_simple(ehr_service):
    """Test simple numeric MRN barcode"""
    mrn = ehr_service._parse_barcode("12345678")
    assert mrn == "12345678"


def test_parse_barcode_prefixed(ehr_service):
    """Test MRN: prefixed barcode"""
    mrn = ehr_service._parse_barcode("MRN:12345678")
    assert mrn == "12345678"


def test_parse_barcode_caret_delimited(ehr_service):
    """Test caret-delimited barcode format"""
    mrn = ehr_service._parse_barcode("^MRN^12345678^NAME^SMITH^")
    assert mrn == "12345678"


def test_parse_barcode_complex(ehr_service):
    """Test complex barcode with multiple fields"""
    mrn = ehr_service._parse_barcode("^12345678^SMITH^JOHN^1965-03-15^")
    assert mrn == "12345678"


# ============================================================================
# End-to-End Integration Tests
# ============================================================================


@pytest.mark.asyncio
async def test_full_patient_workflow(epic_client, ehr_service):
    """Test complete workflow: MRN → Patient → Conditions → Medications"""
    # 1. Search patient by MRN
    patient_bundle = await epic_client.get(
        "/Patient", params={"identifier": f"mrn|{TEST_MRN_JOHN}"}
    )
    assert patient_bundle["total"] == 1

    patient_resource = patient_bundle["entry"][0]["resource"]
    patient_fhir_id = patient_resource["id"]

    # 2. Parse patient
    patient = ehr_service._parse_patient_resource(patient_resource)
    assert patient.patient_mrn == TEST_MRN_JOHN
    assert patient.full_name == "John Michael Smith"

    # 3. Get active conditions
    conditions_bundle = await epic_client.get(
        "/Condition", params={"patient": patient_fhir_id, "clinical-status": "active"}
    )
    assert conditions_bundle["total"] == 2

    # 4. Parse conditions
    conditions = [
        ehr_service._parse_condition_resource(entry["resource"])
        for entry in conditions_bundle["entry"]
    ]
    assert len(conditions) == 2
    assert any("Diabetes" in c.condition_display for c in conditions)
    assert any("Hypertension" in c.condition_display for c in conditions)

    # 5. Get active medications
    meds_bundle = await epic_client.get(
        "/MedicationRequest", params={"patient": patient_fhir_id, "status": "active"}
    )
    assert meds_bundle["total"] == 2

    # 6. Parse medications
    medications = [
        ehr_service._parse_medication_resource(entry["resource"])
        for entry in meds_bundle["entry"]
    ]
    assert len(medications) == 2
    assert any("Metformin" in m.medication_display for m in medications)
    assert any("Lisinopril" in m.medication_display for m in medications)


@pytest.mark.asyncio
async def test_document_reference_creation(epic_client):
    """Test DocumentReference write-back"""
    document = {
        "resourceType": "DocumentReference",
        "status": "current",
        "type": {"coding": [{"code": "discharge-summary"}]},
        "subject": {"reference": "Patient/eXYZ123"},
        "context": {"encounter": [{"reference": "Encounter/eXYZ999"}]},
        "content": [
            {
                "attachment": {
                    "contentType": "application/pdf",
                    "data": "base64_encoded_pdf_data_here",
                }
            }
        ],
    }

    result = await epic_client.post("/DocumentReference", data=document)

    assert result["resourceType"] == "DocumentReference"
    assert "id" in result
    assert result["status"] == "current"


# ============================================================================
# Client Statistics Tests
# ============================================================================


@pytest.mark.asyncio
async def test_client_statistics(epic_client):
    """Test Epic client request statistics"""
    # Make a few requests
    await epic_client.get("/Patient/eXYZ123")
    await epic_client.get("/Patient/eABC456")

    stats = epic_client.get_stats()

    assert "total_requests" in stats
    assert stats["total_requests"] >= 2
    assert "error_rate" in stats
    assert stats["token_valid"] is True
    assert "last_request" in stats


# ============================================================================
# Error Handling Tests
# ============================================================================


@pytest.mark.asyncio
async def test_invalid_endpoint_404(epic_client):
    """Test 404 error handling"""
    with pytest.raises(Exception) as exc_info:
        await epic_client.get("/InvalidEndpoint")

    assert "404" in str(exc_info.value) or "not found" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_missing_required_params(epic_client):
    """Test error when required parameters missing"""
    with pytest.raises(Exception) as exc_info:
        await epic_client.get("/Condition")  # Missing patient parameter

    assert "400" in str(exc_info.value) or "required" in str(exc_info.value).lower()


# ============================================================================
# Factory Function Tests
# ============================================================================


def test_create_epic_client_factory():
    """Test Epic client factory function"""
    client = create_epic_client(
        base_url=MOCK_BASE_URL,
        client_id=MOCK_CLIENT_ID,
        client_secret=MOCK_CLIENT_SECRET,
        token_url=MOCK_TOKEN_URL,
    )

    assert isinstance(client, EpicFHIRClient)
    assert client.base_url == MOCK_BASE_URL
    assert client.oauth_manager.client_id == MOCK_CLIENT_ID


def test_create_epic_client_missing_params():
    """Test factory function validation"""
    with pytest.raises(ValueError) as exc_info:
        create_epic_client(
            base_url=None,  # Missing required parameter
            client_id=MOCK_CLIENT_ID,
            client_secret=MOCK_CLIENT_SECRET,
            token_url=MOCK_TOKEN_URL,
        )

    assert "base URL" in str(exc_info.value).lower()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
