"""
Main Streamlit Application for PV Testing Protocol Framework
DELAM-001 Delamination Test with EL Analysis
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Page configuration
st.set_page_config(
    page_title="PV Testing Protocol Framework",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
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
        color: #ff7f0e;
        margin-bottom: 0.5rem;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin-bottom: 1rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main application entry point"""

    # Sidebar navigation
    st.sidebar.markdown("# 🔬 PV Testing Framework")
    st.sidebar.markdown("---")

    # Protocol selection
    st.sidebar.markdown("### Protocol Selection")
    protocol_id = st.sidebar.selectbox(
        "Select Protocol",
        ["DELAM-001 - Delamination Test"],
        key="protocol_selector"
    )

    st.sidebar.markdown("---")

    # Navigation
    st.sidebar.markdown("### Navigation")
    st.sidebar.markdown("""
    Navigate to different sections using the pages in the sidebar:

    - **Protocol Setup**: Configure test parameters
    - **Data Entry**: Enter test measurements
    - **Analysis**: Run EL image analysis
    - **Report**: Generate test reports
    """)

    st.sidebar.markdown("---")

    # Session info
    st.sidebar.markdown("### Session Information")
    if 'user_name' not in st.session_state:
        st.session_state.user_name = "Test User"

    st.sidebar.info(f"**User:** {st.session_state.user_name}")

    # Main content
    st.markdown('<div class="main-header">PV Testing Protocol Framework</div>', unsafe_allow_html=True)

    st.markdown("""
    Welcome to the **Photovoltaic Testing Protocol Framework** - a comprehensive platform for
    managing and executing PV module testing protocols with automated analysis and reporting.
    """)

    # Protocol information card
    st.markdown("---")
    st.markdown('<div class="sub-header">DELAM-001: Delamination Test Protocol</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("**Standard**")
        st.markdown("IEC 61215:2021")
        st.markdown("Section 10.13")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("**Test Type**")
        st.markdown("Environmental")
        st.markdown("Accelerated Aging")
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("**Analysis Method**")
        st.markdown("EL Imaging")
        st.markdown("Automated Defect Detection")
        st.markdown('</div>', unsafe_allow_html=True)

    # Features
    st.markdown("---")
    st.markdown("### Key Features")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Testing Capabilities:**
        - 📋 JSON-based protocol definitions
        - 🌡️ Environmental condition monitoring
        - 📸 EL image capture and storage
        - 📊 Real-time data visualization
        - ✅ Automated validation
        """)

    with col2:
        st.markdown("""
        **Analysis & Reporting:**
        - 🔍 Automated defect detection
        - 📈 Delamination quantification
        - 🎯 Pass/fail criteria evaluation
        - 📄 Automated report generation
        - 🔗 LIMS/QMS integration
        """)

    # Quick Start
    st.markdown("---")
    st.markdown("### Quick Start Guide")

    with st.expander("🚀 Getting Started", expanded=True):
        st.markdown("""
        1. **Protocol Setup**: Navigate to *Protocol Setup* page to configure test parameters
        2. **Sample Registration**: Register your module samples in the system
        3. **Test Execution**: Use *Data Entry* page to record measurements
        4. **EL Analysis**: Upload EL images in *Analysis* page for automated defect detection
        5. **Report Generation**: Generate comprehensive test reports in *Report* page
        """)

    with st.expander("📖 Protocol Overview"):
        st.markdown("""
        **DELAM-001 Delamination Test Protocol**

        This protocol evaluates the resistance of PV modules to delamination under
        accelerated environmental stress conditions.

        **Test Conditions:**
        - Temperature: 85°C ± 2°C
        - Humidity: 85% RH ± 5%
        - Duration: 1000 hours
        - Inspection Intervals: 0, 250, 500, 1000 hours

        **Acceptance Criteria:**
        - Maximum delamination area: 5% of module area
        - Maximum power degradation: 5%
        - No visible defects (bubbles, discoloration, broken cells)
        """)

    with st.expander("🔧 Equipment Requirements"):
        st.markdown("""
        **Required Equipment:**
        - Environmental chamber (0-100°C, 10-98% RH)
        - EL camera system (InGaAs or Si CCD, ≥2MP, ≥12-bit)
        - IV curve tracer (0-100V, 0-20A, ±0.5% accuracy)
        - Solar simulator or LED array (850nm, ±5% uniformity)

        All equipment must be calibrated and within certification period.
        """)

    # Statistics dashboard (placeholder)
    st.markdown("---")
    st.markdown("### Test Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Tests", "0", help="Total number of tests executed")

    with col2:
        st.metric("In Progress", "0", help="Tests currently in progress")

    with col3:
        st.metric("Completed", "0", help="Completed tests")

    with col4:
        st.metric("Pass Rate", "0%", help="Overall pass rate")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        PV Testing Protocol Framework v1.0.0 | IEC 61215:2021 Compliant
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
