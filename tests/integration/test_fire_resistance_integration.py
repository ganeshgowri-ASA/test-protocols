"""
Integration Tests for Fire Resistance Testing Protocol
Tests the complete workflow from sample registration to report generation
"""

import unittest
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from models.fire_resistance_model import (
    SampleInformation,
    EnvironmentalConditions,
    EquipmentCalibration,
    TestObservations,
    PassFailResult,
    SmokeLevel,
    MaterialIntegrity
)
from handlers.fire_resistance_handler import FireResistanceProtocolHandler


class TestFireResistanceIntegration(unittest.TestCase):
    """Integration tests for complete test workflow"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.handler = FireResistanceProtocolHandler()

        # Create test sample
        self.sample = SampleInformation(
            sample_id="INT-TEST-001",
            manufacturer="Integration Test Manufacturer",
            model_number="ITM-600",
            serial_number="SN-INT-123456",
            date_of_manufacture="2025-01-15",
            batch_number="BATCH-INT-001",
            receipt_date=datetime.now(),
            visual_condition="Excellent - No visible defects",
            dimensions={"length_mm": 1956, "width_mm": 992, "thickness_mm": 40},
            weight_kg=22.5
        )

        # Create equipment calibrations
        self.equipment = [
            EquipmentCalibration(
                equipment_id="EQ-FIRE-003",
                equipment_name="Temperature Measurement System",
                calibration_date=datetime.now() - timedelta(days=100),
                calibration_due_date=datetime.now() + timedelta(days=265),
                calibration_certificate="CAL-2024-TMS-001",
                calibrated_by="Metrology Lab Inc"
            ),
            EquipmentCalibration(
                equipment_id="EQ-FIRE-004",
                equipment_name="Timer System",
                calibration_date=datetime.now() - timedelta(days=50),
                calibration_due_date=datetime.now() + timedelta(days=315),
                calibration_certificate="CAL-2024-TIM-001",
                calibrated_by="Metrology Lab Inc"
            )
        ]

    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)

    def test_complete_passing_test_workflow(self):
        """Test complete workflow for a passing test"""
        # Step 1: Create test session
        test_session = self.handler.create_test_session(
            sample=self.sample,
            test_personnel=["John Doe (Technician)", "Jane Smith (Engineer)"],
            test_id="FIRE-INT-PASS-001"
        )

        self.assertIsNotNone(test_session)
        self.assertEqual(test_session.test_id, "FIRE-INT-PASS-001")
        self.assertEqual(len(test_session.test_personnel), 2)

        # Step 2: Set environmental conditions
        test_session.environmental_conditions = EnvironmentalConditions(
            temperature_c=23.5,
            relative_humidity=48.0,
            conditioning_start=datetime.now() - timedelta(hours=26),
            conditioning_end=datetime.now()
        )

        # Validate conditions
        is_valid, issues = self.handler.validate_environmental_conditions(
            test_session.environmental_conditions
        )
        self.assertTrue(is_valid)
        self.assertEqual(len(issues), 0)

        # Step 3: Add equipment
        test_session.equipment_used = self.equipment

        # Validate calibrations
        is_valid, issues = self.handler.validate_equipment_calibration(self.equipment)
        self.assertTrue(is_valid)
        self.assertEqual(len(issues), 0)

        # Step 4: Record real-time measurements
        time_points = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300,
                       330, 360, 390, 420, 450, 480, 510, 540, 570, 600]

        # Simulate temperature profile
        for t in time_points:
            temp = 25.0 + (t / 10) if t < 300 else 25.0 + (30 - (t - 300) / 20)
            flame_spread = min(t / 10, 75.0) if t < 300 else 75.0

            self.handler.record_measurement(
                elapsed_time_seconds=float(t),
                surface_temperature_c=temp,
                flame_spread_mm=flame_spread,
                observations=f"Measurement at t={t}s"
            )

        self.assertEqual(len(test_session.real_time_data), len(time_points))

        # Step 5: Finalize test with passing observations
        observations = TestObservations(
            ignition_occurred=True,
            time_to_ignition_seconds=35.0,
            self_extinguishing=True,
            self_extinguishing_time_seconds=45.0,
            dripping_materials=False,
            flaming_drips=False,
            smoke_generation=SmokeLevel.LIGHT,
            material_integrity=MaterialIntegrity.MINOR_DAMAGE,
            max_flame_spread_mm=75.0,
            burning_duration_seconds=45.0,
            continued_smoldering=False,
            notes="Test completed successfully with no major issues"
        )

        results = self.handler.finalize_test(observations)

        # Verify results
        self.assertEqual(results.overall_result, PassFailResult.PASS)
        self.assertGreater(len(results.acceptance_results), 0)

        # Check all critical criteria passed
        critical_failures = [
            c for c in results.acceptance_results
            if c.severity == "critical" and c.result == PassFailResult.FAIL
        ]
        self.assertEqual(len(critical_failures), 0)

        # Step 6: Generate report
        report = self.handler.generate_report(
            test_results=results,
            prepared_by="John Doe",
            reviewed_by="Jane Smith",
            approved_by="Quality Manager"
        )

        self.assertIsNotNone(report)
        self.assertEqual(report.results.overall_result, PassFailResult.PASS)
        self.assertIn("PASS", report.executive_summary)

        # Step 7: Export results
        exported_files = self.handler.export_results(
            test_results=results,
            output_dir=self.temp_dir,
            formats=['json', 'csv']
        )

        self.assertIn('json', exported_files)
        self.assertIn('csv', exported_files)

        # Verify files exist
        self.assertTrue(Path(exported_files['json']).exists())
        self.assertTrue(Path(exported_files['csv']).exists())

    def test_complete_failing_test_workflow(self):
        """Test complete workflow for a failing test"""
        # Create test session
        test_session = self.handler.create_test_session(
            sample=self.sample,
            test_personnel=["Technician A", "Engineer B"],
            test_id="FIRE-INT-FAIL-001"
        )

        # Set environmental conditions
        test_session.environmental_conditions = EnvironmentalConditions(
            temperature_c=24.0,
            relative_humidity=52.0
        )
        test_session.equipment_used = self.equipment

        # Record measurements showing excessive flame spread
        for t in range(0, 601, 30):
            temp = 25.0 + (t / 5)  # Higher temperatures
            flame_spread = min(t / 4, 150.0)  # Exceeds 100mm limit

            self.handler.record_measurement(
                elapsed_time_seconds=float(t),
                surface_temperature_c=temp,
                flame_spread_mm=flame_spread
            )

        # Finalize with failing observations
        observations = TestObservations(
            ignition_occurred=True,
            time_to_ignition_seconds=15.0,
            self_extinguishing=True,
            self_extinguishing_time_seconds=85.0,  # Exceeds 60s limit
            dripping_materials=True,
            flaming_drips=True,  # Critical failure
            smoke_generation=SmokeLevel.HEAVY,
            material_integrity=MaterialIntegrity.SEVERE_DAMAGE,
            max_flame_spread_mm=150.0,  # Exceeds 100mm limit
            burning_duration_seconds=85.0,
            notes="Test failed - excessive flame spread and flaming drips observed"
        )

        results = self.handler.finalize_test(observations)

        # Verify failure
        self.assertEqual(results.overall_result, PassFailResult.FAIL)

        # Check that critical criteria failed
        critical_failures = [
            c for c in results.acceptance_results
            if c.severity == "critical" and c.result == PassFailResult.FAIL
        ]
        self.assertGreater(len(critical_failures), 0)

        # Generate failure report
        report = self.handler.generate_report(
            test_results=results,
            prepared_by="Technician A",
            reviewed_by="Engineer B",
            approved_by="Quality Manager"
        )

        self.assertIn("FAIL", report.executive_summary)
        self.assertGreater(len(report.recommendations), 0)

    def test_equipment_calibration_validation(self):
        """Test equipment calibration validation"""
        # Valid equipment
        is_valid, issues = self.handler.validate_equipment_calibration(self.equipment)
        self.assertTrue(is_valid)

        # Expired equipment
        expired_equipment = [
            EquipmentCalibration(
                equipment_id="EQ-FIRE-003",
                equipment_name="Temperature Measurement System",
                calibration_date=datetime.now() - timedelta(days=400),
                calibration_due_date=datetime.now() - timedelta(days=35),
                calibration_certificate="CAL-2023-OLD",
                calibrated_by="Old Cal Lab"
            )
        ]

        is_valid, issues = self.handler.validate_equipment_calibration(expired_equipment)
        self.assertFalse(is_valid)
        self.assertGreater(len(issues), 0)
        self.assertIn("expired", issues[0].lower())

    def test_environmental_conditions_validation(self):
        """Test environmental conditions validation"""
        # Valid conditions
        valid_conditions = EnvironmentalConditions(
            temperature_c=23.0,
            relative_humidity=50.0
        )
        is_valid, issues = self.handler.validate_environmental_conditions(valid_conditions)
        self.assertTrue(is_valid)

        # Invalid temperature
        invalid_temp = EnvironmentalConditions(
            temperature_c=15.0,
            relative_humidity=50.0
        )
        is_valid, issues = self.handler.validate_environmental_conditions(invalid_temp)
        self.assertFalse(is_valid)
        self.assertIn("Temperature", issues[0])

        # Invalid humidity
        invalid_humidity = EnvironmentalConditions(
            temperature_c=23.0,
            relative_humidity=25.0
        )
        is_valid, issues = self.handler.validate_environmental_conditions(invalid_humidity)
        self.assertFalse(is_valid)
        self.assertIn("humidity", issues[0].lower())

    def test_conditioning_period_validation(self):
        """Test sample conditioning period validation"""
        # Adequate conditioning (25 hours)
        start_time = datetime.now() - timedelta(hours=25)
        is_adequate, message = self.handler.check_sample_conditioning(start_time)
        self.assertTrue(is_adequate)
        self.assertIn("OK", message)

        # Insufficient conditioning (10 hours)
        start_time = datetime.now() - timedelta(hours=10)
        is_adequate, message = self.handler.check_sample_conditioning(start_time)
        self.assertFalse(is_adequate)
        self.assertIn("Insufficient", message)

    def test_protocol_loading(self):
        """Test protocol JSON loading"""
        protocol_info = self.handler.get_protocol_info()

        self.assertEqual(protocol_info['protocol_id'], "FIRE-001")
        self.assertEqual(protocol_info['protocol_name'], "Fire Resistance Testing Protocol")
        self.assertEqual(protocol_info['version'], "1.0.0")
        self.assertEqual(protocol_info['category'], "Safety")
        self.assertEqual(protocol_info['standard']['name'], "IEC 61730-2")


class TestAcceptanceCriteriaEvaluation(unittest.TestCase):
    """Test acceptance criteria evaluation logic"""

    def setUp(self):
        """Set up test handler"""
        self.handler = FireResistanceProtocolHandler()

    def test_all_criteria_pass(self):
        """Test when all criteria pass"""
        observations = TestObservations(
            self_extinguishing_time_seconds=45.0,
            max_flame_spread_mm=75.0,
            flaming_drips=False
        )

        criteria_results = self.handler.evaluate_acceptance_criteria(observations)

        # Should have 3 critical criteria
        critical_results = [c for c in criteria_results if c.severity == "critical"]
        self.assertEqual(len(critical_results), 3)

        # All should pass
        failures = [c for c in critical_results if c.result == PassFailResult.FAIL]
        self.assertEqual(len(failures), 0)

    def test_sustained_burning_failure(self):
        """Test failure due to sustained burning"""
        observations = TestObservations(
            self_extinguishing_time_seconds=75.0,  # Exceeds 60s
            max_flame_spread_mm=75.0,
            flaming_drips=False
        )

        criteria_results = self.handler.evaluate_acceptance_criteria(observations)

        # Find sustained burning criterion
        sustained_burning = next(
            (c for c in criteria_results if "Sustained Burning" in c.criterion_name),
            None
        )
        self.assertIsNotNone(sustained_burning)
        self.assertEqual(sustained_burning.result, PassFailResult.FAIL)

    def test_flame_spread_failure(self):
        """Test failure due to excessive flame spread"""
        observations = TestObservations(
            self_extinguishing_time_seconds=45.0,
            max_flame_spread_mm=125.0,  # Exceeds 100mm
            flaming_drips=False
        )

        criteria_results = self.handler.evaluate_acceptance_criteria(observations)

        # Find flame spread criterion
        flame_spread = next(
            (c for c in criteria_results if "Flame Spread" in c.criterion_name),
            None
        )
        self.assertIsNotNone(flame_spread)
        self.assertEqual(flame_spread.result, PassFailResult.FAIL)

    def test_flaming_drips_failure(self):
        """Test failure due to flaming drips"""
        observations = TestObservations(
            self_extinguishing_time_seconds=45.0,
            max_flame_spread_mm=75.0,
            flaming_drips=True  # Critical failure
        )

        criteria_results = self.handler.evaluate_acceptance_criteria(observations)

        # Find flaming drips criterion
        drips = next(
            (c for c in criteria_results if "Flaming Drips" in c.criterion_name),
            None
        )
        self.assertIsNotNone(drips)
        self.assertEqual(drips.result, PassFailResult.FAIL)


if __name__ == '__main__':
    unittest.main()
