#!/usr/bin/env python3
"""
Test HPO disease-to-phenotype annotations API
HPO has a dedicated API for getting phenotypes associated with diseases
"""
import requests
import json
from typing import List, Dict, Any


def get_hpo_disease_annotations(disease_name: str = None, disease_id: str = None) -> List[Dict[str, Any]]:
    """
    Get HPO phenotype annotations for a disease using HPO's annotations API

    Args:
        disease_name: Disease name (e.g., "diabetes mellitus")
        disease_id: Disease ID like OMIM, MONDO, ORPHA (e.g., "OMIM:222100")
    """
    # HPO annotations endpoint
    base_url = "https://hpo.jax.org/api/hpo/disease"

    # Build query
    if disease_id:
        url = f"{base_url}/{disease_id}"
    elif disease_name:
        # Search for disease first
        search_url = "https://hpo.jax.org/api/hpo/search"
        params = {"q": disease_name, "max": 10, "category": "diseases"}

        try:
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            results = response.json()

            if results.get("diseases"):
                # Use first disease result
                first_disease = results["diseases"][0]
                disease_id = first_disease.get("diseaseId")
                url = f"{base_url}/{disease_id}"
            else:
                print(f"  No diseases found for: {disease_name}")
                return []
        except Exception as e:
            print(f"  Error searching for disease: {e}")
            return []
    else:
        print("  Must provide either disease_name or disease_id")
        return []

    # Get disease details including phenotypes
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        disease_data = response.json()

        # Extract phenotype annotations
        phenotypes = []
        if disease_data.get("catTermsMap"):
            for category, terms in disease_data["catTermsMap"].items():
                for term in terms:
                    phenotypes.append({
                        "id": term.get("id"),
                        "name": term.get("name"),
                        "category": category,
                        "definition": term.get("definition", "")
                    })

        return phenotypes
    except Exception as e:
        print(f"  Error getting disease annotations: {e}")
        return []


def test_disease_with_known_ids():
    """Test with diseases using known IDs"""

    test_cases = [
        # Use OMIM IDs which HPO supports well
        ("Type 1 Diabetes Mellitus", "OMIM:222100"),
        ("Asthma", "OMIM:600807"),
        # Try MONDO IDs
        ("Type 1 Diabetes (MONDO)", "MONDO:0005147"),
        ("Asthma (MONDO)", "MONDO:0004979"),
    ]

    results = []

    for disease_name, disease_id in test_cases:
        print(f"\n{'='*80}")
        print(f"Testing: {disease_name} ({disease_id})")
        print(f"{'='*80}")

        phenotypes = get_hpo_disease_annotations(disease_id=disease_id)

        print(f"Phenotypes found: {len(phenotypes)}")
        if phenotypes:
            print("\nSample phenotypes:")
            for i, pheno in enumerate(phenotypes[:10], 1):
                print(f"  {i}. [{pheno.get('category')}] {pheno.get('name')} ({pheno.get('id')})")
                if pheno.get('definition'):
                    print(f"     {pheno['definition'][:80]}...")

        results.append({
            "disease": disease_name,
            "id": disease_id,
            "phenotype_count": len(phenotypes),
            "phenotypes": phenotypes
        })

    return results


def test_disease_by_name_search():
    """Test by searching for disease names"""

    disease_names = [
        "type 1 diabetes mellitus",
        "asthma",
        "hypertension",
        "pneumonia"
    ]

    results = []

    for disease_name in disease_names:
        print(f"\n{'='*80}")
        print(f"Testing: {disease_name}")
        print(f"{'='*80}")

        phenotypes = get_hpo_disease_annotations(disease_name=disease_name)

        print(f"Phenotypes found: {len(phenotypes)}")
        if phenotypes:
            print("\nSample phenotypes:")
            for i, pheno in enumerate(phenotypes[:10], 1):
                print(f"  {i}. [{pheno.get('category')}] {pheno.get('name')} ({pheno.get('id')})")

        results.append({
            "disease": disease_name,
            "phenotype_count": len(phenotypes)
        })

    return results


def main():
    print("\n" + "="*80)
    print("HPO DISEASE ANNOTATIONS TEST")
    print("Testing HPO's disease-to-phenotype annotation API")
    print("="*80)

    # Test with known IDs first
    print("\n### TEST 1: Known Disease IDs ###")
    id_results = test_disease_with_known_ids()

    # Test with name search
    print("\n\n### TEST 2: Disease Name Search ###")
    name_results = test_disease_by_name_search()

    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY & RECOMMENDATION")
    print(f"{'='*80}\n")

    id_with_phenotypes = sum(1 for r in id_results if r["phenotype_count"] > 0)
    name_with_phenotypes = sum(1 for r in name_results if r["phenotype_count"] > 0)

    print(f"ID-based queries with phenotypes: {id_with_phenotypes}/{len(id_results)}")
    print(f"Name-based queries with phenotypes: {name_with_phenotypes}/{len(name_results)}")

    if id_with_phenotypes > 0 or name_with_phenotypes > 0:
        print("\n✅ HPO disease annotations API can provide phenotype/symptom data!")
        print("\nImplementation strategy:")
        print("1. When we have a MONDO ID from disease lookup:")
        print("   - Try HPO with MONDO ID")
        print("   - Fallback to OMIM ID if available in disease data")
        print("2. Extract phenotypes from HPO 'catTermsMap'")
        print("3. Map phenotypes to 'symptoms' field for frontend display")
        print("\nNext step: Integrate HPO annotations into disease_service.py")
    else:
        print("\n⚠️  HPO annotations API needs different approach")
        print("   May need to use different disease ID system or API endpoint")


if __name__ == "__main__":
    main()
