"""Chart components for UI."""

import streamlit as st
from typing import List, Dict, Any, Optional
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from analysis.charting import ProtocolChartGenerator


class ChartComponents:
    """Streamlit components for displaying charts."""

    def __init__(self, protocol_id: str):
        """
        Initialize chart components.

        Args:
            protocol_id: Protocol identifier
        """
        self.protocol_id = protocol_id
        self.chart_generator = ProtocolChartGenerator(protocol_id)

    def render_degradation_chart(
        self,
        measurements: List[Dict[str, Any]],
        baseline_power: float
    ) -> None:
        """
        Render degradation chart.

        Args:
            measurements: List of measurements
            baseline_power: Baseline power value
        """
        st.markdown("### Power Degradation Analysis")

        if not measurements:
            st.warning("No measurement data available")
            return

        try:
            fig = self.chart_generator.create_degradation_chart(
                measurements,
                baseline_power,
                title="Power Degradation Over Time"
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error generating chart: {e}")

    def render_environmental_chart(
        self,
        measurements: List[Dict[str, Any]]
    ) -> None:
        """
        Render environmental conditions chart.

        Args:
            measurements: List of measurements
        """
        st.markdown("### Environmental Conditions")

        if not measurements:
            st.warning("No measurement data available")
            return

        try:
            fig = self.chart_generator.create_environmental_conditions_chart(
                measurements,
                title="Environmental Conditions Monitoring"
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error generating chart: {e}")

    def render_iv_curve(
        self,
        iv_data: List[Dict[str, float]],
        title: str = "I-V Curve"
    ) -> None:
        """
        Render I-V curve chart.

        Args:
            iv_data: I-V curve data points
            title: Chart title
        """
        st.markdown(f"### {title}")

        if not iv_data:
            st.warning("No I-V curve data available")
            return

        try:
            fig = self.chart_generator.create_iv_curve_chart(iv_data, title=title)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error generating chart: {e}")

    def render_comparison_chart(
        self,
        test_runs: List[Dict[str, Any]],
        metric: str = "degradation"
    ) -> None:
        """
        Render comparison chart for multiple test runs.

        Args:
            test_runs: List of test run data
            metric: Metric to compare
        """
        st.markdown(f"### Test Comparison - {metric.title()}")

        if not test_runs:
            st.warning("No test runs to compare")
            return

        try:
            fig = self.chart_generator.create_comparison_chart(
                test_runs,
                metric=metric,
                title=f"Test Comparison - {metric.title()}"
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error generating chart: {e}")
