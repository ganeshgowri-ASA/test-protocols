"""
Integration tests for complete workflow
"""

import pytest
from src.models import Sample, Equipment, TestExecution, TestOutcome, TestStatus
from src.runners import GroundContinuityRunner


class TestFullWorkflow:
    """Integration tests for complete test execution workflow"""

    def test_complete_ground_continuity_workflow(self, db_session):
        """Test complete workflow from sample creation to test completion"""

        # 1. Create a sample
        sample = Sample(
            sample_id="INT-TEST-001",
            serial_number="INT-SN-12345",
            module_type="Monocrystalline",
            rated_power_pmax=450.0,
            rated_voltage_vmp=42.0,
            rated_current_imp=10.7,
            open_circuit_voltage_voc=50.4,
            short_circuit_current_isc=11.2,
            max_overcurrent_protection=20.0,
            is_active=True
        )
        db_session.add(sample)
        db_session.commit()
        db_session.refresh(sample)

        assert sample.id is not None

        # 2. Create equipment
        equipment = Equipment(
            equipment_id="INT-EQ-001",
            name="Integration Test Ground Tester",
            equipment_type="Ground Continuity Tester",
            manufacturer="Test Corp",
            model="GT-2000",
            is_active=True
        )
        db_session.add(equipment)
        db_session.commit()
        db_session.refresh(equipment)

        assert equipment.id is not None

        # 3. Initialize test runner
        runner = GroundContinuityRunner(db_session=db_session)

        assert runner.protocol is not None
        assert runner.protocol.protocol_id == "GROUND-001"

        # 4. Calculate test parameters
        input_params = {
            'max_overcurrent_protection': sample.max_overcurrent_protection,
            'ambient_temperature': 23.5,
            'relative_humidity': 45.0
        }

        calculated_params = runner.calculate_parameters(input_params)

        assert calculated_params['test_current'] == 2.5 * 20.0
        assert calculated_params['test_current'] == 50.0

        # 5. Create test execution
        test_execution = runner.create_test_execution(
            sample_id=sample.id,
            operator_id="INT-OP-001",
            operator_name="Integration Test Operator",
            equipment_id=equipment.id,
            parameters=calculated_params
        )

        assert test_execution is not None
        assert test_execution.status == TestStatus.PENDING
        assert test_execution.sample_id == sample.id
        assert test_execution.equipment_id == equipment.id

        # 6. Run the test
        measurement_points = [
            "Frame to Junction Box",
            "Frame to Connector Ground Pin"
        ]

        outcome = runner.run_test(
            test_execution=test_execution,
            measurement_points=measurement_points,
            auto_mode=False  # Simulated manual mode
        )

        # 7. Verify test completion
        assert test_execution.status == TestStatus.COMPLETED
        assert test_execution.outcome == TestOutcome.PASS
        assert test_execution.actual_start is not None
        assert test_execution.actual_end is not None
        assert test_execution.duration_seconds is not None

        # 8. Verify measurements were recorded
        measurements = test_execution.measurements
        assert len(measurements) > 0

        # Should have measurements for each point
        measurement_points_recorded = {
            m.measurement_point for m in measurements
            if m.measurement_point is not None
        }
        assert "Frame to Junction Box" in measurement_points_recorded
        assert "Frame to Connector Ground Pin" in measurement_points_recorded

        # 9. Verify key measurements exist
        measurement_names = {m.measurement_name for m in measurements}
        assert "voltage_drop" in measurement_names
        assert "measured_resistance" in measurement_names
        assert "test_current_actual" in measurement_names

        # 10. Verify pass/fail criteria were evaluated
        results = test_execution.results
        assert len(results) > 0

        # Check that critical criteria passed
        critical_results = [r for r in results if r.severity == 'critical']
        assert len(critical_results) > 0

        for result in critical_results:
            assert result.passed is True, f"Critical criterion failed: {result.criterion_name}"

        # 11. Verify relationships
        assert test_execution.sample == sample
        assert test_execution.equipment == equipment
        assert test_execution.protocol == runner.protocol

        # 12. Verify data integrity
        db_session.refresh(sample)
        assert len(sample.test_executions) > 0
        assert test_execution in sample.test_executions

    def test_multiple_tests_on_same_sample(self, db_session):
        """Test running multiple tests on the same sample"""

        # Create sample
        sample = Sample(
            sample_id="MULTI-TEST-001",
            serial_number="MULTI-SN-001",
            max_overcurrent_protection=15.0,
            is_active=True
        )
        db_session.add(sample)
        db_session.commit()
        db_session.refresh(sample)

        runner = GroundContinuityRunner(db_session=db_session)

        # Run three tests on the same sample
        test_numbers = []

        for i in range(3):
            input_params = {
                'max_overcurrent_protection': 15.0,
                'ambient_temperature': 25.0 + i,  # Slightly different temps
                'relative_humidity': 50.0
            }

            calculated_params = runner.calculate_parameters(input_params)

            test_execution = runner.create_test_execution(
                sample_id=sample.id,
                operator_id=f"OP-{i:03d}",
                operator_name=f"Operator {i}",
                parameters=calculated_params
            )

            outcome = runner.run_test(
                test_execution=test_execution,
                measurement_points=["Frame to Point 1"],
                auto_mode=False
            )

            assert outcome == TestOutcome.PASS
            test_numbers.append(test_execution.test_number)

        # Verify all test numbers are unique
        assert len(test_numbers) == len(set(test_numbers))

        # Verify sample has all three tests
        db_session.refresh(sample)
        assert len(sample.test_executions) == 3

    def test_protocol_version_management(self, db_session):
        """Test protocol version management"""

        runner = GroundContinuityRunner(db_session=db_session)

        protocol = runner.protocol
        assert protocol is not None

        # Check that a protocol version was created
        assert len(protocol.versions) > 0

        current_version = [v for v in protocol.versions if v.is_current][0]
        assert current_version is not None
        assert current_version.version == "1.0.0"
        assert current_version.json_definition is not None

        # Verify JSON definition contains expected keys
        json_def = current_version.json_definition
        assert 'protocol_id' in json_def
        assert 'parameters' in json_def
        assert 'measurements' in json_def
        assert 'pass_criteria' in json_def
