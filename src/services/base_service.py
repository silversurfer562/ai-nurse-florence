"""
Base Service - AI Nurse Florence

This module provides the foundational abstract base class for all service layer
components in AI Nurse Florence. It enforces consistent architecture patterns,
error handling, response formatting, and logging across all medical data services.

Key Features:
    - Abstract base class for service layer architecture
    - Standardized response formatting with educational banners
    - Consistent error handling with fallback support
    - Automatic logging configuration per service
    - Generic type support for type-safe subclassing

Architecture Patterns:
    - Service Layer Architecture: Business logic separated from routing
    - Template Method Pattern: _process_request() must be implemented by subclasses
    - Dependency Injection: Settings and config injected at initialization
    - Error Handling Strategy: Graceful degradation with fallbacks
    - Generic Programming: Type-safe with TypeVar[T]

Design Principles:
    - DRY: Common response/error handling in one place
    - Open/Closed: Open for extension (subclass), closed for modification
    - Single Responsibility: Each service handles one medical data domain
    - Liskov Substitution: All services interchangeable via base interface

Subclass Requirements:
    Must implement:
        _process_request(*args, **kwargs) -> T
            - Core business logic for the service
            - Returns service-specific data type T

    May override:
        _create_response(data, query, **kwargs) -> Dict
        _handle_external_service_error(error, fallback_data) -> Dict

Services Inheriting from BaseService:
    - DiseaseService: Multi-source disease information lookup
    - (Other services currently don't inherit but should in refactoring)

Examples:
    >>> # Creating a new service
    >>> class WeatherService(BaseService[Dict[str, Any]]):
    ...     def __init__(self):
    ...         super().__init__("weather")
    ...
    ...     async def _process_request(self, location: str) -> Dict[str, Any]:
    ...         # Fetch weather data
    ...         data = await fetch_weather(location)
    ...         return self._create_response(data, location)

    >>> # Using the service
    >>> service = WeatherService()
    >>> result = await service._process_request("New York")
    >>> print(result["educational_banner"])
    Educational use only - not medical advice

Self-Improvement Checklist:
    [ ] Refactor all services to inherit from BaseService
    [ ] Add unit tests for BaseService methods
    [ ] Add async version: AsyncBaseService
    [ ] Add retry logic support in base class
    [ ] Add circuit breaker pattern support
    [ ] Add telemetry/metrics collection hooks
    [ ] Add request/response validation with Pydantic
    [ ] Add caching decorator support in base class
    [ ] Document migration guide for existing services
    [ ] Add rate limiting support in base class

Version: 2.4.2
Last Updated: 2025-10-04
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Generic, TypeVar

from ..utils.config import get_educational_banner, get_settings
from ..utils.exceptions import ExternalServiceException

T = TypeVar("T")


class BaseService(ABC, Generic[T]):
    """
    Abstract base class for all medical data services in AI Nurse Florence.

    This class provides the foundation for service layer architecture, enforcing
    consistent patterns for error handling, response formatting, logging, and
    configuration management across all medical data services.

    Type Parameters:
        T: The return type for _process_request() method
           Examples: Dict[str, Any], List[str], CustomDataClass

    Attributes:
        service_name (str): Unique identifier for this service (e.g., "disease", "drug")
        logger (logging.Logger): Configured logger instance for this service
        settings: Application configuration from get_settings()
        educational_banner (str): Standard educational disclaimer text

    Abstract Methods:
        _process_request(*args, **kwargs) -> T
            Must be implemented by subclasses to define service-specific logic

    Concrete Methods:
        _create_response(data, query, **kwargs) -> Dict[str, Any]
            Creates standardized response with educational banner
        _handle_external_service_error(error, fallback_data) -> Dict[str, Any]
            Handles external API failures with optional fallback data

    Examples:
        >>> class MyMedicalService(BaseService[Dict[str, Any]]):
        ...     def __init__(self):
        ...         super().__init__("myservice")
        ...
        ...     async def _process_request(self, query: str) -> Dict[str, Any]:
        ...         data = await self._fetch_data(query)
        ...         return self._create_response(data, query)

    Notes:
        - All subclasses must call super().__init__(service_name) in __init__
        - Logger is automatically configured with service-specific namespace
        - Educational banner automatically included in all responses
    """

    def __init__(self, service_name: str) -> None:
        """
        Initialize base service with configuration and logging.

        Args:
            service_name (str): Unique service identifier for logging and tracking
                Examples: "disease", "drug", "clinical_trials"

        Side Effects:
            - Creates logger instance with namespace "ai_nurse_florence.services.{service_name}"
            - Loads application settings from get_settings()
            - Loads educational banner from get_educational_banner()

        Examples:
            >>> # In subclass __init__
            >>> super().__init__("my_service")
            >>> self.logger.info("Service initialized")
        """
        self.service_name = service_name
        self.logger = logging.getLogger(f"ai_nurse_florence.services.{service_name}")
        self.settings = get_settings()
        self.educational_banner = get_educational_banner()

    @abstractmethod
    def _process_request(self, *args, **kwargs) -> T:
        """
        Process the actual service request - MUST be implemented by subclasses.

        This is the core business logic method that each service must implement.
        It should handle the specific data fetching, processing, and return logic
        for that service's domain.

        Args:
            *args: Variable positional arguments (service-specific)
            **kwargs: Variable keyword arguments (service-specific)

        Returns:
            T: Service-specific return type (defined by Generic[T])

        Raises:
            Service-specific exceptions (typically ExternalServiceException)

        Implementation Guidelines:
            - Fetch data from external APIs or databases
            - Transform data into service-specific format
            - Use self._create_response() for standardized output
            - Use self._handle_external_service_error() for error handling
            - Log important operations using self.logger

        Examples:
            >>> # In DiseaseService
            >>> async def _process_request(self, query: str, **kwargs) -> Dict[str, Any]:
            ...     return await self.lookup_disease(query, **kwargs)

            >>> # In DrugService
            >>> async def _process_request(self, drug_name: str) -> Dict[str, Any]:
            ...     data = await self._fetch_drug_data(drug_name)
            ...     return self._create_response(data, drug_name)
        """
        pass

    def _create_response(self, data: Any, query: str, **kwargs) -> Dict[str, Any]:
        """
        Create standardized service response with educational banner and metadata.

        This method provides consistent response formatting across all services,
        including educational disclaimers, service identification, and timestamps.

        Args:
            data (Any): The actual response data (service-specific format)
            query (str): The original user query that triggered this request
            **kwargs: Additional metadata to include in response
                Examples: source="FDA", needs_clarification=True

        Returns:
            Dict[str, Any]: Standardized response with structure:
                {
                    "data": Any,  # Service-specific payload
                    "query": str,  # Original query
                    "educational_banner": str,  # Compliance disclaimer
                    "service": str,  # Service name
                    "timestamp": str,  # ISO 8601 timestamp
                    **kwargs  # Any additional metadata
                }

        Examples:
            >>> # Simple response
            >>> response = self._create_response(
            ...     data={"name": "Diabetes Mellitus", "symptoms": [...]},
            ...     query="diabetes"
            ... )
            >>> print(response.keys())
            dict_keys(['data', 'query', 'educational_banner', 'service', 'timestamp'])

            >>> # Response with metadata
            >>> response = self._create_response(
            ...     data=trial_results,
            ...     query="cancer trials",
            ...     source="ClinicalTrials.gov",
            ...     total_results=42
            ... )

        Notes:
            - Timestamp is in ISO 8601 format for easy parsing
            - Educational banner is always included for compliance
            - Service name helps with debugging and monitoring
        """
        return {
            "data": data,
            "query": query,
            "educational_banner": self.educational_banner,
            "service": self.service_name,
            "timestamp": datetime.now().isoformat(),
            **kwargs,
        }

    def _handle_external_service_error(
        self, error: Exception, fallback_data: Any = None
    ) -> Dict[str, Any]:
        """
        Handle external service errors with graceful degradation and fallback support.

        This method provides consistent error handling across all services, logging
        errors and either returning fallback data (if available) or raising an
        exception (if no fallback available).

        Args:
            error (Exception): The exception that occurred during external service call
                Examples: HTTPError, TimeoutError, ConnectionError
            fallback_data (Any, optional): Alternative data to return if primary fails.
                Could be cached data, stub data, or None. Defaults to None.

        Returns:
            Dict[str, Any]: Response with fallback data and degraded status metadata:
                {
                    "data": Any,  # The fallback data
                    "educational_banner": str,
                    "service_status": {
                        "primary_service": str,  # Service name
                        "status": "degraded",  # Service health status
                        "fallback_used": True,
                        "error": str  # Error message
                    }
                }

        Raises:
            ExternalServiceException: If no fallback_data available
                Contains error message and service name for client handling

        Examples:
            >>> # With fallback data (cached)
            >>> try:
            ...     data = await fetch_from_api(query)
            ... except Exception as e:
            ...     cached = get_from_cache(query)
            ...     return self._handle_external_service_error(e, cached)
            >>> # Returns degraded response with cached data

            >>> # Without fallback (raises)
            >>> try:
            ...     data = await fetch_from_api(query)
            ... except Exception as e:
            ...     return self._handle_external_service_error(e)
            >>> # Raises ExternalServiceException

        Notes:
            - Always logs warning before returning/raising
            - Graceful degradation: Returns partial data when possible
            - Fail-fast: Raises exception when no recovery possible
            - Clients can detect degraded mode via service_status field
        """
        self.logger.warning(f"{self.service_name} external service error: {error}")

        if fallback_data is not None:
            return {
                "data": fallback_data,
                "educational_banner": self.educational_banner,
                "service_status": {
                    "primary_service": self.service_name,
                    "status": "degraded",
                    "fallback_used": True,
                    "error": str(error),
                },
            }

        raise ExternalServiceException(
            service_name=self.service_name,
            message="temporarily unavailable",
            original_error=error,
        )
