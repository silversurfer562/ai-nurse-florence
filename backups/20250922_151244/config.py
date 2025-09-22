"""
Centralized application configuration using Pydantic.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List, Optional
from functools import lru_cache

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra='ignore'  # Allow extra environment variables without validation errors
    )
    
    # Core App Settings
    API_BEARER: str = "default-api-key-change-in-production"
    CORS_ORIGINS_STR: str = Field("https://ainurseflorence.com,https://www.ainurseflorence.com", alias="CORS_ORIGINS")
    LOG_LEVEL: str = "INFO"
    
    # OpenAI Settings
    OPENAI_API_KEY: Optional[str] = None
    
    # Service Settings
    USE_LIVE: bool = False
    
    # Infrastructure Settings
    REDIS_URL: Optional[str] = None
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    
    # Feature Settings
    RATE_LIMIT_PER_MINUTE: int = 60

    # OAuth2 Settings
    OAUTH_CLIENT_ID: Optional[str] = None
    OAUTH_CLIENT_SECRET: Optional[str] = None
    JWT_SECRET_KEY: str = "a_very_secret_key_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    
    # External API Keys (Optional)
    NCBI_API_KEY: Optional[str] = None
    
    # Monitoring Settings (Optional)
    GRAFANA_ADMIN_USER: Optional[str] = None
    GRAFANA_ADMIN_PASSWORD: Optional[str] = None
    
    # Docker Settings (Optional)
    DOCKER_REGISTRY: Optional[str] = None
    TAG: Optional[str] = None

    @property
    def CORS_ORIGINS(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS_STR.split(",") if origin.strip()]

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
