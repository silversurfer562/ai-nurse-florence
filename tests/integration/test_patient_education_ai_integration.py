"""
Integration tests for Patient Education Document Generation with Claude AI

Tests the full patient education document generation workflow including:
- Claude AI integration for missing content
- Fallback behavior when AI is unavailable
- Multi-language support with AI
- Reading level adaptation

Version: 1.0.0
Created: 2025-10-05
"""

from unittest.mock import AsyncMock, patch

import pytest

from routers.patient_education_documents import (
    PatientEducationRequest,
    _build_document_content,
)
from src.models.content_settings import DiagnosisContentMap


class TestPatientEducationAIIntegration:
    """Test suite for Claude AI integration in patient education documents"""

    @pytest.fixture
    def sample_request(self):
        """Create sample patient education request"""
        return PatientEducationRequest(
            diagnosis_id="1",
            icd10_code="E11.9",
            patient_name="John Doe",
            preferred_language="en",
            reading_level="6th-8th grade",
            care_setting="home",
            include_description=True,
            include_warning_signs=True,
            include_medications=True,
            include_diet=True,
            include_follow_up=True,
            include_medlineplus=False,
            custom_instructions=None,
            follow_up_date=None,
        )

    @pytest.fixture
    def diagnosis_with_content(self):
        """Diagnosis with full database content"""
        return DiagnosisContentMap(
            id=1,
            diagnosis_display="Type 2 Diabetes Mellitus",
            patient_friendly_description="A condition where your body doesn't use insulin properly, causing high blood sugar levels.",
            standard_warning_signs=[
                "Severe confusion",
                "Extreme thirst",
                "Rapid breathing",
            ],
            standard_medications=[
                {
                    "medication_display": "Metformin",
                    "dosage": "500mg twice daily",
                    "purpose": "Controls blood sugar levels",
                }
            ],
            standard_diet_instructions="Limit sugar and carbohydrates. Eat regular meals.",
            standard_follow_up_instructions="Check blood sugar daily. Follow up in 2 weeks.",
        )

    @pytest.fixture
    def diagnosis_without_content(self):
        """Diagnosis with missing database content (requires AI)"""
        return DiagnosisContentMap(
            id=2,
            diagnosis_display="Chronic Obstructive Pulmonary Disease",
            patient_friendly_description=None,  # Missing - should trigger AI
            standard_warning_signs=["Severe shortness of breath", "Blue lips"],
            standard_medications=None,
            standard_diet_instructions=None,
            standard_follow_up_instructions=None,  # Missing - should trigger AI
        )

    @pytest.mark.asyncio
    async def test_build_content_with_database_only(
        self, sample_request, diagnosis_with_content
    ):
        """Test document generation when all content exists in database (no AI needed)"""
        with patch("routers.patient_education_documents.claude_service") as mock_claude:
            result = await _build_document_content(
                request=sample_request,
                diagnosis=diagnosis_with_content,
                medlineplus_content=None,
            )

            # AI should NOT be called when database has content
            mock_claude.generate_patient_education.assert_not_called()

            # Verify document structure
            assert result["diagnosis_name"] == "Type 2 Diabetes Mellitus"
            assert result["patient_name"] == "John Doe"
            assert (
                len(result["sections"]) >= 3
            )  # Description, warnings, medications, diet, follow-up

            # Find description section
            desc_section = next(
                s for s in result["sections"] if s.get("icon") == "info-circle"
            )
            assert "insulin" in desc_section["content"].lower()

    @pytest.mark.asyncio
    async def test_build_content_with_ai_fallback(
        self, sample_request, diagnosis_without_content
    ):
        """Test AI is used when database content is missing"""
        mock_ai_response = {
            "response": "COPD is a lung disease that makes it hard to breathe. Your airways become damaged over time.",
            "success": True,
        }

        with patch("routers.patient_education_documents.claude_service") as mock_claude:
            mock_claude.generate_patient_education = AsyncMock(
                return_value=mock_ai_response
            )

            result = await _build_document_content(
                request=sample_request,
                diagnosis=diagnosis_without_content,
                medlineplus_content=None,
            )

            # AI should be called for missing description
            assert mock_claude.generate_patient_education.call_count >= 1

            # Verify AI content was used
            desc_section = next(
                s for s in result["sections"] if s.get("icon") == "info-circle"
            )
            assert "COPD" in desc_section["content"]
            assert "lung disease" in desc_section["content"].lower()

    @pytest.mark.asyncio
    async def test_ai_integration_with_patient_context(
        self, sample_request, diagnosis_without_content
    ):
        """Test that AI receives proper patient context"""
        with patch("routers.patient_education_documents.claude_service") as mock_claude:
            mock_claude.generate_patient_education = AsyncMock(
                return_value={"response": "AI-generated content", "success": True}
            )

            await _build_document_content(
                request=sample_request,
                diagnosis=diagnosis_without_content,
                medlineplus_content=None,
            )

            # Verify AI was called with correct patient context
            call_args = mock_claude.generate_patient_education.call_args
            assert call_args[1]["condition"] == "Chronic Obstructive Pulmonary Disease"
            assert call_args[1]["patient_context"]["reading_level"] == "6th-8th grade"
            assert call_args[1]["patient_context"]["care_setting"] == "home"
            assert call_args[1]["patient_context"]["patient_name"] == "John Doe"
            assert call_args[1]["language"] == "en"

    @pytest.mark.asyncio
    async def test_ai_failure_graceful_degradation(
        self, sample_request, diagnosis_without_content
    ):
        """Test graceful fallback when AI service fails"""
        with patch("routers.patient_education_documents.claude_service") as mock_claude:
            # Simulate AI failure
            mock_claude.generate_patient_education = AsyncMock(
                side_effect=Exception("AI service unavailable")
            )

            result = await _build_document_content(
                request=sample_request,
                diagnosis=diagnosis_without_content,
                medlineplus_content=None,
            )

            # Should still generate document with fallback content
            assert result is not None
            assert len(result["sections"]) > 0

            # Description section should use diagnosis display name as fallback
            desc_section = next(
                s for s in result["sections"] if s.get("icon") == "info-circle"
            )
            assert "Chronic Obstructive Pulmonary Disease" in desc_section["content"]

    @pytest.mark.asyncio
    async def test_follow_up_instructions_ai_enhancement(
        self, sample_request, diagnosis_without_content
    ):
        """Test AI generates follow-up instructions when missing from database"""
        mock_followup_response = {
            "response": "Schedule a follow-up appointment within 1 week. Monitor your breathing daily. Keep rescue inhaler accessible.",
            "success": True,
        }

        with patch("routers.patient_education_documents.claude_service") as mock_claude:
            mock_claude.generate_patient_education = AsyncMock(
                return_value=mock_followup_response
            )

            result = await _build_document_content(
                request=sample_request,
                diagnosis=diagnosis_without_content,
                medlineplus_content=None,
            )

            # AI should be called multiple times (description + follow-up)
            assert mock_claude.generate_patient_education.call_count >= 2

            # Verify follow-up section has AI-generated content
            followup_section = next(
                s for s in result["sections"] if s.get("icon") == "calendar-check"
            )
            assert (
                "breathing" in followup_section["content"].lower()
                or "inhaler" in followup_section["content"].lower()
            )

    @pytest.mark.asyncio
    async def test_multilingual_ai_support(self, diagnosis_without_content):
        """Test AI integration works with different languages"""
        spanish_request = PatientEducationRequest(
            diagnosis_id="2",
            icd10_code="J44.9",
            patient_name="Maria Garcia",
            preferred_language="es",
            reading_level="6th-8th grade",
            care_setting="home",
            include_description=True,
            include_warning_signs=False,
            include_medications=False,
            include_diet=False,
            include_follow_up=False,
            include_medlineplus=False,
            custom_instructions=None,
            follow_up_date=None,
        )

        with patch("routers.patient_education_documents.claude_service") as mock_claude:
            mock_claude.generate_patient_education = AsyncMock(
                return_value={
                    "response": "La EPOC es una enfermedad pulmonar crónica que dificulta la respiración.",
                    "success": True,
                }
            )

            result = await _build_document_content(
                request=spanish_request,
                diagnosis=diagnosis_without_content,
                medlineplus_content=None,
            )

            # Verify AI was called with Spanish language parameter
            call_args = mock_claude.generate_patient_education.call_args
            assert call_args[1]["language"] == "es"

            # Verify Spanish content was used
            desc_section = next(
                s for s in result["sections"] if s.get("icon") == "info-circle"
            )
            assert (
                "EPOC" in desc_section["content"]
                or "enfermedad" in desc_section["content"].lower()
            )

    @pytest.mark.asyncio
    async def test_reading_level_adaptation(self, diagnosis_without_content):
        """Test AI receives reading level for appropriate language complexity"""
        advanced_request = PatientEducationRequest(
            diagnosis_id="2",
            icd10_code="J44.9",
            patient_name="Dr. Smith",
            preferred_language="en",
            reading_level="College",
            care_setting="hospital",
            include_description=True,
            include_warning_signs=False,
            include_medications=False,
            include_diet=False,
            include_follow_up=False,
            include_medlineplus=False,
            custom_instructions=None,
            follow_up_date=None,
        )

        with patch("routers.patient_education_documents.claude_service") as mock_claude:
            mock_claude.generate_patient_education = AsyncMock(
                return_value={
                    "response": "COPD is a progressive obstructive pulmonary disease characterized by chronic airflow limitation.",
                    "success": True,
                }
            )

            await _build_document_content(
                request=advanced_request,
                diagnosis=diagnosis_without_content,
                medlineplus_content=None,
            )

            # Verify reading level was passed to AI
            call_args = mock_claude.generate_patient_education.call_args
            assert call_args[1]["patient_context"]["reading_level"] == "College"

    @pytest.mark.asyncio
    async def test_skip_description_when_not_requested(
        self, sample_request, diagnosis_without_content
    ):
        """Test AI is not called when description section is not requested"""
        sample_request.include_description = False

        with patch("routers.patient_education_documents.claude_service"):
            result = await _build_document_content(
                request=sample_request,
                diagnosis=diagnosis_without_content,
                medlineplus_content=None,
            )

            # AI might still be called for follow-up, but not for description
            # Verify no description section exists
            desc_sections = [
                s for s in result["sections"] if s.get("icon") == "info-circle"
            ]
            assert len(desc_sections) == 0
