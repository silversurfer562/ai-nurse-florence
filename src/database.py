"""
Database session management for synchronous database operations
Used by routers that need SQLAlchemy ORM access
"""

import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Use DATABASE_URL from environment (PostgreSQL) or fall back to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///ai_nurse_florence.db")

# For PostgreSQL, replace postgresql:// with postgresql+psycopg2://
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# Create engine with appropriate connection args based on database type
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}  # Required for SQLite
elif DATABASE_URL.startswith("postgresql"):
    connect_args = {
        "connect_timeout": 5,  # 5 second connection timeout
        "options": "-c statement_timeout=10000",  # 10 second query timeout
    }

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=300,  # Recycle connections after 5 minutes
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session.

    Usage in FastAPI:
        @router.get("/endpoint")
        def my_endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


__all__ = ["get_db", "engine", "SessionLocal"]
