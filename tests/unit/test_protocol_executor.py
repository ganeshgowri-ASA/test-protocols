"""Unit tests for protocol executor."""

import unittest
from datetime import datetime

from src.parsers import ProtocolLoader, ProtocolExecutor
from src.models.base import get_engine, init_db, get_session
from src.models.test_run import TestStatus, TestResult


class TestProtocolExecutor(unittest.TestCase):
    """Test cases for ProtocolExecutor class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create in-memory database for testing
        self.engine = get_engine("sqlite:///:memory:")
        init_db(self.engine)
        self.session = get_session(self.engine)

        # Create a test protocol
        self.protocol_data = {
            "protocol_id": "EXEC-TEST-001",
            "protocol_name": "Executor Test Protocol",
            "version": "1.0.0",
            "category": "Mechanical",
            "description": "Protocol for testing executor functionality",
            "standard_reference": [],
            "test_parameters": {
                "specimen_requirements": {
                    "quantity": 1,
                    "description": "Test specimen"
                },
                "environmental_conditions": {},
                "test_specific_parameters": {}
            },
            "test_steps": [
                {
                    "step_number": 1,
                    "description": "Step 1",
                    "action": "setup",
                    "automation_capable": False
                },
                {
                    "step_number": 2,
                    "description": "Step 2",
                    "action": "measurement",
                    "automation_capable": True
                }
            ],
            "acceptance_criteria": [
                {
                    "criterion_id": "AC-001",
                    "description": "Power degradation <= 5%",
                    "evaluation_method": "calculation",
                    "threshold": {
                        "parameter": "power_degradation",
                        "operator": "<=",
                        "value": 5.0,
                        "unit": "%"
                    }
                }
            ],
            "data_collection": {
                "measurements": [],
                "documentation": []
            }
        }

        # Import protocol to database
        loader = ProtocolLoader()
        self.protocol = loader.import_to_database(self.protocol_data, self.session)

    def tearDown(self):
        """Clean up test fixtures."""
        self.session.close()

    def test_create_test_run(self):
        """Test creating a new test run."""
        executor = ProtocolExecutor(self.session)

        test_run = executor.create_test_run(
            protocol=self.protocol,
            specimen_id="SPECIMEN-001",
            operator_name="Test Operator",
            manufacturer="Test Manufacturer",
            model_number="TEST-MODEL-123"
        )

        self.assertIsNotNone(test_run)
        self.assertEqual(test_run.specimen_id, "SPECIMEN-001")
        self.assertEqual(test_run.operator_name, "Test Operator")
        self.assertEqual(test_run.manufacturer, "Test Manufacturer")
        self.assertEqual(test_run.status, TestStatus.PENDING)
        self.assertEqual(test_run.result, TestResult.NOT_EVALUATED)

    def test_initialize_test_steps(self):
        """Test that test steps are initialized from protocol."""
        executor = ProtocolExecutor(self.session)

        test_run = executor.create_test_run(
            protocol=self.protocol,
            specimen_id="SPECIMEN-002",
            operator_name="Test Operator"
        )

        # Should have created 2 test steps
        self.assertEqual(len(test_run.test_steps), 2)
        self.assertEqual(test_run.test_steps[0].step_number, 1)
        self.assertEqual(test_run.test_steps[1].step_number, 2)
        self.assertEqual(test_run.test_steps[0].status, TestStatus.PENDING)

    def test_start_test_run(self):
        """Test starting a test run."""
        executor = ProtocolExecutor(self.session)

        test_run = executor.create_test_run(
            protocol=self.protocol,
            specimen_id="SPECIMEN-003",
            operator_name="Test Operator"
        )

        executor.start_test_run(test_run)

        self.assertEqual(test_run.status, TestStatus.IN_PROGRESS)
        self.assertIsNotNone(test_run.started_at)

    def test_complete_test_run(self):
        """Test completing a test run."""
        executor = ProtocolExecutor(self.session)

        test_run = executor.create_test_run(
            protocol=self.protocol,
            specimen_id="SPECIMEN-004",
            operator_name="Test Operator"
        )

        executor.start_test_run(test_run)
        executor.complete_test_run(test_run, TestResult.PASS)

        self.assertEqual(test_run.status, TestStatus.COMPLETED)
        self.assertEqual(test_run.result, TestResult.PASS)
        self.assertIsNotNone(test_run.completed_at)

    def test_abort_test_run(self):
        """Test aborting a test run."""
        executor = ProtocolExecutor(self.session)

        test_run = executor.create_test_run(
            protocol=self.protocol,
            specimen_id="SPECIMEN-005",
            operator_name="Test Operator"
        )

        executor.start_test_run(test_run)
        executor.abort_test_run(test_run, "Equipment failure")

        self.assertEqual(test_run.status, TestStatus.ABORTED)
        self.assertIn("Equipment failure", test_run.notes)

    def test_start_step(self):
        """Test starting a test step."""
        executor = ProtocolExecutor(self.session)

        test_run = executor.create_test_run(
            protocol=self.protocol,
            specimen_id="SPECIMEN-006",
            operator_name="Test Operator"
        )

        step = test_run.test_steps[0]
        executor.start_step(step)

        self.assertEqual(step.status, TestStatus.IN_PROGRESS)
        self.assertIsNotNone(step.started_at)

    def test_complete_step(self):
        """Test completing a test step."""
        executor = ProtocolExecutor(self.session)

        test_run = executor.create_test_run(
            protocol=self.protocol,
            specimen_id="SPECIMEN-007",
            operator_name="Test Operator"
        )

        step = test_run.test_steps[0]
        executor.start_step(step)
        executor.complete_step(
            step,
            observations="Test observation",
            pass_fail=True
        )

        self.assertEqual(step.status, TestStatus.COMPLETED)
        self.assertEqual(step.observations, "Test observation")
        self.assertTrue(step.pass_fail)
        self.assertIsNotNone(step.completed_at)

    def test_record_measurement(self):
        """Test recording a measurement."""
        executor = ProtocolExecutor(self.session)

        test_run = executor.create_test_run(
            protocol=self.protocol,
            specimen_id="SPECIMEN-008",
            operator_name="Test Operator"
        )

        measurement = executor.record_measurement(
            test_run=test_run,
            measurement_id="M-001",
            parameter="Power",
            value=350.5,
            unit="W",
            instrument="Solar Simulator"
        )

        self.assertIsNotNone(measurement)
        self.assertEqual(measurement.parameter, "Power")
        self.assertEqual(measurement.value_numeric, 350.5)
        self.assertEqual(measurement.unit, "W")
        self.assertEqual(measurement.instrument, "Solar Simulator")

    def test_record_measurement_types(self):
        """Test recording different types of measurements."""
        executor = ProtocolExecutor(self.session)

        test_run = executor.create_test_run(
            protocol=self.protocol,
            specimen_id="SPECIMEN-009",
            operator_name="Test Operator"
        )

        # Numeric
        m1 = executor.record_measurement(
            test_run=test_run,
            measurement_id="M-001",
            parameter="Voltage",
            value=48.5
        )
        self.assertEqual(m1.value_numeric, 48.5)

        # Boolean
        m2 = executor.record_measurement(
            test_run=test_run,
            measurement_id="M-002",
            parameter="Pass",
            value=True
        )
        self.assertTrue(m2.value_boolean)

        # String
        m3 = executor.record_measurement(
            test_run=test_run,
            measurement_id="M-003",
            parameter="Status",
            value="OK"
        )
        self.assertEqual(m3.value_text, "OK")

    def test_evaluate_threshold(self):
        """Test threshold evaluation."""
        executor = ProtocolExecutor(self.session)

        # Test less than or equal
        self.assertTrue(executor._evaluate_threshold(4.5, "<=", 5.0))
        self.assertTrue(executor._evaluate_threshold(5.0, "<=", 5.0))
        self.assertFalse(executor._evaluate_threshold(5.5, "<=", 5.0))

        # Test greater than
        self.assertTrue(executor._evaluate_threshold(6.0, ">", 5.0))
        self.assertFalse(executor._evaluate_threshold(4.0, ">", 5.0))

        # Test equal
        self.assertTrue(executor._evaluate_threshold("PASS", "==", "PASS"))
        self.assertFalse(executor._evaluate_threshold("FAIL", "==", "PASS"))

        # Test between
        self.assertTrue(executor._evaluate_threshold(50, "between", [40, 60]))
        self.assertFalse(executor._evaluate_threshold(70, "between", [40, 60]))

    def test_get_test_run_summary(self):
        """Test getting test run summary."""
        executor = ProtocolExecutor(self.session)

        test_run = executor.create_test_run(
            protocol=self.protocol,
            specimen_id="SPECIMEN-010",
            operator_name="Test Operator"
        )

        # Complete first step
        step = test_run.test_steps[0]
        executor.start_step(step)
        executor.complete_step(step, pass_fail=True)

        summary = executor.get_test_run_summary(test_run)

        self.assertEqual(summary["progress"]["total_steps"], 2)
        self.assertEqual(summary["progress"]["completed_steps"], 1)
        self.assertEqual(summary["progress"]["percentage"], 50.0)


if __name__ == '__main__':
    unittest.main()
