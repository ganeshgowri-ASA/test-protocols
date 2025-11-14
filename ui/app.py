"""Main Streamlit application for Test Protocols Framework."""

import streamlit as st
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logging_config import setup_logging

# Setup logging
logger = setup_logging()

# Page configuration
st.set_page_config(
    page_title="PV Test Protocols",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #262730;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #F0F2F6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .metric-container {
        background-color: #FFFFFF;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Main app
st.markdown('<div class="main-header">☀️ PV Test Protocols Framework</div>', unsafe_allow_html=True)

st.markdown("""
### Welcome to the Modular PV Testing Protocol Framework

This application provides a comprehensive platform for managing and executing photovoltaic module test protocols.

**Features:**
- 📋 Protocol Management: JSON-based dynamic protocol templates
- 📊 Data Entry: Streamlined measurement data collection
- 📈 Analysis: Automated calculations and charting
- ✅ QC: Real-time quality control checks
- 📄 Reports: Automated report generation
- 🔗 Integration: LIMS, QMS, and Project Management systems

**Available Protocols:**
- **LID-001**: Light-Induced Degradation
- More protocols coming soon...

### Getting Started

Use the sidebar to navigate between different sections:

1. **Protocol Setup**: Configure test parameters and samples
2. **Data Entry**: Enter measurement data
3. **Analysis**: View charts and analysis results
4. **Reports**: Generate and export test reports

### Quick Links

- [Documentation](https://github.com/test-protocols/docs)
- [Support](https://github.com/test-protocols/issues)
- [Version]: 0.1.0
""")

# Sidebar information
with st.sidebar:
    st.image("https://via.placeholder.com/150x50.png?text=Logo", width=150)

    st.markdown("### System Status")
    st.success("🟢 System Online")

    st.markdown("### Statistics")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Active Tests", "0")
    with col2:
        st.metric("Completed", "0")

    st.markdown("### Recent Activity")
    st.info("No recent activity")

    st.markdown("---")
    st.markdown("**Version**: 0.1.0")
    st.markdown("**Build**: Alpha")

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666;">© 2025 Test Protocols Framework | MIT License</div>',
    unsafe_allow_html=True
)
