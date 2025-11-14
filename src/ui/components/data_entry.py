"""Data entry form component."""

import streamlit as st
from datetime import datetime
import json


def render_data_entry_form():
    """Render data entry form for test protocol."""
    st.title("Test Data Entry")

    protocol_id = st.session_state.current_protocol
    protocol_manager = st.session_state.protocol_manager
    validator = st.session_state.schema_validator

    st.markdown(f"**Protocol:** {protocol_id.upper()}")

    # Initialize form data in session state
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {
            'test_run_id': '',
            'sample_id': '',
            'operator': '',
            'measurements': []
        }

    # Test Information Section
    st.subheader("Test Information")
    col1, col2 = st.columns(2)

    with col1:
        test_run_id = st.text_input(
            "Test Run ID",
            value=st.session_state.form_data.get('test_run_id', ''),
            placeholder=protocol_manager.generate_test_run_id(protocol_id),
            help="Format: PROTOCOL-YYYYMMDD-####"
        )
        st.session_state.form_data['test_run_id'] = test_run_id

        sample_id = st.text_input(
            "Sample ID",
            value=st.session_state.form_data.get('sample_id', ''),
            placeholder="PV-SAMPLE-001"
        )
        st.session_state.form_data['sample_id'] = sample_id

    with col2:
        operator = st.text_input(
            "Operator Name",
            value=st.session_state.form_data.get('operator', '')
        )
        st.session_state.form_data['operator'] = operator

        timestamp = st.text_input(
            "Test Date & Time",
            value=datetime.now().isoformat(),
            disabled=True
        )
        st.session_state.form_data['timestamp'] = timestamp

    # Equipment Information Section
    st.subheader("Equipment Information")
    col1, col2, col3 = st.columns(3)

    with col1:
        solar_simulator = st.selectbox(
            "Solar Simulator",
            ["SIM-001-ClassAAA", "SIM-002-ClassAAA", "SIM-003-ClassABA"]
        )

    with col2:
        reference_cell = st.selectbox(
            "Reference Cell",
            ["REF-CELL-001", "REF-CELL-002", "REF-CELL-003"]
        )

    with col3:
        calibration_date = st.date_input(
            "Last Calibration Date"
        )

    st.session_state.form_data['equipment'] = {
        'solar_simulator_id': solar_simulator,
        'reference_cell_id': reference_cell,
        'calibration_date': str(calibration_date)
    }

    # Environmental Conditions
    st.subheader("Environmental Conditions")
    col1, col2, col3 = st.columns(3)

    with col1:
        ambient_temp = st.number_input(
            "Ambient Temperature (°C)",
            min_value=15.0,
            max_value=35.0,
            value=25.0,
            step=0.1
        )

    with col2:
        humidity = st.number_input(
            "Humidity (%)",
            min_value=0.0,
            max_value=100.0,
            value=50.0,
            step=1.0
        )

    with col3:
        pressure = st.number_input(
            "Atmospheric Pressure (kPa)",
            min_value=80.0,
            max_value=110.0,
            value=101.3,
            step=0.1
        )

    st.session_state.form_data['environmental_conditions'] = {
        'ambient_temperature_c': ambient_temp,
        'humidity_percent': humidity,
        'atmospheric_pressure_kpa': pressure
    }

    # Measurements Section
    st.subheader("Concentration Measurements")

    # Initialize measurements list if not exists
    if 'measurements' not in st.session_state.form_data:
        st.session_state.form_data['measurements'] = []

    # Add measurement button
    if st.button("Add Measurement"):
        st.session_state.form_data['measurements'].append({
            'concentration_suns': 1.0,
            'temperature_c': 25.0,
            'voc': 0.0,
            'isc': 0.0,
            'vmp': 0.0,
            'imp': 0.0,
            'fill_factor': 0.0,
            'efficiency': 0.0
        })

    # Display existing measurements
    measurements = st.session_state.form_data.get('measurements', [])

    if measurements:
        for idx, measurement in enumerate(measurements):
            with st.expander(f"Measurement {idx + 1}", expanded=(idx == len(measurements) - 1)):
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    concentration = st.number_input(
                        "Concentration (suns)",
                        min_value=0.1,
                        max_value=5000.0,
                        value=measurement.get('concentration_suns', 1.0),
                        step=0.1,
                        key=f"conc_{idx}"
                    )
                    measurement['concentration_suns'] = concentration

                    voc = st.number_input(
                        "Voc (V)",
                        min_value=0.0,
                        value=measurement.get('voc', 0.0),
                        step=0.001,
                        format="%.3f",
                        key=f"voc_{idx}"
                    )
                    measurement['voc'] = voc

                with col2:
                    temperature = st.number_input(
                        "Temperature (°C)",
                        min_value=-40.0,
                        max_value=200.0,
                        value=measurement.get('temperature_c', 25.0),
                        step=0.1,
                        key=f"temp_{idx}"
                    )
                    measurement['temperature_c'] = temperature

                    isc = st.number_input(
                        "Isc (A)",
                        min_value=0.0,
                        value=measurement.get('isc', 0.0),
                        step=0.001,
                        format="%.3f",
                        key=f"isc_{idx}"
                    )
                    measurement['isc'] = isc

                with col3:
                    vmp = st.number_input(
                        "Vmp (V)",
                        min_value=0.0,
                        value=measurement.get('vmp', 0.0),
                        step=0.001,
                        format="%.3f",
                        key=f"vmp_{idx}"
                    )
                    measurement['vmp'] = vmp

                    fill_factor = st.number_input(
                        "Fill Factor",
                        min_value=0.0,
                        max_value=1.0,
                        value=measurement.get('fill_factor', 0.0),
                        step=0.001,
                        format="%.3f",
                        key=f"ff_{idx}"
                    )
                    measurement['fill_factor'] = fill_factor

                with col4:
                    imp = st.number_input(
                        "Imp (A)",
                        min_value=0.0,
                        value=measurement.get('imp', 0.0),
                        step=0.001,
                        format="%.3f",
                        key=f"imp_{idx}"
                    )
                    measurement['imp'] = imp

                    efficiency = st.number_input(
                        "Efficiency (%)",
                        min_value=0.0,
                        max_value=100.0,
                        value=measurement.get('efficiency', 0.0),
                        step=0.01,
                        format="%.2f",
                        key=f"eff_{idx}"
                    )
                    measurement['efficiency'] = efficiency

                if st.button(f"Remove Measurement {idx + 1}", key=f"remove_{idx}"):
                    st.session_state.form_data['measurements'].pop(idx)
                    st.rerun()

    # Notes section
    st.subheader("Additional Notes")
    notes = st.text_area(
        "Observations and Notes",
        value=st.session_state.form_data.get('notes', ''),
        placeholder="Enter any observations, anomalies, or additional information..."
    )
    st.session_state.form_data['notes'] = notes

    # Validation and submission
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        if st.button("Validate Data", type="secondary"):
            validation_result = validator.validate_data(
                protocol_id,
                st.session_state.form_data
            )

            if validation_result.get('valid'):
                st.success("Data validation passed!")
            else:
                st.error("Data validation failed!")
                for error in validation_result.get('errors', []):
                    st.error(f"- {error}")

            if validation_result.get('warnings'):
                st.warning("Warnings:")
                for warning in validation_result.get('warnings', []):
                    st.warning(f"- {warning}")

    with col2:
        if st.button("Save Data", type="primary"):
            st.session_state.test_data = st.session_state.form_data.copy()
            st.success("Data saved successfully!")

    with col3:
        if st.button("Clear Form"):
            st.session_state.form_data = {
                'test_run_id': '',
                'sample_id': '',
                'operator': '',
                'measurements': []
            }
            st.rerun()

    # Display current data
    with st.expander("View Current Data (JSON)"):
        st.json(st.session_state.form_data)
