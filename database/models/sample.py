"""Sample model for storing PV module/sample information."""

from sqlalchemy import Column, String, Text, JSON, Float, Integer
from .base import Base, IDMixin, TimestampMixin


class Sample(Base, IDMixin, TimestampMixin):
    """
    Sample model representing a PV module or test sample.

    This stores information about the physical samples being tested.
    """

    __tablename__ = "samples"

    sample_id = Column(String(100), unique=True, nullable=False, index=True)
    sample_name = Column(String(200))

    # Module specifications
    manufacturer = Column(String(100))
    model = Column(String(100))
    serial_number = Column(String(100), index=True)
    technology = Column(String(50))  # e.g., "mono-Si", "poly-Si", "PERC", "n-type"

    # Rated specifications
    rated_power = Column(Float)  # Watts
    rated_voltage = Column(Float)  # Volts
    rated_current = Column(Float)  # Amps

    # Physical properties
    area = Column(Float)  # m²
    num_cells = Column(Integer)

    # Additional data
    specifications = Column(JSON)  # Full datasheet specs
    notes = Column(Text)

    # Tracking
    location = Column(String(200))
    status = Column(String(50), default="available")  # available, in_test, retired

    def __repr__(self):
        return f"<Sample(id={self.sample_id}, name='{self.sample_name}', model='{self.model}')>"

    def to_dict(self):
        """Convert sample to dictionary."""
        return {
            "id": self.id,
            "sample_id": self.sample_id,
            "sample_name": self.sample_name,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "serial_number": self.serial_number,
            "technology": self.technology,
            "rated_power": self.rated_power,
            "rated_voltage": self.rated_voltage,
            "rated_current": self.rated_current,
            "area": self.area,
            "num_cells": self.num_cells,
            "specifications": self.specifications,
            "notes": self.notes,
            "location": self.location,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
