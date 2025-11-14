"""HOT-001 Visualization Components

Plotly-based visualizations for Hot Spot Endurance Test.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from datetime import datetime
from typing import List, Dict, Tuple, Optional


def create_iv_curve_comparison(
    initial_voltage: np.ndarray,
    initial_current: np.ndarray,
    final_voltage: np.ndarray,
    final_current: np.ndarray,
    initial_pmax: float,
    final_pmax: float
) -> go.Figure:
    """Create I-V curve comparison chart

    Args:
        initial_voltage: Initial voltage array (V)
        initial_current: Initial current array (A)
        final_voltage: Final voltage array (V)
        final_current: Final current array (A)
        initial_pmax: Initial maximum power (W)
        final_pmax: Final maximum power (W)

    Returns:
        Plotly figure object
    """
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('I-V Curves', 'Power Curves'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}]]
    )

    # Calculate power curves
    initial_power = initial_voltage * initial_current
    final_power = final_voltage * final_current

    # I-V curves
    fig.add_trace(
        go.Scatter(
            x=initial_voltage,
            y=initial_current,
            mode='lines',
            name='Initial I-V',
            line=dict(color='blue', width=2)
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=final_voltage,
            y=final_current,
            mode='lines',
            name='Final I-V',
            line=dict(color='red', width=2, dash='dash')
        ),
        row=1, col=1
    )

    # Power curves
    fig.add_trace(
        go.Scatter(
            x=initial_voltage,
            y=initial_power,
            mode='lines',
            name=f'Initial P (Pmax={initial_pmax:.2f}W)',
            line=dict(color='blue', width=2)
        ),
        row=1, col=2
    )

    fig.add_trace(
        go.Scatter(
            x=final_voltage,
            y=final_power,
            mode='lines',
            name=f'Final P (Pmax={final_pmax:.2f}W)',
            line=dict(color='red', width=2, dash='dash')
        ),
        row=1, col=2
    )

    # Update axes
    fig.update_xaxes(title_text="Voltage (V)", row=1, col=1)
    fig.update_yaxes(title_text="Current (A)", row=1, col=1)
    fig.update_xaxes(title_text="Voltage (V)", row=1, col=2)
    fig.update_yaxes(title_text="Power (W)", row=1, col=2)

    fig.update_layout(
        title="I-V and Power Curve Comparison",
        height=400,
        showlegend=True,
        hovermode='x unified'
    )

    return fig


def create_temperature_profile(
    hot_spot_tests: List[Dict]
) -> go.Figure:
    """Create temperature profile chart for all hot spot tests

    Args:
        hot_spot_tests: List of hot spot test data dictionaries

    Returns:
        Plotly figure object
    """
    fig = go.Figure()

    colors = ['red', 'orange', 'darkred']

    for idx, test in enumerate(hot_spot_tests):
        if 'temperature_profile' not in test or not test['temperature_profile']:
            continue

        timestamps = [point[0] for point in test['temperature_profile']]
        temperatures = [point[1] for point in test['temperature_profile']]

        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=temperatures,
                mode='lines',
                name=f"Cell {test['cell_id']}",
                line=dict(color=colors[idx % len(colors)], width=2)
            )
        )

    # Add target temperature line
    if hot_spot_tests and hot_spot_tests[0].get('target_temperature'):
        target_temp = hot_spot_tests[0]['target_temperature']
        fig.add_hline(
            y=target_temp,
            line_dash="dash",
            line_color="green",
            annotation_text=f"Target: {target_temp}°C"
        )

    # Add safety limit line
    fig.add_hline(
        y=120,
        line_dash="dash",
        line_color="darkred",
        annotation_text="Safety Limit: 120°C"
    )

    fig.update_layout(
        title="Hot Spot Temperature Profiles",
        xaxis_title="Time",
        yaxis_title="Temperature (°C)",
        height=500,
        showlegend=True,
        hovermode='x unified'
    )

    return fig


def create_power_degradation_chart(
    initial_pmax: float,
    final_pmax: float,
    limit_percent: float = 5.0
) -> go.Figure:
    """Create power degradation bar chart

    Args:
        initial_pmax: Initial maximum power (W)
        final_pmax: Final maximum power (W)
        limit_percent: Maximum allowable degradation (%)

    Returns:
        Plotly figure object
    """
    degradation_percent = ((initial_pmax - final_pmax) / initial_pmax) * 100

    # Determine color based on pass/fail
    color = 'green' if degradation_percent <= limit_percent else 'red'

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=['Initial Power', 'Final Power'],
            y=[initial_pmax, final_pmax],
            marker_color=['blue', color],
            text=[f'{initial_pmax:.2f}W', f'{final_pmax:.2f}W'],
            textposition='outside'
        )
    )

    # Add degradation annotation
    fig.add_annotation(
        x=1,
        y=final_pmax,
        text=f"Degradation: {degradation_percent:.2f}%<br>Limit: {limit_percent}%<br>Status: {'PASS' if degradation_percent <= limit_percent else 'FAIL'}",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor=color,
        ax=50,
        ay=-50,
        bgcolor='white',
        bordercolor=color,
        borderwidth=2
    )

    fig.update_layout(
        title="Power Degradation Analysis",
        yaxis_title="Maximum Power (W)",
        height=400,
        showlegend=False
    )

    return fig


def create_parameter_comparison_table(
    initial_iv: Dict,
    final_iv: Dict
) -> pd.DataFrame:
    """Create parameter comparison table

    Args:
        initial_iv: Initial I-V parameters
        final_iv: Final I-V parameters

    Returns:
        Pandas DataFrame with comparison
    """
    parameters = ['voc', 'isc', 'pmax', 'fill_factor']
    param_names = ['Voc (V)', 'Isc (A)', 'Pmax (W)', 'Fill Factor']

    data = []
    for param, name in zip(parameters, param_names):
        initial_val = initial_iv.get(param, 0)
        final_val = final_iv.get(param, 0)
        change = final_val - initial_val
        change_percent = (change / initial_val * 100) if initial_val != 0 else 0

        data.append({
            'Parameter': name,
            'Initial': f'{initial_val:.3f}',
            'Final': f'{final_val:.3f}',
            'Change': f'{change:+.3f}',
            'Change (%)': f'{change_percent:+.2f}%'
        })

    return pd.DataFrame(data)


def create_hot_spot_summary_table(
    hot_spot_tests: List[Dict]
) -> pd.DataFrame:
    """Create hot spot test summary table

    Args:
        hot_spot_tests: List of hot spot test data

    Returns:
        Pandas DataFrame with summary
    """
    data = []
    for test in hot_spot_tests:
        data.append({
            'Cell ID': test['cell_id'],
            'Start Time': test['start_time'].strftime('%Y-%m-%d %H:%M:%S'),
            'Duration': f"{(test['end_time'] - test['start_time']).total_seconds() / 3600:.2f}h" if test.get('end_time') else 'In Progress',
            'Target Temp (°C)': f"{test.get('target_temperature', 0):.1f}",
            'Max Temp (°C)': f"{test.get('max_temperature_reached', 0):.1f}",
            'Reverse Bias (V)': f"{test.get('reverse_bias_voltage', 0):.2f}",
            'Status': 'Complete' if test.get('completed') else 'In Progress'
        })

    return pd.DataFrame(data)


def create_test_status_indicator(
    pass_fail: bool,
    degradation_percent: float,
    limit_percent: float
) -> str:
    """Create HTML status indicator

    Args:
        pass_fail: Overall pass/fail status
        degradation_percent: Measured degradation (%)
        limit_percent: Maximum allowed degradation (%)

    Returns:
        HTML string for status indicator
    """
    status_color = '#28a745' if pass_fail else '#dc3545'  # Green or Red
    status_text = 'PASS' if pass_fail else 'FAIL'

    html = f"""
    <div style='padding: 20px; border-radius: 10px; background-color: {status_color}; color: white; text-align: center;'>
        <h1 style='margin: 0;'>{status_text}</h1>
        <h3 style='margin: 10px 0;'>Power Degradation: {degradation_percent:.2f}%</h3>
        <p style='margin: 0;'>Limit: {limit_percent}%</p>
    </div>
    """
    return html


def create_defect_timeline(
    initial_inspection: Dict,
    final_inspection: Dict
) -> go.Figure:
    """Create visual inspection timeline

    Args:
        initial_inspection: Initial inspection data
        final_inspection: Final inspection data

    Returns:
        Plotly figure object
    """
    fig = go.Figure()

    # Create timeline data
    inspections = []

    if initial_inspection:
        inspections.append({
            'Inspection': 'Initial',
            'Timestamp': initial_inspection['timestamp'],
            'Defects': len(initial_inspection.get('defects', [])),
            'Severity': initial_inspection.get('severity', 'none')
        })

    if final_inspection:
        inspections.append({
            'Inspection': 'Final',
            'Timestamp': final_inspection['timestamp'],
            'Defects': len(final_inspection.get('defects', [])),
            'Severity': final_inspection.get('severity', 'none')
        })

    if not inspections:
        return fig

    df = pd.DataFrame(inspections)

    # Map severity to colors
    severity_colors = {
        'none': 'green',
        'minor': 'orange',
        'major': 'red'
    }

    fig = px.scatter(
        df,
        x='Timestamp',
        y='Defects',
        color='Severity',
        color_discrete_map=severity_colors,
        size='Defects',
        size_max=20,
        hover_data=['Inspection'],
        title='Visual Inspection Timeline'
    )

    fig.update_layout(
        xaxis_title='Inspection Time',
        yaxis_title='Number of Defects',
        height=300
    )

    return fig


def create_thermal_image_grid(
    image_paths: List[str],
    cell_ids: List[str]
) -> str:
    """Create HTML grid of thermal images

    Args:
        image_paths: List of thermal image file paths
        cell_ids: List of cell IDs corresponding to images

    Returns:
        HTML string for image grid
    """
    html = "<div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;'>"

    for cell_id, img_path in zip(cell_ids, image_paths):
        html += f"""
        <div style='text-align: center;'>
            <h4>Cell {cell_id}</h4>
            <img src='{img_path}' style='width: 100%; border: 2px solid #ddd; border-radius: 5px;'/>
        </div>
        """

    html += "</div>"
    return html


def create_qr_code_display(
    qr_code_base64: str,
    test_id: str
) -> str:
    """Create HTML for QR code display

    Args:
        qr_code_base64: Base64 encoded QR code image
        test_id: Test ID for label

    Returns:
        HTML string for QR code display
    """
    html = f"""
    <div style='text-align: center; padding: 20px; border: 1px solid #ddd; border-radius: 10px;'>
        <h3>Test Traceability QR Code</h3>
        <img src='data:image/png;base64,{qr_code_base64}' style='max-width: 300px;'/>
        <p><strong>Test ID:</strong> {test_id}</p>
        <p style='font-size: 0.9em; color: #666;'>Scan for complete test details and history</p>
    </div>
    """
    return html
