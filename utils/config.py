"""
Centralized application configuration using Pydantic Settings.
Updated to handle existing environment variables.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings with validation and type safety."""
    
    # pydantic v2: use plain dict for model_config
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",
    }
    
    # Core Application Settings
    API_BEARER: str = "default-api-key-change-in-production"
    CORS_ORIGINS_STR: str = Field(
        default="http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:8000",
        alias="CORS_ORIGINS"
    )
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False
    
    # Environment variables from your existing .env
    NODE_ENV: Optional[str] = None
    PYTHON_ENV: Optional[str] = None
    USE_MYDISEASE: bool = True
    USE_MEDLINEPLUS: bool = True
    USE_PUBMED: bool = True
    ENABLE_DEBUG_ROUTES: bool = True
    ENABLE_DOCS: bool = True
    RATE_LIMIT_ENABLED: bool = False
    CACHE_TTL_SECONDS: int = 300
    ENABLE_CACHING: bool = True
    GRAFANA_ADMIN_USER: str = "admin"
    GRAFANA_ADMIN_PASSWORD: str = "admin"
    ENABLE_METRICS: bool = False
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    
    # Service Configuration
    USE_LIVE: bool = False
    
    # Database Configuration
    DATABASE_URL: str = "sqlite+aiosqlite:///./ai_nurse_florence.db"
    
    # Cache Configuration (Redis)
    REDIS_URL: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    ENABLE_RATE_LIMITING: bool = True
    
    # Authentication & Security
    JWT_SECRET_KEY: str = "a_very_secret_key_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # OAuth2 Configuration
    OAUTH_CLIENT_ID: Optional[str] = None
    OAUTH_CLIENT_SECRET: Optional[str] = None
    OAUTH_REDIRECT_URI: str = "http://localhost:8000/auth/callback"
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        origins = [origin.strip() for origin in self.CORS_ORIGINS_STR.split(",")]
        return [origin for origin in origins if origin]

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

# Global settings instance
settings = get_settings()

"""
Test Framework Configuration - AI Nurse Florence
Comprehensive test suite for deployment readiness assessment
Following coding instructions for Configuration Management
"""
import pytest
from typing import List, Optional

# Test configuration following Configuration Management patterns
class TestFrameworkSettings:
    """Test framework configuration settings"""
    
    # Test Environment Configuration
    TEST_MODE = True
    MOCK_EXTERNAL_APIS = True
    SKIP_OPENAI_TESTS = False
    SKIP_REDIS_TESTS = False
    
    # Test Data Configuration
    TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
    TEST_REDIS_URL = "redis://localhost:6379/1"
    
    # Mock API Responses
    MOCK_MYDISEASE_RESPONSE = {
        "query": "diabetes",
        "hits": [{"_id": "D003920", "name": "Diabetes Mellitus"}]
    }
    
    MOCK_PUBMED_RESPONSE = {
        "esearchresult": {
            "count": "1000", 
            "idlist": ["12345", "67890"]
        }
    }
    
    MOCK_OPENAI_RESPONSE = {
        "choices": [{
            "message": {
                "content": "Mock AI response for testing"
            }
        }]
    }

# Test configuration fixtures following Testing Patterns
@pytest.fixture
def test_settings():
    """Test settings fixture"""
    return TestFrameworkSettings()

@pytest.fixture
def mock_config():
    """Mock configuration for testing"""
    return {
        "USE_LIVE": False,
        "OPENAI_API_KEY": "test-key",
        "DEBUG": True,
        "ENABLE_CACHING": False
    }

@pytest.fixture
def deployment_checklist():
    """Deployment readiness checklist"""
    return {
        "core_components": [
            "app.py exists and imports",
            "utils/config.py configuration complete", 
            "services layer functional",
            "routers layer functional"
        ],
        "external_integrations": [
            "OpenAI client configured",
            "MyDisease.info integration",
            "PubMed integration", 
            "ClinicalTrials.gov integration"
        ],
        "deployment_readiness": [
            "Environment variables configured",
            "Database configuration complete",
            "Caching layer functional",
            "Health checks operational"
        ]
    }

# Deployment Assessment Tests
class TestDeploymentReadiness:
    """Test suite for deployment readiness assessment"""
    
    def test_core_application_structure(self):
        """Test core application file structure"""
        # IMPLEMENTATION NEEDED
        # Test that all required files exist:
        # - app.py (main FastAPI application)
        # - utils/config.py (configuration management)
        # - services/ directory with medical services
        # - routers/ directory with API endpoints
        pass
    
    def test_configuration_completeness(self):
        """Test configuration management completeness"""
        # IMPLEMENTATION NEEDED
        # Test utils/config.py Settings class
        # Verify all required environment variables have defaults
        # Test configuration loading and validation
        pass
    
    def test_external_service_integrations(self):
        """Test external service integration readiness"""
        # IMPLEMENTATION NEEDED
        # Test OpenAI client configuration
        # Test medical API integrations (MyDisease, PubMed, etc.)
        # Test graceful degradation with Conditional Imports Pattern
        pass
    
    def test_database_configuration(self):
        """Test database configuration and connectivity"""
        # IMPLEMENTATION NEEDED  
        # Test database URL configuration
        # Test SQLAlchemy async session setup
        # Test Alembic migration configuration
        pass
    
    def test_caching_layer_readiness(self):
        """Test caching layer configuration"""
        # IMPLEMENTATION NEEDED
        # Test Redis configuration and fallback
        # Test cache decorators functionality
        # Test cache key generation
        pass
    
    def test_security_configuration(self):
        """Test security and authentication configuration"""
        # IMPLEMENTATION NEEDED
        # Test JWT configuration
        # Test API bearer token validation
        # Test CORS configuration
        # Test rate limiting setup
        pass
    
    def test_monitoring_and_health_checks(self):
        """Test monitoring and health check configuration"""
        # IMPLEMENTATION NEEDED
        # Test health check endpoints
        # Test metrics collection setup
        # Test logging configuration
        pass
    
    def test_wizard_implementations(self):
        """Test wizard pattern implementations"""
        # IMPLEMENTATION NEEDED
        # Test treatment plan wizard
        # Test SBAR wizard
        # Test patient education wizard
        pass

# Integration Tests for Deployment
class TestIntegrationReadiness:
    """Integration tests for deployment readiness"""
    
    @pytest.mark.asyncio
    async def test_full_application_startup(self):
        """Test complete application startup process"""
        # IMPLEMENTATION NEEDED
        # Test FastAPI app creation and configuration
        # Test router loading with Conditional Imports Pattern
        # Test middleware stack initialization
        pass
    
    @pytest.mark.asyncio
    async def test_medical_service_pipeline(self):
        """Test complete medical information pipeline"""
        # IMPLEMENTATION NEEDED
        # Test disease lookup -> AI enhancement -> response formatting
        # Test PubMed search -> content summarization -> response
        # Test clinical trials search -> result formatting
        pass
    
    @pytest.mark.asyncio  
    async def test_wizard_workflow_complete(self):
        """Test complete wizard workflow"""
        # IMPLEMENTATION NEEDED
        # Test treatment plan wizard from start to completion
        # Test session management and state persistence
        # Test final document generation
        pass

# Deployment Environment Tests
class TestEnvironmentConfiguration:
    """Test environment-specific configuration"""
    
    def test_development_environment(self):
        """Test development environment configuration"""
        # IMPLEMENTATION NEEDED
        # Test local development settings
        # Test debug mode configuration
        # Test local database setup
        pass
    
    def test_production_environment(self):
        """Test production environment readiness"""
        # IMPLEMENTATION NEEDED  
        # Test production settings validation
        # Test security configuration
        # Test external service credentials
        pass
    
    def test_railway_deployment_config(self):
        """Test Railway.com deployment configuration"""
        # IMPLEMENTATION NEEDED
        # Test Railway environment variables
        # Test Railway database configuration
        # Test Railway Redis configuration
        pass

# Performance and Load Tests
class TestPerformanceReadiness:
    """Test performance characteristics for deployment"""
    
    def test_api_response_times(self):
        """Test API response time benchmarks"""
        # IMPLEMENTATION NEEDED
        # Test medical API response times under load
        # Test caching effectiveness
        # Test concurrent request handling
        pass
    
    def test_database_performance(self):
        """Test database performance characteristics"""
        # IMPLEMENTATION NEEDED
        # Test query performance
        # Test connection pooling
        # Test migration performance
        pass
    
    def test_memory_usage(self):
        """Test memory usage patterns"""
        # IMPLEMENTATION NEEDED
        # Test memory usage under normal load
        # Test memory leak detection
        # Test cache memory management
        pass

# Export test configuration
__all__ = [
    "TestFrameworkSettings",
    "TestDeploymentReadiness", 
    "TestIntegrationReadiness",
    "TestEnvironmentConfiguration",
    "TestPerformanceReadiness"
]
