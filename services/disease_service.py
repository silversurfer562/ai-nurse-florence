from typing import Dict, Any
from models.schemas import Reference

try:
    import live_mydisease as mydisease_live
except Exception:
    mydisease_live = None
try:
    import medlineplus as medlineplus_mod
except Exception:
    medlineplus_mod = None


def lookup_disease(term: str) -> Dict[str, Any]:
    if mydisease_live and hasattr(mydisease_live, "lookup"):
        try:
            data = mydisease_live.lookup(term)
            refs = [Reference(**r) for r in data.get("references", [])]
            return {
                "name": data.get("name"),
                "summary": data.get("summary"),
                "references": [r.model_dump() for r in refs],
            }
        except Exception:
            pass
    if medlineplus_mod and hasattr(medlineplus_mod, "summary"):
        try:
            s, refs = medlineplus_mod.summary(term)
            return {
                "name": term.title(),
                "summary": s,
                "references": [
                    {
                        "title": r.get("title"),
                        "url": r.get("url"),
                        "source": "MedlinePlus",
                    }
                    for r in (refs or [])
                ],
            }
        except Exception:
            pass
    return {
        "name": term.title(),
        "summary": f"No live connector found. Placeholder for '{term}'.",
        "references": [],
    }
