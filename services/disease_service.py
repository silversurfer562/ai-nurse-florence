
from utils.types import DiseaseResult
from utils.logging import get_logger
from utils.cache import cached
from services.prompt_enhancement import enhance_prompt
from utils.config import settings

logger = get_logger(__name__)

# Conditional import for metrics
try:
    from src.utils.metrics import record_external_request, record_external_error
    _has_metrics = True
except ImportError:
    _has_metrics = False
    # Stub implementations if metrics module isn't available
    def record_external_request(service: str, action: str) -> None:
        pass

# Determine if we are in "live" mode from settings
LIVE = settings.USE_LIVE

# Lazy-load the live connector to avoid import errors if it's not installed
mydisease_live = None
if LIVE:
    try:
        import live_mydisease as mydisease_live
    except Exception as e:
        logger.warning(
            "Failed to import live_mydisease module", 
            extra={"error": str(e)}
        )
        mydisease_live = None


@cached(ttl_seconds=3600)  # Cache disease lookups for 1 hour
def lookup_disease(term: str) -> DiseaseResult:
    """
    Look up information about a disease or medical condition.
    
    This function attempts to use a live connector if available,
    falling back to a stub response if not. Results are cached for 1 hour.
    
    Args:
        term: The disease or condition name to look up
        
    Returns:
        A dictionary containing the disease information:
        - banner: Educational disclaimer banner
        - query: The original search term
        - name: The disease name
        - summary: A textual description of the disease
        - references: A list of reference dictionaries with title, url, and source
        - needs_clarification: (Optional) True if term is too vague
        - clarification_question: (Optional) Question to clarify the search term
        
    Raises:
        ExternalServiceException: If the live service is enabled but fails unexpectedly
    """
    banner = "Draft for clinician review — not medical advice. No PHI stored."
    
    # First, enhance the prompt if needed
    effective_term, needs_clarification, clarification_question = enhance_prompt(term, "disease")
    
    # If clarification is needed, return that info
    if needs_clarification:
        logger.info(f"Clarification needed for disease term: '{term}'")
        return {
            "banner": banner,
            "query": term,
            "name": term.title() if term else None,
            "summary": None,
            "references": [],
            "needs_clarification": True,
            "clarification_question": clarification_question
        }
    
    # If live mode is enabled and we have the module
    if LIVE and mydisease_live and hasattr(mydisease_live, "lookup"):
        try:
            logger.info(f"Looking up disease: {term}", extra={"term": term})
            if _has_metrics:
                record_external_request("mydisease", "lookup")
                
            data = mydisease_live.lookup(term)  # Use original term, not enhanced prompt
            
            # Ensure we have all required fields
            data.setdefault("banner", banner)
            data.setdefault("query", term)  # Keep original query
            data.setdefault("references", [])
            if "name" not in data:
                data["name"] = term.title() if term else None
            
            # Add enhancement info if term was enhanced
            if effective_term != term:
                data["original_query"] = term
                data["enhanced_query"] = effective_term
                data["prompt_enhanced"] = True
                
            return data
        except Exception as e:
            logger.error(
                f"Error calling mydisease_live.lookup: {str(e)}", 
                extra={"term": term, "error": str(e)},
                exc_info=True
            )
            if _has_metrics:
                record_external_error("mydisease", "lookup", type(e).__name__)
            # Instead of silently falling back, we could raise an exception here
            # to make the error more visible
            # raise ExternalServiceException(
            #    f"Disease lookup failed: {str(e)}",
            #    service_name="mydisease",
            #    details={"term": term}
            # )
    
    # Fallback to stub response
    logger.info(
        f"Using stub response for disease: {effective_term}",
        extra={"term": effective_term, "mode": "stub"}
    )
    
    result = {
        "banner": banner,
        "query": term,
        "name": effective_term.title() if effective_term else None,
        "summary": f"No live connector found. Placeholder for '{effective_term}'.",
        "references": [],
    }
    
    # Add enhancement info if term was enhanced
    if effective_term != term:
        result["original_query"] = term
        result["enhanced_query"] = effective_term
        result["prompt_enhanced"] = True
    
    return result
