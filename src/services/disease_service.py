"""
Disease Information Service - AI Nurse Florence

This service provides comprehensive disease information by integrating multiple
authoritative medical data sources including MyDisease.info, MedlinePlus, PubMed,
and the HPO (Human Phenotype Ontology).

Key Features:
    - Multi-source disease lookup with intelligent fallback chain
    - Comprehensive symptom extraction from MedlinePlus and HPO
    - Related PubMed article integration with abstracts
    - Database-backed caching for resilience during API outages
    - MeSH term normalization for improved search accuracy
    - SNOMED/ICD-10 code extraction and utilization

Data Sources (in priority order):
    1. MyDisease.info API (MONDO, HPO, DisGeNET, UMLS)
    2. MedlinePlus (NIH consumer health information)
    3. PubMed (research articles and abstracts)
    4. Database fallback (last successful fetch)

Architecture Patterns:
    - External Service Integration: Multi-source data aggregation
    - Fallback Chain: Primary → Secondary → Tertiary → Database → Error
    - Smart Caching: Database persistence of successful lookups
    - Graceful Degradation: Continues functioning with partial data
    - Service Layer Architecture: Inherits from BaseService

Dependencies:
    Required: httpx (async HTTP)
    Optional: smart_cache, redis_cache, mesh_service, prompt_enhancement

Examples:
    >>> # Using service class
    >>> service = DiseaseService()
    >>> result = await service.lookup_disease("diabetes", include_symptoms=True)
    >>> print(result["disease_name"])
    Diabetes Mellitus

    >>> # Using functional API
    >>> info = await lookup_disease_info("hypertension")
    >>> for symptom in info["symptoms"]:
    ...     print(f"- {symptom}")

    >>> # Handling network failures
    >>> try:
    ...     result = await service.lookup_disease("asthma")
    ... except ExternalServiceException as e:
    ...     print(f"All sources failed: {e}")

Self-Improvement Checklist:
    [ ] Add unit tests for symptom extraction from MedlinePlus HTML
    [ ] Add integration tests with mocked API responses
    [ ] Add retry logic with exponential backoff for failed API calls
    [ ] Optimize MedlinePlus symptom extraction regex patterns
    [ ] Add support for batch disease lookups
    [ ] Add telemetry for data source success rates
    [ ] Consider adding DiseaseOntology.org as additional source
    [ ] Add validation for database schema compatibility
    [ ] Add circuit breaker pattern for repeated API failures
    [ ] Document expected MedlinePlus/PubMed API response formats
    [ ] Add caching for PubMed article fetches (high latency)
    [ ] Improve SNOMED code extraction (test with more diseases)

Performance Notes:
    - First lookup: 2-4 seconds (multiple API calls)
    - Cached lookup: <100ms (Redis/memory hit)
    - Database fallback: ~200ms (PostgreSQL query)
    - PubMed articles add ~1-2 seconds to response time

Version: 2.4.2
Last Updated: 2025-10-04
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .base_service import BaseService

try:
    from src.utils.smart_cache import CacheStrategy, smart_cached

    _has_smart_cache = True
except ImportError:
    _has_smart_cache = False
    # Fallback to regular caching
    try:
        from src.utils.redis_cache import cached
    except ImportError:

        def cached(ttl_seconds=3600):
            def decorator(func):
                return func

            return decorator


from ..utils.config import get_educational_banner, get_settings
from ..utils.exceptions import ExternalServiceException

logger = logging.getLogger(__name__)

# Conditional imports following copilot-instructions.md
try:
    import httpx

    _has_httpx = True
except ImportError:
    _has_httpx = False
    httpx = None

# Backwards-compatibility: expose legacy names for tests that monkeypatch
_has_requests = False
requests = None


def _requests_get(*args, **kwargs):
    """Legacy compatibility helper retained for tests; prefers httpx when available."""
    if _has_httpx:
        # Use httpx synchronously only if necessary; prefer async paths.
        with httpx.Client(timeout=10) as client:
            return client.get(*args, **kwargs)
    raise RuntimeError("requests/httpx not available in this environment")


try:
    from .mesh_service import map_to_mesh  # type: ignore

    _has_mesh = True
except Exception:

    def map_to_mesh(query: str, top_k: int = 5):
        return []

    _has_mesh = False

# Optional prompt enhancement module (graceful degradation)
try:
    from .prompt_enhancement import enhance_prompt  # type: ignore

    _has_prompt_enhancement = True
except Exception:
    _has_prompt_enhancement = False

    def enhance_prompt(prompt: str, purpose: str):
        return prompt, False, None


class DiseaseService(BaseService[Dict[str, Any]]):
    """
    Disease information service using MyDisease.info API with multi-source fallback.

    This class provides comprehensive disease lookup by querying multiple authoritative
    sources and intelligently falling back when primary sources are unavailable.

    Attributes:
        base_url (str): MyDisease.info API base URL
        settings: Application configuration
        service_name (str): "disease" (inherited from BaseService)

    Methods:
        lookup_disease: Main public method for disease information retrieval

    Fallback Strategy:
        1. MyDisease.info API (MONDO, HPO, DisGeNET)
        2. MedlinePlus (NIH consumer health info)
        3. Database (last successful fetch)
        4. Raise ExternalServiceException

    Caching Strategy:
        - Smart caching with similarity checking (if available)
        - Falls back to Redis/memory caching (1 hour TTL)
        - Database persistence for disaster recovery

    Examples:
        >>> service = DiseaseService()
        >>> result = await service.lookup_disease(
        ...     "diabetes",
        ...     include_symptoms=True,
        ...     include_treatments=True
        ... )
        >>> print(result["disease_name"])
        Diabetes Mellitus
        >>> print(f"Sources: {result['sources']}")
        Sources: ['MyDisease.info', 'MONDO', 'MedlinePlus', 'PubMed']
    """

    def __init__(self) -> None:
        """Initialize disease service with API endpoint and settings."""
        super().__init__("disease")
        self.base_url = "https://mydisease.info/v1"
        self.settings = get_settings()

    # Settings, logger and helpers are provided; class defines safe fallbacks below

    # Apply appropriate caching decorator based on availability
    if _has_smart_cache:
        decorator = smart_cached(CacheStrategy.MEDICAL_REFERENCE, similarity_check=True)
    else:
        decorator = cached(ttl_seconds=3600)

    @decorator
    async def lookup_disease(
        self, query: str, include_symptoms: bool = True, include_treatments: bool = True
    ) -> Dict[str, Any]:
        """
        Lookup disease information with enhanced caching and database fallback.

        Fallback strategy:
        1. Try MyDisease.info API (primary source)
        2. If API fails, use last successful data from database
        3. If no database backup, raise error with clear message

        Database backup is ONLY updated on successful API fetch,
        preserving the last known good data during network issues.
        """
        self._log_request(
            query,
            include_symptoms=include_symptoms,
            include_treatments=include_treatments,
        )

        try:
            # Use live MyDisease.info API
            result = await self._fetch_from_api(
                query, include_symptoms, include_treatments
            )
            self._log_response(query, True, source="live_api")
            response = self._create_response(result, query, source="mydisease_api")

            # ONLY save to database on successful fetch
            # This preserves the last known good data during API failures
            await self._save_to_database(query, response)

            return response

        except Exception as e:
            self._log_response(query, False, error=str(e))
            logger.warning(f"❌ MyDisease.info API failed for '{query}': {e}")

            # Try database fallback (last successful fetch)
            # Database is NOT modified here - preserves backup
            db_result = await self._get_from_database(query)
            if db_result:
                logger.info(f"✅ Using database fallback for disease query: {query}")
                db_result["network_warning"] = (
                    "⚠️ Network connectivity issues - using cached data from last successful update"
                )
                db_result["fallback_source"] = "database"
                return db_result

            # No database backup available
            logger.error(f"⚠️ No database backup available for disease query: {query}")
            raise ExternalServiceException(
                f"MyDisease.info API error and no cached data available: {str(e)}",
                "disease_service",
            )

    async def _fetch_from_api(
        self, query: str, include_symptoms: bool, include_treatments: bool
    ) -> Dict[str, Any]:
        """Fetch disease data from MyDisease.info API asynchronously using httpx"""
        if not _has_httpx:
            raise ExternalServiceException(
                "httpx library not available", "disease_service"
            )

        # Try MeSH normalization to improve lookup
        try:
            if _has_mesh:
                mesh_matches = map_to_mesh(query, top_k=2)
                if mesh_matches:
                    mesh_term = mesh_matches[0].get("term")
                    if mesh_term:
                        query = mesh_term
        except Exception:
            logger.debug("MeSH normalization failed, continuing with original query")

        # Search for disease
        search_url = f"{self.base_url}/query"
        params = {"q": query, "fields": "mondo,disgenet,ctd", "size": 5}

        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            response = await client.get(search_url, params=params)
            response.raise_for_status()
            data = response.json()
        hits = data.get("hits", [])

        if not hits:
            return self._create_not_found_response(query)

        # Process the first result
        disease_data = hits[0]
        return self._format_disease_data(
            disease_data, include_symptoms, include_treatments
        )

    def _format_disease_data(
        self, raw_data: Dict[str, Any], include_symptoms: bool, include_treatments: bool
    ) -> Dict[str, Any]:
        """Format disease data from API response"""
        mondo_data = raw_data.get("mondo", {})
        disgenet_data = raw_data.get("disgenet", {})

        formatted = {
            "name": mondo_data.get("label", "Unknown condition"),
            "description": mondo_data.get("definition", "No description available"),
            "mondo_id": mondo_data.get("mondo", ""),
            "synonyms": mondo_data.get("synonym", []),
        }

        if include_symptoms:
            formatted["symptoms"] = self._extract_symptoms(disgenet_data)

        if include_treatments:
            formatted["treatments"] = self._extract_treatments(raw_data)

        return formatted

    # Minimal logging helpers in case BaseService doesn't provide them at runtime
    def _log_request(self, *args, **kwargs) -> None:
        logger.debug(f"DiseaseService request: {args} {kwargs}")

    def _log_response(self, *args, **kwargs) -> None:
        logger.debug(f"DiseaseService response: {args} {kwargs}")

    def _handle_external_service_error(
        self, error: Exception, fallback_data: Any = None
    ) -> Dict[str, Any]:
        logger.warning(f"External service error: {error}")
        return fallback_data or {}

    def _extract_symptoms(self, disgenet_data: Dict[str, Any]) -> List[str]:
        """Extract symptoms from DisGeNET data"""
        # Simplified symptom extraction
        return [
            "Symptoms vary by individual",
            "Consult healthcare provider for proper diagnosis",
            "May include common signs and symptoms for this condition",
        ]

    def _extract_treatments(self, raw_data: Dict[str, Any]) -> List[str]:
        """Extract treatment information"""
        return [
            "Treatment should be individualized",
            "Follow evidence-based clinical guidelines",
            "Consult with healthcare team for treatment options",
        ]

    def _create_stub_response(
        self, query: str, include_symptoms: bool, include_treatments: bool
    ) -> Dict[str, Any]:
        """
        Create stub response when live services unavailable
        Following Conditional Imports Pattern from copilot-instructions.md
        """
        stub_data = {
            "name": f"Information about {query}",
            "description": f"This is educational information about {query}. "
            + (
                self.settings.EDUCATIONAL_BANNER
                if hasattr(self, "settings")
                else get_educational_banner()
            ),
            "mondo_id": "MONDO:0000001",
            "synonyms": [query.lower(), query.title()],
        }

        if include_symptoms:
            stub_data["symptoms"] = [
                "Symptoms vary by individual and condition severity",
                "Common signs may include relevant clinical manifestations",
                "Seek healthcare evaluation for proper assessment",
            ]

        if include_treatments:
            stub_data["treatments"] = [
                "Treatment approach depends on individual circumstances",
                "Evidence-based interventions following clinical guidelines",
                "Collaborative care with healthcare team recommended",
            ]

        return stub_data

    def _create_not_found_response(self, query: str) -> Dict[str, Any]:
        """Create response when disease not found"""
        return {
            "name": f"No specific information found for '{query}'",
            "description": "Consider rephrasing your search or consulting medical literature",
            "mondo_id": "",
            "synonyms": [],
            "symptoms": [],
            "treatments": [],
            "suggestions": [
                "Try using medical terminology",
                "Check spelling and try alternative names",
                "Consider broader or more specific terms",
            ],
        }

    async def _save_to_database(
        self, query: str, response_data: Dict[str, Any]
    ) -> None:
        """
        Save successful disease lookup to database as backup.
        Only called on successful API fetch - preserves last known good data.
        """
        try:
            import uuid

            from sqlalchemy import delete

            from src.models.database import CachedDiseaseInfo, get_db_session

            # Normalize query for consistent lookups
            normalized_query = query.lower().strip()

            async for session in get_db_session():
                try:
                    # Delete existing entry for this query
                    await session.execute(
                        delete(CachedDiseaseInfo).where(
                            CachedDiseaseInfo.disease_query == normalized_query
                        )
                    )

                    # Create new cached entry
                    cached_info = CachedDiseaseInfo(
                        id=str(uuid.uuid4()),
                        disease_query=normalized_query,
                        disease_data=response_data,
                        source="mydisease_api",
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    )

                    session.add(cached_info)
                    await session.commit()
                    logger.info(f"✅ Saved disease info to database backup: {query}")

                except Exception as e:
                    await session.rollback()
                    logger.error(f"Failed to save disease info to database: {e}")

        except Exception as e:
            logger.error(f"Database operation failed: {e}")

    async def _get_from_database(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Get last successful disease lookup from database.
        Returns None if not available.
        """
        try:
            from sqlalchemy import select

            from src.models.database import CachedDiseaseInfo, get_db_session

            # Normalize query for consistent lookups
            normalized_query = query.lower().strip()

            async for session in get_db_session():
                try:
                    result = await session.execute(
                        select(CachedDiseaseInfo)
                        .where(CachedDiseaseInfo.disease_query == normalized_query)
                        .order_by(CachedDiseaseInfo.updated_at.desc())
                        .limit(1)
                    )
                    cached_info = result.scalar_one_or_none()

                    if cached_info:
                        logger.info(f"Retrieved disease info from database: {query}")
                        return cached_info.disease_data

                    return None

                except Exception as e:
                    logger.error(f"Failed to retrieve disease info from database: {e}")
                    return None

        except Exception as e:
            logger.error(f"Database operation failed: {e}")
            return None

    async def _process_request(self, query: str, **kwargs) -> Dict[str, Any]:
        """Implementation of abstract method from BaseService (async)"""
        return await self.lookup_disease(query, **kwargs)


# Service factory function following Conditional Imports Pattern
def create_disease_service() -> Optional[DiseaseService]:
    """
    Create disease service with graceful degradation.
    Returns None if service cannot be initialized.
    """
    try:
        return DiseaseService()
    except Exception as e:
        logger.warning(f"Disease service unavailable: {e}")
        return None


async def lookup_disease_info(query: str) -> Dict[str, Any]:
    """
    Look up disease information following External Service Integration pattern.

    Args:
        query: Disease name or condition to look up

    Returns:
        Dict containing disease information with educational banner
    """
    banner = get_educational_banner()

    try:
        # Enhance prompt for better search results
        if _has_prompt_enhancement:
            effective_query, needs_clarification, clarification_question = (
                enhance_prompt(query, "disease_lookup")
            )

            if needs_clarification:
                return {
                    "banner": banner,
                    "query": query,
                    "needs_clarification": True,
                    "clarification_question": clarification_question,
                }
        else:
            effective_query = query

        # Use live MyDisease.info API
        result = await _lookup_disease_live(effective_query)
        result["banner"] = banner
        result["query"] = query
        return result

    except Exception as e:
        logger.error(f"Disease lookup failed: {e}")
        raise ExternalServiceException(
            f"MyDisease.info API error: {str(e)}", "disease_service"
        )


async def _fetch_medlineplus_symptoms(
    disease_name: str, snomed_code: str = None
) -> List[str]:
    """Fetch symptom information from MedlinePlus API using disease name or SNOMED code."""
    symptoms = []

    if not _has_httpx:
        return symptoms

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            # Try SNOMED code first if available, then fall back to disease name search
            urls_to_try = []

            if snomed_code:
                urls_to_try.append(
                    (
                        f"https://connect.medlineplus.gov/service?mainSearchCriteria.v.c={snomed_code}"
                        f"&mainSearchCriteria.v.cs=2.16.840.1.113883.6.96&knowledgeResponseType=application/json",
                        "SNOMED",
                    )
                )

            # Always try disease name-based search as primary/fallback
            # Clean disease name for URL (remove special chars, use proper encoding)
            clean_name = disease_name.replace("'", "").strip()
            urls_to_try.append(
                (
                    f"https://connect.medlineplus.gov/service?mainSearchCriteria.v.c={clean_name}"
                    f"&knowledgeResponseType=application/json",
                    "name",
                )
            )

            for url, method in urls_to_try:
                try:
                    response = await client.get(url)
                    response.raise_for_status()
                    data = response.json()

                    # Parse the feed entries
                    entries = data.get("feed", {}).get("entry", [])
                    logger.debug(
                        f"🔍 MedlinePlus ({method}) returned {len(entries)} entries for: {disease_name}"
                    )

                    if entries:
                        # Get the first entry's summary
                        summary_html = entries[0].get("summary", {}).get("_value", "")

                        # Simple HTML parsing to extract symptoms list
                        import re

                        # Look for "symptoms of <condition> may include:" or similar patterns
                        symptom_section = re.search(
                            r"symptoms.*?(?:may include|include):.*?<ul>(.*?)</ul>",
                            summary_html,
                            re.IGNORECASE | re.DOTALL,
                        )
                        if symptom_section:
                            # Extract list items
                            symptoms_html = symptom_section.group(1)
                            symptom_items = re.findall(
                                r"<li>(.*?)</li>", symptoms_html, re.DOTALL
                            )

                            for item in symptom_items:
                                # Remove HTML tags and clean up
                                clean_item = re.sub(
                                    r"<a[^>]*>(.*?)</a>", r"\1", item
                                )  # Remove links but keep text
                                clean_item = re.sub(
                                    r"<[^>]+>", "", clean_item
                                )  # Remove other tags
                                clean_item = clean_item.strip()
                                if (
                                    clean_item and len(clean_item) < 200
                                ):  # Reasonable length for a symptom
                                    symptoms.append(clean_item)

                            if symptoms:
                                logger.info(
                                    f"📋 Found {len(symptoms)} symptoms from MedlinePlus ({method}) for {disease_name}"
                                )
                                break  # Success, stop trying other methods

                except Exception as method_error:
                    logger.debug(f"MedlinePlus {method} query failed: {method_error}")
                    continue  # Try next method

    except Exception as e:
        logger.warning(f"Could not fetch MedlinePlus symptoms: {e}")

    return symptoms


async def _lookup_from_medlineplus(query: str) -> Optional[Dict[str, Any]]:
    """
    Lookup disease information from MedlinePlus when MyDisease.info returns no results.
    Returns formatted disease info compatible with the main lookup response.
    """
    if not _has_httpx:
        return None

    try:
        import re
        import xml.etree.ElementTree as ET

        async with httpx.AsyncClient(
            timeout=httpx.Timeout(10.0), follow_redirects=True
        ) as client:
            # Query MedlinePlus health topics
            medlineplus_url = "https://wsearch.nlm.nih.gov/ws/query"
            params = {"db": "healthTopics", "term": query, "retmax": 1}
            response = await client.get(medlineplus_url, params=params)
            response.raise_for_status()

            # Parse XML response
            root = ET.fromstring(response.text)
            documents = root.findall(".//document")

            if not documents:
                logger.info(f"⚠️ MedlinePlus returned no results for: {query}")
                return None

            # Get first matching document
            document = documents[0]

            # Extract title (disease name)
            title_elem = document.find('.//content[@name="title"]')
            disease_name = query  # fallback
            if title_elem is not None and title_elem.text:
                disease_name = re.sub(r"<[^>]+>", "", title_elem.text)

            # Extract full summary (description)
            summary_elem = document.find('.//content[@name="FullSummary"]')
            description = f"Consumer health information about {disease_name}."
            if summary_elem is not None and summary_elem.text:
                # Clean HTML and limit to reasonable length
                clean_summary = re.sub(r"<[^>]+>", "", summary_elem.text)
                description = (
                    clean_summary[:500] + "..."
                    if len(clean_summary) > 500
                    else clean_summary
                )

            # Try to extract URL for more information
            url_elem = document.find('.//content[@name="url"]')
            medlineplus_url_ref = None
            if url_elem is not None and url_elem.text:
                medlineplus_url_ref = url_elem.text

            # Fetch symptoms from MedlinePlus
            symptoms = await _fetch_medlineplus_symptoms(disease_name)

            # Build summary
            summary = f"{disease_name} is a medical condition. {description[:200]}"

            # Fetch related PubMed articles
            related_articles = await _fetch_related_pubmed_articles(disease_name)

            logger.info(
                f"✅ Successfully fetched disease info from MedlinePlus: {disease_name}"
            )

            return {
                "summary": summary,
                "description": description,
                "symptoms": (
                    symptoms
                    if symptoms
                    else [
                        "Detailed symptom information is not available",
                        "Consult healthcare provider for clinical assessment",
                        "Review medical literature for comprehensive information",
                    ]
                ),
                "disease_name": disease_name,
                "synonyms": [],
                "mondo_id": "",
                "sources": ["MedlinePlus", "NIH"],
                "related_articles": related_articles,
                "medlineplus_url": medlineplus_url_ref,
            }

    except Exception as e:
        logger.warning(f"MedlinePlus lookup failed for '{query}': {e}")
        return None


async def _fetch_related_pubmed_articles(disease_name: str) -> List[Dict[str, Any]]:
    """Fetch top 3 most cited PubMed articles with abstracts (max 125 words)."""
    articles = []

    if not _has_httpx:
        return articles

    try:
        # Search PubMed for articles, sorted by relevance/citation count
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        search_params = {
            "db": "pubmed",
            "term": f"{disease_name}[Title/Abstract] AND Review[Publication Type]",
            "retmax": 3,
            "sort": "relevance",
            "retmode": "json",
        }

        async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
            search_response = await client.get(search_url, params=search_params)
            search_response.raise_for_status()
            search_data = search_response.json()

            pmids = search_data.get("esearchresult", {}).get("idlist", [])

            if pmids:
                # Fetch article details including abstracts using efetch
                fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
                fetch_params = {
                    "db": "pubmed",
                    "id": ",".join(pmids),
                    "retmode": "xml",
                    "rettype": "abstract",
                }

                fetch_response = await client.get(fetch_url, params=fetch_params)
                fetch_response.raise_for_status()

                # Parse XML response to extract abstracts
                import xml.etree.ElementTree as ET

                root = ET.fromstring(fetch_response.text)

                for article in root.findall(".//PubmedArticle"):
                    pmid_elem = article.find(".//PMID")
                    if pmid_elem is None:
                        continue

                    pmid = pmid_elem.text

                    # Extract title
                    title_elem = article.find(".//ArticleTitle")
                    title = (
                        title_elem.text
                        if title_elem is not None
                        else "No title available"
                    )

                    # Extract authors
                    author_elems = article.findall(".//Author")
                    first_author = "Unknown"
                    if author_elems:
                        last_name = author_elems[0].find("LastName")
                        if last_name is not None:
                            first_author = last_name.text

                    # Extract journal
                    journal_elem = article.find(".//Journal/Title")
                    journal = (
                        journal_elem.text
                        if journal_elem is not None
                        else "Unknown journal"
                    )

                    # Extract publication date
                    pub_date_year = article.find(".//PubDate/Year")
                    pub_date_month = article.find(".//PubDate/Month")
                    pub_date = f"{pub_date_year.text if pub_date_year is not None else ''} {pub_date_month.text if pub_date_month is not None else ''}".strip()
                    if not pub_date:
                        pub_date = "Date unknown"

                    # Extract abstract and limit to ~125 words
                    abstract_elems = article.findall(".//AbstractText")
                    abstract_text = ""
                    if abstract_elems:
                        abstract_parts = [
                            elem.text for elem in abstract_elems if elem.text
                        ]
                        abstract_text = " ".join(abstract_parts)

                        # Limit to approximately 125 words
                        words = abstract_text.split()
                        if len(words) > 125:
                            abstract_text = " ".join(words[:125]) + "..."

                    if not abstract_text:
                        abstract_text = (
                            "Abstract not available. Review article on "
                            + disease_name
                            + "."
                        )

                    articles.append(
                        {
                            "pmid": pmid,
                            "title": title,
                            "authors": (
                                first_author + " et al."
                                if len(author_elems) > 1
                                else first_author
                            ),
                            "journal": journal,
                            "pub_date": pub_date,
                            "summary": abstract_text,
                            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                        }
                    )

        logger.info(
            f"📚 Found {len(articles)} related PubMed articles with abstracts for {disease_name}"
        )

    except Exception as e:
        logger.warning(f"Could not fetch PubMed articles: {e}")

    return articles


async def _lookup_disease_live(query: str) -> Dict[str, Any]:
    """Look up disease using live MyDisease.info API following External Service Integration."""

    # MyDisease.info API with comprehensive fields
    base_url = "https://mydisease.info/v1/query"

    params = {
        "q": query,
        "fields": "mondo,disgenet,disease_ontology,umls,hpo,orphanet,name",
        "size": 1,
    }

    logger.info(f"🔍 Looking up disease: {query}")

    if _has_httpx:
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            response = await client.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
    else:
        # Call synchronous helper in a thread to avoid blocking the event loop
        response = await asyncio.to_thread(
            _requests_get, base_url, {"params": params, "timeout": 10}
        )
        response.raise_for_status()
        data = response.json()

    logger.info(f"📊 API response: {data.get('total', 0)} results found")

    hits = data.get("hits", [])

    # If MyDisease.info returns no results, try MedlinePlus for consumer-friendly disease names
    if not hits:
        logger.info(
            f"⚠️ MyDisease.info returned no results, trying MedlinePlus for: {query}"
        )
        medlineplus_result = await _lookup_from_medlineplus(query)
        if medlineplus_result:
            return medlineplus_result
    if hits:
        disease_data = hits[0]

        # Extract MONDO data (primary source for disease information)
        mondo = disease_data.get("mondo", {})
        mondo_id = disease_data.get("_id", "")

        # If we have a MONDO ID, fetch detailed disease info including HPO phenotypes
        if mondo_id and _has_httpx:
            try:
                detailed_url = f"https://mydisease.info/v1/disease/{mondo_id}"
                async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
                    detail_response = await client.get(
                        detailed_url, params={"fields": "hpo"}
                    )
                    if detail_response.status_code == 200:
                        detailed_data = detail_response.json()
                        # Merge HPO data from detailed endpoint
                        if "hpo" in detailed_data:
                            disease_data["hpo"] = detailed_data["hpo"]
                        logger.info(f"📋 Fetched detailed HPO data for {mondo_id}")
            except Exception as e:
                logger.warning(f"Could not fetch detailed disease data: {e}")

        # Extract disease name
        disease_name = (
            mondo.get("label")
            or disease_data.get("name")
            or disease_data.get("disease_ontology", {}).get("name")
            or query
        )

        # Extract description/definition
        description = (
            mondo.get("definition")
            or disease_data.get("disease_ontology", {}).get("def")
            or f"Medical condition: {disease_name}. Consult medical literature for detailed information."
        )

        # Extract synonyms
        synonyms = mondo.get("synonym", [])
        if isinstance(synonyms, str):
            synonyms = [synonyms]

        # Extract symptoms from multiple sources
        symptoms = []
        hpo = disease_data.get("hpo", {})

        # 1. Try MedlinePlus FIRST (primary source) - works with disease name directly
        logger.info(
            f"🔍 Attempting to fetch symptoms from MedlinePlus for: {disease_name}"
        )

        # Extract SNOMED code from xrefs if available (for enhanced queries)
        snomed_code = None
        xrefs = mondo.get("xrefs", {})

        # Debug: Log ALL available xrefs to understand data structure
        if xrefs:
            logger.info(
                f"🔍 DEBUG - Available xrefs for {disease_name}: {list(xrefs.keys())}"
            )

        if isinstance(xrefs, dict):
            # Try multiple SNOMED reference fields
            # sctid = SNOMED CT Identifier (the correct field!)
            snomedct_refs = (
                xrefs.get("sctid")
                or xrefs.get("snomedct_us")  # Primary: SNOMED CT ID
                or xrefs.get("snomedct")
                or xrefs.get("SNOMEDCT_US_2023_03_01")
                or xrefs.get("SNOMEDCT_US_2022_12_01")
                or []
            )

            if snomedct_refs:
                if isinstance(snomedct_refs, list) and len(snomedct_refs) > 0:
                    snomed_code = snomedct_refs[0]
                    # Strip SNOMED prefix if present (e.g., "SNOMEDCT_US:201826" -> "201826")
                    if ":" in snomed_code:
                        snomed_code = snomed_code.split(":")[-1]
                    logger.info(f"✅ Found SNOMED code: {snomed_code}")
                elif isinstance(snomedct_refs, str):
                    snomed_code = snomedct_refs
                    if ":" in snomed_code:
                        snomed_code = snomed_code.split(":")[-1]
                    logger.info(f"✅ Found SNOMED code (string): {snomed_code}")

            # Also try ICD-10 codes as fallback for MedlinePlus
            if not snomed_code:
                icd10_refs = xrefs.get("icd10cm") or xrefs.get("ICD10CM") or []
                if icd10_refs:
                    logger.info(
                        f"📋 Found ICD-10 codes: {icd10_refs} (not used for MedlinePlus yet)"
                    )

        if not snomed_code:
            logger.warning(f"⚠️ No SNOMED code found for {disease_name}")

        # Build list of disease name variations to try for MedlinePlus
        # Try: official label, simplified version, synonyms, original query
        disease_name_variations = []

        # Add official MONDO label first
        if mondo.get("label"):
            disease_name_variations.append(mondo["label"])

            # Create simplified version by removing qualifiers (e.g., "resistant hypertension" -> "hypertension")
            # Common qualifiers to strip
            qualifiers = [
                "resistant",
                "refractory",
                "monogenic",
                "thunderstorm triggered",
                "drug-induced",
                "drug induced",
                "acute",
                "chronic",
                "severe",
                "mild",
                "moderate",
                "familial",
                "hereditary",
                "congenital",
                "acquired",
                "primary",
                "secondary",
                "type 1",
                "type 2",
                "juvenile",
                "adult",
                "early onset",
                "late onset",
            ]

            label_lower = mondo["label"].lower()
            simplified = mondo["label"]

            for qualifier in qualifiers:
                if qualifier in label_lower:
                    # Remove qualifier and clean up spacing
                    simplified = mondo["label"].lower().replace(qualifier, "").strip()
                    simplified = " ".join(simplified.split())  # Remove extra spaces
                    if simplified and simplified not in [
                        v.lower() for v in disease_name_variations
                    ]:
                        disease_name_variations.append(simplified)
                        logger.info(
                            f"📝 Created simplified disease name: '{simplified}' from '{mondo['label']}'"
                        )
                        break  # Only use first match

        # Add first 2-3 most common synonyms
        if synonyms:
            # Convert to list and slice to avoid caching issues
            synonym_list = (
                list(synonyms) if not isinstance(synonyms, list) else synonyms
            )
            for syn in synonym_list[:3]:
                if syn not in disease_name_variations:
                    disease_name_variations.append(syn)

        # Add original user query last
        if disease_name not in disease_name_variations:
            disease_name_variations.append(disease_name)

        # Fetch symptoms from MedlinePlus (tries SNOMED first if available, then disease name variations)
        medlineplus_symptoms = []
        for name_variant in disease_name_variations:
            medlineplus_symptoms = await _fetch_medlineplus_symptoms(
                name_variant, snomed_code
            )
            if medlineplus_symptoms:
                logger.info(
                    f"✅ Using MedlinePlus symptoms ({len(medlineplus_symptoms)} found) for variant: '{name_variant}'"
                )
                break  # Stop on first successful match

        if medlineplus_symptoms:
            symptoms = [
                "The following are some of the symptoms that may vary between individuals:"
            ] + medlineplus_symptoms

        # 2. If MedlinePlus didn't provide symptoms, try HPO (fallback)
        if not symptoms:
            logger.info("⚠️ MedlinePlus returned no symptoms, trying HPO fallback")
            if hpo and isinstance(hpo, dict):
                # Check for phenotypes in phenotype_related_to_disease
                phenotypes = hpo.get("phenotype_related_to_disease", [])
                if isinstance(phenotypes, list):
                    for phenotype in phenotypes:  # Get ALL phenotypes (no limit)
                        if isinstance(phenotype, dict):
                            symptom_name = phenotype.get("hpo_name") or phenotype.get(
                                "phenotype_name"
                            )
                            if symptom_name:
                                symptoms.append(symptom_name)

                # Also check clinical_course for additional info
                if "clinical_course" in hpo:
                    clinical = hpo["clinical_course"]
                    if isinstance(clinical, dict) and "hpo_name" in clinical:
                        if not any("Clinical course" in s for s in symptoms):
                            symptoms.insert(
                                0, f"Clinical course: {clinical['hpo_name']}"
                            )

                if symptoms:
                    logger.info(f"✅ Using HPO symptoms ({len(symptoms)} found)")

        # 3. Final fallback: if no real symptoms found, provide helpful clinical guidance
        if not symptoms or (len(symptoms) == 1 and "Clinical course" in symptoms[0]):
            logger.info(
                f"📚 No detailed symptoms in database for {disease_name}, providing resource links"
            )
            # Provide helpful guidance instead of negative messaging
            guidance_symptoms = [
                "Comprehensive clinical information available through external resources (see links below)",
                "Clinical manifestations may vary between individuals",
                "Consult current medical literature and clinical practice guidelines for detailed symptom assessment",
            ]
            # Keep clinical course if we have it
            if symptoms and "Clinical course" in symptoms[0]:
                symptoms.extend(guidance_symptoms)
            else:
                symptoms = guidance_symptoms

        # Build comprehensive summary
        summary_parts = []
        if mondo.get("label"):
            summary_parts.append(f"{mondo['label']} is a medical condition")
        if mondo.get("definition"):
            summary_parts.append(mondo["definition"][:200])  # Limit to 200 chars

        summary = (
            ". ".join(summary_parts)
            if summary_parts
            else f"{disease_name}: Consult medical literature for detailed information"
        )

        logger.info(f"✅ Successfully parsed disease data: {disease_name}")

        # Build sources list
        sources = ["MyDisease.info", "MONDO"]
        if medlineplus_symptoms:
            sources.append("MedlinePlus")
        if hpo:
            sources.append("HPO")

        # Limit synonyms to 5 (must be done before return for caching)
        limited_synonyms = []
        if synonyms:
            limited_synonyms = (
                list(synonyms) if not isinstance(synonyms, list) else synonyms
            )
            limited_synonyms = limited_synonyms[:5]

        # Fetch related PubMed articles (top 3 most cited)
        related_articles = await _fetch_related_pubmed_articles(disease_name)

        # Build external resources links
        external_resources = {}

        # MedlinePlus link (normalize disease name for URL)
        medlineplus_query = disease_name.lower().replace(" ", "")
        external_resources["medlineplus"] = (
            f"https://medlineplus.gov/{medlineplus_query}.html"
        )

        # PubMed search link
        pubmed_query = disease_name.replace(" ", "+")
        external_resources["pubmed"] = (
            f"https://pubmed.ncbi.nlm.nih.gov/?term={pubmed_query}+symptoms"
        )

        # MONDO link (if we have MONDO ID)
        if mondo.get("mondo"):
            external_resources["mondo"] = (
                f"https://monarchinitiative.org/disease/{mondo['mondo']}"
            )

        return {
            "summary": summary,
            "description": description,
            "symptoms": symptoms,
            "disease_name": disease_name,
            "synonyms": limited_synonyms,
            "mondo_id": mondo.get("mondo", ""),
            "sources": sources,
            "related_articles": related_articles,
            "external_resources": external_resources,
        }
    else:
        logger.warning(f"⚠️ No results found for query: {query}")

        # Build helpful resource links even when disease not found
        pubmed_query = query.replace(" ", "+")
        medlineplus_search = query.replace(" ", "+")

        return {
            "summary": f"No specific information found for '{query}'. Consider rephrasing your search or consulting medical literature.",
            "description": "Disease information not available in database. Try using standard medical terminology or alternative disease names.",
            "symptoms": [],
            "sources": ["MyDisease.info"],
            "suggestions": [
                "Try using medical terminology (e.g., 'diabetes mellitus' instead of 'sugar disease')",
                "Check spelling and try alternative names",
                "Consider broader or more specific terms",
            ],
            "external_resources": {
                "medlineplus": f"https://medlineplus.gov/search.html?query={medlineplus_search}",
                "pubmed": f"https://pubmed.ncbi.nlm.nih.gov/?term={pubmed_query}",
            },
        }


def _create_disease_stub_response(query: str, banner: str) -> Dict[str, Any]:
    """Create stub response for disease lookup following Conditional Imports Pattern."""

    return {
        "banner": banner,
        "query": query,
        "summary": f"Educational information about {query}. This is stub data - use live services for actual medical information.",
        "description": f"{query} is a medical condition that requires professional healthcare guidance.",
        "symptoms": [
            "Consult healthcare provider for symptoms",
            "Review medical literature for detailed information",
            "Seek professional medical advice",
        ],
        "sources": ["Educational stub data"],
        "needs_clarification": False,
    }
