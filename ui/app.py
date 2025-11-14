"""
Main Streamlit Application
Entry point for the test protocols UI
"""

import streamlit as st
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ui.protocol_selector import render_protocol_selector
from ui.parameter_input import render_parameter_input
from ui.results_display import render_results_display
from database import init_db


# Page configuration
st.set_page_config(
    page_title="Test Protocols - PV Testing Framework",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_session_state():
    """Initialize session state variables"""
    if 'selected_protocol' not in st.session_state:
        st.session_state.selected_protocol = None
    if 'test_parameters' not in st.session_state:
        st.session_state.test_parameters = {}
    if 'test_run_id' not in st.session_state:
        st.session_state.test_run_id = None
    if 'test_status' not in st.session_state:
        st.session_state.test_status = 'not_started'


def main():
    """Main application entry point"""

    # Initialize database
    try:
        init_db()
    except Exception as e:
        st.error(f"Database initialization failed: {e}")
        return

    # Initialize session state
    initialize_session_state()

    # Header
    st.title("☀️ PV Testing Protocol Framework")
    st.markdown("---")

    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Select Page",
            ["Protocol Selection", "Test Execution", "Results & Reports", "Protocol Management"],
            key="navigation"
        )

        st.markdown("---")
        st.header("System Info")
        st.info(f"**Status:** {'Test Running' if st.session_state.test_status == 'running' else 'Ready'}")

        if st.session_state.selected_protocol:
            st.success(f"**Protocol:** {st.session_state.selected_protocol}")

    # Main content area
    if page == "Protocol Selection":
        render_protocol_selection_page()
    elif page == "Test Execution":
        render_test_execution_page()
    elif page == "Results & Reports":
        render_results_page()
    elif page == "Protocol Management":
        render_protocol_management_page()


def render_protocol_selection_page():
    """Render protocol selection page"""
    st.header("Protocol Selection")
    st.markdown("Select and configure a test protocol")

    protocol = render_protocol_selector()

    if protocol:
        st.session_state.selected_protocol = protocol['metadata']['id']
        st.success(f"✓ Selected: **{protocol['metadata']['name']}** (v{protocol['metadata']['version']})")

        # Display protocol information
        with st.expander("Protocol Details", expanded=True):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**ID:** {protocol['metadata']['id']}")
                st.markdown(f"**Category:** {protocol['metadata']['category']}")
                st.markdown(f"**Description:** {protocol['metadata']['description']}")

            with col2:
                st.markdown(f"**Protocol Number:** {protocol['metadata']['protocol_number']}")
                st.markdown(f"**Version:** {protocol['metadata']['version']}")
                st.markdown(f"**Author:** {protocol['metadata']['author']}")

        # Parameter configuration
        st.subheader("Test Parameters")
        parameters = render_parameter_input(protocol)
        st.session_state.test_parameters = parameters


def render_test_execution_page():
    """Render test execution page"""
    st.header("Test Execution")

    if not st.session_state.selected_protocol:
        st.warning("⚠️ Please select a protocol first from the Protocol Selection page")
        return

    st.markdown(f"**Protocol:** {st.session_state.selected_protocol}")

    # Test control buttons
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("▶️ Start Test", disabled=st.session_state.test_status == 'running'):
            st.session_state.test_status = 'running'
            st.success("Test started!")
            st.rerun()

    with col2:
        if st.button("⏸️ Pause Test", disabled=st.session_state.test_status != 'running'):
            st.session_state.test_status = 'paused'
            st.warning("Test paused")
            st.rerun()

    with col3:
        if st.button("⏹️ Stop Test", disabled=st.session_state.test_status not in ['running', 'paused']):
            st.session_state.test_status = 'stopped'
            st.info("Test stopped")
            st.rerun()

    with col4:
        if st.button("🔄 Reset"):
            st.session_state.test_status = 'not_started'
            st.rerun()

    st.markdown("---")

    # Test progress
    if st.session_state.test_status in ['running', 'paused']:
        st.subheader("Test Progress")

        # Simulated progress
        progress = st.progress(0)
        status_text = st.empty()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Current Cycle", "15/200")
        with col2:
            st.metric("Phase", "Daytime")
        with col3:
            st.metric("Elapsed Time", "45:30:12")

        # Real-time data (placeholder)
        st.subheader("Real-time Monitoring")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Chamber Temp", "65.2°C", "0.1°C")
        with col2:
            st.metric("Chamber RH", "14.8%", "-0.2%")
        with col3:
            st.metric("Module Temp", "75.4°C", "0.3°C")
        with col4:
            st.metric("UV Irradiance", "998 W/m²", "-2 W/m²")

        # Charts placeholder
        st.subheader("Environmental Profile")
        st.line_chart({"temperature": [65, 65.1, 65.2, 64.9, 65.0]})


def render_results_page():
    """Render results and reports page"""
    st.header("Results & Reports")

    if not st.session_state.test_run_id:
        st.info("ℹ️ No test results available. Run a test to see results here.")
        return

    render_results_display(st.session_state.test_run_id)


def render_protocol_management_page():
    """Render protocol management page"""
    st.header("Protocol Management")

    tab1, tab2, tab3 = st.tabs(["View Protocols", "Import Protocol", "Create Protocol"])

    with tab1:
        st.subheader("Available Protocols")
        st.info("Protocol list will be displayed here")

    with tab2:
        st.subheader("Import Protocol from JSON")
        uploaded_file = st.file_uploader("Choose a JSON file", type=['json'])

        if uploaded_file:
            st.success("File uploaded successfully")
            st.json(uploaded_file.getvalue().decode())

    with tab3:
        st.subheader("Create New Protocol")
        st.info("Protocol creation form will be available here")


if __name__ == "__main__":
    main()
