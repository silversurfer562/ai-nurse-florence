"""
Tests that middleware-configured rate limiting takes precedence over global settings
"""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.utils.rate_limit import RateLimiter
from src.utils.config import get_settings


def test_middleware_config_overrides_global_flag():
    """Ensure that constructing RateLimiter with a requests_per_minute > 0
    enforces limits even when global settings.RATE_LIMIT_ENABLED is False.
    """
    settings = get_settings()

    # Force global feature flag off to simulate environment .env disabling rate limiting
    settings.RATE_LIMIT_ENABLED = False

    # Clear in-memory rate limit state to avoid cross-test pollution
    from src.utils import rate_limit as _rl
    _rl._memory_rate_limit.clear()

    app = FastAPI()

    # Install rate limiter with a very low limit so we can trigger blocking
    app.add_middleware(RateLimiter, requests_per_minute=1, exempt_paths=[])

    @app.get("/")
    def root():
        return {"message": "ok"}

    client = TestClient(app)

    # First request should succeed and include rate limit headers
    r1 = client.get("/")
    assert r1.status_code == 200
    assert "X-RateLimit-Limit" in r1.headers

    # Second request should be rate limited (429)
    r2 = client.get("/")
    assert r2.status_code == 429
