"""
SAND-001: Sand and Dust Resistance Test
IEC 60068-2-68 Implementation with Real-time Particle Tracking

This module provides a comprehensive implementation for conducting sand and dust
resistance testing on photovoltaic modules and components according to IEC 60068-2-68.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import numpy as np
from pathlib import Path


class TestPhase(Enum):
    """Test execution phases"""
    INITIALIZATION = "initialization"
    PRE_CONDITIONING = "pre_conditioning"
    CHAMBER_PREP = "chamber_preparation"
    STABILIZATION = "environmental_stabilization"
    DUST_EXPOSURE = "dust_exposure"
    SETTLING = "settling_period"
    POST_ASSESSMENT = "post_exposure_assessment"
    COMPLETE = "complete"
    FAILED = "failed"


class SeverityLevel(Enum):
    """Dust ingress severity levels per IEC 60068-2-68"""
    LEVEL_1 = (1, "No visible dust ingress")
    LEVEL_2 = (2, "Superficial dust, easily removable, no functional impact")
    LEVEL_3 = (3, "Dust ingress but no impairment of function")
    LEVEL_4 = (4, "Dust ingress causing partial functional impairment")
    LEVEL_5 = (5, "Dust ingress causing complete functional failure")

    def __init__(self, level: int, description: str):
        self.level = level
        self.description = description


@dataclass
class ParticleData:
    """Real-time particle tracking data"""
    timestamp: datetime
    point_id: str
    location: Tuple[float, float, float]  # x, y, z coordinates
    particle_size_microns: float
    particle_count: int
    concentration: float  # kg/m³
    velocity: Tuple[float, float, float]  # velocity vector m/s
    temperature: float  # °C
    humidity: float  # %

    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'point_id': self.point_id,
            'location': {'x': self.location[0], 'y': self.location[1], 'z': self.location[2]},
            'particle_size_microns': self.particle_size_microns,
            'particle_count': self.particle_count,
            'concentration': self.concentration,
            'velocity': {'vx': self.velocity[0], 'vy': self.velocity[1], 'vz': self.velocity[2]},
            'temperature': self.temperature,
            'humidity': self.humidity
        }


@dataclass
class EnvironmentalConditions:
    """Environmental conditions during test"""
    timestamp: datetime
    temperature: float  # °C
    humidity: float  # %
    air_velocity: float  # m/s
    atmospheric_pressure: float  # kPa
    dust_concentration: float  # kg/m³
    in_tolerance: bool = True

    def check_tolerance(self, target: Dict[str, float], tolerances: Dict[str, float]) -> bool:
        """Check if conditions are within tolerance"""
        checks = [
            abs(self.temperature - target['temperature']) <= tolerances.get('temperature', 3),
            abs(self.humidity - target['humidity']) <= tolerances.get('humidity', 5),
            abs(self.air_velocity - target['air_velocity']) <= tolerances.get('air_velocity', 0.5)
        ]
        self.in_tolerance = all(checks)
        return self.in_tolerance


@dataclass
class SpecimenData:
    """Specimen information and measurements"""
    specimen_id: str
    specimen_type: str
    manufacturer: str
    model: str
    serial_number: str
    initial_weight: float  # grams
    initial_dimensions: Tuple[float, float, float]  # length, width, height in mm
    initial_surface_roughness: float  # μm
    initial_electrical_params: Optional[Dict[str, float]] = None
    post_weight: Optional[float] = None
    post_dimensions: Optional[Tuple[float, float, float]] = None
    post_surface_roughness: Optional[float] = None
    post_electrical_params: Optional[Dict[str, float]] = None
    deposited_dust_weight: Optional[float] = None
    ingress_severity: Optional[SeverityLevel] = None
    photos: List[str] = field(default_factory=list)


@dataclass
class TestConfiguration:
    """Test configuration parameters"""
    dust_type: str
    particle_size_range: Tuple[float, float, float]  # min, max, median in μm
    dust_concentration: float  # kg/m³
    target_temperature: float  # °C
    target_humidity: float  # %
    target_air_velocity: float  # m/s
    exposure_time_hours: float
    cycles: int
    settling_time_hours: float
    tracking_enabled: bool = True
    sampling_interval_seconds: int = 60

    @classmethod
    def from_protocol(cls, protocol_path: str) -> 'TestConfiguration':
        """Load configuration from protocol JSON"""
        with open(protocol_path, 'r') as f:
            protocol = json.load(f)

        params = protocol['test_parameters']
        return cls(
            dust_type=params['test_dust']['properties']['dust_type']['default'],
            particle_size_range=(0.1, 200, 50),  # Example values
            dust_concentration=params['test_dust']['properties']['dust_concentration']['default'],
            target_temperature=params['environmental_conditions']['properties']['temperature']['default'],
            target_humidity=params['environmental_conditions']['properties']['relative_humidity'].get('default', 50),
            target_air_velocity=params['environmental_conditions']['properties']['air_velocity']['default'],
            exposure_time_hours=params['test_duration']['properties']['exposure_time']['default'],
            cycles=params['test_duration']['properties']['cycles']['default'],
            settling_time_hours=params['test_duration']['properties']['settling_time']['default'],
            tracking_enabled=params['particle_tracking']['properties']['tracking_enabled']['default'],
            sampling_interval_seconds=params['particle_tracking']['properties']['sampling_interval']['default']
        )


class ParticleTracker:
    """Real-time particle tracking system"""

    def __init__(self, measurement_points: List[Dict], sampling_interval: int = 60):
        """
        Initialize particle tracker

        Args:
            measurement_points: List of measurement point configurations
            sampling_interval: Sampling interval in seconds
        """
        self.measurement_points = measurement_points
        self.sampling_interval = sampling_interval
        self.particle_history: List[ParticleData] = []
        self.logger = logging.getLogger(__name__)

    def record_measurement(self, point_id: str, location: Tuple[float, float, float],
                          particle_size: float, count: int, concentration: float,
                          velocity: Tuple[float, float, float],
                          temperature: float, humidity: float) -> ParticleData:
        """
        Record a particle measurement

        Args:
            point_id: Measurement point identifier
            location: (x, y, z) coordinates in mm
            particle_size: Particle size in microns
            count: Particle count
            concentration: Dust concentration in kg/m³
            velocity: Velocity vector (vx, vy, vz) in m/s
            temperature: Temperature in °C
            humidity: Relative humidity in %

        Returns:
            ParticleData object
        """
        data = ParticleData(
            timestamp=datetime.now(),
            point_id=point_id,
            location=location,
            particle_size_microns=particle_size,
            particle_count=count,
            concentration=concentration,
            velocity=velocity,
            temperature=temperature,
            humidity=humidity
        )
        self.particle_history.append(data)
        return data

    def get_particle_distribution(self, start_time: Optional[datetime] = None,
                                  end_time: Optional[datetime] = None) -> Dict[str, List[ParticleData]]:
        """
        Get particle distribution by measurement point

        Args:
            start_time: Start of time range
            end_time: End of time range

        Returns:
            Dictionary mapping point_id to list of measurements
        """
        filtered = self.particle_history
        if start_time:
            filtered = [p for p in filtered if p.timestamp >= start_time]
        if end_time:
            filtered = [p for p in filtered if p.timestamp <= end_time]

        distribution = {}
        for data in filtered:
            if data.point_id not in distribution:
                distribution[data.point_id] = []
            distribution[data.point_id].append(data)

        return distribution

    def calculate_uniformity(self) -> float:
        """
        Calculate spatial uniformity of particle distribution

        Returns:
            Uniformity coefficient (0-1, where 1 is perfectly uniform)
        """
        if len(self.particle_history) < 2:
            return 1.0

        # Group by point and get average concentration
        point_concentrations = {}
        for data in self.particle_history:
            if data.point_id not in point_concentrations:
                point_concentrations[data.point_id] = []
            point_concentrations[data.point_id].append(data.concentration)

        avg_concentrations = [np.mean(concs) for concs in point_concentrations.values()]

        if len(avg_concentrations) < 2:
            return 1.0

        # Calculate coefficient of variation
        mean_conc = np.mean(avg_concentrations)
        std_conc = np.std(avg_concentrations)

        if mean_conc == 0:
            return 0.0

        cv = std_conc / mean_conc
        # Convert to uniformity (lower CV = higher uniformity)
        uniformity = max(0, 1 - cv)

        return uniformity

    def get_deposition_rate(self, time_window_minutes: int = 60) -> Dict[str, float]:
        """
        Calculate deposition rate for each measurement point

        Args:
            time_window_minutes: Time window for rate calculation

        Returns:
            Dictionary mapping point_id to deposition rate in g/m²/h
        """
        cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
        recent_data = [p for p in self.particle_history if p.timestamp >= cutoff_time]

        deposition_rates = {}
        for point_id in set(p.point_id for p in recent_data):
            point_data = [p for p in recent_data if p.point_id == point_id]
            if len(point_data) < 2:
                deposition_rates[point_id] = 0.0
                continue

            # Estimate deposition rate from concentration changes
            # Simplified calculation: assume some percentage settles
            avg_concentration = np.mean([p.concentration for p in point_data])
            # Rough estimate: 10% of airborne particles deposit per hour
            deposition_rates[point_id] = avg_concentration * 1000 * 0.1  # g/m²/h

        return deposition_rates

    def export_data(self, filepath: str):
        """Export particle tracking data to JSON"""
        data = [p.to_dict() for p in self.particle_history]
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


class SandDustResistanceTest:
    """
    Main class for conducting Sand and Dust Resistance Tests
    according to IEC 60068-2-68
    """

    def __init__(self, test_id: str, config: TestConfiguration, specimen: SpecimenData):
        """
        Initialize test instance

        Args:
            test_id: Unique test identifier
            config: Test configuration
            specimen: Specimen data
        """
        self.test_id = test_id
        self.config = config
        self.specimen = specimen
        self.phase = TestPhase.INITIALIZATION
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.environmental_history: List[EnvironmentalConditions] = []
        self.particle_tracker: Optional[ParticleTracker] = None
        self.test_passed: Optional[bool] = None
        self.deviations: List[str] = []
        self.logger = logging.getLogger(__name__)

        # Test results
        self.results = {
            'test_id': test_id,
            'protocol': 'SAND-001',
            'standard': 'IEC 60068-2-68',
            'start_time': None,
            'end_time': None,
            'specimen': None,
            'configuration': asdict(config),
            'environmental_data': [],
            'particle_data': [],
            'acceptance_criteria': {},
            'test_passed': None,
            'deviations': []
        }

    def initialize_particle_tracking(self, measurement_points: List[Dict]):
        """
        Initialize particle tracking system

        Args:
            measurement_points: List of measurement point configurations
        """
        if self.config.tracking_enabled:
            self.particle_tracker = ParticleTracker(
                measurement_points,
                self.config.sampling_interval_seconds
            )
            self.logger.info(f"Particle tracking initialized with {len(measurement_points)} points")

    def start_test(self):
        """Start the test sequence"""
        self.start_time = datetime.now()
        self.phase = TestPhase.PRE_CONDITIONING
        self.results['start_time'] = self.start_time.isoformat()
        self.logger.info(f"Test {self.test_id} started at {self.start_time}")

    def record_environmental_conditions(self, temperature: float, humidity: float,
                                       air_velocity: float, atmospheric_pressure: float,
                                       dust_concentration: float) -> EnvironmentalConditions:
        """
        Record environmental conditions

        Args:
            temperature: Temperature in °C
            humidity: Relative humidity in %
            air_velocity: Air velocity in m/s
            atmospheric_pressure: Atmospheric pressure in kPa
            dust_concentration: Dust concentration in kg/m³

        Returns:
            EnvironmentalConditions object
        """
        conditions = EnvironmentalConditions(
            timestamp=datetime.now(),
            temperature=temperature,
            humidity=humidity,
            air_velocity=air_velocity,
            atmospheric_pressure=atmospheric_pressure,
            dust_concentration=dust_concentration
        )

        # Check tolerance if in exposure phase
        if self.phase == TestPhase.DUST_EXPOSURE:
            target = {
                'temperature': self.config.target_temperature,
                'humidity': self.config.target_humidity,
                'air_velocity': self.config.target_air_velocity
            }
            tolerances = {
                'temperature': 3,
                'humidity': 5,
                'air_velocity': 0.5
            }
            conditions.check_tolerance(target, tolerances)

            if not conditions.in_tolerance:
                self.deviations.append(
                    f"Environmental conditions out of tolerance at {conditions.timestamp}"
                )
                self.logger.warning("Environmental conditions out of tolerance")

        self.environmental_history.append(conditions)
        return conditions

    def advance_phase(self, new_phase: TestPhase):
        """
        Advance to next test phase

        Args:
            new_phase: Next phase to advance to
        """
        self.logger.info(f"Advancing from {self.phase.value} to {new_phase.value}")
        self.phase = new_phase

    def record_particle_measurement(self, point_id: str, location: Tuple[float, float, float],
                                   particle_size: float, count: int, concentration: float,
                                   velocity: Tuple[float, float, float],
                                   temperature: float, humidity: float):
        """
        Record particle measurement during test

        Args:
            point_id: Measurement point ID
            location: (x, y, z) coordinates
            particle_size: Particle size in microns
            count: Particle count
            concentration: Concentration in kg/m³
            velocity: Velocity vector in m/s
            temperature: Temperature in °C
            humidity: Humidity in %
        """
        if self.particle_tracker:
            self.particle_tracker.record_measurement(
                point_id, location, particle_size, count,
                concentration, velocity, temperature, humidity
            )

    def check_particle_uniformity(self, threshold: float = 0.7) -> Tuple[bool, float]:
        """
        Check if particle distribution is sufficiently uniform

        Args:
            threshold: Minimum acceptable uniformity (0-1)

        Returns:
            Tuple of (is_uniform, uniformity_value)
        """
        if not self.particle_tracker:
            return True, 1.0

        uniformity = self.particle_tracker.calculate_uniformity()
        is_uniform = uniformity >= threshold

        if not is_uniform:
            self.deviations.append(
                f"Non-uniform particle distribution: {uniformity:.3f} < {threshold}"
            )
            self.logger.warning(f"Particle distribution uniformity {uniformity:.3f} below threshold")

        return is_uniform, uniformity

    def complete_exposure_phase(self):
        """Complete dust exposure phase"""
        self.logger.info("Completing dust exposure phase")
        self.advance_phase(TestPhase.SETTLING)

    def record_post_test_measurements(self, weight: float, dimensions: Tuple[float, float, float],
                                     surface_roughness: float, deposited_dust_weight: float,
                                     ingress_severity: SeverityLevel,
                                     electrical_params: Optional[Dict[str, float]] = None):
        """
        Record post-test measurements

        Args:
            weight: Post-test weight in grams
            dimensions: Post-test dimensions (L, W, H) in mm
            surface_roughness: Surface roughness in μm
            deposited_dust_weight: Weight of deposited dust in grams
            ingress_severity: Dust ingress severity level
            electrical_params: Electrical parameters (optional)
        """
        self.specimen.post_weight = weight
        self.specimen.post_dimensions = dimensions
        self.specimen.post_surface_roughness = surface_roughness
        self.specimen.deposited_dust_weight = deposited_dust_weight
        self.specimen.ingress_severity = ingress_severity
        self.specimen.post_electrical_params = electrical_params

        self.logger.info("Post-test measurements recorded")

    def evaluate_acceptance_criteria(self) -> Dict[str, Any]:
        """
        Evaluate test results against acceptance criteria

        Returns:
            Dictionary with evaluation results
        """
        evaluation = {
            'dust_ingress': {'pass': False, 'severity_level': None, 'details': ''},
            'electrical_performance': {'pass': True, 'details': []},
            'physical_integrity': {'pass': True, 'details': []},
            'surface_degradation': {'pass': True, 'details': []},
            'overall_pass': False
        }

        # Check dust ingress
        if self.specimen.ingress_severity:
            severity_level = self.specimen.ingress_severity.level
            evaluation['dust_ingress']['severity_level'] = severity_level
            evaluation['dust_ingress']['details'] = self.specimen.ingress_severity.description
            evaluation['dust_ingress']['pass'] = severity_level <= 3

        # Check electrical performance
        if self.specimen.initial_electrical_params and self.specimen.post_electrical_params:
            initial = self.specimen.initial_electrical_params
            post = self.specimen.post_electrical_params

            # Check power degradation
            if 'power' in initial and 'power' in post:
                power_change = abs((post['power'] - initial['power']) / initial['power'] * 100)
                if power_change > 5:
                    evaluation['electrical_performance']['pass'] = False
                    evaluation['electrical_performance']['details'].append(
                        f"Power degradation {power_change:.2f}% exceeds 5% limit"
                    )

            # Check Isc, Voc, FF changes
            for param, limit in [('Isc', 3), ('Voc', 3), ('FF', 5)]:
                if param in initial and param in post:
                    change = abs((post[param] - initial[param]) / initial[param] * 100)
                    if change > limit:
                        evaluation['electrical_performance']['pass'] = False
                        evaluation['electrical_performance']['details'].append(
                            f"{param} change {change:.2f}% exceeds {limit}% limit"
                        )

        # Check surface degradation
        roughness_increase = self.specimen.post_surface_roughness - self.specimen.initial_surface_roughness
        if roughness_increase > 2.0:
            evaluation['surface_degradation']['pass'] = False
            evaluation['surface_degradation']['details'].append(
                f"Surface roughness increased by {roughness_increase:.2f} μm (limit: 2.0 μm)"
            )

        # Overall pass/fail
        evaluation['overall_pass'] = all([
            evaluation['dust_ingress']['pass'],
            evaluation['electrical_performance']['pass'],
            evaluation['physical_integrity']['pass'],
            evaluation['surface_degradation']['pass']
        ])

        self.test_passed = evaluation['overall_pass']
        self.results['acceptance_criteria'] = evaluation
        self.results['test_passed'] = self.test_passed

        return evaluation

    def complete_test(self):
        """Complete the test and finalize results"""
        self.end_time = datetime.now()
        self.phase = TestPhase.COMPLETE if self.test_passed else TestPhase.FAILED
        self.results['end_time'] = self.end_time.isoformat()
        self.results['deviations'] = self.deviations

        # Add specimen data
        self.results['specimen'] = {
            'specimen_id': self.specimen.specimen_id,
            'type': self.specimen.specimen_type,
            'manufacturer': self.specimen.manufacturer,
            'model': self.specimen.model,
            'serial_number': self.specimen.serial_number,
            'initial_measurements': {
                'weight': self.specimen.initial_weight,
                'dimensions': self.specimen.initial_dimensions,
                'surface_roughness': self.specimen.initial_surface_roughness,
                'electrical_params': self.specimen.initial_electrical_params
            },
            'post_measurements': {
                'weight': self.specimen.post_weight,
                'dimensions': self.specimen.post_dimensions,
                'surface_roughness': self.specimen.post_surface_roughness,
                'electrical_params': self.specimen.post_electrical_params,
                'deposited_dust_weight': self.specimen.deposited_dust_weight,
                'ingress_severity': self.specimen.ingress_severity.level if self.specimen.ingress_severity else None
            }
        }

        # Add environmental data
        self.results['environmental_data'] = [
            {
                'timestamp': e.timestamp.isoformat(),
                'temperature': e.temperature,
                'humidity': e.humidity,
                'air_velocity': e.air_velocity,
                'atmospheric_pressure': e.atmospheric_pressure,
                'dust_concentration': e.dust_concentration,
                'in_tolerance': e.in_tolerance
            }
            for e in self.environmental_history
        ]

        self.logger.info(f"Test {self.test_id} completed. Result: {'PASS' if self.test_passed else 'FAIL'}")

    def export_results(self, output_dir: str):
        """
        Export test results to files

        Args:
            output_dir: Directory to save results
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Export main results
        results_file = output_path / f"{self.test_id}_results.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        # Export particle tracking data
        if self.particle_tracker:
            particle_file = output_path / f"{self.test_id}_particle_data.json"
            self.particle_tracker.export_data(str(particle_file))

        self.logger.info(f"Results exported to {output_dir}")

    def generate_report_data(self) -> Dict[str, Any]:
        """
        Generate structured data for report generation

        Returns:
            Dictionary with all report data
        """
        report_data = {
            'test_identification': {
                'test_id': self.test_id,
                'protocol': 'SAND-001',
                'standard': 'IEC 60068-2-68',
                'test_date': self.start_time.strftime('%Y-%m-%d') if self.start_time else None,
                'duration_hours': (self.end_time - self.start_time).total_seconds() / 3600 if self.end_time and self.start_time else None
            },
            'specimen_details': asdict(self.specimen) if hasattr(self.specimen, '__dict__') else {},
            'test_configuration': asdict(self.config),
            'environmental_summary': self._summarize_environmental_data(),
            'particle_tracking_summary': self._summarize_particle_data(),
            'test_results': self.results['acceptance_criteria'],
            'deviations': self.deviations,
            'conclusion': 'PASS' if self.test_passed else 'FAIL'
        }

        return report_data

    def _summarize_environmental_data(self) -> Dict[str, Any]:
        """Summarize environmental monitoring data"""
        if not self.environmental_history:
            return {}

        temps = [e.temperature for e in self.environmental_history]
        humids = [e.humidity for e in self.environmental_history]
        velocities = [e.air_velocity for e in self.environmental_history]
        concentrations = [e.dust_concentration for e in self.environmental_history]

        return {
            'temperature': {
                'mean': np.mean(temps),
                'std': np.std(temps),
                'min': np.min(temps),
                'max': np.max(temps)
            },
            'humidity': {
                'mean': np.mean(humids),
                'std': np.std(humids),
                'min': np.min(humids),
                'max': np.max(humids)
            },
            'air_velocity': {
                'mean': np.mean(velocities),
                'std': np.std(velocities),
                'min': np.min(velocities),
                'max': np.max(velocities)
            },
            'dust_concentration': {
                'mean': np.mean(concentrations),
                'std': np.std(concentrations),
                'min': np.min(concentrations),
                'max': np.max(concentrations)
            },
            'total_samples': len(self.environmental_history),
            'out_of_tolerance_count': sum(1 for e in self.environmental_history if not e.in_tolerance)
        }

    def _summarize_particle_data(self) -> Dict[str, Any]:
        """Summarize particle tracking data"""
        if not self.particle_tracker or not self.particle_tracker.particle_history:
            return {}

        uniformity = self.particle_tracker.calculate_uniformity()
        deposition_rates = self.particle_tracker.get_deposition_rate()
        distribution = self.particle_tracker.get_particle_distribution()

        return {
            'total_measurements': len(self.particle_tracker.particle_history),
            'measurement_points': len(distribution),
            'spatial_uniformity': uniformity,
            'deposition_rates': deposition_rates,
            'measurement_duration_hours': (
                (self.particle_tracker.particle_history[-1].timestamp -
                 self.particle_tracker.particle_history[0].timestamp).total_seconds() / 3600
                if len(self.particle_tracker.particle_history) > 1 else 0
            )
        }


def create_test_from_protocol(test_id: str, protocol_path: str, specimen: SpecimenData) -> SandDustResistanceTest:
    """
    Convenience function to create test from protocol JSON

    Args:
        test_id: Unique test identifier
        protocol_path: Path to protocol JSON file
        specimen: Specimen data

    Returns:
        Configured SandDustResistanceTest instance
    """
    config = TestConfiguration.from_protocol(protocol_path)
    test = SandDustResistanceTest(test_id, config, specimen)
    return test
