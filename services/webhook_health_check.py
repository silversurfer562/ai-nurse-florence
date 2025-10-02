"""
Post-Deployment Health Check Service
Automatically verifies deployment health after successful Railway deployments.
"""

import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class HealthCheckResult(BaseModel):
    """Result of a single health check."""

    endpoint: str
    status: str  # "passed", "failed", "warning"
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    timestamp: datetime
    details: Dict = {}


class HealthCheckReport(BaseModel):
    """Complete health check report."""

    deployment_id: str
    timestamp: datetime
    overall_status: str  # "healthy", "degraded", "unhealthy"
    checks_passed: int
    checks_failed: int
    checks_total: int
    results: List[HealthCheckResult]
    summary: str


def get_base_url() -> str:
    """Get the deployment base URL for health checks."""
    # Try to get from environment variable first
    base_url = os.getenv("DEPLOYMENT_URL", os.getenv("RAILWAY_PUBLIC_DOMAIN"))

    if base_url:
        # Ensure it has https://
        if not base_url.startswith("http"):
            base_url = f"https://{base_url}"
        return base_url

    # Fallback to localhost for development
    return "http://localhost:8000"


async def check_endpoint(
    client: httpx.AsyncClient,
    endpoint: str,
    method: str = "GET",
    expected_status: int = 200,
    timeout: float = 10.0
) -> HealthCheckResult:
    """
    Check a single endpoint.

    Args:
        client: HTTP client to use
        endpoint: Endpoint path (e.g., "/api/v1/health")
        method: HTTP method
        expected_status: Expected HTTP status code
        timeout: Request timeout in seconds

    Returns:
        HealthCheckResult: Result of the health check
    """
    base_url = get_base_url()
    full_url = f"{base_url}{endpoint}"

    logger.info(f"🔍 Checking endpoint: {method} {full_url}")

    start_time = datetime.utcnow()

    try:
        response = await client.request(method, full_url, timeout=timeout)
        end_time = datetime.utcnow()

        response_time_ms = (end_time - start_time).total_seconds() * 1000

        # Determine status
        if response.status_code == expected_status:
            status = "passed"
            error_message = None
        elif 200 <= response.status_code < 300:
            status = "warning"
            error_message = f"Unexpected status code: {response.status_code} (expected {expected_status})"
        else:
            status = "failed"
            error_message = f"HTTP {response.status_code}"

        # Try to parse JSON response for additional details
        details = {}
        try:
            details = response.json()
        except Exception:
            details = {"raw_response": response.text[:200]}

        return HealthCheckResult(
            endpoint=endpoint,
            status=status,
            status_code=response.status_code,
            response_time_ms=round(response_time_ms, 2),
            error_message=error_message,
            timestamp=end_time,
            details=details
        )

    except httpx.TimeoutException:
        return HealthCheckResult(
            endpoint=endpoint,
            status="failed",
            error_message="Request timeout",
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        return HealthCheckResult(
            endpoint=endpoint,
            status="failed",
            error_message=str(e),
            timestamp=datetime.utcnow()
        )


async def run_post_deployment_health_checks(deployment_id: str = "unknown") -> HealthCheckReport:
    """
    Run comprehensive health checks after deployment.

    This function tests critical endpoints to ensure the deployment is healthy:
    - Core health endpoint
    - API endpoints
    - Database connectivity
    - External service integrations

    Args:
        deployment_id: ID of the deployment being checked

    Returns:
        HealthCheckReport: Complete health check report
    """
    logger.info(f"🏥 Starting post-deployment health checks for: {deployment_id}")

    results: List[HealthCheckResult] = []

    async with httpx.AsyncClient() as client:
        # Define critical endpoints to check
        endpoints = [
            {
                "endpoint": "/api/v1/health",
                "method": "GET",
                "expected_status": 200,
                "timeout": 10.0
            },
            {
                "endpoint": "/api/v1/disease/lookup?q=diabetes",
                "method": "GET",
                "expected_status": 200,
                "timeout": 15.0
            },
            {
                "endpoint": "/api/v1/genes/search?q=BRCA1",
                "method": "GET",
                "expected_status": 200,
                "timeout": 15.0
            },
            {
                "endpoint": "/docs",
                "method": "GET",
                "expected_status": 200,
                "timeout": 10.0
            },
            {
                "endpoint": "/api/v1/literature/search?q=nursing",
                "method": "GET",
                "expected_status": 200,
                "timeout": 20.0
            }
        ]

        # Run all health checks
        for endpoint_config in endpoints:
            result = await check_endpoint(client, **endpoint_config)
            results.append(result)

            # Log result
            if result.status == "passed":
                logger.info(f"  ✅ {result.endpoint}: {result.status_code} ({result.response_time_ms}ms)")
            elif result.status == "warning":
                logger.warning(f"  ⚠️  {result.endpoint}: {result.error_message}")
            else:
                logger.error(f"  ❌ {result.endpoint}: {result.error_message}")

    # Calculate summary statistics
    checks_passed = sum(1 for r in results if r.status == "passed")
    checks_failed = sum(1 for r in results if r.status == "failed")
    checks_total = len(results)

    # Determine overall status
    if checks_failed == 0:
        overall_status = "healthy"
        summary = f"All {checks_total} health checks passed"
    elif checks_passed >= checks_total * 0.7:  # 70% threshold
        overall_status = "degraded"
        summary = f"{checks_passed}/{checks_total} checks passed, {checks_failed} failed"
    else:
        overall_status = "unhealthy"
        summary = f"{checks_failed}/{checks_total} checks failed"

    report = HealthCheckReport(
        deployment_id=deployment_id,
        timestamp=datetime.utcnow(),
        overall_status=overall_status,
        checks_passed=checks_passed,
        checks_failed=checks_failed,
        checks_total=checks_total,
        results=results,
        summary=summary
    )

    # Log final summary
    if overall_status == "healthy":
        logger.info(f"✅ Health checks PASSED: {summary}")
    elif overall_status == "degraded":
        logger.warning(f"⚠️  Health checks DEGRADED: {summary}")
    else:
        logger.error(f"❌ Health checks FAILED: {summary}")

    return report


async def run_continuous_health_monitoring(interval_seconds: int = 300):
    """
    Run continuous health monitoring (optional background task).

    Args:
        interval_seconds: Interval between health checks (default: 5 minutes)
    """
    import asyncio

    logger.info(f"🔄 Starting continuous health monitoring (interval: {interval_seconds}s)")

    while True:
        try:
            await run_post_deployment_health_checks(deployment_id="continuous-monitor")
            await asyncio.sleep(interval_seconds)
        except Exception as e:
            logger.error(f"❌ Error in continuous health monitoring: {str(e)}")
            await asyncio.sleep(60)  # Wait 1 minute before retrying


# Export for use in webhook router
__all__ = [
    "run_post_deployment_health_checks",
    "run_continuous_health_monitoring",
    "HealthCheckReport",
    "HealthCheckResult"
]
