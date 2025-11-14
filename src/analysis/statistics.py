"""
Statistics Module
=================

Statistical analysis functions for test protocols.
"""

from typing import List, Dict, Any
import statistics
import math


class StatisticsCalculator:
    """Statistical calculations for test data analysis"""

    @staticmethod
    def calculate_basic_stats(values: List[float]) -> Dict[str, float]:
        """Calculate basic statistics"""
        if not values:
                return {'mean': 0, 'median': 0, 'std_dev': 0, 'min': 0, 'max': 0}

        return {
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'std_dev': statistics.stdev(values) if len(values) > 1 else 0,
            'min': min(values),
            'max': max(values),
            'count': len(values)
        }

    @staticmethod
    def calculate_control_limits(
        values: List[float],
        sigma_level: float = 3.0
    ) -> Dict[str, float]:
        """Calculate statistical process control limits"""
        if len(values) < 2:
            return {'mean': 0, 'ucl': 0, 'lcl': 0}

        mean = statistics.mean(values)
        std_dev = statistics.stdev(values)

        ucl = mean + (sigma_level * std_dev)
        lcl = mean - (sigma_level * std_dev)

        return {
            'mean': mean,
            'ucl': ucl,
            'lcl': lcl,
            'std_dev': std_dev
        }
