"""
Configuration Management - AI Nurse Florence
Following coding instructions centralized configuration with Pydantic Settings
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """
    Centralized configuration following coding instructions.
    Environment-based with sensible defaults and feature flags.
    """
    
    # App Configuration
    APP_NAME: str = Field(default="AI Nurse Florence", description="Application name")
    APP_VERSION: str = Field(default="2.1.0", description="Application version")
    DEBUG: bool = Field(default=False, description="Debug mode")
    
    # Environment Configuration
    NODE_ENV: str = Field(default="development", description="Node environment")
    PYTHON_ENV: str = Field(default="development", description="Python environment")
    
    # Server Configuration
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    
    # CORS Configuration - Fixed attribute name
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,https://localhost:3000",
        description="Comma-separated CORS origins"
    )
    
    # Authentication Configuration following Authentication & Authorization
    API_BEARER: str = Field(
        default="dev-bearer-token-change-me",
        description="API Bearer token"
    )
    
    # Database Configuration following Database Patterns
    DATABASE_URL: str = Field(
        default="sqlite:///./ai_nurse_florence.db",
        description="Database connection URL"
    )
    
    # External Services Configuration following External Service Integration
    USE_LIVE: bool = Field(default=False, description="Use live external APIs vs stubs")
    USE_LIVE_SERVICES: bool = Field(default=False, description="Alias for USE_LIVE")
    USE_MYDISEASE: bool = Field(default=True, description="Enable MyDisease.info service")
    USE_MEDLINEPLUS: bool = Field(default=True, description="Enable MedlinePlus service")
    USE_PUBMED: bool = Field(default=True, description="Enable PubMed service")
    
    # OpenAI Configuration following OpenAI Integration
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API key")
    OPENAI_MODEL: str = Field(default="gpt-3.5-turbo", description="Default OpenAI model")
    
    # Redis Configuration following Caching Strategy
    REDIS_URL: Optional[str] = Field(default=None, description="Redis connection URL")
    
    # Rate Limiting Configuration following Security & Middleware Stack
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting")
    RATE_LIMIT_REQUESTS: int = Field(default=60, description="Requests per minute limit")
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, description="Alias for rate limit requests")
    
    # Feature Flags Configuration following Feature Flags pattern
    ENABLE_DEBUG_ROUTES: bool = Field(default=True, description="Enable debug routes")
    ENABLE_DOCS: bool = Field(default=True, description="Enable API documentation")
    ENABLE_METRICS: bool = Field(default=False, description="Enable Prometheus metrics")
    ENABLE_HEALTH_CHECKS: bool = Field(default=True, description="Enable health check endpoints")
    ENABLE_CACHING: bool = Field(default=True, description="Enable caching")
    
    # Cache Configuration following Caching Strategy
    CACHE_TTL_SECONDS: int = Field(default=300, description="Cache TTL in seconds")
    
    # Monitoring Configuration
    GRAFANA_ADMIN_USER: str = Field(default="admin", description="Grafana admin user")
    GRAFANA_ADMIN_PASSWORD: str = Field(default="admin", description="Grafana admin password")
    
    # Educational Banner following API Design Standards
    EDUCATIONAL_BANNER: str = Field(
        default="Draft for clinician review — not medical advice. No PHI stored.",
        description="Educational disclaimer banner"
    )
    
    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        # Allow extra fields to prevent validation errors
        extra = "allow"
    
    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        """Parse CORS origins into list format."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    def has_openai(self) -> bool:
        """Check if OpenAI API key is configured following OpenAI Integration."""
        return self.OPENAI_API_KEY is not None and self.OPENAI_API_KEY.strip() != ""
    
    def has_redis(self) -> bool:
        """Check if Redis is configured following Caching Strategy."""
        return self.REDIS_URL is not None and self.REDIS_URL.strip() != ""

def get_redis_config() -> dict:
    """Get Redis configuration following Caching Strategy pattern."""
    settings = get_settings()
    return {
        "url": settings.REDIS_URL,
        "available": settings.has_redis(),
        "ttl_seconds": settings.CACHE_TTL_SECONDS
    }

def get_cache_config() -> dict:
    """Get cache configuration following Caching Strategy pattern."""
    settings = get_settings()
    return {
        "enabled": settings.ENABLE_CACHING,
        "redis_available": settings.has_redis(),
        "ttl_seconds": settings.CACHE_TTL_SECONDS,
        "fallback_to_memory": True
    }

# Global settings instance following Configuration Management pattern
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get settings instance with caching."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

__all__ = [
    "Settings",
    "get_settings", 
    "get_redis_config",
    "get_cache_config"
]
