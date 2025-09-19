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
    
    # Notion Integration Settings
    NOTION_TOKEN: Optional[str] = Field(default=None, description="Notion API integration token")
    NOTION_DATABASE_ID: Optional[str] = Field(default=None, description="Notion database ID for tracking")
    
    # GitHub Webhook Settings
    GITHUB_WEBHOOK_SECRET: Optional[str] = Field(default=None, description="GitHub webhook secret for verification")
    
    # Integration Features
    ENABLE_NOTION_SYNC: bool = Field(default=False, description="Enable Notion synchronization")
    RETRY_ATTEMPTS: int = Field(default=3, description="Number of retry attempts for external API calls")
    RETRY_DELAY: int = Field(default=1, description="Delay between retry attempts in seconds")

    model_config = SettingsConfigDict(
        env_prefix="",          # set to "ANF_" if you want a prefix
        case_sensitive=False,
    )

@lru_cache
def get_settings() -> Settings:
    # Load envs only when first used, not at import time.
    return Settings()
