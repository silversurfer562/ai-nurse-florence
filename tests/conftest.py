"""
Test configuration and fixtures
Enhanced for service layer testing
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import tempfile
import os

# Test environment setup
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment variables"""
    os.environ["ENVIRONMENT"] = "test"
    os.environ["DEBUG"] = "true"
    os.environ["DATABASE_URL"] = "sqlite:///test.db"
    os.environ["LOG_LEVEL"] = "DEBUG"
    # Disable external services in tests
    os.environ["USE_LIVE_SERVICES"] = "false"
    os.environ["OPENAI_API_KEY"] = ""  # Disable OpenAI in tests
    os.environ["REDIS_URL"] = ""  # Disable Redis in tests

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

# Mock external services
@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing"""
    with patch('src.services.openai_client.get_openai_client') as mock:
        mock_client = AsyncMock()
        mock.return_value = mock_client
        yield mock_client

@pytest.fixture
def mock_redis_cache():
    """Mock Redis cache for testing"""
    with patch('src.utils.redis_cache.get_redis_client') as mock:
        mock.return_value = None  # Force fallback to memory cache
        yield mock

@pytest.fixture
def disable_external_services():
    """Disable all external service calls"""
    with patch('src.services.openai_client.is_openai_available', return_value=False), \
         patch('src.utils.redis_cache.get_redis_client', return_value=None):
        yield

# Sample data fixtures
@pytest.fixture
def sample_clinical_request():
    """Sample clinical decision request"""
    from src.models.schemas import ClinicalDecisionRequest, SeverityLevel, CareSetting
    return ClinicalDecisionRequest(
        patient_condition="acute heart failure",
        severity=SeverityLevel.MODERATE,
        care_setting=CareSetting.MED_SURG,
        comorbidities=["diabetes", "hypertension"],
        additional_context="Patient reports shortness of breath"
    )

@pytest.fixture
def sample_literature_request():
    """Sample literature search request"""
    from src.models.schemas import LiteratureSearchRequest
    return LiteratureSearchRequest(
        query="heart failure nursing interventions",
        max_results=10,
        filter_years=2020
    )

@pytest.fixture
def sample_sbar_request():
    """Sample SBAR request"""
    from src.models.schemas import SBARRequest
    return SBARRequest(
        situation="Patient experiencing increased shortness of breath",
        background="72-year-old male with history of heart failure",
        assessment="Bilateral crackles, oxygen saturation 88% on room air",
        recommendation="Increase oxygen therapy and administer diuretic"
    )

# Test database fixtures
@pytest.fixture
def temp_database():
    """Create temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    yield f"sqlite:///{db_path}"
    
    # Cleanup
    try:
        os.unlink(db_path)
    except FileNotFoundError:
        pass

# Service fixtures
@pytest.fixture
def clinical_decision_service():
    """Clinical decision service instance"""
    from src.services.clinical_decision_service import ClinicalDecisionService
    return ClinicalDecisionService()

@pytest.fixture 
def evidence_service():
    """Evidence service instance"""
    from src.services.evidence_service import EvidenceService
    return EvidenceService()

# Mock response fixtures
@pytest.fixture
def mock_openai_response():
    """Mock OpenAI response"""
    return """
    **Primary Nursing Interventions:**
    1. Monitor daily weights and strict I&O
    2. Assess for signs of fluid overload
    3. Position patient in semi-Fowler's position
    4. Administer diuretics as ordered
    
    **Patient Education:**
    - Sodium restriction (2g daily)
    - Daily weight monitoring
    - When to contact healthcare provider
    """

@pytest.fixture
def mock_literature_response():
    """Mock literature search response"""
    from src.models.schemas import LiteratureItem, EvidenceLevel
    return [
        LiteratureItem(
            title="Evidence-Based Heart Failure Management",
            authors=["Smith, J.", "Johnson, M."],
            journal="Journal of Cardiac Nursing",
            year=2023,
            abstract="Comprehensive review of evidence-based nursing interventions for heart failure management.",
            evidence_level=EvidenceLevel.LEVEL_I
        ),
        LiteratureItem(
            title="Heart Failure Patient Education Strategies", 
            authors=["Davis, R.", "Wilson, K."],
            journal="Patient Education Journal",
            year=2022,
            abstract="Systematic review of patient education strategies for heart failure self-management.",
            evidence_level=EvidenceLevel.LEVEL_II
        )
    ]

# Performance testing fixtures
@pytest.fixture
def performance_timer():
    """Timer for performance testing"""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
            return self.elapsed
        
        @property
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
    
    return Timer()

# Error testing fixtures
@pytest.fixture
def force_service_error():
    """Force service errors for testing error handling"""
    with patch('src.services.clinical_decision_service.ClinicalDecisionService._get_base_interventions') as mock:
        mock.side_effect = Exception("Forced test error")
        yield mock

# Caching test fixtures
@pytest.fixture
def mock_cache_operations():
    """Mock cache operations for testing"""
    cache_data = {}
    
    async def mock_cache_set(key, value, ttl=3600):
        cache_data[key] = value
        return True
    
    async def mock_cache_get(key):
        return cache_data.get(key)
    
    async def mock_cache_delete(key):
        cache_data.pop(key, None)
        return True
    
    with patch('src.utils.redis_cache.cache_set', side_effect=mock_cache_set), \
         patch('src.utils.redis_cache.cache_get', side_effect=mock_cache_get), \
         patch('src.utils.redis_cache.cache_delete', side_effect=mock_cache_delete):
        yield cache_data
