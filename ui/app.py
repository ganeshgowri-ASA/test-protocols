"""
Main Streamlit Application
Entry point for the test protocol UI
"""

import streamlit as st
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from protocols.loader import ProtocolLoader
from protocols.environmental.h2s_001 import H2S001Protocol
from database.session import init_db
from ui.pages import (
    show_home_page,
    show_protocol_selection,
    show_test_execution,
    show_results_viewer,
    show_data_analysis
)


def init_session_state():
    """Initialize Streamlit session state"""
    if "db_initialized" not in st.session_state:
        # Initialize database
        init_db()
        st.session_state.db_initialized = True

    if "current_protocol" not in st.session_state:
        st.session_state.current_protocol = None

    if "current_execution" not in st.session_state:
        st.session_state.current_execution = None

    if "page" not in st.session_state:
        st.session_state.page = "home"


def main():
    """Main application entry point"""
    st.set_page_config(
        page_title="PV Test Protocol Framework",
        page_icon="☀️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    init_session_state()

    # Sidebar navigation
    with st.sidebar:
        st.title("☀️ PV Test Protocols")
        st.markdown("---")

        page = st.radio(
            "Navigation",
            ["Home", "New Test", "View Results", "Data Analysis", "Settings"],
            key="navigation"
        )

        st.markdown("---")
        st.caption("Version 1.0.0")
        st.caption("© 2025 Test Protocol Framework")

    # Main content area
    if page == "Home":
        show_home_page()
    elif page == "New Test":
        show_protocol_selection()
        if st.session_state.current_protocol:
            show_test_execution()
    elif page == "View Results":
        show_results_viewer()
    elif page == "Data Analysis":
        show_data_analysis()
    elif page == "Settings":
        show_settings_page()


def show_settings_page():
    """Display settings page"""
    st.title("⚙️ Settings")

    st.subheader("Database")
    st.info("Database location: ~/.test_protocols/test_protocols.db")

    st.subheader("Equipment Calibration")
    # Add calibration management UI here

    st.subheader("Export/Import")
    # Add data export/import functionality


def run_app():
    """Run the Streamlit application"""
    main()


if __name__ == "__main__":
    run_app()
