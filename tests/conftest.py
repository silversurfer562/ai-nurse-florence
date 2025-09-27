"""
Test configuration and fixtures following Testing Patterns from coding instructions.
Provides path setup, service layer mocks, and test client for comprehensive testing.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient

# Add project root to path following conftest.py pattern from coding instructions
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture
def test_client():
    """FastAPI test client following TestClient pattern from coding instructions."""
    from app import app
    return TestClient(app)

@pytest.fixture
def mock_disease_service():
    """
    Disease service mock following Fixture-based mocking pattern.
    Provides type-safe mock responses matching Pydantic definitions.
    """
    mock_service = AsyncMock()
    
    # Mock disease lookup response following API Design Standards
    mock_service.lookup_disease.return_value = {
        "banner": "Draft for clinician review — not medical advice. No PHI stored.",
        "query": "diabetes",
        "disease_name": "Diabetes Mellitus",
        "description": "Mock disease information for testing",
        "symptoms": ["Polyuria", "Polydipsia", "Polyphagia"],
        "risk_factors": ["Family history", "Obesity"],
        "complications": ["Diabetic nephropathy", "Retinopathy"],
        "references": ["Mock Reference 1", "Mock Reference 2"],
        "educational_note": "This is mock data for testing purposes"
    }
    
    # Mock symptom search response
    mock_service.search_by_symptoms.return_value = {
        "banner": "Draft for clinician review — not medical advice. No PHI stored.",
        "symptoms_searched": ["fatigue", "thirst"],
        "potential_diseases": [
            {
                "disease_name": "Mock Disease Match",
                "match_score": "Mock scoring",
                "matching_symptoms": ["fatigue", "thirst"],
                "additional_symptoms": ["Mock symptom A", "Mock symptom B"]
            }
        ],
        "disclaimer": "Mock symptom matching for testing",
        "educational_note": "Mock data - not for actual diagnosis"
    }
    
    return mock_service

@pytest.fixture
def mock_pubmed_service():
    """
    PubMed service mock following Service mocking pattern.
    Mock responses match Pydantic type definitions.
    """
    mock_service = AsyncMock()
    
    # Mock literature search response
    mock_service.search_literature.return_value = {
        "banner": "Draft for clinician review — not medical advice. No PHI stored.",
        "query": "nursing interventions",
        "articles": [
            {
                "title": "Mock Article: Nursing Interventions for Patient Care",
                "authors": ["Mock Author A", "Mock Author B"],
                "journal": "Mock Nursing Journal",
                "year": "2024",
                "pmid": "12345678",
                "abstract": "Mock abstract for testing purposes",
                "keywords": ["nursing", "interventions", "mock"],
                "doi": "10.1000/mock.2024"
            }
        ],
        "total_results": 1,
        "search_strategy": "Mock search strategy",
        "service_note": "Mock PubMed data for testing",
        "disclaimer": "Mock literature data - not actual articles"
    }
    
    return mock_service

@pytest.fixture
def mock_clinical_trials_service():
    """
    Clinical trials service mock following External Service Integration pattern.
    Provides educational stub responses for testing.
    """
    mock_service = AsyncMock()
    
    # Mock trials search response
    mock_service.search_trials.return_value = {
        "banner": "Draft for clinician review — not medical advice. No PHI stored.",
        "query": "diabetes",
        "trials": [
            {
                "nct_id": "NCT12345678",
                "title": "Mock Clinical Trial: Diabetes Management Study",
                "brief_summary": "Mock trial for testing purposes",
                "phase": "Phase 3",
                "status": "Recruiting",
                "conditions": ["Diabetes Mellitus"],
                "interventions": ["Mock intervention"],
                "primary_outcomes": ["Mock outcome"],
                "enrollment": 500,
                "sponsor": "Mock Medical Center"
            }
        ],
        "total_results": 1,
        "service_note": "Mock clinical trials data for testing",
        "disclaimer": "Mock trial data - not actual studies"
    }
    
    return mock_service

@pytest.fixture
def mock_sbar_service():
    """
    SBAR service mock following Wizard Pattern Implementation.
    Provides mock SBAR templates and validation responses.
    """
    mock_service = AsyncMock()
    
    # Mock SBAR template response
    mock_service.get_sbar_template.return_value = {
        "banner": "Draft for clinician review — not medical advice. No PHI stored.",
        "specialty": "general",
        "template": {
            "situation": {
                "prompt": "Mock situation prompt",
                "example": "Mock situation example",
                "required_fields": ["patient_id", "chief_complaint"]
            }
        },
        "instructions": "Mock SBAR instructions for testing",
        "timestamp": "2024-01-01T00:00:00"
    }
    
    return mock_service

@pytest.fixture
def mock_openai_service():
    """
    OpenAI service mock following OpenAI Integration pattern.
    Provides mock AI responses for testing.
    """
    mock_service = AsyncMock()
    
    # Mock AI response
    mock_service.generate_response.return_value = {
        "response": "Mock AI response for testing purposes",
        "context": "Mock context",
        "service_note": "Mock OpenAI response - testing mode",
        "disclaimer": "Mock AI content for testing only"
    }
    
    return mock_service

@pytest.fixture(autouse=True)
def mock_services(monkeypatch, mock_disease_service, mock_pubmed_service, 
                  mock_clinical_trials_service, mock_sbar_service, mock_openai_service):
    """
    Auto-use fixture that mocks all services following Service layer mocking pattern.
    Ensures tests run with consistent mock data and don't call external APIs.
    """
    
    # Mock service registry to return our mocked services
    def mock_get_service(service_name: str):
        service_map = {
            'disease': mock_disease_service,
            'pubmed': mock_pubmed_service, 
            'clinical_trials': mock_clinical_trials_service,
            'sbar': mock_sbar_service,
            'openai': mock_openai_service
        }
        return service_map.get(service_name)
    
    def mock_get_available_services():
        return {
            'disease': True,
            'pubmed': True,
            'clinical_trials': True,
            'sbar': True,
            'openai': True
        }
    
    # Patch service registry functions
    monkeypatch.setattr("src.services.get_service", mock_get_service)
    monkeypatch.setattr("src.services.get_available_services", mock_get_available_services)

# Pytest configuration following pytest.ini pattern
def pytest_configure(config):
    """Configure pytest markers following Testing Patterns."""
    config.addinivalue_line(
        "markers", "unit: mark test as unit test with mocked dependencies"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (may require external services)"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow (takes more than a few seconds)"
    )
