"""
Mock Epic FHIR Server for Testing
Provides realistic Epic FHIR R4 responses without requiring actual Epic credentials
"""

from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Query

app = FastAPI(title="Mock Epic FHIR Server")


# Sample test data - realistic Epic FHIR responses
MOCK_PATIENTS = {
    "12345678": {
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
        "gender": "male",
        "birthDate": "1965-03-15",
        "address": [
            {
                "line": ["123 Main St"],
                "city": "Seattle",
                "state": "WA",
                "postalCode": "98101",
            }
        ],
    },
    "87654321": {
        "resourceType": "Patient",
        "id": "eABC456",
        "identifier": [
            {
                "system": "urn:oid:1.2.840.114350",
                "value": "87654321",
                "type": {"text": "MRN"},
            }
        ],
        "name": [{"family": "Johnson", "given": ["Sarah", "Ann"], "use": "official"}],
        "gender": "female",
        "birthDate": "1978-07-22",
        "address": [
            {
                "line": ["456 Oak Ave"],
                "city": "Portland",
                "state": "OR",
                "postalCode": "97201",
            }
        ],
    },
}

MOCK_CONDITIONS = {
    "eXYZ123": [
        {
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
            "subject": {"reference": "Patient/eXYZ123"},
        },
        {
            "resourceType": "Condition",
            "id": "cXYZ790",
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
                    {"system": "http://hl7.org/fhir/sid/icd-10", "code": "I10"},
                    {"system": "http://snomed.info/sct", "code": "38341003"},
                ],
                "text": "Essential Hypertension",
            },
            "subject": {"reference": "Patient/eXYZ123"},
        },
    ],
    "eABC456": [
        {
            "resourceType": "Condition",
            "id": "cABC100",
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
                    {"system": "http://hl7.org/fhir/sid/icd-10", "code": "J45.909"},
                    {"system": "http://snomed.info/sct", "code": "195967001"},
                ],
                "text": "Asthma, unspecified",
            },
            "subject": {"reference": "Patient/eABC456"},
        }
    ],
}

MOCK_MEDICATIONS = {
    "eXYZ123": [
        {
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
            "subject": {"reference": "Patient/eXYZ123"},
            "dosageInstruction": [
                {
                    "text": "Take 1 tablet by mouth twice daily with meals",
                    "timing": {
                        "code": {"coding": [{"code": "BID", "display": "twice a day"}]}
                    },
                    "doseAndRate": [{"doseQuantity": {"value": 500, "unit": "mg"}}],
                }
            ],
        },
        {
            "resourceType": "MedicationRequest",
            "id": "mXYZ457",
            "status": "active",
            "medicationCodeableConcept": {
                "coding": [
                    {
                        "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                        "code": "197361",
                    }
                ],
                "text": "Lisinopril 10 MG Oral Tablet",
            },
            "subject": {"reference": "Patient/eXYZ123"},
            "dosageInstruction": [
                {
                    "text": "Take 1 tablet by mouth once daily",
                    "timing": {
                        "code": {"coding": [{"code": "QD", "display": "once a day"}]}
                    },
                    "doseAndRate": [{"doseQuantity": {"value": 10, "unit": "mg"}}],
                }
            ],
        },
    ],
    "eABC456": [
        {
            "resourceType": "MedicationRequest",
            "id": "mABC100",
            "status": "active",
            "medicationCodeableConcept": {
                "coding": [
                    {
                        "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                        "code": "745752",
                    }
                ],
                "text": "Albuterol 0.09 MG/ACTUAT Metered Dose Inhaler",
            },
            "subject": {"reference": "Patient/eABC456"},
            "dosageInstruction": [
                {
                    "text": "Inhale 2 puffs by mouth every 4-6 hours as needed for wheezing",
                    "timing": {
                        "code": {"coding": [{"code": "PRN", "display": "as needed"}]}
                    },
                }
            ],
        }
    ],
}

MOCK_ENCOUNTERS = {
    "eXYZ999": {
        "resourceType": "Encounter",
        "id": "eXYZ999",
        "status": "in-progress",
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
            "code": "EMER",
            "display": "Emergency",
        },
        "type": [
            {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": "50849002",
                        "display": "Emergency room admission",
                    }
                ]
            }
        ],
        "subject": {"reference": "Patient/eXYZ123"},
        "period": {"start": "2025-10-07T08:30:00Z"},
        "location": [{"location": {"display": "Emergency Department - Main Campus"}}],
    }
}


# ============================================================================
# FHIR Endpoints
# ============================================================================


@app.get("/Patient")
async def search_patient(identifier: Optional[str] = Query(None)):
    """
    Search for patient by MRN
    Epic format: GET /Patient?identifier=mrn|{mrn}
    """
    if not identifier:
        raise HTTPException(status_code=400, detail="identifier parameter required")

    # Parse MRN from identifier (format: "mrn|12345678")
    if "|" in identifier:
        _, mrn = identifier.split("|", 1)
    else:
        mrn = identifier

    patient = MOCK_PATIENTS.get(mrn)
    if not patient:
        return {"resourceType": "Bundle", "type": "searchset", "total": 0, "entry": []}

    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": 1,
        "entry": [{"resource": patient}],
    }


@app.get("/Patient/{patient_id}")
async def get_patient(patient_id: str):
    """Get patient by FHIR ID"""
    for patient in MOCK_PATIENTS.values():
        if patient["id"] == patient_id:
            return patient

    raise HTTPException(status_code=404, detail="Patient not found")


@app.get("/Condition")
async def search_conditions(
    patient: Optional[str] = Query(None), clinical_status: Optional[str] = Query(None)
):
    """
    Search for active conditions by patient
    Epic format: GET /Condition?patient={patient_id}&clinical-status=active
    """
    if not patient:
        raise HTTPException(status_code=400, detail="patient parameter required")

    conditions = MOCK_CONDITIONS.get(patient, [])

    # Filter by clinical status if provided
    if clinical_status:
        conditions = [
            c
            for c in conditions
            if c.get("clinicalStatus", {}).get("coding", [{}])[0].get("code")
            == clinical_status
        ]

    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": len(conditions),
        "entry": [{"resource": c} for c in conditions],
    }


@app.get("/MedicationRequest")
async def search_medications(
    patient: Optional[str] = Query(None), status: Optional[str] = Query(None)
):
    """
    Search for active medications by patient
    Epic format: GET /MedicationRequest?patient={patient_id}&status=active
    """
    if not patient:
        raise HTTPException(status_code=400, detail="patient parameter required")

    medications = MOCK_MEDICATIONS.get(patient, [])

    # Filter by status if provided
    if status:
        medications = [m for m in medications if m.get("status") == status]

    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": len(medications),
        "entry": [{"resource": m} for m in medications],
    }


@app.get("/Encounter/{encounter_id}")
async def get_encounter(encounter_id: str):
    """Get encounter by FHIR ID"""
    encounter = MOCK_ENCOUNTERS.get(encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")

    return encounter


@app.post("/DocumentReference")
async def create_document_reference(document: dict):
    """
    Create DocumentReference (write discharge note to chart)
    Epic format: POST /DocumentReference
    """
    # Validate basic FHIR structure
    if document.get("resourceType") != "DocumentReference":
        raise HTTPException(
            status_code=400, detail="resourceType must be DocumentReference"
        )

    # In real Epic, this would create the document in the chart
    # For mock server, just return success with generated ID
    document["id"] = f"doc{len(MOCK_ENCOUNTERS) + 1}"
    return document


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "server": "Mock Epic FHIR R4",
        "patients_available": len(MOCK_PATIENTS),
        "test_mrns": list(MOCK_PATIENTS.keys()),
    }


# ============================================================================
# OAuth Token Endpoint (Mock)
# ============================================================================


@app.post("/oauth2/token")
async def mock_token_endpoint(grant_type: str, client_id: Optional[str] = None):
    """
    Mock OAuth 2.0 token endpoint
    Returns dummy access token for testing
    """
    if grant_type != "client_credentials":
        raise HTTPException(status_code=400, detail="Unsupported grant_type")

    return {
        "access_token": "mock_access_token_12345",
        "token_type": "Bearer",
        "expires_in": 3600,
        "scope": "Patient.Read Condition.Read MedicationRequest.Read DocumentReference.Write",
    }


# ============================================================================
# Server Startup
# ============================================================================


def start_mock_server(port: int = 8888):
    """Start the mock FHIR server for testing"""
    print(f"\n🏥 Mock Epic FHIR Server starting on http://localhost:{port}")
    print(f"📋 Test MRNs available: {', '.join(MOCK_PATIENTS.keys())}")
    print(f"🔗 Base URL: http://localhost:{port}")
    print(f"✅ Health check: http://localhost:{port}/health\n")

    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    start_mock_server()
