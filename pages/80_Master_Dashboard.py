"""
Master Dashboard
Real-time overview of PV Testing operations
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.database.db_manager import DatabaseManager

st.set_page_config(
    page_title="Master Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
if 'db' not in st.session_state:
    st.session_state.db = DatabaseManager()

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_kpi_metrics() -> Dict:
    """Get KPI metrics for dashboard"""
    db = st.session_state.db

    # Total requests
    total_requests_query = "SELECT COUNT(*) as count FROM service_requests"
    total_requests = db.execute_query(total_requests_query)[0]['count']

    # Active tests (in_progress)
    active_tests_query = """
        SELECT COUNT(*) as count
        FROM protocol_executions
        WHERE status = 'in_progress'
    """
    active_tests = db.execute_query(active_tests_query)[0]['count']

    # Completion rate
    completed_query = """
        SELECT COUNT(*) as count
        FROM protocol_executions
        WHERE status = 'completed'
    """
    completed = db.execute_query(completed_query)[0]['count']

    total_executions_query = "SELECT COUNT(*) as count FROM protocol_executions"
    total_executions = db.execute_query(total_executions_query)[0]['count']

    completion_rate = (completed / total_executions * 100) if total_executions > 0 else 0

    # Tests today
    tests_today_query = """
        SELECT COUNT(*) as count
        FROM protocol_executions
        WHERE DATE(created_at) = DATE('now')
    """
    tests_today = db.execute_query(tests_today_query)[0]['count']

    # Pending requests
    pending_query = """
        SELECT COUNT(*) as count
        FROM service_requests
        WHERE status = 'pending'
    """
    pending_requests = db.execute_query(pending_query)[0]['count']

    # Open NCs
    nc_query = """
        SELECT COUNT(*) as count
        FROM nc_register
        WHERE status IN ('open', 'in_progress')
    """
    open_ncs = db.execute_query(nc_query)[0]['count']

    return {
        'total_requests': total_requests,
        'active_tests': active_tests,
        'completion_rate': completion_rate,
        'tests_today': tests_today,
        'pending_requests': pending_requests,
        'open_ncs': open_ncs,
        'total_executions': total_executions,
        'completed': completed
    }

def get_tests_by_status() -> List[Dict]:
    """Get test distribution by status"""
    query = """
        SELECT status, COUNT(*) as count
        FROM protocol_executions
        GROUP BY status
    """
    return st.session_state.db.execute_query(query)

def get_recent_activity(limit: int = 10) -> List[Dict]:
    """Get recent test activity"""
    query = f"""
        SELECT
            pe.execution_id,
            pe.protocol_name,
            pe.status,
            pe.test_result,
            pe.created_at,
            pe.updated_at,
            sr.customer_name,
            sr.project_name
        FROM protocol_executions pe
        LEFT JOIN service_requests sr ON pe.request_id = sr.request_id
        ORDER BY pe.updated_at DESC
        LIMIT {limit}
    """
    return st.session_state.db.execute_query(query)

def get_protocol_distribution() -> List[Dict]:
    """Get distribution of protocols"""
    query = """
        SELECT
            protocol_id,
            protocol_name,
            COUNT(*) as count,
            status
        FROM protocol_executions
        GROUP BY protocol_id, protocol_name, status
        ORDER BY count DESC
    """
    return st.session_state.db.execute_query(query)

def get_timeline_data() -> List[Dict]:
    """Get timeline data for last 30 days"""
    query = """
        SELECT
            DATE(created_at) as date,
            COUNT(*) as count,
            status
        FROM protocol_executions
        WHERE created_at >= DATE('now', '-30 days')
        GROUP BY DATE(created_at), status
        ORDER BY date
    """
    return st.session_state.db.execute_query(query)

# ============================================
# PAGE HEADER
# ============================================

st.title("📊 Master Dashboard")
st.markdown("### Real-time Overview of PV Testing Operations")
st.markdown("---")

# Refresh button
col1, col2, col3 = st.columns([6, 1, 1])
with col3:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

# ============================================
# KPI CARDS
# ============================================

try:
    metrics = get_kpi_metrics()

    st.subheader("📈 Key Performance Indicators")

    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)

    with kpi_col1:
        st.metric(
            label="Total Requests",
            value=metrics['total_requests'],
            delta=None
        )

    with kpi_col2:
        st.metric(
            label="Active Tests",
            value=metrics['active_tests'],
            delta=None
        )

    with kpi_col3:
        st.metric(
            label="Completion Rate",
            value=f"{metrics['completion_rate']:.1f}%",
            delta=None
        )

    with kpi_col4:
        st.metric(
            label="Tests Today",
            value=metrics['tests_today'],
            delta=None
        )

    with kpi_col5:
        st.metric(
            label="Pending Requests",
            value=metrics['pending_requests'],
            delta=None
        )

    with kpi_col6:
        st.metric(
            label="Open NCs",
            value=metrics['open_ncs'],
            delta=None if metrics['open_ncs'] == 0 else f"-{metrics['open_ncs']}"
        )

    st.markdown("---")

    # ============================================
    # CHARTS ROW 1
    # ============================================

    st.subheader("📊 Test Analytics")

    chart_col1, chart_col2 = st.columns(2)

    # Tests by Status Chart
    with chart_col1:
        st.markdown("#### Tests by Status")
        status_data = get_tests_by_status()

        if status_data:
            # Create pie chart
            fig_status = go.Figure(data=[go.Pie(
                labels=[item['status'] for item in status_data],
                values=[item['count'] for item in status_data],
                hole=0.3,
                marker=dict(
                    colors=['#00CC96', '#636EFA', '#FFA15A', '#EF553B', '#AB63FA', '#B6E880']
                )
            )])

            fig_status.update_layout(
                height=350,
                margin=dict(t=30, b=0, l=0, r=0),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )

            st.plotly_chart(fig_status, use_container_width=True)
        else:
            st.info("No test data available")

    # Protocol Distribution Chart
    with chart_col2:
        st.markdown("#### Top Protocols")
        protocol_data = get_protocol_distribution()

        if protocol_data:
            # Group by protocol_id and sum counts
            protocol_summary = {}
            for item in protocol_data:
                protocol_id = item['protocol_id']
                if protocol_id not in protocol_summary:
                    protocol_summary[protocol_id] = {
                        'name': item['protocol_name'],
                        'count': 0
                    }
                protocol_summary[protocol_id]['count'] += item['count']

            # Sort by count and take top 10
            top_protocols = sorted(
                protocol_summary.items(),
                key=lambda x: x[1]['count'],
                reverse=True
            )[:10]

            fig_protocols = go.Figure(data=[go.Bar(
                x=[item[1]['count'] for item in top_protocols],
                y=[f"{item[0]}: {item[1]['name'][:30]}" for item in top_protocols],
                orientation='h',
                marker=dict(color='#636EFA')
            )])

            fig_protocols.update_layout(
                height=350,
                margin=dict(t=30, b=0, l=0, r=0),
                xaxis_title="Number of Executions",
                yaxis_title="Protocol"
            )

            st.plotly_chart(fig_protocols, use_container_width=True)
        else:
            st.info("No protocol data available")

    # ============================================
    # TIMELINE CHART
    # ============================================

    st.markdown("#### 📅 Test Timeline (Last 30 Days)")

    timeline_data = get_timeline_data()

    if timeline_data:
        # Prepare data for stacked bar chart
        dates = sorted(list(set([item['date'] for item in timeline_data])))
        statuses = list(set([item['status'] for item in timeline_data]))

        fig_timeline = go.Figure()

        status_colors = {
            'not_started': '#B6E880',
            'in_progress': '#FFA15A',
            'completed': '#00CC96',
            'failed': '#EF553B',
            'paused': '#AB63FA',
            'cancelled': '#636EFA'
        }

        for status in statuses:
            status_counts = []
            for date in dates:
                count = next((item['count'] for item in timeline_data
                            if item['date'] == date and item['status'] == status), 0)
                status_counts.append(count)

            fig_timeline.add_trace(go.Bar(
                name=status.replace('_', ' ').title(),
                x=dates,
                y=status_counts,
                marker=dict(color=status_colors.get(status, '#636EFA'))
            ))

        fig_timeline.update_layout(
            barmode='stack',
            height=300,
            margin=dict(t=30, b=0, l=0, r=0),
            xaxis_title="Date",
            yaxis_title="Number of Tests",
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
        )

        st.plotly_chart(fig_timeline, use_container_width=True)
    else:
        st.info("No timeline data available")

    st.markdown("---")

    # ============================================
    # RECENT ACTIVITY & ALERTS
    # ============================================

    activity_col, alert_col = st.columns([2, 1])

    # Recent Activity
    with activity_col:
        st.subheader("🕐 Recent Activity")

        recent_activity = get_recent_activity(15)

        if recent_activity:
            for activity in recent_activity:
                # Status badge
                status = activity['status']
                if status == 'completed':
                    badge = "✅"
                    color = "green"
                elif status == 'in_progress':
                    badge = "⏳"
                    color = "orange"
                elif status == 'failed':
                    badge = "❌"
                    color = "red"
                else:
                    badge = "⚪"
                    color = "blue"

                # Test result badge
                result = activity.get('test_result')
                if result == 'pass':
                    result_badge = "✓ PASS"
                    result_color = "green"
                elif result == 'fail':
                    result_badge = "✗ FAIL"
                    result_color = "red"
                else:
                    result_badge = ""
                    result_color = "gray"

                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])

                    with col1:
                        st.markdown(f"{badge} **{activity['protocol_name']}**")
                        if activity.get('customer_name'):
                            st.caption(f"Customer: {activity['customer_name']}")
                        if activity.get('project_name'):
                            st.caption(f"Project: {activity['project_name']}")

                    with col2:
                        st.markdown(f":{color}[**{status.upper()}**]")
                        if result_badge:
                            st.markdown(f":{result_color}[{result_badge}]")

                    with col3:
                        st.caption(f"ID: {activity['execution_id'][:12]}...")
                        updated = activity.get('updated_at', activity['created_at'])
                        st.caption(f"Updated: {updated[:10]}")

                    st.markdown("---")
        else:
            st.info("No recent activity")

    # Alerts and Notifications
    with alert_col:
        st.subheader("🔔 Alerts & Notifications")

        # Check for alerts
        alerts = []

        # Pending requests
        if metrics['pending_requests'] > 0:
            alerts.append({
                'type': 'warning',
                'icon': '⚠️',
                'title': 'Pending Requests',
                'message': f"{metrics['pending_requests']} requests awaiting approval"
            })

        # Open NCs
        if metrics['open_ncs'] > 0:
            alerts.append({
                'type': 'error',
                'icon': '🚨',
                'title': 'Open Non-Conformances',
                'message': f"{metrics['open_ncs']} NCs require attention"
            })

        # Check for overdue calibrations
        overdue_cal_query = """
            SELECT COUNT(*) as count
            FROM equipment_planning
            WHERE calibration_status = 'overdue'
        """
        overdue_cal = st.session_state.db.execute_query(overdue_cal_query)[0]['count']

        if overdue_cal > 0:
            alerts.append({
                'type': 'warning',
                'icon': '🔧',
                'title': 'Calibration Overdue',
                'message': f"{overdue_cal} equipment items need calibration"
            })

        # Active tests
        if metrics['active_tests'] > 0:
            alerts.append({
                'type': 'info',
                'icon': '⚡',
                'title': 'Active Tests',
                'message': f"{metrics['active_tests']} tests currently running"
            })

        # Display alerts
        if alerts:
            for alert in alerts:
                if alert['type'] == 'error':
                    st.error(f"{alert['icon']} **{alert['title']}**\n\n{alert['message']}")
                elif alert['type'] == 'warning':
                    st.warning(f"{alert['icon']} **{alert['title']}**\n\n{alert['message']}")
                else:
                    st.info(f"{alert['icon']} **{alert['title']}**\n\n{alert['message']}")
        else:
            st.success("✅ All systems operational")

        # Quick stats
        st.markdown("---")
        st.markdown("#### Quick Stats")
        st.metric("Total Executions", metrics['total_executions'])
        st.metric("Completed Tests", metrics['completed'])
        st.metric("Success Rate", f"{metrics['completion_rate']:.1f}%")

except Exception as e:
    st.error(f"Error loading dashboard: {e}")
    import traceback
    st.code(traceback.format_exc())

# ============================================
# SIDEBAR INFO
# ============================================

with st.sidebar:
    st.markdown("---")
    st.subheader("ℹ️ Dashboard Info")
    st.info("""
    **Master Dashboard**

    Real-time overview of:
    - KPI metrics
    - Test statistics
    - Protocol distribution
    - Recent activity
    - System alerts

    **Auto-refresh:**
    Click Refresh button for latest data

    **Navigation:**
    Use sidebar to access detailed views
    """)

    st.markdown("---")
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
