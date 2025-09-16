import os
from typing import Dict, Any, List, Optional

LIVE = str(os.getenv("USE_LIVE", "0")).lower() in {"1", "true", "yes", "on"}

pubmed_live = None
if LIVE:
    try:
        import live_pubmed as pubmed_live
    except Exception:
        pubmed_live = None

def search(query: str, max_results: int = 10) -> Dict[str, Any]:
    banner = "Draft for clinician review — not medical advice. No PHI stored."
    if LIVE and pubmed_live and hasattr(pubmed_live, "search"):
        try:
            results: List[Dict[str, Optional[str]]] = pubmed_live.search(query, max_results=max_results)
            return {"banner": banner, "query": query, "results": results}
        except Exception:
            pass
    return {
        "banner": banner,
        "query": query,
        "results": [
            {"pmid": None, "title": f"Stub article for '{query}'", "abstract": "No live pubmed module found.", "url": None}
            for _ in range(max_results)
        ],
    }
