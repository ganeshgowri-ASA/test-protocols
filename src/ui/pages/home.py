"""Home page for PV Protocol Framework."""

import streamlit as st


def render():
    """Render home page."""
    st.title("☀️ PV Testing Protocol Framework")

    st.markdown("""
    ## Welcome to the Photovoltaic Testing Protocol Framework

    A modular, JSON-based framework for photovoltaic testing protocols with automated
    analysis, charting, quality control, and report generation.

    ### Key Features

    - **📋 Protocol Management**: JSON-based protocol definitions for flexibility
    - **🔬 Automated Testing**: Streamlined execution of standardized test protocols
    - **📊 Real-time Analysis**: Automated data analysis and visualization
    - **✅ Quality Control**: Built-in pass/fail criteria and validation
    - **📈 Comprehensive Reporting**: Automated report generation with charts and tables
    - **🔗 System Integration**: LIMS, QMS, and project management integration

    ### Available Protocols

    """)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("""
        **CRACK-001**
        Cell Crack Propagation

        *Category:* Degradation
        *Standard:* IEC 61215-2:2021

        Monitor crack propagation under thermal and mechanical stress.
        """)

    with col2:
        st.warning("""
        **More protocols**
        Coming Soon

        Additional protocols for performance, safety, and reliability testing.
        """)

    with col3:
        st.success("""
        **Custom Protocols**
        Build Your Own

        Create custom test protocols using our JSON template system.
        """)

    st.markdown("---")

    st.subheader("🚀 Quick Start")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        #### Run a Test
        1. Navigate to **Protocol Execution**
        2. Select protocol (e.g., CRACK-001)
        3. Configure test parameters
        4. Upload sample metadata
        5. Start test execution

        """)

    with col2:
        st.markdown("""
        #### View Results
        1. Navigate to **Results Viewer**
        2. Select test run from history
        3. View measurements and analysis
        4. Download reports
        5. Export data

        """)

    st.markdown("---")

    st.subheader("📚 Resources")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **📖 Documentation**
        - Protocol definitions
        - API reference
        - User guides
        """)

    with col2:
        st.markdown("""
        **🛠️ Support**
        - Technical support
        - Training materials
        - FAQ
        """)

    with col3:
        st.markdown("""
        **🔧 Tools**
        - Data export utilities
        - Custom report builder
        - Equipment calibration tracker
        """)
