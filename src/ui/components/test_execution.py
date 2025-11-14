"""Test execution component for running protocols."""

import streamlit as st
from datetime import datetime
from pathlib import Path
import uuid

from src.protocols.term001 import TERM001Protocol
from src.database.connection import get_session
from src.database.models import TestExecution as TestExecutionDB
from src.ui.components.charting import render_resistance_chart, render_mechanical_chart


def render_test_execution(protocol_id: str):
    """
    Render test execution interface.

    Args:
        protocol_id: ID of the protocol to execute
    """
    st.markdown("---")
    st.subheader("Test Execution")

    # Initialize protocol in session state
    if "protocol_instance" not in st.session_state:
        if protocol_id == "TERM-001":
            st.session_state.protocol_instance = TERM001Protocol()

    protocol = st.session_state.protocol_instance

    # Test initialization
    if not protocol.test_id:
        render_test_initialization(protocol)
    else:
        render_test_steps(protocol)


def render_test_initialization(protocol):
    """Render test initialization form."""
    st.info("Please enter test information to begin")

    with st.form("test_init"):
        col1, col2 = st.columns(2)

        with col1:
            test_id = st.text_input(
                "Test ID", value=f"TEST-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            )
            module_serial = st.text_input("Module Serial Number", placeholder="e.g., MOD-2025-001")

        with col2:
            operator = st.text_input("Operator Name", placeholder="Enter your name")

        st.subheader("Test Conditions")
        col3, col4 = st.columns(2)

        with col3:
            temp = st.number_input("Ambient Temperature (°C)", value=25.0, min_value=-40.0, max_value=85.0)
        with col4:
            humidity = st.number_input("Relative Humidity (%)", value=50.0, min_value=0.0, max_value=100.0)

        submitted = st.form_submit_button("Start Test", type="primary")

        if submitted:
            if not module_serial or not operator:
                st.error("Please fill in all required fields")
            else:
                protocol.start_test(test_id, module_serial, operator)

                # Save to database
                with get_session() as session:
                    # Create protocol record if it doesn't exist
                    protocol_db = (
                        session.query(src.database.models.Protocol)
                        .filter_by(protocol_id=protocol.protocol_id)
                        .first()
                    )

                    if not protocol_db:
                        protocol_db = src.database.models.Protocol(
                            protocol_id=protocol.protocol_id,
                            version=protocol.version,
                            title=protocol.title,
                            category=protocol.category,
                            description=protocol.description,
                        )
                        session.add(protocol_db)
                        session.flush()

                    # Create test execution record
                    test_exec = TestExecutionDB(
                        test_id=test_id,
                        protocol_id=protocol_db.id,
                        module_serial_number=module_serial,
                        operator=operator,
                        start_time=datetime.now(),
                        status="In Progress",
                        test_conditions_actual={"temperature": temp, "humidity": humidity},
                    )
                    session.add(test_exec)

                st.success("Test started successfully!")
                st.rerun()


def render_test_steps(protocol):
    """Render test step execution interface."""
    current_step = protocol.get_current_step()

    if not current_step:
        # All steps completed
        render_test_completion(protocol)
        return

    # Progress indicator
    progress = protocol.current_step_index / len(protocol.steps)
    st.progress(progress, text=f"Step {protocol.current_step_index + 1} of {len(protocol.steps)}")

    st.subheader(f"Step {current_step.step_number}: {current_step.name}")
    st.write(current_step.description)

    st.info(f"⏱️ Estimated duration: {current_step.duration} {current_step.duration_unit}")

    # Render input fields
    if current_step.inputs:
        st.markdown("### Inputs")
        for input_field in current_step.inputs:
            render_input_field(input_field, current_step)

    # Render measurement fields
    st.markdown("### Measurements")
    for measurement in current_step.measurements:
        if not measurement.get("calculated", False):
            render_measurement_field(measurement, current_step, protocol)

    # Step completion
    col1, col2 = st.columns([3, 1])

    with col2:
        if st.button("Complete Step", type="primary", key=f"complete_{current_step.step_number}"):
            # Calculate derived values
            protocol.calculate_derived_values(current_step)

            # Validate and complete step
            passed, failures = protocol.complete_current_step()

            if not passed:
                st.error("Step validation failed:")
                for failure in failures:
                    st.error(f"❌ {failure}")
            else:
                st.success("✅ Step completed successfully!")
                st.rerun()

    # Display live results
    if current_step.results:
        with st.expander("Current Results", expanded=False):
            st.json(current_step.results)


def render_input_field(input_field: dict, step):
    """Render an input field."""
    name = input_field["name"]
    input_type = input_field["type"]
    required = input_field.get("required", True)

    label = name.replace("_", " ").title()
    if required:
        label += " *"

    if input_type == "select":
        value = st.selectbox(label, options=input_field["options"], key=f"input_{step.step_number}_{name}")
        step.results[name] = value


def render_measurement_field(measurement: dict, step, protocol):
    """Render a measurement field."""
    name = measurement["name"]
    meas_type = measurement["type"]
    required = measurement.get("required", True)

    label = name.replace("_", " ").title()
    if measurement.get("unit"):
        label += f" ({measurement['unit']})"
    if required:
        label += " *"

    key = f"meas_{step.step_number}_{name}"

    if meas_type == "number":
        min_val = measurement.get("min", 0.0)
        max_val = measurement.get("max", 1000.0)
        value = st.number_input(
            label, min_value=min_val, max_value=max_val, key=key, format="%.2f"
        )
        protocol.record_measurement(name, value)

    elif meas_type == "text":
        value = st.text_area(label, key=key)
        protocol.record_measurement(name, value)

    elif meas_type == "boolean":
        value = st.checkbox(label, key=key)
        protocol.record_measurement(name, value)

    elif meas_type == "select":
        value = st.selectbox(label, options=measurement["options"], key=key)
        protocol.record_measurement(name, value)


def render_test_completion(protocol):
    """Render test completion summary."""
    st.success("🎉 All steps completed!")

    result = protocol.generate_result()

    st.subheader("Test Summary")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Test ID", result.test_id)
    with col2:
        st.metric("Module Serial", result.module_serial_number)
    with col3:
        result_color = "🟢" if result.overall_result == "Pass" else "🔴"
        st.metric("Overall Result", f"{result_color} {result.overall_result}")

    st.markdown("---")

    # Display step results
    st.subheader("Step Results")
    for step_result in result.step_results:
        status_icon = "✅" if step_result["passed"] else "❌"
        with st.expander(f"{status_icon} Step {step_result['step_number']}: {step_result['name']}"):
            st.json(step_result["results"])

            if step_result["failures"]:
                st.error("Failures:")
                for failure in step_result["failures"]:
                    st.write(f"- {failure}")

    # Charts
    if protocol.protocol_id == "TERM-001":
        st.subheader("Charts")

        col1, col2 = st.columns(2)
        with col1:
            render_resistance_chart(protocol)
        with col2:
            render_mechanical_chart(protocol)

    # Export options
    st.markdown("---")
    st.subheader("Export Results")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📄 Export to PDF"):
            st.info("PDF export coming soon...")
    with col2:
        if st.button("📊 Export to Excel"):
            st.info("Excel export coming soon...")
    with col3:
        if st.button("🔄 Start New Test"):
            # Reset protocol
            st.session_state.protocol_instance = None
            st.rerun()
