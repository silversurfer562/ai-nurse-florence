"""
Tests for clinical services
Service layer unit tests with mocking
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from src.models.schemas import (
    ClinicalDecisionRequest,
    LiteratureSearchRequest,
    SeverityLevel,
    CareSetting
)
from src.services.clinical_decision_service import ClinicalDecisionService, get_clinical_decision_service
from src.services.evidence_service import EvidenceService, get_evidence_service
from src.utils.exceptions import ValidationException

class TestClinicalDecisionService:
    """Test clinical decision support service"""
    
    @pytest.fixture
    def service(self):
        return ClinicalDecisionService()
    
    @pytest.fixture 
    def sample_request(self):
        return ClinicalDecisionRequest(
            patient_condition="heart failure",
            severity=SeverityLevel.MODERATE,
            care_setting=CareSetting.MED_SURG
        )
    
    @pytest.mark.asyncio
    async def test_get_nursing_interventions_success(self, service, sample_request):
        """Test successful intervention generation"""
        with patch('src.services.clinical_decision_service.is_openai_available', return_value=False):
            response = await service.get_nursing_interventions(sample_request)
            
            assert response.success is True
            assert "Monitor daily weights" in response.nursing_interventions
            assert len(response.safety_considerations) > 0
            assert response.evidence_level is not None
    
    @pytest.mark.asyncio
    async def test_get_nursing_interventions_with_ai(self, service, sample_request):
        """Test intervention generation with AI enhancement"""
        mock_ai_response = "Additional AI-generated clinical guidance"
        
        with patch('src.services.clinical_decision_service.is_openai_available', return_value=True), \
             patch('src.services.clinical_decision_service.clinical_decision_support', 
                   return_value=mock_ai_response):
            
            response = await service.get_nursing_interventions(sample_request)
            
            assert response.success is True
            assert mock_ai_response in response.nursing_interventions
            assert response.clinical_context["ai_enhanced"] is True
    
    @pytest.mark.asyncio
    async def test_empty_condition_validation(self, service):
        """Test validation for empty patient condition"""
        request = ClinicalDecisionRequest(
            patient_condition="",
            severity=SeverityLevel.MODERATE
        )
        
        with pytest.raises(ValidationException) as exc_info:
            await service.get_nursing_interventions(request)
        
        assert "Patient condition cannot be empty" in str(exc_info.value)
    
    def test_normalize_condition(self, service):
        """Test condition normalization"""
        assert service._normalize_condition("Heart Failure") == "heart_failure"
        assert service._normalize_condition("COPD exacerbation") == "copd_exacerbation"
    
    def test_safety_considerations_by_severity(self, service):
        """Test safety considerations based on severity"""
        critical_request = ClinicalDecisionRequest(
            patient_condition="sepsis",
            severity=SeverityLevel.CRITICAL
        )
        
        safety = service._get_safety_considerations(critical_request)
        
        assert any("continuous" in item.lower() for item in safety)
        assert any("ICU" in item for item in safety)
    
    def test_singleton_service(self):
        """Test service singleton pattern"""
        service1 = get_clinical_decision_service()
        service2 = get_clinical_decision_service()
        assert service1 is service2

class TestEvidenceService:
    """Test evidence service"""
    
    @pytest.fixture
    def service(self):
        return EvidenceService()
    
    @pytest.fixture
    def sample_search(self):
        return LiteratureSearchRequest(
            query="heart failure",
            max_results=5
        )
    
    @pytest.mark.asyncio
    async def test_search_literature_fallback(self, service, sample_search):
        """Test literature search with fallback to mock data"""
        response = await service.search_literature(sample_search)
        
        assert response.success is True
        assert len(response.articles) > 0
        assert response.total_found >= len(response.articles)
        assert "heart failure" in response.search_strategy.lower()
    
    @pytest.mark.asyncio
    async def test_search_literature_filtering(self, service):
        """Test literature search with year filtering"""
        request = LiteratureSearchRequest(
            query="diabetes",
            max_results=10,
            filter_years=2023
        )
        
        response = await service.search_literature(request)
        
        # Should only return articles from 2023 or later
        for article in response.articles:
            assert article.year >= 2023
    
    @pytest.mark.asyncio
    async def test_search_no_results(self, service):
        """Test search with no matching results"""
        request = LiteratureSearchRequest(
            query="nonexistent medical condition xyz123",
            max_results=5
        )
        
        response = await service.search_literature(request)
        
        assert response.success is True
        assert len(response.articles) == 0
        assert "No evidence found" in response.evidence_summary
    
    @pytest.mark.asyncio
    async def test_clinical_guidelines(self, service):
        """Test clinical guidelines retrieval"""
        guidelines = await service.get_clinical_guidelines("heart failure")
        
        assert "organization" in guidelines
        assert "key_recommendations" in guidelines
        assert len(guidelines["key_recommendations"]) > 0
    
    def test_evidence_summary_generation(self, service):
        """Test evidence summary generation"""
        from src.models.schemas import LiteratureItem, EvidenceLevel
        
        articles = [
            LiteratureItem(
                title="Heart Failure Management",
                authors=["Smith, J."],
                journal="Test Journal",
                year=2023,
                abstract="Test abstract",
                evidence_level=EvidenceLevel.LEVEL_I
            ),
            LiteratureItem(
                title="Heart Failure Outcomes",
                authors=["Jones, K."],
                journal="Test Journal", 
                year=2022,
                abstract="Test abstract",
                evidence_level=EvidenceLevel.LEVEL_II
            )
        ]
        
        summary = service._generate_evidence_summary(articles, "heart failure")
        
        assert "2 relevant studies" in summary
        assert "Level I" in summary
        assert "Level II" in summary

# Test fixtures for async testing
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# Integration test
@pytest.mark.asyncio
async def test_service_integration():
    """Test integration between services"""
    clinical_service = get_clinical_decision_service()
    evidence_service = get_evidence_service()
    
    # Test clinical decision
    request = ClinicalDecisionRequest(
        patient_condition="diabetes",
        severity=SeverityLevel.MODERATE
    )
    
    clinical_response = await clinical_service.get_nursing_interventions(request)
    assert clinical_response.success is True
    
    # Test evidence search for same condition
    search_request = LiteratureSearchRequest(
        query="diabetes",
        max_results=3
    )
    
    evidence_response = await evidence_service.search_literature(search_request)
    assert evidence_response.success is True
    
    # Both services should work independently
    assert clinical_response.nursing_interventions is not None
    assert len(evidence_response.articles) >= 0
