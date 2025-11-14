"""
Unit tests for Ground Continuity Test Runner
"""

import pytest
from src.runners import GroundContinuityRunner
from src.models import TestExecution, TestOutcome, TestStatus


class TestGroundContinuityRunner:
    """Test cases for GroundContinuityRunner"""

    def test_initialization(self, db_session):
        """Test runner initialization"""
        runner = GroundContinuityRunner(db_session=db_session)

        assert runner.protocol_id == "GROUND-001"
        assert runner.protocol is not None
        assert runner.protocol.protocol_name == "Ground Continuity Test (Equipotential Bonding)"

    def test_calculate_parameters(self, db_session):
        """Test parameter calculation"""
        runner = GroundContinuityRunner(db_session=db_session)

        input_params = {
            'max_overcurrent_protection': 15.0,
            'ambient_temperature': 25.0,
            'relative_humidity': 50.0
        }

        calculated = runner.calculate_parameters(input_params)

        # Test current should be 2.5 × max overcurrent protection
        assert calculated['test_current'] == 2.5 * 15.0
        assert calculated['test_current'] == 37.5

        # Other parameters should be present
        assert calculated['test_duration'] == 120
        assert calculated['voltage_limit'] == 12
        assert calculated['max_resistance'] == 0.1
        assert calculated['ambient_temperature'] == 25.0
        assert calculated['relative_humidity'] == 50.0

    def test_calculate_parameters_missing_input(self, db_session):
        """Test parameter calculation with missing required input"""
        runner = GroundContinuityRunner(db_session=db_session)

        with pytest.raises(ValueError, match="max_overcurrent_protection is required"):
            runner.calculate_parameters({})

    def test_create_test_execution(self, db_session, sample_data):
        """Test creating a test execution"""
        runner = GroundContinuityRunner(db_session=db_session)

        test_execution = runner.create_test_execution(
            sample_id=sample_data.id,
            operator_id="OP123",
            operator_name="Test Operator",
            parameters={'test_current': 37.5}
        )

        assert test_execution is not None
        assert test_execution.test_number.startswith("GROUND-001-")
        assert test_execution.protocol_id == runner.protocol.id
        assert test_execution.sample_id == sample_data.id
        assert test_execution.operator_id == "OP123"
        assert test_execution.status == TestStatus.PENDING

    def test_run_test_simulated(self, db_session, sample_data, equipment_data):
        """Test running a simulated test"""
        runner = GroundContinuityRunner(db_session=db_session)

        # Create test execution
        input_params = {
            'max_overcurrent_protection': 15.0,
            'ambient_temperature': 25.0,
            'relative_humidity': 50.0
        }
        calculated_params = runner.calculate_parameters(input_params)

        test_execution = runner.create_test_execution(
            sample_id=sample_data.id,
            operator_id="OP123",
            operator_name="Test Operator",
            equipment_id=equipment_data.id,
            parameters=calculated_params
        )

        # Run test in simulated mode
        outcome = runner.run_test(
            test_execution=test_execution,
            measurement_points=["Frame to J-Box"],
            auto_mode=False  # Use simulated manual mode
        )

        # Verify outcome
        assert outcome == TestOutcome.PASS
        assert test_execution.status == TestStatus.COMPLETED
        assert test_execution.outcome == TestOutcome.PASS

        # Verify measurements were recorded
        measurements = test_execution.measurements
        assert len(measurements) > 0

        # Check for key measurements
        measurement_names = [m.measurement_name for m in measurements]
        assert "voltage_drop" in measurement_names
        assert "measured_resistance" in measurement_names
        assert "test_current_actual" in measurement_names

    def test_validate_sample(self, db_session, sample_data):
        """Test sample validation"""
        runner = GroundContinuityRunner(db_session=db_session)

        # Valid sample
        is_valid, error = runner.validate_sample(sample_data)
        assert is_valid is True
        assert error is None

        # Invalid sample (no max_overcurrent_protection)
        sample_data.max_overcurrent_protection = None
        is_valid, error = runner.validate_sample(sample_data)
        assert is_valid is False
        assert "max_overcurrent_protection" in error

    def test_safety_limits(self, db_session):
        """Test safety limit checking"""
        runner = GroundContinuityRunner(db_session=db_session)

        # Normal measurements - no safety limit exceeded
        normal_measurements = {
            'voltage': 5.0,
            'current': 100.0
        }
        action = runner.check_safety_limits(normal_measurements)
        assert action is None

        # Excessive voltage - should trigger stop
        high_voltage_measurements = {
            'voltage': 20.0,  # Exceeds 15V limit
            'current': 100.0
        }
        action = runner.check_safety_limits(high_voltage_measurements)
        assert action == 'stop'

        # Excessive current - should trigger stop
        high_current_measurements = {
            'voltage': 5.0,
            'current': 350.0  # Exceeds 300A limit
        }
        action = runner.check_safety_limits(high_current_measurements)
        assert action == 'stop'

    def test_measurement_recording(self, db_session, sample_data):
        """Test measurement recording"""
        runner = GroundContinuityRunner(db_session=db_session)

        calculated_params = runner.calculate_parameters({
            'max_overcurrent_protection': 15.0
        })

        test_execution = runner.create_test_execution(
            sample_id=sample_data.id,
            operator_id="OP123",
            operator_name="Test Operator",
            parameters=calculated_params
        )

        # Add a measurement
        measurement = runner.add_measurement(
            test_execution=test_execution,
            measurement_name="voltage_drop",
            value=1.5,
            unit="V",
            measurement_point="Frame to J-Box",
            within_limits=True
        )

        assert measurement is not None
        assert measurement.measurement_name == "voltage_drop"
        assert measurement.value == 1.5
        assert measurement.unit == "V"
        assert measurement.within_limits is True

    def test_criteria_evaluation(self, db_session, sample_data):
        """Test pass/fail criteria evaluation"""
        runner = GroundContinuityRunner(db_session=db_session)

        calculated_params = runner.calculate_parameters({
            'max_overcurrent_protection': 15.0
        })

        test_execution = runner.create_test_execution(
            sample_id=sample_data.id,
            operator_id="OP123",
            operator_name="Test Operator",
            parameters=calculated_params
        )

        # Measurements that should pass
        measurements = {
            'measured_resistance': 0.05,  # Below 0.1 Ω limit
            'voltage_drop': 2.0,  # Below 12V limit
            'test_duration_actual': 120,  # Meets 120s requirement
            'test_current_actual': 37.5,  # Matches calculated
            'test_current': 37.5,
            'max_resistance': 0.1,
            'voltage_limit': 12,
            'test_duration': 120
        }

        results = runner.evaluate_criteria(test_execution, measurements)

        assert len(results) > 0

        # All criteria should pass with these measurements
        for result in results:
            if result.severity == 'critical':
                assert result.passed is True
