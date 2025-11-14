"""GenSpark UI - Test Protocols Management System

Streamlit-based user interface for managing and executing test protocols.
"""

import streamlit as st
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from protocols.mechanical.snow_load import (
    SnowLoadTestProtocol,
    SnowLoadTestConfig,
    ModuleSpecs
)
from protocols.mechanical.snow_load.analysis import SnowLoadAnalyzer


# Page configuration
st.set_page_config(
    page_title="Test Protocols - GenSpark UI",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
    }
    .fail-box {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)


def main():
    """Main application entry point"""

    # Sidebar navigation
    st.sidebar.title("🔬 Test Protocols")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigation",
        [
            "Home",
            "Snow Load Test (SNOW-001)",
            "Test History",
            "Equipment Management",
            "Reports"
        ]
    )

    if page == "Home":
        show_home_page()
    elif page == "Snow Load Test (SNOW-001)":
        show_snow_load_page()
    elif page == "Test History":
        show_test_history_page()
    elif page == "Equipment Management":
        show_equipment_page()
    elif page == "Reports":
        show_reports_page()


def show_home_page():
    """Display home page"""
    st.markdown('<div class="main-header">PV Testing Protocol Framework</div>', unsafe_allow_html=True)

    st.markdown("""
    Welcome to the **GenSpark Test Protocols Management System** - a comprehensive platform for
    managing and executing photovoltaic module testing protocols.

    ### Available Test Protocols

    #### Mechanical Testing
    - **SNOW-001**: Snow Load Test (IEC 61215-1:2016)
    - **WIND-001**: Wind Load Test *(Coming Soon)*
    - **ICE-001**: Ice Load Test *(Coming Soon)*

    #### Environmental Testing
    - **HF-001**: Humidity-Freeze Test *(Coming Soon)*
    - **TC-001**: Thermal Cycling Test *(Coming Soon)*
    - **UV-001**: UV Exposure Test *(Coming Soon)*

    #### Electrical Testing
    - **IV-001**: IV Curve Characterization *(Coming Soon)*
    - **FLASH-001**: Flash Test *(Coming Soon)*

    ### Features
    - ✅ JSON-based dynamic protocol templates
    - ✅ Real-time data monitoring
    - ✅ Automated data analysis and charting
    - ✅ Quality control checks
    - ✅ Automated report generation
    - ✅ Database persistence
    - ✅ LIMS/QMS integration ready

    ### Quick Start
    1. Select a protocol from the sidebar
    2. Enter module specifications
    3. Configure test parameters
    4. Execute the test
    5. Review results and generate reports

    ---
    *Version 1.0.0 | © 2025 Test Protocols Framework*
    """)


def show_snow_load_page():
    """Display Snow Load test page"""
    from ui.components.snow_load_ui import render_snow_load_test

    render_snow_load_test()


def show_test_history_page():
    """Display test history page"""
    st.markdown('<div class="main-header">Test History</div>', unsafe_allow_html=True)

    st.info("📊 Test history tracking coming soon. This will display all completed tests with filtering and search capabilities.")

    # Placeholder for future implementation
    st.markdown("""
    ### Features (Coming Soon)
    - View all test runs
    - Filter by protocol type, date, module, result
    - Export test data
    - Compare test results
    - Trend analysis
    """)


def show_equipment_page():
    """Display equipment management page"""
    st.markdown('<div class="main-header">Equipment Management</div>', unsafe_allow_html=True)

    st.info("🔧 Equipment management coming soon. This will track all testing equipment, calibration dates, and availability.")

    st.markdown("""
    ### Features (Coming Soon)
    - Equipment inventory
    - Calibration tracking
    - Maintenance scheduling
    - Equipment reservation system
    - Calibration certificate management
    """)


def show_reports_page():
    """Display reports page"""
    st.markdown('<div class="main-header">Reports & Analytics</div>', unsafe_allow_html=True)

    st.info("📄 Report generation coming soon. This will provide comprehensive test reports and analytics.")

    st.markdown("""
    ### Features (Coming Soon)
    - Generate PDF test reports
    - Export data to Excel
    - Custom report templates
    - Batch report generation
    - Statistical analysis
    - Trend charts and dashboards
    """)


if __name__ == "__main__":
    main()
