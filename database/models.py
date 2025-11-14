"""SQLAlchemy database models for test protocols"""

from datetime import datetime
from typing import List
from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey,
    Integer, JSON, String, Text
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Protocol(Base):
    """Protocol definition table"""
    __tablename__ = 'protocols'

    id = Column(Integer, primary_key=True, index=True)
    protocol_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    version = Column(String(20), nullable=False)
    standard = Column(String(100))
    category = Column(String(100))
    description = Column(Text)
    template_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    test_runs = relationship('TestRun', back_populates='protocol', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Protocol(protocol_id='{self.protocol_id}', name='{self.name}')>"


class TestRun(Base):
    """Test run/execution table"""
    __tablename__ = 'test_runs'

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(String(100), unique=True, nullable=False, index=True)
    protocol_id = Column(Integer, ForeignKey('protocols.id'), nullable=False)

    # Sample information
    module_serial = Column(String(100), nullable=False, index=True)
    module_manufacturer = Column(String(100))
    module_model = Column(String(100))

    # Test execution
    operator_id = Column(String(50), nullable=False)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime)
    status = Column(String(20), nullable=False, default='pending')  # pending, running, completed, failed, aborted

    # Results
    pass_fail = Column(Boolean)
    power_degradation = Column(Float)
    failure_modes = Column(JSON)  # List of failure mode strings

    # Measurements
    initial_pmax = Column(Float)
    final_pmax = Column(Float)
    initial_voc = Column(Float)
    final_voc = Column(Float)
    initial_isc = Column(Float)
    final_isc = Column(Float)
    initial_ff = Column(Float)
    final_ff = Column(Float)
    initial_insulation = Column(Float)
    final_insulation = Column(Float)

    # Traceability
    qr_code = Column(String(200))
    report_path = Column(String(500))

    # Equipment used
    equipment_ids = Column(JSON)  # List of equipment IDs
    calibration_status = Column(JSON)  # Calibration data

    # Additional data
    notes = Column(Text)
    metadata = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    protocol = relationship('Protocol', back_populates='test_runs')
    measurements = relationship('Measurement', back_populates='test_run', cascade='all, delete-orphan')
    visual_inspections = relationship('VisualInspection', back_populates='test_run', cascade='all, delete-orphan')
    cycles = relationship('CycleLog', back_populates='test_run', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<TestRun(test_id='{self.test_id}', status='{self.status}')>"


class Measurement(Base):
    """Individual measurement data points"""
    __tablename__ = 'measurements'

    id = Column(Integer, primary_key=True, index=True)
    test_run_id = Column(Integer, ForeignKey('test_runs.id'), nullable=False, index=True)

    timestamp = Column(DateTime, nullable=False, index=True)
    parameter = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(20))
    phase = Column(String(50))  # initial, cycle_N, final
    notes = Column(Text)

    # Relationships
    test_run = relationship('TestRun', back_populates='measurements')

    def __repr__(self):
        return f"<Measurement(parameter='{self.parameter}', value={self.value}, unit='{self.unit}')>"


class VisualInspection(Base):
    """Visual inspection records"""
    __tablename__ = 'visual_inspections'

    id = Column(Integer, primary_key=True, index=True)
    test_run_id = Column(Integer, ForeignKey('test_runs.id'), nullable=False, index=True)

    inspection_time = Column(DateTime, nullable=False)
    inspection_type = Column(String(20), nullable=False)  # initial, final

    # Defects
    broken_cells = Column(Integer, default=0)
    delamination = Column(Boolean, default=False)
    junction_box_intact = Column(Boolean, default=True)
    discoloration = Column(Boolean, default=False)
    bubbles_count = Column(Integer, default=0)
    bubbles_max_size_mm = Column(Float)

    # Overall assessment
    inspection_passed = Column(Boolean, nullable=False)
    notes = Column(Text)
    photos = Column(JSON)  # List of photo file paths

    inspector_id = Column(String(50))

    # Relationships
    test_run = relationship('TestRun', back_populates='visual_inspections')

    def __repr__(self):
        return f"<VisualInspection(type='{self.inspection_type}', passed={self.inspection_passed})>"


class CycleLog(Base):
    """Humidity-freeze cycle monitoring data"""
    __tablename__ = 'cycle_logs'

    id = Column(Integer, primary_key=True, index=True)
    test_run_id = Column(Integer, ForeignKey('test_runs.id'), nullable=False, index=True)

    cycle_number = Column(Integer, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    status = Column(String(20), default='running')  # running, completed, failed, aborted

    # Summary statistics
    temp_min = Column(Float)
    temp_max = Column(Float)
    temp_avg = Column(Float)
    humidity_min = Column(Float)
    humidity_max = Column(Float)
    humidity_avg = Column(Float)

    # Excursions/alarms
    temperature_excursions = Column(Integer, default=0)
    humidity_excursions = Column(Integer, default=0)
    excursion_details = Column(JSON)

    # Relationships
    test_run = relationship('TestRun', back_populates='cycles')
    datapoints = relationship('CycleDataPoint', back_populates='cycle', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<CycleLog(cycle={self.cycle_number}, status='{self.status}')>"


class CycleDataPoint(Base):
    """Individual temperature/humidity data points during cycles"""
    __tablename__ = 'cycle_datapoints'

    id = Column(Integer, primary_key=True, index=True)
    cycle_id = Column(Integer, ForeignKey('cycle_logs.id'), nullable=False, index=True)

    timestamp = Column(DateTime, nullable=False, index=True)
    temperature = Column(Float)  # °C
    humidity = Column(Float)  # %RH
    chamber_status = Column(String(50))

    # Relationships
    cycle = relationship('CycleLog', back_populates='datapoints')

    def __repr__(self):
        return f"<CycleDataPoint(temp={self.temperature}, humidity={self.humidity})>"


class Equipment(Base):
    """Equipment registry and calibration tracking"""
    __tablename__ = 'equipment'

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(String(50), unique=True, nullable=False, index=True)
    equipment_type = Column(String(100), nullable=False)
    manufacturer = Column(String(100))
    model = Column(String(100))
    serial_number = Column(String(100))

    # Calibration
    calibration_required = Column(Boolean, default=True)
    calibration_interval_days = Column(Integer)
    last_calibration_date = Column(DateTime)
    next_calibration_date = Column(DateTime, index=True)
    calibration_certificate = Column(String(500))

    # Status
    status = Column(String(20), default='active')  # active, maintenance, retired
    location = Column(String(200))

    notes = Column(Text)
    specifications = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Equipment(equipment_id='{self.equipment_id}', type='{self.equipment_type}')>"
