"""
Integration tests for the Disease Search wizard.
"""
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

@pytest.mark.integration
def test_disease_search_wizard_full_workflow():
    # Step 1: Start the wizard
    response = client.post(
        "/v1/wizards/disease-search/start",
        json={"topic": "Hypertension"}
    )
    assert response.status_code == 200
    data = response.json()["data"]
    wizard_id = data["wizard_id"]
    assert wizard_id is not None
    assert data["topic"] == "Hypertension"
    assert "Standard Treatment Guidelines" in data["suggested_sections"]

    # Step 2: Generate the report with context
    with pytest.raises(Exception): # Mocking the OpenAI call would be better here
        response = client.post(
            "/v1/wizards/disease-search/generate",
            json={
                "wizard_id": wizard_id,
                "selected_sections": ["Diagnostic Criteria", "Common Medications and Dosages"],
                "age_group": "Geriatric",
                "comorbidities": ["Type 2 Diabetes"]
            }
        )
        assert response.status_code == 200
        report_data = response.json()["data"]
        assert report_data["topic"] == "Hypertension"
        assert "Diagnostic Criteria" in report_data["report"]
        assert "Common Medications" in report_data["report"]

        # Verify session is cleaned up
        response = client.post(
            "/v1/wizards/disease-search/generate",
            json={"wizard_id": wizard_id, "selected_sections": []}
        )
        assert response.status_code == 404

@pytest.mark.integration
def test_disease_lookup_includes_wizard_link():
    # Test that the quick search endpoint returns a link to the wizard
    response = client.get("/v1/disease?q=Asthma")
    assert response.status_code == 200
    links = response.json().get("_links")
    assert links is not None
    assert "advanced_search" in links
    assert "/v1/wizards/disease-search/start?topic=Asthma" in links["advanced_search"]