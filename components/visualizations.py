"""
Unified Visualization Components
================================
Reusable visualization components for test data and analytics.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import streamlit as st


def create_iv_curve(
    voltage: List[float],
    current: List[float],
    title: str = "I-V Curve",
    show_mpp: bool = True
) -> go.Figure:
    """
    Create I-V (Current-Voltage) curve

    Args:
        voltage: List of voltage values
        current: List of current values
        title: Chart title
        show_mpp: Whether to highlight Maximum Power Point

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    # I-V curve
    fig.add_trace(go.Scatter(
        x=voltage,
        y=current,
        mode='lines+markers',
        name='I-V Curve',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=6)
    ))

    if show_mpp and len(voltage) > 0 and len(current) > 0:
        # Calculate power and find MPP
        power = [v * i for v, i in zip(voltage, current)]
        mpp_idx = power.index(max(power))

        # Mark MPP
        fig.add_trace(go.Scatter(
            x=[voltage[mpp_idx]],
            y=[current[mpp_idx]],
            mode='markers',
            name='MPP',
            marker=dict(size=15, color='red', symbol='star')
        ))

        # Add annotation
        fig.add_annotation(
            x=voltage[mpp_idx],
            y=current[mpp_idx],
            text=f"MPP<br>V={voltage[mpp_idx]:.2f}V<br>I={current[mpp_idx]:.2f}A",
            showarrow=True,
            arrowhead=2
        )

    fig.update_layout(
        title=title,
        xaxis_title="Voltage (V)",
        yaxis_title="Current (A)",
        hovermode='x unified',
        height=500
    )

    return fig


def create_pv_curve(
    voltage: List[float],
    power: List[float],
    title: str = "P-V Curve",
    show_mpp: bool = True
) -> go.Figure:
    """
    Create P-V (Power-Voltage) curve

    Args:
        voltage: List of voltage values
        power: List of power values
        title: Chart title
        show_mpp: Whether to highlight Maximum Power Point

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    # P-V curve
    fig.add_trace(go.Scatter(
        x=voltage,
        y=power,
        mode='lines+markers',
        name='P-V Curve',
        line=dict(color='#2ca02c', width=3),
        marker=dict(size=6),
        fill='tozeroy',
        fillcolor='rgba(44, 160, 44, 0.1)'
    ))

    if show_mpp and len(voltage) > 0 and len(power) > 0:
        # Find MPP
        mpp_idx = power.index(max(power))

        # Mark MPP
        fig.add_trace(go.Scatter(
            x=[voltage[mpp_idx]],
            y=[power[mpp_idx]],
            mode='markers',
            name='MPP',
            marker=dict(size=15, color='red', symbol='star')
        ))

        # Add annotation
        fig.add_annotation(
            x=voltage[mpp_idx],
            y=power[mpp_idx],
            text=f"Pmax={power[mpp_idx]:.2f}W<br>Vmp={voltage[mpp_idx]:.2f}V",
            showarrow=True,
            arrowhead=2
        )

    fig.update_layout(
        title=title,
        xaxis_title="Voltage (V)",
        yaxis_title="Power (W)",
        hovermode='x unified',
        height=500
    )

    return fig


def create_time_series_chart(
    timestamps: List,
    values: List[float],
    title: str,
    y_label: str,
    setpoint: float = None,
    tolerance_upper: float = None,
    tolerance_lower: float = None
) -> go.Figure:
    """
    Create time series chart with optional setpoint and tolerance bands

    Args:
        timestamps: List of timestamps
        values: List of measurement values
        title: Chart title
        y_label: Y-axis label
        setpoint: Target setpoint value
        tolerance_upper: Upper tolerance limit
        tolerance_lower: Lower tolerance limit

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    # Actual values
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=values,
        mode='lines+markers',
        name='Measured',
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=4)
    ))

    # Setpoint line
    if setpoint is not None:
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=[setpoint] * len(timestamps),
            mode='lines',
            name='Setpoint',
            line=dict(color='green', width=2, dash='dash')
        ))

    # Tolerance bands
    if tolerance_upper is not None and tolerance_lower is not None:
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=[tolerance_upper] * len(timestamps),
            mode='lines',
            name='Upper Limit',
            line=dict(color='red', width=1, dash='dot'),
            showlegend=True
        ))

        fig.add_trace(go.Scatter(
            x=timestamps,
            y=[tolerance_lower] * len(timestamps),
            mode='lines',
            name='Lower Limit',
            line=dict(color='red', width=1, dash='dot'),
            fill='tonexty',
            fillcolor='rgba(255, 0, 0, 0.1)',
            showlegend=True
        ))

    fig.update_layout(
        title=title,
        xaxis_title="Time",
        yaxis_title=y_label,
        hovermode='x unified',
        height=400
    )

    return fig


def create_degradation_chart(
    measurements: List[Dict[str, Any]],
    title: str = "Power Degradation Over Time"
) -> go.Figure:
    """
    Create degradation chart showing power loss over time

    Args:
        measurements: List of measurement dictionaries with 'timestamp' and 'power'
        title: Chart title

    Returns:
        Plotly figure
    """
    df = pd.DataFrame(measurements)

    if df.empty:
        return go.Figure()

    # Calculate degradation percentage
    initial_power = df['power'].iloc[0]
    df['degradation_%'] = ((df['power'] - initial_power) / initial_power) * 100

    fig = go.Figure()

    # Power over time
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['power'],
        mode='lines+markers',
        name='Power',
        yaxis='y',
        line=dict(color='#1f77b4', width=2)
    ))

    # Degradation percentage
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['degradation_%'],
        mode='lines+markers',
        name='Degradation %',
        yaxis='y2',
        line=dict(color='#ff7f0e', width=2)
    ))

    fig.update_layout(
        title=title,
        xaxis_title="Time",
        yaxis=dict(
            title="Power (W)",
            titlefont=dict(color='#1f77b4'),
            tickfont=dict(color='#1f77b4')
        ),
        yaxis2=dict(
            title="Degradation (%)",
            titlefont=dict(color='#ff7f0e'),
            tickfont=dict(color='#ff7f0e'),
            anchor='x',
            overlaying='y',
            side='right'
        ),
        hovermode='x unified',
        height=500
    )

    return fig


def create_heatmap(
    data: pd.DataFrame,
    title: str,
    x_label: str,
    y_label: str,
    colorscale: str = "RdYlGn"
) -> go.Figure:
    """
    Create heatmap visualization

    Args:
        data: DataFrame with data to plot
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        colorscale: Color scale to use

    Returns:
        Plotly figure
    """
    fig = go.Figure(data=go.Heatmap(
        z=data.values,
        x=data.columns,
        y=data.index,
        colorscale=colorscale,
        text=data.values,
        texttemplate='%{text:.2f}',
        textfont={"size": 10},
        colorbar=dict(title="Value")
    ))

    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        height=500
    )

    return fig


def create_comparison_chart(
    categories: List[str],
    datasets: List[Dict[str, Any]],
    title: str,
    y_label: str
) -> go.Figure:
    """
    Create comparison bar chart for multiple datasets

    Args:
        categories: List of category names
        datasets: List of dataset dictionaries with 'name' and 'values'
        title: Chart title
        y_label: Y-axis label

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    for dataset in datasets:
        fig.add_trace(go.Bar(
            name=dataset['name'],
            x=categories,
            y=dataset['values'],
            text=dataset['values'],
            texttemplate='%{text:.2f}',
            textposition='outside'
        ))

    fig.update_layout(
        title=title,
        xaxis_title="Category",
        yaxis_title=y_label,
        barmode='group',
        height=500
    )

    return fig


def create_gauge_chart(
    value: float,
    title: str,
    min_value: float = 0,
    max_value: float = 100,
    threshold: float = None,
    units: str = ""
) -> go.Figure:
    """
    Create gauge chart for single value display

    Args:
        value: Current value
        title: Chart title
        min_value: Minimum value on gauge
        max_value: Maximum value on gauge
        threshold: Threshold value to highlight
        units: Units to display

    Returns:
        Plotly figure
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        number={'suffix': f" {units}"},
        gauge={
            'axis': {'range': [min_value, max_value]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [min_value, (max_value - min_value) * 0.6], 'color': "lightgray"},
                {'range': [(max_value - min_value) * 0.6, (max_value - min_value) * 0.8], 'color': "gray"},
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': threshold if threshold else max_value * 0.9
            }
        }
    ))

    fig.update_layout(height=300)

    return fig


def create_box_plot(
    data: pd.DataFrame,
    y_column: str,
    x_column: str = None,
    title: str = "Distribution Analysis"
) -> go.Figure:
    """
    Create box plot for statistical distribution

    Args:
        data: DataFrame with data
        y_column: Column name for y-axis values
        x_column: Column name for x-axis categories (optional)
        title: Chart title

    Returns:
        Plotly figure
    """
    if x_column:
        fig = px.box(data, x=x_column, y=y_column, title=title)
    else:
        fig = px.box(data, y=y_column, title=title)

    fig.update_layout(height=500)

    return fig


def create_3d_surface_plot(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray,
    title: str,
    x_label: str,
    y_label: str,
    z_label: str
) -> go.Figure:
    """
    Create 3D surface plot

    Args:
        x: X-axis values
        y: Y-axis values
        z: Z-axis values (2D array)
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        z_label: Z-axis label

    Returns:
        Plotly figure
    """
    fig = go.Figure(data=[go.Surface(z=z, x=x, y=y)])

    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title=x_label,
            yaxis_title=y_label,
            zaxis_title=z_label
        ),
        height=600
    )

    return fig


def render_test_summary_card(
    title: str,
    value: Any,
    unit: str = "",
    status: str = "info",
    delta: Any = None,
    delta_label: str = ""
):
    """
    Render a summary card for test results

    Args:
        title: Card title
        value: Main value to display
        unit: Unit of measurement
        status: Status type (success, warning, error, info)
        delta: Change/delta value
        delta_label: Label for delta
    """
    # Color mapping
    color_map = {
        'success': '#28a745',
        'warning': '#ffc107',
        'error': '#dc3545',
        'info': '#17a2b8'
    }

    color = color_map.get(status, '#17a2b8')

    st.markdown(f"""
    <div style='
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid {color};
    '>
        <div style='color: #666; font-size: 0.875rem; margin-bottom: 0.5rem;'>{title}</div>
        <div style='font-size: 2rem; font-weight: bold; color: {color};'>
            {value} <span style='font-size: 1rem; font-weight: normal;'>{unit}</span>
        </div>
        {f"<div style='color: #666; font-size: 0.875rem; margin-top: 0.5rem;'>{delta_label}: {delta}</div>" if delta is not None else ""}
    </div>
    """, unsafe_allow_html=True)
