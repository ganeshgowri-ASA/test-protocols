"""
Database Configuration and Connection Management
================================================
Handles database initialization, session management, and connection pooling.
"""

import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event
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
        admin_exists = db.query(User).filter_by(username="admin").first()

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

        # Seed test protocols if table is empty
    protocols_count = db.query(TestProtocol).count()
    if protocols_count == 0:
        protocols = [
            # Original P1-P10 protocols
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
            # P11-P20: Degradation category
            TestProtocol(protocol_id="P11", name="Light-Induced Degradation Test", category="degradation", is_active=True),
            TestProtocol(protocol_id="P12", name="Potential-Induced Degradation Test", category="degradation", is_active=True),
            TestProtocol(protocol_id="P13", name="LeTID Degradation Test", category="degradation", is_active=True),
            TestProtocol(protocol_id="P14", name="Encapsulant Discoloration Test", category="degradation", is_active=True),
            TestProtocol(protocol_id="P15", name="Backsheet Degradation Test", category="degradation", is_active=True),
            TestProtocol(protocol_id="P16", name="Solder Bond Degradation Test", category="degradation", is_active=True),
            TestProtocol(protocol_id="P17", name="Cell Microcrack Propagation Test", category="degradation", is_active=True),
            TestProtocol(protocol_id="P18", name="Hotspot Degradation Test", category="degradation", is_active=True),
            TestProtocol(protocol_id="P19", name="Corrosion Resistance Test", category="degradation", is_active=True),
            TestProtocol(protocol_id="P20", name="Long-term Outdoor Exposure Test", category="degradation", is_active=True),
            # P21-P30: Environmental category
            TestProtocol(protocol_id="P21", name="Salt Mist Corrosion Test", category="environmental", is_active=True),
            TestProtocol(protocol_id="P22", name="Ammonia Corrosion Test", category="environmental", is_active=True),
            TestProtocol(protocol_id="P23", name="Sand and Dust Exposure Test", category="environmental", is_active=True),
            TestProtocol(protocol_id="P24", name="Hail Impact Test", category="environmental", is_active=True),
            TestProtocol(protocol_id="P25", name="Snow Load Test", category="environmental", is_active=True),
            TestProtocol(protocol_id="P26", name="Wind Load Test", category="environmental", is_active=True),
            TestProtocol(protocol_id="P27", name="Rain Penetration Test", category="environmental", is_active=True),
            TestProtocol(protocol_id="P28", name="Static Environmental Load Test", category="environmental", is_active=True),
            TestProtocol(protocol_id="P29", name="Dynamic Environmental Load Test", category="environmental", is_active=True),
            TestProtocol(protocol_id="P30", name="Altitude Simulation Test", category="environmental", is_active=True),
            # P31-P40: Mechanical category
            TestProtocol(protocol_id="P31", name="Junction Box Pull Test", category="mechanical", is_active=True),
            TestProtocol(protocol_id="P32", name="Cable Stress Test", category="mechanical", is_active=True),
            TestProtocol(protocol_id="P33", name="Connector Durability Test", category="mechanical", is_active=True),
            TestProtocol(protocol_id="P34", name="Frame Integrity Test", category="mechanical", is_active=True),
            TestProtocol(protocol_id="P35", name="Glass Breakage Test", category="mechanical", is_active=True),
            TestProtocol(protocol_id="P36", name="Mounting System Test", category="mechanical", is_active=True),
            TestProtocol(protocol_id="P37", name="Vibration Test", category="mechanical", is_active=True),
            TestProtocol(protocol_id="P38", name="Transport Simulation Test", category="mechanical", is_active=True),
            TestProtocol(protocol_id="P39", name="Edge Seal Adhesion Test", category="mechanical", is_active=True),
            TestProtocol(protocol_id="P40", name="Laminate Adhesion Test", category="mechanical", is_active=True),
            # P41-P50: Safety category
            TestProtocol(protocol_id="P41", name="Electrical Insulation Test", category="safety", is_active=True),
            TestProtocol(protocol_id="P42", name="Dielectric Withstand Test", category="safety", is_active=True),
            TestProtocol(protocol_id="P43", name="Ground Continuity Test", category="safety", is_active=True),
            TestProtocol(protocol_id="P44", name="Bypass Diode Test", category="safety", is_active=True),
            TestProtocol(protocol_id="P45", name="Reverse Current Overload Test", category="safety", is_active=True),
            TestProtocol(protocol_id="P46", name="Fire Classification Test", category="safety", is_active=True),
            TestProtocol(protocol_id="P47", name="Arc Fault Detection Test", category="safety", is_active=True),
            TestProtocol(protocol_id="P48", name="Hot Spot Endurance Test", category="safety", is_active=True),
            TestProtocol(protocol_id="P49", name="Sharp Edge Test", category="safety", is_active=True),
            TestProtocol(protocol_id="P50", name="Accessibility Test", category="safety", is_active=True),
            # P51-P54: Performance category
            TestProtocol(protocol_id="P51", name="Low Irradiance Performance Test", category="performance", is_active=True),
            TestProtocol(protocol_id="P52", name="Spectral Response Test", category="performance", is_active=True),
            TestProtocol(protocol_id="P53", name="Angular Response Test", category="performance", is_active=True),
            TestProtocol(protocol_id="P54", name="Nominal Operating Cell Temperature Test", category="performance", is_active=True),
        ]
        for protocol in protocols:
            db.add(protocol)
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
