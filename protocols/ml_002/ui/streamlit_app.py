"""
ML-002 Streamlit Application

Complete Streamlit application for ML-002 Mechanical Load Dynamic Test

Author: ganeshgowri-ASA
Date: 2025-11-14
Version: 1.0.0
"""

import streamlit as st
import sys
from pathlib import Path
import json
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from implementation import ML002MechanicalLoadTest, TestSample, TestStatus, AlertLevel
from analyzer import ML002Analyzer
from ui.components import ML002UIComponents


# Page configuration
st.set_page_config(
    page_title="ML-002 Mechanical Load Test",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)


def load_protocol():
    """Load protocol from JSON file"""
    protocol_file = Path(__file__).parent.parent / "protocol.json"
    with open(protocol_file, 'r') as f:
        return json.load(f)


def initialize_session_state():
    """Initialize Streamlit session state"""
    if 'protocol' not in st.session_state:
        st.session_state.protocol = load_protocol()

    if 'test_instance' not in st.session_state:
        st.session_state.test_instance = None

    if 'test_running' not in st.session_state:
        st.session_state.test_running = False

    if 'test_results' not in st.session_state:
        st.session_state.test_results = None

    if 'sample_data' not in st.session_state:
        st.session_state.sample_data = None

    if 'test_parameters' not in st.session_state:
        st.session_state.test_parameters = None

    if 'live_data' not in st.session_state:
        st.session_state.live_data = {
            'current_load_pa': 0,
            'current_deflection_mm': 0,
            'current_cycle': 0,
            'total_cycles': 1000,
            'elapsed_time_seconds': 0,
            'load_history': [],
            'deflection_history': []
        }


def main():
    """Main application"""
    initialize_session_state()

    # Sidebar
    with st.sidebar:
        st.title("🔧 ML-002 Test")
        st.markdown("---")

        st.markdown("### Navigation")
        page = st.radio(
            "Select Page",
            ["Home", "Configure Test", "Run Test", "View Results", "Protocol Info"],
            label_visibility="collapsed"
        )

        st.markdown("---")
        st.markdown("### Protocol Info")
        protocol_meta = st.session_state.protocol['metadata']
        st.info(f"""
        **{protocol_meta['name']}**

        Version: {protocol_meta['version']}

        Standard: {protocol_meta.get('standard', 'N/A')}

        Category: {protocol_meta.get('category', 'N/A')}
        """)

    # Main content
    if page == "Home":
        render_home_page()
    elif page == "Configure Test":
        render_configure_page()
    elif page == "Run Test":
        render_run_test_page()
    elif page == "View Results":
        render_results_page()
    elif page == "Protocol Info":
        render_protocol_info_page()


def render_home_page():
    """Render home page"""
    st.title("ML-002 Mechanical Load Dynamic Test")
    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        ## Welcome to the ML-002 Test Interface

        This application provides a complete interface for executing and analyzing
        **Mechanical Load Dynamic Tests** on photovoltaic modules.

        ### Test Overview

        - **Load**: 1000 Pa cyclic loading
        - **Cycles**: Configurable (default: 1000 cycles)
        - **Standard**: IEC 61215-2:2021 MQT 16
        - **Purpose**: Evaluate module structural integrity under wind/snow loads

        ### Features

        - 📦 Sample registration and tracking
        - ⚙️ Configurable test parameters
        - 📊 Real-time monitoring
        - 📈 Comprehensive data analysis
        - ✓ Quality control evaluation
        - 📄 Automated report generation

        ### Getting Started

        1. **Configure Test**: Register module and set test parameters
        2. **Run Test**: Execute the test with real-time monitoring
        3. **View Results**: Analyze results and generate reports
        """)

    with col2:
        st.markdown("### Quick Stats")

        if st.session_state.sample_data:
            st.success("✅ Sample Registered")
            st.code(st.session_state.sample_data.get('sample_id', 'N/A'))
        else:
            st.warning("⚠️ No Sample Registered")

        if st.session_state.test_parameters:
            st.success("✅ Parameters Configured")
        else:
            st.warning("⚠️ Parameters Not Set")

        if st.session_state.test_results:
            st.success("✅ Results Available")
            passed = st.session_state.test_results.get('passed', False)
            if passed:
                st.success("✅ TEST PASSED")
            else:
                st.error("❌ TEST FAILED")
        else:
            st.info("ℹ️ No Test Results Yet")

        st.markdown("---")

        if st.button("🚀 Quick Start", type="primary", use_container_width=True):
            st.switch_page


def render_configure_page():
    """Render configuration page"""
    st.title("⚙️ Test Configuration")
    st.markdown("---")

    ui_components = ML002UIComponents(st.session_state.protocol)

    # Sample input
    sample_data = ui_components.render_sample_input_form()
    if sample_data:
        st.session_state.sample_data = sample_data
        st.success(f"✅ Module registered: {sample_data['sample_id']}")
        st.balloons()

    st.markdown("---")

    # Test parameters
    test_params = ui_components.render_test_parameters_form()
    if test_params:
        st.session_state.test_parameters = test_params
        st.success("✅ Test parameters configured")

    # Show current configuration
    if st.session_state.sample_data or st.session_state.test_parameters:
        st.markdown("---")
        st.markdown("### Current Configuration")

        col1, col2 = st.columns(2)

        with col1:
            if st.session_state.sample_data:
                st.markdown("#### Sample Data")
                st.json(st.session_state.sample_data)

        with col2:
            if st.session_state.test_parameters:
                st.markdown("#### Test Parameters")
                st.json(st.session_state.test_parameters)


def render_run_test_page():
    """Render test execution page"""
    st.title("🚀 Run Test")
    st.markdown("---")

    # Check prerequisites
    if not st.session_state.sample_data:
        st.error("❌ Please register a module first (Configure Test page)")
        return

    if not st.session_state.test_parameters:
        st.warning("⚠️ Using default test parameters")

    # Test controls
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("▶️ Start Test", type="primary", disabled=st.session_state.test_running, use_container_width=True):
            start_test()

    with col2:
        if st.button("⏸️ Pause", disabled=not st.session_state.test_running, use_container_width=True):
            pause_test()

    with col3:
        if st.button("⏹️ Stop", disabled=not st.session_state.test_running, use_container_width=True):
            stop_test()

    with col4:
        if st.button("🔄 Reset", use_container_width=True):
            reset_test()

    st.markdown("---")

    # Live monitoring
    if st.session_state.test_running or st.session_state.test_results:
        ui_components = ML002UIComponents(st.session_state.protocol)
        ui_components.render_live_test_monitor(st.session_state.live_data)

        # Auto-refresh while test is running
        if st.session_state.test_running:
            time.sleep(1)
            st.rerun()
    else:
        st.info("ℹ️ Test not started. Click 'Start Test' to begin.")


def render_results_page():
    """Render results page"""
    st.title("📊 Test Results")
    st.markdown("---")

    if not st.session_state.test_results:
        st.warning("⚠️ No test results available. Please run a test first.")
        return

    ui_components = ML002UIComponents(st.session_state.protocol)
    ui_components.render_test_results(st.session_state.test_results)


def render_protocol_info_page():
    """Render protocol information page"""
    st.title("📖 Protocol Information")
    st.markdown("---")

    protocol = st.session_state.protocol

    # Metadata
    st.markdown("### Protocol Metadata")
    metadata = protocol['metadata']
    st.json(metadata)

    # Parameters
    with st.expander("⚙️ Parameters", expanded=False):
        st.json(protocol['parameters'])

    # Data Collection
    with st.expander("📡 Data Collection", expanded=False):
        st.json(protocol['data_collection'])

    # Quality Control
    with st.expander("✓ Quality Control", expanded=False):
        st.json(protocol['quality_control'])

    # Reporting
    with st.expander("📄 Reporting", expanded=False):
        st.json(protocol['reporting'])


# Test control functions

def start_test():
    """Start test execution"""
    st.session_state.test_running = True

    # Create test instance
    protocol_file = Path(__file__).parent.parent / "protocol.json"
    test = ML002MechanicalLoadTest(str(protocol_file))

    # Create sample object
    sample = TestSample(**st.session_state.sample_data)

    # Set callbacks
    def progress_callback(cycle, total, data):
        st.session_state.live_data.update({
            'current_cycle': cycle,
            'total_cycles': total,
            'current_load_pa': data.get('current_load', 0),
            'current_deflection_mm': data.get('max_deflection', 0)
        })

    def alert_callback(level, message):
        if level == AlertLevel.CRITICAL:
            st.error(f"🚨 {message}")
        elif level == AlertLevel.WARNING:
            st.warning(f"⚠️ {message}")
        else:
            st.info(f"ℹ️ {message}")

    test.set_progress_callback(progress_callback)
    test.set_alert_callback(alert_callback)

    st.session_state.test_instance = test

    # Execute test (in real implementation, this should be async)
    st.info("▶️ Test started...")

    # For demo purposes, simulate test
    # In production, run in background thread
    # results = test.execute_test(sample)
    # st.session_state.test_results = results.to_dict()
    # st.session_state.test_running = False


def pause_test():
    """Pause test"""
    if st.session_state.test_instance:
        st.session_state.test_instance.pause_test()
        st.warning("⏸️ Test paused")


def stop_test():
    """Stop test"""
    if st.session_state.test_instance:
        st.session_state.test_instance.abort_test()
        st.session_state.test_running = False
        st.error("⏹️ Test stopped")


def reset_test():
    """Reset test state"""
    st.session_state.test_running = False
    st.session_state.test_instance = None
    st.session_state.test_results = None
    st.session_state.live_data = {
        'current_load_pa': 0,
        'current_deflection_mm': 0,
        'current_cycle': 0,
        'total_cycles': 1000,
        'elapsed_time_seconds': 0,
        'load_history': [],
        'deflection_history': []
    }
    st.success("🔄 Test reset")
    st.rerun()


if __name__ == "__main__":
    main()
