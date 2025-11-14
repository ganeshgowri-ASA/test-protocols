"""Protocol selector component."""

import streamlit as st
from pathlib import Path
import json
from typing import Optional, Dict, Any


class ProtocolSelector:
    """Component for selecting and displaying protocol information."""

    def __init__(self, protocols_path: Optional[str] = None):
        """
        Initialize protocol selector.

        Args:
            protocols_path: Path to protocols definitions directory
        """
        if protocols_path is None:
            protocols_path = Path(__file__).parent.parent.parent / "protocols" / "definitions"

        self.protocols_path = Path(protocols_path)
        self.available_protocols = self._load_available_protocols()

    def _load_available_protocols(self) -> Dict[str, Dict[str, Any]]:
        """Load all available protocol definitions."""
        protocols = {}

        if not self.protocols_path.exists():
            return protocols

        for protocol_file in self.protocols_path.glob("*.json"):
            try:
                with open(protocol_file, 'r') as f:
                    protocol_data = json.load(f)
                    protocol_id = protocol_data.get("protocol_id")
                    if protocol_id:
                        protocols[protocol_id] = protocol_data
            except Exception as e:
                st.error(f"Error loading protocol {protocol_file.name}: {e}")

        return protocols

    def render(self, key: str = "protocol_selector") -> Optional[str]:
        """
        Render the protocol selector.

        Args:
            key: Unique key for this component

        Returns:
            Selected protocol ID or None
        """
        if not self.available_protocols:
            st.warning("No protocols available. Please check the protocols directory.")
            return None

        # Create selection options
        protocol_options = {
            f"{pid} - {data.get('protocol_name', 'Unknown')}": pid
            for pid, data in self.available_protocols.items()
        }

        # Select protocol
        selected_label = st.selectbox(
            "Select Protocol",
            options=list(protocol_options.keys()),
            key=key
        )

        selected_id = protocol_options.get(selected_label)

        return selected_id

    def display_protocol_info(self, protocol_id: str) -> None:
        """
        Display detailed protocol information.

        Args:
            protocol_id: Protocol identifier
        """
        if protocol_id not in self.available_protocols:
            st.error(f"Protocol {protocol_id} not found")
            return

        protocol = self.available_protocols[protocol_id]

        # Header
        st.markdown(f"### {protocol.get('protocol_name', 'Unknown Protocol')}")

        # Basic info
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**Protocol ID**")
            st.info(protocol.get('protocol_id', 'N/A'))

        with col2:
            st.markdown("**Version**")
            st.info(protocol.get('version', 'N/A'))

        with col3:
            st.markdown("**Category**")
            st.info(protocol.get('category', 'N/A'))

        # Description
        st.markdown("**Description**")
        st.markdown(protocol.get('description', 'No description available'))

        # Standards
        standards = protocol.get('standards', [])
        if standards:
            st.markdown("**Standards**")
            for standard in standards:
                st.markdown(f"- {standard}")

        # Test parameters
        with st.expander("⚙️ Test Parameters", expanded=False):
            parameters = protocol.get('parameters', {})
            st.json(parameters)

        # Measurements
        with st.expander("📊 Measurements", expanded=False):
            measurements = protocol.get('measurements', {})
            required_fields = measurements.get('required_fields', [])
            optional_fields = measurements.get('optional_fields', [])

            st.markdown("**Required Fields:**")
            for field in required_fields:
                st.markdown(f"- {field}")

            if optional_fields:
                st.markdown("**Optional Fields:**")
                for field in optional_fields:
                    st.markdown(f"- {field}")

        # QC Criteria
        with st.expander("✅ QC Criteria", expanded=False):
            qc_criteria = protocol.get('qc_criteria', {})
            st.json(qc_criteria)

        # Test procedure
        with st.expander("📋 Test Procedure", expanded=False):
            procedure = protocol.get('test_procedure', [])
            for step in procedure:
                step_num = step.get('step', '?')
                description = step.get('description', 'No description')
                duration = step.get('duration', 'N/A')

                st.markdown(f"**Step {step_num}** (Duration: {duration})")
                st.markdown(description)
                st.markdown("")

    def get_protocol_data(self, protocol_id: str) -> Optional[Dict[str, Any]]:
        """
        Get protocol data by ID.

        Args:
            protocol_id: Protocol identifier

        Returns:
            Protocol data dictionary or None
        """
        return self.available_protocols.get(protocol_id)
