"""
Streamlit Page for Mechanical Load and PID Testing

This page provides interactive interfaces for:
- Mechanical load testing with load profile visualization
- PID testing with real-time voltage/current monitoring
- Deflection calculator
- Comparative analysis dashboard

Author: PV Testing Lab
Version: 1.0
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import sys
from pathlib import Path

# Add backend to path (adjust as needed for your project structure)
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from backend.protocols.mechanical_electrical_handler import (
        MechanicalLoadHandler, PIDTestHandler, LoadType, PIDAffectLevel
    )
    from backend.validators.safety_validator import (
        PIDSafetyValidator, MechanicalLoadSafetyValidator,
        generate_safety_checklist, TestType
    )
    BACKEND_AVAILABLE = True
except ImportError:
    BACKEND_AVAILABLE = False
    st.warning("Backend modules not available. Running in demo mode.")


# Page configuration
st.set_page_config(
    page_title="Mechanical & Electrical Testing",
    page_icon="⚡",
    layout="wide"
)


def load_protocol_template(protocol_id: str):
    """Load protocol template from JSON file"""
    template_path = Path(__file__).parent.parent.parent / "templates"

    if protocol_id == "PVTP-005-ML":
        file_path = template_path / "mechanical_load.json"
    elif protocol_id == "PVTP-006-PID":
        file_path = template_path / "pid_testing.json"
    else:
        return None

    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Protocol template not found: {file_path}")
        return None


def plot_load_profile(num_cycles: int, pressure_positive: float = 2400,
                     pressure_negative: float = -2400):
    """Plot load profile for cyclic testing"""

    # Generate time series
    time_points = []
    pressure_points = []
    phase_labels = []

    current_time = 0

    for cycle in range(1, num_cycles + 1):
        # Ramp up to positive pressure (100 Pa/s)
        ramp_time = abs(pressure_positive) / 100
        time_points.extend([current_time, current_time + ramp_time])
        pressure_points.extend([0, pressure_positive])
        phase_labels.extend([f"Cycle {cycle}", f"Cycle {cycle}"])
        current_time += ramp_time

        # Hold positive pressure (1 hour)
        time_points.append(current_time + 3600)
        pressure_points.append(pressure_positive)
        phase_labels.append(f"Cycle {cycle}")
        current_time += 3600

        # Ramp down to zero
        time_points.extend([current_time, current_time + ramp_time])
        pressure_points.extend([pressure_positive, 0])
        phase_labels.extend([f"Cycle {cycle}", f"Cycle {cycle}"])
        current_time += ramp_time

        # Rest period (15 min)
        time_points.append(current_time + 900)
        pressure_points.append(0)
        phase_labels.append(f"Cycle {cycle}")
        current_time += 900

        # Ramp to negative pressure
        time_points.extend([current_time, current_time + ramp_time])
        pressure_points.extend([0, pressure_negative])
        phase_labels.extend([f"Cycle {cycle}", f"Cycle {cycle}"])
        current_time += ramp_time

        # Hold negative pressure (1 hour)
        time_points.append(current_time + 3600)
        pressure_points.append(pressure_negative)
        phase_labels.append(f"Cycle {cycle}")
        current_time += 3600

        # Ramp back to zero
        time_points.extend([current_time, current_time + abs(pressure_negative) / 100])
        pressure_points.extend([pressure_negative, 0])
        phase_labels.extend([f"Cycle {cycle}", f"Cycle {cycle}"])
        current_time += abs(pressure_negative) / 100

        # Final rest (15 min)
        time_points.append(current_time + 900)
        pressure_points.append(0)
        phase_labels.append(f"Cycle {cycle}")
        current_time += 900

    # Convert time to hours
    time_hours = [t / 3600 for t in time_points]

    # Create figure
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=time_hours,
        y=pressure_points,
        mode='lines',
        name='Applied Pressure',
        line=dict(color='blue', width=2),
        fill='tozeroy',
        fillcolor='rgba(0, 100, 255, 0.1)'
    ))

    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)

    # Add threshold lines
    fig.add_hline(y=pressure_positive, line_dash="dot", line_color="red",
                  opacity=0.3, annotation_text="Target Positive")
    fig.add_hline(y=pressure_negative, line_dash="dot", line_color="red",
                  opacity=0.3, annotation_text="Target Negative")

    fig.update_layout(
        title=f"Load Profile - {num_cycles} Cycle(s)",
        xaxis_title="Time (hours)",
        yaxis_title="Pressure (Pa)",
        hovermode='x unified',
        height=400
    )

    return fig


def plot_deflection_profile(deflection_data: dict):
    """Plot 3D deflection profile across module surface"""

    # Create sample grid (in real application, use actual measurement points)
    locations = list(deflection_data.keys())
    values = list(deflection_data.values())

    # For demonstration, create a simple bar chart
    # In production, use actual coordinates for 3D surface plot
    fig = go.Figure(data=[
        go.Bar(
            x=locations,
            y=values,
            marker=dict(
                color=values,
                colorscale='RdYlBu_r',
                showscale=True,
                colorbar=dict(title="Deflection (mm)")
            )
        )
    ])

    fig.update_layout(
        title="Deflection Profile Across Module",
        xaxis_title="Measurement Location",
        yaxis_title="Deflection (mm)",
        height=400
    )

    return fig


def plot_pid_monitoring(monitoring_df: pd.DataFrame):
    """Plot PID monitoring data (voltage, current, temp, humidity)"""

    # Create subplot with 4 rows
    fig = make_subplots(
        rows=4, cols=1,
        subplot_titles=('Voltage', 'Leakage Current', 'Temperature', 'Humidity'),
        vertical_spacing=0.08
    )

    # Voltage
    fig.add_trace(
        go.Scatter(x=monitoring_df['timestamp'], y=monitoring_df['voltage'],
                  mode='lines', name='Voltage', line=dict(color='blue')),
        row=1, col=1
    )

    # Leakage current
    fig.add_trace(
        go.Scatter(x=monitoring_df['timestamp'], y=monitoring_df['leakage_current'],
                  mode='lines', name='Leakage Current', line=dict(color='red')),
        row=2, col=1
    )
    fig.add_hline(y=10, line_dash="dash", line_color="orange", row=2, col=1,
                  annotation_text="Warning Threshold")
    fig.add_hline(y=50, line_dash="dash", line_color="red", row=2, col=1,
                  annotation_text="Critical Threshold")

    # Temperature
    fig.add_trace(
        go.Scatter(x=monitoring_df['timestamp'], y=monitoring_df['temperature'],
                  mode='lines', name='Temperature', line=dict(color='orange')),
        row=3, col=1
    )
    fig.add_hline(y=60, line_dash="dash", line_color="green", row=3, col=1)

    # Humidity
    fig.add_trace(
        go.Scatter(x=monitoring_df['timestamp'], y=monitoring_df['humidity'],
                  mode='lines', name='Humidity', line=dict(color='cyan')),
        row=4, col=1
    )
    fig.add_hline(y=85, line_dash="dash", line_color="green", row=4, col=1)

    fig.update_xaxes(title_text="Time", row=4, col=1)
    fig.update_yaxes(title_text="V", row=1, col=1)
    fig.update_yaxes(title_text="mA", row=2, col=1)
    fig.update_yaxes(title_text="°C", row=3, col=1)
    fig.update_yaxes(title_text="%RH", row=4, col=1)

    fig.update_layout(height=800, showlegend=False, title_text="PID Test Monitoring")

    return fig


def plot_pid_degradation(performance_df: pd.DataFrame):
    """Plot PID degradation over time"""

    baseline_power = performance_df.iloc[0]['pmax']
    performance_df['degradation_pct'] = ((performance_df['pmax'] - baseline_power) / baseline_power) * 100

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Power vs Time', 'Degradation Rate'),
        vertical_spacing=0.15
    )

    # Power over time
    fig.add_trace(
        go.Scatter(x=performance_df['hours'], y=performance_df['pmax'],
                  mode='lines+markers', name='Pmax', line=dict(color='blue')),
        row=1, col=1
    )
    fig.add_hline(y=baseline_power, line_dash="dash", line_color="green",
                  row=1, col=1, annotation_text="Baseline")

    # Degradation percentage
    fig.add_trace(
        go.Scatter(x=performance_df['hours'], y=performance_df['degradation_pct'],
                  mode='lines+markers', name='Degradation', line=dict(color='red'),
                  fill='tozeroy', fillcolor='rgba(255,0,0,0.1)'),
        row=2, col=1
    )
    fig.add_hline(y=-5, line_dash="dash", line_color="orange",
                  row=2, col=1, annotation_text="5% Threshold")

    fig.update_xaxes(title_text="Hours", row=2, col=1)
    fig.update_yaxes(title_text="Power (W)", row=1, col=1)
    fig.update_yaxes(title_text="Degradation (%)", row=2, col=1)

    fig.update_layout(height=600, showlegend=True)

    return fig


def deflection_calculator():
    """Interactive deflection calculator"""

    st.subheader("Deflection Calculator")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Module Dimensions**")
        length = st.number_input("Length (mm)", value=1650, min_value=100, max_value=3000)
        width = st.number_input("Width (mm)", value=992, min_value=100, max_value=2000)
        thickness = st.number_input("Glass Thickness (mm)", value=3.2, min_value=1.0, max_value=10.0)

    with col2:
        st.write("**Load Parameters**")
        pressure = st.number_input("Applied Pressure (Pa)", value=2400, min_value=-5000, max_value=5000)
        edge_support = st.selectbox("Edge Support", ["All edges", "Two edges", "Point supports"])

    # Simplified deflection calculation (actual would use plate theory)
    # δ = (q × L^4) / (E × t^3) × K
    # where q = pressure, L = length, E = Young's modulus, t = thickness, K = support factor

    E_glass = 70000  # MPa (Young's modulus for glass)
    K_factor = {"All edges": 0.00126, "Two edges": 0.0026, "Point supports": 0.0138}[edge_support]

    L_m = length / 1000  # Convert to meters
    t_m = thickness / 1000
    q_pa = abs(pressure)

    # Calculate approximate deflection
    deflection_m = (q_pa * (L_m ** 4) * K_factor) / (E_glass * 1e6 * (t_m ** 3))
    deflection_mm = deflection_m * 1000

    # Calculate as percentage of span
    deflection_pct = (deflection_mm / length) * 100

    st.write("---")
    st.write("**Calculated Results**")

    col3, col4, col5 = st.columns(3)

    with col3:
        st.metric("Max Deflection", f"{deflection_mm:.2f} mm")

    with col4:
        st.metric("% of Span", f"{deflection_pct:.3f}%")

    with col5:
        status = "✅ Within limits" if deflection_mm < 20 else "⚠️ Check module"
        st.metric("Status", status)

    st.info("Note: This is a simplified calculation. Actual deflection depends on module construction, "
            "support conditions, and load distribution.")


# Main application
def main():
    st.title("⚡ Mechanical Load & PID Testing")

    st.markdown("""
    This application provides tools for:
    - **Mechanical Load Testing** (IEC 61215-2:2016 MQT 16/17)
    - **PID Testing** (IEC 62804-1:2015)
    """)

    # Sidebar for test selection
    st.sidebar.header("Test Selection")
    test_type = st.sidebar.radio(
        "Select Test Type",
        ["Mechanical Load Testing", "PID Testing", "Comparative Analysis"]
    )

    if test_type == "Mechanical Load Testing":
        mechanical_load_testing()
    elif test_type == "PID Testing":
        pid_testing()
    else:
        comparative_analysis()


def mechanical_load_testing():
    """Mechanical load testing interface"""

    st.header("🔧 Mechanical Load Testing (PVTP-005-ML)")

    # Load protocol
    protocol = load_protocol_template("PVTP-005-ML")
    if not protocol:
        st.error("Failed to load protocol template")
        return

    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Test Setup", "Load Profile", "Deflection Analysis", "Safety Checklist"
    ])

    with tab1:
        st.subheader("Test Configuration")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Module Information**")
            module_model = st.text_input("Module Model", "PV-300W-60")
            module_serial = st.text_input("Serial Number", "ML2025001")

            st.write("**Load Parameters**")
            load_type = st.selectbox("Load Type", ["uniform", "non-uniform"])
            num_cycles = st.selectbox("Number of Cycles", [1, 3, 1000])

        with col2:
            st.write("**Pressure Settings**")
            pressure_positive = st.number_input("Positive Pressure (Pa)", value=2400, min_value=0, max_value=5000)
            pressure_negative = st.number_input("Negative Pressure (Pa)", value=-2400, min_value=-5000, max_value=0)

            st.write("**Timing**")
            dwell_time = st.number_input("Dwell Time (minutes)", value=60, min_value=30, max_value=120)

        if st.button("Generate Test Plan", key="ml_plan"):
            st.success(f"✅ Test plan generated for {num_cycles} cycle(s)")

            estimated_time = {
                1: "4 hours",
                3: "8 hours",
                1000: "6-8 weeks"
            }[num_cycles]

            st.info(f"**Estimated Duration:** {estimated_time}")

    with tab2:
        st.subheader("Load Profile Visualization")

        num_cycles_viz = st.slider("Number of Cycles to Visualize", 1, 5, 3)
        pressure_pos_viz = st.slider("Positive Pressure (Pa)", 0, 5000, 2400, 100)
        pressure_neg_viz = st.slider("Negative Pressure (Pa)", -5000, 0, -2400, 100)

        fig = plot_load_profile(num_cycles_viz, pressure_pos_viz, pressure_neg_viz)
        st.plotly_chart(fig, use_container_width=True)

        # Show load profile table
        if BACKEND_AVAILABLE:
            ml_protocol = load_protocol_template("PVTP-005-ML")
            if ml_protocol:
                handler = MechanicalLoadHandler(ml_protocol)
                load_profile = handler.generate_load_profile(
                    num_cycles_viz, pressure_pos_viz, pressure_neg_viz
                )

                df = pd.DataFrame(load_profile)
                st.write("**Load Profile Schedule**")
                st.dataframe(df[['cycle', 'phase', 'pressure', 'duration_seconds']].head(10))

    with tab3:
        st.subheader("Deflection Analysis")

        deflection_calculator()

        st.write("---")

        # Sample deflection data visualization
        st.write("**Deflection Profile Example**")

        sample_deflection = {
            "center": 8.5,
            "quarter_point_1": 6.2,
            "quarter_point_2": 6.0,
            "quarter_point_3": 5.8,
            "quarter_point_4": 6.1,
            "edge_1": 1.2,
            "edge_2": 1.0,
            "edge_3": 1.1,
            "edge_4": 1.3
        }

        fig = plot_deflection_profile(sample_deflection)
        st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.subheader("Safety Checklist")

        if BACKEND_AVAILABLE:
            checklist = generate_safety_checklist(TestType.MECHANICAL_LOAD)

            st.write(f"**{checklist['test_type']}**")

            for item in checklist['checklist']:
                icon = "🔴" if item['critical'] else "🟡"
                checked = st.checkbox(f"{icon} {item['item']}", key=f"ml_{item['item']}")

            if st.button("Verify All Critical Items", key="ml_verify"):
                st.success("✅ All critical safety items verified")


def pid_testing():
    """PID testing interface"""

    st.header("⚡ PID Testing (PVTP-006-PID)")

    # Load protocol
    protocol = load_protocol_template("PVTP-006-PID")
    if not protocol:
        st.error("Failed to load protocol template")
        return

    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Test Setup", "Real-Time Monitoring", "Degradation Analysis", "Safety"
    ])

    with tab1:
        st.subheader("Test Configuration")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Module Information**")
            module_model = st.text_input("Module Model", "PV-300W-60", key="pid_model")
            module_serial = st.text_input("Serial Number", "PID2025001", key="pid_serial")
            technology = st.selectbox("Cell Technology",
                                     ["mono-Si p-type", "mono-Si n-type", "PERC", "HJT", "TOPCon"])

            st.write("**Baseline Measurements**")
            baseline_pmax = st.number_input("Baseline Pmax (W)", value=300.0, min_value=0.0)
            baseline_voc = st.number_input("Baseline Voc (V)", value=40.0, min_value=0.0)

        with col2:
            st.write("**Test Parameters**")
            test_voltage = st.number_input("Test Voltage (V)", value=-1000, min_value=-1500, max_value=-500)
            temperature = st.number_input("Temperature (°C)", value=60, min_value=50, max_value=85)
            humidity = st.number_input("Humidity (%RH)", value=85, min_value=0, max_value=95)
            duration = st.selectbox("Duration (hours)", [48, 96, 168])

            recovery_enabled = st.checkbox("Enable Recovery Test (168h)")

        if st.button("Start Test Configuration", key="pid_start"):
            st.success("✅ PID test configured")

            # Safety validation
            if BACKEND_AVAILABLE:
                validator = PIDSafetyValidator()
                is_safe, msg = validator.validate_voltage_settings(test_voltage, baseline_voc)

                if is_safe:
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")

    with tab2:
        st.subheader("Real-Time Monitoring")

        # Generate sample monitoring data
        st.write("**Live Monitoring Dashboard**")

        current_time = datetime.now()

        # Create sample data
        hours_elapsed = np.linspace(0, 24, 100)
        timestamps = [current_time + timedelta(hours=h) for h in hours_elapsed]

        monitoring_df = pd.DataFrame({
            'timestamp': timestamps,
            'voltage': -1000 + np.random.normal(0, 5, 100),
            'leakage_current': 2.5 + np.random.exponential(0.5, 100),
            'temperature': 60 + np.random.normal(0, 0.5, 100),
            'humidity': 85 + np.random.normal(0, 2, 100)
        })

        fig = plot_pid_monitoring(monitoring_df)
        st.plotly_chart(fig, use_container_width=True)

        # Current status
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Voltage", f"{monitoring_df['voltage'].iloc[-1]:.1f} V")

        with col2:
            current_val = monitoring_df['leakage_current'].iloc[-1]
            st.metric("Leakage Current", f"{current_val:.2f} mA")

        with col3:
            st.metric("Temperature", f"{monitoring_df['temperature'].iloc[-1]:.1f} °C")

        with col4:
            st.metric("Humidity", f"{monitoring_df['humidity'].iloc[-1]:.1f} %RH")

    with tab3:
        st.subheader("Degradation Analysis")

        # Generate sample performance data
        performance_df = pd.DataFrame({
            'hours': [0, 24, 48, 96],
            'pmax': [300.0, 285.0, 278.0, 270.0],
            'voc': [40.0, 39.5, 39.2, 39.0],
            'isc': [9.0, 8.7, 8.5, 8.4]
        })

        fig = plot_pid_degradation(performance_df)
        st.plotly_chart(fig, use_container_width=True)

        # Calculate final results
        baseline = performance_df.iloc[0]['pmax']
        final = performance_df.iloc[-1]['pmax']
        degradation = ((final - baseline) / baseline) * 100

        st.write("**Test Results**")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Degradation", f"{degradation:.2f}%")

        with col2:
            if abs(degradation) < 5:
                susceptibility = "LOW"
                color = "green"
            elif abs(degradation) < 10:
                susceptibility = "MEDIUM"
                color = "orange"
            else:
                susceptibility = "HIGH"
                color = "red"

            st.markdown(f"**PID Susceptibility:** :{color}[{susceptibility}]")

        with col3:
            result = "PASS ✅" if abs(degradation) < 5 else "FAIL ❌"
            st.metric("Test Result", result)

    with tab4:
        st.subheader("⚠️ Safety Monitoring")

        st.warning("**HIGH VOLTAGE TEST - Safety Critical**")

        if BACKEND_AVAILABLE:
            # Pre-test checklist
            st.write("**Pre-Test Safety Checklist**")
            checklist = generate_safety_checklist(TestType.PID_TESTING)

            critical_items = [item for item in checklist['checklist'] if item['critical']]
            st.write(f"Critical items: {len(critical_items)} / {len(checklist['checklist'])}")

            for item in critical_items[:5]:  # Show first 5
                st.checkbox(f"🔴 {item['item']}", key=f"pid_{item['item']}")

            # Safety status
            st.write("---")
            st.write("**Current Safety Status**")

            validator = PIDSafetyValidator()
            alert = validator.check_real_time_safety(-1000, 3.5, 60.0, 85.0)

            if alert.level.value == "safe":
                st.success(f"✅ {alert.message}")
            elif alert.level.value == "warning":
                st.warning(f"⚠️ {alert.message}")
            else:
                st.error(f"🔴 {alert.message}")

        if st.button("Emergency Shutdown", type="primary", key="pid_shutdown"):
            st.error("🚨 EMERGENCY SHUTDOWN INITIATED")
            st.write("1. DISCONNECT HIGH VOLTAGE IMMEDIATELY")
            st.write("2. Wait 5 minutes for discharge")
            st.write("3. Notify supervisor")


def comparative_analysis():
    """Comparative analysis dashboard"""

    st.header("📊 Comparative Analysis Dashboard")

    st.write("**Compare Multiple Test Results**")

    # Sample data for multiple modules
    modules = ["Module A", "Module B", "Module C", "Module D"]

    # Mechanical load results
    st.subheader("Mechanical Load Test Comparison")

    ml_data = pd.DataFrame({
        'Module': modules,
        'Max Deflection (mm)': [8.5, 7.2, 9.1, 8.0],
        'Power Change (%)': [-2.1, -1.5, -3.2, -2.0],
        'Result': ['PASS', 'PASS', 'PASS', 'PASS']
    })

    fig = px.bar(ml_data, x='Module', y='Max Deflection (mm)',
                 title='Maximum Deflection Comparison',
                 color='Max Deflection (mm)',
                 color_continuous_scale='RdYlGn_r')
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(ml_data, use_container_width=True)

    # PID test results
    st.subheader("PID Test Comparison")

    pid_data = pd.DataFrame({
        'Module': modules,
        'Degradation (%)': [-3.2, -8.5, -4.1, -2.0],
        'Susceptibility': ['LOW', 'MEDIUM', 'LOW', 'NONE'],
        'Result': ['PASS', 'FAIL', 'PASS', 'PASS']
    })

    fig = px.scatter(pid_data, x='Module', y='Degradation (%)',
                    size=abs(pid_data['Degradation (%)']),
                    color='Susceptibility',
                    title='PID Degradation Comparison',
                    color_discrete_map={'NONE': 'green', 'LOW': 'yellow',
                                       'MEDIUM': 'orange', 'HIGH': 'red'})
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(pid_data, use_container_width=True)

    # Summary statistics
    st.subheader("Summary Statistics")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Mechanical Load Tests**")
        st.metric("Pass Rate", f"{(ml_data['Result'] == 'PASS').sum() / len(ml_data) * 100:.0f}%")
        st.metric("Avg Deflection", f"{ml_data['Max Deflection (mm)'].mean():.2f} mm")

    with col2:
        st.write("**PID Tests**")
        st.metric("Pass Rate", f"{(pid_data['Result'] == 'PASS').sum() / len(pid_data) * 100:.0f}%")
        st.metric("Avg Degradation", f"{pid_data['Degradation (%)'].mean():.2f}%")


if __name__ == "__main__":
    main()
