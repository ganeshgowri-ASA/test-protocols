"""Protocol form component for Streamlit UI."""

import streamlit as st
from typing import Dict, Any, Optional
from datetime import datetime


def render_protocol_form(
    protocol_schema: Dict[str, Any],
    default_values: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """
    Render dynamic protocol form based on schema.

    Args:
        protocol_schema: Protocol JSON schema
        default_values: Default values for form fields

    Returns:
        Form data dictionary if submitted, None otherwise
    """
    if default_values is None:
        default_values = {}

    st.subheader("Test Parameters")

    # Get parameter definitions
    params = protocol_schema.get("test_parameters", {}).get("properties", {})
    required = protocol_schema.get("test_parameters", {}).get("required", [])

    form_data = {}

    with st.form("protocol_form"):
        for param_name, param_def in params.items():
            param_type = param_def.get("type")
            description = param_def.get("description", "")
            default = default_values.get(param_name, param_def.get("default"))
            is_required = param_name in required

            label = param_name.replace("_", " ").title()
            if is_required:
                label += " *"

            # Render appropriate input based on type
            if param_type == "string":
                if param_name == "notes":
                    form_data[param_name] = st.text_area(
                        label,
                        value=default or "",
                        help=description
                    )
                else:
                    form_data[param_name] = st.text_input(
                        label,
                        value=default or "",
                        help=description
                    )

            elif param_type == "number":
                min_val = param_def.get("minimum", 0.0)
                max_val = param_def.get("maximum", 1000000.0)
                form_data[param_name] = st.number_input(
                    label,
                    min_value=float(min_val),
                    max_value=float(max_val),
                    value=float(default) if default is not None else float(min_val),
                    help=description,
                    format="%.2f"
                )

            elif param_type == "integer":
                min_val = param_def.get("minimum", 0)
                max_val = param_def.get("maximum", 1000000)
                form_data[param_name] = st.number_input(
                    label,
                    min_value=int(min_val),
                    max_value=int(max_val),
                    value=int(default) if default is not None else int(min_val),
                    help=description,
                    step=1
                )

        # Submit button
        col1, col2 = st.columns([1, 4])
        with col1:
            submitted = st.form_submit_button("Start Test", type="primary", use_container_width=True)
        with col2:
            st.form_submit_button("Reset", type="secondary", use_container_width=True)

        if submitted:
            return form_data

    return None


def render_test_execution_card(test_execution: Dict[str, Any]) -> None:
    """
    Render test execution summary card.

    Args:
        test_execution: Test execution data
    """
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Test ID", test_execution.get("test_name", "N/A"))
        st.metric("Module ID", test_execution.get("module_id", "N/A"))

    with col2:
        status = test_execution.get("status", "unknown")
        status_emoji = {
            "pending": "⏳",
            "in_progress": "▶️",
            "completed": "✅",
            "failed": "❌",
            "aborted": "⏹️"
        }
        st.metric("Status", f"{status_emoji.get(status, '')} {status.replace('_', ' ').title()}")

        if test_execution.get("start_time"):
            st.metric("Start Time", test_execution["start_time"][:19])

    with col3:
        qc_status = test_execution.get("qc_status")
        if qc_status:
            qc_emoji = {"pass": "✅", "warning": "⚠️", "fail": "❌"}
            st.metric("QC Status", f"{qc_emoji.get(qc_status, '')} {qc_status.upper()}")

        if test_execution.get("duration_hours"):
            st.metric("Duration", f"{test_execution['duration_hours']:.1f} hours")


def render_validation_rules_info(validation_rules: Dict[str, Any]) -> None:
    """
    Render validation rules information.

    Args:
        validation_rules: Validation rules from schema
    """
    with st.expander("📋 Validation Rules & Thresholds"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Leakage Current Limits**")
            leakage_limits = validation_rules.get("leakage_current_limits", {})
            st.info(f"⚠️ Warning: {leakage_limits.get('warning_threshold')} {leakage_limits.get('unit')}")
            st.error(f"🚨 Critical: {leakage_limits.get('critical_threshold')} {leakage_limits.get('unit')}")

        with col2:
            st.markdown("**Power Degradation Limits**")
            power_limits = validation_rules.get("power_degradation_limits", {})
            st.info(f"⚠️ Warning: {power_limits.get('warning_threshold')} {power_limits.get('unit')}")
            st.error(f"🚨 Critical: {power_limits.get('critical_threshold')} {power_limits.get('unit')}")
