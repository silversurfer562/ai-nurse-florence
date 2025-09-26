"""
Configuration management using Pydantic Settings v2
Following AI Nurse Florence Conditional Imports Pattern for graceful degradation
"""

import os
import logging
from typing import Optional, List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

# Educational banner following AI Nurse Florence pattern
EDU_BANNER = "Draft for clinician review — not medical advice. No PHI stored."

class Settings(BaseSettings):
    """Application settings with environment variable loading and graceful fallbacks."""
    
    # App Configuration
    APP_NAME: str = Field(default="AI Nurse Florence", description="Application name")
    APP_VERSION: str = Field(default="2.1.0", description="Application version")
    DEBUG: bool = Field(default=False, description="Debug mode")
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")
    
    # Educational Content - Following healthcare AI requirements
    EDUCATIONAL_BANNER: str = Field(default=EDU_BANNER, description="Educational disclaimer banner")
    
    # Server Configuration  
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    
    # Database Configuration - Following Database Patterns
    DATABASE_URL: str = Field(default="sqlite:///./ai_nurse_florence.db", description="Database URL")
    DATABASE_ECHO: bool = Field(default=False, description="Log SQL queries")
    
    # Redis Configuration (Optional - Conditional Imports Pattern)
    REDIS_URL: Optional[str] = Field(default=None, description="Redis URL for caching")
    REDIS_TTL_DEFAULT: int = Field(default=3600, description="Default Redis TTL in seconds")
    
    # OpenAI Configuration - Following OpenAI Integration patterns
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API key")
    OPENAI_MODEL: str = Field(default="gpt-3.5-turbo", description="Default OpenAI model")
    OPENAI_MAX_TOKENS: int = Field(default=2000, description="OpenAI max tokens")
    OPENAI_TEMPERATURE: float = Field(default=0.1, description="OpenAI temperature for clinical consistency")
    
    # External Services (AI Nurse Florence pattern)
    USE_LIVE_SERVICES: bool = Field(default=False, description="Use live external services")
    
    # CORS Configuration - Following Security & Middleware Stack
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,https://localhost:3000", 
        description="CORS allowed origins (comma-separated string)"
    )
    
    # Rate Limiting - Following Security patterns
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting")
    RATE_LIMIT_REQUESTS: int = Field(default=60, description="Requests per minute")
    
    # Monitoring & Observability
    METRICS_ENABLED: bool = Field(default=False, description="Enable Prometheus metrics")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # Security Configuration
    SECRET_KEY: str = Field(default="dev-secret-change-in-production", description="Secret key for JWT")
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins - graceful fallback following AI Nurse Florence patterns."""
        try:
            if isinstance(v, str):
                return v  # Keep as string, parse later
            elif isinstance(v, list):
                return ','.join(v)  # Convert list to string
            else:
                return "http://localhost:3000"  # Safe fallback
        except Exception:
            # Graceful degradation - AI Nurse Florence pattern
            return "http://localhost:3000"
    
    @field_validator('ENVIRONMENT')
    @classmethod
    def validate_environment(cls, v):
        """Validate environment value."""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            return "development"  # Safe default
        return v
    
    def get_cors_origins_list(self) -> List[str]:
        """Get CORS origins as list - following AI Nurse Florence utility pattern."""
        try:
            if isinstance(self.CORS_ORIGINS, str):
                return [origin.strip() for origin in self.CORS_ORIGINS.split(',') if origin.strip()]
            return ["http://localhost:3000"]  # Safe fallback
        except Exception:
            return ["http://localhost:3000"]
    
    def has_openai(self) -> bool:
        """Check if OpenAI is available - Conditional Imports Pattern."""
        try:
            return self.OPENAI_API_KEY is not None and len(self.OPENAI_API_KEY.strip()) > 0
        except Exception:
            return False
    
    def has_redis(self) -> bool:
        """Check if Redis is available - Conditional Imports Pattern."""
        try:
            return self.REDIS_URL is not None and len(self.REDIS_URL.strip()) > 0
        except Exception:
            return False
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT == "production"
    
    @property
    def database_url_async(self) -> str:
        """Get async database URL for SQLAlchemy."""
        if self.DATABASE_URL.startswith("sqlite"):
            return self.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")
        elif self.DATABASE_URL.startswith("postgresql://"):
            return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
        return self.DATABASE_URL
    
    model_config = {
        'env_file': '.env',
        'env_file_encoding': 'utf-8',
        'extra': 'ignore',  # Ignore unknown environment variables
        'validate_default': True
    }

# Global settings instance - AI Nurse Florence singleton pattern
_settings = None

def get_settings() -> Settings:
    """
    Get application settings singleton with graceful error handling.
    Following AI Nurse Florence Conditional Imports Pattern.
    """
    global _settings
    if _settings is None:
        try:
            _settings = Settings()
        except Exception as e:
            # Graceful degradation - log warning and use defaults
            logging.warning(f"Config loading failed ({e}), using safe defaults")
            try:
                # Try loading without .env file
                _settings = Settings(_env_file=None)
            except Exception:
                # Last resort - create minimal settings
                _settings = Settings.model_construct()
    return _settings

# Feature flag helpers following AI Nurse Florence patterns
def is_feature_enabled(feature_name: str) -> bool:
    """
    Check if a feature is enabled - following Conditional Imports Pattern.
    Used for graceful degradation when optional services unavailable.
    """
    settings = get_settings()
    
    feature_map = {
        'openai': settings.has_openai(),
        'redis': settings.has_redis(),
        'live_services': settings.USE_LIVE_SERVICES,
        'rate_limiting': settings.RATE_LIMIT_ENABLED,
        'metrics': settings.METRICS_ENABLED
    }
    
    return feature_map.get(feature_name.lower(), False)

def get_cors_origins() -> List[str]:
    """Get CORS origins list with fallback - Service Layer Architecture pattern."""
    try:
        return get_settings().get_cors_origins_list()
    except Exception:
        return ["http://localhost:3000"]  # Safe fallback

def get_educational_banner() -> str:
    """Get educational disclaimer banner for medical content."""
    try:
        return get_settings().EDUCATIONAL_BANNER
    except Exception:
        return EDU_BANNER  # Safe fallback

def get_app_info() -> dict:
    """Get application information following Router Organization pattern."""
    try:
        settings = get_settings()
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "features": {
                "openai": settings.has_openai(),
                "redis": settings.has_redis(),
                "live_services": settings.USE_LIVE_SERVICES,
                "rate_limiting": settings.RATE_LIMIT_ENABLED,
                "metrics": settings.METRICS_ENABLED
            }
        }
    except Exception:
        # Graceful fallback
        return {
            "name": "AI Nurse Florence",
            "version": "2.1.0",
            "environment": "development",
            "features": {"error": "config_unavailable"}
        }

# Database configuration helpers
def get_database_config() -> dict:
    """Get database configuration for SQLAlchemy - Following Database Patterns."""
    try:
        settings = get_settings()
        return {
            "url": settings.database_url_async,
            "echo": settings.DATABASE_ECHO,
            "pool_pre_ping": True,
            "pool_recycle": 3600 if settings.is_production else -1,
        }
    except Exception:
        return {
            "url": "sqlite+aiosqlite:///./ai_nurse_florence.db",
            "echo": False,
            "pool_pre_ping": True
        }

# Cache configuration helpers
def get_redis_config() -> Optional[dict]:
    """Get Redis configuration if available - Following Caching Strategy."""
    try:
        settings = get_settings()
        if not settings.has_redis():
            return None
        
        return {
            "url": settings.REDIS_URL,
            "default_ttl": settings.REDIS_TTL_DEFAULT,
            "decode_responses": True,
        }
    except Exception:
        return None

# OpenAI configuration helpers
def get_openai_config() -> Optional[dict]:
    """Get OpenAI configuration if available - Following OpenAI Integration."""
    try:
        settings = get_settings()
        if not settings.has_openai():
            return None
        
        return {
            "api_key": settings.OPENAI_API_KEY,
            "model": settings.OPENAI_MODEL,
            "max_tokens": settings.OPENAI_MAX_TOKENS,
            "temperature": settings.OPENAI_TEMPERATURE,
        }
    except Exception:
        return None

# Export commonly used functions following API Design Standards
__all__ = [
    "Settings",
    "get_settings",
    "is_feature_enabled",
    "get_cors_origins",
    "get_educational_banner",
    "get_app_info",
    "get_database_config",
    "get_redis_config", 
    "get_openai_config",
    "EDU_BANNER"
]
