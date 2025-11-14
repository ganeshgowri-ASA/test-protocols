"""
Unit Tests for Fire Resistance Testing Protocol Models
"""

import unittest
from datetime import datetime, timedelta
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from models.fire_resistance_model import (
    SampleInformation,
    EnvironmentalConditions,
    EquipmentCalibration,
    RealTimeMeasurement,
    TestObservations,
    AcceptanceCriteriaResult,
    TestResults,
    TestReport,
    TestStatus,
    PassFailResult,
    SmokeLevel,
    MaterialIntegrity
)


class TestSampleInformation(unittest.TestCase):
    """Test SampleInformation model"""

    def setUp(self):
        """Set up test data"""
        self.sample = SampleInformation(
            sample_id="TEST-001",
            manufacturer="Test Manufacturer",
            model_number="TM-500",
            serial_number="SN123456",
            date_of_manufacture="2025-01-01",
            batch_number="BATCH-2025-A",
            receipt_date=datetime.now(),
            visual_condition="Good",
            dimensions={"length_mm": 1956, "width_mm": 992, "thickness_mm": 40},
            weight_kg=22.5
        )

    def test_sample_creation(self):
        """Test sample object creation"""
        self.assertEqual(self.sample.sample_id, "TEST-001")
        self.assertEqual(self.sample.manufacturer, "Test Manufacturer")
        self.assertEqual(self.sample.serial_number, "SN123456")

    def test_sample_to_dict(self):
        """Test conversion to dictionary"""
        sample_dict = self.sample.to_dict()
        self.assertIsInstance(sample_dict, dict)
        self.assertEqual(sample_dict['sample_id'], "TEST-001")
        self.assertEqual(sample_dict['dimensions']['length_mm'], 1956)


class TestEnvironmentalConditions(unittest.TestCase):
    """Test EnvironmentalConditions model"""

    def test_conditions_within_spec(self):
        """Test conditions within specification"""
        conditions = EnvironmentalConditions(
            temperature_c=23.0,
            relative_humidity=50.0
        )
        self.assertTrue(conditions.is_within_spec())

    def test_conditions_outside_spec_temperature(self):
        """Test conditions outside temperature specification"""
        conditions = EnvironmentalConditions(
            temperature_c=15.0,  # Below 18°C
            relative_humidity=50.0
        )
        self.assertFalse(conditions.is_within_spec())

    def test_conditions_outside_spec_humidity(self):
        """Test conditions outside humidity specification"""
        conditions = EnvironmentalConditions(
            temperature_c=23.0,
            relative_humidity=25.0  # Below 30%
        )
        self.assertFalse(conditions.is_within_spec())

    def test_conditions_to_dict(self):
        """Test conversion to dictionary"""
        conditions = EnvironmentalConditions(
            temperature_c=23.0,
            relative_humidity=50.0
        )
        cond_dict = conditions.to_dict()
        self.assertTrue(cond_dict['within_spec'])


class TestEquipmentCalibration(unittest.TestCase):
    """Test EquipmentCalibration model"""

    def test_valid_calibration(self):
        """Test valid calibration"""
        cal = EquipmentCalibration(
            equipment_id="EQ-001",
            equipment_name="Temperature Sensor",
            calibration_date=datetime.now(),
            calibration_due_date=datetime.now() + timedelta(days=365),
            calibration_certificate="CAL-2025-001",
            calibrated_by="Cal Lab Inc"
        )
        self.assertTrue(cal.check_validity())

    def test_expired_calibration(self):
        """Test expired calibration"""
        cal = EquipmentCalibration(
            equipment_id="EQ-001",
            equipment_name="Temperature Sensor",
            calibration_date=datetime.now() - timedelta(days=400),
            calibration_due_date=datetime.now() - timedelta(days=35),
            calibration_certificate="CAL-2024-001",
            calibrated_by="Cal Lab Inc"
        )
        self.assertFalse(cal.check_validity())


class TestRealTimeMeasurement(unittest.TestCase):
    """Test RealTimeMeasurement model"""

    def test_measurement_creation(self):
        """Test measurement creation"""
        measurement = RealTimeMeasurement(
            timestamp=datetime.now(),
            elapsed_time_seconds=30.0,
            surface_temperature_c=150.5,
            flame_spread_mm=25.0,
            observations="Visible smoke"
        )
        self.assertEqual(measurement.elapsed_time_seconds, 30.0)
        self.assertEqual(measurement.surface_temperature_c, 150.5)

    def test_measurement_to_dict(self):
        """Test measurement to dictionary conversion"""
        measurement = RealTimeMeasurement(
            timestamp=datetime.now(),
            elapsed_time_seconds=30.0,
            surface_temperature_c=150.5
        )
        meas_dict = measurement.to_dict()
        self.assertIn('timestamp', meas_dict)
        self.assertEqual(meas_dict['elapsed_time_seconds'], 30.0)


class TestTestObservations(unittest.TestCase):
    """Test TestObservations model"""

    def test_observations_no_ignition(self):
        """Test observations with no ignition"""
        obs = TestObservations(
            ignition_occurred=False,
            smoke_generation=SmokeLevel.LIGHT,
            material_integrity=MaterialIntegrity.INTACT
        )
        self.assertFalse(obs.ignition_occurred)
        self.assertIsNone(obs.time_to_ignition_seconds)

    def test_observations_with_ignition(self):
        """Test observations with ignition"""
        obs = TestObservations(
            ignition_occurred=True,
            time_to_ignition_seconds=45.0,
            self_extinguishing=True,
            self_extinguishing_time_seconds=55.0,
            max_flame_spread_mm=75.0
        )
        self.assertTrue(obs.ignition_occurred)
        self.assertEqual(obs.time_to_ignition_seconds, 45.0)
        self.assertEqual(obs.max_flame_spread_mm, 75.0)

    def test_observations_to_dict(self):
        """Test observations to dictionary"""
        obs = TestObservations(
            ignition_occurred=True,
            smoke_generation=SmokeLevel.MODERATE,
            material_integrity=MaterialIntegrity.MINOR_DAMAGE
        )
        obs_dict = obs.to_dict()
        self.assertEqual(obs_dict['smoke_generation'], 'Moderate')
        self.assertEqual(obs_dict['material_integrity'], 'Minor Damage')


class TestAcceptanceCriteriaResult(unittest.TestCase):
    """Test AcceptanceCriteriaResult model"""

    def test_passing_criterion(self):
        """Test passing acceptance criterion"""
        criterion = AcceptanceCriteriaResult(
            criterion_name="No Sustained Burning",
            requirement="Self-extinguish within 60 seconds",
            measured_value=45.0,
            pass_condition="<= 60 seconds",
            result=PassFailResult.PASS,
            severity="critical"
        )
        self.assertEqual(criterion.result, PassFailResult.PASS)

    def test_failing_criterion(self):
        """Test failing acceptance criterion"""
        criterion = AcceptanceCriteriaResult(
            criterion_name="Limited Flame Spread",
            requirement="Flame spread <= 100mm",
            measured_value=125.0,
            pass_condition="<= 100 mm",
            result=PassFailResult.FAIL,
            severity="critical"
        )
        self.assertEqual(criterion.result, PassFailResult.FAIL)


class TestTestResults(unittest.TestCase):
    """Test TestResults model"""

    def setUp(self):
        """Set up test data"""
        self.sample = SampleInformation(
            sample_id="TEST-001",
            manufacturer="Test Manufacturer",
            model_number="TM-500",
            serial_number="SN123456"
        )

        self.conditions = EnvironmentalConditions(
            temperature_c=23.0,
            relative_humidity=50.0
        )

        self.observations = TestObservations(
            ignition_occurred=True,
            time_to_ignition_seconds=30.0,
            self_extinguishing=True,
            self_extinguishing_time_seconds=45.0,
            max_flame_spread_mm=75.0,
            flaming_drips=False
        )

    def test_test_results_pass(self):
        """Test passing test results"""
        results = TestResults(
            test_id="FIRE-TEST-001",
            sample=self.sample,
            test_date=datetime.now(),
            test_personnel=["Tech A", "Engineer B"],
            environmental_conditions=self.conditions,
            equipment_used=[],
            real_time_data=[],
            observations=self.observations,
            acceptance_results=[
                AcceptanceCriteriaResult(
                    criterion_name="No Sustained Burning",
                    requirement="Self-extinguish within 60 seconds",
                    measured_value=45.0,
                    pass_condition="<= 60 seconds",
                    result=PassFailResult.PASS,
                    severity="critical"
                ),
                AcceptanceCriteriaResult(
                    criterion_name="Limited Flame Spread",
                    requirement="Flame spread <= 100mm",
                    measured_value=75.0,
                    pass_condition="<= 100 mm",
                    result=PassFailResult.PASS,
                    severity="critical"
                ),
                AcceptanceCriteriaResult(
                    criterion_name="No Flaming Drips",
                    requirement="No flaming drips",
                    measured_value=False,
                    pass_condition="No flaming drips",
                    result=PassFailResult.PASS,
                    severity="critical"
                )
            ],
            overall_result=PassFailResult.PENDING
        )

        overall = results.evaluate_acceptance_criteria()
        self.assertEqual(overall, PassFailResult.PASS)

    def test_test_results_fail(self):
        """Test failing test results"""
        results = TestResults(
            test_id="FIRE-TEST-002",
            sample=self.sample,
            test_date=datetime.now(),
            test_personnel=["Tech A", "Engineer B"],
            environmental_conditions=self.conditions,
            equipment_used=[],
            real_time_data=[],
            observations=self.observations,
            acceptance_results=[
                AcceptanceCriteriaResult(
                    criterion_name="Limited Flame Spread",
                    requirement="Flame spread <= 100mm",
                    measured_value=125.0,
                    pass_condition="<= 100 mm",
                    result=PassFailResult.FAIL,
                    severity="critical"
                )
            ],
            overall_result=PassFailResult.PENDING
        )

        overall = results.evaluate_acceptance_criteria()
        self.assertEqual(overall, PassFailResult.FAIL)

    def test_test_results_to_json(self):
        """Test JSON export"""
        results = TestResults(
            test_id="FIRE-TEST-003",
            sample=self.sample,
            test_date=datetime.now(),
            test_personnel=["Tech A"],
            environmental_conditions=self.conditions,
            equipment_used=[],
            real_time_data=[],
            observations=self.observations,
            acceptance_results=[],
            overall_result=PassFailResult.PASS
        )

        json_str = results.to_json()
        self.assertIsInstance(json_str, str)

        # Parse JSON to verify it's valid
        data = json.loads(json_str)
        self.assertEqual(data['test_id'], "FIRE-TEST-003")


class TestTestReport(unittest.TestCase):
    """Test TestReport model"""

    def setUp(self):
        """Set up test data"""
        self.sample = SampleInformation(
            sample_id="TEST-001",
            manufacturer="Test Manufacturer",
            model_number="TM-500",
            serial_number="SN123456"
        )

        self.results = TestResults(
            test_id="FIRE-TEST-001",
            sample=self.sample,
            test_date=datetime.now(),
            test_personnel=["Tech A"],
            environmental_conditions=EnvironmentalConditions(23.0, 50.0),
            equipment_used=[],
            real_time_data=[],
            observations=TestObservations(
                ignition_occurred=True,
                self_extinguishing=True,
                max_flame_spread_mm=75.0
            ),
            acceptance_results=[],
            overall_result=PassFailResult.PASS
        )

    def test_report_creation(self):
        """Test report creation"""
        report = TestReport(
            report_id="RPT-001",
            protocol_id="FIRE-001",
            results=self.results
        )
        self.assertEqual(report.report_id, "RPT-001")
        self.assertEqual(report.protocol_id, "FIRE-001")

    def test_executive_summary_generation(self):
        """Test executive summary auto-generation"""
        report = TestReport(
            report_id="RPT-001",
            protocol_id="FIRE-001",
            results=self.results
        )
        summary = report.generate_executive_summary()
        self.assertIn("FIRE-TEST-001", summary)
        self.assertIn("Test Manufacturer", summary)
        self.assertIn("Pass", summary)

    def test_report_to_dict(self):
        """Test report to dictionary conversion"""
        report = TestReport(
            report_id="RPT-001",
            protocol_id="FIRE-001",
            results=self.results,
            prepared_by="Engineer A",
            reviewed_by="Manager B"
        )
        report_dict = report.to_dict()
        self.assertIn('report_id', report_dict)
        self.assertEqual(report_dict['prepared_by'], "Engineer A")


if __name__ == '__main__':
    unittest.main()
