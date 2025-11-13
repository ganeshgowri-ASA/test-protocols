"""
Data Entry Page
Record test measurements and environmental data
"""

import streamlit as st
from pathlib import Path
import sys
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from protocols.delam_001 import DELAM001Protocol, DELAM001Validator

st.set_page_config(page_title="Data Entry", page_icon="📝", layout="wide")

st.markdown("# 📝 Test Data Entry")
st.markdown("Record measurements and environmental data for DELAM-001 test")
st.markdown("---")


def main():
    # Initialize session state for test data
    if 'test_data' not in st.session_state:
        st.session_state.test_data = {
            'test_id': '',
            'module_id': '',
            'start_time': datetime.now(),
            'measurements': [],
            'environmental_data': []
        }

    # Test identification
    st.markdown("### Test Identification")

    col1, col2, col3 = st.columns(3)

    with col1:
        test_id = st.text_input(
            "Test ID",
            value=st.session_state.test_data['test_id'],
            placeholder="TEST-DELAM-001-001",
            help="Unique test identifier"
        )

    with col2:
        module_id = st.text_input(
            "Module ID",
            value=st.session_state.test_data['module_id'],
            placeholder="MOD-2025-001",
            help="Module identifier"
        )

    with col3:
        operator_id = st.text_input(
            "Operator ID",
            placeholder="OPERATOR-001",
            help="Operator identifier"
        )

    # Update session state
    st.session_state.test_data['test_id'] = test_id
    st.session_state.test_data['module_id'] = module_id

    # Validate module ID
    if module_id:
        validator = DELAM001Validator()
        is_valid, errors = validator.validate_module_id(module_id)
        if not is_valid:
            st.error(f"❌ Invalid Module ID: {', '.join(errors)}")

    st.markdown("---")

    # Tabs for different data entry sections
    tabs = st.tabs([
        "🌡️ Environmental Data",
        "⚡ Electrical Measurements",
        "👁️ Visual Inspection",
        "📊 Data Summary"
    ])

    # Environmental Data Tab
    with tabs[0]:
        st.markdown("### Environmental Conditions")

        col1, col2, col3 = st.columns(3)

        with col1:
            temperature = st.number_input(
                "Temperature (°C)",
                min_value=-40.0,
                max_value=150.0,
                value=85.0,
                step=0.1,
                help="Current chamber temperature"
            )

        with col2:
            humidity = st.number_input(
                "Humidity (% RH)",
                min_value=0.0,
                max_value=100.0,
                value=85.0,
                step=0.1,
                help="Current chamber humidity"
            )

        with col3:
            pressure = st.number_input(
                "Pressure (kPa)",
                min_value=0.0,
                value=101.325,
                step=0.1,
                help="Current atmospheric pressure"
            )

        measurement_time = st.time_input("Measurement Time", datetime.now().time())

        if st.button("📊 Record Environmental Data", type="primary"):
            env_data = {
                'timestamp': datetime.now().isoformat(),
                'temperature': temperature,
                'humidity': humidity,
                'pressure': pressure
            }

            validator = DELAM001Validator()
            is_valid, errors = validator.validate_environmental_data(env_data)

            if is_valid:
                st.session_state.test_data['environmental_data'].append(env_data)
                st.success("✅ Environmental data recorded successfully!")
            else:
                st.error(f"❌ Validation errors: {', '.join(errors)}")

        # Display recorded data
        if st.session_state.test_data['environmental_data']:
            st.markdown("#### Recorded Environmental Data")
            st.dataframe(st.session_state.test_data['environmental_data'])

    # Electrical Measurements Tab
    with tabs[1]:
        st.markdown("### Electrical Measurements")

        col1, col2, col3 = st.columns(3)

        with col1:
            voltage = st.number_input(
                "Voltage (V)",
                min_value=0.0,
                value=0.0,
                step=0.1,
                help="Open circuit voltage or operating voltage"
            )

        with col2:
            current = st.number_input(
                "Current (A)",
                min_value=0.0,
                value=0.0,
                step=0.01,
                help="Short circuit current or operating current"
            )

        with col3:
            power = st.number_input(
                "Power (W)",
                min_value=0.0,
                value=voltage * current,
                step=0.1,
                help="Module power output"
            )

        measurement_type = st.selectbox(
            "Measurement Type",
            options=["Initial", "Interim (250h)", "Interim (500h)", "Final (1000h)"],
            help="Type of measurement"
        )

        if st.button("⚡ Record Electrical Measurement", type="primary"):
            measurement = {
                'timestamp': datetime.now().isoformat(),
                'type': measurement_type,
                'voltage': voltage,
                'current': current,
                'power': power
            }

            validator = DELAM001Validator()
            is_valid, errors = validator.validate_measurement_data(measurement)

            if is_valid:
                st.session_state.test_data['measurements'].append(measurement)
                st.success("✅ Measurement recorded successfully!")
            else:
                st.error(f"❌ Validation errors: {', '.join(errors)}")

        # Display recorded measurements
        if st.session_state.test_data['measurements']:
            st.markdown("#### Recorded Measurements")
            st.dataframe(st.session_state.test_data['measurements'])

    # Visual Inspection Tab
    with tabs[2]:
        st.markdown("### Visual Inspection Checklist")

        st.markdown("Check all defects observed:")

        col1, col2 = st.columns(2)

        with col1:
            bubbles = st.checkbox("Bubbles or blisters")
            discoloration = st.checkbox("Discoloration or yellowing")
            delamination = st.checkbox("Visible delamination")

        with col2:
            broken_cells = st.checkbox("Broken cells")
            broken_interconnects = st.checkbox("Broken interconnects")
            other_defects = st.checkbox("Other defects")

        if other_defects:
            defect_description = st.text_area(
                "Describe other defects",
                height=100
            )

        inspector_notes = st.text_area(
            "Inspector Notes",
            height=100,
            help="Additional observations"
        )

        if st.button("👁️ Record Visual Inspection", type="primary"):
            visual_data = {
                'timestamp': datetime.now().isoformat(),
                'no_bubbles': not bubbles,
                'no_discoloration': not discoloration,
                'no_broken_cells': not broken_cells,
                'no_broken_interconnects': not broken_interconnects,
                'notes': inspector_notes
            }

            if 'visual_inspections' not in st.session_state.test_data:
                st.session_state.test_data['visual_inspections'] = []

            st.session_state.test_data['visual_inspections'].append(visual_data)
            st.success("✅ Visual inspection recorded successfully!")

    # Data Summary Tab
    with tabs[3]:
        st.markdown("### Test Data Summary")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Environmental Records",
                len(st.session_state.test_data.get('environmental_data', []))
            )

        with col2:
            st.metric(
                "Electrical Measurements",
                len(st.session_state.test_data.get('measurements', []))
            )

        with col3:
            st.metric(
                "Visual Inspections",
                len(st.session_state.test_data.get('visual_inspections', []))
            )

        st.markdown("#### Complete Test Data")
        st.json(st.session_state.test_data)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("💾 Save Test Data", type="primary"):
                import json
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = project_root / "data" / f"test_data_{test_id}_{timestamp}.json"
                save_path.parent.mkdir(parents=True, exist_ok=True)

                with open(save_path, 'w') as f:
                    json.dump(st.session_state.test_data, f, indent=2, default=str)

                st.success(f"✅ Data saved to: {save_path}")

        with col2:
            if st.button("🗑️ Clear All Data"):
                st.session_state.test_data = {
                    'test_id': '',
                    'module_id': '',
                    'start_time': datetime.now(),
                    'measurements': [],
                    'environmental_data': []
                }
                st.success("✅ All data cleared!")
                st.rerun()


if __name__ == "__main__":
    main()
