"""
Traceability Viewer
Complete traceability chain for PV testing workflow
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import json
import plotly.graph_objects as go
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.database.db_manager import DatabaseManager

st.set_page_config(
    page_title="Traceability",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
if 'db' not in st.session_state:
    st.session_state.db = DatabaseManager()

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_all_entities_by_type(entity_type: str) -> List[Dict]:
    """Get all entities of a specific type"""
    db = st.session_state.db

    if entity_type == 'request':
        query = "SELECT request_id, customer_name, project_name, status, requested_date FROM service_requests ORDER BY requested_date DESC"
        return db.execute_query(query)
    elif entity_type == 'inspection':
        query = "SELECT inspection_id, request_id, sample_id, sample_type, inspection_date FROM incoming_inspections ORDER BY inspection_date DESC"
        return db.execute_query(query)
    elif entity_type == 'execution':
        query = "SELECT execution_id, protocol_name, request_id, status, created_at FROM protocol_executions ORDER BY created_at DESC"
        return db.execute_query(query)
    elif entity_type == 'report':
        query = "SELECT report_id, execution_id, report_type, report_title, generated_date FROM reports ORDER BY generated_date DESC"
        return db.execute_query(query)
    else:
        return []

def build_traceability_chain(entity_type: str, entity_id: str) -> Dict:
    """Build complete traceability chain"""
    db = st.session_state.db
    chain = {
        'entity_type': entity_type,
        'entity_id': entity_id,
        'request': None,
        'inspection': None,
        'equipment': None,
        'execution': None,
        'measurements': [],
        'reports': [],
        'qc_records': [],
        'audit_trail': []
    }

    try:
        if entity_type == 'execution':
            # Get execution
            exec_query = "SELECT * FROM protocol_executions WHERE execution_id = ?"
            execution = db.execute_query(exec_query, (entity_id,))
            if execution:
                chain['execution'] = execution[0]

                # Get linked request
                if execution[0].get('request_id'):
                    req_query = "SELECT * FROM service_requests WHERE request_id = ?"
                    request = db.execute_query(req_query, (execution[0]['request_id'],))
                    if request:
                        chain['request'] = request[0]

                # Get linked inspection
                if execution[0].get('inspection_id'):
                    insp_query = "SELECT * FROM incoming_inspections WHERE inspection_id = ?"
                    inspection = db.execute_query(insp_query, (execution[0]['inspection_id'],))
                    if inspection:
                        chain['inspection'] = inspection[0]

                # Get equipment
                if execution[0].get('equipment_id'):
                    eq_query = "SELECT * FROM equipment_planning WHERE equipment_id = ?"
                    equipment = db.execute_query(eq_query, (execution[0]['equipment_id'],))
                    if equipment:
                        chain['equipment'] = equipment[0]

                # Get measurements
                meas_query = "SELECT * FROM measurements WHERE execution_id = ? ORDER BY timestamp"
                chain['measurements'] = db.execute_query(meas_query, (entity_id,))

                # Get reports
                rep_query = "SELECT * FROM reports WHERE execution_id = ?"
                chain['reports'] = db.execute_query(rep_query, (entity_id,))

                # Get QC records
                qc_query = "SELECT * FROM qc_records WHERE execution_id = ?"
                chain['qc_records'] = db.execute_query(qc_query, (entity_id,))

                # Get audit trail
                audit_query = "SELECT * FROM audit_trail WHERE record_id = ? ORDER BY timestamp DESC"
                chain['audit_trail'] = db.execute_query(audit_query, (entity_id,))

        elif entity_type == 'request':
            # Get request
            req_query = "SELECT * FROM service_requests WHERE request_id = ?"
            request = db.execute_query(req_query, (entity_id,))
            if request:
                chain['request'] = request[0]

                # Get linked inspections
                insp_query = "SELECT * FROM incoming_inspections WHERE request_id = ?"
                inspections = db.execute_query(insp_query, (entity_id,))
                if inspections:
                    chain['inspection'] = inspections[0]  # Take first

                # Get linked executions
                exec_query = "SELECT * FROM protocol_executions WHERE request_id = ?"
                chain['executions'] = db.execute_query(exec_query, (entity_id,))

        elif entity_type == 'inspection':
            # Get inspection
            insp_query = "SELECT * FROM incoming_inspections WHERE inspection_id = ?"
            inspection = db.execute_query(insp_query, (entity_id,))
            if inspection:
                chain['inspection'] = inspection[0]

                # Get linked request
                if inspection[0].get('request_id'):
                    req_query = "SELECT * FROM service_requests WHERE request_id = ?"
                    request = db.execute_query(req_query, (inspection[0]['request_id'],))
                    if request:
                        chain['request'] = request[0]

                # Get linked executions
                exec_query = "SELECT * FROM protocol_executions WHERE inspection_id = ?"
                chain['executions'] = db.execute_query(exec_query, (entity_id,))

        elif entity_type == 'report':
            # Get report
            rep_query = "SELECT * FROM reports WHERE report_id = ?"
            report = db.execute_query(rep_query, (entity_id,))
            if report:
                chain['report'] = report[0]

                # Get linked execution
                if report[0].get('execution_id'):
                    exec_query = "SELECT * FROM protocol_executions WHERE execution_id = ?"
                    execution = db.execute_query(exec_query, (report[0]['execution_id'],))
                    if execution:
                        chain['execution'] = execution[0]

                        # Continue chain backwards
                        if execution[0].get('request_id'):
                            req_query = "SELECT * FROM service_requests WHERE request_id = ?"
                            request = db.execute_query(req_query, (execution[0]['request_id'],))
                            if request:
                                chain['request'] = request[0]

    except Exception as e:
        st.error(f"Error building traceability chain: {e}")

    return chain

def create_timeline_visualization(chain: Dict) -> go.Figure:
    """Create timeline visualization of traceability chain"""
    events = []

    # Add request
    if chain.get('request'):
        req = chain['request']
        events.append({
            'date': req.get('requested_date', req.get('created_at')),
            'event': 'Service Request',
            'id': req['request_id'],
            'details': f"Customer: {req.get('customer_name', 'N/A')}"
        })

    # Add inspection
    if chain.get('inspection'):
        insp = chain['inspection']
        events.append({
            'date': insp.get('inspection_date', insp.get('created_at')),
            'event': 'Incoming Inspection',
            'id': insp['inspection_id'],
            'details': f"Sample: {insp.get('sample_id', 'N/A')}"
        })

    # Add execution
    if chain.get('execution'):
        exe = chain['execution']
        events.append({
            'date': exe.get('start_date', exe.get('created_at')),
            'event': 'Protocol Execution',
            'id': exe['execution_id'],
            'details': exe.get('protocol_name', 'N/A')
        })

    # Add report
    if chain.get('report'):
        rep = chain['report']
        events.append({
            'date': rep.get('generated_date', rep.get('created_at')),
            'event': 'Report Generated',
            'id': rep['report_id'],
            'details': rep.get('report_title', 'N/A')
        })

    # Sort by date
    events.sort(key=lambda x: x['date'] if x['date'] else '')

    if not events:
        return None

    # Create figure
    fig = go.Figure()

    # Add timeline
    fig.add_trace(go.Scatter(
        x=[e['date'] for e in events],
        y=[i for i in range(len(events))],
        mode='markers+lines+text',
        text=[f"{e['event']}<br>{e['id']}" for e in events],
        textposition="top center",
        marker=dict(size=15, color='#636EFA'),
        line=dict(width=2, color='#636EFA'),
        hovertemplate='<b>%{text}</b><br>%{x}<extra></extra>'
    ))

    fig.update_layout(
        height=300,
        showlegend=False,
        xaxis_title="Date/Time",
        yaxis_title="Workflow Stage",
        yaxis=dict(
            tickmode='array',
            tickvals=[i for i in range(len(events))],
            ticktext=[e['event'] for e in events]
        ),
        margin=dict(t=50, b=50, l=150, r=50)
    )

    return fig

def export_traceability_report(chain: Dict) -> str:
    """Export traceability chain as formatted text"""
    report = []
    report.append("=" * 80)
    report.append("TRACEABILITY REPORT")
    report.append("=" * 80)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Entity Type: {chain['entity_type'].upper()}")
    report.append(f"Entity ID: {chain['entity_id']}")
    report.append("")

    # Request section
    if chain.get('request'):
        req = chain['request']
        report.append("-" * 80)
        report.append("SERVICE REQUEST")
        report.append("-" * 80)
        report.append(f"Request ID: {req['request_id']}")
        report.append(f"Customer: {req.get('customer_name', 'N/A')}")
        report.append(f"Project: {req.get('project_name', 'N/A')}")
        report.append(f"Status: {req.get('status', 'N/A')}")
        report.append(f"Date: {req.get('requested_date', 'N/A')}")
        report.append("")

    # Inspection section
    if chain.get('inspection'):
        insp = chain['inspection']
        report.append("-" * 80)
        report.append("INCOMING INSPECTION")
        report.append("-" * 80)
        report.append(f"Inspection ID: {insp['inspection_id']}")
        report.append(f"Sample ID: {insp.get('sample_id', 'N/A')}")
        report.append(f"Sample Type: {insp.get('sample_type', 'N/A')}")
        report.append(f"Manufacturer: {insp.get('manufacturer', 'N/A')}")
        report.append(f"Condition: {insp.get('condition', 'N/A')}")
        report.append(f"Date: {insp.get('inspection_date', 'N/A')}")
        report.append("")

    # Execution section
    if chain.get('execution'):
        exe = chain['execution']
        report.append("-" * 80)
        report.append("PROTOCOL EXECUTION")
        report.append("-" * 80)
        report.append(f"Execution ID: {exe['execution_id']}")
        report.append(f"Protocol: {exe.get('protocol_name', 'N/A')}")
        report.append(f"Version: {exe.get('protocol_version', 'N/A')}")
        report.append(f"Status: {exe.get('status', 'N/A')}")
        report.append(f"Result: {exe.get('test_result', 'N/A')}")
        report.append(f"Start: {exe.get('start_date', 'N/A')}")
        report.append(f"End: {exe.get('end_date', 'N/A')}")
        report.append("")

    # Measurements section
    if chain.get('measurements'):
        report.append("-" * 80)
        report.append(f"MEASUREMENTS ({len(chain['measurements'])} records)")
        report.append("-" * 80)
        for meas in chain['measurements'][:10]:  # Limit to first 10
            report.append(f"  Type: {meas.get('measurement_type', 'N/A')} | Time: {meas.get('timestamp', 'N/A')}")
        if len(chain['measurements']) > 10:
            report.append(f"  ... and {len(chain['measurements']) - 10} more")
        report.append("")

    # Reports section
    if chain.get('reports'):
        report.append("-" * 80)
        report.append(f"REPORTS ({len(chain['reports'])} documents)")
        report.append("-" * 80)
        for rep in chain['reports']:
            report.append(f"  {rep.get('report_id')}: {rep.get('report_title', 'N/A')}")
        report.append("")

    report.append("=" * 80)

    return "\n".join(report)

# ============================================
# PAGE CONTENT
# ============================================

st.title("🔗 Traceability Viewer")
st.markdown("### Complete Workflow Traceability Chain")
st.markdown("---")

# ============================================
# ENTITY SELECTION
# ============================================

st.subheader("🔍 Select Entity for Traceability")

col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    entity_type = st.selectbox(
        "Entity Type",
        options=['execution', 'request', 'inspection', 'report'],
        format_func=lambda x: {
            'execution': 'Protocol Execution',
            'request': 'Service Request',
            'inspection': 'Incoming Inspection',
            'report': 'Report'
        }[x]
    )

with col2:
    # Get entities of selected type
    entities = get_all_entities_by_type(entity_type)

    if entities:
        # Create display options
        if entity_type == 'execution':
            options = {f"{e['execution_id']} - {e['protocol_name']}": e['execution_id'] for e in entities}
        elif entity_type == 'request':
            options = {f"{e['request_id']} - {e['customer_name']} ({e['project_name']})": e['request_id'] for e in entities}
        elif entity_type == 'inspection':
            options = {f"{e['inspection_id']} - Sample: {e['sample_id']}": e['inspection_id'] for e in entities}
        elif entity_type == 'report':
            options = {f"{e['report_id']} - {e.get('report_title', 'N/A')}": e['report_id'] for e in entities}
        else:
            options = {}

        selected_display = st.selectbox("Select Entity", options=list(options.keys()))
        entity_id = options[selected_display]
    else:
        st.warning(f"No {entity_type}s found in database")
        entity_id = None

with col3:
    st.write("")
    st.write("")
    trace_button = st.button("🔗 View Traceability", use_container_width=True)

# ============================================
# TRACEABILITY CHAIN DISPLAY
# ============================================

if entity_id and trace_button:
    st.markdown("---")

    with st.spinner("Building traceability chain..."):
        chain = build_traceability_chain(entity_type, entity_id)

    # ============================================
    # TIMELINE VISUALIZATION
    # ============================================

    st.subheader("📅 Traceability Timeline")

    timeline_fig = create_timeline_visualization(chain)
    if timeline_fig:
        st.plotly_chart(timeline_fig, use_container_width=True)
    else:
        st.info("No timeline data available")

    st.markdown("---")

    # ============================================
    # DETAILED CHAIN VIEW
    # ============================================

    st.subheader("🔗 Complete Traceability Chain")

    # Create workflow diagram
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("#### 📝 Service Request")
        if chain.get('request'):
            req = chain['request']
            st.success(f"**{req['request_id']}**")
            st.write(f"**Customer:** {req.get('customer_name', 'N/A')}")
            st.write(f"**Project:** {req.get('project_name', 'N/A')}")
            st.write(f"**Status:** {req.get('status', 'N/A')}")
            st.caption(f"Date: {req.get('requested_date', 'N/A')[:10]}")
        else:
            st.info("No request linked")

    with col2:
        st.markdown("#### 🔍 Inspection")
        if chain.get('inspection'):
            insp = chain['inspection']
            st.success(f"**{insp['inspection_id']}**")
            st.write(f"**Sample:** {insp.get('sample_id', 'N/A')}")
            st.write(f"**Type:** {insp.get('sample_type', 'N/A')}")
            st.write(f"**Condition:** {insp.get('condition', 'N/A')}")
            st.caption(f"Date: {insp.get('inspection_date', 'N/A')[:10]}")
        else:
            st.info("No inspection linked")

    with col3:
        st.markdown("#### ⚙️ Execution")
        if chain.get('execution'):
            exe = chain['execution']
            st.success(f"**{exe['execution_id']}**")
            st.write(f"**Protocol:** {exe.get('protocol_name', 'N/A')[:30]}")
            st.write(f"**Status:** {exe.get('status', 'N/A')}")
            st.write(f"**Result:** {exe.get('test_result', 'N/A')}")
            st.caption(f"Date: {exe.get('created_at', 'N/A')[:10]}")
        else:
            st.info("No execution linked")

    with col4:
        st.markdown("#### 📄 Reports")
        if chain.get('reports') and len(chain['reports']) > 0:
            st.success(f"**{len(chain['reports'])} Report(s)**")
            for rep in chain['reports']:
                st.write(f"- {rep.get('report_type', 'N/A')}")
        else:
            st.info("No reports generated")

    st.markdown("---")

    # ============================================
    # DETAILED DATA TABS
    # ============================================

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Details",
        "📊 Measurements",
        "✅ QC Records",
        "📝 Audit Trail",
        "📄 Export"
    ])

    # Tab 1: Details
    with tab1:
        st.subheader("Detailed Information")

        if chain.get('execution'):
            with st.expander("⚙️ Protocol Execution Details", expanded=True):
                exe = chain['execution']
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Execution ID:** {exe.get('execution_id')}")
                    st.write(f"**Protocol:** {exe.get('protocol_name')}")
                    st.write(f"**Version:** {exe.get('protocol_version')}")
                    st.write(f"**Status:** {exe.get('status')}")
                    st.write(f"**Result:** {exe.get('test_result')}")

                with col2:
                    st.write(f"**Start Date:** {exe.get('start_date', 'N/A')}")
                    st.write(f"**End Date:** {exe.get('end_date', 'N/A')}")
                    st.write(f"**Duration:** {exe.get('duration_hours', 'N/A')} hours")
                    st.write(f"**Operator ID:** {exe.get('operator_id', 'N/A')}")
                    st.write(f"**Reviewer ID:** {exe.get('reviewer_id', 'N/A')}")

                # Protocol inputs
                if exe.get('protocol_inputs'):
                    st.markdown("**Protocol Inputs:**")
                    try:
                        inputs = json.loads(exe['protocol_inputs']) if isinstance(exe['protocol_inputs'], str) else exe['protocol_inputs']
                        st.json(inputs)
                    except:
                        st.write(exe['protocol_inputs'])

        if chain.get('equipment'):
            with st.expander("🔧 Equipment Details"):
                eq = chain['equipment']
                st.write(f"**Equipment ID:** {eq.get('equipment_id')}")
                st.write(f"**Equipment Name:** {eq.get('equipment_name')}")
                st.write(f"**Type:** {eq.get('equipment_type')}")
                st.write(f"**Location:** {eq.get('location')}")
                st.write(f"**Calibration Status:** {eq.get('calibration_status')}")
                st.write(f"**Calibration Due:** {eq.get('calibration_due_date', 'N/A')}")

    # Tab 2: Measurements
    with tab2:
        st.subheader("Measurement Data")

        if chain.get('measurements') and len(chain['measurements']) > 0:
            st.write(f"**Total Measurements:** {len(chain['measurements'])}")

            for idx, meas in enumerate(chain['measurements'], 1):
                with st.expander(f"Measurement {idx}: {meas.get('measurement_type', 'N/A')}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Type:** {meas.get('measurement_type')}")
                        st.write(f"**Sequence:** {meas.get('sequence_number', 'N/A')}")
                        st.write(f"**Unit:** {meas.get('unit', 'N/A')}")
                        st.write(f"**Timestamp:** {meas.get('timestamp')}")

                    with col2:
                        st.write(f"**Equipment:** {meas.get('equipment_used', 'N/A')}")
                        st.write(f"**QC Status:** {meas.get('qc_status', 'N/A')}")
                        st.write(f"**Operator ID:** {meas.get('operator_id', 'N/A')}")

                    # Display measurement data
                    if meas.get('data'):
                        st.markdown("**Data:**")
                        try:
                            data = json.loads(meas['data']) if isinstance(meas['data'], str) else meas['data']
                            st.json(data)
                        except:
                            st.write(meas['data'])
        else:
            st.info("No measurements recorded")

    # Tab 3: QC Records
    with tab3:
        st.subheader("Quality Control Records")

        if chain.get('qc_records') and len(chain['qc_records']) > 0:
            st.write(f"**Total QC Records:** {len(chain['qc_records'])}")

            for qc in chain['qc_records']:
                with st.expander(f"{qc.get('checkpoint_name', 'QC Checkpoint')} - {qc.get('status', 'N/A')}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Checkpoint ID:** {qc.get('checkpoint_id')}")
                        st.write(f"**Type:** {qc.get('checkpoint_type')}")
                        st.write(f"**Status:** {qc.get('status')}")

                    with col2:
                        st.write(f"**Checked By:** {qc.get('checked_by')}")
                        st.write(f"**Date:** {qc.get('checked_date')}")
                        st.write(f"**Verified:** {qc.get('verification_status', 'N/A')}")

                    if qc.get('findings'):
                        st.markdown("**Findings:**")
                        st.write(qc['findings'])

                    if qc.get('corrective_actions'):
                        st.markdown("**Corrective Actions:**")
                        st.write(qc['corrective_actions'])
        else:
            st.info("No QC records found")

    # Tab 4: Audit Trail
    with tab4:
        st.subheader("Audit Trail")

        if chain.get('audit_trail') and len(chain['audit_trail']) > 0:
            st.write(f"**Total Audit Entries:** {len(chain['audit_trail'])}")

            for audit in chain['audit_trail']:
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.write(f"**Action:** {audit.get('action')}")

                with col2:
                    st.write(f"**User ID:** {audit.get('user_id')}")

                with col3:
                    st.write(f"**Table:** {audit.get('table_name')}")

                with col4:
                    st.write(f"**Time:** {audit.get('timestamp', 'N/A')[:19]}")

                if audit.get('new_values'):
                    with st.expander("View Changes"):
                        try:
                            changes = json.loads(audit['new_values']) if isinstance(audit['new_values'], str) else audit['new_values']
                            st.json(changes)
                        except:
                            st.write(audit['new_values'])

                st.markdown("---")
        else:
            st.info("No audit trail available")

    # Tab 5: Export
    with tab5:
        st.subheader("Export Traceability Report")

        report_text = export_traceability_report(chain)

        st.text_area("Report Preview", report_text, height=400)

        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            st.download_button(
                label="📥 Download Report",
                data=report_text,
                file_name=f"traceability_{entity_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )

        with col2:
            # Export as JSON
            json_data = json.dumps(chain, indent=2, default=str)
            st.download_button(
                label="📥 Download JSON",
                data=json_data,
                file_name=f"traceability_{entity_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

# ============================================
# SIDEBAR INFO
# ============================================

with st.sidebar:
    st.markdown("---")
    st.subheader("ℹ️ Page Info")
    st.info("""
    **Traceability Viewer**

    Complete workflow traceability:
    - Service Request → Inspection
    - Equipment → Protocol
    - Execution → Reports

    **Features:**
    - Timeline visualization
    - Detailed chain view
    - Measurement history
    - QC records
    - Audit trail
    - Export reports

    **Usage:**
    1. Select entity type
    2. Choose specific entity
    3. View complete chain
    4. Export if needed
    """)

    st.markdown("---")
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
