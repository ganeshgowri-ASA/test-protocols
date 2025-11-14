"""
Test Runner Module

Manages execution of test protocols and data collection.
"""

from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum
import json
from pathlib import Path


class TestStatus(Enum):
    """Test execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class PhaseStatus(Enum):
    """Test phase status."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TestRun:
    """Represents a single test run execution."""

    def __init__(self, protocol: Dict[str, Any], test_run_id: str,
                 operator: str, sample_id: str):
        """
        Initialize a test run.

        Args:
            protocol: Protocol definition dictionary
            test_run_id: Unique identifier for this test run
            operator: Name of the test operator
            sample_id: Identifier for the sample being tested
        """
        self.protocol = protocol
        self.test_run_id = test_run_id
        self.operator = operator
        self.sample_id = sample_id
        self.status = TestStatus.PENDING
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.current_phase: Optional[str] = None
        self.current_step: Optional[str] = None
        self.phase_results: Dict[str, Dict] = {}
        self.measurements: List[Dict] = []
        self.notes: List[Dict] = []
        self.qc_results: Dict[str, Any] = {}

    def start(self) -> None:
        """Start the test run."""
        self.status = TestStatus.IN_PROGRESS
        self.start_time = datetime.now()

    def complete(self) -> None:
        """Mark the test run as completed."""
        self.status = TestStatus.COMPLETED
        self.end_time = datetime.now()

    def fail(self, reason: str) -> None:
        """Mark the test run as failed."""
        self.status = TestStatus.FAILED
        self.end_time = datetime.now()
        self.add_note(f"Test failed: {reason}", "error")

    def add_measurement(self, measurement_id: str, value: float,
                       unit: str, timestamp: Optional[datetime] = None,
                       metadata: Optional[Dict] = None) -> None:
        """
        Add a measurement to the test run.

        Args:
            measurement_id: ID of the measurement type
            value: Measured value
            unit: Unit of measurement
            timestamp: Time of measurement (default: now)
            metadata: Additional metadata
        """
        measurement = {
            'measurement_id': measurement_id,
            'value': value,
            'unit': unit,
            'timestamp': timestamp or datetime.now(),
            'phase': self.current_phase,
            'step': self.current_step,
            'metadata': metadata or {}
        }
        self.measurements.append(measurement)

    def add_note(self, note: str, category: str = "general") -> None:
        """
        Add a note to the test run.

        Args:
            note: Note text
            category: Note category (general, warning, error, info)
        """
        self.notes.append({
            'timestamp': datetime.now(),
            'category': category,
            'note': note,
            'phase': self.current_phase,
            'step': self.current_step
        })

    def set_phase(self, phase_id: str, status: PhaseStatus) -> None:
        """
        Set the status of a test phase.

        Args:
            phase_id: Phase identifier
            status: Phase status
        """
        if phase_id not in self.phase_results:
            self.phase_results[phase_id] = {
                'phase_id': phase_id,
                'status': status.value,
                'start_time': None,
                'end_time': None,
                'steps': {}
            }
        else:
            self.phase_results[phase_id]['status'] = status.value

        if status == PhaseStatus.IN_PROGRESS:
            self.phase_results[phase_id]['start_time'] = datetime.now()
            self.current_phase = phase_id
        elif status in [PhaseStatus.COMPLETED, PhaseStatus.FAILED, PhaseStatus.SKIPPED]:
            self.phase_results[phase_id]['end_time'] = datetime.now()

    def set_step(self, phase_id: str, step_id: str, status: str,
                 result: Optional[Dict] = None) -> None:
        """
        Set the status and result of a test step.

        Args:
            phase_id: Phase identifier
            step_id: Step identifier
            status: Step status
            result: Step result data
        """
        if phase_id not in self.phase_results:
            self.set_phase(phase_id, PhaseStatus.IN_PROGRESS)

        self.phase_results[phase_id]['steps'][step_id] = {
            'step_id': step_id,
            'status': status,
            'timestamp': datetime.now(),
            'result': result or {}
        }
        self.current_step = step_id

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the test run.

        Returns:
            Dictionary containing test run summary
        """
        return {
            'test_run_id': self.test_run_id,
            'protocol_id': self.protocol['protocol_id'],
            'protocol_name': self.protocol['name'],
            'sample_id': self.sample_id,
            'operator': self.operator,
            'status': self.status.value,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration_hours': (
                (self.end_time - self.start_time).total_seconds() / 3600
                if self.start_time and self.end_time else None
            ),
            'phases_completed': sum(
                1 for p in self.phase_results.values()
                if p['status'] == PhaseStatus.COMPLETED.value
            ),
            'total_phases': len(self.protocol['test_phases']),
            'measurements_count': len(self.measurements),
            'notes_count': len(self.notes),
            'qc_pass': self.qc_results.get('overall_pass', None)
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert test run to dictionary for serialization.

        Returns:
            Dictionary representation of test run
        """
        def serialize_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return obj

        return {
            'test_run_id': self.test_run_id,
            'protocol': self.protocol,
            'sample_id': self.sample_id,
            'operator': self.operator,
            'status': self.status.value,
            'start_time': serialize_datetime(self.start_time),
            'end_time': serialize_datetime(self.end_time),
            'current_phase': self.current_phase,
            'current_step': self.current_step,
            'phase_results': {
                k: {
                    **v,
                    'start_time': serialize_datetime(v.get('start_time')),
                    'end_time': serialize_datetime(v.get('end_time'))
                }
                for k, v in self.phase_results.items()
            },
            'measurements': [
                {**m, 'timestamp': serialize_datetime(m['timestamp'])}
                for m in self.measurements
            ],
            'notes': [
                {**n, 'timestamp': serialize_datetime(n['timestamp'])}
                for n in self.notes
            ],
            'qc_results': self.qc_results
        }

    def save(self, output_dir: str = "test_runs") -> str:
        """
        Save test run to JSON file.

        Args:
            output_dir: Directory to save test run data

        Returns:
            Path to saved file
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        filename = f"{self.test_run_id}_{self.sample_id}.json"
        filepath = output_path / filename

        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2, default=str)

        return str(filepath)


class TestRunner:
    """Manages test protocol execution."""

    def __init__(self):
        """Initialize the test runner."""
        self.active_runs: Dict[str, TestRun] = {}
        self.callbacks: Dict[str, List[Callable]] = {
            'on_test_start': [],
            'on_test_complete': [],
            'on_phase_start': [],
            'on_phase_complete': [],
            'on_measurement': []
        }

    def create_test_run(self, protocol: Dict[str, Any], test_run_id: str,
                       operator: str, sample_id: str) -> TestRun:
        """
        Create a new test run.

        Args:
            protocol: Protocol definition
            test_run_id: Unique test run identifier
            operator: Test operator name
            sample_id: Sample identifier

        Returns:
            TestRun instance
        """
        test_run = TestRun(protocol, test_run_id, operator, sample_id)
        self.active_runs[test_run_id] = test_run
        return test_run

    def start_test_run(self, test_run_id: str) -> None:
        """
        Start a test run.

        Args:
            test_run_id: Test run identifier
        """
        test_run = self.active_runs.get(test_run_id)
        if not test_run:
            raise ValueError(f"Test run {test_run_id} not found")

        test_run.start()
        self._trigger_callbacks('on_test_start', test_run)

    def complete_test_run(self, test_run_id: str) -> None:
        """
        Complete a test run.

        Args:
            test_run_id: Test run identifier
        """
        test_run = self.active_runs.get(test_run_id)
        if not test_run:
            raise ValueError(f"Test run {test_run_id} not found")

        test_run.complete()
        self._trigger_callbacks('on_test_complete', test_run)

    def get_test_run(self, test_run_id: str) -> Optional[TestRun]:
        """
        Get a test run by ID.

        Args:
            test_run_id: Test run identifier

        Returns:
            TestRun instance or None
        """
        return self.active_runs.get(test_run_id)

    def register_callback(self, event: str, callback: Callable) -> None:
        """
        Register a callback for test events.

        Args:
            event: Event name (on_test_start, on_test_complete, etc.)
            callback: Callback function
        """
        if event in self.callbacks:
            self.callbacks[event].append(callback)

    def _trigger_callbacks(self, event: str, test_run: TestRun) -> None:
        """
        Trigger callbacks for an event.

        Args:
            event: Event name
            test_run: Test run instance
        """
        for callback in self.callbacks.get(event, []):
            try:
                callback(test_run)
            except Exception as e:
                print(f"Callback error: {e}")


if __name__ == "__main__":
    # Example usage
    from protocol_loader import ProtocolLoader

    # Load protocol
    loader = ProtocolLoader()
    protocol = loader.load_protocol("JBOX-001")

    # Create test run
    runner = TestRunner()
    test_run = runner.create_test_run(
        protocol=protocol,
        test_run_id="TR-001",
        operator="John Doe",
        sample_id="MODULE-123"
    )

    # Start test
    runner.start_test_run("TR-001")

    # Simulate phase execution
    test_run.set_phase("P1", PhaseStatus.IN_PROGRESS)
    test_run.add_measurement("M1", 5.2, "mΩ")
    test_run.add_note("Initial resistance measured")
    test_run.set_phase("P1", PhaseStatus.COMPLETED)

    # Complete test
    runner.complete_test_run("TR-001")

    # Save results
    filepath = test_run.save()
    print(f"Test run saved to: {filepath}")
    print(f"Summary: {test_run.get_summary()}")
