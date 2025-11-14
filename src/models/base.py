"""Base database configuration and utilities."""

from datetime import datetime
from sqlalchemy import create_engine, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column
from typing import Optional

Base = declarative_base()


class TimestampMixin:
    """Mixin to add timestamp fields to models."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )


def get_engine(database_url: str = "sqlite:///test_protocols.db"):
    """Create and return a database engine.

    Args:
        database_url: Database connection URL. Defaults to SQLite.

    Returns:
        SQLAlchemy engine instance.
    """
    return create_engine(database_url, echo=False)


def get_session(engine):
    """Create and return a database session.

    Args:
        engine: SQLAlchemy engine instance.

    Returns:
        SQLAlchemy session instance.
    """
    Session = sessionmaker(bind=engine)
    return Session()


def init_db(engine):
    """Initialize database schema.

    Args:
        engine: SQLAlchemy engine instance.
    """
    Base.metadata.create_all(engine)
