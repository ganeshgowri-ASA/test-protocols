"""
QA Dashboard
Quality Assurance metrics and monitoring
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
    page_title="QA Dashboard",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
if 'db' not in st.session_state:
    st.session_state.db = DatabaseManager()

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_qc_summary() -> Dict:
    """Get QC checkpoint summary statistics"""
    db = st.session_state.db

    # Total QC checkpoints
    total_query = "SELECT COUNT(*) as count FROM qc_records"
    total = db.execute_query(total_query)[0]['count']

    # QC by status
    status_query = """
        SELECT status, COUNT(*) as count
        FROM qc_records
        GROUP BY status
    """
    status_data = db.execute_query(status_query)

    # Convert to dict
    status_counts = {item['status']: item['count'] for item in status_data}

    # Recent QC activities
    recent_query = """
        SELECT qc_id, checkpoint_name, status, checked_date
        FROM qc_records
        ORDER BY checked_date DESC
        LIMIT 5
    """
    recent = db.execute_query(recent_query)

    return {
        'total': total,
        'pass': status_counts.get('pass', 0),
        'fail': status_counts.get('fail', 0),
        'na': status_counts.get('na', 0),
        'recent': recent
    }

def get_test_pass_fail_stats() -> Dict:
    """Get pass/fail statistics for protocol executions"""
    db = st.session_state.db

    # Overall stats
    stats_query = """
        SELECT test_result, COUNT(*) as count
        FROM protocol_executions
        WHERE test_result IS NOT NULL
        GROUP BY test_result
    """
    stats_data = db.execute_query(stats_query)

    stats = {item['test_result']: item['count'] for item in stats_data}

    # By protocol
    protocol_query = """
        SELECT
            protocol_name,
            test_result,
            COUNT(*) as count
        FROM protocol_executions
        WHERE test_result IS NOT NULL
        GROUP BY protocol_name, test_result
    """
    protocol_stats = db.execute_query(protocol_query)

    return {
        'overall': stats,
        'by_protocol': protocol_stats
    }

def get_nc_register_summary() -> Dict:
    """Get non-conformance register summary"""
    db = st.session_state.db

    # Total NCs
    total_query = "SELECT COUNT(*) as count FROM nc_register"
    total = db.execute_query(total_query)[0]['count']

    # By status
    status_query = """
        SELECT status, COUNT(*) as count
        FROM nc_register
        GROUP BY status
    """
    status_data = db.execute_query(status_query)

    # By severity
    severity_query = """
        SELECT severity, COUNT(*) as count
        FROM nc_register
        GROUP BY severity
    """
    severity_data = db.execute_query(severity_query)

    # Open NCs
    open_query = """
        SELECT nc_id, nc_type, severity, description, detected_date, status
        FROM nc_register
        WHERE status IN ('open', 'in_progress')
        ORDER BY detected_date DESC
    """
    open_ncs = db.execute_query(open_query)

    # Overdue NCs
    overdue_query = """
        SELECT COUNT(*) as count
        FROM nc_register
        WHERE status IN ('open', 'in_progress')
        AND due_date < DATE('now')
    """
    overdue = db.execute_query(overdue_query)[0]['count']

    return {
        'total': total,
        'status': status_data,
        'severity': severity_data,
        'open_ncs': open_ncs,
        'overdue': overdue
    }

def get_quality_trends(days: int = 30) -> List[Dict]:
    """Get quality trends over time"""
    db = st.session_state.db

    query = f"""
        SELECT
            DATE(checked_date) as date,
            status,
            COUNT(*) as count
        FROM qc_records
        WHERE checked_date >= DATE('now', '-{days} days')
        GROUP BY DATE(checked_date), status
        ORDER BY date
    """
    return db.execute_query(query)

def get_action_items() -> List[Dict]:
    """Get outstanding action items"""
    db = st.session_state.db

    # Get open NCs
    nc_query = """
        SELECT
            nc_id as item_id,
            'NC' as item_type,
            description as title,
            severity as priority,
            assigned_to,
            due_date,
            status
        FROM nc_register
        WHERE status IN ('open', 'in_progress')
        ORDER BY
            CASE severity
                WHEN 'critical' THEN 1
                WHEN 'major' THEN 2
                WHEN 'minor' THEN 3
            END,
            due_date
    """
    nc_items = db.execute_query(nc_query)

    # Get pending tasks
    task_query = """
        SELECT
            task_id as item_id,
            'Task' as item_type,
            task_name as title,
            priority,
            assigned_to,
            due_date,
            status
        FROM pm_tasks
        WHERE status IN ('not_started', 'in_progress')
        ORDER BY
            CASE priority
                WHEN 'urgent' THEN 1
                WHEN 'high' THEN 2
                WHEN 'medium' THEN 3
                WHEN 'low' THEN 4
            END,
            due_date
    """
    task_items = db.execute_query(task_query)

    return nc_items + task_items

# ============================================
# PAGE CONTENT
# ============================================

st.title("✅ QA Dashboard")
st.markdown("### Quality Assurance Metrics and Monitoring")
st.markdown("---")

# Refresh button
col1, col2, col3 = st.columns([6, 1, 1])
with col3:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

# ============================================
# QC SUMMARY CARDS
# ============================================

try:
    qc_summary = get_qc_summary()
    nc_summary = get_nc_register_summary()
    pass_fail_stats = get_test_pass_fail_stats()

    st.subheader("📊 QC Checkpoint Summary")

    qc_col1, qc_col2, qc_col3, qc_col4, qc_col5 = st.columns(5)

    with qc_col1:
        st.metric("Total Checkpoints", qc_summary['total'])

    with qc_col2:
        st.metric("Pass", qc_summary['pass'], delta="✓", delta_color="off")

    with qc_col3:
        st.metric("Fail", qc_summary['fail'], delta="✗" if qc_summary['fail'] > 0 else None, delta_color="inverse")

    with qc_col4:
        pass_rate = (qc_summary['pass'] / qc_summary['total'] * 100) if qc_summary['total'] > 0 else 0
        st.metric("Pass Rate", f"{pass_rate:.1f}%")

    with qc_col5:
        st.metric("N/A", qc_summary['na'])

    st.markdown("---")

    # ============================================
    # CHARTS ROW 1
    # ============================================

    st.subheader("📈 Quality Metrics")

    chart_col1, chart_col2 = st.columns(2)

    # Pass/Fail Statistics Chart
    with chart_col1:
        st.markdown("#### Test Results Distribution")

        overall_stats = pass_fail_stats['overall']

        if overall_stats:
            fig_passfail = go.Figure(data=[go.Pie(
                labels=list(overall_stats.keys()),
                values=list(overall_stats.values()),
                hole=0.4,
                marker=dict(
                    colors={
                        'pass': '#00CC96',
                        'fail': '#EF553B',
                        'conditional': '#FFA15A',
                        'na': '#B6E880'
                    }.get(k, '#636EFA') for k in overall_stats.keys()
                )
            )])

            fig_passfail.update_layout(
                height=300,
                margin=dict(t=30, b=0, l=0, r=0),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )

            st.plotly_chart(fig_passfail, use_container_width=True)
        else:
            st.info("No test result data available")

    # NC Register Summary Chart
    with chart_col2:
        st.markdown("#### Non-Conformances by Severity")

        severity_data = nc_summary['severity']

        if severity_data:
            fig_nc = go.Figure(data=[go.Bar(
                x=[item['severity'] for item in severity_data],
                y=[item['count'] for item in severity_data],
                marker=dict(
                    color=['#EF553B' if s['severity'] == 'critical'
                           else '#FFA15A' if s['severity'] == 'major'
                           else '#FFA500' for s in severity_data]
                )
            )])

            fig_nc.update_layout(
                height=300,
                margin=dict(t=30, b=0, l=0, r=0),
                xaxis_title="Severity",
                yaxis_title="Count"
            )

            st.plotly_chart(fig_nc, use_container_width=True)
        else:
            st.info("No NC data available")

    st.markdown("---")

    # ============================================
    # QUALITY TRENDS
    # ============================================

    st.subheader("📊 Quality Trends Over Time")

    # Time range selector
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        trend_days = st.selectbox(
            "Time Range",
            options=[7, 14, 30, 60, 90],
            index=2,
            format_func=lambda x: f"Last {x} days"
        )

    # Get trend data
    trend_data = get_quality_trends(trend_days)

    if trend_data:
        # Prepare data for stacked area chart
        dates = sorted(list(set([item['date'] for item in trend_data])))
        statuses = list(set([item['status'] for item in trend_data]))

        fig_trends = go.Figure()

        status_colors = {
            'pass': '#00CC96',
            'fail': '#EF553B',
            'na': '#B6E880'
        }

        for status in statuses:
            status_counts = []
            for date in dates:
                count = next((item['count'] for item in trend_data
                            if item['date'] == date and item['status'] == status), 0)
                status_counts.append(count)

            fig_trends.add_trace(go.Scatter(
                name=status.upper(),
                x=dates,
                y=status_counts,
                mode='lines+markers',
                stackgroup='one',
                line=dict(width=2),
                marker=dict(size=6, color=status_colors.get(status, '#636EFA'))
            ))

        fig_trends.update_layout(
            height=300,
            margin=dict(t=30, b=0, l=0, r=0),
            xaxis_title="Date",
            yaxis_title="QC Checkpoints",
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
        )

        st.plotly_chart(fig_trends, use_container_width=True)
    else:
        st.info("No trend data available for selected time range")

    st.markdown("---")

    # ============================================
    # NC REGISTER & ACTION ITEMS
    # ============================================

    nc_col, action_col = st.columns([3, 2])

    # Non-Conformance Register
    with nc_col:
        st.subheader("🚨 Non-Conformance Register")

        # Summary metrics
        nc_metric_col1, nc_metric_col2, nc_metric_col3 = st.columns(3)

        with nc_metric_col1:
            st.metric("Total NCs", nc_summary['total'])

        with nc_metric_col2:
            open_count = sum(item['count'] for item in nc_summary['status']
                           if item['status'] in ['open', 'in_progress'])
            st.metric("Open NCs", open_count)

        with nc_metric_col3:
            st.metric("Overdue", nc_summary['overdue'], delta=f"-{nc_summary['overdue']}" if nc_summary['overdue'] > 0 else None)

        # Open NCs List
        st.markdown("#### Open Non-Conformances")

        if nc_summary['open_ncs']:
            for nc in nc_summary['open_ncs'][:10]:  # Limit to 10
                severity = nc.get('severity', 'minor')
                if severity == 'critical':
                    badge = "🔴"
                    color = "red"
                elif severity == 'major':
                    badge = "🟠"
                    color = "orange"
                else:
                    badge = "🟡"
                    color = "normal"

                with st.container():
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown(f"{badge} **{nc.get('nc_id')}** - {nc.get('description', 'N/A')[:60]}")
                        st.caption(f"Type: {nc.get('nc_type', 'N/A')} | Detected: {nc.get('detected_date', 'N/A')[:10]}")

                    with col2:
                        st.markdown(f"**{severity.upper()}**")
                        st.caption(f"Status: {nc.get('status', 'N/A')}")

                    st.markdown("---")

            if len(nc_summary['open_ncs']) > 10:
                st.info(f"... and {len(nc_summary['open_ncs']) - 10} more NCs")
        else:
            st.success("✅ No open non-conformances")

    # Action Items
    with action_col:
        st.subheader("📋 Action Items")

        action_items = get_action_items()

        if action_items:
            st.write(f"**{len(action_items)} Outstanding Items**")

            for item in action_items[:15]:  # Limit to 15
                priority = item.get('priority', 'medium')

                if priority in ['critical', 'urgent']:
                    icon = "🔴"
                elif priority in ['major', 'high']:
                    icon = "🟠"
                else:
                    icon = "🟢"

                with st.container():
                    st.markdown(f"{icon} **[{item.get('item_type')}]** {item.get('title', 'N/A')[:40]}")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.caption(f"Priority: {priority}")
                    with col2:
                        due = item.get('due_date')
                        if due:
                            # Check if overdue
                            if due < datetime.now().strftime('%Y-%m-%d'):
                                st.caption(f"⚠️ Due: {due}")
                            else:
                                st.caption(f"Due: {due}")
                        else:
                            st.caption("Due: Not set")

                    st.markdown("---")

            if len(action_items) > 15:
                st.info(f"... and {len(action_items) - 15} more items")
        else:
            st.success("✅ No outstanding action items")

    st.markdown("---")

    # ============================================
    # RECENT QC ACTIVITY
    # ============================================

    st.subheader("🕐 Recent QC Activity")

    if qc_summary['recent']:
        qc_table_data = []
        for qc in qc_summary['recent']:
            qc_table_data.append({
                'QC ID': qc.get('qc_id', 'N/A'),
                'Checkpoint': qc.get('checkpoint_name', 'N/A'),
                'Status': qc.get('status', 'N/A'),
                'Date': qc.get('checked_date', 'N/A')[:19] if qc.get('checked_date') else 'N/A'
            })

        st.dataframe(qc_table_data, use_container_width=True)
    else:
        st.info("No recent QC activity")

    # ============================================
    # PROTOCOL PASS/FAIL BREAKDOWN
    # ============================================

    st.markdown("---")
    st.subheader("📊 Protocol Performance Breakdown")

    protocol_stats = pass_fail_stats['by_protocol']

    if protocol_stats:
        # Create summary table
        protocol_summary = {}
        for stat in protocol_stats:
            protocol = stat['protocol_name']
            result = stat['test_result']
            count = stat['count']

            if protocol not in protocol_summary:
                protocol_summary[protocol] = {'pass': 0, 'fail': 0, 'conditional': 0, 'total': 0}

            protocol_summary[protocol][result] = count
            protocol_summary[protocol]['total'] += count

        # Convert to table data
        table_data = []
        for protocol, stats in protocol_summary.items():
            total = stats['total']
            pass_rate = (stats['pass'] / total * 100) if total > 0 else 0

            table_data.append({
                'Protocol': protocol[:50],
                'Pass': stats['pass'],
                'Fail': stats['fail'],
                'Conditional': stats.get('conditional', 0),
                'Total': total,
                'Pass Rate': f"{pass_rate:.1f}%"
            })

        # Sort by total (descending)
        table_data.sort(key=lambda x: x['Total'], reverse=True)

        st.dataframe(table_data, use_container_width=True)

        # Create bar chart
        top_protocols = table_data[:10]

        fig_protocol_perf = go.Figure()

        fig_protocol_perf.add_trace(go.Bar(
            name='Pass',
            x=[p['Protocol'] for p in top_protocols],
            y=[p['Pass'] for p in top_protocols],
            marker=dict(color='#00CC96')
        ))

        fig_protocol_perf.add_trace(go.Bar(
            name='Fail',
            x=[p['Protocol'] for p in top_protocols],
            y=[p['Fail'] for p in top_protocols],
            marker=dict(color='#EF553B')
        ))

        fig_protocol_perf.update_layout(
            barmode='group',
            height=400,
            margin=dict(t=30, b=100, l=0, r=0),
            xaxis_title="Protocol",
            yaxis_title="Count",
            xaxis=dict(tickangle=-45),
            legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="center", x=0.5)
        )

        st.plotly_chart(fig_protocol_perf, use_container_width=True)
    else:
        st.info("No protocol performance data available")

except Exception as e:
    st.error(f"Error loading QA dashboard: {e}")
    import traceback
    st.code(traceback.format_exc())

# ============================================
# SIDEBAR INFO
# ============================================

with st.sidebar:
    st.markdown("---")
    st.subheader("ℹ️ Page Info")
    st.info("""
    **QA Dashboard**

    Quality assurance monitoring:
    - QC checkpoint summary
    - Pass/fail statistics
    - Non-conformance register
    - Quality trends
    - Action items
    - Protocol performance

    **Features:**
    - Real-time metrics
    - Trend analysis
    - NC tracking
    - Performance breakdown

    **Usage:**
    - Monitor QC metrics
    - Track open NCs
    - Review action items
    - Analyze trends
    """)

    st.markdown("---")
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
