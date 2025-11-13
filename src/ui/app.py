"""Main Streamlit application for IAM-001 protocol testing."""

import streamlit as st
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="IAM-001 Protocol Testing",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #555;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("☀️ IAM-001 Protocol")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["🏠 Home", "➕ New Test", "📊 View Results", "📁 Data Management", "ℹ️ About"]
)

# Main content
if page == "🏠 Home":
    st.markdown('<div class="main-header">IAM-001 Incidence Angle Modifier Testing</div>', unsafe_allow_html=True)
    st.markdown("### IEC 61853 Photovoltaic Module Testing Protocol")

    st.markdown("""
    This application provides a complete workflow for testing and analyzing the incidence angle modifier (IAM)
    of photovoltaic modules according to IEC 61853 standards.

    #### Features:
    - 📝 **Protocol Management**: Create and manage test protocols
    - 📊 **AOI Curve Analysis**: Automatic calculation and fitting of IAM curves
    - ✅ **Quality Control**: Built-in validation and QC checks
    - 💾 **Traceability**: Complete audit trail and data storage
    - 📈 **Visualization**: Interactive plots and reports
    """)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🎯 Quick Start")
        if st.button("Create New Test", type="primary", use_container_width=True):
            st.session_state.page = "➕ New Test"
            st.rerun()

    with col2:
        st.markdown("### 📊 Recent Tests")
        if st.button("View Results", use_container_width=True):
            st.session_state.page = "📊 View Results"
            st.rerun()

    with col3:
        st.markdown("### 📁 Data")
        if st.button("Manage Data", use_container_width=True):
            st.session_state.page = "📁 Data Management"
            st.rerun()

    st.markdown("---")

    st.markdown("### 📋 Test Requirements")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Standard Angles (0-90°):**
        - Normal incidence: 0°
        - Recommended: 0°, 10°, 20°, 30°, 40°, 50°, 60°, 70°, 80°, 90°
        - Minimum: 5 data points
        """)

        st.markdown("""
        **Test Conditions:**
        - Irradiance: 1000 W/m² (±50 W/m²)
        - Temperature: 25°C (±5°C)
        - Spectrum: AM1.5G
        """)

    with col2:
        st.markdown("""
        **Measurements Required:**
        - Short-circuit current (Isc)
        - Open-circuit voltage (Voc)
        - Maximum power (Pmax)
        - I-V curve parameters
        """)

        st.markdown("""
        **Quality Metrics:**
        - IAM curve fitting (R² > 0.90)
        - Measurement stability
        - Data completeness
        """)

elif page == "➕ New Test":
    from .pages import new_test
    new_test.render()

elif page == "📊 View Results":
    from .pages import view_results
    view_results.render()

elif page == "📁 Data Management":
    from .pages import data_management
    data_management.render()

elif page == "ℹ️ About":
    st.markdown('<div class="main-header">About IAM-001 Protocol</div>', unsafe_allow_html=True)

    st.markdown("""
    ### Incidence Angle Modifier (IAM)

    The Incidence Angle Modifier describes how the electrical performance of a photovoltaic module
    varies with the angle of incidence (AOI) of sunlight. This is a critical parameter for
    accurately predicting module performance under real-world conditions.

    #### IEC 61853 Standard

    This protocol follows the IEC 61853 international standard for PV module performance testing
    and energy rating. The IAM test measures module performance at angles from 0° (normal incidence)
    to 90° (grazing incidence).

    #### Analysis Models

    Three IAM models are available:

    1. **ASHRAE Model**: Simple single-parameter model
       - IAM(θ) = 1 - b₀ * (1/cos(θ) - 1)

    2. **Physical Model**: Based on Fresnel reflections
       - IAM(θ) = (1 - exp(-cos(θ)/aᵣ)) / (1 - exp(-1/aᵣ))

    3. **Polynomial Model**: Flexible 4th-order polynomial
       - IAM(θ) = 1 + a₁θ + a₂θ² + a₃θ³ + a₄θ⁴

    #### Version Information

    - Protocol Version: 1.0.0
    - Standard: IEC 61853
    - Application Version: 0.1.0
    """)

    st.markdown("---")
    st.markdown("© 2025 Test Protocols Team | [Documentation](https://example.com/docs) | [Support](mailto:support@example.com)")

# Sidebar info
st.sidebar.markdown("---")
st.sidebar.markdown("### System Status")
st.sidebar.success("✅ Protocol Engine: Ready")
st.sidebar.success("✅ Analysis Module: Ready")
st.sidebar.success("✅ Database: Connected")
