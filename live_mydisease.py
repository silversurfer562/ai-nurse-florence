import requests

BASE = "https://mydisease.info/v1"

def lookup(term: str):
    # Try a query by name; pull first hit’s fields
    r = requests.get(f"{BASE}/query", params={"q": term, "scopes": "name", "fields": "name,definition,dbs"}, timeout=15)
    r.raise_for_status()
    hits = r.json().get("hits", [])
    if not hits:
        return {"name": None, "summary": None, "references": []}
    top = hits[0]
    name = top.get("name")
    summary = top.get("definition") or None
    refs = []
    dbs = top.get("dbs") or {}
    for k, v in dbs.items():
        if isinstance(v, dict):
            url = v.get("url") or None
        elif isinstance(v, list) and v and isinstance(v[0], dict):
            url = v[0].get("url") or None
        else:
            url = None
        refs.append({"id": None, "title": k, "url": url, "source": "mydisease.info"})
    return {"name": name, "summary": summary, "references": refs}
