"""Test Dashboard page for running and monitoring tests."""

import streamlit as st
from datetime import datetime
import json
from pathlib import Path

from src.tests.track.track_001.protocol import TRACK001Protocol
from src.tests.track.track_001.test_runner import TRACK001TestRunner
from src.core.protocol import ProtocolConfig
from src.utils.db import get_db_manager


def render_test_dashboard() -> None:
    """Render the test dashboard page."""
    st.markdown('<p class="main-header">Test Dashboard</p>', unsafe_allow_html=True)

    # Protocol selection
    st.markdown("### 1. Select Protocol")
    protocol_option = st.selectbox(
        "Choose a test protocol",
        ["TRACK-001 - Tracker Performance Test"],
        key="protocol_select"
    )

    if protocol_option.startswith("TRACK-001"):
        render_track001_dashboard()


def render_track001_dashboard() -> None:
    """Render TRACK-001 specific test dashboard."""
    st.markdown("---")
    st.markdown("### 2. Test Configuration")

    col1, col2 = st.columns(2)

    with col1:
        operator = st.text_input("Operator Name", value="Test Operator", key="operator")
        sample_id = st.text_input("Sample/Tracker ID", value="TRACKER-001", key="sample_id")
        device_id = st.text_input("Device ID", value="DUT-001", key="device_id")
        location = st.text_input("Test Location", value="Test Lab", key="location")

    with col2:
        latitude = st.number_input("Latitude (degrees)", value=40.0, key="latitude")
        longitude = st.number_input("Longitude (degrees)", value=-105.0, key="longitude")
        data_source = st.selectbox(
            "Data Source",
            ["simulated", "hardware", "file"],
            key="data_source"
        )

    st.markdown("---")
    st.markdown("### 3. Test Parameters")

    # Load protocol configuration
    protocol_file = Path("schemas/examples/track_001_example.json")

    if protocol_file.exists():
        with open(protocol_file, 'r') as f:
            protocol_data = json.load(f)

        # Display key parameters
        params_col1, params_col2, params_col3 = st.columns(3)

        with params_col1:
            st.metric(
                "Test Duration",
                f"{protocol_data['test_parameters']['duration']['value']} {protocol_data['test_parameters']['duration']['unit']}"
            )

        with params_col2:
            st.metric(
                "Sample Interval",
                f"{protocol_data['test_parameters']['sample_interval']['value']} {protocol_data['test_parameters']['sample_interval']['unit']}"
            )

        with params_col3:
            st.metric(
                "Tracking Mode",
                protocol_data['test_parameters']['tracking_mode']
            )

        # Show metrics
        with st.expander("Measurement Metrics"):
            metrics_df = {
                "Metric": [m['name'] for m in protocol_data['test_parameters']['metrics']],
                "Type": [m['type'] for m in protocol_data['test_parameters']['metrics']],
                "Unit": [m['unit'] for m in protocol_data['test_parameters']['metrics']],
                "Description": [m['description'] for m in protocol_data['test_parameters']['metrics']]
            }
            st.dataframe(metrics_df, use_container_width=True)

        # Show QC criteria
        with st.expander("QC Criteria"):
            st.json(protocol_data['qc_criteria'])

        st.markdown("---")
        st.markdown("### 4. Run Test")

        # Run test button
        col_run, col_stop = st.columns([1, 3])

        with col_run:
            if st.button("▶️ Start Test", type="primary", use_container_width=True):
                run_track001_test(
                    protocol_data,
                    operator,
                    sample_id,
                    device_id,
                    location,
                    latitude,
                    longitude,
                    data_source
                )

        with col_stop:
            if st.button("⏹️ Stop Test", use_container_width=True):
                st.warning("Test stop functionality - Coming soon!")

    else:
        st.error(f"Protocol configuration file not found: {protocol_file}")
        st.info("Please ensure the protocol schema exists in the schemas/examples directory.")


def run_track001_test(
    protocol_data: dict,
    operator: str,
    sample_id: str,
    device_id: str,
    location: str,
    latitude: float,
    longitude: float,
    data_source: str
) -> None:
    """Run TRACK-001 test with progress tracking."""
    try:
        # Create protocol configuration
        config = ProtocolConfig(
            protocol_id=protocol_data['protocol_id'],
            name=protocol_data['name'],
            version=protocol_data['version'],
            category=protocol_data['category'],
            test_parameters=protocol_data['test_parameters'],
            qc_criteria=protocol_data.get('qc_criteria', {}),
            analysis_methods=protocol_data.get('analysis_methods', {}),
            description=protocol_data.get('description', ''),
            metadata=protocol_data.get('metadata', {})
        )

        # Create protocol and test runner
        protocol = TRACK001Protocol(config)
        test_runner = TRACK001TestRunner(protocol)

        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        metrics_placeholder = st.empty()

        # Callback for real-time updates
        def update_callback(data: dict) -> None:
            progress = data.get('progress', 0)
            progress_bar.progress(int(progress) / 100)
            status_text.text(f"Test running... {progress:.1f}% complete")

            # Show current measurements
            with metrics_placeholder.container():
                cols = st.columns(5)
                measurements = data.get('measurements', {})

                for idx, (metric, value) in enumerate(measurements.items()):
                    if idx < 5:
                        cols[idx].metric(metric, f"{value:.2f}")

        # Run test
        status_text.text("Initializing test...")
        run_id = test_runner.run_test(
            data_source=data_source,
            operator=operator,
            sample_id=sample_id,
            device_id=device_id,
            location=location,
            latitude=latitude,
            longitude=longitude,
            callback=update_callback
        )

        progress_bar.progress(100)
        status_text.text("Test completed successfully!")

        st.success(f"✅ Test completed successfully! Run ID: {run_id}")

        # Show summary
        summary = protocol.get_test_summary()
        if summary:
            st.markdown("### Test Summary")
            st.json(summary)

    except Exception as e:
        st.error(f"❌ Test execution failed: {str(e)}")
        st.exception(e)
