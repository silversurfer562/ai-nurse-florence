# utils/config.py  (Pydantic v2)
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Example settings — edit to match your app
    OPENAI_API_KEY: str = Field(..., description="Server-side OpenAI API key")
    NIH_API_BASE: str | None = Field(default=None)
    MODEL: str = Field(default="gpt-4o-mini")

    # Pydantic v2 settings config
    model_config = SettingsConfigDict(
        env_prefix="",           # or e.g. "ANF_"
        env_file=".env",         # optional
        case_sensitive=False
    )

settings = Settings()
