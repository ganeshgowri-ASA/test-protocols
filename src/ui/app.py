"""Main Streamlit application for Test Protocol Framework."""

import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.protocol_loader import ProtocolLoader
from src.database.connection import DatabaseManager
from src.database.schema import SchemaManager

# Page configuration
st.set_page_config(
    page_title="PV Testing Protocol Framework",
    page_icon="⚗️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def init_session_state():
    """Initialize session state variables."""
    if "db_manager" not in st.session_state:
        st.session_state.db_manager = DatabaseManager("sqlite:///test_protocols.db")
        st.session_state.db_manager.init_db()

    if "protocol_loader" not in st.session_state:
        st.session_state.protocol_loader = ProtocolLoader()

    if "current_protocol" not in st.session_state:
        st.session_state.current_protocol = None

    if "test_run_id" not in st.session_state:
        st.session_state.test_run_id = None


def main():
    """Main application entry point."""
    init_session_state()

    # Sidebar navigation
    with st.sidebar:
        st.title("⚗️ Test Protocol Framework")
        st.markdown("---")

        page = st.radio(
            "Navigation",
            [
                "🏠 Home",
                "📋 Protocol Runner",
                "📊 Data Viewer",
                "📈 Analysis & Results",
                "📝 Reports",
                "⚙️ Database Management",
            ],
        )

        st.markdown("---")
        st.markdown("### System Info")
        st.caption("Version: 0.1.0")
        st.caption("Database: SQLite")

    # Main content area
    if page == "🏠 Home":
        show_home_page()
    elif page == "📋 Protocol Runner":
        show_protocol_runner()
    elif page == "📊 Data Viewer":
        show_data_viewer()
    elif page == "📈 Analysis & Results":
        show_analysis_page()
    elif page == "📝 Reports":
        show_reports_page()
    elif page == "⚙️ Database Management":
        show_database_management()


def show_home_page():
    """Display home page."""
    st.title("PV Testing Protocol Framework")
    st.markdown(
        """
    ## Welcome to the Test Protocol Framework

    This framework provides a comprehensive solution for managing and executing
    photovoltaic module testing protocols according to international standards.

    ### Features

    - **Protocol Management**: Define test protocols using JSON templates
    - **Data Collection**: Automated data collection and validation
    - **Quality Control**: Real-time QC checks and outlier detection
    - **Analysis**: Statistical analysis and visualization
    - **Reporting**: Automated report generation in multiple formats

    ### Available Protocols
    """
    )

    # List available protocols
    loader = st.session_state.protocol_loader
    protocols = loader.list_protocols()

    if protocols:
        cols = st.columns(len(protocols))
        for idx, protocol in enumerate(protocols):
            with cols[idx]:
                st.metric(
                    label=protocol["name"],
                    value=f"v{protocol['version']}",
                )
                st.caption(protocol.get("description", "")[:100])
    else:
        st.info("No protocols found. Please add protocol definitions to src/protocols/")

    st.markdown("---")
    st.markdown("### Quick Start")
    st.markdown(
        """
    1. Select **Protocol Runner** from the sidebar
    2. Choose a protocol to execute
    3. Enter test parameters
    4. Start the test and monitor progress
    5. View results and generate reports
    """
    )


def show_protocol_runner():
    """Display protocol runner page."""
    st.title("Protocol Runner")

    loader = st.session_state.protocol_loader
    protocols = loader.list_protocols()

    if not protocols:
        st.warning("No protocols available. Please add protocol definitions.")
        return

    # Protocol selection
    protocol_options = {p["name"]: p["id"] for p in protocols}
    selected_name = st.selectbox("Select Protocol", list(protocol_options.keys()))

    if selected_name:
        protocol_id = protocol_options[selected_name]

        try:
            protocol = loader.load_protocol(protocol_id)
            st.session_state.current_protocol = protocol

            # Display protocol info
            protocol_info = protocol["protocol"]

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Protocol Code", protocol_info.get("code", "N/A"))
            with col2:
                st.metric("Category", protocol_info.get("category", "N/A"))
            with col3:
                st.metric("Standard", protocol_info.get("standard", "N/A"))

            st.markdown("---")
            st.subheader("Protocol Description")
            st.write(protocol_info.get("description", ""))

            # Display test phases
            st.markdown("---")
            st.subheader("Test Phases")
            phases = protocol_info.get("test_phases", [])

            for phase in phases:
                with st.expander(
                    f"Phase {phase['sequence']}: {phase['name']}", expanded=False
                ):
                    st.write(phase.get("description", ""))
                    if "duration_minutes" in phase:
                        st.caption(f"Duration: {phase['duration_minutes']} minutes")
                    if "duration_hours" in phase:
                        st.caption(f"Duration: {phase['duration_hours']} hours")

            # Parameter input form
            st.markdown("---")
            st.subheader("Test Parameters")

            # Get parameters from first phase (setup)
            first_phase = phases[0] if phases else {}
            parameters = first_phase.get("parameters", [])

            if parameters:
                with st.form("test_parameters"):
                    param_values = {}

                    for param in parameters:
                        param_id = param["param_id"]
                        param_name = param["name"]
                        param_type = param["type"]
                        required = param.get("required", False)

                        label = f"{param_name} {'*' if required else ''}"

                        if param_type == "float":
                            param_values[param_id] = st.number_input(
                                label,
                                value=float(param.get("default_value", 0.0)),
                                min_value=float(param.get("min_value", 0.0)),
                                max_value=float(param.get("max_value", 1000.0)),
                                step=0.1,
                                help=param.get("description", ""),
                            )
                        elif param_type == "integer":
                            param_values[param_id] = st.number_input(
                                label,
                                value=int(param.get("default_value", 0)),
                                min_value=int(param.get("min_value", 0)),
                                max_value=int(param.get("max_value", 100)),
                                step=1,
                                help=param.get("description", ""),
                            )
                        elif param_type == "string":
                            if "validation" in param and param["validation"].get("type") == "enum":
                                param_values[param_id] = st.selectbox(
                                    label,
                                    param["validation"]["values"],
                                    help=param.get("description", ""),
                                )
                            else:
                                param_values[param_id] = st.text_input(
                                    label,
                                    value=param.get("default_value", ""),
                                    help=param.get("description", ""),
                                )
                        elif param_type == "boolean":
                            param_values[param_id] = st.checkbox(
                                label,
                                value=param.get("default_value", False),
                                help=param.get("description", ""),
                            )

                    submitted = st.form_submit_button("Start Test Run")

                    if submitted:
                        st.success("Test parameters validated successfully!")
                        st.session_state.test_parameters = param_values
                        st.info("Test execution feature coming soon!")

        except Exception as e:
            st.error(f"Error loading protocol: {e}")


def show_data_viewer():
    """Display data viewer page."""
    st.title("Data Viewer")
    st.info("Data viewer feature coming soon!")


def show_analysis_page():
    """Display analysis and results page."""
    st.title("Analysis & Results")
    st.info("Analysis feature coming soon!")


def show_reports_page():
    """Display reports page."""
    st.title("Reports")
    st.info("Report generation feature coming soon!")


def show_database_management():
    """Display database management page."""
    st.title("Database Management")

    db_manager = st.session_state.db_manager
    schema_manager = SchemaManager(db_manager)

    # Verify schema
    st.subheader("Database Schema Status")
    schema_status = schema_manager.verify_schema()

    status_df = []
    for table, exists in schema_status.items():
        status_df.append(
            {"Table": table, "Status": "✅ Exists" if exists else "❌ Missing"}
        )

    import pandas as pd

    st.dataframe(pd.DataFrame(status_df), use_container_width=True)

    # Database stats
    st.markdown("---")
    st.subheader("Database Statistics")

    try:
        stats = schema_manager.get_database_stats()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Protocols", stats.get("protocols_count", 0))
            st.metric("Test Runs", stats.get("test_runs_count", 0))
        with col2:
            st.metric("Measurements", stats.get("measurements_count", 0))
            st.metric("QC Flags", stats.get("qc_flags_count", 0))
        with col3:
            st.metric("Reports", stats.get("test_reports_count", 0))
            st.metric("Equipment", stats.get("equipment_count", 0))
    except Exception as e:
        st.error(f"Error getting database stats: {e}")

    # Maintenance actions
    st.markdown("---")
    st.subheader("Database Maintenance")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Initialize Database"):
            try:
                db_manager.init_db()
                st.success("Database initialized successfully!")
            except Exception as e:
                st.error(f"Error initializing database: {e}")

    with col2:
        if st.button("⚠️ Drop All Tables", type="secondary"):
            st.warning("This will delete all data! Use with caution.")


if __name__ == "__main__":
    main()
