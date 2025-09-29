"""
Configuration Management - AI Nurse Florence
Following coding instructions centralized configuration with Pydantic Settings
"""

import os
from typing import List, Optional, Union

from pydantic import Field
from pydantic_settings import BaseSettings


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
    # Public Base URL for deployment and local testing. If not provided, constructed from HOST and PORT.
    APP_BASE_URL: Optional[str] = Field(
        default=None,
        description="Public base URL for the application (e.g., https://api.example.com). If not set, constructed from HOST and PORT.",
    )

    # CORS Configuration
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,https://localhost:3000",
        description="Comma-separated CORS origins",
    )

    # Authentication Configuration following Authentication & Authorization
    API_BEARER: str = Field(
        default="dev-bearer-token-change-me", description="API Bearer token"
    )

    # Database Configuration following Database Patterns
    DATABASE_URL: str = Field(
        default="sqlite:///./ai_nurse_florence.db",
        description="Database connection URL",
    )

    # External Services Configuration following External Service Integration
    USE_LIVE: bool = Field(default=False, description="Use live external APIs vs stubs")
    USE_LIVE_SERVICES: bool = Field(default=False, description="Alias for USE_LIVE")
    USE_MYDISEASE: bool = Field(
        default=True, description="Enable MyDisease.info service"
    )
    USE_MEDLINEPLUS: bool = Field(
        default=True, description="Enable MedlinePlus service"
    )
    USE_PUBMED: bool = Field(default=True, description="Enable PubMed service")

    # OpenAI Configuration following OpenAI Integration - loads from environment
    OPENAI_API_KEY: Optional[str] = Field(
        default=None, description="OpenAI API key from environment variable"
    )
    OPENAI_MODEL: str = Field(
        default="gpt-3.5-turbo", description="Default OpenAI model"
    )

    # Redis Configuration following Caching Strategy
    REDIS_URL: Optional[str] = Field(default=None, description="Redis connection URL")

    # Rate Limiting Configuration following Security & Middleware Stack
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting")
    RATE_LIMIT_REQUESTS: int = Field(
        default=60, description="Requests per minute limit"
    )
    RATE_LIMIT_PER_MINUTE: int = Field(
        default=60, description="Alias for rate limit requests"
    )

    # Feature Flags Configuration following Feature Flags pattern
    ENABLE_DEBUG_ROUTES: bool = Field(default=True, description="Enable debug routes")
    ENABLE_DOCS: bool = Field(default=True, description="Enable API documentation")
    ENABLE_METRICS: bool = Field(default=False, description="Enable Prometheus metrics")
    ENABLE_HEALTH_CHECKS: bool = Field(
        default=True, description="Enable health check endpoints"
    )
    ENABLE_CACHING: bool = Field(default=True, description="Enable caching")

    # Cache Configuration following Caching Strategy
    CACHE_TTL_SECONDS: int = Field(default=300, description="Cache TTL in seconds")

    # Monitoring Configuration
    GRAFANA_ADMIN_USER: str = Field(default="admin", description="Grafana admin user")
    GRAFANA_ADMIN_PASSWORD: str = Field(
        default="admin", description="Grafana admin password"
    )

    # Force HTTPS when constructing base URL if APP_BASE_URL is not set
    FORCE_HTTPS: bool = Field(
        default=False, description="Force https scheme when constructing base URL"
    )

    # Educational Banner following API Design Standards
    EDUCATIONAL_BANNER: str = Field(
        default="Draft for clinician review — not medical advice. No PHI stored.",
        description="Educational disclaimer banner",
    )

    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # Use a plain dict for model_config to match pydantic v2 / pydantic-settings expectations
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "allow",
    }

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

    def get_database_url(self) -> str:
        """Get database URL with environment variable override."""
        return os.getenv("DATABASE_URL", self.DATABASE_URL)

    @property
    def effective_use_live_services(self) -> bool:
        """Get effective USE_LIVE_SERVICES setting (USE_LIVE takes precedence)."""
        return self.USE_LIVE or self.USE_LIVE_SERVICES


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


def get_educational_banner() -> str:
    """Get educational banner following API Design Standards pattern."""
    settings = get_settings()
    return settings.EDUCATIONAL_BANNER


def get_openai_config() -> dict[str, Union[str, bool, None]]:
    """Get OpenAI configuration following OpenAI Integration pattern."""
    settings = get_settings()
    return {
        "api_key": settings.OPENAI_API_KEY,
        "model": settings.OPENAI_MODEL,
        "available": settings.has_openai(),
    }


def get_redis_config() -> dict[str, Union[str, bool, int, None]]:
    """Get Redis configuration following Caching Strategy pattern."""
    settings = get_settings()
    return {
        "url": settings.REDIS_URL,
        "available": settings.has_redis(),
        "ttl_seconds": settings.CACHE_TTL_SECONDS,
    }


def get_cache_config() -> dict[str, str | bool | int]:
    """Get cache configuration following Caching Strategy pattern."""
    settings = get_settings()
    return {
        "enabled": settings.ENABLE_CACHING,
        "redis_available": settings.has_redis(),
        "ttl_seconds": settings.CACHE_TTL_SECONDS,
        "fallback_to_memory": True,
    }


def get_base_url() -> str:
    """Return an effective base URL for the application.

    Priority: APP_BASE_URL env var if set; otherwise construct from HOST and PORT.
    """
    settings = get_settings()
    if settings.APP_BASE_URL and settings.APP_BASE_URL.strip():
        return settings.APP_BASE_URL
    # Default scheme decision controlled by settings.FORCE_HTTPS
    scheme = "https" if settings.FORCE_HTTPS else "http"
    host = settings.HOST or "127.0.0.1"
    port = settings.PORT
    return f"{scheme}://{host}:{port}"


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
    elif feature == "caching":
        return settings.ENABLE_CACHING
    elif feature == "docs":
        return settings.ENABLE_DOCS
    elif feature == "debug_routes":
        return settings.ENABLE_DEBUG_ROUTES
    else:
        return False


# Export commonly used items
__all__ = [
    "Settings",
    "get_settings",
    "get_educational_banner",
    "get_openai_config",
    "get_redis_config",
    "get_cache_config",
    "get_base_url",
    "is_feature_enabled",
]
