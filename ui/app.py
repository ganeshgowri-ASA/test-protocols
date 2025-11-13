"""Main Streamlit application for PV Testing Protocol Framework."""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.protocol_loader import get_protocol_loader
from src.database.connection import get_db_manager
from src.database.models import Protocol as ProtocolModel, TestRun
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="PV Testing Protocol Framework",
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
        text-align: center;
        margin-bottom: 2rem;
    }
    .protocol-card {
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #ddd;
        margin-bottom: 1rem;
        background-color: #f8f9fa;
    }
    .metric-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #e3f2fd;
        text-align: center;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 0.25rem;
        font-weight: bold;
        font-size: 0.875rem;
    }
    .status-active {
        background-color: #d4edda;
        color: #155724;
    }
    .status-pending {
        background-color: #fff3cd;
        color: #856404;
    }
    .status-completed {
        background-color: #d1ecf1;
        color: #0c5460;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = get_db_manager()

    if 'protocol_loader' not in st.session_state:
        st.session_state.protocol_loader = get_protocol_loader()

    if 'selected_protocol' not in st.session_state:
        st.session_state.selected_protocol = None

    if 'current_test_run' not in st.session_state:
        st.session_state.current_test_run = None


def load_protocols():
    """Load protocols into database from JSON files."""
    loader = st.session_state.protocol_loader
    db_manager = st.session_state.db_manager

    protocols = loader.list_protocols()

    with db_manager.session_scope() as session:
        for protocol_data in protocols:
            # Check if protocol already exists
            existing = session.query(ProtocolModel).filter_by(
                protocol_id=protocol_data['protocol_id']
            ).first()

            if not existing:
                # Load full protocol config
                protocol_config = loader.load(protocol_data['protocol_id'])

                # Create new protocol entry
                protocol = ProtocolModel(
                    protocol_id=protocol_data['protocol_id'],
                    name=protocol_data['name'],
                    version=protocol_data['version'],
                    category=protocol_data['category'],
                    description=protocol_data['description'],
                    config=protocol_config,
                    standard_references=protocol_config.get('metadata', {}).get('standard_references'),
                    is_active=True
                )
                session.add(protocol)

    return protocols


def main():
    """Main application."""
    initialize_session_state()

    # Header
    st.markdown('<div class="main-header">🔬 PV Testing Protocol Framework</div>',
               unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("Navigation")

        # Load protocols
        with st.spinner("Loading protocols..."):
            protocols = load_protocols()

        # Protocol selection
        protocol_options = {f"{p['protocol_id']}: {p['name']}": p['protocol_id']
                          for p in protocols}

        if protocol_options:
            selected = st.selectbox(
                "Select Protocol",
                options=list(protocol_options.keys()),
                index=0 if protocol_options else None
            )

            if selected:
                st.session_state.selected_protocol = protocol_options[selected]
        else:
            st.warning("No protocols available")
            st.session_state.selected_protocol = None

        st.divider()

        # Navigation menu
        st.subheader("Menu")
        page = st.radio(
            "Go to:",
            ["Home", "Protocol Info", "New Test Run", "View Results", "Reports"],
            label_visibility="collapsed"
        )

        st.divider()

        # Statistics
        st.subheader("Statistics")
        with st.session_state.db_manager.session_scope() as session:
            total_protocols = session.query(ProtocolModel).filter_by(is_active=True).count()
            total_test_runs = session.query(TestRun).count()
            completed_runs = session.query(TestRun).filter_by(status='completed').count()

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Protocols", total_protocols)
            st.metric("Test Runs", total_test_runs)
        with col2:
            st.metric("Completed", completed_runs)
            if total_test_runs > 0:
                completion_rate = (completed_runs / total_test_runs) * 100
                st.metric("Completion", f"{completion_rate:.1f}%")

    # Main content area
    if page == "Home":
        show_home_page()
    elif page == "Protocol Info":
        show_protocol_info_page()
    elif page == "New Test Run":
        show_new_test_run_page()
    elif page == "View Results":
        show_results_page()
    elif page == "Reports":
        show_reports_page()


def show_home_page():
    """Display home page."""
    st.header("Welcome to PV Testing Protocol Framework")

    st.markdown("""
    ### 🎯 Purpose
    This framework provides a modular, JSON-based system for managing and executing
    photovoltaic module testing protocols with automated analysis, quality control,
    and reporting capabilities.

    ### ✨ Features
    - **Dynamic Protocol Management**: JSON-based protocol definitions
    - **Interactive Testing Interface**: User-friendly data collection
    - **Automated Analysis**: Real-time calculations and statistics
    - **Quality Control**: Automated QC checks and validation
    - **Comprehensive Reporting**: PDF and HTML report generation
    - **Data Traceability**: Complete audit trail and version control
    - **Standards Compliance**: IEC 61853, IEC 60904, and other standards

    ### 📋 Available Protocols
    """)

    loader = st.session_state.protocol_loader
    protocols = loader.list_protocols()

    for protocol in protocols:
        with st.expander(f"**{protocol['protocol_id']}**: {protocol['name']}"):
            st.markdown(f"**Category**: {protocol['category']}")
            st.markdown(f"**Version**: {protocol['version']}")
            st.markdown(f"**Description**: {protocol['description']}")

            if protocol['protocol_id'] == st.session_state.selected_protocol:
                if st.button(f"Start Test Run", key=f"start_{protocol['protocol_id']}"):
                    st.session_state.selected_protocol = protocol['protocol_id']
                    st.rerun()

    st.divider()

    st.markdown("""
    ### 🚀 Quick Start
    1. Select a protocol from the sidebar
    2. Review the protocol information
    3. Create a new test run
    4. Enter measurement data
    5. Review analysis and QC results
    6. Generate reports
    """)


def show_protocol_info_page():
    """Display protocol information page."""
    if not st.session_state.selected_protocol:
        st.warning("Please select a protocol from the sidebar")
        return

    loader = st.session_state.protocol_loader
    protocol_id = st.session_state.selected_protocol

    try:
        protocol = loader.load(protocol_id)
    except Exception as e:
        st.error(f"Error loading protocol: {e}")
        return

    st.header(f"{protocol['name']}")
    st.subheader(f"Protocol ID: {protocol['protocol_id']} | Version: {protocol['version']}")

    # Basic information
    st.markdown("### 📄 Description")
    st.write(protocol.get('description', 'No description available'))

    # Metadata
    metadata = protocol.get('metadata', {})
    st.markdown("### 📊 Metadata")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Author**: {metadata.get('author', 'N/A')}")
        st.write(f"**Created**: {metadata.get('created_date', 'N/A')}")
    with col2:
        st.write(f"**Last Modified**: {metadata.get('last_modified', 'N/A')}")
        st.write(f"**Category**: {protocol.get('category', 'N/A')}")

    # Standards references
    standards = metadata.get('standard_references', [])
    if standards:
        st.markdown("### 📚 Standards References")
        for standard in standards:
            st.write(f"- {standard}")

    # Test configuration
    st.markdown("### ⚙️ Test Configuration")
    test_config = protocol.get('test_configuration', {})

    if protocol_id == 'PERF-002':
        irradiance_levels = test_config.get('irradiance_levels', [])
        st.write("**Irradiance Levels:**")
        for level in irradiance_levels:
            st.write(f"- {level['level']} {level['unit']}: {level['description']}")

    # Equipment required
    equipment = test_config.get('equipment_required', [])
    if equipment:
        st.markdown("### 🔧 Required Equipment")
        for item in equipment:
            st.write(f"- **{item.get('type', 'Unknown')}**: {item.get('specification', 'N/A')}")

    # Data collection fields
    st.markdown("### 📝 Data Collection Fields")
    fields = protocol.get('data_collection', {}).get('fields', [])
    if fields:
        field_df = []
        for field in fields:
            field_df.append({
                'Field': field['name'],
                'Type': field['type'],
                'Unit': field.get('unit', '-'),
                'Required': '✓' if field.get('required', False) else '',
                'Description': field.get('description', '')
            })
        st.dataframe(field_df, use_container_width=True)


def show_new_test_run_page():
    """Display new test run creation page."""
    if not st.session_state.selected_protocol:
        st.warning("Please select a protocol from the sidebar")
        return

    st.header("Create New Test Run")

    protocol_id = st.session_state.selected_protocol
    st.info(f"Selected Protocol: **{protocol_id}**")

    with st.form("new_test_run"):
        st.subheader("Test Run Information")

        col1, col2 = st.columns(2)

        with col1:
            operator = st.text_input("Operator Name*", placeholder="Enter operator name")
            module_serial = st.text_input("Module Serial Number*", placeholder="MOD-XXXXX")
            batch_number = st.text_input("Batch Number", placeholder="BATCH-XXX")

        with col2:
            project_code = st.text_input("Project Code", placeholder="PROJ-XXX")
            ambient_temp = st.number_input("Ambient Temperature (°C)", value=25.0, step=0.1)
            ambient_humidity = st.number_input("Ambient Humidity (%)", value=45.0, step=1.0)

        st.subheader("Equipment")
        equipment_ids = st.text_area(
            "Equipment IDs (one per line)",
            placeholder="REF-CELL-001\nPYRAN-002\nIV-TRACER-003"
        )

        notes = st.text_area("Notes", placeholder="Enter any additional notes or comments")

        submitted = st.form_submit_button("Create Test Run", type="primary")

        if submitted:
            if not operator or not module_serial:
                st.error("Operator name and module serial number are required")
            else:
                # Create test run
                run_number = f"{protocol_id}-{datetime.now().strftime('%Y-%m%d%H%M%S')}"

                equipment_list = [eq.strip() for eq in equipment_ids.split('\n') if eq.strip()]

                with st.session_state.db_manager.session_scope() as session:
                    # Get protocol from database
                    protocol = session.query(ProtocolModel).filter_by(
                        protocol_id=protocol_id
                    ).first()

                    if not protocol:
                        st.error("Protocol not found in database")
                        return

                    # Create test run
                    test_run = TestRun(
                        protocol_id=protocol.id,
                        run_number=run_number,
                        operator=operator,
                        module_serial=module_serial,
                        batch_number=batch_number if batch_number else None,
                        project_code=project_code if project_code else None,
                        ambient_temperature=ambient_temp,
                        ambient_humidity=ambient_humidity,
                        equipment_ids=equipment_list if equipment_list else None,
                        notes=notes if notes else None,
                        status='pending'
                    )
                    session.add(test_run)
                    session.flush()

                    st.session_state.current_test_run = test_run.run_number

                st.success(f"✅ Test run created successfully: **{run_number}**")
                st.info("You can now proceed to data entry")


def show_results_page():
    """Display test results page."""
    st.header("Test Results")

    with st.session_state.db_manager.session_scope() as session:
        test_runs = session.query(TestRun).order_by(TestRun.start_time.desc()).limit(50).all()

        if not test_runs:
            st.info("No test runs found")
            return

        # Create dataframe
        runs_data = []
        for run in test_runs:
            runs_data.append({
                'Run Number': run.run_number,
                'Protocol': run.protocol.protocol_id if run.protocol else 'N/A',
                'Operator': run.operator,
                'Module Serial': run.module_serial or 'N/A',
                'Status': run.status,
                'Start Time': run.start_time.strftime('%Y-%m-%d %H:%M') if run.start_time else 'N/A'
            })

        st.dataframe(runs_data, use_container_width=True)


def show_reports_page():
    """Display reports page."""
    st.header("Reports")
    st.info("Report generation feature coming soon!")


if __name__ == "__main__":
    main()
