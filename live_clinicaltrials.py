import requests

# ClinicalTrials.gov API v2 (current stable API)
BASE = "https://clinicaltrials.gov/api/v2/studies"

def search(condition: str, status: str | None = None, max_results: int = 10):
    params = {
        'query.cond': condition,
        'countTotal': 'true',
        'pageSize': min(max_results, 1000)  # API max is 1000
    }
    
    # Note: API v2 status filtering is complex, so we'll filter results after retrieval
    # if status is specified
    
    r = requests.get(BASE, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    
    studies = data.get("studies", [])
    out = []
    
    for study in studies:
        protocol = study.get("protocolSection", {})
        identification = protocol.get("identificationModule", {})
        status_module = protocol.get("statusModule", {})
        conditions_module = protocol.get("conditionsModule", {})
        contacts_locations = protocol.get("contactsLocationsModule", {})
        
        nct_id = identification.get("nctId")
        title = identification.get("briefTitle")
        overall_status = status_module.get("overallStatus")
        conditions = conditions_module.get("conditions", [])
        
        # Filter by status if specified (post-API filtering)
        if status:
            status_map = {
                "recruiting": "RECRUITING",
                "active": "ACTIVE_NOT_RECRUITING", 
                "completed": "COMPLETED",
                "not yet recruiting": "NOT_YET_RECRUITING"
            }
            target_status = status_map.get(status.lower(), status.upper())
            if overall_status != target_status:
                continue
        
        # Get locations/countries
        locations = []
        if contacts_locations.get("locations"):
            for loc in contacts_locations["locations"]:
                country = loc.get("country")
                if country and country not in locations:
                    locations.append(country)
        
        url = f"https://clinicaltrials.gov/study/{nct_id}" if nct_id else None
        
        out.append({
            "nct_id": nct_id,
            "title": title,
            "status": overall_status,
            "conditions": conditions,
            "locations": locations[:5],  # Limit to 5 countries
            "url": url,
        })
        
        # Stop when we have enough results after filtering
        if len(out) >= max_results:
            break
    
    return out
