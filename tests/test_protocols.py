"""Tests for protocol classes and functionality."""

import pytest
from datetime import datetime
from pathlib import Path
import json
import tempfile

from src.protocols.base import BaseProtocol, ProtocolStep
from src.protocols.term001 import TERM001Protocol


class TestProtocolStep:
    """Tests for ProtocolStep class."""

    def test_validate_measurements_success(self):
        """Test successful measurement validation."""
        step = ProtocolStep(
            step_number=1,
            name="Test Step",
            description="Test",
            duration=10,
            duration_unit="minutes",
            inputs=[],
            measurements=[
                {"name": "value1", "type": "number", "required": True},
                {"name": "value2", "type": "number", "required": False},
            ],
            acceptance_criteria=[],
        )

        step.results = {"value1": 50}
        valid, errors = step.validate_measurements()
        assert valid
        assert len(errors) == 0

    def test_validate_measurements_missing_required(self):
        """Test validation failure when required measurement is missing."""
        step = ProtocolStep(
            step_number=1,
            name="Test Step",
            description="Test",
            duration=10,
            duration_unit="minutes",
            inputs=[],
            measurements=[
                {"name": "value1", "type": "number", "required": True},
            ],
            acceptance_criteria=[],
        )

        step.results = {}
        valid, errors = step.validate_measurements()
        assert not valid
        assert len(errors) == 1
        assert "value1" in errors[0]

    def test_check_acceptance_criteria_pass(self):
        """Test acceptance criteria checking with passing values."""
        step = ProtocolStep(
            step_number=1,
            name="Test Step",
            description="Test",
            duration=10,
            duration_unit="minutes",
            inputs=[],
            measurements=[],
            acceptance_criteria=[
                {"parameter": "value1", "condition": "less_than", "value": 100},
                {"parameter": "value2", "condition": "equals", "value": "Pass"},
            ],
        )

        step.results = {"value1": 50, "value2": "Pass"}
        passed, failures = step.check_acceptance_criteria()
        assert passed
        assert len(failures) == 0

    def test_check_acceptance_criteria_fail(self):
        """Test acceptance criteria checking with failing values."""
        step = ProtocolStep(
            step_number=1,
            name="Test Step",
            description="Test",
            duration=10,
            duration_unit="minutes",
            inputs=[],
            measurements=[],
            acceptance_criteria=[
                {"parameter": "value1", "condition": "less_than", "value": 100},
            ],
        )

        step.results = {"value1": 150}
        passed, failures = step.check_acceptance_criteria()
        assert not passed
        assert len(failures) == 1

    def test_evaluate_condition_all_operators(self):
        """Test all condition operators."""
        step = ProtocolStep(
            step_number=1,
            name="Test Step",
            description="Test",
            duration=10,
            duration_unit="minutes",
            inputs=[],
            measurements=[],
            acceptance_criteria=[],
        )

        # Test equals
        assert step._evaluate_condition(50, "equals", 50)
        assert not step._evaluate_condition(50, "equals", 60)

        # Test less_than
        assert step._evaluate_condition(50, "less_than", 100)
        assert not step._evaluate_condition(150, "less_than", 100)

        # Test greater_than
        assert step._evaluate_condition(150, "greater_than", 100)
        assert not step._evaluate_condition(50, "greater_than", 100)

        # Test less_than_or_equal
        assert step._evaluate_condition(100, "less_than_or_equal", 100)
        assert step._evaluate_condition(50, "less_than_or_equal", 100)

        # Test greater_than_or_equal
        assert step._evaluate_condition(100, "greater_than_or_equal", 100)
        assert step._evaluate_condition(150, "greater_than_or_equal", 100)

        # Test not_equals
        assert step._evaluate_condition(50, "not_equals", 100)
        assert not step._evaluate_condition(100, "not_equals", 100)


class TestTERM001Protocol:
    """Tests for TERM-001 Terminal Robustness Test protocol."""

    def test_protocol_initialization(self, term001_protocol):
        """Test that TERM-001 protocol initializes correctly."""
        assert term001_protocol.protocol_id == "TERM-001"
        assert term001_protocol.version == "1.0"
        assert term001_protocol.title == "Terminal Robustness Test"
        assert term001_protocol.category == "Mechanical"
        assert len(term001_protocol.steps) == 7  # Should have 7 steps

    def test_start_test(self, term001_protocol):
        """Test starting a test execution."""
        test_id = "TEST-001"
        serial = "MOD-2025-001"
        operator = "John Doe"

        term001_protocol.start_test(test_id, serial, operator)

        assert term001_protocol.test_id == test_id
        assert term001_protocol.module_serial_number == serial
        assert term001_protocol.operator == operator
        assert term001_protocol.start_time is not None
        assert term001_protocol.current_step_index == 0

    def test_record_measurement(self, term001_protocol):
        """Test recording measurements."""
        term001_protocol.start_test("TEST-001", "MOD-001", "Operator")

        current_step = term001_protocol.get_current_step()
        term001_protocol.record_measurement("terminal_condition", "Pass")

        assert current_step.results["terminal_condition"] == "Pass"

    def test_complete_step_success(self, term001_protocol):
        """Test completing a step successfully."""
        term001_protocol.start_test("TEST-001", "MOD-001", "Operator")

        # Step 1: Initial Visual Inspection
        term001_protocol.record_measurement("terminal_condition", "Pass")

        passed, failures = term001_protocol.complete_current_step()
        assert passed
        assert len(failures) == 0
        assert term001_protocol.current_step_index == 1

    def test_complete_step_failure(self, term001_protocol):
        """Test completing a step with validation failure."""
        term001_protocol.start_test("TEST-001", "MOD-001", "Operator")

        # Step 1: Initial Visual Inspection - fail condition
        term001_protocol.record_measurement("terminal_condition", "Fail")

        passed, failures = term001_protocol.complete_current_step()
        assert not passed
        assert len(failures) > 0

    def test_calculate_derived_values(self, term001_protocol):
        """Test calculation of derived resistance change values."""
        term001_protocol.start_test("TEST-001", "MOD-001", "Operator")

        # Complete step 1 (visual inspection)
        term001_protocol.record_measurement("terminal_condition", "Pass")
        term001_protocol.complete_current_step()

        # Complete step 2 (initial resistance)
        term001_protocol.record_measurement("resistance_positive", 30.0)
        term001_protocol.record_measurement("resistance_negative", 32.0)
        term001_protocol.complete_current_step()

        # Skip to step 5 (post-stress resistance)
        # Complete steps 3 and 4 first
        # Step 3: Pull force test
        term001_protocol.record_measurement("cable_gauge", "12 AWG")
        term001_protocol.record_measurement("pull_force_applied", 250.0)
        term001_protocol.record_measurement("terminal_displacement", 1.5)
        term001_protocol.record_measurement("cable_pulled_out", False)
        term001_protocol.complete_current_step()

        # Step 4: Torque test
        term001_protocol.record_measurement("terminal_type", "MC4")
        term001_protocol.record_measurement("torque_applied", 3.0)
        term001_protocol.record_measurement("terminal_integrity", "No damage")
        term001_protocol.complete_current_step()

        # Step 5: Post-stress resistance
        term001_protocol.record_measurement("resistance_positive_post", 32.0)
        term001_protocol.record_measurement("resistance_negative_post", 34.0)

        # Calculate derived values
        step_5 = term001_protocol.get_current_step()
        term001_protocol.calculate_derived_values(step_5)

        # Check calculated values
        assert "resistance_change_positive" in step_5.results
        assert "resistance_change_negative" in step_5.results

        # 32-30)/30 * 100 = 6.67%
        assert abs(step_5.results["resistance_change_positive"] - 6.67) < 0.1

    def test_get_resistance_data(self, term001_protocol):
        """Test getting resistance data for reporting."""
        term001_protocol.start_test("TEST-001", "MOD-001", "Operator")

        # Complete initial steps to get resistance data
        term001_protocol.record_measurement("terminal_condition", "Pass")
        term001_protocol.complete_current_step()

        term001_protocol.record_measurement("resistance_positive", 30.0)
        term001_protocol.record_measurement("resistance_negative", 32.0)
        term001_protocol.complete_current_step()

        data = term001_protocol.get_resistance_data()

        assert data["initial_positive"] == 30.0
        assert data["initial_negative"] == 32.0

    def test_validate_equipment_calibration(self, term001_protocol):
        """Test equipment calibration validation."""
        from datetime import datetime, timedelta

        # Valid equipment list
        equipment_list = [
            {
                "name": "Digital Multimeter",
                "calibration_due_date": datetime.now() + timedelta(days=30),
            },
            {
                "name": "Pull Force Gauge",
                "calibration_due_date": datetime.now() + timedelta(days=60),
            },
            {
                "name": "Torque Wrench",
                "calibration_due_date": datetime.now() + timedelta(days=45),
            },
            {
                "name": "High-Pot Tester",
                "calibration_due_date": datetime.now() + timedelta(days=90),
            },
        ]

        valid, issues = term001_protocol.validate_equipment_calibration(equipment_list)
        assert valid
        assert len(issues) == 0

    def test_validate_equipment_calibration_expired(self, term001_protocol):
        """Test equipment calibration validation with expired calibration."""
        from datetime import datetime, timedelta

        # Equipment with expired calibration
        equipment_list = [
            {
                "name": "Digital Multimeter",
                "calibration_due_date": datetime.now() - timedelta(days=30),  # Expired
            },
            {
                "name": "Pull Force Gauge",
                "calibration_due_date": datetime.now() + timedelta(days=60),
            },
            {
                "name": "Torque Wrench",
                "calibration_due_date": datetime.now() + timedelta(days=45),
            },
            {
                "name": "High-Pot Tester",
                "calibration_due_date": datetime.now() + timedelta(days=90),
            },
        ]

        valid, issues = term001_protocol.validate_equipment_calibration(equipment_list)
        assert not valid
        assert len(issues) > 0
        assert "Digital Multimeter" in issues[0]

    def test_is_complete(self, term001_protocol):
        """Test checking if all steps are completed."""
        term001_protocol.start_test("TEST-001", "MOD-001", "Operator")

        assert not term001_protocol.is_complete()

        # Mark all steps as completed
        for step in term001_protocol.steps:
            step.completed = True

        assert term001_protocol.is_complete()

    def test_generate_result(self, term001_protocol):
        """Test generating final test result."""
        term001_protocol.start_test("TEST-001", "MOD-001", "Operator")

        # Complete first step
        term001_protocol.record_measurement("terminal_condition", "Pass")
        term001_protocol.complete_current_step()

        result = term001_protocol.generate_result()

        assert result.protocol_id == "TERM-001"
        assert result.test_id == "TEST-001"
        assert result.module_serial_number == "MOD-001"
        assert result.operator == "Operator"
        assert len(result.step_results) == 7
