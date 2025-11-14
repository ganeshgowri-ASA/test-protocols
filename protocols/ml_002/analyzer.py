"""
ML-002 Data Analysis Module

This module provides comprehensive data analysis capabilities for ML-002 test results:
- Statistical analysis of deflection data
- Load-deflection linearity analysis
- Cyclic behavior analysis
- Quality control evaluation
- Report generation

Author: ganeshgowri-ASA
Date: 2025-11-14
Version: 1.0.0
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import numpy as np
from scipy import stats
from scipy.optimize import curve_fit
import pandas as pd


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class StatisticalSummary:
    """Statistical summary of a dataset"""
    mean: float
    std_dev: float
    min: float
    max: float
    range: float
    median: float
    q25: float
    q75: float
    iqr: float
    coefficient_of_variation: float
    count: int

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary"""
        return {
            'mean': self.mean,
            'std_dev': self.std_dev,
            'min': self.min,
            'max': self.max,
            'range': self.range,
            'median': self.median,
            'q25': self.q25,
            'q75': self.q75,
            'iqr': self.iqr,
            'coefficient_of_variation': self.coefficient_of_variation,
            'count': self.count
        }


@dataclass
class RegressionResults:
    """Linear regression analysis results"""
    slope: float
    intercept: float
    r_squared: float
    p_value: float
    std_error: float
    predicted_values: List[float] = field(default_factory=list)
    residuals: List[float] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'slope': self.slope,
            'intercept': self.intercept,
            'r_squared': self.r_squared,
            'p_value': self.p_value,
            'std_error': self.std_error,
            'equation': f'y = {self.slope:.6f}x + {self.intercept:.6f}',
            'quality': 'excellent' if self.r_squared >= 0.95 else 'good' if self.r_squared >= 0.90 else 'poor'
        }


@dataclass
class CyclicBehaviorAnalysis:
    """Cyclic behavior analysis results"""
    peak_to_peak_variation: StatisticalSummary
    cycle_to_cycle_variation: float
    trend_slope: float
    trend_p_value: float
    fatigue_indicator: float
    outlier_cycles: List[int] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'peak_to_peak_variation': self.peak_to_peak_variation.to_dict(),
            'cycle_to_cycle_variation': self.cycle_to_cycle_variation,
            'trend_slope': self.trend_slope,
            'trend_p_value': self.trend_p_value,
            'fatigue_indicator': self.fatigue_indicator,
            'outlier_cycles': self.outlier_cycles,
            'trend_interpretation': 'increasing' if self.trend_slope > 0.001 else 'decreasing' if self.trend_slope < -0.001 else 'stable'
        }


class ML002Analyzer:
    """
    Comprehensive data analyzer for ML-002 test results

    This class processes raw test data and performs:
    - Statistical analysis
    - Linearity assessment
    - Cyclic behavior evaluation
    - Quality control verification
    """

    def __init__(self, test_results, protocol: Dict[str, Any]):
        """
        Initialize analyzer

        Args:
            test_results: TestResults object from implementation
            protocol: Protocol dictionary
        """
        self.test_results = test_results
        self.protocol = protocol
        self.analysis_results: Dict[str, Any] = {}

    def perform_full_analysis(self) -> Dict[str, Any]:
        """
        Perform complete analysis of test data

        Returns:
            Dictionary containing all analysis results
        """
        logger.info("Starting comprehensive data analysis...")

        self.analysis_results = {
            'deflection_statistics': self.analyze_deflection_statistics(),
            'load_deflection_linearity': self.analyze_load_deflection_linearity(),
            'cyclic_behavior': self.analyze_cyclic_behavior(),
            'permanent_deformation': self.analyze_permanent_deformation(),
            'environmental_effects': self.analyze_environmental_effects(),
            'load_control_quality': self.analyze_load_control_quality(),
            'acceptance_criteria': self.evaluate_acceptance_criteria()
        }

        logger.info("Analysis complete")
        return self.analysis_results

    def analyze_deflection_statistics(self) -> Dict[str, Any]:
        """
        Analyze deflection data statistics

        Returns:
            Statistical summary of deflection measurements
        """
        logger.info("Analyzing deflection statistics...")

        # Extract deflection data from all cycles
        max_deflections = []
        min_deflections = []
        center_deflections = []

        for cycle in self.test_results.cycle_data:
            max_deflections.append(cycle.max_deflection_mm)
            min_deflections.append(cycle.min_deflection_mm)

            # Extract center deflection readings
            center_readings = [
                r.value for r in cycle.sensor_readings
                if 'center' in r.sensor_id and 'deflection' in r.sensor_id
            ]
            if center_readings:
                center_deflections.extend(center_readings)

        results = {
            'max_deflection_stats': self._calculate_statistics(max_deflections),
            'min_deflection_stats': self._calculate_statistics(min_deflections),
            'overall_deflection_range': {
                'absolute_max': max(max_deflections) if max_deflections else 0,
                'absolute_min': min(min_deflections) if min_deflections else 0
            }
        }

        if center_deflections:
            results['center_deflection_stats'] = self._calculate_statistics(center_deflections)

        return results

    def analyze_load_deflection_linearity(self) -> Dict[str, Any]:
        """
        Analyze load vs deflection linearity

        Returns:
            Regression analysis results
        """
        logger.info("Analyzing load-deflection linearity...")

        # Extract load and deflection pairs
        loads = []
        deflections = []

        for cycle in self.test_results.cycle_data:
            # Get readings at peak load
            peak_readings = [r for r in cycle.sensor_readings if r.value > 0]

            load_vals = [r.value for r in peak_readings if 'load' in r.sensor_id]
            defl_vals = [r.value for r in peak_readings if 'deflection' in r.sensor_id and 'center' in r.sensor_id]

            if load_vals and defl_vals:
                loads.append(load_vals[0])
                deflections.append(defl_vals[0])

        if not loads or not deflections:
            logger.warning("Insufficient data for linearity analysis")
            return {'error': 'Insufficient data'}

        # Perform linear regression
        regression = self._linear_regression(loads, deflections)

        return {
            'regression': regression.to_dict(),
            'data_points': len(loads),
            'load_range': {'min': min(loads), 'max': max(loads)},
            'deflection_range': {'min': min(deflections), 'max': max(deflections)}
        }

    def analyze_cyclic_behavior(self) -> Dict[str, Any]:
        """
        Analyze cyclic behavior and fatigue indicators

        Returns:
            Cyclic behavior analysis results
        """
        logger.info("Analyzing cyclic behavior...")

        # Extract peak-to-peak deflections per cycle
        peak_to_peak = [cycle.peak_to_peak_deflection_mm for cycle in self.test_results.cycle_data]
        max_deflections = [cycle.max_deflection_mm for cycle in self.test_results.cycle_data]

        if not peak_to_peak:
            return {'error': 'No cyclic data available'}

        # Calculate statistics
        ptp_stats = self._calculate_statistics(peak_to_peak)

        # Cycle-to-cycle variation
        if len(max_deflections) > 1:
            variations = [abs(max_deflections[i] - max_deflections[i-1])
                         for i in range(1, len(max_deflections))]
            cycle_variation = np.mean(variations) if variations else 0
        else:
            cycle_variation = 0

        # Trend analysis (is deflection increasing over time?)
        cycle_numbers = list(range(1, len(max_deflections) + 1))
        trend_regression = self._linear_regression(cycle_numbers, max_deflections)

        # Fatigue indicator (normalized trend)
        fatigue_indicator = trend_regression.slope / (np.mean(max_deflections) + 1e-10) * 100

        # Outlier detection
        outliers = self._detect_outliers(max_deflections)

        analysis = CyclicBehaviorAnalysis(
            peak_to_peak_variation=ptp_stats,
            cycle_to_cycle_variation=cycle_variation,
            trend_slope=trend_regression.slope,
            trend_p_value=trend_regression.p_value,
            fatigue_indicator=fatigue_indicator,
            outlier_cycles=[i+1 for i, is_outlier in enumerate(outliers) if is_outlier]
        )

        return analysis.to_dict()

    def analyze_permanent_deformation(self) -> Dict[str, Any]:
        """
        Analyze permanent deformation after load removal

        Returns:
            Permanent deformation analysis
        """
        logger.info("Analyzing permanent deformation...")

        # Get deflection at zero load after test
        if not self.test_results.cycle_data:
            return {'error': 'No cycle data available'}

        last_cycle = self.test_results.cycle_data[-1]
        permanent_deflection = last_cycle.min_deflection_mm

        # Compare to first cycle
        first_cycle = self.test_results.cycle_data[0]
        initial_zero_deflection = first_cycle.min_deflection_mm

        permanent_change = permanent_deflection - initial_zero_deflection

        return {
            'permanent_deflection_mm': permanent_deflection,
            'initial_zero_deflection_mm': initial_zero_deflection,
            'permanent_change_mm': permanent_change,
            'within_tolerance': abs(permanent_change) <= 0.5,
            'assessment': 'acceptable' if abs(permanent_change) <= 0.5 else 'excessive'
        }

    def analyze_environmental_effects(self) -> Dict[str, Any]:
        """
        Analyze environmental condition effects on deflection

        Returns:
            Environmental correlation analysis
        """
        logger.info("Analyzing environmental effects...")

        if not self.test_results.environmental_data:
            return {'error': 'No environmental data available'}

        # Extract environmental data
        temperatures = [e.temperature_celsius for e in self.test_results.environmental_data]
        humidities = [e.humidity_percent for e in self.test_results.environmental_data]

        # Calculate stability
        temp_stats = self._calculate_statistics(temperatures)
        humidity_stats = self._calculate_statistics(humidities)

        return {
            'temperature': {
                'stats': temp_stats.to_dict(),
                'stable': temp_stats.std_dev < 2.0,
                'within_spec': temp_stats.min >= 15 and temp_stats.max <= 35
            },
            'humidity': {
                'stats': humidity_stats.to_dict(),
                'stable': humidity_stats.std_dev < 5.0,
                'within_spec': humidity_stats.min >= 45 and humidity_stats.max <= 75
            },
            'overall_environmental_stability': (
                temp_stats.std_dev < 2.0 and
                humidity_stats.std_dev < 5.0 and
                temp_stats.min >= 15 and temp_stats.max <= 35 and
                humidity_stats.min >= 45 and humidity_stats.max <= 75
            )
        }

    def analyze_load_control_quality(self) -> Dict[str, Any]:
        """
        Analyze quality of load control

        Returns:
            Load control performance metrics
        """
        logger.info("Analyzing load control quality...")

        target_load = self.protocol['parameters']['load_configuration']['test_load_pa']['value']

        # Extract actual loads
        actual_loads = [cycle.max_load_pa for cycle in self.test_results.cycle_data]

        if not actual_loads:
            return {'error': 'No load data available'}

        # Calculate errors
        errors = [actual - target_load for actual in actual_loads]
        percent_errors = [(error / target_load) * 100 for error in errors]

        stats_errors = self._calculate_statistics(errors)
        stats_percent = self._calculate_statistics(percent_errors)

        return {
            'target_load_pa': target_load,
            'actual_load_stats': self._calculate_statistics(actual_loads).to_dict(),
            'absolute_error_stats': stats_errors.to_dict(),
            'percent_error_stats': stats_percent.to_dict(),
            'within_tolerance': abs(stats_percent.mean) <= 5.0 and stats_percent.std_dev <= 3.0,
            'control_quality': 'excellent' if abs(stats_percent.mean) <= 2.0 else 'good' if abs(stats_percent.mean) <= 5.0 else 'poor'
        }

    def evaluate_acceptance_criteria(self) -> Dict[str, Any]:
        """
        Evaluate all acceptance criteria from protocol

        Returns:
            Pass/fail status for each criterion
        """
        logger.info("Evaluating acceptance criteria...")

        criteria = self.protocol['quality_control']['acceptance_criteria']
        results = {}
        overall_pass = True

        for criterion in criteria:
            criteria_id = criterion['criteria_id']
            is_critical = criterion['is_critical']

            logger.debug(f"Evaluating criterion: {criteria_id}")

            # Evaluate based on criterion type
            if criteria_id == 'deflection_linearity':
                linearity = self.analysis_results.get('load_deflection_linearity', {})
                regression = linearity.get('regression', {})
                r_squared = regression.get('r_squared', 0)
                min_required = criterion.get('min_r_squared', 0.95)

                passed = r_squared >= min_required
                results[criteria_id] = {
                    'passed': passed,
                    'is_critical': is_critical,
                    'actual_value': r_squared,
                    'required_value': min_required,
                    'description': criterion['description']
                }

            elif criteria_id == 'max_deflection_limit':
                deflection_stats = self.analysis_results.get('deflection_statistics', {})
                max_defl = deflection_stats.get('overall_deflection_range', {}).get('absolute_max', 0)
                max_allowed = criterion.get('max_value_mm', 30)

                passed = max_defl <= max_allowed
                results[criteria_id] = {
                    'passed': passed,
                    'is_critical': is_critical,
                    'actual_value': max_defl,
                    'required_value': max_allowed,
                    'description': criterion['description']
                }

            elif criteria_id == 'deflection_consistency':
                cyclic = self.analysis_results.get('cyclic_behavior', {})
                ptp_var = cyclic.get('peak_to_peak_variation', {})
                cv = ptp_var.get('coefficient_of_variation', 0)
                max_var = criterion.get('max_variation_percent', 10)

                passed = cv <= max_var
                results[criteria_id] = {
                    'passed': passed,
                    'is_critical': is_critical,
                    'actual_value': cv,
                    'required_value': max_var,
                    'description': criterion['description']
                }

            elif criteria_id == 'load_accuracy':
                load_quality = self.analysis_results.get('load_control_quality', {})
                percent_error = load_quality.get('percent_error_stats', {})
                mean_error = abs(percent_error.get('mean', 0))
                tolerance = criterion.get('tolerance_percent', 5)

                passed = mean_error <= tolerance
                results[criteria_id] = {
                    'passed': passed,
                    'is_critical': is_critical,
                    'actual_value': mean_error,
                    'required_value': tolerance,
                    'description': criterion['description']
                }

            elif criteria_id == 'no_permanent_deformation':
                perm_deform = self.analysis_results.get('permanent_deformation', {})
                perm_change = abs(perm_deform.get('permanent_change_mm', 0))
                max_allowed = criterion.get('max_permanent_deflection_mm', 0.5)

                passed = perm_change <= max_allowed
                results[criteria_id] = {
                    'passed': passed,
                    'is_critical': is_critical,
                    'actual_value': perm_change,
                    'required_value': max_allowed,
                    'description': criterion['description']
                }

            elif criteria_id == 'environmental_stability':
                env_effects = self.analysis_results.get('environmental_effects', {})
                stable = env_effects.get('overall_environmental_stability', True)

                passed = stable
                results[criteria_id] = {
                    'passed': passed,
                    'is_critical': is_critical,
                    'description': criterion['description']
                }

            else:
                # Default to pass for undefined criteria
                results[criteria_id] = {
                    'passed': True,
                    'is_critical': is_critical,
                    'description': criterion['description'],
                    'note': 'Evaluation not implemented'
                }

            # Update overall pass status
            if is_critical and not results[criteria_id]['passed']:
                overall_pass = False

        results['overall_pass'] = overall_pass
        results['total_criteria'] = len(criteria)
        results['passed_criteria'] = sum(1 for r in results.values() if isinstance(r, dict) and r.get('passed', False))

        return results

    # Helper methods

    def _calculate_statistics(self, data: List[float]) -> StatisticalSummary:
        """Calculate comprehensive statistics for a dataset"""
        if not data:
            return StatisticalSummary(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        arr = np.array(data)
        mean = np.mean(arr)
        std_dev = np.std(arr, ddof=1) if len(arr) > 1 else 0

        return StatisticalSummary(
            mean=float(mean),
            std_dev=float(std_dev),
            min=float(np.min(arr)),
            max=float(np.max(arr)),
            range=float(np.max(arr) - np.min(arr)),
            median=float(np.median(arr)),
            q25=float(np.percentile(arr, 25)),
            q75=float(np.percentile(arr, 75)),
            iqr=float(np.percentile(arr, 75) - np.percentile(arr, 25)),
            coefficient_of_variation=float((std_dev / mean * 100) if mean != 0 else 0),
            count=len(arr)
        )

    def _linear_regression(self, x: List[float], y: List[float]) -> RegressionResults:
        """Perform linear regression analysis"""
        if len(x) < 2 or len(y) < 2:
            return RegressionResults(0, 0, 0, 1, 0)

        x_arr = np.array(x)
        y_arr = np.array(y)

        # Perform regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_arr, y_arr)

        # Calculate predictions and residuals
        predicted = slope * x_arr + intercept
        residuals = y_arr - predicted

        return RegressionResults(
            slope=float(slope),
            intercept=float(intercept),
            r_squared=float(r_value ** 2),
            p_value=float(p_value),
            std_error=float(std_err),
            predicted_values=predicted.tolist(),
            residuals=residuals.tolist()
        )

    def _detect_outliers(self, data: List[float], method: str = 'iqr', threshold: float = 3.0) -> List[bool]:
        """
        Detect outliers in dataset

        Args:
            data: Data array
            method: Detection method ('iqr' or 'zscore')
            threshold: Threshold for outlier detection

        Returns:
            Boolean array indicating outliers
        """
        if not data or len(data) < 3:
            return [False] * len(data)

        arr = np.array(data)

        if method == 'iqr':
            q25, q75 = np.percentile(arr, [25, 75])
            iqr = q75 - q25
            lower_bound = q25 - threshold * iqr
            upper_bound = q75 + threshold * iqr
            return [(x < lower_bound or x > upper_bound) for x in arr]

        elif method == 'zscore':
            mean = np.mean(arr)
            std = np.std(arr)
            z_scores = np.abs((arr - mean) / std) if std > 0 else np.zeros_like(arr)
            return [z > threshold for z in z_scores]

        return [False] * len(data)

    def generate_summary_report(self) -> str:
        """
        Generate text summary report

        Returns:
            Formatted text report
        """
        if not self.analysis_results:
            self.perform_full_analysis()

        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("ML-002 MECHANICAL LOAD DYNAMIC TEST - ANALYSIS REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"\nTest ID: {self.test_results.test_id}")
        report_lines.append(f"Sample: {self.test_results.sample.sample_id}")
        report_lines.append(f"Module Type: {self.test_results.sample.module_type}")
        report_lines.append(f"Test Date: {self.test_results.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Cycles Completed: {self.test_results.completed_cycles}/{self.test_results.total_cycles}")

        # Deflection statistics
        report_lines.append("\n" + "-" * 80)
        report_lines.append("DEFLECTION STATISTICS")
        report_lines.append("-" * 80)
        defl_stats = self.analysis_results.get('deflection_statistics', {})
        max_stats = defl_stats.get('max_deflection_stats', {})
        if max_stats:
            report_lines.append(f"Maximum Deflection: {max_stats.get('mean', 0):.3f} ± {max_stats.get('std_dev', 0):.3f} mm")
            report_lines.append(f"Range: {max_stats.get('min', 0):.3f} - {max_stats.get('max', 0):.3f} mm")
            report_lines.append(f"Coefficient of Variation: {max_stats.get('coefficient_of_variation', 0):.2f}%")

        # Linearity
        report_lines.append("\n" + "-" * 80)
        report_lines.append("LOAD-DEFLECTION LINEARITY")
        report_lines.append("-" * 80)
        linearity = self.analysis_results.get('load_deflection_linearity', {}).get('regression', {})
        if linearity:
            report_lines.append(f"R²: {linearity.get('r_squared', 0):.4f}")
            report_lines.append(f"Equation: {linearity.get('equation', 'N/A')}")
            report_lines.append(f"Quality: {linearity.get('quality', 'N/A')}")

        # Acceptance criteria
        report_lines.append("\n" + "-" * 80)
        report_lines.append("ACCEPTANCE CRITERIA EVALUATION")
        report_lines.append("-" * 80)
        criteria = self.analysis_results.get('acceptance_criteria', {})
        for key, value in criteria.items():
            if isinstance(value, dict) and 'passed' in value:
                status = "✓ PASS" if value['passed'] else "✗ FAIL"
                critical = " [CRITICAL]" if value.get('is_critical') else ""
                report_lines.append(f"{status}{critical} - {key}: {value.get('description', '')}")

        # Overall result
        report_lines.append("\n" + "=" * 80)
        overall_pass = criteria.get('overall_pass', False)
        result_text = "✓ PASSED" if overall_pass else "✗ FAILED"
        report_lines.append(f"OVERALL TEST RESULT: {result_text}")
        report_lines.append("=" * 80)

        return "\n".join(report_lines)


if __name__ == "__main__":
    # Example usage
    print("ML-002 Analyzer module")
    print("Import this module to analyze test results")
