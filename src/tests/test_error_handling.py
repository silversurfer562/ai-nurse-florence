"""
Tests for the exception handling and logging functionality.
"""
import pytest
from fastapi.testclient import TestClient
from app import app
from utils.exceptions import ServiceException, ValidationException, NotFoundException

client = TestClient(app)


def test_service_exception_handler():
    """Test that a ServiceException is properly handled."""
    
    @app.get("/test-service-exception")
    def raise_service_exception():
        raise ServiceException(
            message="Test service error",
            service_name="test_service",
            status_code=500
        )
    
    response = client.get("/test-service-exception")
    assert response.status_code == 500
    data = response.json()
    assert data["error"]["message"] == "Test service error"
    assert data["error"]["service"] == "test_service"
    assert data["error"]["type"] == "ServiceException"
    assert "request_id" in data["error"]


def test_validation_exception_handler():
    """Test that a ValidationException is properly handled."""
    
    @app.get("/test-validation-exception")
    def raise_validation_exception():
        raise ValidationException(
            message="Invalid input data",
            service_name="validation_service",
            details={"field": "username", "error": "Must be at least 3 characters"}
        )
    
    response = client.get("/test-validation-exception")
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["message"] == "Invalid input data"
    assert data["error"]["service"] == "validation_service"
    assert data["error"]["type"] == "ValidationError"
    assert data["error"]["field"] == "username"
    assert data["error"]["error"] == "Must be at least 3 characters"


def test_not_found_exception_handler():
    """Test that a NotFoundException is properly handled."""
    
    @app.get("/test-not-found-exception")
    def raise_not_found_exception():
        raise NotFoundException(
            message="Resource not found",
            service_name="resource_service",
            resource_type="article",
            resource_id="123"
        )
    
    response = client.get("/test-not-found-exception")
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["message"] == "Resource not found"
    assert data["error"]["service"] == "resource_service"
    assert data["error"]["type"] == "NotFoundError"
    assert data["error"]["resource_type"] == "article"
    assert data["error"]["resource_id"] == "123"


def test_request_id_middleware():
    """Test that the RequestIdMiddleware adds a request ID to responses."""
    
    @app.get("/test-request-id")
    def get_with_request_id():
        return {"message": "success"}
    
    response = client.get("/test-request-id")
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"] != ""