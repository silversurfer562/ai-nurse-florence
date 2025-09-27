#!/usr/bin/env python3
"""
Quick script to check if Railway has deployed the latest version
"""

import requests

def check_deployment():
    base_url = "https://ai-nurse-florence-production.up.railway.app"
    
    print("🔍 Checking Railway deployment status...")
    print("=" * 50)
    
    # Check if debug endpoint exists (new version)
    try:
        response = requests.get(f"{base_url}/debug/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ NEW VERSION DEPLOYED!")
            print(f"   Routers loaded: {data.get('routers_loaded', 'N/A')}")
            print(f"   Routers failed: {data.get('routers_failed', 'N/A')}")
            print(f"   Wizards available: {data.get('wizards_available', 'N/A')}")
            print(f"   Auth available: {data.get('auth_available', 'N/A')}")
            return True
        else:
            print(f"❌ Debug endpoint returned {response.status_code}")
    except Exception as e:
        print(f"❌ Debug endpoint not available: {e}")
    
    # Check available endpoints via OpenAPI
    try:
        response = requests.get(f"{base_url}/openapi.json", timeout=10)
        if response.status_code == 200:
            data = response.json()
            paths = list(data.get('paths', {}).keys())
            print(f"\n📋 Available endpoints ({len(paths)} total):")
            for path in sorted(paths)[:10]:  # Show first 10
                print(f"   {path}")
            if len(paths) > 10:
                print(f"   ... and {len(paths) - 10} more")
                
            # Check for advanced endpoints
            advanced_endpoints = [
                '/debug/status',
                '/api/v1/summarize/chat',
                '/api/v1/wizards/sbar-report/start'
            ]
            
            found_advanced = [ep for ep in advanced_endpoints if ep in paths]
            if found_advanced:
                print(f"\n✅ Advanced endpoints found: {found_advanced}")
                return True
            else:
                print("\n❌ No advanced endpoints found. Still running old version.")
                return False
    except Exception as e:
        print(f"❌ Could not check OpenAPI: {e}")
    
    return False

if __name__ == "__main__":
    success = check_deployment()
    if success:
        print("\n🎉 Deployment successful!")
    else:
        print("\n⚠️  Still running old version - manual intervention needed")
