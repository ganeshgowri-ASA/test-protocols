"""Database Models

SQLAlchemy models for test protocol data storage.
"""

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean,
    Text, ForeignKey, JSON, Enum
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from database.connection import Base


class TestStatus(enum.Enum):
    """Test run status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


class DefectSeverity(enum.Enum):
    """Defect severity enumeration"""
    NONE = "none"
    MINOR = "minor"
    MAJOR = "major"


class Protocol(Base):
    """Protocol definition table"""
    __tablename__ = "protocols"

    id = Column(Integer, primary_key=True, index=True)
    protocol_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    version = Column(String(20), nullable=False)
    standard = Column(String(100), nullable=False)
    category = Column(String(100))
    description = Column(Text)
    json_template = Column(JSON)  # Store entire JSON template
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    test_runs = relationship("TestRun", back_populates="protocol", cascade="all, delete-orphan")


class TestRun(Base):
    """Test run instance table"""
    __tablename__ = "test_runs"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(String(100), unique=True, nullable=False, index=True)
    protocol_id = Column(Integer, ForeignKey("protocols.id"), nullable=False)

    # Module information
    module_serial_number = Column(String(100), nullable=False, index=True)
    module_manufacturer = Column(String(100))
    module_model = Column(String(100))
    module_nameplate_power = Column(Float)
    module_manufacturing_date = Column(DateTime)

    # Test metadata
    operator_name = Column(String(100), nullable=False)
    operator_certification = Column(String(100))
    test_facility = Column(String(200))
    start_time = Column(DateTime, nullable=False, default=datetime.now)
    end_time = Column(DateTime)
    status = Column(Enum(TestStatus), default=TestStatus.PENDING)

    # Results
    pass_fail = Column(Boolean)
    power_degradation_percent = Column(Float)
    notes = Column(Text)

    # I-V curve data
    initial_voc = Column(Float)
    initial_isc = Column(Float)
    initial_pmax = Column(Float)
    initial_fill_factor = Column(Float)
    final_voc = Column(Float)
    final_isc = Column(Float)
    final_pmax = Column(Float)
    final_fill_factor = Column(Float)

    # Insulation and leakage
    initial_insulation_resistance = Column(Float)
    final_insulation_resistance = Column(Float)
    wet_leakage_current = Column(Float)

    # Traceability
    qr_code = Column(Text)  # Base64 encoded QR code image

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    protocol = relationship("Protocol", back_populates="test_runs")
    measurements = relationship("Measurement", back_populates="test_run", cascade="all, delete-orphan")
    visual_inspections = relationship("VisualInspectionRecord", back_populates="test_run", cascade="all, delete-orphan")
    hot_spot_tests = relationship("HotSpotTest", back_populates="test_run", cascade="all, delete-orphan")


class Measurement(Base):
    """Individual measurement records"""
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, index=True)
    test_run_id = Column(Integer, ForeignKey("test_runs.id"), nullable=False)

    timestamp = Column(DateTime, nullable=False, default=datetime.now, index=True)
    parameter = Column(String(100), nullable=False, index=True)
    value = Column(Float, nullable=False)
    unit = Column(String(20))
    notes = Column(Text)

    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    test_run = relationship("TestRun", back_populates="measurements")


class VisualInspectionRecord(Base):
    """Visual inspection records"""
    __tablename__ = "visual_inspections"

    id = Column(Integer, primary_key=True, index=True)
    test_run_id = Column(Integer, ForeignKey("test_runs.id"), nullable=False)

    inspection_type = Column(String(50), nullable=False)  # "initial" or "final"
    timestamp = Column(DateTime, nullable=False, default=datetime.now)
    inspector = Column(String(100), nullable=False)
    defects = Column(JSON)  # List of defect descriptions
    photographs = Column(JSON)  # List of photograph file paths
    severity = Column(Enum(DefectSeverity), default=DefectSeverity.NONE)
    notes = Column(Text)

    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    test_run = relationship("TestRun", back_populates="visual_inspections")


class HotSpotTest(Base):
    """Hot spot test records (for HOT-001 protocol)"""
    __tablename__ = "hot_spot_tests"

    id = Column(Integer, primary_key=True, index=True)
    test_run_id = Column(Integer, ForeignKey("test_runs.id"), nullable=False)

    cell_id = Column(String(50), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    target_temperature = Column(Float)  # °C
    max_temperature_reached = Column(Float)  # °C
    reverse_bias_voltage = Column(Float)  # V
    current_limit = Column(Float)  # A

    # Store temperature profile as JSON array of [timestamp, temperature]
    temperature_profile = Column(JSON)

    # Store thermal image paths as JSON array
    thermal_images = Column(JSON)

    completed = Column(Boolean, default=False)
    notes = Column(Text)

    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    test_run = relationship("TestRun", back_populates="hot_spot_tests")


class Equipment(Base):
    """Equipment registry"""
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    equipment_type = Column(String(100), nullable=False)  # solar_simulator, iv_tracer, etc.
    manufacturer = Column(String(100))
    model = Column(String(100))
    serial_number = Column(String(100))
    specifications = Column(JSON)  # Store equipment specs as JSON

    location = Column(String(200))
    status = Column(String(50), default="active")  # active, maintenance, retired

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    calibrations = relationship("EquipmentCalibration", back_populates="equipment", cascade="all, delete-orphan")


class EquipmentCalibration(Base):
    """Equipment calibration records"""
    __tablename__ = "equipment_calibrations"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)

    calibration_date = Column(DateTime, nullable=False, index=True)
    calibration_due_date = Column(DateTime, nullable=False, index=True)
    calibration_certificate = Column(String(200))  # Certificate file path or number
    performed_by = Column(String(100))
    calibration_standard = Column(String(200))  # Traceability standard
    results = Column(JSON)  # Calibration results as JSON
    notes = Column(Text)

    is_valid = Column(Boolean, default=True)  # Computed: calibration_due_date > now

    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    equipment = relationship("Equipment", back_populates="calibrations")
