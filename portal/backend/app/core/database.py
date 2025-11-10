"""
Database connection and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import sys
import os

from .config import settings

# Add indexer path to Python path to import existing modules
sys.path.insert(0, settings.indexer_path)

# Import existing models
from models import Base, Job, NewsArticle, TNNews, AIJob

# Create database engine
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False  # Set to True for SQL debugging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Get database session for dependency injection
    
    Usage in FastAPI endpoints:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database (if needed)
    Note: Tables should already exist from the indexer project
    """
    # Create tables if they don't exist (shouldn't be needed)
    Base.metadata.create_all(bind=engine)
