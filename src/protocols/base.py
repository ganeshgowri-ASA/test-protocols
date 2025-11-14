"""
Base Protocol Classes for PV Testing Framework
Provides abstract base classes and common functionality for all test protocols.
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from enum import Enum


class ProtocolStatus(Enum):
    """Enumeration of protocol execution statuses."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MeasurementType(Enum):
    """Types of measurements supported."""
    ELECTROLUMINESCENCE = "electroluminescence"
    IV_CURVE = "iv_curve"
    VISUAL_INSPECTION = "visual_inspection"
    IR_THERMOGRAPHY = "infrared_thermography"
    SPECTRAL_RESPONSE = "spectral_response"


@dataclass
class ProtocolResult:
    """Container for protocol execution results."""
    protocol_id: str
    sample_id: str
    status: ProtocolStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    measurements: Dict[str, Any] = field(default_factory=dict)
    analysis_results: Dict[str, Any] = field(default_factory=dict)
    pass_fail: Optional[bool] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization."""
        return {
            "protocol_id": self.protocol_id,
            "sample_id": self.sample_id,
            "status": self.status.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "measurements": self.measurements,
            "analysis_results": self.analysis_results,
            "pass_fail": self.pass_fail,
            "errors": self.errors,
            "warnings": self.warnings,
            "metadata": self.metadata
        }


@dataclass
class SampleMetadata:
    """Metadata for test samples."""
    sample_id: str
    manufacturer: str
    cell_type: str
    cell_efficiency: float
    cell_area: float  # cm²
    manufacturing_date: str
    initial_pmax: float  # W
    initial_voc: float  # V
    initial_isc: float  # A
    initial_ff: float  # Fill factor (0-1)
    batch_number: Optional[str] = None
    wafer_type: Optional[str] = None
    texture_type: Optional[str] = None
    metallization_process: Optional[str] = None
    additional_info: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SampleMetadata':
        """Create SampleMetadata from dictionary."""
        known_fields = {
            'sample_id', 'manufacturer', 'cell_type', 'cell_efficiency',
            'cell_area', 'manufacturing_date', 'initial_pmax', 'initial_voc',
            'initial_isc', 'initial_ff', 'batch_number', 'wafer_type',
            'texture_type', 'metallization_process'
        }
        additional = {k: v for k, v in data.items() if k not in known_fields}

        return cls(
            sample_id=data['sample_id'],
            manufacturer=data['manufacturer'],
            cell_type=data['cell_type'],
            cell_efficiency=data['cell_efficiency'],
            cell_area=data['cell_area'],
            manufacturing_date=data['manufacturing_date'],
            initial_pmax=data['initial_pmax'],
            initial_voc=data['initial_voc'],
            initial_isc=data['initial_isc'],
            initial_ff=data['initial_ff'],
            batch_number=data.get('batch_number'),
            wafer_type=data.get('wafer_type'),
            texture_type=data.get('texture_type'),
            metallization_process=data.get('metallization_process'),
            additional_info=additional
        )


class ProtocolDefinition:
    """Container for protocol definition loaded from JSON."""

    def __init__(self, json_path: Union[str, Path]):
        """Load protocol definition from JSON file."""
        self.json_path = Path(json_path)
        with open(self.json_path, 'r') as f:
            self.data = json.load(f)

        # Parse key fields
        self.protocol_id = self.data['protocol_id']
        self.name = self.data['name']
        self.version = self.data['version']
        self.category = self.data['category']
        self.description = self.data['description']
        self.test_parameters = self.data.get('test_parameters', {})
        self.measurements = self.data.get('measurements', {})
        self.pass_fail_criteria = self.data.get('pass_fail_criteria', {})
        self.workflow = self.data.get('workflow', {})

    def get_parameter(self, param_name: str, default: Any = None) -> Any:
        """Get a test parameter by name."""
        param_def = self.test_parameters.get(param_name, {})
        return param_def.get('default', default)

    def validate_parameters(self, params: Dict[str, Any]) -> List[str]:
        """Validate provided parameters against protocol definition."""
        errors = []

        for param_name, param_value in params.items():
            if param_name not in self.test_parameters:
                errors.append(f"Unknown parameter: {param_name}")
                continue

            param_def = self.test_parameters[param_name]
            param_type = param_def.get('type')

            # Type checking
            if param_type == 'integer' and not isinstance(param_value, int):
                errors.append(f"{param_name} must be an integer")
            elif param_type == 'float' and not isinstance(param_value, (int, float)):
                errors.append(f"{param_name} must be a number")
            elif param_type == 'enum':
                options = param_def.get('options', [])
                if param_value not in options:
                    errors.append(f"{param_name} must be one of {options}")

            # Range checking
            if param_type in ['integer', 'float']:
                if 'min' in param_def and param_value < param_def['min']:
                    errors.append(f"{param_name} must be >= {param_def['min']}")
                if 'max' in param_def and param_value > param_def['max']:
                    errors.append(f"{param_name} must be <= {param_def['max']}")

        return errors


class BaseProtocol(ABC):
    """
    Abstract base class for all test protocols.

    All protocol implementations must inherit from this class and implement
    the required abstract methods.
    """

    def __init__(self, definition: ProtocolDefinition):
        """Initialize protocol with its definition."""
        self.definition = definition
        self.status = ProtocolStatus.PENDING
        self.current_step = 0
        self.results: List[ProtocolResult] = []

    @abstractmethod
    def validate_setup(self, samples: List[SampleMetadata],
                      parameters: Dict[str, Any]) -> List[str]:
        """
        Validate that all requirements are met before starting protocol.

        Args:
            samples: List of sample metadata
            parameters: Test parameters

        Returns:
            List of validation errors (empty if valid)
        """
        pass

    @abstractmethod
    def execute(self, samples: List[SampleMetadata],
                parameters: Dict[str, Any]) -> List[ProtocolResult]:
        """
        Execute the protocol for given samples.

        Args:
            samples: List of sample metadata
            parameters: Test parameters

        Returns:
            List of protocol results for each sample
        """
        pass

    @abstractmethod
    def analyze(self, measurements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze measurement data.

        Args:
            measurements: Raw measurement data

        Returns:
            Analysis results
        """
        pass

    @abstractmethod
    def evaluate_pass_fail(self, analysis_results: Dict[str, Any]) -> bool:
        """
        Evaluate pass/fail criteria.

        Args:
            analysis_results: Results from analyze()

        Returns:
            True if sample passes, False otherwise
        """
        pass

    def generate_report(self, results: List[ProtocolResult],
                       output_path: Path) -> None:
        """
        Generate test report.

        Args:
            results: List of protocol results
            output_path: Path to save report
        """
        # Default implementation - can be overridden
        report_data = {
            'protocol': self.definition.name,
            'protocol_id': self.definition.protocol_id,
            'version': self.definition.version,
            'timestamp': datetime.now().isoformat(),
            'results': [r.to_dict() for r in results]
        }

        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2)

    def get_status(self) -> ProtocolStatus:
        """Get current protocol status."""
        return self.status

    def pause(self) -> None:
        """Pause protocol execution."""
        if self.status == ProtocolStatus.IN_PROGRESS:
            self.status = ProtocolStatus.PAUSED

    def resume(self) -> None:
        """Resume paused protocol."""
        if self.status == ProtocolStatus.PAUSED:
            self.status = ProtocolStatus.IN_PROGRESS

    def cancel(self) -> None:
        """Cancel protocol execution."""
        self.status = ProtocolStatus.CANCELLED


class ProtocolRegistry:
    """Registry for managing available protocols."""

    def __init__(self):
        self._protocols: Dict[str, type] = {}

    def register(self, protocol_id: str, protocol_class: type) -> None:
        """Register a protocol class."""
        if not issubclass(protocol_class, BaseProtocol):
            raise ValueError("Protocol class must inherit from BaseProtocol")
        self._protocols[protocol_id] = protocol_class

    def get(self, protocol_id: str) -> Optional[type]:
        """Get protocol class by ID."""
        return self._protocols.get(protocol_id)

    def list_protocols(self) -> List[str]:
        """List all registered protocol IDs."""
        return list(self._protocols.keys())


# Global protocol registry
protocol_registry = ProtocolRegistry()
