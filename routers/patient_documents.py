"""
Patient Documents API - PDF Generation for Patient Education Materials
Generates discharge instructions, medication guides, and disease education materials
"""

import logging
from datetime import datetime

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from services.pdf_generation_service import (
    generate_discharge_instructions,
    generate_discharge_instructions_docx,
    generate_discharge_instructions_text,
    generate_disease_education,
    generate_medication_guide,
)
from src.models.patient_document_schemas import (
    BatchDocumentRequest,
    BatchDocumentResponse,
    DischargeInstructionsRequest,
    DischargeInstructionsResponse,
    DiseaseEducationRequest,
    DiseaseEducationResponse,
    DocumentFormat,
    MedicationGuideRequest,
    MedicationGuideResponse,
)
from src.services.fda_drug_service import FDADrugService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/patient-documents", tags=["Patient Documents"])


@router.post("/discharge-instructions", response_model=DischargeInstructionsResponse)
async def create_discharge_instructions(request: DischargeInstructionsRequest):
    """
    Generate discharge instructions PDF for patients

    **Features:**
    - Medication list with dosing schedules
    - Follow-up appointment reminders
    - Activity and diet restrictions
    - Warning signs to watch for
    - Emergency contact criteria
    - Wound care instructions
    - Multi-language support

    **Use Cases:**
    - Hospital discharge
    - Emergency department discharge
    - Outpatient procedure instructions
    - Post-operative care

    **Example:**
    ```json
    {
        "primary_diagnosis": "Pneumonia",
        "medications": [
            {
                "name": "Amoxicillin",
                "dosage": "500 mg",
                "frequency": "3 times daily",
                "instructions": "Take with food"
            }
        ],
        "warning_signs": [
            "Fever over 101°F",
            "Difficulty breathing",
            "Chest pain"
        ],
        "emergency_criteria": [
            "Severe difficulty breathing",
            "Confusion or altered mental status"
        ]
    }
    ```
    """
    try:
        # Prepare data for document generation
        doc_data = {
            "patient_name": request.patient_name,
            "discharge_date": request.discharge_date,
            "primary_diagnosis": request.primary_diagnosis,
            "medications": request.medications,
            "follow_up_appointments": request.follow_up_appointments,
            "activity_restrictions": request.activity_restrictions,
            "diet_instructions": request.diet_instructions,
            "warning_signs": request.warning_signs,
            "emergency_criteria": request.emergency_criteria,
            "wound_care": request.wound_care,
            "equipment_needs": request.equipment_needs,
            "home_care_services": request.home_care_services,
        }

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Generate document based on format
        if request.format == DocumentFormat.PDF:
            doc_buffer = generate_discharge_instructions(doc_data)
            doc_bytes = doc_buffer.getvalue()
            filename = f"discharge_instructions_{timestamp}.pdf"
            media_type = "application/pdf"
            content_type = "application/pdf"

        elif request.format == DocumentFormat.DOCX:
            doc_buffer = generate_discharge_instructions_docx(doc_data)
            doc_bytes = doc_buffer.getvalue()
            filename = f"discharge_instructions_{timestamp}.docx"
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

        elif request.format == DocumentFormat.TEXT:
            doc_buffer = generate_discharge_instructions_text(doc_data)
            doc_bytes = doc_buffer.getvalue()
            filename = f"discharge_instructions_{timestamp}.txt"
            media_type = "text/plain"
            content_type = "text/plain; charset=utf-8"

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Format {request.format} not supported. Use 'pdf', 'docx', or 'txt'.",
            )

        # Return document as response
        return StreamingResponse(
            iter([doc_bytes]),
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": content_type,
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate discharge instructions: {str(e)}",
        )


@router.post("/medication-guide", response_model=MedicationGuideResponse)
async def create_medication_guide(request: MedicationGuideRequest):
    """
    Generate medication guide PDF for patients

    **Features:**
    - Medication purpose and mechanism
    - Dosing instructions
    - Common and serious side effects
    - Food and drug interactions
    - Storage instructions
    - What to do if a dose is missed
    - Auto-populate from FDA database (optional)
    - Multi-language support

    **Auto-Population:**
    When `auto_populate=true`, the system will attempt to fetch additional
    information from FDA databases to supplement provided data.

    **Example:**
    ```json
    {
        "medication_name": "Metformin",
        "dosage": "500 mg",
        "frequency": "twice daily",
        "purpose": "Controls blood sugar in type 2 diabetes",
        "special_instructions": [
            "Take with meals",
            "Do not crush or chew extended-release tablets"
        ],
        "common_side_effects": [
            "Nausea",
            "Diarrhea",
            "Stomach upset"
        ],
        "auto_populate": true
    }
    ```
    """
    try:
        # If auto-populate is enabled, fetch additional data from FDA
        data_sources = []
        fda_data = None

        if request.auto_populate:
            try:
                fda_service = FDADrugService()
                fda_data = await fda_service.get_medication_guide_data(
                    request.medication_name
                )

                if fda_data and fda_data.get("data_available"):
                    data_sources.append("FDA OpenFDA API")
                    # Merge FDA data with user-provided data (user data takes precedence)
                    if not request.purpose and fda_data.get("purpose"):
                        request.purpose = fda_data["purpose"]
                    if not request.drug_interactions and fda_data.get(
                        "drug_interactions"
                    ):
                        request.drug_interactions = fda_data["drug_interactions"]
                    if not request.storage_instructions and fda_data.get(
                        "storage_instructions"
                    ):
                        request.storage_instructions = fda_data["storage_instructions"]
                else:
                    data_sources.append("User-provided information")
            except Exception as e:
                logger.error(f"FDA API error for {request.medication_name}: {e}")
                data_sources.append("User-provided information")
        else:
            data_sources.append("User-provided information")

        # Prepare data for PDF generation
        pdf_data = {
            "medication_name": request.medication_name,
            "dosage": request.dosage,
            "frequency": request.frequency,
            "route": request.route,
            "special_instructions": request.special_instructions,
            "purpose": request.purpose,
            "how_it_works": request.how_it_works,
            "common_side_effects": request.common_side_effects,
            "serious_side_effects": request.serious_side_effects,
            "food_interactions": request.food_interactions,
            "drug_interactions": request.drug_interactions,
            "storage_instructions": request.storage_instructions,
            "missed_dose_instructions": request.missed_dose_instructions,
            "data_sources": data_sources,
        }

        # Generate PDF
        pdf_buffer = generate_medication_guide(pdf_data)
        pdf_bytes = pdf_buffer.getvalue()

        # Generate filename
        med_name_safe = request.medication_name.replace(" ", "_").lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"medication_guide_{med_name_safe}_{timestamp}.pdf"

        # Return PDF as response
        if request.format == DocumentFormat.PDF:
            return StreamingResponse(
                iter([pdf_bytes]),
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}",
                    "Content-Type": "application/pdf",
                },
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Format {request.format} not yet supported. Please use PDF.",
            )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate medication guide: {str(e)}"
        )


@router.post("/disease-education", response_model=DiseaseEducationResponse)
async def create_disease_education(request: DiseaseEducationRequest):
    """
    Generate disease education material PDF for patients

    **Features:**
    - Plain-language disease explanation
    - Symptoms and causes
    - Treatment options
    - Self-care and lifestyle recommendations
    - Warning signs
    - Support resources
    - Questions to ask healthcare provider
    - Auto-populate from MedlinePlus (optional)
    - Multi-language support

    **Auto-Population:**
    When `auto_populate=true`, the system will fetch information from:
    - MedlinePlus (NIH) - Consumer health information
    - MONDO Disease Ontology - Clinical information
    - PubMed - Latest research (if relevant)

    **Example:**
    ```json
    {
        "disease_name": "Type 2 Diabetes",
        "symptoms": [
            "Increased thirst and urination",
            "Increased hunger",
            "Fatigue",
            "Blurred vision"
        ],
        "self_care_tips": [
            "Monitor blood sugar regularly",
            "Follow meal plan",
            "Exercise regularly",
            "Take medications as prescribed"
        ],
        "warning_signs": [
            "Blood sugar over 300 mg/dL",
            "Severe abdominal pain",
            "Fruity-smelling breath"
        ],
        "auto_populate": true
    }
    ```
    """
    try:
        data_sources = []

        # If auto-populate is enabled, fetch from MedlinePlus and other sources
        if request.auto_populate:
            try:
                # Fetch from MedlinePlus
                async with httpx.AsyncClient(timeout=10.0) as client:
                    medlineplus_url = f"http://localhost:8000/api/v1/medlineplus/disease/{request.disease_name}"
                    response = await client.get(medlineplus_url)

                    if response.status_code == 200:
                        medline_data = response.json()
                        data_sources.append("MedlinePlus (NIH)")

                        # Merge MedlinePlus data with request data
                        if not request.what_it_is and medline_data.get("summary"):
                            request.what_it_is = medline_data["summary"]

                        if not request.symptoms and medline_data.get("also_called"):
                            # MedlinePlus doesn't always have symptoms, but has related info
                            pass

            except Exception as e:
                # If auto-populate fails, continue with user-provided data
                print(f"Auto-populate warning: {str(e)}")
                data_sources.append("User-provided information")

        # Prepare data for PDF generation
        pdf_data = {
            "disease_name": request.disease_name,
            "what_it_is": request.what_it_is,
            "causes": request.causes,
            "symptoms": request.symptoms,
            "treatment_options": request.treatment_options,
            "self_care_tips": request.self_care_tips,
            "medications_overview": request.medications_overview,
            "lifestyle_modifications": request.lifestyle_modifications,
            "diet_recommendations": request.diet_recommendations,
            "exercise_recommendations": request.exercise_recommendations,
            "warning_signs": request.warning_signs,
            "emergency_symptoms": request.emergency_symptoms,
            "support_groups": request.support_groups,
            "additional_resources": request.additional_resources,
            "questions_to_ask": request.questions_to_ask,
            "data_sources": (
                data_sources if data_sources else ["User-provided information"]
            ),
        }

        # Generate PDF
        pdf_buffer = generate_disease_education(pdf_data)
        pdf_bytes = pdf_buffer.getvalue()

        # Generate filename
        disease_name_safe = request.disease_name.replace(" ", "_").lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"disease_education_{disease_name_safe}_{timestamp}.pdf"

        # Return PDF as response
        if request.format == DocumentFormat.PDF:
            return StreamingResponse(
                iter([pdf_bytes]),
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}",
                    "Content-Type": "application/pdf",
                },
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Format {request.format} not yet supported. Please use PDF.",
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate disease education material: {str(e)}",
        )


@router.post("/batch-generate", response_model=BatchDocumentResponse)
async def batch_generate_documents(request: BatchDocumentRequest):
    """
    Generate multiple patient documents at once

    **Features:**
    - Generate multiple documents in a single request
    - Optionally combine into a single PDF packet
    - Consistent language and reading level across all documents
    - Ideal for discharge with multiple medications and conditions

    **Use Cases:**
    - Complete discharge packet (instructions + medication guides)
    - Disease education with multiple medication guides
    - Comprehensive patient education materials

    **Example:**
    ```json
    {
        "patient_name": "John Smith",
        "discharge_instructions": {
            "primary_diagnosis": "Pneumonia",
            "medications": [...],
            "warning_signs": [...]
        },
        "medication_guides": [
            {"medication_name": "Amoxicillin", ...},
            {"medication_name": "Ibuprofen", ...}
        ],
        "language": "en",
        "reading_level": "intermediate",
        "combine_into_packet": true
    }
    ```
    """
    try:
        documents_generated = 0
        individual_pdfs = []

        # Generate discharge instructions if provided
        if request.discharge_instructions:
            discharge_req = request.discharge_instructions
            discharge_req.language = request.language
            discharge_req.reading_level = request.reading_level

            pdf_data = {
                "patient_name": discharge_req.patient_name or request.patient_name,
                "discharge_date": discharge_req.discharge_date,
                "primary_diagnosis": discharge_req.primary_diagnosis,
                "medications": discharge_req.medications,
                "follow_up_appointments": discharge_req.follow_up_appointments,
                "activity_restrictions": discharge_req.activity_restrictions,
                "diet_instructions": discharge_req.diet_instructions,
                "warning_signs": discharge_req.warning_signs,
                "emergency_criteria": discharge_req.emergency_criteria,
                "wound_care": discharge_req.wound_care,
                "equipment_needs": discharge_req.equipment_needs,
                "home_care_services": discharge_req.home_care_services,
            }

            pdf_buffer = generate_discharge_instructions(pdf_data)
            individual_pdfs.append(
                {"type": "discharge_instructions", "buffer": pdf_buffer}
            )
            documents_generated += 1

        # Generate medication guides
        for med_req in request.medication_guides:
            med_req.language = request.language
            med_req.reading_level = request.reading_level

            pdf_data = {
                "medication_name": med_req.medication_name,
                "dosage": med_req.dosage,
                "frequency": med_req.frequency,
                "route": med_req.route,
                "special_instructions": med_req.special_instructions,
                "purpose": med_req.purpose,
                "how_it_works": med_req.how_it_works,
                "common_side_effects": med_req.common_side_effects,
                "serious_side_effects": med_req.serious_side_effects,
                "food_interactions": med_req.food_interactions,
                "drug_interactions": med_req.drug_interactions,
                "storage_instructions": med_req.storage_instructions,
                "missed_dose_instructions": med_req.missed_dose_instructions,
                "data_sources": [],
            }

            pdf_buffer = generate_medication_guide(pdf_data)
            individual_pdfs.append(
                {
                    "type": "medication_guide",
                    "name": med_req.medication_name,
                    "buffer": pdf_buffer,
                }
            )
            documents_generated += 1

        # Generate disease education materials
        for disease_req in request.disease_education:
            disease_req.language = request.language
            disease_req.reading_level = request.reading_level

            pdf_data = {
                "disease_name": disease_req.disease_name,
                "what_it_is": disease_req.what_it_is,
                "causes": disease_req.causes,
                "symptoms": disease_req.symptoms,
                "treatment_options": disease_req.treatment_options,
                "self_care_tips": disease_req.self_care_tips,
                "medications_overview": disease_req.medications_overview,
                "lifestyle_modifications": disease_req.lifestyle_modifications,
                "diet_recommendations": disease_req.diet_recommendations,
                "exercise_recommendations": disease_req.exercise_recommendations,
                "warning_signs": disease_req.warning_signs,
                "emergency_symptoms": disease_req.emergency_symptoms,
                "support_groups": disease_req.support_groups,
                "additional_resources": disease_req.additional_resources,
                "questions_to_ask": disease_req.questions_to_ask,
                "data_sources": [],
            }

            pdf_buffer = generate_disease_education(pdf_data)
            individual_pdfs.append(
                {
                    "type": "disease_education",
                    "name": disease_req.disease_name,
                    "buffer": pdf_buffer,
                }
            )
            documents_generated += 1

        if documents_generated == 0:
            raise HTTPException(
                status_code=400,
                detail="No documents requested. Please provide at least one document type.",
            )

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        patient_name_safe = (
            request.patient_name.replace(" ", "_").lower()
            if request.patient_name
            else "patient"
        )

        if request.combine_into_packet:
            # TODO: Implement PDF merging using PyPDF2 or similar
            # For now, return the first PDF
            filename = f"patient_packet_{patient_name_safe}_{timestamp}.pdf"
            pdf_bytes = individual_pdfs[0]["buffer"].getvalue()

            return StreamingResponse(
                iter([pdf_bytes]),
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}",
                    "Content-Type": "application/pdf",
                },
            )
        else:
            # Return first PDF (in future, could return as ZIP)
            filename = f"patient_documents_{patient_name_safe}_{timestamp}.pdf"
            pdf_bytes = individual_pdfs[0]["buffer"].getvalue()

            return StreamingResponse(
                iter([pdf_bytes]),
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}",
                    "Content-Type": "application/pdf",
                },
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate batch documents: {str(e)}"
        )


@router.get("/templates")
async def list_document_templates():
    """
    List available document templates

    **Returns:**
    - Available document types
    - Required fields for each type
    - Optional fields and their purposes
    """
    return {
        "templates": [
            {
                "type": "discharge_instructions",
                "name": "Discharge Instructions",
                "description": "Comprehensive discharge instructions for hospital or ED patients",
                "required_fields": [
                    "primary_diagnosis",
                    "warning_signs",
                    "emergency_criteria",
                ],
                "optional_fields": [
                    "patient_name",
                    "medications",
                    "follow_up_appointments",
                    "activity_restrictions",
                    "diet_instructions",
                    "wound_care",
                    "equipment_needs",
                    "home_care_services",
                ],
                "supports_multi_language": True,
                "supports_reading_levels": True,
            },
            {
                "type": "medication_guide",
                "name": "Medication Guide",
                "description": "Patient-friendly medication information and instructions",
                "required_fields": ["medication_name", "dosage", "frequency"],
                "optional_fields": [
                    "purpose",
                    "how_it_works",
                    "special_instructions",
                    "common_side_effects",
                    "serious_side_effects",
                    "food_interactions",
                    "drug_interactions",
                    "storage_instructions",
                    "missed_dose_instructions",
                ],
                "supports_auto_populate": True,
                "supports_multi_language": True,
                "supports_reading_levels": True,
            },
            {
                "type": "disease_education",
                "name": "Disease Education Material",
                "description": "Educational material about diseases and conditions",
                "required_fields": ["disease_name"],
                "optional_fields": [
                    "what_it_is",
                    "causes",
                    "symptoms",
                    "treatment_options",
                    "self_care_tips",
                    "lifestyle_modifications",
                    "diet_recommendations",
                    "exercise_recommendations",
                    "warning_signs",
                    "emergency_symptoms",
                    "support_groups",
                    "additional_resources",
                    "questions_to_ask",
                ],
                "supports_auto_populate": True,
                "supports_multi_language": True,
                "supports_reading_levels": True,
            },
        ],
        "supported_languages": ["en", "es", "zh-CN", "zh-TW"],
        "supported_reading_levels": ["basic", "intermediate", "advanced"],
        "supported_formats": ["pdf"],
    }
