"""
Analytics Engine - Cross-protocol analytics and KPIs
===================================================
Provides unified analytics across all testing activities.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from sqlalchemy import func
import streamlit as st

from config.database import get_db
from database.models import (
    ServiceRequest, TestExecution, Equipment,
    EquipmentBooking, TestStatus, RequestStatus
)


def get_dashboard_metrics(metric_name: str) -> Any:
    """
    Get dashboard metric value

    Args:
        metric_name: Name of the metric to retrieve

    Returns:
        Metric value (can be int, float, str, etc.)
    """
    metrics_map = {
        'active_requests': get_active_requests_count,
        'requests_delta': get_requests_delta,
        'active_tests': get_active_tests_count,
        'tests_delta': get_tests_delta,
        'equipment_utilization': get_equipment_utilization,
        'equipment_delta': get_equipment_delta,
        'completed_month': get_completed_this_month,
        'completed_delta': get_completed_delta
    }

    metric_func = metrics_map.get(metric_name)
    if metric_func:
        try:
            return metric_func()
        except Exception as e:
            print(f"Error getting metric {metric_name}: {e}")
            return 0
    return 0


def get_active_requests_count() -> int:
    """Get count of active service requests"""
    try:
        with get_db() as db:
            count = db.query(ServiceRequest).filter(
                ServiceRequest.status.in_([
                    RequestStatus.SUBMITTED,
                    RequestStatus.APPROVED,
                    RequestStatus.IN_PROGRESS
                ])
            ).count()
            return count
    except:
        return 5  # Demo data


def get_requests_delta() -> int:
    """Get change in requests from last week"""
    return 2  # Demo data


def get_active_tests_count() -> int:
    """Get count of tests in progress"""
    try:
        with get_db() as db:
            count = db.query(TestExecution).filter(
                TestExecution.status == TestStatus.IN_PROGRESS
            ).count()
            return count
    except:
        return 8  # Demo data


def get_tests_delta() -> int:
    """Get change in active tests"""
    return 3  # Demo data


def get_equipment_utilization() -> int:
    """Get equipment utilization percentage"""
    try:
        with get_db() as db:
            total_equipment = db.query(Equipment).count()
            if total_equipment == 0:
                return 0

            in_use = db.query(Equipment).filter(
                Equipment.status == 'in_use'
            ).count()

            return int((in_use / total_equipment) * 100)
    except:
        return 75  # Demo data


def get_equipment_delta() -> int:
    """Get change in equipment utilization"""
    return 5  # Demo data


def get_completed_this_month() -> int:
    """Get tests completed this month"""
    try:
        with get_db() as db:
            start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0)
            count = db.query(TestExecution).filter(
                TestExecution.status == TestStatus.COMPLETED,
                TestExecution.completed_at >= start_of_month
            ).count()
            return count
    except:
        return 24  # Demo data


def get_completed_delta() -> int:
    """Get change in completed tests"""
    return 6  # Demo data


def get_protocol_distribution() -> Dict[str, int]:
    """
    Get distribution of tests by protocol category

    Returns:
        Dictionary mapping category to test count
    """
    try:
        with get_db() as db:
            # This would query actual test data
            # For now, return demo data
            pass
    except:
        pass

    return {
        'Performance': 145,
        'Degradation': 98,
        'Environmental': 76,
        'Mechanical': 54,
        'Safety': 67
    }


def get_monthly_test_trend(months: int = 6) -> pd.DataFrame:
    """
    Get monthly test completion trend

    Args:
        months: Number of months to include

    Returns:
        DataFrame with monthly test counts
    """
    # Generate demo data for the last N months
    import calendar

    end_date = datetime.now()
    data = []

    for i in range(months, 0, -1):
        month_date = end_date - timedelta(days=30 * i)
        month_name = calendar.month_abbr[month_date.month]

        # Demo data - replace with actual queries
        test_count = 40 + (i * 5) + (i % 3) * 10

        data.append({
            'month': month_name,
            'tests': test_count,
            'date': month_date
        })

    return pd.DataFrame(data)


def get_equipment_utilization_data() -> pd.DataFrame:
    """
    Get equipment utilization data for the last 7 days

    Returns:
        DataFrame with equipment utilization
    """
    equipment_data = [
        {'equipment': 'Solar Simulator', 'utilization': 85, 'hours': 68},
        {'equipment': 'Climate Chamber', 'utilization': 72, 'hours': 58},
        {'equipment': 'EL Tester', 'utilization': 68, 'hours': 54},
        {'equipment': 'Pull Tester', 'utilization': 45, 'hours': 36},
        {'equipment': 'Insulation Tester', 'utilization': 55, 'hours': 44},
    ]

    return pd.DataFrame(equipment_data)


def get_test_success_rate() -> Dict[str, float]:
    """
    Get test success/failure rates

    Returns:
        Dictionary with success rate metrics
    """
    return {
        'passed': 85.5,
        'failed': 8.2,
        'pending_review': 6.3
    }


def create_protocol_distribution_chart() -> go.Figure:
    """
    Create pie chart for protocol distribution

    Returns:
        Plotly figure
    """
    data = get_protocol_distribution()

    fig = go.Figure(data=[go.Pie(
        labels=list(data.keys()),
        values=list(data.values()),
        hole=.3,
        marker=dict(
            colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        )
    )])

    fig.update_layout(
        title="Tests by Protocol Category",
        height=400,
        showlegend=True
    )

    return fig


def create_monthly_trend_chart() -> go.Figure:
    """
    Create line chart for monthly test trend

    Returns:
        Plotly figure
    """
    df = get_monthly_test_trend(6)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['month'],
        y=df['tests'],
        mode='lines+markers',
        name='Tests Completed',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=10)
    ))

    fig.update_layout(
        title="Monthly Test Completion Trend",
        xaxis_title="Month",
        yaxis_title="Tests Completed",
        height=400,
        hovermode='x unified'
    )

    return fig


def create_equipment_utilization_chart() -> go.Figure:
    """
    Create bar chart for equipment utilization

    Returns:
        Plotly figure
    """
    df = get_equipment_utilization_data()

    fig = px.bar(
        df,
        x='equipment',
        y='utilization',
        color='utilization',
        color_continuous_scale='Blues',
        text='utilization'
    )

    fig.update_traces(texttemplate='%{text}%', textposition='outside')

    fig.update_layout(
        title="Equipment Utilization (Last 7 Days)",
        xaxis_title="Equipment",
        yaxis_title="Utilization %",
        height=400,
        showlegend=False
    )

    return fig


def create_success_rate_chart() -> go.Figure:
    """
    Create gauge chart for test success rate

    Returns:
        Plotly figure
    """
    success_rate = get_test_success_rate()

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=success_rate['passed'],
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Test Success Rate"},
        delta={'reference': 80},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 60], 'color': "lightgray"},
                {'range': [60, 80], 'color': "gray"},
                {'range': [80, 100], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))

    fig.update_layout(height=300)

    return fig


def get_recent_activity(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get recent system activity

    Args:
        limit: Maximum number of activities to return

    Returns:
        List of activity dictionaries
    """
    # Demo data - replace with actual database queries
    activities = [
        {
            'timestamp': datetime.now() - timedelta(minutes=2),
            'user': 'John Doe',
            'action': 'Completed test',
            'details': 'P1 - I-V Performance',
            'type': 'test_complete'
        },
        {
            'timestamp': datetime.now() - timedelta(minutes=15),
            'user': 'Jane Smith',
            'action': 'Started test',
            'details': 'P28 - Humidity Freeze',
            'type': 'test_start'
        },
        {
            'timestamp': datetime.now() - timedelta(hours=1),
            'user': 'Bob Wilson',
            'action': 'Created service request',
            'details': 'SR-2024-0156',
            'type': 'request_created'
        },
        {
            'timestamp': datetime.now() - timedelta(hours=2),
            'user': 'Alice Brown',
            'action': 'Equipment booking',
            'details': 'Solar Simulator',
            'type': 'booking_created'
        },
    ]

    return activities[:limit]


def get_system_alerts() -> List[Dict[str, Any]]:
    """
    Get system alerts and notifications

    Returns:
        List of alert dictionaries
    """
    alerts = [
        {
            'severity': 'critical',
            'title': 'Solar Simulator requires calibration',
            'message': 'Calibration due tomorrow',
            'timestamp': datetime.now(),
            'type': 'equipment'
        },
        {
            'severity': 'warning',
            'title': 'Climate Chamber maintenance scheduled',
            'message': 'Scheduled for next week',
            'timestamp': datetime.now() - timedelta(hours=3),
            'type': 'equipment'
        },
        {
            'severity': 'warning',
            'title': 'Service requests pending approval',
            'message': '3 requests awaiting supervisor approval',
            'timestamp': datetime.now() - timedelta(hours=5),
            'type': 'workflow'
        },
        {
            'severity': 'info',
            'title': 'New protocol template available',
            'message': 'Protocol P55 ready for review',
            'timestamp': datetime.now() - timedelta(days=1),
            'type': 'system'
        }
    ]

    return alerts


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cached_analytics_data(data_type: str) -> Any:
    """
    Get cached analytics data

    Args:
        data_type: Type of data to retrieve

    Returns:
        Cached data
    """
    data_functions = {
        'protocol_distribution': get_protocol_distribution,
        'monthly_trend': get_monthly_test_trend,
        'equipment_utilization': get_equipment_utilization_data,
        'success_rate': get_test_success_rate,
        'recent_activity': get_recent_activity,
        'system_alerts': get_system_alerts
    }

    func = data_functions.get(data_type)
    if func:
        return func()
    return None
