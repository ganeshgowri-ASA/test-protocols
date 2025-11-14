"""
Test Protocols Streamlit Application
=====================================

Main application entry point for the PV Test Protocols Framework.
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.protocol_loader import ProtocolLoader
from src.core.data_validator import DataValidator
from src.core.test_runner import TestRunner
from src.analysis.calculators import DielectricCalculator

# Page configuration
st.set_page_config(
    page_title="PV Test Protocols",
    page_icon="⚡",
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
    .protocol-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin: 1rem 0;
    }
    .pass-result {
        color: #28a745;
        font-weight: bold;
    }
    .fail-result {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'protocol_loader' not in st.session_state:
    st.session_state.protocol_loader = ProtocolLoader("./protocols")

if 'current_protocol' not in st.session_state:
    st.session_state.current_protocol = None

if 'test_data' not in st.session_state:
    st.session_state.test_data = {}

def main():
    """Main application function"""

    # Sidebar
    with st.sidebar:
        st.title("⚡ PV Test Protocols")
        st.markdown("---")

        # Protocol selection
        st.subheader("Protocol Selection")
        protocols = st.session_state.protocol_loader.list_available_protocols()

        if protocols:
            protocol_names = {
                f"{p.protocol_id}: {p.protocol_name}": p.protocol_id
                for p in protocols
            }

            selected = st.selectbox(
                "Select Protocol",
                options=list(protocol_names.keys())
            )

            if selected:
                protocol_id = protocol_names[selected]
                if st.button("Load Protocol"):
                    protocol = st.session_state.protocol_loader.load_protocol(protocol_id)
                    st.session_state.current_protocol = protocol
                    st.success(f"Loaded {protocol_id}")
                    st.rerun()
        else:
            st.warning("No protocols found")

        st.markdown("---")
        st.subheader("Navigation")
        page = st.radio(
            "Go to",
            ["Home", "Test Execution", "Results", "Reports"]
        )

    # Main content area
    if page == "Home":
        show_home_page()
    elif page == "Test Execution":
        show_test_execution_page()
    elif page == "Results":
        show_results_page()
    elif page == "Reports":
        show_reports_page()

def show_home_page():
    """Show home page"""
    st.markdown('<p class="main-header">PV Test Protocols Framework</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Active Protocols", "1")
    with col2:
        st.metric("Tests Today", "0")
    with col3:
        st.metric("Pass Rate", "100%")

    st.markdown("---")

    if st.session_state.current_protocol:
        protocol = st.session_state.current_protocol
        st.subheader(f"Current Protocol: {protocol['protocol_name']}")

        with st.expander("Protocol Details", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**ID:** {protocol['protocol_id']}")
                st.write(f"**Version:** {protocol['version']}")
                st.write(f"**Standard:** {protocol['standard']}")
            with col2:
                st.write(f"**Category:** {protocol['category']}")
                st.write(f"**Description:** {protocol['description']}")

def show_test_execution_page():
    """Show test execution page"""
    st.markdown('<p class="main-header">Test Execution</p>', unsafe_allow_html=True)

    if not st.session_state.current_protocol:
        st.warning("Please load a protocol first")
        return

    protocol = st.session_state.current_protocol

    # Test information form
    st.subheader("Test Information")

    col1, col2 = st.columns(2)
    with col1:
        module_id = st.text_input("Module ID *", key="module_id")
        operator = st.text_input("Operator Name *", key="operator")
    with col2:
        test_date = st.date_input("Test Date *", key="test_date")

    st.markdown("---")

    # Dynamic form based on protocol data points
    st.subheader("Test Data")

    for data_point in protocol.get('data_points', []):
        field = data_point['field']
        label = data_point.get('label', field)
        required = data_point.get('required', False)
        field_type = data_point['type']

        label_text = f"{label} {'*' if required else ''}"

        if field_type == 'number':
            min_val = data_point.get('min')
            max_val = data_point.get('max')
            unit = data_point.get('unit', '')
            value = st.number_input(
                f"{label_text} ({unit})" if unit else label_text,
                min_value=min_val,
                max_value=max_val,
                key=field
            )
            st.session_state.test_data[field] = value

        elif field_type == 'string':
            value = st.text_input(label_text, key=field)
            st.session_state.test_data[field] = value

        elif field_type == 'boolean':
            value = st.checkbox(label_text, key=field)
            st.session_state.test_data[field] = value

        elif field_type == 'date':
            value = st.date_input(label_text, key=field)
            st.session_state.test_data[field] = str(value)

    st.markdown("---")

    # Calculate derived fields for DIEL-001
    if protocol['protocol_id'] == 'DIEL-001':
        if 'max_system_voltage' in st.session_state.test_data:
            max_sys_v = st.session_state.test_data['max_system_voltage']
            if max_sys_v > 0:
                test_voltage = DielectricCalculator.calculate_test_voltage(max_sys_v)
                st.session_state.test_data['test_voltage_calculated'] = test_voltage
                st.info(f"📊 Calculated Test Voltage: {test_voltage:.0f} V")

    # Submit button
    if st.button("Validate & Submit Test Data", type="primary"):
        validator = DataValidator(protocol)
        result = validator.validate(st.session_state.test_data)

        if result.is_valid:
            st.success("✅ Test data validation passed!")

            # Show test evaluation for DIEL-001
            if protocol['protocol_id'] == 'DIEL-001':
                evaluation = DielectricCalculator.evaluate_test_result(st.session_state.test_data)

                st.subheader("Test Result Evaluation")

                if evaluation['overall_pass']:
                    st.markdown('<p class="pass-result">✅ PASS</p>', unsafe_allow_html=True)
                else:
                    st.markdown('<p class="fail-result">❌ FAIL</p>', unsafe_allow_html=True)

                for check_name, check_data in evaluation['checks'].items():
                    with st.expander(f"{check_name.replace('_', ' ').title()}", expanded=not check_data['pass']):
                        if check_data['pass']:
                            st.success(f"✅ {check_data.get('requirement', 'Check passed')}")
                        else:
                            st.error(f"❌ {check_data.get('requirement', 'Check failed')}")

                        if 'value' in check_data:
                            st.write(f"Value: {check_data['value']:.2f}")

                if evaluation['failures']:
                    st.error("**Failures:**")
                    for failure in evaluation['failures']:
                        st.write(f"- {failure}")

        else:
            st.error("❌ Test data validation failed!")
            for error in result.errors:
                st.error(f"- {error.field}: {error.message}")

def show_results_page():
    """Show results page"""
    st.markdown('<p class="main-header">Test Results</p>', unsafe_allow_html=True)
    st.info("Results page - Connect to database to view historical results")

def show_reports_page():
    """Show reports page"""
    st.markdown('<p class="main-header">Reports</p>', unsafe_allow_html=True)
    st.info("Reports page - Generate and download test reports")

if __name__ == "__main__":
    main()
