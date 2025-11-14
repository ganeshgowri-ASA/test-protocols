"""
Unit Tests for Protocol Executor

Tests protocol execution and data recording functionality.
"""

import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core import ProtocolExecutor, StepStatus


class TestProtocolExecutor:
    """Test cases for ProtocolExecutor class."""

    @pytest.fixture
    def sample_protocol(self):
        """Create a sample protocol for testing."""
        return {
            "protocol_id": "TEST-001",
            "name": "Test Protocol",
            "version": "1.0.0",
            "category": "test",
            "test_sequence": {
                "steps": [
                    {
                        "step_id": 1,
                        "name": "Step 1",
                        "type": "measurement",
                        "substeps": [
                            {
                                "substep_id": 1.1,
                                "name": "Substep 1.1",
                                "type": "measurement",
                                "data_fields": [
                                    {
                                        "field_id": "test_value",
                                        "type": "number"
                                    }
                                ]
                            },
                            {
                                "substep_id": 1.2,
                                "name": "Substep 1.2",
                                "type": "procedure",
                                "data_fields": []
                            }
                        ]
                    },
                    {
                        "step_id": 2,
                        "name": "Step 2",
                        "type": "analysis",
                        "substeps": [
                            {
                                "substep_id": 2.1,
                                "name": "Substep 2.1",
                                "type": "calculation",
                                "data_fields": []
                            }
                        ]
                    }
                ]
            }
        }

    @pytest.fixture
    def executor(self, sample_protocol):
        """Create a ProtocolExecutor instance."""
        return ProtocolExecutor(sample_protocol, "TEST-RUN-001")

    def test_initialization(self, executor, sample_protocol):
        """Test ProtocolExecutor initialization."""
        assert executor.protocol == sample_protocol
        assert executor.test_run_id == "TEST-RUN-001"
        assert executor.test_data['protocol_id'] == "TEST-001"
        assert executor.test_data['status'] == StepStatus.PENDING.value

    def test_start_test(self, executor):
        """Test starting a test run."""
        metadata = {"operator": "John Doe", "facility": "Lab A"}
        executor.start_test(metadata)

        assert executor.test_data['status'] == StepStatus.IN_PROGRESS.value
        assert executor.test_data['start_time'] is not None
        assert executor.test_data['metadata']['operator'] == "John Doe"
        assert executor.test_data['metadata']['facility'] == "Lab A"

    def test_start_step(self, executor):
        """Test starting a step."""
        substep = executor.start_step(1, 1.1)

        assert substep['name'] == "Substep 1.1"
        assert executor.current_step_id == 1
        assert executor.current_substep_id == 1.1

        step_key = "1.1.1"
        assert "1.1.1" in executor.test_data['steps']
        step_data = executor.test_data['steps']["1.1.1"]
        assert step_data['status'] == StepStatus.IN_PROGRESS.value

    def test_start_step_invalid(self, executor):
        """Test starting an invalid step."""
        with pytest.raises(ValueError):
            executor.start_step(99, 99.9)

    def test_record_data(self, executor):
        """Test recording data for a step."""
        executor.start_step(1, 1.1)

        data = {"test_value": 42.5, "notes": "Test notes"}
        executor.record_data(1, 1.1, data)

        step_data = executor.get_step_data(1, 1.1)
        assert step_data['data']['test_value'] == 42.5
        assert step_data['data']['notes'] == "Test notes"

        # Check measurements
        value = executor.get_measurement(1, 1.1, "test_value")
        assert value == 42.5

    def test_record_data_not_started(self, executor):
        """Test recording data for a step that wasn't started."""
        with pytest.raises(ValueError):
            executor.record_data(1, 1.1, {"test_value": 42.5})

    def test_complete_step(self, executor):
        """Test completing a step."""
        executor.start_step(1, 1.1)
        executor.complete_step(1, 1.1, StepStatus.COMPLETED, "Step completed successfully")

        step_data = executor.get_step_data(1, 1.1)
        assert step_data['status'] == StepStatus.COMPLETED.value
        assert step_data['end_time'] is not None
        assert "Step completed successfully" in step_data['notes']

    def test_complete_step_not_started(self, executor):
        """Test completing a step that wasn't started."""
        with pytest.raises(ValueError):
            executor.complete_step(1, 1.1, StepStatus.COMPLETED)

    def test_add_qc_flag(self, executor):
        """Test adding a QC flag."""
        executor.add_qc_flag(
            rule_id="QC001",
            severity="warning",
            message="Test warning",
            step_id=1,
            substep_id=1.1
        )

        assert len(executor.test_data['qc_flags']) == 1
        flag = executor.test_data['qc_flags'][0]
        assert flag['rule_id'] == "QC001"
        assert flag['severity'] == "warning"
        assert flag['message'] == "Test warning"
        assert flag['step_id'] == 1
        assert flag['substep_id'] == 1.1

    def test_complete_test(self, executor):
        """Test completing the test run."""
        executor.start_test()
        executor.complete_test(StepStatus.COMPLETED)

        assert executor.test_data['status'] == StepStatus.COMPLETED.value
        assert executor.test_data['end_time'] is not None

    def test_get_test_data(self, executor):
        """Test getting complete test data."""
        executor.start_test()
        executor.start_step(1, 1.1)
        executor.record_data(1, 1.1, {"test_value": 42.5})
        executor.complete_step(1, 1.1, StepStatus.COMPLETED)

        test_data = executor.get_test_data()

        assert test_data['test_run_id'] == "TEST-RUN-001"
        assert test_data['protocol_id'] == "TEST-001"
        assert len(test_data['steps']) == 1
        assert len(test_data['measurements']) == 1

    def test_get_measurement(self, executor):
        """Test getting a specific measurement."""
        executor.start_step(1, 1.1)
        executor.record_data(1, 1.1, {"test_value": 42.5})

        value = executor.get_measurement(1, 1.1, "test_value")
        assert value == 42.5

        # Non-existent measurement
        value = executor.get_measurement(1, 1.1, "nonexistent")
        assert value is None

    def test_calculate_field(self, executor):
        """Test field calculation."""
        context = {
            "pmax_initial": 100,
            "pmax_final": 95
        }

        formula = "((pmax_initial - pmax_final) / pmax_initial) * 100"
        result = executor.calculate_field(formula, context)

        assert result == 5.0

    def test_calculate_field_error(self, executor):
        """Test field calculation with error."""
        context = {}
        formula = "invalid_variable * 2"

        result = executor.calculate_field(formula, context)
        assert result is None

    def test_get_progress(self, executor):
        """Test getting test progress."""
        executor.start_test()

        # Initially no progress
        progress = executor.get_progress()
        assert progress['total_steps'] == 2
        assert progress['total_substeps'] == 3
        assert progress['completed_substeps'] == 0
        assert progress['progress_percent'] == 0

        # Complete one substep
        executor.start_step(1, 1.1)
        executor.complete_step(1, 1.1, StepStatus.COMPLETED)

        progress = executor.get_progress()
        assert progress['completed_substeps'] == 1
        assert progress['progress_percent'] == pytest.approx(33.33, rel=0.01)

        # Complete another substep
        executor.start_step(1, 1.2)
        executor.complete_step(1, 1.2, StepStatus.COMPLETED)

        progress = executor.get_progress()
        assert progress['completed_substeps'] == 2
        assert progress['progress_percent'] == pytest.approx(66.67, rel=0.01)

    def test_full_workflow(self, executor):
        """Test a complete workflow."""
        # Start test
        executor.start_test({"operator": "Test Operator"})

        # Execute step 1.1
        executor.start_step(1, 1.1)
        executor.record_data(1, 1.1, {"test_value": 100})
        executor.complete_step(1, 1.1, StepStatus.COMPLETED)

        # Execute step 1.2
        executor.start_step(1, 1.2)
        executor.complete_step(1, 1.2, StepStatus.COMPLETED)

        # Execute step 2.1
        executor.start_step(2, 2.1)
        executor.complete_step(2, 2.1, StepStatus.COMPLETED)

        # Add QC flag
        executor.add_qc_flag("QC001", "info", "Test completed")

        # Complete test
        executor.complete_test(StepStatus.COMPLETED)

        # Verify final state
        test_data = executor.get_test_data()
        assert test_data['status'] == StepStatus.COMPLETED.value
        assert len(test_data['steps']) == 3
        assert len(test_data['qc_flags']) == 1

        progress = executor.get_progress()
        assert progress['completed_substeps'] == 3
        assert progress['progress_percent'] == 100.0
