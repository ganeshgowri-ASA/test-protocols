"""
Unit tests for core modules (protocol_loader, test_runner, data_validator).
"""

import unittest
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.protocol_loader import ProtocolLoader
from core.test_runner import TestRunner, TestRun, TestStatus, PhaseStatus
from core.data_validator import DataValidator


class TestProtocolLoader(unittest.TestCase):
    """Test cases for ProtocolLoader."""

    def setUp(self):
        """Set up test fixtures."""
        self.loader = ProtocolLoader()

    def test_load_jbox001_protocol(self):
        """Test loading JBOX-001 protocol."""
        protocol = self.loader.load_protocol("JBOX-001")

        self.assertEqual(protocol['protocol_id'], "JBOX-001")
        self.assertEqual(protocol['name'], "Junction Box Degradation Test")
        self.assertEqual(protocol['category'], "Degradation")
        self.assertEqual(protocol['version'], "1.0.0")

    def test_protocol_has_required_fields(self):
        """Test that protocol has all required fields."""
        protocol = self.loader.load_protocol("JBOX-001")

        required_fields = [
            'protocol_id', 'name', 'version', 'category',
            'metadata', 'test_phases', 'measurements', 'qc_criteria'
        ]

        for field in required_fields:
            self.assertIn(field, protocol, f"Protocol missing required field: {field}")

    def test_protocol_has_six_phases(self):
        """Test that JBOX-001 has 6 test phases."""
        protocol = self.loader.load_protocol("JBOX-001")
        self.assertEqual(len(protocol['test_phases']), 6)

    def test_protocol_has_measurements(self):
        """Test that protocol has measurement definitions."""
        protocol = self.loader.load_protocol("JBOX-001")
        self.assertGreater(len(protocol['measurements']), 0)

        # Check first measurement structure
        measurement = protocol['measurements'][0]
        self.assertIn('measurement_id', measurement)
        self.assertIn('name', measurement)
        self.assertIn('type', measurement)
        self.assertIn('unit', measurement)

    def test_list_protocols(self):
        """Test listing available protocols."""
        protocols = self.loader.list_protocols()
        self.assertGreater(len(protocols), 0)

        # Check that JBOX-001 is in the list
        protocol_ids = [p['protocol_id'] for p in protocols]
        self.assertIn('JBOX-001', protocol_ids)

    def test_get_protocol_metadata(self):
        """Test getting protocol metadata."""
        metadata = self.loader.get_protocol_metadata("JBOX-001")

        self.assertIn('description', metadata)
        self.assertIn('standards', metadata)
        self.assertIn('author', metadata)

    def test_get_test_phases(self):
        """Test getting test phases."""
        phases = self.loader.get_test_phases("JBOX-001")

        self.assertEqual(len(phases), 6)
        self.assertEqual(phases[0]['phase_id'], 'P1')
        self.assertEqual(phases[0]['name'], 'Initial Characterization')

    def test_get_qc_criteria(self):
        """Test getting QC criteria."""
        qc_criteria = self.loader.get_qc_criteria("JBOX-001")

        self.assertIn('acceptance_criteria', qc_criteria)
        self.assertGreater(len(qc_criteria['acceptance_criteria']), 0)


class TestTestRunner(unittest.TestCase):
    """Test cases for TestRunner."""

    def setUp(self):
        """Set up test fixtures."""
        self.loader = ProtocolLoader()
        self.protocol = self.loader.load_protocol("JBOX-001")
        self.runner = TestRunner()

    def test_create_test_run(self):
        """Test creating a new test run."""
        test_run = self.runner.create_test_run(
            protocol=self.protocol,
            test_run_id="TEST-001",
            operator="John Doe",
            sample_id="MODULE-001"
        )

        self.assertEqual(test_run.test_run_id, "TEST-001")
        self.assertEqual(test_run.operator, "John Doe")
        self.assertEqual(test_run.sample_id, "MODULE-001")
        self.assertEqual(test_run.status, TestStatus.PENDING)

    def test_start_test_run(self):
        """Test starting a test run."""
        test_run = self.runner.create_test_run(
            protocol=self.protocol,
            test_run_id="TEST-002",
            operator="Jane Smith",
            sample_id="MODULE-002"
        )

        self.runner.start_test_run("TEST-002")

        self.assertEqual(test_run.status, TestStatus.IN_PROGRESS)
        self.assertIsNotNone(test_run.start_time)

    def test_add_measurement(self):
        """Test adding a measurement to a test run."""
        test_run = self.runner.create_test_run(
            protocol=self.protocol,
            test_run_id="TEST-003",
            operator="Bob Johnson",
            sample_id="MODULE-003"
        )

        test_run.add_measurement("M1", 5.2, "mΩ")

        self.assertEqual(len(test_run.measurements), 1)
        self.assertEqual(test_run.measurements[0]['measurement_id'], "M1")
        self.assertEqual(test_run.measurements[0]['value'], 5.2)
        self.assertEqual(test_run.measurements[0]['unit'], "mΩ")

    def test_add_note(self):
        """Test adding a note to a test run."""
        test_run = self.runner.create_test_run(
            protocol=self.protocol,
            test_run_id="TEST-004",
            operator="Alice Brown",
            sample_id="MODULE-004"
        )

        test_run.add_note("Test note", "info")

        self.assertEqual(len(test_run.notes), 1)
        self.assertEqual(test_run.notes[0]['note'], "Test note")
        self.assertEqual(test_run.notes[0]['category'], "info")

    def test_set_phase(self):
        """Test setting phase status."""
        test_run = self.runner.create_test_run(
            protocol=self.protocol,
            test_run_id="TEST-005",
            operator="Charlie Wilson",
            sample_id="MODULE-005"
        )

        test_run.set_phase("P1", PhaseStatus.IN_PROGRESS)

        self.assertIn("P1", test_run.phase_results)
        self.assertEqual(test_run.phase_results["P1"]["status"], PhaseStatus.IN_PROGRESS.value)
        self.assertIsNotNone(test_run.phase_results["P1"]["start_time"])

    def test_complete_test_run(self):
        """Test completing a test run."""
        test_run = self.runner.create_test_run(
            protocol=self.protocol,
            test_run_id="TEST-006",
            operator="Diana Martinez",
            sample_id="MODULE-006"
        )

        self.runner.start_test_run("TEST-006")
        self.runner.complete_test_run("TEST-006")

        self.assertEqual(test_run.status, TestStatus.COMPLETED)
        self.assertIsNotNone(test_run.end_time)

    def test_get_summary(self):
        """Test getting test run summary."""
        test_run = self.runner.create_test_run(
            protocol=self.protocol,
            test_run_id="TEST-007",
            operator="Eve Davis",
            sample_id="MODULE-007"
        )

        self.runner.start_test_run("TEST-007")
        test_run.add_measurement("M1", 5.5, "mΩ")
        test_run.set_phase("P1", PhaseStatus.COMPLETED)

        summary = test_run.get_summary()

        self.assertEqual(summary['test_run_id'], "TEST-007")
        self.assertEqual(summary['sample_id'], "MODULE-007")
        self.assertEqual(summary['measurements_count'], 1)
        self.assertEqual(summary['phases_completed'], 1)


class TestDataValidator(unittest.TestCase):
    """Test cases for DataValidator."""

    def setUp(self):
        """Set up test fixtures."""
        self.loader = ProtocolLoader()
        self.protocol = self.loader.load_protocol("JBOX-001")
        self.validator = DataValidator(self.protocol)

    def test_validate_measurement_valid(self):
        """Test validating a valid measurement."""
        is_valid, error = self.validator.validate_measurement("M1", 5.2)

        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_validate_measurement_out_of_range(self):
        """Test validating an out-of-range measurement."""
        is_valid, error = self.validator.validate_measurement("M1", 150.0)

        self.assertFalse(is_valid)
        self.assertIsNotNone(error)

    def test_calculate_degradation_metrics(self):
        """Test calculating degradation metrics."""
        initial = {'M1': 5.0, 'M5': 300.0}
        final = {'M1': 5.5, 'M5': 288.0}

        metrics = self.validator.calculate_degradation_metrics(initial, final)

        self.assertIn('M1_absolute_change', metrics)
        self.assertIn('M5_percentage_change', metrics)
        self.assertIn('power_degradation_percentage', metrics)

        # Check power degradation
        self.assertEqual(metrics['M5_absolute_change'], -12.0)
        self.assertAlmostEqual(metrics['power_degradation_percentage'], 4.0, places=1)

    def test_evaluate_acceptance_criteria_pass(self):
        """Test evaluating acceptance criteria - passing case."""
        test_data = {
            'power_degradation_percentage': 3.0,
            'resistance_increase_percentage': 10.0,
            'insulation_resistance_final': 50.0,
            'diode_voltage_drift_percentage': 5.0,
            'visual_defects_critical': 0,
            'weight_gain_percentage': 0.5,
            'max_temperature_rise': 35.0
        }

        results = self.validator.evaluate_acceptance_criteria(test_data)

        self.assertTrue(results['overall_pass'])
        self.assertEqual(len(results['critical_failures']), 0)

    def test_evaluate_acceptance_criteria_fail(self):
        """Test evaluating acceptance criteria - failing case."""
        test_data = {
            'power_degradation_percentage': 7.0,  # Exceeds 5% limit
            'resistance_increase_percentage': 10.0,
            'insulation_resistance_final': 30.0,  # Below 40 MΩ limit
            'diode_voltage_drift_percentage': 5.0,
            'visual_defects_critical': 0,
            'weight_gain_percentage': 0.5,
            'max_temperature_rise': 35.0
        }

        results = self.validator.evaluate_acceptance_criteria(test_data)

        self.assertFalse(results['overall_pass'])
        self.assertGreater(len(results['critical_failures']), 0)

    def test_detect_outliers(self):
        """Test outlier detection."""
        measurements = [
            {'measurement_id': 'M1', 'value': 5.0},
            {'measurement_id': 'M1', 'value': 5.1},
            {'measurement_id': 'M1', 'value': 5.2},
            {'measurement_id': 'M1', 'value': 5.3},
            {'measurement_id': 'M1', 'value': 10.0},  # Outlier
        ]

        outliers = self.validator.detect_outliers(measurements, 'M1', method='iqr')

        self.assertGreater(len(outliers), 0)

    def test_generate_validation_report(self):
        """Test generating validation report."""
        test_run_data = {
            'test_run_id': 'TEST-001',
            'measurements': [
                {'measurement_id': 'M1', 'value': 5.2},
                {'measurement_id': 'M2', 'value': 0.65},
            ]
        }

        report = self.validator.generate_validation_report(test_run_data)

        self.assertIn('test_run_id', report)
        self.assertIn('protocol_id', report)
        self.assertIn('data_quality', report)
        self.assertEqual(report['protocol_id'], 'JBOX-001')


class TestJBOX001Integration(unittest.TestCase):
    """Integration tests for JBOX-001 protocol."""

    def setUp(self):
        """Set up test fixtures."""
        from protocols.jbox001 import JBOX001Protocol
        self.protocol = JBOX001Protocol()

    def test_create_test_run(self):
        """Test creating a JBOX-001 test run."""
        test_run = self.protocol.create_test_run(
            sample_id="MODULE-JBOX-001",
            operator="Test Operator"
        )

        self.assertIsNotNone(test_run)
        self.assertEqual(test_run.sample_id, "MODULE-JBOX-001")

    def test_run_initial_characterization(self):
        """Test running initial characterization phase."""
        test_run = self.protocol.create_test_run(
            sample_id="MODULE-JBOX-002",
            operator="Test Operator"
        )

        self.protocol.runner.start_test_run(test_run.test_run_id)

        self.protocol.run_initial_characterization(
            test_run=test_run,
            visual_inspection={'defects_count': 0, 'notes': 'Clean'},
            contact_resistance=5.2,
            diode_voltage=[0.65, 0.64, 0.66],
            insulation_resistance=100.0,
            iv_curve_data={'pmax': 300.0, 'voc': 40.5, 'isc': 9.2}
        )

        self.assertIn('P1', test_run.phase_results)
        self.assertEqual(test_run.phase_results['P1']['status'], PhaseStatus.COMPLETED.value)
        self.assertGreater(len(test_run.measurements), 0)

    def test_full_test_workflow(self):
        """Test a complete test workflow."""
        test_run = self.protocol.create_test_run(
            sample_id="MODULE-JBOX-003",
            operator="Test Operator"
        )

        self.protocol.runner.start_test_run(test_run.test_run_id)

        # Initial characterization
        self.protocol.run_initial_characterization(
            test_run=test_run,
            visual_inspection={'defects_count': 0, 'notes': 'Clean'},
            contact_resistance=5.0,
            diode_voltage=[0.65, 0.64, 0.66],
            insulation_resistance=100.0,
            iv_curve_data={'pmax': 300.0, 'voc': 40.5, 'isc': 9.2}
        )

        # Thermal cycling
        self.protocol.run_thermal_cycling(test_run, cycles_completed=200)

        # Final characterization
        self.protocol.run_final_characterization(
            test_run=test_run,
            visual_inspection={'defects_count': 1, 'notes': 'Minor discoloration'},
            contact_resistance=5.5,
            diode_voltage=[0.66, 0.65, 0.67],
            insulation_resistance=95.0,
            iv_curve_data={'pmax': 288.0, 'voc': 40.3, 'isc': 9.1}
        )

        self.protocol.runner.complete_test_run(test_run.test_run_id)

        # Check test completion
        self.assertEqual(test_run.status, TestStatus.COMPLETED)
        self.assertIsNotNone(test_run.qc_results)

        # Generate report
        report = self.protocol.generate_test_report(test_run)
        self.assertIn('protocol', report)
        self.assertIn('test_run', report)
        self.assertIn('validation', report)


if __name__ == '__main__':
    unittest.main()
