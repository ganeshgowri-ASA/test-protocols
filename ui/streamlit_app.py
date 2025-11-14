"""Main Streamlit application for Test Protocols Framework."""

import streamlit as st
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.config import load_config, get_config
from utils.logging import setup_logging, get_logger
from database.session import init_database

# Initialize configuration and logging
load_config()
setup_logging()
logger = get_logger(__name__)

# Initialize database
try:
    init_database()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")
    st.error(f"Database initialization failed: {e}")

# Page configuration
st.set_page_config(
    page_title=get_config('ui.title', 'Test Protocol Framework'),
    page_icon=get_config('ui.page_icon', '🔬'),
    layout=get_config('ui.layout', 'wide'),
    initial_sidebar_state=get_config('ui.sidebar_state', 'expanded'),
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Home", "Run Test", "View Results", "Manage Samples", "Settings"]
)

# Main content area
if page == "Home":
    st.markdown('<div class="main-header">IEC 61730 Test Protocol Framework</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Dynamic JSON-based test protocols for PV module testing</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Available Protocols", "1")
        st.info("**WET-001**: Wet Leakage Current Test")

    with col2:
        st.metric("Total Test Runs", "0")
        st.info("No test runs yet")

    with col3:
        st.metric("Pass Rate", "N/A")
        st.info("Run tests to see statistics")

    st.divider()

    st.subheader("📋 Available Test Protocols")

    # WET-001 Protocol Card
    with st.expander("**WET-001**: Wet Leakage Current Test (IEC 61730 MST 02)", expanded=True):
        st.markdown("""
        **Category**: Safety
        **Standard**: IEC 61730 MST 02
        **Version**: 1.0.0

        **Description**:
        The Wet Leakage Current Test assesses the electrical safety of PV modules under humid conditions.
        The test measures leakage current while the module is subjected to high humidity and test voltage.

        **Key Parameters**:
        - Test Voltage: 1500V DC (default)
        - Test Duration: 168 hours (1 week)
        - Temperature: 20-30°C
        - Humidity: 85-95% RH

        **Acceptance Criteria**:
        - Maximum Leakage Current: ≤ 0.25 mA
        - Minimum Insulation Resistance: ≥ 400 MΩ
        - No surface tracking or breakdown
        """)

        if st.button("🚀 Start WET-001 Test", key="start_wet001"):
            st.switch_page("pages/run_test.py")

    st.divider()

    st.subheader("ℹ️ System Information")
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Framework Version:**", get_config('app.version', '1.0.0'))
        st.write("**Environment:**", get_config('app.environment', 'development'))

    with col2:
        st.write("**Database:**", get_config('database.type', 'sqlite'))
        st.write("**Logging Level:**", get_config('logging.level', 'INFO'))

elif page == "Run Test":
    from pages.run_test import render_run_test_page
    render_run_test_page()

elif page == "View Results":
    from pages.results import render_results_page
    render_results_page()

elif page == "Manage Samples":
    from pages.samples import render_samples_page
    render_samples_page()

elif page == "Settings":
    from pages.settings import render_settings_page
    render_settings_page()

# Footer
st.sidebar.divider()
st.sidebar.caption("IEC 61730 Test Protocol Framework v1.0.0")
st.sidebar.caption("© 2025 ASA Testing")
