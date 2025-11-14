"""
Protocol Selector Component

Streamlit component for selecting and displaying protocols.
"""

import streamlit as st
from typing import Optional, Dict, Any
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import ProtocolLoader


class ProtocolSelector:
    """Protocol selection component."""

    def __init__(self, loader: Optional[ProtocolLoader] = None):
        """
        Initialize the ProtocolSelector.

        Args:
            loader: ProtocolLoader instance
        """
        self.loader = loader or ProtocolLoader()

    def render(self) -> Optional[Dict[str, Any]]:
        """
        Render the protocol selector.

        Returns:
            Selected protocol or None
        """
        st.subheader("Select Protocol")

        # Get available protocols
        protocols = self.loader.list_protocols()

        if not protocols:
            st.warning("No protocols found in the system.")
            return None

        # Create protocol selection options
        protocol_options = {
            f"{p['protocol_id']} - {p['name']} (v{p['version']})": p
            for p in protocols
        }

        # Selection dropdown
        selected_key = st.selectbox(
            "Protocol",
            options=list(protocol_options.keys()),
            key="protocol_selector"
        )

        if selected_key:
            selected_protocol_info = protocol_options[selected_key]

            # Display protocol information
            with st.expander("Protocol Details", expanded=False):
                col1, col2 = st.columns(2)

                with col1:
                    st.write("**Protocol ID:**", selected_protocol_info['protocol_id'])
                    st.write("**Version:**", selected_protocol_info['version'])
                    st.write("**Category:**", selected_protocol_info['category'])

                with col2:
                    if selected_protocol_info.get('subcategory'):
                        st.write("**Subcategory:**", selected_protocol_info['subcategory'])

            # Load full protocol
            protocol = self.loader.load_protocol(selected_protocol_info['protocol_id'])

            # Display metadata
            if 'metadata' in protocol:
                metadata = protocol['metadata']
                if metadata.get('description'):
                    st.info(metadata['description'])

                if metadata.get('estimated_duration_hours'):
                    st.caption(
                        f"⏱️ Estimated Duration: {metadata['estimated_duration_hours']} hours"
                    )

            return protocol

        return None

    def render_protocol_info(self, protocol: Dict[str, Any]):
        """
        Render detailed protocol information.

        Args:
            protocol: Protocol definition
        """
        st.subheader("Protocol Information")

        # Basic info
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Protocol ID", protocol['protocol_id'])

        with col2:
            st.metric("Version", protocol['version'])

        with col3:
            st.metric("Category", protocol['category'])

        # Metadata
        if 'metadata' in protocol:
            with st.expander("Metadata", expanded=False):
                metadata = protocol['metadata']
                for key, value in metadata.items():
                    st.write(f"**{key.replace('_', ' ').title()}:** {value}")

        # Test parameters
        if 'test_parameters' in protocol:
            with st.expander("Test Parameters", expanded=True):
                params = protocol['test_parameters']
                for param_id, param_config in params.items():
                    if isinstance(param_config, dict):
                        value = param_config.get('value')
                        unit = param_config.get('unit', '')
                        description = param_config.get('description', '')

                        st.write(f"**{param_id.replace('_', ' ').title()}:** {value} {unit}")
                        if description:
                            st.caption(description)
                    else:
                        st.write(f"**{param_id.replace('_', ' ').title()}:** {param_config}")

        # Equipment requirements
        if 'equipment_requirements' in protocol:
            with st.expander("Equipment Requirements", expanded=False):
                equipment = protocol['equipment_requirements']
                for equip in equipment:
                    st.write(f"**{equip['name']}** ({equip['equipment_id']})")
                    if equip.get('calibration_required'):
                        st.caption(
                            f"⚠️ Calibration required every "
                            f"{equip.get('calibration_interval_months', 'N/A')} months"
                        )

        # Test sequence overview
        if 'test_sequence' in protocol:
            with st.expander("Test Sequence", expanded=False):
                steps = protocol['test_sequence'].get('steps', [])
                for step in steps:
                    st.write(
                        f"**Step {step['step_id']}: {step['name']}** "
                        f"({step['type']}, {step.get('duration_hours', 'N/A')} hours)"
                    )
                    st.caption(step.get('description', ''))

        # Safety requirements
        if 'safety_requirements' in protocol:
            with st.expander("Safety Requirements", expanded=False):
                safety = protocol['safety_requirements']

                if 'hazards' in safety:
                    st.write("**Hazards:**")
                    for hazard in safety['hazards']:
                        st.warning(f"**{hazard['hazard']}** (Severity: {hazard['severity']})")

                if 'ppe_required' in safety:
                    st.write("**Required PPE:**")
                    for ppe in safety['ppe_required']:
                        st.write(f"- {ppe}")
