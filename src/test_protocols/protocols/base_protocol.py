"""Base protocol class for all test protocol implementations."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

from ..core.protocol_loader import ProtocolLoader


class BaseProtocol(ABC):
    """Abstract base class for all test protocols."""

    PROTOCOL_ID: str = None
    VERSION: str = None

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the protocol.

        Args:
            config_path: Path to protocol JSON configuration file
        """
        self.loader = ProtocolLoader()

        if config_path:
            # Load from specific file
            with open(config_path, "r") as f:
                import json
                self.config = json.load(f)
        else:
            # Load from standard location using protocol ID
            if not self.PROTOCOL_ID:
                raise ValueError("PROTOCOL_ID must be defined in subclass")
            self.config = self.loader.load_protocol(self.PROTOCOL_ID)

        self.metadata = self.config.get("metadata", {})
        self.test_conditions = self.config.get("test_conditions", {})
        self.parameters = self.config.get("parameters", [])
        self.outputs = self.config.get("outputs", [])
        self.quality_checks = self.config.get("quality_checks", [])
        self.charts_config = self.config.get("charts", [])

        # Initialize results storage
        self.results: Optional[Dict[str, Any]] = None
        self.test_data: Optional[pd.DataFrame] = None

    @abstractmethod
    def validate_inputs(self, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate input data against protocol requirements.

        Args:
            data: Input data dictionary or DataFrame

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        pass

    @abstractmethod
    def run_test(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Execute the test protocol.

        Args:
            data: Test measurement data

        Returns:
            Dictionary containing test results
        """
        pass

    def _validate_parameters(self, data: pd.DataFrame) -> tuple[bool, List[str]]:
        """
        Validate data parameters against protocol specification.

        Args:
            data: DataFrame containing measurement data

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        for param in self.parameters:
            param_id = param["id"]
            is_required = param.get("required", False)

            # Check if required parameter exists
            if is_required and param_id not in data.columns:
                errors.append(f"Required parameter '{param_id}' is missing")
                continue

            # Skip validation if parameter doesn't exist and is optional
            if param_id not in data.columns:
                continue

            # Validate data type
            param_type = param["type"]
            if param_type in ["float", "int"]:
                if not pd.api.types.is_numeric_dtype(data[param_id]):
                    errors.append(f"Parameter '{param_id}' must be numeric")
                    continue

            # Validate range if specified
            validation = param.get("validation", {})
            if "min" in validation or "max" in validation:
                min_val = validation.get("min", -np.inf)
                max_val = validation.get("max", np.inf)

                if param_type in ["float", "int"]:
                    out_of_range = (data[param_id] < min_val) | (data[param_id] > max_val)
                    if out_of_range.any():
                        errors.append(
                            f"Parameter '{param_id}' has {out_of_range.sum()} values "
                            f"out of range [{min_val}, {max_val}]"
                        )

        return len(errors) == 0, errors

    def _run_quality_checks(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Execute quality checks on test data.

        Args:
            data: Test measurement data

        Returns:
            List of quality check results
        """
        qc_results = []

        for qc in self.quality_checks:
            result = {
                "id": qc["id"],
                "name": qc["name"],
                "type": qc["type"],
                "severity": qc.get("severity", "warning"),
                "passed": True,
                "message": "",
            }

            param = qc.get("parameter")

            try:
                if qc["type"] == "threshold":
                    # Check if parameter variation is within threshold
                    if param and param in data.columns:
                        std_dev = data[param].std()
                        mean_val = data[param].mean()
                        relative_std = (std_dev / mean_val * 100) if mean_val != 0 else 0

                        # Parse condition (e.g., "std_dev < 2%")
                        condition = qc.get("condition", "")
                        if "%" in condition:
                            threshold = float(condition.split("<")[1].replace("%", "").strip())
                            result["passed"] = relative_std < threshold
                            result["message"] = (
                                f"Relative std dev: {relative_std:.2f}% "
                                f"(threshold: {threshold}%)"
                            )

                elif qc["type"] == "range":
                    # Check if all values are within range
                    if param and param in data.columns:
                        min_val = qc.get("min", -np.inf)
                        max_val = qc.get("max", np.inf)
                        out_of_range = (data[param] < min_val) | (data[param] > max_val)
                        result["passed"] = not out_of_range.any()
                        result["message"] = (
                            f"All values in range [{min_val}, {max_val}]"
                            if result["passed"]
                            else f"{out_of_range.sum()} values out of range"
                        )

                elif qc["type"] == "completeness":
                    # Check data completeness
                    missing = data.isnull().sum().sum()
                    result["passed"] = missing == 0
                    result["message"] = (
                        "No missing values"
                        if result["passed"]
                        else f"{missing} missing values found"
                    )

            except Exception as e:
                result["passed"] = False
                result["message"] = f"QC check failed: {str(e)}"

            qc_results.append(result)

        return qc_results

    def _process_measurements(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Process raw measurements.

        Args:
            data: Raw measurement data

        Returns:
            Processed measurement data
        """
        # Create a copy to avoid modifying original
        processed = data.copy()

        # Add timestamp if not present
        if "timestamp" not in processed.columns:
            processed["timestamp"] = datetime.now().isoformat()

        return processed

    def generate_report(
        self, results: Dict[str, Any], output_path: str, format: str = "pdf"
    ) -> str:
        """
        Generate test report.

        Args:
            results: Test results dictionary
            output_path: Path for output report file
            format: Report format ('pdf', 'html', 'json')

        Returns:
            Path to generated report
        """
        # This will be implemented by specific protocols or report generator
        raise NotImplementedError("Report generation not yet implemented")

    def get_protocol_info(self) -> Dict[str, Any]:
        """
        Get protocol information.

        Returns:
            Dictionary with protocol metadata
        """
        return {
            "protocol_id": self.config["protocol_id"],
            "version": self.config["version"],
            "name": self.config["name"],
            "category": self.config["category"],
            "description": self.config["description"],
            "standards": self.metadata.get("standards", []),
        }

    def export_results(self, output_path: str, format: str = "json") -> None:
        """
        Export test results to file.

        Args:
            output_path: Output file path
            format: Export format ('json', 'csv', 'excel')
        """
        if self.results is None:
            raise ValueError("No results to export. Run test first.")

        output_file = Path(output_path)

        if format == "json":
            import json
            with open(output_file, "w") as f:
                json.dump(self.results, f, indent=2, default=str)

        elif format == "csv" and self.test_data is not None:
            self.test_data.to_csv(output_file, index=False)

        elif format == "excel" and self.test_data is not None:
            with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
                self.test_data.to_excel(writer, sheet_name="Measurements", index=False)
                if "analysis" in self.results:
                    analysis_df = pd.DataFrame([self.results["analysis"]])
                    analysis_df.to_excel(writer, sheet_name="Analysis", index=False)

        else:
            raise ValueError(f"Unsupported export format: {format}")
