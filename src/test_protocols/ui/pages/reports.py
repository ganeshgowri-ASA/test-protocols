"""Reports page."""

import streamlit as st


def show_reports_page():
    """Display reports page."""
    st.title("Reports")
    st.write("Generate and manage test reports.")

    st.info("📄 Report generation features coming soon!")

    st.markdown(
        """
    ### Planned Features:
    - PDF report generation
    - HTML report generation
    - Excel export with multiple sheets
    - Customizable report templates
    - Batch report generation
    - Email delivery
    """
    )

    # If there are test results, show option to generate report
    if "test_results" in st.session_state:
        results = st.session_state["test_results"]

        st.markdown("---")
        st.subheader("Generate Report for Current Session")

        st.write(f"Session ID: **{results['session_id']}**")

        report_format = st.selectbox("Report Format", ["PDF", "HTML", "Excel", "JSON"])

        if st.button("Generate Report", disabled=True):
            st.info("Report generation will be implemented in future version.")


if __name__ == "__main__":
    show_reports_page()
