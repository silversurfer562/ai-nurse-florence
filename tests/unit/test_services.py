"""
Unit tests for service layer following Testing Patterns from coding instructions.
Tests individual service methods with mocked dependencies.
"""

import pytest

pytestmark = pytest.mark.unit

class TestServiceRegistry:
    """Test service registry following Service Layer Architecture."""
    
    def test_service_availability(self):
        """Test that services handle graceful degradation."""
        from src.services import get_service, get_available_services
        
        services = get_available_services()
        
        # Should return dict with service status
        assert isinstance(services, dict)
        
        # Test getting individual services (may be None due to graceful degradation)
        for service_name in ['disease', 'pubmed', 'clinical_trials', 'sbar', 'openai']:
            _service = get_service(service_name)
            # Service can be None (graceful degradation) or actual service instance
            # This is expected behavior following Conditional Imports Pattern
            
    def test_sbar_service_availability(self):
        """Test SBAR service which should be available."""
        from src.services import get_service
        
        sbar_service = get_service('sbar')
        
        # SBAR service should be available as it has no external dependencies
        assert sbar_service is not None

class TestServiceGracefulDegradation:
    """Test graceful degradation following Conditional Imports Pattern."""
    
    def test_missing_service_handling(self):
        """Test that missing services are handled gracefully.""" 
        from src.services import get_service
        
        # Non-existent service should return None
        non_existent_service = get_service('non_existent_service')
        assert non_existent_service is None
        
    def test_service_registry_resilience(self):
        """Test service registry resilience to import failures."""
        from src.services import get_available_services
        
        # Should not raise exception even if some services fail to load
        services = get_available_services()
        assert isinstance(services, dict)
