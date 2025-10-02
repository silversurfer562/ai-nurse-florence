"""
UMLS API Client for ICD-10 to SNOMED CT Code Mapping

This client uses the UMLS (Unified Medical Language System) Metathesaurus API
to map ICD-10-CM codes to SNOMED CT codes, which are required for Epic/EHR integration.

UMLS Account Required:
- Sign up: https://uts.nlm.nih.gov/uts/signup-login
- Free for research/development
- Approval time: 1-2 business days

Usage:
    from src.integrations.umls_client import UMLSClient

    client = UMLSClient(api_key="your-api-key-here")
    snomed_code = client.map_icd10_to_snomed("E11.9")
    # Returns: "44054006" (Type 2 Diabetes in SNOMED CT)
"""

import requests
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import json


class UMLSClient:
    """
    UMLS API client for medical terminology mapping and crosswalks.

    Primary Use Case: Map ICD-10-CM codes to SNOMED CT codes for Epic integration
    """

    BASE_URL = "https://uts-ws.nlm.nih.gov/rest"
    CROSSWALK_ENDPOINT = "/crosswalk/current/source"

    def __init__(self, api_key: str, cache_enabled: bool = True):
        """
        Initialize UMLS client.

        Args:
            api_key: UMLS API key from https://uts.nlm.nih.gov
            cache_enabled: Cache results to reduce API calls
        """
        self.api_key = api_key
        self.cache_enabled = cache_enabled
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

        # In-memory cache (in production, use Redis or database cache)
        self._cache: Dict[str, Dict] = {}

    def map_icd10_to_snomed(self, icd10_code: str) -> Optional[str]:
        """
        Map an ICD-10-CM code to SNOMED CT code.

        Args:
            icd10_code: ICD-10-CM code (e.g., "E11.9")

        Returns:
            SNOMED CT code (e.g., "44054006") or None if not found

        Example:
            >>> client = UMLSClient(api_key="YOUR_KEY")
            >>> client.map_icd10_to_snomed("E11.9")
            "44054006"
        """
        # Check cache first
        if self.cache_enabled and icd10_code in self._cache:
            cached = self._cache[icd10_code]
            if cached.get("snomed_code"):
                return cached["snomed_code"]

        # Clean ICD-10 code (remove dot if present)
        clean_code = icd10_code.replace(".", "")

        # UMLS crosswalk API
        url = f"{self.BASE_URL}{self.CROSSWALK_ENDPOINT}/ICD10CM/{clean_code}"

        try:
            response = self.session.get(
                url,
                params={
                    "apiKey": self.api_key,
                    "targetSource": "SNOMEDCT_US"  # US Edition of SNOMED CT
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()

                # Extract SNOMED CT code from response
                # Response structure: {"result": [{"ui": "C0011860", "name": "...", ...}]}
                if data.get("result") and len(data["result"]) > 0:
                    # The first result is usually the best match
                    result = data["result"][0]

                    # Get SNOMED CT concept ID (different from UMLS CUI)
                    # We need to do another lookup for the actual SNOMED code
                    snomed_code = self._get_snomed_from_umls_cui(result.get("ui"))

                    if snomed_code:
                        # Cache the result
                        if self.cache_enabled:
                            self._cache[icd10_code] = {
                                "snomed_code": snomed_code,
                                "umls_cui": result.get("ui"),
                                "cached_at": datetime.utcnow().isoformat()
                            }
                        return snomed_code

            elif response.status_code == 404:
                print(f"⚠️  No SNOMED CT mapping found for ICD-10: {icd10_code}")
                return None

            else:
                print(f"❌ UMLS API error: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ UMLS API request failed: {e}")
            return None

    def _get_snomed_from_umls_cui(self, umls_cui: str) -> Optional[str]:
        """
        Convert UMLS CUI to SNOMED CT code.

        UMLS CUI (Concept Unique Identifier) is not the same as SNOMED CT code.
        This method looks up the SNOMED CT code from the CUI.

        Args:
            umls_cui: UMLS CUI (e.g., "C0011860")

        Returns:
            SNOMED CT code (e.g., "44054006") or None
        """
        if not umls_cui:
            return None

        url = f"{self.BASE_URL}/content/current/CUI/{umls_cui}/atoms"

        try:
            response = self.session.get(
                url,
                params={
                    "apiKey": self.api_key,
                    "sabs": "SNOMEDCT_US",  # Only SNOMED CT US Edition
                    "ttys": "PT"  # Preferred Terms only
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()

                # Extract SNOMED CT code from atoms
                # Structure: {"result": [{"code": "44054006", "name": "...", ...}]}
                if data.get("result") and len(data["result"]) > 0:
                    # Return the first SNOMED CT code
                    return data["result"][0].get("code")

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to get SNOMED code for CUI {umls_cui}: {e}")

        return None

    def batch_map_icd10_to_snomed(
        self,
        icd10_codes: List[str],
        delay_ms: int = 100
    ) -> Dict[str, Optional[str]]:
        """
        Map multiple ICD-10 codes to SNOMED CT in batch.

        Args:
            icd10_codes: List of ICD-10 codes
            delay_ms: Delay between API calls to avoid rate limiting (milliseconds)

        Returns:
            Dictionary mapping ICD-10 codes to SNOMED CT codes

        Example:
            >>> codes = ["E11.9", "I10", "J45.909"]
            >>> results = client.batch_map_icd10_to_snomed(codes)
            >>> results
            {"E11.9": "44054006", "I10": "38341003", "J45.909": "195967001"}
        """
        import time

        results = {}

        for code in icd10_codes:
            snomed_code = self.map_icd10_to_snomed(code)
            results[code] = snomed_code

            # Delay to avoid rate limiting
            if delay_ms > 0:
                time.sleep(delay_ms / 1000.0)

        return results

    def search_concept(self, search_term: str, source: str = "SNOMEDCT_US") -> List[Dict]:
        """
        Search for a concept in UMLS by name.

        Args:
            search_term: Search query (e.g., "diabetes")
            source: Source vocabulary (default: SNOMEDCT_US)

        Returns:
            List of matching concepts with codes and names

        Example:
            >>> client.search_concept("type 2 diabetes")
            [
                {"code": "44054006", "name": "Diabetes mellitus type 2", "source": "SNOMEDCT_US"},
                ...
            ]
        """
        url = f"{self.BASE_URL}/search/current"

        try:
            response = self.session.get(
                url,
                params={
                    "apiKey": self.api_key,
                    "string": search_term,
                    "sabs": source,
                    "returnIdType": "code",
                    "pageSize": 10
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                results = []

                for item in data.get("result", {}).get("results", []):
                    results.append({
                        "code": item.get("ui"),
                        "name": item.get("name"),
                        "source": item.get("rootSource"),
                        "umls_cui": item.get("ui")
                    })

                return results

        except requests.exceptions.RequestException as e:
            print(f"❌ UMLS search failed: {e}")

        return []

    def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        return {
            "cache_size": len(self._cache),
            "cached_codes": list(self._cache.keys())
        }

    def clear_cache(self):
        """Clear the cache."""
        self._cache = {}
        print("✅ Cache cleared")


# Validation test cases (known mappings for verification)
VALIDATION_TEST_CASES = {
    "E11.9": "44054006",   # Type 2 Diabetes Mellitus
    "I10": "38341003",      # Essential Hypertension
    "J45.909": "195967001", # Asthma, Unspecified
    "E10.9": "46635009",    # Type 1 Diabetes Mellitus
    "I50.9": "84114007",    # Heart Failure, Unspecified
    "N39.0": "68566005",    # UTI, Unspecified
}


def validate_mappings(api_key: str) -> bool:
    """
    Validate UMLS client with known ICD-10 to SNOMED CT mappings.

    Args:
        api_key: UMLS API key

    Returns:
        True if all validations pass, False otherwise
    """
    client = UMLSClient(api_key=api_key)

    print("=" * 70)
    print("UMLS MAPPING VALIDATION")
    print("=" * 70)
    print()

    passed = 0
    failed = 0

    for icd10, expected_snomed in VALIDATION_TEST_CASES.items():
        actual_snomed = client.map_icd10_to_snomed(icd10)

        if actual_snomed == expected_snomed:
            print(f"✅ {icd10} → {actual_snomed} (PASS)")
            passed += 1
        else:
            print(f"❌ {icd10} → Expected: {expected_snomed}, Got: {actual_snomed} (FAIL)")
            failed += 1

    print()
    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python umls_client.py YOUR_API_KEY")
        print()
        print("Get your API key from: https://uts.nlm.nih.gov/uts/")
        sys.exit(1)

    api_key = sys.argv[1]

    # Run validation
    if validate_mappings(api_key):
        print()
        print("✅ All validations passed!")
        print("✅ UMLS client is ready to use")
    else:
        print()
        print("⚠️  Some validations failed")
        print("⚠️  Check your API key and network connection")
        sys.exit(1)
