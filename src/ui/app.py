"""
GenSpark UI - Main Application Entry Point
Multi-protocol test framework interface
"""
import streamlit as st
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from core.protocol_loader import ProtocolLoader


def main():
    """Main application entry point"""

    st.set_page_config(
        page_title="PV Test Protocol Framework",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Sidebar navigation
    st.sidebar.title("⚡ PV Test Protocols")
    st.sidebar.markdown("---")

    # Protocol selection
    loader = ProtocolLoader()

    try:
        protocols = loader.list_protocols()

        if not protocols:
            st.error("No protocols found. Please add protocol definitions to the protocols/ directory.")
            st.stop()

        # Group by category
        categories = {}
        for p in protocols:
            cat = p['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(p)

        # Category selector
        selected_category = st.sidebar.selectbox(
            "Category",
            options=list(categories.keys())
        )

        # Protocol selector
        protocols_in_category = categories[selected_category]
        protocol_options = {
            f"{p['protocol_id']} - {p['name']}": p['protocol_id']
            for p in protocols_in_category
        }

        selected_protocol_name = st.sidebar.selectbox(
            "Protocol",
            options=list(protocol_options.keys())
        )

        selected_protocol_id = protocol_options[selected_protocol_name]

        # Load selected protocol
        protocol = loader.load_protocol(selected_protocol_id)

        # Navigation
        st.sidebar.markdown("---")
        page = st.sidebar.radio(
            "Navigation",
            ["📋 Overview", "🚀 Execute Test", "📊 View Results", "⚙️ Settings"]
        )

        # Main content area
        if page == "📋 Overview":
            render_overview(protocol)
        elif page == "🚀 Execute Test":
            render_execute_test(protocol)
        elif page == "📊 View Results":
            render_results()
        elif page == "⚙️ Settings":
            render_settings()

    except Exception as e:
        st.error(f"Error loading protocols: {e}")
        st.exception(e)


def render_overview(protocol):
    """Render protocol overview page"""

    st.title(f"{protocol['protocol_id']} - {protocol['name']}")
    st.markdown(f"**Version:** {protocol['version']} | **Category:** {protocol['category']}")

    st.markdown("---")

    # Description
    st.subheader("Description")
    st.write(protocol.get('description', 'No description available'))

    # Key information
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Test Duration",
            f"{protocol['test_sequence']['total_test_duration']} "
            f"{protocol['test_sequence']['total_test_duration_unit']}"
        )

    with col2:
        st.metric(
            "Total Cycles",
            protocol['test_sequence'].get('total_cycles', 'N/A')
        )

    with col3:
        sample_size = protocol['test_requirements']['sample_size']
        st.metric(
            "Sample Size",
            f"{sample_size['minimum']}-{sample_size.get('recommended', 'N/A')}"
        )

    # Standards
    if 'standard' in protocol:
        st.subheader("Standards & References")
        st.info(f"📚 {protocol['standard']}")

    # Test sequence
    st.subheader("Test Sequence")

    steps = protocol['test_sequence']['steps']

    for i, step in enumerate(steps, 1):
        with st.expander(f"Step {i}: {step['name']}"):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Duration:** {step['duration']} {step['duration_unit']}")
                if 'temperature' in step:
                    st.write(f"**Temperature:** {step['temperature']}{step['temperature_unit']}")
                if 'relative_humidity' in step:
                    st.write(f"**Humidity:** {step['relative_humidity']}{step['humidity_unit']}")

            with col2:
                if 'repeat_count' in step:
                    st.write(f"**Repeat Count:** {step['repeat_count']}")
                if 'description' in step:
                    st.write(f"**Description:** {step['description']}")

    # Acceptance criteria
    st.subheader("Acceptance Criteria")

    criteria = protocol['acceptance_criteria']

    if 'visual' in criteria:
        st.write("**Visual:**")
        for check in criteria['visual'].get('specific_checks', []):
            st.write(f"  - {check}")

    if 'electrical' in criteria:
        st.write("**Electrical:**")
        elec = criteria['electrical']
        if 'power_degradation' in elec:
            st.write(
                f"  - Maximum power degradation: {elec['power_degradation']['max']}"
                f"{elec['power_degradation']['unit']}"
            )


def render_execute_test(protocol):
    """Render test execution page"""

    st.title(f"Execute: {protocol['protocol_id']}")

    # Check if there's a dedicated UI for this protocol
    protocol_id = protocol['protocol_id']

    if protocol_id == "TROP-001":
        st.info("Launching dedicated TROP-001 interface...")
        st.markdown("[Click here to launch TROP-001 interface](tropical_climate_ui.py)")

        st.markdown("---")
        st.subheader("Quick Start")

        st.write("""
        To run the TROP-001 dedicated interface:

        ```bash
        streamlit run src/ui/tropical_climate_ui.py
        ```
        """)

    else:
        st.warning(f"No dedicated UI available for {protocol_id}")
        st.info("Generic test execution interface coming soon...")


def render_results():
    """Render results viewing page"""

    st.title("Test Results")

    st.info("Results viewing interface coming soon...")

    # Placeholder for results
    st.subheader("Recent Tests")

    st.write("No test results available yet.")


def render_settings():
    """Render settings page"""

    st.title("Settings")

    st.subheader("System Configuration")

    # Database settings
    with st.expander("Database Settings"):
        db_type = st.selectbox("Database Type", ["SQLite", "PostgreSQL", "MySQL"])
        db_path = st.text_input("Database Path/URL", value="test_protocols.db")

        if st.button("Test Connection"):
            st.success("Connection successful!")

    # LIMS Integration
    with st.expander("LIMS Integration"):
        lims_enabled = st.checkbox("Enable LIMS Integration")
        if lims_enabled:
            lims_url = st.text_input("LIMS API URL")
            lims_key = st.text_input("API Key", type="password")

    # QMS Integration
    with st.expander("QMS Integration"):
        qms_enabled = st.checkbox("Enable QMS Integration")
        if qms_enabled:
            qms_url = st.text_input("QMS API URL")

    # Data Logger Settings
    with st.expander("Data Logger Settings"):
        logger_type = st.selectbox("Logger Type", ["Agilent", "Keysight", "Generic"])
        logger_ip = st.text_input("Logger IP Address")
        sampling_rate = st.number_input("Sampling Rate (seconds)", min_value=1, value=60)

    # Save settings
    if st.button("Save Settings", type="primary"):
        st.success("Settings saved successfully!")


if __name__ == "__main__":
    main()
