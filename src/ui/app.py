"""
Main Streamlit application for PV Testing Protocol Framework
"""

import streamlit as st

from .spec_001_ui import render_spec_001_ui


def main():
    """Main application entry point"""
    st.set_page_config(
        page_title="PV Testing Protocol Framework",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Sidebar navigation
    st.sidebar.title("⚡ PV Testing Protocols")
    st.sidebar.markdown("---")

    # Protocol selection
    protocol_options = {
        "SPEC-001: Spectral Response Test": "spec_001",
        # Future protocols can be added here
        # "IV-001: I-V Curve Measurement": "iv_001",
        # "EL-001: Electroluminescence Imaging": "el_001",
    }

    selected_protocol = st.sidebar.selectbox(
        "Select Protocol",
        options=list(protocol_options.keys())
    )

    # Information
    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.info(
        "**Modular PV Testing Protocol Framework**\n\n"
        "JSON-based dynamic templates for automated testing, "
        "analysis, and reporting of photovoltaic devices.\n\n"
        "Integrated with LIMS, QMS, and Project Management systems."
    )

    st.sidebar.markdown("### Features")
    st.sidebar.markdown(
        "✅ Standardized test protocols\n"
        "✅ Automated data acquisition\n"
        "✅ Real-time analysis\n"
        "✅ Quality control checks\n"
        "✅ Interactive visualizations\n"
        "✅ Report generation\n"
        "✅ Database integration"
    )

    # Render selected protocol
    protocol_key = protocol_options[selected_protocol]

    if protocol_key == "spec_001":
        render_spec_001_ui()
    else:
        st.error("Protocol not yet implemented")


if __name__ == "__main__":
    main()
