"""Measurement database model."""

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


class Measurement(Base):
    """Database model for individual measurements."""

    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign key to test session
    session_id = Column(Integer, ForeignKey("test_sessions.id"), nullable=False)

    # Measurement timestamp
    timestamp = Column(DateTime, nullable=False, index=True)

    # Test conditions
    irradiance = Column(Float)  # W/m²
    module_temp = Column(Float)  # °C
    ambient_temp = Column(Float)  # °C

    # Electrical measurements
    voltage = Column(Float)  # V
    current = Column(Float)  # A
    power = Column(Float)  # W

    # Calculated parameters
    efficiency = Column(Float)  # %
    fill_factor = Column(Float)  # %

    # Additional metadata
    measurement_point = Column(Integer)  # Sequential point number
    test_condition_id = Column(String(50))  # e.g., "G1000_T25"

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    session = relationship("TestSession", back_populates="measurements")

    # Create composite index for efficient queries
    __table_args__ = (
        Index("idx_session_timestamp", "session_id", "timestamp"),
        Index("idx_session_condition", "session_id", "irradiance", "module_temp"),
    )

    def __repr__(self) -> str:
        return (
            f"<Measurement(id={self.id}, session_id={self.session_id}, "
            f"G={self.irradiance}, T={self.module_temp}, "
            f"V={self.voltage}, I={self.current})>"
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "irradiance": self.irradiance,
            "module_temp": self.module_temp,
            "ambient_temp": self.ambient_temp,
            "voltage": self.voltage,
            "current": self.current,
            "power": self.power,
            "efficiency": self.efficiency,
            "fill_factor": self.fill_factor,
            "measurement_point": self.measurement_point,
            "test_condition_id": self.test_condition_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict, session_id: int) -> "Measurement":
        """
        Create Measurement instance from dictionary.

        Args:
            data: Measurement data dictionary
            session_id: Test session ID

        Returns:
            Measurement instance
        """
        # Parse timestamp if string
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        elif timestamp is None:
            timestamp = datetime.utcnow()

        # Calculate power if not provided
        power = data.get("power")
        if power is None and data.get("voltage") and data.get("current"):
            power = data["voltage"] * data["current"]

        return cls(
            session_id=session_id,
            timestamp=timestamp,
            irradiance=data.get("irradiance"),
            module_temp=data.get("module_temp"),
            ambient_temp=data.get("ambient_temp"),
            voltage=data.get("voltage"),
            current=data.get("current"),
            power=power,
            efficiency=data.get("efficiency"),
            fill_factor=data.get("fill_factor"),
            measurement_point=data.get("measurement_point"),
            test_condition_id=data.get("test_condition_id"),
        )
