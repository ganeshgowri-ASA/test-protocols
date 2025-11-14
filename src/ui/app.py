"""
Main Streamlit Application

GenSpark UI for Test Protocol Execution
"""

import streamlit as st
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import ProtocolLoader, ProtocolValidator, ProtocolExecutor, StepStatus
from database import init_database, get_db_manager
from ui.components.protocol_selector import ProtocolSelector
from ui.components.data_entry_form import DataEntryForm
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="PV Test Protocol System",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'protocol_loader' not in st.session_state:
        st.session_state.protocol_loader = ProtocolLoader()

    if 'protocol_validator' not in st.session_state:
        st.session_state.protocol_validator = ProtocolValidator()

    if 'selected_protocol' not in st.session_state:
        st.session_state.selected_protocol = None

    if 'executor' not in st.session_state:
        st.session_state.executor = None

    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0

    if 'current_substep' not in st.session_state:
        st.session_state.current_substep = 0

    if 'test_run_id' not in st.session_state:
        st.session_state.test_run_id = None


def main():
    """Main application function."""

    # Initialize session state
    initialize_session_state()

    # Sidebar navigation
    st.sidebar.title("⚡ PV Test Protocol System")

    menu = st.sidebar.radio(
        "Navigation",
        ["Home", "New Test", "View Tests", "Protocols", "Equipment", "Settings"]
    )

    # Main content area
    if menu == "Home":
        render_home()

    elif menu == "New Test":
        render_new_test()

    elif menu == "View Tests":
        render_view_tests()

    elif menu == "Protocols":
        render_protocols()

    elif menu == "Equipment":
        render_equipment()

    elif menu == "Settings":
        render_settings()


def render_home():
    """Render home page."""
    st.title("Welcome to PV Test Protocol System")

    st.markdown("""
    ## Modular PV Testing Protocol Framework

    This system provides a JSON-based dynamic templates system for executing
    PV module test protocols with automated analysis, charting, QC, and
    report generation.

    ### Key Features

    - 📋 **Dynamic Protocol Templates** - JSON-based protocol definitions
    - ✅ **Automated QC** - Real-time quality control checks
    - 📊 **Data Analysis** - Automated charting and statistics
    - 📝 **Report Generation** - Comprehensive test reports
    - 🔗 **System Integration** - LIMS, QMS, and Project Management

    ### Quick Start

    1. Select **New Test** from the sidebar to start a test run
    2. Choose a protocol from the available options
    3. Follow the guided workflow to complete the test
    4. Review results and generate reports

    ### Currently Available Protocols

    """)

    # List available protocols
    protocols = st.session_state.protocol_loader.list_protocols()

    if protocols:
        for protocol in protocols:
            with st.expander(f"{protocol['protocol_id']} - {protocol['name']}"):
                st.write(f"**Version:** {protocol['version']}")
                st.write(f"**Category:** {protocol['category']}")
                if protocol.get('subcategory'):
                    st.write(f"**Subcategory:** {protocol['subcategory']}")
    else:
        st.info("No protocols loaded. Please add protocol templates to the system.")


def render_new_test():
    """Render new test execution page."""
    st.title("New Test Run")

    # Protocol selection
    selector = ProtocolSelector(st.session_state.protocol_loader)

    # Step 1: Select protocol
    if st.session_state.selected_protocol is None:
        protocol = selector.render()

        if protocol:
            # Validate protocol
            is_valid, errors = st.session_state.protocol_validator.validate_protocol_structure(protocol)

            if is_valid:
                st.success("✅ Protocol validated successfully!")
                st.session_state.selected_protocol = protocol

                # Display protocol info
                selector.render_protocol_info(protocol)

                if st.button("Start Test Run"):
                    # Initialize executor
                    test_run_id = f"TEST-{uuid.uuid4().hex[:8]}"
                    st.session_state.test_run_id = test_run_id
                    st.session_state.executor = ProtocolExecutor(protocol, test_run_id)
                    st.session_state.executor.start_test()
                    st.session_state.current_step = 1
                    st.session_state.current_substep = 1.1
                    st.rerun()
            else:
                st.error("Protocol validation failed:")
                for error in errors:
                    st.error(f"- {error}")
        return

    # Step 2: Execute test steps
    protocol = st.session_state.selected_protocol
    executor = st.session_state.executor

    if executor is None:
        st.error("Executor not initialized. Please restart the test.")
        if st.button("Restart"):
            st.session_state.selected_protocol = None
            st.rerun()
        return

    # Display test run info
    st.info(f"**Test Run ID:** {st.session_state.test_run_id}")

    # Get progress
    progress = executor.get_progress()

    # Render progress
    form = DataEntryForm()
    form.render_progress(
        progress['total_substeps'],
        progress['completed_substeps'],
        f"{st.session_state.current_step}.{st.session_state.current_substep}"
    )

    # Get current step
    steps = protocol['test_sequence']['steps']

    # Find current step
    current_step_def = None
    current_substep_def = None

    for step in steps:
        if step['step_id'] == st.session_state.current_step:
            current_step_def = step
            for substep in step.get('substeps', []):
                if substep['substep_id'] == st.session_state.current_substep:
                    current_substep_def = substep
                    break
            break

    if current_substep_def is None:
        st.success("🎉 Test Completed!")
        executor.complete_test(StepStatus.COMPLETED)

        # Display results
        test_data = executor.get_test_data()

        st.subheader("Test Summary")
        st.json(test_data)

        if st.button("Start New Test"):
            st.session_state.selected_protocol = None
            st.session_state.executor = None
            st.session_state.test_run_id = None
            st.session_state.current_step = 0
            st.session_state.current_substep = 0
            st.rerun()

        return

    # Render current step
    step_key = f"{st.session_state.current_step}.{st.session_state.current_substep}"

    # Start step if not already started
    executor.start_step(st.session_state.current_step, st.session_state.current_substep)

    # Render data entry form
    data = form.render_step_form(current_substep_def, step_key)

    if data is not None:
        # Record data
        executor.record_data(
            st.session_state.current_step,
            st.session_state.current_substep,
            data
        )

        # Complete step
        executor.complete_step(
            st.session_state.current_step,
            st.session_state.current_substep,
            StepStatus.COMPLETED
        )

        st.success(f"✅ Step {step_key} completed!")

        # Move to next substep
        current_substeps = current_step_def.get('substeps', [])
        current_substep_index = next(
            (i for i, s in enumerate(current_substeps) if s['substep_id'] == st.session_state.current_substep),
            -1
        )

        if current_substep_index < len(current_substeps) - 1:
            # Next substep in same step
            st.session_state.current_substep = current_substeps[current_substep_index + 1]['substep_id']
        else:
            # Move to next step
            current_step_index = next(
                (i for i, s in enumerate(steps) if s['step_id'] == st.session_state.current_step),
                -1
            )

            if current_step_index < len(steps) - 1:
                next_step = steps[current_step_index + 1]
                st.session_state.current_step = next_step['step_id']
                st.session_state.current_substep = next_step['substeps'][0]['substep_id']
            else:
                # Test complete
                st.session_state.current_step = None
                st.session_state.current_substep = None

        st.rerun()


def render_view_tests():
    """Render test viewing page."""
    st.title("View Test Runs")
    st.info("Test run history will be displayed here (database integration required).")


def render_protocols():
    """Render protocols management page."""
    st.title("Protocol Management")

    selector = ProtocolSelector(st.session_state.protocol_loader)
    protocol = selector.render()

    if protocol:
        selector.render_protocol_info(protocol)


def render_equipment():
    """Render equipment management page."""
    st.title("Equipment Management")
    st.info("Equipment registry and calibration tracking (coming soon).")


def render_settings():
    """Render settings page."""
    st.title("Settings")

    st.subheader("Database Configuration")
    st.text_input("Database URL", value="sqlite:///data/test_protocols.db")

    if st.button("Initialize Database"):
        try:
            init_database()
            st.success("Database initialized successfully!")
        except Exception as e:
            st.error(f"Database initialization failed: {e}")

    st.subheader("System Information")
    st.write(f"**Python Version:** {sys.version}")
    st.write(f"**Streamlit Version:** {st.__version__}")


if __name__ == "__main__":
    main()
