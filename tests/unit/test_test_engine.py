"""
Unit tests for Test Engine
"""
import unittest
from pathlib import Path
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.protocol_loader import ProtocolLoader
from core.test_engine import TestEngine, TestStatus


class TestTestEngine(unittest.TestCase):
    """Test cases for TestEngine class"""

    def setUp(self):
        """Set up test fixtures"""
        loader = ProtocolLoader()
        self.protocol = loader.load_protocol("TROP-001")
        self.test_id = "TEST-001"
        self.engine = TestEngine(self.protocol, self.test_id)

    def test_initialization(self):
        """Test engine initialization"""
        self.assertEqual(self.engine.protocol['protocol_id'], "TROP-001")
        self.assertEqual(self.engine.test_id, self.test_id)
        self.assertEqual(self.engine.status, TestStatus.PENDING)
        self.assertIsNone(self.engine.start_time)
        self.assertEqual(self.engine.current_step, 0)
        self.assertEqual(self.engine.current_cycle, 0)

    def test_start_test(self):
        """Test starting a test"""
        modules = ["MOD001", "MOD002", "MOD003"]
        operator = "John Doe"

        result = self.engine.start_test(modules, operator)

        # Verify result structure
        self.assertEqual(result['test_id'], self.test_id)
        self.assertEqual(result['status'], TestStatus.RUNNING.value)
        self.assertEqual(result['modules'], modules)
        self.assertEqual(result['operator'], operator)
        self.assertIn('start_time', result)
        self.assertIn('expected_end_time', result)

        # Verify engine state
        self.assertEqual(self.engine.status, TestStatus.RUNNING)
        self.assertIsNotNone(self.engine.start_time)

    def test_start_test_insufficient_samples(self):
        """Test starting test with insufficient samples"""
        modules = ["MOD001"]  # Only 1 module, need at least 3
        operator = "John Doe"

        with self.assertRaises(ValueError):
            self.engine.start_test(modules, operator)

    def test_record_measurement(self):
        """Test recording a measurement"""
        self.engine.start_test(["MOD001", "MOD002", "MOD003"], "John Doe")

        self.engine.record_measurement("temperature", 85.0, "°C")

        # Verify measurement was recorded
        self.assertEqual(len(self.engine.measurements), 1)

        measurement = self.engine.measurements[0]
        self.assertEqual(measurement['parameter'], "temperature")
        self.assertEqual(measurement['value'], 85.0)
        self.assertEqual(measurement['unit'], "°C")
        self.assertEqual(measurement['test_id'], self.test_id)

    def test_record_measurement_out_of_tolerance(self):
        """Test recording measurement that triggers alert"""
        self.engine.start_test(["MOD001", "MOD002", "MOD003"], "John Doe")

        # Record temperature way out of tolerance
        self.engine.record_measurement("temperature", 95.0, "°C")

        # Should create an alert
        self.assertGreater(len(self.engine.alerts), 0)

        alert = self.engine.alerts[0]
        self.assertEqual(alert['severity'], "WARNING")
        self.assertIn('temperature', alert['message'].lower())

    def test_record_deviation(self):
        """Test recording a deviation"""
        self.engine.start_test(["MOD001", "MOD002", "MOD003"], "John Doe")

        self.engine.record_deviation(
            "Chamber door opened during test",
            "MINOR",
            "Door closed immediately, minimal impact"
        )

        # Verify deviation was recorded
        self.assertEqual(len(self.engine.deviations), 1)

        deviation = self.engine.deviations[0]
        self.assertEqual(deviation['severity'], "MINOR")
        self.assertIn('door', deviation['description'].lower())

    def test_advance_step(self):
        """Test advancing test steps"""
        self.engine.start_test(["MOD001", "MOD002", "MOD003"], "John Doe")

        initial_step = self.engine.current_step
        result = self.engine.advance_step()

        # Verify step or cycle advanced
        self.assertTrue(
            self.engine.current_step > initial_step or
            self.engine.current_cycle > 0
        )

    def test_complete_test(self):
        """Test completing a test"""
        self.engine.start_test(["MOD001", "MOD002", "MOD003"], "John Doe")

        self.engine.complete_test()

        # Verify test completion
        self.assertEqual(self.engine.status, TestStatus.COMPLETED)
        self.assertIsNotNone(self.engine.end_time)

    def test_abort_test(self):
        """Test aborting a test"""
        self.engine.start_test(["MOD001", "MOD002", "MOD003"], "John Doe")

        reason = "Equipment failure"
        self.engine.abort_test(reason)

        # Verify test abort
        self.assertEqual(self.engine.status, TestStatus.ABORTED)
        self.assertIsNotNone(self.engine.end_time)
        self.assertGreater(len(self.engine.deviations), 0)

    def test_get_status(self):
        """Test getting test status"""
        self.engine.start_test(["MOD001", "MOD002", "MOD003"], "John Doe")

        status = self.engine.get_status()

        # Verify status structure
        self.assertEqual(status['test_id'], self.test_id)
        self.assertEqual(status['status'], TestStatus.RUNNING.value)
        self.assertIn('current_step', status)
        self.assertIn('current_cycle', status)
        self.assertIn('progress_percent', status)
        self.assertIn('total_measurements', status)
        self.assertIn('total_alerts', status)
        self.assertIn('total_deviations', status)

    def test_evaluate_acceptance_criteria(self):
        """Test evaluating acceptance criteria"""
        self.engine.start_test(["MOD001", "MOD002", "MOD003"], "John Doe")

        pre_test = {'Pmax': 300.0, 'Voc': 40.0, 'Isc': 9.0}
        post_test = {'Pmax': 288.0, 'Voc': 39.5, 'Isc': 8.9}  # 4% degradation

        result = self.engine.evaluate_acceptance_criteria(pre_test, post_test)

        # Verify result structure
        self.assertIn('overall_pass', result)
        self.assertIn('electrical_pass', result)
        self.assertIn('details', result)
        self.assertIn('pass_fail', result)

        # Should pass (4% < 5% limit)
        self.assertTrue(result['overall_pass'])
        self.assertEqual(result['pass_fail'], 'PASS')

    def test_evaluate_acceptance_criteria_fail(self):
        """Test failing acceptance criteria"""
        self.engine.start_test(["MOD001", "MOD002", "MOD003"], "John Doe")

        pre_test = {'Pmax': 300.0, 'Voc': 40.0, 'Isc': 9.0}
        post_test = {'Pmax': 280.0, 'Voc': 39.0, 'Isc': 8.8}  # 6.67% degradation

        result = self.engine.evaluate_acceptance_criteria(pre_test, post_test)

        # Should fail (6.67% > 5% limit)
        self.assertFalse(result['overall_pass'])
        self.assertEqual(result['pass_fail'], 'FAIL')


if __name__ == '__main__':
    unittest.main()
