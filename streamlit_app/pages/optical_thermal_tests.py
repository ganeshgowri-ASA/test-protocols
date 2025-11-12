"""
Optical and Thermal Tests - Streamlit Interface

Interactive dashboard for:
- UV Exposure Test (PVTP-007-UV)
- Hot Spot Endurance Test (PVTP-008-HS)
- Bypass Diode Thermal Test (PVTP-009-BD)

Features:
- UV dose progress tracker
- Thermal imaging overlay tool
- Diode I-V curve plotter
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
from pathlib import Path
import sys

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent.parent / "backend"))

try:
    from protocols.optical_thermal_handler import (
        UVDoseCalculator,
        HotSpotDetector,
        DiodeCharacteristicAnalyzer,
        generate_test_report
    )
    HANDLER_AVAILABLE = True
except ImportError:
    HANDLER_AVAILABLE = False
    st.warning("Backend handler not available. Running in UI-only mode.")


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Optical & Thermal Tests",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🔬 Optical & Thermal Test Protocols")
st.markdown("""
Comprehensive testing suite for UV exposure, hot spot endurance, and bypass diode performance.
Based on IEC 61215-2:2016 standards.
""")


# ============================================================================
# SIDEBAR - TEST SELECTION
# ============================================================================

st.sidebar.header("Test Selection")

test_type = st.sidebar.selectbox(
    "Select Test Protocol",
    [
        "UV Exposure Test (PVTP-007-UV)",
        "Hot Spot Endurance Test (PVTP-008-HS)",
        "Bypass Diode Thermal Test (PVTP-009-BD)"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("""
**Standards Reference:**
- IEC 61215-2:2016 MQT 09 (Hot Spot)
- IEC 61215-2:2016 MQT 10 (UV)
- IEC 61215-2:2016 MQT 18 (Bypass Diode)
""")


# ============================================================================
# UV EXPOSURE TEST
# ============================================================================

if "UV Exposure" in test_type:
    st.header("☀️ UV Exposure Test (PVTP-007-UV)")

    st.markdown("""
    **Purpose:** Verify module resistance to UV radiation exposure
    **Standard:** IEC 61215-2:2016 MQT 10
    **Duration:** 1000-4000 hours
    """)

    # Test Configuration
    st.subheader("1. Test Configuration")

    col1, col2, col3 = st.columns(3)

    with col1:
        target_dose = st.selectbox(
            "Target UV Dose",
            options=[15.0, 60.0],
            format_func=lambda x: f"{x} kWh/m² ({'Standard' if x == 15 else 'Extended'})"
        )

    with col2:
        irradiance_target = st.number_input(
            "Target Irradiance (W/m²/nm @ 340 nm)",
            min_value=0.5,
            max_value=0.7,
            value=0.6,
            step=0.01
        )

    with col3:
        chamber_temp = st.number_input(
            "Chamber Temperature (°C)",
            min_value=55,
            max_value=65,
            value=60,
            step=1
        )

    # UV Dose Progress Tracker
    st.subheader("2. UV Dose Progress Tracker")

    # Sample data generator
    if st.button("Generate Sample UV Exposure Data"):
        st.session_state['uv_data_generated'] = True

        # Simulate exposure data
        hours = 500  # Example: 500 hours of exposure
        time_points = np.linspace(0, hours, 1000)

        # Simulate varying irradiance with day/night cycles
        daily_pattern = np.sin(2 * np.pi * time_points / 24) * 0.5 + 0.5
        irradiance = daily_pattern * 60 + np.random.normal(0, 2, len(time_points))
        irradiance = np.clip(irradiance, 0, 70)

        # Add temperature variation
        temperature = 60 + np.sin(2 * np.pi * time_points / 24) * 3 + np.random.normal(0, 1, len(time_points))

        st.session_state['uv_time'] = time_points
        st.session_state['uv_irradiance'] = irradiance
        st.session_state['uv_temperature'] = temperature

        if HANDLER_AVAILABLE:
            calc = UVDoseCalculator(target_dose=target_dose)
            cumulative_dose = calc.calculate_cumulative_dose(irradiance, time_points)
            st.session_state['uv_dose'] = cumulative_dose

    if st.session_state.get('uv_data_generated', False):
        time_points = st.session_state['uv_time']
        irradiance = st.session_state['uv_irradiance']
        temperature = st.session_state['uv_temperature']

        if HANDLER_AVAILABLE:
            cumulative_dose = st.session_state['uv_dose']
            current_dose = cumulative_dose[-1]
            completion_pct = (current_dose / target_dose) * 100

            # Progress metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Current Dose", f"{current_dose:.2f} kWh/m²")

            with col2:
                st.metric("Target Dose", f"{target_dose:.2f} kWh/m²")

            with col3:
                st.metric("Completion", f"{completion_pct:.1f}%")

            with col4:
                calc = UVDoseCalculator(target_dose=target_dose)
                avg_irrad = np.mean(irradiance[irradiance > 0])
                hours_rem, time_str = calc.estimate_remaining_time(current_dose, avg_irrad)
                st.metric("Est. Remaining", time_str)

            # Progress bar
            st.progress(min(completion_pct / 100, 1.0))

        # Visualization
        tab1, tab2, tab3 = st.tabs(["Dose Progress", "Irradiance & Temperature", "Statistics"])

        with tab1:
            if HANDLER_AVAILABLE:
                fig = make_subplots(
                    rows=2, cols=1,
                    subplot_titles=("Cumulative UV Dose", "Instantaneous Irradiance"),
                    vertical_spacing=0.12
                )

                # Cumulative dose
                fig.add_trace(
                    go.Scatter(
                        x=time_points,
                        y=cumulative_dose,
                        mode='lines',
                        name='Cumulative Dose',
                        line=dict(color='#FF6B35', width=2)
                    ),
                    row=1, col=1
                )

                # Target line
                fig.add_hline(
                    y=target_dose,
                    line_dash="dash",
                    line_color="green",
                    annotation_text=f"Target: {target_dose} kWh/m²",
                    row=1, col=1
                )

                # Irradiance
                fig.add_trace(
                    go.Scatter(
                        x=time_points,
                        y=irradiance,
                        mode='lines',
                        name='Irradiance',
                        line=dict(color='#004E89', width=1)
                    ),
                    row=2, col=1
                )

                fig.update_xaxes(title_text="Exposure Time (hours)", row=2, col=1)
                fig.update_yaxes(title_text="Dose (kWh/m²)", row=1, col=1)
                fig.update_yaxes(title_text="Irradiance (W/m²)", row=2, col=1)

                fig.update_layout(height=700, showlegend=True)
                st.plotly_chart(fig, use_container_width=True)

        with tab2:
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=("UV Irradiance Over Time", "Chamber Temperature"),
                vertical_spacing=0.12
            )

            fig.add_trace(
                go.Scatter(
                    x=time_points,
                    y=irradiance,
                    mode='lines',
                    name='Irradiance',
                    line=dict(color='#FF6B35')
                ),
                row=1, col=1
            )

            fig.add_trace(
                go.Scatter(
                    x=time_points,
                    y=temperature,
                    mode='lines',
                    name='Temperature',
                    line=dict(color='#F77F00')
                ),
                row=2, col=1
            )

            # Temperature spec limits
            fig.add_hline(y=65, line_dash="dash", line_color="red", annotation_text="Upper Limit", row=2, col=1)
            fig.add_hline(y=55, line_dash="dash", line_color="blue", annotation_text="Lower Limit", row=2, col=1)

            fig.update_xaxes(title_text="Time (hours)", row=2, col=1)
            fig.update_yaxes(title_text="Irradiance (W/m²)", row=1, col=1)
            fig.update_yaxes(title_text="Temperature (°C)", row=2, col=1)

            fig.update_layout(height=700, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)

        with tab3:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Irradiance Statistics**")
                stats_df = pd.DataFrame({
                    'Metric': ['Mean', 'Std Dev', 'Min', 'Max', 'Median'],
                    'Value (W/m²)': [
                        f"{np.mean(irradiance):.2f}",
                        f"{np.std(irradiance):.2f}",
                        f"{np.min(irradiance):.2f}",
                        f"{np.max(irradiance):.2f}",
                        f"{np.median(irradiance):.2f}"
                    ]
                })
                st.dataframe(stats_df, hide_index=True)

            with col2:
                st.markdown("**Temperature Statistics**")
                temp_df = pd.DataFrame({
                    'Metric': ['Mean', 'Std Dev', 'Min', 'Max', 'Median'],
                    'Value (°C)': [
                        f"{np.mean(temperature):.2f}",
                        f"{np.std(temperature):.2f}",
                        f"{np.min(temperature):.2f}",
                        f"{np.max(temperature):.2f}",
                        f"{np.median(temperature):.2f}"
                    ]
                })
                st.dataframe(temp_df, hide_index=True)

            # Histogram
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=irradiance,
                name='Irradiance Distribution',
                nbinsx=50,
                marker_color='#004E89'
            ))
            fig.update_layout(
                title="Irradiance Distribution",
                xaxis_title="Irradiance (W/m²)",
                yaxis_title="Frequency",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# HOT SPOT ENDURANCE TEST
# ============================================================================

elif "Hot Spot" in test_type:
    st.header("🔥 Hot Spot Endurance Test (PVTP-008-HS)")

    st.markdown("""
    **Purpose:** Verify module can withstand thermal stress from partial shading
    **Standard:** IEC 61215-2:2016 MQT 09
    **Duration:** 1-5 hours
    """)

    # Test Configuration
    st.subheader("1. Test Configuration")

    col1, col2, col3 = st.columns(3)

    with col1:
        irradiance = st.number_input(
            "Irradiance (W/m²)",
            min_value=900,
            max_value=1100,
            value=1000,
            step=10
        )

    with col2:
        test_duration = st.number_input(
            "Test Duration (hours)",
            min_value=1,
            max_value=5,
            value=1,
            step=1
        )

    with col3:
        shading_pattern = st.selectbox(
            "Shading Pattern",
            ["Single Cell (100%)", "Partial Cell (50%)", "Multi-Cell", "String"]
        )

    # Thermal Imaging Overlay Tool
    st.subheader("2. Thermal Imaging Overlay Tool")

    if st.button("Generate Thermal Image Data"):
        st.session_state['thermal_data_generated'] = True

        # Create synthetic thermal image
        rows, cols = 48, 64  # Typical module grid (6×10 cells, multiple pixels per cell)

        # Background temperature
        thermal_img = np.random.normal(50, 3, (rows, cols))

        # Add hot spot (simulate shaded cell)
        hotspot_row, hotspot_col = rows // 2, cols // 2
        for i in range(hotspot_row - 5, hotspot_row + 5):
            for j in range(hotspot_col - 5, hotspot_col + 5):
                if 0 <= i < rows and 0 <= j < cols:
                    dist = np.sqrt((i - hotspot_row)**2 + (j - hotspot_col)**2)
                    thermal_img[i, j] = 95 - dist * 2  # Peak at 95°C

        st.session_state['thermal_image'] = thermal_img

        # Generate time series
        time_minutes = np.linspace(0, test_duration * 60, test_duration * 60)

        # Temperature transient (exponential rise)
        T_final = 95
        tau = 15  # minutes
        T_initial = 50
        temps = T_final * (1 - np.exp(-time_minutes / tau)) + T_initial
        temps += np.random.normal(0, 1, len(temps))

        st.session_state['hotspot_time'] = time_minutes
        st.session_state['hotspot_temp'] = temps

    if st.session_state.get('thermal_data_generated', False):
        thermal_img = st.session_state['thermal_image']

        tab1, tab2, tab3 = st.tabs(["Thermal Image", "Temperature Transient", "Analysis"])

        with tab1:
            st.markdown("**Real-Time Thermal Overlay**")

            # Detection settings
            col1, col2 = st.columns(2)

            with col1:
                threshold_method = st.radio(
                    "Detection Method",
                    ["Absolute", "Adaptive", "Statistical"],
                    horizontal=True
                )

            with col2:
                if threshold_method == "Absolute":
                    threshold_temp = st.slider("Temperature Threshold (°C)", 70, 100, 85)
                else:
                    threshold_temp = st.slider("Offset from Mean (°C)", 10, 40, 20)

            # Apply detection
            if HANDLER_AVAILABLE:
                detector = HotSpotDetector(
                    threshold_method=threshold_method.lower(),
                    min_hotspot_area_cm2=10.0
                )

                results = detector.detect_hotspots(
                    thermal_img,
                    pixel_size_cm=0.5,
                    absolute_threshold_c=threshold_temp if threshold_method == "Absolute" else 85,
                    adaptive_offset_c=threshold_temp if threshold_method == "Adaptive" else 20
                )

                # Display metrics
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Max Temperature", f"{results['max_temperature_c']:.1f}°C")

                with col2:
                    st.metric("Mean Temperature", f"{results['mean_temperature_c']:.1f}°C")

                with col3:
                    st.metric("Temperature Gradient", f"{results['temperature_gradient_c']:.1f}°C")

                with col4:
                    st.metric("Hot Spots Detected", results['num_hotspots_detected'])

                # Check acceptance
                if results['max_temperature_c'] > 105:
                    st.error("⚠️ CRITICAL: Temperature exceeds 105°C limit!")
                elif results['max_temperature_c'] > 85:
                    st.warning("⚠️ WARNING: Temperature approaching limit")
                else:
                    st.success("✓ Temperature within acceptable range")

            # Thermal image visualization
            fig = go.Figure(data=go.Heatmap(
                z=thermal_img,
                colorscale='Hot',
                colorbar=dict(title="Temperature (°C)")
            ))

            fig.update_layout(
                title="Thermal Image of PV Module",
                xaxis_title="Column",
                yaxis_title="Row",
                height=600
            )

            st.plotly_chart(fig, use_container_width=True)

            # Show detected hot spots
            if HANDLER_AVAILABLE and results['num_hotspots_detected'] > 0:
                st.markdown("**Detected Hot Spots:**")
                hotspot_df = pd.DataFrame(results['hotspots'])
                st.dataframe(hotspot_df, hide_index=True)

        with tab2:
            time_minutes = st.session_state['hotspot_time']
            temps = st.session_state['hotspot_temp']

            st.markdown("**Hot Spot Temperature Over Time**")

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=time_minutes,
                y=temps,
                mode='lines+markers',
                name='Hot Spot Temperature',
                line=dict(color='#FF6B35', width=2)
            ))

            # Add threshold lines
            fig.add_hline(y=105, line_dash="dash", line_color="red",
                         annotation_text="Critical Limit (105°C)")
            fig.add_hline(y=85, line_dash="dash", line_color="orange",
                         annotation_text="Warning Threshold (85°C)")

            fig.update_layout(
                xaxis_title="Time (minutes)",
                yaxis_title="Temperature (°C)",
                height=500,
                showlegend=True
            )

            st.plotly_chart(fig, use_container_width=True)

            # Fit exponential model
            if HANDLER_AVAILABLE:
                detector = HotSpotDetector()
                transient_results = detector.track_temperature_transient(
                    temps,
                    time_minutes
                )

                if transient_results.get('fit_successful', False):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Initial Temp", f"{transient_results['T_initial_c']:.1f}°C")

                    with col2:
                        st.metric("Final Temp", f"{transient_results['T_final_c']:.1f}°C")

                    with col3:
                        st.metric("Time Constant", f"{transient_results['time_constant_tau_min']:.1f} min")

                    st.info(f"Steady state: {'Yes' if transient_results['is_steady_state'] else 'No'} | "
                           f"R²: {transient_results['r_squared']:.3f}")

        with tab3:
            if HANDLER_AVAILABLE:
                detector = HotSpotDetector()
                dist_results = detector.calculate_thermal_distribution(thermal_img)

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Temperature Distribution Statistics**")
                    stats_df = pd.DataFrame({
                        'Metric': [
                            'Mean', 'Median', 'Std Dev', 'Min', 'Max',
                            'Range', 'Skewness', 'Kurtosis'
                        ],
                        'Value': [
                            f"{dist_results['mean_temperature_c']:.2f}°C",
                            f"{dist_results['median_temperature_c']:.2f}°C",
                            f"{dist_results['std_temperature_c']:.2f}°C",
                            f"{dist_results['min_temperature_c']:.2f}°C",
                            f"{dist_results['max_temperature_c']:.2f}°C",
                            f"{dist_results['range_c']:.2f}°C",
                            f"{dist_results['skewness']:.3f}",
                            f"{dist_results['kurtosis']:.3f}"
                        ]
                    })
                    st.dataframe(stats_df, hide_index=True)

                with col2:
                    # Histogram
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=(dist_results['histogram_bin_edges'][:-1] +
                           dist_results['histogram_bin_edges'][1:]) / 2,
                        y=dist_results['histogram_counts'],
                        marker_color='#004E89',
                        name='Temperature Distribution'
                    ))

                    fig.update_layout(
                        title="Temperature Histogram",
                        xaxis_title="Temperature (°C)",
                        yaxis_title="Pixel Count",
                        height=400
                    )

                    st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# BYPASS DIODE THERMAL TEST
# ============================================================================

elif "Bypass Diode" in test_type:
    st.header("⚡ Bypass Diode Thermal Test (PVTP-009-BD)")

    st.markdown("""
    **Purpose:** Verify bypass diode performance under thermal and electrical stress
    **Standard:** IEC 61215-2:2016 MQT 18
    **Duration:** 200 thermal cycles (~7-10 days)
    """)

    # Test Configuration
    st.subheader("1. Test Configuration")

    col1, col2, col3 = st.columns(3)

    with col1:
        module_isc = st.number_input(
            "Module Isc (A)",
            min_value=5.0,
            max_value=15.0,
            value=11.0,
            step=0.1
        )
        test_current = module_isc * 1.25
        st.info(f"Test Current: {test_current:.2f} A")

    with col2:
        module_voc = st.number_input(
            "Module Voc (V)",
            min_value=30.0,
            max_value=60.0,
            value=48.0,
            step=0.5
        )

    with col3:
        num_thermal_cycles = st.number_input(
            "Thermal Cycles",
            min_value=50,
            max_value=200,
            value=200,
            step=50
        )

    # Diode I-V Curve Plotter
    st.subheader("2. Diode I-V Characteristic Curves")

    if st.button("Generate Diode I-V Data"):
        st.session_state['diode_data_generated'] = True

        # Generate synthetic I-V curves
        # Forward characteristics
        v_forward = np.linspace(0, 1.0, 200)

        # Baseline (Schottky diode)
        Is_baseline = 1e-6
        n_baseline = 1.2
        T = 298.15  # 25°C
        k = 1.380649e-23
        q = 1.602176634e-19
        Vt = (k * T) / q
        i_forward_baseline = Is_baseline * (np.exp(v_forward / (n_baseline * Vt)) - 1)

        # Post-test (slight degradation)
        Is_posttest = 1.2e-6
        n_posttest = 1.25
        i_forward_posttest = Is_posttest * (np.exp(v_forward / (n_posttest * Vt)) - 1)

        # Reverse characteristics
        v_reverse = np.linspace(0, -module_voc, 100)
        i_reverse_baseline = -1e-4 * np.ones_like(v_reverse)  # 0.1 mA leakage
        i_reverse_posttest = -2e-4 * np.ones_like(v_reverse)  # 0.2 mA leakage (degraded)

        st.session_state['v_forward'] = v_forward
        st.session_state['i_forward_baseline'] = i_forward_baseline
        st.session_state['i_forward_posttest'] = i_forward_posttest
        st.session_state['v_reverse'] = v_reverse
        st.session_state['i_reverse_baseline'] = i_reverse_baseline
        st.session_state['i_reverse_posttest'] = i_reverse_posttest

    if st.session_state.get('diode_data_generated', False):
        v_forward = st.session_state['v_forward']
        i_forward_baseline = st.session_state['i_forward_baseline']
        i_forward_posttest = st.session_state['i_forward_posttest']
        v_reverse = st.session_state['v_reverse']
        i_reverse_baseline = st.session_state['i_reverse_baseline']
        i_reverse_posttest = st.session_state['i_reverse_posttest']

        tab1, tab2, tab3 = st.tabs(["I-V Curves", "Analysis", "Thermal Performance"])

        with tab1:
            curve_type = st.radio(
                "Select Characteristic",
                ["Forward", "Reverse", "Full (Forward + Reverse)"],
                horizontal=True
            )

            fig = go.Figure()

            if curve_type in ["Forward", "Full (Forward + Reverse)"]:
                fig.add_trace(go.Scatter(
                    x=v_forward,
                    y=i_forward_baseline,
                    mode='lines',
                    name='Baseline (Forward)',
                    line=dict(color='#004E89', width=2)
                ))

                fig.add_trace(go.Scatter(
                    x=v_forward,
                    y=i_forward_posttest,
                    mode='lines',
                    name='Post-Test (Forward)',
                    line=dict(color='#FF6B35', width=2, dash='dash')
                ))

                # Mark test current point
                if HANDLER_AVAILABLE:
                    analyzer = DiodeCharacteristicAnalyzer()
                    forward_results = analyzer.analyze_forward_characteristics(
                        v_forward,
                        i_forward_baseline,
                        test_current
                    )

                    if forward_results['vf_at_test_current_v'] is not None:
                        fig.add_trace(go.Scatter(
                            x=[forward_results['vf_at_test_current_v']],
                            y=[test_current],
                            mode='markers',
                            name=f'Test Point ({test_current:.1f} A)',
                            marker=dict(size=12, color='red', symbol='star')
                        ))

            if curve_type in ["Reverse", "Full (Forward + Reverse)"]:
                fig.add_trace(go.Scatter(
                    x=v_reverse,
                    y=i_reverse_baseline * 1000,  # Convert to mA
                    mode='lines',
                    name='Baseline (Reverse)',
                    line=dict(color='#06A77D', width=2)
                ))

                fig.add_trace(go.Scatter(
                    x=v_reverse,
                    y=i_reverse_posttest * 1000,
                    mode='lines',
                    name='Post-Test (Reverse)',
                    line=dict(color='#D62828', width=2, dash='dash')
                ))

            ylabel = "Current (A)" if curve_type == "Forward" else "Current (mA)"
            fig.update_layout(
                title="Bypass Diode I-V Characteristics",
                xaxis_title="Voltage (V)",
                yaxis_title=ylabel,
                height=600,
                showlegend=True,
                hovermode='x unified'
            )

            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            if HANDLER_AVAILABLE:
                analyzer = DiodeCharacteristicAnalyzer()

                # Forward analysis
                st.markdown("**Forward Characteristic Analysis**")

                forward_baseline = analyzer.analyze_forward_characteristics(
                    v_forward,
                    i_forward_baseline,
                    test_current
                )

                forward_posttest = analyzer.analyze_forward_characteristics(
                    v_forward,
                    i_forward_posttest,
                    test_current
                )

                col1, col2, col3 = st.columns(3)

                with col1:
                    vf_base = forward_baseline['vf_at_test_current_v']
                    vf_post = forward_posttest['vf_at_test_current_v']
                    delta_vf = vf_post - vf_base if (vf_base and vf_post) else 0

                    st.metric(
                        "Vf @ Test Current",
                        f"{vf_post:.3f} V" if vf_post else "N/A",
                        f"{delta_vf:+.3f} V" if delta_vf != 0 else None
                    )

                with col2:
                    if forward_posttest['ideality_factor']:
                        st.metric("Ideality Factor (n)", f"{forward_posttest['ideality_factor']:.2f}")
                    else:
                        st.metric("Ideality Factor (n)", "N/A")

                with col3:
                    if forward_posttest['power_dissipation_w']:
                        st.metric("Power Dissipation", f"{forward_posttest['power_dissipation_w']:.2f} W")
                    else:
                        st.metric("Power Dissipation", "N/A")

                # Acceptance check
                if vf_post and vf_post <= 0.9:
                    st.success("✓ Forward voltage within acceptable limit (≤ 0.9 V)")
                elif vf_post:
                    st.error("✗ Forward voltage exceeds limit!")

                # Reverse analysis
                st.markdown("**Reverse Characteristic Analysis**")

                reverse_baseline = analyzer.analyze_reverse_characteristics(
                    v_reverse,
                    i_reverse_baseline,
                    module_voc
                )

                reverse_posttest = analyzer.analyze_reverse_characteristics(
                    v_reverse,
                    i_reverse_posttest,
                    module_voc
                )

                col1, col2 = st.columns(2)

                with col1:
                    leak_base = reverse_baseline['leakage_at_minus_voc_a']
                    leak_post = reverse_posttest['leakage_at_minus_voc_a']
                    delta_leak = leak_post - leak_base if (leak_base and leak_post) else 0

                    st.metric(
                        "Leakage @ -Voc",
                        f"{abs(leak_post)*1000:.2f} mA" if leak_post else "N/A",
                        f"{delta_leak*1000:+.2f} mA" if delta_leak != 0 else None
                    )

                with col2:
                    if reverse_posttest['breakdown_voltage_v']:
                        st.metric("Breakdown Voltage", f"{reverse_posttest['breakdown_voltage_v']:.1f} V")
                    else:
                        st.metric("Breakdown Voltage", "None Detected")

                # Acceptance check
                if leak_post and abs(leak_post) <= 0.001:
                    st.success("✓ Reverse leakage within acceptable limit (≤ 1 mA @ 25°C)")
                elif leak_post:
                    st.warning("⚠ Reverse leakage exceeds typical limit")

                # Comparison
                st.markdown("**Baseline vs Post-Test Comparison**")

                comparison = analyzer.compare_iv_curves(
                    v_forward,
                    i_forward_baseline,
                    v_forward,
                    i_forward_posttest
                )

                comp_df = pd.DataFrame({
                    'Metric': [
                        'RMS Current Difference',
                        'Max Absolute Difference',
                        'Avg Percent Difference',
                        'Degradation Acceptable'
                    ],
                    'Value': [
                        f"{comparison['rms_current_difference_a']:.4f} A",
                        f"{comparison['max_abs_current_difference_a']:.4f} A",
                        f"{comparison['avg_percent_difference']:.2f}%",
                        "Yes" if comparison['degradation_acceptable'] else "No"
                    ]
                })

                st.dataframe(comp_df, hide_index=True)

        with tab3:
            st.markdown("**Thermal Performance Analysis**")

            col1, col2, col3 = st.columns(3)

            with col1:
                vf_thermal = st.number_input(
                    "Vf during stress test (V)",
                    min_value=0.4,
                    max_value=1.0,
                    value=0.6,
                    step=0.01
                )

            with col2:
                jbox_temp = st.number_input(
                    "Junction Box Temp (°C)",
                    min_value=40.0,
                    max_value=100.0,
                    value=75.0,
                    step=1.0
                )

            with col3:
                ambient_temp = st.number_input(
                    "Ambient Temp (°C)",
                    min_value=15.0,
                    max_value=35.0,
                    value=25.0,
                    step=1.0
                )

            if HANDLER_AVAILABLE:
                analyzer = DiodeCharacteristicAnalyzer()
                thermal_results = analyzer.calculate_thermal_resistance(
                    vf_thermal,
                    test_current,
                    jbox_temp,
                    ambient_temp
                )

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Power Dissipation", f"{thermal_results['power_dissipation_w']:.2f} W")

                with col2:
                    st.metric("Temperature Rise", f"{thermal_results['temperature_rise_c']:.1f}°C")

                with col3:
                    if thermal_results['thermal_resistance_c_per_w']:
                        st.metric("Thermal Resistance",
                                f"{thermal_results['thermal_resistance_c_per_w']:.1f} °C/W")

                # Acceptance
                if thermal_results['temperature_acceptable']:
                    st.success("✓ Junction box temperature < 85°C (acceptable)")
                else:
                    st.error("✗ Junction box temperature exceeds 85°C limit!")

                # Visualization
                st.markdown("**Temperature Profile**")

                fig = go.Figure()

                categories = ['Ambient', 'Temperature\nRise', 'Junction Box']
                values = [
                    ambient_temp,
                    thermal_results['temperature_rise_c'],
                    jbox_temp
                ]
                colors = ['#004E89', '#F77F00', '#D62828' if not thermal_results['temperature_acceptable'] else '#06A77D']

                fig.add_trace(go.Bar(
                    x=categories,
                    y=values,
                    marker_color=colors,
                    text=[f"{v:.1f}°C" for v in values],
                    textposition='auto'
                ))

                fig.add_hline(y=85, line_dash="dash", line_color="red",
                            annotation_text="Max Limit (85°C)")

                fig.update_layout(
                    yaxis_title="Temperature (°C)",
                    height=400,
                    showlegend=False
                )

                st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>PV Test Protocols System | Standards: IEC 61215-2:2016</p>
    <p>For technical support, refer to protocol documentation</p>
</div>
""", unsafe_allow_html=True)
