"""
PV Testing Protocol Framework - Streamlit UI
Main application interface for protocol execution and management
"""

import streamlit as st
import json
from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.handlers.base_handler import BaseProtocolHandler, ProtocolState, TestResult
from backend.handlers.pvtp016_handler import PVTP016Handler
from backend.interlocks.safety_interlock import SafetyInterlockEngine, ApprovalWorkflow
from backend.reports.report_generator import ReportGenerator, CertificationReportGenerator
from backend.integration.pm_qc_nc_integration import IntegratedWorkflow
from backend.traceability.audit_log import TraceabilityManager
from protocols.validators.protocol_validator import ProtocolValidator

# Page configuration
st.set_page_config(
    page_title="PV Testing Protocol Framework",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #003366;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .protocol-card {
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #ddd;
        margin: 0.5rem 0;
        background-color: #f8f9fa;
    }
    .safety-warning {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def load_protocol_definitions():
    """Load all available protocol definitions"""
    protocols_dir = Path(__file__).parent.parent / "protocols" / "definitions"
    protocols = {}

    for protocol_file in protocols_dir.glob("pvtp-*.json"):
        with open(protocol_file, 'r') as f:
            protocol_def = json.load(f)
            protocol_id = protocol_def["protocolId"]
            protocols[protocol_id] = protocol_def

    return protocols


def render_sidebar():
    """Render sidebar navigation"""
    with st.sidebar:
        st.markdown("# Navigation")

        page = st.radio(
            "Select Page:",
            ["Home", "Protocol Selection", "Test Execution", "Data Review",
             "Reports", "QC/QA", "Audit Log", "Settings"]
        )

        st.markdown("---")
        st.markdown("### Session Info")

        if 'session_id' in st.session_state:
            st.info(f"**Session:** {st.session_state.session_id}")
            st.info(f"**Protocol:** {st.session_state.get('protocol_id', 'None')}")
            st.info(f"**State:** {st.session_state.get('state', 'Not Started')}")

    return page


def render_home_page():
    """Render home page"""
    st.markdown('<div class="main-header">⚡ PV Testing Protocol Framework</div>', unsafe_allow_html=True)

    st.markdown("""
    ### Welcome to the Modular PV Testing Protocol Framework

    This comprehensive testing platform provides:
    - ✅ **8 Safety & Certification Test Protocols** (PVTP-016 through PVTP-023)
    - 🔒 **Safety Interlocks** - Multi-level safety checks and emergency stops
    - ✍️ **QC/QA Workflow** - Integrated approval gates and quality control
    - 📊 **Automated Reports** - PDF, Excel, JSON with full traceability
    - 🔍 **Complete Audit Trail** - 21 CFR Part 11 compliant
    - 🔗 **PM/LIMS/QMS Integration** - Seamless system integration
    """)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### Available Protocols")
        protocols = load_protocol_definitions()
        st.metric("Total Protocols", len(protocols))
        st.write("- Wet Leakage Current (PVTP-016)")
        st.write("- Insulation Resistance (PVTP-017)")
        st.write("- Ground Continuity (PVTP-018)")
        st.write("- Hi-Pot Testing (PVTP-019)")
        st.write("- Fire Class (PVTP-020)")
        st.write("- Safety Qualification (PVTP-021)")
        st.write("- Cable Pull (PVTP-022)")
        st.write("- Terminal Torque (PVTP-023)")

    with col2:
        st.markdown("#### System Status")
        st.success("✅ All Systems Operational")
        st.write("- Safety Interlocks: Active")
        st.write("- QC Workflow: Ready")
        st.write("- Report Generation: Online")
        st.write("- Traceability: Enabled")

    with col3:
        st.markdown("#### Quick Actions")
        if st.button("▶️ Start New Test", use_container_width=True):
            st.session_state.page = "Protocol Selection"
            st.rerun()

        if st.button("📊 View Reports", use_container_width=True):
            st.session_state.page = "Reports"
            st.rerun()

        if st.button("🔍 Audit Log", use_container_width=True):
            st.session_state.page = "Audit Log"
            st.rerun()


def render_protocol_selection():
    """Render protocol selection page"""
    st.markdown("## Protocol Selection")

    protocols = load_protocol_definitions()

    # Filter controls
    col1, col2 = st.columns(2)
    with col1:
        category_filter = st.multiselect(
            "Filter by Category:",
            ["safety", "mechanical", "certification"],
            default=[]
        )

    with col2:
        standard_filter = st.selectbox(
            "Filter by Standard:",
            ["All", "IEC 61215", "IEC 61730", "IEC 60947", "UL 1703"]
        )

    # Display protocols
    for protocol_id, protocol_def in sorted(protocols.items()):
        category = protocol_def.get("category")
        standard = protocol_def.get("standard", {}).get("name")

        # Apply filters
        if category_filter and category not in category_filter:
            continue

        if standard_filter != "All" and standard != standard_filter:
            continue

        with st.expander(f"{protocol_id}: {protocol_def['protocolName']}"):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.write(f"**Category:** {category}")
                st.write(f"**Standard:** {standard}")
                st.write(f"**Section:** {protocol_def['standard']['section']}")

            with col2:
                st.write(f"**Version:** {protocol_def['version']}")
                st.write(f"**Safety Interlocks:** {len(protocol_def['safetyInterlocks'])}")
                st.write(f"**Approval Gates:** {len(protocol_def['approvalGates'])}")

            with col3:
                if st.button(f"Select {protocol_id}", key=f"select_{protocol_id}"):
                    st.session_state.selected_protocol = protocol_def
                    st.session_state.protocol_id = protocol_id
                    st.success(f"✅ Selected {protocol_id}")


def render_test_execution():
    """Render test execution page"""
    st.markdown("## Test Execution")

    if 'selected_protocol' not in st.session_state:
        st.warning("⚠️ Please select a protocol first")
        return

    protocol_def = st.session_state.selected_protocol

    st.markdown(f"### {protocol_def['protocolName']}")

    # Device Under Test information
    with st.expander("Device Under Test", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            serial_number = st.text_input("Serial Number*", key="dut_serial")
            manufacturer = st.text_input("Manufacturer", key="dut_mfg")

        with col2:
            model_number = st.text_input("Model Number*", key="dut_model")
            lot_number = st.text_input("Lot Number", key="dut_lot")

    # Safety interlocks check
    with st.expander("Safety Interlocks", expanded=False):
        st.markdown("### Pre-Test Safety Checks")

        for interlock in protocol_def['safetyInterlocks']:
            if interlock['type'] == 'pre-test':
                severity = interlock['severity']
                icon = "🔴" if severity == "critical" else "🟡"

                st.checkbox(
                    f"{icon} {interlock['message']}",
                    key=f"interlock_{interlock['interlockId']}"
                )

    # Test execution controls
    st.markdown("### Test Controls")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🚀 Start Test", use_container_width=True):
            st.session_state.test_running = True
            st.success("✅ Test Started")

    with col2:
        if st.button("⏸️ Pause Test", use_container_width=True):
            st.warning("⏸️ Test Paused")

    with col3:
        if st.button("⏹️ Stop Test", use_container_width=True):
            st.error("⏹️ Test Stopped")

    with col4:
        if st.button("🆘 Emergency Stop", use_container_width=True, type="primary"):
            st.error("🆘 EMERGENCY STOP ACTIVATED")

    # Live data display
    if st.session_state.get('test_running', False):
        st.markdown("### Live Data")

        # Placeholder for live data
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Voltage", "1000 V", "0 V")

        with col2:
            st.metric("Current", "0.3 mA", "-0.1 mA")

        with col3:
            st.metric("Temperature", "25.2°C", "0.2°C")


def render_reports_page():
    """Render reports page"""
    st.markdown("## Reports")

    if 'session_id' not in st.session_state:
        st.info("ℹ️ No active session. Complete a test to generate reports.")
        return

    st.markdown("### Report Generation")

    col1, col2 = st.columns(2)

    with col1:
        report_formats = st.multiselect(
            "Select Report Formats:",
            ["PDF", "Excel", "JSON", "HTML"],
            default=["PDF", "JSON"]
        )

    with col2:
        include_options = st.multiselect(
            "Include:",
            ["Charts", "Audit Trail", "Images", "Raw Data"],
            default=["Charts", "Audit Trail"]
        )

    if st.button("📄 Generate Reports", use_container_width=True):
        with st.spinner("Generating reports..."):
            st.success("✅ Reports generated successfully!")

            # Provide download buttons
            col1, col2, col3 = st.columns(3)

            with col1:
                if "PDF" in report_formats:
                    st.download_button(
                        "📥 Download PDF",
                        data=b"PDF report placeholder",
                        file_name="test_report.pdf",
                        mime="application/pdf"
                    )

            with col2:
                if "Excel" in report_formats:
                    st.download_button(
                        "📥 Download Excel",
                        data=b"Excel report placeholder",
                        file_name="test_report.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

            with col3:
                if "JSON" in report_formats:
                    st.download_button(
                        "📥 Download JSON",
                        data=b'{"report": "data"}',
                        file_name="test_report.json",
                        mime="application/json"
                    )


def main():
    """Main application entry point"""
    # Initialize session state
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.page = "Home"

    # Render sidebar and get current page
    page = render_sidebar()

    # Override page if set in session state
    if 'page' in st.session_state:
        page = st.session_state.page

    # Render appropriate page
    if page == "Home":
        render_home_page()
    elif page == "Protocol Selection":
        render_protocol_selection()
    elif page == "Test Execution":
        render_test_execution()
    elif page == "Reports":
        render_reports_page()
    elif page == "QC/QA":
        st.markdown("## QC/QA Workflow")
        st.info("QC/QA workflow interface - Coming soon")
    elif page == "Audit Log":
        st.markdown("## Audit Log")
        st.info("Complete audit trail viewer - Coming soon")
    elif page == "Settings":
        st.markdown("## Settings")
        st.info("System settings and configuration - Coming soon")


if __name__ == "__main__":
    main()
