"""
Unit and Integration Tests for SAND-001 Sand/Dust Resistance Test Protocol
"""

import unittest
import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'python'))

from protocols.sand_dust_test import (
    SandDustResistanceTest,
    TestPhase,
    SeverityLevel,
    ParticleData,
    EnvironmentalConditions,
    SpecimenData,
    TestConfiguration,
    ParticleTracker,
    create_test_from_protocol
)


class TestSeverityLevel(unittest.TestCase):
    """Test SeverityLevel enum"""

    def test_severity_levels(self):
        """Test severity level definitions"""
        self.assertEqual(SeverityLevel.LEVEL_1.level, 1)
        self.assertEqual(SeverityLevel.LEVEL_5.level, 5)
        self.assertIn("No visible dust ingress", SeverityLevel.LEVEL_1.description)

    def test_all_levels_present(self):
        """Test all severity levels are defined"""
        levels = [level.level for level in SeverityLevel]
        self.assertEqual(sorted(levels), [1, 2, 3, 4, 5])


class TestParticleData(unittest.TestCase):
    """Test ParticleData dataclass"""

    def test_particle_data_creation(self):
        """Test creating ParticleData instance"""
        data = ParticleData(
            timestamp=datetime.now(),
            point_id="P001",
            location=(100.0, 200.0, 300.0),
            particle_size_microns=50.0,
            particle_count=1000,
            concentration=0.01,
            velocity=(1.5, 0.5, 0.2),
            temperature=25.0,
            humidity=50.0
        )

        self.assertEqual(data.point_id, "P001")
        self.assertEqual(data.particle_size_microns, 50.0)
        self.assertEqual(data.particle_count, 1000)

    def test_particle_data_to_dict(self):
        """Test converting ParticleData to dictionary"""
        timestamp = datetime.now()
        data = ParticleData(
            timestamp=timestamp,
            point_id="P001",
            location=(100.0, 200.0, 300.0),
            particle_size_microns=50.0,
            particle_count=1000,
            concentration=0.01,
            velocity=(1.5, 0.5, 0.2),
            temperature=25.0,
            humidity=50.0
        )

        data_dict = data.to_dict()

        self.assertIsInstance(data_dict, dict)
        self.assertEqual(data_dict['point_id'], "P001")
        self.assertEqual(data_dict['location']['x'], 100.0)
        self.assertEqual(data_dict['velocity']['vx'], 1.5)
        self.assertEqual(data_dict['timestamp'], timestamp.isoformat())


class TestEnvironmentalConditions(unittest.TestCase):
    """Test EnvironmentalConditions dataclass"""

    def test_environmental_conditions_creation(self):
        """Test creating EnvironmentalConditions instance"""
        conditions = EnvironmentalConditions(
            timestamp=datetime.now(),
            temperature=25.0,
            humidity=50.0,
            air_velocity=2.0,
            atmospheric_pressure=101.325,
            dust_concentration=0.01
        )

        self.assertEqual(conditions.temperature, 25.0)
        self.assertEqual(conditions.humidity, 50.0)
        self.assertTrue(conditions.in_tolerance)

    def test_tolerance_checking_within_range(self):
        """Test tolerance checking when values are within range"""
        conditions = EnvironmentalConditions(
            timestamp=datetime.now(),
            temperature=26.0,
            humidity=52.0,
            air_velocity=2.3,
            atmospheric_pressure=101.325,
            dust_concentration=0.01
        )

        target = {'temperature': 25.0, 'humidity': 50.0, 'air_velocity': 2.0}
        tolerances = {'temperature': 3.0, 'humidity': 5.0, 'air_velocity': 0.5}

        result = conditions.check_tolerance(target, tolerances)

        self.assertTrue(result)
        self.assertTrue(conditions.in_tolerance)

    def test_tolerance_checking_out_of_range(self):
        """Test tolerance checking when values are out of range"""
        conditions = EnvironmentalConditions(
            timestamp=datetime.now(),
            temperature=30.0,  # 5 degrees over target (tolerance is 3)
            humidity=52.0,
            air_velocity=2.3,
            atmospheric_pressure=101.325,
            dust_concentration=0.01
        )

        target = {'temperature': 25.0, 'humidity': 50.0, 'air_velocity': 2.0}
        tolerances = {'temperature': 3.0, 'humidity': 5.0, 'air_velocity': 0.5}

        result = conditions.check_tolerance(target, tolerances)

        self.assertFalse(result)
        self.assertFalse(conditions.in_tolerance)


class TestSpecimenData(unittest.TestCase):
    """Test SpecimenData dataclass"""

    def test_specimen_data_creation(self):
        """Test creating SpecimenData instance"""
        specimen = SpecimenData(
            specimen_id="SPEC-001",
            specimen_type="PV Module",
            manufacturer="Test Manufacturer",
            model="Model-X",
            serial_number="SN12345",
            initial_weight=5000.0,
            initial_dimensions=(1000.0, 600.0, 40.0),
            initial_surface_roughness=0.5
        )

        self.assertEqual(specimen.specimen_id, "SPEC-001")
        self.assertEqual(specimen.specimen_type, "PV Module")
        self.assertEqual(specimen.initial_weight, 5000.0)
        self.assertIsNone(specimen.post_weight)
        self.assertIsNone(specimen.ingress_severity)

    def test_specimen_data_with_post_measurements(self):
        """Test SpecimenData with post-test measurements"""
        specimen = SpecimenData(
            specimen_id="SPEC-001",
            specimen_type="PV Module",
            manufacturer="Test Manufacturer",
            model="Model-X",
            serial_number="SN12345",
            initial_weight=5000.0,
            initial_dimensions=(1000.0, 600.0, 40.0),
            initial_surface_roughness=0.5,
            post_weight=5002.5,
            post_dimensions=(1000.0, 600.0, 40.0),
            post_surface_roughness=0.7,
            deposited_dust_weight=2.5,
            ingress_severity=SeverityLevel.LEVEL_2
        )

        self.assertEqual(specimen.post_weight, 5002.5)
        self.assertEqual(specimen.deposited_dust_weight, 2.5)
        self.assertEqual(specimen.ingress_severity, SeverityLevel.LEVEL_2)


class TestTestConfiguration(unittest.TestCase):
    """Test TestConfiguration dataclass"""

    def test_test_configuration_creation(self):
        """Test creating TestConfiguration instance"""
        config = TestConfiguration(
            dust_type="Arizona Test Dust",
            particle_size_range=(0.1, 200.0, 50.0),
            dust_concentration=0.01,
            target_temperature=25.0,
            target_humidity=50.0,
            target_air_velocity=2.0,
            exposure_time_hours=8.0,
            cycles=1,
            settling_time_hours=1.0
        )

        self.assertEqual(config.dust_type, "Arizona Test Dust")
        self.assertEqual(config.exposure_time_hours, 8.0)
        self.assertTrue(config.tracking_enabled)
        self.assertEqual(config.sampling_interval_seconds, 60)

    def test_configuration_from_protocol(self):
        """Test loading configuration from protocol JSON"""
        # Create temporary protocol file
        protocol_data = {
            "test_parameters": {
                "test_dust": {
                    "properties": {
                        "dust_type": {"default": "Arizona Test Dust"},
                        "dust_concentration": {"default": 0.01}
                    }
                },
                "environmental_conditions": {
                    "properties": {
                        "temperature": {"default": 25},
                        "relative_humidity": {"default": 50},
                        "air_velocity": {"default": 2}
                    }
                },
                "test_duration": {
                    "properties": {
                        "exposure_time": {"default": 8},
                        "cycles": {"default": 1},
                        "settling_time": {"default": 1}
                    }
                },
                "particle_tracking": {
                    "properties": {
                        "tracking_enabled": {"default": True},
                        "sampling_interval": {"default": 60}
                    }
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(protocol_data, f)
            temp_path = f.name

        try:
            config = TestConfiguration.from_protocol(temp_path)
            self.assertEqual(config.dust_type, "Arizona Test Dust")
            self.assertEqual(config.target_temperature, 25.0)
            self.assertEqual(config.exposure_time_hours, 8.0)
        finally:
            Path(temp_path).unlink()


class TestParticleTracker(unittest.TestCase):
    """Test ParticleTracker class"""

    def setUp(self):
        """Set up test fixtures"""
        self.measurement_points = [
            {'point_id': 'P001', 'location': (100, 200, 300)},
            {'point_id': 'P002', 'location': (400, 200, 300)},
            {'point_id': 'P003', 'location': (700, 200, 300)}
        ]
        self.tracker = ParticleTracker(self.measurement_points, sampling_interval=60)

    def test_particle_tracker_initialization(self):
        """Test ParticleTracker initialization"""
        self.assertEqual(len(self.tracker.measurement_points), 3)
        self.assertEqual(self.tracker.sampling_interval, 60)
        self.assertEqual(len(self.tracker.particle_history), 0)

    def test_record_measurement(self):
        """Test recording a particle measurement"""
        data = self.tracker.record_measurement(
            point_id='P001',
            location=(100.0, 200.0, 300.0),
            particle_size=50.0,
            count=1000,
            concentration=0.01,
            velocity=(1.5, 0.5, 0.2),
            temperature=25.0,
            humidity=50.0
        )

        self.assertIsInstance(data, ParticleData)
        self.assertEqual(len(self.tracker.particle_history), 1)
        self.assertEqual(data.point_id, 'P001')
        self.assertEqual(data.particle_count, 1000)

    def test_get_particle_distribution(self):
        """Test getting particle distribution by point"""
        # Record measurements for different points
        self.tracker.record_measurement('P001', (100, 200, 300), 50, 1000, 0.01, (1, 0, 0), 25, 50)
        self.tracker.record_measurement('P002', (400, 200, 300), 60, 1100, 0.011, (1, 0, 0), 25, 50)
        self.tracker.record_measurement('P001', (100, 200, 300), 55, 1050, 0.0105, (1, 0, 0), 25, 50)

        distribution = self.tracker.get_particle_distribution()

        self.assertEqual(len(distribution), 2)
        self.assertEqual(len(distribution['P001']), 2)
        self.assertEqual(len(distribution['P002']), 1)

    def test_get_particle_distribution_with_time_range(self):
        """Test getting particle distribution with time filtering"""
        base_time = datetime.now()

        # Manually set timestamps
        data1 = ParticleData(base_time - timedelta(hours=2), 'P001', (100, 200, 300), 50, 1000, 0.01, (1, 0, 0), 25, 50)
        data2 = ParticleData(base_time - timedelta(minutes=30), 'P001', (100, 200, 300), 55, 1050, 0.0105, (1, 0, 0), 25, 50)
        data3 = ParticleData(base_time, 'P002', (400, 200, 300), 60, 1100, 0.011, (1, 0, 0), 25, 50)

        self.tracker.particle_history = [data1, data2, data3]

        # Get only recent data (last hour)
        distribution = self.tracker.get_particle_distribution(
            start_time=base_time - timedelta(hours=1)
        )

        total_measurements = sum(len(measurements) for measurements in distribution.values())
        self.assertEqual(total_measurements, 2)  # Should only include data2 and data3

    def test_calculate_uniformity_single_point(self):
        """Test uniformity calculation with single measurement"""
        uniformity = self.tracker.calculate_uniformity()
        self.assertEqual(uniformity, 1.0)  # Single point should be perfectly uniform

    def test_calculate_uniformity_uniform_distribution(self):
        """Test uniformity calculation with uniform distribution"""
        # Add measurements with same concentration at all points
        for point_id in ['P001', 'P002', 'P003']:
            self.tracker.record_measurement(point_id, (100, 200, 300), 50, 1000, 0.01, (1, 0, 0), 25, 50)

        uniformity = self.tracker.calculate_uniformity()
        self.assertGreater(uniformity, 0.99)  # Should be very close to 1

    def test_calculate_uniformity_non_uniform_distribution(self):
        """Test uniformity calculation with non-uniform distribution"""
        # Add measurements with varying concentrations
        self.tracker.record_measurement('P001', (100, 200, 300), 50, 1000, 0.005, (1, 0, 0), 25, 50)
        self.tracker.record_measurement('P002', (400, 200, 300), 60, 1100, 0.010, (1, 0, 0), 25, 50)
        self.tracker.record_measurement('P003', (700, 200, 300), 70, 1200, 0.020, (1, 0, 0), 25, 50)

        uniformity = self.tracker.calculate_uniformity()
        self.assertLess(uniformity, 1.0)  # Should indicate non-uniformity

    def test_get_deposition_rate(self):
        """Test deposition rate calculation"""
        # Add recent measurements
        for i in range(5):
            self.tracker.record_measurement('P001', (100, 200, 300), 50, 1000, 0.01, (1, 0, 0), 25, 50)

        rates = self.tracker.get_deposition_rate(time_window_minutes=60)

        self.assertIn('P001', rates)
        self.assertGreater(rates['P001'], 0)

    def test_export_data(self):
        """Test exporting particle data"""
        # Add some measurements
        self.tracker.record_measurement('P001', (100, 200, 300), 50, 1000, 0.01, (1, 0, 0), 25, 50)
        self.tracker.record_measurement('P002', (400, 200, 300), 60, 1100, 0.011, (1, 0, 0), 25, 50)

        # Export to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name

        try:
            self.tracker.export_data(temp_path)

            # Verify file was created and contains data
            self.assertTrue(Path(temp_path).exists())

            with open(temp_path, 'r') as f:
                data = json.load(f)

            self.assertEqual(len(data), 2)
            self.assertEqual(data[0]['point_id'], 'P001')
        finally:
            Path(temp_path).unlink()


class TestSandDustResistanceTest(unittest.TestCase):
    """Test SandDustResistanceTest main class"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = TestConfiguration(
            dust_type="Arizona Test Dust",
            particle_size_range=(0.1, 200.0, 50.0),
            dust_concentration=0.01,
            target_temperature=25.0,
            target_humidity=50.0,
            target_air_velocity=2.0,
            exposure_time_hours=8.0,
            cycles=1,
            settling_time_hours=1.0
        )

        self.specimen = SpecimenData(
            specimen_id="SPEC-001",
            specimen_type="PV Module",
            manufacturer="Test Manufacturer",
            model="Model-X",
            serial_number="SN12345",
            initial_weight=5000.0,
            initial_dimensions=(1000.0, 600.0, 40.0),
            initial_surface_roughness=0.5
        )

        self.test = SandDustResistanceTest("TEST-001", self.config, self.specimen)

    def test_test_initialization(self):
        """Test test instance initialization"""
        self.assertEqual(self.test.test_id, "TEST-001")
        self.assertEqual(self.test.phase, TestPhase.INITIALIZATION)
        self.assertIsNone(self.test.start_time)
        self.assertIsNone(self.test.end_time)
        self.assertIsNone(self.test.test_passed)
        self.assertEqual(len(self.test.deviations), 0)

    def test_start_test(self):
        """Test starting a test"""
        self.test.start_test()

        self.assertIsNotNone(self.test.start_time)
        self.assertEqual(self.test.phase, TestPhase.PRE_CONDITIONING)
        self.assertEqual(self.test.results['test_id'], "TEST-001")

    def test_advance_phase(self):
        """Test advancing test phase"""
        self.test.start_test()
        self.test.advance_phase(TestPhase.CHAMBER_PREP)

        self.assertEqual(self.test.phase, TestPhase.CHAMBER_PREP)

    def test_record_environmental_conditions_within_tolerance(self):
        """Test recording environmental conditions within tolerance"""
        self.test.start_test()
        self.test.advance_phase(TestPhase.DUST_EXPOSURE)

        conditions = self.test.record_environmental_conditions(
            temperature=26.0,  # Within 3°C tolerance
            humidity=52.0,     # Within 5% tolerance
            air_velocity=2.3,  # Within 0.5 m/s tolerance
            atmospheric_pressure=101.325,
            dust_concentration=0.01
        )

        self.assertTrue(conditions.in_tolerance)
        self.assertEqual(len(self.test.deviations), 0)
        self.assertEqual(len(self.test.environmental_history), 1)

    def test_record_environmental_conditions_out_of_tolerance(self):
        """Test recording environmental conditions out of tolerance"""
        self.test.start_test()
        self.test.advance_phase(TestPhase.DUST_EXPOSURE)

        conditions = self.test.record_environmental_conditions(
            temperature=30.0,  # 5°C over target (tolerance is 3°C)
            humidity=52.0,
            air_velocity=2.3,
            atmospheric_pressure=101.325,
            dust_concentration=0.01
        )

        self.assertFalse(conditions.in_tolerance)
        self.assertGreater(len(self.test.deviations), 0)

    def test_initialize_particle_tracking(self):
        """Test initializing particle tracking"""
        measurement_points = [
            {'point_id': 'P001', 'location': (100, 200, 300)},
            {'point_id': 'P002', 'location': (400, 200, 300)}
        ]

        self.test.initialize_particle_tracking(measurement_points)

        self.assertIsNotNone(self.test.particle_tracker)
        self.assertEqual(len(self.test.particle_tracker.measurement_points), 2)

    def test_record_particle_measurement(self):
        """Test recording particle measurements"""
        measurement_points = [{'point_id': 'P001', 'location': (100, 200, 300)}]
        self.test.initialize_particle_tracking(measurement_points)

        self.test.record_particle_measurement(
            point_id='P001',
            location=(100.0, 200.0, 300.0),
            particle_size=50.0,
            count=1000,
            concentration=0.01,
            velocity=(1.5, 0.5, 0.2),
            temperature=25.0,
            humidity=50.0
        )

        self.assertEqual(len(self.test.particle_tracker.particle_history), 1)

    def test_check_particle_uniformity(self):
        """Test checking particle uniformity"""
        measurement_points = [
            {'point_id': 'P001', 'location': (100, 200, 300)},
            {'point_id': 'P002', 'location': (400, 200, 300)}
        ]
        self.test.initialize_particle_tracking(measurement_points)

        # Add uniform measurements
        self.test.record_particle_measurement('P001', (100, 200, 300), 50, 1000, 0.01, (1, 0, 0), 25, 50)
        self.test.record_particle_measurement('P002', (400, 200, 300), 50, 1000, 0.01, (1, 0, 0), 25, 50)

        is_uniform, uniformity = self.test.check_particle_uniformity(threshold=0.7)

        self.assertTrue(is_uniform)
        self.assertGreaterEqual(uniformity, 0.7)

    def test_record_post_test_measurements(self):
        """Test recording post-test measurements"""
        self.test.record_post_test_measurements(
            weight=5002.5,
            dimensions=(1000.0, 600.0, 40.0),
            surface_roughness=0.7,
            deposited_dust_weight=2.5,
            ingress_severity=SeverityLevel.LEVEL_2,
            electrical_params={'power': 280, 'Isc': 9.5, 'Voc': 38.0, 'FF': 0.78}
        )

        self.assertEqual(self.specimen.post_weight, 5002.5)
        self.assertEqual(self.specimen.deposited_dust_weight, 2.5)
        self.assertEqual(self.specimen.ingress_severity, SeverityLevel.LEVEL_2)

    def test_evaluate_acceptance_criteria_pass(self):
        """Test acceptance criteria evaluation - passing case"""
        # Set up specimen with passing measurements
        self.specimen.initial_electrical_params = {'power': 300, 'Isc': 10.0, 'Voc': 40.0, 'FF': 0.75}

        self.test.record_post_test_measurements(
            weight=5002.0,
            dimensions=(1000.0, 600.0, 40.0),
            surface_roughness=1.0,  # Increase of 0.5, within 2.0 limit
            deposited_dust_weight=2.0,
            ingress_severity=SeverityLevel.LEVEL_2,  # Level 2 passes (≤3)
            electrical_params={'power': 297, 'Isc': 9.9, 'Voc': 39.5, 'FF': 0.74}  # Small changes
        )

        evaluation = self.test.evaluate_acceptance_criteria()

        self.assertTrue(evaluation['dust_ingress']['pass'])
        self.assertTrue(evaluation['electrical_performance']['pass'])
        self.assertTrue(evaluation['surface_degradation']['pass'])
        self.assertTrue(evaluation['overall_pass'])
        self.assertTrue(self.test.test_passed)

    def test_evaluate_acceptance_criteria_fail_ingress(self):
        """Test acceptance criteria evaluation - failing due to dust ingress"""
        self.specimen.initial_electrical_params = {'power': 300, 'Isc': 10.0, 'Voc': 40.0, 'FF': 0.75}

        self.test.record_post_test_measurements(
            weight=5002.0,
            dimensions=(1000.0, 600.0, 40.0),
            surface_roughness=1.0,
            deposited_dust_weight=2.0,
            ingress_severity=SeverityLevel.LEVEL_4,  # Level 4 fails (>3)
            electrical_params={'power': 297, 'Isc': 9.9, 'Voc': 39.5, 'FF': 0.74}
        )

        evaluation = self.test.evaluate_acceptance_criteria()

        self.assertFalse(evaluation['dust_ingress']['pass'])
        self.assertFalse(evaluation['overall_pass'])

    def test_evaluate_acceptance_criteria_fail_power_degradation(self):
        """Test acceptance criteria evaluation - failing due to power degradation"""
        self.specimen.initial_electrical_params = {'power': 300, 'Isc': 10.0, 'Voc': 40.0, 'FF': 0.75}

        self.test.record_post_test_measurements(
            weight=5002.0,
            dimensions=(1000.0, 600.0, 40.0),
            surface_roughness=1.0,
            deposited_dust_weight=2.0,
            ingress_severity=SeverityLevel.LEVEL_2,
            electrical_params={'power': 280, 'Isc': 9.9, 'Voc': 39.5, 'FF': 0.74}  # >5% power loss
        )

        evaluation = self.test.evaluate_acceptance_criteria()

        self.assertFalse(evaluation['electrical_performance']['pass'])
        self.assertFalse(evaluation['overall_pass'])

    def test_evaluate_acceptance_criteria_fail_surface_degradation(self):
        """Test acceptance criteria evaluation - failing due to surface degradation"""
        self.specimen.initial_electrical_params = {'power': 300, 'Isc': 10.0, 'Voc': 40.0, 'FF': 0.75}

        self.test.record_post_test_measurements(
            weight=5002.0,
            dimensions=(1000.0, 600.0, 40.0),
            surface_roughness=3.0,  # Increase of 2.5, exceeds 2.0 limit
            deposited_dust_weight=2.0,
            ingress_severity=SeverityLevel.LEVEL_2,
            electrical_params={'power': 297, 'Isc': 9.9, 'Voc': 39.5, 'FF': 0.74}
        )

        evaluation = self.test.evaluate_acceptance_criteria()

        self.assertFalse(evaluation['surface_degradation']['pass'])
        self.assertFalse(evaluation['overall_pass'])

    def test_complete_test(self):
        """Test completing a test"""
        self.test.start_test()
        self.test.test_passed = True
        self.test.complete_test()

        self.assertIsNotNone(self.test.end_time)
        self.assertEqual(self.test.phase, TestPhase.COMPLETE)
        self.assertIsNotNone(self.test.results['end_time'])

    def test_export_results(self):
        """Test exporting test results"""
        self.test.start_test()
        self.test.test_passed = True
        self.test.complete_test()

        with tempfile.TemporaryDirectory() as temp_dir:
            self.test.export_results(temp_dir)

            results_file = Path(temp_dir) / f"{self.test.test_id}_results.json"
            self.assertTrue(results_file.exists())

            with open(results_file, 'r') as f:
                results = json.load(f)

            self.assertEqual(results['test_id'], "TEST-001")
            self.assertEqual(results['protocol'], 'SAND-001')

    def test_generate_report_data(self):
        """Test generating report data"""
        self.test.start_test()

        # Add some environmental data
        self.test.record_environmental_conditions(25.0, 50.0, 2.0, 101.325, 0.01)

        self.test.test_passed = True
        self.test.complete_test()

        report_data = self.test.generate_report_data()

        self.assertIn('test_identification', report_data)
        self.assertIn('specimen_details', report_data)
        self.assertIn('environmental_summary', report_data)
        self.assertEqual(report_data['conclusion'], 'PASS')


class TestIntegration(unittest.TestCase):
    """Integration tests for complete test workflow"""

    def test_complete_test_workflow(self):
        """Test complete test workflow from start to finish"""
        # Create configuration
        config = TestConfiguration(
            dust_type="Arizona Test Dust",
            particle_size_range=(0.1, 200.0, 50.0),
            dust_concentration=0.01,
            target_temperature=25.0,
            target_humidity=50.0,
            target_air_velocity=2.0,
            exposure_time_hours=8.0,
            cycles=1,
            settling_time_hours=1.0
        )

        # Create specimen
        specimen = SpecimenData(
            specimen_id="SPEC-INT-001",
            specimen_type="PV Module",
            manufacturer="Integration Test Mfr",
            model="IT-Model",
            serial_number="IT-SN-001",
            initial_weight=5000.0,
            initial_dimensions=(1000.0, 600.0, 40.0),
            initial_surface_roughness=0.5,
            initial_electrical_params={'power': 300, 'Isc': 10.0, 'Voc': 40.0, 'FF': 0.75}
        )

        # Create and start test
        test = SandDustResistanceTest("INT-TEST-001", config, specimen)
        test.start_test()

        # Initialize particle tracking
        measurement_points = [
            {'point_id': 'P001', 'location': (100, 200, 300)},
            {'point_id': 'P002', 'location': (400, 200, 300)},
            {'point_id': 'P003', 'location': (700, 200, 300)}
        ]
        test.initialize_particle_tracking(measurement_points)

        # Simulate test phases
        test.advance_phase(TestPhase.CHAMBER_PREP)
        test.advance_phase(TestPhase.STABILIZATION)
        test.advance_phase(TestPhase.DUST_EXPOSURE)

        # Record environmental data
        for i in range(10):
            test.record_environmental_conditions(
                temperature=25.0 + (i % 3) * 0.5,
                humidity=50.0 + (i % 2) * 1.0,
                air_velocity=2.0 + (i % 2) * 0.1,
                atmospheric_pressure=101.325,
                dust_concentration=0.01 + (i % 2) * 0.0001
            )

        # Record particle measurements
        for i in range(15):
            point_id = f"P00{(i % 3) + 1}"
            test.record_particle_measurement(
                point_id=point_id,
                location=(100.0 * ((i % 3) + 1), 200.0, 300.0),
                particle_size=50.0 + i,
                count=1000 + i * 10,
                concentration=0.01 + i * 0.0001,
                velocity=(1.5, 0.5, 0.2),
                temperature=25.0,
                humidity=50.0
            )

        # Check uniformity
        is_uniform, uniformity = test.check_particle_uniformity()
        self.assertIsNotNone(uniformity)

        # Complete exposure and move to post-assessment
        test.complete_exposure_phase()
        test.advance_phase(TestPhase.POST_ASSESSMENT)

        # Record post-test measurements
        test.record_post_test_measurements(
            weight=5002.0,
            dimensions=(1000.0, 600.0, 40.0),
            surface_roughness=1.2,
            deposited_dust_weight=2.0,
            ingress_severity=SeverityLevel.LEVEL_2,
            electrical_params={'power': 297, 'Isc': 9.9, 'Voc': 39.5, 'FF': 0.74}
        )

        # Evaluate acceptance criteria
        evaluation = test.evaluate_acceptance_criteria()
        self.assertIsNotNone(evaluation)
        self.assertIn('overall_pass', evaluation)

        # Complete test
        test.complete_test()

        # Verify final state
        self.assertIsNotNone(test.end_time)
        self.assertIsNotNone(test.test_passed)
        self.assertEqual(len(test.environmental_history), 10)
        self.assertEqual(len(test.particle_tracker.particle_history), 15)

        # Generate report data
        report_data = test.generate_report_data()
        self.assertIsNotNone(report_data)
        self.assertIn('test_identification', report_data)
        self.assertIn('environmental_summary', report_data)
        self.assertIn('particle_tracking_summary', report_data)

        # Export results
        with tempfile.TemporaryDirectory() as temp_dir:
            test.export_results(temp_dir)

            results_file = Path(temp_dir) / f"{test.test_id}_results.json"
            particle_file = Path(temp_dir) / f"{test.test_id}_particle_data.json"

            self.assertTrue(results_file.exists())
            self.assertTrue(particle_file.exists())


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSeverityLevel))
    suite.addTests(loader.loadTestsFromTestCase(TestParticleData))
    suite.addTests(loader.loadTestsFromTestCase(TestEnvironmentalConditions))
    suite.addTests(loader.loadTestsFromTestCase(TestSpecimenData))
    suite.addTests(loader.loadTestsFromTestCase(TestTestConfiguration))
    suite.addTests(loader.loadTestsFromTestCase(TestParticleTracker))
    suite.addTests(loader.loadTestsFromTestCase(TestSandDustResistanceTest))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
