"""
Database Configuration and Connection Management
================================================
Handles database initialization, session management, and connection pooling.
"""

import os
import sys
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event, select, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import streamlit as st

from config.settings import config

# Create declarative base for models
Base = declarative_base()

# Database engine
_engine = None
_SessionLocal = None


def get_engine():
    """Get or create database engine (singleton pattern)"""
    global _engine

    if _engine is None:
        # Configure engine based on database type
        if config.DATABASE_URL.startswith("sqlite"):
            _engine = create_engine(
                config.DATABASE_URL,
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
            # PostgreSQL or other databases
            _engine = create_engine(
                config.DATABASE_URL,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
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
            db.execute(select(Model)).scalars().all()
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
    from sqlalchemy import select, func
    from database.models import (
        User, ServiceRequest, IncomingInspection,
        Equipment, EquipmentBooking, TestProtocol,
        TestExecution, TestData, AuditLog, QRCode,
        CompanyProfile
    )

    engine = get_engine()

    # CRITICAL FIX: Configure mappers before creating tables
    # This ensures all relationships are properly set up
    from sqlalchemy.orm import configure_mappers
    try:
        configure_mappers()
    except Exception as e:
        # If mapper configuration fails, clear and retry
        from sqlalchemy.orm import clear_mappers
        clear_mappers()
        configure_mappers()

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Initialize session factory
    SessionLocal = get_session_local()

    # Create default admin user if not exists
    with get_db() as db:
        admin_exists = db.execute(select(User).where(User.username == "admin")).scalar_one_or_none()

        if not admin_exists:
            admin_user = User(
                username="admin",
                email="admin@solarpv.com",
                full_name="System Administrator",
                role="admin",
                is_active=True,
            )
            db.add(admin_user)
            db.commit()
            print("[DB_INIT] Created default admin user", flush=True)
            sys.stdout.flush()

    # Seed test protocols - MUST be in separate context to ensure fresh session
    print("[DB_INIT] Starting test protocols seeding check...", flush=True)
    sys.stdout.flush()

    with get_db() as db:
        try:
            protocols_count = db.query(TestProtocol).count()
            print(f"[DB_INIT] Current protocols count: {protocols_count}", flush=True)
            sys.stdout.flush()

            if protocols_count < 54:
                print(f"[DB_INIT] Protocols count ({protocols_count}) < 54, seeding required...", flush=True)
                sys.stdout.flush()

                protocols = [
                    TestProtocol(protocol_id="P1", name="I-V Performance Test", category="performance", is_active=True),
                    TestProtocol(protocol_id="P2", name="PMax Tracking Test", category="performance", is_active=True),
                    TestProtocol(protocol_id="P3", name="Temperature Coefficient", category="performance", is_active=True),
                    TestProtocol(protocol_id="P4", name="Module Thermal Test", category="performance", is_active=True),
                    TestProtocol(protocol_id="P5", name="Humidity-Freeze Test", category="environmental", is_active=True),
                    TestProtocol(protocol_id="P6", name="Hot-Humid Test", category="environmental", is_active=True),
                    TestProtocol(protocol_id="P7", name="Thermal Cycling Test", category="degradation", is_active=True),
                    TestProtocol(protocol_id="P8", name="UV Degradation Test", category="degradation", is_active=True),
                    TestProtocol(protocol_id="P9", name="Mechanical Load Test", category="mechanical", is_active=True),
                    TestProtocol(protocol_id="P10", name="Wet Leakage Test", category="safety", is_active=True),
                    TestProtocol(protocol_id="P11", name="Hail Impact Test", category="mechanical", is_active=True),
                    TestProtocol(protocol_id="P12", name="Static Load Test", category="mechanical", is_active=True),
                    TestProtocol(protocol_id="P13", name="Dynamic Load Test", category="mechanical", is_active=True),
                    TestProtocol(protocol_id="P14", name="Bypass Diode Test", category="safety", is_active=True),
                    TestProtocol(protocol_id="P15", name="Ground Continuity Test", category="safety", is_active=True),
                    TestProtocol(protocol_id="P16", name="Insulation Resistance Test", category="safety", is_active=True),
                    TestProtocol(protocol_id="P17", name="Junction Box Test", category="safety", is_active=True),
                    TestProtocol(protocol_id="P18", name="Connector Test", category="safety", is_active=True),
                    TestProtocol(protocol_id="P19", name="Fire Safety Test", category="safety", is_active=True),
                    TestProtocol(protocol_id="P20", name="Hot Spot Endurance Test", category="safety", is_active=True),
                    TestProtocol(protocol_id="P21", name="EL Imaging Test", category="visual", is_active=True),
                    TestProtocol(protocol_id="P22", name="IR Thermography Test", category="visual", is_active=True),
                    TestProtocol(protocol_id="P23", name="Visual Inspection", category="visual", is_active=True),
                    TestProtocol(protocol_id="P24", name="Cell Crack Detection", category="visual", is_active=True),
                    TestProtocol(protocol_id="P25", name="Soldering Quality Test", category="visual", is_active=True),
                    TestProtocol(protocol_id="P26", name="PID Test", category="degradation", is_active=True),
                    TestProtocol(protocol_id="P27", name="LID Test", category="degradation", is_active=True),
                    TestProtocol(protocol_id="P28", name="LeTID Test", category="degradation", is_active=True),
                    TestProtocol(protocol_id="P29", name="Damp Heat Test", category="environmental", is_active=True),
                    TestProtocol(protocol_id="P30", name="Salt Mist Test", category="environmental", is_active=True),
                    TestProtocol(protocol_id="P31", name="Ammonia Corrosion Test", category="environmental", is_active=True),
                    TestProtocol(protocol_id="P32", name="Sand/Dust Test", category="environmental", is_active=True),
                    TestProtocol(protocol_id="P33", name="Altitude Test", category="environmental", is_active=True),
                    TestProtocol(protocol_id="P34", name="Snow Load Test", category="mechanical", is_active=True),
                    TestProtocol(protocol_id="P35", name="Wind Load Test", category="mechanical", is_active=True),
                    TestProtocol(protocol_id="P36", name="Vibration Test", category="mechanical", is_active=True),
                    TestProtocol(protocol_id="P37", name="Impact Resistance Test", category="mechanical", is_active=True),
                    TestProtocol(protocol_id="P38", name="Abrasion Test", category="mechanical", is_active=True),
                    TestProtocol(protocol_id="P39", name="Ribbon Pull Test", category="mechanical", is_active=True),
                    TestProtocol(protocol_id="P40", name="Peel Test", category="mechanical", is_active=True),
                    TestProtocol(protocol_id="P41", name="Low Irradiance Test", category="performance", is_active=True),
                    TestProtocol(protocol_id="P42", name="Spectral Response Test", category="performance", is_active=True),
                    TestProtocol(protocol_id="P43", name="Angular Response Test", category="performance", is_active=True),
                    TestProtocol(protocol_id="P44", name="NOCT Measurement", category="performance", is_active=True),
                    TestProtocol(protocol_id="P45", name="Power Stabilization", category="performance", is_active=True),
                    TestProtocol(protocol_id="P46", name="Outdoor Exposure Test", category="environmental", is_active=True),
                    TestProtocol(protocol_id="P47", name="Accelerated Aging Test", category="degradation", is_active=True),
                    TestProtocol(protocol_id="P48", name="Encapsulant Adhesion Test", category="mechanical", is_active=True),
                    TestProtocol(protocol_id="P49", name="Frame Adhesion Test", category="mechanical", is_active=True),
                    TestProtocol(protocol_id="P50", name="Backsheet Integrity Test", category="visual", is_active=True),
                    TestProtocol(protocol_id="P51", name="Glass Breakage Test", category="mechanical", is_active=True),
                    TestProtocol(protocol_id="P52", name="Edge Seal Test", category="safety", is_active=True),
                    TestProtocol(protocol_id="P53", name="Label Durability Test", category="visual", is_active=True),
                    TestProtocol(protocol_id="P54", name="Warranty Verification Test", category="performance", is_active=True),
                ]

                inserted_count = 0
                for protocol in protocols:
                    try:
                        # Check if protocol already exists
                        existing = db.query(TestProtocol).filter_by(protocol_id=protocol.protocol_id).first()
                        if not existing:
                            db.add(protocol)
                            inserted_count += 1
                            print(f"[DB_INIT] Inserted protocol: {protocol.protocol_id} - {protocol.name}", flush=True)
                            sys.stdout.flush()
                        else:
                            print(f"[DB_INIT] Protocol already exists: {protocol.protocol_id}", flush=True)
                            sys.stdout.flush()
                    except Exception as insert_error:
                        print(f"[DB_INIT] ERROR inserting protocol {protocol.protocol_id}: {insert_error}", flush=True)
                        sys.stdout.flush()
                        raise

                db.commit()
                print(f"[DB_INIT] Successfully inserted {inserted_count} new protocols", flush=True)
                sys.stdout.flush()

                # Verify final count
                final_count = db.query(TestProtocol).count()
                print(f"[DB_INIT] VERIFICATION - Final protocols count: {final_count}", flush=True)
                sys.stdout.flush()

                if final_count < 54:
                    error_msg = f"[DB_INIT] CRITICAL ERROR: Expected 54 protocols, but only {final_count} exist!"
                    print(error_msg, flush=True)
                    sys.stdout.flush()
                    raise RuntimeError(error_msg)
                else:
                    print(f"[DB_INIT] SUCCESS: All {final_count} protocols seeded correctly", flush=True)
                    sys.stdout.flush()
            else:
                print(f"[DB_INIT] Protocols already seeded ({protocols_count} >= 54), skipping...", flush=True)
                sys.stdout.flush()

        except Exception as e:
            print(f"[DB_INIT] CRITICAL SEEDING ERROR: {type(e).__name__}: {e}", flush=True)
            sys.stdout.flush()
            raise RuntimeError(f"Failed to seed test protocols: {e}") from e

    print("[DB_INIT] Database initialization complete", flush=True)
    sys.stdout.flush()

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
        from sqlalchemy import text
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database_url": config.DATABASE_URL.split("@")[-1],  # Hide credentials
            "connected": True
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "connected": False
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
