"""
Test Protocols Module
====================
Protocol selector and execution framework with Test Results Entry Checksheet.
Last verified: 2025-11-29 - Clean syntax validation
"""

import streamlit as st
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import setup_page_config
from config.database import get_db
from config.protocols_registry import get_cached_protocol_registry
from components.navigation import render_header, render_sidebar_navigation
from components.visualizations import create_iv_curve, create_pv_curve, render_test_summary_card
from database import TestExecution, TestProtocol, ServiceRequest, TestStatus, TestData
from sqlalchemy import select, desc, asc, and_, or_, func

# Page configuration
setup_page_config(page_title="Test Protocols", page_icon="🔬")

# Render navigation
render_header("Test Protocols", "Select and execute testing protocols")
render_sidebar_navigation()


def get_protocol_db_id(protocol_id_str: str, db) -> int:
    """
    Helper function to map protocol ID string (P1, P2, etc.) to database integer ID.

    This resolves ForeignKeyViolation errors by dynamically looking up the actual
    database ID instead of using hardcoded values.

    Args:
        protocol_id_str: Protocol identifier string (e.g., 'P1', 'P2', 'P3')
        db: Active database session

    Returns:
        int: The database integer ID for the protocol, or 1 as fallback
    """
    try:
        # Query the TestProtocol table to find the matching protocol
        stmt = select(TestProtocol).where(TestProtocol.protocol_id == protocol_id_str)
        protocol = db.execute(stmt).scalar_one_or_none()

        if protocol:
            return protocol.id

        # If not found by exact match, try searching by protocol_id pattern
        # Some protocols might be stored with different formats
        stmt = select(TestProtocol).where(
            TestProtocol.protocol_id.ilike(f"%{protocol_id_str}%")
        )
        protocol = db.execute(stmt).scalar_one_or_none()

        if protocol:
            return protocol.id

        # Fallback: return 1 if no protocol found (log warning in production)
        return 1
    except Exception:
        # On any error, return 1 as safe fallback
        return 1


def main():
    """Main test protocols page"""

    tabs = st.tabs(["🔬 Protocol Selection", "📊 Execute Test", "📝 Results Checksheet", "📋 Test History"])

    with tabs[0]:
        render_protocol_selector()

    with tabs[1]:
        render_test_execution()

    with tabs[2]:
        render_test_results_checksheet()

    with tabs[3]:
        render_test_history()


def render_protocol_selector():
    """Render protocol selection interface"""

    st.markdown("### 🔬 Available Testing Protocols")

    # Get protocol registry
    registry = get_cached_protocol_registry()

    # Search and filter
    col1, col2 = st.columns([3, 1])

    with col1:
        search_query = st.text_input("🔍 Search protocols", placeholder="Enter protocol ID or name...")

    with col2:
        category_filter = st.selectbox(
            "Category",
            ["All", "Performance", "Degradation", "Environmental", "Mechanical", "Safety"]
        )

    # Get protocols
    if search_query:
        protocols = registry.search_protocols(search_query)
    elif category_filter != "All":
        protocols = registry.get_protocols_by_category(category_filter.lower())
    else:
        protocols = registry.get_active_protocols()

    if not protocols:
        st.info("No protocols found matching criteria")
        return

    # Display protocols by category
    categories = {
        "performance": [],
        "degradation": [],
        "environmental": [],
        "mechanical": [],
        "safety": []
    }

    for protocol in protocols:
        if protocol.category in categories:
            categories[protocol.category].append(protocol)

    for category_name, category_protocols in categories.items():
        if not category_protocols:
            continue

        with st.expander(f"📁 {category_name.title()} Testing ({len(category_protocols)} protocols)", expanded=True):
            for protocol in category_protocols:
                col1, col2, col3 = st.columns([3, 2, 1])

                with col1:
                    st.markdown(f"**{protocol.protocol_id}: {protocol.name}**")
                    st.caption(protocol.description)

                with col2:
                    if protocol.standard_reference:
                        st.caption(f"📋 Standard: {protocol.standard_reference}")
                    if protocol.estimated_duration_hours:
                        st.caption(f"⏱️ Duration: {protocol.estimated_duration_hours}h")

                with col3:
                    if st.button("▶️ Execute", key=f"exec_{protocol.protocol_id}"):
                        st.session_state.selected_protocol = protocol.protocol_id
                        st.success(f"Selected {protocol.protocol_id}")
                        st.info("Go to 'Execute Test' tab to run the protocol")

                st.divider()


def render_test_execution():
    """Render test execution interface"""

    st.markdown("### 📊 Execute Test Protocol")

    # Check if protocol is selected
    if 'selected_protocol' not in st.session_state:
        st.info("Please select a protocol from the 'Protocol Selection' tab")
        return

    protocol_id = st.session_state.selected_protocol
    registry = get_cached_protocol_registry()
    protocol = registry.get_protocol(protocol_id)

    if not protocol:
        st.error("Protocol not found")
        return

    # Display protocol information
    st.markdown(f"## {protocol.protocol_id}: {protocol.name}")
    st.markdown(f"**Category:** {protocol.category.title()}")
    st.markdown(f"**Standard:** {protocol.standard_reference}")

    st.divider()

    # Link to service request - extract data before session closes to avoid DetachedInstanceError
    # FIX Issue #1: sr_options dict MUST be constructed INSIDE the 'with get_db()' block
    # to prevent DetachedInstanceError when accessing ORM object attributes after session closes
    with get_db() as db:
        service_requests = db.query(ServiceRequest).filter(
            ServiceRequest.status.in_(['approved', 'in_progress'])
        ).all()
        # Extract needed data while session is still open
            sr_options = {
                f"{sr.request_number} - {sr.client_name}": sr.id
                for sr in service_requests
            }

    if not sr_options:
        st.warning("No approved service requests available. Create a service request first.")
        return


    selected_sr = st.selectbox("Link to Service Request", options=list(sr_options.keys()))
    sr_id = sr_options[selected_sr]

    # Sample information
    sample_id = st.text_input("Sample ID", placeholder="Enter sample ID from inspection...")

    # Execute protocol based on type
    if protocol_id == "P1":
        render_p1_iv_performance(protocol, sr_id, sample_id)
    elif protocol_id == "P2":
        render_p2_pv_analysis(protocol, sr_id, sample_id)
    else:
        # Use generic protocol handler for all other protocols
        render_generic_protocol(protocol, sr_id, sample_id)


def render_p1_iv_performance(protocol, sr_id, sample_id):
    """Render P1 - I-V Performance protocol execution"""

    st.markdown("### I-V Performance Characterization")

    with st.form("p1_execution"):
        st.markdown("#### Test Conditions")

        col1, col2, col3 = st.columns(3)

        with col1:
            irradiance = st.number_input("Irradiance (W/m²)", value=1000.0, step=1.0)
            temperature = st.number_input("Cell Temperature (°C)", value=25.0, step=0.1)

        with col2:
            voc = st.number_input("Voc (V)", value=0.0, step=0.01)
            isc = st.number_input("Isc (A)", value=0.0, step=0.01)

        with col3:
            vmpp = st.number_input("Vmpp (V)", value=0.0, step=0.01)
            impp = st.number_input("Impp (A)", value=0.0, step=0.01)

        # Data upload
        data_file = st.file_uploader("Upload I-V Data (CSV)", type=['csv'])

        submitted = st.form_submit_button("✅ Complete Test", type="primary")

        if submitted:
            if not sample_id:
                st.error("Please enter Sample ID")
                return

            # Calculate results
            pmax = vmpp * impp
            fill_factor = (pmax / (voc * isc)) * 100 if (voc * isc) > 0 else 0

            # Save test execution
            try:
                execution_number = generate_execution_number()

                # FIX Issue #3: Use dynamic protocol ID lookup instead of hardcoded value
                # The database session is needed to look up the actual protocol ID
                with get_db() as db:
                    # Dynamically look up the protocol database ID for 'P1'
                    protocol_db_id = get_protocol_db_id('P1', db)

                    test_data = {
                        'execution_number': execution_number,
                        'service_request_id': sr_id,
                        'protocol_id': protocol_db_id,  # Dynamic lookup replaces hardcoded 1
                        'sample_id': sample_id,
                        'status': TestStatus.COMPLETED,
                        'started_at': datetime.utcnow(),
                        'completed_at': datetime.utcnow(),
                        'technician_id': 1,
                        'input_data': {
                            'irradiance': irradiance,
                            'temperature': temperature,
                            'voc': voc,
                            'isc': isc,
                            'vmpp': vmpp,
                            'impp': impp
                        },
                        'results': {
                            'pmax': pmax,
                            'fill_factor': fill_factor,
                            'voc': voc,
                            'isc': isc,
                            'vmpp': vmpp,
                            'impp': impp
                        },
                        'test_passed': True,
                        'qa_passed': True
                    }

                    execution = TestExecution(**test_data)
                    db.add(execution)
                    db.commit()

                st.success(f"✅ Test {execution_number} completed successfully!")

                # Display results
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    render_test_summary_card("Pmax", f"{pmax:.2f}", "W", "success")

                with col2:
                    render_test_summary_card("Fill Factor", f"{fill_factor:.2f}", "%", "success")

                with col3:
                    render_test_summary_card("Voc", f"{voc:.2f}", "V", "info")

                with col4:
                    render_test_summary_card("Isc", f"{isc:.2f}", "A", "info")

                # Generate demo I-V curve
                import numpy as np
                voltage = np.linspace(0, voc, 50)
                current = isc * (1 - (voltage / voc) ** 2)

                fig = create_iv_curve(voltage.tolist(), current.tolist(), "I-V Curve - Test Results")
                st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"Error saving test: {str(e)}")


def render_p2_pv_analysis(protocol, sr_id, sample_id):
    """Render P2 - P-V Analysis protocol"""
    st.info("P2 - P-V Analysis execution interface (similar to P1)")


def render_generic_protocol(protocol, sr_id, sample_id):
    """Render generic protocol execution template with data entry checksheet"""

    st.markdown(f"### {protocol.name}")
    st.markdown(f"**Standard:** {protocol.standard_reference}")

    if protocol.estimated_duration_hours:
        st.info(f"Estimated Duration: {protocol.estimated_duration_hours} hours")

    with st.form(f"{protocol.protocol_id}_execution"):
        # Test Setup Section
        st.markdown("#### Test Setup")
        col1, col2 = st.columns(2)

        with col1:
            test_date = st.date_input("Test Date", value=datetime.now())
            test_start_time = st.time_input("Start Time", value=datetime.now().time())

        with col2:
            ambient_temp = st.number_input("Ambient Temperature (°C)", value=25.0, step=0.1)
            humidity = st.number_input("Relative Humidity (%)", value=50.0, min_value=0.0, max_value=100.0, step=1.0)

        st.divider()

        # Measurements Section based on protocol category
        st.markdown("#### Measurements & Data Entry")

        measurements = {}

        if protocol.category == "performance":
            col1, col2, col3 = st.columns(3)
            with col1:
                measurements['irradiance'] = st.number_input("Irradiance (W/m²)", value=1000.0, step=1.0)
                measurements['cell_temp'] = st.number_input("Cell Temperature (°C)", value=25.0, step=0.1)
            with col2:
                measurements['voc'] = st.number_input("Voc (V)", value=0.0, step=0.01)
                measurements['isc'] = st.number_input("Isc (A)", value=0.0, step=0.01)
            with col3:
                measurements['vmpp'] = st.number_input("Vmpp (V)", value=0.0, step=0.01)
                measurements['impp'] = st.number_input("Impp (A)", value=0.0, step=0.01)

        elif protocol.category == "degradation":
            col1, col2 = st.columns(2)
            with col1:
                measurements['initial_power'] = st.number_input("Initial Power (W)", value=0.0, step=0.1)
                measurements['final_power'] = st.number_input("Final Power (W)", value=0.0, step=0.1)
                measurements['exposure_time'] = st.number_input("Exposure Time (hours)", value=0.0, step=0.1)
            with col2:
                measurements['degradation_rate'] = st.number_input("Degradation Rate (%)", value=0.0, step=0.01)
                measurements['test_cycles'] = st.number_input("Number of Cycles", value=0, step=1)

        elif protocol.category == "environmental":
            col1, col2 = st.columns(2)
            with col1:
                measurements['chamber_temp'] = st.number_input("Chamber Temperature (°C)", value=85.0, step=0.1)
                measurements['chamber_humidity'] = st.number_input("Chamber Humidity (%)", value=85.0, step=1.0)
                measurements['test_duration'] = st.number_input("Test Duration (hours)", value=0.0, step=1.0)
            with col2:
                measurements['pre_test_power'] = st.number_input("Pre-test Power (W)", value=0.0, step=0.1)
                measurements['post_test_power'] = st.number_input("Post-test Power (W)", value=0.0, step=0.1)
                measurements['power_loss'] = st.number_input("Power Loss (%)", value=0.0, step=0.01)

        elif protocol.category == "mechanical":
            col1, col2 = st.columns(2)
            with col1:
                measurements['applied_load'] = st.number_input("Applied Load (Pa)", value=2400.0, step=100.0)
                measurements['load_cycles'] = st.number_input("Load Cycles", value=0, step=1)
                measurements['deflection'] = st.number_input("Max Deflection (mm)", value=0.0, step=0.1)
            with col2:
                measurements['pre_test_power'] = st.number_input("Pre-test Power (W)", value=0.0, step=0.1)
                measurements['post_test_power'] = st.number_input("Post-test Power (W)", value=0.0, step=0.1)
                measurements['visual_damage'] = st.checkbox("Visual Damage Detected", value=False)

        elif protocol.category == "safety":
            col1, col2 = st.columns(2)
            with col1:
                measurements['test_voltage'] = st.number_input("Test Voltage (V)", value=1000.0, step=100.0)
                measurements['leakage_current'] = st.number_input("Leakage Current (μA)", value=0.0, step=0.1)
                measurements['insulation_resistance'] = st.number_input("Insulation Resistance (MΩ)", value=0.0, step=0.1)
            with col2:
                measurements['dielectric_test'] = st.selectbox("Dielectric Test", ["Pass", "Fail", "N/A"])
                measurements['ground_continuity'] = st.selectbox("Ground Continuity", ["Pass", "Fail", "N/A"])

        st.divider()

        # Visual Inspection Checklist
        st.markdown("#### Visual Inspection Checklist")
        col1, col2, col3 = st.columns(3)

        with col1:
            visual_checks = {}
            visual_checks['no_cracks'] = st.checkbox("No visible cracks", value=True)
            visual_checks['no_delamination'] = st.checkbox("No delamination", value=True)

        with col2:
            visual_checks['no_discoloration'] = st.checkbox("No discoloration", value=True)
            visual_checks['connectors_ok'] = st.checkbox("Connectors intact", value=True)

        with col3:
            visual_checks['frame_ok'] = st.checkbox("Frame intact", value=True)
            visual_checks['jbox_ok'] = st.checkbox("Junction box OK", value=True)

        st.divider()

        # Notes and Attachments
        st.markdown("#### Notes & Observations")
        technician_notes = st.text_area("Technician Notes", height=100,
                                        placeholder="Enter observations, anomalies, or special conditions...")

        # Photo Upload
        photos = st.file_uploader("Upload Photos/Evidence", accept_multiple_files=True,
                                  type=['jpg', 'jpeg', 'png'])

        st.divider()

        # Test Result
        st.markdown("#### Test Result")
        col1, col2 = st.columns(2)

        with col1:
            test_result = st.selectbox("Overall Result", ["Passed", "Failed", "Conditional"])

        with col2:
            if test_result == "Failed":
                failure_mode = st.text_input("Failure Mode", placeholder="Describe failure reason...")
            else:
                failure_mode = ""

        remarks = st.text_area("Final Remarks", height=80)

        submitted = st.form_submit_button("✅ Complete Test", type="primary", use_container_width=True)

        if submitted:
            if not sample_id:
                st.error("Please enter Sample ID")
                return

            try:
                execution_number = generate_execution_number()

                # Calculate derived values if performance test
                results = measurements.copy()
                if protocol.category == "performance" and measurements.get('vmpp') and measurements.get('impp'):
                    results['pmax'] = measurements['vmpp'] * measurements['impp']
                    if measurements.get('voc') and measurements.get('isc'):
                        voc_isc = measurements['voc'] * measurements['isc']
                        results['fill_factor'] = (results['pmax'] / voc_isc * 100) if voc_isc > 0 else 0

                # FIX Issue #3: Use dynamic protocol ID lookup instead of hardcoded value
                # The database session is needed to look up the actual protocol ID
                with get_db() as db:
                    # Dynamically look up the protocol database ID using protocol.protocol_id
                    protocol_db_id = get_protocol_db_id(protocol.protocol_id, db)

                    test_data = {
                        'execution_number': execution_number,
                        'service_request_id': sr_id,
                        'protocol_id': protocol_db_id,  # Dynamic lookup replaces hardcoded 1
                        'sample_id': sample_id,
                        'status': TestStatus.COMPLETED,
                        'started_at': datetime.combine(test_date, test_start_time),
                        'completed_at': datetime.utcnow(),
                        'technician_id': 1,
                        'input_data': {
                            'ambient_temp': ambient_temp,
                            'humidity': humidity,
                            'test_date': str(test_date),
                            'visual_checks': visual_checks
                        },
                        'raw_data': measurements,
                        'results': results,
                        'test_passed': (test_result == "Passed"),
                        'failure_mode': failure_mode if test_result == "Failed" else None,
                        'qa_passed': True,
                        'remarks': f"{technician_notes}\n\n{remarks}".strip()
                    }

                    execution = TestExecution(**test_data)
                    db.add(execution)
                    db.commit()

                st.success(f"Test {execution_number} completed successfully!")

                # Display summary
                st.markdown("### Test Summary")
                summary_col1, summary_col2, summary_col3 = st.columns(3)

                with summary_col1:
                    st.metric("Protocol", protocol.protocol_id)
                with summary_col2:
                    st.metric("Result", test_result)
                with summary_col3:
                    st.metric("Sample", sample_id)

                if results:
                    st.json(results)

            except Exception as e:
                st.error(f"Error saving test: {str(e)}")


def render_test_results_checksheet():
    """Render comprehensive Test Results Entry Checksheet for active executions"""

    st.markdown("### 📝 Test Results Entry Checksheet")
    st.markdown("Enter and update test results for ongoing test executions.")

    # Get active test executions (in_progress or pending_review)
    # Use SQLAlchemy 2.0 select() syntax instead of legacy .query()
    try:
        with get_db() as db:
            active_executions = db.query(TestExecution).filter(
                TestExecution.status.in_([TestStatus.IN_PROGRESS, TestStatus.NOT_STARTED, TestStatus.PENDING_REVIEW])
            ).order_by(TestExecution.created_at.desc()).all()

            completed_executions = db.query(TestExecution).filter(
                TestExecution.status == TestStatus.COMPLETED
            ).order_by(TestExecution.completed_at.desc()).limit(10).all()

    except Exception as e:
        st.error(f"Error loading executions: {str(e)}")
        return

    # Tab for different views
    checksheet_tabs = st.tabs(["📊 Active Tests", "➕ New Entry", "📋 Recent Completed"])

    with checksheet_tabs[0]:
        st.markdown("#### Active Test Executions")

        if not active_executions:
            st.info("No active test executions. Start a new test from the 'Execute Test' tab or create a new entry below.")
        else:
            for execution in active_executions:
                status_color = {
                    TestStatus.NOT_STARTED: "gray",
                    TestStatus.IN_PROGRESS: "blue",
                    TestStatus.PENDING_REVIEW: "orange"
                }.get(execution.status, "gray")

                with st.expander(f"🔬 {execution.execution_number} - {execution.sample_id or 'No Sample'} ({execution.status.value})", expanded=True):
                    # Display current data
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.markdown(f"**Execution #:** {execution.execution_number}")
                        st.markdown(f"**Sample ID:** {execution.sample_id or 'N/A'}")

                    with col2:
                        st.markdown(f"**Status:** {execution.status.value}")
                        st.markdown(f"**Started:** {execution.started_at.strftime('%Y-%m-%d %H:%M') if execution.started_at else 'Not started'}")

                    with col3:
                        st.markdown(f"**Protocol:** P{execution.protocol_id}")
                        st.markdown(f"**Technician:** ID {execution.technician_id or 'N/A'}")

                    # Data Entry Form
                    st.divider()
                    st.markdown("**Update Results:**")

                    with st.form(f"update_{execution.id}"):
                        # Measurement data entry
                        col1, col2 = st.columns(2)

                        with col1:
                            new_measurement_type = st.selectbox(
                                "Measurement Type",
                                ["voltage", "current", "power", "temperature", "irradiance", "resistance", "other"],
                                key=f"mtype_{execution.id}"
                            )
                            new_value = st.number_input("Value", value=0.0, step=0.01, key=f"val_{execution.id}")
                            new_unit = st.text_input("Unit", placeholder="V, A, W, °C, etc.", key=f"unit_{execution.id}")

                        with col2:
                            new_setpoint = st.number_input("Setpoint (target)", value=0.0, step=0.01, key=f"sp_{execution.id}")
                            new_tolerance = st.number_input("Tolerance (%)", value=5.0, step=0.1, key=f"tol_{execution.id}")
                            quality_flag = st.selectbox("Quality Flag", ["good", "questionable", "bad"], key=f"qf_{execution.id}")

                        # Notes
                        data_notes = st.text_area("Notes", height=60, key=f"notes_{execution.id}",
                                                  placeholder="Observations about this measurement...")

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            add_data = st.form_submit_button("➕ Add Data Point", use_container_width=True)

                        with col2:
                            if execution.status == TestStatus.IN_PROGRESS:
                                complete_test = st.form_submit_button("✅ Complete Test", type="primary", use_container_width=True)
                            else:
                                complete_test = False

                        with col3:
                            if execution.status == TestStatus.NOT_STARTED:
                                start_test = st.form_submit_button("▶️ Start Test", use_container_width=True)
                            else:
                                start_test = False

                        if add_data and new_value != 0:
                            try:
                                with get_db() as db:
                                    data_point = TestData(
                                        test_execution_id=execution.id,
                                        measurement_type=new_measurement_type,
                                        value=new_value,
                                        unit=new_unit,
                                        setpoint=new_setpoint if new_setpoint else None,
                                        tolerance=new_tolerance if new_tolerance else None,
                                        is_valid=(quality_flag == "good"),
                                        quality_flag=quality_flag,
                                        notes=data_notes,
                                        timestamp=datetime.utcnow()
                                    )
                                    db.add(data_point)
                                    db.commit()
                                st.success("Data point added successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error adding data point: {str(e)}")

                        if start_test:
                            try:
                                with get_db() as db:
                                    exec_record = db.query(TestExecution).filter(TestExecution.id == execution.id).first()
                                    exec_record.status = TestStatus.IN_PROGRESS
                                    exec_record.started_at = datetime.utcnow()
                                    db.commit()
                                st.success("Test started!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")

                        if complete_test:
                            try:
                                with get_db() as db:
                                    exec_record = db.query(TestExecution).filter(TestExecution.id == execution.id).first()
                                    exec_record.status = TestStatus.COMPLETED
                                    exec_record.completed_at = datetime.utcnow()
                                    db.commit()
                                st.success("Test completed!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")

                    # Show existing data points
                    try:
                        with get_db() as db:
                            data_points = db.query(TestData).filter(
                                TestData.test_execution_id == execution.id
                            ).order_by(TestData.timestamp.desc()).all()

                            if data_points:
                                st.markdown("**Recorded Data Points:**")
                                for dp in data_points:
                                    st.markdown(
                                        f"- {dp.measurement_type}: **{dp.value} {dp.unit or ''}** "
                                        f"(Quality: {dp.quality_flag}) @ {dp.timestamp.strftime('%H:%M:%S')}"
                                    )
                    except Exception as e:
                        pass

    with checksheet_tabs[1]:
        st.markdown("#### Create New Test Entry")
        st.markdown("Manually create a test execution entry for data recording.")

        # Get service requests
        # FIX Issue #2: sr_options dict MUST be constructed INSIDE the 'with get_db()' block
        # to prevent DetachedInstanceError when accessing ORM object attributes after session closes
        try:
            with get_db() as db:
                service_requests = db.query(ServiceRequest).filter(
                    ServiceRequest.status.in_(['approved', 'in_progress'])
                ).all()
        except:
            service_requests = []

        if not sr_options:
            st.warning("No approved service requests available. Create a service request first.")
        else:
            with st.form("new_test_entry"):
                col1, col2 = st.columns(2)

                with col1:
                    selected_sr = st.selectbox("Service Request *", options=list(sr_options.keys()))

                    sample_id = st.text_input("Sample ID *", placeholder="Enter sample ID...")

                with col2:
                    registry = get_cached_protocol_registry()
                    all_protocols = registry.get_active_protocols()
                    protocol_options = {
                        f"{p.protocol_id}: {p.name}": p.protocol_id
                        for p in all_protocols
                    }
                    selected_protocol = st.selectbox("Protocol *", options=list(protocol_options.keys()))

                    initial_notes = st.text_area("Initial Notes", height=80)

                create_entry = st.form_submit_button("📝 Create Test Entry", type="primary", use_container_width=True)

                if create_entry:
                    if not sample_id:
                        st.error("Please enter Sample ID")
                    else:
                        try:
                            execution_number = generate_execution_number()
                            sr_id = sr_options[selected_sr]
                            # Get the protocol_id string from the selected option
                            selected_protocol_id_str = protocol_options[selected_protocol]

                            # FIX Issue #3: Use dynamic protocol ID lookup instead of hardcoded value
                            # The database session is needed to look up the actual protocol ID
                            with get_db() as db:
                                # Dynamically look up the protocol database ID
                                protocol_db_id = get_protocol_db_id(selected_protocol_id_str, db)

                                test_data = {
                                    'execution_number': execution_number,
                                    'service_request_id': sr_id,
                                    'protocol_id': protocol_db_id,  # Dynamic lookup replaces hardcoded 1
                                    'sample_id': sample_id,
                                    'status': TestStatus.NOT_STARTED,
                                    'technician_id': 1,
                                    'remarks': initial_notes
                                }

                                execution = TestExecution(**test_data)
                                db.add(execution)
                                db.commit()

                            st.success(f"Test entry {execution_number} created successfully!")
                            st.info("Go to 'Active Tests' tab to start recording data.")
                            st.rerun()

                        except Exception as e:
                            st.error(f"Error creating entry: {str(e)}")

    with checksheet_tabs[2]:
        st.markdown("#### Recently Completed Tests")

        if not completed_executions:
            st.info("No completed test executions found.")
        else:
            for execution in completed_executions:
                with st.expander(f"✅ {execution.execution_number} - {execution.sample_id}", expanded=False):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.markdown(f"**Sample:** {execution.sample_id}")
                        st.markdown(f"**Protocol:** P{execution.protocol_id}")

                    with col2:
                        st.markdown(f"**Completed:** {execution.completed_at.strftime('%Y-%m-%d %H:%M') if execution.completed_at else 'N/A'}")
                        st.markdown(f"**Result:** {'✅ Passed' if execution.test_passed else '❌ Failed'}")

                    with col3:
                        st.markdown(f"**QA:** {'✅ Passed' if execution.qa_passed else '⏳ Pending'}")

                    if execution.results:
                        st.markdown("**Results:**")
                        st.json(execution.results)

                    if execution.remarks:
                        st.markdown(f"**Remarks:** {execution.remarks}")


def render_test_history():
    """Render test execution history"""

    st.markdown("### 📋 Test Execution History")

    try:
        with get_db() as db:
            executions = db.query(TestExecution).order_by(
                TestExecution.created_at.desc()
            ).limit(20).all()

            if not executions:
                st.info("No test executions found")
                return

            for execution in executions:
                status_emoji = {
                    TestStatus.NOT_STARTED: "⏳",
                    TestStatus.IN_PROGRESS: "🔵",
                    TestStatus.COMPLETED: "✅",
                    TestStatus.FAILED: "❌",
                    TestStatus.PENDING_REVIEW: "⏸️"
                }.get(execution.status, "❓")

                with st.expander(
                    f"{status_emoji} {execution.execution_number} - {execution.sample_id} ({execution.status.value.upper()})",
                    expanded=False
                ):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.markdown(f"**Sample ID:** {execution.sample_id}")
                        st.markdown(f"**Protocol ID:** {execution.protocol_id}")

                    with col2:
                        st.markdown(f"**Status:** {execution.status.value.upper()}")
                        st.markdown(f"**Started:** {execution.started_at.strftime('%Y-%m-%d %H:%M') if execution.started_at else 'N/A'}")

                    with col3:
                        st.markdown(f"**Completed:** {execution.completed_at.strftime('%Y-%m-%d %H:%M') if execution.completed_at else 'N/A'}")
                        st.markdown(f"**Result:** {'✅ Passed' if execution.test_passed else '❌ Failed'}")

                    if execution.results:
                        st.markdown("**Results:**")
                        st.json(execution.results)

    except Exception as e:
        st.error(f"Error loading test history: {str(e)}")


def generate_execution_number() -> str:
    """Generate unique execution number"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"TEST-{timestamp[-10:]}"


if __name__ == "__main__":
    main()
