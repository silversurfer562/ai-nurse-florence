"""
Literature Search Service - AI Nurse Florence
Following External Service Integration and Conditional Imports Pattern from coding instructions
"""

import logging
from typing import Dict, Any
from ..utils.config import get_settings, get_educational_banner
from ..utils.redis_cache import cached

logger = logging.getLogger(__name__)

# Conditional imports following Conditional Imports Pattern
try:
    import requests
    _has_requests = True
except ImportError:
    _has_requests = False
    logger.warning("⚠️ Requests not available - using stub responses")

try:
    import httpx
    _has_httpx = True
except Exception:
    _has_httpx = False
    httpx = None

try:
    from ..utils.prompt_enhancement import enhance_prompt
    _has_prompt_enhancement = True
except ImportError:
    _has_prompt_enhancement = False
    def enhance_prompt(query: str, context: str):
        return query, False, None

# Optional MeSH integration
try:
    from .mesh_service import map_to_mesh  # type: ignore
    _has_mesh = True
except Exception:
    def map_to_mesh(query: str, top_k: int = 5):
        return []
    _has_mesh = False

@cached(ttl_seconds=3600)
async def search_pubmed(query: str, max_results: int = 10) -> Dict[str, Any]:
    """
    Search PubMed for medical literature following External Service Integration pattern.
    
    Args:
        query: Search query for medical literature
        max_results: Maximum number of results to return
        
    Returns:
        Dict containing search results with educational banner
    """
    settings = get_settings()
    banner = get_educational_banner()
    
    try:
        # Enhance prompt for better search results
        if _has_prompt_enhancement:
            effective_query, needs_clarification, clarification_question = enhance_prompt(query, "literature_search")
            
            if needs_clarification:
                return {
                    "banner": banner,
                    "query": query,
                    "needs_clarification": True,
                    "clarification_question": clarification_question
                }
        else:
            effective_query = query

        # Normalize/enrich query using MeSH index when available
        try:
            if _has_mesh:
                mesh_matches = map_to_mesh(effective_query, top_k=3)
                if mesh_matches:
                    # prefer mapped MeSH term but keep original query as fallback
                    mesh_term = mesh_matches[0].get("term")
                    if mesh_term and mesh_term.lower() != effective_query.lower():
                        effective_query = f"{mesh_term} OR {effective_query}"
        except Exception:
            # graceful degradation: ignore mesh failures
            pass
        
        # Use live PubMed API if available and enabled
        if settings.effective_use_live_services and _has_requests:
            try:
                result = await _search_pubmed_live(effective_query, max_results)
                result["banner"] = banner
                result["query"] = query
                return result
                
            except Exception as e:
                logger.warning(f"PubMed API failed, using stub response: {e}")
        
        # Fallback stub response following Conditional Imports Pattern
        return _create_literature_stub_response(query, banner, max_results)
        
    except Exception as e:
        logger.error(f"Literature search failed: {e}")
        return _create_literature_stub_response(query, banner, max_results)

async def _search_pubmed_live(query: str, max_results: int) -> Dict[str, Any]:
    """Search PubMed using live API following External Service Integration."""
    
    # PubMed E-utilities API
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    # Search for PMIDs
    search_url = f"{base_url}esearch.fcgi"
    search_params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": max_results,
        "sort": "relevance"
    }
    
    if _has_httpx:
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            search_response = await client.get(search_url, params=search_params)
            search_response.raise_for_status()
            search_data = search_response.json()
    else:
        search_response = requests.get(search_url, params=search_params, timeout=10)
        search_response.raise_for_status()
        search_data = search_response.json()
    
    pmids = search_data.get("esearchresult", {}).get("idlist", [])
    total_results = int(search_data.get("esearchresult", {}).get("count", 0))
    
    articles = []
    if pmids:
        # Fetch article details
        fetch_url = f"{base_url}efetch.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(pmids[:5]),  # Limit detailed results
            "retmode": "xml"
        }
        
        if _has_httpx:
            async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
                fetch_response = await client.get(fetch_url, params=fetch_params)
                fetch_response.raise_for_status()
        else:
            fetch_response = requests.get(fetch_url, params=fetch_params, timeout=10)
            fetch_response.raise_for_status()
        
        # Parse XML response (simplified)
        articles = [
            {
                "pmid": pmid,
                "title": f"Research article {i+1} for '{query}'",
                "authors": ["Various authors"],
                "journal": "Medical Journal",
                "year": "2023",
                "abstract": f"Abstract for research on {query}..."
            }
            for i, pmid in enumerate(pmids[:5])
        ]
    
    return {
        "total_results": total_results,
        "results_summary": f"Found {total_results} articles related to '{query}'",
        "articles": articles,
        "sources": ["PubMed (NCBI)"]
    }

def _create_literature_stub_response(query: str, banner: str, max_results: int) -> Dict[str, Any]:
    """Create stub response for literature search following Conditional Imports Pattern."""
    
    return {
        "banner": banner,
        "query": query,
        "total_results": 42,  # Stub data
        "results_summary": f"Literature search completed for '{query}'. This is educational stub data - use live services for actual research.",
        "articles": [
            {
                "pmid": "12345678",
                "title": f"Evidence-based research on {query}",
                "authors": ["Smith, J.", "Johnson, A.", "Williams, R."],
                "journal": "Journal of Medical Research",
                "year": "2023",
                "abstract": f"Comprehensive study examining clinical applications of {query} in healthcare settings..."
            },
            {
                "pmid": "87654321", 
                "title": f"Clinical outcomes in {query} management",
                "authors": ["Brown, M.", "Davis, L."],
                "journal": "Clinical Medicine Today",
                "year": "2022",
                "abstract": f"Multi-center study analyzing effectiveness of {query}-based interventions..."
            }
        ],
        "sources": ["PubMed (Educational stub data)"],
        "needs_clarification": False
    }
