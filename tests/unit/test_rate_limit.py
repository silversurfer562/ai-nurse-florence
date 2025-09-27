"""
Tests for rate limiting middleware
"""

import pytest
import time
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.utils.rate_limit import RateLimiter
from src.utils.config import get_settings

# Create a test app
def create_test_app(rate_limit: int = 5, window_seconds: int = 60):
    app = FastAPI()
    
    app.add_middleware(
        RateLimiter,
        requests_per_minute=rate_limit,
        exempt_paths=["/exempt"]
    )
    
    @app.get("/")
    def read_root():
        return {"message": "Hello World"}
    
    @app.get("/exempt")
    def exempt_path():
        return {"message": "Exempt Path"}
    
    return app

def test_rate_limiting():
    """Test basic rate limiting functionality"""
    # Create app with low rate limit for testing
    app = create_test_app(rate_limit=5)
    client = TestClient(app)
    
    # Make requests up to limit
    for i in range(5):
        response = client.get("/")
        assert response.status_code == 200
        
        # Check rate limit headers
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers
        
        limit = int(response.headers["X-RateLimit-Limit"])
        remaining = int(response.headers["X-RateLimit-Remaining"])
        
        assert limit == 5
        assert remaining == 5 - (i + 1)
    
    # Next request should be rate limited
    response = client.get("/")
    assert response.status_code == 429
    assert "Retry-After" in response.headers
    
    # Response body should contain error details
    error = response.json()
    assert error["error"] == "Too many requests"
    assert error["error_type"] == "rate_limit_error"
    assert "retry_after" in error

def test_exempt_paths():
    """Test that exempt paths bypass rate limiting"""
    # Create app with low rate limit for testing
    app = create_test_app(rate_limit=2)
    client = TestClient(app)
    
    # First use up the rate limit on normal path
    client.get("/")
    client.get("/")
    
    # Regular path should be rate limited now
    response = client.get("/")
    assert response.status_code == 429
    
    # Exempt path should still be accessible
    response = client.get("/exempt")
    assert response.status_code == 200
    assert response.json() == {"message": "Exempt Path"}

if __name__ == "__main__":
    # Run tests manually
    test_rate_limiting()
    test_exempt_paths()
    print("All tests passed!")
