"""
Solar PV Testing Protocol - Unified LIMS-QMS System
====================================================
Main Application Entry Point

This is the master integration point for all 54 solar PV testing protocols,
providing a unified interface for Service Request → Inspection → Equipment → Testing workflow.
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import configuration
from config.settings import AppConfig, setup_page_config
from config.database import init_database
from components.navigation import render_sidebar_navigation, render_header
from components.analytics_engine import get_dashboard_metrics

# Initialize app configuration
setup_page_config(
    page_title="Solar PV Testing LIMS-QMS",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
db_session = init_database()


def main():
    """Main application entry point - Home Dashboard"""

    # Render header and navigation
    render_header("Solar PV Testing LIMS-QMS System")
    render_sidebar_navigation()

    # Main dashboard content
    st.markdown("""
    ## 🏠 Welcome to the Solar PV Testing LIMS-QMS System

    A comprehensive, production-ready platform for managing all aspects of solar PV module
    testing, from service requests through final reporting.
    """)

    # System overview
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="📋 Active Service Requests",
            value=get_dashboard_metrics('active_requests'),
            delta=get_dashboard_metrics('requests_delta')
        )

    with col2:
        st.metric(
            label="🔬 Tests in Progress",
            value=get_dashboard_metrics('active_tests'),
            delta=get_dashboard_metrics('tests_delta')
        )

    with col3:
        st.metric(
            label="⚙️ Equipment Utilization",
            value=f"{get_dashboard_metrics('equipment_utilization')}%",
            delta=f"{get_dashboard_metrics('equipment_delta')}%"
        )

    with col4:
        st.metric(
            label="✅ Completed This Month",
            value=get_dashboard_metrics('completed_month'),
            delta=get_dashboard_metrics('completed_delta')
        )

    st.divider()

    # Quick Actions
    st.subheader("🚀 Quick Actions")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📝 New Service Request", use_container_width=True, type="primary"):
            st.switch_page("pages/2_📋_Service_Request.py")

    with col2:
        if st.button("📦 Incoming Inspection", use_container_width=True):
            st.switch_page("pages/3_📦_Incoming_Inspection.py")

    with col3:
        if st.button("⚙️ Book Equipment", use_container_width=True):
            st.switch_page("pages/4_⚙️_Equipment_Booking.py")

    with col4:
        if st.button("🔬 Start Testing", use_container_width=True):
            st.switch_page("pages/5_🔬_Test_Protocols.py")

    st.divider()

    # Recent Activity and Analytics
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview",
        "🔄 Recent Activity",
        "📈 Analytics",
        "⚠️ Alerts"
    ])

    with tab1:
        render_overview_dashboard()

    with tab2:
        render_recent_activity()

    with tab3:
        render_analytics_dashboard()

    with tab4:
        render_alerts_panel()

    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>Solar PV Testing LIMS-QMS System v1.0.0 |
        54 Testing Protocols | Complete Traceability | Production Ready</p>
    </div>
    """, unsafe_allow_html=True)


def render_overview_dashboard():
    """Render the overview dashboard with key metrics"""
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📋 Protocol Coverage")
        protocol_data = {
            "Performance Testing (P1-P12)": 12,
            "Degradation Testing (P13-P27)": 15,
            "Environmental Testing (P28-P39)": 12,
            "Mechanical Testing (P40-P47)": 8,
            "Safety & Electrical (P48-P54)": 7
        }

        for category, count in protocol_data.items():
            st.progress(count / 15, text=f"{category}: {count} protocols")

    with col2:
        st.markdown("### 🎯 System Status")
        st.success("✅ All systems operational")
        st.info("📊 Database: Connected")
        st.info("⚙️ Equipment: 12/15 available")
        st.info("👥 Active Users: 8")


def render_recent_activity():
    """Render recent activity feed"""
    st.markdown("### Recent Activity")

    activities = [
        {"time": "2 minutes ago", "user": "John Doe", "action": "Completed test", "protocol": "P1 - I-V Performance"},
        {"time": "15 minutes ago", "user": "Jane Smith", "action": "Started test", "protocol": "P28 - Humidity Freeze"},
        {"time": "1 hour ago", "user": "Bob Wilson", "action": "Created service request", "protocol": "SR-2024-0156"},
        {"time": "2 hours ago", "user": "Alice Brown", "action": "Equipment booking", "protocol": "Solar Simulator"},
    ]

    for activity in activities:
        with st.container():
            col1, col2, col3 = st.columns([2, 3, 3])
            with col1:
                st.caption(activity['time'])
            with col2:
                st.text(activity['user'])
            with col3:
                st.text(f"{activity['action']}: {activity['protocol']}")
            st.divider()


def render_analytics_dashboard():
    """Render analytics dashboard with charts"""
    import plotly.graph_objects as go
    import plotly.express as px
    import pandas as pd

    st.markdown("### 📈 Testing Analytics")

    col1, col2 = st.columns(2)

    with col1:
        # Protocol distribution pie chart
        fig = go.Figure(data=[go.Pie(
            labels=['Performance', 'Degradation', 'Environmental', 'Mechanical', 'Safety'],
            values=[25, 30, 20, 15, 10],
            hole=.3
        )])
        fig.update_layout(title="Tests by Protocol Category", height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Monthly test trend
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        tests = [45, 52, 48, 65, 70, 68]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=months, y=tests,
            mode='lines+markers',
            name='Tests Completed',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=10)
        ))
        fig.update_layout(
            title="Monthly Test Completion Trend",
            xaxis_title="Month",
            yaxis_title="Tests Completed",
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)

    # Equipment utilization
    st.markdown("### ⚙️ Equipment Utilization (Last 7 Days)")
    equipment_data = pd.DataFrame({
        'Equipment': ['Solar Simulator', 'Climate Chamber', 'EL Tester', 'Pull Tester', 'Insulation Tester'],
        'Utilization': [85, 72, 68, 45, 55]
    })

    fig = px.bar(
        equipment_data,
        x='Equipment',
        y='Utilization',
        color='Utilization',
        color_continuous_scale='Blues'
    )
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)


def render_alerts_panel():
    """Render alerts and notifications panel"""
    st.markdown("### ⚠️ System Alerts & Notifications")

    # Critical alerts
    st.error("🔴 **Critical**: Solar Simulator requires calibration (Due: Tomorrow)")

    # Warnings
    st.warning("🟡 **Warning**: Climate Chamber maintenance scheduled for next week")
    st.warning("🟡 **Warning**: 3 service requests pending approval")

    # Info
    st.info("🔵 **Info**: New protocol P55 template available for review")
    st.info("🔵 **Info**: Database backup completed successfully")

    # Success
    st.success("🟢 **Success**: All pending reports generated and distributed")


if __name__ == "__main__":
    main()
