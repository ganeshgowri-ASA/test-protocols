"""Protocol selection component."""

import streamlit as st


def render_protocol_selector():
    """Render protocol selection interface."""
    st.title("Protocol Selection")
    st.markdown("Select a test protocol to begin testing.")

    protocol_manager = st.session_state.protocol_manager
    protocols = protocol_manager.list_protocols()

    if not protocols:
        st.error(
            "No protocols found. Please ensure protocol definitions "
            "are available in the protocols/ directory."
        )
        return

    # Protocol selection
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Available Protocols")

        selected_protocol = st.selectbox(
            "Select Protocol",
            protocols,
            format_func=lambda x: x.upper()
        )

        if st.button("Load Protocol", type="primary"):
            st.session_state.current_protocol = selected_protocol
            st.success(f"Protocol {selected_protocol.upper()} loaded successfully!")

    with col2:
        if selected_protocol:
            st.subheader("Protocol Details")

            metadata = protocol_manager.get_protocol_metadata(selected_protocol)

            if metadata:
                st.markdown(f"**Name:** {metadata.get('name', 'N/A')}")
                st.markdown(f"**Version:** {metadata.get('version', 'N/A')}")
                st.markdown(f"**Description:** {metadata.get('description', 'N/A')}")

                with st.expander("Additional Information"):
                    protocol_metadata = metadata.get('metadata', {})

                    st.markdown(f"**Category:** {protocol_metadata.get('category', 'N/A')}")
                    st.markdown(f"**Estimated Duration:** {protocol_metadata.get('estimated_duration_hours', 'N/A')} hours")

                    equipment = protocol_metadata.get('equipment_required', [])
                    if equipment:
                        st.markdown("**Equipment Required:**")
                        for item in equipment:
                            st.markdown(f"- {item.replace('_', ' ').title()}")

                    safety = protocol_metadata.get('safety_requirements', [])
                    if safety:
                        st.markdown("**Safety Requirements:**")
                        for item in safety:
                            st.markdown(f"- {item}")

                # QC Criteria
                with st.expander("Quality Control Criteria"):
                    qc_criteria = protocol_manager.get_qc_criteria(selected_protocol)

                    if qc_criteria:
                        for criterion_name, criterion_spec in qc_criteria.items():
                            st.markdown(f"**{criterion_name.replace('_', ' ').title()}**")
                            st.markdown(f"- {criterion_spec.get('description', 'N/A')}")

                            # Display specific values
                            for key, value in criterion_spec.items():
                                if key != 'description':
                                    st.markdown(f"  - {key}: {value}")

    # Current protocol status
    if st.session_state.current_protocol:
        st.markdown("---")
        st.info(f"**Currently Loaded Protocol:** {st.session_state.current_protocol.upper()}")
