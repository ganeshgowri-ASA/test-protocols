"""
Protocol and TestStep data models.

This module defines the core data structures for representing test protocols.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class TestCategory(Enum):
    """Test category classifications."""
    MECHANICAL = "mechanical"
    ENVIRONMENTAL = "environmental"
    ELECTRICAL = "electrical"
    THERMAL = "thermal"
    OPTICAL = "optical"


class MeasurementType(Enum):
    """Common measurement types."""
    FORCE = "force"
    DEFLECTION = "deflection"
    PRESSURE = "applied_pressure"
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    VOLTAGE = "voltage"
    CURRENT = "current"
    POWER = "power"
    RESISTANCE = "resistance"


@dataclass
class Standard:
    """Test standard information."""
    name: str
    code: str
    version: Optional[str] = None
    url: Optional[str] = None

    def __str__(self) -> str:
        """String representation of standard."""
        if self.version:
            return f"{self.name} {self.code} v{self.version}"
        return f"{self.name} {self.code}"


@dataclass
class Equipment:
    """Test equipment specification."""
    name: str
    type: str
    model: Optional[str] = None
    calibration_required: bool = True
    calibration_interval_days: Optional[int] = None

    def needs_calibration(self, last_calibration: datetime) -> bool:
        """Check if equipment needs calibration."""
        if not self.calibration_required or not self.calibration_interval_days:
            return False

        days_since_calibration = (datetime.now() - last_calibration).days
        return days_since_calibration >= self.calibration_interval_days


@dataclass
class Measurement:
    """Measurement specification."""
    measurement_type: str
    unit: str
    interval_seconds: Optional[float] = None
    sensor_id: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    target_value: Optional[float] = None
    tolerance: Optional[float] = None

    def is_within_limits(self, value: float) -> bool:
        """Check if a measurement value is within acceptable limits."""
        if self.min_value is not None and value < self.min_value:
            return False
        if self.max_value is not None and value > self.max_value:
            return False
        return True

    def is_within_tolerance(self, value: float) -> bool:
        """Check if a measurement value is within tolerance of target."""
        if self.target_value is None or self.tolerance is None:
            return True
        return abs(value - self.target_value) <= self.tolerance


@dataclass
class TestStep:
    """Individual test step within a protocol."""
    step_id: str
    name: str
    sequence: int
    parameters: Dict[str, Any]
    description: Optional[str] = None
    duration_minutes: Optional[float] = None
    measurements: List[Measurement] = field(default_factory=list)
    acceptance_criteria: Dict[str, Any] = field(default_factory=dict)
    operator_instructions: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Convert measurement dicts to Measurement objects."""
        if self.measurements and isinstance(self.measurements[0], dict):
            self.measurements = [
                Measurement(**m) if isinstance(m, dict) else m
                for m in self.measurements
            ]

    def get_measurement(self, measurement_type: str) -> Optional[Measurement]:
        """Get a specific measurement by type."""
        for measurement in self.measurements:
            if measurement.measurement_type == measurement_type:
                return measurement
        return None


@dataclass
class Protocol:
    """
    Test protocol definition.

    Represents a complete test protocol including metadata, test steps,
    equipment requirements, and acceptance criteria.
    """
    protocol_id: str
    version: str
    name: str
    category: str
    standard: Standard
    tests: List[TestStep]
    description: Optional[str] = None
    duration_minutes: Optional[float] = None
    equipment_required: List[Equipment] = field(default_factory=list)
    safety_requirements: List[str] = field(default_factory=list)
    environmental_conditions: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Convert nested dicts to proper objects."""
        # Convert standard dict to Standard object
        if isinstance(self.standard, dict):
            self.standard = Standard(**self.standard)

        # Convert equipment dicts to Equipment objects
        if self.equipment_required and isinstance(self.equipment_required[0], dict):
            self.equipment_required = [
                Equipment(**e) if isinstance(e, dict) else e
                for e in self.equipment_required
            ]

        # Convert test step dicts to TestStep objects
        if self.tests and isinstance(self.tests[0], dict):
            self.tests = [
                TestStep(**t) if isinstance(t, dict) else t
                for t in self.tests
            ]

        # Sort tests by sequence
        self.tests.sort(key=lambda x: x.sequence)

    def get_step(self, step_id: str) -> Optional[TestStep]:
        """Get a specific test step by ID."""
        for step in self.tests:
            if step.step_id == step_id:
                return step
        return None

    def get_step_by_sequence(self, sequence: int) -> Optional[TestStep]:
        """Get a test step by sequence number."""
        for step in self.tests:
            if step.sequence == sequence:
                return step
        return None

    def validate(self) -> tuple[bool, List[str]]:
        """
        Validate protocol structure and data.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check required fields
        if not self.protocol_id:
            errors.append("protocol_id is required")
        if not self.version:
            errors.append("version is required")
        if not self.name:
            errors.append("name is required")
        if not self.tests:
            errors.append("at least one test step is required")

        # Validate test step sequences
        sequences = [step.sequence for step in self.tests]
        if len(sequences) != len(set(sequences)):
            errors.append("duplicate sequence numbers found in test steps")

        if sequences and min(sequences) < 1:
            errors.append("sequence numbers must start at 1")

        # Validate step IDs are unique
        step_ids = [step.step_id for step in self.tests]
        if len(step_ids) != len(set(step_ids)):
            errors.append("duplicate step_id found in test steps")

        return len(errors) == 0, errors

    def get_total_duration(self) -> float:
        """Calculate total protocol duration in minutes."""
        if self.duration_minutes:
            return self.duration_minutes

        total = sum(
            step.duration_minutes for step in self.tests
            if step.duration_minutes is not None
        )
        return total

    def get_category_enum(self) -> TestCategory:
        """Get the category as an enum value."""
        try:
            return TestCategory(self.category)
        except ValueError:
            return TestCategory.MECHANICAL  # default

    def __str__(self) -> str:
        """String representation of protocol."""
        return f"{self.protocol_id} v{self.version}: {self.name}"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"Protocol(id={self.protocol_id}, version={self.version}, "
            f"name={self.name}, steps={len(self.tests)})"
        )
