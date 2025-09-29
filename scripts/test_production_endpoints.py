#!/usr/bin/env python3
"""
AI Nurse Florence - Production Endpoint Testing Script
Tests all live endpoints to ensure Railway deployment is working correctly
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx


class ProductionTester:
    """Test production endpoints for AI Nurse Florence on Railway"""

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize the production tester

        Args:
            base_url: Base URL of the deployed application (e.g., https://your-app.railway.app)
            api_key: Optional API key for authenticated endpoints
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {}
        if api_key:
            self.headers['Authorization'] = f'Bearer {api_key}'

        self.results: List[Dict[str, Any]] = []
        self.start_time = time.time()

    async def test_endpoint(
        self,
        method: str,
        path: str,
        expected_status: int = 200,
        data: Optional[Dict] = None,
        timeout: int = 30,
        description: str = ""
    ) -> Dict[str, Any]:
        """Test a single endpoint"""
        url = f"{self.base_url}{path}"
        test_start = time.time()

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                if method.upper() == 'GET':
                    response = await client.get(url, headers=self.headers)
                elif method.upper() == 'POST':
                    response = await client.post(url, headers=self.headers, json=data)
                else:
                    raise ValueError(f"Unsupported method: {method}")

                duration = time.time() - test_start

                result = {
                    "endpoint": path,
                    "method": method.upper(),
                    "url": url,
                    "status_code": response.status_code,
                    "expected_status": expected_status,
                    "success": response.status_code == expected_status,
                    "duration_ms": round(duration * 1000, 2),
                    "description": description,
                    "timestamp": datetime.now().isoformat(),
                }

                # Try to parse JSON response
                try:
                    result["response_data"] = response.json()
                except:
                    result["response_text"] = response.text[:500]  # First 500 chars

                # Add response headers info
                result["content_type"] = response.headers.get("content-type", "unknown")
                result["response_size"] = len(response.content)

                return result

        except Exception as e:
            duration = time.time() - test_start
            return {
                "endpoint": path,
                "method": method.upper(),
                "url": url,
                "status_code": 0,
                "expected_status": expected_status,
                "success": False,
                "duration_ms": round(duration * 1000, 2),
                "description": description,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def run_health_tests(self):
        """Test health and readiness endpoints"""
        print("🏥 Testing Health Endpoints...")

        tests = [
            ("GET", "/health", 200, "Main health check"),
            ("GET", "/health/", 200, "Health check with trailing slash"),
            ("GET", "/health/ready", 200, "Readiness probe"),
            ("GET", "/health/live", 200, "Liveness probe"),
            ("GET", "/api/v1/health", 200, "API health endpoint"),
        ]

        for method, path, status, desc in tests:
            result = await self.test_endpoint(method, path, status, description=desc)
            self.results.append(result)
            self._print_result(result)

    async def run_api_tests(self):
        """Test core API endpoints with live data"""
        print("\n📚 Testing Live Data API Endpoints...")

        tests = [
            ("GET", "/api/v1/disease/lookup?q=diabetes", 200, "Disease lookup - diabetes"),
            ("GET", "/api/v1/disease/lookup?q=hypertension", 200, "Disease lookup - hypertension"),
            ("GET", "/api/v1/pubmed/search?q=heart+disease&limit=5", 200, "PubMed literature search"),
            ("GET", "/api/v1/trials/search?condition=cancer&limit=3", 200, "Clinical trials search"),
            ("GET", "/api/v1/medlineplus/summary?topic=diabetes", 200, "MedlinePlus health info"),
        ]

        for method, path, status, desc in tests:
            result = await self.test_endpoint(method, path, status, description=desc)
            self.results.append(result)
            self._print_result(result)

    async def run_ai_tests(self):
        """Test AI-powered endpoints (requires OpenAI key)"""
        print("\n🤖 Testing AI-Powered Endpoints...")

        # Test patient education generation
        education_data = {
            "topic": "diabetes management",
            "reading_level": "elementary",
            "language": "en"
        }

        tests = [
            ("POST", "/api/v1/education/generate", 200, education_data, "Patient education generation"),
        ]

        for method, path, status, data, desc in tests:
            result = await self.test_endpoint(method, path, status, data=data, description=desc)
            self.results.append(result)
            self._print_result(result)

    async def run_performance_tests(self):
        """Test performance and concurrent requests"""
        print("\n⚡ Testing Performance...")

        # Test concurrent requests to health endpoint
        concurrent_tests = []
        for i in range(5):
            concurrent_tests.append(
                self.test_endpoint("GET", "/health", 200, description=f"Concurrent health check {i+1}")
            )

        concurrent_results = await asyncio.gather(*concurrent_tests)
        for result in concurrent_results:
            self.results.append(result)

        avg_duration = sum(r["duration_ms"] for r in concurrent_results) / len(concurrent_results)
        print(f"   Average response time: {avg_duration:.2f}ms")

    def _print_result(self, result: Dict[str, Any]):
        """Print test result in a readable format"""
        status_icon = "✅" if result["success"] else "❌"
        duration = result["duration_ms"]
        endpoint = result["endpoint"]
        description = result["description"]

        print(f"   {status_icon} {endpoint} ({duration}ms) - {description}")

        if not result["success"]:
            if "error" in result:
                print(f"      Error: {result['error']}")
            else:
                print(f"      Expected {result['expected_status']}, got {result['status_code']}")

    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive test report"""
        total_duration = time.time() - self.start_time
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - successful_tests

        # Calculate average response time
        response_times = [r["duration_ms"] for r in self.results if r["success"]]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0

        # Group results by success/failure
        successful_results = [r for r in self.results if r["success"]]
        failed_results = [r for r in self.results if not r["success"]]

        report = {
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": round((successful_tests / total_tests) * 100, 2) if total_tests > 0 else 0,
                "total_duration_seconds": round(total_duration, 2),
                "average_response_time_ms": round(avg_response_time, 2),
                "base_url": self.base_url,
                "timestamp": datetime.now().isoformat(),
            },
            "successful_endpoints": successful_results,
            "failed_endpoints": failed_results,
            "performance_metrics": {
                "fastest_response_ms": min(response_times) if response_times else 0,
                "slowest_response_ms": max(response_times) if response_times else 0,
                "median_response_ms": sorted(response_times)[len(response_times)//2] if response_times else 0,
            }
        }

        return report

    def print_summary(self, report: Dict[str, Any]):
        """Print a summary of test results"""
        summary = report["summary"]

        print("\n" + "="*60)
        print("🏥 AI NURSE FLORENCE - PRODUCTION TEST SUMMARY")
        print("="*60)
        print(f"🌐 Base URL: {summary['base_url']}")
        print(f"⏱️  Total Duration: {summary['total_duration_seconds']}s")
        print(f"📊 Success Rate: {summary['success_rate']}% ({summary['successful_tests']}/{summary['total_tests']})")
        print(f"⚡ Average Response Time: {summary['average_response_time_ms']}ms")

        if summary["failed_tests"] > 0:
            print(f"\n❌ Failed Tests ({summary['failed_tests']}):")
            for failed in report["failed_endpoints"]:
                print(f"   • {failed['endpoint']} - {failed.get('error', 'Status code mismatch')}")
        else:
            print("\n✅ All tests passed!")

        perf = report["performance_metrics"]
        print(f"\n📈 Performance Metrics:")
        print(f"   Fastest: {perf['fastest_response_ms']}ms")
        print(f"   Slowest: {perf['slowest_response_ms']}ms")
        print(f"   Median: {perf['median_response_ms']}ms")

        print("\n🚀 Production deployment is ready!" if summary["success_rate"] >= 80 else
              "\n⚠️  Some issues detected - check failed endpoints")


async def main():
    """Main test runner"""
    # Get configuration from environment or command line
    base_url = os.getenv("TEST_BASE_URL") or sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    api_key = os.getenv("API_BEARER") or (sys.argv[2] if len(sys.argv) > 2 else None)

    print("🏥 AI Nurse Florence - Production Endpoint Testing")
    print(f"🌐 Testing: {base_url}")
    print(f"🔑 API Key: {'✅ Configured' if api_key else '❌ Not provided'}")
    print("-" * 60)

    tester = ProductionTester(base_url, api_key)

    # Run all test suites
    await tester.run_health_tests()
    await tester.run_api_tests()

    if api_key:
        await tester.run_ai_tests()
    else:
        print("\n🔑 Skipping AI tests (no API key provided)")

    await tester.run_performance_tests()

    # Generate and print report
    report = tester.generate_report()
    tester.print_summary(report)

    # Save detailed report to file
    with open("production_test_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Detailed report saved to: production_test_report.json")

    # Exit with error code if tests failed
    if report["summary"]["success_rate"] < 80:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())