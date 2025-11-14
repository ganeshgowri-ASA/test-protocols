"""
Unit Tests for UV-001 Preconditioning Protocol

Comprehensive test suite for UV preconditioning protocol implementation
including dosage tracking, irradiance monitoring, and spectral data logging.
"""

import unittest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import json
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / 'src'))

from protocols.environmental.uv_preconditioning import (
    UVPreconditioningProtocol,
    TestSession,
    TestStatus,
    ComplianceStatus,
    IrradianceData,
    EnvironmentalData,
    SpectralData,
    ElectricalParameters
)


class TestUVPreconditioningProtocol(unittest.TestCase):
    """Test suite for UVPreconditioningProtocol class"""

    def setUp(self):
        """Set up test fixtures"""
        self.protocol = UVPreconditioningProtocol()
        self.session_id = "TEST_001"
        self.sample_id = "MODULE_TEST_001"
        self.operator = "Test Operator"

    def tearDown(self):
        """Clean up after tests"""
        self.protocol = None

    # =========================================================================
    # Test Session Management
    # =========================================================================

    def test_start_test_session(self):
        """Test starting a new test session"""
        session = self.protocol.start_test_session(
            session_id=self.session_id,
            sample_id=self.sample_id,
            operator=self.operator,
            notes="Test session"
        )

        self.assertIsInstance(session, TestSession)
        self.assertEqual(session.session_id, self.session_id)
        self.assertEqual(session.sample_id, self.sample_id)
        self.assertEqual(session.operator, self.operator)
        self.assertEqual(session.status, TestStatus.IN_PROGRESS)
        self.assertIsNotNone(session.start_time)
        self.assertEqual(session.cumulative_uv_dose, 0.0)

    def test_cannot_start_session_while_active(self):
        """Test that starting a session while another is active raises error"""
        self.protocol.start_test_session(
            session_id=self.session_id,
            sample_id=self.sample_id,
            operator=self.operator
        )

        with self.assertRaises(ValueError):
            self.protocol.start_test_session(
                session_id="TEST_002",
                sample_id="MODULE_002",
                operator=self.operator
            )

    def test_complete_test_session(self):
        """Test completing a test session"""
        self.protocol.start_test_session(
            session_id=self.session_id,
            sample_id=self.sample_id,
            operator=self.operator
        )

        session = self.protocol.complete_test_session()

        self.assertEqual(session.status, TestStatus.COMPLETED)
        self.assertIsNotNone(session.end_time)

    def test_abort_test_session(self):
        """Test aborting a test session"""
        self.protocol.start_test_session(
            session_id=self.session_id,
            sample_id=self.sample_id,
            operator=self.operator
        )

        reason = "Equipment failure"
        session = self.protocol.abort_test_session(reason)

        self.assertEqual(session.status, TestStatus.ABORTED)
        self.assertIn(reason, session.notes)

    # =========================================================================
    # Test Irradiance Measurements
    # =========================================================================

    def test_add_irradiance_measurement(self):
        """Test adding UV irradiance measurement"""
        self.protocol.start_test_session(
            session_id=self.session_id,
            sample_id=self.sample_id,
            operator=self.operator
        )

        measurement = self.protocol.add_irradiance_measurement(
            uv_irradiance=300.0,
            sensor_temperature=35.0
        )

        self.assertIsInstance(measurement, IrradianceData)
        self.assertEqual(measurement.uv_irradiance, 300.0)
        self.assertEqual(measurement.sensor_temperature, 35.0)
        self.assertEqual(len(self.protocol.current_session.irradiance_measurements), 1)

    def test_irradiance_without_session_raises_error(self):
        """Test that adding irradiance without session raises error"""
        with self.assertRaises(ValueError):
            self.protocol.add_irradiance_measurement(uv_irradiance=300.0)

    def test_irradiance_compliance_check(self):
        """Test irradiance compliance checking"""
        # Compliant value
        status = self.protocol._check_irradiance_compliance(300.0)
        self.assertEqual(status, ComplianceStatus.COMPLIANT)

        # Too low
        status = self.protocol._check_irradiance_compliance(200.0)
        self.assertEqual(status, ComplianceStatus.OUT_OF_SPEC)

        # Too high
        status = self.protocol._check_irradiance_compliance(450.0)
        self.assertEqual(status, ComplianceStatus.OUT_OF_SPEC)

    def test_cumulative_dose_calculation(self):
        """Test cumulative UV dose calculation"""
        self.protocol.start_test_session(
            session_id=self.session_id,
            sample_id=self.sample_id,
            operator=self.operator
        )

        # First measurement
        t1 = datetime.now()
        self.protocol.add_irradiance_measurement(
            uv_irradiance=300.0,
            timestamp=t1
        )

        # Second measurement after 1 hour
        t2 = t1 + timedelta(hours=1)
        self.protocol.add_irradiance_measurement(
            uv_irradiance=300.0,
            timestamp=t2
        )

        # Expected dose: (300 W/m² * 1 hour) / 1000 = 0.3 kWh/m²
        dose = self.protocol.get_cumulative_dose()
        self.assertAlmostEqual(dose, 0.3, places=2)

    def test_uniformity_calculation(self):
        """Test irradiance uniformity calculation"""
        measurement = IrradianceData(
            timestamp=datetime.now(),
            uv_irradiance=300.0,
            uniformity_measurements=[295.0, 300.0, 305.0, 298.0]
        )

        uniformity = measurement.calculate_uniformity()
        self.assertIsNotNone(uniformity)
        self.assertLess(uniformity, 5.0)  # Should be < 5% deviation

    # =========================================================================
    # Test Environmental Measurements
    # =========================================================================

    def test_add_environmental_measurement(self):
        """Test adding environmental conditions measurement"""
        self.protocol.start_test_session(
            session_id=self.session_id,
            sample_id=self.sample_id,
            operator=self.operator
        )

        measurement = self.protocol.add_environmental_measurement(
            module_temperature=60.0,
            ambient_temperature=25.0,
            relative_humidity=50.0,
            air_velocity=1.0
        )

        self.assertIsInstance(measurement, EnvironmentalData)
        self.assertEqual(measurement.module_temperature, 60.0)
        self.assertEqual(measurement.ambient_temperature, 25.0)
        self.assertEqual(measurement.relative_humidity, 50.0)

    def test_temperature_compliance_check(self):
        """Test temperature compliance checking"""
        # Compliant module temperature
        module_status, ambient_status = self.protocol._check_temperature_compliance(60.0, 25.0)
        self.assertEqual(module_status, ComplianceStatus.COMPLIANT)
        self.assertEqual(ambient_status, ComplianceStatus.COMPLIANT)

        # Out of spec module temperature
        module_status, ambient_status = self.protocol._check_temperature_compliance(75.0, 25.0)
        self.assertEqual(module_status, ComplianceStatus.OUT_OF_SPEC)

    def test_humidity_compliance_check(self):
        """Test humidity compliance checking"""
        # Compliant
        status = self.protocol._check_humidity_compliance(50.0)
        self.assertEqual(status, ComplianceStatus.COMPLIANT)

        # Out of spec
        status = self.protocol._check_humidity_compliance(80.0)
        self.assertEqual(status, ComplianceStatus.OUT_OF_SPEC)

    # =========================================================================
    # Test Spectral Measurements
    # =========================================================================

    def test_add_spectral_measurement(self):
        """Test adding spectral irradiance measurement"""
        self.protocol.start_test_session(
            session_id=self.session_id,
            sample_id=self.sample_id,
            operator=self.operator
        )

        # Generate sample spectral data
        wavelengths = list(range(280, 401, 10))
        # Simple Gaussian distribution centered at 340 nm
        import math
        irradiances = [
            50 * math.exp(-((w - 340) ** 2) / (2 * 30 ** 2))
            for w in wavelengths
        ]

        measurement = self.protocol.add_spectral_measurement(
            wavelengths=wavelengths,
            irradiance_values=irradiances
        )

        self.assertIsInstance(measurement, SpectralData)
        self.assertGreater(measurement.total_uv_irradiance, 0)
        self.assertGreater(measurement.uv_a_percentage, 0)
        self.assertGreater(measurement.uv_b_percentage, 0)
        self.assertAlmostEqual(
            measurement.uv_a_percentage + measurement.uv_b_percentage,
            100.0,
            places=1
        )

    def test_spectral_peak_detection(self):
        """Test peak wavelength detection in spectral data"""
        self.protocol.start_test_session(
            session_id=self.session_id,
            sample_id=self.sample_id,
            operator=self.operator
        )

        wavelengths = [300, 310, 320, 330, 340, 350, 360]
        irradiances = [10, 20, 30, 40, 50, 40, 30]  # Peak at 340 nm

        measurement = self.protocol.add_spectral_measurement(
            wavelengths=wavelengths,
            irradiance_values=irradiances
        )

        self.assertEqual(measurement.peak_wavelength, 340)

    # =========================================================================
    # Test Electrical Characterization
    # =========================================================================

    def test_add_pre_test_electrical_characterization(self):
        """Test adding pre-test electrical characterization"""
        self.protocol.start_test_session(
            session_id=self.session_id,
            sample_id=self.sample_id,
            operator=self.operator
        )

        params = self.protocol.add_electrical_characterization(
            voc=45.2,
            isc=9.8,
            pmax=350.0,
            ff=0.79,
            efficiency=18.5,
            is_pre_test=True
        )

        self.assertIsInstance(params, ElectricalParameters)
        self.assertEqual(params.open_circuit_voltage, 45.2)
        self.assertEqual(params.maximum_power, 350.0)
        self.assertEqual(self.protocol.current_session.pre_test_electrical, params)

    def test_add_post_test_electrical_characterization(self):
        """Test adding post-test electrical characterization"""
        self.protocol.start_test_session(
            session_id=self.session_id,
            sample_id=self.sample_id,
            operator=self.operator
        )

        # Add pre-test data first
        self.protocol.add_electrical_characterization(
            voc=45.2,
            isc=9.8,
            pmax=350.0,
            ff=0.79,
            is_pre_test=True
        )

        # Add post-test data
        params = self.protocol.add_electrical_characterization(
            voc=45.0,
            isc=9.75,
            pmax=340.0,
            ff=0.78,
            is_pre_test=False
        )

        self.assertEqual(self.protocol.current_session.post_test_electrical, params)

    def test_power_degradation_calculation(self):
        """Test power degradation percentage calculation"""
        self.protocol.start_test_session(
            session_id=self.session_id,
            sample_id=self.sample_id,
            operator=self.operator
        )

        # Pre-test: 350 W
        self.protocol.add_electrical_characterization(
            voc=45.2, isc=9.8, pmax=350.0, ff=0.79, is_pre_test=True
        )

        # Post-test: 340 W (2.86% degradation)
        self.protocol.add_electrical_characterization(
            voc=45.0, isc=9.75, pmax=340.0, ff=0.78, is_pre_test=False
        )

        degradation = self.protocol.calculate_power_degradation()
        self.assertIsNotNone(degradation)
        self.assertAlmostEqual(degradation, 2.857, places=2)

    # =========================================================================
    # Test Dose Tracking and Completion
    # =========================================================================

    def test_get_remaining_dose(self):
        """Test remaining dose calculation"""
        self.protocol.start_test_session(
            session_id=self.session_id,
            sample_id=self.sample_id,
            operator=self.operator
        )

        # Simulate some dose accumulation
        self.protocol.current_session.cumulative_uv_dose = 10.0

        remaining = self.protocol.get_remaining_dose()
        self.assertEqual(remaining, 5.0)  # 15 - 10 = 5

    def test_dose_completion_percentage(self):
        """Test dose completion percentage calculation"""
        self.protocol.start_test_session(
            session_id=self.session_id,
            sample_id=self.sample_id,
            operator=self.operator
        )

        self.protocol.current_session.cumulative_uv_dose = 7.5

        completion = self.protocol.get_dose_completion_percentage()
        self.assertEqual(completion, 50.0)  # 7.5 / 15 * 100 = 50%

    def test_check_dose_target_reached(self):
        """Test dose target reached check"""
        self.protocol.start_test_session(
            session_id=self.session_id,
            sample_id=self.sample_id,
            operator=self.operator
        )

        # Below target
        self.protocol.current_session.cumulative_uv_dose = 14.0
        self.assertFalse(self.protocol.check_dose_target_reached())

        # At target (within tolerance)
        self.protocol.current_session.cumulative_uv_dose = 15.0
        self.assertTrue(self.protocol.check_dose_target_reached())

        # Slightly above target (within tolerance)
        self.protocol.current_session.cumulative_uv_dose = 15.2
        self.assertTrue(self.protocol.check_dose_target_reached())

    def test_estimate_remaining_time(self):
        """Test remaining time estimation"""
        self.protocol.start_test_session(
            session_id=self.session_id,
            sample_id=self.sample_id,
            operator=self.operator
        )

        # Set current dose and average irradiance
        self.protocol.current_session.cumulative_uv_dose = 10.0
        self.protocol.current_session.average_irradiance = 300.0

        # Remaining: 5 kWh/m² at 300 W/m² = 5 / 0.3 = 16.67 hours
        remaining_time = self.protocol.estimate_remaining_time()
        self.assertIsNotNone(remaining_time)
        self.assertAlmostEqual(remaining_time, 16.67, places=1)

    # =========================================================================
    # Test Acceptance Criteria
    # =========================================================================

    def test_acceptance_criteria_pass(self):
        """Test acceptance criteria when test passes"""
        self.protocol.start_test_session(
            session_id=self.session_id,
            sample_id=self.sample_id,
            operator=self.operator
        )

        # Set dose to target
        self.protocol.current_session.cumulative_uv_dose = 15.0

        # Add electrical data showing acceptable degradation
        self.protocol.add_electrical_characterization(
            voc=45.2, isc=9.8, pmax=350.0, ff=0.79, is_pre_test=True
        )
        self.protocol.add_electrical_characterization(
            voc=45.0, isc=9.75, pmax=340.0, ff=0.78, is_pre_test=False
        )

        criteria = self.protocol.check_acceptance_criteria()
        self.assertTrue(criteria['overall_pass'])
        self.assertTrue(criteria['criteria']['power_degradation']['pass'])
        self.assertTrue(criteria['criteria']['uv_dose']['pass'])

    def test_acceptance_criteria_fail(self):
        """Test acceptance criteria when test fails"""
        self.protocol.start_test_session(
            session_id=self.session_id,
            sample_id=self.sample_id,
            operator=self.operator
        )

        # Set dose to target
        self.protocol.current_session.cumulative_uv_dose = 15.0

        # Add electrical data showing excessive degradation (>5%)
        self.protocol.add_electrical_characterization(
            voc=45.2, isc=9.8, pmax=350.0, ff=0.79, is_pre_test=True
        )
        self.protocol.add_electrical_characterization(
            voc=44.0, isc=9.5, pmax=330.0, ff=0.77, is_pre_test=False
        )

        criteria = self.protocol.check_acceptance_criteria()
        self.assertFalse(criteria['overall_pass'])
        self.assertFalse(criteria['criteria']['power_degradation']['pass'])

    # =========================================================================
    # Test Data Export
    # =========================================================================

    def test_session_export(self):
        """Test exporting session data to JSON"""
        self.protocol.start_test_session(
            session_id=self.session_id,
            sample_id=self.sample_id,
            operator=self.operator
        )

        # Add some data
        self.protocol.add_irradiance_measurement(uv_irradiance=300.0)
        self.protocol.add_environmental_measurement(
            module_temperature=60.0,
            ambient_temperature=25.0,
            relative_humidity=50.0
        )

        # Export to temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = Path(f.name)

        try:
            output_path = self.protocol.export_session_data(temp_path)
            self.assertTrue(output_path.exists())

            # Verify JSON structure
            with open(output_path, 'r') as f:
                data = json.load(f)

            self.assertEqual(data['session_id'], self.session_id)
            self.assertEqual(data['sample_id'], self.sample_id)
            self.assertGreater(len(data['irradiance_measurements']), 0)
            self.assertGreater(len(data['environmental_measurements']), 0)

        finally:
            # Clean up
            if temp_path.exists():
                temp_path.unlink()

    def test_get_session_summary(self):
        """Test getting session summary"""
        self.protocol.start_test_session(
            session_id=self.session_id,
            sample_id=self.sample_id,
            operator=self.operator
        )

        # Add some measurements
        self.protocol.add_irradiance_measurement(uv_irradiance=300.0)
        self.protocol.add_environmental_measurement(
            module_temperature=60.0,
            ambient_temperature=25.0,
            relative_humidity=50.0
        )

        summary = self.protocol.get_session_summary()

        self.assertEqual(summary['session_id'], self.session_id)
        self.assertEqual(summary['sample_id'], self.sample_id)
        self.assertIn('cumulative_dose', summary)
        self.assertIn('completion_percentage', summary)
        self.assertIn('measurement_counts', summary)
        self.assertEqual(summary['measurement_counts']['irradiance'], 1)
        self.assertEqual(summary['measurement_counts']['environmental'], 1)

    # =========================================================================
    # Test Data Serialization
    # =========================================================================

    def test_irradiance_data_to_dict(self):
        """Test IrradianceData serialization"""
        data = IrradianceData(
            timestamp=datetime(2025, 1, 1, 12, 0, 0),
            uv_irradiance=300.0,
            sensor_temperature=35.0
        )

        data_dict = data.to_dict()
        self.assertEqual(data_dict['uv_irradiance'], 300.0)
        self.assertEqual(data_dict['sensor_temperature'], 35.0)
        self.assertIn('timestamp', data_dict)

    def test_environmental_data_to_dict(self):
        """Test EnvironmentalData serialization"""
        data = EnvironmentalData(
            timestamp=datetime(2025, 1, 1, 12, 0, 0),
            module_temperature=60.0,
            ambient_temperature=25.0,
            relative_humidity=50.0
        )

        data_dict = data.to_dict()
        self.assertEqual(data_dict['module_temperature'], 60.0)
        self.assertEqual(data_dict['ambient_temperature'], 25.0)
        self.assertEqual(data_dict['relative_humidity'], 50.0)


class TestProtocolConstants(unittest.TestCase):
    """Test protocol constants and specifications"""

    def test_protocol_constants(self):
        """Test that protocol constants match IEC 61215 MQT 10"""
        protocol = UVPreconditioningProtocol()

        self.assertEqual(protocol.TARGET_UV_DOSE, 15.0)
        self.assertEqual(protocol.WAVELENGTH_MIN, 280)
        self.assertEqual(protocol.WAVELENGTH_MAX, 400)
        self.assertEqual(protocol.PEAK_WAVELENGTH_TARGET, 340)
        self.assertEqual(protocol.IRRADIANCE_MIN, 250)
        self.assertEqual(protocol.IRRADIANCE_MAX, 400)
        self.assertEqual(protocol.MODULE_TEMP_TARGET, 60)
        self.assertEqual(protocol.MAX_POWER_DEGRADATION, 5.0)


if __name__ == '__main__':
    unittest.main()
