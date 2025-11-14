"""
Main Streamlit Application for PV Testing Protocol Framework
"""
import streamlit as st
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings

# Page configuration
st.set_page_config(
    page_title=settings.APP_NAME,
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .protocol-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
        background-color: #f8f9fa;
    }
    .metric-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #ffffff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("Navigation")
st.sidebar.markdown("---")

# Protocol categories
protocols = {
    "Electrical Performance": [
        ("PVTP-010", "Flash Test / STC Performance"),
        ("PVTP-011", "I-V Curve Characterization"),
        ("PVTP-012", "Low Irradiance Performance"),
        ("PVTP-013", "Temperature Coefficient"),
        ("PVTP-014", "Spectral Response"),
        ("PVTP-015", "Dark I-V Analysis")
    ]
}

# Main navigation menu
page = st.sidebar.radio(
    "Select Page",
    ["Dashboard", "Protocol Selection", "Test Execution", "Reports", "QC Review", "Settings"]
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Version:** {settings.APP_VERSION}")
st.sidebar.markdown(f"**Environment:** {'DEBUG' if settings.DEBUG else 'PRODUCTION'}")

# Main content area
if page == "Dashboard":
    st.markdown('<h1 class="main-header">⚡ PV Testing Dashboard</h1>', unsafe_allow_html=True)

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Active Tests", "12", "+3")
    with col2:
        st.metric("Completed Today", "8", "+2")
    with col3:
        st.metric("QC Pass Rate", "95.2%", "+1.5%")
    with col4:
        st.metric("Avg Uncertainty", "±2.8%", "-0.3%")

    st.markdown("---")

    # Recent tests
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("📊 Recent Test Activity")

        # Sample data - would be from database
        import pandas as pd

        test_data = pd.DataFrame({
            'Test ID': ['TEST-001', 'TEST-002', 'TEST-003', 'TEST-004', 'TEST-005'],
            'Protocol': ['PVTP-010', 'PVTP-011', 'PVTP-010', 'PVTP-013', 'PVTP-012'],
            'Sample ID': ['MOD-A-001', 'MOD-A-002', 'MOD-B-001', 'MOD-C-001', 'MOD-A-003'],
            'Status': ['Completed', 'In Progress', 'Completed', 'QC Review', 'Completed'],
            'QC': ['✅ Pass', '⏳ Pending', '✅ Pass', '⚠️ Warning', '✅ Pass'],
            'Date': ['2025-01-12', '2025-01-12', '2025-01-12', '2025-01-11', '2025-01-11']
        })

        st.dataframe(test_data, use_container_width=True)

    with col_right:
        st.subheader("📈 Test Distribution")

        # Protocol distribution
        protocol_counts = pd.DataFrame({
            'Protocol': ['PVTP-010', 'PVTP-011', 'PVTP-012', 'PVTP-013', 'PVTP-014', 'PVTP-015'],
            'Count': [45, 38, 22, 15, 8, 12]
        })

        st.bar_chart(protocol_counts.set_index('Protocol'))

    st.markdown("---")

    # Protocol quick access
    st.subheader("🔬 Electrical Performance Protocols")

    cols = st.columns(3)

    for idx, (proto_id, proto_name) in enumerate(protocols["Electrical Performance"]):
        with cols[idx % 3]:
            with st.container():
                st.markdown(f"**{proto_id}**")
                st.markdown(f"*{proto_name}*")
                if st.button(f"Start Test", key=f"btn_{proto_id}"):
                    st.switch_page(f"pages/test_{proto_id.lower().replace('-', '_')}.py")

elif page == "Protocol Selection":
    st.markdown('<h1 class="main-header">📋 Protocol Selection</h1>', unsafe_allow_html=True)

    st.markdown("### Available Protocols")

    for category, protocol_list in protocols.items():
        st.subheader(f"**{category}**")

        for proto_id, proto_name in protocol_list:
            with st.expander(f"{proto_id}: {proto_name}"):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"**Protocol ID:** {proto_id}")
                    st.markdown(f"**Category:** {category}")
                    st.markdown(f"**Estimated Duration:** 45-90 minutes")
                    st.markdown("**Description:** Comprehensive testing protocol with automated analysis and QC checks.")

                with col2:
                    st.button("View Details", key=f"view_{proto_id}")
                    st.button("Start Test", key=f"start_{proto_id}", type="primary")

elif page == "Test Execution":
    st.markdown('<h1 class="main-header">🧪 Test Execution</h1>', unsafe_allow_html=True)
    st.info("Select a protocol from the Protocol Selection page to begin testing.")

elif page == "Reports":
    st.markdown('<h1 class="main-header">📄 Reports</h1>', unsafe_allow_html=True)

    st.subheader("Generate Reports")

    col1, col2 = st.columns(2)

    with col1:
        test_id = st.selectbox("Select Test", ["TEST-001", "TEST-002", "TEST-003"])
        report_type = st.selectbox("Report Type", ["Test Report (PDF)", "Certificate (PDF)", "Data Export (Excel)", "Raw Data (CSV)"])

    with col2:
        include_charts = st.checkbox("Include Charts", value=True)
        include_raw_data = st.checkbox("Include Raw Data", value=False)

    if st.button("Generate Report", type="primary"):
        st.success("✅ Report generated successfully!")
        st.download_button("Download Report", data="Sample report data", file_name="report.pdf")

elif page == "QC Review":
    st.markdown('<h1 class="main-header">✅ Quality Control Review</h1>', unsafe_allow_html=True)

    st.subheader("Tests Awaiting QC Review")

    # Sample QC data
    qc_data = pd.DataFrame({
        'Test ID': ['TEST-004', 'TEST-006'],
        'Protocol': ['PVTP-013', 'PVTP-010'],
        'Sample ID': ['MOD-C-001', 'MOD-D-001'],
        'Issue': ['Temperature coefficient outside typical range', 'Low fill factor detected'],
        'Severity': ['Warning', 'Major'],
        'Date': ['2025-01-11', '2025-01-10']
    })

    st.dataframe(qc_data, use_container_width=True)

    if st.button("Review Selected Tests"):
        st.info("Opening QC review interface...")

elif page == "Settings":
    st.markdown('<h1 class="main-header">⚙️ Settings</h1>', unsafe_allow_html=True)

    tabs = st.tabs(["General", "Database", "Integration", "Equipment"])

    with tabs[0]:
        st.subheader("General Settings")
        st.text_input("Laboratory Name", value=settings.REPORT_COMPANY_NAME)
        st.text_input("Default Operator", value="")
        st.selectbox("Temperature Unit", ["°C", "°F", "K"], index=0)

    with tabs[1]:
        st.subheader("Database Configuration")
        st.text_input("Database URL", value=settings.DATABASE_URL, type="password")
        st.number_input("Connection Pool Size", value=5, min_value=1, max_value=20)

    with tabs[2]:
        st.subheader("External Integrations")
        st.text_input("LIMS API URL", value=settings.LIMS_API_URL or "")
        st.text_input("QMS API URL", value=settings.QMS_API_URL or "")
        st.text_input("PM Dashboard URL", value=settings.PM_DASHBOARD_URL or "")

    with tabs[3]:
        st.subheader("Equipment Management")
        st.info("Equipment calibration tracking and maintenance scheduling")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("© 2025 PV Testing Laboratory")
