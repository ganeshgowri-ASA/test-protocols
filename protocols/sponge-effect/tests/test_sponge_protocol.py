"""
Unit Tests for SPONGE-001 Protocol Implementation

Tests protocol specification loading, test plan creation, data recording,
analysis calculations, and report generation.
"""

import unittest
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from implementation import (
    SpongeProtocol, TestParameters, TestPhase, TestStatus,
    Measurement, AnalysisResults
)


class TestProtocolSpecification(unittest.TestCase):
    """Test protocol specification loading and validation"""

    def setUp(self):
        """Set up test fixtures"""
        self.protocol = SpongeProtocol()

    def test_spec_loading(self):
        """Test that specification is loaded correctly"""
        self.assertIsNotNone(self.protocol.spec)
        self.assertEqual(self.protocol.spec['protocol_id'], 'SPONGE-001')
        self.assertEqual(self.protocol.spec['protocol_name'], 'Sponge Effect Testing')
        self.assertEqual(self.protocol.spec['version'], '1.0.0')
        self.assertEqual(self.protocol.spec['category'], 'degradation')

    def test_spec_has_required_sections(self):
        """Test that spec contains all required sections"""
        required_sections = [
            'protocol_id', 'protocol_name', 'version', 'category',
            'test_parameters', 'measurement_points', 'data_analysis',
            'quality_control', 'reporting', 'database_schema'
        ]

        for section in required_sections:
            self.assertIn(section, self.protocol.spec,
                         f"Missing required section: {section}")

    def test_test_parameters_structure(self):
        """Test test parameters structure in spec"""
        params = self.protocol.spec['test_parameters']

        # Check key parameters exist
        key_params = [
            'humidity_cycles', 'humid_phase_temperature', 'humid_phase_rh',
            'dry_phase_temperature', 'dry_phase_rh'
        ]

        for param in key_params:
            self.assertIn(param, params)
            self.assertIn('type', params[param])
            self.assertIn('default', params[param])
            self.assertIn('unit', params[param])


class TestTestParameters(unittest.TestCase):
    """Test TestParameters class"""

    def setUp(self):
        """Set up test fixtures"""
        self.protocol = SpongeProtocol()
        self.params = TestParameters()

    def test_default_parameters(self):
        """Test default parameter values"""
        self.assertEqual(self.params.humidity_cycles, 10)
        self.assertEqual(self.params.humid_phase_temperature, 85.0)
        self.assertEqual(self.params.humid_phase_rh, 85.0)
        self.assertEqual(self.params.dry_phase_temperature, 25.0)
        self.assertEqual(self.params.dry_phase_rh, 10.0)

    def test_custom_parameters(self):
        """Test custom parameter values"""
        params = TestParameters(
            humidity_cycles=20,
            humid_phase_temperature=90.0,
            humid_phase_rh=90.0
        )

        self.assertEqual(params.humidity_cycles, 20)
        self.assertEqual(params.humid_phase_temperature, 90.0)
        self.assertEqual(params.humid_phase_rh, 90.0)

    def test_parameter_validation_success(self):
        """Test parameter validation with valid values"""
        errors = self.params.validate(self.protocol.spec)
        self.assertEqual(len(errors), 0)

    def test_parameter_validation_failure(self):
        """Test parameter validation with invalid values"""
        params = TestParameters(
            humidity_cycles=100,  # Above max of 50
            humid_phase_temperature=50.0  # Below min of 60
        )

        errors = params.validate(self.protocol.spec)
        self.assertGreater(len(errors), 0)


class TestTestPlanCreation(unittest.TestCase):
    """Test test plan creation"""

    def setUp(self):
        """Set up test fixtures"""
        self.protocol = SpongeProtocol()
        self.params = TestParameters(humidity_cycles=3)
        self.sample_ids = ['MODULE-001', 'MODULE-002', 'MODULE-003']

    def test_create_test_plan(self):
        """Test test plan creation"""
        test_plan = self.protocol.create_test_plan(self.params, self.sample_ids)

        self.assertIn('test_id', test_plan)
        self.assertIn('protocol_id', test_plan)
        self.assertEqual(test_plan['protocol_id'], 'SPONGE-001')
        self.assertEqual(test_plan['num_samples'], 3)

    def test_test_plan_duration_calculation(self):
        """Test duration calculation in test plan"""
        test_plan = self.protocol.create_test_plan(self.params, self.sample_ids)

        expected_duration = (self.params.humid_phase_duration +
                           self.params.dry_phase_duration) * self.params.humidity_cycles

        self.assertEqual(test_plan['estimated_duration_hours'], expected_duration)

    def test_measurement_schedule(self):
        """Test measurement schedule generation"""
        test_plan = self.protocol.create_test_plan(self.params, self.sample_ids)

        self.assertIn('measurement_schedule', test_plan)
        schedule = test_plan['measurement_schedule']

        # Should have initial + (2 per cycle) + final
        expected_measurements = 1 + (2 * self.params.humidity_cycles) + 1
        self.assertEqual(len(schedule), expected_measurements)

    def test_invalid_parameters_raise_error(self):
        """Test that invalid parameters raise error"""
        params = TestParameters(humidity_cycles=100)  # Invalid

        with self.assertRaises(ValueError):
            self.protocol.create_test_plan(params, self.sample_ids)


class TestDataRecording(unittest.TestCase):
    """Test measurement data recording"""

    def setUp(self):
        """Set up test fixtures"""
        self.protocol = SpongeProtocol()
        self.sample_id = 'MODULE-001'

    def test_record_measurement(self):
        """Test recording a measurement"""
        measurement = self.protocol.record_measurement(
            sample_id=self.sample_id,
            cycle=0,
            phase=TestPhase.INITIAL,
            weight_g=18000.0,
            pmax_w=300.0,
            voc_v=38.5,
            isc_a=9.0,
            ff_percent=76.5
        )

        self.assertIsInstance(measurement, Measurement)
        self.assertEqual(measurement.sample_id, self.sample_id)
        self.assertEqual(measurement.cycle_number, 0)
        self.assertEqual(measurement.phase, TestPhase.INITIAL.value)
        self.assertEqual(measurement.weight_g, 18000.0)

    def test_multiple_measurements(self):
        """Test recording multiple measurements"""
        for i in range(5):
            self.protocol.record_measurement(
                sample_id=self.sample_id,
                cycle=i,
                phase=TestPhase.DRY,
                weight_g=18000.0 + i
            )

        self.assertEqual(len(self.protocol.measurements), 5)

    def test_get_measurements_dataframe(self):
        """Test converting measurements to DataFrame"""
        self.protocol.record_measurement(
            sample_id=self.sample_id,
            cycle=0,
            phase=TestPhase.INITIAL,
            weight_g=18000.0
        )

        df = self.protocol.get_measurements_df()

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 1)
        self.assertIn('sample_id', df.columns)
        self.assertIn('weight_g', df.columns)


class TestMoistureMetrics(unittest.TestCase):
    """Test moisture metric calculations"""

    def setUp(self):
        """Set up test fixtures with sample data"""
        self.protocol = SpongeProtocol()
        self.sample_id = 'MODULE-001'

        # Record initial measurement
        self.protocol.record_measurement(
            sample_id=self.sample_id,
            cycle=0,
            phase=TestPhase.INITIAL,
            weight_g=18000.0
        )

        # Record humid phase measurements
        for cycle in range(1, 4):
            self.protocol.record_measurement(
                sample_id=self.sample_id,
                cycle=cycle,
                phase=TestPhase.HUMID,
                weight_g=18100.0  # +100g moisture gain
            )

            self.protocol.record_measurement(
                sample_id=self.sample_id,
                cycle=cycle,
                phase=TestPhase.DRY,
                weight_g=18020.0  # -80g after drying
            )

    def test_calculate_moisture_metrics(self):
        """Test moisture absorption and desorption calculation"""
        metrics = self.protocol.calculate_moisture_metrics(self.sample_id)

        self.assertIn('moisture_absorption_percent', metrics)
        self.assertIn('moisture_desorption_percent', metrics)
        self.assertIn('sponge_coefficient', metrics)

        # Check absorption calculation
        expected_absorption = ((18100.0 - 18000.0) / 18000.0) * 100
        self.assertAlmostEqual(
            metrics['moisture_absorption_percent'],
            expected_absorption,
            places=2
        )

    def test_sponge_coefficient_calculation(self):
        """Test sponge coefficient calculation"""
        metrics = self.protocol.calculate_moisture_metrics(self.sample_id)

        # Sponge coefficient should be absorption / desorption
        expected_coefficient = (
            metrics['moisture_absorption_percent'] /
            metrics['moisture_desorption_percent']
        )

        self.assertAlmostEqual(
            metrics['sponge_coefficient'],
            expected_coefficient,
            places=3
        )

    def test_no_measurements_raises_error(self):
        """Test that missing measurements raise error"""
        with self.assertRaises(ValueError):
            self.protocol.calculate_moisture_metrics('NONEXISTENT-SAMPLE')


class TestPerformanceDegradation(unittest.TestCase):
    """Test performance degradation calculations"""

    def setUp(self):
        """Set up test fixtures with sample data"""
        self.protocol = SpongeProtocol()
        self.sample_id = 'MODULE-001'

        # Initial performance
        self.protocol.record_measurement(
            sample_id=self.sample_id,
            cycle=0,
            phase=TestPhase.INITIAL,
            pmax_w=300.0,
            voc_v=38.5,
            isc_a=9.0,
            ff_percent=76.5
        )

        # Humid and dry phase measurements
        for cycle in range(1, 4):
            self.protocol.record_measurement(
                sample_id=self.sample_id,
                cycle=cycle,
                phase=TestPhase.HUMID,
                pmax_w=295.0  # 5W loss when humid
            )

            self.protocol.record_measurement(
                sample_id=self.sample_id,
                cycle=cycle,
                phase=TestPhase.DRY,
                pmax_w=298.0  # 2W permanent loss
            )

        # Final measurement
        self.protocol.record_measurement(
            sample_id=self.sample_id,
            cycle=3,
            phase=TestPhase.FINAL,
            pmax_w=297.0,
            voc_v=38.3,
            isc_a=8.95,
            ff_percent=76.0
        )

    def test_calculate_performance_degradation(self):
        """Test performance degradation calculation"""
        metrics = self.protocol.calculate_performance_degradation(self.sample_id)

        self.assertIn('pmax_degradation_percent', metrics)
        self.assertIn('initial_pmax_w', metrics)
        self.assertIn('final_pmax_w', metrics)

        # Check degradation calculation
        expected_degradation = ((300.0 - 297.0) / 300.0) * 100
        self.assertAlmostEqual(
            metrics['pmax_degradation_percent'],
            expected_degradation,
            places=1
        )

    def test_reversible_vs_irreversible_degradation(self):
        """Test reversible and irreversible degradation calculation"""
        metrics = self.protocol.calculate_performance_degradation(self.sample_id)

        self.assertIn('reversible_degradation_percent', metrics)
        self.assertIn('irreversible_degradation_percent', metrics)

        # Reversible should be the difference between humid and dry
        # Irreversible should be permanent loss
        self.assertGreater(metrics['reversible_degradation_percent'], 0)


class TestAnalysis(unittest.TestCase):
    """Test complete sample analysis"""

    def setUp(self):
        """Set up test fixtures with complete data"""
        self.protocol = SpongeProtocol()
        self.sample_id = 'MODULE-001'

        # Create complete test data
        self.protocol.record_measurement(
            sample_id=self.sample_id,
            cycle=0,
            phase=TestPhase.INITIAL,
            weight_g=18000.0,
            pmax_w=300.0,
            voc_v=38.5,
            isc_a=9.0,
            ff_percent=76.5
        )

        for cycle in range(1, 4):
            self.protocol.record_measurement(
                sample_id=self.sample_id,
                cycle=cycle,
                phase=TestPhase.HUMID,
                weight_g=18100.0
            )

            self.protocol.record_measurement(
                sample_id=self.sample_id,
                cycle=cycle,
                phase=TestPhase.DRY,
                weight_g=18020.0,
                pmax_w=298.0,
                voc_v=38.4,
                isc_a=8.98,
                ff_percent=76.3
            )

        self.protocol.record_measurement(
            sample_id=self.sample_id,
            cycle=3,
            phase=TestPhase.FINAL,
            weight_g=18015.0,
            pmax_w=297.5,
            voc_v=38.4,
            isc_a=8.95,
            ff_percent=76.2
        )

    def test_analyze_sample(self):
        """Test complete sample analysis"""
        analysis = self.protocol.analyze_sample(self.sample_id)

        self.assertIsInstance(analysis, AnalysisResults)
        self.assertEqual(analysis.sample_id, self.sample_id)
        self.assertIn(analysis.pass_fail, ['PASS', 'FAIL', 'WARNING'])

    def test_analysis_pass_fail_determination(self):
        """Test pass/fail determination"""
        analysis = self.protocol.analyze_sample(self.sample_id)

        # With small degradation (<5%), should pass
        self.assertEqual(analysis.pass_fail, 'PASS')


class TestReporting(unittest.TestCase):
    """Test report generation"""

    def setUp(self):
        """Set up test fixtures"""
        self.protocol = SpongeProtocol()

        # Create data for multiple samples
        for i, sample_id in enumerate(['MODULE-001', 'MODULE-002']):
            self.protocol.record_measurement(
                sample_id=sample_id,
                cycle=0,
                phase=TestPhase.INITIAL,
                weight_g=18000.0,
                pmax_w=300.0,
                voc_v=38.5,
                isc_a=9.0,
                ff_percent=76.5
            )

            self.protocol.record_measurement(
                sample_id=sample_id,
                cycle=1,
                phase=TestPhase.FINAL,
                weight_g=18020.0,
                pmax_w=298.0,
                voc_v=38.4,
                isc_a=8.98,
                ff_percent=76.3
            )

    def test_generate_report(self):
        """Test report generation"""
        report = self.protocol.generate_report()

        self.assertIn('test_id', report)
        self.assertIn('protocol_id', report)
        self.assertIn('summary', report)
        self.assertIn('sample_results', report)

    def test_report_summary(self):
        """Test report summary section"""
        report = self.protocol.generate_report()
        summary = report['summary']

        self.assertEqual(summary['total_samples'], 2)
        self.assertIn('passed', summary)
        self.assertIn('failed', summary)

    def test_export_data_csv(self):
        """Test CSV export"""
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            exported = self.protocol.export_data(Path(tmpdir), formats=['csv'])

            self.assertIn('csv', exported)
            self.assertTrue(exported['csv'].exists())

    def test_export_data_json(self):
        """Test JSON export"""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            exported = self.protocol.export_data(Path(tmpdir), formats=['json'])

            self.assertIn('json', exported)
            self.assertTrue(exported['json'].exists())

            # Verify JSON is valid
            with open(exported['json'], 'r') as f:
                data = json.load(f)
                self.assertIn('test_id', data)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""

    def test_empty_protocol(self):
        """Test protocol with no measurements"""
        protocol = SpongeProtocol()
        df = protocol.get_measurements_df()

        self.assertTrue(df.empty)

    def test_partial_measurements(self):
        """Test with partial measurements (missing some parameters)"""
        protocol = SpongeProtocol()

        measurement = protocol.record_measurement(
            sample_id='MODULE-001',
            cycle=0,
            phase=TestPhase.INITIAL,
            weight_g=18000.0
            # Missing electrical measurements
        )

        self.assertIsNone(measurement.pmax_w)
        self.assertIsNone(measurement.voc_v)

    def test_measurement_to_dict(self):
        """Test measurement serialization"""
        protocol = SpongeProtocol()

        measurement = protocol.record_measurement(
            sample_id='MODULE-001',
            cycle=0,
            phase=TestPhase.INITIAL,
            weight_g=18000.0,
            pmax_w=300.0
        )

        data = measurement.to_dict()
        self.assertIn('measurement_id', data)
        self.assertIn('timestamp', data)
        self.assertEqual(data['weight_g'], 18000.0)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestProtocolSpecification))
    suite.addTests(loader.loadTestsFromTestCase(TestTestParameters))
    suite.addTests(loader.loadTestsFromTestCase(TestTestPlanCreation))
    suite.addTests(loader.loadTestsFromTestCase(TestDataRecording))
    suite.addTests(loader.loadTestsFromTestCase(TestMoistureMetrics))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformanceDegradation))
    suite.addTests(loader.loadTestsFromTestCase(TestAnalysis))
    suite.addTests(loader.loadTestsFromTestCase(TestReporting))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == '__main__':
    result = run_tests()
    sys.exit(0 if result.wasSuccessful() else 1)
