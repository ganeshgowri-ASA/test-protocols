"""Main Streamlit application for PV Testing Protocol Framework."""

import streamlit as st
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.models.base import get_engine, init_db, get_session
from src.parsers import ProtocolLoader, ProtocolExecutor


# Page configuration
st.set_page_config(
    page_title="PV Testing Protocol Framework",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
@st.cache_resource
def init_database():
    """Initialize the database connection."""
    engine = get_engine()
    init_db(engine)
    return engine


def initialize_session_state():
    """Initialize session state variables."""
    if "engine" not in st.session_state:
        st.session_state.engine = init_database()

    if "current_test_run" not in st.session_state:
        st.session_state.current_test_run = None

    if "protocol_loader" not in st.session_state:
        st.session_state.protocol_loader = ProtocolLoader()


def main():
    """Main application entry point."""
    initialize_session_state()

    # Sidebar navigation
    st.sidebar.title("🔬 PV Testing Framework")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Home",
            "📋 Protocols",
            "🧪 Run Test",
            "📊 Results",
            "📈 Analytics",
            "⚙️ Settings"
        ]
    )

    # Route to appropriate page
    if page == "🏠 Home":
        show_home_page()
    elif page == "📋 Protocols":
        show_protocols_page()
    elif page == "🧪 Run Test":
        show_run_test_page()
    elif page == "📊 Results":
        show_results_page()
    elif page == "📈 Analytics":
        show_analytics_page()
    elif page == "⚙️ Settings":
        show_settings_page()


def show_home_page():
    """Display the home page."""
    st.title("PV Testing Protocol Framework")
    st.markdown("### Modular PV Testing with Dynamic JSON Protocols")

    st.markdown("""
    Welcome to the PV Testing Protocol Framework! This system provides:

    - **Dynamic Protocol Definition**: JSON-based test protocols for flexibility
    - **Automated Test Execution**: Streamlined test running and data collection
    - **Real-time Monitoring**: Track test progress and results in real-time
    - **Comprehensive Analytics**: Analyze test results and trends
    - **Quality Control**: Automated acceptance criteria evaluation
    - **Report Generation**: Generate professional test reports

    ---

    #### Quick Start

    1. **📋 Browse Protocols**: View available test protocols
    2. **🧪 Run Test**: Execute a test protocol on a specimen
    3. **📊 View Results**: Review test results and measurements
    4. **📈 Analyze Data**: Explore trends and statistics
    """)

    # Display system status
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Loaded Protocols", get_protocol_count())

    with col2:
        st.metric("Active Test Runs", get_active_test_runs_count())

    with col3:
        st.metric("Completed Tests", get_completed_tests_count())


def show_protocols_page():
    """Display the protocols page."""
    from .pages.protocols import render_protocols_page
    render_protocols_page()


def show_run_test_page():
    """Display the run test page."""
    from .pages.run_test import render_run_test_page
    render_run_test_page()


def show_results_page():
    """Display the results page."""
    from .pages.results import render_results_page
    render_results_page()


def show_analytics_page():
    """Display the analytics page."""
    from .pages.analytics import render_analytics_page
    render_analytics_page()


def show_settings_page():
    """Display the settings page."""
    from .pages.settings import render_settings_page
    render_settings_page()


def get_protocol_count() -> int:
    """Get count of loaded protocols."""
    session = get_session(st.session_state.engine)
    from src.models import Protocol
    count = session.query(Protocol).filter_by(is_active=True).count()
    session.close()
    return count


def get_active_test_runs_count() -> int:
    """Get count of active test runs."""
    session = get_session(st.session_state.engine)
    from src.models import TestRun
    from src.models.test_run import TestStatus
    count = session.query(TestRun).filter_by(status=TestStatus.IN_PROGRESS).count()
    session.close()
    return count


def get_completed_tests_count() -> int:
    """Get count of completed tests."""
    session = get_session(st.session_state.engine)
    from src.models import TestRun
    from src.models.test_run import TestStatus
    count = session.query(TestRun).filter_by(status=TestStatus.COMPLETED).count()
    session.close()
    return count


if __name__ == "__main__":
    main()
