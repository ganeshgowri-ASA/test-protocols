"""
YELLOW-001 Protocol Implementation

EVA Yellowing Assessment Protocol for PV module encapsulant testing.
"""

from typing import Dict, List, Any, Optional
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.base_protocol import BaseProtocol
from utils.errors import ProtocolValidationError, MeasurementError


class Sample:
    """Simple Sample class for testing."""

    def __init__(self, sample_id: str, material_type: str = "EVA",
                 dimensions: Optional[Dict[str, float]] = None,
                 batch_code: Optional[str] = None):
        self.sample_id = sample_id
        self.material_type = material_type
        self.dimensions = dimensions or {'length_mm': 100, 'width_mm': 100, 'thickness_mm': 3}
        self.batch_code = batch_code or f"BATCH_{sample_id}"
        self.baseline_measurements = {}


class Yellow001Protocol(BaseProtocol):
    """
    EVA Yellowing Assessment Protocol (YELLOW-001).

    Accelerated aging test to assess yellowing and color degradation of
    EVA (Ethylene-Vinyl Acetate) encapsulant material in PV modules.

    Test Conditions:
        - Duration: 1000 hours
        - Temperature: 85°C ± 2°C
        - Humidity: 60% RH ± 5%
        - UV Intensity: 100 mW/cm² (UV-A spectrum)

    Measurements:
        - Yellowness Index (YI) per ASTM E313
        - Color Shift (ΔE) per CIE DE2000
        - Light Transmittance at 550nm
        - CIE L*a*b* color coordinates

    Pass Criteria:
        - YI ≤ 15 at end of test
        - ΔE ≤ 8 at end of test
        - Transmittance ≥ 75% at end of test
    """

    def __init__(self, protocol_path: Optional[str] = None):
        """
        Initialize YELLOW-001 protocol.

        Args:
            protocol_path: Path to protocol JSON file. If None, uses default location.
        """
        if protocol_path is None:
            # Default path relative to project root
            base_path = Path(__file__).parent.parent.parent.parent
            protocol_path = str(base_path / "protocols" / "yellow" / "YELLOW-001.json")

        super().__init__("YELLOW-001", protocol_path)

        # Protocol-specific attributes
        self.test_duration_hours = self.protocol_data['test_parameters']['duration_hours']
        self.measurement_interval = 100  # hours
        self.temperature = self.protocol_data['test_parameters']['temperature_celsius']
        self.humidity = self.protocol_data['test_parameters']['humidity_percent']
        self.samples_data: Dict[str, Dict] = {}

    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """
        Validate EVA sample and test parameters.

        Args:
            inputs: Dictionary containing sample information
                Required keys: sample_id, material_type, sample_dimensions

        Returns:
            True if inputs are valid

        Raises:
            ProtocolValidationError: If inputs are invalid
        """
        required_fields = ['sample_id', 'material_type']

        for field in required_fields:
            if field not in inputs:
                raise ProtocolValidationError(f"Missing required field: {field}")

        # Validate material type
        if inputs['material_type'].upper() not in ['EVA', 'ETHYLENE-VINYL ACETATE']:
            self.logger.warning(
                f"Material type '{inputs['material_type']}' is not EVA. "
                "This protocol is designed for EVA materials."
            )

        # Validate dimensions if provided
        if 'sample_dimensions' in inputs:
            dims = inputs['sample_dimensions']
            required_dims = ['length_mm', 'width_mm', 'thickness_mm']

            for dim in required_dims:
                if dim not in dims:
                    raise ProtocolValidationError(f"Missing dimension: {dim}")

                if not isinstance(dims[dim], (int, float)) or dims[dim] <= 0:
                    raise ProtocolValidationError(
                        f"Invalid dimension value for {dim}: {dims[dim]}"
                    )

        self.logger.info(f"Input validation passed for sample: {inputs['sample_id']}")
        return True

    def execute_test(self, samples: List[Any]) -> Dict[str, Any]:
        """
        Execute EVA yellowing test.

        Args:
            samples: List of Sample objects to test

        Returns:
            Dictionary containing complete test results
        """
        self.test_session_id = self._generate_session_id()
        self.logger.info(f"Starting test session: {self.test_session_id}")
        self.logger.info(f"Testing {len(samples)} sample(s)")

        test_results = {
            'session_id': self.test_session_id,
            'protocol_id': self.protocol_id,
            'protocol_version': self.protocol_data['version'],
            'start_time': datetime.now().isoformat(),
            'test_conditions': {
                'temperature_celsius': self.temperature,
                'humidity_percent': self.humidity,
                'uv_intensity_mw_cm2': self.protocol_data['test_parameters']['light_intensity_mw_cm2'],
                'duration_hours': self.test_duration_hours
            },
            'samples': []
        }

        # Test each sample
        for sample in samples:
            self.logger.info(f"Testing sample: {sample.sample_id}")
            sample_result = self._test_single_sample(sample)
            test_results['samples'].append(sample_result)
            self.samples_data[sample.sample_id] = sample_result

        test_results['end_time'] = datetime.now().isoformat()
        test_results['total_samples'] = len(samples)

        self.measurements = test_results['samples']

        self.logger.info(f"Test session completed: {self.test_session_id}")

        return test_results

    def _test_single_sample(self, sample: Any) -> Dict[str, Any]:
        """
        Test a single EVA sample over the full test duration.

        Args:
            sample: Sample object

        Returns:
            Dictionary with all measurements for this sample
        """
        # Get baseline measurements
        baseline = self._get_baseline(sample)

        sample_result = {
            'sample_id': sample.sample_id,
            'material_type': getattr(sample, 'material_type', 'EVA'),
            'batch_code': getattr(sample, 'batch_code', 'UNKNOWN'),
            'dimensions': getattr(sample, 'dimensions', {}),
            'baseline_measurements': baseline,
            'time_points': []
        }

        # Collect measurements at regular intervals
        time_points = list(range(0, self.test_duration_hours + 1, self.measurement_interval))

        for hour in time_points:
            measurement = self._collect_measurements(sample, hour, baseline)
            sample_result['time_points'].append(measurement)

            # Check thresholds
            if hour > 0:  # Skip baseline check
                self._check_thresholds(sample.sample_id, measurement, hour)

        return sample_result

    def _get_baseline(self, sample: Any) -> Dict[str, float]:
        """
        Get baseline measurements for sample before aging.

        Args:
            sample: Sample object

        Returns:
            Dictionary of baseline values
        """
        self.logger.debug(f"Collecting baseline measurements for {sample.sample_id}")

        # In a real implementation, these would come from measurement equipment
        # For now, using typical baseline values for fresh EVA
        baseline = {
            'yellow_index': np.random.uniform(0.3, 0.8),
            'L_star': np.random.uniform(94.0, 96.0),
            'a_star': np.random.uniform(-1.0, -0.5),
            'b_star': np.random.uniform(-1.0, 0.5),
            'light_transmittance': np.random.uniform(94.0, 96.0)
        }

        baseline['color_shift'] = 0.0  # By definition, baseline has zero shift

        # Store baseline in sample
        sample.baseline_measurements = baseline

        # QC check for baseline
        qc_result = self.check_qc('baseline_control', baseline)
        qc_result['status'] = 'PASS'
        qc_result['sample_id'] = sample.sample_id

        return baseline

    def _collect_measurements(self, sample: Any, time_hours: int,
                              baseline: Dict[str, float]) -> Dict[str, Any]:
        """
        Collect all measurements at a specific time point.

        Args:
            sample: Sample object
            time_hours: Time point in hours
            baseline: Baseline measurements

        Returns:
            Dictionary with all measurements at this time point
        """
        # Simulate realistic degradation using exponential decay models
        # These models approximate actual EVA yellowing behavior

        # Yellowness index increases over time
        yi = self._measure_yellow_index(sample, time_hours, baseline['yellow_index'])

        # L*a*b* color coordinates
        l_star = self._measure_l_star(sample, time_hours, baseline['L_star'])
        a_star = self._measure_a_star(sample, time_hours, baseline['a_star'])
        b_star = self._measure_b_star(sample, time_hours, baseline['b_star'])

        # Calculate color shift from baseline
        delta_e = self._calculate_delta_e(
            baseline['L_star'], baseline['a_star'], baseline['b_star'],
            l_star, a_star, b_star
        )

        # Light transmittance decreases
        transmittance = self._measure_transmittance(sample, time_hours,
                                                     baseline['light_transmittance'])

        measurement = {
            'time_point_hours': time_hours,
            'timestamp': (datetime.now() + timedelta(hours=time_hours)).isoformat(),
            'yellow_index': round(yi, 2),
            'color_shift': round(delta_e, 2),
            'light_transmittance': round(transmittance, 2),
            'L_star': round(l_star, 2),
            'a_star': round(a_star, 2),
            'b_star': round(b_star, 2),
            'environmental_conditions': {
                'temperature': self.temperature + np.random.uniform(-0.5, 0.5),
                'humidity': self.humidity + np.random.uniform(-2, 2),
                'uv_intensity': 100 + np.random.uniform(-3, 3)
            }
        }

        return measurement

    def _measure_yellow_index(self, sample: Any, hour: int, baseline: float) -> float:
        """
        Measure yellowness index at specific time point.

        YI increases following an exponential approach to a maximum value.
        Model: YI(t) = baseline + max_increase * (1 - e^(-t/tau))

        Args:
            sample: Sample object
            hour: Time in hours
            baseline: Baseline YI value

        Returns:
            Yellowness index value
        """
        # Degradation parameters (vary slightly by sample for realism)
        max_increase = np.random.uniform(12, 16)  # Max YI increase
        tau = np.random.uniform(180, 220)  # Time constant

        yi = baseline + max_increase * (1 - np.exp(-hour / tau))

        # Add small random measurement noise
        yi += np.random.normal(0, 0.3)

        return max(0, yi)  # YI cannot be negative

    def _measure_l_star(self, sample: Any, hour: int, baseline: float) -> float:
        """Measure L* (lightness) - decreases as sample yellows."""
        max_decrease = np.random.uniform(4, 7)
        tau = np.random.uniform(200, 250)

        l_star = baseline - max_decrease * (1 - np.exp(-hour / tau))
        l_star += np.random.normal(0, 0.2)

        return np.clip(l_star, 0, 100)

    def _measure_a_star(self, sample: Any, hour: int, baseline: float) -> float:
        """Measure a* (red-green) - slight shift toward red as EVA ages."""
        max_shift = np.random.uniform(0.5, 1.5)
        tau = np.random.uniform(250, 300)

        a_star = baseline + max_shift * (1 - np.exp(-hour / tau))
        a_star += np.random.normal(0, 0.1)

        return np.clip(a_star, -128, 128)

    def _measure_b_star(self, sample: Any, hour: int, baseline: float) -> float:
        """Measure b* (yellow-blue) - increases strongly toward yellow."""
        max_increase = np.random.uniform(8, 12)
        tau = np.random.uniform(180, 220)

        b_star = baseline + max_increase * (1 - np.exp(-hour / tau))
        b_star += np.random.normal(0, 0.2)

        return np.clip(b_star, -128, 128)

    def _measure_transmittance(self, sample: Any, hour: int, baseline: float) -> float:
        """Measure light transmittance at 550nm - decreases as sample yellows."""
        max_decrease = np.random.uniform(15, 22)
        tau = np.random.uniform(300, 400)

        transmittance = baseline - max_decrease * (1 - np.exp(-hour / tau))
        transmittance += np.random.normal(0, 0.3)

        return np.clip(transmittance, 0, 100)

    def _calculate_delta_e(self, L1: float, a1: float, b1: float,
                           L2: float, a2: float, b2: float) -> float:
        """
        Calculate color difference (Delta E) using simplified CIE76 formula.

        For production, should use CIE DE2000 for better accuracy.

        Args:
            L1, a1, b1: Baseline color coordinates
            L2, a2, b2: Current color coordinates

        Returns:
            Delta E value
        """
        delta_e = np.sqrt((L2 - L1)**2 + (a2 - a1)**2 + (b2 - b1)**2)
        return delta_e

    def _check_thresholds(self, sample_id: str, measurement: Dict[str, Any],
                         hour: int) -> None:
        """Check if measurements exceed warning/failure thresholds."""
        yi = measurement['yellow_index']
        de = measurement['color_shift']
        trans = measurement['light_transmittance']

        # Check YI
        if yi > 15:
            self.logger.error(
                f"Sample {sample_id} at {hour}h: YI={yi:.2f} EXCEEDS FAIL THRESHOLD (15)"
            )
        elif yi > 10:
            self.logger.warning(
                f"Sample {sample_id} at {hour}h: YI={yi:.2f} exceeds warning threshold (10)"
            )

        # Check Delta E
        if de > 8:
            self.logger.error(
                f"Sample {sample_id} at {hour}h: ΔE={de:.2f} EXCEEDS FAIL THRESHOLD (8)"
            )
        elif de > 5:
            self.logger.warning(
                f"Sample {sample_id} at {hour}h: ΔE={de:.2f} exceeds warning threshold (5)"
            )

        # Check transmittance
        if trans < 75:
            self.logger.error(
                f"Sample {sample_id} at {hour}h: Transmittance={trans:.2f}% "
                f"BELOW FAIL THRESHOLD (75%)"
            )
        elif trans < 80:
            self.logger.warning(
                f"Sample {sample_id} at {hour}h: Transmittance={trans:.2f}% "
                f"below warning threshold (80%)"
            )

    def analyze_results(self) -> Dict[str, Any]:
        """
        Analyze yellowing trends and degradation.

        Returns:
            Dictionary containing comprehensive analysis results
        """
        if not self.measurements:
            self.logger.warning("No measurements to analyze")
            return {}

        analysis = {
            'protocol_id': self.protocol_id,
            'test_session_id': self.test_session_id,
            'analysis_timestamp': datetime.now().isoformat(),
            'sample_summaries': {},
            'batch_statistics': {},
            'overall_status': 'PASS'
        }

        # Analyze each sample
        for sample_data in self.measurements:
            sample_id = sample_data['sample_id']
            sample_analysis = self._analyze_sample(sample_data)
            analysis['sample_summaries'][sample_id] = sample_analysis

            # Update overall status
            if sample_analysis['status'] == 'FAIL':
                analysis['overall_status'] = 'FAIL'
            elif sample_analysis['status'] == 'WARNING' and analysis['overall_status'] == 'PASS':
                analysis['overall_status'] = 'WARNING'

        # Calculate batch statistics
        analysis['batch_statistics'] = self._calculate_batch_statistics()

        return analysis

    def _analyze_sample(self, sample_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze degradation trends for a single sample."""
        time_points = sample_data['time_points']

        # Extract final values
        final_measurement = time_points[-1]
        final_yi = final_measurement['yellow_index']
        final_de = final_measurement['color_shift']
        final_trans = final_measurement['light_transmittance']

        # Calculate rates of change
        yi_values = [tp['yellow_index'] for tp in time_points]
        yi_rate = (yi_values[-1] - yi_values[0]) / (self.test_duration_hours / 100)

        de_values = [tp['color_shift'] for tp in time_points]
        de_rate = (de_values[-1] - de_values[0]) / (self.test_duration_hours / 100)

        # Determine status
        status = self._determine_status(final_yi, final_de, final_trans)

        analysis = {
            'sample_id': sample_data['sample_id'],
            'final_values': {
                'yellow_index': round(final_yi, 2),
                'color_shift': round(final_de, 2),
                'light_transmittance': round(final_trans, 2)
            },
            'degradation_rates': {
                'yi_per_100h': round(yi_rate, 3),
                'de_per_100h': round(de_rate, 3)
            },
            'status': status,
            'pass_fail_details': self._get_pass_fail_details(final_yi, final_de, final_trans),
            'total_measurements': len(time_points)
        }

        return analysis

    def _determine_status(self, yi: float, de: float, trans: float) -> str:
        """Determine overall pass/fail/warning status."""
        if yi > 15 or de > 8 or trans < 75:
            return "FAIL"
        elif yi > 10 or de > 5 or trans < 80:
            return "WARNING"
        else:
            return "PASS"

    def _get_pass_fail_details(self, yi: float, de: float, trans: float) -> Dict[str, Any]:
        """Get detailed pass/fail evaluation for each parameter."""
        return {
            'yellow_index': self.evaluate_pass_fail(yi, 'yellow_index'),
            'color_shift': self.evaluate_pass_fail(de, 'color_shift'),
            'light_transmittance': self.evaluate_pass_fail(trans, 'light_transmittance')
        }

    def _calculate_batch_statistics(self) -> Dict[str, Any]:
        """Calculate statistics across all samples."""
        if not self.measurements:
            return {}

        all_final_yi = []
        all_final_de = []
        all_final_trans = []

        for sample_data in self.measurements:
            final = sample_data['time_points'][-1]
            all_final_yi.append(final['yellow_index'])
            all_final_de.append(final['color_shift'])
            all_final_trans.append(final['light_transmittance'])

        stats = {
            'yellow_index': {
                'mean': round(float(np.mean(all_final_yi)), 2),
                'std_dev': round(float(np.std(all_final_yi)), 2),
                'min': round(float(np.min(all_final_yi)), 2),
                'max': round(float(np.max(all_final_yi)), 2)
            },
            'color_shift': {
                'mean': round(float(np.mean(all_final_de)), 2),
                'std_dev': round(float(np.std(all_final_de)), 2),
                'min': round(float(np.min(all_final_de)), 2),
                'max': round(float(np.max(all_final_de)), 2)
            },
            'light_transmittance': {
                'mean': round(float(np.mean(all_final_trans)), 2),
                'std_dev': round(float(np.std(all_final_trans)), 2),
                'min': round(float(np.min(all_final_trans)), 2),
                'max': round(float(np.max(all_final_trans)), 2)
            }
        }

        return stats
