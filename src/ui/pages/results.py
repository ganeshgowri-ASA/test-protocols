"""Results page for viewing test results."""

import streamlit as st
import pandas as pd
from datetime import datetime

from src.models.base import get_session
from src.models import TestRun
from src.models.test_run import TestStatus, TestResult


def render_results_page():
    """Render the results page."""
    st.title("📊 Test Results")
    st.markdown("View and analyze test results")

    # Get all test runs
    session = get_session(st.session_state.engine)
    test_runs = session.query(TestRun).order_by(TestRun.created_at.desc()).all()

    if not test_runs:
        st.info("No test results available yet. Run a test to see results here.")
        session.close()
        return

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox(
            "Status",
            ["All"] + [s.value for s in TestStatus]
        )

    with col2:
        result_filter = st.selectbox(
            "Result",
            ["All"] + [r.value for r in TestResult]
        )

    with col3:
        search_term = st.text_input("Search", placeholder="Specimen ID...")

    # Apply filters
    filtered_runs = test_runs

    if status_filter != "All":
        filtered_runs = [r for r in filtered_runs if r.status.value == status_filter]

    if result_filter != "All":
        filtered_runs = [r for r in filtered_runs if r.result.value == result_filter]

    if search_term:
        filtered_runs = [
            r for r in filtered_runs
            if search_term.lower() in r.specimen_id.lower() or
               search_term.lower() in r.run_id.lower()
        ]

    st.markdown("---")

    # Summary statistics
    st.subheader("Summary Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_tests = len(test_runs)
        st.metric("Total Tests", total_tests)

    with col2:
        completed = len([r for r in test_runs if r.status == TestStatus.COMPLETED])
        st.metric("Completed", completed)

    with col3:
        passed = len([r for r in test_runs if r.result == TestResult.PASS])
        st.metric("Passed", passed)

    with col4:
        failed = len([r for r in test_runs if r.result == TestResult.FAIL])
        st.metric("Failed", failed)

    st.markdown("---")

    # Results table
    st.subheader(f"Test Runs ({len(filtered_runs)} results)")

    if filtered_runs:
        # Create DataFrame
        df_data = []
        for run in filtered_runs:
            df_data.append({
                "Run ID": run.run_id,
                "Specimen": run.specimen_id,
                "Protocol": run.protocol.protocol_id if run.protocol else "N/A",
                "Status": run.status.value,
                "Result": run.result.value,
                "Operator": run.operator_name or "N/A",
                "Started": run.started_at.strftime("%Y-%m-%d %H:%M") if run.started_at else "N/A",
                "Completed": run.completed_at.strftime("%Y-%m-%d %H:%M") if run.completed_at else "N/A",
            })

        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)

        # Detailed view
        st.markdown("---")
        st.subheader("Detailed View")

        selected_run_id = st.selectbox(
            "Select test run to view details",
            [r.run_id for r in filtered_runs]
        )

        if selected_run_id:
            selected_run = next(r for r in filtered_runs if r.run_id == selected_run_id)
            render_test_run_details(selected_run)

    else:
        st.info("No test runs match the selected filters.")

    session.close()


def render_test_run_details(test_run):
    """Render detailed view of a test run."""
    with st.expander(f"Details: {test_run.run_id}", expanded=True):
        # Basic information
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**Specimen Information**")
            st.markdown(f"- ID: {test_run.specimen_id}")
            st.markdown(f"- Manufacturer: {test_run.manufacturer or 'N/A'}")
            st.markdown(f"- Model: {test_run.model_number or 'N/A'}")
            st.markdown(f"- Serial: {test_run.serial_number or 'N/A'}")

        with col2:
            st.markdown("**Test Information**")
            st.markdown(f"- Protocol: {test_run.protocol.protocol_id if test_run.protocol else 'N/A'}")
            st.markdown(f"- Operator: {test_run.operator_name or 'N/A'}")
            st.markdown(f"- Facility: {test_run.facility or 'N/A'}")
            st.markdown(f"- Station: {test_run.test_station or 'N/A'}")

        with col3:
            st.markdown("**Status & Results**")
            st.markdown(f"- Status: {test_run.status.value}")
            st.markdown(f"- Result: {test_run.result.value}")
            if test_run.started_at:
                st.markdown(f"- Started: {test_run.started_at.strftime('%Y-%m-%d %H:%M')}")
            if test_run.completed_at:
                st.markdown(f"- Completed: {test_run.completed_at.strftime('%Y-%m-%d %H:%M')}")

        # Environmental conditions
        if test_run.ambient_temperature or test_run.ambient_humidity:
            st.markdown("**Environmental Conditions**")
            if test_run.ambient_temperature:
                st.markdown(f"- Temperature: {test_run.ambient_temperature}°C")
            if test_run.ambient_humidity:
                st.markdown(f"- Humidity: {test_run.ambient_humidity}%RH")

        # Notes
        if test_run.notes:
            st.markdown("**Notes**")
            st.markdown(test_run.notes)

        # Measurements
        if test_run.measurements:
            st.markdown("**Measurements**")

            meas_data = []
            for m in test_run.measurements:
                value = m.value_numeric or m.value_text or m.value_boolean
                meas_data.append({
                    "Parameter": m.parameter,
                    "Value": value,
                    "Unit": m.unit or "",
                    "Type": m.measurement_type,
                    "Timestamp": m.measured_at.strftime("%Y-%m-%d %H:%M:%S") if m.measured_at else "N/A"
                })

            df_meas = pd.DataFrame(meas_data)
            st.dataframe(df_meas, use_container_width=True)

        # Test steps
        if test_run.test_steps:
            st.markdown("**Test Steps**")

            steps_data = []
            for s in test_run.test_steps:
                steps_data.append({
                    "Step": s.step_number,
                    "Description": s.description,
                    "Status": s.status.value,
                    "Pass/Fail": "✅" if s.pass_fail else "❌" if s.pass_fail is not None else "N/A"
                })

            df_steps = pd.DataFrame(steps_data)
            st.dataframe(df_steps, use_container_width=True)
