"""Charting functions for test data visualization."""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Any, Optional
import numpy as np


def create_iv_curve_plot(
    voltage: List[float],
    current: List[float],
    label: str = "I-V Curve",
    title: str = "Current-Voltage Characteristic"
) -> go.Figure:
    """Create I-V curve plot.

    Args:
        voltage: Voltage values (V)
        current: Current values (A)
        label: Curve label
        title: Plot title

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=voltage,
        y=current,
        mode='lines+markers',
        name=label,
        line=dict(width=2),
        marker=dict(size=6)
    ))

    fig.update_layout(
        title=title,
        xaxis_title="Voltage (V)",
        yaxis_title="Current (A)",
        hovermode='x unified',
        template='plotly_white'
    )

    return fig


def create_iv_comparison_plot(
    pre_test_data: Dict[str, List[float]],
    post_test_data: Dict[str, List[float]],
    title: str = "Pre-test vs Post-test I-V Curves"
) -> go.Figure:
    """Create comparison plot of pre and post I-V curves.

    Args:
        pre_test_data: Dict with 'voltage' and 'current' lists
        post_test_data: Dict with 'voltage' and 'current' lists
        title: Plot title

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    # Pre-test curve
    fig.add_trace(go.Scatter(
        x=pre_test_data['voltage'],
        y=pre_test_data['current'],
        mode='lines+markers',
        name='Pre-test',
        line=dict(width=2, color='blue'),
        marker=dict(size=6)
    ))

    # Post-test curve
    fig.add_trace(go.Scatter(
        x=post_test_data['voltage'],
        y=post_test_data['current'],
        mode='lines+markers',
        name='Post-test',
        line=dict(width=2, color='red'),
        marker=dict(size=6)
    ))

    fig.update_layout(
        title=title,
        xaxis_title="Voltage (V)",
        yaxis_title="Current (A)",
        hovermode='x unified',
        template='plotly_white',
        legend=dict(x=0.7, y=0.95)
    )

    return fig


def create_power_comparison_chart(
    pre_test_power: float,
    post_test_power: float,
    sample_labels: Optional[List[str]] = None,
    title: str = "Pre-test vs Post-test Power Comparison"
) -> go.Figure:
    """Create bar chart comparing pre and post test power.

    Args:
        pre_test_power: Pre-test power value(s)
        post_test_power: Post-test power value(s)
        sample_labels: Optional sample labels
        title: Plot title

    Returns:
        Plotly figure
    """
    # Handle single values or lists
    if not isinstance(pre_test_power, list):
        pre_test_power = [pre_test_power]
    if not isinstance(post_test_power, list):
        post_test_power = [post_test_power]

    if sample_labels is None:
        sample_labels = [f"Sample {i+1}" for i in range(len(pre_test_power))]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=sample_labels,
        y=pre_test_power,
        name='Pre-test',
        marker_color='blue'
    ))

    fig.add_trace(go.Bar(
        x=sample_labels,
        y=post_test_power,
        name='Post-test',
        marker_color='red'
    ))

    fig.update_layout(
        title=title,
        xaxis_title="Sample",
        yaxis_title="Power (W)",
        barmode='group',
        template='plotly_white',
        legend=dict(x=0.7, y=0.95)
    )

    return fig


def create_degradation_chart(
    parameters: Dict[str, float],
    limits: Optional[Dict[str, float]] = None,
    title: str = "Parameter Degradation"
) -> go.Figure:
    """Create bar chart showing parameter degradation.

    Args:
        parameters: Dict of parameter names and degradation percentages
        limits: Optional dict of parameter names and limit values
        title: Plot title

    Returns:
        Plotly figure
    """
    param_names = list(parameters.keys())
    degradation_values = list(parameters.values())

    # Color bars based on whether they exceed limits
    colors = []
    if limits:
        for param, value in parameters.items():
            if param in limits and abs(value) > limits[param]:
                colors.append('red')
            else:
                colors.append('green')
    else:
        colors = ['blue'] * len(param_names)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=param_names,
        y=degradation_values,
        marker_color=colors,
        text=[f"{v:.2f}%" for v in degradation_values],
        textposition='outside'
    ))

    # Add limit lines if provided
    if limits:
        for param, limit in limits.items():
            if param in param_names:
                idx = param_names.index(param)
                fig.add_shape(
                    type="line",
                    x0=idx - 0.4,
                    x1=idx + 0.4,
                    y0=limit,
                    y1=limit,
                    line=dict(color="orange", width=2, dash="dash")
                )

    fig.update_layout(
        title=title,
        xaxis_title="Parameter",
        yaxis_title="Degradation (%)",
        template='plotly_white',
        showlegend=False
    )

    return fig


def create_psd_plot(
    frequencies: List[float],
    psd_values: List[float],
    target_psd: Optional[Dict[float, float]] = None,
    title: str = "Power Spectral Density"
) -> go.Figure:
    """Create PSD plot for vibration data.

    Args:
        frequencies: Frequency values (Hz)
        psd_values: PSD values (g²/Hz)
        target_psd: Optional target PSD profile
        title: Plot title

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    # Measured PSD
    fig.add_trace(go.Scatter(
        x=frequencies,
        y=psd_values,
        mode='lines',
        name='Measured',
        line=dict(width=2, color='blue')
    ))

    # Target PSD if provided
    if target_psd:
        target_freq = list(target_psd.keys())
        target_vals = list(target_psd.values())

        fig.add_trace(go.Scatter(
            x=target_freq,
            y=target_vals,
            mode='lines+markers',
            name='Target',
            line=dict(width=2, color='red', dash='dash'),
            marker=dict(size=8)
        ))

    fig.update_layout(
        title=title,
        xaxis_title="Frequency (Hz)",
        yaxis_title="PSD (g²/Hz)",
        xaxis_type="log",
        yaxis_type="log",
        hovermode='x unified',
        template='plotly_white',
        legend=dict(x=0.7, y=0.95)
    )

    return fig


def create_time_series_plot(
    timestamps: List[float],
    values: List[float],
    ylabel: str = "Value",
    title: str = "Time Series Data"
) -> go.Figure:
    """Create time series plot.

    Args:
        timestamps: Time values (seconds or datetime)
        values: Measured values
        ylabel: Y-axis label
        title: Plot title

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=timestamps,
        y=values,
        mode='lines',
        name=ylabel,
        line=dict(width=1)
    ))

    fig.update_layout(
        title=title,
        xaxis_title="Time",
        yaxis_title=ylabel,
        hovermode='x unified',
        template='plotly_white'
    )

    return fig


def create_acceleration_time_history(
    time: List[float],
    accel_x: List[float],
    accel_y: List[float],
    accel_z: List[float],
    title: str = "Acceleration Time History"
) -> go.Figure:
    """Create multi-axis acceleration time history plot.

    Args:
        time: Time values (seconds)
        accel_x: X-axis acceleration (g)
        accel_y: Y-axis acceleration (g)
        accel_z: Z-axis acceleration (g)
        title: Plot title

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=time,
        y=accel_x,
        mode='lines',
        name='X-axis',
        line=dict(width=1)
    ))

    fig.add_trace(go.Scatter(
        x=time,
        y=accel_y,
        mode='lines',
        name='Y-axis',
        line=dict(width=1)
    ))

    fig.add_trace(go.Scatter(
        x=time,
        y=accel_z,
        mode='lines',
        name='Z-axis',
        line=dict(width=1)
    ))

    fig.update_layout(
        title=title,
        xaxis_title="Time (s)",
        yaxis_title="Acceleration (g)",
        hovermode='x unified',
        template='plotly_white',
        legend=dict(x=0.02, y=0.98)
    )

    return fig


def create_pass_fail_summary(
    criteria_results: Dict[str, str],
    title: str = "Pass/Fail Criteria Summary"
) -> go.Figure:
    """Create pass/fail summary visualization.

    Args:
        criteria_results: Dict mapping criterion names to status
        title: Plot title

    Returns:
        Plotly figure
    """
    criteria_names = list(criteria_results.keys())
    statuses = list(criteria_results.values())

    # Map status to numeric values for plotting
    status_values = []
    colors = []

    for status in statuses:
        if status.lower() == 'pass':
            status_values.append(1)
            colors.append('green')
        elif status.lower() == 'fail':
            status_values.append(0)
            colors.append('red')
        else:
            status_values.append(0.5)
            colors.append('orange')

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=criteria_names,
        x=status_values,
        orientation='h',
        marker_color=colors,
        text=statuses,
        textposition='inside'
    ))

    fig.update_layout(
        title=title,
        xaxis_title="Status",
        yaxis_title="Criterion",
        xaxis=dict(
            tickvals=[0, 0.5, 1],
            ticktext=['FAIL', 'CONDITIONAL', 'PASS']
        ),
        template='plotly_white',
        showlegend=False,
        height=max(400, len(criteria_names) * 40)
    )

    return fig


def create_dashboard_layout(
    figures: Dict[str, go.Figure],
    title: str = "Test Results Dashboard"
) -> go.Figure:
    """Create dashboard with multiple plots.

    Args:
        figures: Dict mapping subplot titles to figures
        title: Dashboard title

    Returns:
        Plotly figure with subplots
    """
    n_plots = len(figures)
    rows = (n_plots + 1) // 2
    cols = 2 if n_plots > 1 else 1

    fig = make_subplots(
        rows=rows,
        cols=cols,
        subplot_titles=list(figures.keys()),
        vertical_spacing=0.1,
        horizontal_spacing=0.1
    )

    for idx, (subplot_title, subplot_fig) in enumerate(figures.items()):
        row = (idx // cols) + 1
        col = (idx % cols) + 1

        for trace in subplot_fig.data:
            fig.add_trace(trace, row=row, col=col)

    fig.update_layout(
        title_text=title,
        showlegend=True,
        template='plotly_white',
        height=400 * rows
    )

    return fig
