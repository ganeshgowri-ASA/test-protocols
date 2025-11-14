"""Chart generation module for ENER-001 Energy Rating Test."""

from typing import Dict, Any, List
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np


class ChartGenerator:
    """Generates charts for energy rating test results."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize chart generator.

        Args:
            config: Protocol configuration dictionary
        """
        self.config = config
        self.charts_config = config.get("charts", [])

    def generate_charts(
        self,
        data: pd.DataFrame,
        iv_curves: Dict[str, Any],
        analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate all charts for the test report.

        Args:
            data: Measurement data
            iv_curves: Dictionary of IV curves
            analysis: Analysis results

        Returns:
            Dictionary of chart objects
        """
        charts = {}

        # Generate each configured chart
        charts["iv_curves"] = self.plot_iv_curves(iv_curves)
        charts["pv_curves"] = self.plot_pv_curves(iv_curves)
        charts["power_vs_irradiance"] = self.plot_power_vs_irradiance(iv_curves)
        charts["power_vs_temperature"] = self.plot_power_vs_temperature(iv_curves)
        charts["efficiency_map"] = self.plot_efficiency_map(iv_curves)
        charts["energy_rating_contribution"] = self.plot_energy_contribution(analysis)

        return charts

    def plot_iv_curves(self, iv_curves: Dict[str, Any]) -> go.Figure:
        """
        Plot I-V characteristics for all test conditions.

        Args:
            iv_curves: Dictionary of IV curves

        Returns:
            Plotly figure object
        """
        fig = go.Figure()

        # Group by temperature
        temp_groups = {}
        for key, curve in iv_curves.items():
            temp = curve["temperature"]
            if temp not in temp_groups:
                temp_groups[temp] = []
            temp_groups[temp].append(curve)

        # Plot each temperature group
        colors = ["blue", "green", "orange", "red", "purple"]
        temp_idx = 0

        for temp in sorted(temp_groups.keys()):
            curves = sorted(temp_groups[temp], key=lambda x: x["irradiance"])

            for curve in curves:
                irr = curve["irradiance"]
                label = f"G={int(irr)} W/m², T={int(temp)}°C"

                fig.add_trace(
                    go.Scatter(
                        x=curve["voltage"],
                        y=curve["current"],
                        mode="lines+markers",
                        name=label,
                        line=dict(color=colors[temp_idx % len(colors)]),
                        legendgroup=f"temp_{temp}",
                    )
                )

            temp_idx += 1

        fig.update_layout(
            title="I-V Characteristics",
            xaxis_title="Voltage (V)",
            yaxis_title="Current (A)",
            hovermode="closest",
            legend=dict(x=1.05, y=1, xanchor="left", yanchor="top"),
            height=600,
        )

        return fig

    def plot_pv_curves(self, iv_curves: Dict[str, Any]) -> go.Figure:
        """
        Plot P-V characteristics for all test conditions.

        Args:
            iv_curves: Dictionary of IV curves

        Returns:
            Plotly figure object
        """
        fig = go.Figure()

        # Group by temperature
        temp_groups = {}
        for key, curve in iv_curves.items():
            temp = curve["temperature"]
            if temp not in temp_groups:
                temp_groups[temp] = []
            temp_groups[temp].append(curve)

        colors = ["blue", "green", "orange", "red", "purple"]
        temp_idx = 0

        for temp in sorted(temp_groups.keys()):
            curves = sorted(temp_groups[temp], key=lambda x: x["irradiance"])

            for curve in curves:
                irr = curve["irradiance"]
                label = f"G={int(irr)} W/m², T={int(temp)}°C"

                fig.add_trace(
                    go.Scatter(
                        x=curve["voltage"],
                        y=curve["power"],
                        mode="lines+markers",
                        name=label,
                        line=dict(color=colors[temp_idx % len(colors)]),
                        legendgroup=f"temp_{temp}",
                    )
                )

                # Mark MPP
                fig.add_trace(
                    go.Scatter(
                        x=[curve["vmpp"]],
                        y=[curve["pmpp"]],
                        mode="markers",
                        name=f"MPP: {label}",
                        marker=dict(
                            size=10,
                            color=colors[temp_idx % len(colors)],
                            symbol="star",
                        ),
                        legendgroup=f"temp_{temp}",
                        showlegend=False,
                    )
                )

            temp_idx += 1

        fig.update_layout(
            title="P-V Characteristics",
            xaxis_title="Voltage (V)",
            yaxis_title="Power (W)",
            hovermode="closest",
            legend=dict(x=1.05, y=1, xanchor="left", yanchor="top"),
            height=600,
        )

        return fig

    def plot_power_vs_irradiance(self, iv_curves: Dict[str, Any]) -> go.Figure:
        """
        Plot maximum power vs irradiance at different temperatures.

        Args:
            iv_curves: Dictionary of IV curves

        Returns:
            Plotly figure object
        """
        fig = go.Figure()

        # Organize data by temperature
        temp_data = {}
        for key, curve in iv_curves.items():
            temp = curve["temperature"]
            if temp not in temp_data:
                temp_data[temp] = {"irradiance": [], "power": []}

            temp_data[temp]["irradiance"].append(curve["irradiance"])
            temp_data[temp]["power"].append(curve["pmpp"])

        # Plot each temperature series
        colors = ["blue", "green", "orange", "red"]
        temp_idx = 0

        for temp in sorted(temp_data.keys()):
            # Sort by irradiance
            sorted_indices = np.argsort(temp_data[temp]["irradiance"])
            irr = np.array(temp_data[temp]["irradiance"])[sorted_indices]
            power = np.array(temp_data[temp]["power"])[sorted_indices]

            fig.add_trace(
                go.Scatter(
                    x=irr,
                    y=power,
                    mode="lines+markers",
                    name=f"T = {int(temp)}°C",
                    line=dict(color=colors[temp_idx % len(colors)], width=2),
                    marker=dict(size=8),
                )
            )

            # Add trendline
            if len(irr) >= 2:
                z = np.polyfit(irr, power, 1)
                p = np.poly1d(z)
                fig.add_trace(
                    go.Scatter(
                        x=irr,
                        y=p(irr),
                        mode="lines",
                        name=f"Trend: T = {int(temp)}°C",
                        line=dict(color=colors[temp_idx % len(colors)], dash="dash"),
                        showlegend=False,
                    )
                )

            temp_idx += 1

        fig.update_layout(
            title="Maximum Power vs Irradiance",
            xaxis_title="Irradiance (W/m²)",
            yaxis_title="Maximum Power (W)",
            hovermode="closest",
            height=500,
        )

        return fig

    def plot_power_vs_temperature(self, iv_curves: Dict[str, Any]) -> go.Figure:
        """
        Plot maximum power vs temperature at different irradiance levels.

        Args:
            iv_curves: Dictionary of IV curves

        Returns:
            Plotly figure object
        """
        fig = go.Figure()

        # Organize data by irradiance
        irr_data = {}
        for key, curve in iv_curves.items():
            irr = curve["irradiance"]
            if irr not in irr_data:
                irr_data[irr] = {"temperature": [], "power": []}

            irr_data[irr]["temperature"].append(curve["temperature"])
            irr_data[irr]["power"].append(curve["pmpp"])

        # Plot each irradiance series
        colors = ["purple", "blue", "green", "orange", "red", "brown"]
        irr_idx = 0

        for irr in sorted(irr_data.keys()):
            # Sort by temperature
            sorted_indices = np.argsort(irr_data[irr]["temperature"])
            temp = np.array(irr_data[irr]["temperature"])[sorted_indices]
            power = np.array(irr_data[irr]["power"])[sorted_indices]

            fig.add_trace(
                go.Scatter(
                    x=temp,
                    y=power,
                    mode="lines+markers",
                    name=f"G = {int(irr)} W/m²",
                    line=dict(color=colors[irr_idx % len(colors)], width=2),
                    marker=dict(size=8),
                )
            )

            # Add trendline
            if len(temp) >= 2:
                z = np.polyfit(temp, power, 1)
                p = np.poly1d(z)
                fig.add_trace(
                    go.Scatter(
                        x=temp,
                        y=p(temp),
                        mode="lines",
                        name=f"Trend: G = {int(irr)} W/m²",
                        line=dict(color=colors[irr_idx % len(colors)], dash="dash"),
                        showlegend=False,
                    )
                )

            irr_idx += 1

        fig.update_layout(
            title="Maximum Power vs Temperature",
            xaxis_title="Module Temperature (°C)",
            yaxis_title="Maximum Power (W)",
            hovermode="closest",
            height=500,
        )

        return fig

    def plot_efficiency_map(self, iv_curves: Dict[str, Any]) -> go.Figure:
        """
        Plot efficiency heatmap across irradiance-temperature matrix.

        Args:
            iv_curves: Dictionary of IV curves

        Returns:
            Plotly figure object
        """
        # Organize data
        irradiances = sorted(set(c["irradiance"] for c in iv_curves.values()))
        temperatures = sorted(set(c["temperature"] for c in iv_curves.values()))

        # Create efficiency matrix
        eff_matrix = np.zeros((len(temperatures), len(irradiances)))

        for i, temp in enumerate(temperatures):
            for j, irr in enumerate(irradiances):
                # Find matching curve
                for key, curve in iv_curves.items():
                    if curve["irradiance"] == irr and curve["temperature"] == temp:
                        eff_matrix[i, j] = curve.get("efficiency", 0)
                        break

        fig = go.Figure(
            data=go.Heatmap(
                z=eff_matrix,
                x=irradiances,
                y=temperatures,
                colorscale="Viridis",
                colorbar=dict(title="Efficiency (%)"),
                text=np.round(eff_matrix, 2),
                texttemplate="%{text}%",
                textfont={"size": 10},
            )
        )

        fig.update_layout(
            title="Efficiency Map",
            xaxis_title="Irradiance (W/m²)",
            yaxis_title="Module Temperature (°C)",
            height=500,
        )

        return fig

    def plot_energy_contribution(self, analysis: Dict[str, Any]) -> go.Figure:
        """
        Plot energy rating contribution by operating conditions.

        Args:
            analysis: Analysis results with energy rating

        Returns:
            Plotly figure object
        """
        if "energy_rating" not in analysis:
            return go.Figure()

        contributions = analysis["energy_rating"].get("contributions", {})

        if not contributions:
            return go.Figure()

        conditions = list(contributions.keys())
        energies = [contributions[c]["energy_contribution"] for c in conditions]
        weights = [contributions[c]["weight"] for c in conditions]

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=conditions,
                y=energies,
                text=[f"{e:.1f}" for e in energies],
                textposition="auto",
                marker=dict(
                    color=energies,
                    colorscale="Blues",
                    colorbar=dict(title="Energy (kWh/kWp)"),
                ),
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    + "Energy: %{y:.2f} kWh/kWp<br>"
                    + "Weight: %{customdata:.1%}<br>"
                    + "<extra></extra>"
                ),
                customdata=weights,
            )
        )

        fig.update_layout(
            title="Energy Rating Contribution by Operating Conditions",
            xaxis_title="Operating Condition",
            yaxis_title="Energy Contribution (kWh/kWp)",
            height=500,
            xaxis_tickangle=-45,
        )

        return fig

    def export_chart(self, fig: go.Figure, filename: str, format: str = "html") -> None:
        """
        Export chart to file.

        Args:
            fig: Plotly figure
            filename: Output filename
            format: Export format ('html', 'png', 'svg', 'pdf')
        """
        if format == "html":
            fig.write_html(filename)
        elif format == "png":
            fig.write_image(filename)
        elif format == "svg":
            fig.write_image(filename, format="svg")
        elif format == "pdf":
            fig.write_image(filename, format="pdf")
        else:
            raise ValueError(f"Unsupported export format: {format}")
