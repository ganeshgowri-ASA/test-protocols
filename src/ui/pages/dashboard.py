"""
Dashboard Page
"""

import streamlit as st
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.models import SessionLocal, TestExecution, Sample, Protocol, TestStatus, TestOutcome
from sqlalchemy import func


def render_dashboard():
    """Render the dashboard page"""
    st.title("📊 Dashboard")

    db = SessionLocal()

    try:
        # Key metrics
        st.header("Overview")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_tests = db.query(TestExecution).count()
            st.metric("Total Tests", total_tests)

        with col2:
            completed_tests = db.query(TestExecution).filter(
                TestExecution.status == TestStatus.COMPLETED
            ).count()
            st.metric("Completed Tests", completed_tests)

        with col3:
            passed_tests = db.query(TestExecution).filter(
                TestExecution.outcome == TestOutcome.PASS
            ).count()
            st.metric("Passed Tests", passed_tests)

        with col4:
            active_samples = db.query(Sample).filter(Sample.is_active == True).count()
            st.metric("Active Samples", active_samples)

        # Recent tests
        st.header("Recent Tests")

        recent_tests = db.query(TestExecution).order_by(
            TestExecution.created_at.desc()
        ).limit(10).all()

        if recent_tests:
            import pandas as pd

            data = []
            for test in recent_tests:
                data.append({
                    'Test Number': test.test_number,
                    'Protocol': test.protocol.protocol_name if test.protocol else 'N/A',
                    'Sample': test.sample.sample_id if test.sample else 'N/A',
                    'Status': test.status.value if test.status else 'N/A',
                    'Outcome': test.outcome.value if test.outcome else 'N/A',
                    'Date': test.created_at.strftime('%Y-%m-%d %H:%M') if test.created_at else 'N/A'
                })

            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No tests found. Start by executing a test.")

        # Test statistics by protocol
        st.header("Test Statistics by Protocol")

        protocol_stats = db.query(
            Protocol.protocol_name,
            func.count(TestExecution.id).label('count'),
            func.sum(func.cast(TestExecution.outcome == TestOutcome.PASS, type_=db.bind.dialect.BIGINT)).label('passed')
        ).join(
            TestExecution, Protocol.id == TestExecution.protocol_id
        ).group_by(
            Protocol.protocol_name
        ).all()

        if protocol_stats:
            import pandas as pd

            stats_data = []
            for stat in protocol_stats:
                total = stat.count
                passed = stat.passed or 0
                pass_rate = (passed / total * 100) if total > 0 else 0

                stats_data.append({
                    'Protocol': stat.protocol_name,
                    'Total Tests': total,
                    'Passed': passed,
                    'Pass Rate (%)': f"{pass_rate:.1f}"
                })

            df = pd.DataFrame(stats_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No test statistics available yet.")

    finally:
        db.close()
