"""Base protocol class for all test protocols."""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from utils.logging import get_logger
from utils.validators import validate_parameters, load_json_schema

logger = get_logger(__name__)


@dataclass
class MeasurementPoint:
    """Represents a single measurement point in a test."""

    timestamp: datetime
    values: Dict[str, float]  # Flexible structure for different measurements
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'values': self.values,
            'notes': self.notes
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MeasurementPoint':
        """Create from dictionary."""
        return cls(
            timestamp=datetime.fromisoformat(data['timestamp']),
            values=data['values'],
            notes=data.get('notes')
        )


@dataclass
class TestResult:
    """Test result with pass/fail and detailed information."""

    protocol_id: str
    sample_id: str
    start_time: datetime
    end_time: datetime
    passed: bool
    summary: str
    details: Dict[str, Any]
    acceptance_criteria: Dict[str, Any]
    operator: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'protocol_id': self.protocol_id,
            'sample_id': self.sample_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'passed': self.passed,
            'summary': self.summary,
            'details': self.details,
            'acceptance_criteria': self.acceptance_criteria,
            'operator': self.operator
        }


class BaseProtocol(ABC):
    """Abstract base class for all test protocols.

    All protocol implementations must inherit from this class and
    implement the required abstract methods.
    """

    def __init__(
        self,
        protocol_id: str,
        name: str,
        standard: str,
        version: str = "1.0.0",
        schema_path: Optional[str] = None
    ):
        """Initialize protocol.

        Args:
            protocol_id: Unique protocol identifier (e.g., WET-001)
            name: Human-readable protocol name
            standard: Standard reference (e.g., IEC 61730 MST 02)
            version: Protocol version
            schema_path: Path to JSON schema file
        """
        self.protocol_id = protocol_id
        self.name = name
        self.standard = standard
        self.version = version
        self.schema_path = schema_path
        self.schema: Optional[Dict[str, Any]] = None
        self.measurements: List[MeasurementPoint] = []
        self.parameters: Dict[str, Any] = {}
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

        # Load schema if path provided
        if schema_path:
            self._load_schema()

        logger.info(f"Initialized protocol {protocol_id} - {name}")

    def _load_schema(self) -> None:
        """Load JSON schema from file."""
        if self.schema_path:
            try:
                self.schema = load_json_schema(self.schema_path)
                logger.debug(f"Loaded schema for {self.protocol_id}")
            except Exception as e:
                logger.error(f"Failed to load schema: {e}")
                raise

    @abstractmethod
    def validate_parameters(self, params: Dict[str, Any]) -> bool:
        """Validate test parameters against protocol requirements.

        Args:
            params: Dictionary of test parameters

        Returns:
            True if parameters are valid

        Raises:
            ValueError: If parameters are invalid
        """
        pass

    @abstractmethod
    def run_test(
        self,
        params: Dict[str, Any],
        sample_id: str,
        operator: Optional[str] = None
    ) -> TestResult:
        """Execute the test protocol.

        Args:
            params: Test parameters
            sample_id: Unique sample identifier
            operator: Name of test operator

        Returns:
            TestResult object with results

        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If test execution fails
        """
        pass

    @abstractmethod
    def analyze_results(self) -> Dict[str, Any]:
        """Analyze measurements and determine pass/fail.

        Returns:
            Dictionary containing analysis results
        """
        pass

    @abstractmethod
    def generate_report(self, test_result: TestResult, format: str = 'html') -> str:
        """Generate test report.

        Args:
            test_result: TestResult object
            format: Report format ('html', 'pdf', 'json')

        Returns:
            Report content as string or file path
        """
        pass

    def add_measurement(self, measurement: MeasurementPoint) -> None:
        """Add a measurement point to the test data.

        Args:
            measurement: MeasurementPoint to add
        """
        self.measurements.append(measurement)
        logger.debug(f"Added measurement at {measurement.timestamp}")

    def clear_measurements(self) -> None:
        """Clear all measurements."""
        self.measurements.clear()
        logger.debug("Cleared all measurements")

    def get_measurements(self) -> List[MeasurementPoint]:
        """Get all measurements.

        Returns:
            List of MeasurementPoint objects
        """
        return self.measurements.copy()

    def export_measurements(self, file_path: str, format: str = 'json') -> None:
        """Export measurements to file.

        Args:
            file_path: Output file path
            format: Export format ('json', 'csv')
        """
        if format == 'json':
            data = [m.to_dict() for m in self.measurements]
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        elif format == 'csv':
            import csv
            if not self.measurements:
                return

            with open(file_path, 'w', newline='') as f:
                # Get all unique value keys
                all_keys = set()
                for m in self.measurements:
                    all_keys.update(m.values.keys())

                fieldnames = ['timestamp'] + sorted(all_keys) + ['notes']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for m in self.measurements:
                    row = {'timestamp': m.timestamp.isoformat(), 'notes': m.notes}
                    row.update(m.values)
                    writer.writerow(row)

        logger.info(f"Exported {len(self.measurements)} measurements to {file_path}")

    def get_info(self) -> Dict[str, Any]:
        """Get protocol information.

        Returns:
            Dictionary with protocol metadata
        """
        return {
            'protocol_id': self.protocol_id,
            'name': self.name,
            'standard': self.standard,
            'version': self.version,
            'measurement_count': len(self.measurements)
        }
