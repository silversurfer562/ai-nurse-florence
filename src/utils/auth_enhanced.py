"""
Enhanced Authentication Utilities for AI Nurse Florence
Phase 3.2: Complete Authentication System Implementation

Following Conditional Imports Pattern and Security patterns from coding instructions.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import uuid

from fastapi import HTTPException, status
from passlib.context import CryptContext
from jose import JWTError, jwt

logger = logging.getLogger(__name__)

# Password hashing context with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration defaults - will be loaded from settings
JWT_SECRET_KEY = "your-super-secret-jwt-key-change-in-production-min-32-chars"
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

def validate_password(password: str) -> Dict[str, Any]:
    """
    Validate password strength for healthcare security compliance.
    Returns validation result with detailed feedback.
    """
    errors = []
    
    # Get validation rules from config
    try:
        from src.utils.config import get_settings
        settings = get_settings()
        min_length = getattr(settings, 'PASSWORD_MIN_LENGTH', 8)
        require_upper = getattr(settings, 'PASSWORD_REQUIRE_UPPERCASE', True)
        require_lower = getattr(settings, 'PASSWORD_REQUIRE_LOWERCASE', True)
        require_numbers = getattr(settings, 'PASSWORD_REQUIRE_NUMBERS', True)
        require_special = getattr(settings, 'PASSWORD_REQUIRE_SPECIAL', True)
    except Exception:
        # Fallback to secure defaults for healthcare
        min_length = 8
        require_upper = require_lower = require_numbers = require_special = True
    
    # Length check
    if len(password) < min_length:
        errors.append(f"Password must be at least {min_length} characters long")
    
    # Character type checks
    if require_upper and not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")
    
    if require_lower and not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")
    
    if require_numbers and not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one number")
    
    if require_special and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        errors.append("Password must contain at least one special character")
    
    # Common password checks for healthcare security
    common_passwords = ["password", "123456", "admin", "nurse", "healthcare", "hospital", "medical"]
    if password.lower() in common_passwords:
        errors.append("Password is too common, please choose a more secure password")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "strength": "strong" if len(errors) == 0 else "weak"
    }

# JWT Token Functions
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token with educational banner compliance."""
    auth_settings = get_auth_settings()
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=auth_settings["access_token_expire"])
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": str(uuid.uuid4()),  # JWT ID for token revocation
        "app": "ai-nurse-florence",
        "purpose": "healthcare-education"  # Educational use compliance
    })
    
    encoded_jwt = jwt.encode(
        to_encode, 
        auth_settings["jwt_secret"], 
        algorithm=auth_settings["jwt_algorithm"]
    )
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create JWT refresh token with longer expiration."""
    auth_settings = get_auth_settings()
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=auth_settings["refresh_token_expire"])
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": str(uuid.uuid4()),
        "type": "refresh",  # Mark as refresh token
        "app": "ai-nurse-florence"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        auth_settings["jwt_secret"],
        algorithm=auth_settings["jwt_algorithm"]
    )
    return encoded_jwt

def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode JWT token.
    Returns token payload or raises HTTPException.
    Following security patterns from coding instructions.
    """
    auth_settings = get_auth_settings()
    
    try:
        payload = jwt.decode(
            token,
            auth_settings["jwt_secret"],
            algorithms=[auth_settings["jwt_algorithm"]]
        )
        
        # Check token expiration
        exp = payload.get("exp")
        if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Validate app context for security
        if payload.get("app") != "ai-nurse-florence":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token context",
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

def extract_user_id_from_token(token: str) -> str:
    """Extract user ID from JWT token."""
    payload = verify_token(token)
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token does not contain user ID",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user_id

def refresh_access_token(refresh_token: str) -> Dict[str, Any]:
    """
    Generate new access token from valid refresh token.
    Following security patterns for token rotation.
    """
    try:
        payload = verify_token(refresh_token)
        
        # Verify this is a refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type for refresh"
            )
        
        user_id = payload.get("sub")
        session_id = payload.get("session_id")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token payload"
            )
        
        # Create new access token
        new_token_data = {
            "sub": user_id,
            "session_id": session_id
        }
        
        access_token = create_access_token(new_token_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": get_auth_settings()["access_token_expire"] * 60
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh token"
        )

# Session Management
def create_user_session(user_id: str, device_info: Optional[str] = None, role: str = "user") -> Dict[str, Any]:
    """
    Create a new user session with tokens.
    Following authentication patterns from coding instructions.
    """
    session_data = {
        "sub": user_id,
        "session_id": str(uuid.uuid4()),
        "device_info": device_info or "unknown",
        "login_time": datetime.utcnow().isoformat(),
        "role": role,
        "permissions": get_role_permissions(role)
    }
    
    access_token = create_access_token(session_data)
    refresh_token = create_refresh_token({
        "sub": user_id, 
        "session_id": session_data["session_id"],
        "role": role
    })
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": get_auth_settings()["access_token_expire"] * 60,  # seconds
        "session_id": session_data["session_id"],
        "user_id": user_id,
        "role": role,
        "educational_notice": "For educational purposes only - not medical advice. No PHI stored."
    }

def get_role_permissions(role: str) -> List[str]:
    """
    Get permissions for user role.
    Following role-based access patterns for healthcare applications.
    """
    role_permissions = {
        "user": [
            "read:basic_info",
            "read:educational_content"
        ],
        "nurse": [
            "read:basic_info",
            "read:educational_content", 
            "read:clinical_decisions",
            "read:literature",
            "create:sbar_reports",
            "read:clinical_trials"
        ],
        "admin": [
            "read:*",
            "write:*",
            "admin:*"
        ]
    }
    
    return role_permissions.get(role, role_permissions["user"])

def validate_user_role(token_payload: Dict[str, Any], required_permission: str) -> bool:
    """
    Validate if user has required permission.
    Following role-based access control patterns.
    """
    user_permissions = token_payload.get("permissions", [])
    user_role = token_payload.get("role", "user")
    
    # Admin has all permissions
    if user_role == "admin" or "admin:*" in user_permissions:
        return True
    
    # Check for wildcard permissions
    if "read:*" in user_permissions and required_permission.startswith("read:"):
        return True
    if "write:*" in user_permissions and required_permission.startswith("write:"):
        return True
    
    # Check exact permission match
    return required_permission in user_permissions

# Security utilities
def generate_secure_token(length: int = 32) -> str:
    """Generate cryptographically secure random token."""
    import secrets
    return secrets.token_urlsafe(length)

def mask_sensitive_data(data: str, show_chars: int = 4) -> str:
    """Mask sensitive data for logging."""
    if len(data) <= show_chars * 2:
        return "*" * len(data)
    return data[:show_chars] + "*" * (len(data) - show_chars * 2) + data[-show_chars:]