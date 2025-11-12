"""
Test Protocols Master Dashboard - Main Entry Point
Streamlit multi-page application for test protocol management
"""
import streamlit as st
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from config.config import (
    DASHBOARD_TITLE, DASHBOARD_ICON, PAGE_LAYOUT,
    INITIAL_SIDEBAR_STATE, TOTAL_PROTOCOLS
)
from utils.data_generator import get_sample_data
from utils.helpers import format_datetime

# Page configuration
st.set_page_config(
    page_title=DASHBOARD_TITLE,
    page_icon=DASHBOARD_ICON,
    layout=PAGE_LAYOUT,
    initial_sidebar_state=INITIAL_SIDEBAR_STATE
)

# Custom CSS for modern UI
st.markdown("""
    <style>
    /* Main styling */
    .main {
        padding: 0rem 1rem;
    }

    /* Card styling */
    .info-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        margin: 20px 0;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }

    .feature-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 10px 0;
        transition: transform 0.3s ease;
    }

    .feature-card:hover {
        transform: translateX(5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }

    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: bold;
    }

    /* Button styling */
    .stButton>button {
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        transform: scale(1.05);
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }

    /* Header styling */
    h1 {
        color: #1f77b4;
        font-weight: 800;
    }

    h2 {
        color: #2c3e50;
        font-weight: 700;
    }

    h3 {
        color: #34495e;
        font-weight: 600;
    }

    /* Link styling */
    a {
        text-decoration: none;
        color: #1f77b4;
    }

    a:hover {
        color: #0d5a8f;
    }

    /* Status badge */
    .status-live {
        background-color: #2ca02c;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.title(f"{DASHBOARD_ICON} {DASHBOARD_TITLE}")
st.markdown("### Comprehensive Real-time Monitoring & Analytics for 54 Test Protocols")

# Status indicator
st.markdown(
    '<div style="text-align: right;"><span class="status-live">🟢 LIVE</span></div>',
    unsafe_allow_html=True
)

st.markdown("---")

# Welcome section
st.markdown("""
    <div class="info-card">
        <h2>🎯 Welcome to the Master Dashboard</h2>
        <p style='font-size: 18px;'>
            Your complete solution for test protocol management, featuring real-time visibility,
            advanced analytics, and comprehensive traceability across all testing operations.
        </p>
    </div>
""", unsafe_allow_html=True)

# Quick stats
st.markdown("### 📊 System Overview")

# Load data for quick stats
@st.cache_data(ttl=300)
def load_data():
    return get_sample_data()

try:
    data = load_data()
    protocols = data['protocols']
    service_requests = data['service_requests']
    equipment = data['equipment']

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Protocols",
            value=TOTAL_PROTOCOLS,
            delta=f"{len(protocols)} Active"
        )

    with col2:
        active_requests = len([sr for sr in service_requests if sr.status == "active"])
        st.metric(
            label="Service Requests",
            value=len(service_requests),
            delta=f"{active_requests} Active"
        )

    with col3:
        available_eq = len([eq for eq in equipment if eq.status == "available"])
        st.metric(
            label="Equipment Units",
            value=len(equipment),
            delta=f"{available_eq} Available"
        )

    with col4:
        from models.protocol import ProtocolStatus
        completed = len([p for p in protocols if p.status == ProtocolStatus.COMPLETED])
        st.metric(
            label="Completion Rate",
            value=f"{(completed/len(protocols)*100):.1f}%" if protocols else "0%",
            delta="Target: 95%"
        )

except Exception as e:
    st.warning("⚠️ Sample data loading... Please wait or refresh the page.")

st.markdown("---")

# Feature overview
st.markdown("### 🚀 Key Features")

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("""
        <div class="feature-card">
            <h4>📊 Master Dashboard</h4>
            <p>Real-time protocol execution status, active service requests, pending inspections,
            equipment utilization, and interactive Gantt charts for timeline visualization.</p>
        </div>

        <div class="feature-card">
            <h4>📈 Protocol Analytics</h4>
            <p>Individual protocol performance metrics, trend analysis, comparative analysis,
            statistical process control charts, and predictive maintenance indicators.</p>
        </div>

        <div class="feature-card">
            <h4>🔍 Data Traceability</h4>
            <p>Complete audit trail visualization with interactive flowcharts tracking the journey
            from service request to inspection to protocol execution to final report.</p>
        </div>

        <div class="feature-card">
            <h4>🎯 KPI Dashboard</h4>
            <p>Comprehensive KPI tracking including throughput metrics, TAT analysis,
            pass/fail rates, equipment efficiency, and quality metrics.</p>
        </div>

        <div class="feature-card">
            <h4>📊 Interactive Visualizations</h4>
            <p>Plotly-based interactive charts, heat maps, Sankey diagrams, real-time gauges,
            and time-series analysis with zoom/pan capabilities.</p>
        </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown("""
        <div class="feature-card">
            <h4>📄 Report Generator</h4>
            <p>One-click report generation, custom report builder, scheduled automated reports,
            multi-format export (PDF/Excel/CSV), and email distribution.</p>
        </div>

        <div class="feature-card">
            <h4>🔎 Search & Filter</h4>
            <p>Global search across all modules, advanced filters by date range and protocol type,
            saved search presets, and quick access to recent items.</p>
        </div>

        <div class="feature-card">
            <h4>🔔 Notification System</h4>
            <p>Real-time alerts for critical events, QC failure notifications,
            equipment maintenance reminders, and customizable notification preferences.</p>
        </div>

        <div class="feature-card">
            <h4>🔌 Analytics API</h4>
            <p>REST endpoints for dashboard data, real-time data streaming, export APIs,
            and integration capabilities with BI tools.</p>
        </div>

        <div class="feature-card">
            <h4>📱 Mobile-Responsive</h4>
            <p>Dashboard optimized for tablets and phones, touch-friendly controls,
            responsive charts and tables for on-the-go access.</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Navigation guide
st.markdown("### 🧭 Navigation Guide")

st.info("""
**Use the sidebar** (←) to navigate between different modules:

- **Dashboard** - Real-time monitoring and overview
- **Traceability** - Complete audit trail and data journey
- **KPI Dashboard** - Key performance indicators and metrics
- **Reports** - Generate and manage reports

Each page offers comprehensive functionality with filters, export options, and interactive visualizations.
""")

# Quick actions
st.markdown("### ⚡ Quick Actions")

action_col1, action_col2, action_col3, action_col4 = st.columns(4)

with action_col1:
    if st.button("📊 View Dashboard", use_container_width=True, type="primary"):
        st.switch_page("pages/Dashboard.py")

with action_col2:
    if st.button("🔍 Search Data", use_container_width=True):
        st.switch_page("pages/Traceability.py")

with action_col3:
    if st.button("📈 View KPIs", use_container_width=True):
        st.switch_page("pages/KPI_Dashboard.py")

with action_col4:
    if st.button("📄 Generate Report", use_container_width=True):
        st.switch_page("pages/Reports.py")

# System information
st.markdown("---")
st.markdown("### ℹ️ System Information")

info_col1, info_col2, info_col3 = st.columns(3)

with info_col1:
    st.markdown("""
        **Version:** 1.0.0
        **Last Updated:** {}
        **Status:** 🟢 Operational
    """.format(format_datetime(datetime.now())))

with info_col2:
    st.markdown("""
        **Total Protocols:** 54
        **Protocol Categories:** 8
        **Supported Formats:** PDF, Excel, CSV, JSON
    """)

with info_col3:
    st.markdown("""
        **API Version:** v1
        **Theme Support:** Light/Dark
        **Languages:** English (more coming soon)
    """)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: gray; padding: 20px;'>
        <p><strong>Test Protocols Master Dashboard & Analytics Engine v1.0</strong></p>
        <p>Modular PV Testing Protocol Framework - JSON-based dynamic templates</p>
        <p>Integrated with LIMS, QMS, and Project Management Systems</p>
        <p style='font-size: 12px; margin-top: 10px;'>
            For support or feedback, please contact your system administrator
        </p>
    </div>
""", unsafe_allow_html=True)

# Sidebar information
with st.sidebar:
    st.image("https://via.placeholder.com/200x80/1f77b4/ffffff?text=Test+Protocols", use_container_width=True)

    st.markdown("---")

    st.markdown("### 📱 Quick Links")
    st.markdown("- [Dashboard](Dashboard)")
    st.markdown("- [Traceability](Traceability)")
    st.markdown("- [KPI Dashboard](KPI_Dashboard)")
    st.markdown("- [Reports](Reports)")

    st.markdown("---")

    st.markdown("### 📊 Live Stats")
    try:
        data = load_data()
        notifications = data['notifications']
        unread = len([n for n in notifications if not n.read])

        st.metric("Unread Notifications", unread)
        st.metric("Active Protocols", len([p for p in data['protocols'] if p.status.value == 'in_progress']))

    except:
        pass

    st.markdown("---")

    st.markdown("### ⚙️ Settings")
    theme = st.selectbox("Theme", ["Light", "Dark"], disabled=True)
    st.info("Theme switching coming soon!")

    st.markdown("---")

    st.markdown(
        f"<div style='text-align: center; font-size: 11px; color: gray;'>"
        f"Last refresh: {format_datetime(datetime.now(), '%H:%M:%S')}"
        f"</div>",
        unsafe_allow_html=True
    )
