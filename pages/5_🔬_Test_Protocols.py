"""
Test Protocols Module
====================
Protocol selector and execution framework.
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
from database.models import TestExecution, TestProtocol, ServiceRequest, TestStatus

# Page configuration
setup_page_config(page_title="Test Protocols", page_icon="🔬")

# Render navigation
render_header("Test Protocols", "Select and execute testing protocols")
render_sidebar_navigation()


def main():
    """Main test protocols page"""

    tabs = st.tabs(["🔬 Protocol Selection", "📊 Execute Test", "📋 Test History"])

    with tabs[0]:
        render_protocol_selector()

    with tabs[1]:
        render_test_execution()

    with tabs[2]:
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

    # Link to service request
    with get_db() as db:
        service_requests = db.query(ServiceRequest).filter(
            ServiceRequest.status.in_(['approved', 'in_progress'])
        ).all()

    if not service_requests:
        st.warning("No approved service requests available. Create a service request first.")
        return

    sr_options = {
        f"{sr.request_number} - {sr.client_name}": sr.id
        for sr in service_requests
    }

    selected_sr = st.selectbox("Link to Service Request", options=list(sr_options.keys()))
    sr_id = sr_options[selected_sr]

    # Sample information
    sample_id = st.text_input("Sample ID", placeholder="Enter sample ID from inspection...")

    # Execute protocol based on type
    if protocol_id == "P1":
        render_p1_iv_performance(protocol, sr_id, sample_id)
    elif protocol_id == "P2":
        render_p2_pv_analysis(protocol, sr_id, sample_id)
    elif protocol_id in ["P13", "P28", "P40", "P48"]:
        render_generic_protocol(protocol, sr_id, sample_id)
    else:
        st.info(f"Execution interface for {protocol_id} is under development")
        st.markdown("**This is a placeholder for the protocol execution interface.**")


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

                test_data = {
                    'execution_number': execution_number,
                    'service_request_id': sr_id,
                    'protocol_id': 1,  # Assuming P1 is ID 1
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

                with get_db() as db:
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
    """Render generic protocol execution template"""

    st.markdown(f"### {protocol.name}")
    st.info("Generic protocol execution interface")

    with st.form(f"{protocol.protocol_id}_execution"):
        st.text_area("Test Notes", height=150)

        test_passed = st.selectbox("Test Result", ["Passed", "Failed"])

        submitted = st.form_submit_button("✅ Complete Test", type="primary")

        if submitted:
            st.success(f"Test {protocol.protocol_id} completed (placeholder)")


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
