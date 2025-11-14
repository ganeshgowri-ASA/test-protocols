"""Database Connection Management

Handles database connections and initialization.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
from typing import Generator
import os

# Base class for models
Base = declarative_base()

# Database URL from environment or default to SQLite
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'sqlite:///./test_protocols.db'
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith('sqlite') else {},
    echo=False,  # Set to True for SQL query logging
    pool_pre_ping=True,
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def init_db():
    """Initialize database tables"""
    from database.models import (
        Protocol, TestRun, Measurement, VisualInspectionRecord,
        HotSpotTest, Equipment, EquipmentCalibration
    )
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Get database session

    Yields:
        SQLAlchemy session
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db_session() -> Session:
    """Get a new database session

    Returns:
        SQLAlchemy session

    Note:
        Caller is responsible for closing the session
    """
    return SessionLocal()
