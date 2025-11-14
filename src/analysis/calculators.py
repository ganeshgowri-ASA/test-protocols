"""
Calculators Module
==================

Calculation functions for test protocols, including DIEL-001 specific calculations.
"""

from typing import Dict, Any, Optional
import math
import logging

logger = logging.getLogger(__name__)


class DielectricCalculator:
    """
    Calculator for dielectric withstand test (DIEL-001) specific calculations.

    Based on IEC 61730 MST 15 requirements.
    """

    @staticmethod
    def calculate_test_voltage(max_system_voltage: float) -> float:
        """
        Calculate required test voltage per IEC 61730.

        Formula: Test voltage = 1000V + (2 × maximum system voltage)

        Args:
            max_system_voltage: Maximum rated system voltage (V)

        Returns:
            Required test voltage (V)
        """
        test_voltage = 1000.0 + (2.0 * max_system_voltage)
        logger.debug(f"Calculated test voltage: {test_voltage}V for system voltage: {max_system_voltage}V")
        return test_voltage

    @staticmethod
    def calculate_insulation_resistance_per_area(
        insulation_resistance: float,
        module_area: float
    ) -> float:
        """
        Calculate area-normalized insulation resistance.

        Args:
            insulation_resistance: Measured insulation resistance (MΩ)
            module_area: Module area (m²)

        Returns:
            Insulation resistance per area (MΩ/m²)
        """
        if module_area <= 0:
            raise ValueError("Module area must be positive")

        resistance_per_area = insulation_resistance / module_area
        logger.debug(f"Calculated resistance per area: {resistance_per_area:.2f} MΩ/m²")
        return resistance_per_area

    @staticmethod
    def check_voltage_tolerance(
        calculated_voltage: float,
        applied_voltage: float,
        tolerance: float = 50.0
    ) -> tuple[bool, float]:
        """
        Check if applied voltage is within tolerance of calculated voltage.

        Args:
            calculated_voltage: Calculated test voltage (V)
            applied_voltage: Actually applied voltage (V)
            tolerance: Acceptable tolerance (V), default ±50V per IEC 61730

        Returns:
            Tuple of (is_within_tolerance, deviation)
        """
        deviation = abs(applied_voltage - calculated_voltage)
        within_tolerance = deviation <= tolerance

        logger.debug(f"Voltage deviation: {deviation}V, within tolerance: {within_tolerance}")
        return within_tolerance, deviation

    @staticmethod
    def check_insulation_resistance_minimum(
        insulation_resistance: float,
        module_area: float,
        minimum_per_area: float = 40.0
    ) -> tuple[bool, float]:
        """
        Check if insulation resistance meets minimum requirement.

        IEC 61730 requires minimum 40 MΩ/m².

        Args:
            insulation_resistance: Measured resistance (MΩ)
            module_area: Module area (m²)
            minimum_per_area: Minimum required (MΩ/m²), default 40

        Returns:
            Tuple of (meets_requirement, resistance_per_area)
        """
        resistance_per_area = DielectricCalculator.calculate_insulation_resistance_per_area(
            insulation_resistance, module_area
        )

        meets_requirement = resistance_per_area >= minimum_per_area

        logger.info(
            f"Insulation resistance: {resistance_per_area:.2f} MΩ/m² "
            f"(minimum: {minimum_per_area} MΩ/m²) - {'PASS' if meets_requirement else 'FAIL'}"
        )

        return meets_requirement, resistance_per_area

    @staticmethod
    def check_leakage_current(
        leakage_current_ma: float,
        maximum_allowed: float = 50.0
    ) -> tuple[bool, float]:
        """
        Check if leakage current is within acceptable limits.

        Args:
            leakage_current_ma: Measured leakage current (mA)
            maximum_allowed: Maximum allowed (mA), default 50mA per IEC 61730

        Returns:
            Tuple of (is_acceptable, margin)
        """
        is_acceptable = leakage_current_ma <= maximum_allowed
        margin = maximum_allowed - leakage_current_ma

        logger.info(
            f"Leakage current: {leakage_current_ma}mA "
            f"(max: {maximum_allowed}mA) - {'PASS' if is_acceptable else 'FAIL'}"
        )

        return is_acceptable, margin

    @staticmethod
    def calculate_voltage_ramp_time(
        target_voltage: float,
        initial_voltage: float = 0.0,
        ramp_rate: float = 500.0
    ) -> float:
        """
        Calculate time required for voltage ramp up.

        Args:
            target_voltage: Target voltage (V)
            initial_voltage: Initial voltage (V), default 0
            ramp_rate: Ramp rate (V/s), default 500 V/s per IEC 61730

        Returns:
            Ramp time (seconds)
        """
        voltage_delta = abs(target_voltage - initial_voltage)
        ramp_time = voltage_delta / ramp_rate

        logger.debug(f"Voltage ramp time: {ramp_time:.2f}s at {ramp_rate}V/s")
        return ramp_time

    @staticmethod
    def evaluate_test_result(test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive evaluation of DIEL-001 test results.

        Args:
            test_data: Complete test data dictionary

        Returns:
            Evaluation result dictionary with pass/fail and details
        """
        results = {
            'overall_pass': True,
            'checks': {},
            'failures': [],
            'warnings': []
        }

        # Check 1: Initial insulation resistance
        if 'insulation_resistance_initial' in test_data and 'module_area' in test_data:
            passed, value = DielectricCalculator.check_insulation_resistance_minimum(
                test_data['insulation_resistance_initial'],
                test_data['module_area']
            )
            results['checks']['initial_insulation_resistance'] = {
                'pass': passed,
                'value': value,
                'requirement': '≥ 40 MΩ/m²'
            }
            if not passed:
                results['overall_pass'] = False
                results['failures'].append('Initial insulation resistance below minimum')

        # Check 2: Final insulation resistance
        if 'insulation_resistance_final' in test_data and 'module_area' in test_data:
            passed, value = DielectricCalculator.check_insulation_resistance_minimum(
                test_data['insulation_resistance_final'],
                test_data['module_area']
            )
            results['checks']['final_insulation_resistance'] = {
                'pass': passed,
                'value': value,
                'requirement': '≥ 40 MΩ/m²'
            }
            if not passed:
                results['overall_pass'] = False
                results['failures'].append('Final insulation resistance below minimum')

        # Check 3: Test voltage accuracy
        if all(k in test_data for k in ['test_voltage_calculated', 'test_voltage_applied']):
            passed, deviation = DielectricCalculator.check_voltage_tolerance(
                test_data['test_voltage_calculated'],
                test_data['test_voltage_applied']
            )
            results['checks']['voltage_accuracy'] = {
                'pass': passed,
                'deviation': deviation,
                'requirement': '±50V or ±3%'
            }
            if not passed:
                results['overall_pass'] = False
                results['failures'].append(f'Test voltage out of tolerance (±{deviation:.1f}V)')

        # Check 4: Leakage current
        if 'leakage_current_max' in test_data:
            passed, margin = DielectricCalculator.check_leakage_current(
                test_data['leakage_current_max']
            )
            results['checks']['leakage_current'] = {
                'pass': passed,
                'value': test_data['leakage_current_max'],
                'margin': margin,
                'requirement': '≤ 50 mA'
            }
            if not passed:
                results['overall_pass'] = False
                results['failures'].append('Leakage current exceeds maximum')

        # Check 5: Breakdown occurred
        if 'breakdown_occurred' in test_data:
            breakdown = test_data['breakdown_occurred']
            results['checks']['no_breakdown'] = {
                'pass': not breakdown,
                'requirement': 'No dielectric breakdown'
            }
            if breakdown:
                results['overall_pass'] = False
                results['failures'].append('Dielectric breakdown occurred during test')

        # Check 6: Visual inspection
        if 'visual_inspection_pass' in test_data:
            passed = test_data['visual_inspection_pass']
            results['checks']['visual_inspection'] = {
                'pass': passed,
                'requirement': 'No visible damage after test'
            }
            if not passed:
                results['overall_pass'] = False
                results['failures'].append('Failed visual inspection')

        # Check 7: Test duration
        if 'test_duration' in test_data:
            duration = test_data['test_duration']
            passed = duration >= 60
            results['checks']['test_duration'] = {
                'pass': passed,
                'value': duration,
                'requirement': '≥ 60 seconds'
            }
            if not passed:
                results['overall_pass'] = False
                results['failures'].append(f'Test duration too short ({duration}s < 60s)')

        return results


class TestCalculator:
    """
    General test calculator for common calculations across protocols.
    """

    @staticmethod
    def calculate_deviation(
        measured: float,
        reference: float,
        as_percentage: bool = False
    ) -> float:
        """
        Calculate deviation from reference value.

        Args:
            measured: Measured value
            reference: Reference value
            as_percentage: Return as percentage if True

        Returns:
            Deviation (absolute or percentage)
        """
        deviation = measured - reference

        if as_percentage and reference != 0:
            return (deviation / reference) * 100.0

        return deviation

    @staticmethod
    def calculate_uncertainty(
        measurements: list[float],
        confidence_level: float = 0.95
    ) -> Dict[str, float]:
        """
        Calculate measurement uncertainty.

        Args:
            measurements: List of repeat measurements
            confidence_level: Confidence level for uncertainty

        Returns:
            Dictionary with mean, std_dev, and uncertainty
        """
        if not measurements:
            return {'mean': 0, 'std_dev': 0, 'uncertainty': 0}

        import statistics

        mean = statistics.mean(measurements)
        std_dev = statistics.stdev(measurements) if len(measurements) > 1 else 0

        # Simplified uncertainty calculation
        # For more accurate calculation, use Student's t-distribution
        n = len(measurements)
        uncertainty = std_dev / math.sqrt(n) if n > 0 else 0

        return {
            'mean': mean,
            'std_dev': std_dev,
            'uncertainty': uncertainty,
            'num_measurements': n
        }

    @staticmethod
    def is_within_tolerance(
        value: float,
        target: float,
        tolerance: float,
        tolerance_type: str = 'absolute'
    ) -> bool:
        """
        Check if value is within tolerance of target.

        Args:
            value: Measured value
            target: Target value
            tolerance: Tolerance value
            tolerance_type: 'absolute' or 'percentage'

        Returns:
            True if within tolerance
        """
        if tolerance_type == 'percentage':
            tolerance_abs = abs(target * tolerance / 100.0)
        else:
            tolerance_abs = tolerance

        deviation = abs(value - target)
        return deviation <= tolerance_abs

    @staticmethod
    def normalize_value(
        value: float,
        normalization_factor: float
    ) -> float:
        """
        Normalize a value by a factor.

        Args:
            value: Value to normalize
            normalization_factor: Normalization factor

        Returns:
            Normalized value
        """
        if normalization_factor == 0:
            raise ValueError("Normalization factor cannot be zero")

        return value / normalization_factor

    @staticmethod
    def interpolate(
        x: float,
        x1: float,
        y1: float,
        x2: float,
        y2: float
    ) -> float:
        """
        Linear interpolation between two points.

        Args:
            x: Value to interpolate at
            x1, y1: First point
            x2, y2: Second point

        Returns:
            Interpolated y value
        """
        if x2 == x1:
            return y1

        return y1 + (x - x1) * (y2 - y1) / (x2 - x1)

    @staticmethod
    def calculate_pass_rate(
        total_tests: int,
        passed_tests: int
    ) -> float:
        """
        Calculate pass rate percentage.

        Args:
            total_tests: Total number of tests
            passed_tests: Number of passed tests

        Returns:
            Pass rate as percentage
        """
        if total_tests == 0:
            return 0.0

        return (passed_tests / total_tests) * 100.0


# Convenience functions for DIEL-001

def calculate_diel001_test_voltage(max_system_voltage: float) -> float:
    """Calculate DIEL-001 test voltage"""
    return DielectricCalculator.calculate_test_voltage(max_system_voltage)


def evaluate_diel001_test(test_data: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate complete DIEL-001 test"""
    return DielectricCalculator.evaluate_test_result(test_data)
