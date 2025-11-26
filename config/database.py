"""
Database Configuration and Connection Management
================================================
Handles database initialization, session management, and connection pooling.
Supports multiple platforms: Railway, Replit, GenSpark, Streamlit Cloud, and Local.

ROLLBACK MECHANISM:
- Set FORCE_SQLITE=1 environment variable to force SQLite fallback
- This provides instant rollback capability without code changes
"""

import os
import logging
from contextlib import contextmanager
from typing import Generator, Optional, Dict, Any

from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool, QueuePool
import streamlit as st

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create declarative base for models
Base = declarative_base()

# Database engine and session (singletons)
_engine = None
_SessionLocal = None
_platform_config = None


def get_platform_config():
    """Get or load platform configuration (lazy loading)"""
    global _platform_config
    if _platform_config is None:
        from config.platform import get_platform_config as load_config
        _platform_config = load_config()
        logger.info(f"Platform: {_platform_config.platform.value}, "
                    f"Database: {_platform_config.database_type.value}")
    return _platform_config


def get_engine():
    """
    Get or create database engine (singleton pattern).
    Automatically configures for the detected platform.
    """
    global _engine

    if _engine is None:
        config = get_platform_config()
        db_url = config.database_url
        db_type = config.database_type.value

        logger.info(f"Initializing database engine for {db_type}")

        # Configure engine based on database type
        if db_type == "sqlite":
            _engine = create_engine(
                db_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=os.getenv("DB_ECHO", "").lower() == "true"
            )

            # Enable foreign keys for SQLite
            @event.listens_for(_engine, "connect")
            def set_sqlite_pragma(dbapi_conn, connection_record):
                cursor = dbapi_conn.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

            logger.info("SQLite engine created with foreign keys enabled")

        else:
            # PostgreSQL configuration with platform-optimized pool settings
            from config.platform import get_pool_config
            pool_config = get_pool_config(config.platform, config.database_type)

            _engine = create_engine(
                db_url,
                poolclass=QueuePool,
                pool_pre_ping=pool_config.get("pool_pre_ping", True),
                pool_size=pool_config.get("pool_size", 3),
                max_overflow=pool_config.get("max_overflow", 5),
                pool_recycle=pool_config.get("pool_recycle", 1800),
                pool_timeout=pool_config.get("pool_timeout", 30),
                echo=os.getenv("DB_ECHO", "").lower() == "true"
            )

            logger.info(f"PostgreSQL engine created with pool_size={pool_config.get('pool_size', 3)}")

    return _engine


def get_session_local():
    """Get or create session factory"""
    global _SessionLocal

    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
            expire_on_commit=False  # Prevent detached instance errors
        )

    return _SessionLocal


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Database session context manager.

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
        logger.error(f"Database error: {e}")
        raise e
    finally:
        db.close()


def init_database():
    """
    Initialize database - create all tables.
    Handles both SQLite and PostgreSQL.

    Returns:
        Database session factory
    """
    from database.models import (
        User, ServiceRequest, IncomingInspection,
        Equipment, EquipmentBooking, TestProtocol,
        TestExecution, TestData, AuditLog, QRCode,
        CompanyProfile
    )

    engine = get_engine()
    config = get_platform_config()

    # Configure mappers before creating tables
    from sqlalchemy.orm import configure_mappers
    try:
        configure_mappers()
    except Exception as e:
        logger.warning(f"Mapper configuration warning: {e}")
        from sqlalchemy.orm import clear_mappers
        clear_mappers()
        try:
            configure_mappers()
        except Exception as e2:
            logger.warning(f"Mapper reconfiguration warning: {e2}")

    # Create all tables
    Base.metadata.create_all(bind=engine)
    logger.info(f"Database tables created ({config.database_type.value})")

    # Initialize session factory
    SessionLocal = get_session_local()

    # Create default admin user if not exists
    with get_db() as db:
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
            logger.info("Default admin user created")

    return SessionLocal


def reset_database():
    """Drop all tables and recreate - USE WITH CAUTION"""
    engine = get_engine()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    logger.warning("Database reset complete - all data has been deleted")


def get_cached_db_session():
    """
    Get cached database session for Streamlit.
    Uses Streamlit's session state to maintain a single session per user session.
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


def check_database_health() -> Dict[str, Any]:
    """
    Check database connection and health.

    Returns:
        Dictionary with health status information
    """
    try:
        config = get_platform_config()
        engine = get_engine()

        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()

        return {
            "status": "healthy",
            "platform": config.platform.value,
            "database_type": config.database_type.value,
            "connected": True,
            "is_rollback_mode": is_rollback_mode()
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "connected": False,
            "is_rollback_mode": is_rollback_mode()
        }


def is_rollback_mode() -> bool:
    """Check if the application is in SQLite rollback mode"""
    from config.platform import is_rollback_mode as check_rollback
    return check_rollback()


def get_database_info() -> Dict[str, Any]:
    """
    Get detailed database information for display.
    Masks sensitive information like passwords.
    """
    config = get_platform_config()
    from config.platform import get_platform_info
    return get_platform_info()


# Migration utilities
def run_migrations():
    """
    Run database migrations using Alembic.

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
    except ImportError:
        logger.warning("Alembic not installed - migrations skipped")
        return False
    except Exception as e:
        logger.error(f"Migration error: {e}")
        return False


# Export for backward compatibility
def get_config():
    """Get the legacy config object for backward compatibility"""
    from config.settings import config as legacy_config
    return legacy_config


# Ensure config has DATABASE_URL from platform detection
def _update_legacy_config():
    """Update legacy config with platform-detected DATABASE_URL"""
    try:
        from config.settings import config as legacy_config
        platform_config = get_platform_config()
        legacy_config.DATABASE_URL = platform_config.database_url
    except Exception as e:
        logger.debug(f"Could not update legacy config: {e}")


# Auto-update on import
_update_legacy_config()
