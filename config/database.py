"""
Database Configuration and Connection Management
================================================
Handles database initialization, session management, and connection pooling.
"""

import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event, select, func
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import streamlit as st

from config.settings import config

# Create declarative base for models
# CRITICAL FIX: Create custom declarative base with extend_existing=True
# SYSTEMATIC FIX: Use standard declarative_base() pattern
# The @st.cache_resource in database/__init__.py already prevents model reimports correctly

# Mixin class for extend_existing support
class ExtendExistingMixin:
    """Mixin to add extend_existing=True to all model tables"""
    @declared_attr
    def __table_args__(cls):
        # CRITICAL FIX: Merge extend_existing with any model-specific __table_args__
        # Models may define __table_args__ as tuple (for indexes) - we must preserve them
        args = cls.__dict__.get('__table_args__', ())
        if isinstance(args, tuple):
            # If tuple, append extend_existing dict to the tuple
            return args + ({'extend_existing': True},)
        elif isinstance(args, dict):
            # If dict, merge extend_existing into it
            return {**args, 'extend_existing': True}
        else:
            # Default: return dict with extend_existing
            return {'extend_existing': True}

# Database engine
_engine = None
_SessionLocal = None

Base = declarative_base(cls=ExtendExistingMixin)
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
                        expire_on_commit=False,
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
        CompanyProfile, AnalysisResult, DataExport
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
                password_hash="admin123",  # Default password (should be changed)
                full_name="System Administrator",
                role="admin",
                is_active=True,
            )
            db.add(admin_user)
            db.commit()

        # Seed ALL 54 test protocols - use idempotent INSERT logic
        # Check if we need to seed (either empty or missing protocols)
        protocols_count = db.query(TestProtocol).count()
        if protocols_count < 54:
            # All 54 protocols matching protocols_registry.py
            all_protocols = [
                # PERFORMANCE TESTING (P1-P12) - 12 protocols
                {"protocol_id": "P1", "name": "I-V Performance Characterization", "category": "performance",
                 "description": "Measure current-voltage characteristics under STC (Standard Test Conditions)",
                 "standard_reference": "IEC 61215-2:2021 MQT 06", "estimated_duration_hours": 2.0, "is_active": True},
                {"protocol_id": "P2", "name": "P-V Performance Analysis", "category": "performance",
                 "description": "Power-voltage characteristic measurement and maximum power point analysis",
                 "standard_reference": "IEC 61215-2:2021 MQT 06", "estimated_duration_hours": 2.0, "is_active": True},
                {"protocol_id": "P3", "name": "STC Power Rating", "category": "performance",
                 "description": "Power rating at Standard Test Conditions (1000 W/m², 25°C, AM1.5G)",
                 "standard_reference": "IEC 61215-1:2021", "estimated_duration_hours": 2.0, "is_active": True},
                {"protocol_id": "P4", "name": "NOCT Determination", "category": "performance",
                 "description": "Nominal Operating Cell Temperature determination",
                 "standard_reference": "IEC 61215-2:2021 MQT 05", "estimated_duration_hours": 8.0, "is_active": True},
                {"protocol_id": "P5", "name": "Temperature Coefficient Measurement", "category": "performance",
                 "description": "Determine temperature coefficients for Isc, Voc, and Pmax",
                 "standard_reference": "IEC 61215-2:2021 MQT 04", "estimated_duration_hours": 6.0, "is_active": True},
                {"protocol_id": "P6", "name": "Low Irradiance Performance", "category": "performance",
                 "description": "Performance measurement at 200 W/m² irradiance",
                 "standard_reference": "IEC 61215-2:2021 MQT 07", "estimated_duration_hours": 3.0, "is_active": True},
                {"protocol_id": "P7", "name": "Performance Matrix Test", "category": "performance",
                 "description": "Multi-condition performance mapping (IEC 61853-1)",
                 "standard_reference": "IEC 61853-1:2011", "estimated_duration_hours": 24.0, "is_active": True},
                {"protocol_id": "P8", "name": "Spectral Response Measurement", "category": "performance",
                 "description": "Measure spectral response and quantum efficiency",
                 "standard_reference": "IEC 60904-8:2014", "estimated_duration_hours": 4.0, "is_active": True},
                {"protocol_id": "P9", "name": "Incidence Angle Modifier (IAM)", "category": "performance",
                 "description": "Measure power output vs. angle of incidence",
                 "standard_reference": "IEC 61853-2:2016", "estimated_duration_hours": 6.0, "is_active": True},
                {"protocol_id": "P10", "name": "Bifacial Performance Test", "category": "performance",
                 "description": "Characterization of bifacial module performance and bifaciality factor",
                 "standard_reference": "IEC TS 60904-1-2:2019", "estimated_duration_hours": 8.0, "is_active": True},
                {"protocol_id": "P11", "name": "Energy Rating Test", "category": "performance",
                 "description": "Energy yield prediction and rating under reference conditions",
                 "standard_reference": "IEC 61853-3:2018", "estimated_duration_hours": 4.0, "is_active": True},
                {"protocol_id": "P12", "name": "Bypass Diode Functionality", "category": "performance",
                 "description": "Verify bypass diode operation under partial shading",
                 "standard_reference": "IEC 61215-2:2021 MQT 18", "estimated_duration_hours": 2.0, "is_active": True},

                # DEGRADATION TESTING (P13-P27) - 15 protocols
                {"protocol_id": "P13", "name": "Light-Induced Degradation (LID)", "category": "degradation",
                 "description": "Assess power degradation under continuous light exposure",
                 "standard_reference": "IEC 61215-2:2021 MQT 19", "estimated_duration_hours": 48.0, "is_active": True},
                {"protocol_id": "P14", "name": "Light & Elevated Temperature ID (LETID)", "category": "degradation",
                 "description": "Light and elevated temperature induced degradation test",
                 "standard_reference": "IEC TS 63202-1:2021", "estimated_duration_hours": 162.0, "is_active": True},
                {"protocol_id": "P15", "name": "Potential-Induced Degradation (PID)", "category": "degradation",
                 "description": "Test for voltage stress induced degradation",
                 "standard_reference": "IEC TS 62804-1:2015", "estimated_duration_hours": 96.0, "is_active": True},
                {"protocol_id": "P16", "name": "PID Recovery Test", "category": "degradation",
                 "description": "Evaluate PID reversibility under recovery conditions",
                 "standard_reference": "IEC TS 62804-1:2015", "estimated_duration_hours": 48.0, "is_active": True},
                {"protocol_id": "P17", "name": "UV Degradation Test", "category": "degradation",
                 "description": "Assess degradation from UV exposure (UV preconditioning)",
                 "standard_reference": "IEC 61215-2:2021 MQT 10", "estimated_duration_hours": 120.0, "is_active": True},
                {"protocol_id": "P18", "name": "Hot Spot Endurance Test", "category": "degradation",
                 "description": "Verify module resilience to localized heating (hot spots)",
                 "standard_reference": "IEC 61215-2:2021 MQT 09", "estimated_duration_hours": 5.0, "is_active": True},
                {"protocol_id": "P19", "name": "Snail Trail Assessment", "category": "degradation",
                 "description": "Visual and electrical assessment of snail trail formation",
                 "standard_reference": "IEC 62759-1:2015", "estimated_duration_hours": 2.0, "is_active": True},
                {"protocol_id": "P20", "name": "Cell Crack Detection", "category": "degradation",
                 "description": "Electroluminescence imaging for micro-crack detection",
                 "standard_reference": "IEC TS 60904-13:2018", "estimated_duration_hours": 1.0, "is_active": True},
                {"protocol_id": "P21", "name": "Solder Bond Degradation", "category": "degradation",
                 "description": "Evaluate solder joint integrity and interconnect degradation",
                 "standard_reference": "IEC 61215-1:2021", "estimated_duration_hours": 4.0, "is_active": True},
                {"protocol_id": "P22", "name": "Delamination Assessment", "category": "degradation",
                 "description": "Identify and quantify delamination in module layers",
                 "standard_reference": "IEC 61215-1:2021", "estimated_duration_hours": 2.0, "is_active": True},
                {"protocol_id": "P23", "name": "Yellowing/Browning Test", "category": "degradation",
                 "description": "Assess encapsulant discoloration and its effect on performance",
                 "standard_reference": "IEC 62788-1-6:2017", "estimated_duration_hours": 2.0, "is_active": True},
                {"protocol_id": "P24", "name": "Corrosion Assessment", "category": "degradation",
                 "description": "Evaluate corrosion of metallic components and interconnects",
                 "standard_reference": "IEC 61701:2020", "estimated_duration_hours": 2.0, "is_active": True},
                {"protocol_id": "P25", "name": "Backsheet Chalking Test", "category": "degradation",
                 "description": "Assess backsheet surface degradation and chalking",
                 "standard_reference": "IEC 62788-2-1:2021", "estimated_duration_hours": 1.0, "is_active": True},
                {"protocol_id": "P26", "name": "Junction Box Degradation", "category": "degradation",
                 "description": "Evaluate junction box integrity and connector condition",
                 "standard_reference": "IEC 62790:2020", "estimated_duration_hours": 2.0, "is_active": True},
                {"protocol_id": "P27", "name": "Long-term Outdoor Exposure", "category": "degradation",
                 "description": "Natural weathering and outdoor degradation monitoring",
                 "standard_reference": "IEC 61215-1:2021", "estimated_duration_hours": 8760.0, "is_active": True},

                # ENVIRONMENTAL TESTING (P28-P39) - 12 protocols
                {"protocol_id": "P28", "name": "Humidity Freeze Test", "category": "environmental",
                 "description": "Assess module resistance to humidity freeze cycles (10 cycles)",
                 "standard_reference": "IEC 61215-2:2021 MQT 12", "estimated_duration_hours": 240.0, "is_active": True},
                {"protocol_id": "P29", "name": "Damp Heat Test (1000h)", "category": "environmental",
                 "description": "Exposure to 85°C/85% RH for 1000 hours",
                 "standard_reference": "IEC 61215-2:2021 MQT 13", "estimated_duration_hours": 1000.0, "is_active": True},
                {"protocol_id": "P30", "name": "Damp Heat Extended (2000h)", "category": "environmental",
                 "description": "Extended damp heat test for enhanced durability",
                 "standard_reference": "IEC 61215-2:2021", "estimated_duration_hours": 2000.0, "is_active": True},
                {"protocol_id": "P31", "name": "Thermal Cycling Test (200 cycles)", "category": "environmental",
                 "description": "Temperature cycling from -40°C to +85°C (200 cycles)",
                 "standard_reference": "IEC 61215-2:2021 MQT 11", "estimated_duration_hours": 800.0, "is_active": True},
                {"protocol_id": "P32", "name": "Salt Mist Corrosion Test", "category": "environmental",
                 "description": "Exposure to salt spray for coastal environment simulation",
                 "standard_reference": "IEC 61701:2020", "estimated_duration_hours": 500.0, "is_active": True},
                {"protocol_id": "P33", "name": "Ammonia Corrosion Test", "category": "environmental",
                 "description": "Ammonia exposure for agricultural environment simulation",
                 "standard_reference": "IEC 62716:2013", "estimated_duration_hours": 500.0, "is_active": True},
                {"protocol_id": "P34", "name": "Sand/Dust Abrasion Test", "category": "environmental",
                 "description": "Sand and dust abrasion resistance testing",
                 "standard_reference": "IEC 60068-2-68:1994", "estimated_duration_hours": 4.0, "is_active": True},
                {"protocol_id": "P35", "name": "SO2/H2S Corrosion Test", "category": "environmental",
                 "description": "Sulfur dioxide and hydrogen sulfide exposure",
                 "standard_reference": "IEC 60068-2-42:2003", "estimated_duration_hours": 240.0, "is_active": True},
                {"protocol_id": "P36", "name": "Desert Climate Simulation", "category": "environmental",
                 "description": "High temperature, low humidity, and UV stress testing",
                 "standard_reference": "IEC 62892:2019", "estimated_duration_hours": 720.0, "is_active": True},
                {"protocol_id": "P37", "name": "Tropical Climate Simulation", "category": "environmental",
                 "description": "High humidity and temperature cycling for tropical environments",
                 "standard_reference": "IEC 62892:2019", "estimated_duration_hours": 720.0, "is_active": True},
                {"protocol_id": "P38", "name": "Snow Load Test", "category": "environmental",
                 "description": "Static load test simulating accumulated snow",
                 "standard_reference": "IEC 61215-2:2021 MQT 16", "estimated_duration_hours": 4.0, "is_active": True},
                {"protocol_id": "P39", "name": "UV Exposure Test", "category": "environmental",
                 "description": "Accelerated UV exposure (15 kWh/m² minimum)",
                 "standard_reference": "IEC 61215-2:2021 MQT 10", "estimated_duration_hours": 120.0, "is_active": True},

                # MECHANICAL TESTING (P40-P47) - 8 protocols
                {"protocol_id": "P40", "name": "Mechanical Load Test", "category": "mechanical",
                 "description": "Static and cyclic mechanical load testing (2400 Pa / 5400 Pa)",
                 "standard_reference": "IEC 61215-2:2021 MQT 16", "estimated_duration_hours": 8.0, "is_active": True},
                {"protocol_id": "P41", "name": "Dynamic Mechanical Load", "category": "mechanical",
                 "description": "Dynamic loading cycles (1000 cycles at 1000 Pa)",
                 "standard_reference": "IEC TS 62782:2016", "estimated_duration_hours": 24.0, "is_active": True},
                {"protocol_id": "P42", "name": "Hail Impact Test", "category": "mechanical",
                 "description": "Impact resistance test with ice balls (25mm @ 23 m/s)",
                 "standard_reference": "IEC 61215-2:2021 MQT 17", "estimated_duration_hours": 2.0, "is_active": True},
                {"protocol_id": "P43", "name": "Wind Load Simulation", "category": "mechanical",
                 "description": "Cyclic wind load simulation for structural integrity",
                 "standard_reference": "IEC 61215-2:2021 MQT 16", "estimated_duration_hours": 4.0, "is_active": True},
                {"protocol_id": "P44", "name": "Module Twist Test", "category": "mechanical",
                 "description": "Torsional stress test for frame and laminate integrity",
                 "standard_reference": "IEC 62892:2019", "estimated_duration_hours": 2.0, "is_active": True},
                {"protocol_id": "P45", "name": "Vibration Test", "category": "mechanical",
                 "description": "Transportation and installation vibration simulation",
                 "standard_reference": "IEC 60068-2-6:2007", "estimated_duration_hours": 6.0, "is_active": True},
                {"protocol_id": "P46", "name": "Frame/Mounting Stress Test", "category": "mechanical",
                 "description": "Mounting point load test and frame integrity verification",
                 "standard_reference": "IEC 61215-2:2021", "estimated_duration_hours": 4.0, "is_active": True},
                {"protocol_id": "P47", "name": "Robustness of Terminations", "category": "mechanical",
                 "description": "Pull and push test on cables and connectors",
                 "standard_reference": "IEC 61215-2:2021 MQT 14", "estimated_duration_hours": 2.0, "is_active": True},

                # SAFETY & ELECTRICAL TESTING (P48-P54) - 7 protocols
                {"protocol_id": "P48", "name": "Wet Leakage Current Test", "category": "safety",
                 "description": "Measure leakage current under wet conditions",
                 "standard_reference": "IEC 61215-2:2021 MQT 15", "estimated_duration_hours": 4.0, "is_active": True},
                {"protocol_id": "P49", "name": "Insulation Resistance Test", "category": "safety",
                 "description": "Dry insulation resistance measurement (1000V DC)",
                 "standard_reference": "IEC 61215-2:2021 MQT 03", "estimated_duration_hours": 1.0, "is_active": True},
                {"protocol_id": "P50", "name": "Dielectric Withstand Test", "category": "safety",
                 "description": "High voltage insulation test (system voltage + 1000V)",
                 "standard_reference": "IEC 61730-2:2016 MST 16", "estimated_duration_hours": 1.0, "is_active": True},
                {"protocol_id": "P51", "name": "Ground Continuity Test", "category": "safety",
                 "description": "Frame grounding and continuity verification",
                 "standard_reference": "IEC 61730-2:2016 MST 13", "estimated_duration_hours": 0.5, "is_active": True},
                {"protocol_id": "P52", "name": "Fire Resistance Test", "category": "safety",
                 "description": "Spread of flame test for building-integrated applications",
                 "standard_reference": "IEC 61730-2:2016 MST 23-25", "estimated_duration_hours": 4.0, "is_active": True},
                {"protocol_id": "P53", "name": "Reverse Current Overload", "category": "safety",
                 "description": "Bypass diode thermal test under reverse current",
                 "standard_reference": "IEC 61215-2:2021 MQT 18", "estimated_duration_hours": 2.0, "is_active": True},
                {"protocol_id": "P54", "name": "Impulse Voltage Test", "category": "safety",
                 "description": "Lightning impulse withstand test (1.2/50 μs)",
                 "standard_reference": "IEC 61730-2:2016 MST 14", "estimated_duration_hours": 2.0, "is_active": True},
            ]

            # Idempotent INSERT - check if protocol exists before inserting
            for protocol_data in all_protocols:
                existing = db.query(TestProtocol).filter_by(
                    protocol_id=protocol_data["protocol_id"]
                ).first()
                if not existing:
                    protocol = TestProtocol(**protocol_data)
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
