"""
Reports Page

Generate and download test reports.
"""

import streamlit as st
from pathlib import Path
import sys
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def render():
    """Render reports page"""

    st.header("Reports")

    # Check if test run exists
    if not st.session_state.get("current_test_run"):
        st.warning("No active test run.")
        st.info("Go to 'Protocol Selection' to start a new test run.")
        return

    protocol_instance = st.session_state.protocol_instance
    test_run = st.session_state.current_test_run
    test_data = st.session_state.test_data

    if not test_data:
        st.info("No test data available yet. Complete some test steps first.")
        return

    # Report generation options
    st.subheader("Report Generation")

    col1, col2 = st.columns(2)

    with col1:
        report_format = st.selectbox(
            "Report Format",
            ["Markdown", "PDF", "HTML", "JSON"],
            help="Select the output format for the report"
        )

    with col2:
        include_raw_data = st.checkbox("Include Raw Data", value=False)
        include_charts = st.checkbox("Include Charts", value=True)

    st.markdown("---")

    # Report preview
    st.subheader("Report Preview")

    try:
        # Generate report
        report_content = protocol_instance.generate_report()

        if report_format == "Markdown":
            st.markdown(report_content)
        elif report_format == "JSON":
            import json
            report_json = {
                "test_run": test_run,
                "test_data": test_data,
                "qc_results": st.session_state.qc_results,
                "analysis_results": st.session_state.analysis_results
            }
            st.json(report_json)
        else:
            st.markdown(report_content)
            st.info(f"{report_format} export coming soon!")

    except Exception as e:
        st.error(f"Error generating report: {e}")

    st.markdown("---")

    # Download section
    st.subheader("Download Report")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Download Markdown", type="primary", use_container_width=True):
            try:
                report_content = protocol_instance.generate_report()
                filename = f"{test_run['run_id']}_report_{datetime.now().strftime('%Y%m%d')}.md"

                st.download_button(
                    label="📥 Download MD File",
                    data=report_content,
                    file_name=filename,
                    mime="text/markdown"
                )
            except Exception as e:
                st.error(f"Error: {e}")

    with col2:
        if st.button("Download JSON", use_container_width=True):
            try:
                import json
                report_json = {
                    "test_run": test_run,
                    "protocol_id": test_run["protocol_id"],
                    "test_data": test_data,
                    "qc_results": st.session_state.qc_results,
                    "analysis_results": st.session_state.analysis_results,
                    "generated_at": datetime.now().isoformat()
                }

                filename = f"{test_run['run_id']}_data_{datetime.now().strftime('%Y%m%d')}.json"

                st.download_button(
                    label="📥 Download JSON File",
                    data=json.dumps(report_json, indent=2),
                    file_name=filename,
                    mime="application/json"
                )
            except Exception as e:
                st.error(f"Error: {e}")

    with col3:
        if st.button("Export CSV", use_container_width=True):
            try:
                import pandas as pd

                # Convert test data to DataFrame
                df = pd.DataFrame([test_data])

                filename = f"{test_run['run_id']}_data_{datetime.now().strftime('%Y%m%d')}.csv"

                st.download_button(
                    label="📥 Download CSV File",
                    data=df.to_csv(index=False),
                    file_name=filename,
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown("---")

    # Report templates
    st.subheader("Report Templates")

    st.info("Custom report templates feature coming soon!")

    with st.expander("Template Options"):
        st.markdown("""
        Available templates:
        - **Standard Report**: Complete test report with all data
        - **Executive Summary**: High-level overview for management
        - **Technical Details**: Detailed technical data for engineers
        - **QC Report**: Quality control focused report
        - **Compliance Report**: Standards compliance documentation
        """)

    st.markdown("---")

    # Export to external systems
    st.subheader("Export to External Systems")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Export to LIMS", use_container_width=True):
            st.info("LIMS integration coming soon!")

    with col2:
        if st.button("Export to QMS", use_container_width=True):
            st.info("QMS integration coming soon!")

    with col3:
        if st.button("Export to PM System", use_container_width=True):
            st.info("Project Management integration coming soon!")
