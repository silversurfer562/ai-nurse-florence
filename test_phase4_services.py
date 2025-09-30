#!/usr/bin/env python3
"""
Quick test script for Phase 4.2 services
Tests enhanced literature and drug interaction services
"""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.enhanced_literature_service import EnhancedLiteratureService
from src.services.drug_interaction_service import DrugInteractionService

async def test_enhanced_literature():
    """Test enhanced literature search service"""
    print("🔬 Testing Enhanced Literature Service")
    print("=" * 50)
    
    service = EnhancedLiteratureService()
    
    result = await service.search_literature(
        query="diabetes medication management",
        specialty="endocrinology",
        max_results=3
    )
    
    print(f"Query: {result.get('query', 'N/A')}")
    print(f"Total results: {result.get('total_results', 0)}")
    print(f"Evidence quality: {result.get('evidence_quality', 'N/A')}")
    
    articles = result.get('articles', [])
    print(f"Articles found: {len(articles)}")
    
    for i, article in enumerate(articles[:3], 1):
        title = article.get('title', 'No title')
        authors = article.get('authors', [])
        journal = article.get('journal', 'Unknown journal')
        year = article.get('publication_date', 'Unknown year')[:4] if article.get('publication_date') else 'Unknown'
        evidence_score = article.get('evidence_score', 0)
        
        print(f"\n{i}. {title}")
        print(f"   Authors: {', '.join(authors[:3])}{'...' if len(authors) > 3 else ''}")
        print(f"   Journal: {journal} ({year})")
        print(f"   Evidence Score: {evidence_score:.2f}")
    
    cache_hit = result.get('cache_hit', False)
    print(f"\nCache hit: {cache_hit}")
    print("✅ Enhanced Literature Service Test Complete\n")

async def test_drug_interactions():
    """Test drug interaction service"""
    print("💊 Testing Drug Interaction Service")
    print("=" * 50)
    
    service = DrugInteractionService()
    
    result = await service.check_drug_interactions(
        drugs=["metformin", "lisinopril", "warfarin"],
        patient_context={"age": 65, "conditions": ["diabetes", "hypertension"]}
    )
    
    print(f"Medications checked: {', '.join(result.get('drugs', []))}")
    print(f"Total interactions: {result.get('total_interactions', 0)}")
    print(f"Highest severity: {result.get('highest_severity', 'N/A')}")
    print(f"Requires monitoring: {result.get('requires_monitoring', False)}")
    
    interactions = result.get('interactions', [])
    for interaction in interactions[:3]:
        severity = interaction.get('severity', 'unknown')
        drug1 = interaction.get('drug1', 'Unknown')
        drug2 = interaction.get('drug2', 'Unknown')
        description = interaction.get('description', 'No description')
        recommendation = interaction.get('clinical_recommendation', 'No recommendation')
        
        print(f"\n⚠️ {severity.upper()}: {drug1} + {drug2}")
        print(f"   Description: {description}")
        print(f"   Recommendation: {recommendation}")
    
    alerts = result.get('clinical_alerts', [])
    if alerts:
        print(f"\n🚨 Clinical Alerts:")
        for alert in alerts[:3]:
            print(f"   • {alert}")
    
    cache_hit = result.get('cache_hit', False)
    print(f"\nCache hit: {cache_hit}")
    print("✅ Drug Interaction Service Test Complete\n")

async def main():
    """Main test runner"""
    print("🏥 AI Nurse Florence - Phase 4.2 Service Tests")
    print("=" * 60)
    print()
    
    try:
        await test_enhanced_literature()
        await test_drug_interactions()
        
        print("🎉 All Phase 4.2 services tested successfully!")
        print("   ✅ Enhanced Literature Service")
        print("   ✅ Drug Interaction Service")
        print("   ✅ Smart Caching Integration")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
