"""
MedlinePlus Connect API Integration

Integrates with MedlinePlus Connect API to fetch patient education content
for diagnoses. MedlinePlus is a service of the National Library of Medicine (NLM).

API Documentation: https://medlineplus.gov/connect/
No API key required - free public service

Features:
- Fetch patient education content by ICD-10 code
- Multi-language support (English, Spanish)
- XML parsing to structured data
- Automatic caching (24-hour TTL)
- Fallback to web search if API unavailable
"""

import requests
import xml.etree.ElementTree as ET
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from urllib.parse import quote
import logging

logger = logging.getLogger(__name__)


class MedlinePlusClient:
    """Client for MedlinePlus Connect API"""

    BASE_URL = "https://connect.medlineplus.gov/service"

    # MedlinePlus supports multiple languages
    SUPPORTED_LANGUAGES = {
        "en": "English",
        "es": "Spanish"
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "AI-Nurse-Florence/1.0 (Healthcare Documentation)"
        })

    def fetch_content(
        self,
        icd10_code: str,
        language: str = "en",
        timeout: int = 10
    ) -> Optional[Dict]:
        """
        Fetch patient education content from MedlinePlus Connect API.

        Args:
            icd10_code: ICD-10-CM code (e.g., "E11.9")
            language: Language code ("en" or "es")
            timeout: Request timeout in seconds

        Returns:
            Dict with patient education content or None if not found

        Example:
            >>> client = MedlinePlusClient()
            >>> content = client.fetch_content("E11.9", "en")
            >>> print(content["title"])
            "Type 2 Diabetes"
        """
        try:
            # Build request parameters
            params = {
                "mainSearchCriteria.v.c": icd10_code,
                "mainSearchCriteria.v.cs": "2.16.840.1.113883.6.90",  # ICD-10-CM OID
                "informationRecipient.languageCode.c": language
            }

            logger.info(f"Fetching MedlinePlus content for {icd10_code} ({language})")

            response = self.session.get(
                self.BASE_URL,
                params=params,
                timeout=timeout
            )

            response.raise_for_status()

            # Parse XML response
            content = self._parse_xml_response(response.text)

            if content:
                logger.info(f"Successfully fetched MedlinePlus content for {icd10_code}")
                return content
            else:
                logger.warning(f"No MedlinePlus content found for {icd10_code}")
                return None

        except requests.Timeout:
            logger.error(f"MedlinePlus API timeout for {icd10_code}")
            return None
        except requests.RequestException as e:
            logger.error(f"MedlinePlus API error for {icd10_code}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching MedlinePlus content: {e}")
            return None

    def _parse_xml_response(self, xml_text: str) -> Optional[Dict]:
        """
        Parse MedlinePlus Connect XML response.

        MedlinePlus returns XML in the following format:
        <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <title>Diabetes Type 2</title>
                <link href="https://medlineplus.gov/diabetestype2.html"/>
                <summary>Summary text here...</summary>
            </entry>
        </feed>
        """
        try:
            root = ET.fromstring(xml_text)

            # Define XML namespace
            ns = {"atom": "http://www.w3.org/2005/Atom"}

            # Find first entry
            entry = root.find("atom:entry", ns)
            if entry is None:
                return None

            # Extract content
            title_elem = entry.find("atom:title", ns)
            link_elem = entry.find("atom:link", ns)
            summary_elem = entry.find("atom:summary", ns)

            if title_elem is None:
                return None

            content = {
                "title": title_elem.text or "",
                "url": link_elem.get("href") if link_elem is not None else "",
                "summary": summary_elem.text or "" if summary_elem is not None else "",
                "source": "MedlinePlus",
                "fetched_at": datetime.utcnow().isoformat()
            }

            # Extract additional topics if available
            topics = []
            for topic_entry in root.findall("atom:entry", ns):
                topic_title = topic_entry.find("atom:title", ns)
                topic_link = topic_entry.find("atom:link", ns)
                if topic_title is not None:
                    topics.append({
                        "title": topic_title.text,
                        "url": topic_link.get("href") if topic_link is not None else ""
                    })

            if topics:
                content["related_topics"] = topics

            return content

        except ET.ParseError as e:
            logger.error(f"Error parsing MedlinePlus XML: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error parsing MedlinePlus response: {e}")
            return None

    def get_fallback_url(self, disease_name: str, language: str = "en") -> str:
        """
        Generate fallback MedlinePlus search URL if API fails.

        Args:
            disease_name: Name of disease/condition
            language: Language code

        Returns:
            Direct MedlinePlus search URL
        """
        base_url = "https://medlineplus.gov"
        if language == "es":
            base_url = "https://medlineplus.gov/spanish"

        search_query = quote(disease_name)
        return f"{base_url}/search/?query={search_query}"

    def fetch_multiple(
        self,
        icd10_codes: List[str],
        language: str = "en"
    ) -> Dict[str, Optional[Dict]]:
        """
        Fetch content for multiple ICD-10 codes (batch operation).

        Args:
            icd10_codes: List of ICD-10 codes
            language: Language code

        Returns:
            Dict mapping ICD-10 codes to their content

        Example:
            >>> client = MedlinePlusClient()
            >>> codes = ["E11.9", "I10", "J45.909"]
            >>> results = client.fetch_multiple(codes)
            >>> print(len(results))
            3
        """
        results = {}
        for code in icd10_codes:
            results[code] = self.fetch_content(code, language)
        return results


class MedlinePlusContentEnricher:
    """
    Enriches diagnosis records with MedlinePlus patient education content.

    Handles caching and database updates.
    """

    def __init__(self, db_session):
        self.db = db_session
        self.client = MedlinePlusClient()
        self.cache_ttl_hours = 24

    def enrich_diagnosis(
        self,
        diagnosis_id: str,
        icd10_code: str,
        disease_name: str,
        language: str = "en",
        force_refresh: bool = False
    ) -> Optional[Dict]:
        """
        Enrich a diagnosis with MedlinePlus content.

        Args:
            diagnosis_id: Diagnosis ID in our database
            icd10_code: ICD-10 code
            disease_name: Disease name (for fallback)
            language: Language code
            force_refresh: Force API call even if cached

        Returns:
            MedlinePlus content dict or None
        """
        from src.models.content_settings import MedlinePlusCache

        # Check cache first (unless force refresh)
        if not force_refresh:
            cached = self.db.query(MedlinePlusCache).filter_by(
                icd10_code=icd10_code,
                language=language
            ).first()

            if cached and self._is_cache_valid(cached.cached_at):
                logger.info(f"Using cached MedlinePlus content for {icd10_code}")
                return {
                    "title": cached.title,
                    "url": cached.url,
                    "summary": cached.summary,
                    "source": "MedlinePlus (cached)",
                    "cached_at": cached.cached_at.isoformat()
                }

        # Fetch fresh content from API
        content = self.client.fetch_content(icd10_code, language)

        if content:
            # Update or create cache entry
            self._update_cache(icd10_code, language, content)
            return content
        else:
            # Generate fallback URL
            fallback_url = self.client.get_fallback_url(disease_name, language)
            return {
                "title": f"Search results for {disease_name}",
                "url": fallback_url,
                "summary": "MedlinePlus health information",
                "source": "MedlinePlus (search)",
                "fetched_at": datetime.utcnow().isoformat()
            }

    def _is_cache_valid(self, cached_at: datetime) -> bool:
        """Check if cached content is still valid (within TTL)"""
        expiry = cached_at + timedelta(hours=self.cache_ttl_hours)
        return datetime.utcnow() < expiry

    def _update_cache(self, icd10_code: str, language: str, content: Dict):
        """Update cache in database"""
        from src.models.content_settings import MedlinePlusCache

        try:
            # Try to find existing cache entry
            cached = self.db.query(MedlinePlusCache).filter_by(
                icd10_code=icd10_code,
                language=language
            ).first()

            if cached:
                # Update existing
                cached.title = content.get("title", "")
                cached.url = content.get("url", "")
                cached.summary = content.get("summary", "")
                cached.cached_at = datetime.utcnow()
            else:
                # Create new
                new_cache = MedlinePlusCache(
                    icd10_code=icd10_code,
                    language=language,
                    title=content.get("title", ""),
                    url=content.get("url", ""),
                    summary=content.get("summary", ""),
                    cached_at=datetime.utcnow()
                )
                self.db.add(new_cache)

            self.db.commit()
            logger.info(f"Updated MedlinePlus cache for {icd10_code}")

        except Exception as e:
            logger.error(f"Error updating MedlinePlus cache: {e}")
            self.db.rollback()

    def enrich_batch(
        self,
        diagnoses: List[Dict],
        language: str = "en"
    ) -> Dict[str, Optional[Dict]]:
        """
        Enrich multiple diagnoses in batch.

        Args:
            diagnoses: List of dicts with keys: id, icd10_code, disease_name
            language: Language code

        Returns:
            Dict mapping diagnosis IDs to their MedlinePlus content
        """
        results = {}
        for diagnosis in diagnoses:
            content = self.enrich_diagnosis(
                diagnosis_id=diagnosis["id"],
                icd10_code=diagnosis["icd10_code"],
                disease_name=diagnosis["disease_name"],
                language=language
            )
            results[diagnosis["id"]] = content

        return results


# Convenience functions

def get_medlineplus_content(
    icd10_code: str,
    language: str = "en"
) -> Optional[Dict]:
    """
    Quick function to fetch MedlinePlus content.

    Args:
        icd10_code: ICD-10-CM code
        language: Language code ("en" or "es")

    Returns:
        Content dict or None
    """
    client = MedlinePlusClient()
    return client.fetch_content(icd10_code, language)


def get_patient_education_url(disease_name: str, language: str = "en") -> str:
    """
    Get direct MedlinePlus URL for a disease.

    Args:
        disease_name: Name of disease
        language: Language code

    Returns:
        MedlinePlus URL
    """
    client = MedlinePlusClient()
    return client.get_fallback_url(disease_name, language)


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Test client
    client = MedlinePlusClient()

    # Test single fetch
    print("Testing MedlinePlus API integration...")
    print()

    # Test with common diagnosis
    content = client.fetch_content("E11.9", "en")  # Type 2 Diabetes
    if content:
        print(f"Title: {content['title']}")
        print(f"URL: {content['url']}")
        print(f"Summary: {content['summary'][:100]}...")
        print()
    else:
        print("No content found")
        print()

    # Test fallback URL
    fallback = client.get_fallback_url("Type 2 Diabetes", "en")
    print(f"Fallback URL: {fallback}")
    print()

    # Test Spanish
    content_es = client.fetch_content("E11.9", "es")
    if content_es:
        print(f"Spanish Title: {content_es['title']}")
        print(f"Spanish URL: {content_es['url']}")
    else:
        print("No Spanish content found")
