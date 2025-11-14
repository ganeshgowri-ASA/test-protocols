"""
Database Session Management
Session factory and initialization
"""

import os
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import logging

from .models import Base

logger = logging.getLogger(__name__)


# Database URL from environment or default to SQLite
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./test_protocols.db"
)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("DB_ECHO", "False").lower() == "true",
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """
    Initialize database - create all tables

    Should be called once at application startup
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def get_session() -> Session:
    """
    Get database session

    Returns:
        SQLAlchemy Session instance
    """
    return SessionLocal()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """
    Provide a transactional scope for database operations

    Usage:
        with session_scope() as session:
            session.add(obj)
            # Changes are automatically committed

    Yields:
        SQLAlchemy Session instance
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()


def reset_db() -> None:
    """
    Reset database - drop all tables and recreate

    WARNING: This will delete all data!
    Should only be used in development/testing
    """
    logger.warning("Resetting database - all data will be lost!")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    logger.info("Database reset complete")
