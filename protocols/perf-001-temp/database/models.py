"""
PERF-001 Database Models
SQLAlchemy ORM models for PostgreSQL/SQLite integration
"""

from sqlalchemy import (
    Column, Integer, String, Numeric, Boolean, Text, Date, DateTime, ForeignKey,
    CheckConstraint, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import List, Optional
import json

Base = declarative_base()


class PERF001Test(Base):
    """Main test record"""
    __tablename__ = 'perf_001_tests'

    # Primary identification
    test_id = Column(String(50), primary_key=True)
    protocol_id = Column(String(20), default='PERF-001', nullable=False)
    protocol_version = Column(String(20), default='1.0.0')

    # Test specimen information
    module_id = Column(String(100), nullable=False, index=True)
    manufacturer = Column(String(200), nullable=False)
    model = Column(String(200), nullable=False)
    technology = Column(String(50))
    rated_power_stc = Column(Numeric(10, 2))
    cell_count = Column(Integer)
    module_area = Column(Numeric(10, 4))
    specimen_notes = Column(Text)

    # Test conditions
    irradiance = Column(Numeric(10, 2), default=1000.0)
    spectrum = Column(String(20), default='AM1.5G')
    reference_temperature = Column(Numeric(5, 2), default=25.0)

    # Calculated results
    temp_coef_pmax = Column(Numeric(10, 6))
    temp_coef_pmax_unit = Column(String(10), default='%/°C')
    temp_coef_pmax_r_squared = Column(Numeric(10, 6))
    temp_coef_voc = Column(Numeric(10, 6))
    temp_coef_voc_unit = Column(String(10), default='%/°C')
    temp_coef_voc_r_squared = Column(Numeric(10, 6))
    temp_coef_isc = Column(Numeric(10, 6))
    temp_coef_isc_unit = Column(String(10), default='%/°C')
    temp_coef_isc_r_squared = Column(Numeric(10, 6))
    normalized_power_25c = Column(Numeric(10, 2))

    # Quality checks
    data_completeness = Column(Boolean, default=False)
    measurement_stability = Column(Boolean, default=False)
    linearity_check = Column(Boolean, default=False)
    range_validation = Column(Boolean, default=False)
    quality_warnings = Column(Text)
    quality_errors = Column(Text)

    # Metadata
    test_date = Column(Date, nullable=False, index=True)
    test_facility = Column(String(200), nullable=False)
    operator = Column(String(200), nullable=False)
    ambient_temperature = Column(Numeric(5, 2))
    relative_humidity = Column(Numeric(5, 2))
    barometric_pressure = Column(Numeric(6, 2))

    # Equipment
    solar_simulator = Column(String(200))
    iv_tracer = Column(String(200))
    temperature_control = Column(String(200))
    calibration_date = Column(Date)

    # Project and traceability
    project_id = Column(String(100), index=True)
    client = Column(String(200))
    purchase_order = Column(String(100))
    lims_id = Column(String(100), index=True)
    qms_reference = Column(String(100))
    parent_test_id = Column(String(100), ForeignKey('perf_001_tests.test_id'))

    # Audit trail
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String(100))
    status = Column(String(50), default='draft', index=True)
    notes = Column(Text)

    # Relationships
    measurements = relationship(
        "PERF001Measurement",
        back_populates="test",
        cascade="all, delete-orphan"
    )
    related_tests = relationship(
        "PERF001RelatedTest",
        back_populates="test",
        cascade="all, delete-orphan"
    )
    revisions = relationship(
        "PERF001Revision",
        back_populates="test",
        cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'test_id': self.test_id,
            'protocol_id': self.protocol_id,
            'module_id': self.module_id,
            'manufacturer': self.manufacturer,
            'model': self.model,
            'technology': self.technology,
            'test_date': self.test_date.isoformat() if self.test_date else None,
            'temp_coef_pmax': float(self.temp_coef_pmax) if self.temp_coef_pmax else None,
            'temp_coef_voc': float(self.temp_coef_voc) if self.temp_coef_voc else None,
            'temp_coef_isc': float(self.temp_coef_isc) if self.temp_coef_isc else None,
            'status': self.status,
        }

    def __repr__(self):
        return f"<PERF001Test(test_id='{self.test_id}', module_id='{self.module_id}', date='{self.test_date}')>"


class PERF001Measurement(Base):
    """Individual temperature measurement"""
    __tablename__ = 'perf_001_measurements'

    measurement_id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(String(50), ForeignKey('perf_001_tests.test_id'), nullable=False, index=True)

    # Temperature and electrical parameters
    temperature = Column(Numeric(6, 2), nullable=False, index=True)
    pmax = Column(Numeric(10, 3), nullable=False)
    voc = Column(Numeric(10, 3), nullable=False)
    isc = Column(Numeric(10, 3), nullable=False)
    vmp = Column(Numeric(10, 3), nullable=False)
    imp = Column(Numeric(10, 3), nullable=False)

    # Derived parameters
    fill_factor = Column(Numeric(10, 6))
    efficiency = Column(Numeric(10, 4))

    # Measurement metadata
    measurement_timestamp = Column(DateTime)
    measurement_duration = Column(Numeric(10, 2))
    stabilization_time = Column(Numeric(10, 2))

    # Quality indicators
    stability_indicator = Column(String(20))
    quality_flag = Column(String(20))

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    test = relationship("PERF001Test", back_populates="measurements")
    iv_curves = relationship(
        "PERF001IVCurve",
        back_populates="measurement",
        cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'measurement_id': self.measurement_id,
            'temperature': float(self.temperature),
            'pmax': float(self.pmax),
            'voc': float(self.voc),
            'isc': float(self.isc),
            'vmp': float(self.vmp),
            'imp': float(self.imp),
            'fill_factor': float(self.fill_factor) if self.fill_factor else None,
            'efficiency': float(self.efficiency) if self.efficiency else None,
            'timestamp': self.measurement_timestamp.isoformat() if self.measurement_timestamp else None,
        }

    def __repr__(self):
        return f"<PERF001Measurement(id={self.measurement_id}, T={self.temperature}°C, Pmax={self.pmax}W)>"


class PERF001IVCurve(Base):
    """IV curve data for each measurement"""
    __tablename__ = 'perf_001_iv_curves'

    curve_id = Column(Integer, primary_key=True, autoincrement=True)
    measurement_id = Column(Integer, ForeignKey('perf_001_measurements.measurement_id'), nullable=False, index=True)
    test_id = Column(String(50), ForeignKey('perf_001_tests.test_id'), nullable=False)

    # IV curve data (stored as JSON)
    voltage_data = Column(Text, nullable=False)
    current_data = Column(Text, nullable=False)
    power_data = Column(Text)

    # Curve metadata
    num_points = Column(Integer)
    sweep_rate = Column(Numeric(10, 4))
    reverse_sweep = Column(Boolean, default=False)

    # Quality
    curve_quality = Column(String(20))

    # Relationships
    measurement = relationship("PERF001Measurement", back_populates="iv_curves")

    def set_voltage_data(self, data: List[float]):
        """Set voltage data from list"""
        self.voltage_data = json.dumps(data)
        self.num_points = len(data)

    def get_voltage_data(self) -> List[float]:
        """Get voltage data as list"""
        return json.loads(self.voltage_data) if self.voltage_data else []

    def set_current_data(self, data: List[float]):
        """Set current data from list"""
        self.current_data = json.dumps(data)

    def get_current_data(self) -> List[float]:
        """Get current data as list"""
        return json.loads(self.current_data) if self.current_data else []

    def set_power_data(self, data: List[float]):
        """Set power data from list"""
        self.power_data = json.dumps(data)

    def get_power_data(self) -> Optional[List[float]]:
        """Get power data as list"""
        return json.loads(self.power_data) if self.power_data else None

    def __repr__(self):
        return f"<PERF001IVCurve(id={self.curve_id}, points={self.num_points})>"


class PERF001RelatedTest(Base):
    """Related tests for traceability"""
    __tablename__ = 'perf_001_related_tests'

    relation_id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(String(50), ForeignKey('perf_001_tests.test_id'), nullable=False, index=True)
    related_test_id = Column(String(50), nullable=False)
    relation_type = Column(String(50))
    notes = Column(Text)

    # Relationships
    test = relationship("PERF001Test", back_populates="related_tests")

    def __repr__(self):
        return f"<PERF001RelatedTest(test={self.test_id}, related={self.related_test_id})>"


class PERF001Revision(Base):
    """Revision history for tests"""
    __tablename__ = 'perf_001_revisions'

    revision_id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(String(50), ForeignKey('perf_001_tests.test_id'), nullable=False, index=True)
    revision_number = Column(String(20), nullable=False)
    revision_date = Column(DateTime, default=datetime.utcnow)
    author = Column(String(100), nullable=False)
    changes = Column(Text, nullable=False)
    previous_data = Column(Text)

    # Relationships
    test = relationship("PERF001Test", back_populates="revisions")

    def __repr__(self):
        return f"<PERF001Revision(test={self.test_id}, rev={self.revision_number})>"


# Additional indexes for performance
Index('idx_test_technology', PERF001Test.technology)
Index('idx_test_manufacturer', PERF001Test.manufacturer)
Index('idx_measurement_pmax', PERF001Measurement.pmax)
