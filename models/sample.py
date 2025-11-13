"""
Sample and Module database models
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship

from .base import BaseModel


class Module(BaseModel):
    """Photovoltaic module model"""

    __tablename__ = 'modules'

    module_id = Column(String(50), unique=True, nullable=False, index=True)
    module_type = Column(String(50), nullable=False)  # monocrystalline, polycrystalline, etc.
    manufacturer = Column(String(100))
    model_number = Column(String(100))
    serial_number = Column(String(100))
    manufacturing_date = Column(DateTime)
    rated_power = Column(Float)  # Watts
    rated_voltage = Column(Float)  # Volts
    rated_current = Column(Float)  # Amps
    dimensions = Column(JSON)  # width, height, thickness
    cell_count = Column(Integer)
    cell_type = Column(String(50))
    specifications = Column(JSON)  # Additional specifications
    notes = Column(Text)

    # Relationships
    samples = relationship("Sample", back_populates="module")

    def __repr__(self):
        return f"<Module(id={self.id}, module_id='{self.module_id}', type='{self.module_type}')>"


class Sample(BaseModel):
    """Test sample model"""

    __tablename__ = 'samples'

    sample_id = Column(String(50), unique=True, nullable=False, index=True)
    module_id = Column(Integer, ForeignKey('modules.id'), nullable=False, index=True)
    batch_id = Column(String(50), index=True)
    status = Column(String(50), nullable=False, default='pending')  # pending, testing, completed, failed
    location = Column(String(100))
    storage_conditions = Column(JSON)
    metadata = Column(JSON)  # Additional metadata

    # Relationships
    module = relationship("Module", back_populates="samples")
    tests = relationship("TestExecution", back_populates="sample")

    def __repr__(self):
        return f"<Sample(id={self.id}, sample_id='{self.sample_id}', status='{self.status}')>"
