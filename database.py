"""
Database session management and engine creation.

This module provides the core components for interacting with the database
using SQLAlchemy's asynchronous features. It sets up the database engine
and provides a dependency for getting a database session in API endpoints.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from utils.config import settings

# Create an asynchronous engine to connect to the database.
# The `future=True` flag enables the 2.0 style of usage.
engine = create_async_engine(
    settings.DATABASE_URL,
    future=True,
    echo=False,  # Set to True to see generated SQL statements
)

# Create a sessionmaker factory for creating new AsyncSession objects.
# `expire_on_commit=False` is important for async sessions.
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# A base class for our declarative models (e.g., User, Report).
# All our database models will inherit from this class.
Base = declarative_base()

async def get_db() -> AsyncSession:
    """
    FastAPI dependency to get a database session.
    
    This will create a new session for each request and ensure it's
    closed when the request is finished.
    """
    try:
        async with AsyncSessionLocal() as session:
            yield session
    except Exception as e:
        # Log the error but don't crash - this allows the API to still function
        # even if the database is temporarily unavailable
        from utils.logging import get_logger
        logger = get_logger(__name__)
        logger.error(f"Database connection error: {str(e)}", exc_info=True)
        # Yield None - endpoints should handle this gracefully
        yield None
