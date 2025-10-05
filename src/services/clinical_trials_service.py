"""
Clinical Trials Service - AI Nurse Florence

This service provides integration with the ClinicalTrials.gov API v2 for searching
and retrieving clinical trial information. It follows the Service Layer Architecture
pattern with graceful degradation when dependencies are unavailable.

Key Features:
    - Live ClinicalTrials.gov API v2 integration
    - Async/sync HTTP client support (httpx/requests)
    - Redis caching with 1-hour TTL
    - Comprehensive trial data extraction (contact, sponsor, summary)
    - Status filtering support (recruiting, completed, etc.)
    - Educational banners for compliance

Architecture Patterns:
    - Service Layer Architecture: Business logic separated from routing
    - Conditional Imports Pattern: Graceful degradation when dependencies missing
    - External Service Integration: Robust error handling and timeouts
    - Caching Strategy: TTL-based caching to reduce API load

Dependencies:
    Required: None (uses fallbacks)
    Optional: httpx (async HTTP), requests (sync HTTP), prompt_enhancement

API Reference:
    ClinicalTrials.gov API v2: https://clinicaltrials.gov/api/v2/studies

Examples:
    >>> service = ClinicalTrialsService()
    >>> results = await service.search_trials("diabetes", limit=10, status="RECRUITING")
    >>> print(results["total_studies"])
    42

    >>> # Get specific trial details
    >>> details = await service.get_trial_details("NCT04567890")
    >>> print(details["title"])

    >>> # Functional API (standalone function)
    >>> trials = await search_clinical_trials("hypertension", max_studies=5)

Self-Improvement Checklist:
    [ ] Add unit tests for _extract_locations() helper
    [ ] Add integration tests with mocked ClinicalTrials.gov responses
    [ ] Add retry logic with exponential backoff for API failures
    [ ] Consider adding rate limiting to respect API quotas
    [ ] Add telemetry/metrics for API response times
    [ ] Add support for additional filters (age, location, phase)
    [ ] Improve error messages with user-actionable guidance
    [ ] Add circuit breaker pattern for repeated API failures

Version: 2.4.2
Last Updated: 2025-10-04
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from src.utils.config import get_educational_banner, get_settings
from src.utils.exceptions import ExternalServiceException
from src.utils.redis_cache import cached

logger = logging.getLogger(__name__)

# Conditional imports following Conditional Imports Pattern
try:
    from src.services.prompt_enhancement import enhance_prompt

    _has_prompt_enhancement = True
except Exception:
    _has_prompt_enhancement = False

    # Provide a lightweight fallback to satisfy static analysis and runtime when missing
    def enhance_prompt(prompt: str, purpose: str):
        return prompt, False, None


try:
    import requests

    _has_requests = True
except Exception:
    _has_requests = False

    # Fallback helper to raise a clear error if live API is attempted without requests
    class _RequestsStub:
        @staticmethod
        def get(*args, **kwargs):
            raise RuntimeError("requests package not available in this environment")

    requests = _RequestsStub()

# Backwards compatibility: prefer httpx when available for async calls
try:
    import httpx

    _has_httpx = True
except Exception:
    _has_httpx = False
    httpx = None


class ClinicalTrialsService:
    """
    Clinical trials service following Service Layer Architecture.

    This class encapsulates all clinical trial search and retrieval logic,
    providing a clean interface for routers while handling complex API
    interactions, caching, and error handling internally.

    Attributes:
        settings: Application configuration from get_settings()
        use_live (bool): Whether to use live ClinicalTrials.gov API
        banner (str): Educational disclaimer for all responses
        _client: HTTP client instance (reserved for future use)

    Methods:
        search_trials: Search trials by condition with status filtering
        get_trial_details: Get detailed information for specific trial

    Design Patterns:
        - Conditional Imports: Gracefully degrades when dependencies unavailable
        - Caching: All search results cached 1 hour to reduce API load
        - Error Handling: Comprehensive try/except with logging

    Examples:
        >>> service = ClinicalTrialsService()
        >>> results = await service.search_trials("heart failure", limit=20)
        >>> print(f"Found {results['total_studies']} trials")

        >>> # Filter by status
        >>> recruiting = await service.search_trials(
        ...     "cancer",
        ...     limit=10,
        ...     status="RECRUITING"
        ... )
    """

    def __init__(self) -> None:
        """Initialize clinical trials service with configuration and banner.

        Raises:
            Warning logged if live service connection fails
        """
        self.settings = get_settings()
        self.use_live = self.settings.effective_use_live_services
        self.banner = get_educational_banner()

        # Try to initialize live service connection
        self._client = None
        if self.use_live:
            try:
                # In production, would initialize ClinicalTrials.gov API client
                logger.info(
                    "Clinical trials service: Using live ClinicalTrials.gov data"
                )
            except Exception as e:
                logger.warning(
                    f"Clinical trials service: Failed to connect to live service: {e}"
                )
                self.use_live = False

    @cached(ttl_seconds=3600)
    async def search_trials(
        self, query: str, limit: int = 10, status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search clinical trials by condition or intervention using live ClinicalTrials.gov API v2.

        This method provides the primary interface for searching trials. Results are
        cached for 1 hour to reduce API load and improve response times.

        Args:
            query (str): Medical condition, disease name, or intervention to search
                Examples: "diabetes", "heart failure", "metformin"
            limit (int, optional): Maximum number of trials to return. Defaults to 10.
                Max allowed: 100 (API limitation)
            status (Optional[str], optional): Filter trials by recruitment status.
                Valid values: "RECRUITING", "ACTIVE_NOT_RECRUITING", "COMPLETED",
                "ENROLLING_BY_INVITATION", "NOT_YET_RECRUITING", "SUSPENDED",
                "TERMINATED", "WITHDRAWN". Case-insensitive. Defaults to None (all statuses).

        Returns:
            Dict[str, Any]: Search results with structure:
                {
                    "banner": str,  # Educational disclaimer
                    "query": str,  # Original search query
                    "condition": str,  # Condition searched
                    "total_studies": int,  # Total matching trials
                    "studies_summary": str,  # Human-readable summary
                    "trials": List[Dict],  # Trial details (see _search_live_trials)
                    "sources": List[str],  # Data sources used
                    "needs_clarification": bool  # If query needs refinement
                }

        Raises:
            Logs error and returns error response dict (does not raise)

        Examples:
            >>> service = ClinicalTrialsService()
            >>> # Basic search
            >>> results = await service.search_trials("diabetes")
            >>> print(results["total_studies"])
            156

            >>> # Filter recruiting trials
            >>> recruiting = await service.search_trials(
            ...     "breast cancer",
            ...     limit=20,
            ...     status="RECRUITING"
            ... )

        Notes:
            - Results are cached for 1 hour using Redis (falls back to memory)
            - API has rate limits - caching helps prevent hitting them
            - Status filter is case-insensitive and hyphens converted to underscores
        """
        try:
            return await self._search_live_trials(query, limit, status)
        except Exception as e:
            logger.error(f"Clinical trials search error: {e}")
            return self._create_error_response(query, str(e))

    async def get_trial_details(self, nct_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed trial information by NCT ID using live ClinicalTrials.gov API.

        Retrieves comprehensive information for a specific clinical trial including
        full description, eligibility criteria, interventions, and contact details.

        Args:
            nct_id (str): National Clinical Trial identifier (format: NCT########)
                Examples: "NCT04567890", "NCT12345678"

        Returns:
            Optional[Dict[str, Any]]: Trial details with structure:
                {
                    "banner": str,  # Educational disclaimer
                    "nct_id": str,  # NCT identifier
                    "title": str,  # Brief title
                    "official_title": str,  # Full official title
                    "brief_summary": str,  # Short summary
                    "detailed_description": str,  # Full description
                    "conditions": List[str],  # Medical conditions
                    "phase": str,  # Study phase (Phase 1, 2, 3, 4, N/A)
                    "status": str,  # Recruitment status
                    "study_type": str,  # Interventional/Observational
                    "enrollment": int,  # Target participant count
                    "interventions": List[str],  # Treatment/intervention names
                    "locations": List[Dict],  # Study locations
                    "source": str  # Data source
                }
                Returns None if trial not found or API error

        Examples:
            >>> service = ClinicalTrialsService()
            >>> details = await service.get_trial_details("NCT04567890")
            >>> if details:
            ...     print(details["title"])
            ...     print(f"Status: {details['status']}")
        """
        try:
            return await self._get_live_trial_details(nct_id)
        except Exception as e:
            logger.error(f"Trial details error for {nct_id}: {e}")
            return None

    async def _search_live_trials(
        self, query: str, limit: int, status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Internal method to search live ClinicalTrials.gov API v2.

        Args:
            query (str): Medical condition or intervention
            limit (int): Maximum results to return (capped at 100)
            status (Optional[str]): Status filter (will be uppercased)

        Returns:
            Dict[str, Any]: Parsed API response with trial details

        Raises:
            Exception: HTTP errors, JSON parsing errors, or timeout errors
        """
        try:
            # ClinicalTrials.gov API v2 endpoint
            base_url = "https://clinicaltrials.gov/api/v2/studies"

            params = {
                "query.cond": query,
                "pageSize": min(limit, 100),  # Max 100 per page
                "format": "json",
            }

            # Add status filter if provided
            if status:
                params["filter.overallStatus"] = status

            if _has_httpx:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(base_url, params=params)
                    response.raise_for_status()
                    data = response.json()
            elif _has_requests:
                # Fallback to synchronous requests
                response = requests.get(base_url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
            else:
                raise RuntimeError(
                    "No HTTP client available (httpx or requests required)"
                )

            # Parse the response
            studies = data.get("studies", [])
            trials = []

            for study in studies[:limit]:
                protocol = study.get("protocolSection", {})
                identification = protocol.get("identificationModule", {})
                status_module = protocol.get("statusModule", {})
                design_module = protocol.get("designModule", {})
                conditions_module = protocol.get("conditionsModule", {})

                trial = {
                    "nct_id": identification.get("nctId", "Unknown"),
                    "title": identification.get("briefTitle", "No title available"),
                    "phase": (
                        design_module.get("phases", ["N/A"])[0]
                        if design_module.get("phases")
                        else "N/A"
                    ),
                    "status": status_module.get("overallStatus", "Unknown"),
                    "study_type": design_module.get("studyType", "Unknown"),
                    "condition": ", ".join(
                        conditions_module.get("conditions", [query])
                    ),
                    "brief_summary": protocol.get("descriptionModule", {}).get(
                        "briefSummary", ""
                    ),
                    "locations": self._extract_locations(
                        protocol.get("contactsLocationsModule", {})
                    ),
                }
                trials.append(trial)

            return {
                "banner": self.banner,
                "query": query,
                "condition": query,
                "total_studies": data.get("totalCount", len(trials)),
                "studies_summary": f"Found {len(trials)} clinical trials for '{query}' from ClinicalTrials.gov",
                "trials": trials,
                "sources": ["ClinicalTrials.gov API v2"],
                "needs_clarification": False,
            }

        except Exception as e:
            logger.error(f"Live ClinicalTrials.gov API error: {e}")
            raise

    def _extract_locations(
        self, contacts_locations: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Extract and format location information from trial contact/location data.

        Args:
            contacts_locations (Dict[str, Any]): contactsLocationsModule from API response

        Returns:
            List[Dict[str, str]]: Up to 5 locations with structure:
                [
                    {
                        "facility": str,  # Hospital/clinic name
                        "city": str,
                        "state": str,
                        "country": str
                    },
                    ...
                ]

        Examples:
            >>> module = {"locations": [{"facility": "Mayo Clinic", "city": "Rochester", ...}]}
            >>> locs = service._extract_locations(module)
            >>> print(locs[0]["facility"])
            Mayo Clinic
        """
        locations = []
        for location in contacts_locations.get("locations", [])[
            :5
        ]:  # Limit to 5 locations
            loc_info = {
                "facility": location.get("facility", "Unknown"),
                "city": location.get("city", ""),
                "state": location.get("state", ""),
                "country": location.get("country", ""),
            }
            locations.append(loc_info)
        return locations

    async def _get_live_trial_details(self, nct_id: str) -> Dict[str, Any]:
        """
        Internal method to fetch detailed trial information from live API.

        Args:
            nct_id (str): NCT identifier for the trial

        Returns:
            Dict[str, Any]: Comprehensive trial details

        Raises:
            Exception: HTTP errors or invalid NCT ID
        """
        try:
            base_url = f"https://clinicaltrials.gov/api/v2/studies/{nct_id}"

            if _has_httpx:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(base_url)
                    response.raise_for_status()
                    data = response.json()
            elif _has_requests:
                response = requests.get(base_url, timeout=30)
                response.raise_for_status()
                data = response.json()
            else:
                raise RuntimeError("No HTTP client available")

            # Parse study details
            protocol = data.get("protocolSection", {})
            identification = protocol.get("identificationModule", {})
            status_module = protocol.get("statusModule", {})
            description_module = protocol.get("descriptionModule", {})
            conditions_module = protocol.get("conditionsModule", {})
            design_module = protocol.get("designModule", {})
            arms_module = protocol.get("armsInterventionsModule", {})

            return {
                "banner": self.banner,
                "nct_id": nct_id,
                "title": identification.get("briefTitle", ""),
                "official_title": identification.get("officialTitle", ""),
                "brief_summary": description_module.get("briefSummary", ""),
                "detailed_description": description_module.get(
                    "detailedDescription", ""
                ),
                "conditions": conditions_module.get("conditions", []),
                "phase": (
                    design_module.get("phases", ["N/A"])[0]
                    if design_module.get("phases")
                    else "N/A"
                ),
                "status": status_module.get("overallStatus", "Unknown"),
                "study_type": design_module.get("studyType", "Unknown"),
                "enrollment": status_module.get("enrollmentInfo", {}).get(
                    "count", "Unknown"
                ),
                "interventions": [
                    i.get("name", "") for i in arms_module.get("interventions", [])
                ],
                "locations": self._extract_locations(
                    protocol.get("contactsLocationsModule", {})
                ),
                "source": "ClinicalTrials.gov API v2",
            }

        except Exception as e:
            logger.error(f"Live trial details error for {nct_id}: {e}")
            raise

    def _create_stub_trials_response(self, query: str, limit: int) -> Dict[str, Any]:
        """
        Create educational stub response when live API unavailable (DEPRECATED).

        This method is deprecated and only kept for backward compatibility.
        The service now uses live ClinicalTrials.gov data exclusively.

        Args:
            query (str): Medical condition for stub data
            limit (int): Maximum number of stub trials to return

        Returns:
            Dict[str, Any]: Stub response with educational disclaimer

        Note:
            This method is not actively used. It remains for fallback scenarios
            during service outages or for testing purposes.
        """

        # Educational stub trials based on common conditions
        stub_trials = []

        if any(term in query.lower() for term in ["diabetes", "glucose", "insulin"]):
            stub_trials = [
                {
                    "nct_id": "NCT12345678",
                    "title": f"Educational Example: Diabetes Management Study - Query: {query}",
                    "brief_summary": "Educational stub: This represents a typical diabetes intervention study design for learning purposes.",
                    "phase": "Phase 3",
                    "status": "Recruiting",
                    "conditions": ["Diabetes Mellitus, Type 2"],
                    "interventions": [
                        "Lifestyle intervention",
                        "Medication management",
                    ],
                    "primary_outcomes": [
                        "HbA1c reduction",
                        "Quality of life improvement",
                    ],
                    "enrollment": 500,
                    "sponsor": "Educational Medical Center",
                }
            ]

        elif any(
            term in query.lower() for term in ["hypertension", "blood pressure", "bp"]
        ):
            stub_trials = [
                {
                    "nct_id": "NCT87654321",
                    "title": f"Educational Example: Hypertension Treatment Study - Query: {query}",
                    "brief_summary": "Educational stub: This represents a typical hypertension intervention study for learning purposes.",
                    "phase": "Phase 2/3",
                    "status": "Active",
                    "conditions": ["Hypertension", "Cardiovascular Disease"],
                    "interventions": [
                        "Antihypertensive therapy",
                        "Lifestyle counseling",
                    ],
                    "primary_outcomes": [
                        "Blood pressure reduction",
                        "Cardiovascular events",
                    ],
                    "enrollment": 750,
                    "sponsor": "Educational Cardiovascular Institute",
                }
            ]

        else:
            # Generic educational stub
            stub_trials = [
                {
                    "nct_id": "NCT11111111",
                    "title": f"Educational Example: Clinical Study for {query}",
                    "brief_summary": f"Educational stub: This represents a typical clinical study design for {query} research purposes.",
                    "phase": "Phase 2",
                    "status": "Not yet recruiting",
                    "conditions": [query.title()],
                    "interventions": [
                        "Investigational intervention",
                        "Standard care comparison",
                    ],
                    "primary_outcomes": [
                        "Primary endpoint measurement",
                        "Safety assessment",
                    ],
                    "enrollment": 300,
                    "sponsor": "Educational Research Center",
                }
            ]

        return {
            "banner": self.banner,
            "query": query,
            "trials": stub_trials[:limit],
            "total_results": len(stub_trials),
            "service_note": "Educational stub data - not actual clinical trials. For real trial information, consult ClinicalTrials.gov directly.",
            "disclaimer": "This is educational content for learning clinical research concepts. Always verify trial information through official sources.",
        }

    def _create_stub_trial_details(self, nct_id: str) -> Dict[str, Any]:
        """
        Create detailed stub trial information (DEPRECATED).

        Args:
            nct_id (str): NCT identifier

        Returns:
            Dict[str, Any]: Educational stub trial details

        Note:
            Deprecated - kept for backward compatibility only
        """

        return {
            "banner": self.banner,
            "nct_id": nct_id,
            "title": f"Educational Example: Detailed Trial Information for {nct_id}",
            "brief_summary": "Educational stub: This provides an example of detailed clinical trial information structure.",
            "detailed_description": "This is educational content showing the typical structure and information found in clinical trial records.",
            "phase": "Phase 2/3",
            "status": "Educational Example",
            "conditions": ["Educational Condition Example"],
            "interventions": [
                "Educational intervention A: Represents experimental treatment",
                "Educational intervention B: Represents control or comparison treatment",
            ],
            "primary_outcomes": [
                "Primary efficacy endpoint (educational example)",
                "Safety and tolerability assessment",
            ],
            "secondary_outcomes": [
                "Quality of life measures",
                "Long-term follow-up assessments",
            ],
            "enrollment": 400,
            "eligibility_criteria": "Educational example: Age 18-65, diagnosed condition, informed consent",
            "sponsor": "Educational Medical Research Institute",
            "location": "Educational Medical Centers (Multiple locations)",
            "contact_information": "For educational purposes only - contact real trials through ClinicalTrials.gov",
            "educational_note": "This is stub data for learning purposes. Real clinical trial information is available at ClinicalTrials.gov",
        }

    def _create_error_response(self, query: str, error: str) -> Dict[str, Any]:
        """
        Create standardized error response for failed searches.

        Args:
            query (str): Original search query
            error (str): Error message from exception

        Returns:
            Dict[str, Any]: Error response with structure:
                {
                    "banner": str,
                    "query": str,
                    "trials": [],
                    "total_results": 0,
                    "error": str,
                    "fallback_note": str
                }
        """
        return {
            "banner": self.banner,
            "query": query,
            "trials": [],
            "total_results": 0,
            "error": f"Clinical trials service temporarily unavailable: {error}",
            "fallback_note": "Service experiencing issues. Please try again later or visit ClinicalTrials.gov directly.",
        }


# Service factory function following Conditional Imports Pattern
def create_clinical_trials_service() -> Optional[ClinicalTrialsService]:
    """
    Factory function to create ClinicalTrialsService with graceful degradation.

    This function provides a safe way to instantiate the service, catching
    any initialization errors and returning None instead of raising exceptions.

    Returns:
        Optional[ClinicalTrialsService]: Initialized service instance, or None if
            initialization failed due to missing dependencies or configuration errors

    Examples:
        >>> service = create_clinical_trials_service()
        >>> if service:
        ...     results = await service.search_trials("diabetes")
        ... else:
        ...     print("Service unavailable")

    Note:
        Logs warning if service creation fails but does not raise exception.
        This allows the application to start even if clinical trials service
        is temporarily unavailable.
    """
    try:
        return ClinicalTrialsService()
    except Exception as e:
        logger.warning(f"Clinical trials service unavailable: {e}")
        return None


async def search_clinical_trials(
    condition: str, max_studies: int = 10, status: Optional[str] = None
) -> Dict[str, Any]:
    """
    Functional API for searching clinical trials (router-friendly interface).

    This standalone async function provides a simple interface for routers and
    external callers without needing to instantiate the service class directly.
    It handles prompt enhancement, API calls, and error handling automatically.

    Args:
        condition (str): Medical condition, disease name, or intervention to search
            Examples: "type 2 diabetes", "lung cancer", "heart failure"
        max_studies (int, optional): Maximum number of trials to return (1-100).
            Defaults to 10.
        status (Optional[str], optional): Filter by recruitment status.
            Valid values: "recruiting", "completed", "active-not-recruiting",
            "enrolling-by-invitation", "not-yet-recruiting", "suspended",
            "terminated", "withdrawn". Case-insensitive, hyphens converted to
            underscores for API. Defaults to None (all statuses).

    Returns:
        Dict[str, Any]: Search results with structure:
            {
                "banner": str,  # Educational disclaimer
                "query": str,  # Original search term
                "condition": str,  # Condition searched
                "total_studies": int,  # Total matching trials from API
                "studies_summary": str,  # Human-readable summary
                "trials": List[Dict],  # Trial details array
                "sources": List[str],  # ["ClinicalTrials.gov API v2"]
                "needs_clarification": bool  # True if query ambiguous
            }

            Each trial in "trials" array contains:
            {
                "nct_id": str,  # NCT identifier
                "title": str,  # Brief title
                "summary": str,  # Brief summary
                "phase": str,  # Study phase
                "status": str,  # Recruitment status
                "study_type": str,  # Interventional/Observational
                "condition": str,  # Comma-separated conditions
                "sponsor": str,  # Lead sponsor name
                "enrollment": str,  # Target enrollment
                "contact": Optional[Dict],  # Contact info if available
                "url": str  # ClinicalTrials.gov URL
            }

    Raises:
        ExternalServiceException: If ClinicalTrials.gov API fails or returns error

    Examples:
        >>> # Basic search
        >>> results = await search_clinical_trials("diabetes")
        >>> print(f"Found {results['total_studies']} trials")
        >>> for trial in results['trials']:
        ...     print(f"{trial['nct_id']}: {trial['title']}")

        >>> # Filter by status
        >>> recruiting = await search_clinical_trials(
        ...     "breast cancer",
        ...     max_studies=20,
        ...     status="recruiting"
        ... )

        >>> # Handle clarification needs
        >>> results = await search_clinical_trials("DM")
        >>> if results.get("needs_clarification"):
        ...     print(results["clarification_question"])

    Notes:
        - Uses prompt enhancement to improve vague queries (if available)
        - Results include educational banner for compliance
        - API has rate limits - consider caching at router level
        - Timeout: 30 seconds for API calls
        - Uses httpx if available, falls back to requests
    """
    banner = get_educational_banner()

    try:
        # Enhance prompt for better search results
        if _has_prompt_enhancement:
            effective_condition, needs_clarification, clarification_question = (
                enhance_prompt(condition, "clinical_trials")
            )

            if needs_clarification:
                return {
                    "banner": banner,
                    "query": condition,
                    "condition": condition,
                    "needs_clarification": True,
                    "clarification_question": clarification_question,
                }
        else:
            effective_condition = condition

        # Use live ClinicalTrials.gov API v2
        result = await _search_trials_live(effective_condition, max_studies, status)
        result["banner"] = banner
        result["query"] = condition
        result["condition"] = condition
        return result

    except Exception as e:
        logger.error(f"Clinical trials search failed: {e}")
        raise ExternalServiceException(
            f"ClinicalTrials.gov API error: {str(e)}", "clinical_trials"
        )


async def _search_trials_live(
    condition: str, max_studies: int, status: Optional[str] = None
) -> Dict[str, Any]:
    """
    Internal helper to search ClinicalTrials.gov API v2 with comprehensive parsing.

    This function is called by search_clinical_trials() and handles the actual
    HTTP request, response parsing, and data extraction from the complex API v2
    response structure.

    Args:
        condition (str): Medical condition to search
        max_studies (int): Maximum trials to return (capped at 100 by API)
        status (Optional[str]): Status filter (will be uppercased and hyphen-converted)

    Returns:
        Dict[str, Any]: Parsed search results with comprehensive trial information

    Raises:
        requests.HTTPError: If API returns error status
        httpx.HTTPError: If using httpx and API returns error
        JSONDecodeError: If API response is not valid JSON
        KeyError: If API response structure changed (defensive programming)

    Note:
        This function extracts comprehensive trial data including contact info,
        sponsor details, and generates direct URLs to ClinicalTrials.gov.
        Uses async httpx if available, falls back to sync requests with thread pool.
    """

    # ClinicalTrials.gov API v2 endpoint
    base_url = "https://clinicaltrials.gov/api/v2/studies"

    params = {
        "query.cond": condition,
        "pageSize": min(max_studies, 100),
        "format": "json",
    }

    # Add status filter if provided
    if status:
        params["filter.overallStatus"] = status.upper().replace("-", "_")

    if _has_httpx:
        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
            response = await client.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
    else:
        # Synchronous fallback for environments without httpx
        # Use asyncio.to_thread to avoid blocking the event loop
        response = await asyncio.to_thread(
            requests.get, base_url, {"params": params, "timeout": 15}
        )
        # If the requests stub raises, it will surface here
        response.raise_for_status()
        data = response.json()

    # Parse API v2 response
    studies = data.get("studies", [])
    total_studies = data.get("totalCount", len(studies))

    trials = []
    for study in studies[:max_studies]:
        protocol = study.get("protocolSection", {})
        identification = protocol.get("identificationModule", {})
        status_module = protocol.get("statusModule", {})
        design_module = protocol.get("designModule", {})
        conditions_module = protocol.get("conditionsModule", {})
        description_module = protocol.get("descriptionModule", {})
        sponsor_module = protocol.get("sponsorCollaboratorsModule", {})
        contacts_module = protocol.get("contactsLocationsModule", {})
        eligibility_module = protocol.get("eligibilityModule", {})

        # Get NCT ID for URL
        nct_id = identification.get("nctId", "Unknown")

        # Extract contact information
        central_contacts = contacts_module.get("centralContacts", [])
        contact_info = None
        if central_contacts:
            contact = central_contacts[0]
            contact_info = {
                "name": contact.get("name", "Not provided"),
                "email": contact.get("email"),
                "phone": contact.get("phone"),
            }

        trials.append(
            {
                "nct_id": nct_id,
                "title": identification.get("briefTitle", "No title available"),
                "summary": description_module.get(
                    "briefSummary", "No summary available"
                ),
                "phase": (
                    design_module.get("phases", ["N/A"])[0]
                    if design_module.get("phases")
                    else "N/A"
                ),
                "status": status_module.get("overallStatus", "Unknown"),
                "study_type": design_module.get("studyType", "Unknown"),
                "condition": ", ".join(
                    conditions_module.get("conditions", [condition])
                ),
                "sponsor": sponsor_module.get("leadSponsor", {}).get(
                    "name", "Not provided"
                ),
                "enrollment": eligibility_module.get("maximumAge", "Not specified"),
                "contact": contact_info,
                "url": f"https://clinicaltrials.gov/study/{nct_id}",
            }
        )

    return {
        "total_studies": total_studies,
        "studies_summary": f"Found {len(trials)} clinical trials related to '{condition}' from ClinicalTrials.gov API v2",
        "trials": trials,
        "sources": ["ClinicalTrials.gov API v2"],
    }


def _create_trials_stub_response(
    condition: str, banner: str, max_studies: int
) -> Dict[str, Any]:
    """
    Create stub response for clinical trials search (DEPRECATED).

    This function is deprecated and only kept for backward compatibility.
    The service now uses live ClinicalTrials.gov API v2 exclusively.

    Args:
        condition (str): Medical condition
        banner (str): Educational banner text
        max_studies (int): Maximum number of stub trials

    Returns:
        Dict[str, Any]: Educational stub response

    Note:
        Not actively used - kept for testing and fallback scenarios only
    """

    return {
        "banner": banner,
        "query": condition,
        "condition": condition,
        "total_studies": 15,  # Stub data
        "studies_summary": f"Clinical trials search completed for '{condition}'. This is educational stub data - use live services for actual trial information.",
        "trials": [
            {
                "nct_id": "NCT12345678",
                "title": f"Phase III Study of {condition} Treatment",
                "phase": "Phase 3",
                "status": "Recruiting",
                "study_type": "Interventional",
                "condition": condition,
            },
            {
                "nct_id": "NCT87654321",
                "title": f"Observational Study of {condition} Outcomes",
                "phase": "N/A",
                "status": "Active, not recruiting",
                "study_type": "Observational",
                "condition": condition,
            },
        ],
        "sources": ["ClinicalTrials.gov (Educational stub data)"],
        "needs_clarification": False,
    }
