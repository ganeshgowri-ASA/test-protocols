"""Run Test page for Streamlit UI."""

import streamlit as st
from datetime import datetime, date
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from protocols.wet_leakage_current.protocol import WETLeakageCurrentProtocol
from database.session import get_session
from database.models import TestRun, SampleInformation, TestProtocol
from utils.logging import get_logger

logger = get_logger(__name__)


def render_run_test_page():
    """Render the Run Test page."""
    st.title("🔬 Run Test")
    st.markdown("Configure and execute a test protocol")

    # Protocol Selection
    st.subheader("1. Select Protocol")
    protocol_choice = st.selectbox(
        "Test Protocol",
        ["WET-001: Wet Leakage Current Test"],
        help="Select the test protocol to run"
    )

    if "WET-001" in protocol_choice:
        render_wet001_test_form()


def render_wet001_test_form():
    """Render WET-001 test configuration form."""
    st.divider()

    # Sample Information
    st.subheader("2. Sample Information")
    col1, col2 = st.columns(2)

    with col1:
        sample_id = st.text_input(
            "Sample ID *",
            placeholder="e.g., PV-2025-001",
            help="Unique identifier for the sample"
        )
        module_type = st.text_input(
            "Module Type *",
            placeholder="e.g., Monocrystalline 400W",
            help="PV module type or model"
        )
        manufacturer = st.text_input(
            "Manufacturer",
            placeholder="e.g., Solar Corp"
        )

    with col2:
        serial_number = st.text_input(
            "Serial Number",
            placeholder="e.g., SN123456"
        )
        manufacturing_date = st.date_input(
            "Manufacturing Date",
            value=None
        )
        rated_power = st.number_input(
            "Rated Power (W)",
            min_value=0.0,
            value=400.0,
            step=10.0
        )

    st.divider()

    # Test Conditions
    st.subheader("3. Test Conditions")
    col1, col2 = st.columns(2)

    with col1:
        test_voltage = st.number_input(
            "Test Voltage (V) *",
            min_value=0.0,
            max_value=5000.0,
            value=1500.0,
            step=100.0,
            help="DC test voltage to apply"
        )
        electrode_config = st.selectbox(
            "Electrode Configuration *",
            ["A", "B"],
            help="Electrode configuration type"
        )
        test_duration = st.number_input(
            "Test Duration (hours) *",
            min_value=1.0,
            max_value=720.0,
            value=168.0,
            step=1.0,
            help="Total test duration"
        )

    with col2:
        measurement_interval = st.number_input(
            "Measurement Interval (minutes)",
            min_value=1.0,
            max_value=1440.0,
            value=60.0,
            step=5.0,
            help="Interval between measurements"
        )
        polarity = st.selectbox(
            "Voltage Polarity",
            ["positive", "negative"],
            help="Test voltage polarity"
        )

    st.divider()

    # Environmental Conditions
    st.subheader("4. Environmental Conditions")
    col1, col2 = st.columns(2)

    with col1:
        temperature = st.number_input(
            "Temperature (°C) *",
            min_value=15.0,
            max_value=35.0,
            value=25.0,
            step=0.5,
            help="Ambient temperature during test"
        )
        temp_tolerance = st.number_input(
            "Temperature Tolerance (±°C)",
            min_value=0.0,
            max_value=10.0,
            value=5.0,
            step=0.5
        )

    with col2:
        humidity = st.number_input(
            "Relative Humidity (%)",
            min_value=45.0,
            max_value=100.0,
            value=90.0,
            step=1.0,
            help="Relative humidity during test"
        )
        humidity_tolerance = st.number_input(
            "Humidity Tolerance (±%)",
            min_value=0.0,
            max_value=10.0,
            value=5.0,
            step=0.5
        )

    barometric_pressure = st.number_input(
        "Barometric Pressure (kPa)",
        min_value=80.0,
        max_value=110.0,
        value=101.3,
        step=0.1
    )

    st.divider()

    # Acceptance Criteria
    st.subheader("5. Acceptance Criteria")
    col1, col2 = st.columns(2)

    with col1:
        max_leakage = st.number_input(
            "Maximum Leakage Current (mA)",
            min_value=0.0,
            value=0.25,
            step=0.01,
            format="%.4f",
            help="Maximum allowable leakage current"
        )
        min_insulation = st.number_input(
            "Minimum Insulation Resistance (MΩ)",
            min_value=0.0,
            value=400.0,
            step=10.0,
            help="Minimum required insulation resistance"
        )

    with col2:
        max_voltage_var = st.number_input(
            "Maximum Voltage Variation (%)",
            min_value=0.0,
            value=5.0,
            step=0.5,
            help="Maximum allowed voltage variation"
        )

    no_tracking = st.checkbox("No Surface Tracking Allowed", value=True)
    no_damage = st.checkbox("No Visible Damage Allowed", value=True)

    st.divider()

    # Operator Information
    st.subheader("6. Operator Information")
    col1, col2 = st.columns(2)

    with col1:
        operator_name = st.text_input("Operator Name")
        operator_id = st.text_input("Operator ID")

    with col2:
        test_facility = st.text_input("Test Facility")
        equipment_id = st.text_input("Equipment ID")

    st.divider()

    # Action Buttons
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button("✅ Start Test", type="primary", use_container_width=True):
            # Validate required fields
            if not sample_id or not module_type:
                st.error("Please fill in all required fields marked with *")
                return

            # Create parameters dictionary
            params = {
                "sample_information": {
                    "sample_id": sample_id,
                    "module_type": module_type,
                    "manufacturer": manufacturer,
                    "manufacturing_date": manufacturing_date.isoformat() if manufacturing_date else None,
                    "serial_number": serial_number,
                    "rated_power": rated_power,
                },
                "test_conditions": {
                    "test_voltage": test_voltage,
                    "electrode_configuration": electrode_config,
                    "test_duration": test_duration,
                    "measurement_interval": measurement_interval,
                    "polarity": polarity,
                },
                "environmental_conditions": {
                    "temperature": temperature,
                    "temperature_tolerance": temp_tolerance,
                    "relative_humidity": humidity,
                    "humidity_tolerance": humidity_tolerance,
                    "barometric_pressure": barometric_pressure,
                },
                "acceptance_criteria": {
                    "max_leakage_current": max_leakage,
                    "min_insulation_resistance": min_insulation,
                    "max_voltage_variation": max_voltage_var,
                    "no_surface_tracking": no_tracking,
                    "no_visible_damage": no_damage,
                },
                "operator_information": {
                    "operator_name": operator_name,
                    "operator_id": operator_id,
                    "test_facility": test_facility,
                    "equipment_id": equipment_id,
                }
            }

            try:
                # Initialize protocol
                protocol = WETLeakageCurrentProtocol()

                # Validate parameters
                protocol.validate_parameters(params)

                # Save to database
                # (In a real implementation, this would be more comprehensive)
                st.success("✅ Test parameters validated successfully!")
                st.info("📝 Test configuration saved. Ready to begin data collection.")

                # Store in session state for data collection page
                st.session_state['test_params'] = params
                st.session_state['protocol'] = protocol
                st.session_state['test_started'] = True

                logger.info(f"Test started for sample {sample_id}")

            except Exception as e:
                st.error(f"❌ Error starting test: {str(e)}")
                logger.error(f"Test start failed: {e}")

    with col2:
        if st.button("💾 Save Configuration", use_container_width=True):
            st.info("Configuration saved for later use")

    with col3:
        st.caption("* Required fields")

    # Show test monitoring if test started
    if st.session_state.get('test_started'):
        st.divider()
        st.subheader("📊 Test Monitoring")
        st.info("Test is running. Add measurements or view real-time data.")

        if st.button("➕ Add Manual Measurement"):
            render_measurement_input()


def render_measurement_input():
    """Render form to add a manual measurement."""
    with st.form("measurement_form"):
        st.write("**Add Measurement Point**")

        col1, col2 = st.columns(2)

        with col1:
            leakage_current = st.number_input(
                "Leakage Current (mA)",
                min_value=0.0,
                step=0.0001,
                format="%.4f"
            )
            voltage = st.number_input(
                "Voltage (V)",
                min_value=0.0,
                value=1500.0,
                step=1.0
            )

        with col2:
            temp = st.number_input(
                "Temperature (°C)",
                value=25.0,
                step=0.1
            )
            hum = st.number_input(
                "Humidity (%)",
                value=90.0,
                step=0.1
            )

        notes = st.text_area("Notes (optional)")

        submitted = st.form_submit_button("Add Measurement")

        if submitted:
            protocol = st.session_state.get('protocol')
            if protocol:
                protocol.add_measurement(
                    leakage_current=leakage_current,
                    voltage=voltage,
                    temperature=temp,
                    humidity=hum,
                    notes=notes
                )
                st.success(f"✅ Measurement added ({len(protocol.measurements)} total)")
            else:
                st.error("No active test protocol")
