"""Data validation utilities for test protocols."""

from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np
from datetime import datetime


class DataValidator:
    """Validates test data against protocol specifications."""

    @staticmethod
    def validate_dataframe(
        data: pd.DataFrame, required_columns: List[str], optional_columns: List[str] = None
    ) -> Tuple[bool, List[str]]:
        """
        Validate that DataFrame has required columns.

        Args:
            data: DataFrame to validate
            required_columns: List of required column names
            optional_columns: List of optional column names

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        # Check required columns
        missing_columns = set(required_columns) - set(data.columns)
        if missing_columns:
            errors.append(f"Missing required columns: {missing_columns}")

        # Check for empty DataFrame
        if data.empty:
            errors.append("DataFrame is empty")

        return len(errors) == 0, errors

    @staticmethod
    def validate_numeric_range(
        data: pd.Series, min_val: float = None, max_val: float = None, param_name: str = None
    ) -> Tuple[bool, List[str]]:
        """
        Validate that numeric data is within specified range.

        Args:
            data: Pandas Series with numeric data
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            param_name: Parameter name for error messages

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        name = param_name or "Parameter"

        # Check if data is numeric
        if not pd.api.types.is_numeric_dtype(data):
            errors.append(f"{name} must be numeric")
            return False, errors

        # Check for NaN values
        if data.isna().any():
            nan_count = data.isna().sum()
            errors.append(f"{name} has {nan_count} NaN values")

        # Validate range
        if min_val is not None:
            below_min = data < min_val
            if below_min.any():
                count = below_min.sum()
                errors.append(f"{name} has {count} values below minimum ({min_val})")

        if max_val is not None:
            above_max = data > max_val
            if above_max.any():
                count = above_max.sum()
                errors.append(f"{name} has {count} values above maximum ({max_val})")

        return len(errors) == 0, errors

    @staticmethod
    def validate_stability(
        data: pd.Series,
        threshold_percent: float = 2.0,
        param_name: str = None,
        window_size: int = None,
    ) -> Tuple[bool, str]:
        """
        Validate that data is stable (low variation).

        Args:
            data: Pandas Series with measurement data
            threshold_percent: Maximum allowed coefficient of variation (%)
            param_name: Parameter name for messages
            window_size: Window size for rolling stability check

        Returns:
            Tuple of (is_stable, message)
        """
        name = param_name or "Parameter"

        if window_size:
            # Rolling stability check
            rolling_cv = (data.rolling(window=window_size).std() /
                         data.rolling(window=window_size).mean() * 100)
            max_cv = rolling_cv.max()
            is_stable = max_cv < threshold_percent
            message = f"{name} max rolling CV: {max_cv:.2f}% (threshold: {threshold_percent}%)"
        else:
            # Overall stability check
            mean_val = data.mean()
            std_val = data.std()
            cv = (std_val / mean_val * 100) if mean_val != 0 else np.inf
            is_stable = cv < threshold_percent
            message = f"{name} CV: {cv:.2f}% (threshold: {threshold_percent}%)"

        return is_stable, message

    @staticmethod
    def validate_monotonic(
        data: pd.Series, increasing: bool = True, strict: bool = False, param_name: str = None
    ) -> Tuple[bool, str]:
        """
        Validate that data is monotonic.

        Args:
            data: Pandas Series to check
            increasing: True for monotonic increasing, False for decreasing
            strict: If True, check for strictly monotonic
            param_name: Parameter name for messages

        Returns:
            Tuple of (is_monotonic, message)
        """
        name = param_name or "Parameter"

        if increasing:
            if strict:
                is_monotonic = (data.diff().dropna() > 0).all()
                direction = "strictly increasing"
            else:
                is_monotonic = (data.diff().dropna() >= 0).all()
                direction = "increasing"
        else:
            if strict:
                is_monotonic = (data.diff().dropna() < 0).all()
                direction = "strictly decreasing"
            else:
                is_monotonic = (data.diff().dropna() <= 0).all()
                direction = "decreasing"

        message = (
            f"{name} is {direction}"
            if is_monotonic
            else f"{name} is not {direction}"
        )

        return is_monotonic, message

    @staticmethod
    def validate_completeness(data: pd.DataFrame, required_test_points: List[Dict]) -> Tuple[bool, List[str]]:
        """
        Validate that all required test points are present.

        Args:
            data: Test data DataFrame
            required_test_points: List of dictionaries specifying required test conditions

        Returns:
            Tuple of (is_complete, list of missing test points)
        """
        missing_points = []

        for point in required_test_points:
            # Build query to check if test point exists
            query_parts = []
            for key, value in point.items():
                if isinstance(value, (int, float)):
                    # Allow small tolerance for floating point comparison
                    tolerance = abs(value * 0.01) if value != 0 else 0.1
                    query_parts.append(
                        f"({key} >= {value - tolerance}) and ({key} <= {value + tolerance})"
                    )
                else:
                    query_parts.append(f"{key} == '{value}'")

            query = " and ".join(query_parts)

            try:
                matching_rows = data.query(query)
                if len(matching_rows) == 0:
                    missing_points.append(str(point))
            except Exception as e:
                missing_points.append(f"{point} (query failed: {e})")

        return len(missing_points) == 0, missing_points

    @staticmethod
    def validate_data_quality(
        data: pd.DataFrame, max_missing_percent: float = 5.0
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Perform overall data quality assessment.

        Args:
            data: DataFrame to assess
            max_missing_percent: Maximum allowed percentage of missing values

        Returns:
            Tuple of (passes_quality_check, quality_metrics)
        """
        total_cells = data.size
        missing_cells = data.isna().sum().sum()
        missing_percent = (missing_cells / total_cells * 100) if total_cells > 0 else 0

        duplicates = data.duplicated().sum()
        duplicate_percent = (duplicates / len(data) * 100) if len(data) > 0 else 0

        quality_metrics = {
            "total_rows": len(data),
            "total_columns": len(data.columns),
            "missing_cells": int(missing_cells),
            "missing_percent": float(missing_percent),
            "duplicate_rows": int(duplicates),
            "duplicate_percent": float(duplicate_percent),
            "data_types": data.dtypes.astype(str).to_dict(),
        }

        # Add column-wise statistics
        column_stats = {}
        for col in data.columns:
            if pd.api.types.is_numeric_dtype(data[col]):
                column_stats[col] = {
                    "mean": float(data[col].mean()) if not data[col].isna().all() else None,
                    "std": float(data[col].std()) if not data[col].isna().all() else None,
                    "min": float(data[col].min()) if not data[col].isna().all() else None,
                    "max": float(data[col].max()) if not data[col].isna().all() else None,
                    "missing": int(data[col].isna().sum()),
                }

        quality_metrics["column_statistics"] = column_stats

        passes = missing_percent <= max_missing_percent

        return passes, quality_metrics

    @staticmethod
    def calculate_measurement_uncertainty(
        measurements: pd.Series,
        instrument_uncertainty: float,
        method: str = "type_a",
    ) -> Dict[str, float]:
        """
        Calculate measurement uncertainty.

        Args:
            measurements: Series of repeated measurements
            instrument_uncertainty: Instrument uncertainty specification
            method: Uncertainty calculation method ('type_a' or 'combined')

        Returns:
            Dictionary with uncertainty components
        """
        # Type A uncertainty (statistical)
        n = len(measurements)
        mean = measurements.mean()
        std = measurements.std()
        type_a = std / np.sqrt(n) if n > 1 else std

        # Type B uncertainty (instrument)
        type_b = instrument_uncertainty / np.sqrt(3)  # Assuming rectangular distribution

        # Combined uncertainty
        combined = np.sqrt(type_a**2 + type_b**2)

        # Expanded uncertainty (k=2 for ~95% confidence)
        expanded = 2 * combined

        return {
            "mean": float(mean),
            "std_dev": float(std),
            "type_a_uncertainty": float(type_a),
            "type_b_uncertainty": float(type_b),
            "combined_uncertainty": float(combined),
            "expanded_uncertainty": float(expanded),
            "relative_uncertainty_percent": float((expanded / mean * 100) if mean != 0 else np.inf),
            "n_measurements": int(n),
        }
