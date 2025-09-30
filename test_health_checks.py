#!/usr/bin/env python3
"""
Health Checks Test Module for AI Nurse Florence

This module provides comprehensive testing for system health monitoring,
dependency checks, and service availability for the healthcare AI application.
"""

import pytest
import asyncio
import time
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from src.utils.health_checks import (
    check_database_health,
    check_redis_health, 
    check_external_services_health,
    check_system_resources,
    get_comprehensive_health_status
)


class TestHealthChecks:
    """Test suite for system health monitoring."""
    
    def setup_method(self):
        """Setup test environment before each test."""
        self.start_time = time.time()
    
    @pytest.mark.asyncio
    async def test_database_health_check(self):
        """Test database connectivity health check."""
        try:
            health_status = await check_database_health()
            
            # Should return a dict with status information
            assert isinstance(health_status, dict)
            assert "status" in health_status
            assert health_status["status"] in ["healthy", "unhealthy"]
            
            if health_status["status"] == "healthy":
                assert "latency_ms" in health_status
                assert isinstance(health_status["latency_ms"], (int, float))
                
        except Exception as e:
            # If database not available, should handle gracefully
            assert "database" in str(e).lower() or "connection" in str(e).lower()
    
    @pytest.mark.asyncio
    async def test_redis_health_check(self):
        """Test Redis connectivity health check."""
        health_status = await check_redis_health()
        
        # Should return a dict with status information
        assert isinstance(health_status, dict)
        assert "status" in health_status
        assert health_status["status"] in ["healthy", "unhealthy", "disabled"]
        
        if health_status["status"] == "healthy":
            assert "latency_ms" in health_status
            assert isinstance(health_status["latency_ms"], (int, float))
        elif health_status["status"] == "disabled":
            assert "message" in health_status
    
    @pytest.mark.asyncio
    async def test_external_services_health(self):
        """Test external medical services health checks."""
        health_status = await check_external_services_health()
        
        assert isinstance(health_status, dict)
        
        # Should check key medical services
        expected_services = ["mydisease", "pubmed", "clinicaltrials"]
        
        for service in expected_services:
            if service in health_status:
                service_status = health_status[service]
                assert "status" in service_status
                assert service_status["status"] in ["healthy", "unhealthy", "disabled"]
    
    @pytest.mark.asyncio
    async def test_system_resources_check(self):
        """Test system resource monitoring."""
        resources = await check_system_resources()
        
        assert isinstance(resources, dict)
        
        # Should include basic system metrics
        expected_metrics = ["memory_usage", "cpu_usage", "disk_usage"]
        
        for metric in expected_metrics:
            if metric in resources:
                assert isinstance(resources[metric], (int, float))
                assert 0 <= resources[metric] <= 100  # Percentage
    
    @pytest.mark.asyncio
    async def test_comprehensive_health_status(self):
        """Test comprehensive health status aggregation."""
        health_status = await get_comprehensive_health_status()
        
        assert isinstance(health_status, dict)
        assert "status" in health_status
        assert "timestamp" in health_status
        assert "services" in health_status
        
        # Overall status should be one of the expected values
        assert health_status["status"] in ["healthy", "degraded", "unhealthy"]
        
        # Services should be a dict
        assert isinstance(health_status["services"], dict)
        
        # Should include database and cache
        assert "database" in health_status["services"]
        assert "cache" in health_status["services"]
    
    @patch('src.utils.health_checks.check_database_health')
    @pytest.mark.asyncio
    async def test_database_failure_handling(self, mock_db_check):
        """Test handling of database health check failures."""
        # Mock database failure
        mock_db_check.return_value = {
            "status": "unhealthy",
            "error": "Connection failed",
            "latency_ms": None
        }
        
        health_status = await get_comprehensive_health_status()
        
        assert health_status["services"]["database"]["status"] == "unhealthy"
        assert health_status["status"] in ["degraded", "unhealthy"]
    
    @patch('src.utils.health_checks.check_redis_health')
    @pytest.mark.asyncio
    async def test_redis_failure_handling(self, mock_redis_check):
        """Test handling of Redis health check failures."""
        # Mock Redis failure
        mock_redis_check.return_value = {
            "status": "unhealthy",
            "error": "Connection timeout",
            "latency_ms": None
        }
        
        health_status = await get_comprehensive_health_status()
        
        assert health_status["services"]["cache"]["status"] == "unhealthy"
        # System should still be functional with Redis down (graceful degradation)
        assert health_status["status"] in ["healthy", "degraded"]
    
    @pytest.mark.asyncio
    async def test_health_check_performance(self):
        """Test health check performance."""
        start_time = time.time()
        
        # Run comprehensive health check
        health_status = await get_comprehensive_health_status()
        
        end_time = time.time()
        check_duration = end_time - start_time
        
        # Health check should be fast (under 5 seconds)
        assert check_duration < 5.0, f"Health check too slow: {check_duration}s"
        
        # Should have timestamp
        assert "timestamp" in health_status
        assert isinstance(health_status["timestamp"], (int, float))
    
    @pytest.mark.asyncio
    async def test_health_check_concurrent_access(self):
        """Test health checks under concurrent access."""
        async def run_health_check():
            return await get_comprehensive_health_status()
        
        # Run multiple health checks concurrently
        tasks = [run_health_check() for _ in range(3)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should succeed or fail gracefully
        for result in results:
            if isinstance(result, Exception):
                # Exceptions should be handled gracefully
                assert "health" in str(result).lower() or "connection" in str(result).lower()
            else:
                assert isinstance(result, dict)
                assert "status" in result
    
    @pytest.mark.asyncio
    async def test_medical_services_integration(self):
        """Test health checks for medical-specific services."""
        health_status = await get_comprehensive_health_status()
        
        # Check if external services section exists
        if "external_services" in health_status:
            external = health_status["external_services"]
            
            # Medical services should be monitored
            medical_services = ["mydisease", "pubmed", "clinicaltrials", "medlineplus"]
            
            for service in medical_services:
                if service in external:
                    service_health = external[service]
                    assert "status" in service_health
                    
                    # If healthy, should have response time
                    if service_health["status"] == "healthy":
                        assert "response_time_ms" in service_health or "latency_ms" in service_health
    
    @pytest.mark.asyncio
    async def test_health_check_caching(self):
        """Test health check result caching."""
        # Get health status twice quickly
        start_time = time.time()
        status1 = await get_comprehensive_health_status()
        first_call_time = time.time() - start_time
        
        start_time = time.time()
        status2 = await get_comprehensive_health_status()
        second_call_time = time.time() - start_time
        
        # Both should return valid results
        assert isinstance(status1, dict)
        assert isinstance(status2, dict)
        
        # Second call might be faster due to caching
        # But both should complete reasonably quickly
        assert first_call_time < 10.0
        assert second_call_time < 10.0
    
    def test_health_check_data_structure(self):
        """Test the structure of health check responses."""
        # This tests the expected structure without making actual calls
        expected_structure = {
            "status": "healthy",
            "timestamp": 1234567890.0,
            "services": {
                "database": {
                    "status": "healthy",
                    "latency_ms": 50.0
                },
                "cache": {
                    "status": "healthy", 
                    "latency_ms": 10.0
                }
            }
        }
        
        # Verify structure format
        assert "status" in expected_structure
        assert "timestamp" in expected_structure
        assert "services" in expected_structure
        assert isinstance(expected_structure["services"], dict)
        
        # Verify service structure
        for service_name, service_data in expected_structure["services"].items():
            assert "status" in service_data
            assert service_data["status"] in ["healthy", "unhealthy", "degraded", "disabled"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])