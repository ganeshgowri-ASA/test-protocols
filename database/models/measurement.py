"""Measurement model for storing test measurement data."""

from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, JSON, Text, Boolean
from sqlalchemy.orm import relationship
from .base import Base, IDMixin, TimestampMixin


class Measurement(Base, IDMixin, TimestampMixin):
    """
    Measurement model representing a single measurement point in a test.

    This stores the actual measurement data collected during test execution.
    """

    __tablename__ = "measurements"

    # Foreign key
    test_run_id = Column(Integer, ForeignKey("test_runs.id"), nullable=False, index=True)

    # Relationship
    test_run = relationship("TestRun", back_populates="measurements")

    # Measurement identification
    measurement_sequence = Column(Integer, nullable=False)  # Sequential number within test
    measurement_label = Column(String(100))  # e.g., "Initial", "1 hour", "24 hours"
    timestamp = Column(DateTime, nullable=False, index=True)

    # Core electrical parameters
    voc = Column(Float)  # Open-circuit voltage (V)
    isc = Column(Float)  # Short-circuit current (A)
    pmax = Column(Float)  # Maximum power (W)
    vmp = Column(Float)  # Voltage at max power (V)
    imp = Column(Float)  # Current at max power (A)
    fill_factor = Column(Float)  # Fill factor

    # Environmental conditions
    irradiance = Column(Float)  # W/m²
    temperature = Column(Float)  # °C
    humidity = Column(Float)  # %

    # Optional parameters
    efficiency = Column(Float)  # %
    rs = Column(Float)  # Series resistance (Ω)
    rsh = Column(Float)  # Shunt resistance (Ω)

    # I-V curve data (stored as JSON array)
    iv_curve = Column(JSON)  # [{voltage: V, current: I}, ...]

    # Measurement metadata
    measurement_type = Column(String(50))  # initial, during_exposure, post_exposure, recovery
    elapsed_hours = Column(Float)  # Hours since test start

    # Quality flags
    is_valid = Column(Boolean, default=True)
    validation_flags = Column(JSON)  # Store any validation warnings/errors

    # Notes
    operator = Column(String(100))
    notes = Column(Text)

    def __repr__(self):
        return (f"<Measurement(test_run_id={self.test_run_id}, "
                f"seq={self.measurement_sequence}, pmax={self.pmax}W)>")

    def to_dict(self):
        """Convert measurement to dictionary."""
        return {
            "id": self.id,
            "test_run_id": self.test_run_id,
            "measurement_sequence": self.measurement_sequence,
            "measurement_label": self.measurement_label,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "voc": self.voc,
            "isc": self.isc,
            "pmax": self.pmax,
            "vmp": self.vmp,
            "imp": self.imp,
            "fill_factor": self.fill_factor,
            "irradiance": self.irradiance,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "efficiency": self.efficiency,
            "rs": self.rs,
            "rsh": self.rsh,
            "iv_curve": self.iv_curve,
            "measurement_type": self.measurement_type,
            "elapsed_hours": self.elapsed_hours,
            "is_valid": self.is_valid,
            "validation_flags": self.validation_flags,
            "operator": self.operator,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def calculate_fill_factor(self):
        """Calculate fill factor from measured parameters."""
        if self.voc and self.isc and self.voc > 0 and self.isc > 0:
            self.fill_factor = self.pmax / (self.voc * self.isc)
        return self.fill_factor
