"""
Authentication Router - AI Nurse Florence
Following Router Organization pattern for unprotected auth endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from src.utils.config import get_settings

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={
        401: {"description": "Authentication failed"},
        403: {"description": "Insufficient permissions"},
    },
)

# Security scheme for API documentation
security = HTTPBearer(auto_error=False)


class AuthStatus(BaseModel):
    """Authentication status response following API Design Standards."""

    authenticated: bool
    user_type: Optional[str] = None
    permissions: list[str] = []
    message: str


@router.get(
    "/status",
    response_model=AuthStatus,
    summary="Check authentication status",
    description="Check current authentication status. Unprotected endpoint for auth verification.",
)
async def auth_status(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
):
    """
    Authentication status endpoint following Authentication & Authorization pattern.
    Returns current authentication state without requiring valid credentials.
    """
    if not credentials:
        return AuthStatus(
            authenticated=False, message="No authentication credentials provided"
        )

    # In production, would validate JWT token here
    # For now, return basic auth status
    return AuthStatus(
        authenticated=True,
        user_type="healthcare_professional",
        permissions=["read:medical_info", "create:wizard_sessions"],
        message="Authentication valid (educational mode)",
    )


@router.post(
    "/login",
    response_model=dict,
    summary="User login (educational)",
    description="Educational login endpoint. In production would handle OAuth2 flow.",
)
async def login(credentials: dict):
    """
    Educational login endpoint following Authentication & Authorization pattern.
    In production, would implement OAuth2 + JWT flow from coding instructions.
    """
    settings = get_settings()

    return {
        "access_token": "educational_token_not_for_production",
        "token_type": "bearer",
        "expires_in": 3600,
        "user_type": "healthcare_professional",
        "banner": settings.EDUCATIONAL_BANNER,
        "message": "Educational login - not for production use",
    }


@router.post(
    "/logout", summary="User logout", description="Logout endpoint for session cleanup."
)
async def logout():
    """Logout endpoint following Authentication & Authorization pattern."""
    return {"message": "Logout successful", "timestamp": datetime.now().isoformat()}


@router.get(
    "/validate",
    summary="Validate token",
    description="Validate authentication token. Used by protected endpoints.",
)
async def validate_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
):
    """
    Token validation endpoint following Authentication & Authorization pattern.
    Used by protected endpoints for JWT validation.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials required",
        )

    # In production, would validate JWT here
    # For educational mode, accept any token
    return {
        "valid": True,
        "user_id": "educational_user",
        "permissions": ["read:medical_info", "create:wizard_sessions"],
        "message": "Token valid (educational mode)",
    }
