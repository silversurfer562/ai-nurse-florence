"""
Prometheus metrics for monitoring the application.

This module provides metrics collection and export functionality using Prometheus.
"""
from fastapi import FastAPI, Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
from typing import Callable, Awaitable
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
REQUEST_COUNT = Counter(
    'api_request_count', 
    'Number of requests received',
    ['method', 'endpoint', 'status_code']
)

REQUEST_LATENCY = Histogram(
    'api_request_latency_seconds', 
    'Request latency in seconds',
    ['method', 'endpoint']
)

REQUESTS_IN_PROGRESS = Gauge(
    'api_requests_in_progress',
    'Number of requests currently being processed',
    ['method', 'endpoint']
)

ERROR_COUNT = Counter(
    'api_error_count',
    'Number of errors that have occurred',
    ['method', 'endpoint', 'exception_type']
)

CACHE_HIT_COUNT = Counter(
    'api_cache_hit_count',
    'Number of cache hits',
    ['cache_key']
)

CACHE_MISS_COUNT = Counter(
    'api_cache_miss_count',
    'Number of cache misses',
    ['cache_key']
)

EXTERNAL_SERVICE_REQUEST_COUNT = Counter(
    'api_external_service_request_count',
    'Number of requests to external services',
    ['service', 'operation']
)

EXTERNAL_SERVICE_ERROR_COUNT = Counter(
    'api_external_service_error_count',
    'Number of errors from external services',
    ['service', 'operation', 'error_type']
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Middleware to collect and track Prometheus metrics.
    
    This middleware tracks request counts, latency, and in-progress requests.
    """
    
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        method = request.method
        path = request.url.path
        
        # Skip metrics endpoint to avoid recursive tracking
        if path == "/metrics":
            return await call_next(request)
        
        # Track in-progress requests
        REQUESTS_IN_PROGRESS.labels(method=method, endpoint=path).inc()
        
        # Track request latency
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Record metrics
            status_code = response.status_code
            duration = time.time() - start_time
            
            REQUEST_COUNT.labels(
                method=method, 
                endpoint=path, 
                status_code=status_code
            ).inc()
            
            REQUEST_LATENCY.labels(
                method=method,
                endpoint=path
            ).observe(duration)
            
            return response
            
        except Exception as e:
            # Record exception metrics
            duration = time.time() - start_time
            
            ERROR_COUNT.labels(
                method=method,
                endpoint=path,
                exception_type=type(e).__name__
            ).inc()
            
            REQUEST_LATENCY.labels(
                method=method,
                endpoint=path
            ).observe(duration)
            
            raise
            
        finally:
            # Always decrement in-progress counter
            REQUESTS_IN_PROGRESS.labels(method=method, endpoint=path).dec()


def setup_metrics(app: FastAPI, metrics_route: str = "/metrics") -> None:
    """
    Set up Prometheus metrics for a FastAPI application.
    
    Args:
        app: The FastAPI application
        metrics_route: The route to expose metrics (default: /metrics)
    """
    # Add the metrics middleware
    app.add_middleware(PrometheusMiddleware)
    
    # Add metrics endpoint
    @app.get(metrics_route)
    async def metrics():
        return Response(
            content=prometheus_client.generate_latest(),
            media_type="text/plain"
        )


# Helper functions to record metrics in various parts of the application

def record_cache_hit(cache_key: str) -> None:
    """
    Record a cache hit.
    
    Args:
        cache_key: The cache key that was hit
    """
    CACHE_HIT_COUNT.labels(cache_key=cache_key).inc()


def record_cache_miss(cache_key: str) -> None:
    """
    Record a cache miss.
    
    Args:
        cache_key: The cache key that was missed
    """
    CACHE_MISS_COUNT.labels(cache_key=cache_key).inc()


def record_external_request(service: str, operation: str) -> None:
    """
    Record a request to an external service.
    
    Args:
        service: The name of the external service
        operation: The operation being performed
    """
    EXTERNAL_SERVICE_REQUEST_COUNT.labels(
        service=service,
        operation=operation
    ).inc()


def record_external_error(service: str, operation: str, error_type: str) -> None:
    """
    Record an error from an external service.
    
    Args:
        service: The name of the external service
        operation: The operation being performed
        error_type: The type of error that occurred
    """
    EXTERNAL_SERVICE_ERROR_COUNT.labels(
        service=service,
        operation=operation,
        error_type=error_type
    ).inc()