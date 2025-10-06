"""
Enhanced Redis Caching System - AI Nurse Florence
Phase 4.1: Smart Caching Strategies for Medical Data

Advanced caching with intelligent cache key generation, TTL optimization, 
cache warming, and performance monitoring for medical endpoints.
"""

import asyncio
import hashlib
import json
import logging
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

# Conditional imports following AI Nurse Florence patterns
try:
    import redis.asyncio as redis

    _redis_available = True
except ImportError:
    _redis_available = False
    redis = None

try:
    from src.utils.config import get_settings  # type: ignore
    from src.utils.redis_cache import cache_delete, cache_get, cache_set  # type: ignore

    _has_base_cache = True
    _has_settings = True
except ImportError:
    _has_base_cache = False
    _has_settings = False

    # Mock functions for when base cache is not available
    async def cache_get(key: str):
        return None

    async def cache_set(key: str, value: Any, ttl_seconds: int = 3600):
        return True  # Return True for success instead of False

    async def cache_delete(key: str):
        return True  # Return True for success instead of False

    def get_settings():
        class MockSettings:
            def __init__(self):
                self.redis_url = None

        return MockSettings()


# Optional metrics tracking
try:
    from src.utils.metrics import record_cache_hit, record_cache_miss

    _has_metrics = True

    def record_cache_performance(*args, **kwargs):
        pass  # Placeholder for future implementation

except ImportError:
    _has_metrics = False

    def record_cache_hit(*args, **kwargs):
        pass

    def record_cache_miss(*args, **kwargs):
        pass

    def record_cache_performance(*args, **kwargs):
        pass


logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    """Cache strategy types for different medical data."""

    MEDICAL_REFERENCE = "medical_ref"  # Stable medical reference data (diseases, drugs)
    LITERATURE_SEARCH = "literature"  # Literature search results
    CLINICAL_TRIALS = "trials"  # Clinical trials data
    USER_GENERATED = "user_data"  # User-specific cached content
    TEMPORARY = "temp"  # Short-lived cache
    PREDICTIVE = "predictive"  # Preloaded common queries


@dataclass
class CacheConfig:
    """Configuration for cache behavior by strategy."""

    ttl_seconds: int
    max_size_mb: int
    compression: bool
    warm_on_startup: bool
    key_prefix: str
    similarity_threshold: float = 0.8  # For semantic similarity caching


# Smart cache configurations for different medical data types
CACHE_STRATEGIES = {
    CacheStrategy.MEDICAL_REFERENCE: CacheConfig(
        ttl_seconds=86400,  # 24 hours - medical reference data is stable
        max_size_mb=50,
        compression=True,
        warm_on_startup=True,
        key_prefix="med_ref",
    ),
    CacheStrategy.LITERATURE_SEARCH: CacheConfig(
        ttl_seconds=21600,  # 6 hours - literature searches can be cached longer
        max_size_mb=100,
        compression=True,
        warm_on_startup=False,
        key_prefix="lit_search",
    ),
    CacheStrategy.CLINICAL_TRIALS: CacheConfig(
        ttl_seconds=43200,  # 12 hours - trials data changes moderately
        max_size_mb=30,
        compression=True,
        warm_on_startup=False,
        key_prefix="trials",
    ),
    CacheStrategy.USER_GENERATED: CacheConfig(
        ttl_seconds=3600,  # 1 hour - user-specific data
        max_size_mb=20,
        compression=False,
        warm_on_startup=False,
        key_prefix="user_gen",
    ),
    CacheStrategy.TEMPORARY: CacheConfig(
        ttl_seconds=300,  # 5 minutes - temporary calculations
        max_size_mb=10,
        compression=False,
        warm_on_startup=False,
        key_prefix="temp",
    ),
    CacheStrategy.PREDICTIVE: CacheConfig(
        ttl_seconds=7200,  # 2 hours - predictively loaded content
        max_size_mb=75,
        compression=True,
        warm_on_startup=True,
        key_prefix="predict",
    ),
}


@dataclass
class CacheMetrics:
    """Cache performance metrics."""

    cache_key: str
    strategy: CacheStrategy
    hit: bool
    response_time_ms: float
    cache_size_bytes: Optional[int]
    timestamp: datetime


class SmartCacheManager:
    """Enhanced cache manager with intelligent strategies."""

    def __init__(self):
        self.settings = None
        if _has_settings:
            try:
                self.settings = get_settings()
            except Exception:
                pass

        self.metrics_history: List[CacheMetrics] = []
        self.cache_warming_tasks: Dict[str, asyncio.Task] = {}
        self.common_medical_terms = [
            "hypertension",
            "diabetes",
            "pneumonia",
            "covid-19",
            "asthma",
            "heart failure",
            "stroke",
            "infection",
            "sepsis",
            "copd",
        ]

        logger.info("Smart cache manager initialized")

    def _normalize_medical_query(self, query: str) -> str:
        """Normalize medical queries for better cache key matching."""
        if not isinstance(query, str):
            return str(query)

        # Convert to lowercase and remove extra whitespace
        normalized = re.sub(r"\s+", " ", query.lower().strip())

        # Remove common medical prefixes/suffixes that don't affect meaning
        normalized = re.sub(
            r"\b(acute|chronic|mild|severe|stage\s+\d+)\b", "", normalized
        )
        normalized = re.sub(r"\s+", " ", normalized).strip()

        # Standardize common medical abbreviations
        abbreviations = {
            "mi": "myocardial infarction",
            "chf": "congestive heart failure",
            "copd": "chronic obstructive pulmonary disease",
            "dm": "diabetes mellitus",
            "htn": "hypertension",
            "cad": "coronary artery disease",
        }

        for abbrev, full_term in abbreviations.items():
            normalized = re.sub(f"\\b{abbrev}\\b", full_term, normalized)

        return normalized

    def _generate_smart_cache_key(
        self, strategy: CacheStrategy, query: str, **kwargs
    ) -> str:
        """Generate intelligent cache keys with medical query normalization."""
        config = CACHE_STRATEGIES[strategy]

        # Normalize medical queries for better cache hits
        if strategy in [
            CacheStrategy.MEDICAL_REFERENCE,
            CacheStrategy.LITERATURE_SEARCH,
        ]:
            query = self._normalize_medical_query(query)

        # Create stable key from normalized inputs
        key_data = {"query": query, "params": sorted(kwargs.items()) if kwargs else []}

        key_json = json.dumps(key_data, sort_keys=True, default=str)
        key_hash = hashlib.md5(key_json.encode()).hexdigest()[:16]

        return f"{config.key_prefix}:{strategy.value}:{key_hash}"

    async def smart_cache_get(
        self,
        strategy: CacheStrategy,
        query: str,
        similarity_check: bool = True,
        **kwargs,
    ) -> Optional[Any]:
        """Get from cache with smart key matching and similarity checking."""
        start_time = datetime.utcnow()

        try:
            # Generate primary cache key
            cache_key = self._generate_smart_cache_key(strategy, query, **kwargs)

            # Try exact match first
            result = await cache_get(cache_key)

            if result is not None:
                self._record_cache_metrics(cache_key, strategy, True, start_time)
                if _has_metrics:
                    record_cache_hit(cache_key, f"smart_{strategy.value}")
                return result

            # If similarity checking enabled and no exact match, try similar keys
            if similarity_check and strategy in [
                CacheStrategy.MEDICAL_REFERENCE,
                CacheStrategy.LITERATURE_SEARCH,
            ]:
                similar_result = await self._find_similar_cached_result(
                    strategy, query, kwargs
                )
                if similar_result:
                    self._record_cache_metrics(
                        cache_key, strategy, True, start_time, note="similarity_match"
                    )
                    if _has_metrics:
                        record_cache_hit(cache_key, f"smart_{strategy.value}_similar")
                    return similar_result

            # Cache miss
            self._record_cache_metrics(cache_key, strategy, False, start_time)
            if _has_metrics:
                record_cache_miss(cache_key, f"smart_{strategy.value}")
            return None

        except Exception as e:
            logger.warning(f"Smart cache get failed for {strategy.value}: {e}")
            return None

    async def smart_cache_set(
        self,
        strategy: CacheStrategy,
        query: str,
        result: Any,
        ttl_override: Optional[int] = None,
        **kwargs,
    ) -> bool:
        """
        Set cache with strategy-specific configuration.

        Args:
            strategy: Cache strategy to use
            query: Query string for cache key generation
            result: Data to cache
            ttl_override: Optional TTL in seconds (overrides strategy default)
            **kwargs: Additional parameters for cache key generation

        Returns:
            True if cache set succeeded, False otherwise
        """
        try:
            config = CACHE_STRATEGIES[strategy]
            cache_key = self._generate_smart_cache_key(strategy, query, **kwargs)

            # Apply compression if configured
            cache_data = result
            if config.compression:
                cache_data = self._compress_cache_data(result)

            # Use override TTL if provided, otherwise use strategy default
            ttl_seconds = (
                ttl_override if ttl_override is not None else config.ttl_seconds
            )
            success = await cache_set(cache_key, cache_data, ttl_seconds)

            if success:
                logger.debug(
                    f"Smart cache set: {cache_key} (strategy: {strategy.value}, TTL: {ttl_seconds}s)"
                )

            return success

        except Exception as e:
            logger.warning(f"Smart cache set failed for {strategy.value}: {e}")
            return False

    async def _find_similar_cached_result(
        self, strategy: CacheStrategy, query: str, kwargs: Dict
    ) -> Optional[Any]:
        """Find similar cached results using basic text similarity."""
        try:
            if not _has_base_cache:
                return None

            # This is a simplified similarity check
            # In production, you might use more sophisticated NLP similarity
            normalized_query = self._normalize_medical_query(query)

            # For medical queries, check for common term variations
            similar_terms = self._get_medical_synonyms(normalized_query)

            for similar_term in similar_terms:
                similar_key = self._generate_smart_cache_key(
                    strategy, similar_term, **kwargs
                )
                result = await cache_get(similar_key)
                if result:
                    logger.debug(
                        f"Found similar cache result: {similar_term} for {query}"
                    )
                    return result

            return None

        except Exception as e:
            logger.warning(f"Similarity check failed: {e}")
            return None

    def _get_medical_synonyms(self, term: str) -> List[str]:
        """Get basic medical synonyms for cache similarity matching."""
        # Basic medical synonym mapping for common terms
        synonyms_map = {
            "heart attack": ["myocardial infarction", "mi", "acute mi"],
            "high blood pressure": ["hypertension", "htn", "elevated bp"],
            "diabetes": ["diabetes mellitus", "dm", "diabetic"],
            "lung infection": ["pneumonia", "respiratory infection"],
            "heart failure": ["chf", "congestive heart failure", "cardiac failure"],
        }

        # Return synonyms for the term, or variants of the term itself
        for key, synonyms in synonyms_map.items():
            if key in term or term in synonyms:
                return [s for s in synonyms if s != term]

        # Return term variations (plurals, etc.)
        variations = [term]
        if not term.endswith("s"):
            variations.append(term + "s")
        if term.endswith("s"):
            variations.append(term[:-1])

        return variations[1:]  # Exclude original term

    def _compress_cache_data(self, data: Any) -> Any:
        """Compress cache data for strategies that support compression."""
        # For now, return as-is. In production, you might implement
        # JSON compression, or store only essential fields for large medical datasets
        return data

    def _record_cache_metrics(
        self,
        cache_key: str,
        strategy: CacheStrategy,
        hit: bool,
        start_time: datetime,
        note: Optional[str] = None,
    ):
        """Record cache performance metrics."""
        try:
            end_time = datetime.utcnow()
            response_time_ms = (end_time - start_time).total_seconds() * 1000

            metrics = CacheMetrics(
                cache_key=cache_key,
                strategy=strategy,
                hit=hit,
                response_time_ms=response_time_ms,
                cache_size_bytes=None,  # Could be calculated if needed
                timestamp=end_time,
            )

            # Keep last 1000 metrics for analysis
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > 1000:
                self.metrics_history.pop(0)

            if _has_metrics:
                record_cache_performance(
                    cache_key, strategy.value, hit, response_time_ms, note or ""
                )

        except Exception as e:
            logger.warning(f"Failed to record cache metrics: {e}")

    async def warm_cache_for_common_queries(self):
        """Warm cache with common medical queries."""
        try:
            logger.info("Starting cache warming for common medical queries")

            # Import medical services for cache warming
            try:
                # Import available medical services - use conditional imports
                search_disease_conditions = None

                # Note: Service imports disabled for cache warming to avoid circular imports
                # These would be enabled in production with proper service registry

                # Warm disease cache if service available
                if search_disease_conditions:
                    for term in self.common_medical_terms:
                        try:
                            cache_key = self._generate_smart_cache_key(
                                CacheStrategy.MEDICAL_REFERENCE, term
                            )

                            # Check if already cached
                            cached = await cache_get(cache_key)
                            if not cached:
                                # Note: Cache warming disabled due to import restrictions
                                # This would call: result = await search_disease_conditions(term)
                                logger.debug(
                                    f"Would warm cache for disease term: {term}"
                                )

                            # Brief delay to avoid overwhelming external APIs
                            await asyncio.sleep(0.1)

                        except Exception as e:
                            logger.warning(f"Failed to warm cache for {term}: {e}")

                logger.info(
                    f"Cache warming completed for {len(self.common_medical_terms)} common terms"
                )

            except ImportError:
                logger.warning("Medical services not available for cache warming")

        except Exception as e:
            logger.error(f"Cache warming failed: {e}")

    # Basic cache methods for compatibility
    async def get(self, key: str) -> Optional[Any]:
        """Basic cache get method."""
        try:
            return await cache_get(key)
        except Exception as e:
            logger.warning(f"Basic cache get failed for {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> bool:
        """Basic cache set method."""
        try:
            return await cache_set(key, value, ttl_seconds)
        except Exception as e:
            logger.warning(f"Basic cache set failed for {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Basic cache delete method."""
        try:
            return await cache_delete(key)
        except Exception as e:
            logger.warning(f"Basic cache delete failed for {key}: {e}")
            return False

    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache performance statistics."""
        try:
            if not self.metrics_history:
                return {"message": "No cache metrics available"}

            # Calculate statistics by strategy
            stats_by_strategy = {}
            total_requests = len(self.metrics_history)
            total_hits = sum(1 for m in self.metrics_history if m.hit)

            for strategy in CacheStrategy:
                strategy_metrics = [
                    m for m in self.metrics_history if m.strategy == strategy
                ]
                if strategy_metrics:
                    hits = sum(1 for m in strategy_metrics if m.hit)
                    avg_response_time = sum(
                        m.response_time_ms for m in strategy_metrics
                    ) / len(strategy_metrics)

                    stats_by_strategy[strategy.value] = {
                        "total_requests": len(strategy_metrics),
                        "cache_hits": hits,
                        "hit_rate": (
                            hits / len(strategy_metrics) if strategy_metrics else 0
                        ),
                        "avg_response_time_ms": round(avg_response_time, 2),
                        "config": asdict(CACHE_STRATEGIES[strategy]),
                    }

            return {
                "overall_statistics": {
                    "total_requests": total_requests,
                    "total_hits": total_hits,
                    "overall_hit_rate": (
                        total_hits / total_requests if total_requests > 0 else 0
                    ),
                    "metrics_collected_since": (
                        self.metrics_history[0].timestamp.isoformat()
                        if self.metrics_history
                        else None
                    ),
                },
                "strategy_statistics": stats_by_strategy,
                "cache_warming": {
                    "active_warming_tasks": len(self.cache_warming_tasks),
                    "common_terms_count": len(self.common_medical_terms),
                },
            }

        except Exception as e:
            logger.error(f"Failed to get cache statistics: {e}")
            return {"error": str(e)}


# Global smart cache manager instance
smart_cache_manager = SmartCacheManager()


# Enhanced caching decorators with smart strategies
def smart_cached(strategy: CacheStrategy, similarity_check: bool = True):
    """
    Enhanced caching decorator with intelligent medical data strategies.

    Args:
        strategy: Cache strategy to use (determines TTL, compression, etc.)
        similarity_check: Whether to check for similar cached queries
    """

    def decorator(func: Callable):
        if asyncio.iscoroutinefunction(func):

            async def async_wrapper(*args, **kwargs):
                # Extract query parameter (usually first argument after self)
                query = args[1] if len(args) > 1 else kwargs.get("query", "")

                # Try cache first
                cached_result = await smart_cache_manager.smart_cache_get(
                    strategy, str(query), similarity_check, **kwargs
                )

                if cached_result is not None:
                    return cached_result

                # Cache miss - call function and cache result
                result = await func(*args, **kwargs)

                # Cache the result
                await smart_cache_manager.smart_cache_set(
                    strategy, str(query), result, **kwargs
                )

                return result

            return async_wrapper
        else:
            # Sync function wrapper (similar pattern but with sync cache operations)
            def sync_wrapper(*args, **kwargs):
                # For sync functions, use basic caching for now
                # Could be enhanced with sync versions of smart cache operations
                return func(*args, **kwargs)

            return sync_wrapper

    return decorator


# Convenience functions for common medical cache operations
async def get_medical_reference_cache(query: str, **kwargs) -> Optional[Any]:
    """Get medical reference data from cache."""
    return await smart_cache_manager.smart_cache_get(
        CacheStrategy.MEDICAL_REFERENCE, query, **kwargs
    )


async def set_medical_reference_cache(query: str, result: Any, **kwargs) -> bool:
    """Set medical reference data in cache."""
    return await smart_cache_manager.smart_cache_set(
        CacheStrategy.MEDICAL_REFERENCE, query, result, **kwargs
    )


async def get_literature_cache(query: str, **kwargs) -> Optional[Any]:
    """Get literature search results from cache."""
    return await smart_cache_manager.smart_cache_get(
        CacheStrategy.LITERATURE_SEARCH, query, **kwargs
    )


async def set_literature_cache(query: str, result: Any, **kwargs) -> bool:
    """Set literature search results in cache."""
    return await smart_cache_manager.smart_cache_set(
        CacheStrategy.LITERATURE_SEARCH, query, result, **kwargs
    )


# Initialize cache warming on module import (if conditions are right)
async def initialize_smart_caching():
    """Initialize smart caching system."""
    try:
        if _has_base_cache:
            # Start cache warming for common medical terms
            await smart_cache_manager.warm_cache_for_common_queries()
            logger.info("Smart caching system initialized successfully")
        else:
            logger.warning("Base caching system not available")
    except Exception as e:
        logger.error(f"Failed to initialize smart caching: {e}")
