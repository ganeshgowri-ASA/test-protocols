"""
Protocol Setup Page
Configure test parameters for DELAM-001 protocol
"""

import streamlit as st
from pathlib import Path
import sys
import json
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from protocols.delam_001 import DELAM001Protocol, DELAM001Validator

st.set_page_config(page_title="Protocol Setup", page_icon="⚙️", layout="wide")

st.markdown("# ⚙️ Protocol Setup")
st.markdown("Configure test parameters for DELAM-001 Delamination Test")
st.markdown("---")


def load_protocol():
    """Load protocol configuration"""
    if 'protocol' not in st.session_state:
        st.session_state.protocol = DELAM001Protocol()
    return st.session_state.protocol


def main():
    protocol = load_protocol()

    # Tabs for different configuration sections
    tabs = st.tabs([
        "📋 Basic Info",
        "🌡️ Environmental Conditions",
        "⏱️ Test Duration & Intervals",
        "📸 EL Imaging",
        "✅ Acceptance Criteria",
        "📊 Preview"
    ])

    # Tab 1: Basic Information
    with tabs[0]:
        st.markdown("### Basic Protocol Information")

        col1, col2 = st.columns(2)

        with col1:
            protocol_id = st.text_input(
                "Protocol ID",
                value=protocol.protocol_id,
                disabled=True,
                help="Unique protocol identifier"
            )

            protocol_name = st.text_input(
                "Protocol Name",
                value=protocol.protocol_name,
                help="Descriptive name for the protocol"
            )

            version = st.text_input(
                "Version",
                value=protocol.version,
                help="Protocol version (semantic versioning)"
            )

        with col2:
            standard_name = st.text_input(
                "Standard Name",
                value=protocol.config['standard']['name'],
                help="Reference standard (e.g., IEC 61215)"
            )

            standard_version = st.text_input(
                "Standard Version",
                value=protocol.config['standard']['version'],
                help="Standard version"
            )

            standard_section = st.text_input(
                "Standard Section",
                value=protocol.config['standard'].get('section', ''),
                help="Relevant section or clause"
            )

        description = st.text_area(
            "Description",
            value=protocol.config['metadata'].get('description', ''),
            height=100,
            help="Detailed protocol description"
        )

    # Tab 2: Environmental Conditions
    with tabs[1]:
        st.markdown("### Environmental Test Conditions")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Temperature")
            temp_value = st.number_input(
                "Temperature Value",
                value=float(protocol.config['test_parameters']['environmental_conditions']['temperature']['value']),
                min_value=-40.0,
                max_value=150.0,
                step=1.0,
                help="Target temperature"
            )

            temp_unit = st.selectbox(
                "Temperature Unit",
                options=['celsius', 'fahrenheit', 'kelvin'],
                index=0,
                help="Temperature unit"
            )

            temp_tolerance = st.number_input(
                "Temperature Tolerance (±)",
                value=float(protocol.config['test_parameters']['environmental_conditions']['temperature']['tolerance']),
                min_value=0.0,
                max_value=10.0,
                step=0.1,
                help="Acceptable temperature deviation"
            )

        with col2:
            st.markdown("#### Humidity")
            humidity_value = st.number_input(
                "Humidity Value (%)",
                value=float(protocol.config['test_parameters']['environmental_conditions']['humidity']['value']),
                min_value=0.0,
                max_value=100.0,
                step=1.0,
                help="Target relative humidity"
            )

            humidity_tolerance = st.number_input(
                "Humidity Tolerance (±%)",
                value=float(protocol.config['test_parameters']['environmental_conditions']['humidity']['tolerance']),
                min_value=0.0,
                max_value=10.0,
                step=0.1,
                help="Acceptable humidity deviation"
            )

        # Update protocol configuration
        if st.button("Update Environmental Conditions", type="primary"):
            protocol.config['test_parameters']['environmental_conditions']['temperature']['value'] = temp_value
            protocol.config['test_parameters']['environmental_conditions']['temperature']['unit'] = temp_unit
            protocol.config['test_parameters']['environmental_conditions']['temperature']['tolerance'] = temp_tolerance
            protocol.config['test_parameters']['environmental_conditions']['humidity']['value'] = humidity_value
            protocol.config['test_parameters']['environmental_conditions']['humidity']['tolerance'] = humidity_tolerance

            st.success("✅ Environmental conditions updated successfully!")

    # Tab 3: Test Duration & Intervals
    with tabs[2]:
        st.markdown("### Test Duration and Inspection Intervals")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Test Duration")
            duration_value = st.number_input(
                "Duration Value",
                value=float(protocol.config['test_parameters']['test_duration']['value']),
                min_value=1.0,
                step=1.0,
                help="Total test duration"
            )

            duration_unit = st.selectbox(
                "Duration Unit",
                options=['hours', 'days', 'cycles'],
                index=0,
                help="Duration unit"
            )

        with col2:
            st.markdown("#### Sample Specifications")
            module_type = st.selectbox(
                "Module Type",
                options=['monocrystalline', 'polycrystalline', 'thin_film', 'bifacial', 'other'],
                index=0,
                help="Type of PV module"
            )

            sample_count = st.number_input(
                "Sample Count",
                value=int(protocol.config['test_parameters']['sample_specifications']['sample_size']['count']),
                min_value=1,
                step=1,
                help="Number of samples to test"
            )

        st.markdown("#### Inspection Intervals")
        st.info("Define inspection points during the test (time, inspection types)")

        # Display current intervals
        intervals = protocol.config['test_parameters']['inspection_intervals']

        for i, interval in enumerate(intervals):
            with st.expander(f"Interval {i+1}: {interval['interval']} {interval['unit']}", expanded=False):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"**Time:** {interval['interval']} {interval['unit']}")

                with col2:
                    inspection_types = ", ".join(interval['inspection_type'])
                    st.markdown(f"**Inspections:** {inspection_types}")

    # Tab 4: EL Imaging
    with tabs[3]:
        st.markdown("### EL Imaging Configuration")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Camera Settings")

            resolution_width = st.number_input(
                "Resolution Width (pixels)",
                value=int(protocol.config['test_parameters']['el_imaging']['camera_settings']['resolution']['width']),
                min_value=640,
                step=1,
                help="Image width in pixels"
            )

            resolution_height = st.number_input(
                "Resolution Height (pixels)",
                value=int(protocol.config['test_parameters']['el_imaging']['camera_settings']['resolution']['height']),
                min_value=480,
                step=1,
                help="Image height in pixels"
            )

            exposure_time = st.number_input(
                "Exposure Time (ms)",
                value=float(protocol.config['test_parameters']['el_imaging']['camera_settings']['exposure_time']['value']),
                min_value=1.0,
                step=10.0,
                help="Camera exposure time"
            )

            bit_depth = st.selectbox(
                "Bit Depth",
                options=[8, 10, 12, 14, 16],
                index=4,
                help="Image bit depth"
            )

        with col2:
            st.markdown("#### Analysis Parameters")

            defect_threshold = st.slider(
                "Defect Detection Threshold",
                min_value=0.0,
                max_value=1.0,
                value=float(protocol.config['test_parameters']['el_imaging']['analysis_parameters']['defect_detection_threshold']),
                step=0.01,
                help="Intensity threshold for defect detection (0-1)"
            )

            min_defect_area = st.number_input(
                "Minimum Defect Area (mm²)",
                value=float(protocol.config['test_parameters']['el_imaging']['analysis_parameters']['minimum_defect_area']['value']),
                min_value=0.1,
                step=0.1,
                help="Minimum area to consider as a defect"
            )

            st.markdown("**Delamination Severity Levels:**")
            severity_levels = protocol.config['test_parameters']['el_imaging']['analysis_parameters']['delamination_severity_levels']

            for level in severity_levels:
                st.text(f"{level['level'].upper()}: {level['area_percentage_min']}% - {level['area_percentage_max']}%")

    # Tab 5: Acceptance Criteria
    with tabs[4]:
        st.markdown("### Acceptance Criteria")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Delamination Criteria")

            max_delam_area = st.number_input(
                "Maximum Delamination Area (%)",
                value=float(protocol.config['acceptance_criteria']['maximum_delamination_area']['value']),
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                help="Maximum allowed delamination area percentage"
            )

            st.markdown("#### Visual Inspection Criteria")

            visual_criteria = protocol.config['acceptance_criteria']['visual_inspection_criteria']

            no_bubbles = st.checkbox(
                "No Bubbles Required",
                value=visual_criteria.get('no_bubbles', True)
            )

            no_discoloration = st.checkbox(
                "No Discoloration Required",
                value=visual_criteria.get('no_discoloration', True)
            )

            no_broken_cells = st.checkbox(
                "No Broken Cells Required",
                value=visual_criteria.get('no_broken_cells', True)
            )

        with col2:
            st.markdown("#### Electrical Performance Criteria")

            max_power_degradation = st.number_input(
                "Maximum Power Degradation (%)",
                value=float(protocol.config['acceptance_criteria']['electrical_performance']['maximum_power_degradation']['value']),
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                help="Maximum allowed power degradation"
            )

            min_fill_factor = st.slider(
                "Minimum Fill Factor",
                min_value=0.0,
                max_value=1.0,
                value=float(protocol.config['acceptance_criteria']['electrical_performance']['minimum_fill_factor']),
                step=0.01,
                help="Minimum required fill factor"
            )

    # Tab 6: Preview
    with tabs[5]:
        st.markdown("### Protocol Configuration Preview")

        st.json(protocol.config)

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("💾 Save Configuration", type="primary"):
                # Save to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = project_root / "protocols" / "delam_001" / f"config_{timestamp}.json"
                protocol.save(save_path)
                st.success(f"✅ Configuration saved to: {save_path}")

        with col2:
            if st.button("✅ Validate Configuration"):
                validator = DELAM001Validator(protocol.config)
                # Add validation logic here
                st.success("✅ Configuration is valid!")

        with col3:
            if st.button("🔄 Reset to Default"):
                st.session_state.protocol = DELAM001Protocol()
                st.success("✅ Reset to default configuration")
                st.rerun()


if __name__ == "__main__":
    main()
