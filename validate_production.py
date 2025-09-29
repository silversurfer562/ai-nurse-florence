#!/usr/bin/env python3
"""
AI Nurse Florence - Production Validation Script
Tests live medical data integration and AI clinical decision support
"""

import asyncio
import json
from datetime import datetime

import httpx

# Configuration
BASE_URL = "http://localhost:8001"  # Change to Railway URL when deployed
RAILWAY_URL = "https://your-app.railway.app"  # Replace with actual Railway URL

async def test_health_endpoint():
    """Test basic health and system status"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/api/v1/health")
            data = response.json()
            print("✅ Health Check:")
            print(f"   Status: {data.get('status', 'Unknown')}")
            print(f"   Version: {data.get('version', 'Unknown')}")
            print(f"   Live Services: {data.get('configuration', {}).get('live_services', False)}")
            print(f"   OpenAI Available: {data.get('configuration', {}).get('openai_available', False)}")
            print(f"   Routers Loaded: {len(data.get('routes', {}).get('routers_loaded', {}))}")
            return True
        except Exception as e:
            print(f"❌ Health Check Failed: {e}")
            return False

async def test_disease_lookup():
    """Test live disease information lookup"""
    test_conditions = ["hypertension", "diabetes mellitus", "acute heart failure"]

    async with httpx.AsyncClient() as client:
        print("\n🔬 Testing Disease Lookup (Live Medical Data):")

        for condition in test_conditions:
            try:
                response = await client.get(f"{BASE_URL}/api/v1/disease/lookup?q={condition}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ {condition}: {data.get('name', 'N/A')}")
                    if data.get('summary'):
                        print(f"      Summary: {data['summary'][:100]}...")
                else:
                    print(f"   ❌ {condition}: HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ {condition}: {e}")

async def test_literature_search():
    """Test PubMed literature search"""
    async with httpx.AsyncClient() as client:
        print("\n📚 Testing Literature Search (PubMed API):")

        try:
            response = await client.get(f"{BASE_URL}/api/v1/literature?q=nursing+care+diabetes&max_results=3")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Found {len(data.get('articles', []))} articles")
                for article in data.get('articles', [])[:2]:
                    print(f"      - {article.get('title', 'No title')[:80]}...")
            else:
                print(f"   ❌ Literature Search: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ Literature Search: {e}")

async def test_clinical_trials():
    """Test clinical trials search"""
    async with httpx.AsyncClient() as client:
        print("\n🏥 Testing Clinical Trials (ClinicalTrials.gov API):")

        try:
            response = await client.get(f"{BASE_URL}/api/v1/clinical-trials?condition=heart+failure&max_results=3")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Found {len(data.get('studies', []))} studies")
                for study in data.get('studies', [])[:2]:
                    print(f"      - {study.get('title', 'No title')[:80]}...")
            else:
                print(f"   ❌ Clinical Trials: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ Clinical Trials: {e}")

async def test_clinical_decision_support():
    """Test AI-powered clinical decision support"""
    async with httpx.AsyncClient() as client:
        print("\n🧠 Testing AI Clinical Decision Support:")

        try:
            payload = {
                "patient_condition": "acute heart failure",
                "severity": "moderate",
                "care_setting": "med-surg"
            }

            response = await client.post(
                f"{BASE_URL}/api/v1/clinical-decision-support/interventions",
                params=payload,
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()
                print("   ✅ AI Clinical Recommendations Generated")
                if data.get('nursing_interventions'):
                    print(f"      Interventions: {len(data['nursing_interventions'])} recommendations")
                if data.get('monitoring_parameters'):
                    print(f"      Monitoring: {len(data['monitoring_parameters'])} parameters")
                print(f"      Banner: {data.get('banner', 'N/A')[:60]}...")
            else:
                print(f"   ❌ Clinical Decision Support: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ Clinical Decision Support: {e}")

async def test_wizard_workflow():
    """Test nursing assessment wizard"""
    async with httpx.AsyncClient() as client:
        print("\n🧙 Testing Nursing Assessment Wizard:")

        try:
            # Start wizard
            response = await client.post(f"{BASE_URL}/api/v1/nursing-assessment/start")
            if response.status_code == 200:
                data = response.json()
                wizard_id = data.get('wizard_id')
                print(f"   ✅ Wizard Started: {wizard_id}")

                # Test wizard step
                if wizard_id:
                    step_payload = {
                        "patient_name": "Test Patient",
                        "primary_diagnosis": "Hypertension",
                        "admission_date": datetime.now().isoformat()
                    }

                    step_response = await client.post(
                        f"{BASE_URL}/api/v1/nursing-assessment/{wizard_id}/patient-info",
                        json=step_payload
                    )

                    if step_response.status_code == 200:
                        print("   ✅ Wizard Step Completed Successfully")
                    else:
                        print(f"   ❌ Wizard Step: HTTP {step_response.status_code}")
            else:
                print(f"   ❌ Wizard Start: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ Wizard Workflow: {e}")

async def main():
    """Run comprehensive system validation"""
    print("🏥 AI NURSE FLORENCE - PRODUCTION VALIDATION")
    print("=" * 50)
    print(f"Testing Base URL: {BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    # Run all tests
    health_ok = await test_health_endpoint()

    if health_ok:
        await test_disease_lookup()
        await test_literature_search()
        await test_clinical_trials()
        await test_clinical_decision_support()
        await test_wizard_workflow()
    else:
        print("\n❌ System health check failed. Skipping additional tests.")

    print("\n" + "=" * 50)
    print("🏁 Validation Complete")
    print("\nNext Steps:")
    print("1. Deploy to Railway with environment variables")
    print("2. Update BASE_URL to Railway deployment URL")
    print("3. Run this script against production")
    print("4. Begin clinical validation with healthcare professionals")

if __name__ == "__main__":
    asyncio.run(main())
