"""
LID/LIS Stabilization Protocol - Streamlit Interface
Light Induced Degradation and Light & Elevated Temperature Induced Stabilization Testing
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from protocols.lid_lis_handler import LIDLISProtocolHandler


# Page configuration
st.set_page_config(
    page_title="LID/LIS Stabilization Protocol",
    page_icon="☀️",
    layout="wide"
)

# Initialize session state
if 'protocol_data' not in st.session_state:
    st.session_state.protocol_data = {}

if 'live_readings' not in st.session_state:
    st.session_state.live_readings = []

if 'handler' not in st.session_state:
    st.session_state.handler = LIDLISProtocolHandler()


def main():
    """Main application function"""
    st.title("☀️ LID/LIS Stabilization Protocol")
    st.markdown("**PVTP-001-LID-LIS**: Light Induced Degradation & Stabilization Testing")
    st.markdown("*Standards: IEC 61215, IEC 61730*")

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Section",
        [
            "Protocol Setup",
            "Pre-Test Inspection",
            "Live Data Entry",
            "Analysis & Results",
            "Charts & Visualization",
            "Quality Control",
            "Export & Reports"
        ]
    )

    # Route to appropriate page
    if page == "Protocol Setup":
        protocol_setup_page()
    elif page == "Pre-Test Inspection":
        pre_test_inspection_page()
    elif page == "Live Data Entry":
        live_data_entry_page()
    elif page == "Analysis & Results":
        analysis_results_page()
    elif page == "Charts & Visualization":
        charts_visualization_page()
    elif page == "Quality Control":
        quality_control_page()
    elif page == "Export & Reports":
        export_reports_page()


def protocol_setup_page():
    """Protocol setup and configuration page"""
    st.header("📋 Protocol Setup")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("General Information")

        test_lab = st.text_input("Test Laboratory *", key="test_lab")
        project_name = st.text_input("Project Name *", key="project_name")
        client = st.text_input("Client/Customer *", key="client")
        test_date = st.date_input("Test Start Date *", datetime.now(), key="test_date")
        operator = st.text_input("Test Operator *", key="operator")

        st.subheader("Sample Information")

        module_type = st.selectbox(
            "Module Type *",
            ["mono-Si", "poly-Si", "PERC", "HJT", "TOPCon", "CdTe", "CIGS", "Other"],
            key="module_type"
        )
        manufacturer = st.text_input("Manufacturer *", key="manufacturer")
        model = st.text_input("Model Number *", key="model")
        nameplate_power = st.number_input(
            "Nameplate Power (W) *",
            min_value=0.0,
            value=400.0,
            step=10.0,
            key="nameplate_power"
        )

        # Module serial numbers
        st.markdown("**Module Serial Numbers**")
        num_modules = st.number_input("Number of Modules", min_value=1, max_value=20, value=2, key="num_modules")

        serial_numbers = []
        for i in range(num_modules):
            sn = st.text_input(f"Module {i+1} Serial Number", key=f"serial_{i}")
            if sn:
                serial_numbers.append(sn)

    with col2:
        st.subheader("Protocol Inputs")

        irradiance = st.number_input(
            "Irradiance Level (W/m²) *",
            min_value=800.0,
            max_value=1200.0,
            value=1000.0,
            step=10.0,
            key="irradiance",
            help="Target irradiance level during test"
        )

        temperature = st.number_input(
            "Module Temperature (°C) *",
            min_value=50.0,
            max_value=75.0,
            value=60.0,
            step=1.0,
            key="temperature",
            help="Target module temperature during test"
        )

        duration = st.number_input(
            "Test Duration (hours) *",
            min_value=100.0,
            max_value=500.0,
            value=200.0,
            step=10.0,
            key="duration",
            help="Total test duration in hours"
        )

        st.markdown("**Measurement Intervals (hours)**")
        intervals_text = st.text_input(
            "Enter intervals separated by commas",
            value="0, 24, 48, 96, 144, 200",
            key="intervals"
        )

        try:
            measurement_intervals = [float(x.strip()) for x in intervals_text.split(',')]
        except:
            measurement_intervals = [0, 24, 48, 96, 144, 200]
            st.warning("Invalid interval format. Using default values.")

        st.subheader("Pass/Fail Criteria")

        degradation_limit = st.number_input(
            "Maximum Degradation Limit (%)",
            min_value=0.0,
            max_value=10.0,
            value=2.0,
            step=0.1,
            key="degradation_limit"
        )

        stabilization_required = st.checkbox(
            "Stabilization Required",
            value=True,
            key="stabilization_required"
        )

        min_stabilization_power = st.number_input(
            "Minimum Stabilized Power (% of initial)",
            min_value=90.0,
            max_value=100.0,
            value=98.0,
            step=0.5,
            key="min_stabilization_power"
        )

    # Save button
    if st.button("💾 Save Protocol Setup", type="primary"):
        # Compile protocol data
        protocol_data = {
            'protocol_metadata': {
                'id': 'PVTP-001-LID-LIS',
                'name': 'LID/LIS Stabilization Protocol',
                'version': '1.0',
                'category': 'Performance & Reliability Testing',
                'standards': ['IEC 61215', 'IEC 61730']
            },
            'general_data': {
                'test_lab': test_lab,
                'project_name': project_name,
                'client': client,
                'test_date': str(test_date),
                'operator': operator
            },
            'sample_information': {
                'module_type': module_type,
                'manufacturer': manufacturer,
                'model': model,
                'serial_numbers': serial_numbers,
                'quantity': len(serial_numbers),
                'nameplate_power': nameplate_power
            },
            'protocol_inputs': {
                'irradiance_level': irradiance,
                'temperature': temperature,
                'duration_hours': duration,
                'measurement_intervals': measurement_intervals
            },
            'analysis': {
                'pass_fail_criteria': {
                    'degradation_limit': degradation_limit,
                    'stabilization_required': stabilization_required,
                    'min_stabilization_power': min_stabilization_power
                }
            }
        }

        # Validate
        is_valid, errors = st.session_state.handler.validate_protocol_data(protocol_data)

        if is_valid:
            st.session_state.protocol_data = protocol_data
            st.success("✅ Protocol setup saved successfully!")
        else:
            st.error("❌ Validation failed:")
            for error in errors:
                st.error(f"  • {error}")


def pre_test_inspection_page():
    """Pre-test inspection data entry"""
    st.header("🔍 Pre-Test Inspection")

    if not st.session_state.protocol_data.get('sample_information', {}).get('serial_numbers'):
        st.warning("⚠️ Please complete Protocol Setup first to define modules.")
        return

    serial_numbers = st.session_state.protocol_data['sample_information']['serial_numbers']

    st.subheader("Initial Flash Test Measurements")

    # Create dataframe for flash test data
    if 'flash_test_data' not in st.session_state:
        st.session_state.flash_test_data = pd.DataFrame({
            'Module ID': serial_numbers,
            'Pmax (W)': [0.0] * len(serial_numbers),
            'Voc (V)': [0.0] * len(serial_numbers),
            'Isc (A)': [0.0] * len(serial_numbers),
            'Vmp (V)': [0.0] * len(serial_numbers),
            'Imp (A)': [0.0] * len(serial_numbers),
            'FF (%)': [0.0] * len(serial_numbers)
        })

    # Editable dataframe
    edited_flash_data = st.data_editor(
        st.session_state.flash_test_data,
        use_container_width=True,
        num_rows="fixed"
    )

    st.session_state.flash_test_data = edited_flash_data

    st.subheader("Visual Inspection")

    for module_id in serial_numbers:
        with st.expander(f"Module {module_id}"):
            col1, col2 = st.columns(2)

            with col1:
                defects = st.text_area(
                    "Visual Defects",
                    key=f"defects_{module_id}",
                    help="List any visible defects"
                )

            with col2:
                severity = st.selectbox(
                    "Severity",
                    ["None", "Minor", "Moderate", "Major"],
                    key=f"severity_{module_id}"
                )

    if st.button("💾 Save Pre-Test Data", type="primary"):
        # Convert flash test data to protocol format
        flash_test_records = []
        for _, row in edited_flash_data.iterrows():
            flash_test_records.append({
                'module_id': row['Module ID'],
                'pmax': float(row['Pmax (W)']),
                'voc': float(row['Voc (V)']),
                'isc': float(row['Isc (A)']),
                'vmp': float(row['Vmp (V)']),
                'imp': float(row['Imp (A)']),
                'ff': float(row['FF (%)'])
            })

        if 'pre_test_inspection' not in st.session_state.protocol_data:
            st.session_state.protocol_data['pre_test_inspection'] = {}

        st.session_state.protocol_data['pre_test_inspection']['flash_test_power'] = flash_test_records

        st.success("✅ Pre-test data saved successfully!")


def live_data_entry_page():
    """Live data entry during test"""
    st.header("📊 Live Data Entry")

    if not st.session_state.protocol_data.get('sample_information', {}).get('serial_numbers'):
        st.warning("⚠️ Please complete Protocol Setup first.")
        return

    serial_numbers = st.session_state.protocol_data['sample_information']['serial_numbers']

    st.subheader("Add New Reading")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        reading_timestamp = st.datetime_input(
            "Timestamp",
            datetime.now(),
            key="reading_timestamp"
        )

        elapsed_hours = st.number_input(
            "Elapsed Time (hours)",
            min_value=0.0,
            value=0.0,
            step=0.1,
            key="elapsed_hours"
        )

    with col2:
        irradiance = st.number_input(
            "Irradiance (W/m²)",
            min_value=0.0,
            value=1000.0,
            step=10.0,
            key="reading_irradiance"
        )

        module_temp = st.number_input(
            "Module Temp (°C)",
            min_value=0.0,
            value=60.0,
            step=0.5,
            key="reading_temp"
        )

    with col3:
        module_id = st.selectbox(
            "Module ID",
            serial_numbers,
            key="reading_module_id"
        )

        pmax = st.number_input(
            "Pmax (W)",
            min_value=0.0,
            value=0.0,
            step=0.1,
            key="reading_pmax"
        )

    with col4:
        voc = st.number_input(
            "Voc (V)",
            min_value=0.0,
            value=0.0,
            step=0.1,
            key="reading_voc"
        )

        isc = st.number_input(
            "Isc (A)",
            min_value=0.0,
            value=0.0,
            step=0.1,
            key="reading_isc"
        )

    ff = st.number_input(
        "Fill Factor (%)",
        min_value=0.0,
        max_value=100.0,
        value=0.0,
        step=0.1,
        key="reading_ff"
    )

    notes = st.text_input("Notes", key="reading_notes")

    if st.button("➕ Add Reading", type="primary"):
        reading = {
            'timestamp': str(reading_timestamp),
            'elapsed_hours': elapsed_hours,
            'irradiance': irradiance,
            'module_temp': module_temp,
            'module_id': module_id,
            'pmax': pmax,
            'voc': voc,
            'isc': isc,
            'ff': ff,
            'notes': notes
        }

        st.session_state.live_readings.append(reading)
        st.success(f"✅ Reading added for {module_id} at {elapsed_hours}h")

    # Display current readings
    st.subheader("Current Readings")

    if st.session_state.live_readings:
        df_readings = pd.DataFrame(st.session_state.live_readings)

        # Display in table
        st.dataframe(df_readings, use_container_width=True)

        # Quick statistics
        st.subheader("Live Statistics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Readings", len(st.session_state.live_readings))

        with col2:
            if len(st.session_state.live_readings) > 0:
                avg_power = df_readings['pmax'].mean()
                st.metric("Avg Power (W)", f"{avg_power:.2f}")

        with col3:
            if len(st.session_state.live_readings) > 0:
                avg_temp = df_readings['module_temp'].mean()
                st.metric("Avg Temp (°C)", f"{avg_temp:.1f}")

        with col4:
            if len(st.session_state.live_readings) > 0:
                avg_irr = df_readings['irradiance'].mean()
                st.metric("Avg Irradiance (W/m²)", f"{avg_irr:.0f}")

        # Real-time degradation calculation
        if len(st.session_state.live_readings) >= 2:
            st.subheader("🔄 Real-Time Degradation Analysis")

            results = st.session_state.handler.calculate_degradation_metrics(
                st.session_state.live_readings
            )

            if results.get('module_results'):
                for module_result in results['module_results']:
                    with st.expander(f"Module {module_result['module_id']}"):
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric(
                                "Initial Power",
                                f"{module_result['initial_power']:.2f} W"
                            )
                            st.metric(
                                "Current Power",
                                f"{module_result['final_power']:.2f} W"
                            )

                        with col2:
                            degradation = module_result['degradation_percentage']
                            st.metric(
                                "Degradation",
                                f"{degradation:.2f}%",
                                delta=f"{-degradation:.2f}%"
                            )
                            st.metric(
                                "Recovery",
                                f"{module_result['recovery_percentage']:.2f}%"
                            )

                        with col3:
                            st.metric(
                                "Stabilized",
                                "Yes" if module_result['stabilization_achieved'] else "No"
                            )
                            if module_result['stabilization_time']:
                                st.metric(
                                    "Stabilization Time",
                                    f"{module_result['stabilization_time']:.1f}h"
                                )

        # Option to clear readings
        if st.button("🗑️ Clear All Readings", type="secondary"):
            st.session_state.live_readings = []
            st.rerun()

    else:
        st.info("No readings recorded yet. Add readings above to begin.")


def analysis_results_page():
    """Analysis and results page"""
    st.header("📈 Analysis & Results")

    if not st.session_state.live_readings:
        st.warning("⚠️ No data available for analysis. Please enter readings first.")
        return

    # Save readings to protocol data
    st.session_state.protocol_data['live_readings'] = st.session_state.live_readings

    # Generate analysis report
    if st.button("🔄 Generate Analysis Report", type="primary"):
        with st.spinner("Analyzing data..."):
            report = st.session_state.handler.generate_analysis_report(
                st.session_state.protocol_data
            )

            st.session_state.analysis_report = report

    # Display results
    if 'analysis_report' in st.session_state:
        report = st.session_state.analysis_report

        if report['status'] == 'success':
            st.success("✅ Analysis completed successfully!")

            # Summary metrics
            st.subheader("Test Summary")

            col1, col2, col3, col4 = st.columns(4)

            summary = report.get('summary', {})
            stats = report.get('statistics', {})

            with col1:
                st.metric(
                    "Modules Tested",
                    stats.get('modules_tested', 0)
                )

            with col2:
                st.metric(
                    "Modules Passed",
                    summary.get('modules_passed', 0),
                    delta=f"{summary.get('pass_rate', 0):.1f}%"
                )

            with col3:
                st.metric(
                    "Avg Degradation",
                    f"{stats.get('average_degradation', 0):.2f}%"
                )

            with col4:
                st.metric(
                    "Std Deviation",
                    f"{stats.get('std_deviation', 0):.2f}%"
                )

            # Module results table
            st.subheader("Module Results")

            results_data = []
            for module in report['module_results']:
                results_data.append({
                    'Module ID': module['module_id'],
                    'Initial Power (W)': f"{module['initial_power']:.2f}",
                    'Final Power (W)': f"{module['final_power']:.2f}",
                    'Degradation (%)': f"{module['degradation_percentage']:.2f}",
                    'Recovery (%)': f"{module['recovery_percentage']:.2f}",
                    'Stabilized': '✓' if module['stabilization_achieved'] else '✗',
                    'Status': module['pass_fail']
                })

            df_results = pd.DataFrame(results_data)

            # Color code the status
            def highlight_status(val):
                if val == 'PASS':
                    return 'background-color: #90EE90'
                elif val == 'FAIL':
                    return 'background-color: #FFB6C1'
                return ''

            styled_df = df_results.style.applymap(
                highlight_status,
                subset=['Status']
            )

            st.dataframe(styled_df, use_container_width=True)

            # Detailed module results
            st.subheader("Detailed Results")

            for module in report['module_results']:
                with st.expander(f"Module {module['module_id']} - {module['pass_fail']}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write("**Performance Metrics:**")
                        st.write(f"- Initial Power: {module['initial_power']:.2f} W")
                        st.write(f"- Final Power: {module['final_power']:.2f} W")
                        st.write(f"- Minimum Power: {module['minimum_power']:.2f} W")
                        st.write(f"- Degradation: {module['degradation_percentage']:.3f}%")
                        st.write(f"- Recovery: {module['recovery_percentage']:.3f}%")

                    with col2:
                        st.write("**Stabilization:**")
                        st.write(f"- Achieved: {'Yes' if module['stabilization_achieved'] else 'No'}")
                        if module['stabilization_time']:
                            st.write(f"- Time: {module['stabilization_time']:.1f} hours")
                        st.write(f"- Trend: {module.get('power_trend', 'N/A')}")

                    if 'pass_fail_reasons' in module:
                        st.write("**Assessment:**")
                        for reason in module['pass_fail_reasons']:
                            icon = "✅" if module['pass_fail'] == 'PASS' else "❌"
                            st.write(f"{icon} {reason}")

        else:
            st.error(f"❌ Analysis failed: {report.get('message', 'Unknown error')}")


def charts_visualization_page():
    """Charts and visualization page"""
    st.header("📊 Charts & Visualization")

    if not st.session_state.live_readings:
        st.warning("⚠️ No data available. Please enter readings first.")
        return

    handler = st.session_state.handler

    # Chart selection
    chart_types = [
        "Power vs Time",
        "Degradation Trend",
        "Temperature Profile",
        "Irradiance Profile",
        "Fill Factor vs Time"
    ]

    selected_charts = st.multiselect(
        "Select Charts to Display",
        chart_types,
        default=["Power vs Time", "Degradation Trend"]
    )

    # Generate charts
    for chart_type in selected_charts:
        chart_id = chart_type.lower().replace(' ', '_')

        chart_data = handler.get_chart_data(st.session_state.live_readings, chart_id)

        if not chart_data.get('modules'):
            continue

        st.subheader(chart_type)

        # Create Plotly figure
        fig = go.Figure()

        for module_id, data in chart_data['modules'].items():
            fig.add_trace(go.Scatter(
                x=data['x'],
                y=data['y'],
                mode='lines+markers',
                name=f"Module {module_id}",
                line=dict(width=2),
                marker=dict(size=8)
            ))

        # Update layout
        fig.update_layout(
            xaxis_title=chart_data['modules'][list(chart_data['modules'].keys())[0]]['x_label'],
            yaxis_title=chart_data['modules'][list(chart_data['modules'].keys())[0]]['y_label'],
            hovermode='x unified',
            height=400,
            template='plotly_white'
        )

        st.plotly_chart(fig, use_container_width=True)

    # Comparison chart
    st.subheader("Multi-Parameter Comparison")

    if len(st.session_state.live_readings) >= 2:
        df_readings = pd.DataFrame(st.session_state.live_readings)

        # Group by module
        for module_id in df_readings['module_id'].unique():
            module_data = df_readings[df_readings['module_id'] == module_id].sort_values('elapsed_hours')

            fig = go.Figure()

            # Add multiple parameters with secondary axis
            fig.add_trace(go.Scatter(
                x=module_data['elapsed_hours'],
                y=module_data['pmax'],
                name='Power (W)',
                yaxis='y'
            ))

            fig.add_trace(go.Scatter(
                x=module_data['elapsed_hours'],
                y=module_data['module_temp'],
                name='Temperature (°C)',
                yaxis='y2'
            ))

            fig.update_layout(
                title=f"Module {module_id} - Multi-Parameter View",
                xaxis=dict(title='Time (hours)'),
                yaxis=dict(title='Power (W)', side='left'),
                yaxis2=dict(title='Temperature (°C)', overlaying='y', side='right'),
                hovermode='x unified',
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)


def quality_control_page():
    """Quality control and calibration page"""
    st.header("✅ Quality Control")

    st.subheader("Equipment Calibration Status")

    # Equipment list
    equipment_types = [
        "Solar Simulator",
        "Data Logger",
        "Temperature Sensors",
        "Irradiance Sensor",
        "IV Tracer"
    ]

    calibration_data = []

    for equipment in equipment_types:
        with st.expander(f"{equipment}"):
            col1, col2 = st.columns(2)

            with col1:
                equipment_id = st.text_input("Equipment ID", key=f"eq_id_{equipment}")
                calibration_date = st.date_input("Calibration Date", key=f"cal_date_{equipment}")

            with col2:
                calibration_due = st.date_input("Calibration Due", key=f"cal_due_{equipment}")
                certificate = st.text_input("Certificate Number", key=f"cert_{equipment}")

            status = "Valid" if calibration_due > datetime.now().date() else "Expired"

            calibration_data.append({
                'equipment_id': equipment_id,
                'calibration_date': str(calibration_date),
                'calibration_due': str(calibration_due),
                'certificate_number': certificate,
                'status': status
            })

    st.subheader("Measurement Uncertainty")

    col1, col2 = st.columns(2)

    with col1:
        power_uncertainty = st.number_input("Power Uncertainty (%)", value=2.0, step=0.1)
        irradiance_uncertainty = st.number_input("Irradiance Uncertainty (%)", value=2.5, step=0.1)

    with col2:
        temperature_uncertainty = st.number_input("Temperature Uncertainty (°C)", value=0.5, step=0.1)
        voltage_uncertainty = st.number_input("Voltage Uncertainty (%)", value=0.5, step=0.1)

    if st.button("💾 Save QC Data", type="primary"):
        qc_data = {
            'calibration_status': calibration_data,
            'uncertainty': {
                'power': power_uncertainty,
                'irradiance': irradiance_uncertainty,
                'temperature': temperature_uncertainty,
                'voltage': voltage_uncertainty
            }
        }

        st.session_state.protocol_data['quality_control'] = qc_data
        st.success("✅ Quality control data saved!")


def export_reports_page():
    """Export and reporting page"""
    st.header("📤 Export & Reports")

    if not st.session_state.protocol_data:
        st.warning("⚠️ No protocol data available. Complete the protocol first.")
        return

    st.subheader("Export Options")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Export Protocol Data**")

        if st.button("📥 Download JSON", type="primary"):
            # Compile full protocol data
            full_data = st.session_state.protocol_data.copy()
            full_data['live_readings'] = st.session_state.live_readings

            if 'analysis_report' in st.session_state:
                full_data['analysis'] = st.session_state.analysis_report

            json_str = json.dumps(full_data, indent=2, default=str)

            st.download_button(
                label="💾 Download Protocol Data (JSON)",
                data=json_str,
                file_name=f"lid_lis_protocol_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

    with col2:
        st.write("**Export Analysis Report**")

        if 'analysis_report' in st.session_state:
            if st.button("📥 Download Analysis Report", type="primary"):
                report_json = json.dumps(
                    st.session_state.analysis_report,
                    indent=2,
                    default=str
                )

                st.download_button(
                    label="💾 Download Analysis (JSON)",
                    data=report_json,
                    file_name=f"lid_lis_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

    # Display protocol summary
    st.subheader("Protocol Summary")

    if st.session_state.protocol_data:
        metadata = st.session_state.protocol_data.get('protocol_metadata', {})
        general = st.session_state.protocol_data.get('general_data', {})
        sample = st.session_state.protocol_data.get('sample_information', {})

        st.write(f"**Protocol ID:** {metadata.get('id', 'N/A')}")
        st.write(f"**Project:** {general.get('project_name', 'N/A')}")
        st.write(f"**Client:** {general.get('client', 'N/A')}")
        st.write(f"**Test Date:** {general.get('test_date', 'N/A')}")
        st.write(f"**Modules Tested:** {sample.get('quantity', 0)}")
        st.write(f"**Module Type:** {sample.get('module_type', 'N/A')}")

        if st.session_state.live_readings:
            st.write(f"**Total Readings:** {len(st.session_state.live_readings)}")

        if 'analysis_report' in st.session_state:
            report = st.session_state.analysis_report
            if report['status'] == 'success':
                summary = report.get('summary', {})
                st.write(f"**Pass Rate:** {summary.get('pass_rate', 0):.1f}%")


if __name__ == "__main__":
    main()
