"""
Measurement Model

Data model for test measurements.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional

from .base import BaseModel


@dataclass
class Measurement(BaseModel):
    """
    Measurement data model.

    Represents a single measurement data point collected during testing.
    """

    measurement_id: str
    test_session_id: str
    sample_id: str
    measurement_type: str  # e.g., 'yellow_index', 'color_shift'
    value: float
    unit: str
    timestamp: datetime = field(default_factory=datetime.now)
    time_point_hours: Optional[int] = None  # Time point in test sequence
    equipment_id: Optional[str] = None
    operator_id: Optional[str] = None
    environmental_conditions: Dict[str, float] = field(default_factory=dict)
    measurement_conditions: Dict[str, Any] = field(default_factory=dict)
    quality_flag: Optional[str] = None  # 'GOOD', 'SUSPECT', 'BAD'
    notes: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_valid(self) -> bool:
        """Check if measurement is valid (not flagged as bad)."""
        return self.quality_flag != 'BAD'

    def flag_as_suspect(self, reason: str):
        """Flag measurement as suspect."""
        self.quality_flag = 'SUSPECT'
        self.notes = f"{self.notes or ''}\nSuspect: {reason}"
        self.update()

    def flag_as_bad(self, reason: str):
        """Flag measurement as bad."""
        self.quality_flag = 'BAD'
        self.notes = f"{self.notes or ''}\nBad: {reason}"
        self.update()


@dataclass
class MeasurementSet(BaseModel):
    """
    Collection of related measurements at a single time point.

    Groups multiple measurement types (YI, DE, transmittance, etc.)
    taken at the same time.
    """

    measurement_set_id: str
    test_session_id: str
    sample_id: str
    time_point_hours: int
    timestamp: datetime = field(default_factory=datetime.now)
    measurements: Dict[str, float] = field(default_factory=dict)
    environmental_conditions: Dict[str, float] = field(default_factory=dict)
    operator_id: Optional[str] = None
    notes: Optional[str] = None

    def add_measurement(self, measurement_type: str, value: float):
        """
        Add a measurement to the set.

        Args:
            measurement_type: Type of measurement (e.g., 'yellow_index')
            value: Measurement value
        """
        self.measurements[measurement_type] = value
        self.update()

    def get_measurement(self, measurement_type: str) -> Optional[float]:
        """
        Get a specific measurement value.

        Args:
            measurement_type: Type of measurement

        Returns:
            Measurement value or None if not found
        """
        return self.measurements.get(measurement_type)

    def has_all_required(self, required_types: list) -> bool:
        """
        Check if all required measurements are present.

        Args:
            required_types: List of required measurement types

        Returns:
            True if all required measurements are present
        """
        return all(mt in self.measurements for mt in required_types)
