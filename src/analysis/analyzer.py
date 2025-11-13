"""Main analyzer orchestrator for IAM-001 protocol."""

from typing import Any, Dict, List
from .iam_calculator import IAMCalculator
from .curve_fitting import CurveFitter, ASHRAEModel, PhysicalModel, PolynomialModel


class IAM001Analyzer:
    """Main analyzer for IAM-001 protocol."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize analyzer with configuration.

        Args:
            config: Protocol configuration dictionary
        """
        self.config = config

    def analyze(
        self,
        protocol_data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform complete IAM analysis on protocol data.

        This is the main entry point for analysis, designed to be called
        by ProtocolExecutor.execute_analysis().

        Args:
            protocol_data: Protocol data with measurements
            config: Protocol configuration

        Returns:
            Dictionary with analysis results to be stored in protocol
        """
        measurements = protocol_data.get("measurements", [])

        if not measurements:
            raise ValueError("No measurements available for analysis")

        # Initialize calculator
        calculator = IAMCalculator(measurements)

        # Calculate IAM curve
        iam_curve = calculator.calculate_iam_with_correction(
            metric="pmax",
            normalization_angle=config.get("analysis_settings", {}).get("normalization_angle", 0),
            correct_irradiance=True
        )

        # Validate IAM curve
        is_valid, warnings = calculator.validate_iam_curve(iam_curve)

        # Fit models
        fitter = CurveFitter(iam_curve)
        fit_results = fitter.fit_all_models()

        # Select best model
        default_model = config.get("analysis_settings", {}).get("default_model", "ashrae")
        try:
            best_model_name, best_model_result = fitter.select_best_model(fit_results)
        except ValueError:
            best_model_name = default_model
            best_model_result = fit_results.get(default_model, {})

        # Assess fit quality
        fit_quality = self._assess_fit_quality(
            best_model_result.get("r_squared", 0),
            config
        )

        # Calculate statistics
        stats = calculator.get_statistics(iam_curve)

        # Build results
        analysis_results = {
            "iam_curve": iam_curve,
            "fitting_parameters": {
                "model": best_model_name,
                "parameters": best_model_result.get("parameters", {}),
                "r_squared": best_model_result.get("r_squared", 0),
                "rmse": best_model_result.get("rmse", 0),
                "mae": best_model_result.get("mae", 0)
            },
            "all_model_fits": fit_results,
            "quality_metrics": {
                "measurement_stability": "pass" if is_valid else "warning",
                "data_completeness": self._calculate_completeness(measurements, config),
                "fit_quality": fit_quality,
                "validation_warnings": warnings
            },
            "statistics": stats
        }

        return analysis_results

    def _assess_fit_quality(
        self,
        r_squared: float,
        config: Dict[str, Any]
    ) -> str:
        """Assess the quality of the curve fit.

        Args:
            r_squared: R-squared value
            config: Configuration with quality thresholds

        Returns:
            Quality assessment string
        """
        thresholds = config.get("analysis_settings", {}).get("fit_quality_thresholds", {
            "excellent": 0.99,
            "good": 0.95,
            "acceptable": 0.90,
            "poor": 0.0
        })

        if r_squared >= thresholds.get("excellent", 0.99):
            return "excellent"
        elif r_squared >= thresholds.get("good", 0.95):
            return "good"
        elif r_squared >= thresholds.get("acceptable", 0.90):
            return "acceptable"
        else:
            return "poor"

    def _calculate_completeness(
        self,
        measurements: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> float:
        """Calculate data completeness percentage.

        Args:
            measurements: List of measurements
            config: Configuration with expected angles

        Returns:
            Completeness percentage (0-100)
        """
        recommended_angles = config.get("default_settings", {}).get(
            "recommended_angles",
            [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
        )

        measured_angles = set(m.get("angle", 0) for m in measurements)
        expected_angles = set(recommended_angles)

        # Allow 1 degree tolerance
        matched = 0
        for exp_angle in expected_angles:
            if any(abs(meas_angle - exp_angle) <= 1 for meas_angle in measured_angles):
                matched += 1

        completeness = (matched / len(expected_angles)) * 100 if expected_angles else 100

        return float(completeness)


# Factory function for use with ProtocolExecutor
def create_analyzer(protocol_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Factory function to create and run analyzer.

    This function signature matches what ProtocolExecutor.execute_analysis() expects.

    Args:
        protocol_data: Protocol data with measurements
        config: Protocol configuration

    Returns:
        Analysis results dictionary
    """
    analyzer = IAM001Analyzer(config)
    return analyzer.analyze(protocol_data, config)
