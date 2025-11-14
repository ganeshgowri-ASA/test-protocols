"""Base protocol class and related models."""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime


@dataclass
class ProtocolParameter:
    """Represents a test parameter defined in the protocol."""

    name: str
    param_type: str
    unit: str
    description: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    default_value: Optional[Any] = None
    tolerance: Optional[float] = None
    required: bool = True

    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        """Validate a parameter value against constraints.

        Args:
            value: The value to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if self.required and value is None:
            return False, f"{self.name} is required but not provided"

        if value is None:
            return True, None

        # Type checking
        if self.param_type == "float":
            try:
                value = float(value)
            except (TypeError, ValueError):
                return False, f"{self.name} must be a number"
        elif self.param_type == "integer":
            try:
                value = int(value)
            except (TypeError, ValueError):
                return False, f"{self.name} must be an integer"

        # Range checking
        if self.min_value is not None and value < self.min_value:
            return False, f"{self.name} must be >= {self.min_value} {self.unit}"
        if self.max_value is not None and value > self.max_value:
            return False, f"{self.name} must be <= {self.max_value} {self.unit}"

        return True, None


@dataclass
class Measurement:
    """Represents a single measurement within a measurement point."""

    parameter: str
    name: str
    unit: str
    tolerance: Optional[float]
    method: str


@dataclass
class MeasurementPoint:
    """Represents a measurement point in the test protocol."""

    id: str
    sequence: int
    name: str
    description: str
    timing: str
    required: bool
    measurements: List[Measurement]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MeasurementPoint':
        """Create MeasurementPoint from dictionary."""
        measurements = [
            Measurement(**m) for m in data.get('measurements', [])
        ]
        return cls(
            id=data['id'],
            sequence=data['sequence'],
            name=data['name'],
            description=data['description'],
            timing=data['timing'],
            required=data['required'],
            measurements=measurements
        )


@dataclass
class PassFailCriterion:
    """Represents a pass/fail criterion."""

    name: str
    criterion_type: str
    description: str
    severity: str
    parameter: Optional[str] = None
    min_retention: Optional[float] = None
    standard_reference: Optional[str] = None

    def evaluate(self, initial_value: float, final_value: float) -> tuple[bool, str]:
        """Evaluate the criterion.

        Args:
            initial_value: Initial measurement value
            final_value: Final measurement value

        Returns:
            Tuple of (passes, evaluation_message)
        """
        if self.criterion_type == "percentage_retention":
            if initial_value == 0:
                return False, f"Initial {self.parameter} is zero - cannot calculate retention"

            retention = (final_value / initial_value) * 100
            passes = retention >= self.min_retention

            message = (
                f"{self.parameter} retention: {retention:.2f}% "
                f"(requirement: >= {self.min_retention}%)"
            )
            return passes, message

        return True, "Criterion type not implemented"


class Protocol:
    """Base class for test protocols loaded from JSON definitions."""

    def __init__(self, json_path: Path):
        """Initialize protocol from JSON file.

        Args:
            json_path: Path to the protocol JSON file
        """
        self.json_path = json_path
        self.definition = self._load_definition()
        self.parameters = self._parse_parameters()
        self.measurement_points = self._parse_measurement_points()
        self.pass_fail_criteria = self._parse_criteria()

    def _load_definition(self) -> Dict[str, Any]:
        """Load protocol definition from JSON file."""
        with open(self.json_path, 'r') as f:
            return json.load(f)

    def _parse_parameters(self) -> Dict[str, ProtocolParameter]:
        """Parse test parameters from protocol definition."""
        params = {}
        for name, spec in self.definition.get('test_parameters', {}).items():
            params[name] = ProtocolParameter(
                name=name,
                param_type=spec['type'],
                unit=spec['unit'],
                description=spec['description'],
                min_value=spec.get('min_value'),
                max_value=spec.get('max_value'),
                default_value=spec.get('default_value'),
                tolerance=spec.get('tolerance'),
                required=spec.get('required', True)
            )
        return params

    def _parse_measurement_points(self) -> List[MeasurementPoint]:
        """Parse measurement points from protocol definition."""
        points = []
        for point_data in self.definition.get('measurement_points', []):
            points.append(MeasurementPoint.from_dict(point_data))
        return sorted(points, key=lambda p: p.sequence)

    def _parse_criteria(self) -> Dict[str, PassFailCriterion]:
        """Parse pass/fail criteria from protocol definition."""
        criteria = {}
        for name, spec in self.definition.get('pass_fail_criteria', {}).items():
            criteria[name] = PassFailCriterion(
                name=name,
                criterion_type=spec['type'],
                description=spec['description'],
                severity=spec['severity'],
                parameter=spec.get('parameter'),
                min_retention=spec.get('min_retention'),
                standard_reference=spec.get('standard_reference')
            )
        return criteria

    @property
    def protocol_id(self) -> str:
        """Get protocol ID."""
        return self.definition.get('protocol_id', '')

    @property
    def name(self) -> str:
        """Get protocol name."""
        return self.definition.get('name', '')

    @property
    def version(self) -> str:
        """Get protocol version."""
        return self.definition.get('version', '1.0.0')

    @property
    def category(self) -> str:
        """Get protocol category."""
        return self.definition.get('category', '')

    def validate_parameters(self, params: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate test parameters.

        Args:
            params: Dictionary of parameter values to validate

        Returns:
            Tuple of (all_valid, list_of_errors)
        """
        errors = []

        for param_name, param_spec in self.parameters.items():
            value = params.get(param_name)
            is_valid, error = param_spec.validate(value)

            if not is_valid:
                errors.append(error)

        return len(errors) == 0, errors

    def get_required_measurements(self) -> List[MeasurementPoint]:
        """Get all required measurement points."""
        return [mp for mp in self.measurement_points if mp.required]

    def get_optional_measurements(self) -> List[MeasurementPoint]:
        """Get all optional measurement points."""
        return [mp for mp in self.measurement_points if not mp.required]

    def evaluate_pass_fail(
        self,
        initial_measurements: Dict[str, float],
        final_measurements: Dict[str, float]
    ) -> Dict[str, Any]:
        """Evaluate pass/fail criteria.

        Args:
            initial_measurements: Dictionary of initial measurement values
            final_measurements: Dictionary of final measurement values

        Returns:
            Dictionary with evaluation results
        """
        results = {
            'overall_pass': True,
            'criteria_results': {},
            'timestamp': datetime.utcnow().isoformat()
        }

        for criterion_name, criterion in self.pass_fail_criteria.items():
            if criterion.criterion_type == "percentage_retention":
                param = criterion.parameter
                initial = initial_measurements.get(param)
                final = final_measurements.get(param)

                if initial is None or final is None:
                    results['criteria_results'][criterion_name] = {
                        'pass': False,
                        'message': f"Missing measurement data for {param}",
                        'severity': criterion.severity
                    }
                    results['overall_pass'] = False
                else:
                    passes, message = criterion.evaluate(initial, final)
                    results['criteria_results'][criterion_name] = {
                        'pass': passes,
                        'message': message,
                        'severity': criterion.severity,
                        'initial_value': initial,
                        'final_value': final,
                        'retention_pct': (final / initial * 100) if initial != 0 else 0
                    }

                    if not passes and criterion.severity == 'critical':
                        results['overall_pass'] = False

        return results

    def to_dict(self) -> Dict[str, Any]:
        """Convert protocol to dictionary representation."""
        return self.definition
