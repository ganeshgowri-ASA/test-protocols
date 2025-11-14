"""
GenSpark Test Protocols - Main Streamlit Application

Dynamic test protocol execution and monitoring interface.
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ui.utils.session_state import initialize_session_state
from ui.pages import protocol_selector, data_entry, analysis_view, reports


# Page configuration
st.set_page_config(
    page_title="GenSpark Test Protocols",
    page_icon="🔬",
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
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .status-pass {
        color: #28a745;
        font-weight: bold;
    }
    .status-fail {
        color: #dc3545;
        font-weight: bold;
    }
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main application entry point"""

    # Initialize session state
    initialize_session_state()

    # Sidebar navigation
    st.sidebar.title("🔬 GenSpark Protocols")
    st.sidebar.markdown("---")

    # Page selection
    page = st.sidebar.radio(
        "Navigate",
        ["Protocol Selection", "Data Entry", "Analysis & Results", "Reports"],
        key="page_navigation"
    )

    # Display current test info in sidebar
    if st.session_state.get("current_test_run"):
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Current Test")
        test_run = st.session_state.current_test_run
        st.sidebar.info(f"""
        **Protocol:** {test_run.get('protocol_name', 'N/A')}
        **Sample:** {test_run.get('sample_id', 'N/A')}
        **Status:** {test_run.get('status', 'N/A')}
        """)

    # Main content area
    st.markdown('<div class="main-header">Test Protocols Framework</div>', unsafe_allow_html=True)

    if page == "Protocol Selection":
        protocol_selector.render()
    elif page == "Data Entry":
        data_entry.render()
    elif page == "Analysis & Results":
        analysis_view.render()
    elif page == "Reports":
        reports.render()

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style="text-align: center; color: #999; font-size: 0.8rem;">
        GenSpark Test Protocols v0.1.0<br>
        Modular PV Testing Framework
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
