"""
Main Streamlit Application for PV Testing Protocol Framework
GenSpark UI for dynamic protocol execution and analysis
"""

import streamlit as st
import json
from pathlib import Path
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from protocols.degradation.snail_trail_formation import SnailTrailFormationProtocol
from database.db_config import init_db, get_db_session
from database.models import Protocol, TestRun, Measurement


# Page configuration
st.set_page_config(
    page_title="PV Testing Protocol Framework",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)


def init_session_state():
    """Initialize session state variables"""
    if 'protocol_loaded' not in st.session_state:
        st.session_state.protocol_loaded = False
    if 'test_data' not in st.session_state:
        st.session_state.test_data = {}
    if 'measurements' not in st.session_state:
        st.session_state.measurements = []
    if 'test_result' not in st.session_state:
        st.session_state.test_result = None


def load_protocol_config(protocol_path: Path) -> dict:
    """Load protocol configuration from JSON file"""
    with open(protocol_path, 'r') as f:
        return json.load(f)


def render_protocol_info(config: dict):
    """Render protocol information section"""
    st.header(f"{config['protocol_id']} - {config['name']}")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Category", config['category'])
        st.metric("Version", config['version'])

    with col2:
        st.metric("Duration", f"{config['test_conditions']['duration_hours']} hours")
        st.metric("Recommended Samples", config['test_conditions']['sample_size_recommended'])

    with col3:
        st.info(config['description'])


def render_input_form(config: dict) -> dict:
    """Render dynamic input form based on protocol configuration"""
    st.subheader("Module Information")

    input_data = {}

    # Create form fields based on protocol configuration
    for param in config['input_parameters']:
        param_name = param['name']
        param_type = param['type']
        description = param.get('description', '')
        required = param.get('required', False)

        label = f"{param_name.replace('_', ' ').title()}"
        if required:
            label += " *"

        # Render appropriate input widget based on type
        if param_type == 'string':
            allowed_values = param.get('allowed_values')
            if allowed_values:
                input_data[param_name] = st.selectbox(
                    label,
                    options=allowed_values,
                    help=description
                )
            else:
                input_data[param_name] = st.text_input(
                    label,
                    help=description
                )

        elif param_type == 'float':
            unit = param.get('unit', '')
            validation = param.get('validation', {})
            min_val = validation.get('min', 0.0)
            max_val = validation.get('max', 1000.0)

            input_data[param_name] = st.number_input(
                f"{label} ({unit})" if unit else label,
                min_value=float(min_val),
                max_value=float(max_val),
                value=float(min_val),
                help=description
            )

        elif param_type == 'integer':
            input_data[param_name] = st.number_input(
                label,
                min_value=0,
                value=0,
                step=1,
                help=description
            )

    return input_data


def render_measurement_form(config: dict, inspection_hour: int) -> dict:
    """Render measurement data entry form"""
    st.subheader(f"Measurement Data - Hour {inspection_hour}")

    measurement_data = {'inspection_hour': inspection_hour}

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Visual Inspection**")

        # Visual severity
        severity_options = ['none', 'minor', 'moderate', 'severe']
        measurement_data['visual_snail_trail_severity'] = st.selectbox(
            "Snail Trail Severity",
            options=severity_options,
            key=f"severity_{inspection_hour}"
        )

        # Affected cells
        measurement_data['affected_cells_count'] = st.number_input(
            "Affected Cells Count",
            min_value=0,
            max_value=144,
            value=0,
            step=1,
            key=f"cells_{inspection_hour}"
        )

        # Affected area
        measurement_data['affected_area_percent'] = st.number_input(
            "Affected Area (%)",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=0.1,
            key=f"area_{inspection_hour}"
        )

    with col2:
        st.write("**Electrical Measurements**")

        # Pmax
        measurement_data['pmax_w'] = st.number_input(
            "Pmax (W)",
            min_value=0.0,
            max_value=1000.0,
            value=0.0,
            step=0.1,
            key=f"pmax_{inspection_hour}"
        )

        # Isc
        measurement_data['isc_a'] = st.number_input(
            "Isc (A)",
            min_value=0.0,
            max_value=20.0,
            value=0.0,
            step=0.01,
            key=f"isc_{inspection_hour}"
        )

        # Voc
        measurement_data['voc_v'] = st.number_input(
            "Voc (V)",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=0.1,
            key=f"voc_{inspection_hour}"
        )

        # Fill Factor
        measurement_data['ff_percent'] = st.number_input(
            "Fill Factor (%)",
            min_value=50.0,
            max_value=100.0,
            value=75.0,
            step=0.1,
            key=f"ff_{inspection_hour}"
        )

    # Notes
    measurement_data['notes'] = st.text_area(
        "Notes",
        key=f"notes_{inspection_hour}",
        help="Additional observations"
    )

    return measurement_data


def render_results_visualization(result):
    """Render test results with visualizations"""
    st.header("Test Results")

    # Overall result
    overall_result = result.analysis_results['pass_fail']['overall']
    if overall_result['passed']:
        st.success(f"✅ TEST PASSED")
    else:
        st.error(f"❌ TEST FAILED")

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        power_deg = result.analysis_results['power_degradation']['degradation_percent']
        st.metric(
            "Power Degradation",
            f"{power_deg:.2f}%",
            delta=f"{-power_deg:.2f}%",
            delta_color="inverse"
        )

    with col2:
        affected_area = result.analysis_results['snail_trail_metrics']['final_affected_area_percent']
        st.metric(
            "Affected Area",
            f"{affected_area:.2f}%",
            delta=f"+{affected_area:.2f}%",
            delta_color="inverse"
        )

    with col3:
        affected_cells = result.analysis_results['snail_trail_metrics']['final_affected_cells']
        st.metric(
            "Affected Cells",
            affected_cells
        )

    with col4:
        qc_status = "PASSED" if result.qc_passed else "FAILED"
        st.metric("QC Status", qc_status)

    # Create visualizations
    st.subheader("Performance Trends")

    measurements = result.measurements['raw_data']
    df = pd.DataFrame(measurements)

    # Calculate power degradation for each measurement
    initial_pmax = result.input_data['initial_pmax_w']
    df['power_degradation_percent'] = ((initial_pmax - df['pmax_w']) / initial_pmax * 100)

    # Plot 1: Power Degradation Over Time
    fig1 = px.line(
        df,
        x='inspection_hour',
        y='power_degradation_percent',
        title='Power Degradation Over Time',
        labels={'inspection_hour': 'Test Hours', 'power_degradation_percent': 'Power Degradation (%)'},
        markers=True
    )
    fig1.add_hline(y=5.0, line_dash="dash", line_color="red", annotation_text="Failure Threshold (5%)")
    st.plotly_chart(fig1, use_container_width=True)

    # Plot 2: Snail Trail Progression
    fig2 = px.line(
        df,
        x='inspection_hour',
        y='affected_area_percent',
        title='Snail Trail Area Progression',
        labels={'inspection_hour': 'Test Hours', 'affected_area_percent': 'Affected Area (%)'},
        markers=True
    )
    fig2.add_hline(y=10.0, line_dash="dash", line_color="red", annotation_text="Failure Threshold (10%)")
    st.plotly_chart(fig2, use_container_width=True)

    # Plot 3: Correlation
    fig3 = px.scatter(
        df,
        x='affected_area_percent',
        y='power_degradation_percent',
        title='Correlation: Snail Trail Coverage vs Power Loss',
        labels={'affected_area_percent': 'Affected Area (%)', 'power_degradation_percent': 'Power Degradation (%)'},
        trendline="ols"
    )
    st.plotly_chart(fig3, use_container_width=True)

    # QC Details
    st.subheader("Quality Control Results")

    qc_df = []
    for check_name, check_data in result.qc_details.items():
        if check_name != 'overall':
            qc_df.append({
                'Check': check_name.replace('_', ' ').title(),
                'Status': '✅ Passed' if check_data['passed'] else '❌ Failed',
                'Severity': check_data.get('severity', 'N/A')
            })

    st.table(pd.DataFrame(qc_df))


def main():
    """Main application"""
    init_session_state()

    # Sidebar
    st.sidebar.title("PV Testing Framework")
    st.sidebar.image("https://via.placeholder.com/200x100.png?text=PV+Testing", use_container_width=True)

    # Protocol selection
    st.sidebar.subheader("Protocol Selection")
    protocol_options = {
        "SNAIL-001: Snail Trail Formation": Path(__file__).parent.parent / "protocols" / "degradation" / "snail_trail_formation.json"
    }

    selected_protocol = st.sidebar.selectbox(
        "Select Protocol",
        options=list(protocol_options.keys())
    )

    protocol_path = protocol_options[selected_protocol]
    config = load_protocol_config(protocol_path)

    # Main content
    st.title("🔬 PV Testing Protocol Framework")

    # Display protocol info
    render_protocol_info(config)

    st.markdown("---")

    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Setup", "📊 Data Entry", "📈 Results", "💾 History"])

    with tab1:
        st.subheader("Test Setup")
        input_data = render_input_form(config)

        if st.button("Save Module Information", type="primary"):
            st.session_state.test_data['input_params'] = input_data
            st.success("Module information saved!")

    with tab2:
        st.subheader("Measurement Data Entry")

        if 'input_params' not in st.session_state.test_data:
            st.warning("Please complete the test setup first!")
        else:
            # Inspection intervals
            intervals = config['test_conditions']['inspection_intervals_hours']

            selected_interval = st.selectbox(
                "Select Inspection Interval (hours)",
                options=intervals
            )

            measurement = render_measurement_form(config, selected_interval)

            if st.button("Add Measurement", type="primary"):
                # Check if measurement already exists for this interval
                existing = [m for m in st.session_state.measurements if m['inspection_hour'] == selected_interval]

                if existing:
                    # Update existing
                    for i, m in enumerate(st.session_state.measurements):
                        if m['inspection_hour'] == selected_interval:
                            st.session_state.measurements[i] = measurement
                    st.success(f"Updated measurement for hour {selected_interval}")
                else:
                    # Add new
                    st.session_state.measurements.append(measurement)
                    st.success(f"Added measurement for hour {selected_interval}")

            # Display current measurements
            if st.session_state.measurements:
                st.subheader("Current Measurements")
                measurements_df = pd.DataFrame(st.session_state.measurements)
                measurements_df = measurements_df.sort_values('inspection_hour')
                st.dataframe(measurements_df, use_container_width=True)

                # Run analysis button
                if st.button("🚀 Run Protocol Analysis", type="primary"):
                    with st.spinner("Running analysis..."):
                        try:
                            # Create protocol instance
                            protocol = SnailTrailFormationProtocol()

                            # Prepare test data
                            test_data = {
                                'input_params': st.session_state.test_data['input_params'],
                                'measurements': st.session_state.measurements
                            }

                            # Run protocol
                            result = protocol.run(test_data)
                            st.session_state.test_result = result

                            st.success("Analysis complete! View results in the Results tab.")

                        except Exception as e:
                            st.error(f"Error running analysis: {str(e)}")

    with tab3:
        if st.session_state.test_result:
            render_results_visualization(st.session_state.test_result)

            # Generate report button
            if st.button("📄 Generate PDF Report"):
                with st.spinner("Generating report..."):
                    try:
                        protocol = SnailTrailFormationProtocol()
                        protocol.result = st.session_state.test_result
                        protocol.measurements_df = pd.DataFrame(st.session_state.measurements)

                        report_path = protocol.generate_report(Path("./reports"))
                        st.success(f"Report generated: {report_path}")

                        # Offer download
                        with open(report_path, 'rb') as f:
                            st.download_button(
                                "⬇️ Download Report",
                                f,
                                file_name=report_path.name,
                                mime='application/pdf'
                            )

                    except Exception as e:
                        st.error(f"Error generating report: {str(e)}")
        else:
            st.info("No results available. Please run the protocol analysis first.")

    with tab4:
        st.subheader("Test History")
        st.info("Test history will be displayed here once database integration is complete.")


if __name__ == "__main__":
    main()
