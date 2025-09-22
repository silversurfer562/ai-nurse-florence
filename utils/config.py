"""
Centralized application configuration using Pydantic Settings.
Updated to handle existing environment variables.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List, Optional
from functools import lru_cache
import os

class Settings(BaseSettings):
    """Application settings with validation and type safety."""
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # FIXED: Ignore extra fields from .env
    )
    
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
