"""Base database models and utilities."""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Optional
from pathlib import Path

# Create declarative base
Base = declarative_base()

# Global session factory
_session_factory: Optional[sessionmaker] = None
_engine = None


def init_database(database_url: str = None, echo: bool = False) -> None:
    """
    Initialize database connection.

    Args:
        database_url: SQLAlchemy database URL. If None, uses SQLite in project directory
        echo: Whether to echo SQL statements
    """
    global _session_factory, _engine

    if database_url is None:
        # Default to SQLite in project directory
        project_root = Path(__file__).parent.parent.parent.parent
        db_dir = project_root / "data"
        db_dir.mkdir(exist_ok=True)
        database_url = f"sqlite:///{db_dir}/test_protocols.db"

    _engine = create_engine(database_url, echo=echo)
    _session_factory = sessionmaker(bind=_engine)

    # Create all tables
    Base.metadata.create_all(_engine)


def get_session() -> Session:
    """
    Get a database session.

    Returns:
        SQLAlchemy session

    Raises:
        RuntimeError: If database not initialized
    """
    global _session_factory

    if _session_factory is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")

    return _session_factory()


def get_engine():
    """Get the database engine."""
    global _engine
    if _engine is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return _engine
