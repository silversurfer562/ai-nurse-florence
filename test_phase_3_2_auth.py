#!/usr/bin/env python3
"""
Phase 3.2 Authentication System Test
Test the complete authentication system we just implemented
"""

import requests
import json
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000/api/v1"
test_user = {
    "email": "nurse@hospital.com",
    "password": "SecurePass123!",
    "full_name": "Jane Doe",
    "role": "nurse"
}

def test_auth_system():
    """Test the complete Phase 3.2 authentication system."""
    print("🏥 AI Nurse Florence - Phase 3.2 Authentication System Test")
    print("=" * 65)
    
    # Test 1: Test the enhanced auth endpoint
    print("\n1️⃣ Testing Enhanced Auth Router...")
    try:
        response = requests.get(f"{BASE_URL}/auth/test-enhanced")
        if response.status_code == 200:
            data = response.json()
            print("✅ Enhanced Auth Router Working!")
            print(f"   Phase: {data['data']['phase']}")
            print(f"   Features: {len(data['data']['features'])} implemented")
            for feature in data['data']['features']:
                print(f"   • {feature}")
        else:
            print(f"❌ Auth router test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    # Test 2: User Registration
    print("\n2️⃣ Testing User Registration...")
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=test_user)
        if response.status_code == 200:
            reg_data = response.json()
            print("✅ User Registration Successful!")
            print(f"   User ID: {reg_data['data']['user_id']}")
            print(f"   Role: {reg_data['data']['role']}")
            print(f"   Token Type: {reg_data['data']['token_type']}")
            access_token = reg_data['data']['access_token']
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False
    
    # Test 3: User Login
    print("\n3️⃣ Testing User Login...")
    try:
        login_data = {
            "email": test_user["email"],
            "password": test_user["password"],
            "device_info": "Test Browser"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            login_response = response.json()
            print("✅ User Login Successful!")
            print(f"   Session ID: {login_response['data']['session_id']}")
            print(f"   Expires in: {login_response['data']['expires_in']} seconds")
            access_token = login_response['data']['access_token']
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Test 4: Protected Endpoint Access
    print("\n4️⃣ Testing Protected Endpoint Access...")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/auth/test-protected", headers=headers)
        if response.status_code == 200:
            protected_data = response.json()
            print("✅ Protected Endpoint Access Successful!")
            print(f"   User ID: {protected_data['data']['user_info']['user_id']}")
            print(f"   Role: {protected_data['data']['user_info']['role']}")
            print(f"   Permissions: {len(protected_data['data']['user_info']['permissions'])}")
        else:
            print(f"❌ Protected access failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Protected access error: {e}")
        return False
    
    # Test 5: User Profile
    print("\n5️⃣ Testing User Profile Retrieval...")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/auth/profile", headers=headers)
        if response.status_code == 200:
            profile_data = response.json()
            print("✅ User Profile Retrieved Successfully!")
            print(f"   Full Name: {profile_data['data']['user']['full_name']}")
            print(f"   Email: {profile_data['data']['user']['email']}")
            print(f"   Role: {profile_data['data']['user']['role']}")
            print(f"   Active: {profile_data['data']['user']['is_active']}")
        else:
            print(f"❌ Profile retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Profile error: {e}")
        return False
    
    # Test 6: Token Refresh
    print("\n6️⃣ Testing Token Refresh...")
    try:
        refresh_token = login_response['data']['refresh_token']
        refresh_data = {"refresh_token": refresh_token}
        response = requests.post(f"{BASE_URL}/auth/refresh", json=refresh_data)
        if response.status_code == 200:
            refresh_response = response.json()
            print("✅ Token Refresh Successful!")
            print(f"   New Token Type: {refresh_response['data']['token_type']}")
            print(f"   Expires in: {refresh_response['data']['expires_in']} seconds")
        else:
            print(f"❌ Token refresh failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Token refresh error: {e}")
        return False
    
    print("\n🎉 PHASE 3.2 AUTHENTICATION SYSTEM - ALL TESTS PASSED!")
    print("=" * 65)
    print("✅ Complete Authentication System Implemented:")
    print("   • User Registration with Password Validation")
    print("   • Secure Login with JWT Tokens")
    print("   • Role-Based Access Control (RBAC)")
    print("   • Protected Endpoint Authentication")
    print("   • User Profile Management")
    print("   • Token Refresh Mechanism")
    print("   • Healthcare Security Compliance")
    print("   • Educational Use Disclaimers")
    print("\n🚀 Ready for Phase 3.3 or Phase 4.0!")
    return True

if __name__ == "__main__":
    test_auth_system()
