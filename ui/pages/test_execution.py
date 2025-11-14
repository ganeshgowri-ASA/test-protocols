"""Test Execution UI Component for CHALK-001"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from protocols.implementations.backsheet_chalking import BacksheetChalkingProtocol
from protocols.core.protocol_validator import load_protocol_definition


def render_test_execution():
    """Render the test execution interface"""

    # Initialize session state
    if 'test_protocol' not in st.session_state:
        st.session_state['test_protocol'] = None
    if 'current_step' not in st.session_state:
        st.session_state['current_step'] = 0
    if 'measurements' not in st.session_state:
        st.session_state['measurements'] = []

    # Load protocol if not already loaded
    if st.session_state['test_protocol'] is None:
        try:
            protocol_path = Path(__file__).parent.parent.parent / "protocols" / "templates" / "backsheet_chalking" / "protocol.json"
            protocol_def = load_protocol_definition(str(protocol_path))
            st.session_state['test_protocol'] = BacksheetChalkingProtocol(protocol_def)
        except Exception as e:
            st.error(f"Error loading protocol: {e}")
            return

    protocol = st.session_state['test_protocol']

    # Progress indicator
    steps = protocol.get_test_steps()
    progress = st.session_state['current_step'] / len(steps) if steps else 0
    st.progress(progress)
    st.markdown(f"**Step {st.session_state['current_step']} of {len(steps)}**")

    # Step 0: Sample Information
    if st.session_state['current_step'] == 0:
        render_sample_info()

    # Step 1: Environmental Conditioning
    elif st.session_state['current_step'] == 1:
        render_test_conditions()

    # Step 2: Measurements
    elif st.session_state['current_step'] == 2:
        render_measurements()

    # Step 3: Results
    elif st.session_state['current_step'] == 3:
        render_results()


def render_sample_info():
    """Render sample information form"""
    st.markdown("### Step 1: Sample Information")

    with st.form("sample_info_form"):
        sample_id = st.text_input("Sample ID*", placeholder="e.g., MOD-12345")

        module_type = st.text_input("Module Type*", placeholder="e.g., Monocrystalline 400W")

        backsheet_material = st.selectbox(
            "Backsheet Material*",
            ["PET", "PVF", "PA", "TPT", "PPE", "Other"]
        )

        backsheet_manufacturer = st.text_input("Backsheet Manufacturer", placeholder="Optional")

        col1, col2 = st.columns(2)
        with col1:
            exposure_type = st.selectbox(
                "Exposure Type",
                ["None", "Field", "Accelerated", "Combined"]
            )

        with col2:
            exposure_duration = st.number_input(
                "Exposure Duration (hours)",
                min_value=0,
                max_value=100000,
                value=0
            )

        submitted = st.form_submit_button("Next", type="primary")

        if submitted:
            if not sample_id or not module_type:
                st.error("Please fill in all required fields marked with *")
            else:
                sample_info = {
                    "sample_id": sample_id,
                    "module_type": module_type,
                    "backsheet_material": backsheet_material,
                    "backsheet_manufacturer": backsheet_manufacturer,
                    "exposure_type": exposure_type,
                    "exposure_duration": exposure_duration if exposure_duration > 0 else None,
                }
                st.session_state['sample_info'] = sample_info
                st.session_state['current_step'] = 1
                st.rerun()


def render_test_conditions():
    """Render test conditions form"""
    st.markdown("### Step 2: Test Conditions")

    with st.form("test_conditions_form"):
        col1, col2 = st.columns(2)

        with col1:
            temperature = st.number_input(
                "Temperature (°C)*",
                min_value=20.0,
                max_value=30.0,
                value=25.0,
                step=0.1
            )

            measurement_locations = st.number_input(
                "Number of Measurement Locations*",
                min_value=5,
                max_value=20,
                value=9
            )

        with col2:
            humidity = st.number_input(
                "Relative Humidity (%)*",
                min_value=30.0,
                max_value=70.0,
                value=50.0,
                step=1.0
            )

            tape_type = st.selectbox(
                "Adhesive Tape Type*",
                ["ASTM_Standard", "3M_610", "Scotch_Magic", "Custom"]
            )

        operator_id = st.text_input("Operator ID*", placeholder="e.g., OP-001")

        tape_lot = st.text_input("Tape Lot Number", placeholder="Optional")

        col1, col2 = st.columns(2)
        with col1:
            back_button = st.form_submit_button("Back")
        with col2:
            next_button = st.form_submit_button("Next", type="primary")

        if back_button:
            st.session_state['current_step'] = 0
            st.rerun()

        if next_button:
            if not operator_id:
                st.error("Please fill in all required fields marked with *")
            else:
                test_conditions = {
                    "temperature": temperature,
                    "humidity": humidity,
                    "test_date": datetime.now().strftime("%Y-%m-%d"),
                    "test_start_time": datetime.now().strftime("%H:%M:%S"),
                    "operator_id": operator_id,
                    "measurement_locations": measurement_locations,
                    "tape_type": tape_type,
                    "tape_lot_number": tape_lot if tape_lot else None,
                }
                st.session_state['test_conditions'] = test_conditions

                # Start the test
                protocol = st.session_state['test_protocol']
                protocol.start_test(
                    st.session_state['sample_info'],
                    test_conditions
                )

                st.session_state['current_step'] = 2
                st.rerun()


def render_measurements():
    """Render measurements data entry"""
    st.markdown("### Step 3: Chalking Measurements")

    num_locations = st.session_state['test_conditions']['measurement_locations']

    st.markdown(f"Enter chalking ratings for **{num_locations}** measurement locations.")
    st.markdown("*Rating scale: 0 (no chalking) to 10 (severe chalking)*")

    # Measurement entry
    with st.form("measurements_form"):
        for i in range(num_locations):
            st.markdown(f"**Location {i+1:02d}**")

            col1, col2, col3, col4 = st.columns([1, 1, 1, 2])

            with col1:
                rating = st.number_input(
                    f"Rating",
                    min_value=0.0,
                    max_value=10.0,
                    value=0.0,
                    step=0.5,
                    key=f"rating_{i}"
                )

            with col2:
                x_coord = st.number_input(
                    f"X (mm)",
                    min_value=0.0,
                    value=0.0,
                    key=f"x_{i}"
                )

            with col3:
                y_coord = st.number_input(
                    f"Y (mm)",
                    min_value=0.0,
                    value=0.0,
                    key=f"y_{i}"
                )

            with col4:
                notes = st.text_input(
                    f"Notes",
                    placeholder="Optional observations",
                    key=f"notes_{i}"
                )

        col1, col2 = st.columns(2)
        with col1:
            back_button = st.form_submit_button("Back")
        with col2:
            calculate_button = st.form_submit_button("Calculate Results", type="primary")

        if back_button:
            st.session_state['current_step'] = 1
            st.rerun()

        if calculate_button:
            # Collect all measurements
            measurements = []
            protocol = st.session_state['test_protocol']

            for i in range(num_locations):
                measurement = {
                    "location_id": f"LOC-{i+1:02d}",
                    "chalking_rating": st.session_state[f"rating_{i}"],
                    "location_x": st.session_state[f"x_{i}"],
                    "location_y": st.session_state[f"y_{i}"],
                    "visual_observations": st.session_state[f"notes_{i}"],
                }
                protocol.add_measurement(measurement)
                measurements.append(measurement)

            st.session_state['measurements'] = measurements
            st.session_state['current_step'] = 3
            st.rerun()


def render_results():
    """Render test results and analysis"""
    st.markdown("### Step 4: Test Results")

    protocol = st.session_state['test_protocol']

    # Complete the test
    results = protocol.complete_test()

    # Display results
    st.markdown("#### Summary Statistics")

    calc_results = results['calculated_results']

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Average Rating", f"{calc_results['average_chalking_rating']:.2f}")

    with col2:
        st.metric("Std Dev", f"{calc_results['chalking_std_dev']:.2f}")

    with col3:
        st.metric("Max Rating", f"{calc_results['max_chalking_rating']:.2f}")

    with col4:
        st.metric("Min Rating", f"{calc_results['min_chalking_rating']:.2f}")

    # Pass/Fail Assessment
    st.markdown("#### Pass/Fail Assessment")

    assessment = results['pass_fail_assessment']
    overall_result = assessment['overall_result']

    if overall_result == "PASS":
        st.success(f"✅ Test Result: **{overall_result}**")
    elif overall_result == "WARNING":
        st.warning(f"⚠️ Test Result: **{overall_result}**")
    else:
        st.error(f"❌ Test Result: **{overall_result}**")

    st.markdown(assessment.get('notes', ''))

    # Criteria evaluations
    with st.expander("View Detailed Criteria Evaluations"):
        for criterion in assessment['criteria_evaluations']:
            st.markdown(f"**{criterion['criterion']}**: {criterion['actual_value']:.2f}")
            st.markdown(f"Threshold: {criterion['threshold']} → Result: **{criterion['result']}**")
            st.markdown("---")

    # Recommendations
    st.markdown("#### Recommendations")
    recommendations = protocol.get_recommendations()
    for rec in recommendations:
        st.info(rec)

    # Export options
    st.markdown("#### Export Results")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Export JSON"):
            results_json = json.dumps(results, indent=2)
            st.download_button(
                "Download JSON",
                results_json,
                file_name=f"{results['test_execution_id']}_results.json",
                mime="application/json"
            )

    with col2:
        if st.button("Generate PDF Report"):
            st.info("PDF report generation coming soon!")

    # Reset button
    if st.button("Start New Test"):
        st.session_state['test_protocol'] = None
        st.session_state['current_step'] = 0
        st.session_state['measurements'] = []
        st.rerun()


if __name__ == "__main__":
    render_test_execution()
