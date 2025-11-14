"""Statistical analysis module for test data."""

import logging
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)


class StatisticalAnalyzer:
    """Perform statistical analysis on test measurements."""

    def __init__(self, protocol: Dict[str, Any] = None):
        """
        Initialize StatisticalAnalyzer.

        Args:
            protocol: Optional protocol definition
        """
        self.protocol = protocol
        logger.info("StatisticalAnalyzer initialized")

    def calculate_basic_stats(self, values: List[float]) -> Dict[str, float]:
        """
        Calculate basic statistical metrics.

        Args:
            values: List of numeric values

        Returns:
            Dictionary of statistics
        """
        if not values:
            return {}

        values_array = np.array(values)

        stats_dict = {
            "count": len(values),
            "mean": np.mean(values_array),
            "median": np.median(values_array),
            "std": np.std(values_array, ddof=1) if len(values) > 1 else 0,
            "min": np.min(values_array),
            "max": np.max(values_array),
            "range": np.ptp(values_array),
            "q1": np.percentile(values_array, 25),
            "q3": np.percentile(values_array, 75),
        }

        stats_dict["iqr"] = stats_dict["q3"] - stats_dict["q1"]
        stats_dict["cv"] = (
            (stats_dict["std"] / stats_dict["mean"] * 100) if stats_dict["mean"] != 0 else 0
        )

        logger.debug(f"Calculated stats for {len(values)} values")
        return stats_dict

    def calculate_confidence_interval(
        self, values: List[float], confidence: float = 0.95
    ) -> tuple[float, float]:
        """
        Calculate confidence interval for mean.

        Args:
            values: List of numeric values
            confidence: Confidence level (default 0.95)

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        if not values or len(values) < 2:
            return (0, 0)

        values_array = np.array(values)
        mean = np.mean(values_array)
        std_err = stats.sem(values_array)

        margin = std_err * stats.t.ppf((1 + confidence) / 2, len(values) - 1)

        return (mean - margin, mean + margin)

    def detect_outliers(
        self, values: List[float], method: str = "iqr", threshold: float = 1.5
    ) -> Dict[str, Any]:
        """
        Detect outliers in data.

        Args:
            values: List of numeric values
            method: Detection method ('iqr' or 'zscore')
            threshold: Threshold for outlier detection

        Returns:
            Dictionary with outlier information
        """
        if not values or len(values) < 4:
            return {"outliers": [], "outlier_indices": [], "method": method}

        values_array = np.array(values)
        outlier_indices = []
        outliers = []

        if method == "iqr":
            q1 = np.percentile(values_array, 25)
            q3 = np.percentile(values_array, 75)
            iqr = q3 - q1

            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr

            for i, v in enumerate(values_array):
                if v < lower_bound or v > upper_bound:
                    outlier_indices.append(i)
                    outliers.append(v)

        elif method == "zscore":
            mean = np.mean(values_array)
            std = np.std(values_array)

            if std > 0:
                z_scores = np.abs((values_array - mean) / std)
                for i, (v, z) in enumerate(zip(values_array, z_scores)):
                    if z > threshold:
                        outlier_indices.append(i)
                        outliers.append(v)

        result = {
            "method": method,
            "threshold": threshold,
            "outlier_count": len(outliers),
            "outlier_indices": outlier_indices,
            "outliers": outliers,
            "outlier_percentage": (len(outliers) / len(values)) * 100,
        }

        logger.info(
            f"Detected {len(outliers)} outliers using {method} method "
            f"({result['outlier_percentage']:.1f}%)"
        )

        return result

    def calculate_degradation(
        self, initial_values: List[float], final_values: List[float]
    ) -> Dict[str, Any]:
        """
        Calculate degradation between initial and final measurements.

        Args:
            initial_values: Initial measurement values
            final_values: Final measurement values

        Returns:
            Dictionary with degradation metrics
        """
        if not initial_values or not final_values:
            return {}

        initial_mean = np.mean(initial_values)
        final_mean = np.mean(final_values)

        absolute_change = final_mean - initial_mean
        percent_change = (
            (absolute_change / initial_mean * 100) if initial_mean != 0 else 0
        )

        # Per-element degradation if same length
        element_degradation = []
        if len(initial_values) == len(final_values):
            for init, final in zip(initial_values, final_values):
                if init != 0:
                    deg = ((final - init) / init) * 100
                    element_degradation.append(deg)

        result = {
            "initial_mean": initial_mean,
            "final_mean": final_mean,
            "absolute_change": absolute_change,
            "percent_change": percent_change,
            "element_degradation": element_degradation,
            "max_degradation": max(element_degradation) if element_degradation else None,
            "min_degradation": min(element_degradation) if element_degradation else None,
        }

        logger.info(f"Calculated degradation: {percent_change:.2f}%")
        return result

    def analyze_dataframe(
        self, df: pd.DataFrame, measurement_id: str = None
    ) -> Dict[str, Any]:
        """
        Analyze measurements in a DataFrame.

        Args:
            df: DataFrame with measurements
            measurement_id: Optional filter by measurement ID

        Returns:
            Analysis results dictionary
        """
        if df.empty:
            return {}

        if measurement_id:
            df = df[df["measurement_id"] == measurement_id]

        values = df["value"].dropna().tolist()

        if not values:
            return {}

        analysis = {
            "basic_stats": self.calculate_basic_stats(values),
            "confidence_interval_95": self.calculate_confidence_interval(values, 0.95),
            "outliers": self.detect_outliers(values),
        }

        logger.info(f"Analyzed {len(values)} measurements")
        return analysis

    def perform_normality_test(self, values: List[float]) -> Dict[str, Any]:
        """
        Perform Shapiro-Wilk normality test.

        Args:
            values: List of numeric values

        Returns:
            Test results dictionary
        """
        if not values or len(values) < 3:
            return {"error": "Insufficient data for normality test"}

        stat, p_value = stats.shapiro(values)

        result = {
            "test": "Shapiro-Wilk",
            "statistic": stat,
            "p_value": p_value,
            "is_normal": p_value > 0.05,
            "alpha": 0.05,
        }

        logger.info(
            f"Normality test: p={p_value:.4f}, "
            f"normal={result['is_normal']}"
        )

        return result

    def compare_distributions(
        self, group1: List[float], group2: List[float]
    ) -> Dict[str, Any]:
        """
        Compare two distributions using t-test.

        Args:
            group1: First group of values
            group2: Second group of values

        Returns:
            Comparison results dictionary
        """
        if not group1 or not group2:
            return {"error": "Insufficient data for comparison"}

        # Perform independent t-test
        t_stat, p_value = stats.ttest_ind(group1, group2)

        result = {
            "test": "Independent t-test",
            "t_statistic": t_stat,
            "p_value": p_value,
            "significant_difference": p_value < 0.05,
            "alpha": 0.05,
            "group1_mean": np.mean(group1),
            "group2_mean": np.mean(group2),
            "group1_std": np.std(group1, ddof=1),
            "group2_std": np.std(group2, ddof=1),
        }

        logger.info(
            f"Distribution comparison: p={p_value:.4f}, "
            f"significant={result['significant_difference']}"
        )

        return result
