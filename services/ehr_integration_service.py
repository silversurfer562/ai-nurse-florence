"""
EHR Integration Service
Placeholder for future Epic FHIR integration

Current: Returns None/empty data (standalone mode)
Future: Real-time data exchange with Epic via HL7 FHIR R4 API
"""

import logging
from typing import List, Optional

from src.config import IntegrationMode, is_epic_enabled, settings
from src.models.patient_document_schemas import (
    FHIRCondition,
    FHIREncounter,
    FHIRMedicationRequest,
    FHIRPatientIdentifier,
)

logger = logging.getLogger(__name__)


class EHRIntegrationService:
    """
    EHR Integration Service

    Current Implementation: Stub/placeholder
    - All methods return None or empty lists in standalone mode
    - Raises NotImplementedError if Epic mode is enabled

    Future Implementation (Epic FHIR):
    - OAuth 2.0 authentication with Epic
    - Real-time patient data retrieval
    - Write discharge notes to Epic chart
    - Barcode scanning integration

    Epic FHIR Resources:
    - Patient: Demographics, MRN (GET /Patient?identifier=mrn|{mrn})
    - Encounter: Visit context, location (GET /Encounter/{id})
    - Condition: Active diagnoses with ICD-10/SNOMED (GET /Condition?patient={id}&clinical-status=active)
    - MedicationRequest: Active medications with RxNorm (GET /MedicationRequest?patient={id}&status=active)
    - DocumentReference: Write discharge notes (POST /DocumentReference)

    Authentication: OAuth 2.0 (Epic on FHIR)
    Base URL: https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/
    Standard: HL7 FHIR R4
    """

    def __init__(self):
        self.mode = settings.integration_mode
        self.epic_client = None  # Future: EpicFHIRClient()
        self.base_url = settings.epic_fhir_base_url or settings.epic_sandbox_url

        if is_epic_enabled():
            logger.warning(
                "Epic integration mode is enabled but not yet implemented. "
                "All EHR service methods will raise NotImplementedError."
            )

    # ============================================================================
    # Patient Data Retrieval
    # ============================================================================

    async def fetch_patient_by_mrn(self, mrn: str) -> Optional[FHIRPatientIdentifier]:
        """
        Fetch patient demographics from Epic by Medical Record Number

        Standalone mode: Returns None (manual entry required)
        Epic mode: GET /Patient?identifier=mrn|{mrn}

        Args:
            mrn: Medical Record Number (e.g., "12345678")

        Returns:
            FHIRPatientIdentifier with patient demographics or None

        Example Epic FHIR Response:
        {
            "resourceType": "Patient",
            "id": "eXYZ123",
            "identifier": [{"system": "urn:oid:1.2.840.114350", "value": "12345678"}],
            "name": [{"family": "Smith", "given": ["John"]}]
        }
        """
        if self.mode == IntegrationMode.STANDALONE:
            logger.debug("Standalone mode: Patient data must be entered manually")
            return None

        elif self.mode == IntegrationMode.EPIC_INTEGRATED:
            # Future implementation:
            # response = await self.epic_client.get(
            #     f"{self.base_url}/Patient",
            #     params={"identifier": f"mrn|{mrn}"}
            # )
            # patient_resource = response.json()["entry"][0]["resource"]
            # return self._parse_patient_resource(patient_resource)

            raise NotImplementedError(
                "Epic integration coming in future version. "
                "Enable standalone mode or wait for Epic FHIR implementation."
            )

    async def fetch_active_medications(
        self, patient_fhir_id: str
    ) -> List[FHIRMedicationRequest]:
        """
        Fetch active medications from Epic for a patient

        Epic mode: GET /MedicationRequest?patient={patient_id}&status=active

        Args:
            patient_fhir_id: Epic Patient FHIR ID (e.g., "eXYZ123")

        Returns:
            List of active medication orders with RxNorm codes

        Example Epic FHIR Response:
        {
            "resourceType": "Bundle",
            "entry": [{
                "resource": {
                    "resourceType": "MedicationRequest",
                    "id": "mXYZ456",
                    "medicationCodeableConcept": {
                        "coding": [{"system": "http://www.nlm.nih.gov/research/umls/rxnorm", "code": "860975"}],
                        "text": "Metformin"
                    },
                    "dosageInstruction": [{
                        "doseAndRate": [{"doseQuantity": {"value": 500, "unit": "mg"}}],
                        "timing": {"code": {"coding": [{"code": "BID"}]}}
                    }]
                }
            }]
        }
        """
        if self.mode == IntegrationMode.STANDALONE:
            logger.debug("Standalone mode: No active medications to fetch")
            return []

        elif self.mode == IntegrationMode.EPIC_INTEGRATED:
            # Future implementation:
            # response = await self.epic_client.get(
            #     f"{self.base_url}/MedicationRequest",
            #     params={"patient": patient_fhir_id, "status": "active"}
            # )
            # medications = []
            # for entry in response.json()["entry"]:
            #     medications.append(self._parse_medication_resource(entry["resource"]))
            # return medications

            raise NotImplementedError("Epic integration coming in future version")

    async def fetch_active_conditions(
        self, patient_fhir_id: str
    ) -> List[FHIRCondition]:
        """
        Fetch active diagnoses from Epic for a patient

        Epic mode: GET /Condition?patient={patient_id}&clinical-status=active

        Args:
            patient_fhir_id: Epic Patient FHIR ID

        Returns:
            List of active conditions with ICD-10 and SNOMED codes

        Example Epic FHIR Response:
        {
            "resourceType": "Bundle",
            "entry": [{
                "resource": {
                    "resourceType": "Condition",
                    "id": "cXYZ789",
                    "code": {
                        "coding": [
                            {"system": "http://hl7.org/fhir/sid/icd-10", "code": "E11.9"},
                            {"system": "http://snomed.info/sct", "code": "44054006"}
                        ],
                        "text": "Type 2 Diabetes Mellitus"
                    },
                    "clinicalStatus": {"coding": [{"code": "active"}]}
                }
            }]
        }
        """
        if self.mode == IntegrationMode.STANDALONE:
            logger.debug("Standalone mode: No active conditions to fetch")
            return []

        elif self.mode == IntegrationMode.EPIC_INTEGRATED:
            raise NotImplementedError("Epic integration coming in future version")

    async def fetch_encounter_context(
        self, encounter_fhir_id: str
    ) -> Optional[FHIREncounter]:
        """
        Fetch encounter details from Epic

        Epic mode: GET /Encounter/{encounter_id}

        Args:
            encounter_fhir_id: Epic Encounter FHIR ID

        Returns:
            FHIREncounter with visit context or None

        Example Epic FHIR Response:
        {
            "resourceType": "Encounter",
            "id": "eXYZ999",
            "type": [{"coding": [{"code": "EMER", "display": "Emergency"}]}],
            "period": {
                "start": "2024-01-15T08:30:00Z",
                "end": "2024-01-15T12:45:00Z"
            }
        }
        """
        if self.mode == IntegrationMode.STANDALONE:
            logger.debug("Standalone mode: No encounter context to fetch")
            return None

        elif self.mode == IntegrationMode.EPIC_INTEGRATED:
            raise NotImplementedError("Epic integration coming in future version")

    # ============================================================================
    # Write-Back to Epic
    # ============================================================================

    async def write_discharge_note(
        self,
        encounter_fhir_id: str,
        document_content: str,
        document_format: str = "pdf",
        document_type: str = "discharge_instructions",
    ) -> bool:
        """
        Write discharge instructions to Epic chart as DocumentReference

        Epic mode: POST /DocumentReference
        Creates clinical note attached to encounter

        Args:
            encounter_fhir_id: Epic Encounter FHIR ID
            document_content: Generated discharge instructions (text or PDF base64)
            document_format: "text/plain" or "application/pdf"
            document_type: Document category code

        Returns:
            True if successful

        Example Epic FHIR Request:
        POST /DocumentReference
        {
            "resourceType": "DocumentReference",
            "status": "current",
            "type": {"coding": [{"code": "discharge-summary"}]},
            "subject": {"reference": "Patient/eXYZ123"},
            "context": {"encounter": [{"reference": "Encounter/eXYZ999"}]},
            "content": [{
                "attachment": {
                    "contentType": "application/pdf",
                    "data": "base64_encoded_pdf_data_here"
                }
            }]
        }
        """
        if self.mode == IntegrationMode.STANDALONE:
            logger.info("Standalone mode: Document generated, no write-back to EHR")
            return True  # Document generated successfully, nothing to write

        elif self.mode == IntegrationMode.EPIC_INTEGRATED:
            if not settings.enable_epic_write_back:
                logger.warning("Epic write-back is disabled in settings")
                return False

            # Future implementation:
            # import base64
            # content_type = "application/pdf" if document_format == "pdf" else "text/plain"
            # encoded_content = base64.b64encode(document_content.encode()).decode()
            #
            # document_reference = {
            #     "resourceType": "DocumentReference",
            #     "status": "current",
            #     "type": {"coding": [{"code": document_type}]},
            #     "context": {"encounter": [{"reference": f"Encounter/{encounter_fhir_id}"}]},
            #     "content": [{
            #         "attachment": {
            #             "contentType": content_type,
            #             "data": encoded_content
            #         }
            #     }]
            # }
            #
            # response = await self.epic_client.post(
            #     f"{self.base_url}/DocumentReference",
            #     json=document_reference
            # )
            # return response.status_code == 201

            raise NotImplementedError("Epic integration coming in future version")

    # ============================================================================
    # Barcode Scanning (Future)
    # ============================================================================

    async def scan_patient_wristband(
        self, barcode_data: str
    ) -> Optional[FHIRPatientIdentifier]:
        """
        Parse patient wristband barcode and fetch patient data

        Epic mode: Decodes barcode → Extracts MRN → Calls fetch_patient_by_mrn()

        Args:
            barcode_data: Raw barcode scan data

        Returns:
            FHIRPatientIdentifier or None
        """
        if self.mode == IntegrationMode.STANDALONE:
            logger.debug("Standalone mode: Barcode scanning not available")
            return None

        elif self.mode == IntegrationMode.EPIC_INTEGRATED:
            if not settings.enable_mrn_scanning:
                logger.warning("MRN barcode scanning is disabled in settings")
                return None

            # Future: Parse barcode format and extract MRN
            # mrn = self._parse_barcode(barcode_data)
            # return await self.fetch_patient_by_mrn(mrn)

            raise NotImplementedError("Barcode scanning coming in future version")

    # ============================================================================
    # Helper Methods (Future)
    # ============================================================================

    def _parse_patient_resource(self, patient_resource: dict) -> FHIRPatientIdentifier:
        """
        Parse Epic Patient FHIR resource to FHIRPatientIdentifier

        Args:
            patient_resource: FHIR Patient resource from Epic

        Returns:
            FHIRPatientIdentifier with demographics

        Example Epic Patient resource:
        {
            "resourceType": "Patient",
            "id": "eXYZ123",
            "identifier": [{"system": "urn:oid:1.2.840.114350", "value": "12345678"}],
            "name": [{"family": "Smith", "given": ["John"]}]
        }
        """
        try:
            # Extract FHIR ID
            patient_fhir_id = patient_resource.get("id")

            # Extract MRN from identifiers
            mrn = None
            for identifier in patient_resource.get("identifier", []):
                if identifier.get("type", {}).get("text") == "MRN":
                    mrn = identifier.get("value")
                    break
                # Fallback - use first identifier
                if not mrn and identifier.get("value"):
                    mrn = identifier.get("value")

            # Extract name
            given_name = None
            family_name = None
            for name in patient_resource.get("name", []):
                if (
                    name.get("use") == "official"
                    or len(patient_resource.get("name", [])) == 1
                ):
                    family_name = name.get("family")
                    given_names = name.get("given", [])
                    given_name = given_names[0] if given_names else None
                    break

            return FHIRPatientIdentifier(
                patient_fhir_id=patient_fhir_id,
                patient_mrn=mrn,
                patient_given_name=given_name,
                patient_family_name=family_name,
            )

        except Exception as e:
            logger.error(f"Failed to parse Patient resource: {e}", exc_info=True)
            raise ValueError(f"Invalid Patient FHIR resource: {e}")

    def _parse_medication_resource(self, med_resource: dict) -> FHIRMedicationRequest:
        """
        Parse Epic MedicationRequest FHIR resource to FHIRMedicationRequest

        Args:
            med_resource: FHIR MedicationRequest resource from Epic

        Returns:
            FHIRMedicationRequest with medication details

        Example Epic MedicationRequest resource:
        {
            "resourceType": "MedicationRequest",
            "id": "mXYZ456",
            "medicationCodeableConcept": {
                "coding": [{"system": "http://www.nlm.nih.gov/research/umls/rxnorm", "code": "860975"}],
                "text": "Metformin 500 MG"
            },
            "dosageInstruction": [{"text": "Take 1 tablet twice daily"}]
        }
        """
        try:
            # Extract FHIR ID
            medication_fhir_id = med_resource.get("id")

            # Extract medication name and RxNorm code
            med_concept = med_resource.get("medicationCodeableConcept", {})
            medication_display = med_concept.get("text", "Unknown Medication")

            # Extract RxNorm code
            rxnorm_code = None
            for coding in med_concept.get("coding", []):
                if "rxnorm" in coding.get("system", "").lower():
                    rxnorm_code = coding.get("code")
                    break

            # Extract dosage instruction
            dosage_text = None
            dosage_instructions = med_resource.get("dosageInstruction", [])
            if dosage_instructions:
                dosage_text = dosage_instructions[0].get("text")

            return FHIRMedicationRequest(
                medication_fhir_id=medication_fhir_id,
                medication_code_rxnorm=rxnorm_code,
                medication_display=medication_display,
                medication_dosage_instruction=dosage_text,
                medication_status=med_resource.get("status", "active"),
            )

        except Exception as e:
            logger.error(
                f"Failed to parse MedicationRequest resource: {e}", exc_info=True
            )
            raise ValueError(f"Invalid MedicationRequest FHIR resource: {e}")

    def _parse_condition_resource(self, condition_resource: dict) -> FHIRCondition:
        """
        Parse Epic Condition FHIR resource to FHIRCondition

        Args:
            condition_resource: FHIR Condition resource from Epic

        Returns:
            FHIRCondition with diagnosis details

        Example Epic Condition resource:
        {
            "resourceType": "Condition",
            "id": "cXYZ789",
            "code": {
                "coding": [
                    {"system": "http://hl7.org/fhir/sid/icd-10", "code": "E11.9"},
                    {"system": "http://snomed.info/sct", "code": "44054006"}
                ],
                "text": "Type 2 Diabetes Mellitus"
            },
            "clinicalStatus": {"coding": [{"code": "active"}]}
        }
        """
        try:
            # Extract FHIR ID
            condition_fhir_id = condition_resource.get("id")

            # Extract condition display name
            code_concept = condition_resource.get("code", {})
            condition_display = code_concept.get("text", "Unknown Condition")

            # Extract ICD-10 and SNOMED codes
            icd10_code = None
            snomed_code = None

            for coding in code_concept.get("coding", []):
                system = coding.get("system", "")
                if "icd-10" in system.lower():
                    icd10_code = coding.get("code")
                elif "snomed" in system.lower():
                    snomed_code = coding.get("code")

            # Use first available code as fallback
            if not icd10_code and not snomed_code:
                codings = code_concept.get("coding", [])
                if codings:
                    icd10_code = codings[0].get("code")

            # Extract clinical status
            clinical_status = "active"
            status_coding = condition_resource.get("clinicalStatus", {}).get(
                "coding", []
            )
            if status_coding:
                clinical_status = status_coding[0].get("code", "active")

            return FHIRCondition(
                condition_fhir_id=condition_fhir_id,
                condition_code_icd10=icd10_code or "UNKNOWN",
                condition_code_snomed=snomed_code,
                condition_display=condition_display,
                condition_clinical_status=clinical_status,
            )

        except Exception as e:
            logger.error(f"Failed to parse Condition resource: {e}", exc_info=True)
            raise ValueError(f"Invalid Condition FHIR resource: {e}")

    def _parse_encounter_resource(self, encounter_resource: dict) -> FHIREncounter:
        """
        Parse Epic Encounter FHIR resource to FHIREncounter

        Args:
            encounter_resource: FHIR Encounter resource from Epic

        Returns:
            FHIREncounter with visit details

        Example Epic Encounter resource:
        {
            "resourceType": "Encounter",
            "id": "eXYZ999",
            "status": "in-progress",
            "class": {"code": "EMER", "display": "Emergency"},
            "type": [{"coding": [{"display": "Emergency room admission"}]}],
            "period": {"start": "2024-01-15T08:30:00Z"},
            "location": [{"location": {"display": "Emergency Department"}}]
        }
        """
        try:
            # Extract FHIR ID
            encounter_fhir_id = encounter_resource.get("id")

            # Extract encounter type/class
            encounter_class = encounter_resource.get("class", {})
            encounter_type = encounter_class.get("display") or encounter_class.get(
                "code", "Unknown"
            )

            # Extract encounter types
            type_descriptions = []
            for type_concept in encounter_resource.get("type", []):
                for coding in type_concept.get("coding", []):
                    display = coding.get("display")
                    if display:
                        type_descriptions.append(display)

            # Extract location
            encounter_location = None
            locations = encounter_resource.get("location", [])
            if locations:
                encounter_location = locations[0].get("location", {}).get("display")

            # Extract period
            period = encounter_resource.get("period", {})
            encounter_start = period.get("start")
            encounter_end = period.get("end")

            return FHIREncounter(
                encounter_fhir_id=encounter_fhir_id,
                encounter_type=encounter_type,
                encounter_location=encounter_location,
                encounter_start=encounter_start,
                encounter_end=encounter_end,
                encounter_status=encounter_resource.get("status", "unknown"),
            )

        except Exception as e:
            logger.error(f"Failed to parse Encounter resource: {e}", exc_info=True)
            raise ValueError(f"Invalid Encounter FHIR resource: {e}")

    def _parse_barcode(self, barcode_data: str) -> str:
        """
        Extract MRN from patient wristband barcode data

        Args:
            barcode_data: Raw barcode scan string

        Returns:
            Extracted MRN

        Common barcode formats:
        - Simple MRN: "12345678"
        - Prefixed: "MRN:12345678"
        - Complex: "^MRN^12345678^NAME^SMITH"
        """
        try:
            # Remove whitespace
            barcode_data = barcode_data.strip()

            # Check for common prefixes
            if barcode_data.startswith("MRN:"):
                return barcode_data[4:]

            # Check for caret-delimited format (common in healthcare)
            if "^" in barcode_data:
                parts = barcode_data.split("^")
                # Look for MRN indicator
                for i, part in enumerate(parts):
                    if part.upper() == "MRN" and i + 1 < len(parts):
                        return parts[i + 1]
                # Fallback - use first numeric segment
                for part in parts:
                    if part.isdigit():
                        return part

            # If all digits, assume it's the MRN
            if barcode_data.isdigit():
                return barcode_data

            # Last resort - return as-is and let Epic API handle it
            logger.warning(f"Unknown barcode format: {barcode_data}")
            return barcode_data

        except Exception as e:
            logger.error(f"Failed to parse barcode: {e}")
            raise ValueError(f"Invalid barcode format: {e}")

    # ============================================================================
    # Status and Configuration
    # ============================================================================

    def is_epic_enabled(self) -> bool:
        """Check if Epic integration is active"""
        return self.mode == IntegrationMode.EPIC_INTEGRATED

    def get_integration_status(self) -> dict:
        """Get current integration status and configuration"""
        return {
            "integration_mode": self.mode.value,
            "epic_enabled": self.is_epic_enabled(),
            "epic_base_url": self.base_url if self.is_epic_enabled() else None,
            "epic_oauth_enabled": settings.epic_oauth_enabled,
            "mrn_scanning_enabled": settings.enable_mrn_scanning,
            "write_back_enabled": settings.enable_epic_write_back,
            "sandbox_mode": settings.epic_sandbox_mode,
        }


# Global instance
ehr_service = EHRIntegrationService()
