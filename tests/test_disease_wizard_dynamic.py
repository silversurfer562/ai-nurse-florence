"""
Integration tests for the enhanced Disease Search wizard.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app import app

client = TestClient(app)

@pytest.fixture
def mock_openai_client():
    with patch('services.openai_client.get_client') as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        yield mock_client

@pytest.mark.integration
def test_disease_wizard_dynamic_start(mock_openai_client):
    # Mock the response for the /start endpoint's AI call
    mock_openai_client.chat.completions.create.return_value.choices[0].message.content = """
    {
        "suggested_sections": ["Overview", "Symptoms", "Treatments"],
        "pre_selected_sections": ["Overview", "Treatments"],
        "related_topics": ["COPD", "Bronchitis"]
    }
    """
    
    # Step 1: Start the wizard
    response = client.post(
        "/v1/wizards/disease-search/start",
        json={"topic": "Asthma"}
    )
    
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["topic"] == "Asthma"
    assert "Treatments" in data["suggested_sections"]
    assert "Overview" in data["pre_selected_sections"]
    assert "COPD" in data["related_topics"]
    
    # Verify the AI was called correctly
    mock_openai_client.chat.completions.create.assert_called_once()
    call_args = mock_openai_client.chat.completions.create.call_args
    assert 'For the medical topic "Asthma"' in call_args[1]["messages"][1]["content"]

@pytest.mark.integration
def test_disease_wizard_generates_next_steps(mock_openai_client):
    # --- Start the wizard first to get a wizard_id ---
    start_response_mock = MagicMock()
    start_response_mock.choices[0].message.content = '{"suggested_sections": [], "pre_selected_sections": [], "related_topics": []}'
    
    # --- Configure mocks for the /generate endpoint ---
    report_response_mock = MagicMock()
    report_response_mock.choices[0].message.content = "This is the generated report on Hypertension."
    
    next_steps_response_mock = MagicMock()
    next_steps_response_mock.choices[0].message.content = """
    {
        "suggested_next_steps": [
            {
                "title": "Create Patient Handout",
                "prompt": "Generate a patient-friendly handout about Hypertension.",
                "type": "patient_education"
            }
        ]
    }
    """
    # Set up the side_effect to return different values for each call
    mock_openai_client.chat.completions.create.side_effect = [
        start_response_mock, # For the call in /start
        report_response_mock, # For the report generation in /generate
        next_steps_response_mock # For the next steps generation in /generate
    ]

    # Start the wizard
    start_response = client.post("/v1/wizards/disease-search/start", json={"topic": "Hypertension"})
    wizard_id = start_response.json()["data"]["wizard_id"]

    # Step 2: Generate the report
    response = client.post(
        "/v1/wizards/disease-search/generate",
        json={
            "wizard_id": wizard_id,
            "selected_sections": ["Overview"],
            "age_group": "Geriatric"
        }
    )
    
    assert response.status_code == 200
    data = response.json()["data"]
    assert "This is the generated report" in data["report"]
    
    # Check for suggested next steps
    next_steps = data["suggested_next_steps"]
    assert len(next_steps) > 0
    assert next_steps[0]["title"] == "Create Patient Handout"
    assert "Hypertension" in next_steps[0]["prompt"]
    
    # Verify the AI was called three times (start, report, next_steps)
    assert mock_openai_client.chat.completions.create.call_count == 3
    
    # Check the prompt for the final call (next steps generation)
    final_call_args = mock_openai_client.chat.completions.create.call_args
    assert "Based on the following clinical report" in final_call_args[1]["messages"][1]["content"]
    assert "Age Group: Geriatric" in final_call_args[1]["messages"][1]["content"]