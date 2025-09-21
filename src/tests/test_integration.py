"""
Integration tests for API endpoints.

These tests verify that the API endpoints work correctly with the service layer.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

pytestmark = pytest.mark.integration


def test_disease_endpoint(test_client: TestClient, mock_disease_service: MagicMock):
    """Test that the disease endpoint returns the expected response."""
    response = test_client.get("/v1/disease?q=diabetes")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Diabetes"
    assert data["query"] == "diabetes"
    assert "summary" in data
    assert "references" in data
    assert len(data["references"]) > 0
    mock_disease_service.assert_called_once_with("diabetes")


def test_pubmed_search_endpoint(test_client: TestClient, mock_pubmed_service: MagicMock):
    """Test that the PubMed search endpoint returns the expected response."""
    response = test_client.get("/v1/pubmed/search?q=diabetes+treatment&max_results=5")
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "diabetes treatment"
    assert "results" in data
    assert len(data["results"]) > 0
    assert "title" in data["results"][0]
    mock_pubmed_service.assert_called_once_with("diabetes treatment", max_results=5)


def test_medlineplus_summary_endpoint(test_client: TestClient, mock_medlineplus_service: MagicMock):
    """Test that the MedlinePlus summary endpoint returns the expected response."""
    response = test_client.get("/v1/medlineplus/summary?topic=diabetes")
    assert response.status_code == 200
    data = response.json()
    assert data["topic"] == "diabetes"
    assert "summary" in data
    assert "references" in data
    mock_medlineplus_service.assert_called_once_with("diabetes")


def test_trials_search_endpoint(test_client: TestClient, mock_trials_service: MagicMock):
    """Test that the clinical trials search endpoint returns the expected response."""
    response = test_client.get("/v1/clinicaltrials/search?condition=diabetes&status=recruiting&max_results=5")
    assert response.status_code == 200
    data = response.json()
    assert data["condition"] == "diabetes"
    assert data["status"] == "recruiting"
    assert "results" in data
    assert len(data["results"]) > 0
    assert "title" in data["results"][0]
    mock_trials_service.assert_called_once_with(condition="diabetes", status="recruiting", max_results=5)


def test_summarize_chat_endpoint(test_client: TestClient, mock_openai_client: MagicMock):
    """Test that the summarize chat endpoint returns the expected response."""
    response = test_client.post(
        "/api/v1/summarize/chat",
        json={"prompt": "Summarize this text", "model": "gpt-4o-mini"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "text" in data
    assert data["text"] == "This is a test response from the AI assistant."
    mock_openai_client.chat.completions.create.assert_called_once()
    # Verify the prompt and model were passed correctly
    call_args = mock_openai_client.chat.completions.create.call_args
    assert call_args[1]["model"] == "gpt-4o-mini"
    # Check that the messages structure is correct
    messages = call_args[1]["messages"]
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert "Summarize this text" in messages[1]["content"]