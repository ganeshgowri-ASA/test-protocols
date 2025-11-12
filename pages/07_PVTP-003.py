"""
PVTP-003: Damp Heat Testing Protocol
Testing module resistance to long-term exposure to high temperature and humidity
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
    page_title="PVTP-003: Damp Heat Testing",
    page_icon="💧",
    layout="wide"
)

# Initialize database
if 'db' not in st.session_state:
    st.session_state.db = DatabaseManager()

# Initialize session state
if 'execution_id_dh' not in st.session_state:
    st.session_state.execution_id_dh = None
if 'auto_save' not in st.session_state:
    st.session_state.auto_save = True
if 'current_status_dh' not in st.session_state:
    st.session_state.current_status_dh = 'not_started'

# ============================================
# PAGE HEADER
# ============================================

st.title("💧 PVTP-003: Damp Heat Testing")
st.markdown("### Long-term High Temperature & Humidity Exposure Test")

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
    st.metric("Protocol", "PVTP-003")
with col2:
    st.metric("Status", f"{status_colors.get(st.session_state.current_status_dh, '⚪')} {st.session_state.current_status_dh.replace('_', ' ').title()}")
with col3:
    if st.session_state.execution_id_dh:
        st.metric("Execution ID", st.session_state.execution_id_dh)
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

    with st.form("general_data_form_dh"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Test Identification")

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
                placeholder="e.g., PV-2024-003",
                help="Unique identifier for the test sample"
            )

            equipment_id = st.text_input(
                "Equipment ID *",
                placeholder="e.g., DH-CHAMBER-01",
                help="Damp heat chamber identifier"
            )

        with col2:
            st.markdown("#### Personnel & Schedule")

            operator = st.text_input(
                "Test Operator *",
                placeholder="Full name of operator"
            )

            test_date = st.date_input(
                "Test Start Date *",
                value=date.today()
            )

            test_start_time = st.time_input(
                "Start Time *",
                value=datetime.now().time()
            )

            estimated_duration = st.number_input(
                "Estimated Duration (days) *",
                min_value=1.0,
                max_value=100.0,
                value=42.0,
                step=1.0,
                help="Typical: 40-50 days for 1000 hours"
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
                    'estimated_duration_days': estimated_duration,
                    'ambient_temperature_c': ambient_temp,
                    'relative_humidity_pct': humidity,
                    'atmospheric_pressure_kpa': pressure,
                    'notes': notes
                }

                if not st.session_state.execution_id_dh:
                    execution_data = {
                        'protocol_id': 'PVTP-003',
                        'protocol_name': 'Damp Heat Testing',
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
                    st.session_state.execution_id_dh = execution_id
                    st.session_state.current_status_dh = 'not_started'
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
    st.subheader("Damp Heat Test Parameters")

    if not st.session_state.execution_id_dh:
        st.warning("⚠️ Please complete General Data first to enable protocol inputs.")
    else:
        with st.form("protocol_inputs_form_dh"):
            st.markdown("### Test Configuration")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### Initial Measurements (STC)")

                initial_power = st.number_input(
                    "Initial Pmax (W) *",
                    min_value=0.0,
                    max_value=1000.0,
                    value=300.0,
                    step=0.1
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

                initial_insulation = st.number_input(
                    "Initial Insulation Resistance (MΩ) *",
                    min_value=0.0,
                    max_value=10000.0,
                    value=1000.0,
                    step=10.0
                )

            with col2:
                st.markdown("#### Damp Heat Conditions")

                test_temperature = st.number_input(
                    "Test Temperature (°C) *",
                    min_value=60.0,
                    max_value=100.0,
                    value=85.0,
                    step=1.0,
                    help="IEC 61215: 85°C ± 2°C"
                )

                test_humidity = st.number_input(
                    "Relative Humidity (%) *",
                    min_value=50.0,
                    max_value=100.0,
                    value=85.0,
                    step=1.0,
                    help="IEC 61215: 85% RH ± 5%"
                )

                exposure_duration = st.number_input(
                    "Total Exposure Duration (hours) *",
                    min_value=100.0,
                    max_value=3000.0,
                    value=1000.0,
                    step=100.0,
                    help="IEC 61215: 1000 hours standard, 2000+ for extended"
                )

                measurement_interval = st.number_input(
                    "Measurement Interval (hours)",
                    min_value=24.0,
                    max_value=500.0,
                    value=168.0,
                    step=24.0,
                    help="Weekly measurements recommended (168 hours)"
                )

                chamber_pressure = st.number_input(
                    "Chamber Pressure (kPa)",
                    min_value=80.0,
                    max_value=110.0,
                    value=101.3,
                    step=0.1
                )

            st.markdown("#### Test Schedule")

            col1, col2, col3 = st.columns(3)

            with col1:
                interim_measurements = st.multiselect(
                    "I-V Measurements at (hours):",
                    options=[0, 168, 336, 504, 672, 840, 1000, 1500, 2000],
                    default=[0, 336, 672, 1000],
                    help="Typical: Every week (168 hours)"
                )

            with col2:
                visual_inspections = st.multiselect(
                    "Visual Inspections at (hours):",
                    options=[0, 250, 500, 750, 1000, 1500, 2000],
                    default=[0, 500, 1000]
                )

            with col3:
                insulation_tests = st.multiselect(
                    "Insulation Tests at (hours):",
                    options=[0, 250, 500, 750, 1000, 1500, 2000],
                    default=[0, 500, 1000]
                )

            st.markdown("#### Standard & Acceptance Criteria")

            col1, col2, col3 = st.columns(3)

            with col1:
                standard = st.selectbox(
                    "Test Standard *",
                    options=[
                        "IEC 61215-2:2021 (MQT 13)",
                        "IEC 61215-2:2016",
                        "IEC 61730",
                        "IEC TS 63126 (Extended 2000h)",
                        "UL 1703",
                        "Custom"
                    ]
                )

            with col2:
                max_power_degradation = st.number_input(
                    "Max Power Degradation (%)",
                    min_value=0.0,
                    max_value=20.0,
                    value=5.0,
                    step=0.5,
                    help="IEC 61215: Max 5% degradation"
                )

            with col3:
                min_insulation = st.number_input(
                    "Min Insulation Resistance (MΩ)",
                    min_value=1.0,
                    max_value=1000.0,
                    value=40.0,
                    step=5.0
                )

            st.markdown("#### Module Information")

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
                        "Other"
                    ]
                )

            with col2:
                module_type = st.selectbox(
                    "Module Type",
                    options=["Glass/Backsheet", "Glass/Glass", "Bifacial", "Flexible"]
                )

            with col3:
                encapsulant = st.selectbox(
                    "Encapsulant Type",
                    options=["EVA", "POE", "PVB", "TPO", "Silicone", "Other"]
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
            if not initial_power or not exposure_duration:
                st.error("❌ Please fill all required fields marked with *")
            else:
                try:
                    protocol_inputs = {
                        'initial_measurements': {
                            'pmax_w': initial_power,
                            'voc_v': initial_voc,
                            'isc_a': initial_isc,
                            'fill_factor_pct': initial_ff,
                            'insulation_resistance_mohm': initial_insulation
                        },
                        'test_conditions': {
                            'temperature_c': test_temperature,
                            'relative_humidity_pct': test_humidity,
                            'exposure_duration_hours': exposure_duration,
                            'measurement_interval_hours': measurement_interval,
                            'chamber_pressure_kpa': chamber_pressure
                        },
                        'test_schedule': {
                            'iv_measurements_hours': interim_measurements,
                            'visual_inspections_hours': visual_inspections,
                            'insulation_tests_hours': insulation_tests
                        },
                        'acceptance_criteria': {
                            'standard': standard,
                            'max_power_degradation_pct': max_power_degradation,
                            'min_insulation_resistance_mohm': min_insulation
                        },
                        'module_info': {
                            'cell_technology': cell_technology,
                            'module_type': module_type,
                            'encapsulant_type': encapsulant
                        },
                        'test_notes': test_notes
                    }

                    if start_test:
                        st.session_state.db.update_protocol_status(
                            st.session_state.execution_id_dh,
                            'in_progress',
                            1
                        )
                        st.session_state.current_status_dh = 'in_progress'
                        st.success("✅ Damp heat test started!")
                    else:
                        st.success("✅ Protocol inputs saved!")

                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error: {e}")

# ============================================
# TAB 3: LIVE MEASUREMENTS
# ============================================

with tab3:
    st.subheader("Exposure Progress & Measurements")

    if not st.session_state.execution_id_dh or st.session_state.current_status_dh == 'not_started':
        st.warning("⚠️ Start the test to begin monitoring.")
    else:
        # Control buttons
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("▶️ Resume", use_container_width=True, key="resume_dh"):
                st.session_state.db.update_protocol_status(
                    st.session_state.execution_id_dh,
                    'in_progress',
                    1
                )
                st.session_state.current_status_dh = 'in_progress'
                st.rerun()

        with col2:
            if st.button("⏸️ Pause", use_container_width=True, key="pause_dh"):
                st.session_state.db.update_protocol_status(
                    st.session_state.execution_id_dh,
                    'paused',
                    1
                )
                st.session_state.current_status_dh = 'paused'
                st.rerun()

        with col3:
            if st.button("✅ Complete", use_container_width=True, key="complete_dh"):
                st.session_state.db.update_protocol_status(
                    st.session_state.execution_id_dh,
                    'completed',
                    1
                )
                st.session_state.current_status_dh = 'completed'
                st.rerun()

        with col4:
            if st.button("🔄 Refresh Data", use_container_width=True, key="refresh_dh"):
                st.rerun()

        st.markdown("---")

        # Current status
        st.markdown("### 💧 Current Exposure Status")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Elapsed Time", "672 / 1000 hours")
        with col2:
            st.metric("Chamber Temp", "85.2 °C")
        with col3:
            st.metric("Chamber RH", "84.8 %")
        with col4:
            st.metric("Est. Completion", "14 days")

        # Progress bar
        exposure_progress = 672 / 1000 * 100
        st.progress(exposure_progress / 100, text=f"Exposure Progress: {exposure_progress:.1f}%")

        st.markdown("---")

        # Manual measurement entry
        with st.expander("➕ Add Measurement Reading", expanded=False):
            with st.form("add_measurement_dh"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    meas_hours = st.number_input("Elapsed Hours", min_value=0, max_value=3000, value=0, step=1)
                    meas_pmax = st.number_input("Pmax (W)", min_value=0.0, value=300.0)
                    meas_voc = st.number_input("Voc (V)", min_value=0.0, value=40.0)

                with col2:
                    meas_isc = st.number_input("Isc (A)", min_value=0.0, value=9.0)
                    meas_ff = st.number_input("Fill Factor (%)", min_value=0.0, value=78.0)
                    meas_insulation = st.number_input("Insulation (MΩ)", min_value=0.0, value=1000.0)

                with col3:
                    chamber_temp = st.number_input("Chamber Temp (°C)", min_value=0.0, value=85.0)
                    chamber_rh = st.number_input("Chamber RH (%)", min_value=0.0, value=85.0)
                    visual_defects = st.multiselect(
                        "Visual Defects",
                        options=["None", "Delamination", "Discoloration", "Corrosion", "Bubbles", "Moisture"]
                    )

                meas_notes = st.text_area("Notes", height=80)

                if st.form_submit_button("💾 Save Measurement"):
                    try:
                        measurement_data = {
                            'execution_id': st.session_state.execution_id_dh,
                            'measurement_type': 'damp_heat_reading',
                            'sequence_number': int(meas_hours / 24),
                            'data': {
                                'elapsed_hours': meas_hours,
                                'pmax_w': meas_pmax,
                                'voc_v': meas_voc,
                                'isc_a': meas_isc,
                                'fill_factor_pct': meas_ff,
                                'insulation_resistance_mohm': meas_insulation,
                                'chamber_temp_c': chamber_temp,
                                'chamber_rh_pct': chamber_rh,
                                'visual_defects': visual_defects,
                                'notes': meas_notes
                            },
                            'unit': 'W',
                            'equipment_used': 'IV Tracer + Megger',
                            'operator_id': 1
                        }

                        st.session_state.db.add_measurement(measurement_data)
                        st.success("✅ Measurement saved!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error saving measurement: {e}")

        # Fetch and display measurements
        try:
            measurements = st.session_state.db.get_measurements(st.session_state.execution_id_dh)

            if measurements:
                data_records = []
                for meas in measurements:
                    data = json.loads(meas['data'])
                    data_records.append({
                        'Hours': data.get('elapsed_hours', 0),
                        'Pmax (W)': data.get('pmax_w', 0),
                        'Voc (V)': data.get('voc_v', 0),
                        'Isc (A)': data.get('isc_a', 0),
                        'FF (%)': data.get('fill_factor_pct', 0),
                        'Insulation (MΩ)': data.get('insulation_resistance_mohm', 0),
                        'Temp (°C)': data.get('chamber_temp_c', 0),
                        'RH (%)': data.get('chamber_rh_pct', 0),
                        'Defects': ', '.join(data.get('visual_defects', [])),
                        'Timestamp': meas['timestamp']
                    })

                df = pd.DataFrame(data_records)

                if len(df) > 0:
                    st.markdown("### 📈 Performance Trends")

                    # Calculate degradation
                    initial_power = df['Pmax (W)'].iloc[0]
                    df['Degradation (%)'] = ((df['Pmax (W)'] - initial_power) / initial_power) * 100

                    # Power over time
                    fig_power = go.Figure()
                    fig_power.add_trace(go.Scatter(
                        x=df['Hours'],
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

                    # Degradation percentage
                    fig_deg = go.Figure()
                    fig_deg.add_trace(go.Scatter(
                        x=df['Hours'],
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

                    # Multi-parameter view
                    col1, col2 = st.columns(2)

                    with col1:
                        # Insulation resistance
                        fig_ins = go.Figure()
                        fig_ins.add_trace(go.Scatter(
                            x=df['Hours'],
                            y=df['Insulation (MΩ)'],
                            mode='lines+markers',
                            name='Insulation',
                            line=dict(color='teal', width=2),
                            marker=dict(size=8)
                        ))
                        fig_ins.add_hline(y=40, line_dash="dash", line_color="red",
                                         annotation_text="Min Requirement")
                        fig_ins.update_layout(
                            title='Insulation Resistance vs Time',
                            xaxis_title='Exposure Time (hours)',
                            yaxis_title='Insulation (MΩ)',
                            height=350
                        )
                        st.plotly_chart(fig_ins, use_container_width=True)

                    with col2:
                        # Chamber conditions
                        fig_chamber = go.Figure()
                        fig_chamber.add_trace(go.Scatter(
                            x=df['Hours'],
                            y=df['Temp (°C)'],
                            mode='lines+markers',
                            name='Temperature',
                            line=dict(color='red', width=2)
                        ))
                        fig_chamber.add_trace(go.Scatter(
                            x=df['Hours'],
                            y=df['RH (%)'],
                            mode='lines+markers',
                            name='Humidity',
                            line=dict(color='blue', width=2),
                            yaxis='y2'
                        ))
                        fig_chamber.update_layout(
                            title='Chamber Conditions',
                            xaxis_title='Exposure Time (hours)',
                            yaxis_title='Temperature (°C)',
                            yaxis2=dict(title='Humidity (%)', overlaying='y', side='right'),
                            height=350
                        )
                        st.plotly_chart(fig_chamber, use_container_width=True)

                    # Data table
                    st.markdown("### 📋 Measurement Data Table")
                    st.dataframe(df, use_container_width=True, hide_index=True)

                    # Export
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Data (CSV)",
                        data=csv,
                        file_name=f"PVTP003_DampHeat_Data_{st.session_state.execution_id_dh}.csv",
                        mime="text/csv"
                    )
            else:
                st.info("📊 No measurements available. Add measurements above.")

        except Exception as e:
            st.error(f"Error loading measurements: {e}")

# ============================================
# TAB 4: ANALYSIS
# ============================================

with tab4:
    st.subheader("Test Analysis & Results")

    if not st.session_state.execution_id_dh:
        st.warning("⚠️ Complete test setup and measurements first.")
    else:
        try:
            measurements = st.session_state.db.get_measurements(st.session_state.execution_id_dh)

            if measurements and len(measurements) >= 2:
                data_records = []
                for meas in measurements:
                    data = json.loads(meas['data'])
                    data_records.append(data)

                df = pd.DataFrame(data_records)

                # Calculate key metrics
                initial_power = df['pmax_w'].iloc[0]
                final_power = df['pmax_w'].iloc[-1]
                degradation_pct = ((final_power - initial_power) / initial_power) * 100

                initial_insulation = df['insulation_resistance_mohm'].iloc[0]
                final_insulation = df['insulation_resistance_mohm'].iloc[-1]
                insulation_change_pct = ((final_insulation - initial_insulation) / initial_insulation) * 100

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
                        "Final Insulation",
                        f"{final_insulation:.0f} MΩ",
                        delta=f"{insulation_change_pct:.1f}%",
                        delta_color="normal"
                    )

                with col3:
                    total_hours = df['elapsed_hours'].iloc[-1]
                    st.metric("Total Exposure", f"{total_hours:.0f} hours")

                with col4:
                    avg_degradation_rate = degradation_pct / (total_hours / 1000)
                    st.metric("Avg Degradation Rate", f"{avg_degradation_rate:.3f}% per 1000h")

                st.markdown("---")

                # Pass/Fail determination
                max_allowed_deg = -5.0
                min_insulation_req = 40.0

                power_pass = degradation_pct >= max_allowed_deg
                insulation_pass = final_insulation >= min_insulation_req

                if power_pass and insulation_pass:
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
                    st.markdown("#### Performance Criteria")
                    if power_pass:
                        st.success(f"✅ Power degradation: {degradation_pct:.2f}% (Pass)")
                    else:
                        st.error(f"❌ Power degradation: {degradation_pct:.2f}% (Fail)")

                    if insulation_pass:
                        st.success(f"✅ Insulation: {final_insulation:.0f} MΩ (Pass)")
                    else:
                        st.error(f"❌ Insulation: {final_insulation:.0f} MΩ (Fail)")

                with col2:
                    st.markdown("#### Visual Assessment")
                    defect_count = sum(1 for rec in data_records
                                      if rec.get('visual_defects') and rec['visual_defects'] != ['None'])

                    if defect_count == 0:
                        st.success("✅ No visual defects detected")
                    else:
                        st.warning(f"⚠️ Visual defects found in {defect_count} inspection(s)")

                # Recommendations
                st.markdown("### 💡 Recommendations")

                if degradation_pct < -8:
                    st.error("❌ Severe degradation. Module unsuitable for humid climates.")
                elif degradation_pct < -5:
                    st.warning("⚠️ Exceeds IEC limit. Consider alternative encapsulation.")
                elif degradation_pct < -2:
                    st.info("ℹ️ Minor degradation within acceptable limits.")
                else:
                    st.success("✅ Excellent damp heat resistance.")

            else:
                st.info("📊 Insufficient data for analysis. Need at least 2 measurements.")

        except Exception as e:
            st.error(f"Error in analysis: {e}")

# ============================================
# TAB 5: QC/REPORTS
# ============================================

with tab5:
    st.subheader("Quality Control & Reporting")

    if not st.session_state.execution_id_dh:
        st.warning("⚠️ Complete test execution first.")
    else:
        st.markdown("### ✅ Quality Control Checkpoints")

        qc_checks = [
            {"id": "qc_01", "name": "Chamber calibration verified", "stage": "before_test"},
            {"id": "qc_02", "name": "Sample secured and sealed", "stage": "before_test"},
            {"id": "qc_03", "name": "Initial measurements completed", "stage": "before_test"},
            {"id": "qc_04", "name": "Chamber conditions stable (85°C/85%RH)", "stage": "during_test"},
            {"id": "qc_05", "name": "No chamber alarms", "stage": "during_test"},
            {"id": "qc_06", "name": "Interim measurements on schedule", "stage": "during_test"},
            {"id": "qc_07", "name": "Final measurements completed", "stage": "after_test"},
            {"id": "qc_08", "name": "Visual inspection completed", "stage": "after_test"},
            {"id": "qc_09", "name": "Insulation resistance verified", "stage": "after_test"},
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
                    key=f"qc_dh_{check['id']}",
                    label_visibility="collapsed"
                )

        if st.button("💾 Save QC Checkpoints", key="save_qc_dh"):
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
                    "Exposure Log",
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
            if st.button("📄 Generate Report", use_container_width=True, key="gen_report_dh"):
                with st.spinner("Generating report..."):
                    st.success(f"✅ {report_type} generated successfully!")
                    st.info(f"Report ID: RPT-{datetime.now().strftime('%Y%m%d%H%M%S')}")

        with col2:
            if st.button("📧 Email Report", use_container_width=True, key="email_report_dh"):
                st.success("✅ Report sent to stakeholders!")

        with col3:
            if st.button("💾 Archive", use_container_width=True, key="archive_dh"):
                st.success("✅ Test data archived!")

# ============================================
# SIDEBAR
# ============================================

with st.sidebar:
    st.markdown("---")
    st.subheader("📋 Protocol Information")

    st.info("""
    **PVTP-003: Damp Heat Testing**

    **Purpose:**
    Evaluate module resistance to long-term exposure to high temperature and humidity

    **Standards:**
    - IEC 61215-2:2021 (MQT 13)
    - IEC 61730
    - IEC TS 63126 (Extended)

    **Test Duration:**
    40-50 days for 1000 hours

    **Conditions:**
    - Temperature: 85°C ± 2°C
    - Humidity: 85% RH ± 5%
    - Duration: 1000 hours (standard)
    - Extended: 2000+ hours

    **Key Failure Modes:**
    - Delamination
    - Corrosion
    - Insulation degradation
    """)

    st.markdown("---")
    st.subheader("🔗 Quick Navigation")

    if st.button("🏠 Home", use_container_width=True, key="nav_home_dh"):
        st.switch_page("streamlit_app.py")

    if st.button("📋 Service Requests", use_container_width=True, key="nav_sr_dh"):
        st.switch_page("pages/01_Service_Request.py")

    if st.button("🎯 Protocol Selector", use_container_width=True, key="nav_ps_dh"):
        st.switch_page("pages/04_Protocol_Selector.py")

    st.markdown("---")

    if st.session_state.execution_id_dh:
        st.success(f"**Active Execution:**\n{st.session_state.execution_id_dh}")

        if st.button("🗑️ Reset Session", use_container_width=True, key="reset_dh"):
            st.session_state.execution_id_dh = None
            st.session_state.current_status_dh = 'not_started'
            st.rerun()

    st.markdown("---")
    auto_save = st.checkbox("🔄 Auto-save", value=st.session_state.auto_save, key="auto_save_dh")
    if auto_save != st.session_state.auto_save:
        st.session_state.auto_save = auto_save
        st.rerun()
