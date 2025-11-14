"""Reports Generation Component"""

import streamlit as st
import json
from datetime import datetime


def render_reports():
    """Render reports generation interface"""

    st.markdown("### Test Reports")

    # Check if we have results
    if 'test_protocol' not in st.session_state or st.session_state['test_protocol'] is None:
        st.info("No test data available. Please execute a test first.")
        return

    protocol = st.session_state['test_protocol']
    results = protocol.get_full_results()

    # Report type selection
    report_type = st.selectbox(
        "Select Report Type",
        ["Executive Summary", "Full Technical Report", "QC Certificate", "Custom Report"]
    )

    # Report preview
    st.markdown("#### Report Preview")

    if report_type == "Executive Summary":
        render_executive_summary(results)

    elif report_type == "Full Technical Report":
        render_full_report(results)

    elif report_type == "QC Certificate":
        render_qc_certificate(results)

    else:
        st.info("Custom report builder coming soon!")

    # Export options
    st.markdown("---")
    st.markdown("#### Export Options")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Export PDF"):
            st.info("PDF export coming soon!")

    with col2:
        if st.button("Export Excel"):
            st.info("Excel export coming soon!")

    with col3:
        # JSON export
        results_json = json.dumps(results, indent=2)
        st.download_button(
            "Export JSON",
            results_json,
            file_name=f"{results['test_execution_id']}_report.json",
            mime="application/json"
        )


def render_executive_summary(results):
    """Render executive summary report"""

    st.markdown("---")
    st.markdown(f"## Executive Summary")
    st.markdown(f"**Test ID:** {results['test_execution_id']}")
    st.markdown(f"**Protocol:** {results['protocol_id']} v{results['protocol_version']}")
    st.markdown(f"**Date:** {results['metadata']['created_timestamp'][:10]}")

    st.markdown("### Test Result")

    overall_result = results['pass_fail_assessment']['overall_result']

    if overall_result == "PASS":
        st.success(f"✅ **{overall_result}**")
    elif overall_result == "WARNING":
        st.warning(f"⚠️ **{overall_result}**")
    else:
        st.error(f"❌ **{overall_result}**")

    st.markdown("### Key Findings")

    calc_results = results['calculated_results']

    st.markdown(f"""
- **Average Chalking Rating:** {calc_results['average_chalking_rating']:.2f}
- **Maximum Rating:** {calc_results['max_chalking_rating']:.2f}
- **Standard Deviation:** {calc_results['chalking_std_dev']:.2f}
- **Number of Measurements:** {calc_results['number_of_measurements']}
    """)

    st.markdown("### Sample Information")

    sample_info = results['sample_info']
    st.markdown(f"""
- **Sample ID:** {sample_info['sample_id']}
- **Module Type:** {sample_info['module_type']}
- **Backsheet Material:** {sample_info['backsheet_material']}
    """)


def render_full_report(results):
    """Render full technical report"""

    st.markdown("---")
    st.markdown(f"## Full Technical Report")
    st.markdown(f"### Test Identification")
    st.markdown(f"**Test Execution ID:** {results['test_execution_id']}")
    st.markdown(f"**Protocol:** {results['protocol_id']} v{results['protocol_version']}")
    st.markdown(f"**Test Date:** {results['metadata']['created_timestamp']}")

    st.markdown("### Sample Information")
    sample_info = results['sample_info']
    for key, value in sample_info.items():
        if value is not None:
            st.markdown(f"- **{key.replace('_', ' ').title()}:** {value}")

    st.markdown("### Test Conditions")
    test_conditions = results['test_conditions']
    for key, value in test_conditions.items():
        if value is not None:
            st.markdown(f"- **{key.replace('_', ' ').title()}:** {value}")

    st.markdown("### Calculated Results")
    calc_results = results['calculated_results']
    for key, value in calc_results.items():
        st.markdown(f"- **{key.replace('_', ' ').title()}:** {value}")

    st.markdown("### Pass/Fail Assessment")
    assessment = results['pass_fail_assessment']

    st.markdown(f"**Overall Result:** {assessment['overall_result']}")
    st.markdown(f"**Notes:** {assessment['notes']}")

    st.markdown("**Criteria Evaluations:**")
    for criterion in assessment['criteria_evaluations']:
        st.markdown(f"- {criterion['criterion']}: {criterion['actual_value']} ({criterion['result']})")

    st.markdown("### Measurement Data")
    if results['measurements']:
        st.dataframe(results['measurements'], use_container_width=True)


def render_qc_certificate(results):
    """Render QC certificate"""

    st.markdown("---")
    st.markdown("## Quality Control Certificate")

    st.markdown(f"**Certificate ID:** {results['test_execution_id']}")
    st.markdown(f"**Issue Date:** {datetime.now().strftime('%Y-%m-%d')}")

    st.markdown("### Test Identification")
    st.markdown(f"- **Sample ID:** {results['sample_info']['sample_id']}")
    st.markdown(f"- **Protocol:** {results['protocol_id']}")
    st.markdown(f"- **Test Date:** {results['test_conditions']['test_date']}")

    st.markdown("### Result")
    overall_result = results['pass_fail_assessment']['overall_result']
    st.markdown(f"**Test Result:** {overall_result}")

    st.markdown("### Verification")
    st.markdown("- **Tested by:** " + results['test_conditions'].get('operator_id', 'N/A'))
    st.markdown("- **Reviewed by:** _[To be filled]_")
    st.markdown("- **Approved by:** _[To be filled]_")

    st.markdown("### Signature Block")
    st.markdown("_[Digital signatures to be implemented]_")


if __name__ == "__main__":
    render_reports()
