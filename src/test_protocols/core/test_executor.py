"""
Test execution engine.

This module handles the execution of test protocols, data collection,
and real-time monitoring.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any, Callable
from enum import Enum

from .protocol import Protocol, TestStep


class TestStatus(Enum):
    """Test run status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


class StepStatus(Enum):
    """Individual step status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class MeasurementData:
    """Single measurement data point."""
    measurement_id: str
    test_run_id: str
    step_id: str
    measurement_type: str
    value: float
    unit: str
    timestamp: datetime
    sensor_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def generate_id() -> str:
        """Generate unique measurement ID."""
        return str(uuid.uuid4())


@dataclass
class StepResult:
    """Result from executing a test step."""
    step_id: str
    status: StepStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    measurements: List[MeasurementData] = field(default_factory=list)
    passed: Optional[bool] = None
    notes: str = ""
    errors: List[str] = field(default_factory=list)

    def duration_minutes(self) -> Optional[float]:
        """Calculate step duration in minutes."""
        if self.end_time and self.start_time:
            delta = self.end_time - self.start_time
            return delta.total_seconds() / 60
        return None


@dataclass
class TestRun:
    """
    Test run instance.

    Represents a single execution of a protocol with all collected data
    and results.
    """
    test_run_id: str
    protocol_id: str
    protocol_version: str
    sample_id: str
    operator_id: str
    status: TestStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    current_step: Optional[str] = None
    step_results: List[StepResult] = field(default_factory=list)
    notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def generate_id(protocol_id: str) -> str:
        """Generate unique test run ID."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        random_suffix = str(uuid.uuid4())[:8].upper()
        return f"{protocol_id}-{timestamp}-{random_suffix}"

    def duration_minutes(self) -> Optional[float]:
        """Calculate total test run duration in minutes."""
        if self.end_time and self.start_time:
            delta = self.end_time - self.start_time
            return delta.total_seconds() / 60
        return None

    def get_step_result(self, step_id: str) -> Optional[StepResult]:
        """Get result for a specific step."""
        for result in self.step_results:
            if result.step_id == step_id:
                return result
        return None

    def add_measurement(
        self,
        step_id: str,
        measurement_type: str,
        value: float,
        unit: str,
        sensor_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> MeasurementData:
        """Add a measurement to the current step."""
        measurement = MeasurementData(
            measurement_id=MeasurementData.generate_id(),
            test_run_id=self.test_run_id,
            step_id=step_id,
            measurement_type=measurement_type,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            sensor_id=sensor_id,
            metadata=metadata or {}
        )

        # Add to step result
        step_result = self.get_step_result(step_id)
        if step_result:
            step_result.measurements.append(measurement)

        return measurement


class TestExecutor:
    """
    Test execution engine.

    Manages the execution of test protocols, handles data collection,
    and monitors test progress.
    """

    def __init__(self, protocol: Protocol):
        """
        Initialize test executor.

        Args:
            protocol: Protocol to execute
        """
        self.protocol = protocol
        self.current_run: Optional[TestRun] = None
        self.measurement_callbacks: List[Callable] = []
        self.step_callbacks: List[Callable] = []

    def create_test_run(
        self,
        sample_id: str,
        operator_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TestRun:
        """
        Create a new test run.

        Args:
            sample_id: Identifier for the sample being tested
            operator_id: Identifier for the test operator
            metadata: Additional metadata for the test run

        Returns:
            New TestRun object
        """
        test_run = TestRun(
            test_run_id=TestRun.generate_id(self.protocol.protocol_id),
            protocol_id=self.protocol.protocol_id,
            protocol_version=self.protocol.version,
            sample_id=sample_id,
            operator_id=operator_id,
            status=TestStatus.PENDING,
            start_time=datetime.now(),
            metadata=metadata or {}
        )

        # Initialize step results
        for step in self.protocol.tests:
            step_result = StepResult(
                step_id=step.step_id,
                status=StepStatus.PENDING,
                start_time=datetime.now()
            )
            test_run.step_results.append(step_result)

        self.current_run = test_run
        return test_run

    def start_test(self) -> None:
        """Start the test execution."""
        if not self.current_run:
            raise RuntimeError("No test run created. Call create_test_run first.")

        self.current_run.status = TestStatus.IN_PROGRESS
        self.current_run.start_time = datetime.now()

    def start_step(self, step_id: str) -> StepResult:
        """
        Start executing a test step.

        Args:
            step_id: Step identifier

        Returns:
            StepResult object for the step
        """
        if not self.current_run:
            raise RuntimeError("No active test run")

        step_result = self.current_run.get_step_result(step_id)
        if not step_result:
            raise ValueError(f"Step {step_id} not found in test run")

        step_result.status = StepStatus.IN_PROGRESS
        step_result.start_time = datetime.now()
        self.current_run.current_step = step_id

        # Notify callbacks
        for callback in self.step_callbacks:
            callback(step_id, "started")

        return step_result

    def complete_step(
        self,
        step_id: str,
        passed: bool,
        notes: str = ""
    ) -> StepResult:
        """
        Mark a test step as completed.

        Args:
            step_id: Step identifier
            passed: Whether the step passed acceptance criteria
            notes: Additional notes about the step

        Returns:
            Updated StepResult object
        """
        if not self.current_run:
            raise RuntimeError("No active test run")

        step_result = self.current_run.get_step_result(step_id)
        if not step_result:
            raise ValueError(f"Step {step_id} not found in test run")

        step_result.status = StepStatus.COMPLETED
        step_result.end_time = datetime.now()
        step_result.passed = passed
        step_result.notes = notes

        # Notify callbacks
        for callback in self.step_callbacks:
            callback(step_id, "completed")

        return step_result

    def fail_step(self, step_id: str, error: str) -> StepResult:
        """
        Mark a test step as failed.

        Args:
            step_id: Step identifier
            error: Error message

        Returns:
            Updated StepResult object
        """
        if not self.current_run:
            raise RuntimeError("No active test run")

        step_result = self.current_run.get_step_result(step_id)
        if not step_result:
            raise ValueError(f"Step {step_id} not found in test run")

        step_result.status = StepStatus.FAILED
        step_result.end_time = datetime.now()
        step_result.passed = False
        step_result.errors.append(error)

        return step_result

    def record_measurement(
        self,
        step_id: str,
        measurement_type: str,
        value: float,
        unit: str,
        sensor_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> MeasurementData:
        """
        Record a measurement during test execution.

        Args:
            step_id: Step identifier
            measurement_type: Type of measurement
            value: Measured value
            unit: Unit of measurement
            sensor_id: Sensor/instrument identifier
            metadata: Additional metadata

        Returns:
            MeasurementData object
        """
        if not self.current_run:
            raise RuntimeError("No active test run")

        measurement = self.current_run.add_measurement(
            step_id=step_id,
            measurement_type=measurement_type,
            value=value,
            unit=unit,
            sensor_id=sensor_id,
            metadata=metadata
        )

        # Notify callbacks
        for callback in self.measurement_callbacks:
            callback(measurement)

        return measurement

    def complete_test(self, notes: str = "") -> TestRun:
        """
        Complete the test execution.

        Args:
            notes: Final notes about the test

        Returns:
            Completed TestRun object
        """
        if not self.current_run:
            raise RuntimeError("No active test run")

        self.current_run.status = TestStatus.COMPLETED
        self.current_run.end_time = datetime.now()
        self.current_run.notes = notes

        return self.current_run

    def abort_test(self, reason: str) -> TestRun:
        """
        Abort the test execution.

        Args:
            reason: Reason for aborting

        Returns:
            Aborted TestRun object
        """
        if not self.current_run:
            raise RuntimeError("No active test run")

        self.current_run.status = TestStatus.ABORTED
        self.current_run.end_time = datetime.now()
        self.current_run.notes = f"Aborted: {reason}"

        return self.current_run

    def pause_test(self) -> None:
        """Pause the test execution."""
        if not self.current_run:
            raise RuntimeError("No active test run")

        self.current_run.status = TestStatus.PAUSED

    def resume_test(self) -> None:
        """Resume the test execution."""
        if not self.current_run:
            raise RuntimeError("No active test run")

        self.current_run.status = TestStatus.IN_PROGRESS

    def register_measurement_callback(self, callback: Callable) -> None:
        """
        Register a callback for measurement events.

        Args:
            callback: Function to call when measurements are recorded
        """
        self.measurement_callbacks.append(callback)

    def register_step_callback(self, callback: Callable) -> None:
        """
        Register a callback for step events.

        Args:
            callback: Function to call when step status changes
        """
        self.step_callbacks.append(callback)

    def get_progress(self) -> Dict[str, Any]:
        """
        Get current test progress.

        Returns:
            Dictionary with progress information
        """
        if not self.current_run:
            return {"status": "no_active_run"}

        total_steps = len(self.protocol.tests)
        completed_steps = sum(
            1 for result in self.current_run.step_results
            if result.status in [StepStatus.COMPLETED, StepStatus.FAILED]
        )

        return {
            "test_run_id": self.current_run.test_run_id,
            "status": self.current_run.status.value,
            "current_step": self.current_run.current_step,
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "progress_percent": (completed_steps / total_steps * 100) if total_steps > 0 else 0,
            "duration_minutes": self.current_run.duration_minutes(),
        }
