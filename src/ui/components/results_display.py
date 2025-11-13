"""Results display component for Streamlit UI."""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List


def render_results_summary(results: Dict[str, Any]) -> None:
    """
    Render test results summary.

    Args:
        results: Results dictionary
    """
    st.subheader("Test Results Summary")

    summary = results.get("summary", {})

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Measurements",
            summary.get("total_measurements", 0)
        )

    with col2:
        avg_leakage = summary.get("average_leakage_current", 0)
        st.metric(
            "Avg Leakage Current",
            f"{avg_leakage:.2f} mA"
        )

    with col3:
        max_leakage = summary.get("max_leakage_current", 0)
        st.metric(
            "Max Leakage Current",
            f"{max_leakage:.2f} mA"
        )

    with col4:
        power_deg = summary.get("final_power_degradation")
        if power_deg is not None:
            st.metric(
                "Final Power Degradation",
                f"{power_deg:.2f}%"
            )

    # QC Status
    st.markdown("---")
    qc_status = summary.get("qc_status", "unknown")
    qc_emoji = {"pass": "✅", "warning": "⚠️", "fail": "❌"}

    st.markdown(f"### QC Status: {qc_emoji.get(qc_status, '')} **{qc_status.upper()}**")

    # QC Details
    qc_details = summary.get("qc_details", [])
    if qc_details:
        st.markdown("#### QC Check Details")

        for check in qc_details:
            status = check.get("status", "unknown")
            check_name = check.get("check", "Unknown Check")
            message = check.get("message", "")
            value = check.get("value", 0)
            threshold = check.get("threshold", 0)

            with st.expander(f"{qc_emoji.get(status, '')} {check_name}", expanded=(status != "pass")):
                st.write(message)
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Measured Value", f"{value:.2f}")
                with col2:
                    st.metric("Threshold", f"{threshold:.2f}")

    # Compliance
    st.markdown("---")
    compliance = summary.get("compliance", {})
    if compliance:
        st.markdown("#### IEC 62804 Compliance")
        is_compliant = compliance.get("iec_62804_compliant", False)

        if is_compliant:
            st.success("✅ Test meets IEC 62804 requirements")
        else:
            st.error("❌ Test does not meet IEC 62804 requirements")

        if compliance.get("compliance_notes"):
            st.info(compliance["compliance_notes"])


def render_measurements_table(measurements: List[Dict[str, Any]], limit: int = 100) -> None:
    """
    Render measurements data table.

    Args:
        measurements: List of measurement dictionaries
        limit: Maximum number of rows to display
    """
    st.subheader("Measurement Data")

    if not measurements:
        st.info("No measurements available")
        return

    # Convert to DataFrame
    df = pd.DataFrame(measurements)

    # Select and format columns
    display_columns = [
        "elapsed_time",
        "leakage_current",
        "voltage",
        "power_degradation",
        "temperature",
        "humidity"
    ]
    display_columns = [col for col in display_columns if col in df.columns]

    df_display = df[display_columns].copy()

    # Rename columns for display
    column_rename = {
        "elapsed_time": "Time (h)",
        "leakage_current": "Leakage (mA)",
        "voltage": "Voltage (V)",
        "power_degradation": "Power Deg. (%)",
        "temperature": "Temp (°C)",
        "humidity": "Humidity (%)"
    }
    df_display = df_display.rename(columns=column_rename)

    # Format numbers
    for col in df_display.columns:
        if df_display[col].dtype in ['float64', 'float32']:
            df_display[col] = df_display[col].round(2)

    # Display limited rows
    if len(df_display) > limit:
        st.write(f"Showing first {limit} of {len(df_display)} measurements")
        st.dataframe(df_display.head(limit), use_container_width=True)

        # Download button for full data
        csv = df_display.to_csv(index=False)
        st.download_button(
            label="📥 Download Full Data (CSV)",
            data=csv,
            file_name="measurements.csv",
            mime="text/csv"
        )
    else:
        st.dataframe(df_display, use_container_width=True)


def render_leakage_events(events: List[Dict[str, Any]]) -> None:
    """
    Render leakage events/anomalies.

    Args:
        events: List of leakage event dictionaries
    """
    if not events:
        st.success("✅ No leakage anomalies detected")
        return

    st.warning(f"⚠️ {len(events)} leakage anomaly event(s) detected")

    for event in events:
        severity = event.get("severity", "unknown")
        event_type = event.get("event_type", "unknown")
        description = event.get("description", "")
        leakage_current = event.get("leakage_current", 0)

        severity_emoji = {"warning": "⚠️", "critical": "🚨"}

        with st.expander(f"{severity_emoji.get(severity, '')} {event_type.replace('_', ' ').title()}"):
            st.write(description)
            st.metric("Leakage Current", f"{leakage_current:.2f} mA")


def render_test_metadata(test_execution: Dict[str, Any]) -> None:
    """
    Render test metadata information.

    Args:
        test_execution: Test execution dictionary
    """
    with st.expander("📋 Test Metadata"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Test Information**")
            st.text(f"Test Name: {test_execution.get('test_name', 'N/A')}")
            st.text(f"Module ID: {test_execution.get('module_id', 'N/A')}")
            st.text(f"Test ID: {test_execution.get('id', 'N/A')}")

            if test_execution.get("operator"):
                st.text(f"Operator: {test_execution['operator']}")

        with col2:
            st.markdown("**Test Parameters**")
            params = test_execution.get("input_parameters", {})
            for key, value in params.items():
                if key not in ["test_name", "module_id", "operator", "notes"]:
                    st.text(f"{key.replace('_', ' ').title()}: {value}")

        if test_execution.get("notes"):
            st.markdown("**Notes**")
            st.text(test_execution["notes"])
