"""
Database models for the application.

This module defines the SQLAlchemy ORM models, which represent the tables
in our database (e.g., the 'users' table).
"""
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from database import Base

class User(Base):
    """
    Represents a user in the database.
    
    This model stores a unique internal ID for each user and links it to their
    anonymous, provider-specific user ID (e.g., from OpenAI).
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider = Column(String, nullable=False, default="openai")
    provider_user_id = Column(String, nullable=False, unique=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, provider_user_id='{self.provider_user_id}')>"
