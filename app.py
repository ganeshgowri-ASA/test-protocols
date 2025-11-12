"""
Main Streamlit Application - PV Testing Protocol Framework
Master Workflow Orchestration System

Provides comprehensive UI for managing the complete workflow:
Service Request → Incoming Inspection → Equipment Planning → Protocol Execution → Reports
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import sys
import json
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from workflow.orchestrator import WorkflowOrchestrator
from handlers.service_request_handler import ServiceRequestHandler
from handlers.incoming_inspection_handler import IncomingInspectionHandler
from handlers.equipment_scheduler import EquipmentScheduler
from workflow.protocol_dispatcher import ProtocolDispatcher
from workflow.report_aggregator import ReportAggregator
from traceability.traceability_engine import TraceabilityEngine

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
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .workflow-stage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        background-color: #f0f2f6;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = WorkflowOrchestrator()
    st.session_state.service_request_handler = ServiceRequestHandler()
    st.session_state.inspection_handler = IncomingInspectionHandler()
    st.session_state.equipment_scheduler = EquipmentScheduler()
    st.session_state.protocol_dispatcher = ProtocolDispatcher()
    st.session_state.report_aggregator = ReportAggregator()
    st.session_state.traceability_engine = TraceabilityEngine()

    # Register handlers with orchestrator
    st.session_state.orchestrator.register_handlers(
        st.session_state.service_request_handler,
        st.session_state.inspection_handler,
        st.session_state.equipment_scheduler,
        st.session_state.protocol_dispatcher,
        st.session_state.report_aggregator
    )


def render_workflow_diagram():
    """Render interactive workflow diagram using Plotly."""
    fig = go.Figure()

    # Workflow stages
    stages = [
        {"name": "Service Request", "x": 0, "y": 0, "color": "#3498db"},
        {"name": "Incoming Inspection", "x": 1, "y": 0, "color": "#2ecc71"},
        {"name": "Equipment Planning", "x": 2, "y": 0, "color": "#f39c12"},
        {"name": "Protocol Execution", "x": 3, "y": 0, "color": "#9b59b6"},
        {"name": "Analysis & QC", "x": 4, "y": 0, "color": "#e74c3c"},
        {"name": "Report Generation", "x": 5, "y": 0, "color": "#1abc9c"}
    ]

    # Add nodes
    for stage in stages:
        fig.add_trace(go.Scatter(
            x=[stage["x"]],
            y=[stage["y"]],
            mode="markers+text",
            marker=dict(size=40, color=stage["color"]),
            text=stage["name"],
            textposition="bottom center",
            textfont=dict(size=10),
            hoverinfo="text",
            hovertext=f"<b>{stage['name']}</b>",
            showlegend=False
        ))

    # Add arrows between stages
    for i in range(len(stages) - 1):
        fig.add_annotation(
            x=stages[i+1]["x"],
            y=stages[i+1]["y"],
            ax=stages[i]["x"],
            ay=stages[i]["y"],
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="#95a5a6"
        )

    fig.update_layout(
        title="Workflow Orchestration Pipeline",
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=250,
        margin=dict(l=20, r=20, t=60, b=100),
        plot_bgcolor="rgba(0,0,0,0)"
    )

    return fig


def render_dashboard():
    """Render main dashboard with KPIs and statistics."""
    st.markdown('<div class="main-header">⚡ PV Testing Protocol Framework</div>', unsafe_allow_html=True)

    # Workflow diagram
    st.plotly_chart(render_workflow_diagram(), use_container_width=True)

    st.markdown("---")

    # KPIs
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        service_requests = st.session_state.service_request_handler.list_service_requests()
        st.metric("Service Requests", len(service_requests))

    with col2:
        inspections = st.session_state.inspection_handler.list_inspections()
        st.metric("Inspections", len(inspections))

    with col3:
        workflows = st.session_state.orchestrator.list_active_workflows()
        st.metric("Active Workflows", len([w for w in workflows if w["status"] == "in_progress"]))

    with col4:
        protocols = st.session_state.protocol_dispatcher.list_protocols()
        st.metric("Available Protocols", len(protocols))

    st.markdown("---")

    # Recent Activity
    st.subheader("📊 Recent Activity")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Recent Service Requests**")
        recent_requests = st.session_state.service_request_handler.list_service_requests()[:5]
        if recent_requests:
            for req in recent_requests:
                st.markdown(f"- **{req['request_id']}** - {req['requested_by']} ({req['status']})")
        else:
            st.info("No service requests yet")

    with col2:
        st.markdown("**Recent Workflows**")
        recent_workflows = st.session_state.orchestrator.list_active_workflows()[:5]
        if recent_workflows:
            for wf in recent_workflows:
                progress = st.session_state.orchestrator._calculate_progress(
                    st.session_state.orchestrator.get_workflow(wf['workflow_id'])
                )
                st.markdown(f"- **{wf['workflow_id']}** - {wf['current_stage']} ({progress}%)")
        else:
            st.info("No active workflows yet")

    st.markdown("---")

    # Protocol Categories Chart
    st.subheader("📋 Protocol Categories")

    protocols = st.session_state.protocol_dispatcher.list_protocols()
    if protocols:
        categories = {}
        for protocol in protocols:
            category = protocol["category"]
            categories[category] = categories.get(category, 0) + 1

        fig = px.pie(
            names=list(categories.keys()),
            values=list(categories.values()),
            title="Protocols by Category"
        )
        st.plotly_chart(fig, use_container_width=True)

    # Traceability Statistics
    st.subheader("🔍 Traceability Overview")
    traceability_stats = st.session_state.traceability_engine.get_statistics()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Audit Events", traceability_stats["total_events"])

    with col2:
        st.metric("Entity Relationships", traceability_stats["total_entity_relationships"])

    with col3:
        st.metric("Unique Users", len(traceability_stats["unique_users"]))


def render_sidebar():
    """Render navigation sidebar."""
    st.sidebar.title("🧭 Navigation")

    st.sidebar.markdown("### Workflow Stages")

    pages = {
        "🏠 Dashboard": "dashboard",
        "📝 Service Request": "service_request",
        "🔍 Incoming Inspection": "inspection",
        "⚙️ Equipment Planning": "equipment",
        "🧪 Protocol Execution": "protocol",
        "📊 Reports & Analytics": "reports",
        "🔗 Traceability": "traceability"
    }

    selected_page = st.sidebar.radio("Select Page", list(pages.keys()))

    st.sidebar.markdown("---")

    st.sidebar.markdown("### Quick Actions")
    if st.sidebar.button("➕ New Service Request"):
        st.session_state.current_page = "service_request"
        st.rerun()

    if st.sidebar.button("📋 View All Workflows"):
        st.session_state.show_workflows = True

    st.sidebar.markdown("---")

    st.sidebar.markdown("### System Info")
    st.sidebar.info(f"Version: 1.0.0\nLast Updated: {datetime.now().strftime('%Y-%m-%d')}")

    return pages[selected_page]


def main():
    """Main application entry point."""

    # Render sidebar and get selected page
    current_page = render_sidebar()

    # Route to appropriate page
    if current_page == "dashboard":
        render_dashboard()

    elif current_page == "service_request":
        st.info("Please navigate to 'Service Request' page from the Pages menu in the sidebar.")
        st.markdown("The Service Request page allows you to:")
        st.markdown("- Create new service requests")
        st.markdown("- Submit requests for approval")
        st.markdown("- Track request status")
        st.markdown("- View protocol options")

    elif current_page == "inspection":
        st.info("Please navigate to 'Incoming Inspection' page from the Pages menu in the sidebar.")
        st.markdown("The Incoming Inspection page allows you to:")
        st.markdown("- Perform sample receipt verification")
        st.markdown("- Conduct visual inspections")
        st.markdown("- Check documentation completeness")
        st.markdown("- Make acceptance decisions")

    elif current_page == "equipment":
        st.info("Please navigate to 'Equipment Planning' page from the Pages menu in the sidebar.")
        st.markdown("The Equipment Planning page allows you to:")
        st.markdown("- View equipment catalog")
        st.markdown("- Allocate equipment to protocols")
        st.markdown("- Schedule testing")
        st.markdown("- Optimize resource utilization")

    elif current_page == "protocol":
        st.subheader("🧪 Protocol Execution")
        st.info("Protocol execution functionality - dispatching protocols and tracking execution")

    elif current_page == "reports":
        st.subheader("📊 Reports & Analytics")
        reports = st.session_state.report_aggregator.list_reports()
        if reports:
            for report in reports:
                with st.expander(f"Report: {report['report_id']}"):
                    st.json(report)
        else:
            st.info("No reports generated yet")

    elif current_page == "traceability":
        st.subheader("🔗 Traceability & Audit Trail")
        st.markdown("Complete audit trail and data lineage tracking")

        # Traceability search
        entity_id = st.text_input("Enter Entity ID to trace (e.g., SR-2025-123456)")
        if entity_id:
            # Determine entity type from ID prefix
            entity_type_map = {
                "SR": "service_request",
                "II": "inspection",
                "EP": "equipment_plan",
                "PE": "protocol_execution",
                "WF": "workflow"
            }
            prefix = entity_id.split("-")[0]
            entity_type = entity_type_map.get(prefix)

            if entity_type:
                if st.button("Generate Traceability Report"):
                    report = st.session_state.traceability_engine.generate_traceability_report(
                        entity_type, entity_id
                    )
                    st.success(f"Traceability report generated: {report['report_id']}")
                    st.json(report)
            else:
                st.error("Invalid entity ID format")


if __name__ == "__main__":
    main()
