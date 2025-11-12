"""
Metrics collection system for QA monitoring.
"""
from typing import Dict, Any, List
from datetime import datetime
from collections import defaultdict
import statistics


class MetricsCollector:
    """Collects and aggregates QA metrics."""

    def __init__(self):
        """Initialize metrics collector."""
        self.metrics = defaultdict(list)
        self.protocol_metrics = {}

    def collect_protocol_metrics(
        self, protocol_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Collect metrics from protocol execution.

        Args:
            protocol_data: Protocol data

        Returns:
            Metrics dictionary
        """
        metrics = {
            "protocol_id": protocol_data.get("protocol_id"),
            "timestamp": datetime.now().isoformat(),
            "protocol_type": protocol_data.get("protocol_type"),
            "measurement_count": len(protocol_data.get("measurements", [])),
            "parameter_count": len(protocol_data.get("parameters", {})),
        }

        # Calculate measurement statistics
        measurements = protocol_data.get("measurements", [])
        if measurements:
            metrics["measurement_stats"] = self._calculate_measurement_stats(
                measurements
            )

        # Store metrics
        protocol_id = protocol_data.get("protocol_id")
        if protocol_id:
            self.protocol_metrics[protocol_id] = metrics

        return metrics

    def _calculate_measurement_stats(
        self, measurements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate statistics from measurements.

        Args:
            measurements: List of measurement dictionaries

        Returns:
            Statistics dictionary
        """
        stats = {
            "total_count": len(measurements),
            "by_parameter": defaultdict(list),
            "by_status": defaultdict(int),
        }

        for measurement in measurements:
            if not isinstance(measurement, dict):
                continue

            # Count by parameter
            parameter = measurement.get("parameter")
            value = measurement.get("value")
            if parameter and isinstance(value, (int, float)):
                stats["by_parameter"][parameter].append(value)

            # Count by status
            status = measurement.get("status")
            if status:
                stats["by_status"][status] += 1

        # Calculate statistics for each parameter
        param_stats = {}
        for parameter, values in stats["by_parameter"].items():
            if values:
                param_stats[parameter] = {
                    "count": len(values),
                    "mean": statistics.mean(values),
                    "min": min(values),
                    "max": max(values),
                    "stdev": statistics.stdev(values) if len(values) > 1 else 0,
                }

        stats["parameter_statistics"] = param_stats

        return stats

    def record_test_result(
        self, test_name: str, passed: bool, execution_time: float
    ):
        """
        Record a test result.

        Args:
            test_name: Name of the test
            passed: Whether test passed
            execution_time: Execution time in seconds
        """
        self.metrics["test_results"].append({
            "test_name": test_name,
            "passed": passed,
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat(),
        })

    def record_validation_result(
        self, validator_name: str, is_valid: bool, error_count: int
    ):
        """
        Record a validation result.

        Args:
            validator_name: Name of validator
            is_valid: Whether validation passed
            error_count: Number of errors
        """
        self.metrics["validation_results"].append({
            "validator": validator_name,
            "is_valid": is_valid,
            "error_count": error_count,
            "timestamp": datetime.now().isoformat(),
        })

    def get_test_pass_rate(self) -> float:
        """
        Calculate test pass rate.

        Returns:
            Pass rate as percentage
        """
        results = self.metrics.get("test_results", [])
        if not results:
            return 0.0

        passed = sum(1 for r in results if r["passed"])
        return (passed / len(results)) * 100

    def get_validation_pass_rate(self) -> float:
        """
        Calculate validation pass rate.

        Returns:
            Pass rate as percentage
        """
        results = self.metrics.get("validation_results", [])
        if not results:
            return 0.0

        passed = sum(1 for r in results if r["is_valid"])
        return (passed / len(results)) * 100

    def get_average_execution_time(self) -> float:
        """
        Get average test execution time.

        Returns:
            Average execution time in seconds
        """
        results = self.metrics.get("test_results", [])
        if not results:
            return 0.0

        times = [r["execution_time"] for r in results]
        return statistics.mean(times)

    def get_protocol_metrics(self, protocol_id: str) -> Dict[str, Any]:
        """
        Get metrics for specific protocol.

        Args:
            protocol_id: Protocol identifier

        Returns:
            Metrics dictionary or empty dict
        """
        return self.protocol_metrics.get(protocol_id, {})

    def get_summary(self) -> Dict[str, Any]:
        """
        Get overall metrics summary.

        Returns:
            Summary dictionary
        """
        return {
            "test_count": len(self.metrics.get("test_results", [])),
            "test_pass_rate": self.get_test_pass_rate(),
            "validation_count": len(self.metrics.get("validation_results", [])),
            "validation_pass_rate": self.get_validation_pass_rate(),
            "avg_execution_time": self.get_average_execution_time(),
            "protocol_count": len(self.protocol_metrics),
        }

    def clear_metrics(self):
        """Clear all collected metrics."""
        self.metrics.clear()
        self.protocol_metrics.clear()
