"""
Unit tests for clinical_trials_service.py

Tests cover:
- Service initialization with live/stub modes
- Clinical trials search with ClinicalTrials.gov API v2
- Status filtering (recruiting, completed, etc.)
- Trial details retrieval by NCT ID
- Location extraction from API responses
- Error handling and graceful degradation
- HTTP client fallback (httpx -> requests)
- Caching behavior
- Prompt enhancement integration
- Factory function creation

Test Strategy:
- Mock HTTP clients (httpx/requests) for isolated testing
- Mock ClinicalTrials.gov API v2 responses
- Test both async and sync code paths
- Verify error handling without raising exceptions to user
- Test deprecated stub methods for backward compatibility
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.services.clinical_trials_service import (
    ClinicalTrialsService,
    create_clinical_trials_service,
    search_clinical_trials,
)


@pytest.fixture
def mock_settings():
    """Mock application settings."""
    settings = Mock()
    settings.effective_use_live_services = True
    return settings


@pytest.fixture
def mock_banner():
    """Mock educational banner text."""
    return "⚠️ EDUCATIONAL PURPOSE ONLY - Consult healthcare professionals"


@pytest.fixture
def sample_api_v2_response():
    """Sample ClinicalTrials.gov API v2 response structure."""
    return {
        "totalCount": 42,
        "studies": [
            {
                "protocolSection": {
                    "identificationModule": {
                        "nctId": "NCT04567890",
                        "briefTitle": "Study of Diabetes Management",
                        "officialTitle": "A Randomized Clinical Trial of Diabetes Management",
                    },
                    "statusModule": {
                        "overallStatus": "RECRUITING",
                        "enrollmentInfo": {"count": 500},
                    },
                    "designModule": {
                        "phases": ["PHASE3"],
                        "studyType": "INTERVENTIONAL",
                    },
                    "conditionsModule": {"conditions": ["Type 2 Diabetes Mellitus"]},
                    "descriptionModule": {
                        "briefSummary": "This study evaluates diabetes management strategies.",
                        "detailedDescription": "Full description of the study protocol and methodology.",
                    },
                    "sponsorCollaboratorsModule": {
                        "leadSponsor": {"name": "Research Hospital"}
                    },
                    "contactsLocationsModule": {
                        "centralContacts": [
                            {
                                "name": "Dr. Jane Smith",
                                "email": "jsmith@example.com",
                                "phone": "555-1234",
                            }
                        ],
                        "locations": [
                            {
                                "facility": "Mayo Clinic",
                                "city": "Rochester",
                                "state": "MN",
                                "country": "USA",
                            },
                            {
                                "facility": "Johns Hopkins",
                                "city": "Baltimore",
                                "state": "MD",
                                "country": "USA",
                            },
                        ],
                    },
                    "armsInterventionsModule": {
                        "interventions": [
                            {"name": "Metformin"},
                            {"name": "Lifestyle counseling"},
                        ]
                    },
                    "eligibilityModule": {"maximumAge": "65 YEARS"},
                }
            }
        ],
    }


class TestClinicalTrialsServiceInitialization:
    """Test service initialization and configuration."""

    @patch("src.services.clinical_trials_service.get_settings")
    @patch("src.services.clinical_trials_service.get_educational_banner")
    def test_init_with_live_services(self, mock_banner_fn, mock_settings_fn):
        """Test initialization with live services enabled."""
        mock_settings_fn.return_value.effective_use_live_services = True
        mock_banner_fn.return_value = "Educational Banner"

        service = ClinicalTrialsService()

        assert service.use_live is True
        assert service.banner == "Educational Banner"
        assert service._client is None

    @patch("src.services.clinical_trials_service.get_settings")
    @patch("src.services.clinical_trials_service.get_educational_banner")
    def test_init_without_live_services(self, mock_banner_fn, mock_settings_fn):
        """Test initialization with live services disabled."""
        mock_settings_fn.return_value.effective_use_live_services = False
        mock_banner_fn.return_value = "Educational Banner"

        service = ClinicalTrialsService()

        assert service.use_live is False


class TestSearchTrials:
    """Test clinical trials search functionality."""

    @pytest.mark.asyncio
    @patch("src.services.clinical_trials_service._has_httpx", True)
    @patch("src.services.clinical_trials_service.httpx")
    @patch("src.services.clinical_trials_service.get_settings")
    @patch("src.services.clinical_trials_service.get_educational_banner")
    async def test_search_trials_with_httpx(
        self, mock_banner_fn, mock_settings_fn, mock_httpx, sample_api_v2_response
    ):
        """Test searching trials using httpx async client."""
        # Setup mocks
        mock_settings_fn.return_value.effective_use_live_services = True
        mock_banner_fn.return_value = "Banner"

        mock_response = Mock()
        mock_response.json = Mock(return_value=sample_api_v2_response)
        mock_response.raise_for_status = Mock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        mock_httpx.AsyncClient.return_value = mock_client

        service = ClinicalTrialsService()
        result = await service.search_trials("diabetes", limit=10)

        # Verify results
        assert result["total_studies"] == 42
        assert len(result["trials"]) == 1
        assert result["trials"][0]["nct_id"] == "NCT04567890"
        assert result["trials"][0]["title"] == "Study of Diabetes Management"
        assert result["trials"][0]["status"] == "RECRUITING"
        assert "ClinicalTrials.gov API v2" in result["sources"]

    @pytest.mark.asyncio
    @patch("src.services.clinical_trials_service._has_httpx", False)
    @patch("src.services.clinical_trials_service._has_requests", True)
    @patch("src.services.clinical_trials_service.requests")
    @patch("src.services.clinical_trials_service.get_settings")
    @patch("src.services.clinical_trials_service.get_educational_banner")
    async def test_search_trials_with_requests_fallback(
        self, mock_banner_fn, mock_settings_fn, mock_requests, sample_api_v2_response
    ):
        """Test searching trials with requests fallback when httpx unavailable."""
        mock_settings_fn.return_value.effective_use_live_services = True
        mock_banner_fn.return_value = "Banner"

        mock_response = Mock()
        mock_response.json.return_value = sample_api_v2_response
        mock_response.raise_for_status = Mock()
        mock_requests.get.return_value = mock_response

        service = ClinicalTrialsService()
        result = await service.search_trials("diabetes", limit=10)

        # Verify requests was called
        mock_requests.get.assert_called_once()
        assert "diabetes" in str(mock_requests.get.call_args)

        # Verify results
        assert result["total_studies"] == 42
        assert len(result["trials"]) == 1

    @pytest.mark.asyncio
    @patch("src.services.clinical_trials_service._has_httpx", True)
    @patch("src.services.clinical_trials_service.httpx")
    @patch("src.services.clinical_trials_service.get_settings")
    @patch("src.services.clinical_trials_service.get_educational_banner")
    async def test_search_trials_with_status_filter(
        self, mock_banner_fn, mock_settings_fn, mock_httpx, sample_api_v2_response
    ):
        """Test searching trials with status filter."""
        mock_settings_fn.return_value.effective_use_live_services = True
        mock_banner_fn.return_value = "Banner"

        mock_response = Mock()
        mock_response.json = Mock(return_value=sample_api_v2_response)
        mock_response.raise_for_status = Mock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        mock_httpx.AsyncClient.return_value = mock_client

        service = ClinicalTrialsService()
        await service.search_trials("diabetes", limit=10, status="RECRUITING")

        # Verify status filter was passed to API
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["filter.overallStatus"] == "RECRUITING"

    @pytest.mark.asyncio
    @patch("src.services.clinical_trials_service._has_httpx", True)
    @patch("src.services.clinical_trials_service.httpx")
    @patch("src.services.clinical_trials_service.get_settings")
    @patch("src.services.clinical_trials_service.get_educational_banner")
    async def test_search_trials_limit_respected(
        self, mock_banner_fn, mock_settings_fn, mock_httpx, sample_api_v2_response
    ):
        """Test that search limit parameter is respected."""
        mock_settings_fn.return_value.effective_use_live_services = True
        mock_banner_fn.return_value = "Banner"

        # Create response with 3 studies
        multi_study_response = {
            "totalCount": 100,
            "studies": [sample_api_v2_response["studies"][0]] * 3,
        }

        mock_response = Mock()
        mock_response.json = Mock(return_value=multi_study_response)
        mock_response.raise_for_status = Mock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        mock_httpx.AsyncClient.return_value = mock_client

        service = ClinicalTrialsService()
        result = await service.search_trials("diabetes", limit=2)

        # Should only return 2 trials despite 3 in response
        assert len(result["trials"]) == 2

    @pytest.mark.asyncio
    @patch("src.services.clinical_trials_service._has_httpx", True)
    @patch("src.services.clinical_trials_service.httpx")
    @patch("src.services.clinical_trials_service.get_settings")
    @patch("src.services.clinical_trials_service.get_educational_banner")
    async def test_search_trials_api_error_handling(
        self, mock_banner_fn, mock_settings_fn, mock_httpx
    ):
        """Test graceful error handling when API fails."""
        mock_settings_fn.return_value.effective_use_live_services = True
        mock_banner_fn.return_value = "Banner"

        mock_client = AsyncMock()
        mock_client.get.side_effect = Exception("API Connection Failed")
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = AsyncMock()

        mock_httpx.AsyncClient.return_value = mock_client

        service = ClinicalTrialsService()
        result = await service.search_trials("diabetes")

        # Should return error response, not raise exception
        assert "error" in result
        assert result["trials"] == []
        assert result["total_results"] == 0


class TestGetTrialDetails:
    """Test retrieving detailed trial information by NCT ID."""

    @pytest.mark.asyncio
    @patch("src.services.clinical_trials_service._has_httpx", True)
    @patch("src.services.clinical_trials_service.httpx")
    @patch("src.services.clinical_trials_service.get_settings")
    @patch("src.services.clinical_trials_service.get_educational_banner")
    async def test_get_trial_details_success(
        self, mock_banner_fn, mock_settings_fn, mock_httpx, sample_api_v2_response
    ):
        """Test retrieving trial details by NCT ID."""
        mock_settings_fn.return_value.effective_use_live_services = True
        mock_banner_fn.return_value = "Banner"

        # API returns single study for details endpoint
        mock_response = Mock()
        mock_response.json = Mock(
            return_value={
                "protocolSection": sample_api_v2_response["studies"][0][
                    "protocolSection"
                ]
            }
        )
        mock_response.raise_for_status = Mock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        mock_httpx.AsyncClient.return_value = mock_client

        service = ClinicalTrialsService()
        details = await service.get_trial_details("NCT04567890")

        assert details is not None
        assert details["nct_id"] == "NCT04567890"
        assert details["title"] == "Study of Diabetes Management"
        assert details["phase"] == "PHASE3"
        assert details["status"] == "RECRUITING"
        assert "Type 2 Diabetes Mellitus" in details["conditions"]
        assert len(details["interventions"]) == 2
        assert "Metformin" in details["interventions"]

    @pytest.mark.asyncio
    @patch("src.services.clinical_trials_service._has_httpx", True)
    @patch("src.services.clinical_trials_service.httpx")
    @patch("src.services.clinical_trials_service.get_settings")
    @patch("src.services.clinical_trials_service.get_educational_banner")
    async def test_get_trial_details_not_found(
        self, mock_banner_fn, mock_settings_fn, mock_httpx
    ):
        """Test when trial NCT ID not found."""
        mock_settings_fn.return_value.effective_use_live_services = True
        mock_banner_fn.return_value = "Banner"

        mock_client = AsyncMock()
        mock_client.get.side_effect = Exception("404 Not Found")
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = AsyncMock()

        mock_httpx.AsyncClient.return_value = mock_client

        service = ClinicalTrialsService()
        details = await service.get_trial_details("NCT99999999")

        # Should return None, not raise exception
        assert details is None


class TestExtractLocations:
    """Test location extraction helper method."""

    @patch("src.services.clinical_trials_service.get_settings")
    @patch("src.services.clinical_trials_service.get_educational_banner")
    def test_extract_locations_success(self, mock_banner_fn, mock_settings_fn):
        """Test extracting locations from contacts module."""
        mock_settings_fn.return_value.effective_use_live_services = True
        mock_banner_fn.return_value = "Banner"

        contacts_module = {
            "locations": [
                {
                    "facility": "Mayo Clinic",
                    "city": "Rochester",
                    "state": "MN",
                    "country": "USA",
                },
                {
                    "facility": "Johns Hopkins",
                    "city": "Baltimore",
                    "state": "MD",
                    "country": "USA",
                },
            ]
        }

        service = ClinicalTrialsService()
        locations = service._extract_locations(contacts_module)

        assert len(locations) == 2
        assert locations[0]["facility"] == "Mayo Clinic"
        assert locations[0]["city"] == "Rochester"
        assert locations[1]["facility"] == "Johns Hopkins"

    @patch("src.services.clinical_trials_service.get_settings")
    @patch("src.services.clinical_trials_service.get_educational_banner")
    def test_extract_locations_limit_to_five(self, mock_banner_fn, mock_settings_fn):
        """Test that location extraction limits to 5 locations."""
        mock_settings_fn.return_value.effective_use_live_services = True
        mock_banner_fn.return_value = "Banner"

        contacts_module = {
            "locations": [
                {
                    "facility": f"Hospital {i}",
                    "city": "City",
                    "state": "ST",
                    "country": "USA",
                }
                for i in range(10)
            ]
        }

        service = ClinicalTrialsService()
        locations = service._extract_locations(contacts_module)

        # Should limit to 5
        assert len(locations) == 5

    @patch("src.services.clinical_trials_service.get_settings")
    @patch("src.services.clinical_trials_service.get_educational_banner")
    def test_extract_locations_empty(self, mock_banner_fn, mock_settings_fn):
        """Test extracting locations from empty contacts module."""
        mock_settings_fn.return_value.effective_use_live_services = True
        mock_banner_fn.return_value = "Banner"

        contacts_module = {"locations": []}

        service = ClinicalTrialsService()
        locations = service._extract_locations(contacts_module)

        assert locations == []


class TestFunctionalAPI:
    """Test standalone functional API for routers."""

    @pytest.mark.asyncio
    @patch("src.services.clinical_trials_service._has_httpx", True)
    @patch("src.services.clinical_trials_service.httpx")
    @patch("src.services.clinical_trials_service.get_educational_banner")
    async def test_search_clinical_trials_function(
        self, mock_banner_fn, mock_httpx, sample_api_v2_response
    ):
        """Test standalone search_clinical_trials function."""
        mock_banner_fn.return_value = "Banner"

        mock_response = Mock()
        mock_response.json = Mock(return_value=sample_api_v2_response)
        mock_response.raise_for_status = Mock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        mock_httpx.AsyncClient.return_value = mock_client

        result = await search_clinical_trials("diabetes", max_studies=10)

        assert result["total_studies"] == 42
        assert len(result["trials"]) >= 1
        assert result["banner"] == "Banner"

    @pytest.mark.asyncio
    @patch("src.services.clinical_trials_service._has_prompt_enhancement", True)
    @patch("src.services.clinical_trials_service.enhance_prompt")
    @patch("src.services.clinical_trials_service.get_educational_banner")
    async def test_search_clinical_trials_with_prompt_enhancement(
        self, mock_banner_fn, mock_enhance_prompt
    ):
        """Test prompt enhancement integration in functional API."""
        mock_banner_fn.return_value = "Banner"
        mock_enhance_prompt.return_value = (
            "Type 2 Diabetes Mellitus",
            True,
            "Did you mean Type 2 Diabetes?",
        )

        result = await search_clinical_trials("DM")

        # Should return clarification request
        assert result["needs_clarification"] is True
        assert "clarification_question" in result

    @pytest.mark.asyncio
    @patch("src.services.clinical_trials_service._has_httpx", True)
    @patch("src.services.clinical_trials_service.httpx")
    @patch("src.services.clinical_trials_service.get_educational_banner")
    async def test_search_clinical_trials_with_status_filter(
        self, mock_banner_fn, mock_httpx, sample_api_v2_response
    ):
        """Test status filter in functional API."""
        mock_banner_fn.return_value = "Banner"

        mock_response = Mock()
        mock_response.json = Mock(return_value=sample_api_v2_response)
        mock_response.raise_for_status = Mock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        mock_httpx.AsyncClient.return_value = mock_client

        await search_clinical_trials("diabetes", max_studies=10, status="recruiting")

        # Verify status was converted to uppercase with underscores
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["filter.overallStatus"] == "RECRUITING"


class TestServiceFactory:
    """Test service factory function."""

    @patch("src.services.clinical_trials_service.get_settings")
    @patch("src.services.clinical_trials_service.get_educational_banner")
    def test_create_service_success(self, mock_banner_fn, mock_settings_fn):
        """Test successful service creation via factory."""
        mock_settings_fn.return_value.effective_use_live_services = True
        mock_banner_fn.return_value = "Banner"

        service = create_clinical_trials_service()

        assert service is not None
        assert isinstance(service, ClinicalTrialsService)

    @patch("src.services.clinical_trials_service.get_settings")
    def test_create_service_failure_graceful(self, mock_settings_fn):
        """Test graceful degradation when service creation fails."""
        mock_settings_fn.side_effect = Exception("Config error")

        service = create_clinical_trials_service()

        # Should return None instead of raising
        assert service is None


class TestErrorHandling:
    """Test comprehensive error handling."""

    @pytest.mark.asyncio
    @patch("src.services.clinical_trials_service._has_httpx", False)
    @patch("src.services.clinical_trials_service._has_requests", False)
    @patch("src.services.clinical_trials_service.get_settings")
    @patch("src.services.clinical_trials_service.get_educational_banner")
    async def test_no_http_client_available(self, mock_banner_fn, mock_settings_fn):
        """Test error when no HTTP client available."""
        mock_settings_fn.return_value.effective_use_live_services = True
        mock_banner_fn.return_value = "Banner"

        service = ClinicalTrialsService()
        result = await service.search_trials("diabetes")

        # Should return error response
        assert "error" in result
        assert result["trials"] == []

    @patch("src.services.clinical_trials_service.get_settings")
    @patch("src.services.clinical_trials_service.get_educational_banner")
    def test_create_error_response(self, mock_banner_fn, mock_settings_fn):
        """Test error response creation."""
        mock_settings_fn.return_value.effective_use_live_services = True
        mock_banner_fn.return_value = "Banner"

        service = ClinicalTrialsService()
        error_response = service._create_error_response(
            "diabetes", "Connection timeout"
        )

        assert "error" in error_response
        assert "Connection timeout" in error_response["error"]
        assert error_response["trials"] == []
        assert error_response["total_results"] == 0
        assert "fallback_note" in error_response


class TestDeprecatedMethods:
    """Test deprecated stub methods for backward compatibility."""

    @patch("src.services.clinical_trials_service.get_settings")
    @patch("src.services.clinical_trials_service.get_educational_banner")
    def test_create_stub_trials_response(self, mock_banner_fn, mock_settings_fn):
        """Test deprecated stub response creation."""
        mock_settings_fn.return_value.effective_use_live_services = False
        mock_banner_fn.return_value = "Banner"

        service = ClinicalTrialsService()
        stub_response = service._create_stub_trials_response("diabetes", 10)

        assert "trials" in stub_response
        assert "service_note" in stub_response
        assert "Educational stub data" in stub_response["service_note"]

    @patch("src.services.clinical_trials_service.get_settings")
    @patch("src.services.clinical_trials_service.get_educational_banner")
    def test_create_stub_trial_details(self, mock_banner_fn, mock_settings_fn):
        """Test deprecated stub trial details creation."""
        mock_settings_fn.return_value.effective_use_live_services = False
        mock_banner_fn.return_value = "Banner"

        service = ClinicalTrialsService()
        stub_details = service._create_stub_trial_details("NCT12345678")

        assert stub_details["nct_id"] == "NCT12345678"
        assert "educational_note" in stub_details
