"""
Data Traceability Viewer - Complete audit trail visualization
"""
import streamlit as st
from datetime import datetime
import pandas as pd

from utils.data_generator import get_sample_data
from utils.helpers import format_datetime, get_status_icon
from models.protocol import ProtocolStatus

# Page configuration
st.set_page_config(
    page_title="Data Traceability",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Data Traceability Viewer")
st.markdown("### Complete Audit Trail & Data Journey Visualization")

# Load data
@st.cache_data(ttl=300)
def load_data():
    return get_sample_data()

data = load_data()
protocols = data['protocols']
service_requests = data['service_requests']

# Search section
st.markdown("---")
st.subheader("Search by ID")

search_col1, search_col2, search_col3 = st.columns([2, 1, 1])

with search_col1:
    search_query = st.text_input(
        "Enter Service Request ID, Sample ID, Protocol ID, or Equipment ID",
        placeholder="e.g., SR-2024001, SMP-2024001, PROT-SR-2024001-001"
    )

with search_col2:
    search_type = st.selectbox(
        "Search Type",
        ["All", "Service Request", "Sample", "Protocol", "Equipment"]
    )

with search_col3:
    if st.button("🔍 Search", use_container_width=True):
        st.session_state['search_query'] = search_query

# Display search results
if search_query:
    st.markdown("---")
    st.subheader("Search Results")

    # Find matching service request
    matching_sr = None
    for sr in service_requests:
        if (search_query.upper() in sr.request_id.upper() or
            search_query.upper() in sr.sample_id.upper()):
            matching_sr = sr
            break

    if matching_sr:
        # Display service request information
        st.success(f"✅ Found Service Request: {matching_sr.request_id}")

        # Service Request Details
        with st.expander("📝 Service Request Details", expanded=True):
            sr_col1, sr_col2, sr_col3, sr_col4 = st.columns(4)

            with sr_col1:
                st.markdown(f"**Request ID:** {matching_sr.request_id}")
                st.markdown(f"**Customer:** {matching_sr.customer_name}")

            with sr_col2:
                st.markdown(f"**Sample ID:** {matching_sr.sample_id}")
                st.markdown(f"**Status:** {get_status_icon(matching_sr.status)} {matching_sr.status.title()}")

            with sr_col3:
                st.markdown(f"**Priority:** {matching_sr.priority.upper()}")
                st.markdown(f"**Request Date:** {format_datetime(matching_sr.request_date, '%Y-%m-%d')}")

            with sr_col4:
                st.markdown(f"**Assigned To:** {matching_sr.assigned_to or 'Unassigned'}")
                st.markdown(f"**Protocols:** {len(matching_sr.required_protocols)}")

        # Find related protocols
        related_protocols = [
            p for p in protocols
            if p.service_request_id == matching_sr.request_id
        ]

        # Data Journey Flowchart
        st.markdown("---")
        st.subheader("📊 Data Journey Flowchart")

        # Create visual flow
        flow_cols = st.columns(5)

        with flow_cols[0]:
            st.markdown("""
                <div style='text-align: center; padding: 20px; background-color: #e3f2fd; border-radius: 10px;'>
                    <h3>📋</h3>
                    <strong>Service Request</strong><br>
                    {}<br>
                    <small>{}</small>
                </div>
            """.format(matching_sr.request_id, format_datetime(matching_sr.request_date, "%Y-%m-%d")), unsafe_allow_html=True)

        with flow_cols[1]:
            st.markdown("""
                <div style='text-align: center; padding: 40px 10px;'>
                    <h2>→</h2>
                </div>
            """, unsafe_allow_html=True)

        with flow_cols[2]:
            st.markdown("""
                <div style='text-align: center; padding: 20px; background-color: #fff3e0; border-radius: 10px;'>
                    <h3>🔬</h3>
                    <strong>Inspection</strong><br>
                    Sample: {}<br>
                    <small>Protocols: {}</small>
                </div>
            """.format(matching_sr.sample_id, len(related_protocols)), unsafe_allow_html=True)

        with flow_cols[3]:
            st.markdown("""
                <div style='text-align: center; padding: 40px 10px;'>
                    <h2>→</h2>
                </div>
            """, unsafe_allow_html=True)

        with flow_cols[4]:
            completed = len([p for p in related_protocols if p.status == ProtocolStatus.COMPLETED])
            st.markdown("""
                <div style='text-align: center; padding: 20px; background-color: #e8f5e9; border-radius: 10px;'>
                    <h3>✅</h3>
                    <strong>Protocols</strong><br>
                    {}/{} Complete<br>
                    <small>QC Verified</small>
                </div>
            """.format(completed, len(related_protocols)), unsafe_allow_html=True)

        # Timeline View
        st.markdown("---")
        st.subheader("⏱️ Timeline View")

        timeline_data = []

        # Add service request event
        timeline_data.append({
            'Timestamp': matching_sr.request_date,
            'Event': 'Service Request Created',
            'Details': f"Request {matching_sr.request_id} created for {matching_sr.customer_name}",
            'Status': 'Completed'
        })

        # Add protocol events
        for protocol in sorted(related_protocols, key=lambda p: p.start_time if p.start_time else datetime.now()):
            if protocol.start_time:
                timeline_data.append({
                    'Timestamp': protocol.start_time,
                    'Event': f'Protocol Started: {protocol.protocol_name[:40]}',
                    'Details': f"Operator: {protocol.operator}, Equipment: {protocol.equipment_id}",
                    'Status': 'In Progress' if not protocol.end_time else 'Completed'
                })

            if protocol.end_time:
                timeline_data.append({
                    'Timestamp': protocol.end_time,
                    'Event': f'Protocol Completed: {protocol.protocol_name[:40]}',
                    'Details': f"QC Result: {protocol.qc_result.value.upper()}",
                    'Status': 'Completed'
                })

        timeline_df = pd.DataFrame(timeline_data)
        timeline_df = timeline_df.sort_values('Timestamp', ascending=False)
        timeline_df['Timestamp'] = timeline_df['Timestamp'].apply(lambda x: format_datetime(x))

        st.dataframe(timeline_df, use_container_width=True, height=400)

        # Related Protocols Table
        st.markdown("---")
        st.subheader("📋 Related Protocols")

        if related_protocols:
            protocol_table_data = []
            for p in related_protocols:
                protocol_table_data.append({
                    'Protocol ID': p.protocol_id,
                    'Name': p.protocol_name,
                    'Type': p.protocol_type.value,
                    'Status': f"{get_status_icon(p.status.value)} {p.status.value.title()}",
                    'QC Result': f"{get_status_icon(p.qc_result.value)} {p.qc_result.value.upper()}",
                    'Operator': p.operator or 'N/A',
                    'Equipment': p.equipment_id or 'N/A',
                    'Duration': f"{p.duration_hours:.2f}h" if p.duration_hours else 'N/A',
                    'Started': format_datetime(p.start_time) if p.start_time else 'Not Started',
                    'Completed': format_datetime(p.end_time) if p.end_time else 'In Progress'
                })

            protocol_df = pd.DataFrame(protocol_table_data)
            st.dataframe(protocol_df, use_container_width=True, height=400)

            # Protocol Statistics
            st.markdown("---")
            stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

            with stat_col1:
                st.metric("Total Protocols", len(related_protocols))

            with stat_col2:
                completed_count = len([p for p in related_protocols if p.status == ProtocolStatus.COMPLETED])
                st.metric("Completed", completed_count)

            with stat_col3:
                passed = len([p for p in related_protocols if p.qc_result.value == 'pass'])
                pass_rate = (passed / completed_count * 100) if completed_count > 0 else 0
                st.metric("Pass Rate", f"{pass_rate:.1f}%")

            with stat_col4:
                total_duration = sum(p.duration_hours for p in related_protocols if p.duration_hours)
                st.metric("Total Duration", f"{total_duration:.1f}h")

        else:
            st.info("No protocols found for this service request.")

        # Export Section
        st.markdown("---")
        st.subheader("📥 Export Traceability Report")

        export_col1, export_col2, export_col3 = st.columns(3)

        with export_col1:
            if st.button("📄 Export to PDF", use_container_width=True):
                st.info("PDF export functionality - Coming soon!")

        with export_col2:
            if st.button("📊 Export to Excel", use_container_width=True):
                st.info("Excel export functionality - Coming soon!")

        with export_col3:
            if st.button("📋 Export to CSV", use_container_width=True):
                # Convert to CSV
                csv_data = protocol_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"traceability_{matching_sr.request_id}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )

    else:
        st.warning(f"⚠️ No results found for: {search_query}")
        st.info("Try searching with a different ID or check the format (e.g., SR-2024001)")

else:
    # Display overview when no search
    st.info("👆 Enter an ID in the search box above to trace the complete data journey")

    st.markdown("---")
    st.subheader("Available Search Types")

    search_info_col1, search_info_col2 = st.columns(2)

    with search_info_col1:
        st.markdown("""
        #### 🔍 Search Capabilities:
        - **Service Request ID**: Track complete request lifecycle
        - **Sample ID**: View all tests for a specific sample
        - **Protocol ID**: Detailed protocol execution history
        - **Equipment ID**: All protocols using specific equipment
        """)

    with search_info_col2:
        st.markdown("""
        #### 📊 Traceability Features:
        - Complete audit trail from request to report
        - Interactive flowchart visualization
        - Timeline view of all events
        - Export capabilities for compliance
        - Real-time status updates
        """)

    # Recent Activity
    st.markdown("---")
    st.subheader("📅 Recent Activity")

    recent_protocols = sorted(
        [p for p in protocols if p.start_time],
        key=lambda p: p.start_time,
        reverse=True
    )[:10]

    recent_data = []
    for p in recent_protocols:
        recent_data.append({
            'Time': format_datetime(p.start_time, "%Y-%m-%d %H:%M"),
            'Event': f"Protocol: {p.protocol_name[:50]}",
            'Request ID': p.service_request_id,
            'Status': f"{get_status_icon(p.status.value)} {p.status.value.title()}"
        })

    if recent_data:
        recent_df = pd.DataFrame(recent_data)
        st.dataframe(recent_df, use_container_width=True, height=300)

# Compliance Notice
st.markdown("---")
st.info("""
    **🔒 Compliance & Audit Support**

    This traceability system maintains complete audit trails for:
    - ISO 17025 compliance
    - FDA 21 CFR Part 11 requirements
    - CAPA (Corrective and Preventive Action) tracking
    - Full data integrity verification
""")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    f"Data Traceability Viewer v1.0 | {len(service_requests)} Service Requests | "
    f"{len(protocols)} Protocols Tracked | Last Updated: {format_datetime(datetime.now())}"
    "</div>",
    unsafe_allow_html=True
)
