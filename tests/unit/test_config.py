"""
Unit tests for configuration management following Configuration Management pattern.
Tests centralized configuration with environment variables and feature flags.
"""

import pytest

pytestmark = pytest.mark.unit

class TestConfiguration:
    """Test configuration management following Configuration Management pattern."""
    
    def test_get_settings(self):
        """Test settings loading with defaults."""
        from src.utils.config import get_settings
        
        settings = get_settings()
        
        # Verify basic settings
        assert settings.APP_NAME == "AI Nurse Florence"
        assert settings.APP_VERSION == "2.4.0"
        assert isinstance(settings.ALLOWED_ORIGINS, list)
        
    def test_educational_banner(self):
        """Test educational banner following API Design Standards."""
        from src.utils.config import get_educational_banner
        
        banner = get_educational_banner()
        
        # Verify educational disclaimer content
        assert "not medical advice" in banner.lower()
        assert "no phi stored" in banner.lower()
        
    def test_feature_flags(self):
        """Test feature flags following feature flag pattern."""
        from src.utils.config import is_feature_enabled
        
        # Test various feature flags
        features_to_test = ['openai', 'redis', 'metrics', 'caching', 'docs']
        
        for feature in features_to_test:
            # Should return boolean without error
            result = is_feature_enabled(feature)
            assert isinstance(result, bool)
            
    def test_openai_config(self):
        """Test OpenAI configuration following OpenAI Integration pattern."""
        from src.utils.config import get_openai_config
        
        config = get_openai_config()
        
        # Verify config structure
        assert "api_key" in config
        assert "model" in config  
        assert "available" in config
        assert isinstance(config["available"], bool)
        
    def test_redis_config(self):
        """Test Redis configuration following Caching Strategy pattern."""
        from src.utils.config import get_redis_config
        
        config = get_redis_config()
        
        # Verify config structure
        assert "url" in config
        assert "available" in config
        assert "ttl_seconds" in config
        assert isinstance(config["available"], bool)
        assert isinstance(config["ttl_seconds"], int)

class TestServiceConfiguration:
    """Test service configuration integration."""
    
    def test_service_loading_with_config(self):
        """Test that services can load configuration without errors."""
        try:
            # This should not raise ImportError now
            from src.services import get_available_services
            services = get_available_services()
            
            # Should be a dict with service status
            assert isinstance(services, dict)
            
        except Exception as e:
            pytest.fail(f"Service configuration failed: {e}")
