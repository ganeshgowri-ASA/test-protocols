"""
Base Protocol Classes
Core classes for protocol definition and execution
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ProtocolStatus(Enum):
    """Protocol execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


class TestPhase(Enum):
    """Test execution phases"""
    PRE_TEST = "pre_test"
    PREPARATION = "preparation"
    RUNNING = "running"
    INTERIM_TEST = "interim_test"
    POST_TEST = "post_test"
    RECOVERY = "recovery"
    FINAL_TEST = "final_test"


@dataclass
class ProtocolMetadata:
    """Protocol metadata information"""
    id: str
    protocol_number: str
    name: str
    category: str
    subcategory: str
    version: str
    description: str
    standard_references: List[str] = field(default_factory=list)
    author: str = ""
    created_date: Optional[str] = None
    last_modified: Optional[str] = None
    status: str = "active"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProtocolMetadata':
        """Create metadata from dictionary"""
        return cls(**data)


@dataclass
class TestParameter:
    """Test parameter definition"""
    name: str
    type: str
    description: str
    default: Any
    unit: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    validation: str = "optional"
    tolerance: Optional[float] = None

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> 'TestParameter':
        """Create parameter from dictionary"""
        return cls(
            name=name,
            type=data.get("type", "number"),
            description=data.get("description", ""),
            default=data.get("default"),
            unit=data.get("unit", ""),
            min_value=data.get("min"),
            max_value=data.get("max"),
            validation=data.get("validation", "optional"),
            tolerance=data.get("tolerance")
        )

    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        """Validate parameter value"""
        if self.validation == "required" and value is None:
            return False, f"{self.name} is required"

        if value is None:
            return True, None

        # Type validation
        if self.type == "number":
            try:
                value = float(value)
            except (TypeError, ValueError):
                return False, f"{self.name} must be a number"
        elif self.type == "integer":
            try:
                value = int(value)
            except (TypeError, ValueError):
                return False, f"{self.name} must be an integer"

        # Range validation
        if self.min_value is not None and value < self.min_value:
            return False, f"{self.name} must be >= {self.min_value}"
        if self.max_value is not None and value > self.max_value:
            return False, f"{self.name} must be <= {self.max_value}"

        return True, None


class BaseProtocol(ABC):
    """Base class for all test protocols"""

    def __init__(self, protocol_file: Union[str, Path]):
        """
        Initialize protocol from JSON file

        Args:
            protocol_file: Path to protocol JSON file
        """
        self.protocol_file = Path(protocol_file)
        self.protocol_data: Dict[str, Any] = {}
        self.metadata: Optional[ProtocolMetadata] = None
        self.parameters: Dict[str, TestParameter] = {}
        self.status = ProtocolStatus.PENDING
        self.current_phase = TestPhase.PRE_TEST
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.test_run_id: Optional[str] = None

        self._load_protocol()
        self._parse_metadata()
        self._parse_parameters()

    def _load_protocol(self) -> None:
        """Load protocol from JSON file"""
        try:
            with open(self.protocol_file, 'r') as f:
                self.protocol_data = json.load(f)
            logger.info(f"Loaded protocol from {self.protocol_file}")
        except Exception as e:
            logger.error(f"Failed to load protocol: {e}")
            raise

    def _parse_metadata(self) -> None:
        """Parse protocol metadata"""
        metadata_dict = self.protocol_data.get("metadata", {})
        self.metadata = ProtocolMetadata.from_dict(metadata_dict)

    def _parse_parameters(self) -> None:
        """Parse test parameters"""
        params_dict = self.protocol_data.get("test_parameters", {})
        for param_name, param_data in params_dict.items():
            self.parameters[param_name] = TestParameter.from_dict(param_name, param_data)

    def validate_parameters(self, values: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate test parameter values

        Args:
            values: Dictionary of parameter values

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        for param_name, parameter in self.parameters.items():
            value = values.get(param_name)
            is_valid, error_msg = parameter.validate(value)
            if not is_valid and error_msg:
                errors.append(error_msg)

        return len(errors) == 0, errors

    def get_parameter_defaults(self) -> Dict[str, Any]:
        """Get default values for all parameters"""
        return {name: param.default for name, param in self.parameters.items()}

    def get_test_procedure(self) -> Dict[str, Any]:
        """Get test procedure definition"""
        return self.protocol_data.get("test_procedure", {})

    def get_qc_checks(self) -> List[Dict[str, Any]]:
        """Get QC check definitions"""
        return self.protocol_data.get("qc_checks", [])

    def get_pass_fail_criteria(self) -> Dict[str, Any]:
        """Get pass/fail criteria"""
        return self.protocol_data.get("pass_fail_criteria", {})

    def get_data_collection_config(self) -> Dict[str, Any]:
        """Get data collection configuration"""
        return self.protocol_data.get("data_collection", {})

    @abstractmethod
    def execute(self, parameters: Dict[str, Any]) -> bool:
        """
        Execute the protocol

        Args:
            parameters: Test parameter values

        Returns:
            True if execution successful, False otherwise
        """
        pass

    @abstractmethod
    def collect_data(self, data_point: Dict[str, Any]) -> None:
        """
        Collect a data point

        Args:
            data_point: Data to collect
        """
        pass

    @abstractmethod
    def run_qc_checks(self) -> Dict[str, bool]:
        """
        Run QC checks

        Returns:
            Dictionary of check results
        """
        pass

    @abstractmethod
    def generate_report(self) -> Dict[str, Any]:
        """
        Generate test report

        Returns:
            Report data
        """
        pass

    def start(self) -> None:
        """Mark protocol execution as started"""
        self.status = ProtocolStatus.RUNNING
        self.start_time = datetime.utcnow()
        logger.info(f"Protocol {self.metadata.id} started at {self.start_time}")

    def complete(self) -> None:
        """Mark protocol execution as completed"""
        self.status = ProtocolStatus.COMPLETED
        self.end_time = datetime.utcnow()
        logger.info(f"Protocol {self.metadata.id} completed at {self.end_time}")

    def fail(self, reason: str) -> None:
        """Mark protocol execution as failed"""
        self.status = ProtocolStatus.FAILED
        self.end_time = datetime.utcnow()
        logger.error(f"Protocol {self.metadata.id} failed: {reason}")

    def abort(self, reason: str) -> None:
        """Abort protocol execution"""
        self.status = ProtocolStatus.ABORTED
        self.end_time = datetime.utcnow()
        logger.warning(f"Protocol {self.metadata.id} aborted: {reason}")

    def pause(self) -> None:
        """Pause protocol execution"""
        self.status = ProtocolStatus.PAUSED
        logger.info(f"Protocol {self.metadata.id} paused")

    def resume(self) -> None:
        """Resume protocol execution"""
        self.status = ProtocolStatus.RUNNING
        logger.info(f"Protocol {self.metadata.id} resumed")

    def __repr__(self) -> str:
        """String representation"""
        if self.metadata:
            return f"<Protocol {self.metadata.id}: {self.metadata.name}>"
        return f"<Protocol: {self.protocol_file}>"
