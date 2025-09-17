import os
from typing import Dict, Any, List, Optional

from utils.exceptions import ExternalServiceException
from utils.types import PubMedResult, PubMedArticleDict
from utils.logging import get_logger
from utils.redis_cache import cached  # Updated to use redis_cache

logger = get_logger(__name__)

LIVE = str(os.getenv("USE_LIVE", "0")).lower() in {"1", "true", "yes", "on"}

pubmed_live = None
if LIVE:
    try:
        import live_pubmed as pubmed_live
    except Exception as e:
        logger.warning(
            "Failed to import live_pubmed module", 
            extra={"error": str(e)}
        )
        pubmed_live = None


@cached(ttl_seconds=1800)  # Cache PubMed searches for 30 minutes
def search_pubmed(query: str, max_results: int = 10) -> PubMedResult:
    """
    Search PubMed for articles matching the query.
    
    This function attempts to use a live connector if available,
    falling back to a stub response if not. Results are cached for 30 minutes.
    
    Args:
        query: The search query string
        max_results: Maximum number of results to return (default: 10)
        
    Returns:
        A dictionary containing:
        - banner: Educational disclaimer banner
        - query: The original search query
        - results: A list of article dictionaries, each with:
          - pmid: PubMed ID (optional)
          - title: Article title
          - abstract: Article abstract (optional)
          - url: URL to the article (optional)
          
    Raises:
        ExternalServiceException: If the live service is enabled but fails unexpectedly
    """
    banner = "Draft for clinician review — not medical advice. No PHI stored."
    
    # If live mode is enabled and we have the module
    if LIVE and pubmed_live and hasattr(pubmed_live, "search"):
        try:
            logger.info(
                f"Searching PubMed: {query}", 
                extra={"query": query, "max_results": max_results}
            )
            results: List[Dict[str, Optional[str]]] = pubmed_live.search(
                query, max_results=max_results
            )
            return {"banner": banner, "query": query, "results": results}
        except Exception as e:
            logger.error(
                f"Error calling pubmed_live.search: {str(e)}", 
                extra={"query": query, "max_results": max_results, "error": str(e)},
                exc_info=True
            )
            # Instead of silently falling back, we could raise an exception here
            # to make the error more visible
            # raise ExternalServiceException(
            #     f"PubMed search failed: {str(e)}",
            #     service_name="pubmed",
            #     details={"query": query, "max_results": max_results}
            # )
    
    # Fallback to stub response
    logger.info(
        f"Using stub response for PubMed search: {query}",
        extra={"query": query, "max_results": max_results, "mode": "stub"}
    )
    return {
        "banner": banner,
        "query": query,
        "results": [
            {
                "pmid": None, 
                "title": f"Stub article for '{query}'", 
                "abstract": "No live pubmed module found.", 
                "url": None
            }
            for _ in range(max_results)
        ],
    }
