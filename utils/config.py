"""
Centralized application configuration using Pydantic.

This module defines a `Settings` class that loads configuration from environment
variables and a `.env` file, providing a single, type-safe source of truth for
all application settings.
"""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
from functools import lru_cache

class Settings(BaseSettings):
    """
    Application settings, loaded from environment variables.
    
    Pydantic's BaseSettings automatically reads from the environment.
    The model_config tells it to also load from a .env file.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extra fields to prevent validation errors during development
    )
    
    # Core App Settings
    API_BEARER: str
    CORS_ORIGINS_STR: str = Field("", alias="CORS_ORIGINS")
    LOG_LEVEL: str = "INFO"
    
    # OpenAI Settings
    OPENAI_API_KEY: Optional[str] = None
    
    # Service Settings
    USE_LIVE: bool = False
    
    # Infrastructure Settings
    REDIS_URL: Optional[str] = None
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db" # Default to SQLite for simple local dev
    
    # Feature Settings
    RATE_LIMIT_PER_MINUTE: int = 60

    # --- OAuth2 Settings for GPT Store ---
    # These will be provided by the GPT editor's authentication section
    OAUTH_CLIENT_ID: Optional[str] = None
    OAUTH_CLIENT_SECRET: Optional[str] = None
    # This is a secret key for signing our own JWTs (JSON Web Tokens)
    # In production, this should be a long, random string.
    JWT_SECRET_KEY: str = "a_very_secret_key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 1 week

    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Parses the comma-separated string of origins into a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS_STR.split(",") if origin.strip()]

@lru_cache()
def get_settings() -> Settings:
    """
    Returns a cached instance of the Settings object.
    
    Using lru_cache ensures the .env file and environment are read only once.
    """
    return Settings()

# Create a single instance to be used throughout the application
settings = get_settings()