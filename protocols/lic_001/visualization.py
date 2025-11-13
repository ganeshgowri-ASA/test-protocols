"""
Visualization module for LIC-001 protocol using Plotly
"""

from typing import Dict, List, Any
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np


class LIC001Visualizer:
    """
    Creates Plotly visualizations for LIC-001 test data
    """

    # Color scheme for different irradiance levels
    COLORS = {
        "200": "#FF6B6B",  # Red
        "400": "#FFA500",  # Orange
        "600": "#4ECDC4",  # Teal
        "800": "#45B7D1",  # Blue
    }

    def create_all_plots(self, data: Dict[str, Any]) -> Dict[str, go.Figure]:
        """
        Create all visualizations for LIC-001

        Args:
            data: Complete test data including measurements and results

        Returns:
            Dictionary of Plotly figure objects
        """
        plots = {}

        measurements = data.get("measurements", {})
        results = data.get("results", {}).get("by_irradiance", {})

        # I-V curves (200, 400, 600 W/m² as per requirements)
        plots["iv_curves"] = self.create_iv_curves(measurements, [200, 400, 600])

        # All I-V curves (including 800 W/m²)
        plots["iv_curves_all"] = self.create_iv_curves(measurements, [200, 400, 600, 800])

        # Power curves
        plots["power_curves"] = self.create_power_curves(measurements, [200, 400, 600, 800])

        # Performance summary
        if results:
            plots["performance_summary"] = self.create_performance_summary(results)

            # Irradiance response
            plots["irradiance_response"] = self.create_irradiance_response(results)

            # Fill factor comparison
            plots["fill_factor_comparison"] = self.create_fill_factor_comparison(results)

        return plots

    def create_iv_curves(
        self,
        measurements: Dict[str, Any],
        irradiance_levels: List[int]
    ) -> go.Figure:
        """
        Create I-V curves plot for specified irradiance levels

        Args:
            measurements: Measurement data
            irradiance_levels: List of irradiance levels to plot (e.g., [200, 400, 600])

        Returns:
            Plotly Figure object
        """
        fig = go.Figure()

        for irradiance in irradiance_levels:
            key = str(irradiance)
            if key not in measurements:
                continue

            measurement = measurements[key]
            iv_curve = measurement.get("iv_curve", {})
            voltage = iv_curve.get("voltage", [])
            current = iv_curve.get("current", [])

            if not voltage or not current:
                continue

            actual_irradiance = measurement.get("actual_irradiance", irradiance)
            color = self.COLORS.get(key, "#666666")

            fig.add_trace(go.Scatter(
                x=voltage,
                y=current,
                mode='lines+markers',
                name=f'{actual_irradiance:.0f} W/m²',
                line=dict(color=color, width=2),
                marker=dict(size=4),
                hovertemplate='<b>%{fullData.name}</b><br>' +
                              'Voltage: %{x:.2f} V<br>' +
                              'Current: %{y:.3f} A<br>' +
                              '<extra></extra>'
            ))

        fig.update_layout(
            title={
                'text': 'I-V Curves at Low Irradiance Conditions',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'family': 'Arial, sans-serif'}
            },
            xaxis=dict(
                title='Voltage (V)',
                gridcolor='lightgray',
                showgrid=True,
                zeroline=True
            ),
            yaxis=dict(
                title='Current (A)',
                gridcolor='lightgray',
                showgrid=True,
                zeroline=True
            ),
            plot_bgcolor='white',
            hovermode='closest',
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99,
                bgcolor="rgba(255, 255, 255, 0.8)",
                bordercolor="Gray",
                borderwidth=1
            ),
            height=500,
            margin=dict(l=60, r=40, t=80, b=60)
        )

        return fig

    def create_power_curves(
        self,
        measurements: Dict[str, Any],
        irradiance_levels: List[int]
    ) -> go.Figure:
        """
        Create Power-Voltage curves

        Args:
            measurements: Measurement data
            irradiance_levels: List of irradiance levels to plot

        Returns:
            Plotly Figure object
        """
        fig = go.Figure()

        for irradiance in irradiance_levels:
            key = str(irradiance)
            if key not in measurements:
                continue

            measurement = measurements[key]
            iv_curve = measurement.get("iv_curve", {})
            voltage = iv_curve.get("voltage", [])
            current = iv_curve.get("current", [])

            if not voltage or not current:
                continue

            # Calculate power
            power = [v * i for v, i in zip(voltage, current)]

            actual_irradiance = measurement.get("actual_irradiance", irradiance)
            color = self.COLORS.get(key, "#666666")

            fig.add_trace(go.Scatter(
                x=voltage,
                y=power,
                mode='lines+markers',
                name=f'{actual_irradiance:.0f} W/m²',
                line=dict(color=color, width=2),
                marker=dict(size=4),
                hovertemplate='<b>%{fullData.name}</b><br>' +
                              'Voltage: %{x:.2f} V<br>' +
                              'Power: %{y:.3f} W<br>' +
                              '<extra></extra>'
            ))

            # Mark maximum power point
            max_power = max(power)
            max_idx = power.index(max_power)
            max_voltage = voltage[max_idx]

            fig.add_trace(go.Scatter(
                x=[max_voltage],
                y=[max_power],
                mode='markers',
                name=f'MPP ({actual_irradiance:.0f} W/m²)',
                marker=dict(
                    color=color,
                    size=10,
                    symbol='star',
                    line=dict(color='white', width=2)
                ),
                showlegend=False,
                hovertemplate=f'<b>Maximum Power Point</b><br>' +
                              f'{actual_irradiance:.0f} W/m²<br>' +
                              f'Voltage: {max_voltage:.2f} V<br>' +
                              f'Power: {max_power:.3f} W<br>' +
                              '<extra></extra>'
            ))

        fig.update_layout(
            title={
                'text': 'Power-Voltage Curves',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'family': 'Arial, sans-serif'}
            },
            xaxis=dict(
                title='Voltage (V)',
                gridcolor='lightgray',
                showgrid=True
            ),
            yaxis=dict(
                title='Power (W)',
                gridcolor='lightgray',
                showgrid=True
            ),
            plot_bgcolor='white',
            hovermode='closest',
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99,
                bgcolor="rgba(255, 255, 255, 0.8)",
                bordercolor="Gray",
                borderwidth=1
            ),
            height=500,
            margin=dict(l=60, r=40, t=80, b=60)
        )

        return fig

    def create_performance_summary(self, results: Dict[str, Any]) -> go.Figure:
        """
        Create performance summary bar chart

        Args:
            results: Results by irradiance level

        Returns:
            Plotly Figure with subplots
        """
        irradiances = sorted([int(k) for k in results.keys()])

        # Extract data
        pmax_values = [results[str(irr)]["pmax"] for irr in irradiances]
        ff_values = [results[str(irr)]["fill_factor"] * 100 for irr in irradiances]  # Convert to %
        eff_values = [results[str(irr)]["efficiency"] for irr in irradiances]

        # Create subplots
        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=('Maximum Power (W)', 'Fill Factor (%)', 'Efficiency (%)'),
            horizontal_spacing=0.12
        )

        # Colors for bars
        colors = [self.COLORS.get(str(irr), "#666666") for irr in irradiances]

        # Pmax
        fig.add_trace(
            go.Bar(
                x=[f"{irr}" for irr in irradiances],
                y=pmax_values,
                marker_color=colors,
                text=[f"{p:.2f}" for p in pmax_values],
                textposition='outside',
                name='Pmax',
                showlegend=False,
                hovertemplate='<b>%{x} W/m²</b><br>Pmax: %{y:.3f} W<extra></extra>'
            ),
            row=1, col=1
        )

        # Fill Factor
        fig.add_trace(
            go.Bar(
                x=[f"{irr}" for irr in irradiances],
                y=ff_values,
                marker_color=colors,
                text=[f"{ff:.1f}" for ff in ff_values],
                textposition='outside',
                name='FF',
                showlegend=False,
                hovertemplate='<b>%{x} W/m²</b><br>FF: %{y:.2f}%<extra></extra>'
            ),
            row=1, col=2
        )

        # Efficiency
        fig.add_trace(
            go.Bar(
                x=[f"{irr}" for irr in irradiances],
                y=eff_values,
                marker_color=colors,
                text=[f"{eff:.1f}" for eff in eff_values],
                textposition='outside',
                name='Efficiency',
                showlegend=False,
                hovertemplate='<b>%{x} W/m²</b><br>Efficiency: %{y:.2f}%<extra></extra>'
            ),
            row=1, col=3
        )

        # Update axes
        for col in [1, 2, 3]:
            fig.update_xaxes(title_text="Irradiance (W/m²)", row=1, col=col)

        fig.update_layout(
            title={
                'text': 'Performance Summary Across Irradiance Levels',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'family': 'Arial, sans-serif'}
            },
            plot_bgcolor='white',
            height=400,
            margin=dict(l=60, r=40, t=100, b=60)
        )

        return fig

    def create_irradiance_response(self, results: Dict[str, Any]) -> go.Figure:
        """
        Create irradiance response plot (Pmax vs Irradiance)

        Args:
            results: Results by irradiance level

        Returns:
            Plotly Figure object
        """
        irradiances = sorted([int(k) for k in results.keys()])
        pmax_values = [results[str(irr)]["pmax"] for irr in irradiances]

        # Linear fit
        coeffs = np.polyfit(irradiances, pmax_values, 1)
        fit_line = np.polyval(coeffs, irradiances)

        # Calculate R²
        ss_res = np.sum((np.array(pmax_values) - fit_line) ** 2)
        ss_tot = np.sum((np.array(pmax_values) - np.mean(pmax_values)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        fig = go.Figure()

        # Data points
        fig.add_trace(go.Scatter(
            x=irradiances,
            y=pmax_values,
            mode='markers',
            name='Measured',
            marker=dict(
                size=12,
                color='#4ECDC4',
                line=dict(color='white', width=2)
            ),
            hovertemplate='<b>Measured Point</b><br>' +
                          'Irradiance: %{x} W/m²<br>' +
                          'Pmax: %{y:.3f} W<br>' +
                          '<extra></extra>'
        ))

        # Linear fit
        fig.add_trace(go.Scatter(
            x=irradiances,
            y=fit_line,
            mode='lines',
            name=f'Linear Fit (R² = {r_squared:.4f})',
            line=dict(color='#FF6B6B', width=2, dash='dash'),
            hovertemplate='<b>Linear Fit</b><br>' +
                          'Irradiance: %{x} W/m²<br>' +
                          'Predicted Pmax: %{y:.3f} W<br>' +
                          '<extra></extra>'
        ))

        fig.update_layout(
            title={
                'text': 'Module Response to Irradiance',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'family': 'Arial, sans-serif'}
            },
            xaxis=dict(
                title='Irradiance (W/m²)',
                gridcolor='lightgray',
                showgrid=True
            ),
            yaxis=dict(
                title='Maximum Power (W)',
                gridcolor='lightgray',
                showgrid=True
            ),
            plot_bgcolor='white',
            hovermode='closest',
            legend=dict(
                yanchor="bottom",
                y=0.01,
                xanchor="right",
                x=0.99,
                bgcolor="rgba(255, 255, 255, 0.8)",
                bordercolor="Gray",
                borderwidth=1
            ),
            annotations=[
                dict(
                    x=0.02,
                    y=0.98,
                    xref='paper',
                    yref='paper',
                    text=f'Slope: {coeffs[0]:.4f} W/(W/m²)<br>Intercept: {coeffs[1]:.4f} W',
                    showarrow=False,
                    bgcolor='rgba(255, 255, 255, 0.8)',
                    bordercolor='gray',
                    borderwidth=1,
                    borderpad=8,
                    font=dict(size=11)
                )
            ],
            height=500,
            margin=dict(l=60, r=40, t=80, b=60)
        )

        return fig

    def create_fill_factor_comparison(self, results: Dict[str, Any]) -> go.Figure:
        """
        Create fill factor comparison across irradiance levels

        Args:
            results: Results by irradiance level

        Returns:
            Plotly Figure object
        """
        irradiances = sorted([int(k) for k in results.keys()])
        ff_values = [results[str(irr)]["fill_factor"] * 100 for irr in irradiances]  # Convert to %

        colors = [self.COLORS.get(str(irr), "#666666") for irr in irradiances]

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=irradiances,
            y=ff_values,
            mode='lines+markers',
            name='Fill Factor',
            line=dict(color='#45B7D1', width=3),
            marker=dict(
                size=12,
                color=colors,
                line=dict(color='white', width=2)
            ),
            hovertemplate='<b>Fill Factor</b><br>' +
                          'Irradiance: %{x} W/m²<br>' +
                          'Fill Factor: %{y:.2f}%<br>' +
                          '<extra></extra>'
        ))

        # Add mean line
        mean_ff = np.mean(ff_values)
        fig.add_hline(
            y=mean_ff,
            line_dash="dash",
            line_color="gray",
            annotation_text=f"Mean: {mean_ff:.2f}%",
            annotation_position="right"
        )

        fig.update_layout(
            title={
                'text': 'Fill Factor vs Irradiance',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'family': 'Arial, sans-serif'}
            },
            xaxis=dict(
                title='Irradiance (W/m²)',
                gridcolor='lightgray',
                showgrid=True
            ),
            yaxis=dict(
                title='Fill Factor (%)',
                gridcolor='lightgray',
                showgrid=True,
                range=[min(ff_values) * 0.95, max(ff_values) * 1.05]
            ),
            plot_bgcolor='white',
            hovermode='closest',
            height=500,
            margin=dict(l=60, r=40, t=80, b=60)
        )

        return fig
