"""Settings page for application configuration."""

import streamlit as st

from test_protocols.config import config
from test_protocols.database.connection import db


def show():
    """Show settings page."""
    st.title("⚙️ Settings")
    st.markdown("Configure application settings")
    st.markdown("---")

    # Database settings
    st.subheader("Database Configuration")

    col1, col2 = st.columns(2)

    with col1:
        st.text_input("Database URL", value=config.database.url, disabled=True)
        st.text_input("Pool Size", value=str(config.database.pool_size), disabled=True)

    with col2:
        db_health = db.health_check()
        health_status = "🟢 Connected" if db_health else "🔴 Disconnected"
        st.metric("Database Status", health_status)

    st.markdown("---")

    # Storage settings
    st.subheader("Storage Configuration")

    col1, col2 = st.columns(2)

    with col1:
        st.text_input("Report Output Directory", value=str(config.report_output_dir), disabled=True)

    with col2:
        st.text_input("Image Storage Directory", value=str(config.image_storage_dir), disabled=True)

    st.markdown("---")

    # Application settings
    st.subheader("Application Settings")

    col1, col2 = st.columns(2)

    with col1:
        st.text_input("Log Level", value=config.log_level, disabled=True)

    with col2:
        debug_status = "Enabled" if config.debug else "Disabled"
        st.text_input("Debug Mode", value=debug_status, disabled=True)

    st.markdown("---")

    # Integration settings
    st.subheader("External Integrations")

    st.text_input(
        "LIMS API URL",
        value=config.lims_api_url if config.lims_api_url else "Not configured",
        disabled=True,
    )

    st.text_input(
        "QMS API URL",
        value=config.qms_api_url if config.qms_api_url else "Not configured",
        disabled=True,
    )

    st.markdown("---")

    # About
    st.subheader("About")

    st.markdown("""
    **Test Protocols Framework**
    - Version: 1.0.0
    - Protocol: SALT-001 (IEC 61701)
    - License: MIT

    For configuration changes, modify the `.env` file or environment variables.
    """)
