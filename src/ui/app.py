"""
Main Streamlit application for PV Test Protocol Framework
"""

import streamlit as st
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.models import init_db

# Page configuration
st.set_page_config(
    page_title="PV Test Protocol Framework",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database on first run
if 'db_initialized' not in st.session_state:
    try:
        init_db()
        st.session_state.db_initialized = True
    except Exception as e:
        st.error(f"Database initialization failed: {e}")
        st.stop()

# Sidebar navigation
st.sidebar.title("PV Test Protocol Framework")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Test Execution",
        "Test Results",
        "Sample Management",
        "Equipment Management",
        "Protocol Library"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Version:** 1.0.0\n\n"
    "**Framework:** Modular PV Testing Protocol\n\n"
    "**Standards:** IEC 61730, IEC 61215"
)

# Main content area
if page == "Dashboard":
    from pages.dashboard import render_dashboard
    render_dashboard()

elif page == "Test Execution":
    from pages.test_execution import render_test_execution
    render_test_execution()

elif page == "Test Results":
    from pages.test_results import render_test_results
    render_test_results()

elif page == "Sample Management":
    from pages.sample_management import render_sample_management
    render_sample_management()

elif page == "Equipment Management":
    from pages.equipment_management import render_equipment_management
    render_equipment_management()

elif page == "Protocol Library":
    from pages.protocol_library import render_protocol_library
    render_protocol_library()
