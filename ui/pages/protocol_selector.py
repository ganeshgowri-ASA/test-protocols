"""Protocol Selector UI Component"""

import streamlit as st
import json
from pathlib import Path


def render_protocol_selector():
    """Render the protocol selector interface"""

    st.markdown("### Select a Test Protocol")

    # Load available protocols
    protocols_dir = Path(__file__).parent.parent.parent / "protocols" / "templates"

    available_protocols = []

    if protocols_dir.exists():
        for protocol_dir in protocols_dir.iterdir():
            if protocol_dir.is_dir():
                protocol_file = protocol_dir / "protocol.json"
                if protocol_file.exists():
                    try:
                        with open(protocol_file, "r") as f:
                            protocol_def = json.load(f)
                            available_protocols.append(protocol_def)
                    except Exception as e:
                        st.error(f"Error loading protocol from {protocol_file}: {e}")

    if not available_protocols:
        st.warning("No protocols found in the templates directory.")
        return

    # Display protocol cards
    for protocol in available_protocols:
        with st.expander(f"📋 {protocol.get('name', 'Unknown')} ({protocol.get('protocol_id', 'N/A')})"):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"**Version:** {protocol.get('version', 'N/A')}")
                st.markdown(f"**Category:** {protocol.get('category', 'N/A')}")
                st.markdown(f"**Description:**")
                st.markdown(protocol.get('description', 'No description available'))

                # Display reference standards
                if 'reference_standards' in protocol:
                    st.markdown("**Reference Standards:**")
                    for std in protocol['reference_standards']:
                        st.markdown(f"- {std}")

            with col2:
                if st.button("Select", key=f"select_{protocol.get('protocol_id')}"):
                    st.session_state['selected_protocol'] = protocol
                    st.success(f"Selected: {protocol.get('name')}")
                    st.rerun()

    # Display selected protocol details
    if 'selected_protocol' in st.session_state:
        st.markdown("---")
        st.markdown("### Selected Protocol Details")

        protocol = st.session_state['selected_protocol']

        # Test parameters
        st.markdown("#### Test Parameters")
        params = protocol.get('test_parameters', {})

        for param_category, param_dict in params.items():
            st.markdown(f"**{param_category.replace('_', ' ').title()}:**")
            for param_name, param_spec in param_dict.items():
                if isinstance(param_spec, dict):
                    st.markdown(f"- {param_spec.get('name', param_name)}: {param_spec.get('description', '')}")

        # Test steps
        st.markdown("#### Test Steps")
        steps = protocol.get('test_steps', [])
        for step in steps:
            st.markdown(f"**Step {step.get('step_number', '?')}: {step.get('name', 'Unnamed')}**")
            st.markdown(f"Duration: {step.get('duration_minutes', '?')} minutes")

        # Navigation button
        if st.button("Proceed to Test Execution", type="primary"):
            st.switch_page("pages/test_execution.py")
