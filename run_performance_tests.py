#!/usr/bin/env python3
"""
Performance testing suite for AI Nurse Florence application.

This module provides comprehensive performance testing for medical AI services,
including API endpoints, caching performance, database operations, and external
service integration benchmarks.

Usage:
    python run_performance_tests.py --test-type all
    python run_performance_tests.py --test-type api --endpoints /api/v1/disease-info
    python run_performance_tests.py --test-type cache --concurrent-users 50
"""

import asyncio
import time
import statistics
import argparse
import sys
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import logging

# Conditional imports for graceful degradation
try:
    import httpx
    _has_httpx = True
except ImportError:
    _has_httpx = False
    httpx = None  # type: ignore

try:
    from src.utils.redis_cache import get_redis_client
    _has_redis = True
except ImportError:
    _has_redis = False
    get_redis_client = None  # type: ignore

try:
    import psutil  # type: ignore
    _has_psutil = True
except ImportError:
    _has_psutil = False
    psutil = None  # type: ignore

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics for test results."""
    test_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p50_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    error_rate: float
    total_duration: float
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None


@dataclass
class TestConfig:
    """Configuration for performance tests."""
    base_url: str = "http://localhost:8000"
    concurrent_users: int = 10
    requests_per_user: int = 10
    timeout_seconds: int = 30
    test_endpoints: Optional[List[str]] = None
    medical_test_queries: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.test_endpoints is None:
            self.test_endpoints = [
                "/api/v1/health",
                "/api/v1/disease-info?q=hypertension",
                "/api/v1/drug-info?q=aspirin",
                "/api/v1/pubmed-search?q=diabetes",
                "/api/v1/clinical-trials?q=heart+disease"
            ]
        
        if self.medical_test_queries is None:
            self.medical_test_queries = [
                "hypertension",
                "diabetes mellitus type 2", 
                "acute myocardial infarction",
                "pneumonia",
                "sepsis",
                "heart failure",
                "stroke",
                "chronic kidney disease",
                "COPD",
                "depression"
            ]


class PerformanceTester:
    """Main performance testing class."""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.session_results: List[Dict[str, Any]] = []
        
    async def run_api_performance_test(self) -> PerformanceMetrics:
        """Run comprehensive API performance tests."""
        if not _has_httpx or httpx is None:
            raise RuntimeError("httpx not available for API testing")
        
        logger.info(f"Starting API performance test with {self.config.concurrent_users} concurrent users")
        
        all_response_times = []
        successful_requests = 0
        failed_requests = 0
        start_time = time.time()
        
        # Monitor system resources if available
        initial_memory = self._get_memory_usage()
        initial_cpu = self._get_cpu_usage()
        
        async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
            # Create tasks for concurrent users
            tasks = []
            for user_id in range(self.config.concurrent_users):
                task = self._simulate_user_requests(client, user_id)
                tasks.append(task)
            
            # Execute all user simulations concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for result in results:
                if isinstance(result, Exception):
                    failed_requests += self.config.requests_per_user
                    logger.error(f"User simulation failed: {result}")
                else:
                    user_times, user_successes, user_failures = result
                    all_response_times.extend(user_times)
                    successful_requests += user_successes
                    failed_requests += user_failures
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Calculate final system resource usage
        final_memory = self._get_memory_usage()
        final_cpu = self._get_cpu_usage()
        
        return self._calculate_metrics(
            "API Performance Test",
            all_response_times,
            successful_requests,
            failed_requests,
            total_duration,
            final_memory,
            final_cpu
        )
    
    async def _simulate_user_requests(self, client, user_id: int) -> Tuple[List[float], int, int]:
        """Simulate requests for a single user."""
        response_times = []
        successful = 0
        failed = 0
        
        test_endpoints = self.config.test_endpoints or []
        if not test_endpoints:
            return response_times, successful, failed
        
        for request_num in range(self.config.requests_per_user):
            # Rotate through test endpoints
            endpoint = test_endpoints[request_num % len(test_endpoints)]
            url = f"{self.config.base_url}{endpoint}"
            
            try:
                start_time = time.time()
                response = await client.get(url)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                response_times.append(response_time)
                
                if response.status_code == 200:
                    successful += 1
                else:
                    failed += 1
                    logger.warning(f"User {user_id}: HTTP {response.status_code} for {url}")
                    
            except Exception as e:
                failed += 1
                # Add timeout value for failed requests
                response_times.append(self.config.timeout_seconds * 1000)
                logger.error(f"User {user_id}: Request failed: {e}")
        
        return response_times, successful, failed
    
    async def run_cache_performance_test(self) -> PerformanceMetrics:
        """Run Redis cache performance tests."""
        if not _has_redis or get_redis_client is None:
            raise RuntimeError("Redis not available for cache testing")
        
        logger.info("Starting cache performance test")
        
        redis_client = await get_redis_client()
        if redis_client is None:
            raise RuntimeError("Could not connect to Redis")
        
        all_response_times = []
        successful_requests = 0
        failed_requests = 0
        start_time = time.time()
        
        # Test cache operations with medical data patterns
        tasks = []
        for user_id in range(self.config.concurrent_users):
            task = self._simulate_cache_operations(redis_client, user_id)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for result in results:
            if isinstance(result, Exception):
                failed_requests += self.config.requests_per_user
                logger.error(f"Cache simulation failed: {result}")
            else:
                user_times, user_successes, user_failures = result
                all_response_times.extend(user_times)
                successful_requests += user_successes
                failed_requests += user_failures
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        return self._calculate_metrics(
            "Cache Performance Test",
            all_response_times,
            successful_requests,
            failed_requests,
            total_duration
        )
    
    async def _simulate_cache_operations(self, redis_client, user_id: int) -> Tuple[List[float], int, int]:
        """Simulate cache operations for a single user."""
        response_times = []
        successful = 0
        failed = 0
        
        medical_queries = self.config.medical_test_queries or ["default_query"]
        
        for request_num in range(self.config.requests_per_user):
            query = medical_queries[request_num % len(medical_queries)]
            cache_key = f"medical_test:{user_id}:{request_num}:{query}"
            
            # Simulate medical data caching pattern
            medical_data = {
                "query": query,
                "results": f"Medical information for {query}",
                "timestamp": time.time(),
                "user_id": user_id,
                "request_id": request_num
            }
            
            try:
                # Test SET operation
                start_time = time.time()
                await redis_client.set(cache_key, json.dumps(medical_data), ex=300)
                set_time = time.time()
                
                # Test GET operation  
                cached_result = await redis_client.get(cache_key)
                get_time = time.time()
                
                # Test DELETE operation
                await redis_client.delete(cache_key)
                delete_time = time.time()
                
                total_time = (delete_time - start_time) * 1000
                response_times.append(total_time)
                
                if cached_result:
                    successful += 1
                else:
                    failed += 1
                    
            except Exception as e:
                failed += 1
                response_times.append(1000)  # 1 second timeout for failed ops
                logger.error(f"Cache operation failed for user {user_id}: {e}")
        
        return response_times, successful, failed
    
    def run_medical_query_performance_test(self) -> PerformanceMetrics:
        """Run performance tests for medical query processing."""
        logger.info("Starting medical query performance test")
        
        all_response_times = []
        successful_requests = 0
        failed_requests = 0
        start_time = time.time()
        
        # Simulate medical query processing without external dependencies
        for query in self.config.medical_test_queries * self.config.concurrent_users:
            try:
                process_start = time.time()
                
                # Simulate medical query processing
                processed_query = self._process_medical_query(query)
                
                process_end = time.time()
                response_time = (process_end - process_start) * 1000
                all_response_times.append(response_time)
                
                if processed_query:
                    successful_requests += 1
                else:
                    failed_requests += 1
                    
            except Exception as e:
                failed_requests += 1
                all_response_times.append(100)  # Default 100ms for failed processing
                logger.error(f"Medical query processing failed: {e}")
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        return self._calculate_metrics(
            "Medical Query Performance Test",
            all_response_times,
            successful_requests,
            failed_requests,
            total_duration
        )
    
    def _process_medical_query(self, query: str) -> str:
        """Simulate medical query processing logic."""
        # Simulate processing time based on query complexity
        processing_time = len(query) * 0.001  # 1ms per character
        time.sleep(processing_time)
        
        # Return processed query with medical context
        return f"Processed medical query: {query.lower().strip()}"
    
    def _calculate_metrics(
        self,
        test_name: str,
        response_times: List[float],
        successful: int,
        failed: int,
        duration: float,
        memory_mb: Optional[float] = None,
        cpu_percent: Optional[float] = None
    ) -> PerformanceMetrics:
        """Calculate performance metrics from test results."""
        total_requests = successful + failed
        
        if not response_times:
            return PerformanceMetrics(
                test_name=test_name,
                total_requests=total_requests,
                successful_requests=successful,
                failed_requests=failed,
                avg_response_time=0,
                min_response_time=0,
                max_response_time=0,
                p50_response_time=0,
                p95_response_time=0,
                p99_response_time=0,
                requests_per_second=0,
                error_rate=100 if total_requests > 0 else 0,
                total_duration=duration,
                memory_usage_mb=memory_mb,
                cpu_usage_percent=cpu_percent
            )
        
        sorted_times = sorted(response_times)
        
        return PerformanceMetrics(
            test_name=test_name,
            total_requests=total_requests,
            successful_requests=successful,
            failed_requests=failed,
            avg_response_time=statistics.mean(response_times),
            min_response_time=min(response_times),
            max_response_time=max(response_times),
            p50_response_time=statistics.median(response_times),
            p95_response_time=sorted_times[int(0.95 * len(sorted_times))],
            p99_response_time=sorted_times[int(0.99 * len(sorted_times))],
            requests_per_second=total_requests / duration if duration > 0 else 0,
            error_rate=(failed / total_requests * 100) if total_requests > 0 else 0,
            total_duration=duration,
            memory_usage_mb=memory_mb,
            cpu_usage_percent=cpu_percent
        )
    
    def _get_memory_usage(self) -> Optional[float]:
        """Get current memory usage in MB."""
        if not _has_psutil or psutil is None:
            return None
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except Exception:
            return None
    
    def _get_cpu_usage(self) -> Optional[float]:
        """Get current CPU usage percentage."""
        if not _has_psutil or psutil is None:
            return None
        try:
            return psutil.cpu_percent(interval=1)
        except Exception:
            return None
    
    def print_results(self, metrics: PerformanceMetrics):
        """Print formatted performance test results."""
        print(f"\n{'='*60}")
        print(f"Performance Test Results: {metrics.test_name}")
        print(f"{'='*60}")
        print(f"Total Requests:        {metrics.total_requests}")
        print(f"Successful Requests:   {metrics.successful_requests}")
        print(f"Failed Requests:       {metrics.failed_requests}")
        print(f"Error Rate:            {metrics.error_rate:.2f}%")
        print(f"Total Duration:        {metrics.total_duration:.2f}s")
        print(f"Requests/Second:       {metrics.requests_per_second:.2f}")
        print(f"\nResponse Times (ms):")
        print(f"  Average:             {metrics.avg_response_time:.2f}")
        print(f"  Minimum:             {metrics.min_response_time:.2f}")
        print(f"  Maximum:             {metrics.max_response_time:.2f}")
        print(f"  50th Percentile:     {metrics.p50_response_time:.2f}")
        print(f"  95th Percentile:     {metrics.p95_response_time:.2f}")
        print(f"  99th Percentile:     {metrics.p99_response_time:.2f}")
        
        if metrics.memory_usage_mb:
            print(f"\nSystem Resources:")
            print(f"  Memory Usage:        {metrics.memory_usage_mb:.2f} MB")
        if metrics.cpu_usage_percent:
            print(f"  CPU Usage:           {metrics.cpu_usage_percent:.2f}%")
        print(f"{'='*60}")


async def main():
    """Main function to run performance tests."""
    parser = argparse.ArgumentParser(description="AI Nurse Florence Performance Testing Suite")
    parser.add_argument("--test-type", 
                       choices=["all", "api", "cache", "medical-query"],
                       default="all",
                       help="Type of performance test to run")
    parser.add_argument("--base-url", 
                       default="http://localhost:8000",
                       help="Base URL for API testing")
    parser.add_argument("--concurrent-users", 
                       type=int, 
                       default=10,
                       help="Number of concurrent users to simulate")
    parser.add_argument("--requests-per-user", 
                       type=int, 
                       default=10,
                       help="Number of requests per user")
    parser.add_argument("--timeout", 
                       type=int, 
                       default=30,
                       help="Request timeout in seconds")
    parser.add_argument("--endpoints", 
                       nargs="+",
                       help="Specific endpoints to test")
    
    args = parser.parse_args()
    
    # Create test configuration
    config = TestConfig(
        base_url=args.base_url,
        concurrent_users=args.concurrent_users,
        requests_per_user=args.requests_per_user,
        timeout_seconds=args.timeout,
        test_endpoints=args.endpoints
    )
    
    tester = PerformanceTester(config)
    
    try:
        if args.test_type in ["all", "api"]:
            print("🔍 Running API Performance Tests...")
            api_metrics = await tester.run_api_performance_test()
            tester.print_results(api_metrics)
            
        if args.test_type in ["all", "cache"]:
            print("\n📦 Running Cache Performance Tests...")
            cache_metrics = await tester.run_cache_performance_test()
            tester.print_results(cache_metrics)
            
        if args.test_type in ["all", "medical-query"]:
            print("\n🏥 Running Medical Query Performance Tests...")
            query_metrics = tester.run_medical_query_performance_test()
            tester.print_results(query_metrics)
            
    except RuntimeError as e:
        logger.error(f"Performance test failed: {e}")
        print(f"\n❌ Test failed: {e}")
        print("Ensure the required dependencies are installed and services are running.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Performance testing interrupted by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error during performance testing: {e}")
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("🚀 AI Nurse Florence Performance Testing Suite")
    print("=" * 50)
    asyncio.run(main())
