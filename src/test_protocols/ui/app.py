"""Main Streamlit application for Test Protocols."""

import streamlit as st
from streamlit_option_menu import option_menu

from test_protocols.database.connection import db
from test_protocols.logger import setup_logger

logger = setup_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="Test Protocols - PV Testing Framework",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize database connection
if "db_connected" not in st.session_state:
    try:
        db.connect()
        st.session_state.db_connected = True
        logger.info("Database connected successfully")
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        st.session_state.db_connected = False


def main():
    """Main application entry point."""
    # Sidebar navigation
    with st.sidebar:
        st.title("🔬 Test Protocols")
        st.markdown("---")

        selected = option_menu(
            menu_title="Navigation",
            options=["Home", "New Test", "Active Tests", "Analysis", "Reports", "Settings"],
            icons=["house", "plus-circle", "play-circle", "graph-up", "file-text", "gear"],
            menu_icon="grid",
            default_index=0,
            styles={
                "container": {"padding": "0!important"},
                "nav-link": {
                    "font-size": "14px",
                    "text-align": "left",
                    "margin": "0px",
                    "--hover-color": "#eee",
                },
                "nav-link-selected": {"background-color": "#0068c9"},
            },
        )

        st.markdown("---")
        st.caption("IEC 61701 Compliant")
        st.caption("Version 1.0.0")

    # Route to selected page
    if selected == "Home":
        from test_protocols.ui.pages import home
        home.show()
    elif selected == "New Test":
        from test_protocols.ui.pages import new_test
        new_test.show()
    elif selected == "Active Tests":
        from test_protocols.ui.pages import active_tests
        active_tests.show()
    elif selected == "Analysis":
        from test_protocols.ui.pages import analysis
        analysis.show()
    elif selected == "Reports":
        from test_protocols.ui.pages import reports
        reports.show()
    elif selected == "Settings":
        from test_protocols.ui.pages import settings
        settings.show()


if __name__ == "__main__":
    main()
