"""
GenSpark UI - Main Streamlit Application

Provides web interface for PV protocol execution and analysis.
"""

import streamlit as st
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ui.pages import home, protocol_execution, results_viewer, data_management


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="PV Protocol Framework",
        page_icon="☀️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Sidebar navigation
    st.sidebar.title("☀️ PV Protocol Framework")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigation",
        ["Home", "Protocol Execution", "Results Viewer", "Data Management"]
    )

    st.sidebar.markdown("---")
    st.sidebar.info(
        "**Framework Version:** 1.0.0\n\n"
        "**Active Protocols:** CRACK-001\n\n"
        "For support, contact: support@genspark.com"
    )

    # Route to appropriate page
    if page == "Home":
        home.render()
    elif page == "Protocol Execution":
        protocol_execution.render()
    elif page == "Results Viewer":
        results_viewer.render()
    elif page == "Data Management":
        data_management.render()


if __name__ == "__main__":
    main()
