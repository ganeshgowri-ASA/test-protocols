"""Main Streamlit application for Test Protocols framework."""

import streamlit as st
from pathlib import Path

# Configure page
st.set_page_config(
    page_title="PV Testing Protocol Framework",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        padding-bottom: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def main():
    """Main application entry point."""
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Page",
        [
            "Home",
            "Protocol Selection",
            "Test Execution",
            "Results & Analysis",
            "Reports",
            "Database Explorer",
        ],
    )

    # Main content area
    if page == "Home":
        show_home_page()
    elif page == "Protocol Selection":
        from .pages.protocol_selection import show_protocol_selection_page

        show_protocol_selection_page()
    elif page == "Test Execution":
        from .pages.test_execution import show_test_execution_page

        show_test_execution_page()
    elif page == "Results & Analysis":
        from .pages.results import show_results_page

        show_results_page()
    elif page == "Reports":
        from .pages.reports import show_reports_page

        show_reports_page()
    elif page == "Database Explorer":
        from .pages.database_explorer import show_database_explorer_page

        show_database_explorer_page()


def show_home_page():
    """Display home page."""
    st.markdown('<div class="main-header">PV Testing Protocol Framework</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Modular JSON-based dynamic templates for automated analysis, charting, QC, and reporting</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("📋 Available Protocols")
        st.markdown(
            """
        - **ENER-001**: Energy Rating Test (IEC 61853)
        - More protocols coming soon...
        """
        )

    with col2:
        st.subheader("🔬 Features")
        st.markdown(
            """
        - JSON-based protocol definitions
        - Automated data validation
        - Quality control checks
        - Interactive charts and analysis
        - PDF/HTML report generation
        - LIMS/QMS integration ready
        """
        )

    with col3:
        st.subheader("🚀 Quick Start")
        st.markdown(
            """
        1. Select a protocol
        2. Upload or input test data
        3. Run the test
        4. Review results and QC
        5. Generate reports
        """
        )

    st.markdown("---")

    # Recent sessions
    st.subheader("Recent Test Sessions")

    try:
        from ..models import init_database, get_session, TestSession

        # Initialize database
        init_database()

        # Query recent sessions
        with get_session() as session:
            recent_sessions = (
                session.query(TestSession)
                .order_by(TestSession.created_at.desc())
                .limit(5)
                .all()
            )

            if recent_sessions:
                for test_session in recent_sessions:
                    with st.expander(
                        f"📊 {test_session.session_id} - {test_session.status}"
                    ):
                        st.write(f"**Protocol**: {test_session.protocol.name if test_session.protocol else 'N/A'}")
                        st.write(f"**Status**: {test_session.status}")
                        st.write(f"**Started**: {test_session.started_at}")
                        if test_session.completed_at:
                            st.write(f"**Completed**: {test_session.completed_at}")
                            st.write(f"**Duration**: {test_session.duration_seconds:.1f}s")
            else:
                st.info("No test sessions found. Start by executing a test!")

    except Exception as e:
        st.warning(f"Unable to load recent sessions: {e}")

    st.markdown("---")
    st.info("ℹ️ Select a page from the sidebar to get started.")


if __name__ == "__main__":
    main()
