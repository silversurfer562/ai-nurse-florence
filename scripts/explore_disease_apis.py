#!/usr/bin/env python3
"""
Explore multiple disease APIs to find best symptom data source
"""
import requests
import json
from typing import Dict, Any, List


def test_mydisease_all_fields(disease_query: str):
    """Get ALL available fields from MyDisease.info"""
    print(f"\n{'='*80}")
    print(f"MyDisease.info - ALL FIELDS for: '{disease_query}'")
    print(f"{'='*80}")

    url = "https://mydisease.info/v1/query"
    params = {
        "q": disease_query,
        "size": 1
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        results = response.json()

        if results.get("hits"):
            hit = results["hits"][0]
            print(f"\nDisease ID: {hit.get('_id')}")
            print(f"\nAll available fields:")
            print(json.dumps(hit, indent=2))

            # List top-level keys
            print(f"\nTop-level keys available:")
            for key in sorted(hit.keys()):
                print(f"  • {key}")

        return results
    except Exception as e:
        print(f"Error: {e}")
        return None


def test_hpo_api(disease_name: str):
    """Test Human Phenotype Ontology API"""
    print(f"\n{'='*80}")
    print(f"HPO API for: '{disease_name}'")
    print(f"{'='*80}")

    # HPO search endpoint
    url = "https://ontology.jax.org/api/hp/search"
    params = {
        "q": disease_name,
        "limit": 5
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        results = response.json()

        print(f"\nResults found: {len(results.get('terms', []))}")
        if results.get('terms'):
            for term in results['terms'][:3]:
                print(f"\n  ID: {term.get('id')}")
                print(f"  Name: {term.get('name')}")
                print(f"  Definition: {term.get('definition', 'N/A')[:100]}...")

        return results
    except Exception as e:
        print(f"Error: {e}")
        return None


def test_monarch_disease_phenotypes(disease_id: str):
    """Test Monarch Initiative for disease phenotypes"""
    print(f"\n{'='*80}")
    print(f"Monarch API - Phenotypes for disease ID: '{disease_id}'")
    print(f"{'='*80}")

    # Try to get phenotypes associated with disease
    url = f"https://api.monarchinitiative.org/api/bioentity/disease/{disease_id}/phenotypes"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        results = response.json()

        print(f"\nPhenotypes found: {len(results.get('associations', []))}")

        if results.get('associations'):
            for assoc in results['associations'][:10]:
                phenotype = assoc.get('object', {})
                print(f"\n  • {phenotype.get('label', 'N/A')}")
                print(f"    ID: {phenotype.get('id', 'N/A')}")
                if phenotype.get('definition'):
                    print(f"    Def: {phenotype['definition'][:100]}...")

        return results
    except Exception as e:
        print(f"Error: {e}")
        return None


def test_disease_ontology(disease_name: str):
    """Test Disease Ontology API"""
    print(f"\n{'='*80}")
    print(f"Disease Ontology API for: '{disease_name}'")
    print(f"{'='*80}")

    url = "https://www.disease-ontology.org/api/metadata/search"
    params = {
        "term": disease_name
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        results = response.json()

        print(f"\nResults:")
        print(json.dumps(results, indent=2)[:500])

        return results
    except Exception as e:
        print(f"Error: {e}")
        return None


def test_opentargets(disease_name: str):
    """Test OpenTargets Platform API"""
    print(f"\n{'='*80}")
    print(f"OpenTargets Platform for: '{disease_name}'")
    print(f"{'='*80}")

    # GraphQL query
    query = """
    query DiseaseSearch($queryString: String!) {
      search(queryString: $queryString, entityNames: "disease", page: {size: 3}) {
        hits {
          id
          name
          description
          entity
        }
      }
    }
    """

    url = "https://api.platform.opentargets.org/api/v4/graphql"

    try:
        response = requests.post(
            url,
            json={
                "query": query,
                "variables": {"queryString": disease_name}
            },
            timeout=10
        )
        response.raise_for_status()
        results = response.json()

        if results.get('data', {}).get('search', {}).get('hits'):
            for hit in results['data']['search']['hits']:
                print(f"\n  ID: {hit['id']}")
                print(f"  Name: {hit['name']}")
                print(f"  Description: {hit.get('description', 'N/A')[:100]}...")

        return results
    except Exception as e:
        print(f"Error: {e}")
        return None


def test_orphanet(disease_name: str):
    """Test Orphanet API for rare diseases"""
    print(f"\n{'='*80}")
    print(f"Orphanet API for: '{disease_name}'")
    print(f"{'='*80}")

    # Orphanet search
    url = f"https://api.orphacode.org/EN/ClinicalEntity/ApproximateName/{disease_name}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        results = response.json()

        print(f"\nResults found: {len(results) if isinstance(results, list) else 'N/A'}")
        if isinstance(results, list) and results:
            for result in results[:3]:
                print(f"\n  Name: {result.get('Preferred term', 'N/A')}")
                print(f"  ORPHAcode: {result.get('ORPHAcode', 'N/A')}")

        return results
    except Exception as e:
        print(f"Error: {e}")
        return None


def main():
    test_disease = "type 1 diabetes"

    print("\n" + "="*80)
    print("COMPREHENSIVE API EXPLORATION")
    print("="*80)

    # 1. MyDisease.info - see all fields
    mydisease_results = test_mydisease_all_fields(test_disease)

    # 2. HPO API
    hpo_results = test_hpo_api(test_disease)

    # 3. Monarch with specific MONDO ID
    monarch_results = test_monarch_disease_phenotypes("MONDO:0005147")  # Type 1 diabetes

    # 4. Disease Ontology
    # do_results = test_disease_ontology(test_disease)

    # 5. OpenTargets
    opentargets_results = test_opentargets(test_disease)

    # 6. Orphanet
    # orphanet_results = test_orphanet(test_disease)

    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY & RECOMMENDATIONS")
    print(f"{'='*80}")

    apis_tested = {
        "MyDisease.info": mydisease_results is not None,
        "HPO": hpo_results is not None,
        "Monarch": monarch_results is not None,
        "OpenTargets": opentargets_results is not None,
    }

    for api, success in apis_tested.items():
        status = "✓" if success else "✗"
        print(f"{status} {api}")

    print("\nNext steps:")
    print("1. If Monarch phenotypes API works → use it for symptoms")
    print("2. If HPO has disease-phenotype mappings → explore HPO annotations")
    print("3. Consider hybrid approach: disease info from MyDisease + phenotypes from Monarch")


if __name__ == "__main__":
    main()
