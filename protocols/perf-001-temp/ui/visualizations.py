"""
PERF-001 Visualization Module
Advanced Plotly visualizations for temperature performance data
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class PlotConfig:
    """Configuration for plot styling"""
    template: str = "plotly_white"
    color_scheme: List[str] = None
    font_family: str = "Arial, sans-serif"
    title_font_size: int = 18
    axis_font_size: int = 12

    def __post_init__(self):
        if self.color_scheme is None:
            self.color_scheme = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
                                 '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']


class PERF001Visualizer:
    """
    Advanced visualization generator for PERF-001 test data
    """

    def __init__(self, config: Optional[PlotConfig] = None):
        self.config = config or PlotConfig()

    def plot_temp_power_regression(
        self,
        temperatures: List[float],
        pmax_values: List[float],
        show_confidence: bool = True
    ) -> go.Figure:
        """
        Create temperature vs power plot with linear regression and confidence intervals

        Args:
            temperatures: List of temperature values in Celsius
            pmax_values: List of maximum power values in Watts
            show_confidence: Whether to show 95% confidence intervals

        Returns:
            Plotly Figure object
        """
        temps = np.array(temperatures)
        pmax = np.array(pmax_values)

        # Linear regression
        z = np.polyfit(temps, pmax, 1)
        p = np.poly1d(z)

        # Calculate R²
        residuals = pmax - p(temps)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((pmax - np.mean(pmax))**2)
        r_squared = 1 - (ss_res / ss_tot)

        # Create figure
        fig = go.Figure()

        # Scatter plot of measurements
        fig.add_trace(go.Scatter(
            x=temps,
            y=pmax,
            mode='markers',
            name='Measurements',
            marker=dict(
                size=12,
                color=self.config.color_scheme[0],
                symbol='circle',
                line=dict(width=2, color='white')
            ),
            hovertemplate='<b>T:</b> %{x:.1f}°C<br><b>Pmax:</b> %{y:.2f} W<extra></extra>'
        ))

        # Linear fit line
        temp_fit = np.linspace(min(temps), max(temps), 100)
        pmax_fit = p(temp_fit)

        fig.add_trace(go.Scatter(
            x=temp_fit,
            y=pmax_fit,
            mode='lines',
            name=f'Linear Fit (R²={r_squared:.4f})',
            line=dict(width=3, color=self.config.color_scheme[1], dash='solid'),
            hovertemplate='<b>Fitted:</b> %{y:.2f} W<extra></extra>'
        ))

        # Confidence intervals
        if show_confidence:
            from scipy import stats

            # Calculate prediction intervals
            n = len(temps)
            t_val = stats.t.ppf(0.975, n - 2)
            std_err = np.sqrt(ss_res / (n - 2))
            x_mean = np.mean(temps)
            sxx = np.sum((temps - x_mean)**2)

            # Standard error of prediction
            se_pred = std_err * np.sqrt(1 + 1/n + (temp_fit - x_mean)**2 / sxx)
            ci_upper = pmax_fit + t_val * se_pred
            ci_lower = pmax_fit - t_val * se_pred

            fig.add_trace(go.Scatter(
                x=temp_fit,
                y=ci_upper,
                mode='lines',
                name='95% CI',
                line=dict(width=0),
                showlegend=False,
                hoverinfo='skip'
            ))

            fig.add_trace(go.Scatter(
                x=temp_fit,
                y=ci_lower,
                mode='lines',
                name='95% CI',
                line=dict(width=0),
                fillcolor='rgba(31, 119, 180, 0.2)',
                fill='tonexty',
                showlegend=True,
                hoverinfo='skip'
            ))

        # Layout
        fig.update_layout(
            title=dict(
                text='Temperature vs. Maximum Power<br><sub>Linear Regression Analysis</sub>',
                font=dict(size=self.config.title_font_size)
            ),
            xaxis=dict(
                title='Temperature [°C]',
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray',
                zeroline=False
            ),
            yaxis=dict(
                title='Maximum Power [W]',
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray',
                zeroline=False
            ),
            hovermode='x unified',
            template=self.config.template,
            font=dict(family=self.config.font_family),
            legend=dict(
                x=0.02,
                y=0.98,
                bgcolor='rgba(255, 255, 255, 0.8)',
                bordercolor='gray',
                borderwidth=1
            ),
            height=600
        )

        # Add equation annotation
        slope, intercept = z
        equation_text = f'Pmax = {slope:.3f}·T + {intercept:.2f}<br>R² = {r_squared:.4f}'
        fig.add_annotation(
            xref='paper', yref='paper',
            x=0.98, y=0.02,
            text=equation_text,
            showarrow=False,
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='gray',
            borderwidth=1,
            font=dict(size=11),
            align='right'
        )

        return fig

    def plot_all_parameters_grid(
        self,
        temperatures: List[float],
        pmax: List[float],
        voc: List[float],
        isc: List[float],
        fill_factors: List[float],
        efficiency: Optional[List[float]] = None
    ) -> go.Figure:
        """
        Create comprehensive grid plot of all temperature-dependent parameters

        Args:
            temperatures: Temperature values
            pmax: Maximum power values
            voc: Open circuit voltage values
            isc: Short circuit current values
            fill_factors: Fill factor values
            efficiency: Optional efficiency values

        Returns:
            Plotly Figure object with subplots
        """
        # Determine number of rows
        n_params = 5 if efficiency else 4
        n_rows = 2 if n_params <= 4 else 3
        n_cols = 2

        # Create subplots
        subplot_titles = ['Maximum Power (Pmax)', 'Open Circuit Voltage (Voc)',
                          'Short Circuit Current (Isc)', 'Fill Factor (FF)']
        if efficiency:
            subplot_titles.append('Efficiency (η)')

        fig = make_subplots(
            rows=n_rows, cols=n_cols,
            subplot_titles=subplot_titles,
            vertical_spacing=0.12,
            horizontal_spacing=0.10
        )

        # Helper function to add parameter plot
        def add_param_plot(row, col, y_data, y_label, color_idx):
            # Scatter with line
            fig.add_trace(
                go.Scatter(
                    x=temperatures,
                    y=y_data,
                    mode='markers+lines',
                    marker=dict(size=10, color=self.config.color_scheme[color_idx]),
                    line=dict(width=2),
                    name=y_label,
                    showlegend=False
                ),
                row=row, col=col
            )

            # Linear regression
            z = np.polyfit(temperatures, y_data, 1)
            p = np.poly1d(z)
            temp_fit = np.linspace(min(temperatures), max(temperatures), 50)
            y_fit = p(temp_fit)

            # R²
            residuals = np.array(y_data) - p(np.array(temperatures))
            ss_res = np.sum(residuals**2)
            ss_tot = np.sum((np.array(y_data) - np.mean(y_data))**2)
            r_squared = 1 - (ss_res / ss_tot)

            fig.add_trace(
                go.Scatter(
                    x=temp_fit,
                    y=y_fit,
                    mode='lines',
                    line=dict(width=2, dash='dash', color=self.config.color_scheme[color_idx]),
                    opacity=0.5,
                    showlegend=False,
                    hovertemplate=f'R² = {r_squared:.4f}<extra></extra>'
                ),
                row=row, col=col
            )

        # Add all parameter plots
        add_param_plot(1, 1, pmax, 'Pmax', 0)
        add_param_plot(1, 2, voc, 'Voc', 1)
        add_param_plot(2, 1, isc, 'Isc', 2)
        add_param_plot(2, 2, fill_factors, 'FF', 3)

        if efficiency:
            add_param_plot(3, 1, efficiency, 'Efficiency', 4)

        # Update axes labels
        fig.update_xaxes(title_text="Temperature [°C]", row=1, col=1)
        fig.update_xaxes(title_text="Temperature [°C]", row=1, col=2)
        fig.update_xaxes(title_text="Temperature [°C]", row=2, col=1)
        fig.update_xaxes(title_text="Temperature [°C]", row=2, col=2)

        fig.update_yaxes(title_text="Power [W]", row=1, col=1)
        fig.update_yaxes(title_text="Voltage [V]", row=1, col=2)
        fig.update_yaxes(title_text="Current [A]", row=2, col=1)
        fig.update_yaxes(title_text="Fill Factor", row=2, col=2)

        if efficiency:
            fig.update_xaxes(title_text="Temperature [°C]", row=3, col=1)
            fig.update_yaxes(title_text="Efficiency [%]", row=3, col=1)

        # Global layout
        fig.update_layout(
            title=dict(
                text='Temperature Dependencies of PV Module Parameters',
                font=dict(size=self.config.title_font_size)
            ),
            height=800 if efficiency else 700,
            template=self.config.template,
            font=dict(family=self.config.font_family)
        )

        return fig

    def plot_normalized_comparison(
        self,
        temperatures: List[float],
        pmax: List[float],
        voc: List[float],
        isc: List[float],
        reference_temp: float = 25.0
    ) -> go.Figure:
        """
        Create normalized comparison plot (all parameters on 0-100% scale)

        Args:
            temperatures: Temperature values
            pmax: Maximum power values
            voc: Voltage values
            isc: Current values
            reference_temp: Reference temperature for normalization

        Returns:
            Plotly Figure object
        """
        temps = np.array(temperatures)

        # Find reference values (closest to reference temperature)
        ref_idx = np.argmin(np.abs(temps - reference_temp))

        # Normalize to reference (as percentage)
        pmax_norm = (np.array(pmax) / pmax[ref_idx]) * 100
        voc_norm = (np.array(voc) / voc[ref_idx]) * 100
        isc_norm = (np.array(isc) / isc[ref_idx]) * 100

        fig = go.Figure()

        # Pmax
        fig.add_trace(go.Scatter(
            x=temps,
            y=pmax_norm,
            mode='markers+lines',
            name='Pmax',
            marker=dict(size=10, symbol='circle'),
            line=dict(width=3),
            hovertemplate='<b>Pmax:</b> %{y:.2f}%<extra></extra>'
        ))

        # Voc
        fig.add_trace(go.Scatter(
            x=temps,
            y=voc_norm,
            mode='markers+lines',
            name='Voc',
            marker=dict(size=10, symbol='square'),
            line=dict(width=3),
            hovertemplate='<b>Voc:</b> %{y:.2f}%<extra></extra>'
        ))

        # Isc
        fig.add_trace(go.Scatter(
            x=temps,
            y=isc_norm,
            mode='markers+lines',
            name='Isc',
            marker=dict(size=10, symbol='diamond'),
            line=dict(width=3),
            hovertemplate='<b>Isc:</b> %{y:.2f}%<extra></extra>'
        ))

        # Reference line at 100%
        fig.add_hline(
            y=100,
            line_dash="dash",
            line_color="gray",
            annotation_text=f"Reference ({reference_temp}°C)",
            annotation_position="right"
        )

        fig.update_layout(
            title=dict(
                text=f'Normalized Parameter Comparison<br><sub>Reference: {reference_temp}°C</sub>',
                font=dict(size=self.config.title_font_size)
            ),
            xaxis=dict(
                title='Temperature [°C]',
                showgrid=True
            ),
            yaxis=dict(
                title='Normalized Value [%]',
                showgrid=True
            ),
            hovermode='x unified',
            template=self.config.template,
            legend=dict(
                x=0.02,
                y=0.98,
                bgcolor='rgba(255, 255, 255, 0.8)',
                bordercolor='gray',
                borderwidth=1
            ),
            height=600
        )

        return fig

    def plot_coefficient_comparison(
        self,
        coef_pmax: float,
        coef_voc: float,
        coef_isc: float,
        industry_benchmarks: Optional[Dict[str, tuple]] = None
    ) -> go.Figure:
        """
        Create bar chart comparing calculated coefficients with industry benchmarks

        Args:
            coef_pmax: Pmax temperature coefficient (%/°C)
            coef_voc: Voc temperature coefficient (%/°C)
            coef_isc: Isc temperature coefficient (%/°C)
            industry_benchmarks: Dict with typical ranges for each parameter

        Returns:
            Plotly Figure object
        """
        if industry_benchmarks is None:
            # Typical values for crystalline silicon
            industry_benchmarks = {
                'Pmax': (-0.50, -0.35),  # %/°C
                'Voc': (-0.35, -0.25),   # %/°C
                'Isc': (0.03, 0.08)      # %/°C
            }

        parameters = ['Pmax', 'Voc', 'Isc']
        measured_values = [coef_pmax, coef_voc, coef_isc]
        benchmark_min = [industry_benchmarks['Pmax'][0],
                        industry_benchmarks['Voc'][0],
                        industry_benchmarks['Isc'][0]]
        benchmark_max = [industry_benchmarks['Pmax'][1],
                        industry_benchmarks['Voc'][1],
                        industry_benchmarks['Isc'][1]]

        fig = go.Figure()

        # Measured values
        fig.add_trace(go.Bar(
            x=parameters,
            y=measured_values,
            name='Measured',
            marker_color=self.config.color_scheme[0],
            text=[f'{v:.3f}' for v in measured_values],
            textposition='outside',
            hovertemplate='<b>%{x}:</b> %{y:.4f} %/°C<extra></extra>'
        ))

        # Benchmark ranges
        for i, param in enumerate(parameters):
            fig.add_shape(
                type="rect",
                x0=i - 0.3,
                x1=i + 0.3,
                y0=benchmark_min[i],
                y1=benchmark_max[i],
                fillcolor="rgba(128, 128, 128, 0.2)",
                line=dict(color="gray", width=2, dash="dash"),
                layer="below"
            )

        fig.update_layout(
            title=dict(
                text='Temperature Coefficients vs. Industry Benchmarks<br><sub>Typical range for crystalline silicon shown in gray</sub>',
                font=dict(size=self.config.title_font_size)
            ),
            xaxis=dict(title='Parameter'),
            yaxis=dict(title='Temperature Coefficient [%/°C]'),
            template=self.config.template,
            height=500,
            showlegend=True
        )

        return fig

    def plot_3d_surface(
        self,
        temperatures: List[float],
        irradiances: List[float],
        power_matrix: np.ndarray
    ) -> go.Figure:
        """
        Create 3D surface plot for temperature and irradiance effects

        Args:
            temperatures: Temperature values
            irradiances: Irradiance values
            power_matrix: 2D array of power values

        Returns:
            Plotly Figure object with 3D surface
        """
        fig = go.Figure(data=[go.Surface(
            x=temperatures,
            y=irradiances,
            z=power_matrix,
            colorscale='Viridis',
            colorbar=dict(title='Power [W]')
        )])

        fig.update_layout(
            title='3D Performance Surface: Temperature and Irradiance Effects',
            scene=dict(
                xaxis_title='Temperature [°C]',
                yaxis_title='Irradiance [W/m²]',
                zaxis_title='Power [W]'
            ),
            height=700,
            template=self.config.template
        )

        return fig

    def create_dashboard(
        self,
        test_data: Dict[str, Any]
    ) -> go.Figure:
        """
        Create comprehensive dashboard with multiple visualizations

        Args:
            test_data: Complete test data dictionary

        Returns:
            Plotly Figure object with dashboard layout
        """
        measurements = test_data.get('measurements', [])

        if not measurements:
            return go.Figure()

        temps = [m['temperature'] for m in measurements]
        pmax = [m['pmax'] for m in measurements]
        voc = [m['voc'] for m in measurements]
        isc = [m['isc'] for m in measurements]
        ff = [m['fill_factor'] for m in measurements]

        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Temperature-Power Curve',
                'Normalized Comparison',
                'All Parameters',
                'Quality Metrics'
            ),
            specs=[
                [{"type": "scatter"}, {"type": "scatter"}],
                [{"type": "scatter"}, {"type": "indicator"}]
            ],
            vertical_spacing=0.15,
            horizontal_spacing=0.12
        )

        # 1. Temperature-Power curve (row 1, col 1)
        fig.add_trace(
            go.Scatter(x=temps, y=pmax, mode='markers+lines',
                      marker=dict(size=10), name='Pmax'),
            row=1, col=1
        )

        # 2. Normalized comparison (row 1, col 2)
        ref_idx = len(temps) // 2
        pmax_norm = (np.array(pmax) / pmax[ref_idx]) * 100
        fig.add_trace(
            go.Scatter(x=temps, y=pmax_norm, mode='markers+lines',
                      name='Normalized Pmax'),
            row=1, col=2
        )

        # 3. All parameters mini grid (row 2, col 1)
        fig.add_trace(
            go.Scatter(x=temps, y=voc, mode='markers+lines',
                      name='Voc', marker=dict(size=6)),
            row=2, col=1
        )

        # 4. Quality indicator (row 2, col 2)
        quality = test_data.get('quality_checks', {})
        r_squared = test_data.get('calculated_results', {}).get(
            'temp_coefficient_pmax', {}
        ).get('r_squared', 0)

        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=r_squared,
                title={'text': "R² Value"},
                gauge={
                    'axis': {'range': [0, 1]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 0.90], 'color': "lightgray"},
                        {'range': [0.90, 0.95], 'color': "yellow"},
                        {'range': [0.95, 1.0], 'color': "lightgreen"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 0.95
                    }
                }
            ),
            row=2, col=2
        )

        fig.update_layout(
            title_text="PERF-001 Test Dashboard",
            height=800,
            showlegend=True,
            template=self.config.template
        )

        return fig
