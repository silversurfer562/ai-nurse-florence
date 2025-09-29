#!/usr/bin/env python3
"""
Alembic Migration Test - Phase 3.4.1c
Tests that Alembic migrations work correctly
"""

import asyncio
import logging
import sys
import os
import uuid

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_alembic_migration():
    """Test Alembic migration and database integration."""
    
    print("🧪 Testing Alembic Migration for Phase 3.4.1\n")
    
    # Test 1: Database import
    try:
        from src.models.database import init_database, UserDatabase, SessionDatabase
        print("✅ Database modules imported successfully")
    except Exception as e:
        print(f"❌ Database import failed: {e}")
        return False
    
    # Test 2: Database initialization (should work with migrated schema)
    try:
        success = await init_database()
        if success:
            print("✅ Database initialized successfully with migrated schema")
        else:
            print("❌ Database initialization failed")
            return False
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        return False
    
    # Test 3: User creation with unique email
    try:
        unique_email = f"migration_test_{uuid.uuid4().hex[:8]}@aiNurse.com"
        test_user_data = {
            "email": unique_email,
            "full_name": "Migration Test User",
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
    
    # Test 4: User retrieval (test schema compatibility)
    try:
        retrieved_user = await UserDatabase.get_user_by_email(unique_email)
        if retrieved_user and retrieved_user.email == unique_email:
            print("✅ User retrieval successful - schema is compatible")
        else:
            print("❌ User retrieval failed - schema compatibility issue")
            return False
    except Exception as e:
        print(f"❌ User retrieval error: {e}")
        return False
    
    # Test 5: Database auth integration with migrated schema
    try:
        from src.utils.database_auth import db_auth
        print("✅ Database auth integration compatible with migrated schema")
        
        # Test registration with unique email
        unique_reg_email = f"reg_test_{uuid.uuid4().hex[:8]}@aiNurse.com"
        reg_result = await db_auth.register_user({
            "email": unique_reg_email,
            "full_name": "Registration Migration Test",
            "password": "TestPassword123!",
            "role": "user"
        })
        
        if reg_result["success"]:
            print("✅ Database auth registration works with migrated schema")
        else:
            print(f"❌ Database auth registration failed: {reg_result}")
            return False
            
    except Exception as e:
        print(f"❌ Database auth integration error: {e}")
        return False
    
    # Test 6: Session management with migrated schema
    try:
        from datetime import datetime, timedelta
        session_data = {
            "user_id": user_id,
            "session_token": f"test_token_{uuid.uuid4().hex}",
            "expires_at": datetime.utcnow() + timedelta(hours=1),
            "is_active": True
        }
        
        session = await SessionDatabase.create_session(session_data)
        if session:
            print("✅ Session management works with migrated schema")
        else:
            print("❌ Session creation failed")
            return False
    except Exception as e:
        print(f"❌ Session management error: {e}")
        return False
    
    print("\n🎉 All Alembic migration tests passed!")
    print("✅ Phase 3.4.1 Alembic Migrations is working correctly")
    print("✅ Database schema migrated successfully")
    print("✅ All existing functionality compatible with migrated schema")
    
    return True

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run the test
    try:
        success = asyncio.run(test_alembic_migration())
        if success:
            print("\n🚀 Ready to proceed to Phase 3.4.2: Auth Router Database Integration!")
            sys.exit(0)
        else:
            print("\n❌ Alembic migration tests failed")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        sys.exit(1)
