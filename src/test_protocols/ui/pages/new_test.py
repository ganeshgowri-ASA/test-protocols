"""New test creation page."""

from datetime import datetime

import streamlit as st

from test_protocols.database.connection import db
from test_protocols.models.schema import Protocol, TestRun
from test_protocols.protocols.registry import protocol_registry


def show():
    """Show new test creation page."""
    st.title("➕ Start New Test")
    st.markdown("Configure and start a new test protocol")
    st.markdown("---")

    # Protocol selection
    st.subheader("1. Select Protocol")

    available_protocols = protocol_registry.list_protocols()

    if not available_protocols:
        st.error("No protocols available. Please check protocol registry.")
        return

    selected_protocol = st.selectbox(
        "Protocol",
        options=available_protocols,
        format_func=lambda x: protocol_registry.get_protocol_info(x)["name"],
    )

    if selected_protocol:
        protocol_info = protocol_registry.get_protocol_info(selected_protocol)

        with st.expander("Protocol Information", expanded=True):
            st.write(f"**Code:** {protocol_info['code']}")
            st.write(f"**Name:** {protocol_info['name']}")
            st.write(f"**Version:** {protocol_info['version']}")
            st.write(f"**Category:** {protocol_info['category']}")
            st.write(f"**Standard:** {protocol_info['standard']}")
            st.write(f"**Description:** {protocol_info['description']}")

    st.markdown("---")

    # SALT-001 specific form
    if selected_protocol == "SALT-001":
        st.subheader("2. Test Parameters (SALT-001)")

        with st.form("salt_001_form"):
            # Specimen information
            col1, col2 = st.columns(2)

            with col1:
                specimen_id = st.text_input(
                    "Specimen/Module ID *",
                    placeholder="e.g., PV-MOD-2024-001",
                    help="Unique identifier for the test specimen",
                )

                module_type = st.selectbox(
                    "Module Type *",
                    options=[
                        "Crystalline Silicon",
                        "Thin Film",
                        "CIGS",
                        "CdTe",
                        "Perovskite",
                        "Other",
                    ],
                )

                manufacturer = st.text_input("Manufacturer", placeholder="Optional")

            with col2:
                rated_power = st.number_input(
                    "Rated Power (Wp)",
                    min_value=0.0,
                    max_value=1000.0,
                    value=None,
                    step=1.0,
                    help="Module rated power in watts-peak",
                )

                severity_level = st.selectbox(
                    "IEC 61701 Severity Level *",
                    options=[
                        "Level 1 - 60 hours",
                        "Level 2 - 120 hours",
                        "Level 3 - 240 hours",
                        "Level 4 - 480 hours",
                        "Level 5 - 840 hours",
                    ],
                    index=2,  # Default to Level 3
                )

                operator = st.text_input("Operator Name", placeholder="Optional")

            st.markdown("---")
            st.subheader("Environmental Parameters")

            col1, col2, col3 = st.columns(3)

            with col1:
                salt_concentration = st.number_input(
                    "Salt Concentration (% NaCl) *",
                    min_value=4.5,
                    max_value=5.5,
                    value=5.0,
                    step=0.1,
                    help="IEC 61701: 5.0 ± 0.5%",
                )

            with col2:
                chamber_temperature = st.number_input(
                    "Chamber Temperature (°C) *",
                    min_value=34.0,
                    max_value=36.0,
                    value=35.0,
                    step=0.1,
                    help="IEC 61701: 35 ± 1°C",
                )

            with col3:
                relative_humidity = st.number_input(
                    "Relative Humidity (%) *",
                    min_value=93.0,
                    max_value=97.0,
                    value=95.0,
                    step=0.5,
                    help="IEC 61701: 95 ± 2%",
                )

            st.markdown("---")
            st.subheader("Cycle Configuration")

            col1, col2 = st.columns(2)

            with col1:
                spray_duration = st.number_input(
                    "Spray Duration (hours) *",
                    min_value=1.0,
                    max_value=4.0,
                    value=2.0,
                    step=0.5,
                    help="Salt mist spray duration per cycle",
                )

            with col2:
                dry_duration = st.number_input(
                    "Dry Duration (hours) *",
                    min_value=20.0,
                    max_value=23.0,
                    value=22.0,
                    step=0.5,
                    help="Drying duration per cycle",
                )

            # Validation
            if spray_duration + dry_duration != 24.0:
                st.warning(
                    f"⚠️ Total cycle duration is {spray_duration + dry_duration} hours. "
                    f"Should be 24 hours."
                )

            st.markdown("---")
            st.subheader("Additional Notes")

            notes = st.text_area("Test Notes", placeholder="Optional notes about this test run")

            # Submit button
            submitted = st.form_submit_button("🚀 Start Test", type="primary", use_container_width=True)

            if submitted:
                # Validate required fields
                if not specimen_id:
                    st.error("❌ Specimen ID is required")
                    return

                if spray_duration + dry_duration != 24.0:
                    st.error("❌ Total cycle duration must equal 24 hours")
                    return

                # Create test run
                try:
                    protocol = protocol_registry.get_protocol(selected_protocol)

                    # Prepare parameters
                    parameters = {
                        "specimen_id": specimen_id,
                        "module_type": module_type,
                        "manufacturer": manufacturer,
                        "rated_power": rated_power,
                        "severity_level": severity_level,
                        "salt_concentration": salt_concentration,
                        "chamber_temperature": chamber_temperature,
                        "relative_humidity": relative_humidity,
                        "spray_duration": spray_duration,
                        "dry_duration": dry_duration,
                    }

                    # Execute protocol (initializes test)
                    results = protocol.execute(parameters)

                    # Save to database
                    with db.session_scope() as session:
                        test_run = TestRun(
                            protocol_code=selected_protocol,
                            specimen_id=specimen_id,
                            module_type=module_type,
                            manufacturer=manufacturer,
                            rated_power=rated_power,
                            status="running",
                            parameters=parameters,
                            raw_data={"results": results},
                            operator=operator,
                            notes=notes,
                        )
                        session.add(test_run)
                        session.commit()
                        test_run_id = test_run.id

                    st.success(f"✅ Test started successfully! Test Run ID: {test_run_id}")
                    st.balloons()

                    # Store test run ID in session state
                    st.session_state.active_test_id = test_run_id

                    # Show next steps
                    st.info(
                        "Test is now running. Go to 'Active Tests' to monitor progress and log measurements."
                    )

                except Exception as e:
                    st.error(f"❌ Failed to start test: {str(e)}")
