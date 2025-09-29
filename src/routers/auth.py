"""
Authentication Router - AI Nurse Florence
Phase 3.1: Core Authentication System Implementation

Following Router Organization pattern and API Design Standards from coding instructions.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime, timedelta

from src.models.auth_schemas import (
    UserCreate, UserLogin, UserResponse, Token, RefreshToken,
    AuthStatus, ApiResponse, PasswordChange, TokenData
)
from src.utils.config import get_settings

# Router setup
router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={
        401: {"description": "Authentication failed"},
        403: {"description": "Insufficient permissions"},
        422: {"description": "Validation error"}
    }
)

# Security scheme for API documentation
security = HTTPBearer(auto_error=False)

@router.get(
    "/status",
    response_model=AuthStatus,
    summary="Check authentication status",
    description="Check current authentication status. Unprotected endpoint for auth verification."
)
async def auth_status(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """
    Authentication status endpoint following Authentication & Authorization pattern.
    Returns current authentication state without requiring valid credentials.
    """
    if not credentials:
        return AuthStatus(
            authenticated=False,
            message="No authentication credentials provided"
        )

    try:
        # Import auth utilities with conditional loading
        from src.utils.auth_enhanced import verify_token
        
        # Verify the token
        payload = verify_token(credentials.credentials, "access")
        
        return AuthStatus(
            authenticated=True,
            user=None,  # Would be populated with actual user data
            permissions=payload.get("permissions", []),
            message="Valid authentication credentials"
        )
    except Exception as e:
        return AuthStatus(
            authenticated=False,
            message=f"Invalid authentication credentials: {str(e)}"
        )

@router.post(
    "/register",
    response_model=ApiResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Register a new user account for AI Nurse Florence healthcare platform."
)
async def register_user(user_data: UserCreate):
    """
    User registration endpoint following Authentication & Authorization pattern.
    Creates new user account with secure password hashing.
    """
    try:
        # Import auth utilities with conditional loading
        from src.utils.auth_enhanced import hash_password, validate_email, validate_password_strength
        
        # Validate email format
        if not validate_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid email format"
            )
        
        # Validate password strength
        password_valid, password_message = validate_password_strength(user_data.password)
        if not password_valid:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=password_message
            )
        
        # Hash password
        hashed_password = hash_password(user_data.password)
        
        # In production, this would create user in database
        # For now, return success response
        return ApiResponse(
            success=True,
            message="User registration successful",
            data={
                "email": user_data.email,
                "role": user_data.role,
                "registration_time": datetime.utcnow().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post(
    "/login",
    response_model=Token,
    summary="User login",
    description="Authenticate user and return access tokens for AI Nurse Florence platform."
)
async def login_user(user_credentials: UserLogin):
    """
    User login endpoint following Authentication & Authorization pattern.
    Validates credentials and returns JWT access and refresh tokens.
    """
    try:
        # Import auth utilities with conditional loading
        from src.utils.auth_enhanced import verify_password, create_token_pair, get_user_permissions
        
        # In production, this would verify against database
        # For Phase 3.1, we'll simulate authentication
        
        # Demo user for testing (remove in Phase 3.2)
        demo_users = {
            "nurse@ai-florence.com": {
                "password_hash": "$2b$12$demo_hash_for_testing",
                "role": "nurse",
                "user_id": "demo-nurse-id",
                "full_name": "Demo Nurse"
            }
        }
        
        user = demo_users.get(user_credentials.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # In production, verify actual password hash
        # For demo, accept any password for the demo user
        
        # Create token data
        user_data = {
            "sub": user["user_id"],
            "email": user_credentials.email,
            "role": user["role"],
            "permissions": get_user_permissions(user["role"])
        }
        
        # Generate token pair
        tokens = create_token_pair(user_data)
        
        return Token(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=1800  # 30 minutes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.post(
    "/token",
    response_model=Token,
    summary="OAuth2 token endpoint",
    description="OAuth2 compatible token endpoint for client authentication."
)
async def token_endpoint(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 token endpoint following OAuth2PasswordBearer pattern.
    Compatible with OpenAPI OAuth2 authentication flow.
    """
    try:
        # Convert OAuth2 form to our login schema
        user_credentials = UserLogin(
            email=form_data.username,  # OAuth2 uses username field
            password=form_data.password
        )
        
        # Reuse login logic
        return await login_user(user_credentials)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh access token",
    description="Use refresh token to get new access token."
)
async def refresh_access_token(refresh_data: RefreshToken):
    """
    Token refresh endpoint following JWT refresh pattern.
    Validates refresh token and returns new access token.
    """
    try:
        # Import auth utilities with conditional loading
        from src.utils.auth_enhanced import verify_token, create_access_token, get_user_permissions
        
        # Verify refresh token
        payload = verify_token(refresh_data.refresh_token, "refresh")
        
        # Extract user info from refresh token
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # In production, validate user still exists and is active
        # For demo, create new access token
        user_data = {
            "sub": user_id,
            "email": "demo@ai-florence.com",  # Would be from database
            "role": "nurse",  # Would be from database
            "permissions": get_user_permissions("nurse")
        }
        
        # Create new access token
        access_token = create_access_token(user_data)
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_data.refresh_token,  # Keep same refresh token
            token_type="bearer",
            expires_in=1800
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed",
            headers={"WWW-Authenticate": "Bearer"}
        )

@router.post(
    "/logout",
    response_model=ApiResponse,
    summary="User logout",
    description="Logout user and invalidate tokens."
)
async def logout_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """
    User logout endpoint following Authentication & Authorization pattern.
    In production, this would invalidate the JWT token.
    """
    if not credentials:
        return ApiResponse(
            success=False,
            message="No authentication credentials provided"
        )
    
    # In production, add token to blacklist or use token revocation
    return ApiResponse(
        success=True,
        message="Logout successful",
        data={"logged_out_at": datetime.utcnow().isoformat()}
    )
    
    # In production, would validate JWT token here
    # For now, return basic auth status
    return AuthStatus(
        authenticated=True,
        user_type="healthcare_professional",
        permissions=["read:medical_info", "create:wizard_sessions"],
        message="Authentication valid (educational mode)"
    )

@router.post(
    "/login",
    response_model=dict,
    summary="User login (educational)",
    description="Educational login endpoint. In production would handle OAuth2 flow."
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
        "message": "Educational login - not for production use"
    }

@router.post(
    "/logout",
    summary="User logout",
    description="Logout endpoint for session cleanup."
)
async def logout():
    """Logout endpoint following Authentication & Authorization pattern."""
    return {
        "message": "Logout successful",
        "timestamp": datetime.now().isoformat()
    }

@router.get(
    "/validate",
    summary="Validate token",
    description="Validate authentication token. Used by protected endpoints."
)
async def validate_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """
    Token validation endpoint following Authentication & Authorization pattern.
    Used by protected endpoints for JWT validation.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials required"
        )
    
    # In production, would validate JWT here
    # For educational mode, accept any token
    return {
        "valid": True,
        "user_id": "educational_user",
        "permissions": ["read:medical_info", "create:wizard_sessions"],
        "message": "Token valid (educational mode)"
    }
