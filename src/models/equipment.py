"""
Equipment and calibration models
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class Equipment(Base):
    """
    Test equipment and instruments
    """
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    equipment_type = Column(String(100), nullable=False)

    # Manufacturer details
    manufacturer = Column(String(255))
    model = Column(String(100))
    serial_number = Column(String(100), unique=True)

    # Specifications
    specifications = Column(JSON)

    # Calibration requirements
    calibration_required = Column(Boolean, default=True)
    calibration_interval_days = Column(Integer, default=365)
    last_calibration_date = Column(DateTime)
    next_calibration_date = Column(DateTime)

    # Status
    is_active = Column(Boolean, default=True)
    location = Column(String(255))
    responsible_person = Column(String(255))

    # Notes
    notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    calibrations = relationship("EquipmentCalibration", back_populates="equipment", cascade="all, delete-orphan")
    test_executions = relationship("TestExecution", back_populates="equipment")

    def __repr__(self):
        return f"<Equipment(equipment_id='{self.equipment_id}', name='{self.name}')>"


class EquipmentCalibration(Base):
    """
    Equipment calibration records
    """
    __tablename__ = "equipment_calibrations"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)

    # Calibration details
    calibration_date = Column(DateTime, nullable=False)
    calibration_due_date = Column(DateTime, nullable=False)
    calibration_certificate_number = Column(String(100))

    # Calibration provider
    calibrated_by = Column(String(255))
    calibration_lab = Column(String(255))
    accreditation_number = Column(String(100))

    # Results
    calibration_passed = Column(Boolean)
    calibration_results = Column(JSON)  # Detailed results

    # Documentation
    certificate_path = Column(String(500))
    notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    equipment = relationship("Equipment", back_populates="calibrations")

    def __repr__(self):
        return f"<EquipmentCalibration(equipment_id={self.equipment_id}, date='{self.calibration_date}')>"
