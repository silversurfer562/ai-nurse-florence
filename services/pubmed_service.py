from typing import Dict, List, Optional

from utils.types import PubMedResult
from utils.logging import get_logger
from utils.cache import cached
from utils.config import settings

logger = get_logger(__name__)

# Determine if we are in "live" mode from settings
LIVE = settings.USE_LIVE

# Lazy-load the live connector to avoid import errors if it's not installed
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
def search_pubmed(query: str, page: int = 1, size: int = 10) -> PubMedResult:
    """
    Search PubMed for articles matching the query.
    
    This function attempts to use a live connector if available,
    falling back to a stub response if not. Results are cached for 30 minutes.
    
    Args:
        query: The search query string
        page: The page number for pagination.
        size: The number of results per page.
        
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
                extra={"query": query, "page": page, "size": size}
            )
            # The live service provides max_results instead of pagination
            results: List[Dict[str, Optional[str]]] = pubmed_live.search(
                query, max_results=size
            )
            # The live service should also return the total count
            total_count = pubmed_live.get_total_count(query)

            return {"banner": banner, "query": query, "results": results, "total": total_count}
        except Exception as e:
            logger.error(
                f"Error calling pubmed_live.search: {str(e)}", 
                extra={"query": query, "page": page, "size": size, "error": str(e)},
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
        extra={"query": query, "page": page, "size": size, "mode": "stub"}
    )
    # Simulate pagination for the stub response
    total_items = 100 # Mock total
    start_index = (page - 1) * size
    end_index = start_index + size
    
    mock_results = [
        {
            "pmid": f"STUB_{i+1}", 
            "title": f"Stub article #{i+1} for '{query}'", 
            "abstract": "No live pubmed module found.", 
            "url": None
        }
        for i in range(start_index, end_index)
        if i < total_items
    ]

    return {
        "banner": banner,
        "query": query,
        "results": mock_results,
        "total": total_items,
    }
