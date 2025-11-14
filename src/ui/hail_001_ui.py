"""
Streamlit UI for HAIL-001 Hail Impact Test Protocol
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from pathlib import Path
import sys
import json

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.protocols.loader import ProtocolLoader
from src.protocols.hail_001 import HAIL001Protocol
from src.analysis.database import TestDatabase


def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 'setup'
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    if 'test_data' not in st.session_state:
        st.session_state.test_data = {}
    if 'impact_count' not in st.session_state:
        st.session_state.impact_count = 0


def load_protocol():
    """Load HAIL-001 protocol"""
    try:
        loader = ProtocolLoader(protocols_dir='protocols')
        protocol_data = loader.load_protocol('HAIL-001')
        return HAIL001Protocol(protocol_data)
    except Exception as e:
        st.error(f"Error loading protocol: {e}")
        return None


def render_header(protocol):
    """Render page header"""
    st.title(f"{protocol.protocol_id}: {protocol.title}")
    st.markdown(f"**Standard**: {protocol.standard['name']}")
    st.markdown(f"**Version**: {protocol.version}")
    st.markdown("---")


def render_setup_tab(protocol, db):
    """Render test setup and module information tab"""
    st.header("Test Setup & Module Information")

    with st.form("setup_form"):
        st.subheader("Test Information")
        col1, col2 = st.columns(2)

        with col1:
            test_date = st.date_input("Test Date", datetime.now())
            test_operator = st.text_input("Test Operator", "")

        with col2:
            facility = st.text_input("Facility/Lab", "")

        st.subheader("Module Information")
        col1, col2, col3 = st.columns(3)

        with col1:
            manufacturer = st.text_input("Manufacturer *", "")
            model = st.text_input("Model *", "")

        with col2:
            serial_number = st.text_input("Serial Number *", "")
            nameplate_power = st.number_input("Nameplate Power (W) *", min_value=0.0, step=1.0)

        with col3:
            cell_technology = st.selectbox("Cell Technology",
                ["Monocrystalline", "Polycrystalline", "Thin Film", "Other"])

        st.subheader("Module Dimensions")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            length_mm = st.number_input("Length (mm)", min_value=0.0, step=1.0)
        with col2:
            width_mm = st.number_input("Width (mm)", min_value=0.0, step=1.0)
        with col3:
            thickness_mm = st.number_input("Thickness (mm)", min_value=0.0, step=0.1)
        with col4:
            weight_kg = st.number_input("Weight (kg)", min_value=0.0, step=0.1)

        submit = st.form_submit_button("Start Test Session")

        if submit:
            if not all([manufacturer, model, serial_number, nameplate_power > 0]):
                st.error("Please fill in all required fields (*)")
            else:
                # Create test session
                session_id = db.create_session(
                    protocol_id=protocol.protocol_id,
                    protocol_version=protocol.version,
                    test_date=test_date.isoformat(),
                    test_operator=test_operator,
                    facility=facility
                )

                # Insert module info
                module_data = {
                    'manufacturer': manufacturer,
                    'model': model,
                    'serial_number': serial_number,
                    'nameplate_power': nameplate_power,
                    'dimensions': {
                        'length_mm': length_mm,
                        'width_mm': width_mm,
                        'thickness_mm': thickness_mm
                    },
                    'weight_kg': weight_kg,
                    'cell_technology': cell_technology
                }

                db.insert_module_info(session_id, module_data)

                st.session_state.session_id = session_id
                st.session_state.test_data['module_info'] = module_data
                st.session_state.current_step = 'pre_test'

                st.success(f"Test session created! Session ID: {session_id}")
                st.rerun()


def render_pre_test_tab(protocol, db):
    """Render pre-test measurements tab"""
    st.header("Pre-Test Measurements")

    if st.session_state.session_id is None:
        st.warning("Please complete Test Setup first")
        return

    st.info("Perform initial measurements before impact testing")

    with st.form("pre_test_form"):
        st.subheader("IV Curve Measurements (STC)")

        col1, col2, col3 = st.columns(3)

        with col1:
            pmax_initial = st.number_input("Pmax (W) *", min_value=0.0, step=0.01, format="%.2f")
            voc = st.number_input("Voc (V)", min_value=0.0, step=0.01, format="%.2f")

        with col2:
            isc = st.number_input("Isc (A)", min_value=0.0, step=0.01, format="%.2f")
            vmp = st.number_input("Vmp (V)", min_value=0.0, step=0.01, format="%.2f")

        with col3:
            imp = st.number_input("Imp (A)", min_value=0.0, step=0.01, format="%.2f")
            fill_factor = st.number_input("Fill Factor", min_value=0.0, max_value=1.0,
                                         step=0.001, format="%.3f")

        st.subheader("Insulation Resistance")
        insulation_initial = st.number_input("Insulation Resistance (MΩ) *",
                                            min_value=0.0, step=1.0, format="%.1f")

        st.subheader("Visual Inspection")
        visual_defects = st.text_area("Pre-existing Defects (if any)")

        submit = st.form_submit_button("Save Pre-Test Measurements")

        if submit:
            if pmax_initial <= 0 or insulation_initial <= 0:
                st.error("Please enter valid Pmax and Insulation Resistance values")
            else:
                pre_test_data = {
                    'Pmax_initial': pmax_initial,
                    'Voc': voc,
                    'Isc': isc,
                    'Vmp': vmp,
                    'Imp': imp,
                    'fill_factor': fill_factor,
                    'insulation_resistance_initial': insulation_initial,
                    'visual_defects': visual_defects
                }

                db.insert_pre_test_measurement(st.session_state.session_id, pre_test_data)
                st.session_state.test_data['pre_test_data'] = pre_test_data
                st.session_state.current_step = 'impact_test'

                st.success("Pre-test measurements saved!")
                st.rerun()


def render_impact_test_tab(protocol, db):
    """Render impact test data entry tab"""
    st.header("Impact Test Execution")

    if st.session_state.session_id is None:
        st.warning("Please complete Test Setup first")
        return

    if 'pre_test_data' not in st.session_state.test_data:
        st.warning("Please complete Pre-Test Measurements first")
        return

    # Get impact locations
    impact_locations = protocol.generate_impact_locations()

    st.info(f"Progress: {st.session_state.impact_count}/11 impacts completed")

    # Progress bar
    progress = st.session_state.impact_count / 11
    st.progress(progress)

    if st.session_state.impact_count < 11:
        current_impact = st.session_state.impact_count + 1
        current_location = impact_locations[st.session_state.impact_count]

        st.subheader(f"Impact #{current_impact}")
        st.write(f"**Location**: {current_location['description']}")
        st.write(f"**Coordinates**: ({current_location['x']:.2f}, {current_location['y']:.2f})")

        with st.form(f"impact_form_{current_impact}"):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Ice Ball Parameters**")
                ice_temp = st.number_input("Ice Ball Temperature (°C)",
                                          value=-4.0, step=0.1, format="%.1f")
                ice_diameter = st.number_input("Ice Ball Diameter (mm)",
                                              value=25.0, step=0.1, format="%.1f")
                ice_weight = st.number_input("Ice Ball Weight (g)",
                                            value=7.53, step=0.01, format="%.2f")

            with col2:
                st.markdown("**Impact Data**")
                actual_velocity = st.number_input("Actual Velocity (km/h) *",
                                                 min_value=0.0, step=0.1, format="%.1f")
                time_delta = st.number_input("Time from Retrieval to Impact (s) *",
                                            min_value=0, max_value=120, step=1)
                launcher_pressure = st.number_input("Launcher Pressure (PSI)",
                                                   min_value=0.0, step=0.1, format="%.1f")

            col1, col2 = st.columns(2)

            with col1:
                open_circuit = st.checkbox("Open Circuit Detected")

            with col2:
                visual_damage = st.text_input("Visual Damage Observed")

            submit = st.form_submit_button("Record Impact")

            if submit:
                if actual_velocity <= 0 or time_delta < 0:
                    st.error("Please enter valid velocity and time values")
                else:
                    impact_data = {
                        'impact_number': current_impact,
                        'impact_location': current_location['id'],
                        'location_x': current_location['x'],
                        'location_y': current_location['y'],
                        'location_description': current_location['description'],
                        'ice_ball_diameter_mm': ice_diameter,
                        'ice_ball_weight_g': ice_weight,
                        'ice_ball_temperature_c': ice_temp,
                        'time_delta_seconds': time_delta,
                        'target_velocity_kmh': 80.0,
                        'actual_velocity_kmh': actual_velocity,
                        'velocity_deviation_kmh': actual_velocity - 80.0,
                        'launcher_pressure_psi': launcher_pressure,
                        'open_circuit_detected': open_circuit,
                        'visual_damage': visual_damage
                    }

                    db.insert_impact_data(st.session_state.session_id, impact_data)

                    if 'impacts' not in st.session_state.test_data:
                        st.session_state.test_data['impacts'] = []
                    st.session_state.test_data['impacts'].append(impact_data)

                    st.session_state.impact_count += 1

                    # Check for issues
                    if time_delta > 60:
                        st.warning("⚠️ Time limit exceeded (>60s)")
                    if abs(actual_velocity - 80.0) > 2:
                        st.warning("⚠️ Velocity outside tolerance (±2 km/h)")
                    if open_circuit:
                        st.error("🔴 Open circuit detected!")

                    st.success(f"Impact #{current_impact} recorded!")
                    st.rerun()

    else:
        st.success("✅ All 11 impacts completed!")
        if st.button("Proceed to Post-Test Measurements"):
            st.session_state.current_step = 'post_test'
            st.rerun()


def render_post_test_tab(protocol, db):
    """Render post-test measurements tab"""
    st.header("Post-Test Measurements")

    if st.session_state.impact_count < 11:
        st.warning("Please complete all 11 impact tests first")
        return

    st.info("Perform final measurements after impact testing")

    with st.form("post_test_form"):
        st.subheader("IV Curve Measurements (STC)")

        col1, col2, col3 = st.columns(3)

        with col1:
            pmax_final = st.number_input("Pmax (W) *", min_value=0.0, step=0.01, format="%.2f")
            voc = st.number_input("Voc (V)", min_value=0.0, step=0.01, format="%.2f")

        with col2:
            isc = st.number_input("Isc (A)", min_value=0.0, step=0.01, format="%.2f")
            vmp = st.number_input("Vmp (V)", min_value=0.0, step=0.01, format="%.2f")

        with col3:
            imp = st.number_input("Imp (A)", min_value=0.0, step=0.01, format="%.2f")
            fill_factor = st.number_input("Fill Factor", min_value=0.0, max_value=1.0,
                                         step=0.001, format="%.3f")

        st.subheader("Insulation Resistance")
        insulation_final = st.number_input("Insulation Resistance (MΩ) *",
                                          min_value=0.0, step=1.0, format="%.1f")

        st.subheader("Visual Inspection")

        col1, col2, col3 = st.columns(3)

        with col1:
            front_glass_cracks = st.checkbox("Front Glass Cracks")
            cell_cracks = st.checkbox("Cell Cracks")

        with col2:
            backsheet_cracks = st.checkbox("Backsheet Cracks")
            delamination = st.checkbox("Delamination")

        with col3:
            junction_box_damage = st.checkbox("Junction Box Damage")
            frame_damage = st.checkbox("Frame Damage")

        visual_description = st.text_area("Detailed Visual Inspection Notes")

        submit = st.form_submit_button("Save Post-Test Measurements")

        if submit:
            if pmax_final <= 0 or insulation_final <= 0:
                st.error("Please enter valid Pmax and Insulation Resistance values")
            else:
                post_test_data = {
                    'Pmax_final': pmax_final,
                    'Voc': voc,
                    'Isc': isc,
                    'Vmp': vmp,
                    'Imp': imp,
                    'fill_factor': fill_factor,
                    'insulation_resistance_final': insulation_final,
                    'visual_defects': {
                        'front_glass_cracks': front_glass_cracks,
                        'cell_cracks': cell_cracks,
                        'backsheet_cracks': backsheet_cracks,
                        'delamination': delamination,
                        'junction_box_damage': junction_box_damage,
                        'frame_damage': frame_damage
                    },
                    'visual_description': visual_description
                }

                db.insert_post_test_measurement(st.session_state.session_id, post_test_data)
                st.session_state.test_data['post_test_data'] = post_test_data
                st.session_state.current_step = 'results'

                st.success("Post-test measurements saved!")
                st.rerun()


def render_results_tab(protocol, db):
    """Render results and analysis tab"""
    st.header("Test Results & Analysis")

    if 'post_test_data' not in st.session_state.test_data:
        st.warning("Please complete Post-Test Measurements first")
        return

    # Prepare test data for analysis
    test_data = {
        'pre_test_data': st.session_state.test_data.get('pre_test_data', {}),
        'test_execution_data': {
            'impacts': st.session_state.test_data.get('impacts', [])
        },
        'post_test_data': st.session_state.test_data.get('post_test_data', {})
    }

    # Validate test data
    is_valid, errors = protocol.validate_test_data(test_data)

    if not is_valid:
        st.error("Test data validation failed:")
        for error in errors:
            st.error(f"- {error}")
        return

    # Analyze results
    analysis_results = protocol.analyze_results(test_data)
    pass_fail_results = protocol.evaluate_pass_fail(analysis_results)

    # Save to database
    combined_results = {
        'power_analysis': analysis_results['power_analysis'],
        'impact_analysis': analysis_results['impact_analysis'],
        'insulation_analysis': analysis_results['insulation_analysis'],
        'pass_fail': pass_fail_results
    }
    db.insert_test_results(st.session_state.session_id, combined_results)

    # Update session status
    status = 'passed' if pass_fail_results['overall_result'] == 'PASS' else 'failed'
    db.update_session_status(st.session_state.session_id, status)

    # Display overall result
    overall = pass_fail_results['overall_result']
    if overall == 'PASS':
        st.success(f"## ✅ TEST RESULT: {overall}")
    else:
        st.error(f"## ❌ TEST RESULT: {overall}")

    st.markdown("---")

    # Pass/Fail Criteria
    st.subheader("Pass/Fail Criteria Evaluation")

    criteria_data = []
    for name, data in pass_fail_results['criteria'].items():
        criteria_data.append({
            'Criterion': name.replace('_', ' ').title(),
            'Result': '✓ PASS' if data['pass'] else '✗ FAIL',
            'Value': str(data.get('value', 'N/A')),
            'Threshold': f"{data.get('threshold', '')} {data.get('unit', '')}".strip()
        })

    st.dataframe(pd.DataFrame(criteria_data), use_container_width=True)

    st.markdown("---")

    # Power Analysis
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Power Analysis")
        power = analysis_results['power_analysis']
        st.metric("Initial Pmax", f"{power['Pmax_initial']:.2f} W")
        st.metric("Final Pmax", f"{power['Pmax_final']:.2f} W")
        st.metric("Degradation", f"{power['degradation_percent']:.2f}%",
                 delta=f"-{power['degradation_watts']:.2f} W")

    with col2:
        st.subheader("Insulation Resistance")
        insulation = analysis_results['insulation_analysis']
        st.metric("Initial IR", f"{insulation['initial_resistance']:.1f} MΩ")
        st.metric("Final IR", f"{insulation['final_resistance']:.1f} MΩ")
        st.metric("Change", f"{insulation['degradation_percent']:.2f}%")

    # Impact Analysis
    st.subheader("Impact Test Statistics")

    impact_stats = analysis_results['impact_analysis']

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Mean Velocity", f"{impact_stats['velocity_mean']:.1f} km/h")
    with col2:
        st.metric("Velocity Std Dev", f"{impact_stats['velocity_std']:.1f} km/h")
    with col3:
        st.metric("Time Compliance", f"{impact_stats['time_compliance_count']}/11")
    with col4:
        st.metric("Open Circuits", f"{impact_stats['open_circuit_count']}")

    # Velocity chart
    st.subheader("Impact Velocity Distribution")

    impacts = test_data['test_execution_data']['impacts']
    velocity_data = pd.DataFrame({
        'Impact #': [i['impact_number'] for i in impacts],
        'Velocity (km/h)': [i['actual_velocity_kmh'] for i in impacts]
    })

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=velocity_data['Impact #'],
        y=velocity_data['Velocity (km/h)'],
        mode='markers+lines',
        name='Actual Velocity',
        marker=dict(size=10)
    ))

    # Add target line
    fig.add_hline(y=80, line_dash="dash", line_color="green",
                 annotation_text="Target (80 km/h)")

    # Add tolerance lines
    fig.add_hline(y=82, line_dash="dot", line_color="orange",
                 annotation_text="Upper Tolerance (82 km/h)")
    fig.add_hline(y=78, line_dash="dot", line_color="orange",
                 annotation_text="Lower Tolerance (78 km/h)")

    fig.update_layout(
        title="Impact Velocity per Test",
        xaxis_title="Impact Number",
        yaxis_title="Velocity (km/h)",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    # Impact data table
    st.subheader("Detailed Impact Data")
    impact_df = pd.DataFrame([{
        'Impact': i['impact_number'],
        'Location': i['location_description'],
        'Velocity (km/h)': i['actual_velocity_kmh'],
        'Time (s)': i['time_delta_seconds'],
        'Open Circuit': '🔴' if i['open_circuit_detected'] else '✓',
        'Damage': i['visual_damage'] or '-'
    } for i in impacts])

    st.dataframe(impact_df, use_container_width=True)


def main():
    """Main application"""
    st.set_page_config(
        page_title="HAIL-001 Test Protocol",
        page_icon="🧊",
        layout="wide"
    )

    initialize_session_state()

    protocol = load_protocol()
    if protocol is None:
        return

    db = TestDatabase("test_protocols.db")

    render_header(protocol)

    # Navigation tabs
    tabs = st.tabs([
        "📋 Test Setup",
        "📊 Pre-Test",
        "🎯 Impact Test",
        "📈 Post-Test",
        "✅ Results"
    ])

    with tabs[0]:
        render_setup_tab(protocol, db)

    with tabs[1]:
        render_pre_test_tab(protocol, db)

    with tabs[2]:
        render_impact_test_tab(protocol, db)

    with tabs[3]:
        render_post_test_tab(protocol, db)

    with tabs[4]:
        render_results_tab(protocol, db)

    db.close()


if __name__ == "__main__":
    main()
