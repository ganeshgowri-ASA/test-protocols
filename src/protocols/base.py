"""Base protocol classes and interfaces."""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ProtocolStep:
    """Represents a single step in a test protocol."""

    step_number: int
    name: str
    description: str
    duration: int
    duration_unit: str
    inputs: List[Dict[str, Any]]
    measurements: List[Dict[str, Any]]
    acceptance_criteria: List[Dict[str, Any]]
    completed: bool = False
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    results: Dict[str, Any] = field(default_factory=dict)

    def validate_measurements(self) -> tuple[bool, List[str]]:
        """
        Validate that all required measurements have been recorded.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        for measurement in self.measurements:
            if measurement.get("required", False):
                name = measurement["name"]
                if name not in self.results:
                    errors.append(f"Required measurement '{name}' is missing")

        return len(errors) == 0, errors

    def check_acceptance_criteria(self) -> tuple[bool, List[str]]:
        """
        Check if all acceptance criteria are met.

        Returns:
            Tuple of (all_passed, list_of_failures)
        """
        failures = []
        for criterion in self.acceptance_criteria:
            parameter = criterion["parameter"]
            condition = criterion["condition"]
            expected_value = criterion["value"]

            if parameter not in self.results:
                failures.append(f"Parameter '{parameter}' not found in results")
                continue

            actual_value = self.results[parameter]
            passed = self._evaluate_condition(actual_value, condition, expected_value)

            if not passed:
                failures.append(
                    f"{parameter}: expected {condition} {expected_value}, got {actual_value}"
                )

        return len(failures) == 0, failures

    def _evaluate_condition(self, actual: Any, condition: str, expected: Any) -> bool:
        """Evaluate a single acceptance criterion."""
        if condition == "equals":
            return actual == expected
        elif condition == "less_than":
            return actual < expected
        elif condition == "less_than_or_equal":
            return actual <= expected
        elif condition == "greater_than":
            return actual > expected
        elif condition == "greater_than_or_equal":
            return actual >= expected
        elif condition == "not_equals":
            return actual != expected
        else:
            raise ValueError(f"Unknown condition: {condition}")


@dataclass
class ProtocolResult:
    """Represents the overall result of a protocol execution."""

    protocol_id: str
    test_id: str
    module_serial_number: str
    operator: str
    test_date: datetime
    overall_result: str  # "Pass", "Fail", "In Progress"
    step_results: List[Dict[str, Any]] = field(default_factory=list)
    qc_checks: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization."""
        return {
            "protocol_id": self.protocol_id,
            "test_id": self.test_id,
            "module_serial_number": self.module_serial_number,
            "operator": self.operator,
            "test_date": self.test_date.isoformat(),
            "overall_result": self.overall_result,
            "step_results": self.step_results,
            "qc_checks": self.qc_checks,
            "metadata": self.metadata,
        }


class BaseProtocol(ABC):
    """Abstract base class for all test protocols."""

    def __init__(self, protocol_file: Path):
        """
        Initialize protocol from JSON file.

        Args:
            protocol_file: Path to the protocol JSON definition
        """
        with open(protocol_file, "r") as f:
            self.protocol_data = json.load(f)

        self.protocol_id = self.protocol_data["protocol_id"]
        self.version = self.protocol_data["version"]
        self.title = self.protocol_data["title"]
        self.category = self.protocol_data["category"]
        self.description = self.protocol_data["description"]

        self.steps: List[ProtocolStep] = []
        self._initialize_steps()

        self.current_step_index = 0
        self.test_id: Optional[str] = None
        self.module_serial_number: Optional[str] = None
        self.operator: Optional[str] = None
        self.start_time: Optional[datetime] = None

    def _initialize_steps(self):
        """Initialize protocol steps from JSON data."""
        for step_data in self.protocol_data["test_steps"]:
            step = ProtocolStep(
                step_number=step_data["step_number"],
                name=step_data["name"],
                description=step_data["description"],
                duration=step_data["duration"],
                duration_unit=step_data["duration_unit"],
                inputs=step_data.get("inputs", []),
                measurements=step_data["measurements"],
                acceptance_criteria=step_data["acceptance_criteria"],
            )
            self.steps.append(step)

    def start_test(self, test_id: str, module_serial_number: str, operator: str):
        """
        Start a new test execution.

        Args:
            test_id: Unique identifier for this test execution
            module_serial_number: Serial number of the module being tested
            operator: Name of the test operator
        """
        self.test_id = test_id
        self.module_serial_number = module_serial_number
        self.operator = operator
        self.start_time = datetime.now()
        self.current_step_index = 0

    def get_current_step(self) -> Optional[ProtocolStep]:
        """Get the current active step."""
        if 0 <= self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None

    def record_measurement(self, measurement_name: str, value: Any):
        """
        Record a measurement for the current step.

        Args:
            measurement_name: Name of the measurement
            value: Measured value
        """
        current_step = self.get_current_step()
        if current_step:
            current_step.results[measurement_name] = value

    def complete_current_step(self) -> tuple[bool, List[str]]:
        """
        Complete the current step and move to the next.

        Returns:
            Tuple of (success, list_of_errors)
        """
        current_step = self.get_current_step()
        if not current_step:
            return False, ["No current step to complete"]

        # Validate measurements
        valid, errors = current_step.validate_measurements()
        if not valid:
            return False, errors

        # Check acceptance criteria
        passed, failures = current_step.check_acceptance_criteria()

        current_step.completed = True
        current_step.end_time = datetime.now()

        if passed:
            self.current_step_index += 1

        return passed, failures

    def is_complete(self) -> bool:
        """Check if all steps are completed."""
        return all(step.completed for step in self.steps)

    def get_overall_result(self) -> str:
        """Determine overall test result."""
        if not self.is_complete():
            return "In Progress"

        # Check if all steps passed their acceptance criteria
        for step in self.steps:
            passed, _ = step.check_acceptance_criteria()
            if not passed:
                return "Fail"

        return "Pass"

    def generate_result(self) -> ProtocolResult:
        """Generate a complete test result."""
        step_results = []
        for step in self.steps:
            passed, failures = step.check_acceptance_criteria()
            step_results.append(
                {
                    "step_number": step.step_number,
                    "name": step.name,
                    "completed": step.completed,
                    "passed": passed,
                    "results": step.results,
                    "failures": failures,
                }
            )

        return ProtocolResult(
            protocol_id=self.protocol_id,
            test_id=self.test_id or "",
            module_serial_number=self.module_serial_number or "",
            operator=self.operator or "",
            test_date=self.start_time or datetime.now(),
            overall_result=self.get_overall_result(),
            step_results=step_results,
            metadata={
                "protocol_version": self.version,
                "protocol_title": self.title,
                "category": self.category,
            },
        )

    @abstractmethod
    def calculate_derived_values(self, step: ProtocolStep):
        """
        Calculate any derived values for a step.
        This should be implemented by specific protocol classes.

        Args:
            step: The protocol step to calculate values for
        """
        pass

    def get_test_equipment(self) -> List[Dict[str, Any]]:
        """Get list of required test equipment."""
        return self.protocol_data.get("test_equipment", [])

    def get_test_conditions(self) -> Dict[str, Any]:
        """Get required test conditions."""
        return self.protocol_data.get("test_conditions", {})

    def get_qc_checks(self) -> List[Dict[str, Any]]:
        """Get QC check requirements."""
        return self.protocol_data.get("qc_checks", [])
