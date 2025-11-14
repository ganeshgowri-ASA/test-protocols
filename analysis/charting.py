"""Charting and visualization module for protocol data."""

from typing import List, Dict, Any, Optional
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np


class ProtocolChartGenerator:
    """Generate charts for protocol test data."""

    def __init__(self, protocol_id: str):
        """
        Initialize chart generator.

        Args:
            protocol_id: Protocol identifier
        """
        self.protocol_id = protocol_id

    def create_degradation_chart(
        self,
        measurements: List[Dict[str, Any]],
        baseline_power: float,
        title: str = "Power Degradation Over Time"
    ) -> go.Figure:
        """
        Create power degradation chart.

        Args:
            measurements: List of measurements
            baseline_power: Baseline power for degradation calculation
            title: Chart title

        Returns:
            Plotly figure
        """
        # Extract data
        times = []
        powers = []
        degradations = []

        for m in measurements:
            if m.get("elapsed_hours") is not None and m.get("pmax") is not None:
                times.append(m["elapsed_hours"])
                powers.append(m["pmax"])
                deg = 100 * (baseline_power - m["pmax"]) / baseline_power
                degradations.append(deg)

        # Create figure with secondary y-axis
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Maximum Power", "Power Degradation"),
            vertical_spacing=0.12,
            row_heights=[0.5, 0.5]
        )

        # Power trace
        fig.add_trace(
            go.Scatter(
                x=times,
                y=powers,
                mode='lines+markers',
                name='Pmax',
                line=dict(color='blue', width=2),
                marker=dict(size=6)
            ),
            row=1, col=1
        )

        # Baseline reference
        if times:
            fig.add_trace(
                go.Scatter(
                    x=[min(times), max(times)],
                    y=[baseline_power, baseline_power],
                    mode='lines',
                    name='Baseline',
                    line=dict(color='green', width=2, dash='dash')
                ),
                row=1, col=1
            )

        # Degradation trace
        fig.add_trace(
            go.Scatter(
                x=times,
                y=degradations,
                mode='lines+markers',
                name='Degradation',
                line=dict(color='red', width=2),
                marker=dict(size=6),
                fill='tozeroy',
                fillcolor='rgba(255, 0, 0, 0.1)'
            ),
            row=2, col=1
        )

        # Update axes
        fig.update_xaxes(title_text="Time (hours)", row=1, col=1)
        fig.update_xaxes(title_text="Time (hours)", row=2, col=1)
        fig.update_yaxes(title_text="Power (W)", row=1, col=1)
        fig.update_yaxes(title_text="Degradation (%)", row=2, col=1)

        # Update layout
        fig.update_layout(
            title_text=title,
            height=700,
            showlegend=True,
            hovermode='x unified'
        )

        return fig

    def create_iv_curve_chart(
        self,
        iv_data: List[Dict[str, float]],
        title: str = "I-V Curve"
    ) -> go.Figure:
        """
        Create I-V curve chart.

        Args:
            iv_data: List of {voltage, current} dictionaries
            title: Chart title

        Returns:
            Plotly figure
        """
        voltages = [point["voltage"] for point in iv_data]
        currents = [point["current"] for point in iv_data]
        powers = [v * i for v, i in zip(voltages, currents)]

        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Current trace
        fig.add_trace(
            go.Scatter(
                x=voltages,
                y=currents,
                mode='lines+markers',
                name='Current',
                line=dict(color='blue', width=2),
                marker=dict(size=4)
            ),
            secondary_y=False
        )

        # Power trace
        fig.add_trace(
            go.Scatter(
                x=voltages,
                y=powers,
                mode='lines+markers',
                name='Power',
                line=dict(color='red', width=2),
                marker=dict(size=4)
            ),
            secondary_y=True
        )

        # Update axes
        fig.update_xaxes(title_text="Voltage (V)")
        fig.update_yaxes(title_text="Current (A)", secondary_y=False)
        fig.update_yaxes(title_text="Power (W)", secondary_y=True)

        # Update layout
        fig.update_layout(
            title_text=title,
            hovermode='x unified',
            height=500
        )

        return fig

    def create_environmental_conditions_chart(
        self,
        measurements: List[Dict[str, Any]],
        title: str = "Environmental Conditions"
    ) -> go.Figure:
        """
        Create environmental conditions chart.

        Args:
            measurements: List of measurements
            title: Chart title

        Returns:
            Plotly figure
        """
        times = []
        irradiances = []
        temperatures = []

        for m in measurements:
            if m.get("elapsed_hours") is not None:
                times.append(m["elapsed_hours"])
                irradiances.append(m.get("irradiance"))
                temperatures.append(m.get("temperature"))

        # Create subplots
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Irradiance", "Temperature"),
            vertical_spacing=0.12
        )

        # Irradiance trace
        fig.add_trace(
            go.Scatter(
                x=times,
                y=irradiances,
                mode='lines+markers',
                name='Irradiance',
                line=dict(color='orange', width=2),
                marker=dict(size=6)
            ),
            row=1, col=1
        )

        # Temperature trace
        fig.add_trace(
            go.Scatter(
                x=times,
                y=temperatures,
                mode='lines+markers',
                name='Temperature',
                line=dict(color='purple', width=2),
                marker=dict(size=6)
            ),
            row=2, col=1
        )

        # Update axes
        fig.update_xaxes(title_text="Time (hours)", row=1, col=1)
        fig.update_xaxes(title_text="Time (hours)", row=2, col=1)
        fig.update_yaxes(title_text="Irradiance (W/m²)", row=1, col=1)
        fig.update_yaxes(title_text="Temperature (°C)", row=2, col=1)

        # Update layout
        fig.update_layout(
            title_text=title,
            height=600,
            showlegend=True,
            hovermode='x unified'
        )

        return fig

    def create_qc_summary_chart(
        self,
        qc_results: List[Dict[str, Any]],
        title: str = "QC Check Summary"
    ) -> go.Figure:
        """
        Create QC summary chart.

        Args:
            qc_results: List of QC check results
            title: Chart title

        Returns:
            Plotly figure
        """
        # Count by severity
        severity_counts = {}
        for result in qc_results:
            severity = result.get("severity", "unknown")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        # Create pie chart
        fig = go.Figure(data=[
            go.Pie(
                labels=list(severity_counts.keys()),
                values=list(severity_counts.values()),
                marker=dict(
                    colors=['green', 'yellow', 'orange', 'red'],
                    line=dict(color='white', width=2)
                )
            )
        ])

        fig.update_layout(
            title_text=title,
            height=400
        )

        return fig

    def create_comparison_chart(
        self,
        test_runs: List[Dict[str, Any]],
        metric: str = "degradation",
        title: str = "Test Comparison"
    ) -> go.Figure:
        """
        Create comparison chart for multiple test runs.

        Args:
            test_runs: List of test run data
            metric: Metric to compare
            title: Chart title

        Returns:
            Plotly figure
        """
        fig = go.Figure()

        for run in test_runs:
            run_id = run.get("test_run_id", "Unknown")
            measurements = run.get("measurements", [])

            times = []
            values = []

            for m in measurements:
                if m.get("elapsed_hours") is not None:
                    times.append(m["elapsed_hours"])

                    if metric == "degradation":
                        baseline = run.get("baseline_power", 1.0)
                        pmax = m.get("pmax", 0)
                        value = 100 * (baseline - pmax) / baseline if baseline > 0 else 0
                    elif metric == "power":
                        value = m.get("pmax", 0)
                    elif metric == "efficiency":
                        value = m.get("efficiency", 0)
                    else:
                        value = m.get(metric, 0)

                    values.append(value)

            fig.add_trace(
                go.Scatter(
                    x=times,
                    y=values,
                    mode='lines+markers',
                    name=run_id,
                    line=dict(width=2),
                    marker=dict(size=6)
                )
            )

        # Update layout
        fig.update_layout(
            title_text=title,
            xaxis_title="Time (hours)",
            yaxis_title=metric.capitalize(),
            hovermode='x unified',
            height=500
        )

        return fig
