#!/usr/bin/env python3
"""
Test MedlinePlus API for symptom information
MedlinePlus is maintained by NIH and has comprehensive health information including symptoms
"""
import requests
import json
import xml.etree.ElementTree as ET
from typing import List, Dict, Any


def search_medlineplus(query: str) -> List[Dict[str, Any]]:
    """
    Search MedlinePlus health topics

    MedlinePlus provides XML API for health information
    """
    base_url = "https://wsearch.nlm.nih.gov/ws/query"

    params = {
        "db": "healthTopics",
        "term": query,
        "retmax": 5
    }

    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()

        # Parse XML response
        root = ET.fromstring(response.content)

        results = []
        for document in root.findall('.//document'):
            title = document.get('title', '')
            url = document.get('url', '')
            summary = document.find('.//content[@name="FullSummary"]')
            summary_text = summary.text if summary is not None else ""

            results.append({
                "title": title,
                "url": url,
                "summary": summary_text[:200] if summary_text else ""
            })

        return results

    except Exception as e:
        print(f"Error searching MedlinePlus: {e}")
        return []


def get_medlineplus_page_content(topic_url: str) -> Dict[str, Any]:
    """
    Fetch and parse MedlinePlus page content
    Note: This would require HTML parsing in practice
    """
    try:
        response = requests.get(topic_url, timeout=10)
        response.raise_for_status()

        # In a real implementation, we'd parse the HTML
        # For now, just return the URL
        return {
            "url": topic_url,
            "note": "Would need HTML parsing to extract symptoms section"
        }

    except Exception as e:
        print(f"Error fetching page: {e}")
        return {}


def test_practical_symptom_solution():
    """
    Test a practical approach: use what we have + add helper text
    """

    print("\n" + "="*80)
    print("PRACTICAL SYMPTOM SOLUTION TEST")
    print("="*80)

    test_diseases = [
        "type 1 diabetes",
        "asthma",
        "hypertension",
        "pneumonia"
    ]

    print("\nApproach 1: MedlinePlus Integration")
    print("-" * 80)

    for disease in test_diseases:
        print(f"\nDisease: {disease}")
        results = search_medlineplus(disease)

        if results:
            print(f"  ✓ Found {len(results)} MedlinePlus topics")
            print(f"  Primary: {results[0]['title']}")
            print(f"  URL: {results[0]['url']}")
            if results[0]['summary']:
                print(f"  Summary: {results[0]['summary'][:100]}...")
        else:
            print(f"  ✗ No MedlinePlus results")

    print("\n\n" + "="*80)
    print("RECOMMENDATION: Hybrid Approach")
    print("="*80)

    recommendation = """
Since direct API access to comprehensive symptom data is limited, here's the best approach:

1. **Update Disease Service** to include MedlinePlus links:
   - When disease is looked up, generate MedlinePlus search URL
   - Add to external_resources in response
   - Example: https://medlineplus.gov/diabetes.html

2. **Improve UI Messaging** (remove negative language):
   Instead of: "❌ Detailed symptom information is not available in the database"

   Use: "📚 Comprehensive clinical information available:
          → MedlinePlus: [link] (patient-friendly symptom information)
          → PubMed: [link] (research articles and clinical studies)
          → MONDO: [link] (disease ontology and classification)"

3. **Add Quick Symptom Guide** (curated common symptoms):
   - For top 50-100 common diseases, add curated symptom lists
   - Store in database as part of disease_reference
   - Source from reliable medical textbooks/guidelines

4. **Future Enhancement**:
   - Integrate with clinical knowledge bases (UpToDate API if available)
   - Use LLM to extract symptoms from PubMed abstracts
   - Build symptom database from medical literature

This gives nurses immediate access to symptom information while being honest about
data limitations.
    """

    print(recommendation)

    # Example of improved response structure
    print("\n" + "="*80)
    print("EXAMPLE IMPROVED API RESPONSE")
    print("="*80)

    example_response = {
        "disease_name": "Type 1 Diabetes Mellitus",
        "mondo_id": "MONDO:0005147",
        "icd10_codes": ["E10"],
        "description": "An autoimmune disease causing absolute insulin deficiency...",

        # Enhanced external resources
        "external_resources": {
            "medlineplus": {
                "url": "https://medlineplus.gov/diabetestype1.html",
                "title": "Type 1 Diabetes",
                "description": "Comprehensive patient information including symptoms, causes, treatment"
            },
            "pubmed": {
                "url": "https://pubmed.ncbi.nlm.nih.gov/?term=type+1+diabetes+symptoms",
                "title": "Research Articles",
                "description": "Latest clinical research and studies"
            },
            "mondo": {
                "url": "https://monarchinitiative.org/disease/MONDO:0005147",
                "title": "Disease Ontology",
                "description": "Disease classification and relationships"
            }
        },

        # Common symptoms (curated)
        "common_clinical_features": [
            {
                "feature": "Polyuria",
                "description": "Excessive urination",
                "frequency": "very common"
            },
            {
                "feature": "Polydipsia",
                "description": "Excessive thirst",
                "frequency": "very common"
            },
            {
                "feature": "Weight loss",
                "description": "Unintentional weight loss despite normal eating",
                "frequency": "common"
            },
            {
                "feature": "Fatigue",
                "description": "Persistent tiredness and lack of energy",
                "frequency": "common"
            }
        ],

        # Helpful message
        "clinical_information_note": "For comprehensive symptom information, see MedlinePlus link above. Clinical manifestations may vary between individuals."
    }

    print(json.dumps(example_response, indent=2))


if __name__ == "__main__":
    test_practical_symptom_solution()
