"""
Pytest fixtures for testing.

This module provides fixtures that can be used across test files
to set up test environments, mocks, and other test dependencies.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import os
from typing import Dict, Any, Generator, List, Optional

from app import app
from utils.types import (
    DiseaseResult,
    PubMedResult,
    MedlinePlusResult,
    TrialsResult
)


@pytest.fixture
def test_client() -> TestClient:
    """
    Create a FastAPI TestClient instance.
    
    Returns:
        A TestClient instance for making requests to the app
    """
    return TestClient(app)


@pytest.fixture
def mock_disease_service() -> Generator[MagicMock, None, None]:
    """
    Mock the disease_service.lookup_disease function.
    
    Yields:
        A MagicMock object that replaces the lookup_disease function
    """
    mock_result: DiseaseResult = {
        "banner": "Test banner",
        "query": "diabetes",
        "name": "Diabetes",
        "summary": "A metabolic disease that causes high blood sugar.",
        "references": [
            {
                "title": "Test Reference",
                "url": "https://example.com/reference",
                "source": "Test Source"
            }
        ]
    }
    
    with patch('services.disease_service.lookup_disease') as mock:
        mock.return_value = mock_result
        yield mock


@pytest.fixture
def mock_pubmed_service() -> Generator[MagicMock, None, None]:
    """
    Mock the pubmed_service.search_pubmed function.
    
    Yields:
        A MagicMock object that replaces the search_pubmed function
    """
    mock_result: PubMedResult = {
        "banner": "Test banner",
        "query": "diabetes treatment",
        "results": [
            {
                "pmid": "12345678",
                "title": "Test Article",
                "abstract": "This is a test abstract about diabetes treatment.",
                "url": "https://pubmed.ncbi.nlm.nih.gov/12345678/"
            }
        ]
    }
    
    with patch('services.pubmed_service.search_pubmed') as mock:
        mock.return_value = mock_result
        yield mock


@pytest.fixture
def mock_medlineplus_service() -> Generator[MagicMock, None, None]:
    """
    Mock the medlineplus_service.get_medlineplus_summary function.
    
    Yields:
        A MagicMock object that replaces the get_medlineplus_summary function
    """
    mock_result: MedlinePlusResult = {
        "topic": "diabetes",
        "summary": "Diabetes is a disease that affects how your body uses glucose.",
        "references": [
            {
                "title": "MedlinePlus: Diabetes",
                "url": "https://medlineplus.gov/diabetes.html",
                "source": "MedlinePlus"
            }
        ]
    }
    
    with patch('services.medlineplus_service.get_medlineplus_summary') as mock:
        mock.return_value = mock_result
        yield mock


@pytest.fixture
def mock_trials_service() -> Generator[MagicMock, None, None]:
    """
    Mock the trials_service.search_trials function.
    
    Yields:
        A MagicMock object that replaces the search_trials function
    """
    mock_result: TrialsResult = {
        "banner": "Test banner",
        "condition": "diabetes",
        "status": "recruiting",
        "results": [
            {
                "nct_id": "NCT12345678",
                "title": "Test Clinical Trial",
                "status": "recruiting",
                "conditions": ["diabetes", "type 2 diabetes"],
                "locations": [
                    {
                        "facility": "Test Hospital",
                        "city": "Test City",
                        "state": "Test State",
                        "country": "Test Country"
                    }
                ],
                "url": "https://clinicaltrials.gov/study/NCT12345678"
            }
        ]
    }
    
    with patch('services.trials_service.search_trials') as mock:
        mock.return_value = mock_result
        yield mock


@pytest.fixture
def mock_openai_client() -> Generator[MagicMock, None, None]:
    """
    Mock the OpenAI client with proper chat completions API structure.
    
    Yields:
        A MagicMock object that replaces the OpenAI client
    """
    mock_client = MagicMock()
    
    # Create mock response for chat completions
    mock_choice = MagicMock()
    mock_choice.message.content = "This is a test response from the AI assistant."
    
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    
    # Set up the chat.completions.create method
    mock_client.chat.completions.create.return_value = mock_response
    
    with patch('services.openai_client.get_client', return_value=mock_client):
        yield mock_client