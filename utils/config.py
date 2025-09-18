# utils/config.py  (Pydantic v2)
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    # OpenAI Configuration
    OPENAI_API_KEY: str = Field(..., description="Server-side OpenAI API key")
    MODEL: str = Field(default="gpt-4o-mini")
    
    # NIH API Configuration
    NIH_API_BASE: str | None = Field(default=None)
    
    # API Authentication Configuration
    API_BEARER: str | None = Field(default=None, description="Optional Bearer token for legacy API authentication")
    
    # CORS Configuration 
    CORS_ORIGINS: str = Field(default="http://localhost:3000", description="CORS allowed origins (comma-separated)")
    
    # Service Configuration
    USE_LIVE: bool = Field(default=False, description="Whether to use live services or mocked data")
    
    # Rate Limiting Configuration
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, description="Rate limit requests per minute")
    
    # Redis Configuration
    REDIS_URL: str | None = Field(default=None, description="Redis connection URL for caching and Celery")
    
    # Database Configuration
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./ai_nurse_florence.db", description="Database connection URL")
    
    # JWT Configuration
    JWT_SECRET_KEY: str = Field(default="your-secret-key-change-in-production", description="JWT signing secret key")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="JWT token expiration time in minutes")
    
    # OAuth Configuration
    OAUTH_CLIENT_ID: str | None = Field(default=None, description="OAuth client ID for OpenAI integration")
    OAUTH_CLIENT_SECRET: str | None = Field(default=None, description="OAuth client secret for OpenAI integration")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Convert CORS_ORIGINS from string to list after initialization
        if isinstance(self.CORS_ORIGINS, str):
            self.CORS_ORIGINS = [origin.strip() for origin in self.CORS_ORIGINS.split(',')]

    # Pydantic v2 settings config
    model_config = SettingsConfigDict(
        env_prefix="",           # or e.g. "ANF_"
        env_file=".env",         # optional
        case_sensitive=False
    )

settings = Settings()