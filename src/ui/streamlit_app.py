"""
GenSpark UI - Main Streamlit Application
Modular PV Testing Protocol Framework Interface
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core import ProtocolManager, SchemaValidator, DataProcessor
from src.ui.components import (
    render_protocol_selector,
    render_data_entry_form,
    render_test_results,
    render_qc_dashboard,
    render_report_generator
)


def init_session_state():
    """Initialize Streamlit session state variables."""
    if 'protocol_manager' not in st.session_state:
        st.session_state.protocol_manager = ProtocolManager()

    if 'schema_validator' not in st.session_state:
        st.session_state.schema_validator = SchemaValidator(
            st.session_state.protocol_manager
        )

    if 'data_processor' not in st.session_state:
        st.session_state.data_processor = DataProcessor(
            st.session_state.protocol_manager
        )

    if 'current_protocol' not in st.session_state:
        st.session_state.current_protocol = None

    if 'test_data' not in st.session_state:
        st.session_state.test_data = {}


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="GenSpark Test Protocols",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    init_session_state()

    # Sidebar navigation
    st.sidebar.title("⚡ GenSpark Testing")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigation",
        [
            "Protocol Selection",
            "Data Entry",
            "Test Results",
            "QC Dashboard",
            "Report Generation"
        ]
    )

    st.sidebar.markdown("---")
    st.sidebar.info(
        "**Modular PV Testing Protocol Framework**\n\n"
        "Version 1.0.0"
    )

    # Main content area
    if page == "Protocol Selection":
        render_protocol_selector()

    elif page == "Data Entry":
        if st.session_state.current_protocol:
            render_data_entry_form()
        else:
            st.warning("Please select a protocol first from the Protocol Selection page.")

    elif page == "Test Results":
        if st.session_state.test_data:
            render_test_results()
        else:
            st.info("No test data available. Please enter data in the Data Entry page.")

    elif page == "QC Dashboard":
        if st.session_state.test_data:
            render_qc_dashboard()
        else:
            st.info("No test data available for QC analysis.")

    elif page == "Report Generation":
        if st.session_state.test_data:
            render_report_generator()
        else:
            st.info("No test data available for report generation.")


if __name__ == "__main__":
    main()
