"""Main Streamlit Application for Test Protocols Framework"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Page configuration
st.set_page_config(
    page_title="PV Test Protocols - GenSpark",
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
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .pass-status {
        color: #28a745;
        font-weight: bold;
    }
    .fail-status {
        color: #dc3545;
        font-weight: bold;
    }
    .warning-status {
        color: #ffc107;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application entry point"""

    st.markdown('<div class="main-header">PV Test Protocols - GenSpark UI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Modular Testing Framework for Photovoltaic Systems</div>', unsafe_allow_html=True)

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Page",
        [
            "Home",
            "Protocol Selector",
            "Test Execution",
            "Data Analysis",
            "Reports",
            "QC Review",
        ]
    )

    # Route to appropriate page
    if page == "Home":
        show_home_page()
    elif page == "Protocol Selector":
        show_protocol_selector()
    elif page == "Test Execution":
        show_test_execution()
    elif page == "Data Analysis":
        show_data_analysis()
    elif page == "Reports":
        show_reports()
    elif page == "QC Review":
        show_qc_review()


def show_home_page():
    """Display home page"""
    st.header("Welcome to GenSpark Test Protocols")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Available Protocols", "1", delta="CHALK-001")

    with col2:
        st.metric("Active Tests", "0")

    with col3:
        st.metric("Completed Tests", "0")

    st.markdown("---")

    st.subheader("Quick Start")
    st.markdown("""
    1. **Select a Protocol**: Choose from available test protocols in the Protocol Selector
    2. **Execute Test**: Follow the guided workflow to collect test data
    3. **Review Results**: Analyze data with automated calculations and visualizations
    4. **Generate Reports**: Create standardized test reports for documentation
    5. **QC Review**: Quality control review and approval workflow
    """)

    st.markdown("---")

    st.subheader("Available Protocols")

    protocol_data = {
        "Protocol ID": ["CHALK-001"],
        "Name": ["Backsheet Chalking Protocol"],
        "Category": ["Degradation"],
        "Version": ["1.0.0"],
        "Status": ["Active"],
    }

    st.dataframe(protocol_data, use_container_width=True)


def show_protocol_selector():
    """Display protocol selector page"""
    st.header("Protocol Selector")

    # Import protocol selector component
    from pages.protocol_selector import render_protocol_selector
    render_protocol_selector()


def show_test_execution():
    """Display test execution page"""
    st.header("Test Execution")

    # Import test execution component
    from pages.test_execution import render_test_execution
    render_test_execution()


def show_data_analysis():
    """Display data analysis page"""
    st.header("Data Analysis")

    # Import analysis component
    from pages.analysis_view import render_analysis_view
    render_analysis_view()


def show_reports():
    """Display reports page"""
    st.header("Reports")

    # Import reports component
    from pages.reports import render_reports
    render_reports()


def show_qc_review():
    """Display QC review page"""
    st.header("QC Review")

    # Import QC review component
    from pages.qc_review import render_qc_review
    render_qc_review()


if __name__ == "__main__":
    main()
