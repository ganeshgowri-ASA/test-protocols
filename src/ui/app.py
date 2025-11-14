"""Main Streamlit application for Test Protocols Framework."""

import streamlit as st
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.config import get_config
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="Test Protocols Framework",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load configuration
config = get_config()

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
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/200x80/1f77b4/white?text=Test+Protocols", use_container_width=True)
    st.markdown("---")

    # Navigation
    page = st.radio(
        "Navigation",
        ["🏠 Home", "📊 Test Dashboard", "⚙️ Protocol Editor", "📈 Results Viewer", "📝 Reports"],
        key="navigation"
    )

    st.markdown("---")
    st.caption(f"Environment: {config.get('environment', 'development')}")
    st.caption("Version: 0.1.0")

# Main content area
if page == "🏠 Home":
    st.markdown('<p class="main-header">Test Protocols Framework</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Modular PV Testing Protocol Framework</p>', unsafe_allow_html=True)

    # Welcome message
    st.write("""
    Welcome to the Test Protocols Framework - a comprehensive solution for managing and executing
    photovoltaic testing protocols with automated analysis, charting, QC, and report generation.
    """)

    # Features
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 📋 Protocol Management")
        st.write("Create and manage JSON-based test protocols with built-in validation")

    with col2:
        st.markdown("### 🔬 Test Execution")
        st.write("Execute tests with real-time monitoring and data acquisition")

    with col3:
        st.markdown("### 📊 Analysis & QC")
        st.write("Automated analysis with quality control and acceptance criteria")

    st.markdown("---")

    # Quick Start
    st.markdown("### 🚀 Quick Start")

    quick_start_col1, quick_start_col2 = st.columns(2)

    with quick_start_col1:
        st.markdown("#### Available Protocols")
        protocols = [
            {"id": "TRACK-001", "name": "Tracker Performance Test", "status": "Active"},
        ]

        for protocol in protocols:
            with st.container():
                st.markdown(f"**{protocol['id']}**: {protocol['name']}")
                st.caption(f"Status: {protocol['status']}")

    with quick_start_col2:
        st.markdown("#### Recent Tests")
        st.info("No recent tests found. Start a new test from the Test Dashboard.")

    # System Status
    st.markdown("---")
    st.markdown("### 💻 System Status")

    status_col1, status_col2, status_col3, status_col4 = st.columns(4)

    with status_col1:
        st.metric("Active Protocols", "1")

    with status_col2:
        st.metric("Tests Run", "0")

    with status_col3:
        st.metric("Database Status", "✓ Connected")

    with status_col4:
        st.metric("API Status", "✓ Ready")

elif page == "📊 Test Dashboard":
    from src.ui.pages.test_dashboard import render_test_dashboard
    render_test_dashboard()

elif page == "⚙️ Protocol Editor":
    from src.ui.pages.protocol_editor import render_protocol_editor
    render_protocol_editor()

elif page == "📈 Results Viewer":
    from src.ui.pages.results_viewer import render_results_viewer
    render_results_viewer()

elif page == "📝 Reports":
    st.markdown('<p class="main-header">Reports</p>', unsafe_allow_html=True)
    st.info("Report generation interface - Coming soon!")

# Footer
st.markdown("---")
st.caption("© 2025 Test Protocols Framework | MIT License")
