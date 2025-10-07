"""
Epic FHIR R4 HTTP Client
Production-ready client for Epic FHIR API with OAuth 2.0 authentication
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)

# Remove config dependency - settings will be passed as parameters


class OAuthManager:
    """
    Manage OAuth 2.0 tokens for Epic FHIR API
    Supports client credentials grant with automatic token refresh
    """

    def __init__(
        self,
        token_url: str,
        client_id: str,
        client_secret: str,
        scope: str = "Patient.Read Condition.Read MedicationRequest.Read DocumentReference.Write",
    ):
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope

        self.access_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
        self._lock = asyncio.Lock()

    async def get_access_token(self) -> str:
        """
        Get valid access token (cached or refreshed)
        Thread-safe with lock to prevent multiple simultaneous token requests
        """
        async with self._lock:
            # Check if cached token is still valid (with 60-second buffer)
            if (
                self.access_token
                and self.token_expiry
                and datetime.now() < self.token_expiry - timedelta(seconds=60)
            ):
                logger.debug("Using cached OAuth token")
                return self.access_token

            # Request new token
            logger.info("Requesting new OAuth token from Epic")
            return await self._request_token()

    async def _request_token(self) -> str:
        """
        Request new access token using client credentials grant
        Epic OAuth 2.0 Backend Services: https://fhir.epic.com/Documentation?docId=oauth2
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Client credentials grant
                data = {
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "scope": self.scope,
                }

                logger.debug(f"POST {self.token_url} (OAuth token request)")
                response = await client.post(self.token_url, data=data)

                if response.status_code != 200:
                    error_detail = response.text
                    logger.error(
                        f"OAuth token request failed: {response.status_code} - {error_detail}"
                    )
                    raise Exception(f"Failed to obtain access token: {error_detail}")

                token_data = response.json()
                self.access_token = token_data["access_token"]
                expires_in = token_data.get("expires_in", 3600)  # Default 1 hour
                self.token_expiry = datetime.now() + timedelta(seconds=expires_in)

                logger.info(f"✅ OAuth token obtained, expires in {expires_in} seconds")
                return self.access_token

        except httpx.TimeoutException:
            logger.error("OAuth token request timed out")
            raise Exception("OAuth token request timed out after 30 seconds")
        except Exception as e:
            logger.error(f"OAuth token request failed: {e}", exc_info=True)
            raise

    def is_token_valid(self) -> bool:
        """Check if current token is valid"""
        return (
            self.access_token is not None
            and self.token_expiry is not None
            and datetime.now() < self.token_expiry
        )


class EpicFHIRClient:
    """
    HTTP client for Epic FHIR R4 API
    Handles authentication, rate limiting, retries, and error handling
    """

    def __init__(
        self,
        base_url: str,
        oauth_manager: OAuthManager,
        timeout: float = 30.0,
        max_retries: int = 3,
    ):
        """
        Initialize Epic FHIR client

        Args:
            base_url: Epic FHIR base URL (e.g., https://fhir.epic.com/.../api/FHIR/R4/)
            oauth_manager: OAuth manager for token handling
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts for failed requests
        """
        self.base_url = base_url.rstrip("/")
        self.oauth_manager = oauth_manager
        self.timeout = timeout
        self.max_retries = max_retries

        # Statistics
        self.request_count = 0
        self.error_count = 0
        self.last_request_time: Optional[datetime] = None

    async def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make authenticated GET request to Epic FHIR endpoint

        Args:
            endpoint: FHIR endpoint (e.g., "/Patient", "/Condition")
            params: Query parameters (e.g., {"identifier": "mrn|12345678"})

        Returns:
            FHIR resource or Bundle as dict

        Raises:
            HTTPException: On API errors or network failures
        """
        return await self._request("GET", endpoint, params=params)

    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make authenticated POST request to Epic FHIR endpoint

        Args:
            endpoint: FHIR endpoint (e.g., "/DocumentReference")
            data: FHIR resource to create

        Returns:
            Created FHIR resource as dict

        Raises:
            HTTPException: On API errors or network failures
        """
        return await self._request("POST", endpoint, json_data=data)

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> Dict[str, Any]:
        """
        Internal method to make authenticated FHIR API request with retry logic

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: FHIR endpoint
            params: Query parameters
            json_data: JSON body for POST/PUT
            retry_count: Current retry attempt

        Returns:
            Response JSON

        Raises:
            Exception: On final failure after all retries
        """
        # Get access token
        try:
            access_token = await self.oauth_manager.get_access_token()
        except Exception as e:
            logger.error(f"Failed to obtain access token: {e}")
            self.error_count += 1
            raise

        # Build request
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/fhir+json",
        }

        if json_data:
            headers["Content-Type"] = "application/fhir+json"

        # Log request
        log_params = f"?{params}" if params else ""
        logger.info(f"{method} {endpoint}{log_params}")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method == "GET":
                    response = await client.get(url, headers=headers, params=params)
                elif method == "POST":
                    response = await client.post(url, headers=headers, json=json_data)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                # Update statistics
                self.request_count += 1
                self.last_request_time = datetime.now()

                # Handle response
                if response.status_code == 200 or response.status_code == 201:
                    logger.info(
                        f"✅ {method} {endpoint} -> {response.status_code} ({len(response.content)} bytes)"
                    )
                    return response.json()

                elif response.status_code == 401:
                    # Unauthorized - token might be invalid
                    logger.warning("401 Unauthorized - token may be expired")
                    self.error_count += 1

                    # Retry once with fresh token
                    if retry_count == 0:
                        logger.info("Retrying with fresh OAuth token...")
                        self.oauth_manager.access_token = None  # Force token refresh
                        return await self._request(
                            method, endpoint, params, json_data, retry_count=1
                        )
                    else:
                        raise Exception("Authentication failed after token refresh")

                elif response.status_code == 429:
                    # Rate limited - wait and retry
                    logger.warning("429 Rate Limited - waiting before retry")
                    self.error_count += 1

                    if retry_count < self.max_retries:
                        wait_time = 2**retry_count  # Exponential backoff
                        logger.info(f"Waiting {wait_time} seconds before retry...")
                        await asyncio.sleep(wait_time)
                        return await self._request(
                            method,
                            endpoint,
                            params,
                            json_data,
                            retry_count=retry_count + 1,
                        )
                    else:
                        raise Exception("Rate limit exceeded, max retries reached")

                elif response.status_code >= 500:
                    # Server error - retry
                    logger.error(
                        f"Server error {response.status_code}: {response.text}"
                    )
                    self.error_count += 1

                    if retry_count < self.max_retries:
                        wait_time = 2**retry_count
                        logger.info(
                            f"Server error - waiting {wait_time} seconds before retry..."
                        )
                        await asyncio.sleep(wait_time)
                        return await self._request(
                            method,
                            endpoint,
                            params,
                            json_data,
                            retry_count=retry_count + 1,
                        )
                    else:
                        raise Exception(
                            f"Server error {response.status_code} after {self.max_retries} retries"
                        )

                else:
                    # Client error (4xx) - don't retry
                    error_text = response.text
                    logger.error(f"Request failed {response.status_code}: {error_text}")
                    self.error_count += 1
                    raise Exception(
                        f"Epic FHIR API error {response.status_code}: {error_text}"
                    )

        except httpx.TimeoutException:
            logger.error(f"Request timeout after {self.timeout} seconds")
            self.error_count += 1

            if retry_count < self.max_retries:
                logger.info("Retrying after timeout...")
                return await self._request(
                    method, endpoint, params, json_data, retry_count=retry_count + 1
                )
            else:
                raise Exception(
                    f"Request timeout after {self.max_retries} retry attempts"
                )

        except Exception as e:
            logger.error(f"Request failed: {e}", exc_info=True)
            self.error_count += 1
            raise

    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics"""
        return {
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "error_rate": (
                self.error_count / self.request_count if self.request_count > 0 else 0
            ),
            "last_request": (
                self.last_request_time.isoformat() if self.last_request_time else None
            ),
            "token_valid": self.oauth_manager.is_token_valid(),
            "token_expiry": (
                self.oauth_manager.token_expiry.isoformat()
                if self.oauth_manager.token_expiry
                else None
            ),
        }


# Factory function for creating Epic client
def create_epic_client(
    base_url: Optional[str] = None,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    token_url: Optional[str] = None,
) -> EpicFHIRClient:
    """
    Create Epic FHIR client from settings

    Args:
        base_url: Override epic_fhir_base_url from settings
        client_id: Override epic_client_id from settings
        client_secret: Override epic_client_secret from settings
        token_url: Override epic_oauth_token_url from settings

    Returns:
        Configured EpicFHIRClient instance
    """
    # Validation - all parameters are required now (no settings fallback)
    if not base_url:
        raise ValueError("Epic FHIR base URL is required")
    if not client_id:
        raise ValueError("Epic client ID is required")
    if not client_secret:
        raise ValueError("Epic client secret is required")
    if not token_url:
        raise ValueError("Epic OAuth token URL is required")

    # Create OAuth manager
    oauth_manager = OAuthManager(
        token_url=token_url, client_id=client_id, client_secret=client_secret
    )

    # Create Epic client with default timeout
    epic_client = EpicFHIRClient(
        base_url=base_url,
        oauth_manager=oauth_manager,
        timeout=30,  # Default 30 second timeout
    )

    logger.info(f"Epic FHIR client created for {base_url}")
    return epic_client
