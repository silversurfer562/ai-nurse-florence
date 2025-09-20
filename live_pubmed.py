import os
import requests

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
EMAIL = os.getenv("NCBI_EMAIL")
API_KEY = os.getenv("NCBI_API_KEY")

def search(query: str, max_results: int = 10):
    # 1) esearch to get PMIDs
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json",
    }
    if API_KEY: params["api_key"] = API_KEY
    if EMAIL: params["email"] = EMAIL
    r = requests.get(f"{BASE}/esearch.fcgi", params=params, timeout=15)
    r.raise_for_status()
    ids = r.json().get("esearchresult", {}).get("idlist", [])
    if not ids:
        return []
    # 2) esummary to get titles (abstracts via efetch XML are heavier; leave as None)
    params = {
        "db": "pubmed",
        "id": ",".join(ids),
        "retmode": "json",
    }
    if API_KEY: params["api_key"] = API_KEY
    if EMAIL: params["email"] = EMAIL
    r = requests.get(f"{BASE}/esummary.fcgi", params=params, timeout=15)
    r.raise_for_status()
    data = r.json().get("result", {})
    results = []
    for pmid in ids:
        rec = data.get(pmid, {})
        title = rec.get("title")
        url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else None
        results.append({"pmid": pmid, "title": title, "abstract": None, "url": url})
    return results
