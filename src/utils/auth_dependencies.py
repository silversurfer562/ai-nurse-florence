"""
Authentication Dependencies for AI Nurse Florence
Phase 3.2: Complete Authentication System Dependencies

Following Conditional Imports Pattern and dependency injection from coding instructions.
"""

import logging
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
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
        payload = verify_token(credentials.credentials)
        
        # Extract user information
        user_id = payload.get("sub")
        email = payload.get("email")
        role = payload.get("role", "user")
        permissions = payload.get("permissions", [])
        session_id = payload.get("session_id")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return {
            "user_id": user_id,
            "email": email,
            "role": role,
            "permissions": permissions,
            "session_id": session_id,
            "is_authenticated": True,
            "educational_notice": "For educational purposes only - not medical advice. No PHI stored."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """
    Dependency for optional authentication.
    Returns user data if authenticated, None if not.
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None

def require_permission(permission: str):
    """
    Dependency factory for role-based access control.
    Following role-based access patterns for healthcare applications.
    """
    async def permission_dependency(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        try:
            from src.utils.auth_enhanced import validate_user_role
            
            if not validate_user_role(current_user, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required: {permission}"
                )
            
            return current_user
            
        except Exception as e:
            logger.error(f"Permission validation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission validation failed"
            )
    
    return permission_dependency

def require_role(role: str):
    """
    Dependency factory for role-based access control.
    Following role-based access patterns for healthcare applications.
    """
    async def role_dependency(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        user_role = current_user.get("role", "user")
        
        if user_role != role and user_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {role}"
            )
        
        return current_user
    
    return role_dependency

# Convenience dependencies for common roles
require_nurse = require_role("nurse")
require_admin = require_role("admin")

# Convenience dependencies for common permissions
require_clinical_access = require_permission("read:clinical_decisions")
require_literature_access = require_permission("read:literature")
require_sbar_access = require_permission("create:sbar_reports")

async def get_api_key_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    Alternative authentication for API key based access.
    Following API key auth patterns from coding instructions.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        from src.utils.config import get_settings
        settings = get_settings()
        
        if credentials.credentials == settings.API_BEARER:
            return {
                "user_id": "api_user",
                "email": "api@ai-nurse-florence.org",
                "role": "api",
                "permissions": ["read:*"],
                "session_id": "api_session",
                "is_authenticated": True,
                "educational_notice": "For educational purposes only - not medical advice. No PHI stored."
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
            
    except Exception as e:
        logger.error(f"API key authentication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key authentication failed"
        )