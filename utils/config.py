# utils/config.py  (Pydantic v2)
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Example settings — edit to match your app
    OPENAI_API_KEY: str = Field(default="", description="Server-side OpenAI API key")
    NIH_API_BASE: str | None = Field(default=None)
    MODEL: str = Field(default="gpt-4o-mini")
    
    # Database settings
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./app.db", description="Database connection URL")
    
    # Authentication settings
    API_BEARER: str | None = Field(default=None, description="Legacy API bearer token")
    JWT_SECRET_KEY: str = Field(default="your-secret-key-here-change-in-production", description="Secret key for JWT tokens")
    JWT_ALGORITHM: str = Field(default="HS256", description="Algorithm for JWT tokens")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Token expiration time in minutes")
    
    # OAuth2 settings for OpenAI
    OAUTH_CLIENT_ID: str | None = Field(default=None, description="OAuth2 client ID")
    OAUTH_CLIENT_SECRET: str | None = Field(default=None, description="OAuth2 client secret")
    
    # Service configuration
    USE_LIVE: int = Field(default=0, description="Use live services (0=False, 1=True)")
    CORS_ORIGINS: str = Field(default="*", description="CORS origins")
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, description="Rate limit per minute")
    
    # Redis configuration
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")

    # Pydantic v2 settings config
    model_config = SettingsConfigDict(
        env_prefix="",           # or e.g. "ANF_"
        env_file=".env",         # optional
        case_sensitive=False
    )

settings = Settings()
