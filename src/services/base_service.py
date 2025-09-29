"""
Base service class following Service Layer Architecture
From copilot-instructions.md patterns
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, TypeVar, Generic, Tuple
from datetime import datetime

from ..utils.config import get_settings, get_educational_banner
from ..utils.exceptions import ExternalServiceException

T = TypeVar("T")


class BaseService(ABC, Generic[T]):
    """
    Base service class implementing Service Layer Architecture patterns
    Following copilot-instructions.md Service Layer Architecture
    """

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = logging.getLogger(f"ai_nurse_florence.services.{service_name}")
        self.settings = get_settings()
        self.educational_banner = get_educational_banner()

    @abstractmethod
    async def _process_request(self, *args: Any, **kwargs: Any) -> T:
        """
        Process the actual service request - to be implemented by subclasses
        Async-first signature so subclasses may implement async IO-heavy logic.
        """
        raise NotImplementedError()

    def _create_response(self, data: Any, query: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Create standardized service response with educational banner
        Following API Design Standards from copilot-instructions.md
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
        Handle external service errors with fallback following Conditional Imports Pattern
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

        # Raise a standardized ExternalServiceException with the original error
        # signature: ExternalServiceException(service_name: str, message: str, original_error: Optional[Exception] = None)
        raise ExternalServiceException(self.service_name, str(error), error)
