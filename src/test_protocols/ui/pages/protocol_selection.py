"""Protocol selection page."""

import streamlit as st
from ...core.protocol_loader import ProtocolLoader


def show_protocol_selection_page():
    """Display protocol selection page."""
    st.title("Protocol Selection")
    st.write("Select and configure a test protocol.")

    loader = ProtocolLoader()

    try:
        # List available protocols
        protocols = loader.list_protocols()

        if not protocols:
            st.warning("No protocols found. Please add protocol JSON files to the protocols directory.")
            return

        # Protocol selection
        col1, col2 = st.columns([1, 2])

        with col1:
            selected_protocol = st.selectbox(
                "Select Protocol",
                protocols,
                format_func=lambda x: x,
            )

        if selected_protocol:
            # Load protocol information
            protocol_info = loader.get_protocol_info(selected_protocol)

            with col2:
                st.subheader(protocol_info["name"])
                st.write(f"**Version**: {protocol_info['version']}")
                st.write(f"**Category**: {protocol_info['category']}")

            # Display protocol details
            st.markdown("---")

            tab1, tab2, tab3, tab4 = st.tabs(
                ["Overview", "Test Conditions", "Parameters", "Quality Checks"]
            )

            # Load full protocol configuration
            protocol_config = loader.load_protocol(selected_protocol)

            with tab1:
                st.subheader("Description")
                st.write(protocol_info["description"])

                st.subheader("Standards")
                for standard in protocol_info.get("standards", []):
                    st.write(f"- {standard}")

                st.subheader("Equipment Required")
                metadata = protocol_config.get("metadata", {})
                for equipment in metadata.get("equipment_required", []):
                    st.write(f"- {equipment}")

            with tab2:
                st.subheader("Test Conditions")
                test_conditions = protocol_config.get("test_conditions", {})

                for key, value in test_conditions.items():
                    with st.expander(key.replace("_", " ").title()):
                        if isinstance(value, dict):
                            for k, v in value.items():
                                st.write(f"**{k}**: {v}")
                        else:
                            st.write(value)

            with tab3:
                st.subheader("Parameters")
                parameters = protocol_config.get("parameters", [])

                for param in parameters:
                    with st.expander(f"{param['name']} ({param['id']})"):
                        st.write(f"**Type**: {param['type']}")
                        st.write(f"**Unit**: {param['unit']}")
                        st.write(f"**Required**: {'Yes' if param.get('required') else 'No'}")

                        if "description" in param:
                            st.write(f"**Description**: {param['description']}")

                        if "validation" in param:
                            st.write("**Validation**:")
                            for k, v in param["validation"].items():
                                st.write(f"  - {k}: {v}")

            with tab4:
                st.subheader("Quality Checks")
                quality_checks = protocol_config.get("quality_checks", [])

                for qc in quality_checks:
                    severity_color = {
                        "error": "🔴",
                        "warning": "🟡",
                        "info": "🔵",
                    }.get(qc.get("severity", "info"), "⚪")

                    with st.expander(f"{severity_color} {qc['name']}"):
                        st.write(f"**ID**: {qc['id']}")
                        st.write(f"**Type**: {qc['type']}")
                        st.write(f"**Severity**: {qc.get('severity', 'warning')}")

                        if "description" in qc:
                            st.write(f"**Description**: {qc['description']}")

                        if "condition" in qc:
                            st.write(f"**Condition**: {qc['condition']}")

            # Store selected protocol in session state
            if st.button("Use This Protocol", type="primary"):
                st.session_state["selected_protocol"] = selected_protocol
                st.success(f"Protocol {selected_protocol} selected! Go to 'Test Execution' to run the test.")

    except Exception as e:
        st.error(f"Error loading protocols: {e}")
        st.exception(e)


if __name__ == "__main__":
    show_protocol_selection_page()
