"""SQLAlchemy database models for test protocols."""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Protocol(Base):
    """Protocol definition table."""

    __tablename__ = "protocols"

    id = Column(Integer, primary_key=True, autoincrement=True)
    protocol_id = Column(String(50), unique=True, nullable=False, index=True)
    version = Column(String(20), nullable=False)
    title = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(Text)
    applicable_standards = Column(JSON)
    test_conditions = Column(JSON)
    test_equipment_required = Column(JSON)
    test_steps = Column(JSON)
    qc_checks = Column(JSON)
    report_sections = Column(JSON)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    test_executions = relationship("TestExecution", back_populates="protocol")

    def __repr__(self):
        return f"<Protocol(protocol_id='{self.protocol_id}', version='{self.version}')>"


class TestExecution(Base):
    """Test execution instance table."""

    __tablename__ = "test_executions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(String(100), unique=True, nullable=False, index=True)
    protocol_id = Column(Integer, ForeignKey("protocols.id"), nullable=False)
    module_serial_number = Column(String(100), nullable=False, index=True)
    operator = Column(String(100), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    status = Column(String(20), nullable=False, default="Not Started")
    current_step = Column(Integer, default=0)
    test_conditions_actual = Column(JSON)
    equipment_used = Column(JSON)
    overall_result = Column(String(20))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    protocol = relationship("Protocol", back_populates="test_executions")
    test_steps = relationship(
        "TestStep", back_populates="test_execution", cascade="all, delete-orphan"
    )
    qc_checks = relationship(
        "QCCheck", back_populates="test_execution", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<TestExecution(test_id='{self.test_id}', status='{self.status}')>"


class TestStep(Base):
    """Individual test step results table."""

    __tablename__ = "test_steps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_execution_id = Column(Integer, ForeignKey("test_executions.id"), nullable=False)
    step_number = Column(Integer, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    completed = Column(Boolean, default=False)
    passed = Column(Boolean)
    results = Column(JSON)
    acceptance_criteria_status = Column(JSON)
    failures = Column(JSON)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    test_execution = relationship("TestExecution", back_populates="test_steps")
    measurements = relationship(
        "Measurement", back_populates="test_step", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<TestStep(step_number={self.step_number}, name='{self.name}')>"


class Measurement(Base):
    """Individual measurement records table."""

    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_step_id = Column(Integer, ForeignKey("test_steps.id"), nullable=False)
    measurement_name = Column(String(100), nullable=False)
    measurement_type = Column(String(20), nullable=False)
    value_numeric = Column(Float)
    value_text = Column(Text)
    value_boolean = Column(Boolean)
    unit = Column(String(20))
    timestamp = Column(DateTime, default=datetime.utcnow)
    recorded_by = Column(String(100))
    notes = Column(Text)

    # Relationships
    test_step = relationship("TestStep", back_populates="measurements")

    def __repr__(self):
        return f"<Measurement(name='{self.measurement_name}', value={self.get_value()})>"

    def get_value(self):
        """Get the appropriate value based on measurement type."""
        if self.value_numeric is not None:
            return self.value_numeric
        elif self.value_boolean is not None:
            return self.value_boolean
        else:
            return self.value_text


class QCCheck(Base):
    """QC check records table."""

    __tablename__ = "qc_checks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_execution_id = Column(Integer, ForeignKey("test_executions.id"), nullable=False)
    check_name = Column(String(200), nullable=False)
    description = Column(Text)
    required = Column(Boolean, default=True)
    completed = Column(Boolean, default=False)
    passed = Column(Boolean)
    performed_by = Column(String(100))
    performed_at = Column(DateTime)
    notes = Column(Text)

    # Relationships
    test_execution = relationship("TestExecution", back_populates="qc_checks")

    def __repr__(self):
        return f"<QCCheck(name='{self.check_name}', passed={self.passed})>"


class Equipment(Base):
    """Test equipment records table."""

    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    equipment_type = Column(String(100))
    manufacturer = Column(String(100))
    model = Column(String(100))
    serial_number = Column(String(100), unique=True)
    specification = Column(Text)
    calibration_required = Column(Boolean, default=False)
    calibration_date = Column(DateTime)
    calibration_due_date = Column(DateTime)
    calibration_certificate = Column(String(200))
    status = Column(String(20), default="Active")
    location = Column(String(200))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Equipment(name='{self.name}', serial='{self.serial_number}')>"

    @property
    def is_calibration_valid(self) -> bool:
        """Check if equipment calibration is still valid."""
        if not self.calibration_required:
            return True
        if self.calibration_due_date is None:
            return False
        return self.calibration_due_date > datetime.utcnow()
