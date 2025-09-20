import requests

BASE = "https://mydisease.info/v1"

def lookup(term: str):
    # Try a query by name; pull first hit's fields
    r = requests.get(f"{BASE}/query", params={
        "q": term, 
        "scopes": "name,mondo.label", 
        "fields": "name,definition,mondo.label,mondo.definition,dbs,_id",
        "size": 3
    }, timeout=15)
    r.raise_for_status()
    hits = r.json().get("hits", [])
    if not hits:
        return {"name": None, "summary": None, "references": []}
    
    top = hits[0]
    # Try to get name from different fields
    name = (top.get("name") or 
            (top.get("mondo", {}).get("label") if top.get("mondo") else None) or
            top.get("_id"))
    
    # Try to get definition/summary from different fields  
    summary = (top.get("definition") or 
              (top.get("mondo", {}).get("definition") if top.get("mondo") else None))
    
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
    
    # Add a reference for the source disease ID
    if top.get("_id"):
        refs.append({
            "id": top.get("_id"), 
            "title": f"MyDisease.info: {top.get('_id')}", 
            "url": f"https://mydisease.info/v1/disease/{top.get('_id')}", 
            "source": "mydisease.info"
        })
    
    return {"name": name, "summary": summary, "references": refs}
