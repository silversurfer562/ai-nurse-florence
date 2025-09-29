"""
Database models for user authentication and management.

This module defines the SQLAlchemy ORM models for user authentication,
following the Service Layer Architecture pattern from coding instructions.
"""
from sqlalchemy import Column, String, DateTime, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from database import Base

class User(Base):
    """
    User model for authentication and authorization.
    
    Supports both traditional email/password authentication and
    provider-based authentication (OpenAI, etc.) for AI Nurse Florence.
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Traditional authentication fields
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    
    # Provider-based authentication (existing)
    provider = Column(String, nullable=True, default="email")
    provider_user_id = Column(String, nullable=True, unique=True, index=True)
    
    # User profile and permissions
    full_name = Column(String, nullable=True)
    role = Column(String, nullable=False, default="nurse")  # nurse, admin, readonly
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
