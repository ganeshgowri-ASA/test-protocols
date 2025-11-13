"""Visualization Utilities for PV Testing Protocols"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum


class ChartThemes(Enum):
    """Predefined chart themes"""
    LIGHT = "plotly"
    DARK = "plotly_dark"
    SCIENTIFIC = "plotly_white"
    PRESENTATION = "presentation"


class PlotlyChartBuilder:
    """Builder for creating standardized Plotly charts"""

    DEFAULT_COLORS = px.colors.qualitative.Set2
    GRID_COLOR = "rgba(128, 128, 128, 0.2)"

    def __init__(self, theme: ChartThemes = ChartThemes.SCIENTIFIC):
        self.theme = theme.value
        self.fig: Optional[go.Figure] = None

    @staticmethod
    def create_iv_curve(voltage: np.ndarray, current: np.ndarray,
                       title: str = "I-V Characteristic Curve",
                       annotations: Optional[Dict[str, Tuple[float, float]]] = None) -> go.Figure:
        """
        Create I-V curve with key points annotated.

        Args:
            voltage: Voltage array (V)
            current: Current array (A)
            title: Chart title
            annotations: Dict of point labels and (V, I) coordinates

        Returns:
            Plotly Figure object
        """
        fig = go.Figure()

        # Main I-V curve
        fig.add_trace(go.Scatter(
            x=voltage,
            y=current,
            mode='lines+markers',
            name='I-V Curve',
            line=dict(color='#2E86DE', width=3),
            marker=dict(size=6)
        ))

        # Add annotations for key points
        if annotations:
            for label, (v, i) in annotations.items():
                fig.add_annotation(
                    x=v, y=i,
                    text=f"{label}<br>V={v:.2f}V, I={i:.2f}A",
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor="#E74C3C",
                    bgcolor="white",
                    bordercolor="#E74C3C",
                    borderwidth=2
                )

        fig.update_layout(
            title=title,
            xaxis_title="Voltage (V)",
            yaxis_title="Current (A)",
            template="plotly_white",
            hovermode='x unified',
            showlegend=True
        )

        return fig

    @staticmethod
    def create_pv_curve(voltage: np.ndarray, power: np.ndarray,
                       title: str = "P-V Characteristic Curve",
                       pmax: Optional[float] = None,
                       vmp: Optional[float] = None) -> go.Figure:
        """
        Create P-V curve with maximum power point.

        Args:
            voltage: Voltage array (V)
            power: Power array (W)
            title: Chart title
            pmax: Maximum power (W)
            vmp: Voltage at maximum power (V)

        Returns:
            Plotly Figure object
        """
        fig = go.Figure()

        # Main P-V curve
        fig.add_trace(go.Scatter(
            x=voltage,
            y=power,
            mode='lines+markers',
            name='P-V Curve',
            line=dict(color='#27AE60', width=3),
            marker=dict(size=6),
            fill='tozeroy',
            fillcolor='rgba(39, 174, 96, 0.2)'
        ))

        # Add MPP marker
        if pmax is not None and vmp is not None:
            fig.add_trace(go.Scatter(
                x=[vmp],
                y=[pmax],
                mode='markers',
                name='MPP',
                marker=dict(
                    size=15,
                    color='#E74C3C',
                    symbol='star',
                    line=dict(color='white', width=2)
                )
            ))

            fig.add_annotation(
                x=vmp, y=pmax,
                text=f"Pmax={pmax:.2f}W<br>Vmp={vmp:.2f}V",
                showarrow=True,
                arrowhead=2,
                yshift=20
            )

        fig.update_layout(
            title=title,
            xaxis_title="Voltage (V)",
            yaxis_title="Power (W)",
            template="plotly_white",
            hovermode='x unified',
            showlegend=True
        )

        return fig

    @staticmethod
    def create_time_series(df: pd.DataFrame, x_col: str, y_cols: List[str],
                          title: str = "Time Series",
                          y_label: str = "Value") -> go.Figure:
        """
        Create multi-line time series chart.

        Args:
            df: DataFrame containing data
            x_col: Column name for x-axis (time)
            y_cols: List of column names for y-axis
            title: Chart title
            y_label: Y-axis label

        Returns:
            Plotly Figure object
        """
        fig = go.Figure()

        colors = PlotlyChartBuilder.DEFAULT_COLORS

        for idx, col in enumerate(y_cols):
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df[col],
                mode='lines+markers',
                name=col,
                line=dict(color=colors[idx % len(colors)], width=2),
                marker=dict(size=4)
            ))

        fig.update_layout(
            title=title,
            xaxis_title=x_col,
            yaxis_title=y_label,
            template="plotly_white",
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        return fig

    @staticmethod
    def create_temperature_profile(time: np.ndarray, temperature: np.ndarray,
                                   setpoints: Optional[List[Tuple[float, float, float]]] = None,
                                   title: str = "Temperature Profile") -> go.Figure:
        """
        Create temperature vs time chart with optional setpoint zones.

        Args:
            time: Time array (minutes)
            temperature: Temperature array (°C)
            setpoints: List of (start_time, end_time, temp) tuples for setpoint zones
            title: Chart title

        Returns:
            Plotly Figure object
        """
        fig = go.Figure()

        # Actual temperature
        fig.add_trace(go.Scatter(
            x=time,
            y=temperature,
            mode='lines',
            name='Actual Temperature',
            line=dict(color='#E74C3C', width=3)
        ))

        # Setpoint zones
        if setpoints:
            for idx, (t_start, t_end, temp) in enumerate(setpoints):
                fig.add_shape(
                    type="rect",
                    x0=t_start, x1=t_end,
                    y0=temp-2, y1=temp+2,
                    fillcolor="rgba(46, 134, 222, 0.2)",
                    line=dict(width=0),
                    layer="below"
                )
                fig.add_trace(go.Scatter(
                    x=[t_start, t_end],
                    y=[temp, temp],
                    mode='lines',
                    name=f'Setpoint Zone {idx+1}',
                    line=dict(color='#2E86DE', width=2, dash='dash')
                ))

        fig.update_layout(
            title=title,
            xaxis_title="Time (minutes)",
            yaxis_title="Temperature (°C)",
            template="plotly_white",
            hovermode='x unified',
            showlegend=True
        )

        return fig

    @staticmethod
    def create_histogram(data: np.ndarray, title: str = "Distribution",
                        x_label: str = "Value", bins: int = 30,
                        show_stats: bool = True) -> go.Figure:
        """
        Create histogram with statistical annotations.

        Args:
            data: Data array
            title: Chart title
            x_label: X-axis label
            bins: Number of bins
            show_stats: Whether to show mean/std annotations

        Returns:
            Plotly Figure object
        """
        fig = go.Figure()

        fig.add_trace(go.Histogram(
            x=data,
            nbinsx=bins,
            name='Distribution',
            marker_color='#3498DB',
            opacity=0.75
        ))

        if show_stats:
            mean_val = np.mean(data)
            std_val = np.std(data)

            # Add mean line
            fig.add_vline(
                x=mean_val,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Mean: {mean_val:.2f}",
                annotation_position="top"
            )

            # Add std range
            fig.add_vrect(
                x0=mean_val - std_val,
                x1=mean_val + std_val,
                fillcolor="green",
                opacity=0.15,
                layer="below",
                line_width=0,
                annotation_text="±1σ",
                annotation_position="top left"
            )

        fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title="Frequency",
            template="plotly_white",
            showlegend=False
        )

        return fig

    @staticmethod
    def create_box_plot(df: pd.DataFrame, columns: List[str],
                       title: str = "Box Plot Comparison") -> go.Figure:
        """
        Create box plot for comparing distributions.

        Args:
            df: DataFrame containing data
            columns: List of columns to compare
            title: Chart title

        Returns:
            Plotly Figure object
        """
        fig = go.Figure()

        colors = PlotlyChartBuilder.DEFAULT_COLORS

        for idx, col in enumerate(columns):
            fig.add_trace(go.Box(
                y=df[col],
                name=col,
                marker_color=colors[idx % len(colors)],
                boxmean='sd'  # Show mean and std deviation
            ))

        fig.update_layout(
            title=title,
            yaxis_title="Value",
            template="plotly_white",
            showlegend=True
        )

        return fig

    @staticmethod
    def create_heatmap(data: np.ndarray, x_labels: List[str], y_labels: List[str],
                      title: str = "Heatmap",
                      colorscale: str = "RdYlGn") -> go.Figure:
        """
        Create heatmap visualization.

        Args:
            data: 2D numpy array
            x_labels: Labels for x-axis
            y_labels: Labels for y-axis
            title: Chart title
            colorscale: Plotly colorscale name

        Returns:
            Plotly Figure object
        """
        fig = go.Figure(data=go.Heatmap(
            z=data,
            x=x_labels,
            y=y_labels,
            colorscale=colorscale,
            text=data,
            texttemplate='%{text:.2f}',
            textfont={"size": 10},
            colorbar=dict(title="Value")
        ))

        fig.update_layout(
            title=title,
            template="plotly_white"
        )

        return fig

    @staticmethod
    def create_comparison_chart(baseline: Dict[str, float],
                               test: Dict[str, float],
                               title: str = "Baseline vs Test Comparison") -> go.Figure:
        """
        Create bar chart comparing baseline and test measurements.

        Args:
            baseline: Dict of parameter: value for baseline
            test: Dict of parameter: value for test
            title: Chart title

        Returns:
            Plotly Figure object
        """
        parameters = list(baseline.keys())

        fig = go.Figure()

        fig.add_trace(go.Bar(
            name='Baseline',
            x=parameters,
            y=[baseline[p] for p in parameters],
            marker_color='#3498DB'
        ))

        fig.add_trace(go.Bar(
            name='Test',
            x=parameters,
            y=[test[p] for p in parameters],
            marker_color='#E74C3C'
        ))

        fig.update_layout(
            title=title,
            xaxis_title="Parameter",
            yaxis_title="Value",
            barmode='group',
            template="plotly_white",
            showlegend=True
        )

        return fig

    @staticmethod
    def create_degradation_curve(time: np.ndarray, power: np.ndarray,
                                 title: str = "Power Degradation Over Time",
                                 fit_line: bool = True) -> go.Figure:
        """
        Create degradation curve with optional linear fit.

        Args:
            time: Time array (hours or cycles)
            power: Normalized power array (%)
            title: Chart title
            fit_line: Whether to add linear regression fit

        Returns:
            Plotly Figure object
        """
        fig = go.Figure()

        # Actual data points
        fig.add_trace(go.Scatter(
            x=time,
            y=power,
            mode='markers',
            name='Measured Data',
            marker=dict(size=8, color='#3498DB')
        ))

        # Linear fit
        if fit_line:
            coeffs = np.polyfit(time, power, 1)
            fit_y = np.polyval(coeffs, time)

            fig.add_trace(go.Scatter(
                x=time,
                y=fit_y,
                mode='lines',
                name=f'Linear Fit (slope={coeffs[0]:.4f}%/hr)',
                line=dict(color='#E74C3C', width=2, dash='dash')
            ))

            # Calculate degradation rate
            degradation_rate = abs(coeffs[0])
            fig.add_annotation(
                xref="paper", yref="paper",
                x=0.95, y=0.95,
                text=f"Degradation Rate: {degradation_rate:.4f}%/hr",
                showarrow=False,
                bgcolor="white",
                bordercolor="black",
                borderwidth=1
            )

        fig.update_layout(
            title=title,
            xaxis_title="Time (hours)",
            yaxis_title="Normalized Power (%)",
            template="plotly_white",
            hovermode='x unified',
            showlegend=True
        )

        return fig

    @staticmethod
    def create_dashboard(figures: List[go.Figure],
                        titles: List[str],
                        rows: int,
                        cols: int) -> go.Figure:
        """
        Create multi-panel dashboard from multiple figures.

        Args:
            figures: List of Plotly figures
            titles: List of subplot titles
            rows: Number of rows
            cols: Number of columns

        Returns:
            Combined Plotly Figure object
        """
        fig = make_subplots(
            rows=rows,
            cols=cols,
            subplot_titles=titles,
            vertical_spacing=0.12,
            horizontal_spacing=0.10
        )

        for idx, figure in enumerate(figures):
            row = idx // cols + 1
            col = idx % cols + 1

            for trace in figure.data:
                fig.add_trace(trace, row=row, col=col)

        fig.update_layout(
            height=300 * rows,
            template="plotly_white",
            showlegend=True
        )

        return fig
