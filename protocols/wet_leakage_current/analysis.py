"""Analysis module for WET-001 Wet Leakage Current Test."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from protocols.base import MeasurementPoint
from utils.logging import get_logger

logger = get_logger(__name__)


class WETAnalyzer:
    """Analyzer for wet leakage current test measurements."""

    def __init__(self, acceptance_criteria: Dict[str, Any]):
        """Initialize analyzer with acceptance criteria.

        Args:
            acceptance_criteria: Dictionary containing acceptance thresholds
        """
        self.acceptance_criteria = acceptance_criteria
        self.max_leakage_current = acceptance_criteria.get('max_leakage_current', 0.25)
        self.min_insulation_resistance = acceptance_criteria.get('min_insulation_resistance', 400)
        self.max_voltage_variation = acceptance_criteria.get('max_voltage_variation', 5.0)

        logger.info(f"Initialized WETAnalyzer with criteria: {acceptance_criteria}")

    def analyze_measurements(
        self,
        measurements: List[MeasurementPoint],
        test_voltage: float
    ) -> Dict[str, Any]:
        """Analyze all measurements and determine pass/fail.

        Args:
            measurements: List of measurement points
            test_voltage: Nominal test voltage in volts

        Returns:
            Dictionary containing analysis results
        """
        if not measurements:
            return {
                'passed': False,
                'summary': 'No measurements available',
                'failure_reasons': ['No measurement data']
            }

        # Extract measurement values
        leakage_currents = [m.values.get('leakage_current', 0) for m in measurements]
        voltages = [m.values.get('voltage', 0) for m in measurements]
        insulation_resistances = [m.values.get('insulation_resistance', 0) for m in measurements]

        # Calculate statistics
        stats = self._calculate_statistics(leakage_currents, voltages, insulation_resistances)

        # Check acceptance criteria
        passed, failure_reasons = self._check_acceptance_criteria(
            stats, test_voltage, measurements
        )

        # Generate summary
        summary = self._generate_summary(passed, stats, failure_reasons)

        result = {
            'passed': passed,
            'summary': summary,
            'max_leakage_current_measured': stats['max_leakage'],
            'min_leakage_current_measured': stats['min_leakage'],
            'average_leakage_current': stats['avg_leakage'],
            'std_dev_leakage_current': stats['std_leakage'],
            'min_insulation_resistance_measured': stats['min_insulation'],
            'max_insulation_resistance_measured': stats['max_insulation'],
            'average_insulation_resistance': stats['avg_insulation'],
            'max_voltage_deviation': stats['max_voltage_deviation'],
            'failure_reasons': failure_reasons,
            'measurement_count': len(measurements),
            'test_duration_hours': self._calculate_test_duration(measurements),
        }

        logger.info(f"Analysis complete: {'PASS' if passed else 'FAIL'}")
        return result

    def _calculate_statistics(
        self,
        leakage_currents: List[float],
        voltages: List[float],
        insulation_resistances: List[float]
    ) -> Dict[str, float]:
        """Calculate statistical measures from measurements.

        Args:
            leakage_currents: List of leakage current values in mA
            voltages: List of voltage values in V
            insulation_resistances: List of insulation resistance values in MΩ

        Returns:
            Dictionary of statistical measures
        """
        leakage_array = np.array(leakage_currents)
        voltage_array = np.array(voltages)
        insulation_array = np.array([r for r in insulation_resistances if r > 0])

        stats = {
            'max_leakage': float(np.max(leakage_array)),
            'min_leakage': float(np.min(leakage_array)),
            'avg_leakage': float(np.mean(leakage_array)),
            'std_leakage': float(np.std(leakage_array)),
            'median_leakage': float(np.median(leakage_array)),
        }

        if len(insulation_array) > 0:
            stats.update({
                'max_insulation': float(np.max(insulation_array)),
                'min_insulation': float(np.min(insulation_array)),
                'avg_insulation': float(np.mean(insulation_array)),
                'std_insulation': float(np.std(insulation_array)),
            })
        else:
            stats.update({
                'max_insulation': 0.0,
                'min_insulation': 0.0,
                'avg_insulation': 0.0,
                'std_insulation': 0.0,
            })

        if len(voltage_array) > 0:
            voltage_mean = np.mean(voltage_array)
            if voltage_mean > 0:
                voltage_deviations = np.abs((voltage_array - voltage_mean) / voltage_mean * 100)
                stats['max_voltage_deviation'] = float(np.max(voltage_deviations))
            else:
                stats['max_voltage_deviation'] = 0.0
        else:
            stats['max_voltage_deviation'] = 0.0

        return stats

    def _check_acceptance_criteria(
        self,
        stats: Dict[str, float],
        test_voltage: float,
        measurements: List[MeasurementPoint]
    ) -> Tuple[bool, List[str]]:
        """Check if measurements meet acceptance criteria.

        Args:
            stats: Statistical measures
            test_voltage: Nominal test voltage
            measurements: List of measurements

        Returns:
            Tuple of (passed: bool, failure_reasons: List[str])
        """
        failure_reasons = []

        # Check maximum leakage current
        if stats['max_leakage'] > self.max_leakage_current:
            failure_reasons.append(
                f"Maximum leakage current {stats['max_leakage']:.4f} mA exceeds "
                f"limit of {self.max_leakage_current} mA"
            )

        # Check minimum insulation resistance
        if stats['min_insulation'] > 0 and stats['min_insulation'] < self.min_insulation_resistance:
            failure_reasons.append(
                f"Minimum insulation resistance {stats['min_insulation']:.2f} MΩ "
                f"below limit of {self.min_insulation_resistance} MΩ"
            )

        # Check voltage variation
        if stats['max_voltage_deviation'] > self.max_voltage_variation:
            failure_reasons.append(
                f"Voltage variation {stats['max_voltage_deviation']:.2f}% exceeds "
                f"limit of {self.max_voltage_variation}%"
            )

        # Check for surface tracking or damage (if noted)
        for m in measurements:
            notes = m.notes or ''
            if 'tracking' in notes.lower() or 'breakdown' in notes.lower():
                failure_reasons.append("Surface tracking or breakdown observed")
                break

            if 'damage' in notes.lower():
                failure_reasons.append("Visible damage observed")
                break

        passed = len(failure_reasons) == 0
        return passed, failure_reasons

    def _generate_summary(
        self,
        passed: bool,
        stats: Dict[str, float],
        failure_reasons: List[str]
    ) -> str:
        """Generate human-readable summary of test results.

        Args:
            passed: Whether test passed
            stats: Statistical measures
            failure_reasons: List of failure reasons

        Returns:
            Summary string
        """
        if passed:
            summary = (
                f"Test PASSED. Maximum leakage current: {stats['max_leakage']:.4f} mA, "
                f"Minimum insulation resistance: {stats['min_insulation']:.2f} MΩ. "
                f"All acceptance criteria met."
            )
        else:
            reasons_str = "; ".join(failure_reasons)
            summary = (
                f"Test FAILED. {reasons_str}. "
                f"Maximum leakage current: {stats['max_leakage']:.4f} mA, "
                f"Minimum insulation resistance: {stats['min_insulation']:.2f} MΩ."
            )

        return summary

    def _calculate_test_duration(self, measurements: List[MeasurementPoint]) -> float:
        """Calculate total test duration from measurements.

        Args:
            measurements: List of measurements

        Returns:
            Test duration in hours
        """
        if len(measurements) < 2:
            return 0.0

        start_time = measurements[0].timestamp
        end_time = measurements[-1].timestamp
        duration = (end_time - start_time).total_seconds() / 3600  # Convert to hours

        return round(duration, 2)

    def detect_anomalies(
        self,
        measurements: List[MeasurementPoint],
        threshold_std: float = 3.0
    ) -> List[Tuple[int, str]]:
        """Detect anomalous measurements using statistical methods.

        Args:
            measurements: List of measurements
            threshold_std: Number of standard deviations for anomaly detection

        Returns:
            List of tuples (index, reason) for anomalous measurements
        """
        if len(measurements) < 10:
            return []  # Need sufficient data for anomaly detection

        leakage_currents = np.array([m.values.get('leakage_current', 0) for m in measurements])
        mean = np.mean(leakage_currents)
        std = np.std(leakage_currents)

        anomalies = []
        for i, value in enumerate(leakage_currents):
            z_score = abs((value - mean) / std) if std > 0 else 0
            if z_score > threshold_std:
                anomalies.append((
                    i,
                    f"Leakage current {value:.4f} mA is {z_score:.2f} std dev from mean"
                ))

        logger.info(f"Detected {len(anomalies)} anomalies")
        return anomalies

    def calculate_trending(
        self,
        measurements: List[MeasurementPoint]
    ) -> Dict[str, Any]:
        """Calculate trending information from measurements.

        Args:
            measurements: List of measurements

        Returns:
            Dictionary with trending analysis
        """
        if len(measurements) < 2:
            return {'trend': 'insufficient_data'}

        leakage_currents = np.array([m.values.get('leakage_current', 0) for m in measurements])
        timestamps = np.array([(m.timestamp - measurements[0].timestamp).total_seconds()
                               for m in measurements])

        # Linear regression for trend
        if len(timestamps) > 1:
            coefficients = np.polyfit(timestamps, leakage_currents, 1)
            slope = coefficients[0]

            # Determine trend direction
            if abs(slope) < 1e-6:
                trend = 'stable'
            elif slope > 0:
                trend = 'increasing'
            else:
                trend = 'decreasing'

            return {
                'trend': trend,
                'slope': float(slope),
                'slope_unit': 'mA/second',
                'rate_of_change': float(slope * 3600),  # mA/hour
            }

        return {'trend': 'stable'}
