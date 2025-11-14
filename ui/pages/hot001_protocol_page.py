"""HOT-001 Protocol Page

Streamlit page for executing and monitoring Hot Spot Endurance Tests.
"""

import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import json

from protocols.environmental.hot_001 import HotSpotEnduranceProtocol
from ui.components.hot001_visualizations import (
    create_iv_curve_comparison,
    create_temperature_profile,
    create_power_degradation_chart,
    create_parameter_comparison_table,
    create_hot_spot_summary_table,
    create_test_status_indicator,
    create_defect_timeline,
    create_qr_code_display
)
from database.connection import get_db
from database.models import TestRun, Protocol as ProtocolModel


def initialize_protocol():
    """Initialize protocol instance"""
    if 'protocol' not in st.session_state:
        st.session_state.protocol = HotSpotEnduranceProtocol()
    return st.session_state.protocol


def render_protocol_info():
    """Render protocol information section"""
    protocol = st.session_state.protocol

    st.title("🔥 HOT-001: Hot Spot Endurance Test")
    st.markdown(f"**Standard:** {protocol.metadata.standard}")
    st.markdown(f"**Category:** {protocol.metadata.category}")
    st.markdown(f"**Version:** {protocol.metadata.version}")

    with st.expander("ℹ️ Protocol Description"):
        st.write(protocol.metadata.description)
        st.markdown("""
        **Purpose:** Determine PV module ability to endure hot spot heating effects
        caused by non-uniform irradiance, cell cracking, or reverse bias conditions.

        **Key Steps:**
        1. Initial visual inspection and I-V measurement
        2. Hot spot generation on 3 selected cells (1 hour each at 85°C)
        3. Final visual inspection and I-V measurement
        4. Power degradation analysis (max 5% allowed)
        """)


def render_module_info_form():
    """Render module information input form"""
    st.subheader("📦 Module Information")

    col1, col2 = st.columns(2)

    with col1:
        module_serial = st.text_input(
            "Module Serial Number*",
            key="module_serial",
            help="Enter the unique serial number of the PV module"
        )
        module_manufacturer = st.text_input(
            "Manufacturer*",
            key="module_manufacturer"
        )
        module_model = st.text_input(
            "Model Number*",
            key="module_model"
        )

    with col2:
        module_power = st.number_input(
            "Nameplate Power (W)*",
            min_value=0.0,
            value=300.0,
            key="module_power"
        )
        operator_name = st.text_input(
            "Operator Name*",
            key="operator_name"
        )
        test_facility = st.text_input(
            "Test Facility*",
            value="PV Testing Lab",
            key="test_facility"
        )

    return {
        'module_serial_number': module_serial,
        'module_manufacturer': module_manufacturer,
        'module_model': module_model,
        'nameplate_power': module_power,
        'operator_name': operator_name,
        'test_facility': test_facility
    }


def render_test_step_1_visual_inspection():
    """Step 1: Initial Visual Inspection"""
    st.subheader("Step 1: Initial Visual Inspection")

    inspector = st.text_input("Inspector Name", key="initial_inspector")

    st.markdown("**Inspection Checklist:**")
    defects = []

    if st.checkbox("Check for pre-existing defects"):
        num_defects = st.number_input("Number of defects found", min_value=0, value=0)

        for i in range(int(num_defects)):
            with st.expander(f"Defect {i+1}"):
                defect_type = st.selectbox(
                    "Defect Type",
                    ["Crack", "Discoloration", "Bubble", "Delamination", "Other"],
                    key=f"defect_type_{i}"
                )
                defect_desc = st.text_area(
                    "Description",
                    key=f"defect_desc_{i}"
                )
                defects.append({
                    'type': defect_type,
                    'description': defect_desc
                })

    notes = st.text_area("Additional Notes", key="initial_inspection_notes")

    if st.button("Complete Initial Inspection", key="complete_initial_inspection"):
        protocol = st.session_state.protocol
        protocol.perform_initial_visual_inspection(
            inspector=inspector,
            defects=defects,
            notes=notes
        )
        st.success("✓ Initial visual inspection completed")
        return True

    return False


def render_test_step_2_initial_iv():
    """Step 2: Initial I-V Curve Measurement"""
    st.subheader("Step 2: Initial I-V Curve Measurement")

    st.markdown("**Test Conditions:**")
    col1, col2 = st.columns(2)
    with col1:
        irradiance = st.number_input(
            "Irradiance (W/m²)",
            value=1000.0,
            key="initial_irradiance"
        )
    with col2:
        temperature = st.number_input(
            "Module Temperature (°C)",
            value=25.0,
            key="initial_temperature"
        )

    st.markdown("**I-V Curve Data Input:**")

    data_input_method = st.radio(
        "Data Input Method",
        ["Upload CSV", "Manual Entry", "Generate Sample Data"],
        key="iv_input_method"
    )

    voltage = None
    current = None

    if data_input_method == "Generate Sample Data":
        # Generate sample I-V curve data
        voc = st.number_input("Voc (V)", value=40.0, key="sample_voc")
        isc = st.number_input("Isc (A)", value=9.0, key="sample_isc")

        if st.button("Generate Sample I-V Data", key="gen_sample_iv"):
            voltage = np.linspace(0, voc, 100)
            current = isc * (1 - voltage / voc) ** 1.5  # Simplified model
            st.session_state.initial_voltage = voltage
            st.session_state.initial_current = current
            st.success("Sample data generated")

    if 'initial_voltage' in st.session_state and 'initial_current' in st.session_state:
        voltage = st.session_state.initial_voltage
        current = st.session_state.initial_current

        # Show preview chart
        import plotly.graph_objects as go
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=voltage, y=current, mode='lines', name='I-V'))
        fig.update_layout(
            title="Initial I-V Curve Preview",
            xaxis_title="Voltage (V)",
            yaxis_title="Current (A)",
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)

        if st.button("Save Initial I-V Measurement", key="save_initial_iv"):
            protocol = st.session_state.protocol
            protocol.measure_initial_iv_curve(
                voltage=voltage,
                current=current,
                irradiance=irradiance,
                temperature=temperature
            )
            st.success(f"✓ Initial I-V curve saved (Pmax: {protocol.initial_iv_curve.pmax:.2f}W)")
            return True

    return False


def render_test_step_4_cell_selection():
    """Step 4: Cell Selection"""
    st.subheader("Step 4: Select Test Cells")

    st.markdown("Select 3 cells for hot spot testing (typically one from each third of module):")

    col1, col2, col3 = st.columns(3)
    with col1:
        cell1 = st.text_input("Cell 1 ID", value="A1", key="cell1_id")
    with col2:
        cell2 = st.text_input("Cell 2 ID", value="B5", key="cell2_id")
    with col3:
        cell3 = st.text_input("Cell 3 ID", value="C9", key="cell3_id")

    if st.button("Confirm Cell Selection", key="confirm_cells"):
        cell_ids = [cell1, cell2, cell3]
        protocol = st.session_state.protocol
        protocol.select_test_cells(cell_ids)
        st.session_state.selected_cells = cell_ids
        st.success(f"✓ Selected cells: {', '.join(cell_ids)}")
        return True

    return False


def render_test_step_7_9_hot_spot():
    """Steps 7-9: Hot Spot Tests"""
    st.subheader("Steps 7-9: Hot Spot Generation")

    if 'selected_cells' not in st.session_state:
        st.warning("Please complete cell selection first")
        return False

    protocol = st.session_state.protocol
    selected_cells = st.session_state.selected_cells

    for idx, cell_id in enumerate(selected_cells):
        with st.expander(f"🔥 Hot Spot Test - Cell {cell_id}", expanded=(idx == 0)):
            st.markdown(f"**Cell ID:** {cell_id}")

            col1, col2 = st.columns(2)
            with col1:
                reverse_bias = st.number_input(
                    f"Reverse Bias Voltage (V)",
                    value=50.0,
                    key=f"reverse_bias_{idx}"
                )
                target_temp = st.number_input(
                    f"Target Temperature (°C)",
                    value=85.0,
                    key=f"target_temp_{idx}"
                )

            with col2:
                current_limit = st.number_input(
                    f"Current Limit (A)",
                    value=9.0,
                    key=f"current_limit_{idx}"
                )
                duration = st.number_input(
                    f"Duration (hours)",
                    value=1.0,
                    key=f"duration_{idx}"
                )

            if st.button(f"Execute Hot Spot Test - Cell {cell_id}", key=f"execute_hot_{idx}"):
                # Generate sample temperature profile
                num_points = 120  # 2-minute intervals for 4 hours
                start_time = datetime.now()
                timestamps = [start_time + timedelta(minutes=i*2) for i in range(num_points)]
                # Simulate temperature ramp-up and stabilization
                temps = [
                    25 + (target_temp - 25) * (1 - np.exp(-i / 20)) + np.random.normal(0, 1)
                    for i in range(num_points)
                ]
                temp_profile = list(zip(timestamps, temps))

                # Execute test
                test_data = protocol.execute_hot_spot_test(
                    cell_id=cell_id,
                    reverse_bias_voltage=reverse_bias,
                    current_limit=current_limit,
                    target_temperature=target_temp,
                    duration_hours=duration,
                    temperature_readings=temp_profile
                )

                st.success(f"✓ Hot spot test completed for Cell {cell_id} (Max temp: {test_data.max_temperature_reached:.1f}°C)")

    # Show temperature profile if tests are done
    if len(protocol.hot_spot_tests) > 0:
        st.markdown("### Temperature Profiles")
        test_data = [
            {
                'cell_id': test.cell_id,
                'temperature_profile': test.temperature_profile,
                'target_temperature': test.target_temperature
            }
            for test in protocol.hot_spot_tests
        ]
        fig = create_temperature_profile(test_data)
        st.plotly_chart(fig, use_container_width=True)

        # Show summary table
        summary_df = create_hot_spot_summary_table([
            {
                'cell_id': test.cell_id,
                'start_time': test.start_time,
                'end_time': test.end_time,
                'target_temperature': test.target_temperature,
                'max_temperature_reached': test.max_temperature_reached,
                'reverse_bias_voltage': test.reverse_bias_voltage,
                'completed': test.completed
            }
            for test in protocol.hot_spot_tests
        ])
        st.dataframe(summary_df, use_container_width=True)

        return len(protocol.hot_spot_tests) >= 3

    return False


def render_test_step_12_final_iv():
    """Step 12: Final I-V Curve Measurement"""
    st.subheader("Step 12: Final I-V Curve Measurement")

    col1, col2 = st.columns(2)
    with col1:
        irradiance = st.number_input(
            "Irradiance (W/m²)",
            value=1000.0,
            key="final_irradiance"
        )
    with col2:
        temperature = st.number_input(
            "Module Temperature (°C)",
            value=25.0,
            key="final_temperature"
        )

    if st.button("Generate Final I-V Data", key="gen_final_iv"):
        # Generate sample data with degradation
        protocol = st.session_state.protocol
        if protocol.initial_iv_curve:
            voc = protocol.initial_iv_curve.voc * 0.98  # 2% Voc degradation
            isc = protocol.initial_iv_curve.isc * 0.97  # 3% Isc degradation

            voltage = np.linspace(0, voc, 100)
            current = isc * (1 - voltage / voc) ** 1.5

            st.session_state.final_voltage = voltage
            st.session_state.final_current = current
            st.success("Final I-V data generated")

    if 'final_voltage' in st.session_state and 'final_current' in st.session_state:
        voltage = st.session_state.final_voltage
        current = st.session_state.final_current

        if st.button("Save Final I-V Measurement", key="save_final_iv"):
            protocol = st.session_state.protocol
            protocol.measure_final_iv_curve(
                voltage=voltage,
                current=current,
                irradiance=irradiance,
                temperature=temperature
            )
            st.success(f"✓ Final I-V curve saved (Pmax: {protocol.final_iv_curve.pmax:.2f}W)")
            return True

    return False


def render_results_analysis():
    """Render results analysis section"""
    st.header("📊 Results Analysis")

    protocol = st.session_state.protocol

    if not protocol.initial_iv_curve or not protocol.final_iv_curve:
        st.warning("Complete initial and final I-V measurements to see results")
        return

    # Power degradation chart
    col1, col2 = st.columns([2, 1])

    with col1:
        fig = create_power_degradation_chart(
            protocol.initial_iv_curve.pmax,
            protocol.final_iv_curve.pmax,
            protocol.get_parameter_value('max_power_degradation')
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        degradation = protocol.calculate_power_degradation()
        pass_status, failures = protocol.determine_pass_fail()

        # Status indicator
        status_html = create_test_status_indicator(
            pass_status,
            degradation,
            protocol.get_parameter_value('max_power_degradation')
        )
        st.markdown(status_html, unsafe_allow_html=True)

        if failures:
            st.error("**Failure Reasons:**")
            for failure in failures:
                st.write(f"• {failure}")

    # I-V curve comparison
    st.markdown("### I-V and Power Curve Comparison")
    fig = create_iv_curve_comparison(
        protocol.initial_iv_curve.voltage,
        protocol.initial_iv_curve.current,
        protocol.final_iv_curve.voltage,
        protocol.final_iv_curve.current,
        protocol.initial_iv_curve.pmax,
        protocol.final_iv_curve.pmax
    )
    st.plotly_chart(fig, use_container_width=True)

    # Parameter comparison table
    st.markdown("### Parameter Comparison")
    comparison_df = create_parameter_comparison_table(
        {
            'voc': protocol.initial_iv_curve.voc,
            'isc': protocol.initial_iv_curve.isc,
            'pmax': protocol.initial_iv_curve.pmax,
            'fill_factor': protocol.initial_iv_curve.fill_factor
        },
        {
            'voc': protocol.final_iv_curve.voc,
            'isc': protocol.final_iv_curve.isc,
            'pmax': protocol.final_iv_curve.pmax,
            'fill_factor': protocol.final_iv_curve.fill_factor
        }
    )
    st.dataframe(comparison_df, use_container_width=True)


def render_export_section():
    """Render export and reporting section"""
    st.header("📄 Export & Reporting")

    protocol = st.session_state.protocol

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Export to JSON", key="export_json"):
            filepath = f"HOT001_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            protocol.export_report_to_json(filepath)
            st.success(f"✓ Report exported to {filepath}")

    with col2:
        if st.button("Export to CSV", key="export_csv"):
            filepath = f"HOT001_measurements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            protocol.export_to_csv(filepath)
            st.success(f"✓ Measurements exported to {filepath}")

    with col3:
        if st.button("Generate QR Code", key="gen_qr"):
            if protocol.current_test:
                qr_data = f"{protocol.current_test.test_id}|{protocol.metadata.protocol_id}"
                qr_code = protocol.generate_qr_code(qr_data)
                st.session_state.qr_code = qr_code
                st.success("✓ QR code generated")

    if 'qr_code' in st.session_state:
        st.markdown("### Traceability QR Code")
        qr_html = create_qr_code_display(
            st.session_state.qr_code,
            protocol.current_test.test_id if protocol.current_test else "N/A"
        )
        st.markdown(qr_html, unsafe_allow_html=True)


def main():
    """Main Streamlit app"""
    st.set_page_config(
        page_title="HOT-001: Hot Spot Endurance Test",
        page_icon="🔥",
        layout="wide"
    )

    # Initialize protocol
    initialize_protocol()

    # Render protocol info
    render_protocol_info()

    # Create tabs for different sections
    tabs = st.tabs([
        "📋 Setup",
        "🔬 Test Execution",
        "📊 Results",
        "📄 Reports"
    ])

    with tabs[0]:
        st.header("Test Setup")
        module_info = render_module_info_form()

        if st.button("Start New Test", type="primary"):
            protocol = st.session_state.protocol
            test_id = f"HOT001_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            try:
                protocol.start_test(test_id)
                protocol.module_info = module_info
                st.session_state.test_started = True
                st.success(f"✓ Test started: {test_id}")
            except ValueError as e:
                st.error(f"Error starting test: {e}")

    with tabs[1]:
        if st.session_state.get('test_started'):
            st.header("Test Execution")

            # Show test steps
            render_test_step_1_visual_inspection()
            st.divider()
            render_test_step_2_initial_iv()
            st.divider()
            render_test_step_4_cell_selection()
            st.divider()
            render_test_step_7_9_hot_spot()
            st.divider()
            render_test_step_12_final_iv()

        else:
            st.info("Please complete test setup first")

    with tabs[2]:
        if st.session_state.get('test_started'):
            render_results_analysis()
        else:
            st.info("No test results available")

    with tabs[3]:
        if st.session_state.get('test_started'):
            render_export_section()
        else:
            st.info("No test data to export")


if __name__ == "__main__":
    main()
