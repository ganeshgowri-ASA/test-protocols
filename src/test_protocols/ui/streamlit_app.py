"""
Main Streamlit application for PV Test Protocol Suite.

This module provides the web-based user interface for managing and executing
test protocols.
"""

import streamlit as st
from pathlib import Path
import yaml

# Set page configuration
st.set_page_config(
    page_title="PV Test Protocol Suite",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_config():
    """Load GenSpark UI configuration."""
    config_path = Path(__file__).parent.parent.parent.parent / "config" / "genspark_ui_config.yaml"

    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}


def main():
    """Main application entry point."""
    config = load_config()

    # App header
    st.title("🔬 PV Test Protocol Suite")
    st.markdown("---")

    # Sidebar navigation
    st.sidebar.title("Navigation")

    pages = {
        "Protocol Selection": "📋",
        "Test Runner": "▶️",
        "Live Monitoring": "📊",
        "Results Analysis": "📈",
        "Report Generation": "📄",
        "Equipment Management": "🔧",
        "Admin Panel": "⚙️",
    }

    page = st.sidebar.radio(
        "Select Page",
        list(pages.keys()),
        format_func=lambda x: f"{pages[x]} {x}"
    )

    # Display selected page
    st.sidebar.markdown("---")
    st.sidebar.info(f"Current Page: {page}")

    # Page content
    if page == "Protocol Selection":
        show_protocol_selection()
    elif page == "Test Runner":
        show_test_runner()
    elif page == "Live Monitoring":
        show_live_monitoring()
    elif page == "Results Analysis":
        show_results_analysis()
    elif page == "Report Generation":
        show_report_generation()
    elif page == "Equipment Management":
        show_equipment_management()
    elif page == "Admin Panel":
        show_admin_panel()


def show_protocol_selection():
    """Display protocol selection page."""
    st.header("📋 Protocol Selection")

    st.info("This page allows you to browse and select test protocols.")

    # Category filter
    col1, col2 = st.columns(2)

    with col1:
        category = st.selectbox(
            "Filter by Category",
            ["All", "Mechanical", "Environmental", "Electrical", "Thermal", "Optical"]
        )

    with col2:
        standard = st.selectbox(
            "Filter by Standard",
            ["All", "IEC 61215", "UL 1703", "ASTM E1171"]
        )

    # Protocol list
    st.subheader("Available Protocols")

    # Example protocol data
    protocols = [
        {
            "id": "ML-001",
            "name": "Mechanical Load Static Test (2400Pa)",
            "category": "Mechanical",
            "standard": "IEC 61215 MQT 16",
            "duration": "180 min",
        }
    ]

    for protocol in protocols:
        with st.expander(f"{protocol['id']}: {protocol['name']}"):
            st.write(f"**Category:** {protocol['category']}")
            st.write(f"**Standard:** {protocol['standard']}")
            st.write(f"**Duration:** {protocol['duration']}")

            if st.button(f"Select {protocol['id']}", key=protocol['id']):
                st.session_state['selected_protocol'] = protocol['id']
                st.success(f"Protocol {protocol['id']} selected!")


def show_test_runner():
    """Display test runner page."""
    st.header("▶️ Test Runner")

    if 'selected_protocol' not in st.session_state:
        st.warning("Please select a protocol from the Protocol Selection page first.")
        return

    protocol_id = st.session_state['selected_protocol']
    st.info(f"Running protocol: {protocol_id}")

    # Sample information form
    st.subheader("Sample Information")

    col1, col2 = st.columns(2)

    with col1:
        sample_id = st.text_input("Sample ID*", placeholder="e.g., PV-2025-001")
        manufacturer = st.text_input("Manufacturer*", placeholder="e.g., SolarTech Inc.")
        model = st.text_input("Model*", placeholder="e.g., ST-300W-MONO")

    with col2:
        operator_id = st.selectbox("Test Operator*", ["operator1", "operator2", "operator3"])
        notes = st.text_area("Test Notes", placeholder="Enter any relevant notes...")

    # Control buttons
    st.subheader("Test Controls")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("▶️ Start Test", type="primary"):
            st.success("Test started!")

    with col2:
        if st.button("⏸️ Pause Test"):
            st.warning("Test paused.")

    with col3:
        if st.button("▶️ Resume Test"):
            st.info("Test resumed.")

    with col4:
        if st.button("⏹️ Abort Test"):
            st.error("Test aborted.")


def show_live_monitoring():
    """Display live monitoring page."""
    st.header("📊 Live Monitoring")

    st.info("Real-time test monitoring and data visualization will be displayed here.")

    # Placeholder for live charts
    st.subheader("Current Measurements")

    import numpy as np
    import pandas as pd

    # Example chart
    chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['Pressure (Pa)', 'Deflection (mm)', 'Temperature (°C)']
    )

    st.line_chart(chart_data)


def show_results_analysis():
    """Display results analysis page."""
    st.header("📈 Results Analysis")

    st.info("Test results and analysis will be displayed here.")


def show_report_generation():
    """Display report generation page."""
    st.header("📄 Report Generation")

    st.info("Generate and download test reports.")

    # Report format selection
    format_option = st.selectbox(
        "Select Report Format",
        ["PDF", "HTML", "Markdown"]
    )

    if st.button("Generate Report"):
        st.success(f"Report generated in {format_option} format!")


def show_equipment_management():
    """Display equipment management page."""
    st.header("🔧 Equipment Management")

    st.warning("This page is restricted to authorized personnel.")
    st.info("Equipment inventory and calibration tracking will be displayed here.")


def show_admin_panel():
    """Display admin panel page."""
    st.header("⚙️ Admin Panel")

    st.warning("This page is restricted to administrators.")
    st.info("System administration tools will be displayed here.")


if __name__ == "__main__":
    main()
