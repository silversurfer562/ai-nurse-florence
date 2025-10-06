"""
Unit tests for BaseService foundation class.

Tests the core Service Layer Architecture patterns including response formatting,
error handling with graceful degradation, and abstract method enforcement.
"""

from datetime import datetime
from typing import Any, Dict

import pytest

from src.services.base_service import BaseService
from src.utils.exceptions import ExternalServiceException


class ConcreteService(BaseService[Dict[str, Any]]):
    """Concrete implementation of BaseService for testing."""

    def __init__(self):
        super().__init__("test_service")
        self.process_called = False

    def _process_request(self, *args, **kwargs) -> Dict[str, Any]:
        """Implementation of abstract method."""
        self.process_called = True
        return {"test_data": "success"}


class TestBaseServiceInitialization:
    """Test BaseService initialization and configuration."""

    def test_init_sets_service_name(self):
        """Test that service_name is set correctly during initialization."""
        service = ConcreteService()
        assert service.service_name == "test_service"

    def test_init_creates_logger(self):
        """Test that logger is created with correct namespace."""
        service = ConcreteService()
        assert service.logger is not None
        assert "test_service" in service.logger.name

    def test_init_loads_settings(self):
        """Test that settings are loaded during initialization."""
        service = ConcreteService()
        assert service.settings is not None

    def test_init_loads_educational_banner(self):
        """Test that educational banner is loaded during initialization."""
        service = ConcreteService()
        assert service.educational_banner is not None
        assert isinstance(service.educational_banner, str)


class TestCreateResponse:
    """Test standardized response creation."""

    def test_create_response_includes_required_fields(self):
        """Test that response includes all required standard fields."""
        service = ConcreteService()
        response = service._create_response(data={"key": "value"}, query="test query")

        assert "data" in response
        assert "query" in response
        assert "educational_banner" in response
        assert "service" in response
        assert "timestamp" in response

    def test_create_response_data_field(self):
        """Test that data field contains the provided data."""
        service = ConcreteService()
        test_data = {"result": "test", "count": 42}
        response = service._create_response(data=test_data, query="test")

        assert response["data"] == test_data

    def test_create_response_query_field(self):
        """Test that query field contains the original query."""
        service = ConcreteService()
        test_query = "diabetes treatment"
        response = service._create_response(data={}, query=test_query)

        assert response["query"] == test_query

    def test_create_response_service_field(self):
        """Test that service field identifies the service."""
        service = ConcreteService()
        response = service._create_response(data={}, query="test")

        assert response["service"] == "test_service"

    def test_create_response_timestamp_format(self):
        """Test that timestamp is in ISO 8601 format."""
        service = ConcreteService()
        response = service._create_response(data={}, query="test")

        # Should be parseable as ISO 8601
        timestamp = response["timestamp"]
        parsed = datetime.fromisoformat(timestamp)
        assert isinstance(parsed, datetime)

    def test_create_response_includes_kwargs(self):
        """Test that additional kwargs are included in response."""
        service = ConcreteService()
        response = service._create_response(
            data={}, query="test", source="pubmed", total_results=10
        )

        assert response["source"] == "pubmed"
        assert response["total_results"] == 10

    def test_create_response_educational_banner_present(self):
        """Test that educational banner is always included."""
        service = ConcreteService()
        response = service._create_response(data={}, query="test")

        assert len(response["educational_banner"]) > 0


class TestHandleExternalServiceError:
    """Test error handling with graceful degradation."""

    def test_error_handling_with_fallback_data(self):
        """Test that fallback data is returned when available."""
        service = ConcreteService()
        error = Exception("API timeout")
        fallback_data = {"cached": "data"}

        response = service._handle_external_service_error(error, fallback_data)

        assert response["data"] == fallback_data
        assert "service_status" in response
        assert response["service_status"]["fallback_used"] is True

    def test_error_handling_includes_degraded_status(self):
        """Test that degraded status is indicated in response."""
        service = ConcreteService()
        error = Exception("Connection failed")
        fallback_data = {"fallback": "value"}

        response = service._handle_external_service_error(error, fallback_data)

        assert response["service_status"]["status"] == "degraded"

    def test_error_handling_includes_error_message(self):
        """Test that error message is included in response."""
        service = ConcreteService()
        error_message = "Network error: timeout after 30s"
        error = Exception(error_message)
        fallback_data = {}

        response = service._handle_external_service_error(error, fallback_data)

        assert error_message in response["service_status"]["error"]

    def test_error_handling_includes_service_name(self):
        """Test that service name is included in degraded response."""
        service = ConcreteService()
        error = Exception("Error")
        fallback_data = {}

        response = service._handle_external_service_error(error, fallback_data)

        assert response["service_status"]["primary_service"] == "test_service"

    def test_error_handling_without_fallback_raises_exception(self):
        """Test that exception is raised when no fallback available."""
        service = ConcreteService()
        error = Exception("Complete failure")

        with pytest.raises(ExternalServiceException) as exc_info:
            service._handle_external_service_error(error, fallback_data=None)

        assert "test_service" in str(exc_info.value)
        assert "unavailable" in str(exc_info.value).lower()

    def test_error_handling_exception_contains_service_name(self):
        """Test that raised exception identifies the service."""
        service = ConcreteService()
        error = Exception("Fatal error")

        with pytest.raises(ExternalServiceException) as exc_info:
            service._handle_external_service_error(error)

        exception = exc_info.value
        assert "test_service" in exception.message
        assert exception.details["service"] == "test_service"

    def test_error_handling_logs_warning(self, caplog):
        """Test that errors are logged with warning level."""
        service = ConcreteService()
        error = Exception("Test error")
        fallback_data = {}

        with caplog.at_level("WARNING"):
            service._handle_external_service_error(error, fallback_data)

        assert "external service error" in caplog.text.lower()


class TestAbstractMethodEnforcement:
    """Test that abstract methods must be implemented."""

    def test_cannot_instantiate_base_service_directly(self):
        """Test that BaseService cannot be instantiated without implementation."""
        with pytest.raises(TypeError) as exc_info:
            # This should fail because _process_request is abstract
            BaseService("test")

        assert "abstract" in str(exc_info.value).lower()

    def test_process_request_is_abstract(self):
        """Test that _process_request must be implemented by subclasses."""

        # This class doesn't implement _process_request
        class IncompleteService(BaseService[Dict[str, Any]]):
            pass

        with pytest.raises(TypeError):
            IncompleteService("incomplete")

    def test_concrete_implementation_can_be_instantiated(self):
        """Test that concrete implementation with _process_request works."""
        service = ConcreteService()
        assert service is not None
        assert isinstance(service, BaseService)


class TestGenericTypeSupport:
    """Test generic type parameter support."""

    def test_service_with_dict_return_type(self):
        """Test service with Dict return type."""

        class DictService(BaseService[Dict[str, Any]]):
            def _process_request(self) -> Dict[str, Any]:
                return {"result": "dict"}

        service = DictService("dict_service")
        result = service._process_request()
        assert isinstance(result, dict)

    def test_service_with_list_return_type(self):
        """Test service with List return type."""
        from typing import List

        class ListService(BaseService[List[str]]):
            def _process_request(self) -> List[str]:
                return ["item1", "item2"]

        service = ListService("list_service")
        result = service._process_request()
        assert isinstance(result, list)


class TestServiceIntegration:
    """Integration tests for BaseService functionality."""

    def test_full_service_lifecycle(self):
        """Test complete service lifecycle from init to response."""
        service = ConcreteService()

        # Service initialized
        assert service.service_name == "test_service"

        # Process request
        result = service._process_request()
        assert service.process_called is True

        # Create response
        response = service._create_response(data=result, query="test query")
        assert response["data"] == result
        assert response["service"] == "test_service"

    def test_error_recovery_flow(self):
        """Test error recovery with fallback data flow."""
        service = ConcreteService()
        error = Exception("Simulated failure")
        fallback = {"cached": "response"}

        # Handle error with fallback
        response = service._handle_external_service_error(error, fallback)

        # Response should contain fallback data
        assert response["data"] == fallback
        assert response["service_status"]["status"] == "degraded"
        assert response["service_status"]["fallback_used"] is True

    def test_multiple_services_independent(self):
        """Test that multiple service instances are independent."""

        class ServiceA(BaseService[str]):
            def _process_request(self) -> str:
                return "A"

        class ServiceB(BaseService[str]):
            def _process_request(self) -> str:
                return "B"

        service_a = ServiceA("service_a")
        service_b = ServiceB("service_b")

        assert service_a.service_name == "service_a"
        assert service_b.service_name == "service_b"
        assert service_a._process_request() == "A"
        assert service_b._process_request() == "B"


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_create_response_with_empty_data(self):
        """Test creating response with empty data."""
        service = ConcreteService()
        response = service._create_response(data={}, query="")

        assert response["data"] == {}
        assert "timestamp" in response

    def test_create_response_with_none_query(self):
        """Test creating response with None as query."""
        service = ConcreteService()
        response = service._create_response(data={}, query=None)

        assert response["query"] is None

    def test_error_handling_with_empty_fallback(self):
        """Test error handling with empty but present fallback."""
        service = ConcreteService()
        error = Exception("Error")
        fallback_data = {}

        response = service._handle_external_service_error(error, fallback_data)

        # Empty dict is still valid fallback
        assert response["data"] == {}
        assert response["service_status"]["fallback_used"] is True

    def test_create_response_preserves_complex_data_types(self):
        """Test that complex data structures are preserved in response."""
        service = ConcreteService()
        complex_data = {
            "nested": {"deep": {"value": 123}},
            "list": [1, 2, 3],
            "mixed": [{"a": 1}, {"b": 2}],
        }

        response = service._create_response(data=complex_data, query="test")

        assert response["data"] == complex_data
        assert response["data"]["nested"]["deep"]["value"] == 123


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
