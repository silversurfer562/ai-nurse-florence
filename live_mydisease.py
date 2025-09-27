"""
MyDisease.info API connector for disease information lookup.
"""
import requests
from typing import Dict, Any, List

# MyDisease.info API base URL
BASE_URL = "https://mydisease.info/v1"

def query(term: str, size: int = 10) -> Dict[str, Any]:
    """
    Query MyDisease.info for disease information.
    
    Args:
        term: Search term for disease lookup
        size: Maximum number of results to return
        
    Returns:
        Dict containing the API response
        
    Raises:
        requests.RequestException: If API call fails
    """
    try:
        response = requests.get(
            f"{BASE_URL}/query",
            params={
                "q": term,
                "size": size,
                "fields": "mondo,hpo,orphanet,umls,name,description,type_of_gene,symbol"
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise requests.RequestException(f"MyDisease.info API error: {e}")

def get_disease(disease_id: str) -> Dict[str, Any]:
    """
    Get specific disease information by ID.
    
    Args:
        disease_id: Disease identifier
        
    Returns:
        Dict containing disease details
        
    Raises:
        requests.RequestException: If API call fails
    """
    try:
        response = requests.get(
            f"{BASE_URL}/disease/{disease_id}",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise requests.RequestException(f"MyDisease.info API error: {e}")

def search(term: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Search for diseases using MyDisease.info API.
    Compatible with the existing service expectations.
    
    Args:
        term: Search term
        max_results: Maximum number of results
        
    Returns:
        List of disease information dictionaries
    """
    try:
        result = query(term, max_results)
        
        # Extract hits and format for compatibility
        hits = result.get("hits", [])
        formatted_results = []
        
        for hit in hits:
            # Extract name - try multiple fields
            name = (
                hit.get("name") or 
                hit.get("symbol") or 
                hit.get("_id", "Unknown")
            )
            
            # Extract description
            description = hit.get("description", "No description available")
            
            formatted_results.append({
                "id": hit.get("_id"),
                "name": name,
                "description": description,
                "score": hit.get("_score", 0),
                "raw_data": hit
            })
            
        return formatted_results
        
    except Exception as e:
        # Return empty list if API fails - graceful degradation
        print(f"MyDisease.info search error: {e}")
        return []
