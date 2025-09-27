"""
MedlinePlus connector for health information lookup.
"""
import requests
from typing import Dict, Any, List, Tuple

# MedlinePlus Connect API base URL
BASE_URL = "https://connect.medlineplus.gov/service"

def search_medlineplus(topic: str) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Search MedlinePlus for health topic information.
    
    Args:
        topic: Health topic to search for
        
    Returns:
        Tuple containing (summary_text, references_list)
        
    Raises:
        requests.RequestException: If API call fails
    """
    try:
        # Use MedlinePlus Connect API
        params = {
            "mainSearchCriteria.v.cs": "2.16.840.1.113883.6.177",
            "mainSearchCriteria.v.c": topic,
            "knowledgeResponseType": "application/json"
        }
        
        response = requests.get(
            BASE_URL,
            params=params,
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        
        # Extract information from MedlinePlus Connect response
        summary = f"MedlinePlus information for '{topic}'"
        references = []
        
        # Parse the feed entries
        feed = data.get("feed", {})
        entries = feed.get("entry", [])
        
        if entries:
            for entry in entries[:5]:  # Limit to first 5 entries
                title = entry.get("title", {}).get("_value", "Unknown title")
                link = entry.get("link", {})
                url = link.get("href", "") if isinstance(link, dict) else ""
                
                # Get summary from content
                content = entry.get("summary", {}).get("_value", "")
                if content and len(content) > 200:
                    content = content[:200] + "..."
                
                references.append({
                    "title": title,
                    "url": url,
                    "source": "MedlinePlus",
                    "summary": content
                })
            
            if references:
                summary = f"Found {len(references)} MedlinePlus resources for '{topic}'"
        else:
            # No results found
            summary = f"No specific MedlinePlus resources found for '{topic}'. This may be a very specific or technical term."
            references = []
        
        return summary, references
        
    except requests.RequestException as e:
        # Return fallback information if API fails
        print(f"MedlinePlus API error: {e}")
        summary = f"MedlinePlus lookup for '{topic}' - API temporarily unavailable"
        references = [{
            "title": f"MedlinePlus - {topic}",
            "url": "https://medlineplus.gov/",
            "source": "MedlinePlus",
            "summary": "Search MedlinePlus directly for health information"
        }]
        return summary, references

def get_health_topic_info(topic: str) -> Dict[str, Any]:
    """
    Get health topic information from MedlinePlus.
    
    Args:
        topic: Health topic to search for
        
    Returns:
        Dictionary containing topic information
    """
    try:
        summary, references = search_medlineplus(topic)
        return {
            "topic": topic,
            "summary": summary,
            "references": references,
            "source": "MedlinePlus"
        }
    except Exception as e:
        return {
            "topic": topic,
            "summary": f"Error retrieving information for '{topic}'",
            "references": [],
            "error": str(e)
        }

def summary(topic: str) -> str:
    """
    Get a simple summary text for a health topic.
    Alias for compatibility with existing service expectations.
    
    Args:
        topic: Health topic
        
    Returns:
        Summary text string
    """
    try:
        summary_text, _ = search_medlineplus(topic)
        return summary_text
    except Exception:
        return f"MedlinePlus information lookup for '{topic}' failed"
