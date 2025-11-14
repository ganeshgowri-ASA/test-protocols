"""Degradation-specific visualization page for UVID-001 and similar tests."""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def show_degradation_visualization():
    """Display degradation test visualization."""

    st.title("UV Degradation Test Visualization")

    # Tabs for different visualizations
    tab1, tab2, tab3, tab4 = st.tabs([
        "Degradation Trends",
        "Parameter Comparison",
        "I-V Curves",
        "Environmental Conditions"
    ])

    with tab1:
        show_degradation_trends()

    with tab2:
        show_parameter_comparison()

    with tab3:
        show_iv_curves()

    with tab4:
        show_environmental_conditions()


def show_degradation_trends():
    """Display degradation trends over time."""

    st.subheader("Power Degradation Over Time")

    # Generate sample data for demonstration
    hours = np.linspace(0, 1000, 50)
    pmax_retention = 100 - (hours / 1000) * 3.5  # 3.5% degradation over 1000 hours
    noise = np.random.normal(0, 0.5, len(hours))
    pmax_retention_noisy = pmax_retention + noise

    df = pd.DataFrame({
        'Hours': hours,
        'Pmax Retention (%)': pmax_retention_noisy,
        'Voc Retention (%)': 100 - (hours / 1000) * 1.5 + np.random.normal(0, 0.3, len(hours)),
        'Isc Retention (%)': 100 - (hours / 1000) * 2.0 + np.random.normal(0, 0.4, len(hours)),
        'FF Retention (%)': 100 - (hours / 1000) * 1.8 + np.random.normal(0, 0.3, len(hours))
    })

    # Create plotly figure
    fig = go.Figure()

    parameters = ['Pmax Retention (%)', 'Voc Retention (%)', 'Isc Retention (%)', 'FF Retention (%)']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

    for param, color in zip(parameters, colors):
        fig.add_trace(go.Scatter(
            x=df['Hours'],
            y=df[param],
            mode='lines+markers',
            name=param,
            line=dict(color=color, width=2),
            marker=dict(size=6)
        ))

    # Add requirement line at 95%
    fig.add_hline(
        y=95,
        line_dash="dash",
        line_color="red",
        annotation_text="95% Requirement",
        annotation_position="right"
    )

    fig.update_layout(
        title="Parameter Retention vs. Exposure Time",
        xaxis_title="UV Exposure Time (hours)",
        yaxis_title="Retention (%)",
        yaxis_range=[90, 101],
        hovermode='x unified',
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    # Statistics table
    st.subheader("Degradation Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Pmax Retention",
            f"{df['Pmax Retention (%)'].iloc[-1]:.2f}%",
            f"{df['Pmax Retention (%)'].iloc[-1] - 100:.2f}%"
        )

    with col2:
        st.metric(
            "Voc Retention",
            f"{df['Voc Retention (%)'].iloc[-1]:.2f}%",
            f"{df['Voc Retention (%)'].iloc[-1] - 100:.2f}%"
        )

    with col3:
        st.metric(
            "Isc Retention",
            f"{df['Isc Retention (%)'].iloc[-1]:.2f}%",
            f"{df['Isc Retention (%)'].iloc[-1] - 100:.2f}%"
        )

    with col4:
        st.metric(
            "FF Retention",
            f"{df['FF Retention (%)'].iloc[-1]:.2f}%",
            f"{df['FF Retention (%)'].iloc[-1] - 100:.2f}%"
        )


def show_parameter_comparison():
    """Display parameter comparison before and after."""

    st.subheader("Initial vs. Final Parameter Comparison")

    # Sample data
    parameters = ['Pmax', 'Voc', 'Isc', 'Vmp', 'Imp', 'FF', 'Efficiency']
    initial = [250.5, 38.2, 8.95, 31.5, 7.95, 73.2, 16.8]
    final = [241.2, 37.8, 8.78, 31.1, 7.76, 71.8, 16.2]

    df = pd.DataFrame({
        'Parameter': parameters,
        'Initial': initial,
        'Final': final,
        'Change (%)': [(f - i) / i * 100 for i, f in zip(initial, final)]
    })

    # Create comparison chart
    fig = go.Figure()

    fig.add_trace(go.Bar(
        name='Initial',
        x=df['Parameter'],
        y=df['Initial'],
        marker_color='lightblue'
    ))

    fig.add_trace(go.Bar(
        name='Final',
        x=df['Parameter'],
        y=df['Final'],
        marker_color='darkblue'
    ))

    fig.update_layout(
        title="Parameter Values: Initial vs. Final",
        xaxis_title="Parameter",
        yaxis_title="Value",
        barmode='group',
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    # Change table
    st.subheader("Detailed Changes")

    # Add pass/fail indicator
    df['Status'] = df['Change (%)'].apply(
        lambda x: '✅ PASS' if x >= -5 else '❌ FAIL'
    )

    # Format the dataframe
    styled_df = df.style.format({
        'Initial': '{:.2f}',
        'Final': '{:.2f}',
        'Change (%)': '{:.2f}%'
    }).background_gradient(
        subset=['Change (%)'],
        cmap='RdYlGn',
        vmin=-10,
        vmax=0
    )

    st.dataframe(styled_df, use_container_width=True)


def show_iv_curves():
    """Display I-V curves comparison."""

    st.subheader("I-V Curve Comparison")

    # Generate sample I-V curves
    voltage = np.linspace(0, 40, 100)

    # Initial curve
    current_initial = 9.0 * (1 - np.exp((voltage - 38.5) / 2.5))
    current_initial = np.maximum(current_initial, 0)

    # Final curve (degraded)
    current_final = 8.8 * (1 - np.exp((voltage - 38.0) / 2.5))
    current_final = np.maximum(current_final, 0)

    # Create plot
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=voltage,
        y=current_initial,
        mode='lines',
        name='Initial',
        line=dict(color='blue', width=3)
    ))

    fig.add_trace(go.Scatter(
        x=voltage,
        y=current_final,
        mode='lines',
        name='After 1000h UV',
        line=dict(color='red', width=3)
    ))

    # Mark MPP points
    mpp_v_initial = 31.5
    mpp_i_initial = 7.95
    fig.add_trace(go.Scatter(
        x=[mpp_v_initial],
        y=[mpp_i_initial],
        mode='markers',
        name='Initial MPP',
        marker=dict(size=12, color='blue', symbol='star')
    ))

    mpp_v_final = 31.1
    mpp_i_final = 7.76
    fig.add_trace(go.Scatter(
        x=[mpp_v_final],
        y=[mpp_i_final],
        mode='markers',
        name='Final MPP',
        marker=dict(size=12, color='red', symbol='star')
    ))

    fig.update_layout(
        title="I-V Curves: Initial vs. Final",
        xaxis_title="Voltage (V)",
        yaxis_title="Current (A)",
        height=500,
        hovermode='closest'
    )

    st.plotly_chart(fig, use_container_width=True)

    # Power curves
    st.subheader("P-V Curves")

    power_initial = voltage * current_initial
    power_final = voltage * current_final

    fig_power = go.Figure()

    fig_power.add_trace(go.Scatter(
        x=voltage,
        y=power_initial,
        mode='lines',
        name='Initial',
        line=dict(color='blue', width=3)
    ))

    fig_power.add_trace(go.Scatter(
        x=voltage,
        y=power_final,
        mode='lines',
        name='After 1000h UV',
        line=dict(color='red', width=3)
    ))

    fig_power.update_layout(
        title="Power-Voltage Curves",
        xaxis_title="Voltage (V)",
        yaxis_title="Power (W)",
        height=400
    )

    st.plotly_chart(fig_power, use_container_width=True)


def show_environmental_conditions():
    """Display environmental conditions during test."""

    st.subheader("Environmental Conditions Monitoring")

    # Generate sample environmental data
    hours = np.linspace(0, 1000, 500)
    temperature = 60 + np.random.normal(0, 0.5, len(hours))
    irradiance = 1.0 + np.random.normal(0, 0.03, len(hours))
    humidity = 50 + np.random.normal(0, 2, len(hours))

    df = pd.DataFrame({
        'Hours': hours,
        'Temperature (°C)': temperature,
        'UV Irradiance (W/m²)': irradiance,
        'Humidity (%)': humidity
    })

    # Temperature plot
    st.markdown("#### Temperature Stability")

    fig_temp = go.Figure()

    fig_temp.add_trace(go.Scatter(
        x=df['Hours'],
        y=df['Temperature (°C)'],
        mode='lines',
        name='Temperature',
        line=dict(color='orange', width=1)
    ))

    # Add specification limits
    fig_temp.add_hline(y=62, line_dash="dash", line_color="red", annotation_text="+2°C limit")
    fig_temp.add_hline(y=58, line_dash="dash", line_color="red", annotation_text="-2°C limit")
    fig_temp.add_hline(y=60, line_dash="dot", line_color="green", annotation_text="Target")

    fig_temp.update_layout(
        xaxis_title="Time (hours)",
        yaxis_title="Temperature (°C)",
        height=300,
        showlegend=False
    )

    st.plotly_chart(fig_temp, use_container_width=True)

    # Irradiance plot
    st.markdown("#### UV Irradiance Stability")

    fig_irr = go.Figure()

    fig_irr.add_trace(go.Scatter(
        x=df['Hours'],
        y=df['UV Irradiance (W/m²)'],
        mode='lines',
        name='Irradiance',
        line=dict(color='purple', width=1)
    ))

    fig_irr.add_hline(y=1.1, line_dash="dash", line_color="red", annotation_text="+0.1 W/m² limit")
    fig_irr.add_hline(y=0.9, line_dash="dash", line_color="red", annotation_text="-0.1 W/m² limit")
    fig_irr.add_hline(y=1.0, line_dash="dot", line_color="green", annotation_text="Target")

    fig_irr.update_layout(
        xaxis_title="Time (hours)",
        yaxis_title="UV Irradiance (W/m²)",
        height=300,
        showlegend=False
    )

    st.plotly_chart(fig_irr, use_container_width=True)

    # Summary statistics
    st.subheader("Environmental Conditions Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Temperature",
            f"{df['Temperature (°C)'].mean():.2f}°C",
            f"±{df['Temperature (°C)'].std():.2f}°C"
        )
        temp_in_spec = ((df['Temperature (°C)'] >= 58) & (df['Temperature (°C)'] <= 62)).mean() * 100
        st.write(f"**Within Spec:** {temp_in_spec:.1f}%")

    with col2:
        st.metric(
            "UV Irradiance",
            f"{df['UV Irradiance (W/m²)'].mean():.3f} W/m²",
            f"±{df['UV Irradiance (W/m²)'].std():.3f} W/m²"
        )
        irr_in_spec = ((df['UV Irradiance (W/m²)'] >= 0.9) & (df['UV Irradiance (W/m²)'] <= 1.1)).mean() * 100
        st.write(f"**Within Spec:** {irr_in_spec:.1f}%")

    with col3:
        st.metric(
            "Humidity",
            f"{df['Humidity (%)'].mean():.1f}%",
            f"±{df['Humidity (%)'].std():.1f}%"
        )


if __name__ == "__main__":
    show_degradation_visualization()
