"""
JBOX-001 Test Execution UI

Streamlit page for running JBOX-001 Junction Box Degradation tests.
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from protocols.jbox001 import JBOX001Protocol
from core.test_runner import PhaseStatus


def main():
    """JBOX-001 test execution page."""
    st.set_page_config(
        page_title="JBOX-001 Test Runner",
        page_icon="📦",
        layout="wide"
    )

    st.title("JBOX-001: Junction Box Degradation Test")

    # Initialize protocol
    if 'protocol' not in st.session_state:
        st.session_state.protocol = JBOX001Protocol()

    if 'test_run' not in st.session_state:
        st.session_state.test_run = None

    # Sidebar - Test configuration
    with st.sidebar:
        st.header("Test Configuration")

        if st.session_state.test_run is None:
            sample_id = st.text_input("Sample ID", key="sample_id")
            operator = st.text_input("Operator", key="operator")

            if st.button("Start New Test", type="primary"):
                if sample_id and operator:
                    test_run = st.session_state.protocol.create_test_run(
                        sample_id=sample_id,
                        operator=operator
                    )
                    st.session_state.protocol.runner.start_test_run(test_run.test_run_id)
                    st.session_state.test_run = test_run
                    st.rerun()
                else:
                    st.error("Please fill in all fields")
        else:
            test_run = st.session_state.test_run
            st.success(f"Test Run: {test_run.test_run_id}")
            st.info(f"Sample: {test_run.sample_id}")
            st.info(f"Operator: {test_run.operator}")
            st.info(f"Status: {test_run.status.value}")

            if st.button("End Test"):
                st.session_state.test_run = None
                st.rerun()

    # Main content
    if st.session_state.test_run is None:
        show_protocol_info(st.session_state.protocol)
    else:
        show_test_execution(st.session_state.test_run, st.session_state.protocol)


def show_protocol_info(protocol: JBOX001Protocol):
    """Display protocol information."""
    st.markdown("## Protocol Overview")

    st.markdown(protocol.protocol['metadata']['description'])

    st.markdown("### Standards")
    for standard in protocol.protocol['metadata']['standards']:
        st.markdown(f"- {standard}")

    st.markdown("---")

    # Test phases
    st.markdown("### Test Phases")

    phases_data = []
    for phase in protocol.protocol['test_phases']:
        phases_data.append({
            'Phase ID': phase['phase_id'],
            'Name': phase['name'],
            'Duration': f"{phase.get('duration', {}).get('value', 'N/A')} {phase.get('duration', {}).get('unit', '')}",
            'Steps': len(phase['steps'])
        })

    st.dataframe(pd.DataFrame(phases_data), use_container_width=True)

    # Measurements
    st.markdown("---")
    st.markdown("### Measurements")

    measurements_data = []
    for measurement in protocol.protocol['measurements']:
        measurements_data.append({
            'ID': measurement['measurement_id'],
            'Name': measurement['name'],
            'Type': measurement['type'],
            'Unit': measurement['unit'],
            'Frequency': measurement['frequency']
        })

    st.dataframe(pd.DataFrame(measurements_data), use_container_width=True)


def show_test_execution(test_run, protocol: JBOX001Protocol):
    """Display test execution interface."""
    tabs = st.tabs([
        "Phase 1: Initial",
        "Phase 2: Thermal",
        "Phase 3: Humidity",
        "Phase 4: UV",
        "Phase 5: Electrical",
        "Phase 6: Final",
        "Summary"
    ])

    # Phase 1: Initial Characterization
    with tabs[0]:
        show_phase1_ui(test_run, protocol)

    # Phase 2: Thermal Cycling
    with tabs[1]:
        show_phase2_ui(test_run, protocol)

    # Phase 3: Humidity-Freeze
    with tabs[2]:
        show_phase3_ui(test_run, protocol)

    # Phase 4: UV Exposure
    with tabs[3]:
        show_phase4_ui(test_run, protocol)

    # Phase 5: Electrical Load
    with tabs[4]:
        show_phase5_ui(test_run, protocol)

    # Phase 6: Final Characterization
    with tabs[5]:
        show_phase6_ui(test_run, protocol)

    # Summary
    with tabs[6]:
        show_summary_ui(test_run, protocol)


def show_phase1_ui(test_run, protocol: JBOX001Protocol):
    """Phase 1: Initial Characterization UI."""
    st.header("Initial Characterization")

    with st.form("phase1_form"):
        st.subheader("Visual Inspection")
        defects_count = st.number_input("Defects Count", min_value=0, value=0)
        inspection_notes = st.text_area("Inspection Notes")

        st.subheader("Electrical Measurements")
        col1, col2 = st.columns(2)

        with col1:
            contact_resistance = st.number_input(
                "Contact Resistance (mΩ)",
                min_value=0.0,
                value=5.0,
                step=0.1
            )

            diode_v1 = st.number_input("Diode 1 Voltage (V)", value=0.65, step=0.01)
            diode_v2 = st.number_input("Diode 2 Voltage (V)", value=0.65, step=0.01)
            diode_v3 = st.number_input("Diode 3 Voltage (V)", value=0.65, step=0.01)

        with col2:
            insulation_resistance = st.number_input(
                "Insulation Resistance (MΩ)",
                min_value=0.0,
                value=100.0,
                step=1.0
            )

        st.subheader("I-V Curve Parameters")
        col3, col4, col5 = st.columns(3)

        with col3:
            pmax = st.number_input("Pmax (W)", value=300.0, step=0.1)

        with col4:
            voc = st.number_input("Voc (V)", value=40.0, step=0.1)

        with col5:
            isc = st.number_input("Isc (A)", value=9.0, step=0.1)

        submitted = st.form_submit_button("Submit Phase 1 Data")

        if submitted:
            protocol.run_initial_characterization(
                test_run=test_run,
                visual_inspection={
                    'defects_count': defects_count,
                    'notes': inspection_notes
                },
                contact_resistance=contact_resistance,
                diode_voltage=[diode_v1, diode_v2, diode_v3],
                insulation_resistance=insulation_resistance,
                iv_curve_data={'pmax': pmax, 'voc': voc, 'isc': isc}
            )
            st.success("Phase 1 data submitted successfully!")
            st.rerun()

    # Show phase status
    if 'P1' in test_run.phase_results:
        st.success(f"Phase 1 Status: {test_run.phase_results['P1']['status']}")


def show_phase2_ui(test_run, protocol: JBOX001Protocol):
    """Phase 2: Thermal Cycling UI."""
    st.header("Thermal Cycling Stress")

    st.markdown("""
    **Test Parameters:**
    - Cycles: 200
    - Low Temperature: -40°C
    - High Temperature: 85°C
    - Dwell Time: 30 minutes
    """)

    with st.form("phase2_form"):
        cycles_completed = st.number_input(
            "Cycles Completed",
            min_value=0,
            max_value=200,
            value=0,
            step=50
        )

        st.subheader("Interim Measurements (Optional)")
        add_interim = st.checkbox("Add interim measurement")

        interim_measurements = []
        if add_interim:
            cycle_num = st.number_input("Cycle Number", min_value=0, max_value=200)
            interim_resistance = st.number_input("Contact Resistance (mΩ)", value=5.0)
            interim_diode = st.number_input("Avg Diode Voltage (V)", value=0.65)

            interim_measurements.append({
                'cycle': cycle_num,
                'contact_resistance': interim_resistance,
                'diode_voltage': interim_diode
            })

        submitted = st.form_submit_button("Update Thermal Cycling")

        if submitted:
            protocol.run_thermal_cycling(
                test_run=test_run,
                cycles_completed=cycles_completed,
                interim_measurements=interim_measurements if interim_measurements else None
            )
            st.success(f"Thermal cycling updated: {cycles_completed}/200 cycles")
            st.rerun()

    # Progress bar
    if 'P2' in test_run.phase_results:
        cycles = test_run.phase_results['P2'].get('steps', {}).get('P2-S1', {}).get('result', {}).get('cycles_completed', 0)
        st.progress(cycles / 200, text=f"Progress: {cycles}/200 cycles")


def show_phase3_ui(test_run, protocol: JBOX001Protocol):
    """Phase 3: Humidity-Freeze UI."""
    st.header("Humidity-Freeze Stress")

    with st.form("phase3_form"):
        cycles_completed = st.number_input(
            "HF Cycles Completed",
            min_value=0,
            max_value=10,
            value=0
        )

        weight_gain = st.number_input(
            "Weight Gain (%)",
            min_value=0.0,
            max_value=10.0,
            value=0.0,
            step=0.1
        )

        submitted = st.form_submit_button("Submit Phase 3 Data")

        if submitted:
            protocol.run_humidity_freeze(
                test_run=test_run,
                cycles_completed=cycles_completed,
                weight_gain_percentage=weight_gain
            )
            st.success("Phase 3 data submitted!")
            st.rerun()


def show_phase4_ui(test_run, protocol: JBOX001Protocol):
    """Phase 4: UV Exposure UI."""
    st.header("UV Exposure Stress")

    with st.form("phase4_form"):
        uv_dose = st.number_input(
            "UV Dose (kWh/m²)",
            min_value=0.0,
            max_value=20.0,
            value=15.0,
            step=0.5
        )

        st.subheader("Material Degradation Assessment")
        discoloration = st.checkbox("Discoloration observed")
        cracking = st.checkbox("Cracking observed")
        embrittlement = st.checkbox("Embrittlement observed")
        defects = st.number_input("Total defects", min_value=0, value=0)

        submitted = st.form_submit_button("Submit Phase 4 Data")

        if submitted:
            protocol.run_uv_exposure(
                test_run=test_run,
                uv_dose=uv_dose,
                degradation_assessment={
                    'discoloration': discoloration,
                    'cracking': cracking,
                    'embrittlement': embrittlement,
                    'defects_count': defects
                }
            )
            st.success("Phase 4 data submitted!")
            st.rerun()


def show_phase5_ui(test_run, protocol: JBOX001Protocol):
    """Phase 5: Electrical Load Stress UI."""
    st.header("Electrical Load Stress")

    st.info("Upload CSV files with temperature and resistance monitoring data")

    temp_file = st.file_uploader("Temperature Data (CSV)", type=['csv'])
    res_file = st.file_uploader("Resistance Data (CSV)", type=['csv'])

    if st.button("Submit Phase 5 Data"):
        if temp_file and res_file:
            # Parse CSV files
            temp_df = pd.read_csv(temp_file)
            res_df = pd.read_csv(res_file)

            temp_data = temp_df.to_dict('records')
            res_data = res_df.to_dict('records')

            protocol.run_electrical_load_stress(
                test_run=test_run,
                temperature_data=temp_data,
                resistance_data=res_data
            )
            st.success("Phase 5 data submitted!")
            st.rerun()
        else:
            st.error("Please upload both temperature and resistance data files")


def show_phase6_ui(test_run, protocol: JBOX001Protocol):
    """Phase 6: Final Characterization UI."""
    st.header("Final Characterization")

    with st.form("phase6_form"):
        st.subheader("Visual Inspection")
        defects_count = st.number_input("Defects Count", min_value=0, value=0)
        inspection_notes = st.text_area("Inspection Notes")

        st.subheader("Electrical Measurements")
        col1, col2 = st.columns(2)

        with col1:
            contact_resistance = st.number_input(
                "Contact Resistance (mΩ)",
                min_value=0.0,
                value=5.0,
                step=0.1
            )

            diode_v1 = st.number_input("Diode 1 Voltage (V)", value=0.65, step=0.01)
            diode_v2 = st.number_input("Diode 2 Voltage (V)", value=0.65, step=0.01)
            diode_v3 = st.number_input("Diode 3 Voltage (V)", value=0.65, step=0.01)

        with col2:
            insulation_resistance = st.number_input(
                "Insulation Resistance (MΩ)",
                min_value=0.0,
                value=100.0,
                step=1.0
            )

        st.subheader("I-V Curve Parameters")
        col3, col4, col5 = st.columns(3)

        with col3:
            pmax = st.number_input("Pmax (W)", value=300.0, step=0.1)

        with col4:
            voc = st.number_input("Voc (V)", value=40.0, step=0.1)

        with col5:
            isc = st.number_input("Isc (A)", value=9.0, step=0.1)

        submitted = st.form_submit_button("Submit Phase 6 Data & Complete Test")

        if submitted:
            protocol.run_final_characterization(
                test_run=test_run,
                visual_inspection={
                    'defects_count': defects_count,
                    'notes': inspection_notes
                },
                contact_resistance=contact_resistance,
                diode_voltage=[diode_v1, diode_v2, diode_v3],
                insulation_resistance=insulation_resistance,
                iv_curve_data={'pmax': pmax, 'voc': voc, 'isc': isc}
            )

            protocol.runner.complete_test_run(test_run.test_run_id)

            st.success("Final characterization completed!")

            # Show QC results
            if test_run.qc_results:
                if test_run.qc_results['overall_pass']:
                    st.balloons()
                    st.success("🎉 TEST PASSED!")
                else:
                    st.error("❌ TEST FAILED")
                    st.write(f"Critical failures: {len(test_run.qc_results['critical_failures'])}")
                    st.write(f"Major failures: {len(test_run.qc_results['major_failures'])}")

            st.rerun()


def show_summary_ui(test_run, protocol: JBOX001Protocol):
    """Show test summary and results."""
    st.header("Test Summary")

    summary = test_run.get_summary()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Test Status", summary['status'])

    with col2:
        st.metric("Phases Completed", f"{summary['phases_completed']}/{summary['total_phases']}")

    with col3:
        st.metric("Measurements", summary['measurements_count'])

    with col4:
        if summary['qc_pass'] is not None:
            st.metric("QC Result", "PASS" if summary['qc_pass'] else "FAIL")

    # Measurements chart
    if test_run.measurements:
        st.subheader("Measurements Over Time")

        df = pd.DataFrame(test_run.measurements)

        # Contact resistance trend
        contact_res = df[df['measurement_id'] == 'M1']
        if not contact_res.empty:
            fig = px.line(
                contact_res,
                x='timestamp',
                y='value',
                title='Contact Resistance Over Time',
                labels={'value': 'Resistance (mΩ)', 'timestamp': 'Time'}
            )
            st.plotly_chart(fig, use_container_width=True)

    # QC Results
    if test_run.qc_results:
        st.subheader("QC Results")

        criteria_results = test_run.qc_results.get('criteria_results', [])
        if criteria_results:
            qc_df = pd.DataFrame([
                {
                    'Criterion': r['criterion_id'],
                    'Description': r['description'],
                    'Severity': r['severity'],
                    'Status': '✅ PASS' if r['passed'] else '❌ FAIL',
                    'Actual Value': r.get('actual_value', 'N/A')
                }
                for r in criteria_results
            ])

            st.dataframe(qc_df, use_container_width=True)

    # Download report
    if st.button("Generate & Download Report"):
        report = protocol.generate_test_report(test_run)
        st.json(report)
        st.success("Report generated!")


if __name__ == "__main__":
    main()
