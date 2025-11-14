"""QC Review Component"""

import streamlit as st
from datetime import datetime


def render_qc_review():
    """Render QC review interface"""

    st.markdown("### QC Review and Approval")

    # Check if we have results
    if 'test_protocol' not in st.session_state or st.session_state['test_protocol'] is None:
        st.info("No test data available for review. Please execute a test first.")
        return

    protocol = st.session_state['test_protocol']
    results = protocol.get_full_results()

    # Test summary
    st.markdown("#### Test Summary")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**Test ID:** {results['test_execution_id']}")
        st.markdown(f"**Sample ID:** {results['sample_info']['sample_id']}")
        st.markdown(f"**Protocol:** {results['protocol_id']}")

    with col2:
        st.markdown(f"**Test Date:** {results['test_conditions']['test_date']}")
        st.markdown(f"**Operator:** {results['test_conditions']['operator_id']}")
        overall_result = results['pass_fail_assessment']['overall_result']

        if overall_result == "PASS":
            st.success(f"**Result:** {overall_result}")
        elif overall_result == "WARNING":
            st.warning(f"**Result:** {overall_result}")
        else:
            st.error(f"**Result:** {overall_result}")

    st.markdown("---")

    # QC Checklist
    st.markdown("#### QC Verification Checklist")

    with st.form("qc_verification_form"):
        st.markdown("**Calibration Verification**")
        cal_temp = st.checkbox("Temperature sensor calibration verified")
        cal_humidity = st.checkbox("Humidity sensor calibration verified")

        st.markdown("**Equipment Verification**")
        eq_scale = st.checkbox("Reference scale condition verified")
        eq_tape = st.checkbox("Adhesive tape lot verified for ASTM compliance")

        st.markdown("**Data Verification**")
        data_complete = st.checkbox("All required data fields completed")
        data_reasonable = st.checkbox("Data values are within reasonable ranges")
        data_consistent = st.checkbox("Data is internally consistent")

        st.markdown("**Documentation Verification**")
        doc_photos = st.checkbox("Test photographs attached and labeled")
        doc_cal_cert = st.checkbox("Calibration certificates on file")

        st.markdown("---")

        st.markdown("**QC Review**")

        reviewer_id = st.text_input("Reviewer ID", placeholder="e.g., QC-001")

        review_notes = st.text_area(
            "QC Review Notes",
            placeholder="Enter any observations, concerns, or recommendations...",
            height=150
        )

        qc_decision = st.radio(
            "QC Decision",
            ["Approve", "Approve with Comments", "Reject - Retest Required", "Reject - Invalid Data"]
        )

        submitted = st.form_submit_button("Submit QC Review", type="primary")

        if submitted:
            if not reviewer_id:
                st.error("Please enter Reviewer ID")
            else:
                # Store QC verification data
                qc_data = {
                    "calibration_verified": cal_temp and cal_humidity,
                    "reference_scale_verified": eq_scale,
                    "tape_lot_verified": eq_tape,
                    "data_verified": data_complete and data_reasonable and data_consistent,
                    "documentation_verified": doc_photos and doc_cal_cert,
                    "data_reviewed_by": reviewer_id,
                    "review_date": datetime.now().strftime("%Y-%m-%d"),
                    "qc_notes": review_notes,
                    "qc_decision": qc_decision,
                }

                protocol.qc_verification = qc_data
                st.session_state['qc_verified'] = True

                st.success(f"QC Review submitted: {qc_decision}")

                # Show next steps based on decision
                if "Approve" in qc_decision:
                    st.info("✅ Test approved. Proceed to report generation.")
                else:
                    st.warning("⚠️ Test rejected. Please review and take corrective action.")

    # Display current QC status
    if protocol.qc_verification:
        st.markdown("---")
        st.markdown("#### Current QC Status")

        qc_data = protocol.qc_verification

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**Reviewed by:** {qc_data.get('data_reviewed_by', 'N/A')}")
            st.markdown(f"**Review Date:** {qc_data.get('review_date', 'N/A')}")

        with col2:
            st.markdown(f"**Decision:** {qc_data.get('qc_decision', 'Pending')}")

        if qc_data.get('qc_notes'):
            st.markdown("**Notes:**")
            st.info(qc_data['qc_notes'])


if __name__ == "__main__":
    render_qc_review()
