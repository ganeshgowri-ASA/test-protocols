"""
Unit tests for WIND-001 Wind Load Test Protocol
"""

import unittest
import tempfile
import json
from pathlib import Path
from datetime import datetime
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from protocols.wind_001 import (
    WindLoadTest,
    ElectricalPerformance,
    CycleMeasurement,
    TestStatus,
    LoadType
)


class TestElectricalPerformance(unittest.TestCase):
    """Test ElectricalPerformance class"""

    def test_create_electrical_performance(self):
        """Test creating an ElectricalPerformance instance"""
        perf = ElectricalPerformance(
            voc=48.5,
            isc=10.2,
            vmp=40.0,
            imp=10.0,
            pmax=400.0
        )
        self.assertEqual(perf.voc, 48.5)
        self.assertEqual(perf.pmax, 400.0)

    def test_calculate_degradation(self):
        """Test power degradation calculation"""
        baseline = ElectricalPerformance(
            voc=48.5, isc=10.2, vmp=40.0, imp=10.0, pmax=400.0
        )
        post_test = ElectricalPerformance(
            voc=48.3, isc=10.1, vmp=39.8, imp=9.9, pmax=394.0
        )

        degradation = post_test.calculate_degradation(baseline)
        self.assertAlmostEqual(degradation, 1.5, places=1)

    def test_zero_degradation(self):
        """Test zero power degradation"""
        baseline = ElectricalPerformance(
            voc=48.5, isc=10.2, vmp=40.0, imp=10.0, pmax=400.0
        )
        post_test = ElectricalPerformance(
            voc=48.5, isc=10.2, vmp=40.0, imp=10.0, pmax=400.0
        )

        degradation = post_test.calculate_degradation(baseline)
        self.assertEqual(degradation, 0.0)


class TestCycleMeasurement(unittest.TestCase):
    """Test CycleMeasurement class"""

    def test_create_cycle_measurement(self):
        """Test creating a CycleMeasurement instance"""
        measurement = CycleMeasurement(
            cycle_number=1,
            timestamp=datetime.now().isoformat(),
            actual_pressure=2400.0,
            deflection_center=15.5,
            deflection_edges=[10.2, 11.5, 10.8, 11.0],
            observations="Normal deflection"
        )
        self.assertEqual(measurement.cycle_number, 1)
        self.assertEqual(measurement.actual_pressure, 2400.0)
        self.assertEqual(len(measurement.deflection_edges), 4)

    def test_to_dict(self):
        """Test converting measurement to dictionary"""
        measurement = CycleMeasurement(
            cycle_number=1,
            timestamp=datetime.now().isoformat(),
            actual_pressure=2400.0,
            deflection_center=15.5,
            deflection_edges=[10.2, 11.5, 10.8, 11.0],
            observations="Normal"
        )
        data = measurement.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data['cycle_number'], 1)
        self.assertIn('deflection_edges', data)


class TestWindLoadTest(unittest.TestCase):
    """Test WindLoadTest protocol implementation"""

    def setUp(self):
        """Set up test fixtures"""
        self.protocol = WindLoadTest()
        self.test_metadata = {
            "test_id": "WIND-001-TEST-001",
            "operator": "Test Operator",
            "standard": "IEC 61215-2:2021",
            "equipment_id": "WT-001",
            "calibration_date": "2024-01-15"
        }
        self.sample_info = {
            "sample_id": "TEST-SAMPLE-001",
            "manufacturer": "Test Manufacturer",
            "model": "TEST-400",
            "serial_number": "SN12345",
            "technology": "mono-Si",
            "rated_power": 400.0,
            "dimensions": {
                "length": 1755,
                "width": 1038,
                "thickness": 35
            }
        }
        self.test_parameters = {
            "load_type": "cyclic",
            "pressure": 2400,
            "duration": 60,
            "cycles": 3,
            "temperature": 25,
            "humidity": 50,
            "mounting_configuration": "fixed_tilt"
        }

    def test_initialize_test(self):
        """Test initializing a new wind load test"""
        test_data = self.protocol.initialize_test(
            self.test_metadata,
            self.sample_info,
            self.test_parameters
        )

        self.assertIsInstance(test_data, dict)
        self.assertEqual(test_data['test_metadata']['test_id'], "WIND-001-TEST-001")
        self.assertEqual(test_data['sample_info']['sample_id'], "TEST-SAMPLE-001")
        self.assertEqual(test_data['test_parameters']['pressure'], 2400)
        self.assertEqual(test_data['results']['test_status'], TestStatus.IN_PROGRESS.value)

    def test_record_pre_test_measurements(self):
        """Test recording pre-test measurements"""
        self.protocol.initialize_test(
            self.test_metadata,
            self.sample_info,
            self.test_parameters
        )

        pre_perf = ElectricalPerformance(
            voc=48.5, isc=10.2, vmp=40.0, imp=10.0, pmax=400.0
        )

        self.protocol.record_pre_test_measurements(
            visual_inspection="No defects observed",
            electrical_performance=pre_perf,
            insulation_resistance=500.0
        )

        measurements = self.protocol.test_data['measurements']['pre_test']
        self.assertIn('visual_inspection', measurements)
        self.assertIn('electrical_performance', measurements)
        self.assertEqual(measurements['insulation_resistance'], 500.0)
        self.assertEqual(measurements['electrical_performance']['pmax'], 400.0)

    def test_record_cycle_measurements(self):
        """Test recording cycle measurements"""
        self.protocol.initialize_test(
            self.test_metadata,
            self.sample_info,
            self.test_parameters
        )

        for i in range(1, 4):
            measurement = CycleMeasurement(
                cycle_number=i,
                timestamp=datetime.now().isoformat(),
                actual_pressure=2400.0,
                deflection_center=15.5,
                deflection_edges=[10.2, 11.5, 10.8, 11.0],
                observations="Normal"
            )
            self.protocol.record_cycle_measurement(measurement)

        cycle_data = self.protocol.test_data['measurements']['during_test']
        self.assertEqual(len(cycle_data), 3)
        self.assertEqual(cycle_data[0]['cycle_number'], 1)
        self.assertEqual(cycle_data[2]['cycle_number'], 3)

    def test_record_post_test_measurements(self):
        """Test recording post-test measurements"""
        self.protocol.initialize_test(
            self.test_metadata,
            self.sample_info,
            self.test_parameters
        )

        post_perf = ElectricalPerformance(
            voc=48.3, isc=10.1, vmp=39.8, imp=9.9, pmax=394.0
        )

        self.protocol.record_post_test_measurements(
            visual_inspection="No defects after testing",
            electrical_performance=post_perf,
            insulation_resistance=480.0,
            defects_observed=["none"]
        )

        measurements = self.protocol.test_data['measurements']['post_test']
        self.assertIn('visual_inspection', measurements)
        self.assertEqual(measurements['insulation_resistance'], 480.0)
        self.assertEqual(measurements['electrical_performance']['pmax'], 394.0)

    def test_calculate_results_pass(self):
        """Test calculating results for a passing test"""
        self.protocol.initialize_test(
            self.test_metadata,
            self.sample_info,
            self.test_parameters
        )

        # Pre-test measurements
        pre_perf = ElectricalPerformance(
            voc=48.5, isc=10.2, vmp=40.0, imp=10.0, pmax=400.0
        )
        self.protocol.record_pre_test_measurements(
            visual_inspection="No defects",
            electrical_performance=pre_perf,
            insulation_resistance=500.0
        )

        # Cycle measurements
        for i in range(1, 4):
            measurement = CycleMeasurement(
                cycle_number=i,
                timestamp=datetime.now().isoformat(),
                actual_pressure=2400.0,
                deflection_center=15.5,
                deflection_edges=[10.2, 11.5, 10.8, 11.0]
            )
            self.protocol.record_cycle_measurement(measurement)

        # Post-test measurements (minimal degradation)
        post_perf = ElectricalPerformance(
            voc=48.4, isc=10.1, vmp=39.9, imp=9.95, pmax=397.0
        )
        self.protocol.record_post_test_measurements(
            visual_inspection="No defects after testing",
            electrical_performance=post_perf,
            insulation_resistance=490.0,
            defects_observed=["none"]
        )

        # Calculate results
        results = self.protocol.calculate_results()

        self.assertEqual(results['test_status'], TestStatus.PASS.value)
        self.assertLess(results['power_degradation'], 5.0)
        self.assertEqual(len(results['failure_modes']), 0)

    def test_calculate_results_fail_power_degradation(self):
        """Test calculating results for a test failing due to power degradation"""
        self.protocol.initialize_test(
            self.test_metadata,
            self.sample_info,
            self.test_parameters
        )

        # Pre-test measurements
        pre_perf = ElectricalPerformance(
            voc=48.5, isc=10.2, vmp=40.0, imp=10.0, pmax=400.0
        )
        self.protocol.record_pre_test_measurements(
            visual_inspection="No defects",
            electrical_performance=pre_perf,
            insulation_resistance=500.0
        )

        # Cycle measurements
        measurement = CycleMeasurement(
            cycle_number=1,
            timestamp=datetime.now().isoformat(),
            actual_pressure=2400.0,
            deflection_center=15.5,
            deflection_edges=[10.2, 11.5, 10.8, 11.0]
        )
        self.protocol.record_cycle_measurement(measurement)

        # Post-test measurements (excessive degradation)
        post_perf = ElectricalPerformance(
            voc=47.0, isc=9.5, vmp=38.0, imp=9.0, pmax=342.0  # >10% degradation
        )
        self.protocol.record_post_test_measurements(
            visual_inspection="No defects",
            electrical_performance=post_perf,
            insulation_resistance=490.0,
            defects_observed=["none"]
        )

        # Calculate results
        results = self.protocol.calculate_results()

        self.assertEqual(results['test_status'], TestStatus.FAIL.value)
        self.assertGreater(results['power_degradation'], 5.0)
        self.assertGreater(len(results['failure_modes']), 0)

    def test_calculate_results_fail_insulation(self):
        """Test calculating results for a test failing due to insulation resistance"""
        self.protocol.initialize_test(
            self.test_metadata,
            self.sample_info,
            self.test_parameters
        )

        # Pre-test measurements
        pre_perf = ElectricalPerformance(
            voc=48.5, isc=10.2, vmp=40.0, imp=10.0, pmax=400.0
        )
        self.protocol.record_pre_test_measurements(
            visual_inspection="No defects",
            electrical_performance=pre_perf,
            insulation_resistance=500.0
        )

        # Cycle measurement
        measurement = CycleMeasurement(
            cycle_number=1,
            timestamp=datetime.now().isoformat(),
            actual_pressure=2400.0,
            deflection_center=15.5,
            deflection_edges=[10.2, 11.5, 10.8, 11.0]
        )
        self.protocol.record_cycle_measurement(measurement)

        # Post-test measurements (low insulation resistance)
        post_perf = ElectricalPerformance(
            voc=48.4, isc=10.1, vmp=39.9, imp=9.95, pmax=397.0
        )
        self.protocol.record_post_test_measurements(
            visual_inspection="No defects",
            electrical_performance=post_perf,
            insulation_resistance=30.0,  # Below 40 MΩ limit
            defects_observed=["none"]
        )

        # Calculate results
        results = self.protocol.calculate_results()

        self.assertEqual(results['test_status'], TestStatus.FAIL.value)
        self.assertGreater(len(results['failure_modes']), 0)

    def test_validate_test_data_valid(self):
        """Test validating complete test data"""
        self.protocol.initialize_test(
            self.test_metadata,
            self.sample_info,
            self.test_parameters
        )

        # Add all required measurements
        pre_perf = ElectricalPerformance(
            voc=48.5, isc=10.2, vmp=40.0, imp=10.0, pmax=400.0
        )
        self.protocol.record_pre_test_measurements(
            visual_inspection="No defects",
            electrical_performance=pre_perf,
            insulation_resistance=500.0
        )

        measurement = CycleMeasurement(
            cycle_number=1,
            timestamp=datetime.now().isoformat(),
            actual_pressure=2400.0,
            deflection_center=15.5,
            deflection_edges=[10.2, 11.5, 10.8, 11.0]
        )
        self.protocol.record_cycle_measurement(measurement)

        post_perf = ElectricalPerformance(
            voc=48.4, isc=10.1, vmp=39.9, imp=9.95, pmax=397.0
        )
        self.protocol.record_post_test_measurements(
            visual_inspection="No defects",
            electrical_performance=post_perf,
            insulation_resistance=490.0,
            defects_observed=["none"]
        )

        self.protocol.calculate_results()

        is_valid, errors = self.protocol.validate_test_data()
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_validate_test_data_missing_measurements(self):
        """Test validating incomplete test data"""
        self.protocol.initialize_test(
            self.test_metadata,
            self.sample_info,
            self.test_parameters
        )

        is_valid, errors = self.protocol.validate_test_data()
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)

    def test_export_and_import_test_data(self):
        """Test exporting and importing test data"""
        self.protocol.initialize_test(
            self.test_metadata,
            self.sample_info,
            self.test_parameters
        )

        # Add some test data
        pre_perf = ElectricalPerformance(
            voc=48.5, isc=10.2, vmp=40.0, imp=10.0, pmax=400.0
        )
        self.protocol.record_pre_test_measurements(
            visual_inspection="No defects",
            electrical_performance=pre_perf,
            insulation_resistance=500.0
        )

        # Export to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)

        self.protocol.export_test_data(temp_path)

        # Create new protocol instance and import
        new_protocol = WindLoadTest()
        new_protocol.import_test_data(temp_path)

        # Verify data matches
        self.assertEqual(
            new_protocol.test_data['test_metadata']['test_id'],
            self.test_metadata['test_id']
        )
        self.assertEqual(
            new_protocol.test_data['measurements']['pre_test']['insulation_resistance'],
            500.0
        )

        # Cleanup
        temp_path.unlink()

    def test_generate_summary_report(self):
        """Test generating summary report"""
        self.protocol.initialize_test(
            self.test_metadata,
            self.sample_info,
            self.test_parameters
        )

        # Add measurements
        pre_perf = ElectricalPerformance(
            voc=48.5, isc=10.2, vmp=40.0, imp=10.0, pmax=400.0
        )
        self.protocol.record_pre_test_measurements(
            visual_inspection="No defects",
            electrical_performance=pre_perf,
            insulation_resistance=500.0
        )

        measurement = CycleMeasurement(
            cycle_number=1,
            timestamp=datetime.now().isoformat(),
            actual_pressure=2400.0,
            deflection_center=15.5,
            deflection_edges=[10.2, 11.5, 10.8, 11.0]
        )
        self.protocol.record_cycle_measurement(measurement)

        post_perf = ElectricalPerformance(
            voc=48.4, isc=10.1, vmp=39.9, imp=9.95, pmax=397.0
        )
        self.protocol.record_post_test_measurements(
            visual_inspection="No defects",
            electrical_performance=post_perf,
            insulation_resistance=490.0,
            defects_observed=["none"]
        )

        self.protocol.calculate_results()

        # Generate report
        report = self.protocol.generate_summary_report()

        self.assertIsInstance(report, str)
        self.assertIn("WIND-001", report)
        self.assertIn(self.test_metadata['test_id'], report)
        self.assertIn(self.sample_info['sample_id'], report)
        self.assertIn("Status:", report)


def run_tests():
    """Run all tests"""
    unittest.main()


if __name__ == '__main__':
    run_tests()
