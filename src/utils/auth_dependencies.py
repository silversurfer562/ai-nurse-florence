"""
Authentication Dependencies for AI Nurse Florence
Phase 3.1: Core Authentication System Dependencies

Following Conditional Imports Pattern and dependency injection from coding instructions.
"""

import logging
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """
    Dependency to get current authenticated user.
    Following Authentication & Authorization pattern from coding instructions.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        # Import auth utilities with conditional loading
        from src.utils.auth_enhanced import verify_token
        
        # Verify the access token
        payload = verify_token(credentials.credentials, "access")
        
        # Extract user information
        user_id = payload.get("sub")
        email = payload.get("email")
        role = payload.get("role")
        permissions = payload.get("permissions", [])
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Return user data (in Phase 3.2, this will be from database)
        return {
            "id": user_id,
            "email": email,
            "role": role,
            "permissions": permissions,
            "authenticated": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Authentication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    """
    Dependency to get current active user.
    Ensures user is active and verified for healthcare operations.
    """
    # In Phase 3.2, this will check database for is_active status
    if not current_user.get("authenticated"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active"
        )
    
    return current_user

def require_role(required_role: str):
    """
    Dependency factory to require specific user role.
    
    Usage:
        @router.get("/admin-only")
        async def admin_endpoint(user = Depends(require_role("admin"))):
            return {"message": "Admin access granted"}
    """
    async def role_checker(current_user: dict = Depends(get_current_active_user)):
        user_role = current_user.get("role")
        
        if user_role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role}"
            )
        
        return current_user
    
    return role_checker

def require_permission(required_permission: str):
    """
    Dependency factory to require specific permission.
    
    Usage:
        @router.get("/clinical-data")
        async def clinical_endpoint(user = Depends(require_permission("view_patients"))):
            return {"message": "Clinical access granted"}
    """
    async def permission_checker(current_user: dict = Depends(get_current_active_user)):
        user_permissions = current_user.get("permissions", [])
        
        if required_permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required permission: {required_permission}"
            )
        
        return current_user
    
    return permission_checker

# Healthcare-specific role dependencies
require_admin = require_role("admin")
require_nurse = require_role("nurse")

# Healthcare-specific permission dependencies  
require_clinical_access = require_permission("view_patients")
require_write_access = require_permission("write")
require_manage_users = require_permission("manage_users")

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """
    Optional authentication dependency.
    Returns user if authenticated, None otherwise.
    Useful for endpoints that work with or without authentication.
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
    except Exception:
        return None
