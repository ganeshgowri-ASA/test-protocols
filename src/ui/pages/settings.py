"""Settings page for application configuration."""

import streamlit as st
from pathlib import Path

from src.models.base import get_session, init_db
from src.parsers import ProtocolLoader


def render_settings_page():
    """Render the settings page."""
    st.title("⚙️ Settings")
    st.markdown("Configure application settings and manage data")

    # Tabs for different settings
    tab1, tab2, tab3 = st.tabs(["Database", "Protocol Management", "About"])

    with tab1:
        render_database_settings()

    with tab2:
        render_protocol_management()

    with tab3:
        render_about()


def render_database_settings():
    """Render database settings."""
    st.subheader("Database Management")

    st.markdown("""
    The application uses SQLite for data storage. The database file is located at
    `test_protocols.db` in the project root directory.
    """)

    # Database statistics
    session = get_session(st.session_state.engine)

    from src.models import Protocol, TestRun

    protocol_count = session.query(Protocol).count()
    test_run_count = session.query(TestRun).count()

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Protocols in Database", protocol_count)

    with col2:
        st.metric("Test Runs in Database", test_run_count)

    session.close()

    st.markdown("---")

    # Database actions
    st.markdown("### Database Actions")

    st.warning("⚠️ The following actions can modify or delete data. Use with caution!")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Initialize Database Schema", help="Create or update database tables"):
            init_db(st.session_state.engine)
            st.success("Database schema initialized successfully!")

    with col2:
        if st.button("Clear All Test Data", help="Delete all test runs (protocols preserved)"):
            if st.checkbox("I understand this will delete all test data"):
                session = get_session(st.session_state.engine)
                session.query(TestRun).delete()
                session.commit()
                session.close()
                st.success("All test data cleared.")
                st.rerun()


def render_protocol_management():
    """Render protocol management settings."""
    st.subheader("Protocol Management")

    st.markdown("""
    Manage protocol definitions and bulk operations.
    """)

    # Load protocols from directory
    st.markdown("### Bulk Import Protocols")

    st.markdown("""
    Import all JSON protocol files from the `protocols/` directory into the database.
    """)

    protocols_dir = Path(__file__).parent.parent.parent.parent / "protocols"

    if st.button("Scan and Import Protocols"):
        with st.spinner("Scanning for protocol files..."):
            loader = ProtocolLoader()
            session = get_session(st.session_state.engine)

            imported_count = 0
            error_count = 0

            # Find all JSON files
            for json_file in protocols_dir.rglob("*.json"):
                try:
                    protocol_data = loader.load_and_validate(json_file)
                    loader.import_to_database(protocol_data, session)
                    st.success(f"✓ Imported: {protocol_data['protocol_id']} - {protocol_data['protocol_name']}")
                    imported_count += 1
                except Exception as e:
                    st.error(f"✗ Error loading {json_file.name}: {e}")
                    error_count += 1

            session.close()

            st.info(f"Import complete: {imported_count} protocols imported, {error_count} errors")

    # Export protocols
    st.markdown("---")
    st.markdown("### Export Protocols")

    session = get_session(st.session_state.engine)
    protocols = ProtocolLoader.list_protocols(session)

    if protocols:
        protocol_options = {f"{p.protocol_id} - {p.protocol_name}": p for p in protocols}
        selected_protocol_name = st.selectbox("Select protocol to export", list(protocol_options.keys()))

        if selected_protocol_name:
            selected_protocol = protocol_options[selected_protocol_name]

            import json

            json_str = json.dumps(selected_protocol.protocol_data, indent=2)

            st.download_button(
                label="Download Protocol JSON",
                data=json_str,
                file_name=f"{selected_protocol.protocol_id}.json",
                mime="application/json"
            )

    session.close()


def render_about():
    """Render about section."""
    st.subheader("About PV Testing Protocol Framework")

    st.markdown("""
    ### Version
    **1.0.0**

    ### Description
    The PV Testing Protocol Framework is a modular system for defining, executing, and analyzing
    photovoltaic module testing protocols. It provides:

    - **Dynamic Protocol Definition**: JSON-based test protocol templates
    - **Automated Test Execution**: Streamlined test running and data collection
    - **Real-time Monitoring**: Track test progress and results
    - **Comprehensive Analytics**: Analyze test results and trends
    - **Quality Control**: Automated acceptance criteria evaluation
    - **Professional Reporting**: Generate test reports and documentation

    ### Technology Stack
    - **Backend**: Python, SQLAlchemy
    - **Frontend**: Streamlit
    - **Database**: SQLite
    - **Data Visualization**: Plotly, Pandas

    ### Standards Compliance
    This framework supports protocols based on:
    - IEC 61215 (Terrestrial PV modules - Design qualification and type approval)
    - IEC 61730 (PV module safety qualification)
    - IEC 62716 (Ammonia corrosion testing)
    - And other industry standards

    ### Support
    For issues, questions, or contributions, please visit the project repository.

    ### License
    MIT License

    ---

    **Developed for PV Testing and Quality Assurance**
    """)

    # System information
    st.markdown("### System Information")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Database Location**")
        st.code("test_protocols.db")

    with col2:
        st.markdown("**Schema Version**")
        st.code("1.0.0")
