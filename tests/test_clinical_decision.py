from fastapi.testclient import TestClient


def test_interventions_endpoint_imports_app():
    """Sanity test: importing app and hitting the interventions endpoint returns 200."""
    import importlib
    app_module = importlib.import_module('app')
    client = TestClient(app_module.app)

    response = client.post(
        "/api/v1/clinical-decision-support/interventions",
        params={
            "patient_condition": "acute heart failure",
            "severity": "moderate",
        }
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data.get("success", False) is True
    # The stub returns a data.payload-like structure in 'data'
    assert "data" in data
    payload = data["data"]
    assert "nursing_interventions" in payload
