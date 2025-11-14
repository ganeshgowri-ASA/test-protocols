"""Home page - Dashboard overview."""

import streamlit as st
from sqlalchemy import func

from test_protocols.database.connection import db
from test_protocols.models.schema import TestRun


def show():
    """Show home page dashboard."""
    st.title("🔬 Test Protocols Dashboard")
    st.markdown("**Modular PV Testing Protocol Framework**")
    st.markdown("---")

    # Get statistics
    with db.session_scope() as session:
        total_tests = session.query(func.count(TestRun.id)).scalar() or 0
        running_tests = (
            session.query(func.count(TestRun.id)).filter(TestRun.status == "running").scalar() or 0
        )
        completed_tests = (
            session.query(func.count(TestRun.id)).filter(TestRun.status == "completed").scalar()
            or 0
        )
        failed_tests = (
            session.query(func.count(TestRun.id)).filter(TestRun.status == "failed").scalar() or 0
        )

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Tests",
            value=total_tests,
            delta=None,
        )

    with col2:
        st.metric(
            label="Running",
            value=running_tests,
            delta=None,
        )

    with col3:
        st.metric(
            label="Completed",
            value=completed_tests,
            delta=None,
        )

    with col4:
        st.metric(
            label="Failed",
            value=failed_tests,
            delta=None,
        )

    st.markdown("---")

    # Recent tests
    st.subheader("Recent Test Runs")

    with db.session_scope() as session:
        recent_tests = (
            session.query(TestRun)
            .order_by(TestRun.created_at.desc())
            .limit(10)
            .all()
        )

        if recent_tests:
            for test in recent_tests:
                with st.expander(
                    f"{test.specimen_id} - {test.protocol_code} ({test.status.upper()})",
                    expanded=False,
                ):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.write(f"**Specimen:** {test.specimen_id}")
                        st.write(f"**Protocol:** {test.protocol_code}")
                        st.write(f"**Status:** {test.status}")

                    with col2:
                        st.write(f"**Module Type:** {test.module_type or 'N/A'}")
                        st.write(f"**Manufacturer:** {test.manufacturer or 'N/A'}")
                        st.write(f"**QC Status:** {test.qc_status}")

                    with col3:
                        st.write(f"**Started:** {test.start_date.strftime('%Y-%m-%d %H:%M')}")
                        if test.end_date:
                            st.write(f"**Ended:** {test.end_date.strftime('%Y-%m-%d %H:%M')}")
                        st.write(f"**Operator:** {test.operator or 'N/A'}")

                    if test.notes:
                        st.write(f"**Notes:** {test.notes}")
        else:
            st.info("No test runs found. Create a new test to get started!")

    # Quick actions
    st.markdown("---")
    st.subheader("Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("➕ Start New Test", use_container_width=True):
            st.switch_page("pages/new_test.py")

    with col2:
        if st.button("📊 View Analysis", use_container_width=True):
            st.switch_page("pages/analysis.py")

    with col3:
        if st.button("📄 Generate Report", use_container_width=True):
            st.switch_page("pages/reports.py")

    # Protocol information
    st.markdown("---")
    st.subheader("Available Protocols")

    st.markdown("""
    ### SALT-001: Salt Mist Corrosion Test
    - **Standard:** IEC 61701:2020
    - **Category:** Environmental Testing
    - **Duration:** 60-840 hours (5 severity levels)
    - **Features:**
        - Automated spray/dry cycle management
        - Real-time environmental monitoring
        - I-V curve tracking with degradation analysis
        - Visual inspection logging with image capture
        - IEC 61701 compliant QC checks
    """)
