"""Main Streamlit application for PV Test Protocol Framework."""

import streamlit as st
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.protocol_loader import ProtocolLoader
from src.core.test_executor import TestExecutor
from src.models.test_result import Sample, PassFailStatus, TestStatus
from src.models.protocol import TestStage
import json
from datetime import datetime


# Page configuration
st.set_page_config(
    page_title="PV Test Protocol Framework",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)


def init_session_state():
    """Initialize session state variables."""
    if 'protocol_loader' not in st.session_state:
        st.session_state.protocol_loader = ProtocolLoader()

    if 'selected_protocol' not in st.session_state:
        st.session_state.selected_protocol = None

    if 'test_executor' not in st.session_state:
        st.session_state.test_executor = None

    if 'current_session' not in st.session_state:
        st.session_state.current_session = None

    if 'page' not in st.session_state:
        st.session_state.page = 'protocol_selection'


def protocol_selection_page():
    """Protocol selection page."""
    st.title("🔬 PV Test Protocol Framework")
    st.markdown("### Select a Test Protocol")

    # List available protocols
    protocols = st.session_state.protocol_loader.list_protocols()

    if not protocols:
        st.warning("No protocols found. Please add protocol JSON files to the protocols directory.")
        return

    # Display protocols in a table
    st.markdown("#### Available Protocols")

    for protocol in protocols:
        col1, col2, col3, col4 = st.columns([2, 3, 2, 2])

        with col1:
            st.markdown(f"**{protocol['id']}**")

        with col2:
            st.markdown(protocol['name'])

        with col3:
            st.markdown(f"*{protocol['category']}*")

        with col4:
            if st.button("Select", key=f"select_{protocol['id']}"):
                # Load protocol
                try:
                    loaded_protocol = st.session_state.protocol_loader.load_protocol(protocol['id'])
                    st.session_state.selected_protocol = loaded_protocol
                    st.session_state.test_executor = TestExecutor(loaded_protocol)
                    st.session_state.page = 'protocol_details'
                    st.rerun()
                except Exception as e:
                    st.error(f"Error loading protocol: {e}")

        st.markdown("---")


def protocol_details_page():
    """Protocol details and setup page."""
    protocol = st.session_state.selected_protocol

    if not protocol:
        st.session_state.page = 'protocol_selection'
        st.rerun()
        return

    # Header
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title(f"{protocol.id}: {protocol.name}")
    with col2:
        if st.button("← Back"):
            st.session_state.page = 'protocol_selection'
            st.rerun()

    # Protocol information tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Parameters", "Test Sequence", "Start Test"])

    with tab1:
        st.markdown("### Protocol Overview")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**Standard:** {protocol.standard}")
            st.markdown(f"**Category:** {protocol.category}")
            st.markdown(f"**Test Type:** {protocol.test_type}")
            st.markdown(f"**Version:** {protocol.version}")

        with col2:
            st.markdown(f"**Estimated Duration:** {protocol.metadata.estimated_duration_hours} hours")
            st.markdown(f"**Severity Level:** {protocol.metadata.severity_level}")
            st.markdown(f"**Min Sample Size:** {protocol.sample_requirements.sample_size.min}")

        st.markdown("### Description")
        st.info(protocol.metadata.description)

        if protocol.metadata.required_equipment:
            st.markdown("### Required Equipment")
            for equipment in protocol.metadata.required_equipment:
                st.markdown(f"- {equipment}")

        if protocol.metadata.safety_notes:
            st.markdown("### Safety Notes")
            for note in protocol.metadata.safety_notes:
                st.warning(note)

    with tab2:
        st.markdown("### Test Parameters")

        for param_name, param_def in protocol.parameters.items():
            with st.expander(f"**{param_name.replace('_', ' ').title()}**"):
                st.markdown(f"**Type:** {param_def.type}")
                if param_def.unit:
                    st.markdown(f"**Unit:** {param_def.unit}")
                if param_def.description:
                    st.markdown(f"**Description:** {param_def.description}")

                if param_def.type == "numeric" or param_def.type == "range":
                    if param_def.min is not None:
                        st.markdown(f"**Minimum:** {param_def.min}")
                    if param_def.max is not None:
                        st.markdown(f"**Maximum:** {param_def.max}")
                    if param_def.value is not None:
                        st.markdown(f"**Default:** {param_def.value}")

                elif param_def.type == "select":
                    if param_def.options:
                        st.markdown(f"**Options:** {', '.join(map(str, param_def.options))}")

    with tab3:
        st.markdown("### Test Sequence")

        if protocol.test_sequence:
            for step in protocol.test_sequence:
                with st.expander(f"**Step {step.step}: {step.name}**"):
                    st.markdown(step.description)
                    if step.duration_hours:
                        st.markdown(f"**Duration:** {step.duration_hours} hours")
                    elif step.duration_minutes:
                        st.markdown(f"**Duration:** {step.duration_minutes} minutes")

    with tab4:
        st.markdown("### Start New Test Session")

        with st.form("start_test_form"):
            st.markdown("#### Test Information")

            col1, col2 = st.columns(2)

            with col1:
                operator_name = st.text_input("Operator Name", value="")
                operator_id = st.text_input("Operator ID", value="")

            with col2:
                sample_count = st.number_input(
                    "Number of Samples",
                    min_value=protocol.sample_requirements.sample_size.min,
                    value=protocol.sample_requirements.sample_size.recommended or protocol.sample_requirements.sample_size.min,
                    step=1
                )

            st.markdown("#### Sample Information")

            samples = []
            for i in range(int(sample_count)):
                with st.expander(f"Sample {i+1}"):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        sample_id = st.text_input(f"Sample ID", key=f"sample_id_{i}", value=f"SAMPLE-{i+1:03d}")

                    with col2:
                        manufacturer = st.text_input("Manufacturer", key=f"manufacturer_{i}")

                    with col3:
                        model = st.text_input("Model", key=f"model_{i}")

                    serial_number = st.text_input("Serial Number", key=f"serial_{i}")

                    samples.append({
                        'sample_id': sample_id,
                        'manufacturer': manufacturer,
                        'model': model,
                        'serial_number': serial_number
                    })

            st.markdown("#### Test Parameters")

            # Dynamic parameter inputs
            test_params = {}
            for param_name, param_def in protocol.parameters.items():
                if param_def.type == "numeric":
                    test_params[param_name] = st.number_input(
                        f"{param_name.replace('_', ' ').title()} ({param_def.unit})",
                        min_value=param_def.min if param_def.min is not None else 0.0,
                        max_value=param_def.max if param_def.max is not None else 10000.0,
                        value=float(param_def.value) if param_def.value is not None else (param_def.min or 0.0),
                        key=f"param_{param_name}"
                    )

                elif param_def.type == "select":
                    test_params[param_name] = st.selectbox(
                        f"{param_name.replace('_', ' ').title()}",
                        options=param_def.options,
                        index=param_def.options.index(param_def.value) if param_def.value in param_def.options else 0,
                        key=f"param_{param_name}"
                    )

            submit = st.form_submit_button("Start Test Session", type="primary")

            if submit:
                # Create samples
                sample_objects = [
                    Sample(
                        sample_id=s['sample_id'],
                        manufacturer=s['manufacturer'],
                        model=s['model'],
                        serial_number=s['serial_number']
                    )
                    for s in samples
                ]

                # Start session
                try:
                    session = st.session_state.test_executor.start_session(
                        operator_id=operator_id,
                        operator_name=operator_name,
                        parameters=test_params,
                        samples=sample_objects
                    )

                    st.session_state.current_session = session
                    st.session_state.page = 'test_execution'
                    st.success("Test session started successfully!")
                    st.rerun()

                except Exception as e:
                    st.error(f"Error starting session: {e}")


def test_execution_page():
    """Test execution page."""
    protocol = st.session_state.selected_protocol
    executor = st.session_state.test_executor
    session = st.session_state.current_session

    if not session:
        st.session_state.page = 'protocol_details'
        st.rerun()
        return

    # Header
    st.title(f"Test Execution: {protocol.id}")
    st.markdown(f"**Session ID:** {session.session_id}")
    st.markdown(f"**Status:** {session.status.value}")

    # Progress tabs
    tab1, tab2, tab3 = st.tabs(["Pre-Test", "During Test", "Post-Test"])

    with tab1:
        st.markdown("### Pre-Test Measurements")

        pre_test_measurements = protocol.get_measurements_by_stage(TestStage.PRE_TEST)

        for measurement in pre_test_measurements:
            with st.expander(f"{measurement.name} {'(Required)' if measurement.required else ''}"):
                st.markdown(f"**Type:** {measurement.type}")

                if measurement.type == "qualitative":
                    if measurement.checklist:
                        st.markdown("**Checklist:**")
                        checklist_data = {}
                        for item in measurement.checklist:
                            checklist_data[item] = st.checkbox(item, key=f"{measurement.id}_{item}")

                        notes = st.text_area("Notes", key=f"{measurement.id}_notes")

                        if st.button("Save Measurement", key=f"save_{measurement.id}"):
                            try:
                                executor.add_measurement(
                                    measurement_id=measurement.id,
                                    data=checklist_data,
                                    notes=notes
                                )
                                st.success("Measurement saved!")
                            except Exception as e:
                                st.error(f"Error: {e}")

                elif measurement.type == "quantitative":
                    if measurement.measurements:
                        st.markdown("**Enter measurements:**")
                        measurement_data = {}

                        for param in measurement.measurements:
                            measurement_data[param['parameter']] = st.number_input(
                                f"{param['parameter']} ({param['unit']})",
                                key=f"{measurement.id}_{param['parameter']}"
                            )

                        if st.button("Save Measurement", key=f"save_{measurement.id}"):
                            try:
                                executor.add_measurement(
                                    measurement_id=measurement.id,
                                    data=measurement_data
                                )
                                st.success("Measurement saved!")
                            except Exception as e:
                                st.error(f"Error: {e}")

    with tab2:
        st.markdown("### During Test")
        st.info("Monitor test execution and record real-time data")

        during_measurements = protocol.get_measurements_by_stage(TestStage.DURING_TEST)

        for measurement in during_measurements:
            st.markdown(f"**{measurement.name}**")
            st.markdown(f"*{measurement.type}*")

            if measurement.type == "time_series":
                st.info("Time-series data collection interface would be implemented here")

    with tab3:
        st.markdown("### Post-Test Measurements")

        post_test_measurements = protocol.get_measurements_by_stage(TestStage.POST_TEST)

        for measurement in post_test_measurements:
            with st.expander(f"{measurement.name} {'(Required)' if measurement.required else ''}"):
                st.markdown(f"**Type:** {measurement.type}")

                if measurement.type == "qualitative":
                    if measurement.checklist:
                        st.markdown("**Checklist:**")
                        checklist_data = {}
                        for item in measurement.checklist:
                            checklist_data[item] = st.checkbox(item, key=f"{measurement.id}_{item}")

                        notes = st.text_area("Notes", key=f"{measurement.id}_notes")

                        if st.button("Save Measurement", key=f"save_{measurement.id}"):
                            try:
                                executor.add_measurement(
                                    measurement_id=measurement.id,
                                    data=checklist_data,
                                    notes=notes
                                )
                                st.success("Measurement saved!")
                            except Exception as e:
                                st.error(f"Error: {e}")

                elif measurement.type == "quantitative":
                    if measurement.measurements:
                        st.markdown("**Enter measurements:**")
                        measurement_data = {}

                        for param in measurement.measurements:
                            measurement_data[param['parameter']] = st.number_input(
                                f"{param['parameter']} ({param['unit']})",
                                key=f"{measurement.id}_{param['parameter']}"
                            )

                        if st.button("Save Measurement", key=f"save_{measurement.id}"):
                            try:
                                executor.add_measurement(
                                    measurement_id=measurement.id,
                                    data=measurement_data
                                )
                                st.success("Measurement saved!")
                            except Exception as e:
                                st.error(f"Error: {e}")

    # Complete test button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        if st.button("Complete Test", type="primary", use_container_width=True):
            try:
                executor.complete_session()
                st.session_state.page = 'results'
                st.success("Test completed!")
                st.rerun()
            except Exception as e:
                st.error(f"Error completing test: {e}")


def results_page():
    """Results and evaluation page."""
    protocol = st.session_state.selected_protocol
    executor = st.session_state.test_executor

    st.title("Test Results")

    try:
        # Evaluate results
        result = executor.evaluate_results()

        # Overall status
        status_color = {
            PassFailStatus.PASS: "green",
            PassFailStatus.FAIL: "red",
            PassFailStatus.CONDITIONAL_PASS: "orange",
            PassFailStatus.NOT_EVALUATED: "gray"
        }

        st.markdown(f"### Overall Status: :{status_color[result.overall_status]}[{result.overall_status.value.upper()}]")

        # Summary statistics
        stats = result.get_summary_statistics()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Criteria", stats['total_criteria'])

        with col2:
            st.metric("Passed", stats['passed'])

        with col3:
            st.metric("Failed", stats['failed'])

        with col4:
            if stats['test_duration_minutes']:
                st.metric("Duration (min)", f"{stats['test_duration_minutes']:.1f}")

        # Criterion evaluations
        st.markdown("### Criterion Evaluations")

        for evaluation in result.criterion_evaluations:
            status_icon = "✅" if evaluation.status == PassFailStatus.PASS else "❌"

            with st.expander(f"{status_icon} {evaluation.criterion_name.replace('_', ' ').title()}"):
                st.markdown(f"**Status:** {evaluation.status.value}")

                if evaluation.description:
                    st.markdown(f"**Description:** {evaluation.description}")

                if evaluation.measured_value is not None:
                    st.markdown(f"**Measured Value:** {evaluation.measured_value} {evaluation.unit or ''}")

                if evaluation.limit_value is not None:
                    st.markdown(f"**Limit Value:** {evaluation.limit_value} {evaluation.unit or ''}")

                if evaluation.details:
                    st.json(evaluation.details)

        # Export results
        st.markdown("### Export Results")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Export as JSON"):
                result_dict = result.model_dump(mode='json')
                st.download_button(
                    "Download JSON",
                    data=json.dumps(result_dict, indent=2, default=str),
                    file_name=f"test_result_{result.session.session_id}.json",
                    mime="application/json"
                )

        with col2:
            if st.button("Generate Report"):
                st.info("Report generation feature to be implemented")

        # New test button
        if st.button("Start New Test"):
            st.session_state.page = 'protocol_selection'
            st.session_state.current_session = None
            st.rerun()

    except Exception as e:
        st.error(f"Error evaluating results: {e}")


def main():
    """Main application."""
    init_session_state()

    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/1E88E5/FFFFFF?text=PV+Testing", use_container_width=True)
        st.markdown("---")

        if st.session_state.selected_protocol:
            st.markdown("### Current Protocol")
            st.markdown(f"**{st.session_state.selected_protocol.id}**")
            st.markdown(st.session_state.selected_protocol.name)

            if st.session_state.current_session:
                st.markdown("---")
                st.markdown("### Session Info")
                st.markdown(f"Status: {st.session_state.current_session.status.value}")
                st.markdown(f"Samples: {len(st.session_state.current_session.samples)}")
                st.markdown(f"Measurements: {len(st.session_state.current_session.measurements)}")

        st.markdown("---")
        st.markdown("### About")
        st.markdown("PV Test Protocol Framework v1.0")
        st.markdown("Standardized testing for photovoltaic modules")

    # Page routing
    if st.session_state.page == 'protocol_selection':
        protocol_selection_page()
    elif st.session_state.page == 'protocol_details':
        protocol_details_page()
    elif st.session_state.page == 'test_execution':
        test_execution_page()
    elif st.session_state.page == 'results':
        results_page()


if __name__ == "__main__":
    main()
