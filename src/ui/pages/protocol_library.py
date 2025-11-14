"""
Protocol Library Page
"""

import streamlit as st
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.models import SessionLocal, Protocol, ProtocolVersion


def render_protocol_library():
    """Render the protocol library page"""
    st.title("📚 Protocol Library")

    db = SessionLocal()

    try:
        protocols = db.query(Protocol).filter(Protocol.is_active == True).all()

        if not protocols:
            st.info("No protocols available. Protocols are loaded automatically when tests are executed.")
            return

        # Protocol selection
        protocol_options = {p.id: f"{p.protocol_id} - {p.protocol_name}" for p in protocols}

        selected_protocol_id = st.selectbox(
            "Select Protocol",
            options=list(protocol_options.keys()),
            format_func=lambda x: protocol_options[x]
        )

        protocol = db.query(Protocol).filter(Protocol.id == selected_protocol_id).first()

        if not protocol:
            st.error("Protocol not found")
            return

        # Protocol overview
        st.header("Protocol Overview")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Protocol ID", protocol.protocol_id)
            st.metric("Category", protocol.category)

        with col2:
            st.metric("Standard", protocol.standard_name)
            st.metric("Section", protocol.standard_section)

        with col3:
            if protocol.standard_edition:
                st.metric("Edition", protocol.standard_edition)
            total_executions = len(protocol.test_executions)
            st.metric("Total Executions", total_executions)

        # Description
        if protocol.description:
            st.subheader("Description")
            st.write(protocol.description)

        # Get current version
        current_version = db.query(ProtocolVersion).filter(
            ProtocolVersion.protocol_id == protocol.id,
            ProtocolVersion.is_current == True
        ).first()

        if current_version:
            st.subheader(f"Current Version: {current_version.version}")

            json_def = current_version.json_definition

            # Parameters
            if 'parameters' in json_def:
                with st.expander("Parameters", expanded=True):
                    import pandas as pd

                    params_data = []
                    for param_name, param_config in json_def['parameters'].items():
                        params_data.append({
                            'Parameter': param_name,
                            'Type': param_config.get('type', 'N/A'),
                            'Value': param_config.get('value', 'N/A'),
                            'Unit': param_config.get('unit', 'N/A'),
                            'Description': param_config.get('description', 'N/A')
                        })

                    df = pd.DataFrame(params_data)
                    st.dataframe(df, use_container_width=True)

            # Measurements
            if 'measurements' in json_def:
                with st.expander("Measurements"):
                    import pandas as pd

                    meas_data = []
                    for meas in json_def['measurements']:
                        meas_data.append({
                            'Name': meas.get('name', 'N/A'),
                            'Type': meas.get('type', 'N/A'),
                            'Unit': meas.get('unit', 'N/A'),
                            'Description': meas.get('description', 'N/A')
                        })

                    df = pd.DataFrame(meas_data)
                    st.dataframe(df, use_container_width=True)

            # Pass Criteria
            if 'pass_criteria' in json_def:
                with st.expander("Pass/Fail Criteria"):
                    for idx, criterion in enumerate(json_def['pass_criteria'], 1):
                        st.write(f"**{idx}. {criterion.get('description', 'N/A')}**")
                        st.code(criterion.get('condition', 'N/A'))
                        st.caption(f"Severity: {criterion.get('severity', 'N/A')}")
                        st.markdown("---")

            # Safety Limits
            if 'safety_limits' in json_def:
                with st.expander("Safety Limits"):
                    import pandas as pd

                    safety_data = []
                    for limit_name, limit_config in json_def['safety_limits'].items():
                        safety_data.append({
                            'Limit': limit_name,
                            'Value': limit_config.get('value', 'N/A'),
                            'Action': limit_config.get('action', 'N/A'),
                            'Description': limit_config.get('description', 'N/A')
                        })

                    df = pd.DataFrame(safety_data)
                    st.dataframe(df, use_container_width=True)

            # Equipment
            if 'equipment' in json_def:
                with st.expander("Required Equipment"):
                    for idx, eq in enumerate(json_def['equipment'], 1):
                        st.write(f"**{idx}. {eq.get('name', 'N/A')}**")
                        st.write(f"Type: {eq.get('type', 'N/A')}")
                        if 'specifications' in eq:
                            st.json(eq['specifications'])
                        st.write(f"Calibration Required: {'Yes' if eq.get('calibration_required', True) else 'No'}")
                        st.markdown("---")

            # Procedure
            if 'procedure' in json_def:
                with st.expander("Test Procedure"):
                    for step in json_def['procedure']:
                        step_num = step.get('step', 'N/A')
                        action = step.get('action', 'N/A')
                        expected = step.get('expected_result', '')
                        safety = step.get('safety_note', '')

                        st.write(f"**Step {step_num}:** {action}")
                        if expected:
                            st.caption(f"Expected: {expected}")
                        if safety:
                            st.warning(f"⚠️ Safety: {safety}")
                        st.markdown("---")

            # Raw JSON
            with st.expander("Raw JSON Definition"):
                st.json(json_def)

    finally:
        db.close()
