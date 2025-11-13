"""
Database Connection Management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
import os
from pathlib import Path

from models.base import Base


# Default database URL (SQLite for development)
DEFAULT_DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'sqlite:///./test_protocols.db'
)

# Global engine and session factory
_engine = None
_SessionLocal = None


def get_engine(database_url: str = None, echo: bool = False):
    """
    Get or create database engine

    Args:
        database_url: Database connection URL
        echo: Enable SQL echo for debugging

    Returns:
        SQLAlchemy engine
    """
    global _engine

    if _engine is None:
        db_url = database_url or DEFAULT_DATABASE_URL

        # Special handling for SQLite
        if db_url.startswith('sqlite'):
            connect_args = {"check_same_thread": False}
        else:
            connect_args = {}

        _engine = create_engine(
            db_url,
            echo=echo,
            connect_args=connect_args,
            pool_pre_ping=True  # Verify connections before using
        )

    return _engine


def get_session_factory(engine=None):
    """
    Get or create session factory

    Args:
        engine: SQLAlchemy engine (optional)

    Returns:
        Session factory
    """
    global _SessionLocal

    if _SessionLocal is None:
        eng = engine or get_engine()
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=eng
        )

    return _SessionLocal


def get_session() -> Session:
    """
    Get a new database session

    Returns:
        Database session
    """
    SessionLocal = get_session_factory()
    return SessionLocal()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """
    Provide a transactional scope for database operations

    Usage:
        with session_scope() as session:
            session.add(obj)
            session.commit()

    Yields:
        Database session
    """
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db(engine=None, drop_all: bool = False):
    """
    Initialize database - create all tables

    Args:
        engine: SQLAlchemy engine (optional)
        drop_all: Drop all tables before creating (use with caution!)
    """
    eng = engine or get_engine()

    # Import all models to ensure they're registered
    from models import (
        Protocol, ProtocolVersion,
        Module, Sample,
        TestExecution, TestMeasurement, TestResult,
        AnalysisResult, DefectRegion
    )

    if drop_all:
        Base.metadata.drop_all(bind=eng)

    Base.metadata.create_all(bind=eng)


def close_db():
    """Close database connections"""
    global _engine, _SessionLocal

    if _SessionLocal:
        _SessionLocal.close_all()
        _SessionLocal = None

    if _engine:
        _engine.dispose()
        _engine = None
