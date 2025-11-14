"""Snow Load Test Data Analysis

Analysis and visualization functions for snow load test data.
"""

from typing import List, Dict, Tuple, Optional
import logging
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class LoadDeflectionPoint:
    """Single point on load-deflection curve"""
    load_pa: float
    deflection_mm: float
    phase: str


@dataclass
class AnalysisResults:
    """Results of snow load test analysis"""
    max_deflection_mm: float
    permanent_deflection_mm: float
    stiffness_n_mm: Optional[float]
    elastic_recovery_pct: float
    load_deflection_curve: List[LoadDeflectionPoint]
    pass_fail: bool
    failure_mode: Optional[str] = None


class SnowLoadAnalyzer:
    """Analyzer for snow load test data"""

    def __init__(self, measurements: List[Dict], baseline_deflection: float = 0):
        """
        Initialize analyzer with measurement data.

        Args:
            measurements: List of measurement dictionaries
            baseline_deflection: Baseline deflection measurement
        """
        self.measurements = measurements
        self.baseline_deflection = baseline_deflection

    def analyze(self) -> AnalysisResults:
        """
        Perform comprehensive analysis of test data.

        Returns:
            AnalysisResults: Complete analysis results
        """
        logger.info("Analyzing snow load test data")

        # Extract load-deflection curve
        load_deflection_curve = self._extract_load_deflection_curve()

        # Calculate key metrics
        max_deflection = max(m["deflection_mm"] for m in self.measurements)

        # Get final deflection after recovery
        recovery_measurements = [
            m for m in self.measurements if m.get("phase") == "recovery"
        ]
        final_deflection = recovery_measurements[-1]["deflection_mm"] if recovery_measurements else 0
        permanent_deflection = final_deflection - self.baseline_deflection

        # Calculate stiffness (slope of load-deflection curve)
        stiffness = self._calculate_stiffness(load_deflection_curve)

        # Calculate elastic recovery
        elastic_recovery_pct = self._calculate_elastic_recovery(
            max_deflection, permanent_deflection
        )

        # Determine pass/fail
        pass_fail = self._evaluate_pass_fail(
            max_deflection, permanent_deflection
        )

        # Determine failure mode if failed
        failure_mode = self._determine_failure_mode(
            max_deflection, permanent_deflection
        ) if not pass_fail else None

        logger.info(f"Analysis complete: {'PASS' if pass_fail else 'FAIL'}")

        return AnalysisResults(
            max_deflection_mm=max_deflection,
            permanent_deflection_mm=permanent_deflection,
            stiffness_n_mm=stiffness,
            elastic_recovery_pct=elastic_recovery_pct,
            load_deflection_curve=load_deflection_curve,
            pass_fail=pass_fail,
            failure_mode=failure_mode
        )

    def _extract_load_deflection_curve(self) -> List[LoadDeflectionPoint]:
        """Extract load-deflection curve from measurements"""
        curve_points = []

        for measurement in self.measurements:
            point = LoadDeflectionPoint(
                load_pa=measurement.get("load_applied_pa", 0),
                deflection_mm=measurement["deflection_mm"],
                phase=measurement.get("phase", "unknown")
            )
            curve_points.append(point)

        return curve_points

    def _calculate_stiffness(
        self, curve: List[LoadDeflectionPoint]
    ) -> Optional[float]:
        """
        Calculate module stiffness from load-deflection curve.

        Uses linear regression on loading phase data.

        Returns:
            float: Stiffness in N/mm, or None if insufficient data
        """
        # Filter loading phase points
        loading_points = [p for p in curve if p.phase == "loading"]

        if len(loading_points) < 2:
            logger.warning("Insufficient data for stiffness calculation")
            return None

        # Simple linear regression
        n = len(loading_points)
        sum_load = sum(p.load_pa for p in loading_points)
        sum_deflection = sum(p.deflection_mm for p in loading_points)
        sum_load_deflection = sum(
            p.load_pa * p.deflection_mm for p in loading_points
        )
        sum_deflection_squared = sum(
            p.deflection_mm ** 2 for p in loading_points
        )

        # Calculate slope (stiffness): load / deflection
        denominator = n * sum_deflection_squared - sum_deflection ** 2
        if abs(denominator) < 1e-6:
            logger.warning("Cannot calculate stiffness: degenerate data")
            return None

        stiffness_pa_mm = (
            n * sum_load_deflection - sum_load * sum_deflection
        ) / denominator

        return stiffness_pa_mm

    def _calculate_elastic_recovery(
        self, max_deflection: float, permanent_deflection: float
    ) -> float:
        """
        Calculate elastic recovery percentage.

        Args:
            max_deflection: Maximum deflection during test
            permanent_deflection: Permanent deflection after unloading

        Returns:
            float: Elastic recovery percentage
        """
        if max_deflection == 0:
            return 0.0

        elastic_deflection = max_deflection - permanent_deflection
        recovery_pct = (elastic_deflection / max_deflection) * 100

        return recovery_pct

    def _evaluate_pass_fail(
        self, max_deflection: float, permanent_deflection: float
    ) -> bool:
        """
        Evaluate pass/fail based on acceptance criteria.

        Args:
            max_deflection: Maximum deflection
            permanent_deflection: Permanent deflection

        Returns:
            bool: True if pass, False if fail
        """
        # Default criteria (would normally come from config)
        max_allowed_deflection = 50.0  # mm
        max_allowed_permanent = 5.0  # mm

        if max_deflection > max_allowed_deflection:
            logger.warning(
                f"Max deflection {max_deflection:.2f} mm exceeds limit {max_allowed_deflection} mm"
            )
            return False

        if permanent_deflection > max_allowed_permanent:
            logger.warning(
                f"Permanent deflection {permanent_deflection:.2f} mm exceeds limit {max_allowed_permanent} mm"
            )
            return False

        return True

    def _determine_failure_mode(
        self, max_deflection: float, permanent_deflection: float
    ) -> str:
        """
        Determine the failure mode.

        Args:
            max_deflection: Maximum deflection
            permanent_deflection: Permanent deflection

        Returns:
            str: Description of failure mode
        """
        max_allowed_deflection = 50.0
        max_allowed_permanent = 5.0

        if max_deflection > max_allowed_deflection * 1.5:
            return "excessive_deflection_structural_failure"
        elif max_deflection > max_allowed_deflection:
            return "excessive_deflection"
        elif permanent_deflection > max_allowed_permanent * 2:
            return "severe_permanent_deformation"
        elif permanent_deflection > max_allowed_permanent:
            return "permanent_deformation"
        else:
            return "unknown_failure"

    def generate_summary(self) -> Dict:
        """
        Generate a summary report of the analysis.

        Returns:
            Dict: Summary data
        """
        results = self.analyze()

        return {
            "max_deflection_mm": results.max_deflection_mm,
            "permanent_deflection_mm": results.permanent_deflection_mm,
            "elastic_recovery_pct": results.elastic_recovery_pct,
            "stiffness_n_mm": results.stiffness_n_mm,
            "test_result": "PASS" if results.pass_fail else "FAIL",
            "failure_mode": results.failure_mode,
            "total_measurements": len(self.measurements),
            "load_cycles": len([
                m for m in self.measurements if m.get("phase") == "baseline"
            ])
        }


def plot_load_deflection_curve(
    curve_points: List[LoadDeflectionPoint],
    title: str = "Load-Deflection Curve"
) -> Dict:
    """
    Generate plot data for load-deflection curve.

    Args:
        curve_points: List of load-deflection points
        title: Plot title

    Returns:
        Dict: Plot configuration for visualization
    """
    # Group points by phase
    phases = {}
    for point in curve_points:
        if point.phase not in phases:
            phases[point.phase] = {"load": [], "deflection": []}
        phases[point.phase]["load"].append(point.load_pa)
        phases[point.phase]["deflection"].append(point.deflection_mm)

    # Generate plot data
    plot_data = {
        "title": title,
        "x_label": "Deflection (mm)",
        "y_label": "Load (Pa)",
        "series": []
    }

    # Color scheme for phases
    phase_colors = {
        "baseline": "#808080",
        "loading": "#FF6B6B",
        "hold": "#4ECDC4",
        "unloading": "#45B7D1",
        "recovery": "#96CEB4"
    }

    for phase, data in phases.items():
        plot_data["series"].append({
            "name": phase.capitalize(),
            "x": data["deflection"],
            "y": data["load"],
            "color": phase_colors.get(phase, "#000000"),
            "marker": "o" if phase in ["baseline", "recovery"] else "-"
        })

    return plot_data


def generate_report_summary(
    analysis_results: AnalysisResults,
    config: Dict,
    module_specs: Dict
) -> Dict:
    """
    Generate comprehensive test report summary.

    Args:
        analysis_results: Analysis results
        config: Test configuration
        module_specs: Module specifications

    Returns:
        Dict: Report summary data
    """
    return {
        "executive_summary": {
            "test_result": "PASS" if analysis_results.pass_fail else "FAIL",
            "max_deflection_mm": analysis_results.max_deflection_mm,
            "permanent_deflection_mm": analysis_results.permanent_deflection_mm,
            "elastic_recovery_pct": analysis_results.elastic_recovery_pct,
            "failure_mode": analysis_results.failure_mode
        },
        "module_information": module_specs,
        "test_configuration": config,
        "key_metrics": {
            "stiffness_n_mm": analysis_results.stiffness_n_mm,
            "max_deflection_mm": analysis_results.max_deflection_mm,
            "permanent_deflection_mm": analysis_results.permanent_deflection_mm,
            "elastic_recovery_pct": analysis_results.elastic_recovery_pct
        },
        "visualization": {
            "load_deflection_curve": plot_load_deflection_curve(
                analysis_results.load_deflection_curve,
                "Snow Load Test - Load vs Deflection"
            )
        }
    }


def calculate_safety_factor(
    test_load_pa: float,
    design_load_pa: float
) -> float:
    """
    Calculate safety factor.

    Args:
        test_load_pa: Applied test load
        design_load_pa: Design load specification

    Returns:
        float: Safety factor
    """
    if design_load_pa == 0:
        return float('inf')

    return test_load_pa / design_load_pa


def compare_cycles(
    cycle_results: List[AnalysisResults]
) -> Dict:
    """
    Compare results across multiple test cycles.

    Args:
        cycle_results: List of analysis results for each cycle

    Returns:
        Dict: Comparison data
    """
    if not cycle_results:
        return {}

    return {
        "cycle_count": len(cycle_results),
        "max_deflection_progression": [
            r.max_deflection_mm for r in cycle_results
        ],
        "permanent_deflection_progression": [
            r.permanent_deflection_mm for r in cycle_results
        ],
        "stiffness_degradation": [
            r.stiffness_n_mm for r in cycle_results if r.stiffness_n_mm
        ],
        "degradation_trend": _analyze_degradation_trend(cycle_results)
    }


def _analyze_degradation_trend(
    cycle_results: List[AnalysisResults]
) -> str:
    """
    Analyze degradation trend across cycles.

    Args:
        cycle_results: List of analysis results

    Returns:
        str: Trend description
    """
    if len(cycle_results) < 2:
        return "insufficient_data"

    # Check if permanent deflection is increasing
    permanent_deflections = [
        r.permanent_deflection_mm for r in cycle_results
    ]

    # Calculate average increase per cycle
    total_increase = permanent_deflections[-1] - permanent_deflections[0]
    avg_increase = total_increase / (len(cycle_results) - 1)

    if avg_increase > 1.0:
        return "severe_degradation"
    elif avg_increase > 0.5:
        return "moderate_degradation"
    elif avg_increase > 0.1:
        return "minor_degradation"
    else:
        return "stable"
