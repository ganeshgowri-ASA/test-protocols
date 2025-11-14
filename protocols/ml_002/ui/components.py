"""
ML-002 GenSpark UI Components

This module provides Streamlit-based UI components for:
- Test configuration
- Sample registration
- Real-time monitoring
- Results visualization
- Report generation

Author: ganeshgowri-ASA
Date: 2025-11-14
Version: 1.0.0
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
import json


class ML002UIComponents:
    """GenSpark UI components for ML-002 Mechanical Load Test"""

    def __init__(self, protocol: Dict[str, Any]):
        """
        Initialize UI components

        Args:
            protocol: Protocol dictionary
        """
        self.protocol = protocol

    # ========== Configuration Forms ==========

    def render_sample_input_form(self) -> Optional[Dict[str, Any]]:
        """
        Render sample/module input form

        Returns:
            Sample data dictionary or None
        """
        st.subheader("📦 Module Information")

        with st.form("sample_input_form"):
            col1, col2 = st.columns(2)

            with col1:
                sample_id = st.text_input(
                    "Module ID *",
                    placeholder="PV-MODULE-001",
                    help="Unique identifier for the module under test"
                )
                module_type = st.selectbox(
                    "Module Type *",
                    ["Crystalline Silicon", "Thin Film", "Perovskite", "Bifacial", "Other"],
                    help="Type of photovoltaic module"
                )
                manufacturer = st.text_input(
                    "Manufacturer",
                    placeholder="Example Solar Inc."
                )

            with col2:
                serial_number = st.text_input(
                    "Serial Number *",
                    placeholder="SN123456789",
                    help="Module serial number"
                )
                rated_power = st.number_input(
                    "Rated Power (W)",
                    min_value=0.0,
                    value=400.0,
                    step=10.0,
                    help="Nominal power rating"
                )
                manufacturing_date = st.date_input(
                    "Manufacturing Date",
                    value=None,
                    help="Date of manufacture"
                )

            st.markdown("---")

            col3, col4, col5 = st.columns(3)
            with col3:
                length_mm = st.number_input("Length (mm)", min_value=0.0, value=2000.0, step=10.0)
            with col4:
                width_mm = st.number_input("Width (mm)", min_value=0.0, value=1000.0, step=10.0)
            with col5:
                thickness_mm = st.number_input("Thickness (mm)", min_value=0.0, value=40.0, step=1.0)

            weight_kg = st.number_input("Weight (kg)", min_value=0.0, value=22.0, step=0.1)

            notes = st.text_area("Notes", placeholder="Additional information about the module...")

            submit = st.form_submit_button("Register Module", type="primary", use_container_width=True)

            if submit:
                if not sample_id or not serial_number:
                    st.error("Please fill in required fields (Module ID, Serial Number)")
                    return None

                return {
                    "sample_id": sample_id,
                    "module_type": module_type,
                    "serial_number": serial_number,
                    "manufacturer": manufacturer,
                    "rated_power_w": rated_power,
                    "manufacturing_date": manufacturing_date.isoformat() if manufacturing_date else "",
                    "dimensions_mm": {
                        "length": length_mm,
                        "width": width_mm,
                        "thickness": thickness_mm
                    },
                    "weight_kg": weight_kg,
                    "metadata": {"notes": notes} if notes else {}
                }

        return None

    def render_test_parameters_form(self) -> Optional[Dict[str, Any]]:
        """
        Render test parameters configuration form

        Returns:
            Test parameters dictionary or None
        """
        st.subheader("⚙️ Test Parameters")

        # Get defaults from protocol
        default_load = self.protocol['parameters']['load_configuration']['test_load_pa']['value']
        default_cycles = self.protocol['parameters']['cycle_parameters']['cycle_count']['value']
        default_cycle_duration = self.protocol['parameters']['cycle_parameters']['cycle_duration_seconds']['value']

        with st.form("test_parameters_form"):
            st.markdown("#### Load Configuration")
            col1, col2 = st.columns(2)

            with col1:
                test_load = st.number_input(
                    "Test Load (Pa)",
                    min_value=100,
                    max_value=5400,
                    value=default_load,
                    step=100,
                    help="Cyclic load to apply (default: 1000 Pa)"
                )
                load_rate = st.number_input(
                    "Load Rate (Pa/sec)",
                    min_value=10,
                    max_value=500,
                    value=100,
                    step=10,
                    help="Rate of load application"
                )

            with col2:
                load_direction = st.selectbox(
                    "Load Direction",
                    ["Front", "Rear", "Alternating"],
                    help="Direction of load application"
                )
                load_application = st.selectbox(
                    "Load Application",
                    ["Uniform", "Point Load", "Edge Load"],
                    help="Load distribution pattern"
                )

            st.markdown("#### Cycle Configuration")
            col3, col4 = st.columns(2)

            with col3:
                cycle_count = st.number_input(
                    "Number of Cycles",
                    min_value=100,
                    max_value=10000,
                    value=default_cycles,
                    step=100,
                    help="Total number of load cycles"
                )
                cycle_duration = st.number_input(
                    "Cycle Duration (sec)",
                    min_value=5,
                    max_value=60,
                    value=default_cycle_duration,
                    step=1,
                    help="Duration of each cycle"
                )

            with col4:
                hold_time = st.number_input(
                    "Hold Time at Peak (sec)",
                    min_value=0,
                    max_value=10,
                    value=2,
                    step=1,
                    help="Duration to hold peak load"
                )
                rest_time = st.number_input(
                    "Rest Time Between Cycles (sec)",
                    min_value=0,
                    max_value=5,
                    value=1,
                    step=1,
                    help="Rest period between cycles"
                )

            st.markdown("#### Environmental Conditions")
            col5, col6 = st.columns(2)

            with col5:
                target_temp = st.slider(
                    "Target Temperature (°C)",
                    min_value=15,
                    max_value=35,
                    value=25,
                    help="Target ambient temperature"
                )

            with col6:
                target_humidity = st.slider(
                    "Target Humidity (%RH)",
                    min_value=45,
                    max_value=75,
                    value=50,
                    help="Target relative humidity"
                )

            # Calculate estimated duration
            total_duration_sec = cycle_count * (cycle_duration + rest_time)
            total_hours = total_duration_sec / 3600

            st.info(f"⏱️ Estimated Test Duration: {total_hours:.2f} hours ({total_duration_sec/60:.1f} minutes)")

            submit = st.form_submit_button("Configure Test", type="primary", use_container_width=True)

            if submit:
                return {
                    "load_configuration": {
                        "test_load_pa": test_load,
                        "load_rate_pa_per_sec": load_rate,
                        "load_direction": load_direction.lower(),
                        "load_application": load_application.lower().replace(" ", "_")
                    },
                    "cycle_parameters": {
                        "cycle_count": cycle_count,
                        "cycle_duration_seconds": cycle_duration,
                        "hold_time_at_peak_seconds": hold_time,
                        "rest_time_between_cycles_seconds": rest_time
                    },
                    "environmental_conditions": {
                        "target_temperature_celsius": target_temp,
                        "target_humidity_percent": target_humidity
                    }
                }

        return None

    # ========== Real-time Monitoring ==========

    def render_live_test_monitor(self, test_data: Dict[str, Any]):
        """
        Render real-time test monitoring dashboard

        Args:
            test_data: Current test data
        """
        st.subheader("📊 Live Test Monitoring")

        # Key metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Current Load",
                f"{test_data.get('current_load_pa', 0):.1f} Pa",
                delta=f"{test_data.get('load_error_percent', 0):+.1f}%"
            )

        with col2:
            st.metric(
                "Deflection",
                f"{test_data.get('current_deflection_mm', 0):.3f} mm",
                delta=f"{test_data.get('deflection_change_mm', 0):+.3f} mm"
            )

        with col3:
            current_cycle = test_data.get('current_cycle', 0)
            total_cycles = test_data.get('total_cycles', 1000)
            st.metric(
                "Progress",
                f"{current_cycle}/{total_cycles}",
                delta=f"{(current_cycle/total_cycles*100):.1f}%"
            )

        with col4:
            elapsed_sec = test_data.get('elapsed_time_seconds', 0)
            elapsed_hours = elapsed_sec / 3600
            st.metric(
                "Elapsed Time",
                f"{elapsed_hours:.2f} hrs",
                delta=f"{elapsed_sec/60:.1f} min"
            )

        # Progress bar
        progress = current_cycle / total_cycles if total_cycles > 0 else 0
        st.progress(progress, text=f"Test Progress: {progress*100:.1f}%")

        # Real-time charts
        col5, col6 = st.columns(2)

        with col5:
            # Load vs Time
            if 'load_history' in test_data and test_data['load_history']:
                fig_load = go.Figure()
                fig_load.add_trace(go.Scatter(
                    x=list(range(len(test_data['load_history']))),
                    y=test_data['load_history'],
                    mode='lines',
                    name='Applied Load',
                    line=dict(color='blue', width=2)
                ))
                fig_load.add_hline(
                    y=test_data.get('target_load_pa', 1000),
                    line_dash="dash",
                    line_color="red",
                    annotation_text="Target"
                )
                fig_load.update_layout(
                    title="Load vs Time",
                    xaxis_title="Time",
                    yaxis_title="Load (Pa)",
                    height=300,
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(fig_load, use_container_width=True)
            else:
                st.info("Loading chart data...")

        with col6:
            # Deflection vs Time
            if 'deflection_history' in test_data and test_data['deflection_history']:
                fig_defl = go.Figure()
                fig_defl.add_trace(go.Scatter(
                    x=list(range(len(test_data['deflection_history']))),
                    y=test_data['deflection_history'],
                    mode='lines',
                    name='Deflection',
                    line=dict(color='green', width=2)
                ))
                fig_defl.update_layout(
                    title="Deflection vs Time",
                    xaxis_title="Time",
                    yaxis_title="Deflection (mm)",
                    height=300,
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(fig_defl, use_container_width=True)
            else:
                st.info("Loading chart data...")

        # Environmental conditions
        with st.expander("🌡️ Environmental Conditions", expanded=False):
            col7, col8, col9 = st.columns(3)

            with col7:
                temp = test_data.get('temperature_celsius', 25.0)
                st.metric("Temperature", f"{temp:.1f} °C")

            with col8:
                humidity = test_data.get('humidity_percent', 50.0)
                st.metric("Humidity", f"{humidity:.1f} %RH")

            with col9:
                status = test_data.get('environmental_status', 'OK')
                st.metric("Status", status)

    # ========== Results Display ==========

    def render_test_results(self, results: Dict[str, Any]):
        """
        Display comprehensive test results

        Args:
            results: Test results dictionary
        """
        st.subheader("📋 Test Results")

        # Overall pass/fail
        passed = results.get('passed', False)

        if passed:
            st.success("✅ TEST PASSED - Module meets all acceptance criteria")
        else:
            st.error("❌ TEST FAILED - Module does not meet acceptance criteria")

        # Test summary
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Test ID",
                results.get('test_id', 'N/A')
            )

        with col2:
            st.metric(
                "Sample ID",
                results.get('sample', {}).get('sample_id', 'N/A')
            )

        with col3:
            st.metric(
                "Cycles Completed",
                f"{results.get('completed_cycles', 0)}/{results.get('total_cycles', 0)}"
            )

        # Tabs for different result sections
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Summary",
            "📈 Analysis",
            "✓ QC Assessment",
            "📉 Charts",
            "📄 Report"
        ])

        with tab1:
            self._render_results_summary(results)

        with tab2:
            self._render_analysis_results(results)

        with tab3:
            self._render_qc_assessment(results)

        with tab4:
            self._render_results_charts(results)

        with tab5:
            self._render_text_report(results)

    def _render_results_summary(self, results: Dict[str, Any]):
        """Render results summary section"""
        st.markdown("### Test Summary")

        # Basic info
        start_time = results.get('start_time', 'N/A')
        end_time = results.get('end_time', 'N/A')
        status = results.get('status', 'unknown')

        info_data = {
            "Parameter": ["Start Time", "End Time", "Status", "Module Type"],
            "Value": [
                start_time,
                end_time,
                status,
                results.get('sample', {}).get('module_type', 'N/A')
            ]
        }

        st.table(pd.DataFrame(info_data))

        # Key statistics
        qc_results = results.get('quality_control_results', {})
        defl_stats = qc_results.get('deflection_statistics', {})
        max_stats = defl_stats.get('max_deflection_stats', {})

        if max_stats:
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Mean Deflection",
                    f"{max_stats.get('mean', 0):.3f} mm"
                )

            with col2:
                st.metric(
                    "Max Deflection",
                    f"{max_stats.get('max', 0):.3f} mm"
                )

            with col3:
                st.metric(
                    "Std Deviation",
                    f"{max_stats.get('std_dev', 0):.3f} mm"
                )

    def _render_analysis_results(self, results: Dict[str, Any]):
        """Render detailed analysis results"""
        st.markdown("### Detailed Analysis")

        qc_results = results.get('quality_control_results', {})

        # Linearity analysis
        linearity = qc_results.get('load_deflection_linearity', {})
        if linearity:
            st.markdown("#### Load-Deflection Linearity")
            regression = linearity.get('regression', {})

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("R² Value", f"{regression.get('r_squared', 0):.4f}")
            with col2:
                st.metric("Quality", regression.get('quality', 'N/A'))
            with col3:
                st.metric("Equation", regression.get('equation', 'N/A'))

        # Cyclic behavior
        cyclic = qc_results.get('cyclic_behavior', {})
        if cyclic:
            st.markdown("#### Cyclic Behavior")

            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "Cycle-to-Cycle Variation",
                    f"{cyclic.get('cycle_to_cycle_variation', 0):.4f} mm"
                )
            with col2:
                st.metric(
                    "Trend",
                    cyclic.get('trend_interpretation', 'N/A')
                )

            if cyclic.get('outlier_cycles'):
                st.warning(f"⚠️ Outlier cycles detected: {cyclic['outlier_cycles']}")

        # Permanent deformation
        perm_deform = qc_results.get('permanent_deformation', {})
        if perm_deform:
            st.markdown("#### Permanent Deformation")

            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "Permanent Change",
                    f"{perm_deform.get('permanent_change_mm', 0):.4f} mm"
                )
            with col2:
                assessment = perm_deform.get('assessment', 'N/A')
                if assessment == 'acceptable':
                    st.success(f"✅ {assessment.upper()}")
                else:
                    st.error(f"❌ {assessment.upper()}")

    def _render_qc_assessment(self, results: Dict[str, Any]):
        """Render quality control assessment"""
        st.markdown("### Quality Control Assessment")

        qc_results = results.get('quality_control_results', {})
        criteria = qc_results.get('acceptance_criteria', {})

        if not criteria:
            st.warning("No QC results available")
            return

        # Overall summary
        total = criteria.get('total_criteria', 0)
        passed_count = criteria.get('passed_criteria', 0)
        overall_pass = criteria.get('overall_pass', False)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Criteria", total)
        with col2:
            st.metric("Passed", passed_count)
        with col3:
            pass_rate = (passed_count / total * 100) if total > 0 else 0
            st.metric("Pass Rate", f"{pass_rate:.1f}%")

        # Detailed criteria
        st.markdown("#### Detailed Criteria Evaluation")

        criteria_data = []
        for key, value in criteria.items():
            if isinstance(value, dict) and 'passed' in value:
                criteria_data.append({
                    "Criterion": key.replace('_', ' ').title(),
                    "Status": "✅ PASS" if value['passed'] else "❌ FAIL",
                    "Critical": "Yes" if value.get('is_critical') else "No",
                    "Description": value.get('description', ''),
                    "Actual": value.get('actual_value', 'N/A'),
                    "Required": value.get('required_value', 'N/A')
                })

        if criteria_data:
            df = pd.DataFrame(criteria_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

    def _render_results_charts(self, results: Dict[str, Any]):
        """Render results visualization charts"""
        st.markdown("### Results Visualization")

        cycle_data = results.get('cycle_data', [])

        if not cycle_data:
            st.warning("No cycle data available for charting")
            return

        # Extract data for plotting
        cycle_numbers = [c['cycle_number'] for c in cycle_data]
        max_deflections = [c['max_deflection_mm'] for c in cycle_data]
        max_loads = [c['max_load_pa'] for c in cycle_data]

        # Chart 1: Deflection per cycle
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=cycle_numbers,
            y=max_deflections,
            mode='markers+lines',
            name='Max Deflection',
            marker=dict(size=4, color='blue')
        ))
        fig1.update_layout(
            title="Maximum Deflection per Cycle",
            xaxis_title="Cycle Number",
            yaxis_title="Deflection (mm)",
            height=400
        )
        st.plotly_chart(fig1, use_container_width=True)

        # Chart 2: Load per cycle
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=cycle_numbers,
            y=max_loads,
            mode='markers+lines',
            name='Applied Load',
            marker=dict(size=4, color='red')
        ))
        fig2.update_layout(
            title="Applied Load per Cycle",
            xaxis_title="Cycle Number",
            yaxis_title="Load (Pa)",
            height=400
        )
        st.plotly_chart(fig2, use_container_width=True)

        # Chart 3: Load vs Deflection scatter
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=max_loads,
            y=max_deflections,
            mode='markers',
            name='Data Points',
            marker=dict(size=6, color='green', opacity=0.6)
        ))
        fig3.update_layout(
            title="Load vs Deflection",
            xaxis_title="Load (Pa)",
            yaxis_title="Deflection (mm)",
            height=400
        )
        st.plotly_chart(fig3, use_container_width=True)

    def _render_text_report(self, results: Dict[str, Any]):
        """Render downloadable text report"""
        st.markdown("### Test Report")

        # Generate report text (simplified version)
        report_text = f"""
ML-002 MECHANICAL LOAD DYNAMIC TEST - REPORT
{'='*80}

Test ID: {results.get('test_id', 'N/A')}
Sample ID: {results.get('sample', {}).get('sample_id', 'N/A')}
Module Type: {results.get('sample', {}).get('module_type', 'N/A')}
Test Date: {results.get('start_time', 'N/A')}
Status: {results.get('status', 'N/A')}
Result: {'PASSED' if results.get('passed') else 'FAILED'}

Cycles Completed: {results.get('completed_cycles', 0)}/{results.get('total_cycles', 0)}

{'='*80}
END OF REPORT
        """

        st.code(report_text, language="text")

        # Download button
        st.download_button(
            label="📥 Download Report (TXT)",
            data=report_text,
            file_name=f"ML002_Report_{results.get('test_id', 'test')}.txt",
            mime="text/plain"
        )

        # JSON download
        json_data = json.dumps(results, indent=2, default=str)
        st.download_button(
            label="📥 Download Results (JSON)",
            data=json_data,
            file_name=f"ML002_Results_{results.get('test_id', 'test')}.json",
            mime="application/json"
        )


if __name__ == "__main__":
    st.set_page_config(page_title="ML-002 UI Components", layout="wide")
    st.title("ML-002 UI Components Demo")
    st.info("This module provides UI components for the ML-002 test interface")
