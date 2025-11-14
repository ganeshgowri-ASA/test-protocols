"""
GenSpark/Streamlit UI for WIND-001 Wind Load Test Protocol
Interactive web interface for conducting wind load tests
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from pathlib import Path
import json
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from protocols.wind_001 import (
    WindLoadTest,
    ElectricalPerformance,
    CycleMeasurement,
    TestStatus,
    LoadType
)


# Page configuration
st.set_page_config(
    page_title="WIND-001 Wind Load Test",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded"
)


def init_session_state():
    """Initialize session state variables"""
    if 'protocol' not in st.session_state:
        st.session_state.protocol = WindLoadTest()
    if 'test_initialized' not in st.session_state:
        st.session_state.test_initialized = False
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0
    if 'cycle_count' not in st.session_state:
        st.session_state.cycle_count = 0


def render_sidebar():
    """Render sidebar navigation and test progress"""
    st.sidebar.title("🌬️ WIND-001")
    st.sidebar.markdown("### Wind Load Test Protocol")
    st.sidebar.divider()

    # Test progress
    if st.session_state.test_initialized:
        st.sidebar.markdown("### Test Progress")
        steps = [
            "Pre-test Setup",
            "Pre-test Measurements",
            "Load Testing",
            "Post-test Measurements",
            "Results Analysis",
            "Report Generation"
        ]
        progress = st.session_state.current_step / len(steps)
        st.sidebar.progress(progress)
        st.sidebar.markdown(f"**Current Step:** {steps[st.session_state.current_step]}")
        st.sidebar.divider()

    # Protocol information
    st.sidebar.markdown("### Protocol Info")
    st.sidebar.markdown(f"**Version:** {WindLoadTest.VERSION}")
    st.sidebar.markdown(f"**Standards:**")
    st.sidebar.markdown("- IEC 61215-2:2021")
    st.sidebar.markdown("- IEC 61730-2")
    st.sidebar.markdown("- UL 1703")


def render_test_initialization():
    """Render test initialization form"""
    st.header("📋 Test Initialization")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Test Metadata")
        test_id = st.text_input("Test ID*", value=f"WIND-001-{datetime.now().strftime('%Y%m%d')}-001")
        operator = st.text_input("Operator Name*", value="")
        standard = st.selectbox(
            "Testing Standard*",
            ["IEC 61215-2:2021", "IEC 61730", "UL 1703", "IEC 61215"]
        )
        equipment_id = st.text_input("Equipment ID", value="WT-001")
        calibration_date = st.date_input("Last Calibration Date", value=datetime.now())

        st.subheader("Test Parameters")
        load_type = st.selectbox("Load Type*", ["positive", "negative", "cyclic"])
        pressure = st.number_input("Pressure (Pa)*", min_value=0, max_value=10000, value=2400, step=100)
        duration = st.number_input("Cycle Duration (seconds)*", min_value=1, max_value=300, value=60)
        cycles = st.number_input("Number of Cycles*", min_value=1, max_value=100, value=3)
        temperature = st.number_input("Temperature (°C)", min_value=-40, max_value=85, value=25)
        humidity = st.number_input("Humidity (%)", min_value=0, max_value=100, value=50)

    with col2:
        st.subheader("Sample Information")
        sample_id = st.text_input("Sample ID*", value="")
        manufacturer = st.text_input("Manufacturer*", value="")
        model = st.text_input("Model Number*", value="")
        serial_number = st.text_input("Serial Number", value="")
        technology = st.selectbox(
            "Technology",
            ["mono-Si", "poly-Si", "thin-film", "CIGS", "CdTe", "perovskite"]
        )
        rated_power = st.number_input("Rated Power (W)", min_value=0.0, value=400.0, step=10.0)

        st.subheader("Module Dimensions")
        col_dim1, col_dim2, col_dim3 = st.columns(3)
        with col_dim1:
            length = st.number_input("Length (mm)", value=1755.0)
        with col_dim2:
            width = st.number_input("Width (mm)", value=1038.0)
        with col_dim3:
            thickness = st.number_input("Thickness (mm)", value=35.0)

        mounting = st.selectbox(
            "Mounting Configuration",
            ["fixed_tilt", "tracker", "flat_roof", "ground_mount"]
        )

    st.divider()

    if st.button("Initialize Test", type="primary", use_container_width=True):
        if not all([test_id, operator, sample_id, manufacturer, model]):
            st.error("Please fill in all required fields marked with *")
        else:
            # Initialize test
            st.session_state.protocol.initialize_test(
                test_metadata={
                    "test_id": test_id,
                    "operator": operator,
                    "standard": standard,
                    "equipment_id": equipment_id,
                    "calibration_date": calibration_date.isoformat()
                },
                sample_info={
                    "sample_id": sample_id,
                    "manufacturer": manufacturer,
                    "model": model,
                    "serial_number": serial_number,
                    "technology": technology,
                    "rated_power": rated_power,
                    "dimensions": {
                        "length": length,
                        "width": width,
                        "thickness": thickness
                    }
                },
                test_parameters={
                    "load_type": load_type,
                    "pressure": pressure,
                    "duration": duration,
                    "cycles": cycles,
                    "temperature": temperature,
                    "humidity": humidity,
                    "mounting_configuration": mounting
                }
            )
            st.session_state.test_initialized = True
            st.session_state.current_step = 1
            st.success("Test initialized successfully!")
            st.rerun()


def render_pre_test_measurements():
    """Render pre-test measurements form"""
    st.header("📊 Pre-test Measurements")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Visual Inspection")
        visual_inspection = st.text_area(
            "Pre-test Visual Inspection Notes",
            placeholder="Describe any visible defects, damage, or anomalies...",
            height=150
        )

        st.subheader("Insulation Resistance")
        insulation_resistance = st.number_input(
            "Insulation Resistance (MΩ)",
            min_value=0.0,
            value=500.0,
            step=10.0
        )

    with col2:
        st.subheader("Electrical Performance (I-V Curve)")
        voc = st.number_input("Open Circuit Voltage Voc (V)", min_value=0.0, value=48.5, step=0.1)
        isc = st.number_input("Short Circuit Current Isc (A)", min_value=0.0, value=10.2, step=0.1)
        vmp = st.number_input("Voltage at Max Power Vmp (V)", min_value=0.0, value=40.0, step=0.1)
        imp = st.number_input("Current at Max Power Imp (A)", min_value=0.0, value=10.0, step=0.1)

        pmax = vmp * imp
        st.metric("Maximum Power Pmax", f"{pmax:.2f} W")

    st.divider()

    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if st.button("⬅️ Back"):
            st.session_state.current_step = 0
            st.rerun()
    with col_btn2:
        if st.button("Save & Continue ➡️", type="primary", use_container_width=True):
            if not visual_inspection:
                st.error("Please provide visual inspection notes")
            else:
                st.session_state.protocol.record_pre_test_measurements(
                    visual_inspection=visual_inspection,
                    electrical_performance=ElectricalPerformance(
                        voc=voc, isc=isc, vmp=vmp, imp=imp, pmax=pmax
                    ),
                    insulation_resistance=insulation_resistance
                )
                st.session_state.current_step = 2
                st.success("Pre-test measurements recorded!")
                st.rerun()


def render_load_testing():
    """Render load testing interface"""
    st.header("🌪️ Load Testing")

    params = st.session_state.protocol.test_data["test_parameters"]
    total_cycles = params["cycles"]

    # Progress indicator
    st.progress(st.session_state.cycle_count / total_cycles, text=f"Cycle {st.session_state.cycle_count}/{total_cycles}")

    if st.session_state.cycle_count < total_cycles:
        st.subheader(f"Cycle {st.session_state.cycle_count + 1} of {total_cycles}")

        col1, col2 = st.columns(2)

        with col1:
            st.info(f"**Target Pressure:** {params['pressure']} Pa")
            st.info(f"**Load Type:** {params['load_type'].upper()}")
            st.info(f"**Duration:** {params['duration']} seconds")

            actual_pressure = st.number_input(
                "Actual Pressure (Pa)",
                min_value=0.0,
                value=float(params['pressure']),
                step=10.0
            )

            deflection_center = st.number_input(
                "Deflection at Center (mm)",
                min_value=0.0,
                value=0.0,
                step=0.1
            )

        with col2:
            st.subheader("Edge Deflections (mm)")
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                edge1 = st.number_input("Edge 1", min_value=0.0, value=0.0, step=0.1, key="edge1")
                edge2 = st.number_input("Edge 2", min_value=0.0, value=0.0, step=0.1, key="edge2")
            with col_e2:
                edge3 = st.number_input("Edge 3", min_value=0.0, value=0.0, step=0.1, key="edge3")
                edge4 = st.number_input("Edge 4", min_value=0.0, value=0.0, step=0.1, key="edge4")

            observations = st.text_area(
                "Observations",
                placeholder="Any unusual behavior, sounds, or visual changes...",
                height=100
            )

        st.divider()

        if st.button("Record Cycle Measurement", type="primary", use_container_width=True):
            measurement = CycleMeasurement(
                cycle_number=st.session_state.cycle_count + 1,
                timestamp=datetime.now().isoformat(),
                actual_pressure=actual_pressure,
                deflection_center=deflection_center,
                deflection_edges=[edge1, edge2, edge3, edge4],
                observations=observations
            )
            st.session_state.protocol.record_cycle_measurement(measurement)
            st.session_state.cycle_count += 1
            st.success(f"Cycle {st.session_state.cycle_count} recorded!")
            st.rerun()
    else:
        st.success("All load test cycles completed!")

        # Display cycle data
        cycle_data = st.session_state.protocol.test_data["measurements"]["during_test"]
        df = pd.DataFrame(cycle_data)

        st.subheader("Cycle Measurements Summary")
        st.dataframe(df[["cycle_number", "actual_pressure", "deflection_center"]], use_container_width=True)

        # Plot deflection vs cycle
        fig = px.line(
            df,
            x="cycle_number",
            y="deflection_center",
            markers=True,
            title="Center Deflection vs Cycle Number"
        )
        fig.update_layout(
            xaxis_title="Cycle Number",
            yaxis_title="Deflection (mm)"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        if st.button("Continue to Post-test Measurements ➡️", type="primary", use_container_width=True):
            st.session_state.current_step = 3
            st.rerun()


def render_post_test_measurements():
    """Render post-test measurements form"""
    st.header("📊 Post-test Measurements")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Visual Inspection")
        visual_inspection = st.text_area(
            "Post-test Visual Inspection Notes",
            placeholder="Describe any defects, damage, or changes observed after testing...",
            height=150
        )

        st.subheader("Defects Observed")
        defects = st.multiselect(
            "Select all observed defects",
            ["none", "cell_cracks", "glass_breakage", "delamination",
             "junction_box_damage", "frame_damage", "backsheet_damage"],
            default=["none"]
        )

        st.subheader("Insulation Resistance")
        insulation_resistance = st.number_input(
            "Final Insulation Resistance (MΩ)",
            min_value=0.0,
            value=480.0,
            step=10.0
        )

    with col2:
        st.subheader("Electrical Performance (I-V Curve)")
        voc = st.number_input("Open Circuit Voltage Voc (V)", min_value=0.0, value=48.3, step=0.1, key="post_voc")
        isc = st.number_input("Short Circuit Current Isc (A)", min_value=0.0, value=10.1, step=0.1, key="post_isc")
        vmp = st.number_input("Voltage at Max Power Vmp (V)", min_value=0.0, value=39.8, step=0.1, key="post_vmp")
        imp = st.number_input("Current at Max Power Imp (A)", min_value=0.0, value=9.9, step=0.1, key="post_imp")

        pmax = vmp * imp
        st.metric("Maximum Power Pmax", f"{pmax:.2f} W")

        # Show comparison with pre-test
        pre_test = st.session_state.protocol.test_data["measurements"]["pre_test"]
        pre_pmax = pre_test["electrical_performance"]["pmax"]
        degradation = ((pre_pmax - pmax) / pre_pmax) * 100

        if degradation > 0:
            st.warning(f"Power degradation: {degradation:.2f}%")
        else:
            st.success(f"Power change: {degradation:.2f}%")

    st.divider()

    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if st.button("⬅️ Back"):
            st.session_state.current_step = 2
            st.rerun()
    with col_btn2:
        if st.button("Save & Analyze Results ➡️", type="primary", use_container_width=True):
            if not visual_inspection:
                st.error("Please provide visual inspection notes")
            else:
                st.session_state.protocol.record_post_test_measurements(
                    visual_inspection=visual_inspection,
                    electrical_performance=ElectricalPerformance(
                        voc=voc, isc=isc, vmp=vmp, imp=imp, pmax=pmax
                    ),
                    insulation_resistance=insulation_resistance,
                    defects_observed=defects
                )
                st.session_state.current_step = 4
                st.success("Post-test measurements recorded!")
                st.rerun()


def render_results_analysis():
    """Render results analysis and pass/fail determination"""
    st.header("📈 Results Analysis")

    # Calculate results
    results = st.session_state.protocol.calculate_results()

    # Display status
    status = results["test_status"]
    if status == TestStatus.PASS.value:
        st.success(f"## ✅ TEST PASSED")
    elif status == TestStatus.FAIL.value:
        st.error(f"## ❌ TEST FAILED")
    else:
        st.warning(f"## ⚠️ TEST {status.upper()}")

    # Key metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Power Degradation",
            f"{results['power_degradation']}%",
            delta=f"Limit: {st.session_state.protocol.test_data['acceptance_criteria']['max_power_degradation_percent']}%"
        )
    with col2:
        st.metric(
            "Max Deflection",
            f"{results['max_deflection_measured']} mm"
        )
    with col3:
        post_insulation = st.session_state.protocol.test_data["measurements"]["post_test"]["insulation_resistance"]
        st.metric(
            "Insulation Resistance",
            f"{post_insulation} MΩ",
            delta=f"Min: {st.session_state.protocol.test_data['acceptance_criteria']['min_insulation_resistance_mohm']} MΩ"
        )

    # Failure modes
    if results["failure_modes"]:
        st.subheader("⚠️ Failure Modes Detected")
        for failure in results["failure_modes"]:
            st.error(failure)

    st.divider()

    # Detailed analysis charts
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        # Electrical performance comparison
        pre_test = st.session_state.protocol.test_data["measurements"]["pre_test"]["electrical_performance"]
        post_test = st.session_state.protocol.test_data["measurements"]["post_test"]["electrical_performance"]

        comparison_df = pd.DataFrame({
            "Parameter": ["Voc (V)", "Isc (A)", "Pmax (W)"],
            "Pre-test": [pre_test["voc"], pre_test["isc"], pre_test["pmax"]],
            "Post-test": [post_test["voc"], post_test["isc"], post_test["pmax"]]
        })

        fig = go.Figure()
        fig.add_trace(go.Bar(name="Pre-test", x=comparison_df["Parameter"], y=comparison_df["Pre-test"]))
        fig.add_trace(go.Bar(name="Post-test", x=comparison_df["Parameter"], y=comparison_df["Post-test"]))
        fig.update_layout(title="Electrical Performance Comparison", barmode="group")
        st.plotly_chart(fig, use_container_width=True)

    with col_chart2:
        # Deflection data
        cycle_data = st.session_state.protocol.test_data["measurements"]["during_test"]
        df_cycles = pd.DataFrame(cycle_data)

        fig = px.scatter(
            df_cycles,
            x="actual_pressure",
            y="deflection_center",
            size="cycle_number",
            title="Pressure vs Deflection",
            labels={"actual_pressure": "Pressure (Pa)", "deflection_center": "Deflection (mm)"}
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Additional notes
    notes = st.text_area("Additional Notes", height=100)
    reviewer = st.text_input("Reviewer Name")

    if st.button("Finalize Results ➡️", type="primary", use_container_width=True):
        if notes:
            st.session_state.protocol.test_data["results"]["notes"] = notes
        if reviewer:
            st.session_state.protocol.test_data["results"]["reviewer"] = reviewer
            st.session_state.protocol.test_data["results"]["review_date"] = datetime.now().isoformat()

        st.session_state.current_step = 5
        st.success("Results finalized!")
        st.rerun()


def render_report_generation():
    """Render report generation and export options"""
    st.header("📄 Report Generation")

    # Summary report
    st.subheader("Test Summary")
    summary = st.session_state.protocol.generate_summary_report()
    st.code(summary, language="text")

    # Data validation
    is_valid, errors = st.session_state.protocol.validate_test_data()
    if is_valid:
        st.success("✅ Test data validation passed")
    else:
        st.error("❌ Test data validation failed")
        for error in errors:
            st.warning(error)

    st.divider()

    # Export options
    st.subheader("Export Options")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📥 Download JSON Data", use_container_width=True):
            json_data = json.dumps(st.session_state.protocol.test_data, indent=2)
            st.download_button(
                label="Download",
                data=json_data,
                file_name=f"{st.session_state.protocol.test_data['test_metadata']['test_id']}_data.json",
                mime="application/json"
            )

    with col2:
        if st.button("📄 Download Summary Report", use_container_width=True):
            st.download_button(
                label="Download",
                data=summary,
                file_name=f"{st.session_state.protocol.test_data['test_metadata']['test_id']}_summary.txt",
                mime="text/plain"
            )

    st.divider()

    if st.button("🔄 Start New Test", type="primary", use_container_width=True):
        # Reset session state
        st.session_state.clear()
        st.rerun()


def main():
    """Main application"""
    init_session_state()
    render_sidebar()

    # Main content based on current step
    if not st.session_state.test_initialized:
        render_test_initialization()
    else:
        step = st.session_state.current_step
        if step == 1:
            render_pre_test_measurements()
        elif step == 2:
            render_load_testing()
        elif step == 3:
            render_post_test_measurements()
        elif step == 4:
            render_results_analysis()
        elif step == 5:
            render_report_generation()


if __name__ == "__main__":
    main()
