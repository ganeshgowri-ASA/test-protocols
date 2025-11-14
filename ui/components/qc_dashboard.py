"""QC dashboard component."""

import streamlit as st
from typing import List, Dict, Any


class QCDashboard:
    """Component for displaying QC results and status."""

    def __init__(self):
        """Initialize QC dashboard."""
        pass

    def render_qc_summary(self, qc_results: List[Dict[str, Any]]) -> None:
        """
        Render QC summary dashboard.

        Args:
            qc_results: List of QC check results
        """
        if not qc_results:
            st.info("No QC checks performed yet")
            return

        st.markdown("### Quality Control Summary")

        # Calculate statistics
        total_checks = len(qc_results)
        passed_checks = sum(1 for qc in qc_results if qc.get('passed', False))
        failed_checks = total_checks - passed_checks

        # Overall status
        overall_status = "PASS" if failed_checks == 0 else "FAIL"
        status_color = "green" if overall_status == "PASS" else "red"

        # Display overall status
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
                <div style="text-align: center; padding: 1rem; background-color: {status_color};
                     color: white; border-radius: 0.5rem; font-size: 1.5rem; font-weight: bold;">
                    {overall_status}
                </div>
            """, unsafe_allow_html=True)

        with col2:
            st.metric("Total Checks", total_checks)

        with col3:
            st.metric("Passed", passed_checks, delta=None)

        with col4:
            st.metric("Failed", failed_checks, delta=None if failed_checks == 0 else -failed_checks)

        # Group by severity
        severity_groups = {}
        for qc in qc_results:
            severity = qc.get('severity', 'unknown')
            if severity not in severity_groups:
                severity_groups[severity] = []
            severity_groups[severity].append(qc)

        # Display by severity
        st.markdown("---")

        # Critical issues
        if 'critical' in severity_groups:
            with st.expander(f"🔴 Critical Issues ({len(severity_groups['critical'])})", expanded=True):
                self._render_qc_list(severity_groups['critical'])

        # Errors
        if 'error' in severity_groups:
            with st.expander(f"🟠 Errors ({len(severity_groups['error'])})", expanded=True):
                self._render_qc_list(severity_groups['error'])

        # Warnings
        if 'warning' in severity_groups:
            with st.expander(f"🟡 Warnings ({len(severity_groups['warning'])})", expanded=False):
                self._render_qc_list(severity_groups['warning'])

        # Info
        if 'info' in severity_groups:
            with st.expander(f"🔵 Information ({len(severity_groups['info'])})", expanded=False):
                self._render_qc_list(severity_groups['info'])

    def _render_qc_list(self, qc_checks: List[Dict[str, Any]]) -> None:
        """
        Render list of QC checks.

        Args:
            qc_checks: List of QC check results
        """
        for qc in qc_checks:
            check_name = qc.get('check_name', 'Unknown Check')
            message = qc.get('message', 'No message')
            passed = qc.get('passed', False)

            status_icon = "✅" if passed else "❌"

            # Display check
            st.markdown(f"**{status_icon} {check_name}**")
            st.markdown(f"_{message}_")

            # Show details if available
            expected = qc.get('expected_value')
            actual = qc.get('actual_value')

            if expected or actual:
                col1, col2 = st.columns(2)
                if expected:
                    with col1:
                        st.markdown(f"**Expected:** {expected}")
                if actual:
                    with col2:
                        st.markdown(f"**Actual:** {actual}")

            st.markdown("---")

    def render_qc_trends(self, historical_qc: List[Dict[str, Any]]) -> None:
        """
        Render QC trends over time.

        Args:
            historical_qc: Historical QC results
        """
        st.markdown("### QC Trends")

        if not historical_qc:
            st.info("No historical QC data available")
            return

        import plotly.graph_objects as go
        import pandas as pd

        # Create DataFrame
        df = pd.DataFrame(historical_qc)

        # Count pass/fail by date
        df['date'] = pd.to_datetime(df['check_timestamp']).dt.date
        trend_data = df.groupby(['date', 'passed']).size().unstack(fill_value=0)

        # Create stacked bar chart
        fig = go.Figure()

        if False in trend_data.columns:
            fig.add_trace(go.Bar(
                x=trend_data.index,
                y=trend_data[False],
                name='Failed',
                marker_color='red'
            ))

        if True in trend_data.columns:
            fig.add_trace(go.Bar(
                x=trend_data.index,
                y=trend_data[True],
                name='Passed',
                marker_color='green'
            ))

        fig.update_layout(
            barmode='stack',
            title='QC Results Over Time',
            xaxis_title='Date',
            yaxis_title='Number of Checks',
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    def render_qc_details_table(self, qc_results: List[Dict[str, Any]]) -> None:
        """
        Render detailed QC results table.

        Args:
            qc_results: List of QC check results
        """
        st.markdown("### Detailed QC Results")

        if not qc_results:
            st.info("No QC results available")
            return

        import pandas as pd

        # Create DataFrame
        df = pd.DataFrame(qc_results)

        # Select columns to display
        display_cols = [
            'check_name',
            'passed',
            'severity',
            'message',
            'expected_value',
            'actual_value'
        ]

        display_cols = [col for col in display_cols if col in df.columns]

        # Display table
        st.dataframe(
            df[display_cols],
            use_container_width=True,
            hide_index=True
        )

        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download QC Results (CSV)",
            data=csv,
            file_name="qc_results.csv",
            mime="text/csv"
        )
