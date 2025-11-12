"""
Protocol Viewer Component

Provides UI components for displaying protocol information and metadata.
"""

import streamlit as st
from typing import Dict, Any


def display_protocol_info(protocol_data: Dict[str, Any], expanded: bool = False):
    """
    Display protocol information in a formatted way.

    Args:
        protocol_data: Protocol data dictionary
        expanded: Whether to show expanded view
    """
    metadata = protocol_data.get("protocol_metadata", {})

    if expanded:
        st.markdown("### Protocol Information")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**Protocol ID:** {metadata.get('protocol_id', 'N/A')}")
            st.markdown(f"**Name:** {metadata.get('protocol_name', 'N/A')}")
            st.markdown(f"**Version:** {metadata.get('version', 'N/A')}")

        with col2:
            st.markdown(f"**Category:** {metadata.get('category', 'N/A').title()}")
            st.markdown(f"**Standard:** {metadata.get('standard_reference', 'N/A')}")

        if metadata.get('description'):
            st.markdown("**Description:**")
            st.info(metadata['description'])

        if metadata.get('tags'):
            st.markdown("**Tags:**")
            st.markdown(", ".join([f"`{tag}`" for tag in metadata['tags']]))
    else:
        # Compact view
        st.markdown(f"**{metadata.get('protocol_name', 'Protocol')}** (v{metadata.get('version', '1.0.0')})")


def display_section_summary(section_name: str, section_data: Dict[str, Any]):
    """
    Display a summary of a protocol section.

    Args:
        section_name: Name of the section
        section_data: Section data dictionary
    """
    st.subheader(section_name.replace('_', ' ').title())

    if "fields" in section_data:
        field_count = len(section_data["fields"])
        required_count = sum(1 for f in section_data["fields"] if f.get("required", False))

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Fields", field_count)
        with col2:
            st.metric("Required Fields", required_count)

    elif "tables" in section_data:
        table_count = len(section_data["tables"])
        st.metric("Data Tables", table_count)

    elif "calculations" in section_data:
        calc_count = len(section_data["calculations"])
        st.metric("Calculations", calc_count)


def display_validation_status(validation_results: Dict[str, Any]):
    """
    Display validation status with color-coded results.

    Args:
        validation_results: Dictionary containing validation results
    """
    total = validation_results.get("total", 0)
    passed = validation_results.get("passed", 0)
    failed = validation_results.get("failed", 0)
    warnings = validation_results.get("warnings", 0)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("✅ Passed", passed)

    with col2:
        st.metric("❌ Failed", failed)

    with col3:
        st.metric("⚠️ Warnings", warnings)

    # Progress bar
    if total > 0:
        progress = passed / total
        st.progress(progress)
        st.caption(f"Validation Status: {progress * 100:.1f}% passed")


def display_chart_preview(chart_config: Dict[str, Any]):
    """
    Display a preview/info about a chart configuration.

    Args:
        chart_config: Chart configuration dictionary
    """
    chart_type = chart_config.get("chart_type", "line")
    title = chart_config.get("title", "Chart")

    st.markdown(f"### {title}")
    st.markdown(f"**Type:** {chart_type.title()}")

    x_axis = chart_config.get("x_axis", {})
    y_axis = chart_config.get("y_axis", {})

    if x_axis:
        st.markdown(f"**X-Axis:** {x_axis.get('label', 'N/A')}")

    if y_axis:
        st.markdown(f"**Y-Axis:** {y_axis.get('label', 'N/A')}")
