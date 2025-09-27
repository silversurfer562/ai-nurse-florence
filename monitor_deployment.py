#!/usr/bin/env python3
"""
Monitor Railway deployment progress
"""

import requests
import time
from datetime import datetime

def check_deployment():
    railway_url = "https://ai-nurse-florence-production.up.railway.app"
    
    print(f"🔍 Checking deployment at {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)
    
    try:
        # Check debug endpoint (new version indicator)
        response = requests.get(f"{railway_url}/debug/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("🎉 NEW VERSION DEPLOYED!")
            print(f"   Routers loaded: {data.get('routers_loaded', [])}")
            print(f"   Routers failed: {data.get('routers_failed', [])}")
            print(f"   Wizards available: {data.get('wizards_available', False)}")
            print(f"   Auth available: {data.get('auth_available', False)}")
            return True
        else:
            print(f"❌ Debug endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Debug endpoint error: {e}")
    
    # Check total endpoints
    try:
        response = requests.get(f"{railway_url}/openapi.json", timeout=10)
        if response.status_code == 200:
            data = response.json()
            paths = list(data.get('paths', {}).keys())
            print(f"📊 Total endpoints: {len(paths)}")
            
            # Look for key advanced endpoints
            advanced_endpoints = [
                '/debug/status',
                '/api/v1/summarize/chat', 
                '/api/v1/wizards/sbar-report/start',
                '/api/v1/v1/clinicaltrials/search'
            ]
            
            found = [ep for ep in advanced_endpoints if ep in paths]
            if found:
                print(f"✅ Advanced endpoints found: {len(found)}")
                return True
            else:
                print(f"⏳ Still basic version ({len(paths)} endpoints)")
    except Exception as e:
        print(f"❌ OpenAPI check error: {e}")
    
    return False

if __name__ == "__main__":
    print("🚀 Monitoring Railway deployment...")
    print("Press Ctrl+C to stop")
    print()
    
    success = False
    attempts = 0
    max_attempts = 20  # 10 minutes max
    
    while not success and attempts < max_attempts:
        success = check_deployment()
        attempts += 1
        
        if success:
            print(f"\n🎉 DEPLOYMENT SUCCESSFUL after {attempts} attempts!")
            print("🔗 Advanced features now available at:")
            print("   https://ai-nurse-florence-production.up.railway.app/docs")
            break
        else:
            if attempts < max_attempts:
                print(f"⏳ Waiting 30 seconds... (attempt {attempts}/{max_attempts})")
                print()
                time.sleep(30)
            else:
                print("\n⚠️  Max attempts reached. Build may still be in progress.")
                print("   Check Railway dashboard for build status.")
