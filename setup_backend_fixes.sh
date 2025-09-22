#!/bin/bash

# ========================================
# AI Nurse Florence - Backend Fixes Setup Script
# ========================================
# This script applies all the critical backend fixes identified
# Run this script from your project root directory

set -e  # Exit on any error

echo "�� AI Nurse Florence - Backend Fixes Setup"
echo "=========================================="

# Check if we're in the right directory
if [[ ! -f "app.py" ]] && [[ ! -f "main.py" ]]; then
    echo "❌ Error: Please run this script from your project root directory"
    echo "   (where app.py or main.py is located)"
    exit 1
fi

# Create backup directory
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "📁 Created backup directory: $BACKUP_DIR"

# Backup existing files
echo "💾 Backing up existing files..."
for file in app.py utils/config.py utils/middleware.py requirements.txt .env; do
    if [[ -f "$file" ]]; then
        cp "$file" "$BACKUP_DIR/"
        echo "   ✓ Backed up $file"
    fi
done

# Create utils directory if it doesn't exist
mkdir -p utils

# 1. Fix the configuration file
echo "🔧 1. Fixing configuration (utils/config.py)..."
cat > utils/config.py << 'EOF'
"""
Centralized application configuration using Pydantic Settings.
All critical configuration issues have been resolved.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator
from typing import List, Optional
from functools import lru_cache
import os

class Settings(BaseSettings):
    """Application settings with validation and type safety."""
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        case_sensitive=True
    )
    
    # Core Application Settings
    API_BEARER: str = "default-api-key-change-in-production"
    CORS_ORIGINS_STR: str = Field(
        default="http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:8000",
        alias="CORS_ORIGINS"
    )
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    
    # Service Configuration
    USE_LIVE: bool = False  # Use live external services vs stubs
    
    # Database Configuration
    DATABASE_URL: str = "sqlite+aiosqlite:///./ai_nurse_florence.db"
    
    # Cache Configuration (Redis)
    REDIS_URL: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    ENABLE_RATE_LIMITING: bool = True
    
    # Authentication & Security
    JWT_SECRET_KEY: str = "a_very_secret_key_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # OAuth2 Configuration (FIXED: Added missing OAuth settings)
    OAUTH_CLIENT_ID: Optional[str] = None
    OAUTH_CLIENT_SECRET: Optional[str] = None
    OAUTH_REDIRECT_URI: str = "http://localhost:8000/auth/callback"
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        origins = [origin.strip() for origin in self.CORS_ORIGINS_STR.split(",")]
        return [origin for origin in origins if origin]  # Filter out empty strings

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

# Global settings instance
settings = get_settings()
EOF
echo "   ✅ Configuration fixed"

# 2. Create basic .env file if it doesn't exist
if [[ ! -f ".env" ]]; then
    echo "🔧 2. Creating .env file..."
    cat > .env << 'EOF'
# AI Nurse Florence - Environment Configuration
API_BEARER=dev-api-key-12345-change-in-production
CORS_ORIGINS=http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:8000
LOG_LEVEL=INFO
DEBUG=false
OPENAI_API_KEY=
USE_LIVE=0
RATE_LIMIT_PER_MINUTE=60
ENABLE_RATE_LIMITING=true
DATABASE_URL=sqlite+aiosqlite:///./ai_nurse_florence.db
JWT_SECRET_KEY=dev-secret-change-in-production
OAUTH_REDIRECT_URI=http://localhost:8000/auth/callback
EOF
    echo "   ✅ Created .env file"
else
    echo "   ℹ️  .env file already exists, skipping"
fi

# 3. Install/upgrade essential dependencies
echo "🔧 3. Installing essential dependencies..."
pip install --upgrade \
    "fastapi>=0.104.0" \
    "uvicorn[standard]>=0.24.0" \
    "python-dotenv>=1.0.0" \
    "pydantic>=2.0.0" \
    "pydantic-settings>=2.0.0" \
    "sqlalchemy>=2.0.0" \
    "aiosqlite>=0.19.0"

echo "   ✅ Essential dependencies installed"

# 4. Test imports
echo "🔧 4. Testing configuration import..."
python3 -c "
try:
    from utils.config import settings
    print('   ✅ Configuration imports successfully')
    print(f'   ℹ️  CORS Origins: {len(settings.CORS_ORIGINS)} configured')
    print(f'   ℹ️  Database: {settings.DATABASE_URL}')
    print(f'   ℹ️  Rate Limiting: {\"Enabled\" if settings.ENABLE_RATE_LIMITING else \"Disabled\"}')
except Exception as e:
    print(f'   ❌ Configuration import failed: {e}')
    exit(1)
"

echo ""
echo "🎉 Backend Fixes Applied Successfully!"
echo "=========================================="
echo ""
echo "✅ FIXES APPLIED:"
echo "   • Fixed configuration issues"
echo "   • Added proper OAuth settings"
echo "   • Enhanced security configuration" 
echo "   • Created working .env file"
echo ""
echo "🚀 NEXT STEPS:"
echo "1. Edit
