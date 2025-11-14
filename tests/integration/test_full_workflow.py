"""
Integration Tests for Full Protocol Workflow

Tests the complete workflow from loading to execution.
"""

import pytest
import json
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core import ProtocolLoader, ProtocolValidator, ProtocolExecutor, StepStatus


class TestFullWorkflow:
    """Integration tests for complete protocol workflow."""

    @pytest.fixture
    def pid_002_protocol_file(self, tmp_path):
        """Create PID-002 protocol file in temp directory."""
        protocols_dir = tmp_path / "protocols" / "templates" / "degradation"
        protocols_dir.mkdir(parents=True)

        # Load the actual PID-002 protocol
        src_protocol_path = Path(__file__).parent.parent.parent / "protocols" / "templates" / "degradation" / "pid-002.json"

        if src_protocol_path.exists():
            # Copy the protocol
            with open(src_protocol_path, 'r') as f:
                protocol_data = json.load(f)

            dest_path = protocols_dir / "pid-002.json"
            with open(dest_path, 'w') as f:
                json.dump(protocol_data, f)

            return dest_path, protocol_data
        else:
            # Create a simplified version for testing
            protocol_data = {
                "protocol_id": "PID-002",
                "name": "Potential-Induced Degradation Test",
                "version": "1.0.0",
                "category": "degradation",
                "test_sequence": {
                    "steps": [
                        {
                            "step_id": 1,
                            "name": "Initial Characterization",
                            "type": "measurement",
                            "substeps": [
                                {
                                    "substep_id": 1.1,
                                    "name": "Visual Inspection",
                                    "type": "inspection",
                                    "data_fields": [
                                        {
                                            "field_id": "visual_defects",
                                            "label": "Visual Defects",
                                            "type": "multiselect",
                                            "options": ["None", "Delamination", "Discoloration"],
                                            "required": True
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }

            dest_path = protocols_dir / "pid-002.json"
            with open(dest_path, 'w') as f:
                json.dump(protocol_data, f)

            return dest_path, protocol_data

    def test_load_validate_execute_workflow(self, tmp_path, pid_002_protocol_file):
        """Test complete workflow: load, validate, and execute protocol."""

        protocol_file, _ = pid_002_protocol_file

        # Step 1: Load protocol
        loader = ProtocolLoader(tmp_path / "protocols" / "templates")
        protocol = loader.load_protocol("PID-002")

        assert protocol is not None
        assert protocol['protocol_id'] == "PID-002"

        # Step 2: Validate protocol
        validator = ProtocolValidator()
        is_valid, errors = validator.validate_protocol_structure(protocol)

        assert is_valid, f"Protocol validation failed: {errors}"

        # Step 3: Create executor
        executor = ProtocolExecutor(protocol, "TEST-RUN-001")

        # Step 4: Start test
        executor.start_test(metadata={
            "operator": "Test Operator",
            "facility": "Test Lab",
            "sample_id": "MODULE-001"
        })

        assert executor.test_data['status'] == StepStatus.IN_PROGRESS.value

        # Step 5: Execute first substep
        steps = protocol['test_sequence']['steps']
        first_step = steps[0]
        first_substep = first_step['substeps'][0]

        executor.start_step(
            first_step['step_id'],
            first_substep['substep_id']
        )

        # Record data
        test_data = {"visual_defects": ["None"]}

        # Validate data
        is_valid, errors = validator.validate_test_data(
            protocol,
            first_step['step_id'],
            first_substep['substep_id'],
            test_data
        )

        assert is_valid, f"Data validation failed: {errors}"

        # Record validated data
        executor.record_data(
            first_step['step_id'],
            first_substep['substep_id'],
            test_data
        )

        # Complete step
        executor.complete_step(
            first_step['step_id'],
            first_substep['substep_id'],
            StepStatus.COMPLETED
        )

        # Step 6: Check progress
        progress = executor.get_progress()
        assert progress['completed_substeps'] > 0

        # Step 7: Complete test
        executor.complete_test(StepStatus.COMPLETED)

        # Step 8: Verify final state
        final_data = executor.get_test_data()
        assert final_data['status'] == StepStatus.COMPLETED.value
        assert final_data['start_time'] is not None
        assert final_data['end_time'] is not None

        # Verify recorded data
        measurement = executor.get_measurement(
            first_step['step_id'],
            first_substep['substep_id'],
            "visual_defects"
        )
        assert measurement == ["None"]

    def test_list_and_load_protocols(self, tmp_path, pid_002_protocol_file):
        """Test listing available protocols and loading them."""

        # Create loader
        loader = ProtocolLoader(tmp_path / "protocols" / "templates")

        # List protocols
        protocols = loader.list_protocols()

        assert len(protocols) >= 1
        assert any(p['protocol_id'] == "PID-002" for p in protocols)

        # Get metadata
        metadata = loader.get_protocol_metadata("PID-002")
        assert metadata['protocol_id'] == "PID-002"
        assert metadata['name'] == "Potential-Induced Degradation Test"

        # Get test steps
        steps = loader.get_test_steps("PID-002")
        assert len(steps) >= 1

    def test_qc_validation_workflow(self, tmp_path, pid_002_protocol_file):
        """Test QC validation during execution."""

        protocol_file, protocol_data = pid_002_protocol_file

        # Load protocol
        loader = ProtocolLoader(tmp_path / "protocols" / "templates")
        protocol = loader.load_protocol("PID-002")

        # Create executor
        executor = ProtocolExecutor(protocol, "TEST-RUN-QC-001")
        executor.start_test()

        # Add QC flag
        executor.add_qc_flag(
            rule_id="QC001",
            severity="warning",
            message="Test QC warning"
        )

        # Verify QC flag was added
        assert len(executor.test_data['qc_flags']) == 1
        assert executor.test_data['qc_flags'][0]['severity'] == "warning"

        # Check progress includes QC flags
        progress = executor.get_progress()
        assert progress['qc_flags_count'] == 1

    def test_data_validation_errors(self, tmp_path, pid_002_protocol_file):
        """Test data validation with invalid data."""

        protocol_file, _ = pid_002_protocol_file

        # Load and validate protocol
        loader = ProtocolLoader(tmp_path / "protocols" / "templates")
        protocol = loader.load_protocol("PID-002")

        validator = ProtocolValidator()

        # Get first substep
        first_step = protocol['test_sequence']['steps'][0]
        first_substep = first_step['substeps'][0]

        # Test with missing required field
        invalid_data = {}  # Missing visual_defects

        is_valid, errors = validator.validate_test_data(
            protocol,
            first_step['step_id'],
            first_substep['substep_id'],
            invalid_data
        )

        assert not is_valid
        assert len(errors) > 0

        # Test with invalid option
        invalid_data = {"visual_defects": ["InvalidOption"]}

        is_valid, errors = validator.validate_test_data(
            protocol,
            first_step['step_id'],
            first_substep['substep_id'],
            invalid_data
        )

        assert not is_valid
        assert len(errors) > 0
