"""
Admin Router - AI Nurse Florence
Phase 3.4.3: Admin Endpoints

Administrator interface for user management with role-based access control.
Following Router Organization pattern and API Design Standards from coding instructions.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

# Import utilities following conditional imports pattern
try:
    from src.utils.auth_dependencies import get_current_user
    from src.utils.api_responses import create_success_response, create_error_response
    from src.utils.exceptions import ServiceException
    from src.models.database import UserDatabase
    _has_auth = True
    _has_database = True
except ImportError as e:
    _has_auth = False
    _has_database = False
    
    # Mock functions for testing
    async def get_current_user() -> Dict[str, Any]:
        return {"user_id": "mock_admin", "role": "admin"}
    
    def create_success_response(data: Any) -> Dict[str, Any]:
        return {"success": True, "data": data}
    
    def create_error_response(message: str, status_code: int = 500, details: Optional[Dict] = None) -> Dict[str, Any]:
        return {"success": False, "message": message, "details": details}
    
    class MockUserDatabase:
        @staticmethod
        async def list_users(skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[Any]:
            return []
        
        @staticmethod
        async def count_users(search: Optional[str] = None) -> int:
            return 0
        
        @staticmethod
        async def get_user_by_id(user_id: str) -> Optional[Any]:
            return None
        
        @staticmethod
        async def activate_user(user_id: str) -> bool:
            return True
        
        @staticmethod
        async def deactivate_user(user_id: str) -> bool:
            return True
        
        @staticmethod
        async def change_user_role(user_id: str, role: str) -> bool:
            return True
        
        @staticmethod
        async def verify_user(user_id: str) -> bool:
            return True
        
        @staticmethod
        async def delete_user(user_id: str) -> bool:
            return True
    
    UserDatabase = MockUserDatabase

# Router setup following router organization patterns
router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={
        401: {"description": "Authentication failed"},
        403: {"description": "Insufficient permissions - admin role required"},
        404: {"description": "User not found"},
        422: {"description": "Validation error"}
    }
)

# Pydantic models for request/response validation
class UserListResponse(BaseModel):
    users: List[Dict[str, Any]]
    total: int
    page: int
    limit: int
    has_next: bool
    has_prev: bool

class UserActionRequest(BaseModel):
    user_id: str = Field(..., description="User ID to perform action on")
    reason: Optional[str] = Field(None, description="Reason for the action (for audit purposes)")

class RoleChangeRequest(BaseModel):
    user_id: str = Field(..., description="User ID to change role for")
    new_role: str = Field(..., description="New role to assign")
    reason: Optional[str] = Field(None, description="Reason for role change")

class UserSearchRequest(BaseModel):
    search: Optional[str] = Field(None, description="Search term for email or name")
    page: int = Field(1, description="Page number (1-based)")
    limit: int = Field(20, description="Items per page")

# Helper function to check admin permissions
def require_admin_role(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Dependency to require admin role."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator permissions required"
        )
    return current_user

# Phase 3.4.3: Admin endpoints for user management

@router.get(
    "/users",
    summary="List all users",
    description="Get paginated list of all users with optional search"
)
async def list_users(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search in email or name"),
    current_user: Dict[str, Any] = Depends(require_admin_role)
):
    """
    List all users with pagination and search.
    Requires admin role.
    Phase 3.4.3: Complete admin user management.
    """
    try:
        # Calculate offset
        skip = (page - 1) * limit
        
        # Get users and total count
        users = await UserDatabase.list_users(skip=skip, limit=limit, search=search)
        total = await UserDatabase.count_users(search=search)
        
        # Convert users to safe data (no password hashes)
        safe_users = []
        for user in users:
            if hasattr(user, '__dict__'):
                # Real database user object
                safe_user = {
                    "user_id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                    "is_active": user.is_active,
                    "is_verified": user.is_verified,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
                    "license_number": user.license_number,
                    "institution": user.institution,
                    "department": user.department
                }
            else:
                # Mock user data
                safe_user = {
                    "user_id": "mock_user",
                    "email": "mock@example.com",
                    "full_name": "Mock User",
                    "role": "user",
                    "is_active": True,
                    "is_verified": False
                }
            safe_users.append(safe_user)
        
        # Calculate pagination info
        has_next = skip + limit < total
        has_prev = page > 1
        
        response_data = {
            "users": safe_users,
            "total": total,
            "page": page,
            "limit": limit,
            "has_next": has_next,
            "has_prev": has_prev,
            "search": search
        }
        
        return create_success_response({
            **response_data,
            "educational_notice": "For educational purposes only - not medical advice. No PHI stored."
        })
        
    except Exception as e:
        return create_error_response(
            message="Failed to list users",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )

@router.get(
    "/users/{user_id}",
    summary="Get user details",
    description="Get detailed information about a specific user"
)
async def get_user_details(
    user_id: str,
    current_user: Dict[str, Any] = Depends(require_admin_role)
):
    """
    Get detailed information about a specific user.
    Requires admin role.
    """
    try:
        user = await UserDatabase.get_user_by_id(user_id)
        
        if not user:
            return create_error_response(
                message="User not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Return safe user data (no password hash)
        if hasattr(user, '__dict__'):
            # Real database user object
            user_data = {
                "user_id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
                "license_number": user.license_number,
                "institution": user.institution,
                "department": user.department,
                "updated_at": user.updated_at.isoformat() if hasattr(user, 'updated_at') and user.updated_at else None
            }
        else:
            # Mock user data
            user_data = {
                "user_id": user_id,
                "email": "mock@example.com",
                "full_name": "Mock User",
                "role": "user",
                "is_active": True,
                "is_verified": False
            }
        
        return create_success_response({
            "user": user_data,
            "educational_notice": "For educational purposes only - not medical advice. No PHI stored."
        })
        
    except Exception as e:
        return create_error_response(
            message="Failed to get user details",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )

@router.post(
    "/users/{user_id}/activate",
    summary="Activate user",
    description="Activate a deactivated user account"
)
async def activate_user(
    user_id: str,
    action_data: UserActionRequest,
    current_user: Dict[str, Any] = Depends(require_admin_role)
):
    """
    Activate a user account.
    Requires admin role.
    """
    try:
        # Verify user exists
        user = await UserDatabase.get_user_by_id(user_id)
        if not user:
            return create_error_response(
                message="User not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Activate user
        success = await UserDatabase.activate_user(user_id)
        
        if success:
            # Log admin action (in a real system, this would go to audit log)
            action_log = {
                "action": "user_activated",
                "target_user_id": user_id,
                "admin_user_id": current_user["user_id"],
                "reason": action_data.reason,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return create_success_response({
                "message": "User activated successfully",
                "user_id": user_id,
                "action_log": action_log,
                "educational_notice": "For educational purposes only - not medical advice. No PHI stored."
            })
        else:
            return create_error_response(
                message="Failed to activate user",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    except Exception as e:
        return create_error_response(
            message="User activation failed",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )

@router.post(
    "/users/{user_id}/deactivate",
    summary="Deactivate user",
    description="Deactivate a user account"
)
async def deactivate_user(
    user_id: str,
    action_data: UserActionRequest,
    current_user: Dict[str, Any] = Depends(require_admin_role)
):
    """
    Deactivate a user account.
    Requires admin role.
    """
    try:
        # Prevent admin from deactivating themselves
        if user_id == current_user["user_id"]:
            return create_error_response(
                message="Cannot deactivate your own account",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify user exists
        user = await UserDatabase.get_user_by_id(user_id)
        if not user:
            return create_error_response(
                message="User not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Deactivate user
        success = await UserDatabase.deactivate_user(user_id)
        
        if success:
            # Log admin action
            action_log = {
                "action": "user_deactivated",
                "target_user_id": user_id,
                "admin_user_id": current_user["user_id"],
                "reason": action_data.reason,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return create_success_response({
                "message": "User deactivated successfully",
                "user_id": user_id,
                "action_log": action_log,
                "educational_notice": "For educational purposes only - not medical advice. No PHI stored."
            })
        else:
            return create_error_response(
                message="Failed to deactivate user",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    except Exception as e:
        return create_error_response(
            message="User deactivation failed",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )

@router.post(
    "/users/{user_id}/change-role",
    summary="Change user role",
    description="Change a user's role (user, nurse, admin)"
)
async def change_user_role(
    user_id: str,
    role_data: RoleChangeRequest,
    current_user: Dict[str, Any] = Depends(require_admin_role)
):
    """
    Change a user's role.
    Requires admin role.
    """
    try:
        # Validate role
        valid_roles = ["user", "nurse", "admin"]
        if role_data.new_role not in valid_roles:
            return create_error_response(
                message=f"Invalid role. Must be one of: {valid_roles}",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        
        # Prevent admin from demoting themselves
        if user_id == current_user["user_id"] and role_data.new_role != "admin":
            return create_error_response(
                message="Cannot change your own admin role",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify user exists
        user = await UserDatabase.get_user_by_id(user_id)
        if not user:
            return create_error_response(
                message="User not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Change role
        success = await UserDatabase.change_user_role(user_id, role_data.new_role)
        
        if success:
            # Log admin action
            action_log = {
                "action": "role_changed",
                "target_user_id": user_id,
                "admin_user_id": current_user["user_id"],
                "new_role": role_data.new_role,
                "reason": role_data.reason,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return create_success_response({
                "message": f"User role changed to {role_data.new_role} successfully",
                "user_id": user_id,
                "new_role": role_data.new_role,
                "action_log": action_log,
                "educational_notice": "For educational purposes only - not medical advice. No PHI stored."
            })
        else:
            return create_error_response(
                message="Failed to change user role",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    except Exception as e:
        return create_error_response(
            message="Role change failed",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )

@router.post(
    "/users/{user_id}/verify",
    summary="Verify user",
    description="Mark a user as verified"
)
async def verify_user(
    user_id: str,
    action_data: UserActionRequest,
    current_user: Dict[str, Any] = Depends(require_admin_role)
):
    """
    Verify a user account.
    Requires admin role.
    """
    try:
        # Verify user exists
        user = await UserDatabase.get_user_by_id(user_id)
        if not user:
            return create_error_response(
                message="User not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Verify user
        success = await UserDatabase.verify_user(user_id)
        
        if success:
            # Log admin action
            action_log = {
                "action": "user_verified",
                "target_user_id": user_id,
                "admin_user_id": current_user["user_id"],
                "reason": action_data.reason,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return create_success_response({
                "message": "User verified successfully",
                "user_id": user_id,
                "action_log": action_log,
                "educational_notice": "For educational purposes only - not medical advice. No PHI stored."
            })
        else:
            return create_error_response(
                message="Failed to verify user",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    except Exception as e:
        return create_error_response(
            message="User verification failed",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )

@router.delete(
    "/users/{user_id}",
    summary="Delete user",
    description="Delete a user account (soft delete)"
)
async def delete_user(
    user_id: str,
    action_data: UserActionRequest,
    current_user: Dict[str, Any] = Depends(require_admin_role)
):
    """
    Delete a user account (soft delete).
    Requires admin role.
    """
    try:
        # Prevent admin from deleting themselves
        if user_id == current_user["user_id"]:
            return create_error_response(
                message="Cannot delete your own account",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify user exists
        user = await UserDatabase.get_user_by_id(user_id)
        if not user:
            return create_error_response(
                message="User not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Delete user (soft delete)
        success = await UserDatabase.delete_user(user_id)
        
        if success:
            # Log admin action
            action_log = {
                "action": "user_deleted",
                "target_user_id": user_id,
                "admin_user_id": current_user["user_id"],
                "reason": action_data.reason,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return create_success_response({
                "message": "User deleted successfully",
                "user_id": user_id,
                "action_log": action_log,
                "educational_notice": "For educational purposes only - not medical advice. No PHI stored."
            })
        else:
            return create_error_response(
                message="Failed to delete user",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    except Exception as e:
        return create_error_response(
            message="User deletion failed",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )

# Admin statistics and monitoring endpoints

@router.get(
    "/stats",
    summary="Get admin statistics",
    description="Get system-wide statistics for administrators"
)
async def get_admin_stats(
    current_user: Dict[str, Any] = Depends(require_admin_role)
):
    """
    Get system statistics.
    Requires admin role.
    """
    try:
        # Get user counts
        total_users = await UserDatabase.count_users()
        active_users = await UserDatabase.count_users()  # This would need a filter in real implementation
        
        # Calculate statistics
        stats = {
            "users": {
                "total": total_users,
                "active": active_users,
                "inactive": max(0, total_users - active_users)
            },
            "system": {
                "database_integration": _has_database,
                "auth_system": _has_auth,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        return create_success_response({
            "stats": stats,
            "generated_by": current_user["user_id"],
            "educational_notice": "For educational purposes only - not medical advice. No PHI stored."
        })
        
    except Exception as e:
        return create_error_response(
            message="Failed to get statistics",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )

# Test endpoint for admin functionality

@router.get(
    "/test",
    summary="Test admin functionality",
    description="Test endpoint to verify admin system is working"
)
async def test_admin_system(
    current_user: Dict[str, Any] = Depends(require_admin_role)
):
    """Test admin system functionality."""
    return create_success_response({
        "message": "Admin system operational",
        "admin_user": current_user["user_id"],
        "timestamp": datetime.utcnow().isoformat(),
        "database_integration": _has_database,
        "auth_system": _has_auth,
        "educational_notice": "For educational purposes only - not medical advice. No PHI stored."
    })

@router.post("/seed-medications")
async def seed_medications_endpoint():
    """
    Seed the medications database with 700+ medication names for autocomplete.
    Database is used ONLY for medication name search - NOT for drug details.
    All drug interaction analysis comes from OpenAI.
    ONE-TIME USE endpoint for production database initialization.
    """
    try:
        from src.models.database import get_db_session, Medication
        from sqlalchemy import select, delete
        from uuid import uuid4
        import logging

        logger = logging.getLogger(__name__)

        # Import autocomplete medication list (700+ names)
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from scripts.seed_medications_autocomplete import COMMON_MEDICATIONS

        async for session in get_db_session():
            try:
                # Clear existing medications with TRUNCATE (more aggressive than DELETE)
                from sqlalchemy import text
                await session.execute(text("TRUNCATE TABLE medications RESTART IDENTITY CASCADE"))
                await session.commit()
                logger.info("Truncated medications table")

                # Insert medication names for autocomplete
                medications_created = 0
                for med_name in COMMON_MEDICATIONS:
                    medication = Medication(
                        id=str(uuid4()),
                        name=med_name,
                        source="curated_autocomplete",
                        is_active=True
                    )
                    session.add(medication)
                    medications_created += 1

                    if medications_created % 100 == 0:
                        logger.info(f"Added {medications_created} medications...")

                await session.commit()
                logger.info(f"Successfully seeded {medications_created} medications for autocomplete")

                return create_success_response({
                    "message": f"Successfully seeded {medications_created} medication names for autocomplete",
                    "count": medications_created,
                    "purpose": "Medication name autocomplete only - drug details come from OpenAI",
                    "timestamp": datetime.utcnow().isoformat()
                })

            except Exception as db_error:
                await session.rollback()
                logger.error(f"Database error during seeding: {db_error}")
                raise db_error

    except Exception as e:
        logger.error(f"Medication seeding failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to seed medications: {str(e)}"
        )

@router.get("/medication-count")
async def get_medication_count():
    """Debug endpoint to check medication list count."""
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from scripts.seed_medications_autocomplete import COMMON_MEDICATIONS

        return create_success_response({
            "medication_count": len(COMMON_MEDICATIONS),
            "first_10": COMMON_MEDICATIONS[:10],
            "has_duplicates": len(COMMON_MEDICATIONS) != len(set([m.lower() for m in COMMON_MEDICATIONS])),
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get medication count: {str(e)}"
        )
