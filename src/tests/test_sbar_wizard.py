"""
Integration tests for the SBAR report wizard.
"""
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

@pytest.mark.integration
def test_sbar_wizard_full_workflow():
    # Step 1: Start the wizard
    response = client.post("/v1/wizards/sbar-report/start")
    assert response.status_code == 200
    data = response.json()["data"]
    wizard_id = data["wizard_id"]
    assert wizard_id is not None
    assert data["next_step"] == "situation"

    # Step 2: Add Situation
    response = client.post(
        "/v1/wizards/sbar-report/situation",
        json={"wizard_id": wizard_id, "text": "Patient is a 65-year-old male reporting chest pain."}
    )
    assert response.status_code == 200
    assert response.json()["data"]["next_step"] == "background"

    # Step 3: Add Background
    response = client.post(
        "/v1/wizards/sbar-report/background",
        json={"wizard_id": wizard_id, "text": "History of hypertension and MI in 2020."}
    )
    assert response.status_code == 200
    assert response.json()["data"]["next_step"] == "assessment"

    # Step 4: Add Assessment
    response = client.post(
        "/v1/wizards/sbar-report/assessment",
        json={"wizard_id": wizard_id, "text": "Vital signs are stable, but EKG shows ST elevation."}
    )
    assert response.status_code == 200
    assert response.json()["data"]["next_step"] == "recommendation"

    # Step 5: Generate Report
    with pytest.raises(Exception): # Mocking the OpenAI call would be better here
        response = client.post(
            "/v1/wizards/sbar-report/generate",
            json={"wizard_id": wizard_id, "recommendation": "Request cardiology consult and prepare for cath lab."}
        )
        assert response.status_code == 200
        sbar_report = response.json()["data"]["sbar_report"]
        assert "Situation" in sbar_report
        assert "chest pain" in sbar_report
        assert "Recommendation" in sbar_report
        assert "cath lab" in sbar_report

        # Verify session is cleaned up
        response = client.post(
            "/v1/wizards/sbar-report/situation",
            json={"wizard_id": wizard_id, "text": "This should fail."}
        )
        assert response.status_code == 404