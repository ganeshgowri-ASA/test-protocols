"""Chart components for data visualization."""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import List, Dict, Any


def create_leakage_current_chart(
    elapsed_time: List[float],
    leakage_current: List[float],
    warning_threshold: float = 5.0,
    critical_threshold: float = 10.0
) -> go.Figure:
    """
    Create leakage current vs time chart.

    Args:
        elapsed_time: Time points in hours
        leakage_current: Leakage current values in mA
        warning_threshold: Warning threshold in mA
        critical_threshold: Critical threshold in mA

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    # Add leakage current line
    fig.add_trace(go.Scatter(
        x=elapsed_time,
        y=leakage_current,
        mode='lines+markers',
        name='Leakage Current',
        line=dict(color='royalblue', width=2),
        marker=dict(size=4)
    ))

    # Add warning threshold
    fig.add_hline(
        y=warning_threshold,
        line_dash="dash",
        line_color="orange",
        annotation_text=f"Warning ({warning_threshold} mA)",
        annotation_position="right"
    )

    # Add critical threshold
    fig.add_hline(
        y=critical_threshold,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Critical ({critical_threshold} mA)",
        annotation_position="right"
    )

    fig.update_layout(
        title="Leakage Current vs Time",
        xaxis_title="Elapsed Time (hours)",
        yaxis_title="Leakage Current (mA)",
        hovermode='x unified',
        template="plotly_white"
    )

    return fig


def create_power_degradation_chart(
    elapsed_time: List[float],
    power_degradation: List[float],
    warning_threshold: float = 3.0,
    critical_threshold: float = 5.0
) -> go.Figure:
    """
    Create power degradation vs time chart.

    Args:
        elapsed_time: Time points in hours
        power_degradation: Power degradation values in percent
        warning_threshold: Warning threshold in percent
        critical_threshold: Critical threshold in percent

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    # Add power degradation line
    fig.add_trace(go.Scatter(
        x=elapsed_time,
        y=power_degradation,
        mode='lines+markers',
        name='Power Degradation',
        line=dict(color='crimson', width=2),
        marker=dict(size=4),
        fill='tozeroy',
        fillcolor='rgba(220, 20, 60, 0.1)'
    ))

    # Add warning threshold
    fig.add_hline(
        y=warning_threshold,
        line_dash="dash",
        line_color="orange",
        annotation_text=f"Warning ({warning_threshold}%)",
        annotation_position="right"
    )

    # Add critical threshold
    fig.add_hline(
        y=critical_threshold,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Critical ({critical_threshold}%)",
        annotation_position="right"
    )

    fig.update_layout(
        title="Power Degradation vs Time",
        xaxis_title="Elapsed Time (hours)",
        yaxis_title="Power Degradation (%)",
        hovermode='x unified',
        template="plotly_white"
    )

    return fig


def create_environmental_conditions_chart(
    elapsed_time: List[float],
    temperature: List[float],
    humidity: List[float]
) -> go.Figure:
    """
    Create environmental conditions chart.

    Args:
        elapsed_time: Time points in hours
        temperature: Temperature values in Celsius
        humidity: Humidity values in percent

    Returns:
        Plotly figure
    """
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Temperature", "Relative Humidity"),
        vertical_spacing=0.15
    )

    # Temperature
    fig.add_trace(
        go.Scatter(
            x=elapsed_time,
            y=temperature,
            mode='lines',
            name='Temperature',
            line=dict(color='darkorange', width=2)
        ),
        row=1, col=1
    )

    # Humidity
    fig.add_trace(
        go.Scatter(
            x=elapsed_time,
            y=humidity,
            mode='lines',
            name='Humidity',
            line=dict(color='dodgerblue', width=2)
        ),
        row=2, col=1
    )

    fig.update_xaxes(title_text="Elapsed Time (hours)", row=2, col=1)
    fig.update_yaxes(title_text="Temperature (°C)", row=1, col=1)
    fig.update_yaxes(title_text="Humidity (%)", row=2, col=1)

    fig.update_layout(
        title="Environmental Conditions During Test",
        height=600,
        showlegend=False,
        template="plotly_white"
    )

    return fig


def create_qc_summary_chart(qc_checks: List[Dict[str, Any]]) -> go.Figure:
    """
    Create QC summary bar chart.

    Args:
        qc_checks: List of QC check results

    Returns:
        Plotly figure
    """
    if not qc_checks:
        return go.Figure()

    df = pd.DataFrame(qc_checks)

    # Create color map
    color_map = {
        "pass": "green",
        "warning": "orange",
        "fail": "red"
    }
    colors = [color_map.get(status, "gray") for status in df["status"]]

    fig = go.Figure(data=[
        go.Bar(
            x=df["check"],
            y=df["value"],
            marker_color=colors,
            text=[f"{v:.2f}" for v in df["value"]],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Value: %{y:.2f}<br>Threshold: %{customdata:.2f}<extra></extra>',
            customdata=df["threshold"]
        )
    ])

    # Add threshold lines
    for i, row in df.iterrows():
        fig.add_hline(
            y=row["threshold"],
            line_dash="dash",
            line_color="red",
            opacity=0.5
        )

    fig.update_layout(
        title="QC Check Results",
        xaxis_title="Check Name",
        yaxis_title="Measured Value",
        template="plotly_white",
        showlegend=False
    )

    return fig


def create_measurement_distribution(measurements_df: pd.DataFrame) -> go.Figure:
    """
    Create distribution plots for key measurements.

    Args:
        measurements_df: DataFrame with measurement data

    Returns:
        Plotly figure
    """
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Leakage Current Distribution", "Power Degradation Distribution")
    )

    # Leakage current histogram
    fig.add_trace(
        go.Histogram(
            x=measurements_df["leakage_current"],
            name="Leakage Current",
            marker_color="royalblue",
            nbinsx=30
        ),
        row=1, col=1
    )

    # Power degradation histogram
    if "power_degradation" in measurements_df.columns:
        fig.add_trace(
            go.Histogram(
                x=measurements_df["power_degradation"],
                name="Power Degradation",
                marker_color="crimson",
                nbinsx=30
            ),
            row=1, col=2
        )

    fig.update_xaxes(title_text="Leakage Current (mA)", row=1, col=1)
    fig.update_xaxes(title_text="Power Degradation (%)", row=1, col=2)
    fig.update_yaxes(title_text="Frequency", row=1, col=1)
    fig.update_yaxes(title_text="Frequency", row=1, col=2)

    fig.update_layout(
        title="Measurement Distributions",
        showlegend=False,
        template="plotly_white",
        height=400
    )

    return fig
