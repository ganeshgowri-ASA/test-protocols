"""
Protocol Selector Component
UI for selecting test protocols
"""

import streamlit as st
import json
from pathlib import Path
from typing import Optional, Dict, Any, List


def get_available_protocols() -> List[Dict[str, Any]]:
    """
    Get list of available protocols

    Returns:
        List of protocol metadata dictionaries
    """
    protocols = []
    protocol_dir = Path(__file__).parent.parent / "protocols" / "environmental"

    # Find all JSON protocol files
    if protocol_dir.exists():
        for protocol_file in protocol_dir.glob("*.json"):
            try:
                with open(protocol_file, 'r') as f:
                    protocol_data = json.load(f)
                    protocols.append({
                        'file': str(protocol_file),
                        'metadata': protocol_data.get('metadata', {}),
                        'data': protocol_data
                    })
            except Exception as e:
                st.warning(f"Failed to load protocol {protocol_file.name}: {e}")

    return protocols


def render_protocol_selector() -> Optional[Dict[str, Any]]:
    """
    Render protocol selector UI

    Returns:
        Selected protocol data or None
    """
    st.subheader("Available Protocols")

    # Get available protocols
    protocols = get_available_protocols()

    if not protocols:
        st.error("No protocols found. Please add protocol JSON files to the protocols directory.")
        return None

    # Category filter
    categories = list(set(p['metadata'].get('category', 'Unknown') for p in protocols))
    selected_category = st.selectbox(
        "Filter by Category",
        ["All"] + sorted(categories)
    )

    # Filter protocols by category
    if selected_category != "All":
        filtered_protocols = [p for p in protocols if p['metadata'].get('category') == selected_category]
    else:
        filtered_protocols = protocols

    # Display protocols as cards
    if not filtered_protocols:
        st.info("No protocols found in the selected category.")
        return None

    # Protocol selection
    selected_protocol = None

    for i, protocol in enumerate(filtered_protocols):
        metadata = protocol['metadata']

        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])

            with col1:
                st.markdown(f"### {metadata.get('name', 'Unnamed Protocol')}")
                st.markdown(f"**{metadata.get('id', 'N/A')}** - {metadata.get('protocol_number', 'N/A')}")

            with col2:
                st.markdown(f"**Category:** {metadata.get('category', 'N/A')}")
                st.markdown(f"**Version:** {metadata.get('version', 'N/A')}")

            with col3:
                if st.button("Select", key=f"select_{i}"):
                    selected_protocol = protocol['data']

            # Expandable details
            with st.expander("View Details"):
                st.markdown(f"**Description:** {metadata.get('description', 'No description')}")
                st.markdown(f"**Author:** {metadata.get('author', 'Unknown')}")

                if metadata.get('standard_references'):
                    st.markdown("**Standards:**")
                    for ref in metadata['standard_references']:
                        st.markdown(f"- {ref}")

            st.markdown("---")

    return selected_protocol
