"""
Database session management for synchronous SQLite operations
Used by routers that need SQLAlchemy ORM access
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

# SQLite database for content settings
DATABASE_URL = "sqlite:///ai_nurse_florence.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required for SQLite
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


__all__ = ['get_db', 'engine', 'SessionLocal']
