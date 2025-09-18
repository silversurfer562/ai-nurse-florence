# utils/config.py  (Pydantic v2)
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    # OpenAI Configuration
    OPENAI_API_KEY: str | None = Field(default=None, description="Server-side OpenAI API key")
    NIH_API_BASE: str | None = Field(default=None, description="NIH API base URL")
    MODEL: str = Field(default="gpt-4o-mini", description="Default OpenAI model to use")
    
    # Database Configuration
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./ai_nurse_florence.db",
        description="Database URL for SQLAlchemy"
    )
    
    # Authentication & Security
    JWT_SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT token signing"
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="Algorithm for JWT token signing")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="JWT token expiration time in minutes")
    
    # Legacy API Bearer Token (optional, for backward compatibility)
    API_BEARER: str | None = Field(default=None, description="Legacy API bearer token")
    
    # OAuth2 Configuration (for OpenAI GPT integration)
    OAUTH_CLIENT_ID: str | None = Field(default=None, description="OAuth2 client ID for OpenAI")
    OAUTH_CLIENT_SECRET: str | None = Field(default=None, description="OAuth2 client secret for OpenAI")
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins"
    )
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, description="Rate limit requests per minute")
    
    # Redis Configuration (optional)
    REDIS_URL: str | None = Field(default=None, description="Redis URL for caching and Celery")
    
    # Feature Flags
    USE_LIVE: bool = Field(default=False, description="Use live external APIs instead of mocked data")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # Pydantic v2 settings config
    model_config = SettingsConfigDict(
        env_prefix="",           # or e.g. "ANF_"
        env_file=".env",         # optional
        case_sensitive=False
    )

settings = Settings()
