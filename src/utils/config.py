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
    
    # Server Configuration
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    
    # CORS Configuration - Fixed attribute name
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,https://localhost:3000",
        description="Comma-separated CORS origins"
    )
    
    # Database Configuration following Database Patterns
    DATABASE_URL: str = Field(
        default="sqlite:///./ai_nurse_florence.db",
        description="Database connection URL"
    )
    
    # External Services Configuration following External Service Integration
    USE_LIVE_SERVICES: bool = Field(default=False, description="Use live external APIs vs stubs")
    
    # OpenAI Configuration following OpenAI Integration
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API key")
    OPENAI_MODEL: str = Field(default="gpt-3.5-turbo", description="Default OpenAI model")
    
    # Redis Configuration following Caching Strategy
    REDIS_URL: Optional[str] = Field(default=None, description="Redis connection URL")
    
    # Rate Limiting Configuration following Security & Middleware Stack
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting")
    RATE_LIMIT_REQUESTS: int = Field(default=60, description="Requests per minute limit")
    
    # Educational Banner following API Design Standards
    EDUCATIONAL_BANNER: str = Field(
        default="Draft for clinician review — not medical advice. No PHI stored.",
        description="Educational disclaimer banner"
    )
    
    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # Feature Flags following Configuration Management
    ENABLE_METRICS: bool = Field(default=False, description="Enable Prometheus metrics")
    ENABLE_HEALTH_CHECKS: bool = Field(default=True, description="Enable health check endpoints")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        """
        Parse CORS origins into list format.
        Maintains backward compatibility with ALLOWED_ORIGINS attribute.
        """
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    def has_openai(self) -> bool:
        """Check if OpenAI API key is configured following OpenAI Integration."""
        return self.OPENAI_API_KEY is not None and self.OPENAI_API_KEY.strip() != ""
    
    def has_redis(self) -> bool:
        """Check if Redis is configured following Caching Strategy."""
        return self.REDIS_URL is not None and self.REDIS_URL.strip() != ""
    
    def get_database_url(self) -> str:
        """Get database URL with environment variable override."""
        return os.getenv("DATABASE_URL", self.DATABASE_URL)

# Global settings instance following Configuration Management pattern
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """
    Get settings instance with caching.
    Following Conditional Imports Pattern for graceful configuration loading.
    """
    global _settings
    if _settings is None:
        try:
            _settings = Settings()
        except Exception as e:
            print(f"Configuration error: {e}")
            # Fallback to default settings
            _settings = Settings()
    return _settings

def is_feature_enabled(feature: str) -> bool:
    """
    Check if feature is enabled following feature flag pattern.
    
    Args:
        feature: Feature name (openai, redis, metrics, etc.)
    
    Returns:
        bool: True if feature is enabled and available
    """
    settings = get_settings()
    
    if feature == "openai":
        return settings.has_openai()
    elif feature == "redis":
        return settings.has_redis()
    elif feature == "metrics":
        return settings.ENABLE_METRICS
    elif feature == "rate_limiting":
        return settings.RATE_LIMIT_ENABLED
    elif feature == "health_checks":
        return settings.ENABLE_HEALTH_CHECKS
    else:
        return False

# Export commonly used items
__all__ = [
    "Settings",
    "get_settings", 
    "is_feature_enabled"
]
