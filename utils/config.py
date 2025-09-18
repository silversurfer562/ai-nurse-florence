# utils/config.py  (Pydantic v2)
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Core API Configuration
    OPENAI_API_KEY: str = Field(..., description="Server-side OpenAI API key")
    NIH_API_BASE: str | None = Field(default=None, description="NIH API base URL")
    MODEL: str = Field(default="gpt-4o-mini", description="Default OpenAI model to use")
    
    # Database Configuration
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./florence.db", description="Database connection URL")
    
    # Security Configuration
    API_BEARER: str | None = Field(default=None, description="API Bearer token for authentication")
    JWT_SECRET_KEY: str = Field(default="your-secret-key-change-in-production", description="JWT secret key")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="JWT token expiration in minutes")
    
    # OAuth Configuration
    OAUTH_CLIENT_ID: str | None = Field(default=None, description="OAuth client ID")
    OAUTH_CLIENT_SECRET: str | None = Field(default=None, description="OAuth client secret")
    
    # CORS Configuration
    CORS_ORIGINS: list[str] = Field(default=["http://localhost:3000", "http://localhost:8000"], description="Allowed CORS origins")
    
    # Rate Limiting Configuration
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, description="Rate limit requests per minute per client")
    
    # Redis Configuration
    REDIS_URL: str | None = Field(default=None, description="Redis connection URL for caching and rate limiting")
    
    # Feature Flags
    USE_LIVE: bool = Field(default=False, description="Whether to use live external APIs")

    # Pydantic v2 settings config
    model_config = SettingsConfigDict(
        env_prefix="",           # or e.g. "ANF_"
        env_file=".env",         # optional
        case_sensitive=False
    )

settings = Settings()
