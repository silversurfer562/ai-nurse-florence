"""
Database-backed authentication integration for Phase 3.3
Replaces in-memory user storage with persistent database storage

This module integrates the database models with the auth system.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import asyncio

from src.models.database import (
    init_database, 
    UserDatabase, 
    SessionDatabase, 
    User, 
    UserSession
)
from src.utils.auth_enhanced import hash_password, verify_password

logger = logging.getLogger(__name__)

class DatabaseAuthIntegration:
    """Integration layer between auth system and database."""
    
    def __init__(self):
        self._db_initialized = False
    
    async def ensure_db_initialized(self):
        """Ensure database is initialized."""
        if not self._db_initialized:
            success = await init_database()
            if success:
                self._db_initialized = True
                logger.info("✅ Database auth integration initialized")
            else:
                logger.error("❌ Failed to initialize database for auth")
                raise RuntimeError("Database initialization failed")
    
    async def register_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new user with database persistence."""
        await self.ensure_db_initialized()
        
        try:
            # Hash password
            if "password" in user_data:
                user_data["password_hash"] = hash_password(user_data.pop("password"))
            
            # Set default values
            user_data.setdefault("role", "user")
            user_data.setdefault("is_active", True)
            user_data.setdefault("is_verified", False)
            user_data.setdefault("agreed_to_terms", True)
            
            # Create user in database
            user = await UserDatabase.create_user(user_data)
            
            if user:
                return {
                    "success": True,
                    "user": user.to_dict(),
                    "message": "User registered successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create user",
                    "message": "Database operation failed"
                }
                
        except ValueError as e:
            logger.warning(f"User registration validation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Registration failed"
            }
        except Exception as e:
            logger.error(f"User registration error: {e}")
            return {
                "success": False,
                "error": "Internal server error",
                "message": "Registration failed"
            }
    
    async def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user with database verification."""
        await self.ensure_db_initialized()
        
        try:
            # Get user from database
            user = await UserDatabase.get_user_by_email(email)
            
            if not user:
                return {
                    "success": False,
                    "error": "User not found",
                    "message": "Invalid credentials"
                }
            
            if not user.is_active:
                return {
                    "success": False,
                    "error": "Account disabled",
                    "message": "Account is not active"
                }
            
            # Verify password
            if not verify_password(password, user.password_hash):
                return {
                    "success": False,
                    "error": "Invalid password",
                    "message": "Invalid credentials"
                }
            
            # Update last login time
            await UserDatabase.update_login_time(user.id)
            
            return {
                "success": True,
                "user": user.to_dict(),
                "message": "Authentication successful"
            }
            
        except Exception as e:
            logger.error(f"Authentication error for {email}: {e}")
            return {
                "success": False,
                "error": "Internal server error",
                "message": "Authentication failed"
            }
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID from database."""
        await self.ensure_db_initialized()
        
        try:
            user = await UserDatabase.get_user_by_id(user_id)
            return user.to_dict() if user else None
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    async def update_user_profile(self, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile in database."""
        await self.ensure_db_initialized()
        
        try:
            # Handle password updates
            if "password" in update_data:
                update_data["password_hash"] = hash_password(update_data.pop("password"))
                update_data["password_changed_at"] = datetime.utcnow()
            
            # Remove sensitive fields from direct updates
            sensitive_fields = ["id", "email", "created_at"]
            for field in sensitive_fields:
                update_data.pop(field, None)
            
            user = await UserDatabase.update_user(user_id, update_data)
            
            if user:
                return {
                    "success": True,
                    "user": user.to_dict(),
                    "message": "Profile updated successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "User not found",
                    "message": "Update failed"
                }
                
        except Exception as e:
            logger.error(f"Profile update error for user {user_id}: {e}")
            return {
                "success": False,
                "error": "Internal server error",
                "message": "Update failed"
            }
    
    async def create_user_session(self, user_id: str, session_token: str, 
                                expires_in_hours: int = 24, device_info: str = None, 
                                ip_address: str = None) -> Dict[str, Any]:
        """Create a user session in database."""
        await self.ensure_db_initialized()
        
        try:
            session_data = {
                "user_id": user_id,
                "session_token": session_token,
                "expires_at": datetime.utcnow() + timedelta(hours=expires_in_hours),
                "device_info": device_info,
                "ip_address": ip_address,
                "is_active": True
            }
            
            session = await SessionDatabase.create_session(session_data)
            
            if session:
                return {
                    "success": True,
                    "session_id": session.id,
                    "message": "Session created successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create session",
                    "message": "Session creation failed"
                }
                
        except Exception as e:
            logger.error(f"Session creation error for user {user_id}: {e}")
            return {
                "success": False,
                "error": "Internal server error",
                "message": "Session creation failed"
            }
    
    async def get_active_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Get active session from database."""
        await self.ensure_db_initialized()
        
        try:
            session = await SessionDatabase.get_active_session(session_token)
            if session:
                return {
                    "session_id": session.id,
                    "user_id": session.user_id,
                    "expires_at": session.expires_at,
                    "is_active": session.is_active
                }
            return None
        except Exception as e:
            logger.error(f"Error getting session {session_token}: {e}")
            return None
    
    async def invalidate_session(self, session_token: str) -> bool:
        """Invalidate a session in database."""
        await self.ensure_db_initialized()
        
        try:
            return await SessionDatabase.invalidate_session(session_token)
        except Exception as e:
            logger.error(f"Error invalidating session {session_token}: {e}")
            return False

# Global instance for use throughout the application
db_auth = DatabaseAuthIntegration()

# Convenience functions for backward compatibility
async def register_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Register a new user."""
    return await db_auth.register_user(user_data)

async def authenticate_user(email: str, password: str) -> Dict[str, Any]:
    """Authenticate a user."""
    return await db_auth.authenticate_user(email, password)

async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user by ID."""
    return await db_auth.get_user_by_id(user_id)

async def update_user_profile(user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
    """Update user profile."""
    return await db_auth.update_user_profile(user_id, update_data)

# Test function to verify database integration
async def test_database_auth():
    """Test database authentication integration."""
    try:
        logger.info("🧪 Testing database auth integration...")
        
        # Test user registration
        test_user = {
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "testpassword123",
            "role": "user"
        }
        
        result = await register_user(test_user)
        if result["success"]:
            logger.info("✅ User registration test passed")
            
            # Test authentication
            auth_result = await authenticate_user("test@example.com", "testpassword123")
            if auth_result["success"]:
                logger.info("✅ User authentication test passed")
                logger.info("✅ Database auth integration working correctly")
                return True
            else:
                logger.error(f"❌ Authentication test failed: {auth_result}")
        else:
            logger.error(f"❌ Registration test failed: {result}")
        
        return False
        
    except Exception as e:
        logger.error(f"❌ Database auth test failed: {e}")
        return False

if __name__ == "__main__":
    # Run test if executed directly
    asyncio.run(test_database_auth())
