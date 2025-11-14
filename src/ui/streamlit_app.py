"""Main Streamlit application for test protocol execution."""

import streamlit as st
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.database.connection import init_db
from src.ui.components.protocol_selector import render_protocol_selector
from src.ui.components.test_execution import render_test_execution
from src.ui.components.results_viewer import render_results_viewer

# Page configuration
st.set_page_config(
    page_title="PV Test Protocols",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize database
init_db()

# Session state initialization
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"
if "current_protocol" not in st.session_state:
    st.session_state.current_protocol = None
if "current_test" not in st.session_state:
    st.session_state.current_test = None


def main():
    """Main application entry point."""
    st.title("🔬 PV Test Protocols Framework")
    st.markdown("---")

    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Select Page",
            ["Home", "New Test", "View Results", "Equipment Management"],
            key="navigation",
        )

        st.markdown("---")
        st.subheader("About")
        st.info(
            """
            **Modular PV Testing Protocol Framework**

            Dynamic JSON-based templates for automated testing,
            analysis, and reporting of photovoltaic modules.
            """
        )

    # Route to appropriate page
    if page == "Home":
        render_home_page()
    elif page == "New Test":
        render_new_test_page()
    elif page == "View Results":
        render_results_page()
    elif page == "Equipment Management":
        render_equipment_page()


def render_home_page():
    """Render the home page."""
    st.header("Welcome to the PV Test Protocols Framework")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Available Protocols", "1")
        st.caption("TERM-001: Terminal Robustness Test")

    with col2:
        st.metric("Active Tests", "0")
        st.caption("No tests currently in progress")

    with col3:
        st.metric("Completed Tests", "0")
        st.caption("No completed tests")

    st.markdown("---")

    st.subheader("Quick Start")
    st.write("""
    1. **New Test**: Start a new test execution by selecting a protocol
    2. **View Results**: Review completed test results and generate reports
    3. **Equipment Management**: Manage test equipment and calibration records
    """)

    st.subheader("Available Protocols")
    protocols = [
        {
            "id": "TERM-001",
            "title": "Terminal Robustness Test",
            "category": "Mechanical",
            "description": "Evaluate mechanical robustness and electrical integrity of PV module terminals",
        }
    ]

    for protocol in protocols:
        with st.expander(f"**{protocol['id']}**: {protocol['title']}"):
            st.write(f"**Category**: {protocol['category']}")
            st.write(f"**Description**: {protocol['description']}")
            if st.button(f"Start Test", key=f"start_{protocol['id']}"):
                st.session_state.current_protocol = protocol["id"]
                st.session_state.current_page = "new_test"
                st.rerun()


def render_new_test_page():
    """Render the new test page."""
    st.header("New Test Execution")

    # Protocol selection
    selected_protocol = render_protocol_selector()

    if selected_protocol:
        # Test execution interface
        render_test_execution(selected_protocol)


def render_results_page():
    """Render the results viewing page."""
    st.header("Test Results")
    render_results_viewer()


def render_equipment_page():
    """Render the equipment management page."""
    st.header("Equipment Management")
    st.info("Equipment management interface coming soon...")

    st.subheader("Add New Equipment")
    with st.form("add_equipment"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Equipment Name")
            manufacturer = st.text_input("Manufacturer")
            model = st.text_input("Model")

        with col2:
            serial_number = st.text_input("Serial Number")
            equipment_type = st.selectbox(
                "Type",
                ["Multimeter", "Force Gauge", "Torque Wrench", "High-Pot Tester", "Other"],
            )
            calibration_required = st.checkbox("Calibration Required")

        if calibration_required:
            col3, col4 = st.columns(2)
            with col3:
                calibration_date = st.date_input("Last Calibration Date")
            with col4:
                calibration_due = st.date_input("Calibration Due Date")

        notes = st.text_area("Notes")

        if st.form_submit_button("Add Equipment"):
            st.success(f"Equipment '{name}' added successfully!")


if __name__ == "__main__":
    main()
