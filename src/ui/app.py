"""
GenSpark UI - Main Application

Streamlit-based UI for PV Testing Protocol Framework.
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.protocol_loader import ProtocolLoader


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="PV Testing Protocol Framework",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Sidebar
    st.sidebar.title("PV Testing Framework")
    st.sidebar.markdown("---")

    # Load available protocols
    try:
        loader = ProtocolLoader()
        protocols = loader.list_protocols()

        st.sidebar.subheader("Available Protocols")

        if not protocols:
            st.sidebar.warning("No protocols found")
            protocol_selection = None
        else:
            protocol_options = {
                f"{p['protocol_id']} - {p['name']}": p['protocol_id']
                for p in protocols
            }

            selected = st.sidebar.selectbox(
                "Select Protocol",
                options=list(protocol_options.keys())
            )

            protocol_selection = protocol_options[selected] if selected else None

    except Exception as e:
        st.sidebar.error(f"Error loading protocols: {e}")
        protocol_selection = None

    # Navigation
    st.sidebar.markdown("---")
    page = st.sidebar.radio(
        "Navigation",
        ["Home", "New Test Run", "View Results", "Analysis", "Reports"]
    )

    # Main content area
    if page == "Home":
        show_home_page(protocols if 'protocols' in locals() else [])

    elif page == "New Test Run":
        if protocol_selection:
            show_new_test_page(protocol_selection)
        else:
            st.warning("Please select a protocol from the sidebar")

    elif page == "View Results":
        show_results_page()

    elif page == "Analysis":
        show_analysis_page()

    elif page == "Reports":
        show_reports_page()


def show_home_page(protocols: list):
    """Display home page."""
    st.title("PV Testing Protocol Framework")

    st.markdown("""
    ## Welcome to the Modular PV Testing Protocol Framework

    This framework provides:
    - **JSON-based dynamic protocol templates**
    - **Streamlit/GenSpark UI integration**
    - **Automated analysis, charting, and QC**
    - **Report generation**
    - **Integration with LIMS, QMS, and Project Management systems**
    """)

    st.markdown("---")

    # Display available protocols
    st.subheader("Available Test Protocols")

    if not protocols:
        st.info("No protocols are currently available. Please add protocol templates.")
    else:
        cols = st.columns(min(len(protocols), 3))

        for idx, protocol in enumerate(protocols):
            col_idx = idx % 3
            with cols[col_idx]:
                st.markdown(f"""
                ### {protocol['protocol_id']}
                **{protocol['name']}**

                *Category:* {protocol['category']}

                *Version:* {protocol['version']}

                {protocol['description'][:150]}...
                """)

    st.markdown("---")

    # Quick stats
    st.subheader("System Status")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Available Protocols", len(protocols))

    with col2:
        st.metric("Active Tests", 0)  # TODO: Connect to database

    with col3:
        st.metric("Completed Tests", 0)  # TODO: Connect to database

    with col4:
        st.metric("Reports Generated", 0)  # TODO: Connect to database


def show_new_test_page(protocol_id: str):
    """Display new test run page."""
    st.title("New Test Run")

    try:
        loader = ProtocolLoader()
        protocol = loader.load_protocol(protocol_id)

        st.subheader(f"{protocol['name']} ({protocol['protocol_id']})")
        st.markdown(protocol['metadata']['description'])

        # Test run configuration
        st.markdown("---")
        st.subheader("Test Configuration")

        col1, col2 = st.columns(2)

        with col1:
            sample_id = st.text_input(
                "Sample ID *",
                placeholder="e.g., MODULE-001"
            )

            operator = st.text_input(
                "Operator Name *",
                placeholder="e.g., John Doe"
            )

            test_run_id = st.text_input(
                "Test Run ID (Optional)",
                placeholder="Auto-generated if left blank"
            )

        with col2:
            st.markdown("**Protocol Information**")
            st.markdown(f"- **Category:** {protocol['category']}")
            st.markdown(f"- **Version:** {protocol['version']}")
            st.markdown(f"- **Test Phases:** {len(protocol['test_phases'])}")
            st.markdown(f"- **Measurements:** {len(protocol['measurements'])}")

        # Display test phases
        st.markdown("---")
        st.subheader("Test Phases")

        for phase in protocol['test_phases']:
            with st.expander(f"{phase['phase_id']}: {phase['name']}"):
                st.markdown(f"**Description:** {phase['description']}")

                if 'duration' in phase:
                    st.markdown(
                        f"**Duration:** {phase['duration']['value']} "
                        f"{phase['duration']['unit']}"
                    )

                st.markdown(f"**Steps:** {len(phase['steps'])}")
                for step in phase['steps']:
                    st.markdown(f"- {step['step_id']}: {step['action']}")

        # Start test button
        st.markdown("---")

        if st.button("Start Test Run", type="primary", disabled=not (sample_id and operator)):
            if sample_id and operator:
                st.success(f"Test run started for sample {sample_id}")
                st.info("Navigate to the protocol-specific page to continue")
            else:
                st.error("Please fill in all required fields")

    except Exception as e:
        st.error(f"Error loading protocol: {e}")


def show_results_page():
    """Display test results page."""
    st.title("Test Results")
    st.info("Results viewing functionality coming soon")


def show_analysis_page():
    """Display analysis page."""
    st.title("Data Analysis")
    st.info("Analysis functionality coming soon")


def show_reports_page():
    """Display reports page."""
    st.title("Reports")
    st.info("Report generation functionality coming soon")


if __name__ == "__main__":
    main()
