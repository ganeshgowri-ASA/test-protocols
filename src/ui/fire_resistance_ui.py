"""
Fire Resistance Testing Protocol - Streamlit/GenSpark UI
IEC 61730-2 MST 23

Interactive web-based interface for conducting and managing fire resistance tests.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from pathlib import Path
import json
from typing import List, Dict, Any, Optional

# Import our models and handlers
import sys
sys.path.append(str(Path(__file__).parent.parent))

from models.fire_resistance_model import (
    SampleInformation, EnvironmentalConditions, EquipmentCalibration,
    RealTimeMeasurement, TestObservations, TestResults, TestReport,
    TestStatus, PassFailResult, SmokeLevel, MaterialIntegrity
)
from handlers.fire_resistance_handler import FireResistanceProtocolHandler


class FireResistanceUI:
    """Main UI class for Fire Resistance Testing Protocol"""

    def __init__(self):
        """Initialize the UI application"""
        self.handler = FireResistanceProtocolHandler()
        self.init_session_state()

    def init_session_state(self):
        """Initialize Streamlit session state"""
        if 'current_test' not in st.session_state:
            st.session_state.current_test = None
        if 'measurements' not in st.session_state:
            st.session_state.measurements = []
        if 'test_status' not in st.session_state:
            st.session_state.test_status = TestStatus.RECEIVED
        if 'start_time' not in st.session_state:
            st.session_state.start_time = None

    def run(self):
        """Main application entry point"""
        st.set_page_config(
            page_title="FIRE-001: Fire Resistance Testing",
            page_icon="🔥",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        # Custom CSS
        st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #FF4B4B;
            text-align: center;
            margin-bottom: 1rem;
        }
        .sub-header {
            font-size: 1.2rem;
            color: #666;
            text-align: center;
            margin-bottom: 2rem;
        }
        .status-box {
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
        .status-pass {
            background-color: #D4EDDA;
            border-left: 4px solid #28A745;
        }
        .status-fail {
            background-color: #F8D7DA;
            border-left: 4px solid #DC3545;
        }
        .status-pending {
            background-color: #FFF3CD;
            border-left: 4px solid #FFC107;
        }
        </style>
        """, unsafe_allow_html=True)

        # Header
        st.markdown('<div class="main-header">🔥 Fire Resistance Testing Protocol</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">FIRE-001 | IEC 61730-2 MST 23 | PV Module Safety Testing</div>', unsafe_allow_html=True)

        # Sidebar navigation
        page = st.sidebar.selectbox(
            "Navigation",
            [
                "Protocol Overview",
                "Sample Registration",
                "Test Execution",
                "Data Analysis",
                "Test Reports",
                "Quality Management",
                "Equipment Calibration",
                "Help & Documentation"
            ]
        )

        # Route to appropriate page
        if page == "Protocol Overview":
            self.show_protocol_overview()
        elif page == "Sample Registration":
            self.show_sample_registration()
        elif page == "Test Execution":
            self.show_test_execution()
        elif page == "Data Analysis":
            self.show_data_analysis()
        elif page == "Test Reports":
            self.show_test_reports()
        elif page == "Quality Management":
            self.show_quality_management()
        elif page == "Equipment Calibration":
            self.show_equipment_calibration()
        elif page == "Help & Documentation":
            self.show_help_documentation()

    def show_protocol_overview(self):
        """Display protocol overview page"""
        st.header("Protocol Overview")

        protocol_info = self.handler.get_protocol_info()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Protocol ID", protocol_info['protocol_id'])
        with col2:
            st.metric("Version", protocol_info['version'])
        with col3:
            st.metric("Category", protocol_info['category'])

        st.subheader("Standard Information")
        st.write(f"**Standard:** {protocol_info['standard']['name']}")
        st.write(f"**Section:** {protocol_info['standard']['section']}")
        st.write(f"**Title:** {protocol_info['standard']['title']}")

        st.subheader("Test Objective")
        st.info(self.handler.protocol_data['test_overview']['objective'])

        st.subheader("Test Scope")
        st.write(self.handler.protocol_data['test_overview']['scope'])

        # Test conditions
        st.subheader("Test Conditions")
        conditions = self.handler.protocol_data['test_overview']['test_conditions']
        cond_df = pd.DataFrame([
            {"Parameter": "Ambient Temperature", "Specification": conditions['ambient_temperature']},
            {"Parameter": "Relative Humidity", "Specification": conditions['relative_humidity']},
            {"Parameter": "Conditioning Period", "Specification": conditions['conditioning_period']}
        ])
        st.table(cond_df)

        # Safety requirements
        with st.expander("⚠️ Safety Requirements", expanded=False):
            safety = self.handler.protocol_data['safety_requirements']
            st.write("**Required PPE:**")
            for ppe in safety['ppe_required']:
                st.write(f"- {ppe}")

            st.write("**Safety Procedures:**")
            for proc in safety['safety_procedures']:
                st.write(f"- {proc}")

    def show_sample_registration(self):
        """Display sample registration page"""
        st.header("Sample Registration")

        with st.form("sample_registration_form"):
            st.subheader("Sample Information")

            col1, col2 = st.columns(2)

            with col1:
                sample_id = st.text_input("Sample ID*", placeholder="e.g., SMP-2025-001")
                manufacturer = st.text_input("Manufacturer*", placeholder="e.g., Solar Tech Inc.")
                model_number = st.text_input("Model Number*", placeholder="e.g., ST-400-BF")
                serial_number = st.text_input("Serial Number*", placeholder="e.g., SN123456")

            with col2:
                batch_number = st.text_input("Batch Number", placeholder="e.g., BATCH-2025-A")
                date_of_manufacture = st.date_input("Date of Manufacture")
                receipt_date = st.date_input("Receipt Date", value=datetime.now())
                test_due_date = st.date_input("Test Due Date", value=datetime.now() + timedelta(days=7))

            visual_condition = st.text_area("Visual Condition", placeholder="Describe the visual condition of the sample...")

            st.subheader("Dimensions")
            col3, col4, col5 = st.columns(3)
            with col3:
                length_mm = st.number_input("Length (mm)", min_value=0.0, value=0.0)
            with col4:
                width_mm = st.number_input("Width (mm)", min_value=0.0, value=0.0)
            with col5:
                thickness_mm = st.number_input("Thickness (mm)", min_value=0.0, value=0.0)

            weight_kg = st.number_input("Weight (kg)", min_value=0.0, value=0.0, step=0.1)

            submitted = st.form_submit_button("Register Sample", type="primary")

            if submitted:
                if not all([sample_id, manufacturer, model_number, serial_number]):
                    st.error("Please fill in all required fields marked with *")
                else:
                    sample = SampleInformation(
                        sample_id=sample_id,
                        manufacturer=manufacturer,
                        model_number=model_number,
                        serial_number=serial_number,
                        batch_number=batch_number if batch_number else None,
                        date_of_manufacture=str(date_of_manufacture),
                        receipt_date=datetime.combine(receipt_date, datetime.min.time()),
                        visual_condition=visual_condition,
                        dimensions={
                            "length_mm": length_mm,
                            "width_mm": width_mm,
                            "thickness_mm": thickness_mm
                        },
                        weight_kg=weight_kg if weight_kg > 0 else None
                    )
                    st.session_state.current_sample = sample
                    st.success(f"✅ Sample {sample_id} registered successfully!")
                    st.json(sample.to_dict())

    def show_test_execution(self):
        """Display test execution page"""
        st.header("Test Execution")

        # Check if sample is registered
        if 'current_sample' not in st.session_state:
            st.warning("⚠️ Please register a sample first in the Sample Registration page.")
            return

        # Test setup
        if st.session_state.current_test is None:
            st.subheader("Create New Test Session")

            with st.form("test_setup_form"):
                test_id = st.text_input(
                    "Test ID",
                    value=f"FIRE-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                )

                st.write("**Test Personnel**")
                technician = st.text_input("Test Technician*")
                engineer = st.text_input("Test Engineer*")
                observer = st.text_input("Observer (optional)")

                st.write("**Environmental Conditions**")
                col1, col2 = st.columns(2)
                with col1:
                    temp_c = st.number_input("Temperature (°C)", min_value=15.0, max_value=35.0, value=23.0, step=0.1)
                with col2:
                    humidity = st.number_input("Relative Humidity (%)", min_value=20.0, max_value=80.0, value=50.0, step=1.0)

                start_test = st.form_submit_button("Start Test Session", type="primary")

                if start_test:
                    if not all([technician, engineer]):
                        st.error("Please provide at least test technician and engineer names")
                    else:
                        personnel = [technician, engineer]
                        if observer:
                            personnel.append(observer)

                        test_results = self.handler.create_test_session(
                            sample=st.session_state.current_sample,
                            test_personnel=personnel,
                            test_id=test_id
                        )

                        # Set environmental conditions
                        test_results.environmental_conditions = EnvironmentalConditions(
                            temperature_c=temp_c,
                            relative_humidity=humidity,
                            conditioning_start=datetime.now() - timedelta(hours=24),
                            conditioning_end=datetime.now()
                        )

                        st.session_state.current_test = test_results
                        st.session_state.start_time = datetime.now()
                        st.success(f"✅ Test session {test_id} created!")
                        st.rerun()

        else:
            # Active test session
            st.success(f"🔬 Active Test: {st.session_state.current_test.test_id}")

            # Real-time data entry
            st.subheader("Real-Time Data Collection")

            col1, col2 = st.columns(2)

            with col1:
                st.write("**Current Status**")
                if st.session_state.start_time:
                    elapsed = (datetime.now() - st.session_state.start_time).total_seconds()
                    st.metric("Elapsed Time", f"{elapsed:.0f} seconds")

            with col2:
                st.write("**Quick Actions**")
                if st.button("⏱️ Record Current Time Point"):
                    st.info(f"Current time: {elapsed:.1f}s")

            # Measurement entry
            with st.form("measurement_form"):
                st.write("**Record Measurement**")

                col1, col2, col3 = st.columns(3)
                with col1:
                    time_seconds = st.number_input("Time (seconds)", min_value=0.0, value=elapsed if st.session_state.start_time else 0.0, step=1.0)
                with col2:
                    temperature = st.number_input("Surface Temperature (°C)", min_value=0.0, max_value=1200.0, value=25.0, step=1.0)
                with col3:
                    flame_spread = st.number_input("Flame Spread (mm)", min_value=0.0, max_value=500.0, value=0.0, step=1.0)

                observations = st.text_input("Observations")

                record_measurement = st.form_submit_button("Record Measurement")

                if record_measurement:
                    measurement = self.handler.record_measurement(
                        elapsed_time_seconds=time_seconds,
                        surface_temperature_c=temperature,
                        flame_spread_mm=flame_spread if flame_spread > 0 else None,
                        observations=observations
                    )
                    st.session_state.measurements.append(measurement)
                    st.success(f"✅ Measurement recorded at t={time_seconds}s")

            # Display current measurements
            if st.session_state.measurements:
                st.subheader("Recorded Measurements")
                df = pd.DataFrame([
                    {
                        "Time (s)": m.elapsed_time_seconds,
                        "Temperature (°C)": m.surface_temperature_c,
                        "Flame Spread (mm)": m.flame_spread_mm or 0,
                        "Observations": m.observations
                    }
                    for m in st.session_state.measurements
                ])
                st.dataframe(df, use_container_width=True)

                # Real-time plot
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df["Time (s)"],
                    y=df["Temperature (°C)"],
                    mode='lines+markers',
                    name='Temperature',
                    line=dict(color='red', width=2)
                ))
                fig.update_layout(
                    title="Temperature vs Time",
                    xaxis_title="Time (seconds)",
                    yaxis_title="Temperature (°C)",
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)

            # Test completion
            st.subheader("Complete Test")
            with st.expander("Finalize Test Results"):
                with st.form("finalize_test_form"):
                    st.write("**Test Observations**")

                    col1, col2 = st.columns(2)
                    with col1:
                        ignition_occurred = st.checkbox("Ignition Occurred")
                        time_to_ignition = st.number_input("Time to Ignition (s)", min_value=0.0, disabled=not ignition_occurred)
                        self_extinguishing = st.checkbox("Self-Extinguishing", value=True)
                        self_ext_time = st.number_input("Self-Extinguishing Time (s)", min_value=0.0, value=0.0)

                    with col2:
                        dripping = st.checkbox("Dripping Materials")
                        flaming_drips = st.checkbox("Flaming Drips")
                        smoke = st.selectbox("Smoke Generation", ["None", "Light", "Moderate", "Heavy"])
                        integrity = st.selectbox("Material Integrity", ["Intact", "Minor Damage", "Moderate Damage", "Severe Damage", "Failure"])

                    max_flame_spread = st.number_input("Maximum Flame Spread (mm)", min_value=0.0, value=0.0)
                    burning_duration = st.number_input("Burning Duration (s)", min_value=0.0, value=0.0)
                    test_notes = st.text_area("Additional Notes")

                    finalize = st.form_submit_button("Finalize Test", type="primary")

                    if finalize:
                        observations = TestObservations(
                            ignition_occurred=ignition_occurred,
                            time_to_ignition_seconds=time_to_ignition if ignition_occurred else None,
                            self_extinguishing=self_extinguishing,
                            self_extinguishing_time_seconds=self_ext_time,
                            dripping_materials=dripping,
                            flaming_drips=flaming_drips,
                            smoke_generation=SmokeLevel[smoke.upper().replace(" ", "_")],
                            material_integrity=MaterialIntegrity[integrity.upper().replace(" ", "_")],
                            max_flame_spread_mm=max_flame_spread,
                            burning_duration_seconds=burning_duration,
                            notes=test_notes
                        )

                        results = self.handler.finalize_test(observations)
                        st.session_state.test_results = results

                        st.success("✅ Test finalized!")
                        st.write(f"**Overall Result:** {results.overall_result.value}")

                        # Show acceptance criteria
                        st.subheader("Acceptance Criteria Results")
                        for criterion in results.acceptance_results:
                            status_class = "status-pass" if criterion.result == PassFailResult.PASS else "status-fail"
                            st.markdown(
                                f'<div class="status-box {status_class}">'
                                f'<b>{criterion.criterion_name}:</b> {criterion.result.value}<br>'
                                f'Measured: {criterion.measured_value} | Required: {criterion.pass_condition}'
                                f'</div>',
                                unsafe_allow_html=True
                            )

    def show_data_analysis(self):
        """Display data analysis page"""
        st.header("Data Analysis & Visualization")

        if 'test_results' not in st.session_state:
            st.warning("⚠️ No test results available. Please complete a test first.")
            return

        results = st.session_state.test_results

        # Summary metrics
        st.subheader("Test Summary")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Overall Result", results.overall_result.value)
        with col2:
            st.metric("Test Duration", f"{results.test_duration_minutes:.1f} min" if results.test_duration_minutes else "N/A")
        with col3:
            st.metric("Max Flame Spread", f"{results.observations.max_flame_spread_mm} mm")
        with col4:
            st.metric("Material Integrity", results.observations.material_integrity.value)

        # Temperature analysis
        if results.real_time_data:
            st.subheader("Temperature Analysis")

            df = pd.DataFrame([
                {
                    "Time (s)": m.elapsed_time_seconds,
                    "Temperature (°C)": m.surface_temperature_c,
                    "Flame Spread (mm)": m.flame_spread_mm or 0
                }
                for m in results.real_time_data
            ])

            # Temperature plot
            fig1 = px.line(df, x="Time (s)", y="Temperature (°C)", title="Surface Temperature Over Time")
            fig1.update_traces(line_color='red', line_width=3)
            st.plotly_chart(fig1, use_container_width=True)

            # Flame spread plot
            fig2 = px.line(df, x="Time (s)", y="Flame Spread (mm)", title="Flame Spread Over Time")
            fig2.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="Max Allowable (100mm)")
            st.plotly_chart(fig2, use_container_width=True)

            # Statistics
            st.subheader("Statistical Summary")
            stats_df = pd.DataFrame({
                "Metric": ["Maximum", "Mean", "Minimum", "Std Dev"],
                "Temperature (°C)": [
                    df["Temperature (°C)"].max(),
                    df["Temperature (°C)"].mean(),
                    df["Temperature (°C)"].min(),
                    df["Temperature (°C)"].std()
                ]
            })
            st.table(stats_df)

        # Acceptance criteria breakdown
        st.subheader("Acceptance Criteria Breakdown")
        criteria_data = [
            {
                "Criterion": c.criterion_name,
                "Severity": c.severity,
                "Result": c.result.value,
                "Measured": c.measured_value,
                "Required": c.pass_condition
            }
            for c in results.acceptance_results
        ]
        criteria_df = pd.DataFrame(criteria_data)
        st.dataframe(criteria_df, use_container_width=True)

    def show_test_reports(self):
        """Display test reports page"""
        st.header("Test Reports")

        if 'test_results' not in st.session_state:
            st.warning("⚠️ No test results available for report generation.")
            return

        st.subheader("Generate Test Report")

        with st.form("report_generation_form"):
            report_id = st.text_input("Report ID", value=f"RPT-{st.session_state.test_results.test_id}")

            col1, col2, col3 = st.columns(3)
            with col1:
                prepared_by = st.text_input("Prepared By*")
            with col2:
                reviewed_by = st.text_input("Reviewed By*")
            with col3:
                approved_by = st.text_input("Approved By*")

            generate_report = st.form_submit_button("Generate Report", type="primary")

            if generate_report:
                if not all([prepared_by, reviewed_by, approved_by]):
                    st.error("Please provide all required signatures")
                else:
                    report = self.handler.generate_report(
                        test_results=st.session_state.test_results,
                        report_id=report_id,
                        prepared_by=prepared_by,
                        reviewed_by=reviewed_by,
                        approved_by=approved_by
                    )

                    st.success(f"✅ Report {report_id} generated successfully!")

                    # Display report
                    st.subheader("Executive Summary")
                    st.text(report.executive_summary)

                    st.subheader("Analysis")
                    st.markdown(report.analysis)

                    st.subheader("Conclusion")
                    st.markdown(report.conclusion)

                    st.subheader("Recommendations")
                    for rec in report.recommendations:
                        st.write(f"- {rec}")

                    # Export options
                    st.subheader("Export Report")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📄 Export as JSON"):
                            json_str = json.dumps(report.to_dict(), indent=2)
                            st.download_button(
                                label="Download JSON",
                                data=json_str,
                                file_name=f"{report_id}.json",
                                mime="application/json"
                            )
                    with col2:
                        if st.button("📊 Export Measurements as CSV"):
                            st.info("CSV export functionality available")

    def show_quality_management(self):
        """Display quality management page"""
        st.header("Quality Management System")

        tabs = st.tabs(["Nonconformance Reports", "Change Control", "Training Records", "Audit Trail"])

        with tabs[0]:
            st.subheader("Nonconformance Reports")
            st.info("Track and manage nonconformance events")
            # Add NCR form and list

        with tabs[1]:
            st.subheader("Change Control")
            st.info("Manage protocol and procedure changes")
            # Add change control form

        with tabs[2]:
            st.subheader("Training Records")
            st.info("Personnel training and competency tracking")
            # Add training records

        with tabs[3]:
            st.subheader("Audit Trail")
            st.info("System activity and change history")
            # Add audit trail viewer

    def show_equipment_calibration(self):
        """Display equipment calibration page"""
        st.header("Equipment Calibration Management")

        # Display required equipment
        st.subheader("Required Equipment")
        equipment_data = self.handler.protocol_data['equipment_required']

        for eq in equipment_data:
            with st.expander(f"{eq['name']} ({eq['id']})"):
                st.write(f"**Description:** {eq['description']}")
                st.write(f"**Calibration Required:** {'Yes' if eq.get('calibration_required', False) else 'No'}")
                if eq.get('calibration_required'):
                    st.write(f"**Calibration Interval:** {eq.get('calibration_interval_days', 'N/A')} days")

        # Calibration status
        st.subheader("Calibration Status")
        st.info("Equipment calibration tracking system")

    def show_help_documentation(self):
        """Display help and documentation page"""
        st.header("Help & Documentation")

        st.subheader("Quick Start Guide")
        st.markdown("""
        1. **Sample Registration**: Register your PV module sample with all required information
        2. **Test Execution**: Create a test session and record real-time measurements
        3. **Data Analysis**: Review temperature profiles, flame spread, and acceptance criteria
        4. **Generate Reports**: Create comprehensive test reports with signatures
        5. **Quality Management**: Track nonconformances, training, and calibrations
        """)

        st.subheader("Standard Reference")
        st.write("**IEC 61730-2 MST 23: Fire Resistance Test**")
        st.write("This protocol implements the requirements specified in IEC 61730-2 for photovoltaic module safety qualification.")

        st.subheader("Contact Support")
        st.info("For technical support or questions, contact your LIMS administrator.")


def main():
    """Application entry point"""
    app = FireResistanceUI()
    app.run()


if __name__ == "__main__":
    main()
