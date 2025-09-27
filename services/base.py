"""Base service interfaces for AI Nurse Florence.
Following OpenAI best practices and SOLID principles for extensibility.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class ClinicalResponse:
    """Standardized response format for all clinical services"""
    status: str
    data: Dict[str, Any]
    banner: str
    timestamp: str
    service: str
    confidence: Optional[float] = None
    sources: Optional[List[str]] = None
    warnings: Optional[List[str]] = None

class BaseClinicalService(ABC):
    """Abstract base class for all clinical services.
    
    Following OpenAI best practices for modular AI systems:
    - Clear interfaces
    - Dependency injection
    - Error handling
    - Logging
    - Extensibility
    """
    
    def __init__(self, service_name: str, config: Optional[Dict[str, Any]] = None):
        self.service_name = service_name
        self.config = config or {}
        self.banner = "🏥 Clinical reference tool - Always follow facility protocols and consult providers"
        
    @abstractmethod
    async def process(self, query: str, **kwargs) -> ClinicalResponse:
        """Process a clinical query and return standardized response"""
        pass
    
    def _create_response(self, 
                        status: str, 
                        data: Dict[str, Any], 
                        confidence: Optional[float] = None,
                        sources: Optional[List[str]] = None,
                        warnings: Optional[List[str]] = None) -> ClinicalResponse:
        """Create standardized clinical response"""
        return ClinicalResponse(
            status=status,
            data=data,
            banner=self.banner,
            timestamp=datetime.now().isoformat(),
            service=self.service_name,
            confidence=confidence,
            sources=sources,
            warnings=warnings
        )
    
    def _log_query(self, query: str, **kwargs):
        """Log query for monitoring and improvement"""
        logger.info(f"{self.service_name}: Processing query '{query}' with params {kwargs}")

class BaseAIService(BaseClinicalService):
    """Base class for AI-powered clinical services.
    
    Following OpenAI best practices:
    - Structured prompts
    - Response validation
    - Error handling
    - Token management
    """
    
    def __init__(self, service_name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(service_name, config)
        self.model = config.get('model', 'gpt-3.5-turbo') if config else 'gpt-3.5-turbo'
        self.max_tokens = config.get('max_tokens', 500) if config else 500
        
    def _build_system_prompt(self) -> str:
        """Build system prompt following OpenAI best practices"""
        return """You are AI Nurse Florence, a clinical assistant for healthcare professionals.

ROLE: Provide evidence-based clinical information and decision support
AUDIENCE: Nurses and healthcare professionals
CONSTRAINTS: 
- Educational purposes only
- Always recommend consulting providers for patient care
- Use evidence-based information
- Be concise and actionable

OUTPUT FORMAT: Structured JSON with clear clinical recommendations"""

    def _build_user_prompt(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Build user prompt with clinical context"""
        prompt = f"Clinical Query: {query}"
        if context:
            prompt += f"\n\nContext: {context}"
        return prompt
    
    async def _call_openai(self, messages: List[Dict[str, str]]) -> str:
        """Call OpenAI API with proper error handling"""
        # This would be implemented with actual OpenAI client
        # Following best practices for API calls
        try:
            # Placeholder for actual OpenAI integration
            logger.info(f"Would call OpenAI with model {self.model}")
            return '{"response": "AI-generated clinical insight"}'
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

class ServiceRegistry:
    """Registry for managing clinical services.
    
    Enables dynamic service discovery and dependency injection.
    """
    
    def __init__(self):
        self._services: Dict[str, BaseClinicalService] = {}
        self._service_metadata: Dict[str, Dict[str, Any]] = {}
    
    def register(self, 
                service: BaseClinicalService,
                tags: Optional[List[str]] = None,
                priority: int = 1) -> None:
        """Register a clinical service"""
        self._services[service.service_name] = service
        self._service_metadata[service.service_name] = {
            'tags': tags or [],
            'priority': priority,
            'class': service.__class__.__name__
        }
        logger.info(f"Registered service: {service.service_name}")
    
    def get_service(self, service_name: str) -> Optional[BaseClinicalService]:
        """Get service by name"""
        return self._services.get(service_name)
    
    def get_services_by_tag(self, tag: str) -> List[BaseClinicalService]:
        """Get all services with a specific tag"""
        services = []
        for name, metadata in self._service_metadata.items():
            if tag in metadata['tags']:
                services.append(self._services[name])
        return sorted(services, key=lambda s: self._service_metadata[s.service_name]['priority'], reverse=True)
    
    def list_services(self) -> Dict[str, Dict[str, Any]]:
        """List all registered services with metadata"""
        return {
            name: {
                'service': service,
                'metadata': self._service_metadata[name]
            }
            for name, service in self._services.items()
        }

# Global service registry
clinical_registry = ServiceRegistry()
