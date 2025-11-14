"""
Sample and batch models for PV modules under test
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class SampleBatch(Base):
    """
    Batch or lot of samples (PV modules)
    """
    __tablename__ = "sample_batches"

    id = Column(Integer, primary_key=True, index=True)
    batch_number = Column(String(100), unique=True, nullable=False, index=True)
    batch_name = Column(String(255))

    # Manufacturing details
    manufacturer = Column(String(255))
    manufacturing_date = Column(DateTime)
    manufacturing_location = Column(String(255))

    # Product details
    product_line = Column(String(255))
    model_number = Column(String(100))
    technology_type = Column(String(100))  # e.g., mono-Si, poly-Si, thin-film

    # Batch characteristics
    quantity = Column(Integer)
    nominal_power = Column(Float)  # Watts
    nominal_voltage = Column(Float)  # Volts
    nominal_current = Column(Float)  # Amps

    # Customer/Project
    customer = Column(String(255))
    project_name = Column(String(255))
    purchase_order = Column(String(100))

    # Notes
    notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    samples = relationship("Sample", back_populates="batch", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<SampleBatch(batch_number='{self.batch_number}', manufacturer='{self.manufacturer}')>"


class Sample(Base):
    """
    Individual PV module sample
    """
    __tablename__ = "samples"

    id = Column(Integer, primary_key=True, index=True)
    sample_id = Column(String(100), unique=True, nullable=False, index=True)
    sample_name = Column(String(255))

    # Batch reference
    batch_id = Column(Integer, ForeignKey("sample_batches.id"))

    # Sample identification
    serial_number = Column(String(100), unique=True)
    barcode = Column(String(100))
    qr_code = Column(String(255))

    # Physical characteristics
    module_type = Column(String(100))
    cell_technology = Column(String(100))
    frame_type = Column(String(100))
    dimensions_length = Column(Float)  # mm
    dimensions_width = Column(Float)  # mm
    dimensions_thickness = Column(Float)  # mm
    weight = Column(Float)  # kg

    # Electrical ratings
    rated_power_pmax = Column(Float)  # W
    rated_voltage_vmp = Column(Float)  # V
    rated_current_imp = Column(Float)  # A
    open_circuit_voltage_voc = Column(Float)  # V
    short_circuit_current_isc = Column(Float)  # A
    max_system_voltage = Column(Float)  # V
    max_overcurrent_protection = Column(Float)  # A

    # Status
    is_active = Column(Boolean, default=True)
    current_location = Column(String(255))
    condition = Column(String(100))  # new, tested, damaged, etc.

    # Custom attributes (flexible JSON storage)
    custom_attributes = Column(JSON)

    # Notes
    notes = Column(Text)

    received_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    batch = relationship("SampleBatch", back_populates="samples")
    test_executions = relationship("TestExecution", back_populates="sample", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Sample(sample_id='{self.sample_id}', serial_number='{self.serial_number}')>"
