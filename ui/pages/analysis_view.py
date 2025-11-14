"""
Analysis & Results Page

Display test results, QC checks, and analysis.
"""

import streamlit as st
from pathlib import Path
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def render():
    """Render analysis and results page"""

    st.header("Analysis & Results")

    # Check if test run exists
    if not st.session_state.get("current_test_run"):
        st.warning("No active test run.")
        st.info("Go to 'Protocol Selection' to start a new test run.")
        return

    protocol_instance = st.session_state.protocol_instance
    test_data = st.session_state.test_data

    if not test_data:
        st.info("No test data available yet. Complete some test steps first.")
        return

    # Test run summary
    st.subheader("Test Run Summary")
    test_run = st.session_state.current_test_run

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Protocol", test_run["protocol_id"])
    with col2:
        st.metric("Sample", test_run["sample_id"])
    with col3:
        st.metric("Status", test_run["status"])
    with col4:
        completed = len(st.session_state.completed_steps)
        total = len(protocol_instance.definition.steps)
        st.metric("Progress", f"{completed}/{total}")

    st.markdown("---")

    # Run QC Checks
    st.subheader("Quality Control Checks")

    if st.button("Run QC Checks", type="primary"):
        try:
            qc_results = protocol_instance.run_qc_checks(test_data)
            st.session_state.qc_results = qc_results

            # Count pass/fail
            total = len(qc_results)
            passed = sum(1 for r in qc_results if r["passed"])
            failed = total - passed

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Checks", total)
            with col2:
                st.metric("Passed", passed, delta=None, delta_color="off")
            with col3:
                st.metric("Failed", failed, delta=None, delta_color="inverse")

            st.success("QC checks completed!")

        except Exception as e:
            st.error(f"Error running QC checks: {e}")

    # Display QC results
    if st.session_state.qc_results:
        st.markdown("### QC Results")

        qc_df = pd.DataFrame(st.session_state.qc_results)

        # Color code by result
        def highlight_qc(row):
            if not row['passed']:
                if row['severity'] == 'critical':
                    return ['background-color: #ffcccc'] * len(row)
                else:
                    return ['background-color: #ffffcc'] * len(row)
            return [''] * len(row)

        st.dataframe(
            qc_df[['criterion_id', 'name', 'severity', 'passed', 'message']].style.apply(highlight_qc, axis=1),
            use_container_width=True
        )

        # Show failures in detail
        failures = [r for r in st.session_state.qc_results if not r["passed"]]
        if failures:
            st.error(f"⚠️ {len(failures)} QC check(s) failed:")
            for fail in failures:
                severity_icon = "🔴" if fail["severity"] == "critical" else "🟡"
                st.markdown(f"{severity_icon} **{fail['name']}**: {fail['message']}")

    st.markdown("---")

    # Calculate results
    st.subheader("Calculated Results")

    if st.button("Calculate Results"):
        try:
            calc_results = protocol_instance.calculate_results(test_data)
            st.session_state.analysis_results = calc_results

            if calc_results:
                st.success("Results calculated!")

                for name, result in calc_results.items():
                    if "error" in result:
                        st.error(f"**{name}**: Error - {result['error']}")
                    else:
                        value = result.get("value", "N/A")
                        unit = result.get("unit", "")
                        st.metric(name, f"{value:.2f} {unit}" if isinstance(value, (int, float)) else value)
            else:
                st.info("No calculations defined for this protocol.")

        except Exception as e:
            st.error(f"Error calculating results: {e}")

    st.markdown("---")

    # Visualizations
    st.subheader("Data Visualization")

    # Check if we have baseline and final measurements
    has_baseline = any(key.startswith("baseline_") for key in test_data.keys())
    has_final = any(key.startswith("final_") for key in test_data.keys())

    if has_baseline and has_final:
        # Power comparison
        if "baseline_pmax" in test_data and "final_pmax" in test_data:
            st.markdown("#### Power Comparison")

            comparison_data = {
                "Measurement": ["Baseline", "Final"],
                "Power (W)": [test_data["baseline_pmax"], test_data["final_pmax"]]
            }

            fig = px.bar(
                comparison_data,
                x="Measurement",
                y="Power (W)",
                title="Maximum Power: Baseline vs Final",
                color="Measurement",
                color_discrete_map={"Baseline": "#1f77b4", "Final": "#ff7f0e"}
            )

            st.plotly_chart(fig, use_container_width=True)

            # Degradation
            degradation = ((test_data["baseline_pmax"] - test_data["final_pmax"]) /
                         test_data["baseline_pmax"] * 100)

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Power Degradation", f"{degradation:.2f}%",
                         delta=f"{degradation:.2f}%", delta_color="inverse")
            with col2:
                if degradation <= 5:
                    st.success("✅ Within acceptable degradation limit (≤5%)")
                else:
                    st.error("❌ Exceeds acceptable degradation limit (≤5%)")

        # Electrical parameters comparison
        if all(key in test_data for key in ["baseline_voc", "baseline_isc", "final_voc", "final_isc"]):
            st.markdown("#### Electrical Parameters")

            params = ["Voc", "Isc", "Pmax", "FF"]
            baseline_vals = []
            final_vals = []

            for param in params:
                baseline_key = f"baseline_{param.lower()}"
                final_key = f"final_{param.lower()}"
                baseline_vals.append(test_data.get(baseline_key, 0))
                final_vals.append(test_data.get(final_key, 0))

            fig = go.Figure(data=[
                go.Bar(name='Baseline', x=params, y=baseline_vals),
                go.Bar(name='Final', x=params, y=final_vals)
            ])

            fig.update_layout(
                title="Electrical Parameters: Baseline vs Final",
                barmode='group',
                yaxis_title="Value"
            )

            st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Complete baseline and final measurements to see visualizations.")

    # Degradation curve (if protocol is CorrosionProtocol)
    try:
        if hasattr(protocol_instance, 'get_degradation_curve'):
            st.markdown("#### Degradation Curve")

            curve_df = protocol_instance.get_degradation_curve()

            if not curve_df.empty:
                fig = px.line(
                    curve_df,
                    x="cycle",
                    y="pmax",
                    markers=True,
                    title="Power Degradation Over Test Cycles",
                    labels={"cycle": "Cycle Number", "pmax": "Maximum Power (W)"}
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No degradation data available yet.")
    except:
        pass

    st.markdown("---")

    # Raw data view
    with st.expander("View Raw Test Data"):
        st.json(test_data)
