"""
ClinicalTrials.gov API connector for clinical trial information.
"""
import requests
from typing import Dict, Any, List

# ClinicalTrials.gov API base URL
BASE_URL = "https://clinicaltrials.gov/api/v2"

def search_studies(query: str, max_results: int = 10, status: str = None) -> List[Dict[str, Any]]:
    """
    Search ClinicalTrials.gov for studies matching the query.

    Args:
        query: Search term for clinical trials
        max_results: Maximum number of results to return
        status: Optional recruitment status filter (e.g., 'recruiting', 'active', 'completed')

    Returns:
        List of clinical trial information dictionaries

    Raises:
        requests.RequestException: If API call fails
    """
    try:
        params = {
            "query.term": query,
            "pageSize": min(max_results, 100),  # API limit is 100
            "format": "json",
            "fields": [
                "NCTId",
                "BriefTitle", 
                "OfficialTitle",
                "BriefSummary",
                "OverallStatus",
                "Phase",
                "StudyType",
                "Condition",
                "InterventionName",
                "PrimaryOutcomeMeasure",
                "StartDate",
                "CompletionDate",
                "Sponsor",
                "LocationFacility",
                "LocationCountry"
            ]
        }

        # Add status filter if provided
        if status:
            params["filter.overallStatus"] = status.upper()

        response = requests.get(
            f"{BASE_URL}/studies",
            params=params,
            timeout=15
        )
        response.raise_for_status()
        
        data = response.json()
        studies = data.get("studies", [])
        
        formatted_results = []
        for study in studies:
            protocol_section = study.get("protocolSection", {})
            identification_module = protocol_section.get("identificationModule", {})
            status_module = protocol_section.get("statusModule", {})
            design_module = protocol_section.get("designModule", {})
            conditions_module = protocol_section.get("conditionsModule", {})
            interventions_module = protocol_section.get("interventionsModule", {})
            outcomes_module = protocol_section.get("outcomesModule", {})
            sponsor_module = protocol_section.get("sponsorCollaboratorsModule", {})
            contacts_locations_module = protocol_section.get("contactsLocationsModule", {})
            
            # Extract key information
            nct_id = identification_module.get("nctId", "Unknown")
            brief_title = identification_module.get("briefTitle", "No title available")
            official_title = identification_module.get("officialTitle", brief_title)
            brief_summary = identification_module.get("briefSummary", "No summary available")
            
            # Status and phase
            overall_status = status_module.get("overallStatus", "Unknown")
            phase = design_module.get("phases", ["Unknown"])[0] if design_module.get("phases") else "Unknown"
            study_type = design_module.get("studyType", "Unknown")
            
            # Conditions and interventions
            conditions = conditions_module.get("conditions", [])
            interventions = []
            if interventions_module and "interventions" in interventions_module:
                interventions = [i.get("name", "Unknown") for i in interventions_module["interventions"]]
            
            # Dates
            start_date = status_module.get("startDateStruct", {}).get("date", "Unknown")
            completion_date = status_module.get("primaryCompletionDateStruct", {}).get("date", "Unknown")
            
            # Sponsor
            lead_sponsor = sponsor_module.get("leadSponsor", {}).get("name", "Unknown")
            
            # Primary outcome
            primary_outcomes = outcomes_module.get("primaryOutcomes", [])
            primary_outcome = primary_outcomes[0].get("measure", "Unknown") if primary_outcomes else "Unknown"
            
            # Locations
            locations = []
            if contacts_locations_module and "locations" in contacts_locations_module:
                for location in contacts_locations_module["locations"][:3]:  # Limit to first 3
                    facility = location.get("facility", "Unknown facility")
                    city = location.get("city", "")
                    country = location.get("country", "")
                    location_str = f"{facility}"
                    if city:
                        location_str += f", {city}"
                    if country:
                        location_str += f", {country}"
                    locations.append(location_str)
            
            trial_info = {
                "nct_id": nct_id,
                "title": brief_title,
                "official_title": official_title,
                "summary": brief_summary,
                "status": overall_status,
                "phase": phase,
                "study_type": study_type,
                "conditions": conditions,
                "interventions": interventions,
                "primary_outcome": primary_outcome,
                "start_date": start_date,
                "completion_date": completion_date,
                "sponsor": lead_sponsor,
                "locations": locations,
                "url": f"https://clinicaltrials.gov/study/{nct_id}",
                "raw_data": study
            }
            
            formatted_results.append(trial_info)
            
        return formatted_results
        
    except requests.RequestException as e:
        # Return empty list if API fails - graceful degradation
        print(f"ClinicalTrials.gov API error: {e}")
        return []

def get_study_details(nct_id: str) -> Dict[str, Any]:
    """
    Get detailed information for a specific clinical trial.
    
    Args:
        nct_id: Clinical trial NCT ID
        
    Returns:
        Detailed trial information dictionary
    """
    try:
        response = requests.get(
            f"{BASE_URL}/studies/{nct_id}",
            params={"format": "json"},
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        study = data.get("studies", [{}])[0]
        
        # Use the same extraction logic as search_studies but for single study
        protocol_section = study.get("protocolSection", {})
        identification_module = protocol_section.get("identificationModule", {})
        
        return {
            "nct_id": nct_id,
            "title": identification_module.get("briefTitle", "No title available"),
            "summary": identification_module.get("briefSummary", "No summary available"),
            "url": f"https://clinicaltrials.gov/study/{nct_id}",
            "raw_data": study
        }
        
    except requests.RequestException:
        return {
            "nct_id": nct_id,
            "title": "Trial not found",
            "error": "Failed to retrieve trial details"
        }

def search(condition: str = None, query: str = None, status: str = None, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Alias for search_studies to maintain compatibility with existing services.

    Args:
        condition: Condition/disease to search for (alias for query)
        query: Search term for clinical trials
        status: Optional recruitment status filter
        max_results: Maximum number of results to return

    Returns:
        List of clinical trial information dictionaries
    """
    # Use condition if provided, otherwise use query
    search_term = condition or query or ""
    return search_studies(search_term, max_results, status)
