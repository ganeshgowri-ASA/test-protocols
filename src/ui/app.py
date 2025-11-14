"""GenSpark UI - PV Testing Protocol Framework.

Main Streamlit application for executing and managing test protocols.
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.protocol_loader import ProtocolLoader, ProtocolRegistry
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="GenSpark - PV Test Protocols",
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
        padding-bottom: 1rem;
    }
    .metric-card {
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
    .warning-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize Streamlit session state variables."""
    if 'protocol_loader' not in st.session_state:
        st.session_state.protocol_loader = ProtocolLoader()

    if 'protocol_registry' not in st.session_state:
        st.session_state.protocol_registry = ProtocolRegistry()

    if 'active_protocol' not in st.session_state:
        st.session_state.active_protocol = None

    if 'active_session' not in st.session_state:
        st.session_state.active_session = None

    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0


def show_protocol_selection():
    """Display protocol selection page."""
    st.markdown('<p class="main-header">📋 Protocol Selection</p>', unsafe_allow_html=True)

    # Category filter
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        category_filter = st.selectbox(
            "Filter by Category",
            ["All", "Degradation", "Performance", "Environmental", "Safety"],
            key="category_filter"
        )

    with col2:
        search_term = st.text_input("Search protocols", placeholder="Enter protocol name or ID...")

    with col3:
        st.markdown("###")
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    # Load protocols
    loader = st.session_state.protocol_loader

    try:
        if category_filter == "All":
            protocols = loader.list_protocols()
        else:
            protocols = loader.list_protocols(category=category_filter.lower())

        # Apply search filter
        if search_term:
            protocols = [
                p for p in protocols
                if search_term.lower() in p['name'].lower() or
                   search_term.lower() in p['protocol_id'].lower()
            ]

        # Display protocols
        st.markdown(f"### Available Protocols ({len(protocols)})")

        if not protocols:
            st.info("No protocols found matching your criteria.")
        else:
            for protocol in protocols:
                with st.expander(
                    f"**{protocol['protocol_id']}** - {protocol['name']}",
                    expanded=False
                ):
                    col_a, col_b = st.columns([3, 1])

                    with col_a:
                        st.markdown(f"**Version:** {protocol['version']}")
                        st.markdown(f"**Category:** {protocol['category'].title()}")
                        st.markdown(f"**Description:**")
                        st.markdown(protocol.get('description', 'No description available'))

                    with col_b:
                        st.markdown("###")
                        if st.button(
                            "▶️ Start Test",
                            key=f"start_{protocol['protocol_id']}",
                            use_container_width=True
                        ):
                            st.session_state.active_protocol = protocol['protocol_id']
                            st.session_state.current_page = 'test_execution'
                            st.rerun()

                        if st.button(
                            "📄 View Details",
                            key=f"view_{protocol['protocol_id']}",
                            use_container_width=True
                        ):
                            st.session_state.view_protocol = protocol['protocol_id']

    except Exception as e:
        st.error(f"Error loading protocols: {str(e)}")
        logger.error(f"Protocol loading error: {e}", exc_info=True)


def show_test_execution():
    """Display test execution page."""
    st.markdown('<p class="main-header">🔬 Test Execution</p>', unsafe_allow_html=True)

    protocol_id = st.session_state.get('active_protocol')

    if not protocol_id:
        st.warning("⚠️ No protocol selected. Please select a protocol to begin.")
        if st.button("← Back to Protocol Selection"):
            st.session_state.current_page = 'protocol_selection'
            st.rerun()
        return

    try:
        # Load protocol
        loader = st.session_state.protocol_loader
        registry = st.session_state.protocol_registry

        # Get protocol instance
        if protocol_id in registry.list_registered():
            protocol_class = registry.get_implementation(protocol_id)
            protocol_def = loader.load_protocol(protocol_id)
            protocol = protocol_class(protocol_def)
        else:
            st.error(f"Protocol {protocol_id} is not implemented yet.")
            return

        # Header
        st.markdown(f"## {protocol.name}")
        st.markdown(f"*Version {protocol.version} | Category: {protocol.category.title()}*")

        # Session Information
        st.markdown("### 📝 Test Session Information")

        col1, col2, col3 = st.columns(3)

        with col1:
            session_id = st.text_input(
                "Session ID",
                value=f"TEST-{protocol_id}-001",
                help="Unique identifier for this test session"
            )

        with col2:
            operator_name = st.text_input(
                "Operator Name",
                help="Name of person conducting the test"
            )

        with col3:
            sample_ids_input = st.text_area(
                "Sample IDs",
                help="Enter sample IDs, one per line",
                height=100
            )
            sample_ids = [s.strip() for s in sample_ids_input.split('\n') if s.strip()]

        # Protocol Steps
        st.markdown("---")
        st.markdown("### 🔄 Protocol Steps")

        # Create tabs for each step
        step_names = [f"{step.step_id}" for step in protocol.steps]
        tabs = st.tabs(step_names)

        for idx, (tab, step) in enumerate(zip(tabs, protocol.steps)):
            with tab:
                st.markdown(f"#### {step.name}")
                st.markdown(f"**Type:** {step.type.title()}")
                st.markdown(f"**Description:** {step.description}")

                # Check dependencies
                if step.dependencies:
                    st.info(f"📌 Dependencies: {', '.join(step.dependencies)}")

                st.markdown("---")

                # Measurement inputs
                measurements = {}

                for measurement in step.measurements:
                    meas_name = measurement['name']
                    meas_type = measurement['type']
                    meas_unit = measurement['unit']
                    validation = measurement.get('validation', {})

                    # Create input based on type
                    if meas_type == 'numeric':
                        min_val = validation.get('min', 0.0)
                        max_val = validation.get('max', 1000.0)
                        measurements[meas_name] = st.number_input(
                            f"{meas_name.replace('_', ' ').title()} ({meas_unit})",
                            min_value=float(min_val) if min_val is not None else None,
                            max_value=float(max_val) if max_val is not None else None,
                            value=float(min_val) if min_val is not None else 0.0,
                            key=f"{step.step_id}_{meas_name}",
                            help=f"Range: {min_val} - {max_val}" if min_val is not None and max_val is not None else None
                        )

                    elif meas_type == 'boolean':
                        measurements[meas_name] = st.checkbox(
                            meas_name.replace('_', ' ').title(),
                            key=f"{step.step_id}_{meas_name}"
                        )

                    elif meas_type == 'text':
                        measurements[meas_name] = st.text_area(
                            meas_name.replace('_', ' ').title(),
                            key=f"{step.step_id}_{meas_name}",
                            height=100
                        )

                    elif meas_type == 'image':
                        uploaded_file = st.file_uploader(
                            meas_name.replace('_', ' ').title(),
                            type=['png', 'jpg', 'jpeg'],
                            key=f"{step.step_id}_{meas_name}"
                        )
                        if uploaded_file:
                            measurements[meas_name] = uploaded_file.name
                            st.image(uploaded_file, caption=meas_name, width=300)
                        else:
                            measurements[meas_name] = None

                # Execute button
                st.markdown("---")
                col_btn1, col_btn2 = st.columns([1, 4])

                with col_btn1:
                    if st.button(
                        "✓ Execute Step",
                        key=f"exec_{step.step_id}",
                        use_container_width=True,
                        type="primary"
                    ):
                        if not operator_name:
                            st.error("Please enter operator name")
                        else:
                            try:
                                result = protocol.execute_step(
                                    step.step_id,
                                    measurements,
                                    operator_name
                                )

                                if result.status == 'pass':
                                    st.markdown(
                                        '<div class="success-box">✓ Step completed successfully</div>',
                                        unsafe_allow_html=True
                                    )
                                elif result.status == 'warning':
                                    st.markdown(
                                        '<div class="warning-box">⚠ Step completed with warnings</div>',
                                        unsafe_allow_html=True
                                    )
                                else:
                                    st.markdown(
                                        '<div class="error-box">✗ Step failed QC criteria</div>',
                                        unsafe_allow_html=True
                                    )

                                st.session_state.current_step = idx + 1

                            except Exception as e:
                                st.error(f"❌ Error executing step: {str(e)}")
                                logger.error(f"Step execution error: {e}", exc_info=True)

        # Final Evaluation
        st.markdown("---")
        st.markdown("### 📊 Final Evaluation")

        col_eval1, col_eval2 = st.columns([1, 4])

        with col_eval1:
            if st.button("🎯 Complete Test & Evaluate", use_container_width=True, type="primary"):
                try:
                    # Calculate results
                    calculations = protocol.calculate_results()
                    evaluation = protocol.evaluate_pass_fail()

                    # Store in session state for display
                    st.session_state.test_calculations = calculations
                    st.session_state.test_evaluation = evaluation
                    st.rerun()

                except Exception as e:
                    st.error(f"Error during evaluation: {str(e)}")
                    logger.error(f"Evaluation error: {e}", exc_info=True)

        # Display results if available
        if 'test_evaluation' in st.session_state:
            st.markdown("---")
            st.markdown("### 📈 Test Results")

            evaluation = st.session_state.test_evaluation
            calculations = st.session_state.get('test_calculations', {})

            # Overall result
            if evaluation['overall_pass']:
                st.markdown(
                    '<div class="success-box"><h2>✅ TEST PASSED</h2></div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    '<div class="error-box"><h2>❌ TEST FAILED</h2></div>',
                    unsafe_allow_html=True
                )

            # Calculations
            if calculations:
                st.markdown("#### Calculated Values")
                calc_cols = st.columns(min(len(calculations), 4))
                for idx, (name, value) in enumerate(calculations.items()):
                    with calc_cols[idx % 4]:
                        st.metric(
                            name.replace('_', ' ').title(),
                            f"{value:.2f}" if value is not None else "N/A"
                        )

            # Criteria evaluation
            st.markdown("#### Pass/Fail Criteria")
            for criterion in evaluation['criteria']:
                status_icon = "✅" if criterion['passed'] else "❌"
                severity_color = {
                    'critical': '🔴',
                    'major': '🟠',
                    'minor': '🟡'
                }.get(criterion['severity'], '⚪')

                st.markdown(
                    f"{status_icon} {severity_color} **{criterion['parameter']}**: "
                    f"{criterion['value']} {criterion['operator']} {criterion['threshold']}"
                )

                if criterion.get('description'):
                    st.caption(criterion['description'])

    except Exception as e:
        st.error(f"Error loading protocol: {str(e)}")
        logger.error(f"Protocol execution error: {e}", exc_info=True)


def show_results_viewer():
    """Display results viewer page."""
    st.markdown('<p class="main-header">📊 Results Viewer</p>', unsafe_allow_html=True)

    st.info("Results viewer - Coming soon!")
    st.markdown("This page will display historical test results and allow data analysis.")


def show_reports():
    """Display reports page."""
    st.markdown('<p class="main-header">📑 Reports</p>', unsafe_allow_html=True)

    st.info("Report generation - Coming soon!")
    st.markdown("This page will allow generating and exporting test reports in various formats.")


def show_admin():
    """Display admin page."""
    st.markdown('<p class="main-header">⚙️ Administration</p>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Protocol Validation", "Equipment", "Samples"])

    with tab1:
        st.markdown("### Protocol Validation")

        if st.button("Validate All Protocols"):
            loader = st.session_state.protocol_loader
            results = loader.validate_all_protocols()

            st.markdown(f"**Total Protocols:** {results['total']}")
            st.markdown(f"**Valid:** {results['valid']} ✅")
            st.markdown(f"**Invalid:** {results['invalid']} ❌")

            if results['errors']:
                st.markdown("#### Validation Errors")
                for error in results['errors']:
                    st.error(f"**{error['file']}**: {error['error']}")

    with tab2:
        st.info("Equipment management - Coming soon!")

    with tab3:
        st.info("Sample management - Coming soon!")


def main():
    """Main application entry point."""
    # Initialize session state
    init_session_state()

    # Sidebar navigation
    st.sidebar.title("🔬 GenSpark")
    st.sidebar.markdown("### PV Test Protocols")

    page = st.sidebar.radio(
        "Navigation",
        ["Protocol Selection", "Test Execution", "Results Viewer", "Reports", "Administration"],
        key="navigation"
    )

    # Store current page in session state
    st.session_state.current_page = page.lower().replace(' ', '_')

    st.sidebar.markdown("---")

    # Quick stats
    st.sidebar.markdown("### 📊 Quick Stats")
    try:
        loader = st.session_state.protocol_loader
        all_protocols = loader.list_protocols()
        st.sidebar.metric("Total Protocols", len(all_protocols))

        # Count by category
        degradation = len([p for p in all_protocols if p['category'] == 'degradation'])
        st.sidebar.metric("Degradation Protocols", degradation)

    except Exception as e:
        logger.error(f"Error loading stats: {e}")

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Version:** 1.0.0")
    st.sidebar.markdown("**Protocol:** SEAL-001 Active ✅")

    # Route to appropriate page
    if page == "Protocol Selection":
        show_protocol_selection()
    elif page == "Test Execution":
        show_test_execution()
    elif page == "Results Viewer":
        show_results_viewer()
    elif page == "Reports":
        show_reports()
    elif page == "Administration":
        show_admin()


if __name__ == "__main__":
    main()
