"""
Test for configuration loading to verify API_BEARER and other missing fields are properly defined.
"""
import os
import pytest
from utils.config import Settings


def test_configuration_with_minimal_environment():
    """Test that configuration loads with only required OPENAI_API_KEY."""
    # Clear existing environment
    original_env = os.environ.copy()
    
    try:
        # Set minimal required environment
        os.environ.clear()
        os.environ["OPENAI_API_KEY"] = "test-key"
        
        # Create new settings instance
        settings = Settings()
        
        # Test that API_BEARER is properly defined and optional
        assert hasattr(settings, 'API_BEARER')
        assert settings.API_BEARER is None  # Should be None by default
        
        # Test other fields are properly defined with defaults
        assert hasattr(settings, 'CORS_ORIGINS')
        assert isinstance(settings.CORS_ORIGINS, list)
        assert settings.CORS_ORIGINS == ['http://localhost:3000']
        
        assert hasattr(settings, 'DATABASE_URL')
        assert settings.DATABASE_URL == "sqlite+aiosqlite:///./ai_nurse_florence.db"
        
        assert hasattr(settings, 'JWT_SECRET_KEY')
        assert settings.JWT_SECRET_KEY == "your-secret-key-change-in-production"
        
        assert hasattr(settings, 'RATE_LIMIT_PER_MINUTE')
        assert settings.RATE_LIMIT_PER_MINUTE == 60
        
        assert hasattr(settings, 'USE_LIVE')
        assert settings.USE_LIVE is False
        
        assert hasattr(settings, 'OAUTH_CLIENT_ID')
        assert settings.OAUTH_CLIENT_ID is None
        
        assert hasattr(settings, 'OAUTH_CLIENT_SECRET')
        assert settings.OAUTH_CLIENT_SECRET is None
        
    finally:
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)


def test_configuration_with_api_bearer():
    """Test that API_BEARER can be set via environment variable."""
    original_env = os.environ.copy()
    
    try:
        # Set environment with API_BEARER
        os.environ.clear()
        os.environ["OPENAI_API_KEY"] = "test-key"
        os.environ["API_BEARER"] = "my-secret-token"
        
        # Create new settings instance
        settings = Settings()
        
        # Test that API_BEARER is properly set
        assert settings.API_BEARER == "my-secret-token"
        
    finally:
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)


def test_cors_origins_parsing():
    """Test that CORS_ORIGINS parses comma-separated values correctly."""
    original_env = os.environ.copy()
    
    try:
        # Set environment with comma-separated CORS origins
        os.environ.clear()
        os.environ["OPENAI_API_KEY"] = "test-key"
        os.environ["CORS_ORIGINS"] = "http://localhost:3000,https://example.com,https://api.example.com"
        
        # Create new settings instance
        settings = Settings()
        
        # Test that CORS_ORIGINS is properly parsed
        expected = ['http://localhost:3000', 'https://example.com', 'https://api.example.com']
        assert settings.CORS_ORIGINS == expected
        
    finally:
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)


def test_all_missing_fields_resolved():
    """Test that all previously missing configuration fields are now defined."""
    original_env = os.environ.copy()
    
    try:
        # Set minimal environment
        os.environ.clear()
        os.environ["OPENAI_API_KEY"] = "test-key"
        
        # Create new settings instance
        settings = Settings()
        
        # List of all fields that were missing and should now be defined
        required_fields = [
            'API_BEARER',
            'CORS_ORIGINS', 
            'USE_LIVE',
            'RATE_LIMIT_PER_MINUTE',
            'REDIS_URL',
            'DATABASE_URL',
            'JWT_SECRET_KEY',
            'JWT_ALGORITHM',
            'ACCESS_TOKEN_EXPIRE_MINUTES',
            'OAUTH_CLIENT_ID',
            'OAUTH_CLIENT_SECRET'
        ]
        
        # Verify all fields exist
        for field in required_fields:
            assert hasattr(settings, field), f"Missing field: {field}"
            
        # Verify none of them cause AttributeError when accessed
        for field in required_fields:
            value = getattr(settings, field)
            # Just accessing it should not raise an error
            assert value is not None or field in ['API_BEARER', 'REDIS_URL', 'OAUTH_CLIENT_ID', 'OAUTH_CLIENT_SECRET']
            
    finally:
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)