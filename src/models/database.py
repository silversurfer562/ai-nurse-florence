"""
SQLAlchemy database models and connection management
Phase 3.3: Complete Database Integration - Simplified Working Version

Following Database Patterns from AI Nurse Florence coding instructions
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, AsyncGenerator
import uuid
import os

from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, ForeignKey, JSON
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)

# Base class for all models
Base = declarative_base()

# Global database connection
engine = None
SessionLocal = None

# Database Models
class User(Base):
    """User model for authentication and profile management."""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="user")
    
    # Profile information
    license_number = Column(String(100), nullable=True)
    institution = Column(String(255), nullable=True)
    department = Column(String(255), nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    password_changed_at = Column(DateTime, nullable=True)
    
    # Educational compliance
    agreed_to_terms = Column(Boolean, default=False, nullable=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary (excluding sensitive data)."""
        return {
            "user_id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "license_number": self.license_number,
            "institution": self.institution,
            "department": self.department,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at is not None else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at is not None else None,
            "agreed_to_terms": self.agreed_to_terms
        }

class UserSession(Base):
    """User session tracking for security and analytics."""
    __tablename__ = "user_sessions"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    refresh_token = Column(String(255), unique=True, nullable=True, index=True)
    
    # Session metadata
    device_info = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    # Session lifecycle
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, active={self.is_active})>"

class WizardState(Base):
    """Multi-step wizard state management."""
    __tablename__ = "wizard_states"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    wizard_type = Column(String(100), nullable=False, index=True)

    # Wizard progress
    current_step = Column(Integer, default=1, nullable=False)
    total_steps = Column(Integer, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)

    # State data (JSON)
    step_data = Column(JSON, nullable=True)
    final_result = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<WizardState(id={self.id}, type={self.wizard_type}, step={self.current_step}/{self.total_steps})>"

class CachedDrugList(Base):
    """Cached list of drug names from FDA API (Phase 4.2 - Drug Interactions)."""
    __tablename__ = "cached_drug_lists"

    id = Column(String, primary_key=True)
    drug_names = Column(JSON, nullable=False)  # List of drug names
    source = Column(String(100), nullable=False)  # "fda_api" or "manual"
    count = Column(Integer, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<CachedDrugList(id={self.id}, count={self.count}, source={self.source})>"

class CachedDiseaseList(Base):
    """Cached list of disease names from MONDO ontology (Phase 4.2 - Disease Info)."""
    __tablename__ = "cached_disease_lists"

    id = Column(String, primary_key=True)
    disease_names = Column(JSON, nullable=False)  # List of disease names
    source = Column(String(100), nullable=False)  # "mondo_api" or "manual"
    count = Column(Integer, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<CachedDiseaseList(id={self.id}, count={self.count}, source={self.source})>"

class CachedDiseaseInfo(Base):
    """Cached disease lookup results from MyDisease.info API (Phase 4.2 - Disease Info)."""
    __tablename__ = "cached_disease_info"

    id = Column(String, primary_key=True)
    disease_query = Column(String(255), nullable=False, index=True)  # Search query
    disease_data = Column(JSON, nullable=False)  # Full disease information
    source = Column(String(100), nullable=False)  # "mydisease_api"

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<CachedDiseaseInfo(query={self.disease_query}, source={self.source})>"

class DiseaseOntology(Base):
    """
    Comprehensive disease ontology database from MONDO.
    Stores individual diseases with all metadata including synonyms.
    Progressive collection strategy - accumulates diseases over time.
    """
    __tablename__ = "disease_ontology"

    # Primary identifiers
    id = Column(String, primary_key=True)  # UUID
    mondo_id = Column(String(100), unique=True, nullable=False, index=True)  # e.g., "MONDO:0005148"

    # Core disease information
    label = Column(String(500), nullable=False, index=True)  # Official disease name
    synonyms = Column(JSON, nullable=True)  # List of synonym strings
    definition = Column(Text, nullable=True)  # Disease definition text

    # Cross-references to other ontologies
    xrefs = Column(JSON, nullable=True)  # Dict of xrefs (sctid, icd10cm, etc.)
    snomed_code = Column(String(100), nullable=True, index=True)  # SNOMED CT Identifier (sctid)
    icd10_code = Column(String(100), nullable=True, index=True)  # ICD-10 code
    icd11_code = Column(String(100), nullable=True, index=True)  # ICD-11 code

    # Metadata
    source = Column(String(100), nullable=False, default="mondo_api")  # Data source
    is_obsolete = Column(Boolean, default=False, nullable=False)  # Obsolete flag

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_verified_at = Column(DateTime, nullable=True)  # Last API verification

    def __repr__(self):
        return f"<DiseaseOntology(mondo_id={self.mondo_id}, label={self.label})>"

class DiseaseCollectionProgress(Base):
    """
    Tracks progress of progressive disease collection from MONDO API.
    Single row table that maintains pagination state.
    """
    __tablename__ = "disease_collection_progress"

    id = Column(String, primary_key=True)  # Single row ID

    # Pagination state
    total_fetched = Column(Integer, default=0, nullable=False)  # Total diseases collected
    current_offset = Column(Integer, default=0, nullable=False)  # Next offset to fetch
    batch_size = Column(Integer, default=1000, nullable=False)  # Records per batch

    # Completion tracking
    is_complete = Column(Boolean, default=False, nullable=False)  # All diseases collected
    total_available = Column(Integer, nullable=True)  # Total diseases in MONDO (from API response)

    # Status tracking
    last_fetch_status = Column(String(50), nullable=False, default="pending")  # pending, success, error
    last_error_message = Column(Text, nullable=True)
    consecutive_errors = Column(Integer, default=0, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_fetch_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<DiseaseCollectionProgress(fetched={self.total_fetched}, complete={self.is_complete})>"

class DiseaseAlias(Base):
    """
    Maps user-friendly disease names and synonyms to canonical MONDO identifiers.
    Enables reliable lookups regardless of how users phrase the disease name.

    Examples:
    - "diabetes type 1" -> MONDO:0005147
    - "t1dm" -> MONDO:0005147
    - "juvenile diabetes" -> MONDO:0005147
    """
    __tablename__ = "disease_aliases"

    # Primary key
    id = Column(String, primary_key=True)  # UUID

    # Alias information
    alias = Column(String(500), nullable=False, index=True)  # User-friendly name (normalized lowercase)
    alias_display = Column(String(500), nullable=False)  # Original case for display

    # Canonical reference
    mondo_id = Column(String(100), nullable=False, index=True)  # Points to DiseaseOntology.mondo_id
    canonical_name = Column(String(500), nullable=False)  # Official disease name for display

    # Alias metadata
    alias_type = Column(String(50), nullable=False, default="synonym")  # synonym, abbreviation, common_name, related
    search_weight = Column(Integer, default=1, nullable=False)  # For ranking autocomplete results
    is_preferred = Column(Boolean, default=False, nullable=False)  # Marks the canonical/preferred term

    # Source tracking
    source = Column(String(100), nullable=False, default="mondo_api")  # Where the alias came from

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<DiseaseAlias(alias='{self.alias}', mondo_id={self.mondo_id})>"

class Medication(Base):
    """
    Comprehensive medication database for drug interaction checking and autocomplete.
    Stores both generic and brand names for commonly prescribed medications.
    """
    __tablename__ = "medications"

    # Primary identifier
    id = Column(String, primary_key=True)  # UUID

    # Medication name (generic or brand)
    name = Column(String(255), nullable=False, index=True, unique=True)

    # Generic/Brand classification
    generic_name = Column(String(255), nullable=True, index=True)  # Generic name if this is a brand
    is_brand = Column(Boolean, default=False, nullable=False)  # True if brand name, False if generic
    brand_names = Column(Text, nullable=True)  # JSON array of brand names

    # Drug classification
    drug_class = Column(String(255), nullable=True, index=True)  # e.g., "NSAID", "antibiotic"
    category = Column(String(255), nullable=True, index=True)  # e.g., "Pain & Anti-inflammatory", "Cardiovascular"

    # Clinical information
    indication = Column(Text, nullable=True)  # Primary indication/use
    nursing_considerations = Column(Text, nullable=True)  # JSON array of nursing considerations
    common_side_effects = Column(Text, nullable=True)  # JSON array of common side effects
    warnings = Column(Text, nullable=True)  # JSON array of warnings/contraindications

    # Metadata
    source = Column(String(100), nullable=False, default="curated")  # Data source
    is_active = Column(Boolean, default=True, nullable=False)  # Active medication

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Medication(name={self.name}, generic={self.generic_name}, is_brand={self.is_brand})>"

# Database Connection Management
async def init_database():
    """Initialize database connection and create tables."""
    global engine, SessionLocal
    
    try:
        # Try to import config
        try:
            from src.utils.config import get_settings
            settings = get_settings()
            database_url = settings.DATABASE_URL
        except:
            # Fallback to environment variable or default
            database_url = os.getenv("DATABASE_URL", "sqlite:///./ai_nurse_florence.db")
        
        # Convert to async URLs
        if database_url.startswith("sqlite:"):
            database_url = database_url.replace("sqlite:", "sqlite+aiosqlite:")
        elif database_url.startswith("postgresql:"):
            database_url = database_url.replace("postgresql:", "postgresql+asyncpg:")
        
        logger.info(f"🔄 Initializing database...")
        
        engine = create_async_engine(
            database_url,
            echo=False,
            future=True
        )
        
        SessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✅ Database initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        # Fallback to in-memory SQLite
        try:
            database_url = "sqlite+aiosqlite:///./ai_nurse_florence.db"
            engine = create_async_engine(database_url, echo=False)
            SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
            
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            logger.warning("⚠️ Using fallback SQLite database")
            return True
        except Exception as fallback_error:
            logger.error(f"❌ Fallback database initialization failed: {fallback_error}")
            return False

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session for dependency injection."""
    if SessionLocal is None:
        await init_database()
    
    if SessionLocal is None:
        raise RuntimeError("Database not initialized")
    
    async with SessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

async def close_database():
    """Close database connections."""
    global engine
    if engine:
        await engine.dispose()
        logger.info("Database connections closed")

# Database Operations for Authentication Integration
class UserDatabase:
    """Database operations for users."""
    
    @staticmethod
    async def create_user(user_data: Dict[str, Any]) -> Optional[User]:
        """Create a new user in the database."""
        async for session in get_db_session():
            try:
                # Generate UUID if not provided
                if "id" not in user_data or not user_data["id"]:
                    user_data["id"] = str(uuid.uuid4())
                
                user = User(**user_data)
                session.add(user)
                await session.commit()
                await session.refresh(user)
                logger.info(f"✅ User created: {user.email}")
                return user
                
            except IntegrityError as e:
                await session.rollback()
                if "email" in str(e).lower():
                    logger.warning(f"User creation failed: Email {user_data.get('email')} already exists")
                    raise ValueError("Email already exists")
                raise ValueError(f"Database integrity error: {e}")
            except Exception as e:
                await session.rollback()
                logger.error(f"User creation failed: {e}")
                raise e
    
    @staticmethod
    async def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email address."""
        async for session in get_db_session():
            try:
                result = await session.execute(
                    select(User).where(User.email == email)
                )
                user = result.scalar_one_or_none()
                if user:
                    logger.debug(f"User found: {email}")
                return user
            except Exception as e:
                logger.error(f"Error getting user by email {email}: {e}")
                return None
    
    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[User]:
        """Get user by ID."""
        async for session in get_db_session():
            try:
                result = await session.execute(
                    select(User).where(User.id == user_id)
                )
                return result.scalar_one_or_none()
            except Exception as e:
                logger.error(f"Error getting user by ID {user_id}: {e}")
                return None
    
    @staticmethod
    async def update_user(user_id: str, update_data: Dict[str, Any]) -> Optional[User]:
        """Update user data."""
        async for session in get_db_session():
            try:
                update_data["updated_at"] = datetime.utcnow()
                
                await session.execute(
                    update(User).where(User.id == user_id).values(**update_data)
                )
                await session.commit()
                
                # Get updated user
                result = await session.execute(
                    select(User).where(User.id == user_id)
                )
                updated_user = result.scalar_one_or_none()
                logger.info(f"✅ User updated: {user_id}")
                return updated_user
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Error updating user {user_id}: {e}")
                raise e
    
    @staticmethod
    async def update_login_time(user_id: str) -> bool:
        """Update user's last login time."""
        try:
            await UserDatabase.update_user(user_id, {"last_login_at": datetime.utcnow()})
            return True
        except Exception as e:
            logger.error(f"Error updating login time for user {user_id}: {e}")
            return False

    # Admin-specific methods for Phase 3.4.3
    @staticmethod
    async def list_users(skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[User]:
        """List users with pagination and optional search."""
        async for session in get_db_session():
            try:
                query = select(User)
                
                # Add search filter if provided
                if search:
                    search_filter = f"%{search}%"
                    query = query.where(
                        (User.email.ilike(search_filter)) |
                        (User.full_name.ilike(search_filter))
                    )
                
                # Add pagination
                query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
                
                result = await session.execute(query)
                users = result.scalars().all()
                logger.debug(f"Listed {len(users)} users (skip={skip}, limit={limit}, search={search})")
                return list(users)
                
            except Exception as e:
                logger.error(f"Error listing users: {e}")
                return []
    
    @staticmethod
    async def count_users(search: Optional[str] = None) -> int:
        """Count total users with optional search filter."""
        async for session in get_db_session():
            try:
                query = select(User)
                
                # Add search filter if provided
                if search:
                    search_filter = f"%{search}%"
                    query = query.where(
                        (User.email.ilike(search_filter)) |
                        (User.full_name.ilike(search_filter))
                    )
                
                # Count query
                count_query = select(User.id).select_from(query.subquery())
                result = await session.execute(count_query)
                count = len(result.fetchall())
                return count
                
            except Exception as e:
                logger.error(f"Error counting users: {e}")
                return 0
    
    @staticmethod
    async def activate_user(user_id: str) -> bool:
        """Activate a user account."""
        try:
            result = await UserDatabase.update_user(user_id, {"is_active": True})
            if result:
                logger.info(f"✅ User activated: {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error activating user {user_id}: {e}")
            return False
    
    @staticmethod
    async def deactivate_user(user_id: str) -> bool:
        """Deactivate a user account."""
        try:
            result = await UserDatabase.update_user(user_id, {"is_active": False})
            if result:
                logger.info(f"✅ User deactivated: {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deactivating user {user_id}: {e}")
            return False
    
    @staticmethod
    async def change_user_role(user_id: str, new_role: str) -> bool:
        """Change a user's role."""
        try:
            valid_roles = ["user", "nurse", "admin"]
            if new_role not in valid_roles:
                logger.error(f"Invalid role: {new_role}. Must be one of {valid_roles}")
                return False
                
            result = await UserDatabase.update_user(user_id, {"role": new_role})
            if result:
                logger.info(f"✅ User role changed: {user_id} -> {new_role}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error changing user role {user_id}: {e}")
            return False
    
    @staticmethod
    async def verify_user(user_id: str) -> bool:
        """Verify a user account."""
        try:
            result = await UserDatabase.update_user(user_id, {"is_verified": True})
            if result:
                logger.info(f"✅ User verified: {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error verifying user {user_id}: {e}")
            return False
    
    @staticmethod
    async def delete_user(user_id: str) -> bool:
        """Delete a user account (soft delete by deactivation)."""
        async for session in get_db_session():
            try:
                # First deactivate the user
                await UserDatabase.deactivate_user(user_id)
                
                # Add deleted marker to email to prevent conflicts
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                await session.execute(
                    update(User)
                    .where(User.id == user_id)
                    .values(email=User.email + f"_deleted_{timestamp}")
                )
                await session.commit()
                
                logger.info(f"✅ User soft deleted: {user_id}")
                return True
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Error deleting user {user_id}: {e}")
                return False
    
    # Phase 3.4.4: Session Cleanup Methods
    
    @staticmethod
    async def cleanup_expired_sessions(cutoff_time: datetime) -> int:
        """
        Clean up expired sessions from the database.
        
        Args:
            cutoff_time: Sessions older than this will be removed
            
        Returns:
            Number of sessions removed
        """
        async for session in get_db_session():
            try:
                # Delete expired sessions
                result = await session.execute(
                    delete(UserSession).where(
                        UserSession.expires_at < cutoff_time
                    )
                )
                deleted_count = result.rowcount
                await session.commit()
                
                logger.info(f"✅ Cleaned up {deleted_count} expired sessions")
                return deleted_count
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to cleanup expired sessions: {e}")
                return 0
        
        # Fallback return if no session available
        return 0
    
    @staticmethod
    async def get_session_stats() -> Dict[str, Any]:
        """
        Get comprehensive session statistics.
        
        Returns:
            Dictionary with session statistics
        """
        async for session in get_db_session():
            try:
                # Total sessions
                total_result = await session.execute(
                    select(UserSession).where(UserSession.id.isnot(None))
                )
                total_sessions = len(total_result.scalars().all())
                
                # Active sessions (not expired and is_active=True)
                active_result = await session.execute(
                    select(UserSession).where(
                        UserSession.is_active == True,
                        UserSession.expires_at > datetime.utcnow()
                    )
                )
                active_sessions = len(active_result.scalars().all())
                
                # Expired sessions
                expired_result = await session.execute(
                    select(UserSession).where(
                        UserSession.expires_at <= datetime.utcnow()
                    )
                )
                expired_sessions = len(expired_result.scalars().all())
                
                # Sessions by user count
                users_with_sessions_result = await session.execute(
                    select(UserSession.user_id).distinct()
                )
                users_with_sessions = len(users_with_sessions_result.scalars().all())
                
                return {
                    "total_sessions": total_sessions,
                    "active_sessions": active_sessions,
                    "expired_sessions": expired_sessions,
                    "inactive_sessions": total_sessions - active_sessions,
                    "users_with_sessions": users_with_sessions,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Failed to get session statistics: {e}")
                return {
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        # Fallback return if no session available
        return {
            "error": "Database session not available",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    async def cleanup_user_excess_sessions(user_id: str, max_sessions: int = 5) -> int:
        """
        Clean up excess sessions for a user, keeping only the most recent.
        
        Args:
            user_id: User to clean up sessions for
            max_sessions: Maximum sessions to keep per user
            
        Returns:
            Number of sessions removed
        """
        async for session in get_db_session():
            try:
                # Get all active sessions for user, ordered by creation time (newest first)
                result = await session.execute(
                    select(UserSession)
                    .where(UserSession.user_id == user_id)
                    .order_by(UserSession.created_at.desc())
                )
                user_sessions = result.scalars().all()
                
                if len(user_sessions) <= max_sessions:
                    return 0  # No cleanup needed
                
                # Keep the most recent sessions, delete the rest
                sessions_to_delete = user_sessions[max_sessions:]
                session_ids = [s.id for s in sessions_to_delete]
                
                delete_result = await session.execute(
                    delete(UserSession).where(UserSession.id.in_(session_ids))
                )
                deleted_count = delete_result.rowcount
                await session.commit()
                
                logger.info(f"✅ Cleaned up {deleted_count} excess sessions for user {user_id}")
                return deleted_count
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to cleanup excess sessions for user {user_id}: {e}")
                return 0
        
        # Fallback return if no session available
        return 0

class SessionDatabase:
    """Database operations for user sessions."""
    
    @staticmethod
    async def create_session(session_data: Dict[str, Any]) -> Optional[UserSession]:
        """Create a new user session."""
        async for session in get_db_session():
            try:
                # Generate UUID if not provided
                if "id" not in session_data or not session_data["id"]:
                    session_data["id"] = str(uuid.uuid4())
                
                user_session = UserSession(**session_data)
                session.add(user_session)
                await session.commit()
                await session.refresh(user_session)
                logger.info(f"✅ Session created for user: {session_data.get('user_id')}")
                return user_session
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Session creation failed: {e}")
                raise e
    
    @staticmethod
    async def get_active_session(session_token: str) -> Optional[UserSession]:
        """Get active session by token."""
        async for session in get_db_session():
            try:
                result = await session.execute(
                    select(UserSession).where(
                        UserSession.session_token == session_token,
                        UserSession.is_active == True,
                        UserSession.expires_at > datetime.utcnow()
                    )
                )
                return result.scalar_one_or_none()
            except Exception as e:
                logger.error(f"Error getting session {session_token}: {e}")
                return None
    
    @staticmethod
    async def invalidate_session(session_token: str) -> bool:
        """Invalidate a session."""
        async for session in get_db_session():
            try:
                await session.execute(
                    update(UserSession)
                    .where(UserSession.session_token == session_token)
                    .values(is_active=False)
                )
                await session.commit()
                logger.info(f"✅ Session invalidated: {session_token[:8]}...")
                return True
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to invalidate session: {e}")
                return False
