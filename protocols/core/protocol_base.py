"""Base class for all test protocols"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class ProtocolBase(ABC):
    """
    Abstract base class for all test protocols.

    Provides common functionality for protocol execution, validation,
    and result management.
    """

    def __init__(self, protocol_definition: Dict[str, Any]):
        """
        Initialize protocol with its JSON definition.

        Args:
            protocol_definition: Dictionary containing protocol specification
        """
        self.definition = protocol_definition
        self.protocol_id = protocol_definition.get("protocol_id", "UNKNOWN")
        self.version = protocol_definition.get("version", "0.0.0")
        self.name = protocol_definition.get("name", "Unnamed Protocol")

        # Execution state
        self.test_execution_id: Optional[str] = None
        self.sample_info: Dict[str, Any] = {}
        self.test_conditions: Dict[str, Any] = {}
        self.measurements: List[Dict[str, Any]] = []
        self.calculated_results: Dict[str, Any] = {}
        self.pass_fail_assessment: Dict[str, Any] = {}
        self.qc_verification: Dict[str, Any] = {}

        # Timestamps
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

        logger.info(f"Initialized protocol: {self.protocol_id} v{self.version}")

    def generate_execution_id(self) -> str:
        """
        Generate a unique test execution identifier.

        Returns:
            Unique execution ID in format PROTOCOL-YYYYMMDD-HHMMSS
        """
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        return f"{self.protocol_id}-{timestamp}"

    def start_test(self, sample_info: Dict[str, Any], test_conditions: Dict[str, Any]) -> str:
        """
        Initialize a new test execution.

        Args:
            sample_info: Information about the test sample
            test_conditions: Environmental and test conditions

        Returns:
            Test execution ID
        """
        self.test_execution_id = self.generate_execution_id()
        self.sample_info = sample_info
        self.test_conditions = test_conditions
        self.start_time = datetime.now()
        self.measurements = []
        self.calculated_results = {}

        logger.info(f"Started test execution: {self.test_execution_id}")
        return self.test_execution_id

    def add_measurement(self, measurement: Dict[str, Any]) -> None:
        """
        Add a measurement to the test results.

        Args:
            measurement: Measurement data dictionary
        """
        measurement["measurement_timestamp"] = datetime.now().isoformat()
        self.measurements.append(measurement)
        logger.debug(f"Added measurement: {measurement.get('location_id', 'unknown')}")

    @abstractmethod
    def calculate_results(self) -> Dict[str, Any]:
        """
        Calculate derived metrics from measurements.

        Must be implemented by specific protocol classes.

        Returns:
            Dictionary of calculated results
        """
        pass

    @abstractmethod
    def evaluate_pass_fail(self) -> Dict[str, Any]:
        """
        Evaluate pass/fail criteria based on results.

        Must be implemented by specific protocol classes.

        Returns:
            Dictionary containing pass/fail assessment
        """
        pass

    def complete_test(self) -> Dict[str, Any]:
        """
        Complete the test execution and generate final results.

        Returns:
            Complete test results dictionary
        """
        self.end_time = datetime.now()

        # Calculate results
        self.calculated_results = self.calculate_results()

        # Evaluate pass/fail
        self.pass_fail_assessment = self.evaluate_pass_fail()

        logger.info(f"Completed test execution: {self.test_execution_id}")

        return self.get_full_results()

    def get_full_results(self) -> Dict[str, Any]:
        """
        Get complete test results in standardized format.

        Returns:
            Complete results dictionary
        """
        return {
            "test_execution_id": self.test_execution_id,
            "protocol_id": self.protocol_id,
            "protocol_version": self.version,
            "sample_info": self.sample_info,
            "test_conditions": self.test_conditions,
            "measurements": self.measurements,
            "calculated_results": self.calculated_results,
            "pass_fail_assessment": self.pass_fail_assessment,
            "qc_verification": self.qc_verification,
            "metadata": {
                "created_timestamp": self.start_time.isoformat() if self.start_time else None,
                "completed_timestamp": self.end_time.isoformat() if self.end_time else None,
                "duration_minutes": (
                    (self.end_time - self.start_time).total_seconds() / 60
                    if self.start_time and self.end_time
                    else None
                ),
            },
        }

    def export_to_json(self, file_path: str) -> None:
        """
        Export test results to JSON file.

        Args:
            file_path: Path to output JSON file
        """
        results = self.get_full_results()
        with open(file_path, "w") as f:
            json.dump(results, f, indent=2)
        logger.info(f"Exported results to: {file_path}")

    def get_test_steps(self) -> List[Dict[str, Any]]:
        """
        Get list of test steps from protocol definition.

        Returns:
            List of test step dictionaries
        """
        return self.definition.get("test_steps", [])

    def get_parameter_spec(self, parameter_path: str) -> Optional[Dict[str, Any]]:
        """
        Get specification for a specific parameter.

        Args:
            parameter_path: Dot-notation path to parameter (e.g., 'sample_parameters.sample_id')

        Returns:
            Parameter specification dictionary or None
        """
        path_parts = parameter_path.split(".")
        spec = self.definition.get("test_parameters", {})

        for part in path_parts:
            if part in spec:
                spec = spec[part]
            else:
                return None

        return spec

    def validate_parameter(self, parameter_path: str, value: Any) -> bool:
        """
        Validate a parameter value against its specification.

        Args:
            parameter_path: Dot-notation path to parameter
            value: Value to validate

        Returns:
            True if valid, False otherwise
        """
        spec = self.get_parameter_spec(parameter_path)
        if not spec:
            logger.warning(f"No specification found for parameter: {parameter_path}")
            return False

        param_type = spec.get("type")

        # Type validation
        if param_type == "number":
            if not isinstance(value, (int, float)):
                return False

            # Range validation
            if "range" in spec:
                if value < spec["range"].get("min", float("-inf")):
                    return False
                if value > spec["range"].get("max", float("inf")):
                    return False

        elif param_type == "string":
            if not isinstance(value, str):
                return False

            # Enum validation
            if "enum" in spec and value not in spec["enum"]:
                return False

            # Pattern validation
            if "pattern" in spec:
                import re
                if not re.match(spec["pattern"], value):
                    return False

        elif param_type == "integer":
            if not isinstance(value, int):
                return False

            # Range validation
            if "range" in spec:
                if value < spec["range"].get("min", float("-inf")):
                    return False
                if value > spec["range"].get("max", float("inf")):
                    return False

        return True
