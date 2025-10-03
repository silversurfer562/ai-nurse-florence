#!/usr/bin/env python3
"""
Test script to explore MyDisease.info API for symptom availability
"""
import requests
import json
from typing import Dict, Any


def test_mydisease_symptoms(disease_query: str) -> Dict[str, Any]:
    """Test MyDisease.info for symptom availability"""

    # Query 1: Search for disease
    search_url = "https://mydisease.info/v1/query"
    search_params = {
        "q": disease_query,
        "fields": "mondo,disease_ontology,hpo,symptoms,phenotype,clinical_features,name,definition,synonyms",
        "size": 5
    }

    print(f"\n{'='*80}")
    print(f"Testing MyDisease.info for: '{disease_query}'")
    print(f"{'='*80}")

    try:
        response = requests.get(search_url, params=search_params, timeout=10)
        response.raise_for_status()
        results = response.json()

        print(f"\n--- Search Results ---")
        print(f"Total hits: {results.get('total', 0)}")
        print(f"Returned: {len(results.get('hits', []))}")

        if results.get("hits"):
            for idx, hit in enumerate(results["hits"][:3], 1):  # Show top 3
                print(f"\n--- Result #{idx} ---")
                print(f"ID: {hit.get('_id')}")
                print(f"Score: {hit.get('_score')}")
                print(f"Name: {hit.get('name', 'N/A')}")

                # Check for symptom-related fields
                symptom_fields = {
                    'hpo': 'Human Phenotype Ontology',
                    'symptoms': 'Direct Symptoms',
                    'phenotype': 'Phenotype Data',
                    'clinical_features': 'Clinical Features'
                }

                print(f"\nSymptom-related fields present:")
                for field, description in symptom_fields.items():
                    if field in hit:
                        field_data = hit[field]
                        if isinstance(field_data, list):
                            print(f"  ✓ {description} ({field}): {len(field_data)} items")
                        elif isinstance(field_data, dict):
                            print(f"  ✓ {description} ({field}): dictionary with {len(field_data)} keys")
                        else:
                            print(f"  ✓ {description} ({field}): {type(field_data).__name__}")
                    else:
                        print(f"  ✗ {description} ({field}): not present")

        # Query 2: Get detailed disease info by ID (if we have results)
        if results.get("hits"):
            disease_id = results["hits"][0].get("_id")

            print(f"\n{'='*80}")
            print(f"Detailed Query for ID: {disease_id}")
            print(f"{'='*80}")

            detail_url = f"https://mydisease.info/v1/disease/{disease_id}"
            detail_params = {
                "fields": "mondo,hpo,symptoms,phenotype,clinical_features,name,definition"
            }

            detail_response = requests.get(detail_url, params=detail_params, timeout=10)
            detail_response.raise_for_status()
            detail = detail_response.json()

            print(f"\n--- Detailed Disease Info ---")
            print(json.dumps(detail, indent=2))

            # Extract and display symptoms if available
            print(f"\n--- Symptom Extraction Test ---")
            symptoms_found = []

            # HPO data
            if "hpo" in detail:
                hpo_data = detail["hpo"]
                if isinstance(hpo_data, list):
                    for hpo in hpo_data[:5]:  # First 5
                        if isinstance(hpo, dict):
                            symptoms_found.append({
                                "source": "HPO",
                                "label": hpo.get("label", hpo.get("name", "Unknown")),
                                "id": hpo.get("id", "")
                            })
                elif isinstance(hpo_data, dict):
                    symptoms_found.append({
                        "source": "HPO",
                        "label": hpo_data.get("label", hpo_data.get("name", "Unknown")),
                        "id": hpo_data.get("id", "")
                    })

            # Direct symptoms
            if "symptoms" in detail:
                symptom_data = detail["symptoms"]
                if isinstance(symptom_data, list):
                    for symptom in symptom_data[:5]:
                        if isinstance(symptom, str):
                            symptoms_found.append({
                                "source": "Direct",
                                "label": symptom
                            })
                        elif isinstance(symptom, dict):
                            symptoms_found.append({
                                "source": "Direct",
                                "label": symptom.get("name", symptom.get("label", "Unknown"))
                            })

            # Phenotype data
            if "phenotype" in detail:
                pheno_data = detail["phenotype"]
                if isinstance(pheno_data, list):
                    for pheno in pheno_data[:5]:
                        if isinstance(pheno, dict):
                            symptoms_found.append({
                                "source": "Phenotype",
                                "label": pheno.get("label", pheno.get("name", "Unknown"))
                            })

            print(f"\nTotal symptoms extracted: {len(symptoms_found)}")
            if symptoms_found:
                print("\nSample symptoms:")
                for symptom in symptoms_found[:10]:  # Show first 10
                    print(f"  • [{symptom.get('source')}] {symptom.get('label')}")
                    if symptom.get('id'):
                        print(f"    ID: {symptom['id']}")
            else:
                print("⚠️  No symptoms could be extracted from available fields")

        return results

    except requests.exceptions.RequestException as e:
        print(f"❌ Error querying MyDisease.info: {e}")
        return {}


def main():
    """Test multiple diseases to validate symptom availability"""

    test_diseases = [
        "type 1 diabetes mellitus",
        "asthma",
        "hypertension",
        "pneumonia",
        "heart failure",
        "MONDO:0005148",  # Try with MONDO ID for type 1 diabetes
    ]

    results_summary = []

    for disease in test_diseases:
        results = test_mydisease_symptoms(disease)

        # Collect summary
        if results.get("hits"):
            hit = results["hits"][0]
            symptom_count = 0

            for field in ['hpo', 'symptoms', 'phenotype', 'clinical_features']:
                if field in hit:
                    data = hit[field]
                    if isinstance(data, list):
                        symptom_count += len(data)
                    elif data:
                        symptom_count += 1

            results_summary.append({
                "query": disease,
                "found": True,
                "symptom_fields": symptom_count,
                "name": hit.get("name", "N/A")
            })
        else:
            results_summary.append({
                "query": disease,
                "found": False,
                "symptom_fields": 0
            })

    # Print summary
    print(f"\n{'='*80}")
    print("SUMMARY OF ALL TESTS")
    print(f"{'='*80}\n")

    for summary in results_summary:
        status = "✓" if summary["found"] else "✗"
        print(f"{status} {summary['query']}")
        if summary["found"]:
            print(f"  Name: {summary.get('name', 'N/A')}")
            print(f"  Symptom field items: {summary['symptom_fields']}")
        print()

    # Overall assessment
    found_count = sum(1 for s in results_summary if s["found"])
    symptom_count = sum(s["symptom_fields"] for s in results_summary)

    print(f"\n{'='*80}")
    print("ASSESSMENT")
    print(f"{'='*80}")
    print(f"Diseases found: {found_count}/{len(test_diseases)}")
    print(f"Total symptom field items: {symptom_count}")

    if symptom_count > 0:
        print("\n✅ MyDisease.info HAS symptom data available!")
        print("   Recommendation: Proceed with integration")
    else:
        print("\n⚠️  Limited symptom data found")
        print("   Recommendation: Investigate alternative sources or field names")


if __name__ == "__main__":
    main()
