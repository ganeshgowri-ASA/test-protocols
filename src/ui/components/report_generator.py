"""Report generation component."""

import streamlit as st
from datetime import datetime
import json


def render_report_generator():
    """Render report generation interface."""
    st.title("Report Generation")

    protocol_id = st.session_state.current_protocol
    test_data = st.session_state.test_data
    data_processor = st.session_state.data_processor

    # Generate summary report
    summary_report = data_processor.generate_summary_report(protocol_id, test_data)

    # Report header
    st.subheader("Test Report Summary")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**Protocol:** {summary_report.get('protocol_id', 'N/A').upper()}")
        st.markdown(f"**Test Run ID:** {summary_report.get('test_run_id', 'N/A')}")
        st.markdown(f"**Sample ID:** {summary_report.get('sample_id', 'N/A')}")

    with col2:
        st.markdown(f"**Operator:** {summary_report.get('operator', 'N/A')}")
        st.markdown(f"**Test Date:** {summary_report.get('timestamp', 'N/A')}")
        st.markdown(f"**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Data summary
    st.subheader("Data Summary")

    data_summary = summary_report.get('data_summary', {})

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Measurements",
            data_summary.get('total_measurements', 0)
        )

    with col2:
        conc_range = data_summary.get('concentration_range', {})
        st.metric(
            "Concentration Range",
            f"{conc_range.get('min', 0):.1f} - {conc_range.get('max', 0):.1f} suns"
        )

    with col3:
        temp_range = data_summary.get('temperature_range', {})
        st.metric(
            "Temperature Range",
            f"{temp_range.get('min', 0):.1f} - {temp_range.get('max', 0):.1f} °C"
        )

    # Statistical summary
    st.subheader("Statistical Summary")

    statistics = summary_report.get('statistics', {})

    if statistics:
        # Create summary table
        stats_data = []
        for param, stats in statistics.items():
            if isinstance(stats, dict):
                stats_data.append({
                    'Parameter': param.replace('_', ' ').title(),
                    'Mean': f"{stats.get('mean', 0):.3f}",
                    'Std Dev': f"{stats.get('std', 0):.3f}",
                    'Min': f"{stats.get('min', 0):.3f}",
                    'Max': f"{stats.get('max', 0):.3f}"
                })

        import pandas as pd
        stats_df = pd.DataFrame(stats_data)
        st.table(stats_df)

    # Analysis results
    st.subheader("Analysis Results")

    analysis = summary_report.get('analysis', {})

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Temperature Coefficients**")
        temp_coeff_eff = analysis.get('temperature_coefficient_efficiency')
        temp_coeff_voc = analysis.get('temperature_coefficient_voc')

        if temp_coeff_eff is not None:
            st.markdown(f"- Efficiency: {temp_coeff_eff:.4f} %/°C")
        if temp_coeff_voc is not None:
            st.markdown(f"- Voc: {temp_coeff_voc:.4f} %/°C")

    with col2:
        st.markdown("**Concentration Coefficient**")
        conc_coeff_eff = analysis.get('concentration_coefficient_efficiency')

        if conc_coeff_eff is not None:
            st.markdown(f"- Efficiency: {conc_coeff_eff:.4f} %/sun")

    # Quality indicators
    st.subheader("Quality Indicators")

    quality = summary_report.get('quality_indicators', {})

    col1, col2 = st.columns(2)

    with col1:
        eff_outliers = quality.get('outliers_efficiency', [])
        if eff_outliers:
            st.warning(f"Efficiency outliers detected: {len(eff_outliers)} point(s)")
        else:
            st.success("No efficiency outliers detected")

    with col2:
        ff_outliers = quality.get('outliers_fill_factor', [])
        if ff_outliers:
            st.warning(f"Fill factor outliers detected: {len(ff_outliers)} point(s)")
        else:
            st.success("No fill factor outliers detected")

    # Report export
    st.subheader("Export Report")

    col1, col2, col3 = st.columns(3)

    with col1:
        # JSON export
        json_report = json.dumps(summary_report, indent=2)
        st.download_button(
            label="Download JSON Report",
            data=json_report,
            file_name=f"{test_data.get('test_run_id', 'test')}_report.json",
            mime="application/json"
        )

    with col2:
        # Text report
        text_report = generate_text_report(summary_report)
        st.download_button(
            label="Download Text Report",
            data=text_report,
            file_name=f"{test_data.get('test_run_id', 'test')}_report.txt",
            mime="text/plain"
        )

    with col3:
        st.info("PDF export coming soon")


def generate_text_report(summary_report: dict) -> str:
    """
    Generate formatted text report.

    Args:
        summary_report: Summary report dictionary

    Returns:
        Formatted text report
    """
    report_lines = []

    report_lines.append("=" * 80)
    report_lines.append("TEST PROTOCOL REPORT")
    report_lines.append("=" * 80)
    report_lines.append("")

    # Header
    report_lines.append(f"Protocol: {summary_report.get('protocol_id', 'N/A').upper()}")
    report_lines.append(f"Test Run ID: {summary_report.get('test_run_id', 'N/A')}")
    report_lines.append(f"Sample ID: {summary_report.get('sample_id', 'N/A')}")
    report_lines.append(f"Operator: {summary_report.get('operator', 'N/A')}")
    report_lines.append(f"Test Date: {summary_report.get('timestamp', 'N/A')}")
    report_lines.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")

    # Data summary
    report_lines.append("-" * 80)
    report_lines.append("DATA SUMMARY")
    report_lines.append("-" * 80)

    data_summary = summary_report.get('data_summary', {})
    report_lines.append(f"Total Measurements: {data_summary.get('total_measurements', 0)}")

    conc_range = data_summary.get('concentration_range', {})
    report_lines.append(
        f"Concentration Range: {conc_range.get('min', 0):.1f} - "
        f"{conc_range.get('max', 0):.1f} suns"
    )

    temp_range = data_summary.get('temperature_range', {})
    report_lines.append(
        f"Temperature Range: {temp_range.get('min', 0):.1f} - "
        f"{temp_range.get('max', 0):.1f} °C"
    )
    report_lines.append("")

    # Analysis
    report_lines.append("-" * 80)
    report_lines.append("ANALYSIS RESULTS")
    report_lines.append("-" * 80)

    analysis = summary_report.get('analysis', {})

    temp_coeff_eff = analysis.get('temperature_coefficient_efficiency')
    if temp_coeff_eff is not None:
        report_lines.append(f"Temperature Coefficient (Efficiency): {temp_coeff_eff:.4f} %/°C")

    temp_coeff_voc = analysis.get('temperature_coefficient_voc')
    if temp_coeff_voc is not None:
        report_lines.append(f"Temperature Coefficient (Voc): {temp_coeff_voc:.4f} %/°C")

    conc_coeff_eff = analysis.get('concentration_coefficient_efficiency')
    if conc_coeff_eff is not None:
        report_lines.append(f"Concentration Coefficient (Efficiency): {conc_coeff_eff:.4f} %/sun")

    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("END OF REPORT")
    report_lines.append("=" * 80)

    return "\n".join(report_lines)
