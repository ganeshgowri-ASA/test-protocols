"""
Calculation utilities for test data analysis
"""

from typing import List, Dict, Any, Optional
import statistics
from dataclasses import dataclass


@dataclass
class StatisticalResult:
    """Container for statistical analysis results"""
    mean: float
    median: float
    std: float
    variance: float
    min: float
    max: float
    count: int


class PowerDegradationCalculator:
    """Calculator for power degradation analysis"""

    @staticmethod
    def calculate_degradation(initial_power: float, final_power: float) -> float:
        """
        Calculate power degradation percentage

        Args:
            initial_power: Initial Pmax (W)
            final_power: Final Pmax (W)

        Returns:
            Degradation percentage (positive value indicates loss)
        """
        if initial_power <= 0:
            raise ValueError("Initial power must be greater than 0")

        degradation = ((initial_power - final_power) / initial_power) * 100
        return round(degradation, 2)

    @staticmethod
    def calculate_degradation_watts(initial_power: float, final_power: float) -> float:
        """
        Calculate absolute power degradation in watts

        Args:
            initial_power: Initial Pmax (W)
            final_power: Final Pmax (W)

        Returns:
            Degradation in watts
        """
        return round(initial_power - final_power, 2)

    @staticmethod
    def is_within_tolerance(degradation_percent: float, tolerance: float = 5.0) -> bool:
        """
        Check if degradation is within acceptable tolerance

        Args:
            degradation_percent: Degradation percentage
            tolerance: Maximum acceptable degradation (default 5%)

        Returns:
            True if within tolerance
        """
        return degradation_percent <= tolerance


class StatisticalAnalyzer:
    """Statistical analysis utilities"""

    def calculate_statistics(self, data: List[float]) -> Dict[str, float]:
        """
        Calculate comprehensive statistics for a dataset

        Args:
            data: List of numerical values

        Returns:
            Dictionary with statistical measures
        """
        if not data:
            return {
                'mean': 0,
                'median': 0,
                'std': 0,
                'variance': 0,
                'min': 0,
                'max': 0,
                'count': 0
            }

        return {
            'mean': round(statistics.mean(data), 2),
            'median': round(statistics.median(data), 2),
            'std': round(statistics.stdev(data), 2) if len(data) > 1 else 0,
            'variance': round(statistics.variance(data), 2) if len(data) > 1 else 0,
            'min': round(min(data), 2),
            'max': round(max(data), 2),
            'count': len(data)
        }

    def check_outliers(self, data: List[float], threshold: float = 2.0) -> List[int]:
        """
        Identify outliers using standard deviation method

        Args:
            data: List of numerical values
            threshold: Number of standard deviations for outlier detection

        Returns:
            List of indices of outlier values
        """
        if len(data) < 3:
            return []

        mean = statistics.mean(data)
        std = statistics.stdev(data)

        outliers = []
        for i, value in enumerate(data):
            z_score = abs((value - mean) / std) if std > 0 else 0
            if z_score > threshold:
                outliers.append(i)

        return outliers

    def calculate_compliance_rate(self, compliant_count: int, total_count: int) -> float:
        """
        Calculate compliance rate as percentage

        Args:
            compliant_count: Number of compliant items
            total_count: Total number of items

        Returns:
            Compliance rate percentage
        """
        if total_count == 0:
            return 0.0

        return round((compliant_count / total_count) * 100, 2)


class VelocityAnalyzer:
    """Analyzer for impact velocity data"""

    def __init__(self, target_velocity: float = 80.0, tolerance: float = 2.0):
        """
        Initialize velocity analyzer

        Args:
            target_velocity: Target impact velocity (km/h)
            tolerance: Acceptable velocity deviation (km/h)
        """
        self.target_velocity = target_velocity
        self.tolerance = tolerance

    def check_velocity_compliance(self, actual_velocity: float) -> bool:
        """
        Check if velocity is within tolerance

        Args:
            actual_velocity: Measured velocity (km/h)

        Returns:
            True if within tolerance
        """
        deviation = abs(actual_velocity - self.target_velocity)
        return deviation <= self.tolerance

    def calculate_velocity_deviation(self, actual_velocity: float) -> float:
        """
        Calculate velocity deviation from target

        Args:
            actual_velocity: Measured velocity (km/h)

        Returns:
            Deviation in km/h (positive or negative)
        """
        return round(actual_velocity - self.target_velocity, 2)

    def analyze_velocity_dataset(self, velocities: List[float]) -> Dict[str, Any]:
        """
        Comprehensive analysis of velocity dataset

        Args:
            velocities: List of measured velocities

        Returns:
            Dictionary with velocity analysis
        """
        stat_analyzer = StatisticalAnalyzer()
        stats = stat_analyzer.calculate_statistics(velocities)

        compliant_count = sum(1 for v in velocities if self.check_velocity_compliance(v))
        compliance_rate = stat_analyzer.calculate_compliance_rate(compliant_count, len(velocities))

        deviations = [self.calculate_velocity_deviation(v) for v in velocities]

        return {
            'target_velocity': self.target_velocity,
            'tolerance': self.tolerance,
            'statistics': stats,
            'compliant_count': compliant_count,
            'total_count': len(velocities),
            'compliance_rate': compliance_rate,
            'mean_deviation': round(statistics.mean(deviations), 2) if deviations else 0,
            'max_deviation': round(max(deviations, key=abs), 2) if deviations else 0
        }


class InsulationResistanceAnalyzer:
    """Analyzer for insulation resistance measurements"""

    def __init__(self, minimum_resistance: float = 400.0):
        """
        Initialize insulation resistance analyzer

        Args:
            minimum_resistance: Minimum acceptable resistance (MΩ)
        """
        self.minimum_resistance = minimum_resistance

    def check_compliance(self, resistance: float) -> bool:
        """
        Check if resistance meets minimum requirement

        Args:
            resistance: Measured resistance (MΩ)

        Returns:
            True if meets minimum
        """
        return resistance >= self.minimum_resistance

    def calculate_degradation(self, initial: float, final: float) -> Dict[str, Any]:
        """
        Calculate insulation resistance degradation

        Args:
            initial: Initial resistance (MΩ)
            final: Final resistance (MΩ)

        Returns:
            Dictionary with degradation analysis
        """
        if initial <= 0:
            raise ValueError("Initial resistance must be greater than 0")

        absolute_change = final - initial
        percent_change = (absolute_change / initial) * 100

        return {
            'initial_resistance': round(initial, 2),
            'final_resistance': round(final, 2),
            'absolute_change': round(absolute_change, 2),
            'percent_change': round(percent_change, 2),
            'degradation_detected': percent_change < -10,  # More than 10% drop
            'meets_minimum': final >= self.minimum_resistance
        }
