import requests

# Classic ClinicalTrials.gov v1 StudyFields API (simple, stable)
BASE = "https://classic.clinicaltrials.gov/api/query/study_fields"

def search(condition: str, status: str | None = None, max_results: int = 10):
    expr = condition
    if status in {"recruiting", "active", "completed"}:
        # filter in expression if provided
        expr = f"{condition} AND OverallStatus:{status}"
    params = {
        "expr": expr,
        "fields": "NCTId,BriefTitle,OverallStatus,Condition,LocationCountry",
        "min_rnk": 1,
        "max_rnk": max_results,
        "fmt": "json",
    }
    r = requests.get(BASE, params=params, timeout=20)
    r.raise_for_status()
    studies = r.json().get("StudyFieldsResponse", {}).get("StudyFields", [])
    out = []
    for s in studies:
        nct = (s.get("NCTId") or [None])[0]
        title = (s.get("BriefTitle") or [None])[0]
        st = (s.get("OverallStatus") or [None])[0]
        conds = s.get("Condition") or []
        locs = s.get("LocationCountry") or []
        url = f"https://clinicaltrials.gov/study/{nct}" if nct else None
        out.append({
            "nct_id": nct,
            "title": title,
            "status": st,
            "conditions": conds,
            "locations": locs,
            "url": url,
        })
    return out
