"""
Base service class following Service Layer Architecture
From copilot-instructions.md patterns
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TypeVar, Generic
from datetime import datetime

from ..utils.config import get_settings, get_educational_banner
from ..utils.exceptions import ServiceException, ExternalServiceException
from ..utils.redis_cache import cached

T = TypeVar('T')

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
    def _process_request(self, *args, **kwargs) -> T:
        """
        Process the actual service request - to be implemented by subclasses
        Following Service Layer Architecture pattern
        """
        pass
    
    def _create_response(self, data: Any, query: str, **kwargs) -> Dict[str, Any]:
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
            **kwargs
        }
    
    def _handle_external_service_error(self, error: Exception, fallback_data: Any = None) -> Dict[str, Any]:
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
                    "error": str(error)
                }
            }
        
        raise ExternalServiceException(
            f"{self.service_name} temporarily unavailable",
            self.service_name,
            fallback_available=False
        )