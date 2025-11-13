"""Main Streamlit application for PV Testing Protocol Framework."""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.models.database import init_db
from src.core.protocol_engine import ProtocolEngine
from src.core.schema_validator import SchemaValidator
from protocols.pid_001.implementation import PID001Protocol, LeakageTracker
from src.ui.components.protocol_form import (
    render_protocol_form,
    render_test_execution_card,
    render_validation_rules_info
)
from src.ui.components.results_display import (
    render_results_summary,
    render_measurements_table,
    render_leakage_events,
    render_test_metadata
)
from src.ui.components.chart_components import (
    create_leakage_current_chart,
    create_power_degradation_chart,
    create_environmental_conditions_chart,
    create_qc_summary_chart,
    create_measurement_distribution
)


# Page configuration
st.set_page_config(
    page_title="PV Testing Protocol Framework",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database on first run
@st.cache_resource
def initialize_app():
    """Initialize application resources."""
    init_db()
    return ProtocolEngine()


def main():
    """Main application entry point."""
    st.title("☀️ PV Testing Protocol Framework")
    st.markdown("*Modular testing framework for photovoltaic module quality control*")

    # Initialize
    engine = initialize_app()

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Page",
        ["🏠 Home", "▶️ Run Test", "📊 View Results", "📋 Protocols"]
    )

    if page == "🏠 Home":
        render_home_page()
    elif page == "▶️ Run Test":
        render_run_test_page(engine)
    elif page == "📊 View Results":
        render_results_page(engine)
    elif page == "📋 Protocols":
        render_protocols_page(engine)


def render_home_page():
    """Render home page."""
    st.header("Welcome to the PV Testing Protocol Framework")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### Features
        - 📋 JSON-based protocol definitions
        - 🔄 Dynamic UI generation from schemas
        - 📊 Real-time data visualization
        - ✅ Automated QC validation
        - 📈 Leakage current tracking
        - 🔌 LIMS/QMS integration ready
        - 📄 Automated report generation
        """)

    with col2:
        st.markdown("""
        ### Available Protocols
        - **PID-001**: PID Shunting Test (IEC 62804)
        - More protocols coming soon...

        ### Quick Start
        1. Select **Run Test** from the sidebar
        2. Choose a protocol
        3. Fill in test parameters
        4. Start the test
        5. View results and charts
        """)

    st.markdown("---")
    st.info("💡 This framework provides a modular approach to PV module testing with automated analysis and quality control.")


def render_run_test_page(engine: ProtocolEngine):
    """Render run test page."""
    st.header("▶️ Run Protocol Test")

    # Protocol selection
    protocols = engine.get_all_protocols()

    if not protocols:
        st.warning("No protocols available. Please initialize the database.")
        if st.button("Initialize Database"):
            from scripts.init_db import initialize_database
            initialize_database()
            st.rerun()
        return

    protocol_options = {f"{p.pid} - {p.name}": p for p in protocols}
    selected = st.selectbox("Select Protocol", list(protocol_options.keys()))

    if not selected:
        return

    protocol = protocol_options[selected]

    # Display protocol info
    st.markdown(f"### {protocol.name}")
    st.markdown(f"**Version:** {protocol.version} | **Standard:** {protocol.standard or 'N/A'}")
    st.markdown(protocol.description)

    # Load template
    template_path = Path(__file__).parent.parent.parent / "protocols" / protocol.pid / "template.json"
    import json
    default_values = {}
    if template_path.exists():
        with open(template_path) as f:
            default_values = json.load(f)

    # Render validation rules
    render_validation_rules_info(protocol.schema.get("validation_rules", {}))

    st.markdown("---")

    # Render form
    form_data = render_protocol_form(protocol.schema, default_values)

    if form_data:
        st.success("✅ Test parameters validated successfully!")

        # Show what will be run
        with st.expander("📋 Test Configuration"):
            st.json(form_data)

        # Simulate test execution
        if st.button("🚀 Execute Test (Demo Mode)", type="primary"):
            with st.spinner("Running test simulation..."):
                run_demo_test(protocol, form_data, engine)


def run_demo_test(protocol, parameters, engine):
    """Run a demo test simulation."""
    from datetime import datetime
    import time

    # Create test execution
    pid_protocol = PID001Protocol()
    test_exec = pid_protocol.create_test_execution(protocol.id, parameters)

    # Save to database
    from src.models.database import get_db
    with get_db() as db:
        db.add(test_exec)
        db.commit()
        db.refresh(test_exec)
        test_id = test_exec.id

    # Update status
    engine.update_test_execution_status(
        test_id,
        from src.models.protocol import TestExecutionStatus
        TestExecutionStatus.IN_PROGRESS,
        start_time=datetime.utcnow()
    )

    # Simulate measurements
    leakage_tracker = LeakageTracker(
        threshold_warning=parameters.get("leakage_current_threshold", 10) * 0.5,
        threshold_critical=parameters.get("leakage_current_threshold", 10)
    )

    measurements = []
    leakage_events = []

    progress_bar = st.progress(0)
    status_text = st.empty()

    # Simulate 20 measurements
    num_measurements = 20
    test_duration = parameters.get("test_duration", 96)

    for i in range(num_measurements):
        elapsed = (i / num_measurements) * test_duration

        # Generate measurement
        measurement_data = pid_protocol.simulate_measurement(
            elapsed,
            parameters.get("test_voltage", -1000)
        )

        # Process measurement
        measurement, event = pid_protocol.process_measurement(
            test_exec, measurement_data, leakage_tracker
        )

        measurements.append(measurement)
        if event:
            leakage_events.append(event)

        # Update progress
        progress_bar.progress((i + 1) / num_measurements)
        status_text.text(f"Processing measurement {i+1}/{num_measurements} (t={elapsed:.1f}h)")
        time.sleep(0.1)

    # Perform QC checks
    qc_status, qc_checks = pid_protocol.perform_qc_checks(measurements, parameters)

    # Generate summary
    results_summary = pid_protocol.generate_results_summary(measurements, qc_checks, qc_status)

    # Update test execution
    engine.update_test_execution_status(
        test_id,
        from src.models.protocol import TestExecutionStatus
        TestExecutionStatus.COMPLETED,
        end_time=datetime.utcnow(),
        duration_hours=test_duration,
        results_summary=results_summary,
        qc_status=qc_status
    )

    # Save measurements and QC checks to database
    with get_db() as db:
        for m in measurements:
            db.add(m)
        for qc in qc_checks:
            qc.test_execution_id = test_id
            db.add(qc)
        for event in leakage_events:
            db.add(event)
        db.commit()

    status_text.empty()
    progress_bar.empty()
    st.success(f"✅ Test completed! Test ID: {test_id}")
    st.info("Navigate to 'View Results' to see the full analysis.")


def render_results_page(engine: ProtocolEngine):
    """Render results viewing page."""
    st.header("📊 Test Results")

    # Get all test executions
    from src.models.database import get_db
    from src.models.protocol import TestExecution, Measurement, QCCheck

    with get_db() as db:
        tests = db.query(TestExecution).order_by(TestExecution.created_at.desc()).limit(50).all()
        test_options = {f"{t.test_name} ({t.created_at.strftime('%Y-%m-%d %H:%M')})" if t.created_at else f"{t.test_name}": t.id for t in tests}

    if not test_options:
        st.info("No test results available yet. Run a test first!")
        return

    selected = st.selectbox("Select Test", list(test_options.keys()))

    if not selected:
        return

    test_id = test_options[selected]

    # Load test execution and related data
    with get_db() as db:
        test_exec = db.query(TestExecution).filter_by(id=test_id).first()
        if not test_exec:
            st.error("Test not found")
            return

        measurements = db.query(Measurement).filter_by(test_execution_id=test_id).all()
        qc_checks = db.query(QCCheck).filter_by(test_execution_id=test_id).all()

        # Convert to dicts for display
        test_dict = {
            "id": test_exec.id,
            "test_name": test_exec.test_name,
            "module_id": test_exec.module_id,
            "status": test_exec.status.value,
            "start_time": test_exec.start_time.isoformat() if test_exec.start_time else None,
            "end_time": test_exec.end_time.isoformat() if test_exec.end_time else None,
            "duration_hours": test_exec.duration_hours,
            "qc_status": test_exec.qc_status.value if test_exec.qc_status else None,
            "input_parameters": test_exec.input_parameters,
            "operator": test_exec.operator,
            "notes": test_exec.notes,
            "summary": test_exec.results_summary
        }

        measurements_list = [
            {
                "elapsed_time": m.elapsed_time,
                "leakage_current": m.leakage_current,
                "voltage": m.voltage,
                "power_degradation": m.power_degradation,
                "temperature": m.temperature,
                "humidity": m.humidity,
            }
            for m in measurements
        ]

        qc_list = [
            {
                "check": qc.check_name,
                "status": qc.status.value,
                "message": qc.message,
                "value": qc.measured_value,
                "threshold": qc.threshold_value,
            }
            for qc in qc_checks
        ]

    # Display test execution card
    render_test_execution_card(test_dict)

    st.markdown("---")

    # Display results summary
    if test_dict.get("summary"):
        render_results_summary({"summary": test_dict["summary"]})

    st.markdown("---")

    # Charts
    if measurements_list:
        st.subheader("📈 Data Visualization")

        # Leakage current chart
        elapsed_time = [m["elapsed_time"] for m in measurements_list]
        leakage_current = [m["leakage_current"] for m in measurements_list]

        fig = create_leakage_current_chart(elapsed_time, leakage_current)
        st.plotly_chart(fig, use_container_width=True)

        # Power degradation chart
        power_degradation = [m.get("power_degradation", 0) for m in measurements_list if m.get("power_degradation") is not None]
        if power_degradation:
            fig = create_power_degradation_chart(elapsed_time[:len(power_degradation)], power_degradation)
            st.plotly_chart(fig, use_container_width=True)

        # Environmental conditions
        temperature = [m.get("temperature") for m in measurements_list if m.get("temperature") is not None]
        humidity = [m.get("humidity") for m in measurements_list if m.get("humidity") is not None]

        if temperature and humidity:
            fig = create_environmental_conditions_chart(elapsed_time[:len(temperature)], temperature, humidity)
            st.plotly_chart(fig, use_container_width=True)

        # QC summary chart
        if qc_list:
            fig = create_qc_summary_chart(qc_list)
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Measurements table
    if measurements_list:
        render_measurements_table(measurements_list)

    st.markdown("---")

    # Test metadata
    render_test_metadata(test_dict)


def render_protocols_page(engine: ProtocolEngine):
    """Render protocols page."""
    st.header("📋 Available Protocols")

    protocols = engine.get_all_protocols()

    for protocol in protocols:
        with st.expander(f"{protocol.pid} - {protocol.name}", expanded=True):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**Version:** {protocol.version}")
                st.markdown(f"**Standard:** {protocol.standard or 'N/A'}")
                st.markdown(f"**Status:** {protocol.status.value}")
                st.markdown(f"**Description:** {protocol.description}")

            with col2:
                st.markdown(f"**Created:** {protocol.created_at.strftime('%Y-%m-%d') if protocol.created_at else 'N/A'}")
                st.markdown(f"**Updated:** {protocol.updated_at.strftime('%Y-%m-%d') if protocol.updated_at else 'N/A'}")

            # Show schema info
            if st.checkbox(f"Show Schema Details ({protocol.pid})", key=f"schema_{protocol.pid}"):
                st.json(protocol.schema)


if __name__ == "__main__":
    main()
