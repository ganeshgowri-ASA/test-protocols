"""
PV Testing Protocol System - Unified Streamlit Application
==========================================================
Production-ready application integrating all 54 PV testing protocols
with complete workflow orchestration, dashboards, and traceability.

Author: PV Testing Lab
Version: 1.0.0
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.database.db_manager import DatabaseManager

# ============================================
# PAGE CONFIGURATION
# ============================================

st.set_page_config(
    page_title="PV Testing Protocol System",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://docs.pvtesting.com',
        'Report a bug': 'https://github.com/pvtesting/support',
        'About': """
        # PV Testing Protocol System v1.0.0

        Complete testing protocol management system for photovoltaic modules.

        **Features:**
        - 54 Integrated Testing Protocols
        - Complete Workflow Orchestration
        - Real-time Data Traceability
        - Quality Assurance Integration
        - Comprehensive Reporting

        © 2024 PV Testing Laboratory
        """
    }
)

# ============================================
# SESSION STATE INITIALIZATION
# ============================================

def initialize_session_state():
    """Initialize all session state variables"""

    # Database
    if 'db' not in st.session_state:
        st.session_state.db = DatabaseManager()

    # User info (placeholder - integrate with actual auth)
    if 'user' not in st.session_state:
        st.session_state.user = {
            'user_id': 1,
            'username': 'admin',
            'full_name': 'System Administrator',
            'role': 'admin'
        }

    # Navigation
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Home'

    # Workflow state
    if 'current_request_id' not in st.session_state:
        st.session_state.current_request_id = None

    if 'current_inspection_id' not in st.session_state:
        st.session_state.current_inspection_id = None

    if 'current_execution_id' not in st.session_state:
        st.session_state.current_execution_id = None

    # UI state
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'

    if 'auto_save' not in st.session_state:
        st.session_state.auto_save = True

# Initialize
initialize_session_state()

# ============================================
# PROTOCOL DEFINITIONS (All 54 Protocols)
# ============================================

PROTOCOLS = [
    # IEC 61215 - Electrical Performance & Reliability
    {"id": "PVTP-001", "name": "LID/LIS Testing", "category": "Electrical", "standard": "IEC 61215-1"},
    {"id": "PVTP-002", "name": "Thermal Cycling", "category": "Reliability", "standard": "IEC 61215-2"},
    {"id": "PVTP-003", "name": "Damp Heat Testing", "category": "Environmental", "standard": "IEC 61215-2"},
    {"id": "PVTP-004", "name": "Humidity Freeze", "category": "Environmental", "standard": "IEC 61215-2"},
    {"id": "PVTP-005", "name": "UV Preconditioning", "category": "Environmental", "standard": "IEC 61215-2"},
    {"id": "PVTP-006", "name": "Outdoor Exposure", "category": "Environmental", "standard": "IEC 61215-2"},
    {"id": "PVTP-007", "name": "Hot Spot Endurance", "category": "Reliability", "standard": "IEC 61215-2"},
    {"id": "PVTP-008", "name": "UV Test", "category": "Environmental", "standard": "IEC 61215-2"},
    {"id": "PVTP-009", "name": "Thermal Cycling (Extended)", "category": "Reliability", "standard": "IEC 61215-2"},
    {"id": "PVTP-010", "name": "Damp Heat (Extended)", "category": "Environmental", "standard": "IEC 61215-2"},

    # IEC 61215 - Mechanical & Structural
    {"id": "PVTP-011", "name": "Mechanical Load Test", "category": "Mechanical", "standard": "IEC 61215-2"},
    {"id": "PVTP-012", "name": "Hail Impact Test", "category": "Mechanical", "standard": "IEC 61215-2"},
    {"id": "PVTP-013", "name": "Robustness of Terminations", "category": "Mechanical", "standard": "IEC 61215-2"},
    {"id": "PVTP-014", "name": "Twist Test", "category": "Mechanical", "standard": "IEC 61215-2"},
    {"id": "PVTP-015", "name": "Bypass Diode Thermal Test", "category": "Thermal", "standard": "IEC 61215-2"},

    # IEC 61730 - Safety
    {"id": "PVTP-016", "name": "Fire Test", "category": "Safety", "standard": "IEC 61730-2"},
    {"id": "PVTP-017", "name": "Wet Leakage Current", "category": "Safety", "standard": "IEC 61730-2"},
    {"id": "PVTP-018", "name": "Dielectric Voltage Test", "category": "Safety", "standard": "IEC 61730-2"},
    {"id": "PVTP-019", "name": "Ground Continuity", "category": "Safety", "standard": "IEC 61730-2"},
    {"id": "PVTP-020", "name": "Cut Susceptibility", "category": "Safety", "standard": "IEC 61730-2"},

    # IEC 61853 - PV Module Performance Testing
    {"id": "PVTP-021", "name": "Spectral Response", "category": "Optical", "standard": "IEC 61853-1"},
    {"id": "PVTP-022", "name": "Temperature Coefficients", "category": "Electrical", "standard": "IEC 61853-1"},
    {"id": "PVTP-023", "name": "Irradiance & Temperature", "category": "Environmental", "standard": "IEC 61853-1"},
    {"id": "PVTP-024", "name": "Low Irradiance Performance", "category": "Electrical", "standard": "IEC 61853-1"},
    {"id": "PVTP-025", "name": "Incidence Angle Response", "category": "Optical", "standard": "IEC 61853-2"},

    # IEC 60891 - Electrical Characterization
    {"id": "PVTP-026", "name": "I-V Curve Measurement", "category": "Electrical", "standard": "IEC 60891"},
    {"id": "PVTP-027", "name": "STC Power Rating", "category": "Electrical", "standard": "IEC 60891"},
    {"id": "PVTP-028", "name": "NOCT Measurement", "category": "Thermal", "standard": "IEC 61215-1"},
    {"id": "PVTP-029", "name": "Maximum Power Tracking", "category": "Electrical", "standard": "IEC 60891"},

    # IEC 62804 - PID Testing
    {"id": "PVTP-030", "name": "PID Testing (System Voltage)", "category": "Reliability", "standard": "IEC 62804"},
    {"id": "PVTP-031", "name": "PID Recovery Test", "category": "Reliability", "standard": "IEC 62804"},

    # IEC TS 63126 - Bifacial Modules
    {"id": "PVTP-032", "name": "Bifacial Power Measurement", "category": "Electrical", "standard": "IEC TS 63126"},
    {"id": "PVTP-033", "name": "Bifaciality Factor", "category": "Electrical", "standard": "IEC TS 63126"},

    # Additional Characterization Tests
    {"id": "PVTP-034", "name": "Electroluminescence Imaging", "category": "Quality Control", "standard": "IEC 60904-13"},
    {"id": "PVTP-035", "name": "Thermography Analysis", "category": "Quality Control", "standard": "IEC 62446"},
    {"id": "PVTP-036", "name": "Visual Inspection", "category": "Quality Control", "standard": "IEC 61215-1"},
    {"id": "PVTP-037", "name": "Insulation Resistance", "category": "Safety", "standard": "IEC 61215-2"},
    {"id": "PVTP-038", "name": "Grounding Verification", "category": "Safety", "standard": "IEC 61730-2"},

    # Performance Monitoring
    {"id": "PVTP-039", "name": "Long-term Stability", "category": "Reliability", "standard": "IEC 61215-1"},
    {"id": "PVTP-040", "name": "Performance Degradation", "category": "Reliability", "standard": "IEC 61215-1"},
    {"id": "PVTP-041", "name": "Field Performance Ratio", "category": "Performance", "standard": "IEC 61724"},

    # Module Quality Tests
    {"id": "PVTP-042", "name": "Solderability Test", "category": "Quality Control", "standard": "IEC 61215-2"},
    {"id": "PVTP-043", "name": "Peel Test", "category": "Quality Control", "standard": "IEC 61215-2"},
    {"id": "PVTP-044", "name": "Thermal Shock", "category": "Reliability", "standard": "IEC 61215-2"},
    {"id": "PVTP-045", "name": "Salt Mist Corrosion", "category": "Environmental", "standard": "IEC 61701"},
    {"id": "PVTP-046", "name": "Ammonia Corrosion", "category": "Environmental", "standard": "IEC 62716"},
    {"id": "PVTP-047", "name": "Sand & Dust Test", "category": "Environmental", "standard": "IEC 60068-2-68"},

    # Advanced Testing
    {"id": "PVTP-048", "name": "Dynamic Mechanical Load", "category": "Mechanical", "standard": "IEC 61215-2"},
    {"id": "PVTP-049", "name": "Cell Interconnect Fatigue", "category": "Reliability", "standard": "IEC 61215-2"},
    {"id": "PVTP-050", "name": "Bypass Diode Functionality", "category": "Electrical", "standard": "IEC 61215-2"},

    # Warranty & Compliance
    {"id": "PVTP-051", "name": "Flash Testing", "category": "Quality Control", "standard": "IEC 60904-1"},
    {"id": "PVTP-052", "name": "Power Tolerance Verification", "category": "Quality Control", "standard": "IEC 61215-1"},
    {"id": "PVTP-053", "name": "Nameplate Verification", "category": "Quality Control", "standard": "IEC 61730-1"},
    {"id": "PVTP-054", "name": "Compliance Documentation", "category": "Documentation", "standard": "IEC 61215-1"},
]

# ============================================
# SIDEBAR NAVIGATION
# ============================================

def render_sidebar():
    """Render sidebar with navigation"""

    with st.sidebar:
        st.image("https://via.placeholder.com/200x60/1f77b4/ffffff?text=PV+Testing", use_container_width=True)

        st.title("🔬 PV Testing")
        st.markdown(f"**User:** {st.session_state.user['full_name']}")
        st.markdown(f"**Role:** {st.session_state.user['role'].title()}")
        st.markdown("---")

        # Main Navigation
        st.subheader("📋 Navigation")

        # Workflow Section
        with st.expander("🔄 Workflow", expanded=True):
            if st.button("🏠 Home", use_container_width=True):
                st.switch_page("streamlit_app.py")

            if st.button("📝 Service Request", use_container_width=True):
                st.switch_page("pages/01_Service_Request.py")

            if st.button("🔍 Incoming Inspection", use_container_width=True):
                st.switch_page("pages/02_Incoming_Inspection.py")

            if st.button("⚙️ Equipment Planning", use_container_width=True):
                st.switch_page("pages/03_Equipment_Planning.py")

            if st.button("🎯 Protocol Selector", use_container_width=True):
                st.switch_page("pages/04_Protocol_Selector.py")

        # Dashboards Section
        with st.expander("📊 Dashboards", expanded=False):
            if st.button("📈 Master Dashboard", use_container_width=True):
                st.switch_page("pages/80_Master_Dashboard.py")

            if st.button("🔗 Traceability", use_container_width=True):
                st.switch_page("pages/81_Traceability.py")

            if st.button("✅ QA Dashboard", use_container_width=True):
                st.switch_page("pages/82_QA_Dashboard.py")

            if st.button("📊 Analytics", use_container_width=True):
                st.switch_page("pages/83_Analytics.py")

            if st.button("📄 Reports", use_container_width=True):
                st.switch_page("pages/84_Reports.py")

        # Protocol Categories
        st.markdown("---")
        st.subheader("🧪 Protocol Categories")

        categories = {}
        for protocol in PROTOCOLS:
            cat = protocol['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(protocol)

        selected_category = st.selectbox(
            "Select Category",
            options=list(categories.keys()),
            key="sidebar_category"
        )

        if selected_category:
            st.caption(f"{len(categories[selected_category])} protocols available")

        # Quick Stats
        st.markdown("---")
        st.subheader("📊 Quick Stats")

        try:
            stats = st.session_state.db.get_dashboard_stats()

            # Service Requests
            sr_stats = {s['status']: s['count'] for s in stats.get('service_requests', [])}
            st.metric("Active Requests", sr_stats.get('in_progress', 0))

            # Protocol Executions
            pe_stats = {s['status']: s['count'] for s in stats.get('protocol_executions', [])}
            st.metric("Running Tests", pe_stats.get('in_progress', 0))

        except Exception as e:
            st.error(f"Error loading stats: {e}")

        # Footer
        st.markdown("---")
        st.caption(f"v1.0.0 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# ============================================
# HOME PAGE CONTENT
# ============================================

def render_home():
    """Render home page"""

    # Header
    st.title("🔬 PV Testing Protocol System")
    st.markdown("### Unified Production Application")

    st.markdown("""
    Welcome to the **PV Testing Protocol System** - a comprehensive platform for managing
    and executing all photovoltaic module testing protocols with complete workflow orchestration,
    real-time dashboards, and data traceability.
    """)

    # Key Features
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.info("**📋 54 Protocols**\nComplete protocol coverage")

    with col2:
        st.success("**🔄 Workflow**\nEnd-to-end orchestration")

    with col3:
        st.warning("**📊 Dashboards**\nReal-time KPI monitoring")

    with col4:
        st.error("**🔗 Traceability**\nComplete audit trail")

    # Quick Start
    st.markdown("---")
    st.subheader("🚀 Quick Start Guide")

    st.markdown("""
    ### Typical Workflow:

    1. **📝 Create Service Request** - Submit new testing request
    2. **🔍 Incoming Inspection** - Inspect and log samples
    3. **⚙️ Equipment Planning** - Allocate resources
    4. **🎯 Select Protocol** - Choose from 54 protocols
    5. **🧪 Execute Protocol** - Run tests and record data
    6. **📊 Monitor Progress** - Track on dashboards
    7. **📄 Generate Reports** - Create compliance reports
    8. **🔗 Verify Traceability** - Complete audit trail
    """)

    # Protocol Overview
    st.markdown("---")
    st.subheader("🧪 Available Protocols")

    # Group by category
    categories = {}
    for protocol in PROTOCOLS:
        cat = protocol['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(protocol)

    # Display in tabs
    tabs = st.tabs(list(categories.keys()))

    for tab, (category, protocols) in zip(tabs, categories.items()):
        with tab:
            st.markdown(f"**{len(protocols)} protocols in {category} category**")

            # Display as table
            protocol_data = []
            for p in protocols:
                protocol_data.append({
                    "ID": p['id'],
                    "Protocol Name": p['name'],
                    "Standard": p['standard']
                })

            st.dataframe(protocol_data, use_container_width=True, hide_index=True)

    # Recent Activity
    st.markdown("---")
    st.subheader("📈 Recent Activity")

    try:
        stats = st.session_state.db.get_dashboard_stats()
        recent = stats.get('recent_activity', [])

        if recent:
            for activity in recent[:5]:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.text(activity.get('protocol_name', 'N/A'))
                with col2:
                    status = activity.get('status', 'unknown')
                    if status == 'completed':
                        st.success(status.upper())
                    elif status == 'in_progress':
                        st.warning(status.upper())
                    else:
                        st.info(status.upper())
                with col3:
                    st.caption(activity.get('created_at', ''))
        else:
            st.info("No recent activity")

    except Exception as e:
        st.error(f"Error loading activity: {e}")

    # Core Principles
    st.markdown("---")
    st.subheader("🎯 Core Principles")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **🧩 Modularity**
        - Each protocol is self-contained
        - Plug-and-play architecture
        - Easy to extend and customize

        **📈 Scalability**
        - Optimized for large datasets
        - Concurrent execution support
        - Cloud-ready deployment
        """)

    with col2:
        st.markdown("""
        **🔄 Continuous Improvement**
        - Protocol versioning
        - Feedback integration
        - Regular updates

        **🔗 Complete Interlinkages**
        - Request → Inspection → Equipment → Protocol → Report
        - Bidirectional navigation
        - Full data traceability
        """)

    # Footer
    st.markdown("---")
    st.info("""
    💡 **Tip:** Use the sidebar to navigate between different sections.
    Start with **Service Request** to begin a new testing workflow.
    """)

# ============================================
# MAIN APPLICATION
# ============================================

def main():
    """Main application entry point"""

    # Render sidebar
    render_sidebar()

    # Render home page
    render_home()

if __name__ == "__main__":
    main()
