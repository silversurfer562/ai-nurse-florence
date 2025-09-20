#!/usr/bin/env python3
"""
Simple test runner for unit tests that don't require the full app infrastructure.

This allows testing individual services and utilities without needing Redis, 
database connections, or other external dependencies.
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def test_readability_service():
    """Test the readability service independently."""
    from services.readability_service import analyze_readability
    
    # Test basic functionality
    result = analyze_readability("This is a simple test sentence.")
    expected_keys = {"flesch_reading_ease", "flesch_kincaid_grade", "sentences", "words", "syllables", "suggestions"}
    
    assert isinstance(result, dict)
    for key in expected_keys:
        assert key in result, f"Expected key '{key}' missing from result"
    
    print("✅ Readability service test passed")
    return True

def test_config_loading():
    """Test that configuration can be loaded with minimal environment."""
    # Set minimal required environment
    os.environ.setdefault("API_BEARER", "test-key")
    
    from utils.config import settings
    
    assert settings.API_BEARER is not None
    assert settings.LOG_LEVEL == "INFO"
    assert settings.RATE_LIMIT_PER_MINUTE == 60
    
    print("✅ Configuration loading test passed")
    return True

def test_logging_setup():
    """Test that logging can be set up."""
    from utils.logging import get_logger
    
    logger = get_logger(__name__)
    logger.info("Test log message")
    
    print("✅ Logging setup test passed")
    return True

def run_unit_tests():
    """Run all unit tests that don't require external dependencies."""
    tests = [
        test_readability_service,
        test_config_loading,
        test_logging_setup,
    ]
    
    passed = 0
    total = len(tests)
    
    print(f"Running {total} unit tests...\n")
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All unit tests passed!")
        return True
    else:
        print("💥 Some tests failed")
        return False

if __name__ == "__main__":
    success = run_unit_tests()
    sys.exit(0 if success else 1)