"""
Authentication Schemas for AI Nurse Florence
Pydantic models for Phase 3.1: Core Authentication System

Following API Design Standards and Pydantic patterns from coding instructions.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, validator
import uuid

class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: str = "nurse"
    is_active: bool = True

class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str
    full_name: str
    role: str = "nurse"
    is_active: bool = True
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password meets security requirements."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    @validator('role')
    def validate_role(cls, v):
        """Validate role is allowed."""
        allowed_roles = ["nurse", "admin", "readonly"]
        if v not in allowed_roles:
            raise ValueError(f'Role must be one of: {allowed_roles}')
        return v

class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str

class UserResponse(UserBase):
    """Schema for user data in responses."""
    id: uuid.UUID
    email: Optional[str] = None
    is_verified: bool = False
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    """Schema for updating user data."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    
    @validator('role')
    def validate_role(cls, v):
        """Validate role is allowed."""
        if v is not None:
            allowed_roles = ["nurse", "admin", "readonly"]
            if v not in allowed_roles:
                raise ValueError(f'Role must be one of: {allowed_roles}')
        return v

class Token(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes default

class TokenData(BaseModel):
    """Token payload data."""
    email: Optional[str] = None
    user_id: Optional[str] = None
    role: Optional[str] = None
    permissions: list[str] = []

class RefreshToken(BaseModel):
    """Refresh token request."""
    refresh_token: str

class PasswordChange(BaseModel):
    """Password change schema."""
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password meets security requirements."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class PasswordReset(BaseModel):
    """Password reset request schema."""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema."""
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password meets security requirements."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class AuthStatus(BaseModel):
    """Authentication status response."""
    authenticated: bool
    user: Optional[UserResponse] = None
    permissions: list[str] = []
    message: str

class ApiResponse(BaseModel):
    """Standard API response wrapper."""
    success: bool
    message: str
    data: Optional[dict] = None

# Healthcare-specific schemas
class ClinicalAccess(BaseModel):
    """Clinical access verification for healthcare endpoints."""
    user_id: uuid.UUID
    role: str
    permissions: list[str]
    verified_access: bool
    access_level: str  # "basic", "clinical", "administrative"

class AuditLog(BaseModel):
    """Audit log entry for healthcare compliance."""
    user_id: uuid.UUID
    action: str
    resource: str
    timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool
    details: Optional[dict] = None
