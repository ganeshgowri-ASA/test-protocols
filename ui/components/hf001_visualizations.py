"""HF-001 Visualization Components

Real-time charts and graphs for Humidity Freeze test protocol.
"""

from typing import List, Tuple
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import streamlit as st


def plot_cycle_profile(
    cycle_number: int,
    temperature_data: List[Tuple],
    humidity_data: List[Tuple]
) -> go.Figure:
    """Create real-time temperature and humidity profile plot

    Args:
        cycle_number: Cycle number being displayed
        temperature_data: List of (timestamp, temperature) tuples
        humidity_data: List of (timestamp, humidity) tuples

    Returns:
        Plotly figure with dual-axis plot
    """
    # Convert to DataFrames for easier plotting
    temp_df = pd.DataFrame(temperature_data, columns=['timestamp', 'temperature'])
    humid_df = pd.DataFrame(humidity_data, columns=['timestamp', 'humidity'])

    # Create figure with secondary y-axis
    fig = make_subplots(
        rows=1, cols=1,
        specs=[[{"secondary_y": True}]],
        subplot_titles=[f"Cycle {cycle_number} - Temperature & Humidity Profile"]
    )

    # Add temperature trace
    fig.add_trace(
        go.Scatter(
            x=temp_df['timestamp'],
            y=temp_df['temperature'],
            name="Temperature",
            line=dict(color='#FF6B6B', width=2),
            mode='lines'
        ),
        secondary_y=False
    )

    # Add humidity trace
    fig.add_trace(
        go.Scatter(
            x=humid_df['timestamp'],
            y=humid_df['humidity'],
            name="Humidity",
            line=dict(color='#4ECDC4', width=2),
            mode='lines'
        ),
        secondary_y=True
    )

    # Add temperature setpoint lines
    fig.add_hline(
        y=85, line_dash="dash", line_color="#FF6B6B",
        opacity=0.5, secondary_y=False,
        annotation_text="High Temp (85°C)"
    )
    fig.add_hline(
        y=-40, line_dash="dash", line_color="#4169E1",
        opacity=0.5, secondary_y=False,
        annotation_text="Low Temp (-40°C)"
    )

    # Add humidity setpoint line
    fig.add_hline(
        y=85, line_dash="dash", line_color="#4ECDC4",
        opacity=0.3, secondary_y=True,
        annotation_text="Target RH (85%)"
    )

    # Update axes
    fig.update_xaxes(title_text="Time")
    fig.update_yaxes(
        title_text="Temperature (°C)",
        secondary_y=False,
        range=[-50, 95]
    )
    fig.update_yaxes(
        title_text="Relative Humidity (%)",
        secondary_y=True,
        range=[0, 100]
    )

    # Update layout
    fig.update_layout(
        hovermode='x unified',
        height=500,
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


def plot_all_cycles_overview(cycles_data: List) -> go.Figure:
    """Create overview plot of all cycles

    Args:
        cycles_data: List of cycle data dictionaries

    Returns:
        Plotly figure with all cycles temperature profiles
    """
    fig = go.Figure()

    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
              '#DFE6E9', '#74B9FF', '#A29BFE', '#FD79A8', '#FDCB6E']

    for i, cycle in enumerate(cycles_data):
        temp_df = pd.DataFrame(cycle['temperature_log'], columns=['timestamp', 'temperature'])

        fig.add_trace(
            go.Scatter(
                x=temp_df['timestamp'],
                y=temp_df['temperature'],
                name=f"Cycle {cycle['cycle_number']}",
                line=dict(color=colors[i % len(colors)], width=1.5),
                mode='lines'
            )
        )

    # Add setpoint lines
    fig.add_hline(y=85, line_dash="dash", line_color="red", opacity=0.5)
    fig.add_hline(y=-40, line_dash="dash", line_color="blue", opacity=0.5)

    fig.update_layout(
        title="All Cycles Temperature Profile Overview",
        xaxis_title="Time",
        yaxis_title="Temperature (°C)",
        height=600,
        hovermode='x unified',
        showlegend=True
    )

    return fig


def plot_iv_curve_comparison(
    initial_iv: dict,
    final_iv: dict
) -> go.Figure:
    """Create I-V curve comparison plot

    Args:
        initial_iv: Initial I-V curve data dict
        final_iv: Final I-V curve data dict

    Returns:
        Plotly figure comparing I-V curves
    """
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("I-V Curves", "Power Curves")
    )

    # I-V Curves
    fig.add_trace(
        go.Scatter(
            x=initial_iv['voltage'],
            y=initial_iv['current'],
            name="Initial I-V",
            line=dict(color='#2ECC71', width=2),
            mode='lines'
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=final_iv['voltage'],
            y=final_iv['current'],
            name="Final I-V",
            line=dict(color='#E74C3C', width=2, dash='dash'),
            mode='lines'
        ),
        row=1, col=1
    )

    # Power Curves
    initial_power = [v * i for v, i in zip(initial_iv['voltage'], initial_iv['current'])]
    final_power = [v * i for v, i in zip(final_iv['voltage'], final_iv['current'])]

    fig.add_trace(
        go.Scatter(
            x=initial_iv['voltage'],
            y=initial_power,
            name="Initial Power",
            line=dict(color='#2ECC71', width=2),
            mode='lines',
            showlegend=False
        ),
        row=1, col=2
    )

    fig.add_trace(
        go.Scatter(
            x=final_iv['voltage'],
            y=final_power,
            name="Final Power",
            line=dict(color='#E74C3C', width=2, dash='dash'),
            mode='lines',
            showlegend=False
        ),
        row=1, col=2
    )

    # Mark MPP points
    fig.add_trace(
        go.Scatter(
            x=[initial_iv['Vmp']],
            y=[initial_iv['Vmp'] * initial_iv['Imp']],
            mode='markers',
            marker=dict(color='#2ECC71', size=10, symbol='star'),
            name=f"Initial MPP ({initial_iv['Pmax']:.1f}W)",
            showlegend=True
        ),
        row=1, col=2
    )

    fig.add_trace(
        go.Scatter(
            x=[final_iv['Vmp']],
            y=[final_iv['Vmp'] * final_iv['Imp']],
            mode='markers',
            marker=dict(color='#E74C3C', size=10, symbol='star'),
            name=f"Final MPP ({final_iv['Pmax']:.1f}W)",
            showlegend=True
        ),
        row=1, col=2
    )

    fig.update_xaxes(title_text="Voltage (V)", row=1, col=1)
    fig.update_xaxes(title_text="Voltage (V)", row=1, col=2)
    fig.update_yaxes(title_text="Current (A)", row=1, col=1)
    fig.update_yaxes(title_text="Power (W)", row=1, col=2)

    fig.update_layout(
        height=500,
        showlegend=True,
        hovermode='closest'
    )

    return fig


def plot_degradation_metrics(analysis_data: dict) -> go.Figure:
    """Create degradation metrics visualization

    Args:
        analysis_data: Dictionary with analysis results

    Returns:
        Plotly figure with degradation metrics
    """
    initial = analysis_data['initial_performance']
    final = analysis_data['final_performance']

    # Calculate degradation percentages
    parameters = ['Pmax', 'Voc', 'Isc', 'FF']
    degradations = []

    for param in parameters:
        if initial[param] and final[param]:
            deg = ((initial[param] - final[param]) / initial[param]) * 100
            degradations.append(deg)
        else:
            degradations.append(0)

    # Create bar chart
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=parameters,
            y=degradations,
            marker_color=['#E74C3C' if d > 5 else '#3498DB' for d in degradations],
            text=[f"{d:.2f}%" for d in degradations],
            textposition='outside'
        )
    )

    # Add 5% limit line for power
    fig.add_hline(
        y=5, line_dash="dash", line_color="red",
        annotation_text="5% Limit (Pmax only)",
        opacity=0.7
    )

    fig.update_layout(
        title="Performance Degradation Analysis",
        xaxis_title="Parameter",
        yaxis_title="Degradation (%)",
        height=400,
        showlegend=False
    )

    return fig


def create_qr_code_display(qr_content: str) -> None:
    """Display QR code for traceability

    Args:
        qr_content: QR code content string
    """
    try:
        import qrcode
        from io import BytesIO

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_content)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to bytes for Streamlit
        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)

        st.image(buf, caption=f"Traceability QR Code: {qr_content}", width=250)

    except ImportError:
        st.warning("QR code library not available. Install with: pip install qrcode[pil]")
        st.code(qr_content, language=None)


def display_cycle_progress(current_cycle: int, total_cycles: int, cycle_status: str) -> None:
    """Display cycle progress indicator

    Args:
        current_cycle: Current cycle number
        total_cycles: Total number of cycles
        cycle_status: Status of current cycle
    """
    progress = current_cycle / total_cycles

    # Status emoji
    status_icons = {
        'running': '🔄',
        'completed': '✅',
        'failed': '❌',
        'pending': '⏳'
    }

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.progress(progress)

    with col2:
        st.metric(
            "Cycle Progress",
            f"{current_cycle}/{total_cycles}"
        )

    with col3:
        st.metric(
            "Status",
            f"{status_icons.get(cycle_status, '❓')} {cycle_status.title()}"
        )
