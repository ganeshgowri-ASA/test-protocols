"""
Unit Tests for Base Protocol Classes
Tests for the abstract base protocol functionality
"""

import pytest
from datetime import datetime
from pathlib import Path

from protocols.base import (
    BaseProtocol,
    ProtocolPhase,
    ProtocolStep,
    ProtocolStatus,
    StepStatus,
    AcceptanceCriterion,
    Criticality
)


class TestProtocolStep:
    """Tests for ProtocolStep class"""

    def test_step_creation(self):
        """Test creating a protocol step"""
        step = ProtocolStep(
            step_id="1.1",
            action="Test Action",
            description="Test description",
            acceptance_criteria="Test passes"
        )

        assert step.step_id == "1.1"
        assert step.action == "Test Action"
        assert step.status == StepStatus.PENDING

    def test_step_start(self):
        """Test starting a step"""
        step = ProtocolStep(step_id="1.1", action="Test", description="Test")
        step.start()

        assert step.status == StepStatus.IN_PROGRESS
        assert step.start_time is not None

    def test_step_complete(self):
        """Test completing a step"""
        step = ProtocolStep(step_id="1.1", action="Test", description="Test")
        step.start()
        data = {"measurement": 42.0}
        step.complete(data)

        assert step.status == StepStatus.COMPLETED
        assert step.end_time is not None
        assert step.data["measurement"] == 42.0

    def test_step_fail(self):
        """Test failing a step"""
        step = ProtocolStep(step_id="1.1", action="Test", description="Test")
        step.start()
        step.fail("Test failed due to error")

        assert step.status == StepStatus.FAILED
        assert "Failed: Test failed" in step.operator_notes

    def test_step_skip(self):
        """Test skipping a step"""
        step = ProtocolStep(step_id="1.1", action="Test", description="Test")
        step.skip("Not applicable")

        assert step.status == StepStatus.SKIPPED
        assert "Skipped: Not applicable" in step.operator_notes


class TestProtocolPhase:
    """Tests for ProtocolPhase class"""

    def test_phase_creation(self):
        """Test creating a protocol phase"""
        steps = [
            ProtocolStep("1.1", "Action 1", "Description 1"),
            ProtocolStep("1.2", "Action 2", "Description 2")
        ]
        phase = ProtocolPhase(
            phase_id=1,
            name="Test Phase",
            duration="2 hours",
            steps=steps
        )

        assert phase.phase_id == 1
        assert len(phase.steps) == 2
        assert phase.status == StepStatus.PENDING

    def test_phase_progress(self):
        """Test getting phase progress"""
        steps = [
            ProtocolStep("1.1", "Action 1", "Description 1"),
            ProtocolStep("1.2", "Action 2", "Description 2"),
            ProtocolStep("1.3", "Action 3", "Description 3")
        ]
        phase = ProtocolPhase(1, "Test", "1 hour", steps)

        steps[0].start()
        steps[0].complete()
        steps[1].start()

        progress = phase.get_progress()
        assert progress["total"] == 3
        assert progress["completed"] == 1
        assert progress["in_progress"] == 1
        assert progress["pending"] == 1


class TestAcceptanceCriterion:
    """Tests for AcceptanceCriterion class"""

    def test_criterion_creation(self):
        """Test creating an acceptance criterion"""
        criterion = AcceptanceCriterion(
            parameter="Power Degradation",
            requirement="≤ 5%",
            criticality=Criticality.CRITICAL,
            measurement="ΔPmax from baseline"
        )

        assert criterion.parameter == "Power Degradation"
        assert criterion.criticality == Criticality.CRITICAL
        assert criterion.passed is None

    def test_criterion_evaluation(self):
        """Test evaluating a criterion"""
        criterion = AcceptanceCriterion(
            parameter="Test",
            requirement="≤ 5",
            criticality=Criticality.MAJOR,
            measurement="test value"
        )

        result = criterion.evaluate(3.5)
        assert criterion.actual_value == 3.5


class TestBaseProtocol:
    """Tests for BaseProtocol functionality"""

    def test_protocol_loading(self, sample_protocol_path):
        """Test loading protocol from JSON"""
        from protocols.environmental.h2s_001 import H2S001Protocol
        protocol = H2S001Protocol(sample_protocol_path)

        assert protocol.config is not None
        assert protocol.status == ProtocolStatus.NOT_STARTED

    def test_protocol_info(self, h2s_protocol):
        """Test getting protocol information"""
        info = h2s_protocol.get_protocol_info()

        assert info["id"] == "P37-54"
        assert info["code"] == "H2S-001"
        assert info["name"] == "Hydrogen Sulfide Exposure Test"
        assert info["category"] == "Environmental"

    def test_protocol_description(self, h2s_protocol):
        """Test getting protocol description"""
        desc = h2s_protocol.get_description()

        assert "hydrogen sulfide" in desc["purpose"].lower()
        assert "pv modules" in desc["scope"].lower()

    def test_equipment_list(self, h2s_protocol):
        """Test getting equipment list"""
        equipment = h2s_protocol.get_equipment_list()

        assert "required" in equipment
        assert "optional" in equipment
        assert len(equipment["required"]) > 0

    def test_test_conditions(self, h2s_protocol):
        """Test getting test conditions"""
        conditions = h2s_protocol.get_test_conditions()

        assert "environmental" in conditions
        assert "h2s_concentration" in conditions["environmental"]
        assert conditions["environmental"]["h2s_concentration"]["value"] == 10

    def test_phases_initialization(self, h2s_protocol):
        """Test that phases are properly initialized"""
        assert len(h2s_protocol.phases) > 0

        # Check first phase structure
        phase = h2s_protocol.phases[0]
        assert phase.phase_id == 1
        assert len(phase.steps) > 0

    def test_acceptance_criteria_initialization(self, h2s_protocol):
        """Test that acceptance criteria are initialized"""
        assert len(h2s_protocol.acceptance_criteria) > 0

        # Check for critical criteria
        critical = [c for c in h2s_protocol.acceptance_criteria
                   if c.criticality == Criticality.CRITICAL]
        assert len(critical) > 0

    def test_module_info_setting(self, h2s_protocol, sample_module_info):
        """Test setting module information"""
        h2s_protocol.set_module_info(sample_module_info)

        assert h2s_protocol.module_info == sample_module_info
        assert "module_info" in h2s_protocol.test_data

    def test_protocol_start(self, h2s_protocol):
        """Test starting protocol execution"""
        h2s_protocol.start_protocol()

        assert h2s_protocol.status == ProtocolStatus.IN_PROGRESS
        assert h2s_protocol.start_time is not None

    def test_protocol_complete(self, h2s_protocol):
        """Test completing protocol"""
        h2s_protocol.start_protocol()
        h2s_protocol.complete_protocol()

        assert h2s_protocol.status == ProtocolStatus.COMPLETED
        assert h2s_protocol.end_time is not None

    def test_protocol_abort(self, h2s_protocol):
        """Test aborting protocol"""
        h2s_protocol.start_protocol()
        h2s_protocol.abort_protocol("Equipment failure")

        assert h2s_protocol.status == ProtocolStatus.ABORTED
        assert h2s_protocol.test_data["abort_reason"] == "Equipment failure"

    def test_record_measurement(self, h2s_protocol):
        """Test recording measurements"""
        h2s_protocol.record_measurement("test_table", "voltage", 47.5, "V")

        assert "test_table" in h2s_protocol.test_data
        assert h2s_protocol.test_data["test_table"]["voltage"]["value"] == 47.5
        assert h2s_protocol.test_data["test_table"]["voltage"]["unit"] == "V"

    def test_progress_tracking(self, h2s_protocol):
        """Test progress tracking"""
        progress = h2s_protocol.get_progress()

        assert "status" in progress
        assert "total_phases" in progress
        assert "total_steps" in progress
        assert "progress_percent" in progress

        assert progress["status"] == "not_started"
        assert progress["progress_percent"] == 0

    def test_current_phase(self, h2s_protocol):
        """Test getting current phase"""
        # No phase started
        assert h2s_protocol.get_current_phase() is None

        # Start first phase
        h2s_protocol.phases[0].start()
        current = h2s_protocol.get_current_phase()
        assert current is not None
        assert current.phase_id == 1

    def test_current_step(self, h2s_protocol):
        """Test getting current step"""
        # No step started
        assert h2s_protocol.get_current_step() is None

        # Start first phase and step
        h2s_protocol.phases[0].start()
        h2s_protocol.phases[0].steps[0].start()

        current = h2s_protocol.get_current_step()
        assert current is not None
        assert current.step_id == "1.1"
