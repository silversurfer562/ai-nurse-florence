from typing import List, Dict, Any

try:
    import live_pubmed as pubmed_live
except Exception:
    pubmed_live = None
try:
    import pubmed as pubmed_mod
except Exception:
    pubmed_mod = None


def search_pubmed(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    if pubmed_live and hasattr(pubmed_live, "search"):
        try:
            return pubmed_live.search(query, max_results=max_results)
        except Exception:
            pass
    if pubmed_mod and hasattr(pubmed_mod, "search"):
        try:
            return pubmed_mod.search(query, max_results=max_results)
        except Exception:
            pass
    return [
        {
            "pmid": None,
            "title": f"Stub article for '{query}'",
            "abstract": "No live pubmed module found.",
            "url": None,
        }
        for _ in range(min(max_results, 3))
    ]
