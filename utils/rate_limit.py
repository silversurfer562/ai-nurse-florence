"""
Rate limiting middleware for the application.

This module provides rate limiting functionality to protect endpoints
from abuse by limiting the number of requests per client.
"""
import time
from typing import Dict, List, Tuple, Optional, Set, Callable, Awaitable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
import hashlib
from utils.logging import get_logger
from utils.config import settings

logger = get_logger(__name__)

# Try to use Redis for distributed rate limiting if available
try:
    import redis
    from utils.redis_cache import get_cache
    _redis_available = True
except ImportError:
    _redis_available = False


class RateLimiter(BaseHTTPMiddleware):
    """
    Middleware to enforce rate limits on API endpoints.
    
    This middleware tracks requests by client IP or API key and
    rejects requests that exceed the configured limits.
    """
    
    def __init__(
        self,
        app,
        requests_per_minute: int,
        exempt_paths: Optional[Set[str]] = None,
    ):
        """
        Initialize the rate limiter.
        
        Args:
            app: The FastAPI application
            requests_per_minute: Maximum requests per minute per client
            exempt_paths: Paths that should not be rate limited
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.exempt_paths = exempt_paths or set()
        self.redis_url = settings.REDIS_URL
        
        # Use Redis for distributed rate limiting if available
        if self.redis_url and _redis_available:
            try:
                self.redis = redis.from_url(self.redis_url)
                self.redis.ping()
                self.use_redis = True
                logger.info(f"Using Redis for rate limiting: {self.redis_url}")
            except Exception as e:
                logger.warning(
                    f"Failed to connect to Redis for rate limiting: {str(e)}",
                    extra={"error": str(e)}
                )
                self.use_redis = False
                self.request_timestamps: Dict[str, List[float]] = {}
        else:
            self.use_redis = False
            self.request_timestamps: Dict[str, List[float]] = {}
    
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """
        Process the request and apply rate limiting.
        
        Args:
            request: The incoming request
            call_next: The next request handler
            
        Returns:
            The response from the next handler, or a 429 response if rate limited
        """
        path = request.url.path
        
        # Skip rate limiting for exempt paths
        if path in self.exempt_paths:
            return await call_next(request)
        
        # Get client identifier (IP or API key)
        client_id = self._get_client_id(request)
        
        # Check rate limit
        allow, current_count = await self._check_rate_limit(client_id)
        
        # Add rate limit headers to response
        response = await call_next(request) if allow else JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Please try again later."}
        )
        
        # Add rate limit headers
        remaining = max(0, self.requests_per_minute - current_count)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """
        Get a unique identifier for the client.
        
        Args:
            request: The incoming request
            
        Returns:
            A unique identifier for the client (hashed IP or API key)
        """
        # Try to use API key from Authorization header
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth.split(" ", 1)[1].strip()
            return f"token:{hashlib.sha256(token.encode()).hexdigest()}"
        
        # Fall back to client IP
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{hashlib.sha256(client_ip.encode()).hexdigest()}"
    
    async def _check_rate_limit(self, client_id: str) -> Tuple[bool, int]:
        """
        Check if the client has exceeded their rate limit.
        
        Args:
            client_id: The client identifier
            
        Returns:
            A tuple of (allowed, current_count)
        """
        now = time.time()
        window_start = now - 60  # 1 minute window
        
        if self.use_redis:
            return await self._check_rate_limit_redis(client_id, now, window_start)
        else:
            return self._check_rate_limit_memory(client_id, now, window_start)
    
    def _check_rate_limit_memory(
        self, client_id: str, now: float, window_start: float
    ) -> Tuple[bool, int]:
        """
        Check rate limit using in-memory storage.
        
        Args:
            client_id: The client identifier
            now: Current timestamp
            window_start: Start of the rate limit window
            
        Returns:
            A tuple of (allowed, current_count)
        """
        # Get timestamps for this client
        timestamps = self.request_timestamps.get(client_id, [])
        
        # Remove timestamps outside the window
        valid_timestamps = [ts for ts in timestamps if ts >= window_start]
        
        # Check if we're over the limit
        if len(valid_timestamps) >= self.requests_per_minute:
            logger.warning(
                f"Rate limit exceeded for client: {client_id}",
                extra={"client_id": client_id, "count": len(valid_timestamps)}
            )
            return False, len(valid_timestamps)
        
        # Add current timestamp
        valid_timestamps.append(now)
        self.request_timestamps[client_id] = valid_timestamps
        
        return True, len(valid_timestamps)
    
    async def _check_rate_limit_redis(
        self, client_id: str, now: float, window_start: float
    ) -> Tuple[bool, int]:
        """
        Check rate limit using Redis storage (for distributed environments).
        
        Args:
            client_id: The client identifier
            now: Current timestamp
            window_start: Start of the rate limit window
            
        Returns:
            A tuple of (allowed, current_count)
        """
        redis_key = f"rate_limit:{client_id}"
        
        try:
            pipeline = self.redis.pipeline()
            
            # Remove timestamps outside the window
            pipeline.zremrangebyscore(redis_key, 0, window_start)
            
            # Count remaining items
            pipeline.zcard(redis_key)
            
            # Add current timestamp
            pipeline.zadd(redis_key, {str(now): now})
            
            # Set expiry on the key
            pipeline.expire(redis_key, 60)
            
            # Execute commands
            results = pipeline.execute()
            current_count = results[1]
            
            # Check if we're over the limit
            if current_count >= self.requests_per_minute:
                logger.warning(
                    f"Rate limit exceeded for client: {client_id}",
                    extra={"client_id": client_id, "count": current_count}
                )
                return False, current_count
            
            return True, current_count
            
        except Exception as e:
            # If Redis fails, fall back to allowing the request
            logger.error(
                f"Redis rate limiting error: {str(e)}",
                extra={"client_id": client_id, "error": str(e)},
                exc_info=True
            )
            return True, 0