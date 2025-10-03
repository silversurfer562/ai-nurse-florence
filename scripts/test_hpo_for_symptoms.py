#!/usr/bin/env python3
"""
Test HPO (Human Phenotype Ontology) API for disease-phenotype associations
This will help us determine if we can get symptoms from HPO
"""
import requests
import json
from typing import List, Dict, Any


def search_hpo_disease(disease_name: str) -> List[Dict[str, Any]]:
    """Search HPO for disease terms"""
    url = "https://ontology.jax.org/api/hp/search"
    params = {
        "q": disease_name,
        "limit": 10,
        "category": "diseases"  # Try to filter for diseases
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        results = response.json()
        return results.get("terms", [])
    except Exception as e:
        print(f"Error searching HPO: {e}")
        return []


def get_disease_phenotypes_hpo(hpo_disease_id: str) -> List[Dict[str, Any]]:
    """Get phenotypes associated with a disease from HPO"""
    url = f"https://ontology.jax.org/api/hp/terms/{hpo_disease_id}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting HPO term details: {e}")
        return {}


def search_mondo_for_hpo_mapping(mondo_id: str) -> Dict[str, Any]:
    """Try to get HPO annotations from MONDO directly"""
    # MONDO OLS API
    url = f"https://www.ebi.ac.uk/ols/api/ontologies/mondo/terms"
    params = {
        "iri": f"http://purl.obolibrary.org/obo/{mondo_id.replace(':', '_')}"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        print(f"Error querying MONDO via OLS: {e}")
        return {}


def get_mondo_phenotypes(mondo_id: str) -> List[Dict[str, Any]]:
    """Get phenotypes from MONDO using biolink API"""
    # Try BioThings Explorer or Monarch
    url = f"https://api.monarchinitiative.org/api/bioentity/disease/{mondo_id}/phenotypes"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 404:
            print(f"  404 - Disease not found in Monarch phenotypes endpoint")
            return []

        response.raise_for_status()
        data = response.json()

        phenotypes = []
        for assoc in data.get("associations", []):
            phenotype = assoc.get("object", {})
            phenotypes.append({
                "id": phenotype.get("id"),
                "label": phenotype.get("label"),
                "definition": phenotype.get("definition")
            })

        return phenotypes
    except Exception as e:
        print(f"  Error getting Monarch phenotypes: {e}")
        return []


def test_comprehensive_symptom_lookup(disease_name: str, mondo_id: str = None):
    """Test all available methods to get symptoms/phenotypes for a disease"""
    print(f"\n{'='*80}")
    print(f"Testing symptom lookup for: {disease_name}")
    if mondo_id:
        print(f"MONDO ID: {mondo_id}")
    print(f"{'='*80}")

    # Method 1: HPO search
    print("\n--- Method 1: HPO Search ---")
    hpo_results = search_hpo_disease(disease_name)
    print(f"HPO search results: {len(hpo_results)}")
    if hpo_results:
        for i, term in enumerate(hpo_results[:3], 1):
            print(f"  {i}. {term.get('name')} (ID: {term.get('id')})")
            if term.get('definition'):
                print(f"     Def: {term['definition'][:100]}...")

    # Method 2: Monarch phenotypes (if we have MONDO ID)
    if mondo_id:
        print("\n--- Method 2: Monarch Phenotypes API ---")
        monarch_phenotypes = get_mondo_phenotypes(mondo_id)
        print(f"Monarch phenotypes found: {len(monarch_phenotypes)}")
        if monarch_phenotypes:
            for i, pheno in enumerate(monarch_phenotypes[:10], 1):
                print(f"  {i}. {pheno.get('label')} ({pheno.get('id')})")
                if pheno.get('definition'):
                    print(f"     {pheno['definition'][:100]}...")

        return monarch_phenotypes

    return []


def main():
    """Test diseases we know should have symptoms"""

    test_cases = [
        ("type 1 diabetes", "MONDO:0005147"),
        ("asthma", "MONDO:0004979"),
        ("hypertension", "MONDO:0005044"),
        ("pneumonia", "MONDO:0005249"),
        ("heart failure", "MONDO:0005252"),
    ]

    results_summary = []

    for disease_name, mondo_id in test_cases:
        phenotypes = test_comprehensive_symptom_lookup(disease_name, mondo_id)
        results_summary.append({
            "disease": disease_name,
            "mondo_id": mondo_id,
            "phenotypes_found": len(phenotypes),
            "phenotypes": phenotypes[:5]  # First 5
        })

    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}\n")

    for result in results_summary:
        status = "✓" if result["phenotypes_found"] > 0 else "✗"
        print(f"{status} {result['disease']} ({result['mondo_id']})")
        print(f"  Phenotypes: {result['phenotypes_found']}")
        if result['phenotypes']:
            print(f"  Sample: {result['phenotypes'][0].get('label')}")
        print()

    # Recommendations
    total_with_phenotypes = sum(1 for r in results_summary if r["phenotypes_found"] > 0)

    print(f"\n{'='*80}")
    print("RECOMMENDATION")
    print(f"{'='*80}")
    print(f"Diseases with phenotypes: {total_with_phenotypes}/{len(test_cases)}")

    if total_with_phenotypes >= len(test_cases) * 0.6:  # At least 60% success
        print("\n✅ Monarch phenotypes API is viable for symptom data!")
        print("   Next step: Integrate into disease service")
        print("\n   Implementation plan:")
        print("   1. Add Monarch phenotypes fetch to disease_service.py")
        print("   2. Map phenotypes to 'symptoms' field in response")
        print("   3. Update frontend to display phenotypes as clinical features")
    else:
        print("\n⚠️  Monarch API has limited coverage")
        print("   Alternative: Consider HPO annotations or other sources")


if __name__ == "__main__":
    main()
