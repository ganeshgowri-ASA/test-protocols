"""
Database Configuration and Connection Management
================================================
Handles database initialization, session management, and connection pooling.

CRITICAL FIX FOR STREAMLIT CLOUD:
---------------------------------
Streamlit Cloud uses an ephemeral filesystem - SQLite databases are deleted on every redeploy.
This module supports both SQLite (development) and PostgreSQL (production) to solve this issue.

To use PostgreSQL in production:
1. Set DATABASE_URL environment variable to your PostgreSQL connection string
2. Example: postgresql://user:password@host:5432/database
3. For Railway/Render, use their provided DATABASE_URL

DETACHED INSTANCE ERROR FIX:
----------------------------
SQLAlchemy ORM objects become "detached" when the session that loaded them is closed.
Accessing attributes on detached objects raises DetachedInstanceError.

SOLUTION: Always extract data to Python dicts/primitives INSIDE the session context
before the session closes. Use the helper functions provided here.
"""

import os
from contextlib import contextmanager
from typing import Generator, Any, Dict, List, Optional
from urllib.parse import urlparse

from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool, QueuePool
import streamlit as st

from config.settings import config

# Create declarative base for models
Base = declarative_base()

# Database engine (singleton)
_engine = None
_SessionLocal = None


def get_database_url() -> str:
    """
    Get the database URL with proper handling for different environments.

    Priority:
    1. DATABASE_URL environment variable (for Railway/Render/Heroku)
    2. Config file setting

    Also handles Heroku-style postgres:// URLs that need to be converted to postgresql://
    """
    db_url = os.environ.get('DATABASE_URL', config.DATABASE_URL)

    # Heroku uses postgres:// but SQLAlchemy requires postgresql://
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)

    return db_url


def is_postgresql() -> bool:
    """Check if we're using PostgreSQL"""
    db_url = get_database_url()
    return db_url.startswith('postgresql')


def is_sqlite() -> bool:
    """Check if we're using SQLite"""
    db_url = get_database_url()
    return db_url.startswith('sqlite')


def get_engine():
    """
    Get or create database engine (singleton pattern)

    Supports:
    - SQLite for development (with StaticPool for thread safety)
    - PostgreSQL for production (with connection pooling)
    """
    global _engine

    if _engine is None:
        db_url = get_database_url()

        # Configure engine based on database type
        if db_url.startswith("sqlite"):
            _engine = create_engine(
                db_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=config.DB_ECHO
            )

            # Enable foreign keys for SQLite
            @event.listens_for(_engine, "connect")
            def set_sqlite_pragma(dbapi_conn, connection_record):
                cursor = dbapi_conn.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

        else:
            # PostgreSQL or other databases with proper connection pooling
            _engine = create_engine(
                db_url,
                pool_pre_ping=True,  # Verify connections are alive before using
                pool_size=5,          # Reduced for Streamlit Cloud limits
                max_overflow=10,      # Allow burst connections
                pool_timeout=30,      # Wait 30s for connection
                pool_recycle=1800,    # Recycle connections every 30 min
                echo=config.DB_ECHO
            )

    return _engine


def get_session_local():
    """Get or create session factory"""
    global _SessionLocal

    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )

    return _SessionLocal


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Database session context manager

    Usage:
        with get_db() as db:
            db.query(Model).all()
    """
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def init_database():
    """
    Initialize database - create all tables

    Returns:
        Database session factory
    """
    from database.models import (
        User, ServiceRequest, IncomingInspection,
        Equipment, EquipmentBooking, TestProtocol,
        TestExecution, TestData, AuditLog, QRCode
    )

    engine = get_engine()

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Initialize session factory
    SessionLocal = get_session_local()

    # Create default admin user if not exists
    with get_db() as db:
        from database.models import User
        admin_exists = db.query(User).filter_by(username="admin").first()

        if not admin_exists:
            from datetime import datetime
            import hashlib

            # Simple password hashing (use bcrypt in production)
            password_hash = hashlib.sha256("admin123".encode()).hexdigest()

            admin_user = User(
                username="admin",
                email="admin@solarpv.com",
                password_hash=password_hash,
                full_name="System Administrator",
                role="admin",
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.add(admin_user)
            db.commit()

    return SessionLocal


def reset_database():
    """Drop all tables and recreate - USE WITH CAUTION"""
    engine = get_engine()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def get_cached_db_session():
    """
    Get cached database session for Streamlit

    This uses Streamlit's caching to maintain a single session
    per Streamlit session.
    """
    if 'db_session' not in st.session_state:
        SessionLocal = get_session_local()
        st.session_state.db_session = SessionLocal()

    return st.session_state.db_session


def close_db_session():
    """Close the cached database session"""
    if 'db_session' in st.session_state:
        st.session_state.db_session.close()
        del st.session_state.db_session


# Database health check
def check_database_health() -> dict:
    """
    Check database connection and health

    Returns:
        Dictionary with health status information
    """
    try:
        engine = get_engine()
        db_url = get_database_url()

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        # Hide credentials in URL for display
        display_url = db_url.split("@")[-1] if "@" in db_url else db_url

        return {
            "status": "healthy",
            "database_type": "PostgreSQL" if is_postgresql() else "SQLite",
            "database_url": display_url,
            "connected": True
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "connected": False
        }


# =============================================================================
# ORM TO DICT CONVERSION HELPERS
# =============================================================================
# Use these helpers to prevent DetachedInstanceError by extracting ORM data
# to Python dicts INSIDE the session context.

def orm_to_dict(obj: Any, include_relationships: bool = False) -> Optional[Dict]:
    """
    Convert a SQLAlchemy ORM object to a dictionary.

    IMPORTANT: Call this INSIDE the session context (within the `with get_db()` block)
    to prevent DetachedInstanceError.

    Args:
        obj: SQLAlchemy ORM model instance
        include_relationships: If True, also include simple relationship data

    Returns:
        Dictionary representation of the object, or None if obj is None
    """
    if obj is None:
        return None

    result = {}

    # Get column attributes
    for column in obj.__table__.columns:
        value = getattr(obj, column.name, None)
        # Convert enum values to their string representation
        if hasattr(value, 'value'):
            result[column.name] = value.value
        else:
            result[column.name] = value

    return result


def orm_list_to_dicts(objects: List[Any], include_relationships: bool = False) -> List[Dict]:
    """
    Convert a list of SQLAlchemy ORM objects to a list of dictionaries.

    IMPORTANT: Call this INSIDE the session context (within the `with get_db()` block)
    to prevent DetachedInstanceError.

    Args:
        objects: List of SQLAlchemy ORM model instances
        include_relationships: If True, also include simple relationship data

    Returns:
        List of dictionary representations
    """
    return [orm_to_dict(obj, include_relationships) for obj in objects if obj is not None]


def extract_service_request_display(sr: Any) -> Dict:
    """
    Extract ServiceRequest data needed for display dropdowns.

    Usage:
        with get_db() as db:
            service_requests = db.query(ServiceRequest).all()
            sr_data = [extract_service_request_display(sr) for sr in service_requests]
        # Now safe to use sr_data outside the session

    Args:
        sr: ServiceRequest ORM instance

    Returns:
        Dictionary with display-friendly data
    """
    return {
        'id': sr.id,
        'request_number': sr.request_number,
        'client_name': sr.client_name,
        'status': sr.status.value if sr.status else 'unknown',
        'display': f"{sr.request_number} - {sr.client_name}"
    }


def extract_test_execution_display(execution: Any) -> Dict:
    """
    Extract TestExecution data needed for display.

    Usage:
        with get_db() as db:
            executions = db.query(TestExecution).all()
            exec_data = [extract_test_execution_display(e) for e in executions]
        # Now safe to use exec_data outside the session

    Args:
        execution: TestExecution ORM instance

    Returns:
        Dictionary with display-friendly data
    """
    return {
        'id': execution.id,
        'execution_number': execution.execution_number,
        'sample_id': execution.sample_id,
        'protocol_id': execution.protocol_id,
        'status': execution.status,
        'status_value': execution.status.value if execution.status else 'unknown',
        'started_at': execution.started_at,
        'completed_at': execution.completed_at,
        'test_passed': execution.test_passed,
        'results': execution.results
    }


# Migration utilities
def run_migrations():
    """
    Run database migrations using Alembic

    Note: This is a placeholder. In production, use:
        alembic upgrade head
    """
    try:
        import alembic.config
        alembic_args = [
            '--raiseerr',
            'upgrade', 'head',
        ]
        alembic.config.main(argv=alembic_args)
        return True
    except Exception as e:
        print(f"Migration error: {e}")
        return False
