# utils/config.py  (Pydantic v2)
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # API Configuration
    OPENAI_API_KEY: str = Field(..., description="Server-side OpenAI API key")
    API_BEARER: str | None = Field(default=None, description="Legacy API bearer token")
    NIH_API_BASE: str | None = Field(default=None)
    MODEL: str = Field(default="gpt-4o-mini")
    
    # Database Configuration
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./test.db", description="Database connection URL")
    
    # JWT Configuration
    JWT_SECRET_KEY: str = Field(default="your-secret-key-here", description="JWT secret key")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="JWT token expiration in minutes")
    
    # OAuth Configuration
    OAUTH_CLIENT_ID: str | None = Field(default=None, description="OAuth client ID")
    OAUTH_CLIENT_SECRET: str | None = Field(default=None, description="OAuth client secret")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, description="Rate limit per minute")
    
    # CORS Configuration
    CORS_ORIGINS: str = Field(default="http://localhost:3000", description="Allowed CORS origins")

    # Additional Configuration
    USE_LIVE: str = Field(default="0", description="Use live services")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")

    # Pydantic v2 settings config
    model_config = SettingsConfigDict(
        env_prefix="",           # or e.g. "ANF_"
        env_file=".env",         # optional
        case_sensitive=False,
        extra="ignore"           # Allow extra fields
    )

settings = Settings()
