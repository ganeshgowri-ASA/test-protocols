"""
Audit Pro Enterprise - Main Application
========================================
SESSION-APE-001: Enterprise Audit Management System

Main Streamlit application with authentication and navigation.
"""

import streamlit as st
from config.settings import config
from config.database import init_database, check_database_health
from components.auth import check_authentication, render_login_page, render_user_info


# Page configuration
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)


def init_app():
    """Initialize application and database"""
    # Initialize database
    if 'db_initialized' not in st.session_state:
        try:
            init_database()
            st.session_state.db_initialized = True
        except Exception as e:
            st.error(f"Database initialization error: {e}")
            st.stop()


def render_home():
    """Render home page"""
    st.title("📋 Audit Pro Enterprise")
    st.markdown(f"**Version:** {config.APP_VERSION} | **Session:** {config.SESSION_ID}")

    st.markdown("---")

    # Welcome message
    st.markdown("""
    ## Welcome to Audit Pro Enterprise

    A comprehensive enterprise audit management system with full lifecycle support:

    ### 🎯 Key Features

    **📊 Entity Management**
    - Hierarchical organization structure (Company → Division → Plant → Department)
    - Complete entity tree visualization
    - Contact management and location tracking

    **📅 Audit Planning**
    - Annual audit program management
    - Multi-standard support (ISO 9001, 14001, 45001, 27001, etc.)
    - Auditor assignment and scheduling
    - Resource planning and allocation

    **✅ Audit Execution**
    - Digital checklists with clause references
    - Real-time findings capture
    - Evidence attachment and documentation
    - Progress tracking and status updates

    **⚠️ NC/OFI Tracking**
    - Non-conformance management
    - Opportunity for improvement tracking
    - Severity classification (Critical, Major, Minor, Observation)
    - Assignment and due date management

    **🔧 Corrective Actions**
    - CAR/8D methodology support
    - Root cause analysis tools
    - Action plan tracking
    - Effectiveness verification

    **📈 Reports & Analytics**
    - Real-time dashboard
    - Trend analysis and metrics
    - PDF report generation
    - Excel data export

    ### 🔐 Role-Based Access Control

    - **Admin**: Full system access and configuration
    - **Auditor**: Audit planning and execution
    - **Auditee**: View assigned audits and respond to findings
    - **Viewer**: Read-only access to reports

    ### 🚀 Getting Started

    1. Navigate using the sidebar menu
    2. Start with **Entity Management** to set up your organization
    3. Use **Audit Planning** to schedule audits
    4. Execute audits in **Audit Execution**
    5. Track findings in **NC/OFI Tracking**
    6. Manage corrective actions in **Corrective Actions**
    7. View analytics in **Reports & Analytics**
    """)

    # System Status
    st.markdown("---")
    st.subheader("📊 System Status")

    col1, col2, col3 = st.columns(3)

    # Database health check
    db_health = check_database_health()

    with col1:
        if db_health['status'] == 'healthy':
            st.success("✅ Database: Connected")
        else:
            st.error(f"❌ Database: {db_health.get('error', 'Unknown error')}")

    with col2:
        st.info(f"👤 User: {st.session_state.get('full_name', 'N/A')}")

    with col3:
        st.info(f"🎭 Role: {st.session_state.get('role', 'N/A').upper()}")

    # Quick Stats
    st.markdown("---")
    st.subheader("📈 Quick Stats")

    from config.database import get_db
    from models.entity import Entity
    from models.audit import Audit, AuditSchedule
    from models.nc_ofi import NC_OFI

    try:
        with get_db() as db:
            entity_count = db.query(Entity).count()
            audit_count = db.query(Audit).count()
            schedule_count = db.query(AuditSchedule).count()
            nc_count = db.query(NC_OFI).count()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Entities", entity_count)

        with col2:
            st.metric("Scheduled Audits", schedule_count)

        with col3:
            st.metric("Completed Audits", audit_count)

        with col4:
            st.metric("NC/OFI", nc_count)

    except Exception as e:
        st.warning(f"Unable to load statistics: {e}")

    # Session Info
    st.markdown("---")
    st.info(f"""
    **Session Information**
    - Session ID: {config.SESSION_ID}
    - Application: {config.APP_NAME} v{config.APP_VERSION}
    - Database: SQLite (Audit Pro Enterprise)
    """)


def main():
    """Main application entry point"""
    # Initialize app
    init_app()

    # Check authentication
    if not check_authentication():
        render_login_page()
        return

    # Render sidebar with user info
    with st.sidebar:
        st.title("🎯 Navigation")
        render_user_info()

    # Render home page
    render_home()


if __name__ == "__main__":
    main()
