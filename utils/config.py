from functools import lru_cache
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Make these optional so missing envs don't crash imports.
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="Server-side OpenAI key")
    API_BEARER: Optional[str] = Field(default=None, description="Internal API bearer token")
    NIH_API_BASE: Optional[str] = None
    MODEL: str = "gpt-4o-mini"

    model_config = SettingsConfigDict(
        env_prefix="",          # set to "ANF_" if you want a prefix
        case_sensitive=False,
    )

@lru_cache
def get_settings() -> Settings:
    # Load envs only when first used, not at import time.
    return Settings()
