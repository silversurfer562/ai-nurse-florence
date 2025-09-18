# utils/config.py  (Pydantic v2)
from pydantic import Field, field_validator
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
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v

    # Pydantic v2 settings config
    model_config = SettingsConfigDict(
        env_prefix="",           # or e.g. "ANF_"
        env_file=".env",         # optional
        case_sensitive=False
    )

settings = Settings()

settings = Settings()
