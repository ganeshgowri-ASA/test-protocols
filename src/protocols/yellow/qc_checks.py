"""
YELLOW-001 Quality Control Module

Quality control checks for EVA yellowing test protocol.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging


class QualityControl:
    """
    Quality control checker for YELLOW-001 protocol.

    Implements various QC checks including equipment calibration,
    environmental monitoring, and measurement validation.
    """

    def __init__(self, protocol_data: Dict[str, Any]):
        """
        Initialize QC checker.

        Args:
            protocol_data: Protocol definition data
        """
        self.protocol_data = protocol_data
        self.qc_config = protocol_data.get('quality_controls', [])
        self.logger = logging.getLogger(__name__)
        self.qc_history: List[Dict[str, Any]] = []

    def check_baseline_control(self, baseline_measurements: Dict[str, float]) -> Dict[str, Any]:
        """
        Verify baseline measurements are reasonable.

        Args:
            baseline_measurements: Dictionary of baseline values

        Returns:
            QC check result
        """
        result = {
            'qc_id': 'baseline_control',
            'qc_type': 'INITIAL_REFERENCE',
            'timestamp': datetime.now().isoformat(),
            'status': 'PASS',
            'details': {},
            'issues': []
        }

        # Check if baseline YI is reasonable (fresh EVA should be < 2 YI)
        yi = baseline_measurements.get('yellow_index', 0)
        if yi > 2.0:
            result['status'] = 'WARNING'
            result['issues'].append(
                f"Baseline YI ({yi:.2f}) is higher than expected for fresh EVA (<2.0)"
            )

        # Check transmittance
        trans = baseline_measurements.get('light_transmittance', 0)
        if trans < 90:
            result['status'] = 'WARNING'
            result['issues'].append(
                f"Baseline transmittance ({trans:.2f}%) is lower than typical (>90%)"
            )

        # Check L* value (should be high for clear/white material)
        l_star = baseline_measurements.get('L_star', 0)
        if l_star < 90:
            result['status'] = 'WARNING'
            result['issues'].append(
                f"Baseline L* ({l_star:.2f}) is lower than expected (>90)"
            )

        result['details'] = {
            'baseline_yi': yi,
            'baseline_transmittance': trans,
            'baseline_L_star': l_star
        }

        self.qc_history.append(result)
        self._log_result(result)

        return result

    def check_equipment_calibration(self, calibration_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify equipment calibration status.

        Args:
            calibration_data: Calibration check data

        Returns:
            QC check result
        """
        result = {
            'qc_id': 'equipment_calibration',
            'qc_type': 'CALIBRATION',
            'timestamp': datetime.now().isoformat(),
            'status': 'PASS',
            'details': {},
            'issues': []
        }

        # Check calibration standards
        standards = ['white_tile', 'green_tile', 'gray_tile']

        for standard in standards:
            if standard in calibration_data:
                deviation = calibration_data[standard].get('deviation_percent', 0)

                if abs(deviation) > 2.0:
                    result['status'] = 'FAIL'
                    result['issues'].append(
                        f"{standard} calibration deviation ({deviation:.2f}%) "
                        f"exceeds ±2% tolerance"
                    )
                elif abs(deviation) > 1.0:
                    if result['status'] == 'PASS':
                        result['status'] = 'WARNING'
                    result['issues'].append(
                        f"{standard} calibration deviation ({deviation:.2f}%) "
                        f"is approaching tolerance limit"
                    )

        # Check calibration date
        cal_date = calibration_data.get('calibration_date')
        if cal_date:
            result['details']['calibration_date'] = cal_date

        self.qc_history.append(result)
        self._log_result(result)

        return result

    def check_environmental_conditions(self, conditions: Dict[str, float],
                                      test_parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify environmental chamber conditions are within tolerance.

        Args:
            conditions: Current environmental conditions
            test_parameters: Target test parameters

        Returns:
            QC check result
        """
        result = {
            'qc_id': 'environmental_monitoring',
            'qc_type': 'ENVIRONMENTAL',
            'timestamp': datetime.now().isoformat(),
            'status': 'PASS',
            'details': {},
            'issues': []
        }

        # Check temperature
        target_temp = test_parameters.get('temperature_celsius', 85)
        temp_tol = test_parameters.get('temperature_tolerance', 2)
        actual_temp = conditions.get('temperature', 0)

        if abs(actual_temp - target_temp) > temp_tol:
            result['status'] = 'FAIL'
            result['issues'].append(
                f"Temperature ({actual_temp:.1f}°C) outside tolerance "
                f"({target_temp}°C ± {temp_tol}°C)"
            )

        # Check humidity
        target_humid = test_parameters.get('humidity_percent', 60)
        humid_tol = test_parameters.get('humidity_tolerance', 5)
        actual_humid = conditions.get('humidity', 0)

        if abs(actual_humid - target_humid) > humid_tol:
            result['status'] = 'FAIL'
            result['issues'].append(
                f"Humidity ({actual_humid:.1f}%) outside tolerance "
                f"({target_humid}% ± {humid_tol}%)"
            )

        # Check UV intensity
        target_uv = test_parameters.get('light_intensity_mw_cm2', 100)
        uv_tol_percent = 10
        actual_uv = conditions.get('uv_intensity', 0)

        uv_deviation = abs(actual_uv - target_uv) / target_uv * 100

        if uv_deviation > uv_tol_percent:
            result['status'] = 'FAIL'
            result['issues'].append(
                f"UV intensity ({actual_uv:.1f} mW/cm²) outside ±10% tolerance "
                f"(target: {target_uv} mW/cm²)"
            )

        result['details'] = {
            'temperature': actual_temp,
            'humidity': actual_humid,
            'uv_intensity': actual_uv,
            'deviations': {
                'temp_deviation': round(actual_temp - target_temp, 2),
                'humid_deviation': round(actual_humid - target_humid, 2),
                'uv_deviation_percent': round(uv_deviation, 2)
            }
        }

        self.qc_history.append(result)
        self._log_result(result)

        return result

    def check_reference_sample_stability(self, reference_baseline: Dict[str, float],
                                        reference_current: Dict[str, float]) -> Dict[str, Any]:
        """
        Check that unexposed reference sample remains stable.

        Args:
            reference_baseline: Reference sample baseline measurements
            reference_current: Reference sample current measurements

        Returns:
            QC check result
        """
        result = {
            'qc_id': 'reference_sample',
            'qc_type': 'REFERENCE',
            'timestamp': datetime.now().isoformat(),
            'status': 'PASS',
            'details': {},
            'issues': []
        }

        # Check each parameter for <5% deviation
        parameters = ['yellow_index', 'light_transmittance', 'L_star']

        for param in parameters:
            baseline = reference_baseline.get(param, 0)
            current = reference_current.get(param, 0)

            if baseline == 0:
                continue

            deviation_percent = abs(current - baseline) / baseline * 100

            if deviation_percent > 5.0:
                result['status'] = 'FAIL'
                result['issues'].append(
                    f"Reference {param} changed by {deviation_percent:.2f}% "
                    f"(threshold: <5%)"
                )
            elif deviation_percent > 3.0:
                if result['status'] == 'PASS':
                    result['status'] = 'WARNING'
                result['issues'].append(
                    f"Reference {param} deviation ({deviation_percent:.2f}%) "
                    f"is approaching limit"
                )

            result['details'][param] = {
                'baseline': round(baseline, 2),
                'current': round(current, 2),
                'deviation_percent': round(deviation_percent, 2)
            }

        self.qc_history.append(result)
        self._log_result(result)

        return result

    def check_measurement_repeatability(self, measurements: List[float],
                                       parameter_name: str,
                                       max_cv_percent: float = 5.0) -> Dict[str, Any]:
        """
        Check repeatability of multiple measurements (e.g., 3 readings per sample).

        Args:
            measurements: List of repeated measurement values
            parameter_name: Name of the parameter
            max_cv_percent: Maximum acceptable coefficient of variation (%)

        Returns:
            QC check result
        """
        result = {
            'qc_id': 'measurement_repeatability',
            'qc_type': 'REPEATABILITY',
            'timestamp': datetime.now().isoformat(),
            'status': 'PASS',
            'details': {},
            'issues': []
        }

        if len(measurements) < 2:
            result['status'] = 'WARNING'
            result['issues'].append("Insufficient measurements for repeatability check")
            return result

        import numpy as np

        mean = np.mean(measurements)
        std = np.std(measurements)

        if mean != 0:
            cv_percent = (std / mean) * 100
        else:
            cv_percent = 0

        if cv_percent > max_cv_percent:
            result['status'] = 'FAIL'
            result['issues'].append(
                f"Coefficient of variation ({cv_percent:.2f}%) exceeds limit ({max_cv_percent}%)"
            )

        result['details'] = {
            'parameter': parameter_name,
            'measurements': [round(m, 3) for m in measurements],
            'mean': round(mean, 3),
            'std_dev': round(std, 3),
            'cv_percent': round(cv_percent, 2),
            'range': round(max(measurements) - min(measurements), 3)
        }

        self.qc_history.append(result)
        self._log_result(result)

        return result

    def check_sample_position(self, position_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify sample position and orientation in chamber.

        Args:
            position_data: Sample position information

        Returns:
            QC check result
        """
        result = {
            'qc_id': 'sample_position',
            'qc_type': 'SETUP',
            'timestamp': datetime.now().isoformat(),
            'status': 'PASS',
            'details': position_data,
            'issues': []
        }

        # Check distance from UV source
        target_distance = 300  # mm
        actual_distance = position_data.get('distance_from_uv_mm', 0)

        if abs(actual_distance - target_distance) > 20:
            result['status'] = 'FAIL'
            result['issues'].append(
                f"Sample distance ({actual_distance}mm) differs from specification "
                f"({target_distance}mm ± 20mm)"
            )

        # Check orientation
        orientation = position_data.get('orientation', '')
        if orientation.lower() != 'horizontal':
            result['status'] = 'WARNING'
            result['issues'].append(
                f"Sample orientation ({orientation}) may not match specification (horizontal)"
            )

        self.qc_history.append(result)
        self._log_result(result)

        return result

    def get_qc_summary(self) -> Dict[str, Any]:
        """
        Get summary of all QC checks performed.

        Returns:
            QC summary statistics
        """
        total_checks = len(self.qc_history)

        if total_checks == 0:
            return {
                'total_checks': 0,
                'status': 'NO_CHECKS'
            }

        status_counts = {
            'PASS': 0,
            'WARNING': 0,
            'FAIL': 0
        }

        for check in self.qc_history:
            status = check.get('status', 'UNKNOWN')
            if status in status_counts:
                status_counts[status] += 1

        overall_status = 'PASS'
        if status_counts['FAIL'] > 0:
            overall_status = 'FAIL'
        elif status_counts['WARNING'] > 0:
            overall_status = 'WARNING'

        summary = {
            'total_checks': total_checks,
            'status_counts': status_counts,
            'overall_status': overall_status,
            'pass_rate': round((status_counts['PASS'] / total_checks) * 100, 1),
            'checks_by_type': self._summarize_by_type()
        }

        return summary

    def _summarize_by_type(self) -> Dict[str, int]:
        """Summarize QC checks by type."""
        type_counts = {}

        for check in self.qc_history:
            qc_type = check.get('qc_type', 'UNKNOWN')
            type_counts[qc_type] = type_counts.get(qc_type, 0) + 1

        return type_counts

    def _log_result(self, result: Dict[str, Any]) -> None:
        """Log QC check result."""
        status = result['status']
        qc_id = result['qc_id']

        if status == 'PASS':
            self.logger.info(f"QC Check {qc_id}: PASS")
        elif status == 'WARNING':
            self.logger.warning(f"QC Check {qc_id}: WARNING - {result.get('issues', [])}")
        elif status == 'FAIL':
            self.logger.error(f"QC Check {qc_id}: FAIL - {result.get('issues', [])}")
