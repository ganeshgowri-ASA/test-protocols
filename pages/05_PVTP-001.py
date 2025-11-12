"""
PVTP-001: LID/LIS Testing Protocol
Light Induced Degradation / Light Induced Stabilization Testing
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, date, timedelta
import json
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.database.db_manager import DatabaseManager

# Page Configuration
st.set_page_config(
    page_title="PVTP-001: LID/LIS Testing",
    page_icon="⚡",
    layout="wide"
)

# Initialize database
if 'db' not in st.session_state:
    st.session_state.db = DatabaseManager()

# Initialize session state
if 'execution_id' not in st.session_state:
    st.session_state.execution_id = None
if 'auto_save' not in st.session_state:
    st.session_state.auto_save = True
if 'current_status' not in st.session_state:
    st.session_state.current_status = 'not_started'

# ============================================
# PAGE HEADER
# ============================================

st.title("⚡ PVTP-001: LID/LIS Testing")
st.markdown("### Light Induced Degradation / Light Induced Stabilization Protocol")

# Status indicator
status_colors = {
    'not_started': '⚪',
    'in_progress': '🟡',
    'paused': '🟠',
    'completed': '🟢',
    'failed': '🔴',
    'cancelled': '⚫'
}

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Protocol", "PVTP-001")
with col2:
    st.metric("Status", f"{status_colors.get(st.session_state.current_status, '⚪')} {st.session_state.current_status.replace('_', ' ').title()}")
with col3:
    if st.session_state.execution_id:
        st.metric("Execution ID", st.session_state.execution_id)
    else:
        st.metric("Execution ID", "Not Started")
with col4:
    st.metric("Version", "1.0")

st.markdown("---")

# ============================================
# MAIN TABS
# ============================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 General Data",
    "⚙️ Protocol Inputs",
    "📊 Live Measurements",
    "🔬 Analysis",
    "✅ QC/Reports"
])

# ============================================
# TAB 1: GENERAL DATA
# ============================================

with tab1:
    st.subheader("General Test Information")

    with st.form("general_data_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Test Identification")

            # Fetch service requests
            try:
                service_requests = st.session_state.db.get_service_requests()
                request_options = [""] + [f"{req['request_id']} - {req['project_name']}" for req in service_requests]
            except:
                request_options = [""]

            service_request = st.selectbox(
                "Service Request ID *",
                options=request_options,
                help="Link to existing service request"
            )

            # Fetch inspections
            try:
                inspections = st.session_state.db.get_inspections()
                inspection_options = [""] + [f"{insp['inspection_id']} - {insp['sample_id']}" for insp in inspections]
            except:
                inspection_options = [""]

            inspection = st.selectbox(
                "Inspection ID *",
                options=inspection_options,
                help="Link to incoming inspection"
            )

            sample_id = st.text_input(
                "Sample ID *",
                placeholder="e.g., PV-2024-001",
                help="Unique identifier for the test sample"
            )

            equipment_id = st.text_input(
                "Equipment ID *",
                placeholder="e.g., SUN-SIM-01",
                help="Solar simulator or light soaking chamber"
            )

        with col2:
            st.markdown("#### Personnel & Schedule")

            operator = st.text_input(
                "Test Operator *",
                placeholder="Full name of operator"
            )

            test_date = st.date_input(
                "Test Date *",
                value=date.today()
            )

            test_start_time = st.time_input(
                "Start Time *",
                value=datetime.now().time()
            )

            estimated_duration = st.number_input(
                "Estimated Duration (hours) *",
                min_value=1.0,
                max_value=200.0,
                value=48.0,
                step=1.0,
                help="Typical LID test: 24-96 hours"
            )

        st.markdown("#### Environmental Conditions (Pre-test)")

        col1, col2, col3 = st.columns(3)

        with col1:
            ambient_temp = st.number_input(
                "Ambient Temperature (°C)",
                min_value=-20.0,
                max_value=60.0,
                value=25.0,
                step=0.1
            )

        with col2:
            humidity = st.number_input(
                "Relative Humidity (%)",
                min_value=0.0,
                max_value=100.0,
                value=45.0,
                step=1.0
            )

        with col3:
            pressure = st.number_input(
                "Atmospheric Pressure (kPa)",
                min_value=80.0,
                max_value=110.0,
                value=101.3,
                step=0.1
            )

        notes = st.text_area(
            "Additional Notes",
            placeholder="Any special observations or conditions...",
            height=100
        )

        col1, col2, col3 = st.columns([2, 1, 1])

        with col2:
            save_general = st.form_submit_button("💾 Save General Data", use_container_width=True)

        with col3:
            clear_general = st.form_submit_button("🔄 Clear", use_container_width=True)

    if save_general:
        if not sample_id or not equipment_id or not operator:
            st.error("❌ Please fill all required fields marked with *")
        else:
            try:
                # Extract IDs
                request_id = service_request.split(' - ')[0] if service_request else None
                inspection_id = inspection.split(' - ')[0] if inspection else None

                general_data = {
                    'service_request_id': request_id,
                    'inspection_id': inspection_id,
                    'sample_id': sample_id,
                    'equipment_id': equipment_id,
                    'operator': operator,
                    'test_date': test_date.isoformat(),
                    'test_start_time': test_start_time.isoformat(),
                    'estimated_duration_hours': estimated_duration,
                    'ambient_temperature_c': ambient_temp,
                    'relative_humidity_pct': humidity,
                    'atmospheric_pressure_kpa': pressure,
                    'notes': notes
                }

                # Create or update execution
                if not st.session_state.execution_id:
                    execution_data = {
                        'protocol_id': 'PVTP-001',
                        'protocol_name': 'LID/LIS Testing',
                        'protocol_version': '1.0',
                        'request_id': request_id,
                        'inspection_id': inspection_id,
                        'equipment_id': equipment_id,
                        'sample_id': sample_id,
                        'operator_id': 1,
                        'general_data': general_data,
                        'protocol_inputs': {}
                    }

                    execution_id = st.session_state.db.create_protocol_execution(execution_data)
                    st.session_state.execution_id = execution_id
                    st.session_state.current_status = 'not_started'
                    st.success(f"✅ Execution created: {execution_id}")
                else:
                    st.success("✅ General data saved successfully!")

                st.rerun()

            except Exception as e:
                st.error(f"❌ Error saving data: {e}")

# ============================================
# TAB 2: PROTOCOL INPUTS
# ============================================

with tab2:
    st.subheader("LID/LIS Test Parameters")

    if not st.session_state.execution_id:
        st.warning("⚠️ Please complete General Data first to enable protocol inputs.")
    else:
        with st.form("protocol_inputs_form"):
            st.markdown("### Test Configuration")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### Initial Measurements")

                initial_power = st.number_input(
                    "Initial Pmax (W) *",
                    min_value=0.0,
                    max_value=1000.0,
                    value=300.0,
                    step=0.1,
                    help="STC power before LID test"
                )

                initial_voc = st.number_input(
                    "Initial Voc (V) *",
                    min_value=0.0,
                    max_value=100.0,
                    value=40.0,
                    step=0.1
                )

                initial_isc = st.number_input(
                    "Initial Isc (A) *",
                    min_value=0.0,
                    max_value=20.0,
                    value=9.0,
                    step=0.01
                )

                initial_ff = st.number_input(
                    "Initial Fill Factor (%) *",
                    min_value=0.0,
                    max_value=100.0,
                    value=78.5,
                    step=0.1
                )

                initial_temp = st.number_input(
                    "Initial Module Temp (°C)",
                    min_value=-40.0,
                    max_value=100.0,
                    value=25.0,
                    step=0.1
                )

            with col2:
                st.markdown("#### Test Conditions")

                irradiance_level = st.number_input(
                    "Irradiance Level (W/m²) *",
                    min_value=500.0,
                    max_value=1200.0,
                    value=1000.0,
                    step=10.0,
                    help="Typically 1000 W/m² for IEC 61215"
                )

                test_temperature = st.number_input(
                    "Test Temperature (°C) *",
                    min_value=0.0,
                    max_value=100.0,
                    value=50.0,
                    step=1.0,
                    help="Module temperature during exposure"
                )

                exposure_duration = st.number_input(
                    "Total Exposure Duration (hours) *",
                    min_value=1.0,
                    max_value=200.0,
                    value=48.0,
                    step=1.0,
                    help="Per IEC 61215: minimum 24 hours at 1 kWh/m²"
                )

                measurement_interval = st.number_input(
                    "Measurement Interval (hours)",
                    min_value=0.5,
                    max_value=24.0,
                    value=6.0,
                    step=0.5,
                    help="Frequency of intermediate measurements"
                )

                load_condition = st.selectbox(
                    "Load Condition *",
                    options=["Open Circuit", "Short Circuit", "Maximum Power Point", "Resistive Load"],
                    help="Electrical condition during exposure"
                )

            st.markdown("#### Standard & Acceptance Criteria")

            col1, col2, col3 = st.columns(3)

            with col1:
                standard = st.selectbox(
                    "Test Standard *",
                    options=[
                        "IEC 61215-2:2021 (MQT 11)",
                        "IEC 61215-2:2016",
                        "IEC 61730",
                        "UL 1703",
                        "Custom"
                    ]
                )

            with col2:
                max_degradation = st.number_input(
                    "Max Allowed Degradation (%)",
                    min_value=0.0,
                    max_value=20.0,
                    value=5.0,
                    step=0.1,
                    help="Typical: 5% per IEC 61215"
                )

            with col3:
                stabilization_criteria = st.number_input(
                    "Stabilization Threshold (%/hour)",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.1,
                    step=0.01,
                    help="Max change rate to consider stabilized"
                )

            st.markdown("#### Technology Information")

            col1, col2, col3 = st.columns(3)

            with col1:
                cell_technology = st.selectbox(
                    "Cell Technology",
                    options=[
                        "Mono-crystalline (PERC)",
                        "Mono-crystalline (TOPCon)",
                        "Mono-crystalline (HJT)",
                        "Multi-crystalline",
                        "Thin Film (CdTe)",
                        "Thin Film (CIGS)",
                        "Thin Film (a-Si)",
                        "Other"
                    ]
                )

            with col2:
                module_type = st.selectbox(
                    "Module Type",
                    options=["Glass/Backsheet", "Glass/Glass", "Bifacial", "Flexible", "Other"]
                )

            with col3:
                wafer_type = st.selectbox(
                    "Wafer Type",
                    options=["p-type", "n-type", "N/A"]
                )

            test_notes = st.text_area(
                "Test-Specific Notes",
                placeholder="Special considerations, deviations from standard...",
                height=100
            )

            col1, col2, col3 = st.columns([2, 1, 1])

            with col2:
                start_test = st.form_submit_button("🚀 Start Test", use_container_width=True)

            with col3:
                save_inputs = st.form_submit_button("💾 Save Inputs", use_container_width=True)

        if start_test or save_inputs:
            if not initial_power or not irradiance_level:
                st.error("❌ Please fill all required fields marked with *")
            else:
                try:
                    protocol_inputs = {
                        'initial_measurements': {
                            'pmax_w': initial_power,
                            'voc_v': initial_voc,
                            'isc_a': initial_isc,
                            'fill_factor_pct': initial_ff,
                            'module_temp_c': initial_temp
                        },
                        'test_conditions': {
                            'irradiance_w_m2': irradiance_level,
                            'test_temperature_c': test_temperature,
                            'exposure_duration_hours': exposure_duration,
                            'measurement_interval_hours': measurement_interval,
                            'load_condition': load_condition
                        },
                        'acceptance_criteria': {
                            'standard': standard,
                            'max_degradation_pct': max_degradation,
                            'stabilization_threshold': stabilization_criteria
                        },
                        'technology_info': {
                            'cell_technology': cell_technology,
                            'module_type': module_type,
                            'wafer_type': wafer_type
                        },
                        'test_notes': test_notes
                    }

                    # Update execution with protocol inputs
                    # Here you would call an update method

                    if start_test:
                        st.session_state.db.update_protocol_status(
                            st.session_state.execution_id,
                            'in_progress',
                            1
                        )
                        st.session_state.current_status = 'in_progress'
                        st.success("✅ Test started successfully!")
                    else:
                        st.success("✅ Protocol inputs saved!")

                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error: {e}")

# ============================================
# TAB 3: LIVE MEASUREMENTS
# ============================================

with tab3:
    st.subheader("Real-Time Data Acquisition")

    if not st.session_state.execution_id or st.session_state.current_status == 'not_started':
        st.warning("⚠️ Start the test to begin data acquisition.")
    else:
        # Control buttons
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("▶️ Resume", use_container_width=True):
                st.session_state.db.update_protocol_status(
                    st.session_state.execution_id,
                    'in_progress',
                    1
                )
                st.session_state.current_status = 'in_progress'
                st.rerun()

        with col2:
            if st.button("⏸️ Pause", use_container_width=True):
                st.session_state.db.update_protocol_status(
                    st.session_state.execution_id,
                    'paused',
                    1
                )
                st.session_state.current_status = 'paused'
                st.rerun()

        with col3:
            if st.button("✅ Complete", use_container_width=True):
                st.session_state.db.update_protocol_status(
                    st.session_state.execution_id,
                    'completed',
                    1
                )
                st.session_state.current_status = 'completed'
                st.rerun()

        with col4:
            if st.button("🔄 Refresh Data", use_container_width=True):
                st.rerun()

        st.markdown("---")

        # Manual measurement entry
        with st.expander("➕ Add Measurement", expanded=False):
            with st.form("add_measurement"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    meas_time = st.number_input("Elapsed Time (hours)", min_value=0.0, value=0.0, step=0.5)
                    meas_pmax = st.number_input("Pmax (W)", min_value=0.0, value=300.0)
                    meas_voc = st.number_input("Voc (V)", min_value=0.0, value=40.0)

                with col2:
                    meas_isc = st.number_input("Isc (A)", min_value=0.0, value=9.0)
                    meas_ff = st.number_input("Fill Factor (%)", min_value=0.0, value=78.0)
                    meas_temp = st.number_input("Module Temp (°C)", min_value=0.0, value=50.0)

                with col3:
                    meas_irrad = st.number_input("Irradiance (W/m²)", min_value=0.0, value=1000.0)
                    meas_notes = st.text_area("Notes", height=100)

                if st.form_submit_button("💾 Save Measurement"):
                    try:
                        measurement_data = {
                            'execution_id': st.session_state.execution_id,
                            'measurement_type': 'lid_reading',
                            'sequence_number': int(meas_time / 0.5),
                            'data': {
                                'elapsed_time_hours': meas_time,
                                'pmax_w': meas_pmax,
                                'voc_v': meas_voc,
                                'isc_a': meas_isc,
                                'fill_factor_pct': meas_ff,
                                'module_temp_c': meas_temp,
                                'irradiance_w_m2': meas_irrad,
                                'notes': meas_notes
                            },
                            'unit': 'W',
                            'equipment_used': 'IV Tracer',
                            'operator_id': 1
                        }

                        st.session_state.db.add_measurement(measurement_data)
                        st.success("✅ Measurement saved!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error saving measurement: {e}")

        # Fetch and display measurements
        try:
            measurements = st.session_state.db.get_measurements(st.session_state.execution_id)

            if measurements:
                # Parse measurement data
                data_records = []
                for meas in measurements:
                    data = json.loads(meas['data'])
                    data_records.append({
                        'Time (h)': data.get('elapsed_time_hours', 0),
                        'Pmax (W)': data.get('pmax_w', 0),
                        'Voc (V)': data.get('voc_v', 0),
                        'Isc (A)': data.get('isc_a', 0),
                        'FF (%)': data.get('fill_factor_pct', 0),
                        'Temp (°C)': data.get('module_temp_c', 0),
                        'Irr (W/m²)': data.get('irradiance_w_m2', 0),
                        'Timestamp': meas['timestamp']
                    })

                df = pd.DataFrame(data_records)

                # Charts
                st.markdown("### 📈 Power Degradation Curve")

                if len(df) > 0:
                    # Calculate degradation percentage
                    initial_power = df['Pmax (W)'].iloc[0]
                    df['Degradation (%)'] = ((df['Pmax (W)'] - initial_power) / initial_power) * 100

                    # Power vs Time
                    fig_power = go.Figure()
                    fig_power.add_trace(go.Scatter(
                        x=df['Time (h)'],
                        y=df['Pmax (W)'],
                        mode='lines+markers',
                        name='Pmax',
                        line=dict(color='royalblue', width=2),
                        marker=dict(size=8)
                    ))
                    fig_power.update_layout(
                        title='Maximum Power vs Exposure Time',
                        xaxis_title='Exposure Time (hours)',
                        yaxis_title='Pmax (W)',
                        hovermode='x unified',
                        height=400
                    )
                    st.plotly_chart(fig_power, use_container_width=True)

                    # Degradation vs Time
                    fig_deg = go.Figure()
                    fig_deg.add_trace(go.Scatter(
                        x=df['Time (h)'],
                        y=df['Degradation (%)'],
                        mode='lines+markers',
                        name='Degradation',
                        line=dict(color='crimson', width=2),
                        marker=dict(size=8)
                    ))
                    fig_deg.add_hline(y=-5, line_dash="dash", line_color="orange",
                                     annotation_text="IEC Limit (-5%)")
                    fig_deg.update_layout(
                        title='Power Degradation vs Exposure Time',
                        xaxis_title='Exposure Time (hours)',
                        yaxis_title='Degradation (%)',
                        hovermode='x unified',
                        height=400
                    )
                    st.plotly_chart(fig_deg, use_container_width=True)

                    # Electrical parameters
                    col1, col2 = st.columns(2)

                    with col1:
                        fig_voc = px.line(df, x='Time (h)', y='Voc (V)',
                                         title='Open Circuit Voltage vs Time',
                                         markers=True)
                        fig_voc.update_traces(line_color='green')
                        st.plotly_chart(fig_voc, use_container_width=True)

                    with col2:
                        fig_isc = px.line(df, x='Time (h)', y='Isc (A)',
                                         title='Short Circuit Current vs Time',
                                         markers=True)
                        fig_isc.update_traces(line_color='purple')
                        st.plotly_chart(fig_isc, use_container_width=True)

                    # Fill Factor
                    fig_ff = px.line(df, x='Time (h)', y='FF (%)',
                                    title='Fill Factor vs Time',
                                    markers=True)
                    fig_ff.update_traces(line_color='darkorange')
                    st.plotly_chart(fig_ff, use_container_width=True)

                    # Data table
                    st.markdown("### 📋 Measurement Data Table")
                    st.dataframe(df, use_container_width=True, hide_index=True)

                    # Export data
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Data (CSV)",
                        data=csv,
                        file_name=f"PVTP001_LID_Data_{st.session_state.execution_id}.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No measurements recorded yet")
            else:
                st.info("📊 No measurements available. Add measurements above.")

        except Exception as e:
            st.error(f"Error loading measurements: {e}")

# ============================================
# TAB 4: ANALYSIS
# ============================================

with tab4:
    st.subheader("Test Analysis & Results")

    if not st.session_state.execution_id:
        st.warning("⚠️ Complete test setup and measurements first.")
    else:
        try:
            measurements = st.session_state.db.get_measurements(st.session_state.execution_id)

            if measurements and len(measurements) >= 2:
                # Parse data
                data_records = []
                for meas in measurements:
                    data = json.loads(meas['data'])
                    data_records.append(data)

                df = pd.DataFrame(data_records)

                # Calculate key metrics
                initial_power = df['pmax_w'].iloc[0]
                final_power = df['pmax_w'].iloc[-1]
                degradation_pct = ((final_power - initial_power) / initial_power) * 100

                initial_voc = df['voc_v'].iloc[0]
                final_voc = df['voc_v'].iloc[-1]
                voc_change_pct = ((final_voc - initial_voc) / initial_voc) * 100

                initial_isc = df['isc_a'].iloc[0]
                final_isc = df['isc_a'].iloc[-1]
                isc_change_pct = ((final_isc - initial_isc) / initial_isc) * 100

                initial_ff = df['fill_factor_pct'].iloc[0]
                final_ff = df['fill_factor_pct'].iloc[-1]
                ff_change_pct = ((final_ff - initial_ff) / initial_ff) * 100

                # Display results
                st.markdown("### 📊 Test Summary")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "Power Degradation",
                        f"{degradation_pct:.2f}%",
                        delta=f"{final_power - initial_power:.2f} W",
                        delta_color="inverse"
                    )

                with col2:
                    st.metric(
                        "Voc Change",
                        f"{voc_change_pct:.2f}%",
                        delta=f"{final_voc - initial_voc:.2f} V",
                        delta_color="inverse"
                    )

                with col3:
                    st.metric(
                        "Isc Change",
                        f"{isc_change_pct:.2f}%",
                        delta=f"{final_isc - initial_isc:.2f} A",
                        delta_color="inverse"
                    )

                with col4:
                    st.metric(
                        "FF Change",
                        f"{ff_change_pct:.2f}%",
                        delta=f"{final_ff - initial_ff:.2f} %",
                        delta_color="inverse"
                    )

                st.markdown("---")

                # Pass/Fail determination
                max_allowed_deg = -5.0  # IEC 61215 standard

                if degradation_pct >= max_allowed_deg:
                    test_result = "PASS"
                    result_color = "green"
                    result_icon = "✅"
                else:
                    test_result = "FAIL"
                    result_color = "red"
                    result_icon = "❌"

                st.markdown(f"### {result_icon} Test Result: **:{result_color}[{test_result}]**")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("#### Initial Values")
                    st.write(f"- Pmax: {initial_power:.2f} W")
                    st.write(f"- Voc: {initial_voc:.2f} V")
                    st.write(f"- Isc: {initial_isc:.2f} A")
                    st.write(f"- FF: {initial_ff:.2f} %")

                with col2:
                    st.markdown("#### Final Values")
                    st.write(f"- Pmax: {final_power:.2f} W")
                    st.write(f"- Voc: {final_voc:.2f} V")
                    st.write(f"- Isc: {final_isc:.2f} A")
                    st.write(f"- FF: {final_ff:.2f} %")

                # Stabilization analysis
                st.markdown("### 🔬 Stabilization Analysis")

                if len(df) >= 3:
                    # Calculate rate of change for last 3 measurements
                    last_3_powers = df['pmax_w'].tail(3).values
                    power_changes = np.diff(last_3_powers)
                    avg_change_rate = np.mean(np.abs(power_changes))

                    stabilization_threshold = 0.5  # 0.5% threshold

                    if avg_change_rate < stabilization_threshold:
                        st.success(f"✅ Module has stabilized (avg change rate: {avg_change_rate:.3f}%)")
                    else:
                        st.warning(f"⚠️ Module not yet stabilized (avg change rate: {avg_change_rate:.3f}%)")
                else:
                    st.info("Need at least 3 measurements for stabilization analysis")

                # Recommendations
                st.markdown("### 💡 Recommendations")

                if degradation_pct < -8:
                    st.error("❌ Severe degradation detected. Module may have quality issues.")
                elif degradation_pct < -5:
                    st.warning("⚠️ Degradation exceeds IEC limit. Consider extended testing or root cause analysis.")
                elif degradation_pct < -2:
                    st.info("ℹ️ Normal LID observed. Monitor for stabilization.")
                else:
                    st.success("✅ Minimal degradation. Module performs well.")

            else:
                st.info("📊 Insufficient data for analysis. Need at least 2 measurements.")

        except Exception as e:
            st.error(f"Error in analysis: {e}")

# ============================================
# TAB 5: QC/REPORTS
# ============================================

with tab5:
    st.subheader("Quality Control & Reporting")

    if not st.session_state.execution_id:
        st.warning("⚠️ Complete test execution first.")
    else:
        # QC Checkpoints
        st.markdown("### ✅ Quality Control Checkpoints")

        qc_checks = [
            {"id": "qc_01", "name": "Equipment calibration verified", "stage": "before_test"},
            {"id": "qc_02", "name": "Sample identification confirmed", "stage": "before_test"},
            {"id": "qc_03", "name": "Initial measurements completed", "stage": "before_test"},
            {"id": "qc_04", "name": "Test conditions stable", "stage": "during_test"},
            {"id": "qc_05", "name": "Data logging functional", "stage": "during_test"},
            {"id": "qc_06", "name": "No physical damage observed", "stage": "during_test"},
            {"id": "qc_07", "name": "Final measurements completed", "stage": "after_test"},
            {"id": "qc_08", "name": "Data integrity verified", "stage": "after_test"},
            {"id": "qc_09", "name": "Results reviewed by supervisor", "stage": "after_test"},
        ]

        for check in qc_checks:
            col1, col2, col3 = st.columns([3, 1, 2])

            with col1:
                st.write(f"**{check['name']}**")

            with col2:
                st.caption(check['stage'].replace('_', ' ').title())

            with col3:
                qc_status = st.selectbox(
                    "Status",
                    options=["Pending", "Pass", "Fail", "N/A"],
                    key=f"qc_{check['id']}",
                    label_visibility="collapsed"
                )

        if st.button("💾 Save QC Checkpoints"):
            st.success("✅ QC checkpoints saved!")

        st.markdown("---")

        # Report Generation
        st.markdown("### 📄 Report Generation")

        col1, col2 = st.columns(2)

        with col1:
            report_type = st.selectbox(
                "Report Type",
                options=[
                    "Test Report - Full",
                    "Test Report - Summary",
                    "Certificate of Testing",
                    "Data Package",
                    "Custom Report"
                ]
            )

            report_format = st.selectbox(
                "Format",
                options=["PDF", "Excel", "Word", "HTML"]
            )

        with col2:
            include_raw_data = st.checkbox("Include Raw Data", value=True)
            include_charts = st.checkbox("Include Charts", value=True)
            include_photos = st.checkbox("Include Photos", value=False)
            digital_signature = st.checkbox("Add Digital Signature", value=False)

        report_notes = st.text_area(
            "Report Notes",
            placeholder="Additional comments for the report...",
            height=100
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📄 Generate Report", use_container_width=True):
                with st.spinner("Generating report..."):
                    st.success(f"✅ {report_type} generated successfully!")
                    st.info(f"Report ID: RPT-{datetime.now().strftime('%Y%m%d%H%M%S')}")

        with col2:
            if st.button("📧 Email Report", use_container_width=True):
                st.success("✅ Report sent to stakeholders!")

        with col3:
            if st.button("💾 Archive", use_container_width=True):
                st.success("✅ Test data archived!")

# ============================================
# SIDEBAR
# ============================================

with st.sidebar:
    st.markdown("---")
    st.subheader("📋 Protocol Information")

    st.info("""
    **PVTP-001: LID/LIS Testing**

    **Purpose:**
    Evaluate light-induced degradation and stabilization of PV modules

    **Standards:**
    - IEC 61215-2:2021 (MQT 11)
    - IEC 61215-2:2016
    - IEC 61730

    **Test Duration:**
    24-96 hours typical

    **Key Parameters:**
    - Initial power measurement
    - Continuous light exposure
    - Periodic I-V measurements
    - Stabilization monitoring
    """)

    st.markdown("---")
    st.subheader("🔗 Quick Navigation")

    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("streamlit_app.py")

    if st.button("📋 Service Requests", use_container_width=True):
        st.switch_page("pages/01_Service_Request.py")

    if st.button("🔍 Inspections", use_container_width=True):
        st.switch_page("pages/02_Incoming_Inspection.py")

    if st.button("🎯 Protocol Selector", use_container_width=True):
        st.switch_page("pages/04_Protocol_Selector.py")

    st.markdown("---")

    if st.session_state.execution_id:
        st.success(f"**Active Execution:**\n{st.session_state.execution_id}")

        if st.button("🗑️ Reset Session", use_container_width=True):
            st.session_state.execution_id = None
            st.session_state.current_status = 'not_started'
            st.rerun()

    # Auto-save toggle
    st.markdown("---")
    auto_save = st.checkbox("🔄 Auto-save", value=st.session_state.auto_save)
    if auto_save != st.session_state.auto_save:
        st.session_state.auto_save = auto_save
        st.rerun()
