#!/usr/bin/env python3
"""
Test script to check live API connections for AI Nurse Florence
"""

import json
import os
import sys

import requests

# Add the project root to the Python path
sys.path.insert(0, '/Users/patrickroebuck/projects/ai-nurse-florence')

def test_mydisease_api():
    """Test MyDisease.info API connection"""
    print("🔍 Testing MyDisease.info API...")
    try:
        response = requests.get(
            "https://mydisease.info/v1/query",
            params={
                "q": "diabetes",
                "size": 1,
                "fields": "mondo,name,description"
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        print("✅ MyDisease.info API: SUCCESS")
        if 'hits' in data and data['hits']:
            print(f"   Found {len(data['hits'])} results for 'diabetes'")
            print(f"   Sample: {data['hits'][0].get('name', 'No name')}")
        return True
    except Exception as e:
        print(f"❌ MyDisease.info API: FAILED - {e}")
        return False

def test_pubmed_api():
    """Test PubMed API connection"""
    print("\n🔍 Testing PubMed API...")
    try:
        response = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
            params={
                "db": "pubmed",
                "term": "diabetes nursing",
                "retmax": 5,
                "retmode": "json"
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        print("✅ PubMed API: SUCCESS")
        if 'esearchresult' in data and 'idlist' in data['esearchresult']:
            ids = data['esearchresult']['idlist']
            print(f"   Found {len(ids)} articles for 'diabetes nursing'")
            print(f"   Sample IDs: {ids[:3]}")
        return True
    except Exception as e:
        print(f"❌ PubMed API: FAILED - {e}")
        return False

def test_clinicaltrials_api():
    """Test ClinicalTrials.gov API connection"""
    print("\n🔍 Testing ClinicalTrials.gov API...")
    try:
        response = requests.get(
            "https://clinicaltrials.gov/api/v2/studies",
            params={
                "query.cond": "diabetes",
                "countTotal": "true",
                "pageSize": 5
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        print("✅ ClinicalTrials.gov API: SUCCESS")
        if 'studies' in data:
            print(f"   Found studies for 'diabetes'")
            print(f"   Total count: {data.get('totalCount', 'Unknown')}")
        return True
    except Exception as e:
        print(f"❌ ClinicalTrials.gov API: FAILED - {e}")
        return False

def test_local_server():
    """Test local server health endpoint"""
    print("\n🔍 Testing local AI Nurse Florence server...")
    try:
        response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
        response.raise_for_status()
        data = response.json()
        print("✅ Local Server: SUCCESS")
        print(f"   Service: {data.get('service', 'Unknown')}")
        print(f"   Version: {data.get('version', 'Unknown')}")

        config = data.get('configuration', {})
        print(f"   Live Services: {config.get('live_services', False)}")
        print(f"   OpenAI Available: {config.get('openai_available', False)}")
        return True
    except Exception as e:
        print(f"❌ Local Server: FAILED - {e}")
        return False

def test_admin_endpoints():
    """Test admin endpoints for live data toggle"""
    print("\n🔍 Testing Admin API endpoints...")
    try:
        # Test live data status endpoint
        response = requests.get("http://localhost:8000/api/v1/admin/live-data-status", timeout=5)
        response.raise_for_status()
        data = response.json()
        print("✅ Admin Live Data Status: SUCCESS")
        print(f"   Live Data Enabled: {data.get('live_data_enabled', False)}")
        print(f"   Message: {data.get('message', 'No message')}")
        return True
    except Exception as e:
        print(f"❌ Admin Endpoints: FAILED - {e}")
        return False

def main():
    """Run all tests"""
    print("🏥 AI Nurse Florence - Live Data Connection Tests")
    print("=" * 60)

    results = []
    results.append(test_mydisease_api())
    results.append(test_pubmed_api())
    results.append(test_clinicaltrials_api())
    results.append(test_local_server())
    results.append(test_admin_endpoints())

    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    passed = sum(results)
    total = len(results)
    print(f"   Passed: {passed}/{total}")

    if passed == total:
        print("🎉 All tests passed! Live data connections are working.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
