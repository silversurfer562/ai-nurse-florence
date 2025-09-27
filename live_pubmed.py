"""
PubMed/NCBI API connector for medical literature search.
"""
import os
import requests
from typing import Dict, Any, List

# NCBI E-utilities base URL
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# Get API credentials from environment
EMAIL = os.getenv("NCBI_EMAIL")
API_KEY = os.getenv("NCBI_API_KEY")

def search(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Search PubMed for articles matching the query.
    
    Args:
        query: Search term for PubMed
        max_results: Maximum number of results to return
        
    Returns:
        List of article information dictionaries
        
    Raises:
        requests.RequestException: If API call fails
    """
    try:
        # Step 1: Search for PMIDs
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
        }
        
        if API_KEY:
            search_params["api_key"] = API_KEY
        if EMAIL:
            search_params["email"] = EMAIL
            
        search_response = requests.get(
            f"{BASE_URL}/esearch.fcgi",
            params=search_params,
            timeout=15
        )
        search_response.raise_for_status()
        
        search_data = search_response.json()
        pmids = search_data.get("esearchresult", {}).get("idlist", [])
        
        if not pmids:
            return []
            
        # Step 2: Get article summaries
        summary_params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "json",
        }
        
        if API_KEY:
            summary_params["api_key"] = API_KEY
        if EMAIL:
            summary_params["email"] = EMAIL
            
        summary_response = requests.get(
            f"{BASE_URL}/esummary.fcgi",
            params=summary_params,
            timeout=15
        )
        summary_response.raise_for_status()
        
        summary_data = summary_response.json()
        result_data = summary_data.get("result", {})
        
        # Format results
        articles = []
        for pmid in pmids:
            if pmid in result_data:
                article_data = result_data[pmid]
                article = {
                    "pmid": pmid,
                    "title": article_data.get("title", "No title available"),
                    "authors": article_data.get("authors", []),
                    "journal": article_data.get("source", "Unknown journal"),
                    "pub_date": article_data.get("pubdate", "Unknown date"),
                    "abstract": None,  # Would require additional efetch call
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    "doi": article_data.get("elocationid", "").replace("doi: ", "") if "doi:" in article_data.get("elocationid", "") else None
                }
                articles.append(article)
                
        return articles
        
    except requests.RequestException as e:
        # Return empty list if API fails - graceful degradation
        print(f"PubMed API error: {e}")
        return []

def get_total_count(query: str) -> int:
    """
    Get total count of articles matching the query.
    
    Args:
        query: Search term
        
    Returns:
        Total number of matching articles
    """
    try:
        params = {
            "db": "pubmed",
            "term": query,
            "rettype": "count",
            "retmode": "json",
        }
        
        if API_KEY:
            params["api_key"] = API_KEY
        if EMAIL:
            params["email"] = EMAIL
            
        response = requests.get(
            f"{BASE_URL}/esearch.fcgi",
            params=params,
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        count = data.get("esearchresult", {}).get("count", "0")
        return int(count)
        
    except (requests.RequestException, ValueError):
        return 0

def get_article_details(pmid: str) -> Dict[str, Any]:
    """
    Get detailed information for a specific article.
    
    Args:
        pmid: PubMed ID
        
    Returns:
        Article details dictionary
    """
    try:
        params = {
            "db": "pubmed",
            "id": pmid,
            "retmode": "json",
        }
        
        if API_KEY:
            params["api_key"] = API_KEY
        if EMAIL:
            params["email"] = EMAIL
            
        response = requests.get(
            f"{BASE_URL}/esummary.fcgi",
            params=params,
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        article_data = data.get("result", {}).get(pmid, {})
        
        return {
            "pmid": pmid,
            "title": article_data.get("title", "No title available"),
            "authors": article_data.get("authors", []),
            "journal": article_data.get("source", "Unknown journal"),
            "pub_date": article_data.get("pubdate", "Unknown date"),
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "abstract": None  # Would require efetch XML parsing
        }
        
    except requests.RequestException:
        return {
            "pmid": pmid,
            "title": "Article not found",
            "error": "Failed to retrieve article details"
        }
