"""
Integration tests for the Celery-based asynchronous summarization.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app import app
import time

client = TestClient(app)

@pytest.mark.integration
@patch('services.tasks.summarize_service.summarize_text')
def test_async_summarize_workflow(mock_summarize_text):
    # Mock the core summarization logic
    mock_summarize_text.return_value = {"text": "This is a mock summary."}

    # Step 1: Dispatch the async task
    response = client.post(
        "/api/v1/summarize/chat/async",
        json={"prompt": "Summarize this for me."}
    )
    assert response.status_code == 200
    data = response.json()["data"]
    task_id = data["task_id"]
    assert task_id is not None
    assert data["status"] == "PENDING" # Celery tasks are pending initially
    assert response.json()["_links"]["status"] == f"/api/v1/summarize/tasks/{task_id}"

    # In a real test environment with a running worker, we would wait.
    # Here, we can't easily test the worker, so we'll just check the API layer.
    # We can, however, mock the result backend to simulate completion.
    
    with patch('routers.summarize.AsyncResult') as mock_async_result:
        # Simulate a successful task
        mock_result_instance = MagicMock()
        mock_result_instance.status = "SUCCESS"
        mock_result_instance.ready.return_value = True
        mock_result_instance.get.return_value = {"text": "This is a mock summary."}
        mock_async_result.return_value = mock_result_instance

        # Step 2: Check the task status
        response = client.get(f"/api/v1/summarize/tasks/{task_id}")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["status"] == "SUCCESS"
        assert data["result"]["text"] == "This is a mock summary."

        # Simulate a failed task
        mock_result_instance.status = "FAILURE"
        mock_result_instance.get.return_value = ValueError("AI model failed")
        
        response = client.get(f"/api/v1/summarize/tasks/{task_id}")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["status"] == "FAILURE"
        assert "error" in data
        assert data["error"]["type"] == "ValueError"
        assert data["error"]["message"] == "AI model failed"