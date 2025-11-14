"""Results viewer component for displaying test results."""

import streamlit as st
from src.database.connection import get_session
from src.database import models as db


def render_results_viewer():
    """Render the results viewer interface."""
    st.subheader("Test Results Database")

    with get_session() as session:
        # Get all test executions
        test_executions = session.query(db.TestExecution).order_by(
            db.TestExecution.start_time.desc()
        ).all()

        if not test_executions:
            st.info("No test results available. Start a new test to see results here.")
            return

        # Display summary
        st.metric("Total Tests", len(test_executions))

        # Filter options
        col1, col2, col3 = st.columns(3)

        with col1:
            status_filter = st.selectbox(
                "Filter by Status",
                ["All", "Pass", "Fail", "In Progress"],
                key="status_filter",
            )

        with col2:
            operator_filter = st.selectbox(
                "Filter by Operator",
                ["All"] + list(set(te.operator for te in test_executions)),
                key="operator_filter",
            )

        # Display test results
        for test_exec in test_executions:
            # Apply filters
            if status_filter != "All" and test_exec.overall_result != status_filter:
                continue
            if operator_filter != "All" and test_exec.operator != operator_filter:
                continue

            # Display test card
            with st.expander(
                f"Test {test_exec.test_id} - {test_exec.module_serial_number} - {test_exec.overall_result or 'In Progress'}"
            ):
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.write(f"**Test ID:** {test_exec.test_id}")
                    st.write(f"**Protocol:** {test_exec.protocol.protocol_id}")

                with col2:
                    st.write(f"**Module S/N:** {test_exec.module_serial_number}")
                    st.write(f"**Operator:** {test_exec.operator}")

                with col3:
                    st.write(f"**Start Time:** {test_exec.start_time.strftime('%Y-%m-%d %H:%M')}")
                    if test_exec.end_time:
                        st.write(f"**End Time:** {test_exec.end_time.strftime('%Y-%m-%d %H:%M')}")

                with col4:
                    st.write(f"**Status:** {test_exec.status}")
                    if test_exec.overall_result:
                        result_icon = "🟢" if test_exec.overall_result == "Pass" else "🔴"
                        st.write(f"**Result:** {result_icon} {test_exec.overall_result}")

                # Display test steps
                if test_exec.test_steps:
                    st.markdown("**Test Steps:**")
                    for step in test_exec.test_steps:
                        status_icon = "✅" if step.passed else "❌" if step.passed is False else "⏳"
                        st.write(f"{status_icon} Step {step.step_number}: {step.name}")

                # Action buttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("View Details", key=f"view_{test_exec.id}"):
                        st.info("Detailed view coming soon...")
                with col2:
                    if st.button("Export Report", key=f"export_{test_exec.id}"):
                        st.info("Export functionality coming soon...")
                with col3:
                    if st.button("Delete", key=f"delete_{test_exec.id}"):
                        st.warning("Delete confirmation required")
