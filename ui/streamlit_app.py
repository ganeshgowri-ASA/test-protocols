"""Main Streamlit application for test protocol execution and management."""

import streamlit as st
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from protocols.base import ProtocolRegistry
from protocols.degradation import load_uvid_001


def init_session_state():
    """Initialize Streamlit session state."""
    if 'protocol_registry' not in st.session_state:
        st.session_state.protocol_registry = ProtocolRegistry()

        # Load protocols from directory
        protocols_dir = Path(__file__).parent.parent / 'protocols'
        st.session_state.protocol_registry.register_from_directory(protocols_dir)

    if 'selected_protocol' not in st.session_state:
        st.session_state.selected_protocol = None

    if 'current_test' not in st.session_state:
        st.session_state.current_test = None


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="PV Test Protocol System",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    init_session_state()

    # Sidebar navigation
    st.sidebar.title("⚡ PV Test Protocols")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigation",
        [
            "Protocol Selection",
            "Test Execution",
            "Results Dashboard",
            "Data Visualization",
            "Report Generation",
            "Protocol Management"
        ]
    )

    st.sidebar.markdown("---")
    st.sidebar.info(
        "**System Status**\n\n"
        f"Protocols Loaded: {len(st.session_state.protocol_registry)}\n\n"
        f"Active Test: {'Yes' if st.session_state.current_test else 'No'}"
    )

    # Main content area
    if page == "Protocol Selection":
        show_protocol_selection()
    elif page == "Test Execution":
        show_test_execution()
    elif page == "Results Dashboard":
        show_results_dashboard()
    elif page == "Data Visualization":
        show_data_visualization()
    elif page == "Report Generation":
        show_report_generation()
    elif page == "Protocol Management":
        show_protocol_management()


def show_protocol_selection():
    """Display protocol selection page."""
    st.title("Protocol Selection")
    st.markdown("Select a test protocol to execute")

    # Get available protocols
    protocols = st.session_state.protocol_registry.list_protocols()

    if not protocols:
        st.warning("No protocols loaded. Please check the protocols directory.")
        return

    # Group protocols by category
    categories = {}
    for protocol in protocols:
        category = protocol['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(protocol)

    # Display protocols by category
    for category, proto_list in sorted(categories.items()):
        st.subheader(f"📁 {category}")

        for protocol in proto_list:
            with st.expander(f"{protocol['protocol_id']}: {protocol['name']}"):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write(f"**Protocol ID:** {protocol['protocol_id']}")
                    st.write(f"**Version:** {protocol['version']}")

                    # Load full protocol for details
                    full_protocol = st.session_state.protocol_registry.get(protocol['protocol_id'])
                    if full_protocol:
                        st.write(f"**Description:** {full_protocol.definition.get('description', 'N/A')}")

                with col2:
                    if st.button("Select", key=f"select_{protocol['protocol_id']}"):
                        st.session_state.selected_protocol = protocol['protocol_id']
                        st.success(f"Selected: {protocol['name']}")
                        st.rerun()

    # Show selected protocol
    if st.session_state.selected_protocol:
        st.markdown("---")
        st.success(f"✓ Currently Selected: **{st.session_state.selected_protocol}**")

        if st.button("Proceed to Test Execution"):
            st.switch_page("pages/test_execution.py")


def show_test_execution():
    """Display test execution page."""
    st.title("Test Execution")

    if not st.session_state.selected_protocol:
        st.warning("Please select a protocol first.")
        if st.button("Go to Protocol Selection"):
            st.rerun()
        return

    protocol = st.session_state.protocol_registry.get(st.session_state.selected_protocol)

    st.subheader(f"Executing: {protocol.name}")
    st.write(f"**Protocol ID:** {protocol.protocol_id}")
    st.write(f"**Version:** {protocol.version}")

    # Test parameters form
    st.markdown("### Test Parameters")

    with st.form("test_parameters_form"):
        params = {}

        for param_name, param_spec in protocol.parameters.items():
            st.write(f"**{param_spec.description}**")

            if param_spec.param_type in ['float', 'integer']:
                default = param_spec.default_value or 0
                min_val = param_spec.min_value if param_spec.min_value is not None else 0.0
                max_val = param_spec.max_value if param_spec.max_value is not None else 1000.0

                value = st.number_input(
                    f"{param_name} ({param_spec.unit})",
                    min_value=float(min_val),
                    max_value=float(max_val),
                    value=float(default),
                    key=param_name
                )
                params[param_name] = value
            else:
                value = st.text_input(
                    f"{param_name} ({param_spec.unit})",
                    value=str(param_spec.default_value or ''),
                    key=param_name
                )
                params[param_name] = value

        # Specimen information
        st.markdown("### Specimen Information")
        specimen_code = st.text_input("Specimen Code", key="specimen_code")
        specimen_type = st.text_input("Specimen Type", value="PV Module", key="specimen_type")

        # Operator information
        st.markdown("### Operator Information")
        operator_name = st.text_input("Operator Name", key="operator_name")

        submitted = st.form_submit_button("Start Test")

        if submitted:
            # Validate parameters
            is_valid, errors = protocol.validate_parameters(params)

            if not is_valid:
                st.error("Parameter validation failed:")
                for error in errors:
                    st.error(f"- {error}")
            elif not specimen_code or not operator_name:
                st.error("Please provide specimen code and operator name")
            else:
                st.success("Test configuration validated successfully!")
                st.info("Test execution would start here. (Database integration required)")

                # Store test configuration
                st.session_state.current_test = {
                    'protocol_id': protocol.protocol_id,
                    'parameters': params,
                    'specimen_code': specimen_code,
                    'specimen_type': specimen_type,
                    'operator_name': operator_name
                }


def show_results_dashboard():
    """Display results dashboard page."""
    st.title("Results Dashboard")
    st.info("Results dashboard will display test execution status and results.")

    if st.session_state.current_test:
        st.subheader("Current Test")
        test = st.session_state.current_test
        st.json(test)
    else:
        st.warning("No active test")


def show_data_visualization():
    """Display data visualization page."""
    st.title("Data Visualization")
    st.info("Data visualization page for plotting I-V curves and degradation trends.")


def show_report_generation():
    """Display report generation page."""
    st.title("Report Generation")
    st.info("Report generation page for creating PDF, Excel, and HTML reports.")


def show_protocol_management():
    """Display protocol management page."""
    st.title("Protocol Management")

    st.subheader("Loaded Protocols")

    protocols = st.session_state.protocol_registry.list_protocols()

    if protocols:
        import pandas as pd
        df = pd.DataFrame(protocols)
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("No protocols loaded")

    st.markdown("---")

    st.subheader("Load Protocol from File")

    uploaded_file = st.file_uploader("Upload Protocol JSON", type=['json'])

    if uploaded_file:
        import json
        import tempfile

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            content = uploaded_file.read().decode('utf-8')
            f.write(content)
            temp_path = Path(f.name)

        try:
            # Load protocol
            protocol = st.session_state.protocol_registry.register_from_file(temp_path)
            st.success(f"Loaded protocol: {protocol.name} ({protocol.protocol_id})")
        except Exception as e:
            st.error(f"Failed to load protocol: {e}")
        finally:
            # Clean up temp file
            temp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
