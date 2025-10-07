"""
AI Provider Fallback Service - AI Nurse Florence

Implements automatic failover between AI providers with circuit breaker pattern.
Production-grade reliability for healthcare applications.

Architecture:
- Primary provider: claude-3.5-sonnet (quality-first)
- Fallback provider: gpt-4o (reliable backup)
- Circuit breaker: Prevents cascade failures
- Exponential backoff: Graceful retry logic
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from src.services.claude_service import claude_service
from src.services.openai_client import OpenAIService
from src.utils.config import get_settings

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """
    Circuit breaker pattern to prevent cascade failures.

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, reject requests immediately
    - HALF_OPEN: Testing if service recovered
    """

    def __init__(self, threshold: int, timeout: int):
        self.threshold = threshold  # Failures before opening circuit
        self.timeout = timeout  # Seconds before attempting recovery
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def record_success(self):
        """Record successful request - reset failure count."""
        self.failure_count = 0
        self.state = "CLOSED"
        logger.info("Circuit breaker reset - service healthy")

    def record_failure(self):
        """Record failed request - may open circuit."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.threshold:
            self.state = "OPEN"
            logger.warning(
                f"Circuit breaker OPEN - {self.failure_count} consecutive failures"
            )

    def can_attempt(self) -> bool:
        """Check if request can be attempted."""
        if self.state == "CLOSED":
            return True

        if self.state == "OPEN":
            # Check if timeout expired - try half-open
            if self.last_failure_time:
                elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                if elapsed >= self.timeout:
                    self.state = "HALF_OPEN"
                    logger.info("Circuit breaker HALF_OPEN - testing recovery")
                    return True
            return False

        # HALF_OPEN state - allow single test request
        return True

    def get_state(self) -> Dict[str, Any]:
        """Get circuit breaker state for monitoring."""
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "threshold": self.threshold,
            "last_failure": (
                self.last_failure_time.isoformat() if self.last_failure_time else None
            ),
        }


class AIProviderFallback:
    """
    Unified AI service with automatic fallback and circuit breaker.

    Features:
    - Automatic retry with exponential backoff
    - Circuit breaker to prevent cascade failures
    - Seamless failover to secondary provider
    - Production-grade error handling
    """

    def __init__(self):
        self.settings = get_settings()

        # Initialize providers
        self.openai_service = OpenAIService()
        self.claude_service = claude_service

        # Circuit breakers for each provider
        self.circuit_breakers = {
            "openai": CircuitBreaker(
                threshold=self.settings.AI_CIRCUIT_BREAKER_THRESHOLD,
                timeout=self.settings.AI_CIRCUIT_BREAKER_TIMEOUT,
            ),
            "anthropic": CircuitBreaker(
                threshold=self.settings.AI_CIRCUIT_BREAKER_THRESHOLD,
                timeout=self.settings.AI_CIRCUIT_BREAKER_TIMEOUT,
            ),
        }

        logger.info(
            f"AI Fallback Service initialized - Primary: {self.settings.AI_PROVIDER}, "
            f"Fallback: {self.settings.get_fallback_provider() or 'None'}"
        )

    async def generate_response(
        self,
        prompt: str,
        context: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Generate AI response with automatic fallback.

        Args:
            prompt: User prompt for AI generation
            context: Optional context for better responses
            max_tokens: Maximum response tokens
            temperature: Randomness (0-1)

        Returns:
            Dict with AI response and provider metadata
        """
        primary_provider = self.settings.get_active_ai_provider()
        fallback_provider = self.settings.get_fallback_provider()

        # Try primary provider with retry logic
        result = await self._try_provider_with_retry(
            provider=primary_provider,
            prompt=prompt,
            context=context,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        # If primary succeeded, return result
        if result and not result.get("error"):
            return result

        # Primary failed - try fallback if available
        if fallback_provider and self.settings.AI_FALLBACK_ENABLED:
            logger.warning(
                f"Primary provider ({primary_provider}) failed, "
                f"falling back to {fallback_provider}"
            )

            fallback_result = await self._try_provider_with_retry(
                provider=fallback_provider,
                prompt=prompt,
                context=context,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            if fallback_result and not fallback_result.get("error"):
                fallback_result["fallback_used"] = True
                fallback_result["primary_provider_failed"] = primary_provider
                return fallback_result

        # Both failed or no fallback - return error
        return {
            "error": "All AI providers unavailable",
            "primary_provider": primary_provider,
            "fallback_provider": fallback_provider,
            "service_status": "degraded",
            "circuit_breaker_states": {
                provider: cb.get_state()
                for provider, cb in self.circuit_breakers.items()
            },
        }

    async def _try_provider_with_retry(
        self,
        provider: str,
        prompt: str,
        context: Optional[str],
        max_tokens: int,
        temperature: float,
    ) -> Optional[Dict[str, Any]]:
        """
        Try a provider with exponential backoff retry.

        Args:
            provider: 'openai' or 'anthropic'
            prompt: User prompt
            context: Optional context
            max_tokens: Maximum tokens
            temperature: Temperature setting

        Returns:
            Response dict or None if all retries failed
        """
        circuit_breaker = self.circuit_breakers[provider]

        # Check circuit breaker
        if not circuit_breaker.can_attempt():
            logger.warning(f"Circuit breaker OPEN for {provider} - skipping attempts")
            return {
                "error": f"{provider} circuit breaker open",
                "circuit_breaker_state": circuit_breaker.get_state(),
            }

        max_retries = self.settings.AI_MAX_RETRIES

        for attempt in range(max_retries):
            try:
                # Call provider
                result = await self._call_provider(
                    provider=provider,
                    prompt=prompt,
                    context=context,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )

                # Success - reset circuit breaker
                if result and not result.get("error"):
                    circuit_breaker.record_success()
                    result["provider"] = provider
                    result["attempts"] = attempt + 1
                    return result

                # Provider returned error
                logger.warning(
                    f"{provider} attempt {attempt + 1}/{max_retries} failed: "
                    f"{result.get('error', 'unknown error')}"
                )

            except Exception as e:
                logger.error(
                    f"{provider} attempt {attempt + 1}/{max_retries} exception: {e}"
                )

            # Wait before retry (exponential backoff)
            if attempt < max_retries - 1:
                wait_time = 2**attempt  # 1s, 2s, 4s
                logger.info(f"Retrying {provider} in {wait_time}s...")
                await asyncio.sleep(wait_time)

        # All retries failed - record circuit breaker failure
        circuit_breaker.record_failure()
        return None

    async def _call_provider(
        self,
        provider: str,
        prompt: str,
        context: Optional[str],
        max_tokens: int,
        temperature: float,
    ) -> Dict[str, Any]:
        """
        Call a specific AI provider.

        Args:
            provider: 'openai' or 'anthropic'
            prompt: User prompt
            context: Optional context
            max_tokens: Maximum tokens
            temperature: Temperature setting

        Returns:
            Provider response dict
        """
        if provider == "openai":
            return await self.openai_service.generate_response(
                prompt=prompt,
                context=context,
            )

        elif provider == "anthropic":
            model = self.settings.get_provider_model("anthropic")
            return await self.claude_service.generate_response(
                prompt=prompt,
                context=context,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
            )

        else:
            raise ValueError(f"Unknown provider: {provider}")

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status of all providers.

        Returns:
            Dict with provider health and circuit breaker states
        """
        return {
            "primary_provider": self.settings.AI_PROVIDER,
            "fallback_provider": self.settings.get_fallback_provider(),
            "fallback_enabled": self.settings.AI_FALLBACK_ENABLED,
            "circuit_breakers": {
                "openai": self.circuit_breakers["openai"].get_state(),
                "anthropic": self.circuit_breakers["anthropic"].get_state(),
            },
            "providers_available": {
                "openai": self.settings.has_openai(),
                "anthropic": self.settings.has_anthropic(),
            },
        }


# Global service instance
_ai_fallback_service: Optional[AIProviderFallback] = None


def get_ai_service() -> AIProviderFallback:
    """
    Get or create AI fallback service singleton.

    Returns:
        AIProviderFallback instance
    """
    global _ai_fallback_service
    if _ai_fallback_service is None:
        _ai_fallback_service = AIProviderFallback()
    return _ai_fallback_service


# Convenience function for backward compatibility
async def generate_with_fallback(
    prompt: str,
    context: Optional[str] = None,
    max_tokens: int = 1000,
    temperature: float = 0.7,
) -> Dict[str, Any]:
    """
    Generate AI response with automatic fallback.

    Convenience wrapper around AIProviderFallback.generate_response().

    Args:
        prompt: User prompt
        context: Optional context
        max_tokens: Maximum tokens
        temperature: Temperature setting

    Returns:
        AI response with metadata
    """
    service = get_ai_service()
    return await service.generate_response(
        prompt=prompt,
        context=context,
        max_tokens=max_tokens,
        temperature=temperature,
    )
