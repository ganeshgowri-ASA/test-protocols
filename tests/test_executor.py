"""
Tests for test executor module.
"""

import pytest
from datetime import datetime
from test_protocols.core.protocol_loader import ProtocolLoader
from test_protocols.core.test_executor import (
    TestExecutor, TestRun, StepResult, MeasurementData, TestStatus, StepStatus
)


class TestTestExecutor:
    """Test suite for TestExecutor class."""

    @pytest.fixture
    def protocol(self, ml_001_protocol_path, schema_path):
        """Load ML-001 protocol for testing."""
        loader = ProtocolLoader(schema_path=schema_path)
        return loader.load_protocol(ml_001_protocol_path)

    @pytest.fixture
    def executor(self, protocol):
        """Create test executor."""
        return TestExecutor(protocol)

    def test_create_test_run(self, executor):
        """Test creating a test run."""
        test_run = executor.create_test_run(
            sample_id="PV-2025-001",
            operator_id="operator1"
        )

        assert isinstance(test_run, TestRun)
        assert test_run.protocol_id == "ML-001"
        assert test_run.sample_id == "PV-2025-001"
        assert test_run.operator_id == "operator1"
        assert test_run.status == TestStatus.PENDING

    def test_start_test(self, executor):
        """Test starting a test."""
        executor.create_test_run(
            sample_id="PV-2025-001",
            operator_id="operator1"
        )

        executor.start_test()

        assert executor.current_run.status == TestStatus.IN_PROGRESS

    def test_start_step(self, executor):
        """Test starting a test step."""
        executor.create_test_run(
            sample_id="PV-2025-001",
            operator_id="operator1"
        )
        executor.start_test()

        step_result = executor.start_step("ML-001-S01")

        assert step_result.status == StepStatus.IN_PROGRESS
        assert executor.current_run.current_step == "ML-001-S01"

    def test_complete_step(self, executor):
        """Test completing a test step."""
        executor.create_test_run(
            sample_id="PV-2025-001",
            operator_id="operator1"
        )
        executor.start_test()
        executor.start_step("ML-001-S01")

        step_result = executor.complete_step("ML-001-S01", passed=True, notes="Step completed successfully")

        assert step_result.status == StepStatus.COMPLETED
        assert step_result.passed is True
        assert step_result.notes == "Step completed successfully"

    def test_fail_step(self, executor):
        """Test failing a test step."""
        executor.create_test_run(
            sample_id="PV-2025-001",
            operator_id="operator1"
        )
        executor.start_test()
        executor.start_step("ML-001-S01")

        step_result = executor.fail_step("ML-001-S01", error="Equipment malfunction")

        assert step_result.status == StepStatus.FAILED
        assert step_result.passed is False
        assert "Equipment malfunction" in step_result.errors

    def test_record_measurement(self, executor):
        """Test recording a measurement."""
        executor.create_test_run(
            sample_id="PV-2025-001",
            operator_id="operator1"
        )
        executor.start_test()
        executor.start_step("ML-001-S04")

        measurement = executor.record_measurement(
            step_id="ML-001-S04",
            measurement_type="applied_pressure",
            value=2400.0,
            unit="Pa",
            sensor_id="PRESSURE_01"
        )

        assert isinstance(measurement, MeasurementData)
        assert measurement.measurement_type == "applied_pressure"
        assert measurement.value == 2400.0
        assert measurement.unit == "Pa"

    def test_complete_test(self, executor):
        """Test completing a test."""
        executor.create_test_run(
            sample_id="PV-2025-001",
            operator_id="operator1"
        )
        executor.start_test()

        test_run = executor.complete_test(notes="Test completed successfully")

        assert test_run.status == TestStatus.COMPLETED
        assert test_run.end_time is not None

    def test_abort_test(self, executor):
        """Test aborting a test."""
        executor.create_test_run(
            sample_id="PV-2025-001",
            operator_id="operator1"
        )
        executor.start_test()

        test_run = executor.abort_test(reason="Equipment failure")

        assert test_run.status == TestStatus.ABORTED
        assert "Equipment failure" in test_run.notes

    def test_pause_resume_test(self, executor):
        """Test pausing and resuming a test."""
        executor.create_test_run(
            sample_id="PV-2025-001",
            operator_id="operator1"
        )
        executor.start_test()

        executor.pause_test()
        assert executor.current_run.status == TestStatus.PAUSED

        executor.resume_test()
        assert executor.current_run.status == TestStatus.IN_PROGRESS

    def test_get_progress(self, executor):
        """Test getting test progress."""
        executor.create_test_run(
            sample_id="PV-2025-001",
            operator_id="operator1"
        )
        executor.start_test()

        progress = executor.get_progress()

        assert "test_run_id" in progress
        assert "status" in progress
        assert "total_steps" in progress
        assert "progress_percent" in progress
        assert progress["total_steps"] == 9  # ML-001 has 9 steps


class TestTestRun:
    """Test suite for TestRun class."""

    def test_generate_id(self):
        """Test generating test run ID."""
        run_id = TestRun.generate_id("ML-001")

        assert "ML-001" in run_id
        assert len(run_id) > 20  # Contains timestamp and random suffix

    def test_add_measurement(self):
        """Test adding measurement to test run."""
        test_run = TestRun(
            test_run_id="TEST-001",
            protocol_id="ML-001",
            protocol_version="1.0.0",
            sample_id="PV-001",
            operator_id="operator1",
            status=TestStatus.IN_PROGRESS,
            start_time=datetime.now()
        )

        # Add step result first
        step_result = StepResult(
            step_id="ML-001-S04",
            status=StepStatus.IN_PROGRESS,
            start_time=datetime.now()
        )
        test_run.step_results.append(step_result)

        # Add measurement
        measurement = test_run.add_measurement(
            step_id="ML-001-S04",
            measurement_type="pressure",
            value=2400.0,
            unit="Pa"
        )

        assert isinstance(measurement, MeasurementData)
        assert len(step_result.measurements) == 1
