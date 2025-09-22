import os
from typing import List

class Settings:
    # Railway provides PORT automatically
    port: int = int(os.getenv("PORT", 8000))
    railway_environment: str = os.getenv("RAILWAY_ENVIRONMENT", "development")
    
    # Your settings
    app_name: str = "AI Nurse Florence"
    app_version: str = "1.0.0"
    secret_key: str = os.getenv("SECRET_KEY", "change-this")
    
    # CORS
    cors_origins: List[str] = os.getenv(
        "CORS_ORIGINS", 
        "https://chat.openai.com"
    ).split(",")
    
    def is_production(self) -> bool:
        return self.railway_environment == "production"

settings = Settings()
