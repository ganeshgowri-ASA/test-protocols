"""Protocols page for browsing and managing test protocols."""

import streamlit as st
from pathlib import Path
import json

from src.models.base import get_session
from src.models import Protocol
from src.parsers import ProtocolLoader


def render_protocols_page():
    """Render the protocols page."""
    st.title("📋 Test Protocols")
    st.markdown("Browse and manage test protocol definitions")

    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["Browse Protocols", "Upload Protocol", "Protocol Details"])

    with tab1:
        render_browse_protocols()

    with tab2:
        render_upload_protocol()

    with tab3:
        render_protocol_details()


def render_browse_protocols():
    """Render the browse protocols section."""
    st.subheader("Available Protocols")

    # Filter options
    col1, col2 = st.columns(2)

    with col1:
        category_filter = st.selectbox(
            "Filter by Category",
            ["All", "Mechanical", "Electrical", "Environmental", "Optical", "Safety"]
        )

    with col2:
        search_term = st.text_input("Search protocols", placeholder="Enter protocol ID or name...")

    # Get protocols from database
    session = get_session(st.session_state.engine)

    if category_filter == "All":
        protocols = ProtocolLoader.list_protocols(session)
    else:
        protocols = ProtocolLoader.list_protocols(session, category=category_filter)

    # Apply search filter
    if search_term:
        protocols = [
            p for p in protocols
            if search_term.lower() in p.protocol_id.lower() or
               search_term.lower() in p.protocol_name.lower()
        ]

    # Display protocols
    if protocols:
        st.markdown(f"**Found {len(protocols)} protocol(s)**")
        st.markdown("---")

        for protocol in protocols:
            with st.expander(f"{protocol.protocol_id} - {protocol.protocol_name}"):
                col1, col2, col3 = st.columns([2, 2, 1])

                with col1:
                    st.markdown(f"**Version:** {protocol.version}")
                    st.markdown(f"**Category:** {protocol.category}")

                with col2:
                    st.markdown(f"**Author:** {protocol.author or 'N/A'}")
                    if protocol.tags:
                        st.markdown(f"**Tags:** {protocol.tags}")

                with col3:
                    if st.button("View Details", key=f"view_{protocol.id}"):
                        st.session_state.selected_protocol_id = protocol.id
                        st.rerun()

                st.markdown(f"**Description:** {protocol.description}")

                # Show quick stats
                protocol_data = protocol.protocol_data
                col_a, col_b, col_c = st.columns(3)

                with col_a:
                    st.metric("Test Steps", len(protocol_data.get("test_steps", [])))

                with col_b:
                    st.metric("Measurements", len(protocol_data.get("data_collection", {}).get("measurements", [])))

                with col_c:
                    st.metric("Acceptance Criteria", len(protocol_data.get("acceptance_criteria", [])))

    else:
        st.info("No protocols found. Upload a protocol to get started.")

    session.close()


def render_upload_protocol():
    """Render the upload protocol section."""
    st.subheader("Upload New Protocol")

    st.markdown("""
    Upload a JSON protocol file to add it to the database. The protocol will be validated
    against the schema before being imported.
    """)

    uploaded_file = st.file_uploader("Choose a JSON protocol file", type=["json"])

    if uploaded_file is not None:
        try:
            # Read and parse the JSON file
            protocol_data = json.load(uploaded_file)

            # Display preview
            st.success("File loaded successfully!")
            st.json(protocol_data)

            # Validate and import
            if st.button("Validate and Import"):
                with st.spinner("Validating protocol..."):
                    loader = ProtocolLoader()

                    try:
                        # Validate
                        loader.validate_protocol(protocol_data)
                        st.success("✓ Protocol validation passed!")

                        # Import to database
                        session = get_session(st.session_state.engine)
                        protocol = loader.import_to_database(protocol_data, session)
                        session.close()

                        st.success(f"✓ Protocol imported: {protocol.protocol_id} - {protocol.protocol_name}")

                    except Exception as e:
                        st.error(f"Validation failed: {e}")

        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON file: {e}")


def render_protocol_details():
    """Render the protocol details section."""
    st.subheader("Protocol Details")

    # Check if a protocol is selected
    if "selected_protocol_id" not in st.session_state:
        st.info("Select a protocol from the Browse Protocols tab to view details.")
        return

    # Get protocol from database
    session = get_session(st.session_state.engine)
    protocol = session.query(Protocol).filter_by(id=st.session_state.selected_protocol_id).first()

    if not protocol:
        st.error("Protocol not found.")
        session.close()
        return

    # Display protocol information
    st.markdown(f"## {protocol.protocol_id} - {protocol.protocol_name}")
    st.markdown(f"**Version:** {protocol.version} | **Category:** {protocol.category}")

    if st.button("← Back to Browse"):
        del st.session_state.selected_protocol_id
        st.rerun()

    st.markdown("---")

    # Create tabs for different sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Overview",
        "Test Steps",
        "Measurements",
        "Acceptance Criteria",
        "Equipment"
    ])

    protocol_data = protocol.protocol_data

    with tab1:
        render_protocol_overview(protocol_data)

    with tab2:
        render_test_steps(protocol_data)

    with tab3:
        render_measurements(protocol_data)

    with tab4:
        render_acceptance_criteria(protocol_data)

    with tab5:
        render_equipment(protocol_data)

    session.close()


def render_protocol_overview(protocol_data):
    """Render protocol overview."""
    st.markdown("### Overview")
    st.markdown(protocol_data.get("description", ""))

    st.markdown("### Standard References")
    for ref in protocol_data.get("standard_reference", []):
        st.markdown(f"- **{ref['standard']}**: {ref.get('section', 'N/A')}")

    st.markdown("### Test Parameters")

    # Specimen requirements
    specimen = protocol_data.get("test_parameters", {}).get("specimen_requirements", {})
    st.markdown(f"**Specimen Requirements:** {specimen.get('quantity', 'N/A')} - {specimen.get('description', 'N/A')}")

    # Environmental conditions
    env = protocol_data.get("test_parameters", {}).get("environmental_conditions", {})
    if env:
        st.markdown("**Environmental Conditions:**")
        if "temperature_range" in env:
            temp = env["temperature_range"]
            st.markdown(f"- Temperature: {temp.get('min', 'N/A')} to {temp.get('max', 'N/A')} {temp.get('unit', '°C')}")
        if "humidity_range" in env:
            hum = env["humidity_range"]
            st.markdown(f"- Humidity: {hum.get('min', 'N/A')} to {hum.get('max', 'N/A')} {hum.get('unit', '%RH')}")

    # Safety requirements
    safety = protocol_data.get("safety_requirements", [])
    if safety:
        st.markdown("### Safety Requirements")
        for req in safety:
            st.markdown(f"⚠️ {req}")


def render_test_steps(protocol_data):
    """Render test steps."""
    st.markdown("### Test Steps")

    steps = protocol_data.get("test_steps", [])

    for step in steps:
        with st.expander(f"Step {step['step_number']}: {step['description']}"):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**Action:** {step['action']}")
                if "duration" in step:
                    duration = step["duration"]
                    st.markdown(f"**Duration:** {duration.get('value', 'N/A')} {duration.get('unit', '')}")

            with col2:
                st.markdown(f"**Automation:** {'Yes' if step.get('automation_capable', False) else 'No'}")

            if "parameters" in step:
                st.markdown("**Parameters:**")
                st.json(step["parameters"])


def render_measurements(protocol_data):
    """Render measurements."""
    st.markdown("### Data Collection")

    measurements = protocol_data.get("data_collection", {}).get("measurements", [])

    if measurements:
        # Create a table
        import pandas as pd

        df = pd.DataFrame([
            {
                "ID": m.get("measurement_id"),
                "Parameter": m.get("parameter"),
                "Unit": m.get("unit"),
                "Instrument": m.get("instrument", "N/A"),
                "Accuracy": m.get("accuracy", "N/A"),
                "Type": m.get("data_type", "N/A")
            }
            for m in measurements
        ])

        st.dataframe(df, use_container_width=True)
    else:
        st.info("No measurements defined.")


def render_acceptance_criteria(protocol_data):
    """Render acceptance criteria."""
    st.markdown("### Acceptance Criteria")

    criteria = protocol_data.get("acceptance_criteria", [])

    for criterion in criteria:
        with st.expander(f"{criterion['criterion_id']}: {criterion['description']}"):
            st.markdown(f"**Evaluation Method:** {criterion['evaluation_method']}")

            if "threshold" in criterion:
                threshold = criterion["threshold"]
                st.markdown("**Threshold:**")
                st.json(threshold)


def render_equipment(protocol_data):
    """Render equipment requirements."""
    st.markdown("### Required Equipment")

    equipment = protocol_data.get("equipment", [])

    if equipment:
        for item in equipment:
            with st.expander(f"{item.get('name', 'Unknown')}"):
                st.markdown(f"**Specifications:** {item.get('specifications', 'N/A')}")
                st.markdown(f"**Quantity:** {item.get('quantity', 1)}")
    else:
        st.info("No equipment requirements defined.")
