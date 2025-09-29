"""
Enhanced Authentication Utilities for AI Nurse Florence
Implements Phase 3.1: Core Authentication System

Following Conditional Imports Pattern and Security patterns from coding instructions.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import uuid

from fastapi import HTTPException, status
from passlib.context import CryptContext
from jose import JWTError, jwt

logger = logging.getLogger(__name__)

# Password hashing context with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration - will be loaded from settings
JWT_SECRET_KEY = "your-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

def get_auth_settings():
    """Get authentication settings with environment variable support."""
    try:
        from src.utils.config import get_settings
        settings = get_settings()
        return {
            "jwt_secret": getattr(settings, 'JWT_SECRET_KEY', JWT_SECRET_KEY),
            "jwt_algorithm": getattr(settings, 'JWT_ALGORITHM', JWT_ALGORITHM),
            "access_token_expire": getattr(settings, 'ACCESS_TOKEN_EXPIRE_MINUTES', ACCESS_TOKEN_EXPIRE_MINUTES),
            "refresh_token_expire": getattr(settings, 'REFRESH_TOKEN_EXPIRE_DAYS', REFRESH_TOKEN_EXPIRE_DAYS)
        }
    except Exception as e:
        logger.warning(f"Failed to load auth settings: {e}, using defaults")
        return {
            "jwt_secret": JWT_SECRET_KEY,
            "jwt_algorithm": JWT_ALGORITHM,
            "access_token_expire": ACCESS_TOKEN_EXPIRE_MINUTES,
            "refresh_token_expire": REFRESH_TOKEN_EXPIRE_DAYS
        }

# Password Security Functions
def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

# JWT Token Functions
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    auth_settings = get_auth_settings()
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=auth_settings["access_token_expire"])
    
    to_encode.update({
        "exp": expire,
        "type": "access",
        "iat": datetime.utcnow()
    })
    
    encoded_jwt = jwt.encode(
        to_encode, 
        auth_settings["jwt_secret"], 
        algorithm=auth_settings["jwt_algorithm"]
    )
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT refresh token."""
    auth_settings = get_auth_settings()
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=auth_settings["refresh_token_expire"])
    
    to_encode.update({
        "exp": expire,
        "type": "refresh",
        "iat": datetime.utcnow(),
        "jti": str(uuid.uuid4())  # Unique token ID for revocation
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        auth_settings["jwt_secret"], 
        algorithm=auth_settings["jwt_algorithm"]
    )
    return encoded_jwt

def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """Verify and decode a JWT token."""
    auth_settings = get_auth_settings()
    
    try:
        payload = jwt.decode(
            token,
            auth_settings["jwt_secret"],
            algorithms=[auth_settings["jwt_algorithm"]]
        )
        
        # Verify token type
        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type. Expected {token_type}",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return payload
        
    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

def create_token_pair(user_data: Dict[str, Any]) -> Dict[str, str]:
    """Create both access and refresh tokens for a user."""
    access_token = create_access_token(data=user_data)
    refresh_token = create_refresh_token(data={"sub": user_data.get("sub")})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

# User validation functions
def validate_email(email: str) -> bool:
    """Basic email validation."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password strength for healthcare application security."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        return False, "Password must contain at least one special character"
    
    return True, "Password meets security requirements"

# Role-based access control
ROLE_PERMISSIONS = {
    "admin": ["read", "write", "delete", "manage_users", "view_analytics", "system_config"],
    "nurse": ["read", "write", "view_patients", "create_reports", "access_clinical_tools"],
    "readonly": ["read", "view_patients"]
}

def get_user_permissions(role: str) -> list[str]:
    """Get permissions for a user role."""
    return ROLE_PERMISSIONS.get(role, ["read"])

def check_permission(user_role: str, required_permission: str) -> bool:
    """Check if a user role has a specific permission."""
    user_permissions = get_user_permissions(user_role)
    return required_permission in user_permissions
