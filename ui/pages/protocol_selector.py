"""
Protocol Selection Page

Interface for browsing and selecting test protocols.
"""

import streamlit as st
from pathlib import Path
import json
from typing import List, Dict, Any
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from protocols.implementations.corrosion.corrosion_protocol import CorrosionProtocol
from ui.utils.session_state import reset_test_run


def get_available_protocols() -> List[Dict[str, Any]]:
    """Get list of available protocol definitions"""
    protocols = []

    # Find all protocol JSON files
    protocols_dir = Path(__file__).parent.parent.parent / "protocols" / "definitions"

    for json_file in protocols_dir.rglob("*.json"):
        try:
            with open(json_file, 'r') as f:
                protocol_def = json.load(f)
                protocols.append({
                    "path": json_file,
                    "protocol_id": protocol_def.get("protocol_id"),
                    "name": protocol_def.get("name"),
                    "category": protocol_def.get("category"),
                    "version": protocol_def.get("version"),
                    "description": protocol_def.get("description", ""),
                    "standards": protocol_def.get("standards", []),
                    "metadata": protocol_def.get("metadata", {})
                })
        except Exception as e:
            st.error(f"Error loading protocol {json_file}: {e}")

    return protocols


def render():
    """Render protocol selection page"""

    st.header("Protocol Selection")
    st.markdown("Select a test protocol to begin or continue testing.")

    # Get available protocols
    protocols = get_available_protocols()

    if not protocols:
        st.warning("No protocols found. Please ensure protocol definitions are available.")
        return

    # Filter options
    col1, col2 = st.columns([3, 1])

    with col1:
        search_term = st.text_input("🔍 Search protocols", placeholder="Search by name or ID...")

    with col2:
        categories = list(set(p["category"] for p in protocols))
        selected_category = st.selectbox("Category", ["All"] + categories)

    # Filter protocols
    filtered_protocols = protocols

    if search_term:
        filtered_protocols = [
            p for p in filtered_protocols
            if search_term.lower() in p["name"].lower() or
               search_term.lower() in p["protocol_id"].lower()
        ]

    if selected_category != "All":
        filtered_protocols = [
            p for p in filtered_protocols
            if p["category"] == selected_category
        ]

    # Display protocols
    st.markdown("---")

    if not filtered_protocols:
        st.info("No protocols match your search criteria.")
        return

    for protocol in filtered_protocols:
        with st.expander(f"**{protocol['protocol_id']}** - {protocol['name']}", expanded=False):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**Category:** {protocol['category']}")
                st.markdown(f"**Version:** {protocol['version']}")
                st.markdown(f"**Description:** {protocol['description']}")

                if protocol['standards']:
                    st.markdown("**Standards:**")
                    for standard in protocol['standards']:
                        st.markdown(f"- {standard['name']} {standard['number']}: {standard.get('title', '')}")

                metadata = protocol.get('metadata', {})
                if metadata:
                    st.markdown(f"**Complexity:** {metadata.get('complexity', 'N/A')}")
                    st.markdown(f"**Typical Duration:** {metadata.get('typical_duration', 'N/A')}")

            with col2:
                if st.button("Select Protocol", key=f"select_{protocol['protocol_id']}"):
                    select_protocol(protocol)

    # Show current selection
    if st.session_state.get("selected_protocol"):
        st.markdown("---")
        st.success(f"**Selected Protocol:** {st.session_state.selected_protocol['name']}")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Start New Test Run"):
                start_new_test_run()
        with col2:
            if st.button("Load Existing Run"):
                st.info("Load existing run feature coming soon!")
        with col3:
            if st.button("Clear Selection"):
                reset_test_run()
                st.session_state.selected_protocol = None
                st.rerun()


def select_protocol(protocol: Dict[str, Any]) -> None:
    """Select a protocol for testing"""
    st.session_state.selected_protocol = protocol

    # Initialize protocol instance
    try:
        if protocol["protocol_id"] == "CORR-001":
            st.session_state.protocol_instance = CorrosionProtocol(
                definition_path=Path(protocol["path"])
            )
        else:
            st.warning(f"Protocol {protocol['protocol_id']} implementation not found.")
            return

        st.success(f"Protocol {protocol['protocol_id']} loaded successfully!")
        st.rerun()

    except Exception as e:
        st.error(f"Error loading protocol: {e}")


def start_new_test_run() -> None:
    """Start a new test run"""

    st.markdown("### Start New Test Run")

    with st.form("new_test_run_form"):
        run_id = st.text_input("Run ID *", placeholder="e.g., CORR-001-2025-001")
        sample_id = st.text_input("Sample ID *", placeholder="e.g., SAMPLE-12345")
        operator = st.text_input("Operator Name *", placeholder="e.g., John Doe")

        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("Create Test Run")
        with col2:
            cancel = st.form_submit_button("Cancel")

        if submit:
            if not all([run_id, sample_id, operator]):
                st.error("Please fill in all required fields (marked with *).")
            else:
                # Create test run
                protocol_instance = st.session_state.protocol_instance
                test_run = protocol_instance.create_test_run(
                    run_id=run_id,
                    operator=operator,
                    initial_data={
                        "sample_id": sample_id,
                        "operator": operator
                    }
                )

                st.session_state.current_test_run = {
                    "run_id": run_id,
                    "protocol_id": st.session_state.selected_protocol["protocol_id"],
                    "protocol_name": st.session_state.selected_protocol["name"],
                    "sample_id": sample_id,
                    "operator": operator,
                    "status": "in_progress"
                }

                st.success(f"Test run {run_id} created successfully!")
                st.info("Navigate to 'Data Entry' to begin testing.")
                st.rerun()

        if cancel:
            st.rerun()
