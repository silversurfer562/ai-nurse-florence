"""
PubMed literature search service following External Service Integration
PubMed API integration from copilot-instructions.md
"""

from typing import Dict, Any, List, Optional

# Conditional imports following copilot-instructions.md
try:
    import httpx
    _has_httpx = True
except ImportError:
    _has_httpx = False
    httpx = None

try:
    import requests
    _has_requests = True
except Exception:
    _has_requests = False
    requests = None

try:
    from xml.etree import ElementTree as ET
    _has_xml = True
except ImportError:
    _has_xml = False
    ET = None


from .base_service import BaseService
from ..utils.redis_cache import cached
from ..utils.config import get_settings
from ..utils.exceptions import ExternalServiceException

import logging
import asyncio
logger = logging.getLogger(__name__)

# Backwards-compatibility for tests and older code: expose legacy
# symbols that callers may monkeypatch. We now use httpx internally,
# but keep `_has_requests`, `requests`, and `_requests_get` available so
# tests written against the previous implementation still function.
_has_requests = False
requests = None

def _requests_get(*args, **kwargs):
    """Legacy helper kept for tests; raises if requests not available."""
    if _has_requests:
        return requests.get(*args, **kwargs)
    raise RuntimeError("requests not available in this environment")

class PubMedService(BaseService[Dict[str, Any]]):
    """
    PubMed literature search service
    Following External Service Integration from copilot-instructions.md
    """
    
    def __init__(self):
        super().__init__("pubmed")
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.settings = get_settings()

    @cached(ttl_seconds=3600)
    async def search_literature(
        self,
        query: str,
        max_results: int = 10,
        sort_by: str = "relevance"
    ) -> Dict[str, Any]:
        """
        Async search of medical literature with caching using httpx AsyncClient.
        """
        self._log_request(query, max_results=max_results, sort_by=sort_by)

        try:
            # Use live service if available and enabled
            if self.settings.USE_LIVE_SERVICES and _has_httpx and _has_xml:
                result = await self._fetch_from_pubmed(query, max_results, sort_by)
                self._log_response(query, True, source="pubmed_api")
                return self._create_response(result, query, source="pubmed_api")
            else:
                # Fallback to stub data
                result = self._create_stub_response(query, max_results, sort_by)
                self._log_response(query, True, source="stub_data")
                return self._create_response(result, query, source="stub_data")

        except Exception as e:
            self._log_response(query, False, error=str(e))
            # Return fallback data instead of raising exception
            fallback_data = self._create_stub_response(query, max_results, sort_by)
            return self._handle_external_service_error(e, fallback_data)
    
    async def _fetch_from_pubmed(self, query: str, max_results: int, sort_by: str) -> Dict[str, Any]:
        """Fetch literature data from PubMed API asynchronously using httpx."""
        if not _has_httpx:
            raise ExternalServiceException("httpx library not available", "pubmed_service")

        if not _has_xml:
            raise ExternalServiceException("XML parsing not available", "pubmed_service")

        # Use httpx when available, otherwise call requests in a thread to avoid blocking
        search_url = f"{self.base_url}/esearch.fcgi"
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "sort": "relevance" if sort_by == "relevance" else "pub_date",
            "retmode": "xml"
        }

        if _has_httpx:
            async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
                search_response = await client.get(search_url, params=search_params)
                search_response.raise_for_status()
                search_content = search_response.content
        else:
            if not _has_requests:
                raise ExternalServiceException("httpx or requests library not available", "pubmed_service")
            search_resp = await asyncio.to_thread(requests.get, search_url, params=search_params, timeout=15)
            search_resp.raise_for_status()
            search_content = search_resp.content

        # Parse search results
        search_root = ET.fromstring(search_content)
        pmids = [id_elem.text for id_elem in search_root.findall(".//Id") if id_elem is not None]

        if not pmids:
            return self._create_no_results_response(query)

        # Step 2: Fetch article details
        fetch_url = f"{self.base_url}/efetch.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": ",".join([p for p in pmids[:max_results] if p]),
            "retmode": "xml"
        }

        if _has_httpx:
            async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
                fetch_response = await client.get(fetch_url, params=fetch_params)
                fetch_response.raise_for_status()
                fetch_content = fetch_response.content
        else:
            fetch_resp = await asyncio.to_thread(requests.get, fetch_url, params=fetch_params, timeout=15)
            fetch_resp.raise_for_status()
            fetch_content = fetch_resp.content

        # Parse article details
        articles = self._parse_pubmed_xml(fetch_content)

            return {
                "articles": articles,
                "total_results": len(pmids),
                "query_terms": query,
                "search_metadata": {
                    "max_results": max_results,
                    "sort_by": sort_by,
                    "retrieved": len(articles)
                }
            }
    
    def _parse_pubmed_xml(self, xml_content: bytes) -> List[Dict[str, Any]]:
        """Parse PubMed XML response into structured data"""
        articles = []
        
        try:
            if not _has_xml:
                raise RuntimeError("XML parsing not available in this environment")

            root = ET.fromstring(xml_content)

            for article_elem in root.findall(".//PubmedArticle"):
                article_data = self._extract_article_data(article_elem)
                if article_data:
                    articles.append(article_data)

        except Exception as e:
            # Use module logger; fall back to standard logger when necessary
            try:
                logger.warning(f"XML parsing error: {e}")
            except Exception:
                pass
        
        return articles
    
    def _extract_article_data(self, article_elem) -> Optional[Dict[str, Any]]:
        """Extract article data from XML element"""
        try:
            # PMID
            pmid_elem = article_elem.find(".//PMID")
            pmid = pmid_elem.text if pmid_elem is not None else "unknown"
            
            # Title
            title_elem = article_elem.find(".//ArticleTitle")
            title = title_elem.text if title_elem is not None else "No title available"
            
            # Authors
            authors = []
            for author_elem in article_elem.findall(".//Author"):
                lastname_elem = author_elem.find("LastName")
                forename_elem = author_elem.find("ForeName")
                if lastname_elem is not None:
                    author_name = lastname_elem.text
                    if forename_elem is not None:
                        author_name = f"{forename_elem.text} {author_name}"
                    authors.append(author_name)
            
            # Journal
            journal_elem = article_elem.find(".//Journal/Title")
            journal = journal_elem.text if journal_elem is not None else "Unknown journal"
            
            # Publication date
            pub_date_elem = article_elem.find(".//PubDate")
            pub_date = self._extract_publication_date(pub_date_elem)
            
            # Abstract
            abstract_elem = article_elem.find(".//Abstract/AbstractText")
            abstract = abstract_elem.text if abstract_elem is not None else "No abstract available"
            
            # DOI
            doi_elem = article_elem.find(".//ELocationID[@EIdType='doi']")
            doi = doi_elem.text if doi_elem is not None else None
            
            return {
                "pmid": pmid,
                "title": title,
                "authors": authors,
                "journal": journal,
                "publication_date": pub_date,
                "abstract": abstract[:500] + "..." if len(abstract) > 500 else abstract,
                "doi": doi,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            }
            
        except Exception as e:
            try:
                logger.warning(f"Error extracting article data: {e}")
            except Exception:
                pass
            return None
    
    def _extract_publication_date(self, pub_date_elem) -> str:
        """Extract publication date from XML element"""
        if pub_date_elem is None:
            return "Unknown date"
        
        year_elem = pub_date_elem.find("Year")
        month_elem = pub_date_elem.find("Month")
        
        if year_elem is not None:
            year = year_elem.text
            month = month_elem.text if month_elem is not None else "01"
            return f"{year}-{month.zfill(2)}"
        
        return "Unknown date"
    
    def _create_stub_response(self, query: str, max_results: int, sort_by: str) -> Dict[str, Any]:
        """
        Create stub response when live services unavailable
        Following Conditional Imports Pattern from copilot-instructions.md
        """
        stub_articles = []
        
        for i in range(min(max_results, 3)):  # Create 3 stub articles
            stub_article = {
                "pmid": f"stub_{i+1}",
                "title": f"Educational Article {i+1}: {query} - Literature Review",
                "authors": ["Smith, J.", "Johnson, M.", "Wilson, K."],
                "journal": "Journal of Medical Education",
                "publication_date": "2024-01",
                "abstract": f"This is educational content about {query}. " + 
                           f"{self.educational_banner} " +
                           "This stub represents the type of medical literature available through PubMed searches.",
                "doi": f"10.1000/stub{i+1}",
                "url": f"https://pubmed.ncbi.nlm.nih.gov/stub_{i+1}/"
            }
            stub_articles.append(stub_article)
        
        return {
            "articles": stub_articles,
            "total_results": len(stub_articles),
            "query_terms": query,
            "search_metadata": {
                "max_results": max_results,
                "sort_by": sort_by,
                "retrieved": len(stub_articles),
                "source": "stub_data"
            }
        }
    
    def _create_no_results_response(self, query: str) -> Dict[str, Any]:
        """Create response when no articles found"""
        return {
            "articles": [],
            "total_results": 0,
            "query_terms": query,
            "search_metadata": {
                "retrieved": 0,
                "message": "No articles found for this query"
            },
            "suggestions": [
                "Try broader search terms",
                "Check spelling of medical terms",
                "Use MeSH (Medical Subject Headings) terms",
                "Consider synonyms or related conditions"
            ]
        }
    
    async def _process_request(self, query: str, **kwargs) -> Dict[str, Any]:
        """Implementation of abstract method from BaseService (async)."""
        return await self.search_literature(query, **kwargs)
# Minimal logging helpers in case BaseService doesn't provide them at runtime
    def _log_request(self, *args, **kwargs) -> None:
        logger.debug(f"PubMedService request: {args} {kwargs}")

    def _log_response(self, *args, **kwargs) -> None:
        logger.debug(f"PubMedService response: {args} {kwargs}")

    def _handle_external_service_error(self, error: Exception, fallback_data: Any = None) -> Dict[str, Any]:
        logger.warning(f"External service error: {error}")
        return fallback_data or {}
# Service factory function following Conditional Imports Pattern
def create_pubmed_service() -> Optional[PubMedService]:
    """
    Create PubMed service with graceful degradation.
    Returns None if service cannot be initialized.
    """
    try:
        return PubMedService()
    except Exception as e:
        logger.warning(f"PubMed service unavailable: {e}")
        return None
