"""
Test Results Page
"""

import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.models import SessionLocal, TestExecution, TestMeasurement, TestResult


def render_test_results():
    """Render the test results page"""
    st.title("📋 Test Results")

    db = SessionLocal()

    try:
        # Get all test executions
        tests = db.query(TestExecution).order_by(TestExecution.created_at.desc()).all()

        if not tests:
            st.info("No test results available. Execute tests to see results here.")
            return

        # Test selection
        test_options = {
            t.id: f"{t.test_number} - {t.protocol.protocol_name if t.protocol else 'N/A'} - {t.created_at.strftime('%Y-%m-%d %H:%M')}"
            for t in tests
        }

        selected_test_id = st.selectbox(
            "Select Test",
            options=list(test_options.keys()),
            format_func=lambda x: test_options[x]
        )

        test = db.query(TestExecution).filter(TestExecution.id == selected_test_id).first()

        if not test:
            st.error("Test not found")
            return

        # Test summary
        st.header("Test Summary")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Test Number", test.test_number)

        with col2:
            st.metric("Protocol", test.protocol.protocol_name if test.protocol else 'N/A')

        with col3:
            status_color = "🟢" if test.outcome and test.outcome.value == "pass" else "🔴"
            st.metric("Outcome", f"{status_color} {test.outcome.value.upper() if test.outcome else 'N/A'}")

        with col4:
            duration = test.duration_seconds or 0
            st.metric("Duration", f"{duration:.1f} s")

        # Test details
        with st.expander("Test Details", expanded=True):
            col1, col2 = st.columns(2)

            with col1:
                st.write("**Sample:**", test.sample.sample_id if test.sample else 'N/A')
                st.write("**Operator:**", test.operator_name or 'N/A')
                st.write("**Equipment:**", test.equipment.name if test.equipment else 'N/A')

            with col2:
                st.write("**Start Time:**", test.actual_start.strftime('%Y-%m-%d %H:%M:%S') if test.actual_start else 'N/A')
                st.write("**End Time:**", test.actual_end.strftime('%Y-%m-%d %H:%M:%S') if test.actual_end else 'N/A')
                st.write("**Status:**", test.status.value if test.status else 'N/A')

        # Measurements
        st.header("Measurements")

        measurements = test.measurements
        if measurements:
            import pandas as pd

            data = []
            for m in measurements:
                data.append({
                    'Timestamp': m.timestamp.strftime('%H:%M:%S') if m.timestamp else 'N/A',
                    'Point': m.measurement_point or '-',
                    'Measurement': m.measurement_name,
                    'Value': f"{m.value:.4f}" if m.value is not None else m.value_text or 'N/A',
                    'Unit': m.unit or '-',
                    'Within Limits': '✅' if m.within_limits else '❌' if m.within_limits is not None else '-'
                })

            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No measurements recorded")

        # Pass/Fail Criteria
        st.header("Pass/Fail Criteria")

        results = test.results
        if results:
            for result in results:
                with st.container():
                    if result.passed:
                        st.success(f"✅ {result.criterion_name}")
                    else:
                        st.error(f"❌ {result.criterion_name}")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.caption(f"Condition: `{result.criterion_condition}`")
                    with col2:
                        st.caption(f"Severity: {result.severity}")

                    if result.failure_reason:
                        st.caption(f"Reason: {result.failure_reason}")
        else:
            st.info("No criteria evaluation results")

        # Notes
        if test.pre_test_notes or test.post_test_notes or test.anomalies:
            st.header("Notes")

            if test.pre_test_notes:
                st.subheader("Pre-Test Notes")
                st.write(test.pre_test_notes)

            if test.post_test_notes:
                st.subheader("Post-Test Notes")
                st.write(test.post_test_notes)

            if test.anomalies:
                st.subheader("Anomalies")
                st.warning(test.anomalies)

    finally:
        db.close()
