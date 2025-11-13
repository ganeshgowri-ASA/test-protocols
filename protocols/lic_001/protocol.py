"""
LIC-001 Protocol Implementation
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import json

from core.base_protocol import BaseProtocol, ProtocolMetadata, TestConditions
from core.utils import generate_run_id, calculate_hash
from .analysis import LIC001Analyzer
from .validation import LIC001Validator


class LIC001Protocol(BaseProtocol):
    """
    Low Irradiance Conditions Test Protocol (LIC-001)

    Tests PV module performance at multiple low irradiance levels:
    - 200 W/m²
    - 400 W/m²
    - 600 W/m²
    - 800 W/m²

    All tests conducted at 25°C ± 2°C with AM1.5G spectrum.

    Measurements:
    - I-V curves at each irradiance level
    - Pmax, Vmp, Imp at each level
    - Fill Factor at each level
    - Efficiency at each level
    """

    PROTOCOL_ID = "LIC-001"
    VERSION = "1.0.0"
    STANDARD = "IEC 61215-1:2021"
    CATEGORY = "PERFORMANCE"

    # Test parameters
    REQUIRED_IRRADIANCE_LEVELS = [200, 400, 600, 800]  # W/m²
    TARGET_TEMPERATURE = 25.0  # °C
    TEMPERATURE_TOLERANCE = 2.0  # °C
    IRRADIANCE_TOLERANCE = 10.0  # W/m²

    def __init__(self, schema_path: Optional[Path] = None):
        """
        Initialize LIC-001 protocol

        Args:
            schema_path: Path to JSON schema (optional, uses default if not provided)
        """
        if schema_path is None:
            schema_path = Path(__file__).parent / "schema.json"

        super().__init__(self.PROTOCOL_ID, schema_path)
        self.analyzer = LIC001Analyzer()
        self.validator = LIC001Validator()

    def _get_metadata(self) -> ProtocolMetadata:
        """Return protocol metadata"""
        return ProtocolMetadata(
            protocol_id=self.PROTOCOL_ID,
            name="Low Irradiance Conditions Test",
            version=self.VERSION,
            standard=self.STANDARD,
            category=self.CATEGORY,
            description="Performance test at 200, 400, 600, and 800 W/m² at 25°C"
        )

    def validate_inputs(self, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate input data

        Checks:
        - Required fields present
        - Temperature within tolerance
        - Irradiance levels correct
        - I-V curve data valid

        Returns:
            (is_valid, error_messages)
        """
        return self.validator.validate_all(data)

    def calculate_results(self, measurements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate test results from measurements

        Args:
            measurements: Dictionary containing measurements at each irradiance level

        Returns:
            Dictionary of calculated results including:
            - Pmax, Vmp, Imp at each irradiance
            - Fill factor at each irradiance
            - Efficiency at each irradiance
            - Quality indicators
        """
        results = {
            "by_irradiance": {},
            "summary": {}
        }

        module_area = measurements.get("sample_info", {}).get("module_area", 1.0)

        # Process each irradiance level
        for irradiance_level in self.REQUIRED_IRRADIANCE_LEVELS:
            key = str(irradiance_level)
            if key not in measurements.get("measurements", {}):
                continue

            measurement = measurements["measurements"][key]

            # Extract I-V curve data
            iv_curve = measurement.get("iv_curve", {})
            voltage = iv_curve.get("voltage", [])
            current = iv_curve.get("current", [])
            actual_irradiance = measurement.get("actual_irradiance", irradiance_level)

            # Calculate results for this irradiance level
            level_results = self.analyzer.analyze_iv_curve(
                voltage=voltage,
                current=current,
                irradiance=actual_irradiance,
                temperature=measurement.get("actual_temperature", self.TARGET_TEMPERATURE),
                module_area=module_area
            )

            # Add quality assessment
            quality = self.analyzer.assess_curve_quality(voltage, current)
            level_results["quality_indicators"] = quality

            results["by_irradiance"][key] = level_results

        # Calculate summary statistics
        results["summary"] = self._calculate_summary(results["by_irradiance"])

        self.results = results
        return results

    def _calculate_summary(self, by_irradiance: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate summary statistics across all irradiance levels

        Args:
            by_irradiance: Results by irradiance level

        Returns:
            Summary statistics
        """
        summary = {
            "test_passed": True,
            "quality_score": 0.0,
            "performance_trends": {}
        }

        if not by_irradiance:
            summary["test_passed"] = False
            return summary

        # Calculate average quality score
        quality_scores = []
        for level_data in by_irradiance.values():
            quality = level_data.get("quality_indicators", {})
            score = quality.get("data_quality_score", 0)
            quality_scores.append(score)

        if quality_scores:
            summary["quality_score"] = sum(quality_scores) / len(quality_scores)
            # Test passes if average quality score >= 70
            summary["test_passed"] = summary["quality_score"] >= 70

        # Analyze performance trends
        irradiances = sorted([int(k) for k in by_irradiance.keys()])
        efficiencies = [by_irradiance[str(irr)]["efficiency"] for irr in irradiances]
        fill_factors = [by_irradiance[str(irr)]["fill_factor"] for irr in irradiances]

        summary["performance_trends"] = {
            "efficiency_trend": self._calculate_trend(irradiances, efficiencies),
            "fill_factor_trend": self._calculate_trend(irradiances, fill_factors),
            "avg_efficiency": sum(efficiencies) / len(efficiencies) if efficiencies else 0,
            "avg_fill_factor": sum(fill_factors) / len(fill_factors) if fill_factors else 0
        }

        return summary

    def _calculate_trend(self, x_values: List[float], y_values: List[float]) -> str:
        """
        Calculate trend direction (increasing, decreasing, stable)

        Args:
            x_values: Independent variable values
            y_values: Dependent variable values

        Returns:
            Trend description
        """
        if len(x_values) < 2 or len(y_values) < 2:
            return "insufficient_data"

        # Simple linear regression slope
        n = len(x_values)
        x_mean = sum(x_values) / n
        y_mean = sum(y_values) / n

        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)

        if denominator == 0:
            return "stable"

        slope = numerator / denominator

        if slope > 0.01:
            return "increasing"
        elif slope < -0.01:
            return "decreasing"
        else:
            return "stable"

    def generate_visualizations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Plotly visualizations

        Creates:
        - I-V curves for 200, 400, 600 W/m² (as per requirements)
        - Power curves
        - Performance summary charts

        Returns:
            Dictionary of Plotly figure objects
        """
        from .visualization import LIC001Visualizer

        visualizer = LIC001Visualizer()
        return visualizer.create_all_plots(data)

    def create_test_run(
        self,
        sample_id: str,
        sample_info: Dict[str, Any],
        operator: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new test run data structure

        Args:
            sample_id: Sample identifier
            sample_info: Sample information dictionary
            operator: Test operator name

        Returns:
            Test run data dictionary
        """
        run_id = generate_run_id(self.PROTOCOL_ID, sample_id)
        now = datetime.now()

        test_run = {
            "protocol_info": {
                "protocol_id": self.PROTOCOL_ID,
                "version": self.VERSION,
                "standard": self.STANDARD,
                "category": self.CATEGORY,
                "test_date": now.isoformat()
            },
            "sample_info": {
                "sample_id": sample_id,
                **sample_info
            },
            "test_conditions": {
                "temperature": self.TARGET_TEMPERATURE,
                "temperature_tolerance": self.TEMPERATURE_TOLERANCE,
                "spectrum": "AM1.5G",
                "irradiance_levels": self.REQUIRED_IRRADIANCE_LEVELS,
                "irradiance_tolerance": self.IRRADIANCE_TOLERANCE,
                "operator": operator
            },
            "measurements": {
                "200": self._create_measurement_template(200),
                "400": self._create_measurement_template(400),
                "600": self._create_measurement_template(600),
                "800": self._create_measurement_template(800)
            },
            "metadata": {
                "run_id": run_id,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat()
            }
        }

        return test_run

    def _create_measurement_template(self, irradiance: int) -> Dict[str, Any]:
        """Create empty measurement template for an irradiance level"""
        return {
            "actual_irradiance": irradiance,
            "actual_temperature": self.TARGET_TEMPERATURE,
            "timestamp": None,
            "iv_curve": {
                "voltage": [],
                "current": [],
                "num_points": 0
            },
            "raw_measurements": {
                "voc": None,
                "isc": None
            }
        }

    def finalize_test_run(self, test_run: Dict[str, Any]) -> Dict[str, Any]:
        """
        Finalize test run by calculating hash and updating timestamp

        Args:
            test_run: Test run data

        Returns:
            Updated test run data
        """
        test_run["metadata"]["updated_at"] = datetime.now().isoformat()
        test_run["metadata"]["data_hash"] = calculate_hash(test_run)

        return test_run
