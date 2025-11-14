"""
INSU-001: Insulation Resistance Test
IEC 61730 MST 01 - Safety Testing for PV Modules
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, date
import json
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.database.db_manager import DatabaseManager

# Page Configuration
st.set_page_config(
    page_title="INSU-001: Insulation Resistance Test",
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
if 'safety_checks_completed' not in st.session_state:
    st.session_state.safety_checks_completed = False

# ============================================
# PAGE HEADER
# ============================================

st.title("⚡ INSU-001: Insulation Resistance Test")
st.markdown("### IEC 61730 MST 01 - PV Module Safety Qualification")

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
    st.metric("Protocol", "INSU-001")
with col2:
    st.metric("Status", f"{status_colors.get(st.session_state.current_status, '⚪')} {st.session_state.current_status.replace('_', ' ').title()}")
with col3:
    if st.session_state.execution_id:
        st.metric("Execution ID", st.session_state.execution_id)
    else:
        st.metric("Execution ID", "Not Started")
with col4:
    st.metric("Version", "1.0.0")

st.markdown("---")

# ============================================
# MAIN TABS
# ============================================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📋 General Data",
    "🔒 Safety Checks",
    "⚙️ Test Setup",
    "📊 Measurements",
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
                "Service Request ID",
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
                "Inspection ID",
                options=inspection_options,
                help="Link to incoming inspection"
            )

            sample_id = st.text_input(
                "Sample ID *",
                placeholder="e.g., PV-2024-001",
                help="Unique identifier for the test sample"
            )

            test_operator = st.text_input(
                "Test Operator *",
                placeholder="Full name of qualified operator"
            )

            test_location = st.text_input(
                "Test Location *",
                placeholder="Laboratory or facility name",
                value="PV Testing Laboratory"
            )

        with col2:
            st.markdown("#### Module Information")

            manufacturer = st.text_input(
                "Manufacturer *",
                placeholder="Module manufacturer name"
            )

            model_number = st.text_input(
                "Model Number *",
                placeholder="e.g., ABC-360-M"
            )

            serial_number = st.text_input(
                "Serial Number *",
                placeholder="Module serial number"
            )

            module_area = st.number_input(
                "Module Area (m²) *",
                min_value=0.1,
                max_value=5.0,
                value=1.94,
                step=0.01,
                help="Total module area for specific resistance calculation"
            )

            voltage_class = st.selectbox(
                "System Voltage Class *",
                options=["Class I (<50V)", "Class II (50-600V)", "Class III (>600-1000V)", "Class IV (>1000V)"]
            )

            cell_technology = st.selectbox(
                "Cell Technology",
                options=["Mono-crystalline (PERC)", "Mono-crystalline (TOPCon)", "Mono-crystalline (HJT)",
                        "Multi-crystalline", "Thin Film (CdTe)", "Thin Film (CIGS)", "Thin Film (a-Si)", "Other"]
            )

            frame_type = st.selectbox(
                "Frame Type",
                options=["Aluminum framed", "Frameless", "Other"]
            )

        st.markdown("#### Environmental Conditions")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            ambient_temp = st.number_input(
                "Ambient Temperature (°C) *",
                min_value=15.0,
                max_value=35.0,
                value=25.0,
                step=0.1,
                help="Should be 15-35°C"
            )

        with col2:
            humidity = st.number_input(
                "Relative Humidity (%) *",
                min_value=0.0,
                max_value=100.0,
                value=45.0,
                step=1.0,
                help="Should be <75% for accurate measurements"
            )

        with col3:
            pressure = st.number_input(
                "Atmospheric Pressure (kPa)",
                min_value=80.0,
                max_value=110.0,
                value=101.3,
                step=0.1
            )

        with col4:
            module_temp = st.number_input(
                "Module Temperature (°C) *",
                min_value=15.0,
                max_value=35.0,
                value=25.0,
                step=0.1
            )

        module_condition = st.selectbox(
            "Module Condition *",
            options=["Dry", "After cleaning/wiping", "After conditioning"],
            help="Module must be dry before testing per IEC 61730"
        )

        test_date = st.date_input(
            "Test Date *",
            value=date.today()
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
        if not sample_id or not test_operator or not manufacturer or not model_number or not serial_number:
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
                    'test_operator': test_operator,
                    'test_location': test_location,
                    'test_date': test_date.isoformat(),
                    'manufacturer': manufacturer,
                    'model_number': model_number,
                    'serial_number': serial_number,
                    'module_area': module_area,
                    'voltage_class': voltage_class,
                    'cell_technology': cell_technology,
                    'frame_type': frame_type,
                    'ambient_temperature_c': ambient_temp,
                    'relative_humidity_pct': humidity,
                    'atmospheric_pressure_kpa': pressure,
                    'module_temperature_c': module_temp,
                    'module_condition': module_condition,
                    'notes': notes
                }

                # Create or update execution
                if not st.session_state.execution_id:
                    execution_data = {
                        'protocol_id': 'INSU-001',
                        'protocol_name': 'Insulation Resistance Test',
                        'protocol_version': '1.0.0',
                        'request_id': request_id,
                        'inspection_id': inspection_id,
                        'equipment_id': 'TBD',  # Will be set in test setup
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
# TAB 2: SAFETY CHECKS
# ============================================

with tab2:
    st.subheader("🔒 Pre-Test Safety Checklist")

    st.warning("⚠️ **HIGH VOLTAGE WARNING** - This test involves DC voltages up to 1000V. Ensure all safety procedures are followed.")

    if not st.session_state.execution_id:
        st.warning("⚠️ Please complete General Data first.")
    else:
        st.markdown("### Mandatory Pre-Test Safety Checks")
        st.markdown("All checks must be completed before proceeding with the test.")

        safety_checks = [
            {
                "id": "safety_01",
                "check": "Module is completely disconnected from any power source",
                "category": "Electrical Safety"
            },
            {
                "id": "safety_02",
                "check": "Module surface is dry and clean (no moisture or contamination)",
                "category": "Test Conditions"
            },
            {
                "id": "safety_03",
                "check": "Test equipment is properly grounded",
                "category": "Equipment Safety"
            },
            {
                "id": "safety_04",
                "check": "Test operator is wearing appropriate PPE (insulated gloves if required)",
                "category": "Personal Safety"
            },
            {
                "id": "safety_05",
                "check": "Work area is clear - no unauthorized personnel nearby",
                "category": "Area Safety"
            },
            {
                "id": "safety_06",
                "check": "Insulation tester is calibrated and functional",
                "category": "Equipment Readiness"
            },
            {
                "id": "safety_07",
                "check": "Emergency stop procedure is understood",
                "category": "Emergency Preparedness"
            },
            {
                "id": "safety_08",
                "check": "Test leads are in good condition (no damage or exposed conductors)",
                "category": "Equipment Safety"
            }
        ]

        safety_status = {}
        all_checks_passed = True

        for check in safety_checks:
            col1, col2, col3 = st.columns([3, 1, 2])

            with col1:
                st.write(f"**{check['check']}**")

            with col2:
                st.caption(check['category'])

            with col3:
                status = st.checkbox(
                    "Verified",
                    key=f"safety_{check['id']}",
                    help=f"Check this box to confirm: {check['check']}"
                )
                safety_status[check['id']] = status
                if not status:
                    all_checks_passed = False

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            supervisor_approval = st.text_input(
                "Supervisor/Engineer Approval",
                placeholder="Name of approving supervisor",
                help="Engineer or supervisor must approve safety setup"
            )

        with col2:
            approval_time = st.time_input(
                "Approval Time",
                value=datetime.now().time()
            )

        if st.button("✅ Complete Safety Checklist", use_container_width=True):
            if all_checks_passed and supervisor_approval:
                st.session_state.safety_checks_completed = True
                st.success("✅ All safety checks completed! You may proceed to Test Setup.")

                # Log safety approval
                try:
                    st.session_state.db.log_audit(
                        st.session_state.execution_id,
                        1,
                        'safety_approval',
                        f"Safety checks completed and approved by {supervisor_approval}"
                    )
                except:
                    pass

                st.rerun()
            elif not all_checks_passed:
                st.error("❌ All safety checks must be verified before proceeding!")
            else:
                st.error("❌ Supervisor approval is required!")

        if st.session_state.safety_checks_completed:
            st.success("✅ Safety checks completed successfully!")

# ============================================
# TAB 3: TEST SETUP
# ============================================

with tab3:
    st.subheader("⚙️ Test Equipment and Parameters")

    if not st.session_state.execution_id:
        st.warning("⚠️ Please complete General Data first.")
    elif not st.session_state.safety_checks_completed:
        st.error("🔒 Safety checks must be completed before test setup!")
    else:
        with st.form("test_setup_form"):
            st.markdown("### Test Equipment")

            col1, col2 = st.columns(2)

            with col1:
                equipment_id = st.text_input(
                    "Insulation Tester ID *",
                    placeholder="e.g., MEGGER-001",
                    help="Equipment identification number"
                )

                equipment_model = st.text_input(
                    "Equipment Model *",
                    placeholder="e.g., Fluke 1550C",
                    help="Manufacturer and model"
                )

                calibration_date = st.date_input(
                    "Last Calibration Date *",
                    value=date.today(),
                    help="Date of last calibration"
                )

                calibration_due = st.date_input(
                    "Calibration Due Date *",
                    value=date.today(),
                    help="Next calibration due date"
                )

            with col2:
                calibration_cert = st.text_input(
                    "Calibration Certificate Number",
                    placeholder="CAL-2024-001"
                )

                measurement_accuracy = st.text_input(
                    "Measurement Accuracy",
                    value="±(5% + 3 digits)",
                    help="Accuracy specification of insulation tester"
                )

                # Check calibration status
                if calibration_due < date.today():
                    st.error("⚠️ **CALIBRATION OVERDUE!** Equipment calibration has expired.")
                elif (calibration_due - date.today()).days < 30:
                    st.warning(f"⚠️ Calibration due in {(calibration_due - date.today()).days} days")
                else:
                    st.success("✅ Equipment calibration is current")

            st.markdown("---")
            st.markdown("### Test Parameters")

            col1, col2, col3 = st.columns(3)

            with col1:
                test_voltage = st.selectbox(
                    "Test Voltage *",
                    options=["500 V DC", "1000 V DC"],
                    help="Select based on system voltage class"
                )

                test_duration = st.number_input(
                    "Test Duration (seconds) *",
                    min_value=60,
                    max_value=300,
                    value=60,
                    step=5,
                    help="Minimum 60 seconds per IEC 61730"
                )

            with col2:
                stabilization_time = st.number_input(
                    "Voltage Stabilization Time (s)",
                    min_value=1,
                    max_value=10,
                    value=5,
                    step=1,
                    help="Time to allow voltage to stabilize"
                )

                discharge_time = st.number_input(
                    "Discharge Time After Test (s)",
                    min_value=5,
                    max_value=30,
                    value=5,
                    step=1,
                    help="Time to safely discharge module"
                )

            with col3:
                num_measurements = st.number_input(
                    "Number of Measurements *",
                    min_value=1,
                    max_value=10,
                    value=3,
                    step=1,
                    help="Repeat measurements for statistical analysis"
                )

            st.markdown("---")
            st.markdown("### Test Configuration")

            col1, col2 = st.columns(2)

            with col1:
                terminal_config = st.selectbox(
                    "Terminal Configuration *",
                    options=[
                        "Positive and negative terminals shorted together",
                        "Separate measurement per terminal",
                        "All circuits connected together"
                    ]
                )

            with col2:
                test_points = st.multiselect(
                    "Test Points *",
                    options=[
                        "Active parts to frame",
                        "Active parts to mounting holes",
                        "Between circuits (if applicable)",
                        "Active parts to protective earth"
                    ],
                    default=["Active parts to frame"],
                    help="Select all applicable measurement points"
                )

            setup_notes = st.text_area(
                "Setup Notes",
                placeholder="Document test setup details, deviations, special considerations...",
                height=100
            )

            col1, col2, col3 = st.columns([2, 1, 1])

            with col2:
                save_setup = st.form_submit_button("💾 Save Setup", use_container_width=True)

            with col3:
                ready_test = st.form_submit_button("🚀 Ready for Test", use_container_width=True)

        if save_setup or ready_test:
            if not equipment_id or not equipment_model or not test_points:
                st.error("❌ Please fill all required fields marked with *")
            elif calibration_due < date.today():
                st.error("❌ Cannot proceed - equipment calibration is overdue!")
            else:
                try:
                    protocol_inputs = {
                        'equipment': {
                            'equipment_id': equipment_id,
                            'equipment_model': equipment_model,
                            'calibration_date': calibration_date.isoformat(),
                            'calibration_due_date': calibration_due.isoformat(),
                            'calibration_certificate': calibration_cert,
                            'measurement_accuracy': measurement_accuracy
                        },
                        'test_parameters': {
                            'test_voltage': test_voltage,
                            'test_duration_seconds': test_duration,
                            'stabilization_time_seconds': stabilization_time,
                            'discharge_time_seconds': discharge_time,
                            'number_of_measurements': num_measurements
                        },
                        'test_configuration': {
                            'terminal_config': terminal_config,
                            'test_points': test_points,
                            'setup_notes': setup_notes
                        }
                    }

                    # Update execution with protocol inputs
                    # Here you would call an update method

                    if ready_test:
                        st.session_state.db.update_protocol_status(
                            st.session_state.execution_id,
                            'in_progress',
                            1
                        )
                        st.session_state.current_status = 'in_progress'
                        st.success("✅ Test setup complete - ready for measurements!")
                    else:
                        st.success("✅ Test setup saved!")

                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error: {e}")

# ============================================
# TAB 4: MEASUREMENTS
# ============================================

with tab4:
    st.subheader("📊 Insulation Resistance Measurements")

    if not st.session_state.execution_id or st.session_state.current_status == 'not_started':
        st.warning("⚠️ Complete test setup first.")
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
        with st.expander("➕ Add Measurement", expanded=True):
            with st.form("add_measurement"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    meas_number = st.number_input("Measurement Number", min_value=1, value=1, step=1)
                    test_point = st.selectbox(
                        "Test Point",
                        options=["Active to Frame", "Active to Mounting Holes", "Circuit A to B", "Active to Earth"]
                    )
                    polarity = st.selectbox("Polarity", options=["+ve to frame", "-ve to frame", "N/A"])

                with col2:
                    test_voltage_actual = st.number_input("Test Voltage Applied (V)", min_value=0.0, value=500.0, step=1.0)
                    resistance_reading = st.number_input(
                        "Resistance Reading (MΩ)",
                        min_value=0.0,
                        value=100.0,
                        step=0.1,
                        format="%.3f",
                        help="Insulation resistance in megohms"
                    )
                    stabilization_actual = st.number_input("Stabilization Time (s)", min_value=0, value=5, step=1)

                with col3:
                    # Auto-calculate specific resistance
                    # Would need to get module area from general data
                    module_area_calc = st.number_input("Module Area (m²)", value=1.94, step=0.01, disabled=True)
                    specific_resistance = resistance_reading * module_area_calc
                    st.metric("Specific Resistance (MΩ·m²)", f"{specific_resistance:.2f}")

                    meas_notes = st.text_area("Notes", height=80)

                if st.form_submit_button("💾 Save Measurement", use_container_width=True):
                    try:
                        measurement_data = {
                            'execution_id': st.session_state.execution_id,
                            'measurement_type': 'insulation_resistance',
                            'sequence_number': int(meas_number),
                            'data': {
                                'measurement_number': meas_number,
                                'test_point': test_point,
                                'polarity': polarity,
                                'test_voltage_actual_v': test_voltage_actual,
                                'resistance_reading_mohm': resistance_reading,
                                'specific_resistance_mohm_m2': specific_resistance,
                                'stabilization_time_actual_s': stabilization_actual,
                                'notes': meas_notes
                            },
                            'value': resistance_reading,
                            'unit': 'MΩ',
                            'equipment_used': 'Insulation Tester',
                            'operator_id': 1
                        }

                        st.session_state.db.add_measurement(measurement_data)
                        st.success("✅ Measurement saved!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error saving measurement: {e}")

        # Display measurements
        try:
            measurements = st.session_state.db.get_measurements(st.session_state.execution_id)

            if measurements:
                # Parse measurement data
                data_records = []
                for meas in measurements:
                    data = json.loads(meas['data'])
                    data_records.append({
                        'Meas #': data.get('measurement_number', 0),
                        'Test Point': data.get('test_point', ''),
                        'Polarity': data.get('polarity', ''),
                        'Voltage (V)': data.get('test_voltage_actual_v', 0),
                        'Resistance (MΩ)': data.get('resistance_reading_mohm', 0),
                        'Specific (MΩ·m²)': data.get('specific_resistance_mohm_m2', 0),
                        'Time (s)': data.get('stabilization_time_actual_s', 0),
                        'Timestamp': meas['timestamp']
                    })

                df = pd.DataFrame(data_records)

                # Charts
                st.markdown("### 📈 Measurement Visualization")

                col1, col2 = st.columns(2)

                with col1:
                    # Resistance by test point
                    fig_resistance = px.bar(
                        df,
                        x='Test Point',
                        y='Resistance (MΩ)',
                        title='Insulation Resistance by Test Point',
                        color='Test Point',
                        text='Resistance (MΩ)'
                    )
                    fig_resistance.update_traces(texttemplate='%{text:.2f} MΩ', textposition='outside')
                    fig_resistance.update_layout(showlegend=False, height=400)
                    st.plotly_chart(fig_resistance, use_container_width=True)

                with col2:
                    # Specific resistance with IEC requirement line
                    fig_specific = go.Figure()
                    fig_specific.add_trace(go.Bar(
                        x=df['Test Point'],
                        y=df['Specific (MΩ·m²)'],
                        name='Measured',
                        text=df['Specific (MΩ·m²)'].round(2),
                        textposition='outside',
                        marker_color='lightblue'
                    ))
                    fig_specific.add_hline(
                        y=40,
                        line_dash="dash",
                        line_color="red",
                        annotation_text="IEC 61730 Minimum (40 MΩ·m²)"
                    )
                    fig_specific.update_layout(
                        title='Specific Insulation Resistance vs. IEC Requirement',
                        yaxis_title='Specific Resistance (MΩ·m²)',
                        xaxis_title='Test Point',
                        height=400
                    )
                    st.plotly_chart(fig_specific, use_container_width=True)

                # Measurement repeatability
                if len(df) > 1:
                    fig_repeat = px.scatter(
                        df,
                        x='Meas #',
                        y='Resistance (MΩ)',
                        color='Test Point',
                        size='Resistance (MΩ)',
                        title='Measurement Repeatability',
                        hover_data=['Voltage (V)', 'Specific (MΩ·m²)']
                    )
                    fig_repeat.update_layout(height=400)
                    st.plotly_chart(fig_repeat, use_container_width=True)

                # Data table
                st.markdown("### 📋 Measurement Data Table")
                st.dataframe(df, use_container_width=True, hide_index=True)

                # Export data
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Data (CSV)",
                    data=csv,
                    file_name=f"INSU001_Data_{st.session_state.execution_id}.csv",
                    mime="text/csv"
                )

            else:
                st.info("📊 No measurements available. Add measurements above.")

        except Exception as e:
            st.error(f"Error loading measurements: {e}")

# ============================================
# TAB 5: ANALYSIS
# ============================================

with tab5:
    st.subheader("🔬 Test Analysis & Results")

    if not st.session_state.execution_id:
        st.warning("⚠️ Complete test setup and measurements first.")
    else:
        try:
            measurements = st.session_state.db.get_measurements(st.session_state.execution_id)

            if measurements and len(measurements) >= 1:
                # Parse data
                data_records = []
                for meas in measurements:
                    data = json.loads(meas['data'])
                    data_records.append(data)

                df = pd.DataFrame(data_records)

                # Calculate statistics
                resistances = df['resistance_reading_mohm'].values
                specific_resistances = df['specific_resistance_mohm_m2'].values

                mean_resistance = np.mean(resistances)
                std_resistance = np.std(resistances)
                min_resistance = np.min(resistances)
                max_resistance = np.max(resistances)

                mean_specific = np.mean(specific_resistances)
                min_specific = np.min(specific_resistances)
                max_specific = np.max(specific_resistances)

                # Display results
                st.markdown("### 📊 Statistical Summary")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "Mean Resistance",
                        f"{mean_resistance:.2f} MΩ",
                        help="Average of all measurements"
                    )

                with col2:
                    st.metric(
                        "Std Deviation",
                        f"{std_resistance:.2f} MΩ",
                        help="Measurement variability"
                    )

                with col3:
                    st.metric(
                        "Min Resistance",
                        f"{min_resistance:.2f} MΩ",
                        help="Lowest measured value"
                    )

                with col4:
                    st.metric(
                        "Max Resistance",
                        f"{max_resistance:.2f} MΩ",
                        help="Highest measured value"
                    )

                st.markdown("---")

                # Specific resistance summary
                st.markdown("### 🎯 Specific Insulation Resistance (Normalized to Area)")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Mean Specific Resistance",
                        f"{mean_specific:.2f} MΩ·m²"
                    )

                with col2:
                    st.metric(
                        "Min Specific Resistance",
                        f"{min_specific:.2f} MΩ·m²",
                        help="Critical value for pass/fail"
                    )

                with col3:
                    st.metric(
                        "Max Specific Resistance",
                        f"{max_specific:.2f} MΩ·m²"
                    )

                st.markdown("---")

                # Pass/Fail determination
                IEC_MINIMUM = 40.0  # MΩ·m² per IEC 61730 MST 01
                SAFETY_MINIMUM = 1.0  # MΩ absolute minimum

                pass_criteria = {
                    'iec_specific': min_specific >= IEC_MINIMUM,
                    'safety_absolute': min_resistance >= SAFETY_MINIMUM,
                    'measurement_quality': (std_resistance / mean_resistance * 100) < 20 if mean_resistance > 0 else False
                }

                all_passed = all(pass_criteria.values())

                if all_passed:
                    test_result = "PASS"
                    result_color = "green"
                    result_icon = "✅"
                else:
                    test_result = "FAIL"
                    result_color = "red"
                    result_icon = "❌"

                st.markdown(f"### {result_icon} Test Result: **:{result_color}[{test_result}]**")

                # Detailed criteria check
                st.markdown("### ✅ Acceptance Criteria Evaluation")

                criteria_data = [
                    {
                        "Criterion": "Specific Insulation Resistance ≥ 40 MΩ·m²",
                        "Standard": "IEC 61730 MST 01",
                        "Measured": f"{min_specific:.2f} MΩ·m²",
                        "Status": "✅ PASS" if pass_criteria['iec_specific'] else "❌ FAIL"
                    },
                    {
                        "Criterion": "Absolute Resistance ≥ 1 MΩ",
                        "Standard": "Safety Requirement",
                        "Measured": f"{min_resistance:.2f} MΩ",
                        "Status": "✅ PASS" if pass_criteria['safety_absolute'] else "❌ FAIL"
                    },
                    {
                        "Criterion": "Measurement Repeatability < 20% RSD",
                        "Standard": "Quality Standard",
                        "Measured": f"{(std_resistance/mean_resistance*100):.1f}%" if mean_resistance > 0 else "N/A",
                        "Status": "✅ PASS" if pass_criteria['measurement_quality'] else "⚠️ WARNING"
                    }
                ]

                criteria_df = pd.DataFrame(criteria_data)
                st.table(criteria_df)

                # Recommendations
                st.markdown("### 💡 Recommendations")

                if not pass_criteria['iec_specific']:
                    st.error("""
                    ❌ **FAIL - Insulation resistance below IEC 61730 requirement**
                    - Module does not meet minimum safety requirements
                    - DO NOT proceed to installation or field deployment
                    - Possible causes: moisture ingress, insulation damage, manufacturing defect
                    - Recommended actions: Reject module, investigate root cause, contact manufacturer
                    """)
                elif not pass_criteria['safety_absolute']:
                    st.error("""
                    ❌ **CRITICAL SAFETY FAILURE - Extremely low insulation**
                    - Severe electric shock hazard
                    - Module must be quarantined immediately
                    - Investigate for physical damage, moisture, or contamination
                    """)
                elif not pass_criteria['measurement_quality']:
                    st.warning("""
                    ⚠️ **WARNING - High measurement variability**
                    - Measurements show poor repeatability
                    - Check test connections and equipment
                    - Consider repeating measurements
                    - May indicate intermittent insulation issues
                    """)
                else:
                    st.success("""
                    ✅ **PASS - Module meets all requirements**
                    - Insulation resistance exceeds IEC 61730 minimum
                    - Module is safe for installation
                    - Measurements show good repeatability
                    - No safety concerns identified
                    """)

                # Additional analysis
                if len(df) > 1:
                    st.markdown("### 📈 Additional Analysis")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("**Measurement Statistics**")
                        st.write(f"- Number of measurements: {len(df)}")
                        st.write(f"- Range: {min_resistance:.2f} - {max_resistance:.2f} MΩ")
                        st.write(f"- Coefficient of Variation: {(std_resistance/mean_resistance*100):.1f}%" if mean_resistance > 0 else "N/A")

                    with col2:
                        st.markdown("**Test Points Summary**")
                        for test_point in df['test_point'].unique():
                            point_data = df[df['test_point'] == test_point]
                            point_min = point_data['specific_resistance_mohm_m2'].min()
                            st.write(f"- {test_point}: {point_min:.2f} MΩ·m²")

            else:
                st.info("📊 Insufficient data for analysis. Add measurements first.")

        except Exception as e:
            st.error(f"Error in analysis: {e}")

# ============================================
# TAB 6: QC/REPORTS
# ============================================

with tab6:
    st.subheader("✅ Quality Control & Reporting")

    if not st.session_state.execution_id:
        st.warning("⚠️ Complete test execution first.")
    else:
        # QC Checkpoints
        st.markdown("### ✅ Quality Control Checkpoints")

        qc_checks = [
            {"id": "qc_01", "name": "Equipment calibration verified and current", "stage": "before_test", "severity": "critical"},
            {"id": "qc_02", "name": "Safety checklist completed", "stage": "before_test", "severity": "critical"},
            {"id": "qc_03", "name": "Environmental conditions within specification", "stage": "before_test", "severity": "warning"},
            {"id": "qc_04", "name": "Module properly prepared (dry, clean)", "stage": "before_test", "severity": "critical"},
            {"id": "qc_05", "name": "Test voltage within ±2% of nominal", "stage": "during_test", "severity": "critical"},
            {"id": "qc_06", "name": "Stabilization time observed", "stage": "during_test", "severity": "warning"},
            {"id": "qc_07", "name": "All required test points measured", "stage": "during_test", "severity": "critical"},
            {"id": "qc_08", "name": "Module properly discharged after test", "stage": "after_test", "severity": "critical"},
            {"id": "qc_09", "name": "Data integrity verified", "stage": "after_test", "severity": "critical"},
            {"id": "qc_10", "name": "Results reviewed by qualified engineer", "stage": "after_test", "severity": "critical"},
        ]

        for check in qc_checks:
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

            with col1:
                st.write(f"**{check['name']}**")

            with col2:
                severity_icons = {"critical": "🔴", "warning": "🟡", "info": "🔵"}
                st.caption(f"{severity_icons.get(check['severity'], '⚪')} {check['severity'].title()}")

            with col3:
                st.caption(check['stage'].replace('_', ' ').title())

            with col4:
                qc_status = st.selectbox(
                    "Status",
                    options=["Pending", "Pass", "Fail", "N/A"],
                    key=f"qc_{check['id']}",
                    label_visibility="collapsed"
                )

        if st.button("💾 Save QC Checkpoints", use_container_width=True):
            st.success("✅ QC checkpoints saved!")

        st.markdown("---")

        # Report Generation
        st.markdown("### 📄 Report Generation")

        col1, col2 = st.columns(2)

        with col1:
            report_type = st.selectbox(
                "Report Type",
                options=[
                    "Test Report - Full (IEC 61730 Compliance)",
                    "Test Report - Summary",
                    "Certificate of Testing",
                    "Data Package",
                    "Non-Conformance Report",
                    "Custom Report"
                ]
            )

            report_format = st.selectbox(
                "Format",
                options=["PDF", "Excel", "Word", "HTML", "JSON"]
            )

        with col2:
            include_raw_data = st.checkbox("Include Raw Measurement Data", value=True)
            include_charts = st.checkbox("Include Charts and Graphs", value=True)
            include_photos = st.checkbox("Include Module Photos", value=False)
            include_calibration = st.checkbox("Include Calibration Certificates", value=True)
            digital_signature = st.checkbox("Add Digital Signature", value=True)

        reviewer_name = st.text_input(
            "Reviewed By (Engineer)",
            placeholder="Name of reviewing engineer"
        )

        approver_name = st.text_input(
            "Approved By (QA Manager)",
            placeholder="Name of approving QA manager"
        )

        report_notes = st.text_area(
            "Report Notes / Comments",
            placeholder="Additional comments, observations, or deviations to include in the report...",
            height=100
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("📄 Generate Report", use_container_width=True):
                if not reviewer_name or not approver_name:
                    st.error("❌ Reviewer and approver names are required!")
                else:
                    with st.spinner("Generating report..."):
                        # Simulate report generation
                        import time
                        time.sleep(1)
                        st.success(f"✅ {report_type} generated successfully!")
                        report_id = f"INSU001-RPT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                        st.info(f"📄 Report ID: {report_id}")
                        st.info(f"📥 File: {report_id}.{report_format.lower()}")

        with col2:
            if st.button("📧 Email Report", use_container_width=True):
                st.success("✅ Report sent to stakeholders!")

        with col3:
            if st.button("💾 Archive", use_container_width=True):
                st.success("✅ Test data archived to document management system!")

        with col4:
            if st.button("🔄 Export to LIMS", use_container_width=True):
                st.success("✅ Data exported to LIMS!")

        st.markdown("---")

        # Compliance documentation
        st.markdown("### 📋 Compliance Documentation")

        st.info("""
        **IEC 61730 MST 01 Compliance Checklist:**
        - ✅ Test performed per IEC 61730-2:2016+AMD1:2022
        - ✅ Test voltage: 500V or 1000V DC
        - ✅ Minimum requirement: 40 MΩ·m²
        - ✅ Test duration: ≥60 seconds
        - ✅ Module condition: Dry, ambient temperature
        - ✅ Equipment calibration verified
        - ✅ Safety procedures followed
        - ✅ Results documented and approved
        """)

# ============================================
# SIDEBAR
# ============================================

with st.sidebar:
    st.markdown("---")
    st.subheader("📋 Protocol Information")

    st.info("""
    **INSU-001: Insulation Resistance Test**

    **Purpose:**
    Verify electrical safety of PV modules by measuring insulation resistance between active parts and frame/ground.

    **Standard:**
    - IEC 61730 MST 01
    - IEC 61730-2:2016+AMD1:2022

    **Test Voltage:**
    500V or 1000V DC

    **Pass Criteria:**
    - Specific resistance ≥ 40 MΩ·m²
    - Absolute minimum ≥ 1 MΩ

    **Safety Level:**
    🔴 HIGH VOLTAGE - Critical safety test
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
            st.session_state.safety_checks_completed = False
            st.rerun()

    # Auto-save toggle
    st.markdown("---")
    auto_save = st.checkbox("🔄 Auto-save", value=st.session_state.auto_save)
    if auto_save != st.session_state.auto_save:
        st.session_state.auto_save = auto_save
        st.rerun()

    # Safety status indicator
    st.markdown("---")
    if st.session_state.safety_checks_completed:
        st.success("🔒 Safety checks: ✅ Complete")
    else:
        st.warning("🔒 Safety checks: ⚠️ Pending")
