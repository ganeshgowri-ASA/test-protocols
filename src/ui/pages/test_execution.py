"""
Test Execution Page
"""

import streamlit as st
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.models import SessionLocal, Sample, Equipment, TestOutcome
from src.runners import GroundContinuityRunner


def render_test_execution():
    """Render the test execution page"""
    st.title("🔬 Test Execution")

    # Protocol selection
    st.header("1. Select Test Protocol")

    protocol_options = {
        "GROUND-001": "Ground Continuity Test (IEC 61730 MST 13)"
    }

    selected_protocol = st.selectbox(
        "Protocol",
        options=list(protocol_options.keys()),
        format_func=lambda x: f"{x} - {protocol_options[x]}"
    )

    if selected_protocol == "GROUND-001":
        render_ground_continuity_test()
    else:
        st.info("Select a protocol to begin test execution")


def render_ground_continuity_test():
    """Render Ground Continuity Test execution interface"""

    st.header("2. Test Configuration")

    # Get database session
    db = SessionLocal()

    try:
        # Sample selection
        samples = db.query(Sample).filter(Sample.is_active == True).all()

        if not samples:
            st.warning("No active samples found. Please add samples in Sample Management.")
            return

        sample_options = {s.id: f"{s.sample_id} - {s.serial_number or 'N/A'}" for s in samples}

        selected_sample_id = st.selectbox(
            "Select Sample",
            options=list(sample_options.keys()),
            format_func=lambda x: sample_options[x]
        )

        selected_sample = db.query(Sample).filter(Sample.id == selected_sample_id).first()

        # Display sample information
        with st.expander("Sample Information", expanded=False):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Sample ID", selected_sample.sample_id)
                st.metric("Serial Number", selected_sample.serial_number or "N/A")

            with col2:
                st.metric("Rated Power (W)", selected_sample.rated_power_pmax or "N/A")
                st.metric("Max System Voltage (V)", selected_sample.max_system_voltage or "N/A")

            with col3:
                st.metric("Voc (V)", selected_sample.open_circuit_voltage_voc or "N/A")
                st.metric("Isc (A)", selected_sample.short_circuit_current_isc or "N/A")

        # Equipment selection
        equipment_list = db.query(Equipment).filter(Equipment.is_active == True).all()

        if equipment_list:
            equipment_options = {e.id: f"{e.equipment_id} - {e.name}" for e in equipment_list}

            selected_equipment_id = st.selectbox(
                "Select Equipment (Optional)",
                options=[None] + list(equipment_options.keys()),
                format_func=lambda x: "No equipment" if x is None else equipment_options[x]
            )
        else:
            selected_equipment_id = None
            st.info("No equipment registered. You can proceed without equipment selection.")

        st.header("3. Test Parameters")

        col1, col2 = st.columns(2)

        with col1:
            # Test parameters
            max_overcurrent = st.number_input(
                "Max Overcurrent Protection (A)",
                min_value=0.1,
                max_value=100.0,
                value=selected_sample.max_overcurrent_protection or 15.0,
                step=0.1,
                help="Maximum overcurrent protection device rating for the module"
            )

            ambient_temp = st.number_input(
                "Ambient Temperature (°C)",
                min_value=-10.0,
                max_value=50.0,
                value=25.0,
                step=0.1
            )

        with col2:
            # Calculated test current
            test_current = 2.5 * max_overcurrent
            st.metric(
                "Calculated Test Current (A)",
                f"{test_current:.2f}",
                help="2.5 × Max Overcurrent Protection"
            )

            relative_humidity = st.number_input(
                "Relative Humidity (%)",
                min_value=0.0,
                max_value=95.0,
                value=50.0,
                step=1.0
            )

        # Measurement points
        st.subheader("Measurement Points")

        num_points = st.number_input(
            "Number of Measurement Points",
            min_value=1,
            max_value=10,
            value=1,
            step=1,
            help="Number of bonding points to test"
        )

        measurement_points = []
        for i in range(num_points):
            point_name = st.text_input(
                f"Measurement Point {i + 1}",
                value=f"Frame to Point {i + 1}",
                key=f"point_{i}"
            )
            measurement_points.append(point_name)

        # Operator information
        st.header("4. Operator Information")

        col1, col2 = st.columns(2)

        with col1:
            operator_id = st.text_input(
                "Operator ID",
                value="",
                help="Unique operator identifier"
            )

        with col2:
            operator_name = st.text_input(
                "Operator Name",
                value="",
                help="Full name of the operator"
            )

        # Pre-test notes
        pre_test_notes = st.text_area(
            "Pre-Test Notes (Optional)",
            help="Any observations before starting the test"
        )

        # Test execution mode
        st.header("5. Execution Mode")

        execution_mode = st.radio(
            "Mode",
            ["Manual Entry", "Automated (Simulated)"],
            help="Manual: Enter measurements manually. Automated: Simulate instrument readings."
        )

        auto_mode = execution_mode == "Automated (Simulated)"

        # Execute test button
        st.markdown("---")

        if st.button("▶️ Start Test", type="primary", use_container_width=True):
            if not operator_id or not operator_name:
                st.error("Please enter operator ID and name")
                return

            # Create test runner
            runner = GroundContinuityRunner(db_session=db)

            # Prepare input parameters
            input_params = {
                'max_overcurrent_protection': max_overcurrent,
                'ambient_temperature': ambient_temp,
                'relative_humidity': relative_humidity
            }

            # Calculate parameters
            calculated_params = runner.calculate_parameters(input_params)

            # Create test execution
            test_execution = runner.create_test_execution(
                sample_id=selected_sample.id,
                operator_id=operator_id,
                operator_name=operator_name,
                equipment_id=selected_equipment_id,
                parameters=calculated_params
            )

            # Add pre-test notes
            if pre_test_notes:
                test_execution.pre_test_notes = pre_test_notes
                db.commit()

            # Run test
            with st.spinner("Running test..."):
                try:
                    outcome = runner.run_test(
                        test_execution=test_execution,
                        measurement_points=measurement_points,
                        auto_mode=auto_mode
                    )

                    # Display results
                    st.success(f"Test completed: {test_execution.test_number}")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Test Number", test_execution.test_number)

                    with col2:
                        if outcome == TestOutcome.PASS:
                            st.metric("Result", "✅ PASS", delta="Pass")
                        else:
                            st.metric("Result", "❌ FAIL", delta="Fail", delta_color="inverse")

                    with col3:
                        duration = test_execution.duration_seconds or 0
                        st.metric("Duration", f"{duration:.1f} s")

                    # Display measurements
                    st.subheader("Measurements")

                    measurements = test_execution.measurements
                    if measurements:
                        import pandas as pd

                        data = []
                        for m in measurements:
                            data.append({
                                'Point': m.measurement_point or '-',
                                'Measurement': m.measurement_name,
                                'Value': f"{m.value:.4f}" if m.value else m.value_text,
                                'Unit': m.unit,
                                'Within Limits': '✅' if m.within_limits else '❌' if m.within_limits is not None else '-'
                            })

                        df = pd.DataFrame(data)
                        st.dataframe(df, use_container_width=True)

                    # Display pass/fail criteria
                    st.subheader("Pass/Fail Criteria")

                    results = test_execution.results
                    if results:
                        for result in results:
                            if result.passed:
                                st.success(f"✅ {result.criterion_name}")
                            else:
                                st.error(f"❌ {result.criterion_name}")
                                if result.failure_reason:
                                    st.caption(f"   {result.failure_reason}")

                except Exception as e:
                    st.error(f"Test execution failed: {e}")
                    import traceback
                    st.code(traceback.format_exc())

    finally:
        db.close()


if __name__ == "__main__":
    render_test_execution()
