"""
Unit tests for BifacialProtocol
"""

import unittest
import json
import tempfile
import os
from pathlib import Path
import sys
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from python.protocol import BifacialProtocol
from python.calculator import IVParameters


class TestBifacialProtocol(unittest.TestCase):
    """Test cases for BifacialProtocol class"""

    def setUp(self):
        """Set up test fixtures"""
        self.protocol = BifacialProtocol()

        self.metadata = {
            "protocol_name": "BIFI-001 Bifacial Performance",
            "standard": "IEC 60904-1-2",
            "version": "1.0.0",
            "test_date": "2025-11-13T10:00:00Z",
            "operator": "Test Engineer",
            "facility": "Test Lab"
        }

        self.device_info = {
            "device_id": "TEST-001",
            "manufacturer": "Test Solar",
            "model": "BiModule-500",
            "serial_number": "SN-001",
            "technology": "mono-Si",
            "rated_power_front": 500.0,
            "rated_power_rear": 350.0,
            "bifaciality_factor": 0.70,
            "area_front": 25000.0,
            "area_rear": 25000.0
        }

        self.test_conditions = {
            "front_irradiance": {"value": 1000.0, "tolerance": 2.0, "spectrum": "AM1.5G"},
            "rear_irradiance": {"value": 150.0, "tolerance": 2.0, "spectrum": "AM1.5G"},
            "temperature": {"value": 25.0, "tolerance": 2.0},
            "stc_conditions": True
        }

        # Generate realistic I-V curve
        self.front_iv = self._generate_iv_curve(45.0, 11.0, 50)
        self.rear_iv = self._generate_iv_curve(43.0, 8.0, 50)

    def _generate_iv_curve(self, voc, isc, num_points=50):
        """Generate realistic I-V curve"""
        voltage = np.linspace(0, voc, num_points)
        current = isc * (1 - (voltage / voc) ** 2)
        return [{"voltage": float(v), "current": float(i)} for v, i in zip(voltage, current)]

    def test_load_template(self):
        """Test loading data template"""
        template = self.protocol.load_template()

        self.assertIsInstance(template, dict)
        self.assertIn("metadata", template)
        self.assertIn("device_under_test", template)
        self.assertIn("test_conditions", template)
        self.assertIn("measurements", template)

    def test_create_test(self):
        """Test creating a new test"""
        data = self.protocol.create_test(self.metadata, self.device_info, self.test_conditions)

        self.assertIsNotNone(data)
        self.assertEqual(data["metadata"]["operator"], "Test Engineer")
        self.assertEqual(data["device_under_test"]["device_id"], "TEST-001")
        self.assertEqual(data["test_conditions"]["front_irradiance"]["value"], 1000.0)

    def test_create_test_auto_date(self):
        """Test that test date is auto-generated if not provided"""
        metadata_no_date = self.metadata.copy()
        del metadata_no_date["test_date"]

        data = self.protocol.create_test(metadata_no_date, self.device_info, self.test_conditions)

        self.assertIn("test_date", data["metadata"])
        self.assertIsNotNone(data["metadata"]["test_date"])

    def test_add_iv_measurement_front(self):
        """Test adding front side I-V measurement"""
        self.protocol.create_test(self.metadata, self.device_info, self.test_conditions)

        params = self.protocol.add_iv_measurement(
            "front",
            self.front_iv,
            1000.0,
            25000.0
        )

        self.assertIsInstance(params, IVParameters)
        self.assertGreater(params.pmax, 0)

        # Check data was stored
        front_data = self.protocol.data["measurements"]["front_side"]
        self.assertEqual(len(front_data["iv_curve"]), len(self.front_iv))
        self.assertGreater(front_data["pmax"], 0)

    def test_add_iv_measurement_rear(self):
        """Test adding rear side I-V measurement"""
        self.protocol.create_test(self.metadata, self.device_info, self.test_conditions)

        params = self.protocol.add_iv_measurement(
            "rear",
            self.rear_iv,
            150.0,
            25000.0
        )

        self.assertIsInstance(params, IVParameters)
        self.assertGreater(params.pmax, 0)

        rear_data = self.protocol.data["measurements"]["rear_side"]
        self.assertGreater(rear_data["pmax"], 0)

    def test_add_iv_measurement_invalid_side(self):
        """Test error handling for invalid side"""
        self.protocol.create_test(self.metadata, self.device_info, self.test_conditions)

        with self.assertRaises(ValueError):
            self.protocol.add_iv_measurement("middle", self.front_iv, 1000.0)

    def test_add_iv_measurement_no_test(self):
        """Test error when adding measurement without initializing test"""
        with self.assertRaises(ValueError):
            self.protocol.add_iv_measurement("front", self.front_iv, 1000.0)

    def test_calculate_bifacial_parameters(self):
        """Test calculating bifacial parameters"""
        self.protocol.create_test(self.metadata, self.device_info, self.test_conditions)

        # Add both measurements
        self.protocol.add_iv_measurement("front", self.front_iv, 1000.0, 25000.0)
        self.protocol.add_iv_measurement("rear", self.rear_iv, 150.0, 25000.0)

        # Calculate bifacial parameters
        results = self.protocol.calculate_bifacial_parameters()

        self.assertIn("measured_bifaciality", results)
        self.assertIn("bifacial_gain", results)
        self.assertIn("equivalent_front_efficiency", results)

        self.assertGreater(results["measured_bifaciality"], 0)
        self.assertLess(results["measured_bifaciality"], 1)

    def test_calculate_bifacial_parameters_missing_measurements(self):
        """Test error when calculating without both measurements"""
        self.protocol.create_test(self.metadata, self.device_info, self.test_conditions)

        # Only add front measurement
        self.protocol.add_iv_measurement("front", self.front_iv, 1000.0)

        with self.assertRaises(ValueError):
            self.protocol.calculate_bifacial_parameters()

    def test_run_validation(self):
        """Test running validation"""
        self.protocol.create_test(self.metadata, self.device_info, self.test_conditions)
        self.protocol.add_iv_measurement("front", self.front_iv, 1000.0, 25000.0)
        self.protocol.add_iv_measurement("rear", self.rear_iv, 150.0, 25000.0)
        self.protocol.calculate_bifacial_parameters()

        results = self.protocol.run_validation()

        self.assertIn("overall_valid", results)
        self.assertIn("errors", results)
        self.assertIn("checks", results)

        # Validation checks should be added to QC section
        self.assertIn("validation_checks", self.protocol.data["quality_control"])

    def test_analyze_performance(self):
        """Test performance analysis"""
        self.protocol.create_test(self.metadata, self.device_info, self.test_conditions)
        self.protocol.add_iv_measurement("front", self.front_iv, 1000.0, 25000.0)
        self.protocol.add_iv_measurement("rear", self.rear_iv, 150.0, 25000.0)
        self.protocol.calculate_bifacial_parameters()

        analysis = self.protocol.analyze_performance()

        self.assertIn("pass_fail_status", analysis)
        self.assertIn("deviations", analysis)
        self.assertIn("recommendations", analysis)

        # Should have some deviations since our simulated data differs from rated
        self.assertIsInstance(analysis["deviations"], list)

    def test_save_and_load(self):
        """Test saving and loading test data"""
        self.protocol.create_test(self.metadata, self.device_info, self.test_conditions)
        self.protocol.add_iv_measurement("front", self.front_iv, 1000.0, 25000.0)
        self.protocol.add_iv_measurement("rear", self.rear_iv, 150.0, 25000.0)
        self.protocol.calculate_bifacial_parameters()

        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name

        try:
            self.protocol.save(temp_path)

            # Load into new protocol instance
            new_protocol = BifacialProtocol()
            loaded_data = new_protocol.load(temp_path)

            self.assertEqual(
                loaded_data["device_under_test"]["device_id"],
                self.device_info["device_id"]
            )
            self.assertEqual(
                loaded_data["measurements"]["front_side"]["pmax"],
                self.protocol.data["measurements"]["front_side"]["pmax"]
            )

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_generate_report_data(self):
        """Test generating report data"""
        self.protocol.create_test(self.metadata, self.device_info, self.test_conditions)
        self.protocol.add_iv_measurement("front", self.front_iv, 1000.0, 25000.0)
        self.protocol.add_iv_measurement("rear", self.rear_iv, 150.0, 25000.0)
        self.protocol.calculate_bifacial_parameters()
        self.protocol.run_validation()
        self.protocol.analyze_performance()

        report = self.protocol.generate_report_data()

        self.assertIn("title", report)
        self.assertIn("device", report)
        self.assertIn("conditions", report)
        self.assertIn("results", report)
        self.assertIn("status", report)

        self.assertEqual(report["title"], "BIFI-001 Bifacial Performance Test Report")
        self.assertEqual(report["device"]["id"], "TEST-001")

    def test_complete_workflow(self):
        """Test complete workflow from creation to analysis"""
        # Create test
        self.protocol.create_test(self.metadata, self.device_info, self.test_conditions)

        # Add measurements
        self.protocol.add_iv_measurement("front", self.front_iv, 1000.0, 25000.0)
        self.protocol.add_iv_measurement("rear", self.rear_iv, 150.0, 25000.0)

        # Calculate bifacial parameters
        bifacial_results = self.protocol.calculate_bifacial_parameters()
        self.assertIsNotNone(bifacial_results)

        # Run validation
        validation_results = self.protocol.run_validation()
        self.assertIsNotNone(validation_results)

        # Analyze performance
        analysis_results = self.protocol.analyze_performance()
        self.assertIsNotNone(analysis_results)

        # Generate report
        report = self.protocol.generate_report_data()
        self.assertIsNotNone(report)

        # All should complete without errors
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
