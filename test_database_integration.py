#!/usr/bin/env python3
"""
Database Integration Test for Phase 3.3
Tests database connectivity and basic operations
"""

import asyncio
import logging
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_database_integration():
    """Test database integration step by step."""
    
    print("🧪 Testing Database Integration for Phase 3.3\n")
    
    # Test 1: Database import
    try:
        from src.models.database import init_database, UserDatabase, SessionDatabase
        print("✅ Database modules imported successfully")
    except Exception as e:
        print(f"❌ Database import failed: {e}")
        return False
    
    # Test 2: Database initialization
    try:
        success = await init_database()
        if success:
            print("✅ Database initialized successfully")
        else:
            print("❌ Database initialization failed")
            return False
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        return False
    
    # Test 3: User creation
    try:
        test_user_data = {
            "email": "test@aiNurseFlorence.com",
            "full_name": "Test User",
            "password_hash": "hashed_password_123",
            "role": "user"
        }
        
        user = await UserDatabase.create_user(test_user_data)
        if user:
            print(f"✅ User created successfully: {user.email}")
            user_id = user.id
        else:
            print("❌ User creation failed")
            return False
    except Exception as e:
        print(f"❌ User creation error: {e}")
        return False
    
    # Test 4: User retrieval
    try:
        retrieved_user = await UserDatabase.get_user_by_email("test@aiNurseFlorence.com")
        if retrieved_user and retrieved_user.email == "test@aiNurseFlorence.com":
            print("✅ User retrieval by email successful")
        else:
            print("❌ User retrieval failed")
            return False
            
        retrieved_by_id = await UserDatabase.get_user_by_id(user_id)
        if retrieved_by_id and retrieved_by_id.id == user_id:
            print("✅ User retrieval by ID successful")
        else:
            print("❌ User retrieval by ID failed")
            return False
    except Exception as e:
        print(f"❌ User retrieval error: {e}")
        return False
    
    # Test 5: Database auth integration
    try:
        from src.utils.database_auth import db_auth
        print("✅ Database auth integration imported successfully")
        
        # Test registration
        reg_result = await db_auth.register_user({
            "email": "integration_test@aiNurseFlorence.com",
            "full_name": "Integration Test User",
            "password": "TestPassword123!",
            "role": "user"
        })
        
        if reg_result["success"]:
            print("✅ Database auth registration successful")
        else:
            print(f"❌ Database auth registration failed: {reg_result}")
            return False
            
    except Exception as e:
        print(f"❌ Database auth integration error: {e}")
        return False
    
    print("\n🎉 All database integration tests passed!")
    print("✅ Phase 3.3 Database Integration is working correctly")
    
    return True

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run the test
    try:
        success = asyncio.run(test_database_integration())
        if success:
            print("\n🚀 Ready to integrate with authentication system!")
            sys.exit(0)
        else:
            print("\n❌ Database integration tests failed")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        sys.exit(1)
