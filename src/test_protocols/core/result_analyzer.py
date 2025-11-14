"""
Test result analysis and reporting.

This module provides functionality for analyzing test results, generating
statistics, and creating reports.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from statistics import mean, stdev
from datetime import datetime

from .test_executor import TestRun, StepResult, MeasurementData, TestStatus, StepStatus


@dataclass
class StepAnalysis:
    """Analysis results for a single step."""
    step_id: str
    step_name: str
    passed: bool
    duration_minutes: float
    measurement_count: int
    measurement_summary: Dict[str, Any]
    acceptance_criteria_met: List[str]
    acceptance_criteria_failed: List[str]
    notes: str


@dataclass
class TestAnalysis:
    """Complete analysis of a test run."""
    test_run_id: str
    protocol_id: str
    protocol_version: str
    sample_id: str
    operator_id: str
    overall_passed: bool
    test_status: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_minutes: Optional[float]
    total_steps: int
    passed_steps: int
    failed_steps: int
    total_measurements: int
    step_analyses: List[StepAnalysis]
    summary: str
    recommendations: List[str]


class ResultAnalyzer:
    """
    Analyzes test results and generates reports.

    Provides statistical analysis, pass/fail determination, and
    report generation capabilities.
    """

    def __init__(self, test_run: TestRun):
        """
        Initialize result analyzer.

        Args:
            test_run: TestRun object to analyze
        """
        self.test_run = test_run

    def analyze_step(self, step_result: StepResult, step_name: str) -> StepAnalysis:
        """
        Analyze results from a single test step.

        Args:
            step_result: StepResult to analyze
            step_name: Name of the test step

        Returns:
            StepAnalysis object
        """
        # Group measurements by type
        measurements_by_type: Dict[str, List[float]] = {}
        for measurement in step_result.measurements:
            if measurement.measurement_type not in measurements_by_type:
                measurements_by_type[measurement.measurement_type] = []
            measurements_by_type[measurement.measurement_type].append(measurement.value)

        # Calculate statistics for each measurement type
        measurement_summary = {}
        for mtype, values in measurements_by_type.items():
            if values:
                measurement_summary[mtype] = {
                    "count": len(values),
                    "mean": mean(values),
                    "min": min(values),
                    "max": max(values),
                    "stdev": stdev(values) if len(values) > 1 else 0,
                    "unit": next(
                        (m.unit for m in step_result.measurements if m.measurement_type == mtype),
                        "unknown"
                    )
                }

        return StepAnalysis(
            step_id=step_result.step_id,
            step_name=step_name,
            passed=step_result.passed or False,
            duration_minutes=step_result.duration_minutes() or 0,
            measurement_count=len(step_result.measurements),
            measurement_summary=measurement_summary,
            acceptance_criteria_met=[],  # Would need acceptance criteria logic
            acceptance_criteria_failed=[],
            notes=step_result.notes
        )

    def analyze_test(self) -> TestAnalysis:
        """
        Perform complete analysis of the test run.

        Returns:
            TestAnalysis object with comprehensive results
        """
        # Analyze each step
        step_analyses = []
        for step_result in self.test_run.step_results:
            # Find step name from protocol (would need protocol reference)
            step_name = step_result.step_id  # Simplified
            step_analysis = self.analyze_step(step_result, step_name)
            step_analyses.append(step_analysis)

        # Calculate overall statistics
        total_steps = len(self.test_run.step_results)
        passed_steps = sum(
            1 for result in self.test_run.step_results
            if result.passed is True
        )
        failed_steps = sum(
            1 for result in self.test_run.step_results
            if result.passed is False
        )

        total_measurements = sum(
            len(result.measurements)
            for result in self.test_run.step_results
        )

        # Determine overall pass/fail
        overall_passed = (
            self.test_run.status == TestStatus.COMPLETED and
            failed_steps == 0 and
            passed_steps == total_steps
        )

        # Generate summary
        summary = self._generate_summary(
            overall_passed,
            total_steps,
            passed_steps,
            failed_steps
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(step_analyses)

        return TestAnalysis(
            test_run_id=self.test_run.test_run_id,
            protocol_id=self.test_run.protocol_id,
            protocol_version=self.test_run.protocol_version,
            sample_id=self.test_run.sample_id,
            operator_id=self.test_run.operator_id,
            overall_passed=overall_passed,
            test_status=self.test_run.status.value,
            start_time=self.test_run.start_time,
            end_time=self.test_run.end_time,
            duration_minutes=self.test_run.duration_minutes(),
            total_steps=total_steps,
            passed_steps=passed_steps,
            failed_steps=failed_steps,
            total_measurements=total_measurements,
            step_analyses=step_analyses,
            summary=summary,
            recommendations=recommendations
        )

    def _generate_summary(
        self,
        overall_passed: bool,
        total_steps: int,
        passed_steps: int,
        failed_steps: int
    ) -> str:
        """Generate test summary text."""
        status = "PASSED" if overall_passed else "FAILED"

        summary = f"""
Test Result: {status}

Total Steps: {total_steps}
Passed Steps: {passed_steps}
Failed Steps: {failed_steps}
Success Rate: {(passed_steps / total_steps * 100):.1f}%

Test Run ID: {self.test_run.test_run_id}
Protocol: {self.test_run.protocol_id} v{self.test_run.protocol_version}
Sample: {self.test_run.sample_id}
Operator: {self.test_run.operator_id}
Duration: {self.test_run.duration_minutes():.1f} minutes
""".strip()

        return summary

    def _generate_recommendations(
        self,
        step_analyses: List[StepAnalysis]
    ) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []

        # Check for failed steps
        failed_steps = [s for s in step_analyses if not s.passed]
        if failed_steps:
            recommendations.append(
                f"Review and address failures in steps: "
                f"{', '.join(s.step_name for s in failed_steps)}"
            )

        # Check for steps with no measurements
        steps_no_data = [
            s for s in step_analyses
            if s.measurement_count == 0 and s.step_id.endswith(('S04', 'S05', 'S06'))
        ]
        if steps_no_data:
            recommendations.append(
                "Some measurement steps have no data recorded. "
                "Verify sensor connections and data acquisition system."
            )

        # Add standard recommendations
        if not recommendations:
            recommendations.append("Test completed successfully. Proceed to next protocol step.")

        return recommendations

    def export_to_dict(self) -> Dict[str, Any]:
        """
        Export test results to dictionary format.

        Returns:
            Dictionary containing all test data
        """
        analysis = self.analyze_test()

        return {
            "test_run_id": analysis.test_run_id,
            "protocol_id": analysis.protocol_id,
            "protocol_version": analysis.protocol_version,
            "sample_id": analysis.sample_id,
            "operator_id": analysis.operator_id,
            "overall_passed": analysis.overall_passed,
            "test_status": analysis.test_status,
            "start_time": analysis.start_time.isoformat(),
            "end_time": analysis.end_time.isoformat() if analysis.end_time else None,
            "duration_minutes": analysis.duration_minutes,
            "total_steps": analysis.total_steps,
            "passed_steps": analysis.passed_steps,
            "failed_steps": analysis.failed_steps,
            "total_measurements": analysis.total_measurements,
            "step_results": [
                {
                    "step_id": step.step_id,
                    "step_name": step.step_name,
                    "passed": step.passed,
                    "duration_minutes": step.duration_minutes,
                    "measurement_count": step.measurement_count,
                    "measurement_summary": step.measurement_summary,
                    "notes": step.notes,
                }
                for step in analysis.step_analyses
            ],
            "summary": analysis.summary,
            "recommendations": analysis.recommendations,
        }

    def generate_report_markdown(self) -> str:
        """
        Generate a markdown-formatted test report.

        Returns:
            Markdown string
        """
        analysis = self.analyze_test()

        report = f"""# Test Report: {analysis.protocol_id}

## Test Information
- **Test Run ID**: {analysis.test_run_id}
- **Protocol**: {analysis.protocol_id} v{analysis.protocol_version}
- **Sample ID**: {analysis.sample_id}
- **Operator**: {analysis.operator_id}
- **Start Time**: {analysis.start_time.strftime('%Y-%m-%d %H:%M:%S')}
- **End Time**: {analysis.end_time.strftime('%Y-%m-%d %H:%M:%S') if analysis.end_time else 'In Progress'}
- **Duration**: {analysis.duration_minutes:.1f} minutes

## Overall Result
**Status**: {'✅ PASSED' if analysis.overall_passed else '❌ FAILED'}

## Test Summary
- Total Steps: {analysis.total_steps}
- Passed Steps: {analysis.passed_steps} ({analysis.passed_steps / analysis.total_steps * 100:.1f}%)
- Failed Steps: {analysis.failed_steps} ({analysis.failed_steps / analysis.total_steps * 100:.1f}%)
- Total Measurements: {analysis.total_measurements}

## Step Results

"""

        for step in analysis.step_analyses:
            status_icon = "✅" if step.passed else "❌"
            report += f"""### {status_icon} {step.step_name}
- **Step ID**: {step.step_id}
- **Status**: {'Passed' if step.passed else 'Failed'}
- **Duration**: {step.duration_minutes:.1f} minutes
- **Measurements**: {step.measurement_count}

"""

            if step.measurement_summary:
                report += "**Measurement Summary**:\n\n"
                for mtype, stats in step.measurement_summary.items():
                    report += f"- **{mtype}**: "
                    report += f"Mean={stats['mean']:.2f} {stats['unit']}, "
                    report += f"Range=[{stats['min']:.2f}, {stats['max']:.2f}] {stats['unit']}, "
                    report += f"Std Dev={stats['stdev']:.2f}\n"

            if step.notes:
                report += f"\n**Notes**: {step.notes}\n"

            report += "\n"

        # Add recommendations
        if analysis.recommendations:
            report += "## Recommendations\n\n"
            for i, rec in enumerate(analysis.recommendations, 1):
                report += f"{i}. {rec}\n"

        return report

    def calculate_metrics(self) -> Dict[str, float]:
        """
        Calculate key performance metrics.

        Returns:
            Dictionary of metrics
        """
        analysis = self.analyze_test()

        metrics = {
            "success_rate": (analysis.passed_steps / analysis.total_steps * 100)
            if analysis.total_steps > 0 else 0,
            "total_duration_minutes": analysis.duration_minutes or 0,
            "average_step_duration": (analysis.duration_minutes / analysis.total_steps)
            if analysis.total_steps > 0 and analysis.duration_minutes else 0,
            "measurements_per_step": (analysis.total_measurements / analysis.total_steps)
            if analysis.total_steps > 0 else 0,
        }

        return metrics
