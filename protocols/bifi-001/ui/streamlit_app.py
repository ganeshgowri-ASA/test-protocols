"""
Streamlit UI for BIFI-001 Bifacial Performance Protocol
Interactive interface for front/rear measurements and analysis
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime
from pathlib import Path
import sys

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from python.protocol import BifacialProtocol
from python.calculator import BifacialCalculator
from db.database import DatabaseManager


def init_session_state():
    """Initialize Streamlit session state"""
    if 'protocol' not in st.session_state:
        st.session_state.protocol = BifacialProtocol()
    if 'test_data' not in st.session_state:
        st.session_state.test_data = None
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = DatabaseManager()
        st.session_state.db_manager.create_tables()


def plot_iv_curve(iv_data, title="I-V Curve", show_power=True):
    """
    Plot I-V and P-V curves

    Args:
        iv_data: List of voltage-current measurement points
        title: Plot title
        show_power: Whether to show power curve

    Returns:
        Plotly figure
    """
    if not iv_data:
        return None

    df = pd.DataFrame(iv_data)

    if show_power:
        # Create subplots
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('I-V Curve', 'P-V Curve'),
            vertical_spacing=0.15
        )

        # I-V curve
        fig.add_trace(
            go.Scatter(x=df['voltage'], y=df['current'],
                      mode='lines+markers', name='Current',
                      line=dict(color='blue', width=2)),
            row=1, col=1
        )

        # P-V curve
        df['power'] = df['voltage'] * df['current']
        fig.add_trace(
            go.Scatter(x=df['voltage'], y=df['power'],
                      mode='lines+markers', name='Power',
                      line=dict(color='red', width=2)),
            row=2, col=1
        )

        # Update axes
        fig.update_xaxes(title_text="Voltage (V)", row=1, col=1)
        fig.update_yaxes(title_text="Current (A)", row=1, col=1)
        fig.update_xaxes(title_text="Voltage (V)", row=2, col=1)
        fig.update_yaxes(title_text="Power (W)", row=2, col=1)

        fig.update_layout(height=600, title_text=title, showlegend=True)
    else:
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(x=df['voltage'], y=df['current'],
                      mode='lines+markers', name='Current',
                      line=dict(color='blue', width=2))
        )
        fig.update_layout(
            title=title,
            xaxis_title="Voltage (V)",
            yaxis_title="Current (A)",
            height=400
        )

    return fig


def plot_bifacial_comparison(front_data, rear_data):
    """
    Plot front vs rear I-V curves for comparison

    Args:
        front_data: Front side I-V data
        rear_data: Rear side I-V data

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    # Front side
    df_front = pd.DataFrame(front_data)
    fig.add_trace(
        go.Scatter(x=df_front['voltage'], y=df_front['current'],
                  mode='lines+markers', name='Front Side',
                  line=dict(color='blue', width=2))
    )

    # Rear side
    df_rear = pd.DataFrame(rear_data)
    fig.add_trace(
        go.Scatter(x=df_rear['voltage'], y=df_rear['current'],
                  mode='lines+markers', name='Rear Side',
                  line=dict(color='orange', width=2))
    )

    fig.update_layout(
        title="Front vs Rear I-V Curves",
        xaxis_title="Voltage (V)",
        yaxis_title="Current (A)",
        height=500,
        showlegend=True
    )

    return fig


def metadata_form():
    """Create metadata input form"""
    st.header("1. Test Metadata")

    col1, col2 = st.columns(2)

    with col1:
        operator = st.text_input("Operator Name*", key="operator")
        facility = st.text_input("Facility", key="facility", value="PV Testing Lab")

    with col2:
        test_date = st.date_input("Test Date*", value=datetime.now(), key="test_date")
        test_time = st.time_input("Test Time*", value=datetime.now().time(), key="test_time")

    return {
        "protocol_name": "BIFI-001 Bifacial Performance",
        "standard": "IEC 60904-1-2",
        "version": "1.0.0",
        "test_date": datetime.combine(test_date, test_time).isoformat() + "Z",
        "operator": operator,
        "facility": facility
    }


def device_form():
    """Create device information form"""
    st.header("2. Device Under Test")

    col1, col2 = st.columns(2)

    with col1:
        device_id = st.text_input("Device ID*", key="device_id")
        manufacturer = st.text_input("Manufacturer*", key="manufacturer")
        model = st.text_input("Model*", key="model")
        serial_number = st.text_input("Serial Number", key="serial_number")

    with col2:
        technology = st.selectbox(
            "Technology*",
            ["mono-Si", "poly-Si", "CdTe", "CIGS", "perovskite", "other"],
            key="technology"
        )
        rated_power_front = st.number_input("Rated Power Front (W)*", min_value=0.0, key="rated_power_front")
        rated_power_rear = st.number_input("Rated Power Rear (W)", min_value=0.0, key="rated_power_rear")
        bifaciality_factor = st.number_input(
            "Bifaciality Factor (Spec)",
            min_value=0.0, max_value=1.0, value=0.70, step=0.01,
            key="bifaciality_factor"
        )

    col3, col4 = st.columns(2)
    with col3:
        area_front = st.number_input("Front Area (cm²)", min_value=0.0, value=25000.0, key="area_front")
    with col4:
        area_rear = st.number_input("Rear Area (cm²)", min_value=0.0, value=25000.0, key="area_rear")

    return {
        "device_id": device_id,
        "manufacturer": manufacturer,
        "model": model,
        "serial_number": serial_number,
        "technology": technology,
        "rated_power_front": rated_power_front,
        "rated_power_rear": rated_power_rear,
        "bifaciality_factor": bifaciality_factor,
        "area_front": area_front,
        "area_rear": area_rear
    }


def test_conditions_form():
    """Create test conditions form"""
    st.header("3. Test Conditions")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Front Side")
        front_irradiance = st.number_input("Irradiance (W/m²)*", min_value=0.0, value=1000.0, key="front_irr")
        front_tolerance = st.number_input("Tolerance (W/m²)", min_value=0.0, value=2.0, key="front_tol")
        front_spectrum = st.selectbox("Spectrum", ["AM1.5G", "AM1.5D", "AM0", "custom"], key="front_spec")

    with col2:
        st.subheader("Rear Side")
        rear_irradiance = st.number_input("Irradiance (W/m²)*", min_value=0.0, value=150.0, key="rear_irr")
        rear_tolerance = st.number_input("Tolerance (W/m²)", min_value=0.0, value=2.0, key="rear_tol")
        rear_spectrum = st.selectbox("Spectrum", ["AM1.5G", "AM1.5D", "AM0", "custom"], key="rear_spec")

    col3, col4 = st.columns(2)
    with col3:
        temperature = st.number_input("Cell Temperature (°C)*", value=25.0, key="temp")
        temp_tolerance = st.number_input("Temperature Tolerance (°C)", min_value=0.0, value=2.0, key="temp_tol")

    with col4:
        stc_conditions = st.checkbox("Standard Test Conditions (STC)", value=True, key="stc")

    return {
        "front_irradiance": {
            "value": front_irradiance,
            "tolerance": front_tolerance,
            "spectrum": front_spectrum
        },
        "rear_irradiance": {
            "value": rear_irradiance,
            "tolerance": rear_tolerance,
            "spectrum": rear_spectrum
        },
        "temperature": {
            "value": temperature,
            "tolerance": temp_tolerance
        },
        "stc_conditions": stc_conditions
    }


def iv_measurement_form(side="front"):
    """Create I-V measurement input form"""
    st.subheader(f"{side.title()} Side Measurement")

    # Option to upload CSV or manual entry
    input_method = st.radio(
        f"{side.title()} data input method",
        ["Manual Entry", "Upload CSV", "Simulate Data"],
        key=f"{side}_input_method"
    )

    iv_data = []

    if input_method == "Manual Entry":
        st.write("Enter I-V curve data points (minimum 10 points)")
        num_points = st.number_input(f"Number of points", min_value=10, value=20, key=f"{side}_num_points")

        # Create a data editor
        template_data = {
            "voltage": [i * 0.5 for i in range(int(num_points))],
            "current": [5.0 - i * 0.25 for i in range(int(num_points))]
        }
        df = pd.DataFrame(template_data)

        edited_df = st.data_editor(df, key=f"{side}_data_editor", num_rows="dynamic")
        iv_data = edited_df.to_dict('records')

    elif input_method == "Upload CSV":
        uploaded_file = st.file_uploader(
            f"Upload {side} side I-V curve CSV",
            type=['csv'],
            key=f"{side}_upload"
        )

        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.write("Preview:", df.head())
            iv_data = df.to_dict('records')

    elif input_method == "Simulate Data":
        st.info("Generating simulated I-V curve data")
        # Simulate typical bifacial I-V curve
        import numpy as np

        voc = st.number_input(f"{side} Voc (V)", value=45.0 if side == "front" else 43.0, key=f"{side}_sim_voc")
        isc = st.number_input(f"{side} Isc (A)", value=10.0 if side == "front" else 7.0, key=f"{side}_sim_isc")

        num_points = 50
        voltage = np.linspace(0, voc, num_points)
        # Simple diode equation approximation
        current = isc * (1 - (voltage / voc) ** 2)

        iv_data = [
            {"voltage": float(v), "current": float(i)}
            for v, i in zip(voltage, current)
        ]

    return iv_data


def display_results(protocol):
    """Display test results"""
    st.header("5. Test Results")

    if protocol.data is None:
        st.warning("No test data available")
        return

    measurements = protocol.data.get("measurements", {})

    # Front side results
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Front Side Results")
        front = measurements.get("front_side", {})
        if front.get("pmax"):
            st.metric("Pmax", f"{front['pmax']:.2f} W")
            st.metric("Isc", f"{front['isc']:.3f} A")
            st.metric("Voc", f"{front['voc']:.3f} V")
            st.metric("Fill Factor", f"{front['fill_factor']:.3f}")
            if front.get("efficiency"):
                st.metric("Efficiency", f"{front['efficiency']:.2f} %")

            # Plot front I-V curve
            if front.get("iv_curve"):
                fig = plot_iv_curve(front["iv_curve"], "Front Side I-V Curve")
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Rear Side Results")
        rear = measurements.get("rear_side", {})
        if rear.get("pmax"):
            st.metric("Pmax", f"{rear['pmax']:.2f} W")
            st.metric("Isc", f"{rear['isc']:.3f} A")
            st.metric("Voc", f"{rear['voc']:.3f} V")
            st.metric("Fill Factor", f"{rear['fill_factor']:.3f}")
            if rear.get("efficiency"):
                st.metric("Efficiency", f"{rear['efficiency']:.2f} %")

            # Plot rear I-V curve
            if rear.get("iv_curve"):
                fig = plot_iv_curve(rear["iv_curve"], "Rear Side I-V Curve")
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

    # Bifacial results
    st.subheader("Bifacial Performance")
    bifacial = measurements.get("bifacial_measurements", {})

    if bifacial.get("measured_bifaciality"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Bifaciality Factor", f"{bifacial['measured_bifaciality']:.3f}")
        with col2:
            st.metric("Bifacial Gain", f"{bifacial['bifacial_gain']:.2f} %")
        with col3:
            st.metric("Equiv. Efficiency", f"{bifacial['equivalent_front_efficiency']:.2f} %")

        # Comparison plot
        if front.get("iv_curve") and rear.get("iv_curve"):
            fig = plot_bifacial_comparison(front["iv_curve"], rear["iv_curve"])
            st.plotly_chart(fig, use_container_width=True)

    # Validation results
    st.subheader("Quality Control")
    qc = protocol.data.get("quality_control", {})
    checks = qc.get("validation_checks", [])

    if checks:
        for check in checks:
            status_icon = "✅" if check["status"] == "pass" else "⚠️" if check["status"] == "warning" else "❌"
            st.write(f"{status_icon} **{check['check_name']}**: {check['message']}")

    # Analysis results
    st.subheader("Analysis Results")
    analysis = protocol.data.get("analysis_results", {})

    if analysis:
        status = analysis.get("pass_fail_status", "unknown")
        status_color = "green" if status == "pass" else "orange" if status == "conditional" else "red"

        st.markdown(f"**Overall Status:** :{status_color}[{status.upper()}]")

        deviations = analysis.get("deviations", [])
        if deviations:
            st.write("**Deviations from Specification:**")
            df_dev = pd.DataFrame(deviations)
            st.dataframe(df_dev, use_container_width=True)

        recommendations = analysis.get("recommendations", [])
        if recommendations:
            st.write("**Recommendations:**")
            for rec in recommendations:
                st.write(f"- {rec}")


def main():
    """Main Streamlit application"""
    st.set_page_config(page_title="BIFI-001 Bifacial Performance", layout="wide")

    st.title("🌞 BIFI-001 Bifacial Performance Protocol")
    st.markdown("*IEC 60904-1-2 Compliant Testing Interface*")

    init_session_state()
    protocol = st.session_state.protocol

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Page",
        ["New Test", "View Results", "Database", "Export"]
    )

    if page == "New Test":
        # Step-by-step test creation
        metadata = metadata_form()
        device_info = device_form()
        test_conditions = test_conditions_form()

        if st.button("Initialize Test"):
            try:
                st.session_state.test_data = protocol.create_test(metadata, device_info, test_conditions)
                st.success("Test initialized successfully!")
            except Exception as e:
                st.error(f"Error initializing test: {str(e)}")

        st.header("4. I-V Measurements")

        col1, col2 = st.columns(2)

        with col1:
            front_iv = iv_measurement_form("front")
            if st.button("Add Front Measurement") and front_iv:
                try:
                    front_irr = test_conditions["front_irradiance"]["value"]
                    area = device_info.get("area_front", 25000)
                    params = protocol.add_iv_measurement("front", front_iv, front_irr, area)
                    st.success(f"Front measurement added! Pmax = {params.pmax:.2f} W")
                except Exception as e:
                    st.error(f"Error adding front measurement: {str(e)}")

        with col2:
            rear_iv = iv_measurement_form("rear")
            if st.button("Add Rear Measurement") and rear_iv:
                try:
                    rear_irr = test_conditions["rear_irradiance"]["value"]
                    area = device_info.get("area_rear", 25000)
                    params = protocol.add_iv_measurement("rear", rear_iv, rear_irr, area)
                    st.success(f"Rear measurement added! Pmax = {params.pmax:.2f} W")
                except Exception as e:
                    st.error(f"Error adding rear measurement: {str(e)}")

        # Calculate bifacial parameters
        if st.button("Calculate Bifacial Parameters"):
            try:
                results = protocol.calculate_bifacial_parameters()
                st.success("Bifacial parameters calculated!")
                st.json(results)
            except Exception as e:
                st.error(f"Error calculating bifacial parameters: {str(e)}")

        # Run validation
        if st.button("Run Validation"):
            try:
                validation_results = protocol.run_validation()
                if validation_results["overall_valid"]:
                    st.success("✅ All validation checks passed!")
                else:
                    st.warning("⚠️ Some validation checks failed")
                    for error in validation_results["errors"]:
                        st.error(error)
            except Exception as e:
                st.error(f"Error running validation: {str(e)}")

        # Analyze performance
        if st.button("Analyze Performance"):
            try:
                analysis = protocol.analyze_performance()
                st.success("Performance analysis complete!")
            except Exception as e:
                st.error(f"Error analyzing performance: {str(e)}")

    elif page == "View Results":
        display_results(protocol)

    elif page == "Database":
        st.header("Database Management")

        tab1, tab2 = st.tabs(["Save Test", "Load Test"])

        with tab1:
            if st.button("Save Current Test to Database"):
                try:
                    db = st.session_state.db_manager
                    test_record = db.create_test(protocol.data)
                    st.success(f"Test saved with ID: {test_record.id}")
                except Exception as e:
                    st.error(f"Error saving to database: {str(e)}")

        with tab2:
            device_id = st.text_input("Search by Device ID")
            if st.button("Search"):
                db = st.session_state.db_manager
                tests = db.get_tests_by_device(device_id)
                if tests:
                    st.write(f"Found {len(tests)} tests")
                    for test in tests:
                        st.write(f"Test ID: {test.id}, Date: {test.test_date}, Status: {test.pass_fail_status}")
                else:
                    st.info("No tests found")

    elif page == "Export":
        st.header("Export Test Data")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Export to JSON"):
                if protocol.data:
                    json_str = json.dumps(protocol.data, indent=2)
                    st.download_button(
                        label="Download JSON",
                        data=json_str,
                        file_name=f"bifi_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                else:
                    st.warning("No test data to export")

        with col2:
            if st.button("Generate Report"):
                if protocol.data:
                    report_data = protocol.generate_report_data()
                    st.json(report_data)
                else:
                    st.warning("No test data available for report")


if __name__ == "__main__":
    main()
