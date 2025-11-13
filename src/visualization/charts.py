"""Chart generation for test protocol visualization."""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional


class ChartGenerator:
    """Generates interactive charts for protocol data visualization."""

    def __init__(self):
        """Initialize chart generator."""
        self.default_template = "plotly_white"
        self.color_palette = px.colors.qualitative.Set2

    def create_iv_curves(
        self,
        iv_curves_data: List[Dict[str, Any]],
        title: str = "I-V Curves at All Irradiance Levels"
    ) -> go.Figure:
        """Create I-V curve plot.

        Args:
            iv_curves_data: List of I-V curve data, each with irradiance_level and points
            title: Chart title

        Returns:
            Plotly Figure object
        """
        fig = go.Figure()

        # Sort by irradiance level
        iv_curves_data = sorted(iv_curves_data, key=lambda x: x['irradiance_level'])

        for idx, curve_data in enumerate(iv_curves_data):
            irr_level = curve_data['irradiance_level']
            points = curve_data['points']

            voltages = [p['voltage'] for p in points]
            currents = [p['current'] for p in points]

            color = self.color_palette[idx % len(self.color_palette)]

            fig.add_trace(go.Scatter(
                x=voltages,
                y=currents,
                mode='lines+markers',
                name=f"{irr_level} W/m²",
                line=dict(width=2, color=color),
                marker=dict(size=4)
            ))

        fig.update_layout(
            title=title,
            xaxis_title="Voltage (V)",
            yaxis_title="Current (A)",
            template=self.default_template,
            hovermode='x unified',
            legend=dict(
                title="Irradiance",
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99
            ),
            width=900,
            height=600
        )

        fig.update_xaxis(showgrid=True, gridwidth=1, gridcolor='lightgray')
        fig.update_yaxis(showgrid=True, gridwidth=1, gridcolor='lightgray')

        return fig

    def create_pv_curves(
        self,
        iv_curves_data: List[Dict[str, Any]],
        title: str = "P-V Curves at All Irradiance Levels"
    ) -> go.Figure:
        """Create P-V curve plot.

        Args:
            iv_curves_data: List of I-V curve data
            title: Chart title

        Returns:
            Plotly Figure object
        """
        fig = go.Figure()

        iv_curves_data = sorted(iv_curves_data, key=lambda x: x['irradiance_level'])

        for idx, curve_data in enumerate(iv_curves_data):
            irr_level = curve_data['irradiance_level']
            points = curve_data['points']

            voltages = [p['voltage'] for p in points]
            powers = [p.get('power', p['voltage'] * p['current']) for p in points]

            color = self.color_palette[idx % len(self.color_palette)]

            fig.add_trace(go.Scatter(
                x=voltages,
                y=powers,
                mode='lines+markers',
                name=f"{irr_level} W/m²",
                line=dict(width=2, color=color),
                marker=dict(size=4)
            ))

        fig.update_layout(
            title=title,
            xaxis_title="Voltage (V)",
            yaxis_title="Power (W)",
            template=self.default_template,
            hovermode='x unified',
            legend=dict(
                title="Irradiance",
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99
            ),
            width=900,
            height=600
        )

        fig.update_xaxis(showgrid=True, gridwidth=1, gridcolor='lightgray')
        fig.update_yaxis(showgrid=True, gridwidth=1, gridcolor='lightgray')

        return fig

    def create_power_vs_irradiance(
        self,
        analysis_results: List[Dict[str, Any]],
        title: str = "Maximum Power vs Irradiance"
    ) -> go.Figure:
        """Create scatter plot of power vs irradiance with trendline.

        Args:
            analysis_results: List of per-irradiance analysis results
            title: Chart title

        Returns:
            Plotly Figure object
        """
        irradiances = [r['irradiance_mean'] for r in analysis_results
                      if 'irradiance_mean' in r and 'pmax' in r]
        powers = [r['pmax'] for r in analysis_results
                 if 'irradiance_mean' in r and 'pmax' in r]

        if not irradiances:
            return go.Figure()

        # Calculate trendline
        z = np.polyfit(irradiances, powers, 1)
        p = np.poly1d(z)
        x_trend = np.linspace(min(irradiances), max(irradiances), 100)
        y_trend = p(x_trend)

        # Calculate R²
        residuals = np.array(powers) - p(np.array(irradiances))
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((np.array(powers) - np.mean(powers))**2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

        fig = go.Figure()

        # Scatter points
        fig.add_trace(go.Scatter(
            x=irradiances,
            y=powers,
            mode='markers',
            name='Measurements',
            marker=dict(size=12, color='royalblue'),
            text=[f"{r['irradiance_level']} W/m²" for r in analysis_results
                  if 'irradiance_mean' in r and 'pmax' in r],
            hovertemplate='<b>%{text}</b><br>Irradiance: %{x:.1f} W/m²<br>Power: %{y:.2f} W<extra></extra>'
        ))

        # Trendline
        fig.add_trace(go.Scatter(
            x=x_trend,
            y=y_trend,
            mode='lines',
            name=f'Linear Fit<br>y = {z[0]:.4f}x + {z[1]:.2f}<br>R² = {r_squared:.4f}',
            line=dict(color='red', width=2, dash='dash')
        ))

        fig.update_layout(
            title=title,
            xaxis_title="Irradiance (W/m²)",
            yaxis_title="Maximum Power (W)",
            template=self.default_template,
            hovermode='closest',
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            ),
            width=900,
            height=600
        )

        fig.update_xaxis(showgrid=True, gridwidth=1, gridcolor='lightgray')
        fig.update_yaxis(showgrid=True, gridwidth=1, gridcolor='lightgray')

        return fig

    def create_efficiency_vs_irradiance(
        self,
        analysis_results: List[Dict[str, Any]],
        title: str = "Efficiency at Different Irradiance Levels"
    ) -> go.Figure:
        """Create bar chart of efficiency vs irradiance.

        Args:
            analysis_results: List of per-irradiance analysis results
            title: Chart title

        Returns:
            Plotly Figure object
        """
        irradiances = [r['irradiance_level'] for r in analysis_results
                      if 'efficiency' in r]
        efficiencies = [r['efficiency'] for r in analysis_results
                       if 'efficiency' in r]

        if not irradiances:
            return go.Figure()

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=[f"{irr}" for irr in irradiances],
            y=efficiencies,
            marker=dict(
                color=efficiencies,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Efficiency (%)")
            ),
            text=[f"{eff:.2f}%" for eff in efficiencies],
            textposition='outside',
            hovertemplate='<b>%{x} W/m²</b><br>Efficiency: %{y:.2f}%<extra></extra>'
        ))

        fig.update_layout(
            title=title,
            xaxis_title="Irradiance (W/m²)",
            yaxis_title="Efficiency (%)",
            template=self.default_template,
            width=900,
            height=600
        )

        fig.update_xaxis(showgrid=False)
        fig.update_yaxis(showgrid=True, gridwidth=1, gridcolor='lightgray')

        return fig

    def create_fill_factor_vs_irradiance(
        self,
        analysis_results: List[Dict[str, Any]],
        title: str = "Fill Factor vs Irradiance"
    ) -> go.Figure:
        """Create line plot of fill factor vs irradiance.

        Args:
            analysis_results: List of per-irradiance analysis results
            title: Chart title

        Returns:
            Plotly Figure object
        """
        irradiances = [r['irradiance_level'] for r in analysis_results
                      if 'fill_factor' in r]
        fill_factors = [r['fill_factor'] for r in analysis_results
                       if 'fill_factor' in r]

        if not irradiances:
            return go.Figure()

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=irradiances,
            y=fill_factors,
            mode='lines+markers',
            name='Fill Factor',
            line=dict(color='green', width=3),
            marker=dict(size=10, color='darkgreen'),
            hovertemplate='<b>%{x} W/m²</b><br>Fill Factor: %{y:.2f}%<extra></extra>'
        ))

        fig.update_layout(
            title=title,
            xaxis_title="Irradiance (W/m²)",
            yaxis_title="Fill Factor (%)",
            template=self.default_template,
            width=900,
            height=600
        )

        fig.update_xaxis(showgrid=True, gridwidth=1, gridcolor='lightgray')
        fig.update_yaxis(showgrid=True, gridwidth=1, gridcolor='lightgray', range=[0, 100])

        return fig

    def create_uniformity_heatmap(
        self,
        measurements: List[Dict[str, Any]],
        irradiance_level: float,
        title: Optional[str] = None
    ) -> go.Figure:
        """Create heatmap of spatial irradiance distribution.

        Args:
            measurements: List of measurement data with position_x, position_y, irradiance
            irradiance_level: Target irradiance level for filtering
            title: Chart title

        Returns:
            Plotly Figure object
        """
        # Filter measurements for this irradiance level
        filtered = [m for m in measurements
                   if m.get('target_irradiance') == irradiance_level]

        if not filtered:
            return go.Figure()

        # Create grid
        positions_x = [m['position_x'] for m in filtered if 'position_x' in m]
        positions_y = [m['position_y'] for m in filtered if 'position_y' in m]
        irradiances = [m['irradiance'] for m in filtered if 'irradiance' in m]

        if not positions_x or not positions_y:
            return go.Figure()

        # Create 2D grid
        x_unique = sorted(set(positions_x))
        y_unique = sorted(set(positions_y))

        # Initialize grid with NaN
        grid = np.full((len(y_unique), len(x_unique)), np.nan)

        # Fill grid with data
        for m in filtered:
            if 'position_x' in m and 'position_y' in m and 'irradiance' in m:
                x_idx = x_unique.index(m['position_x'])
                y_idx = y_unique.index(m['position_y'])
                grid[y_idx, x_idx] = m['irradiance']

        if title is None:
            title = f"Irradiance Uniformity - {irradiance_level} W/m²"

        fig = go.Figure(data=go.Heatmap(
            z=grid,
            x=x_unique,
            y=y_unique,
            colorscale='RdYlBu_r',
            colorbar=dict(title="Irradiance<br>(W/m²)"),
            hovertemplate='X: %{x}<br>Y: %{y}<br>Irradiance: %{z:.1f} W/m²<extra></extra>'
        ))

        fig.update_layout(
            title=title,
            xaxis_title="X Position",
            yaxis_title="Y Position",
            template=self.default_template,
            width=800,
            height=700
        )

        fig.update_xaxis(showgrid=False)
        fig.update_yaxis(showgrid=False, autorange='reversed')

        return fig

    def create_parameters_table(
        self,
        analysis_results: List[Dict[str, Any]]
    ) -> pd.DataFrame:
        """Create summary table of key parameters.

        Args:
            analysis_results: List of per-irradiance analysis results

        Returns:
            Pandas DataFrame
        """
        table_data = []

        for result in analysis_results:
            row = {
                'Irradiance (W/m²)': result.get('irradiance_level', '-'),
                'Pmax (W)': f"{result.get('pmax', 0):.2f}",
                'Voc (V)': f"{result.get('voc', 0):.2f}",
                'Isc (A)': f"{result.get('isc', 0):.3f}",
                'Vmp (V)': f"{result.get('vmp', 0):.2f}",
                'Imp (A)': f"{result.get('imp', 0):.3f}",
                'Fill Factor (%)': f"{result.get('fill_factor', 0):.2f}",
                'Efficiency (%)': f"{result.get('efficiency', 0):.2f}"
            }
            table_data.append(row)

        return pd.DataFrame(table_data)

    def create_combined_dashboard(
        self,
        analysis_results: Dict[str, Any],
        measurements: List[Dict[str, Any]],
        iv_curves_data: Optional[List[Dict[str, Any]]] = None
    ) -> go.Figure:
        """Create combined dashboard with multiple subplots.

        Args:
            analysis_results: Complete analysis results
            measurements: Raw measurement data
            iv_curves_data: Optional I-V curve data

        Returns:
            Plotly Figure with subplots
        """
        per_irradiance = analysis_results.get('per_irradiance', [])

        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Maximum Power vs Irradiance',
                'Efficiency vs Irradiance',
                'Fill Factor vs Irradiance',
                'Performance Summary'
            ),
            specs=[
                [{"type": "scatter"}, {"type": "bar"}],
                [{"type": "scatter"}, {"type": "table"}]
            ]
        )

        # 1. Power vs Irradiance
        irradiances = [r['irradiance_mean'] for r in per_irradiance
                      if 'irradiance_mean' in r and 'pmax' in r]
        powers = [r['pmax'] for r in per_irradiance
                 if 'irradiance_mean' in r and 'pmax' in r]

        if irradiances:
            fig.add_trace(
                go.Scatter(x=irradiances, y=powers, mode='markers+lines',
                          marker=dict(size=10), name='Power'),
                row=1, col=1
            )

        # 2. Efficiency bar chart
        irr_levels = [r['irradiance_level'] for r in per_irradiance if 'efficiency' in r]
        efficiencies = [r['efficiency'] for r in per_irradiance if 'efficiency' in r]

        if irr_levels:
            fig.add_trace(
                go.Bar(x=[str(i) for i in irr_levels], y=efficiencies,
                      marker_color='lightblue', name='Efficiency'),
                row=1, col=2
            )

        # 3. Fill Factor
        ff_irr = [r['irradiance_level'] for r in per_irradiance if 'fill_factor' in r]
        fill_factors = [r['fill_factor'] for r in per_irradiance if 'fill_factor' in r]

        if ff_irr:
            fig.add_trace(
                go.Scatter(x=ff_irr, y=fill_factors, mode='markers+lines',
                          marker=dict(size=10), line=dict(color='green'), name='FF'),
                row=2, col=1
            )

        # 4. Summary table
        table_df = self.create_parameters_table(per_irradiance)
        if not table_df.empty:
            fig.add_trace(
                go.Table(
                    header=dict(values=list(table_df.columns),
                              fill_color='paleturquoise',
                              align='left'),
                    cells=dict(values=[table_df[col] for col in table_df.columns],
                             fill_color='lavender',
                             align='left')
                ),
                row=2, col=2
            )

        fig.update_layout(
            height=1000,
            showlegend=False,
            title_text="PERF-002 Performance Dashboard"
        )

        return fig
