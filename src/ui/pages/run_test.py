"""Run test page for executing test protocols."""

import streamlit as st
from datetime import datetime

from src.models.base import get_session
from src.models import Protocol
from src.parsers import ProtocolLoader, ProtocolExecutor
from src.models.test_run import TestStatus, TestResult


def render_run_test_page():
    """Render the run test page."""
    st.title("🧪 Run Test")
    st.markdown("Execute a test protocol on a specimen")

    # Check if we have an active test run
    if st.session_state.current_test_run:
        render_active_test_run()
    else:
        render_new_test_setup()


def render_new_test_setup():
    """Render the new test setup form."""
    st.subheader("Start New Test")

    # Select protocol
    session = get_session(st.session_state.engine)
    protocols = ProtocolLoader.list_protocols(session)

    if not protocols:
        st.warning("No protocols available. Please upload a protocol first.")
        session.close()
        return

    protocol_options = {f"{p.protocol_id} - {p.protocol_name}": p for p in protocols}
    selected_protocol_name = st.selectbox("Select Protocol", list(protocol_options.keys()))
    selected_protocol = protocol_options[selected_protocol_name]

    # Display protocol info
    with st.expander("Protocol Information"):
        st.markdown(f"**Description:** {selected_protocol.description}")
        st.markdown(f"**Category:** {selected_protocol.category}")
        st.markdown(f"**Version:** {selected_protocol.version}")

    st.markdown("---")

    # Test run information form
    st.subheader("Test Specimen Information")

    col1, col2 = st.columns(2)

    with col1:
        specimen_id = st.text_input("Specimen ID*", placeholder="e.g., MODULE-12345")
        manufacturer = st.text_input("Manufacturer", placeholder="e.g., SolarTech Inc.")
        model_number = st.text_input("Model Number", placeholder="e.g., ST-350-72M")

    with col2:
        serial_number = st.text_input("Serial Number", placeholder="e.g., SN123456789")
        operator_name = st.text_input("Operator Name*", placeholder="Your name")
        facility = st.text_input("Test Facility", placeholder="e.g., Lab A")

    specimen_description = st.text_area(
        "Specimen Description",
        placeholder="Additional details about the specimen..."
    )

    st.markdown("---")

    # Environmental conditions
    st.subheader("Environmental Conditions")

    col1, col2, col3 = st.columns(3)

    with col1:
        ambient_temp = st.number_input("Ambient Temperature (°C)", min_value=-50.0, max_value=100.0, value=25.0)

    with col2:
        ambient_humidity = st.number_input("Ambient Humidity (%RH)", min_value=0.0, max_value=100.0, value=50.0)

    with col3:
        test_station = st.text_input("Test Station", placeholder="e.g., Station 1")

    # Notes
    notes = st.text_area("Test Notes", placeholder="Any special notes or observations...")

    # Start button
    st.markdown("---")

    if st.button("Start Test Run", type="primary", use_container_width=True):
        if not specimen_id or not operator_name:
            st.error("Please fill in all required fields (marked with *)")
        else:
            # Create test run
            executor = ProtocolExecutor(session)

            test_run = executor.create_test_run(
                protocol=selected_protocol,
                specimen_id=specimen_id,
                operator_name=operator_name,
                manufacturer=manufacturer,
                model_number=model_number,
                serial_number=serial_number,
                specimen_description=specimen_description,
                facility=facility,
                test_station=test_station,
                ambient_temperature=ambient_temp,
                ambient_humidity=ambient_humidity,
            )

            if notes:
                test_run.notes = notes

            # Start the test run
            executor.start_test_run(test_run)

            # Store in session state
            st.session_state.current_test_run = test_run.id

            st.success(f"Test run started: {test_run.run_id}")
            st.rerun()

    session.close()


def render_active_test_run():
    """Render the active test run interface."""
    session = get_session(st.session_state.engine)
    executor = ProtocolExecutor(session)

    from src.models import TestRun
    test_run = session.query(TestRun).filter_by(id=st.session_state.current_test_run).first()

    if not test_run:
        st.error("Test run not found.")
        st.session_state.current_test_run = None
        session.close()
        return

    # Header
    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        st.title(f"Test Run: {test_run.run_id}")
        st.markdown(f"**Specimen:** {test_run.specimen_id}")

    with col2:
        status_color = {
            TestStatus.IN_PROGRESS: "🟢",
            TestStatus.PENDING: "🟡",
            TestStatus.COMPLETED: "🔵",
            TestStatus.FAILED: "🔴",
            TestStatus.ABORTED: "⚫"
        }
        st.markdown(f"### {status_color.get(test_run.status, '')} {test_run.status.value.upper()}")

    with col3:
        if test_run.status == TestStatus.IN_PROGRESS:
            if st.button("Abort Test", type="secondary"):
                executor.abort_test_run(test_run, "Aborted by operator")
                st.session_state.current_test_run = None
                st.rerun()

    st.markdown("---")

    # Progress
    summary = executor.get_test_run_summary(test_run)
    progress = summary["progress"]

    st.progress(progress["percentage"] / 100)
    st.markdown(f"**Progress:** {progress['completed_steps']} / {progress['total_steps']} steps completed ({progress['percentage']:.1f}%)")

    st.markdown("---")

    # Test steps
    st.subheader("Test Steps")

    for step in test_run.test_steps:
        render_test_step(step, executor, test_run)

    # Complete test button
    if test_run.status == TestStatus.IN_PROGRESS:
        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Complete Test (PASS)", type="primary", use_container_width=True):
                executor.complete_test_run(test_run, TestResult.PASS)
                st.session_state.current_test_run = None
                st.success("Test completed with PASS result!")
                st.rerun()

        with col2:
            if st.button("Complete Test (FAIL)", type="secondary", use_container_width=True):
                executor.complete_test_run(test_run, TestResult.FAIL)
                st.session_state.current_test_run = None
                st.warning("Test completed with FAIL result.")
                st.rerun()

    session.close()


def render_test_step(step, executor, test_run):
    """Render a single test step."""
    status_icons = {
        TestStatus.PENDING: "⏳",
        TestStatus.IN_PROGRESS: "▶️",
        TestStatus.COMPLETED: "✅",
        TestStatus.FAILED: "❌"
    }

    icon = status_icons.get(step.status, "❓")

    with st.expander(f"{icon} Step {step.step_number}: {step.description}", expanded=(step.status == TestStatus.IN_PROGRESS)):
        st.markdown(f"**Action:** {step.action}")
        st.markdown(f"**Status:** {step.status.value}")

        if step.status == TestStatus.PENDING:
            if st.button(f"Start Step {step.step_number}", key=f"start_{step.id}"):
                executor.start_step(step)
                st.rerun()

        elif step.status == TestStatus.IN_PROGRESS:
            # Input fields for observations and data
            observations = st.text_area(
                "Observations",
                value=step.observations or "",
                key=f"obs_{step.id}",
                placeholder="Enter observations..."
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Complete Step {step.step_number}", key=f"complete_{step.id}", type="primary"):
                    executor.complete_step(step, observations=observations, pass_fail=True)
                    st.rerun()

            with col2:
                if st.button(f"Mark as Failed", key=f"fail_{step.id}", type="secondary"):
                    executor.complete_step(step, observations=observations, pass_fail=False)
                    st.rerun()

        elif step.status == TestStatus.COMPLETED:
            if step.observations:
                st.markdown(f"**Observations:** {step.observations}")
            if step.pass_fail is not None:
                st.markdown(f"**Result:** {'✅ PASS' if step.pass_fail else '❌ FAIL'}")
