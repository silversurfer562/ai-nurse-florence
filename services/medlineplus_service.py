from typing import Dict, Any

try:
    import medlineplus as medlineplus_mod
except Exception:
    medlineplus_mod = None


def summary(topic: str) -> Dict[str, Any]:
    if medlineplus_mod and hasattr(medlineplus_mod, "summary"):
        try:
            s, refs = medlineplus_mod.summary(topic)
            return {
                "topic": topic,
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
        "topic": topic,
        "summary": f"No medlineplus connector found. Placeholder for '{topic}'.",
        "references": [],
    }
