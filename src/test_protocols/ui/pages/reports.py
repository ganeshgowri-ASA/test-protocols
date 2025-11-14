"""Reports page for generating test reports."""

import streamlit as st

from test_protocols.database.connection import db
from test_protocols.models.schema import TestRun


def show():
    """Show reports page."""
    st.title("📄 Test Reports")
    st.markdown("Generate and view test reports")
    st.markdown("---")

    # Get completed tests
    with db.session_scope() as session:
        completed_tests = (
            session.query(TestRun)
            .filter(TestRun.status == "completed")
            .order_by(TestRun.end_date.desc())
            .all()
        )

        if not completed_tests:
            st.info("No completed tests available for report generation")
            return

        # Test selection
        test_options = {
            f"{test.specimen_id} - {test.protocol_code} (ID: {test.id})": test.id
            for test in completed_tests
        }

        selected_test_label = st.selectbox("Select Test", options=list(test_options.keys()))
        test_run_id = test_options[selected_test_label]

        test_run = session.query(TestRun).filter(TestRun.id == test_run_id).first()

        if not test_run:
            st.error("Test not found")
            return

        st.markdown("---")
        st.subheader("Report Generation")

        col1, col2 = st.columns(2)

        with col1:
            report_format = st.selectbox("Report Format", options=["PDF", "Excel", "HTML", "JSON"])

        with col2:
            include_images = st.checkbox("Include Images", value=True)
            include_raw_data = st.checkbox("Include Raw Data", value=False)

        if st.button("📄 Generate Report", type="primary", use_container_width=True):
            st.info("Report generation feature coming soon!")
            st.markdown("""
            **Report will include:**
            - Test parameters and configuration
            - Environmental conditions log
            - I-V curve measurements and analysis
            - Visual inspection images and corrosion ratings
            - Power degradation analysis
            - Quality control results
            - Pass/fail determination
            """)
