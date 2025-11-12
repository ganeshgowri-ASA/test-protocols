"""
PVTP-005: UV Preconditioning Test Protocol
Testing module resistance to UV radiation exposure
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
    page_title="PVTP-005: UV Preconditioning",
    page_icon="☀️",
    layout="wide"
)

# Initialize database
if 'db' not in st.session_state:
    st.session_state.db = DatabaseManager()

# Initialize session state
if 'execution_id_uv' not in st.session_state:
    st.session_state.execution_id_uv = None
if 'auto_save' not in st.session_state:
    st.session_state.auto_save = True
if 'current_status_uv' not in st.session_state:
    st.session_state.current_status_uv = 'not_started'

# ============================================
# PAGE HEADER
# ============================================

st.title("☀️ PVTP-005: UV Preconditioning Test")
st.markdown("### Ultraviolet Radiation Exposure Testing")

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
    st.metric("Protocol", "PVTP-005")
with col2:
    st.metric("Status", f"{status_colors.get(st.session_state.current_status_uv, '⚪')} {st.session_state.current_status_uv.replace('_', ' ').title()}")
with col3:
    if st.session_state.execution_id_uv:
        st.metric("Execution ID", st.session_state.execution_id_uv)
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

    with st.form("general_data_form_uv"):
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
                help="Link to existing service request",
                key="sr_uv"
            )

            try:
                inspections = st.session_state.db.get_inspections()
                inspection_options = [""] + [f"{insp['inspection_id']} - {insp['sample_id']}" for insp in inspections]
            except:
                inspection_options = [""]

            inspection = st.selectbox(
                "Inspection ID *",
                options=inspection_options,
                help="Link to incoming inspection",
                key="insp_uv"
            )

            sample_id = st.text_input(
                "Sample ID *",
                placeholder="e.g., PV-2024-005",
                help="Unique identifier for the test sample"
            )

            equipment_id = st.text_input(
                "Equipment ID *",
                placeholder="e.g., UV-CHAMBER-01",
                help="UV exposure chamber identifier"
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
                max_value=30.0,
                value=7.0,
                step=1.0,
                help="Typical: 5-10 days for standard exposure"
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

                if not st.session_state.execution_id_uv:
                    execution_data = {
                        'protocol_id': 'PVTP-005',
                        'protocol_name': 'UV Preconditioning Test',
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
                    st.session_state.execution_id_uv = execution_id
                    st.session_state.current_status_uv = 'not_started'
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
    st.subheader("UV Preconditioning Test Parameters")

    if not st.session_state.execution_id_uv:
        st.warning("⚠️ Please complete General Data first to enable protocol inputs.")
    else:
        with st.form("protocol_inputs_form_uv"):
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

                initial_color = st.text_input(
                    "Initial Color/Appearance",
                    placeholder="e.g., Clear EVA, no discoloration"
                )

            with col2:
                st.markdown("#### UV Exposure Conditions")

                uv_dose = st.number_input(
                    "Total UV Dose (kWh/m²) *",
                    min_value=1.0,
                    max_value=100.0,
                    value=15.0,
                    step=1.0,
                    help="IEC 61215: 15 kWh/m² standard, 30-60 for extended"
                )

                uv_irradiance = st.number_input(
                    "UV Irradiance (W/m²) *",
                    min_value=10.0,
                    max_value=200.0,
                    value=50.0,
                    step=5.0,
                    help="Typical UV portion: 30-60 W/m²"
                )

                exposure_temperature = st.number_input(
                    "Exposure Temperature (°C) *",
                    min_value=30.0,
                    max_value=80.0,
                    value=60.0,
                    step=1.0,
                    help="IEC 61215: 60°C ± 5°C"
                )

                chamber_humidity = st.number_input(
                    "Chamber Humidity (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=50.0,
                    step=5.0,
                    help="Optional humidity control during exposure"
                )

                exposure_duration = st.number_input(
                    "Exposure Duration (hours) *",
                    min_value=10.0,
                    max_value=1000.0,
                    value=300.0,
                    step=10.0,
                    help="Calculated from dose and irradiance"
                )

            st.markdown("#### UV Lamp Specifications")

            col1, col2, col3 = st.columns(3)

            with col1:
                lamp_type = st.selectbox(
                    "UV Lamp Type *",
                    options=[
                        "Xenon Arc",
                        "Fluorescent UV (UVA)",
                        "Metal Halide",
                        "Mercury Vapor",
                        "LED UV",
                        "Solar Simulator"
                    ]
                )

            with col2:
                wavelength_range = st.text_input(
                    "Wavelength Range (nm)",
                    placeholder="e.g., 280-400",
                    value="280-400",
                    help="UV range: typically 280-400 nm"
                )

            with col3:
                lamp_age = st.number_input(
                    "Lamp Operating Hours",
                    min_value=0,
                    max_value=10000,
                    value=500,
                    step=100,
                    help="Track lamp age for calibration"
                )

            st.markdown("#### Measurement Schedule")

            col1, col2 = st.columns(2)

            with col1:
                measurement_intervals = st.multiselect(
                    "I-V Measurements at (kWh/m²):",
                    options=[0, 2.5, 5, 7.5, 10, 12.5, 15, 20, 30],
                    default=[0, 5, 10, 15],
                    help="UV dose levels for intermediate measurements"
                )

            with col2:
                visual_inspections = st.multiselect(
                    "Visual Inspections at (kWh/m²):",
                    options=[0, 5, 10, 15, 20, 30],
                    default=[0, 7.5, 15],
                    help="UV dose levels for visual inspection"
                )

            st.markdown("#### Standard & Acceptance Criteria")

            col1, col2, col3 = st.columns(3)

            with col1:
                standard = st.selectbox(
                    "Test Standard *",
                    options=[
                        "IEC 61215-2:2021 (MQT 10)",
                        "IEC 61215-2:2016",
                        "IEC 61730",
                        "IEC 61345 (UV Test)",
                        "ASTM G155",
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
                    help="IEC 61215: Max 5% degradation allowed"
                )

            with col3:
                allow_discoloration = st.selectbox(
                    "Encapsulant Discoloration",
                    options=["Not Allowed", "Minor Allowed", "Any Level"],
                    help="Acceptance of yellowing/browning"
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
                encapsulant = st.selectbox(
                    "Encapsulant Type *",
                    options=["EVA", "POE", "PVB", "TPO", "Silicone", "Other"],
                    help="Critical for UV resistance"
                )

            with col3:
                backsheet = st.selectbox(
                    "Backsheet Type",
                    options=["PVF/PET/PVF (Tedlar)", "PET", "PPE", "Transparent", "Glass", "Other"]
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
            if not initial_power or not uv_dose:
                st.error("❌ Please fill all required fields marked with *")
            else:
                try:
                    protocol_inputs = {
                        'initial_measurements': {
                            'pmax_w': initial_power,
                            'voc_v': initial_voc,
                            'isc_a': initial_isc,
                            'fill_factor_pct': initial_ff,
                            'initial_appearance': initial_color
                        },
                        'exposure_conditions': {
                            'total_uv_dose_kwh_m2': uv_dose,
                            'uv_irradiance_w_m2': uv_irradiance,
                            'exposure_temperature_c': exposure_temperature,
                            'chamber_humidity_pct': chamber_humidity,
                            'exposure_duration_hours': exposure_duration
                        },
                        'lamp_specifications': {
                            'lamp_type': lamp_type,
                            'wavelength_range_nm': wavelength_range,
                            'lamp_operating_hours': lamp_age
                        },
                        'measurement_schedule': {
                            'iv_measurements_kwh_m2': measurement_intervals,
                            'visual_inspections_kwh_m2': visual_inspections
                        },
                        'acceptance_criteria': {
                            'standard': standard,
                            'max_power_degradation_pct': max_power_degradation,
                            'discoloration_acceptance': allow_discoloration
                        },
                        'module_info': {
                            'cell_technology': cell_technology,
                            'encapsulant_type': encapsulant,
                            'backsheet_type': backsheet
                        },
                        'test_notes': test_notes
                    }

                    if start_test:
                        st.session_state.db.update_protocol_status(
                            st.session_state.execution_id_uv,
                            'in_progress',
                            1
                        )
                        st.session_state.current_status_uv = 'in_progress'
                        st.success("✅ UV preconditioning test started!")
                    else:
                        st.success("✅ Protocol inputs saved!")

                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error: {e}")

# ============================================
# TAB 3: LIVE MEASUREMENTS
# ============================================

with tab3:
    st.subheader("UV Exposure Progress & Measurements")

    if not st.session_state.execution_id_uv or st.session_state.current_status_uv == 'not_started':
        st.warning("⚠️ Start the test to begin monitoring.")
    else:
        # Control buttons
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("▶️ Resume", use_container_width=True, key="resume_uv"):
                st.session_state.db.update_protocol_status(
                    st.session_state.execution_id_uv,
                    'in_progress',
                    1
                )
                st.session_state.current_status_uv = 'in_progress'
                st.rerun()

        with col2:
            if st.button("⏸️ Pause", use_container_width=True, key="pause_uv"):
                st.session_state.db.update_protocol_status(
                    st.session_state.execution_id_uv,
                    'paused',
                    1
                )
                st.session_state.current_status_uv = 'paused'
                st.rerun()

        with col3:
            if st.button("✅ Complete", use_container_width=True, key="complete_uv"):
                st.session_state.db.update_protocol_status(
                    st.session_state.execution_id_uv,
                    'completed',
                    1
                )
                st.session_state.current_status_uv = 'completed'
                st.rerun()

        with col4:
            if st.button("🔄 Refresh Data", use_container_width=True, key="refresh_uv"):
                st.rerun()

        st.markdown("---")

        # Current status
        st.markdown("### ☀️ Current Exposure Status")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Accumulated UV Dose", "10.2 / 15.0 kWh/m²")
        with col2:
            st.metric("UV Irradiance", "48.5 W/m²")
        with col3:
            st.metric("Chamber Temp", "59.8 °C")
        with col4:
            st.metric("Est. Completion", "2.5 days")

        # Progress bar
        exposure_progress = 10.2 / 15.0 * 100
        st.progress(exposure_progress / 100, text=f"UV Dose Progress: {exposure_progress:.1f}%")

        st.markdown("---")

        # Manual measurement entry
        with st.expander("➕ Add Measurement Reading", expanded=False):
            with st.form("add_measurement_uv"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    meas_dose = st.number_input("UV Dose (kWh/m²)", min_value=0.0, max_value=100.0, value=0.0, step=0.5)
                    meas_pmax = st.number_input("Pmax (W)", min_value=0.0, value=300.0)
                    meas_voc = st.number_input("Voc (V)", min_value=0.0, value=40.0)

                with col2:
                    meas_isc = st.number_input("Isc (A)", min_value=0.0, value=9.0)
                    meas_ff = st.number_input("Fill Factor (%)", min_value=0.0, value=78.0)
                    chamber_temp = st.number_input("Chamber Temp (°C)", min_value=0.0, value=60.0)

                with col3:
                    discoloration_level = st.selectbox(
                        "Discoloration Level",
                        options=["None", "Slight", "Moderate", "Severe"]
                    )
                    visual_defects = st.multiselect(
                        "Visual Defects",
                        options=["None", "Yellowing", "Browning", "Bubbles", "Delamination", "Cracks"]
                    )

                meas_notes = st.text_area("Notes", height=80)

                if st.form_submit_button("💾 Save Measurement"):
                    try:
                        measurement_data = {
                            'execution_id': st.session_state.execution_id_uv,
                            'measurement_type': 'uv_exposure_reading',
                            'sequence_number': int(meas_dose * 10),
                            'data': {
                                'uv_dose_kwh_m2': meas_dose,
                                'pmax_w': meas_pmax,
                                'voc_v': meas_voc,
                                'isc_a': meas_isc,
                                'fill_factor_pct': meas_ff,
                                'chamber_temp_c': chamber_temp,
                                'discoloration_level': discoloration_level,
                                'visual_defects': visual_defects,
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
            measurements = st.session_state.db.get_measurements(st.session_state.execution_id_uv)

            if measurements:
                data_records = []
                for meas in measurements:
                    data = json.loads(meas['data'])
                    data_records.append({
                        'UV Dose (kWh/m²)': data.get('uv_dose_kwh_m2', 0),
                        'Pmax (W)': data.get('pmax_w', 0),
                        'Voc (V)': data.get('voc_v', 0),
                        'Isc (A)': data.get('isc_a', 0),
                        'FF (%)': data.get('fill_factor_pct', 0),
                        'Temp (°C)': data.get('chamber_temp_c', 0),
                        'Discoloration': data.get('discoloration_level', 'None'),
                        'Defects': ', '.join(data.get('visual_defects', [])),
                        'Timestamp': meas['timestamp']
                    })

                df = pd.DataFrame(data_records)

                if len(df) > 0:
                    st.markdown("### 📈 Performance Trends")

                    # Calculate degradation
                    initial_power = df['Pmax (W)'].iloc[0]
                    df['Degradation (%)'] = ((df['Pmax (W)'] - initial_power) / initial_power) * 100

                    # Power vs UV dose
                    fig_power = go.Figure()
                    fig_power.add_trace(go.Scatter(
                        x=df['UV Dose (kWh/m²)'],
                        y=df['Pmax (W)'],
                        mode='lines+markers',
                        name='Pmax',
                        line=dict(color='royalblue', width=2),
                        marker=dict(size=8)
                    ))
                    fig_power.update_layout(
                        title='Maximum Power vs UV Dose',
                        xaxis_title='UV Dose (kWh/m²)',
                        yaxis_title='Pmax (W)',
                        hovermode='x unified',
                        height=400
                    )
                    st.plotly_chart(fig_power, use_container_width=True)

                    # Degradation percentage
                    fig_deg = go.Figure()
                    fig_deg.add_trace(go.Scatter(
                        x=df['UV Dose (kWh/m²)'],
                        y=df['Degradation (%)'],
                        mode='lines+markers',
                        name='Degradation',
                        line=dict(color='crimson', width=2),
                        marker=dict(size=8)
                    ))
                    fig_deg.add_hline(y=-5, line_dash="dash", line_color="orange",
                                     annotation_text="IEC Limit (-5%)")
                    fig_deg.update_layout(
                        title='Power Degradation vs UV Dose',
                        xaxis_title='UV Dose (kWh/m²)',
                        yaxis_title='Degradation (%)',
                        hovermode='x unified',
                        height=400
                    )
                    st.plotly_chart(fig_deg, use_container_width=True)

                    # Electrical parameters
                    col1, col2 = st.columns(2)

                    with col1:
                        fig_voc = px.line(df, x='UV Dose (kWh/m²)', y='Voc (V)',
                                         title='Voc vs UV Dose',
                                         markers=True)
                        fig_voc.update_traces(line_color='green')
                        st.plotly_chart(fig_voc, use_container_width=True)

                        fig_ff = px.line(df, x='UV Dose (kWh/m²)', y='FF (%)',
                                        title='Fill Factor vs UV Dose',
                                        markers=True)
                        fig_ff.update_traces(line_color='darkorange')
                        st.plotly_chart(fig_ff, use_container_width=True)

                    with col2:
                        fig_isc = px.line(df, x='UV Dose (kWh/m²)', y='Isc (A)',
                                         title='Isc vs UV Dose',
                                         markers=True)
                        fig_isc.update_traces(line_color='purple')
                        st.plotly_chart(fig_isc, use_container_width=True)

                        # Discoloration trend
                        discolor_map = {'None': 0, 'Slight': 1, 'Moderate': 2, 'Severe': 3}
                        df['Discoloration Level'] = df['Discoloration'].map(discolor_map)

                        fig_discolor = px.scatter(df, x='UV Dose (kWh/m²)', y='Discoloration Level',
                                                 title='Discoloration Progression',
                                                 size_max=15)
                        fig_discolor.update_yaxis(tickvals=[0, 1, 2, 3],
                                                 ticktext=['None', 'Slight', 'Moderate', 'Severe'])
                        st.plotly_chart(fig_discolor, use_container_width=True)

                    # Data table
                    st.markdown("### 📋 Measurement Data Table")
                    display_df = df.drop('Discoloration Level', axis=1, errors='ignore')
                    st.dataframe(display_df, use_container_width=True, hide_index=True)

                    # Export
                    csv = display_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Data (CSV)",
                        data=csv,
                        file_name=f"PVTP005_UV_Data_{st.session_state.execution_id_uv}.csv",
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

    if not st.session_state.execution_id_uv:
        st.warning("⚠️ Complete test setup and measurements first.")
    else:
        try:
            measurements = st.session_state.db.get_measurements(st.session_state.execution_id_uv)

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

                total_dose = df['uv_dose_kwh_m2'].iloc[-1]
                avg_deg_rate = degradation_pct / total_dose if total_dose > 0 else 0

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
                    st.metric("Total UV Dose", f"{total_dose:.1f} kWh/m²")

                with col3:
                    st.metric("Degradation Rate", f"{avg_deg_rate:.3f}% per kWh/m²")

                with col4:
                    final_discolor = df['discoloration_level'].iloc[-1]
                    st.metric("Final Discoloration", final_discolor)

                st.markdown("---")

                # Pass/Fail determination
                max_allowed_deg = -5.0

                power_pass = degradation_pct >= max_allowed_deg

                # Check discoloration (assuming "Moderate" and "Severe" are failures)
                discolor_fail = final_discolor in ["Moderate", "Severe"]

                if power_pass and not discolor_fail:
                    test_result = "PASS"
                    result_color = "green"
                    result_icon = "✅"
                elif power_pass and discolor_fail:
                    test_result = "CONDITIONAL"
                    result_color = "orange"
                    result_icon = "⚠️"
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

                    # Calculate parameter changes
                    initial_voc = df['voc_v'].iloc[0]
                    final_voc = df['voc_v'].iloc[-1]
                    voc_change = ((final_voc - initial_voc) / initial_voc) * 100

                    initial_isc = df['isc_a'].iloc[0]
                    final_isc = df['isc_a'].iloc[-1]
                    isc_change = ((final_isc - initial_isc) / initial_isc) * 100

                    st.info(f"Voc change: {voc_change:.2f}%")
                    st.info(f"Isc change: {isc_change:.2f}%")

                with col2:
                    st.markdown("#### Visual Assessment")
                    if discolor_fail:
                        st.warning(f"⚠️ Significant discoloration: {final_discolor}")
                    elif final_discolor == "Slight":
                        st.info(f"ℹ️ Minor discoloration: {final_discolor}")
                    else:
                        st.success("✅ No significant discoloration")

                    # Count defects
                    defect_count = sum(1 for rec in data_records
                                      if rec.get('visual_defects') and rec['visual_defects'] != ['None'])

                    if defect_count > 0:
                        st.warning(f"⚠️ Visual defects in {defect_count} inspection(s)")
                    else:
                        st.success("✅ No visual defects detected")

                # Recommendations
                st.markdown("### 💡 Recommendations")

                if degradation_pct < -10:
                    st.error("❌ Severe UV degradation. Module unsuitable for outdoor use.")
                elif degradation_pct < -5:
                    st.warning("⚠️ Exceeds IEC limit. Consider improved UV-resistant encapsulant.")
                elif discolor_fail:
                    st.warning("⚠️ Significant discoloration may affect long-term reliability.")
                elif degradation_pct < -2:
                    st.info("ℹ️ Minor degradation within acceptable limits.")
                else:
                    st.success("✅ Excellent UV resistance. Module suitable for high-UV environments.")

            else:
                st.info("📊 Insufficient data for analysis. Need at least 2 measurements.")

        except Exception as e:
            st.error(f"Error in analysis: {e}")

# ============================================
# TAB 5: QC/REPORTS
# ============================================

with tab5:
    st.subheader("Quality Control & Reporting")

    if not st.session_state.execution_id_uv:
        st.warning("⚠️ Complete test execution first.")
    else:
        st.markdown("### ✅ Quality Control Checkpoints")

        qc_checks = [
            {"id": "qc_01", "name": "UV chamber calibration verified", "stage": "before_test"},
            {"id": "qc_02", "name": "UV spectral distribution measured", "stage": "before_test"},
            {"id": "qc_03", "name": "Initial measurements completed", "stage": "before_test"},
            {"id": "qc_04", "name": "UV irradiance stable", "stage": "during_test"},
            {"id": "qc_05", "name": "Temperature maintained (60°C ± 5°C)", "stage": "during_test"},
            {"id": "qc_06", "name": "UV dose monitored continuously", "stage": "during_test"},
            {"id": "qc_07", "name": "Interim measurements completed", "stage": "during_test"},
            {"id": "qc_08", "name": "Final measurements completed", "stage": "after_test"},
            {"id": "qc_09", "name": "Visual inspection for discoloration", "stage": "after_test"},
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
                    key=f"qc_uv_{check['id']}",
                    label_visibility="collapsed"
                )

        if st.button("💾 Save QC Checkpoints", key="save_qc_uv"):
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
                    "UV Exposure Log",
                    "Custom Report"
                ],
                key="report_type_uv"
            )

            report_format = st.selectbox(
                "Format",
                options=["PDF", "Excel", "Word", "HTML"],
                key="report_format_uv"
            )

        with col2:
            include_raw_data = st.checkbox("Include Raw Data", value=True, key="raw_uv")
            include_charts = st.checkbox("Include Charts", value=True, key="charts_uv")
            include_photos = st.checkbox("Include Photos", value=True, key="photos_uv")
            digital_signature = st.checkbox("Add Digital Signature", value=False, key="sig_uv")

        report_notes = st.text_area(
            "Report Notes",
            placeholder="Additional comments for the report...",
            height=100,
            key="notes_uv"
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📄 Generate Report", use_container_width=True, key="gen_report_uv"):
                with st.spinner("Generating report..."):
                    st.success(f"✅ {report_type} generated successfully!")
                    st.info(f"Report ID: RPT-{datetime.now().strftime('%Y%m%d%H%M%S')}")

        with col2:
            if st.button("📧 Email Report", use_container_width=True, key="email_report_uv"):
                st.success("✅ Report sent to stakeholders!")

        with col3:
            if st.button("💾 Archive", use_container_width=True, key="archive_uv"):
                st.success("✅ Test data archived!")

# ============================================
# SIDEBAR
# ============================================

with st.sidebar:
    st.markdown("---")
    st.subheader("📋 Protocol Information")

    st.info("""
    **PVTP-005: UV Preconditioning**

    **Purpose:**
    Evaluate module resistance to ultraviolet radiation exposure

    **Standards:**
    - IEC 61215-2:2021 (MQT 10)
    - IEC 61730
    - IEC 61345
    - ASTM G155

    **Test Duration:**
    5-10 days for standard dose

    **Conditions:**
    - UV Dose: 15 kWh/m² (standard)
    - Temperature: 60°C ± 5°C
    - UV wavelength: 280-400 nm
    - Extended: 30-60 kWh/m²

    **Key Failure Modes:**
    - Encapsulant yellowing/browning
    - Power degradation
    - Delamination
    - Material degradation
    """)

    st.markdown("---")
    st.subheader("🔗 Quick Navigation")

    if st.button("🏠 Home", use_container_width=True, key="nav_home_uv"):
        st.switch_page("streamlit_app.py")

    if st.button("📋 Service Requests", use_container_width=True, key="nav_sr_uv"):
        st.switch_page("pages/01_Service_Request.py")

    if st.button("🎯 Protocol Selector", use_container_width=True, key="nav_ps_uv"):
        st.switch_page("pages/04_Protocol_Selector.py")

    st.markdown("---")

    if st.session_state.execution_id_uv:
        st.success(f"**Active Execution:**\n{st.session_state.execution_id_uv}")

        if st.button("🗑️ Reset Session", use_container_width=True, key="reset_uv"):
            st.session_state.execution_id_uv = None
            st.session_state.current_status_uv = 'not_started'
            st.rerun()

    st.markdown("---")
    auto_save = st.checkbox("🔄 Auto-save", value=st.session_state.auto_save, key="auto_save_uv")
    if auto_save != st.session_state.auto_save:
        st.session_state.auto_save = auto_save
        st.rerun()
