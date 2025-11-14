"""Chart utility functions for Streamlit UI."""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Any, Dict, List, Optional


def create_time_series_chart(
    df: pd.DataFrame,
    metric_name: str,
    unit: str = ""
) -> go.Figure:
    """Create a time series chart for a metric.

    Args:
        df: DataFrame with timestamp and metric_value columns
        metric_name: Name of the metric
        unit: Unit of measurement

    Returns:
        Plotly Figure object
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['metric_value'],
        mode='lines+markers',
        name=metric_name,
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=4)
    ))

    # Add mean line
    mean_value = df['metric_value'].mean()
    fig.add_hline(
        y=mean_value,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Mean: {mean_value:.2f}",
        annotation_position="right"
    )

    fig.update_layout(
        title=f"{metric_name} over Time",
        xaxis_title="Time",
        yaxis_title=f"{metric_name} ({unit})" if unit else metric_name,
        hovermode='x unified',
        template='plotly_white',
        height=400
    )

    return fig


def create_distribution_chart(
    df: pd.DataFrame,
    metric_name: str
) -> go.Figure:
    """Create a distribution histogram for a metric.

    Args:
        df: DataFrame with metric_value column
        metric_name: Name of the metric

    Returns:
        Plotly Figure object
    """
    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=df['metric_value'],
        name=metric_name,
        marker=dict(color='#1f77b4'),
        opacity=0.7
    ))

    fig.update_layout(
        title=f"{metric_name} Distribution",
        xaxis_title="Value",
        yaxis_title="Frequency",
        template='plotly_white',
        height=300,
        showlegend=False
    )

    return fig


def create_scatter_plot(
    df: pd.DataFrame,
    x_metric: str,
    y_metric: str,
    color_metric: Optional[str] = None
) -> go.Figure:
    """Create a scatter plot comparing two metrics.

    Args:
        df: DataFrame with metric data
        x_metric: Metric for x-axis
        y_metric: Metric for y-axis
        color_metric: Optional metric for color coding

    Returns:
        Plotly Figure object
    """
    if color_metric:
        fig = px.scatter(
            df,
            x=x_metric,
            y=y_metric,
            color=color_metric,
            title=f"{y_metric} vs {x_metric}"
        )
    else:
        fig = px.scatter(
            df,
            x=x_metric,
            y=y_metric,
            title=f"{y_metric} vs {x_metric}"
        )

    fig.update_layout(
        template='plotly_white',
        height=400
    )

    return fig


def create_performance_gauge(
    value: float,
    title: str,
    min_value: float = 0,
    max_value: float = 100,
    threshold: float = 80
) -> go.Figure:
    """Create a gauge chart for performance metrics.

    Args:
        value: Current value
        title: Gauge title
        min_value: Minimum value
        max_value: Maximum value
        threshold: Threshold for pass/fail

    Returns:
        Plotly Figure object
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={'text': title},
        delta={'reference': threshold},
        gauge={
            'axis': {'range': [min_value, max_value]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [min_value, threshold * 0.8], 'color': "lightgray"},
                {'range': [threshold * 0.8, threshold], 'color': "gray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': threshold
            }
        }
    ))

    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    return fig
