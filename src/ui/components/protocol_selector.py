"""Protocol selection component."""

import streamlit as st
from pathlib import Path


def render_protocol_selector():
    """
    Render protocol selection interface.

    Returns:
        Selected protocol ID or None
    """
    st.subheader("Select Protocol")

    protocols = [
        {
            "id": "TERM-001",
            "title": "Terminal Robustness Test",
            "category": "Mechanical",
            "version": "1.0",
        }
    ]

    protocol_options = {f"{p['id']}: {p['title']}": p["id"] for p in protocols}

    selected = st.selectbox(
        "Choose a test protocol",
        options=list(protocol_options.keys()),
        key="protocol_select",
    )

    if selected:
        protocol_id = protocol_options[selected]

        # Display protocol details
        protocol = next(p for p in protocols if p["id"] == protocol_id)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Protocol ID", protocol["id"])
        with col2:
            st.metric("Version", protocol["version"])
        with col3:
            st.metric("Category", protocol["category"])

        return protocol_id

    return None
