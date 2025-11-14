"""Database schema models using SQLAlchemy."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Protocol(Base):
    """Protocol template definition."""

    __tablename__ = "protocols"

    code = Column(String(20), primary_key=True)
    name = Column(String(200), nullable=False)
    version = Column(String(10), nullable=False)
    description = Column(Text)
    category = Column(String(50), nullable=False)
    standard = Column(String(100))
    template = Column(JSON, nullable=False)  # Full protocol template
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    test_runs = relationship("TestRun", back_populates="protocol")

    def __repr__(self) -> str:
        return f"<Protocol(code='{self.code}', name='{self.name}', version='{self.version}')>"


class TestRun(Base):
    """Test run instance."""

    __tablename__ = "test_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    protocol_code = Column(String(20), ForeignKey("protocols.code"), nullable=False)
    specimen_id = Column(String(100), nullable=False, index=True)
    module_type = Column(String(100))
    manufacturer = Column(String(200))
    rated_power = Column(Float)

    # Test execution
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    status = Column(String(20), nullable=False, default="pending", index=True)
    # Status: pending, running, paused, completed, failed, aborted

    # Parameters and data (stored as JSON for flexibility)
    parameters = Column(JSON, nullable=False)  # Test parameters
    raw_data = Column(JSON)  # Raw measurement data
    analysis_results = Column(JSON)  # Analyzed results
    metrics = Column(JSON)  # Calculated metrics

    # Quality control
    qc_status = Column(String(20), default="pending", index=True)
    # QC Status: pending, pass, fail, warning
    qc_results = Column(JSON)  # QC check results

    # Metadata
    operator = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    protocol = relationship("Protocol", back_populates="test_runs")
    iv_measurements = relationship("IVMeasurement", back_populates="test_run", cascade="all, delete-orphan")
    visual_inspections = relationship(
        "VisualInspection", back_populates="test_run", cascade="all, delete-orphan"
    )
    environmental_logs = relationship(
        "EnvironmentalLog", back_populates="test_run", cascade="all, delete-orphan"
    )
    qc_checks = relationship("QCCheck", back_populates="test_run", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="test_run", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return (
            f"<TestRun(id={self.id}, protocol='{self.protocol_code}', "
            f"specimen='{self.specimen_id}', status='{self.status}')>"
        )


class IVMeasurement(Base):
    """I-V curve measurement data."""

    __tablename__ = "iv_measurements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(Integer, ForeignKey("test_runs.id"), nullable=False, index=True)
    elapsed_hours = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # I-V curve data
    voltage = Column(JSON, nullable=False)  # Array of voltage points
    current = Column(JSON, nullable=False)  # Array of current points
    power = Column(JSON, nullable=False)  # Array of power points

    # Calculated parameters
    max_power = Column(Float, nullable=False)
    voc = Column(Float, nullable=False)  # Open circuit voltage
    isc = Column(Float, nullable=False)  # Short circuit current
    fill_factor = Column(Float)  # Fill factor percentage
    degradation_percent = Column(Float)  # Power degradation from initial

    # Test conditions
    irradiance = Column(Float, default=1000.0)  # W/m²
    temperature = Column(Float, default=25.0)  # °C

    # Relationships
    test_run = relationship("TestRun", back_populates="iv_measurements")

    def __repr__(self) -> str:
        return (
            f"<IVMeasurement(id={self.id}, test_run_id={self.test_run_id}, "
            f"elapsed_hours={self.elapsed_hours}, max_power={self.max_power})>"
        )


class VisualInspection(Base):
    """Visual inspection record with corrosion rating."""

    __tablename__ = "visual_inspections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(Integer, ForeignKey("test_runs.id"), nullable=False, index=True)
    elapsed_hours = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Corrosion assessment
    corrosion_rating = Column(String(50), nullable=False)  # IEC 61701 rating (0-5)
    affected_area_percent = Column(Float, default=0.0)
    notes = Column(Text)

    # Image documentation
    image_path = Column(String(500))
    image_metadata = Column(JSON)  # Resolution, format, annotations, etc.

    # Relationships
    test_run = relationship("TestRun", back_populates="visual_inspections")

    def __repr__(self) -> str:
        return (
            f"<VisualInspection(id={self.id}, test_run_id={self.test_run_id}, "
            f"elapsed_hours={self.elapsed_hours}, rating='{self.corrosion_rating}')>"
        )


class EnvironmentalLog(Base):
    """Environmental conditions log entry."""

    __tablename__ = "environmental_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(Integer, ForeignKey("test_runs.id"), nullable=False, index=True)
    cycle_number = Column(Integer)
    phase = Column(String(20))  # 'spray' or 'dry'
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Environmental measurements
    temperature = Column(Float, nullable=False)  # °C
    humidity = Column(Float, nullable=False)  # %
    salt_concentration = Column(Float)  # %
    spray_rate = Column(Float)  # mL/h/80cm²

    # QC status for this log entry
    qc_status = Column(String(20), default="pass")  # pass, fail, warning
    qc_messages = Column(JSON)  # QC check messages

    # Relationships
    test_run = relationship("TestRun", back_populates="environmental_logs")

    def __repr__(self) -> str:
        return (
            f"<EnvironmentalLog(id={self.id}, test_run_id={self.test_run_id}, "
            f"cycle={self.cycle_number}, temp={self.temperature}, rh={self.humidity})>"
        )


class QCCheck(Base):
    """Quality control check result."""

    __tablename__ = "qc_checks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(Integer, ForeignKey("test_runs.id"), nullable=False, index=True)
    check_name = Column(String(100), nullable=False)
    parameter = Column(String(100), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Expected vs actual
    expected_range = Column(JSON, nullable=False)  # [min, max]
    actual_value = Column(Float, nullable=False)
    tolerance = Column(Float)
    unit = Column(String(20))

    # Result
    passed = Column(Boolean, nullable=False)
    message = Column(Text)

    # Relationships
    test_run = relationship("TestRun", back_populates="qc_checks")

    def __repr__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        return (
            f"<QCCheck(id={self.id}, test_run_id={self.test_run_id}, "
            f"check='{self.check_name}', status='{status}')>"
        )


class Report(Base):
    """Generated test report."""

    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(Integer, ForeignKey("test_runs.id"), nullable=False, index=True)
    protocol_code = Column(String(20), nullable=False)

    # Report metadata
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    file_path = Column(String(500), nullable=False)
    format = Column(String(10), nullable=False)  # pdf, excel, json, html
    status = Column(String(20), default="generated")  # generated, archived, deleted

    # Report content summary
    title = Column(String(200))
    summary = Column(Text)
    generated_by = Column(String(100))

    # Relationships
    test_run = relationship("TestRun", back_populates="reports")

    def __repr__(self) -> str:
        return (
            f"<Report(id={self.id}, test_run_id={self.test_run_id}, "
            f"format='{self.format}', status='{self.status}')>"
        )


# Create all tables
def create_tables(engine):
    """Create all database tables.

    Args:
        engine: SQLAlchemy engine instance
    """
    Base.metadata.create_all(engine)


# Drop all tables (use with caution!)
def drop_tables(engine):
    """Drop all database tables.

    Args:
        engine: SQLAlchemy engine instance

    Warning:
        This will delete all data in the database!
    """
    Base.metadata.drop_all(engine)
