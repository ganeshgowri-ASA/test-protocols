"""
Data Analysis Module
====================
Analyze test results, generate statistics, and visualize data.
"""

import streamlit as st
from datetime import datetime, timedelta
import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import setup_page_config
from config.database import get_db
from components.navigation import render_header, render_sidebar_navigation
from database import (
    Sample, TestExecution, TestData, ServiceRequest, TestProtocol,
    TestStatus, SampleStatus
)
from sqlalchemy import select, desc, func

# Page configuration
setup_page_config(page_title="Data Analysis", page_icon="📈")

# Render navigation
render_header("Data Analysis", "Analyze test results and generate statistics")
render_sidebar_navigation()


def main():
    """Main data analysis page"""

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Results Overview",
        "📈 Statistical Analysis",
        "🔬 Sample Analysis",
        "📉 Trend Analysis"
    ])

    with tab1:
        render_results_overview()

    with tab2:
        render_statistical_analysis()

    with tab3:
        render_sample_analysis()

    with tab4:
        render_trend_analysis()


def render_results_overview():
    """Render test results overview"""

    st.markdown("### 📊 Test Results Overview")

    with get_db() as db:
        # Overall stats
        total_tests = db.execute(
            select(func.count(TestExecution.id))
        ).scalar() or 0

        completed_tests = db.execute(
            select(func.count(TestExecution.id))
            .where(TestExecution.status == TestStatus.COMPLETED)
        ).scalar() or 0

        passed_tests = db.execute(
            select(func.count(TestExecution.id))
            .where(TestExecution.test_passed == True)
        ).scalar() or 0

        failed_tests = db.execute(
            select(func.count(TestExecution.id))
            .where(TestExecution.test_passed == False)
        ).scalar() or 0

    # Metrics
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Tests", total_tests)
    col2.metric("Completed", completed_tests)
    col3.metric("Passed", passed_tests, delta=f"{(passed_tests/completed_tests*100):.1f}%" if completed_tests > 0 else "0%")
    col4.metric("Failed", failed_tests, delta_color="inverse")

    st.divider()

    # Pass rate by protocol category
    st.markdown("#### Pass Rate by Category")

    protocol_categories = ["performance", "degradation", "environmental", "mechanical", "safety"]

    with get_db() as db:
        category_stats = []

        for category in protocol_categories:
            # Get protocols in category
            protocols = db.execute(
                select(TestProtocol)
                .where(TestProtocol.category == category)
            ).scalars().all()

            protocol_ids = [p.id for p in protocols]

            if protocol_ids:
                total = db.execute(
                    select(func.count(TestExecution.id))
                    .where(TestExecution.protocol_id.in_(protocol_ids))
                    .where(TestExecution.status == TestStatus.COMPLETED)
                ).scalar() or 0

                passed = db.execute(
                    select(func.count(TestExecution.id))
                    .where(TestExecution.protocol_id.in_(protocol_ids))
                    .where(TestExecution.test_passed == True)
                ).scalar() or 0

                pass_rate = (passed / total * 100) if total > 0 else 0

                category_stats.append({
                    'category': category.title(),
                    'total': total,
                    'passed': passed,
                    'pass_rate': pass_rate
                })

        if category_stats:
            cols = st.columns(len(category_stats))

            for idx, stat in enumerate(category_stats):
                with cols[idx]:
                    st.markdown(f"**{stat['category']}**")
                    st.metric(
                        "Pass Rate",
                        f"{stat['pass_rate']:.1f}%",
                        delta=f"{stat['passed']}/{stat['total']} tests"
                    )

    st.divider()

    # Recent test results
    st.markdown("#### Recent Test Results")

    with get_db() as db:
        recent = db.execute(
            select(TestExecution)
            .where(TestExecution.status == TestStatus.COMPLETED)
            .order_by(desc(TestExecution.completed_at))
            .limit(10)
        ).scalars().all()

        if recent:
            for test in recent:
                result_icon = "✅" if test.test_passed else "❌"

                protocol = db.execute(
                    select(TestProtocol).where(TestProtocol.id == test.protocol_id)
                ).scalar()

                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                col1.markdown(f"{result_icon} **{test.execution_number}**")
                col2.markdown(f"{protocol.name if protocol else 'Unknown'}")
                col3.markdown(f"{'PASS' if test.test_passed else 'FAIL'}")
                col4.markdown(f"{test.completed_at.strftime('%Y-%m-%d') if test.completed_at else 'N/A'}")
        else:
            st.info("No completed tests yet")


def render_statistical_analysis():
    """Render statistical analysis tools"""

    st.markdown("### 📈 Statistical Analysis")

    # Analysis type selection
    analysis_type = st.selectbox(
        "Analysis Type",
        options=[
            "Test Duration Analysis",
            "Pass/Fail Distribution",
            "Protocol Performance",
            "Technician Performance"
        ]
    )

    # Date range
    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now().date() - timedelta(days=90)
        )

    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now().date()
        )

    if st.button("📊 Generate Analysis", type="primary"):
        with get_db() as db:
            if analysis_type == "Test Duration Analysis":
                st.markdown("#### Test Duration Statistics")

                # Get completed tests in date range
                tests = db.execute(
                    select(TestExecution)
                    .where(TestExecution.status == TestStatus.COMPLETED)
                    .where(TestExecution.completed_at >= datetime.combine(start_date, datetime.min.time()))
                    .where(TestExecution.completed_at <= datetime.combine(end_date, datetime.max.time()))
                ).scalars().all()

                if tests:
                    durations = [t.duration_hours for t in tests if t.duration_hours]

                    if durations:
                        avg_duration = sum(durations) / len(durations)
                        min_duration = min(durations)
                        max_duration = max(durations)

                        col1, col2, col3 = st.columns(3)
                        col1.metric("Average Duration", f"{avg_duration:.2f} hrs")
                        col2.metric("Minimum", f"{min_duration:.2f} hrs")
                        col3.metric("Maximum", f"{max_duration:.2f} hrs")

                        # Duration distribution
                        st.markdown("**Duration Distribution (hours):**")
                        st.bar_chart({"Duration": durations[:50]})  # Limit for display
                    else:
                        st.info("No duration data available")
                else:
                    st.info("No tests in selected period")

            elif analysis_type == "Pass/Fail Distribution":
                st.markdown("#### Pass/Fail Distribution")

                tests = db.execute(
                    select(TestExecution)
                    .where(TestExecution.status == TestStatus.COMPLETED)
                    .where(TestExecution.completed_at >= datetime.combine(start_date, datetime.min.time()))
                    .where(TestExecution.completed_at <= datetime.combine(end_date, datetime.max.time()))
                ).scalars().all()

                if tests:
                    passed = len([t for t in tests if t.test_passed])
                    failed = len([t for t in tests if t.test_passed == False])
                    unknown = len([t for t in tests if t.test_passed is None])

                    col1, col2, col3 = st.columns(3)
                    col1.metric("Passed", passed, delta=f"{(passed/len(tests)*100):.1f}%")
                    col2.metric("Failed", failed, delta=f"{(failed/len(tests)*100):.1f}%", delta_color="inverse")
                    col3.metric("Unknown", unknown)

                    # Pie chart data
                    st.markdown("**Distribution:**")
                    chart_data = {"Status": ["Passed", "Failed", "Unknown"], "Count": [passed, failed, unknown]}
                    st.bar_chart({"Results": [passed, failed, unknown]})
                else:
                    st.info("No tests in selected period")

            elif analysis_type == "Protocol Performance":
                st.markdown("#### Protocol Performance")

                # Get all protocols with test counts
                protocols = db.execute(select(TestProtocol)).scalars().all()

                for protocol in protocols[:20]:  # Limit display
                    tests = db.execute(
                        select(TestExecution)
                        .where(TestExecution.protocol_id == protocol.id)
                        .where(TestExecution.status == TestStatus.COMPLETED)
                    ).scalars().all()

                    if tests:
                        passed = len([t for t in tests if t.test_passed])
                        pass_rate = (passed / len(tests) * 100)

                        col1, col2, col3 = st.columns([3, 1, 1])
                        col1.markdown(f"**{protocol.protocol_id}:** {protocol.name}")
                        col2.markdown(f"{len(tests)} tests")
                        col3.markdown(f"{pass_rate:.1f}% pass")

            elif analysis_type == "Technician Performance":
                st.markdown("#### Technician Performance")

                # Get unique technicians
                technician_ids = db.execute(
                    select(TestExecution.technician_id)
                    .where(TestExecution.technician_id.isnot(None))
                    .distinct()
                ).scalars().all()

                for tech_id in technician_ids:
                    tests = db.execute(
                        select(TestExecution)
                        .where(TestExecution.technician_id == tech_id)
                        .where(TestExecution.status == TestStatus.COMPLETED)
                    ).scalars().all()

                    if tests:
                        passed = len([t for t in tests if t.test_passed])
                        pass_rate = (passed / len(tests) * 100)

                        col1, col2, col3 = st.columns([2, 1, 1])
                        col1.markdown(f"**Technician ID:** {tech_id}")
                        col2.markdown(f"{len(tests)} tests")
                        col3.markdown(f"{pass_rate:.1f}% pass rate")


def render_sample_analysis():
    """Render sample-specific analysis"""

    st.markdown("### 🔬 Sample Analysis")

    # Sample selection
    with get_db() as db:
        samples = db.execute(
            select(Sample)
            .where(Sample.status.in_([SampleStatus.COMPLETED, SampleStatus.ANALYZED, SampleStatus.REPORTED]))
            .order_by(desc(Sample.created_at))
            .limit(100)
        ).scalars().all()

        sample_options = {f"{s.sample_id}": s for s in samples}

    if not sample_options:
        st.info("No completed samples available for analysis")
        return

    selected_sample = st.selectbox(
        "Select Sample",
        options=["-- Select --"] + list(sample_options.keys())
    )

    if selected_sample != "-- Select --":
        sample = sample_options[selected_sample]

        st.markdown(f"### Sample: {sample.sample_id}")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"**Sample ID:** {sample.sample_id}")
            st.markdown(f"**Project ID:** {sample.project_id}")
            st.markdown(f"**Type:** {sample.sample_type or 'N/A'}")

        with col2:
            st.markdown(f"**Status:** {sample.status.value.upper()}")
            st.markdown(f"**Tests Completed:** {sample.tests_completed}/{sample.tests_total}")
            st.markdown(f"**Overall Result:** {sample.overall_result or 'Pending'}")

        with col3:
            st.markdown(f"**Manufacturer:** {sample.manufacturer or 'N/A'}")
            st.markdown(f"**Model:** {sample.model_number or 'N/A'}")

        st.divider()

        # Get test results for this sample
        st.markdown("#### Test Results for this Sample")

        with get_db() as db:
            test_executions = db.execute(
                select(TestExecution)
                .where(TestExecution.sample_id == sample.sample_id)
                .order_by(TestExecution.started_at)
            ).scalars().all()

            if test_executions:
                for test in test_executions:
                    protocol = db.execute(
                        select(TestProtocol).where(TestProtocol.id == test.protocol_id)
                    ).scalar()

                    result_icon = "✅" if test.test_passed else "❌" if test.test_passed == False else "⏳"

                    with st.expander(f"{result_icon} {protocol.name if protocol else 'Unknown Protocol'} ({test.execution_number})"):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown(f"**Status:** {test.status.value.upper()}")
                            st.markdown(f"**Result:** {'PASS' if test.test_passed else 'FAIL' if test.test_passed == False else 'Pending'}")
                            st.markdown(f"**Duration:** {test.duration_hours or 'N/A'} hours")

                        with col2:
                            st.markdown(f"**Started:** {test.started_at.strftime('%Y-%m-%d %H:%M') if test.started_at else 'N/A'}")
                            st.markdown(f"**Completed:** {test.completed_at.strftime('%Y-%m-%d %H:%M') if test.completed_at else 'N/A'}")

                        # Show results data if available
                        if test.results:
                            st.markdown("**Results Data:**")
                            st.json(test.results)

                        if test.remarks:
                            st.markdown(f"**Remarks:** {test.remarks}")
            else:
                st.info("No test executions found for this sample")


def render_trend_analysis():
    """Render trend analysis over time"""

    st.markdown("### 📉 Trend Analysis")

    # Time period selection
    period = st.selectbox(
        "Analysis Period",
        options=["Last 30 Days", "Last 90 Days", "Last 6 Months", "Last Year"]
    )

    if period == "Last 30 Days":
        days = 30
    elif period == "Last 90 Days":
        days = 90
    elif period == "Last 6 Months":
        days = 180
    else:
        days = 365

    start_date = datetime.utcnow() - timedelta(days=days)

    with get_db() as db:
        # Get tests over time
        tests = db.execute(
            select(TestExecution)
            .where(TestExecution.completed_at >= start_date)
            .where(TestExecution.status == TestStatus.COMPLETED)
            .order_by(TestExecution.completed_at)
        ).scalars().all()

        if tests:
            st.markdown("#### Test Volume Over Time")

            # Group by week
            from collections import defaultdict
            weekly_data = defaultdict(lambda: {'total': 0, 'passed': 0, 'failed': 0})

            for test in tests:
                if test.completed_at:
                    week = test.completed_at.strftime('%Y-W%W')
                    weekly_data[week]['total'] += 1
                    if test.test_passed:
                        weekly_data[week]['passed'] += 1
                    elif test.test_passed == False:
                        weekly_data[week]['failed'] += 1

            if weekly_data:
                weeks = sorted(weekly_data.keys())
                totals = [weekly_data[w]['total'] for w in weeks]
                passed = [weekly_data[w]['passed'] for w in weeks]

                st.markdown("**Weekly Test Volume:**")
                chart_data = {"Total Tests": totals}
                st.line_chart(chart_data)

                st.markdown("**Weekly Pass Rate:**")
                pass_rates = [(weekly_data[w]['passed'] / weekly_data[w]['total'] * 100) if weekly_data[w]['total'] > 0 else 0 for w in weeks]
                st.line_chart({"Pass Rate (%)": pass_rates})

            # Sample throughput
            st.markdown("#### Sample Throughput")

            samples = db.execute(
                select(Sample)
                .where(Sample.created_at >= start_date)
                .order_by(Sample.created_at)
            ).scalars().all()

            sample_weekly = defaultdict(int)
            for sample in samples:
                if sample.created_at:
                    week = sample.created_at.strftime('%Y-W%W')
                    sample_weekly[week] += 1

            if sample_weekly:
                weeks = sorted(sample_weekly.keys())
                counts = [sample_weekly[w] for w in weeks]

                st.line_chart({"Samples Received": counts})

        else:
            st.info("No completed tests in the selected period")


if __name__ == "__main__":
    main()
