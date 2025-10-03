#!/usr/bin/env python3
"""
Test updated disease lookup with improved symptom messaging and external resources
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.disease_service import lookup_disease_info
import json


async def test_disease_lookup(disease_name: str):
    """Test disease lookup and display results"""
    print(f"\n{'='*80}")
    print(f"Testing disease lookup for: {disease_name}")
    print(f"{'='*80}\n")

    try:
        result = await lookup_disease_info(disease_name)

        print("Response structure:")
        print(json.dumps(result, indent=2))

        print(f"\n--- Key Information ---")
        print(f"Disease Name: {result.get('disease_name', 'N/A')}")
        print(f"MONDO ID: {result.get('mondo_id', 'N/A')}")

        print(f"\n--- Symptoms ({len(result.get('symptoms', []))}) ---")
        for i, symptom in enumerate(result.get('symptoms', [])[:5], 1):
            print(f"  {i}. {symptom}")

        if result.get('external_resources'):
            print(f"\n--- External Resources ---")
            resources = result['external_resources']
            if resources.get('medlineplus'):
                print(f"  MedlinePlus: {resources['medlineplus']}")
            if resources.get('pubmed'):
                print(f"  PubMed: {resources['pubmed']}")
            if resources.get('mondo'):
                print(f"  MONDO: {resources['mondo']}")

        print(f"\n--- Sources ---")
        print(f"  {', '.join(result.get('sources', []))}")

        # Check for negative language
        symptoms_text = ' '.join(result.get('symptoms', []))
        if 'not available' in symptoms_text.lower() or 'not found' in symptoms_text.lower():
            print("\n⚠️  WARNING: Negative language found in symptoms!")
        else:
            print("\n✓ No negative language detected")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Test multiple diseases"""

    test_diseases = [
        "type 1 diabetes mellitus",
        "asthma",
        "covid-19",
        "rare_disease_xyz_not_found"  # Test not-found case
    ]

    for disease in test_diseases:
        await test_disease_lookup(disease)
        print("\n")


if __name__ == "__main__":
    asyncio.run(main())
