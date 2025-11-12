"""
Service Request Page - Create and manage service requests for testing protocols.
"""

import streamlit as st
import json
from datetime import datetime
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from handlers.service_request_handler import ServiceRequestHandler
from workflow.orchestrator import WorkflowOrchestrator
from traceability.traceability_engine import TraceabilityEngine

# Page configuration
st.set_page_config(page_title="Service Request", page_icon="📝", layout="wide")

# Initialize handlers
if 'service_request_handler' not in st.session_state:
    st.session_state.service_request_handler = ServiceRequestHandler()
    st.session_state.orchestrator = WorkflowOrchestrator()
    st.session_state.traceability_engine = TraceabilityEngine()

st.title("📝 Service Request Management")

tabs = st.tabs(["➕ New Request", "📋 View Requests", "✅ Approve Requests"])

# Tab 1: Create New Service Request
with tabs[0]:
    st.subheader("Create New Service Request")

    with st.form("service_request_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Requester Information**")
            requester_name = st.text_input("Name*", key="req_name")
            requester_email = st.text_input("Email*", key="req_email")
            requester_phone = st.text_input("Phone", key="req_phone")
            requester_dept = st.text_input("Department*", key="req_dept")

        with col2:
            st.markdown("**Project/Customer Information**")
            project_type = st.selectbox(
                "Type*",
                ["Internal Project", "External Customer", "R&D", "Quality Control"]
            )
            project_name = st.text_input("Project/Customer Name*", key="proj_name")
            project_code = st.text_input("Project Code", key="proj_code")
            purchase_order = st.text_input("Purchase Order (if external)", key="po")

        st.markdown("---")
        st.markdown("**Sample Details**")

        col1, col2 = st.columns(2)

        with col1:
            sample_type = st.selectbox(
                "Sample Type*",
                ["PV Module", "Solar Cell", "Junction Box", "Connector", "Cable",
                 "Backsheet", "Encapsulant", "Frame", "Other"]
            )
            sample_description = st.text_area("Sample Description", key="sample_desc")
            quantity = st.number_input("Quantity*", min_value=1, value=1, key="quantity")

        with col2:
            manufacturer = st.text_input("Manufacturer", key="manuf")
            model_number = st.text_input("Model Number", key="model")
            batch_lot = st.text_input("Batch/Lot Number", key="batch")

        st.markdown("---")
        st.markdown("**Protocol Selection** (Select one or more protocols)")

        # Protocol categories
        available_protocols = {
            "IEC 61215 Series": [
                ("IEC-61215-1", "Crystalline Silicon PV Modules - Design Qualification"),
                ("IEC-61215-2", "Crystalline Silicon Module Test Procedures")
            ],
            "IEC 61730 Series": [
                ("IEC-61730-1", "PV Module Safety - Requirements for Construction"),
                ("IEC-61730-2", "PV Module Safety - Requirements for Testing")
            ],
            "IEC 61646": [
                ("IEC-61646", "Thin-Film Terrestrial PV Modules")
            ],
            "Performance Testing": [
                ("IEC-61853-1", "PV Module Performance - Irradiance and Temperature"),
                ("ASTM-E948", "Electrical Performance Testing")
            ],
            "Degradation Testing": [
                ("IEC-62804-1", "PV Modules - PID Testing")
            ],
            "Safety Standards": [
                ("UL-1703", "Flat-Plate Photovoltaic Modules and Panels")
            ]
        }

        selected_protocols = []
        for category, protocols in available_protocols.items():
            st.markdown(f"**{category}**")
            cols = st.columns(2)
            for idx, (protocol_id, protocol_name) in enumerate(protocols):
                with cols[idx % 2]:
                    if st.checkbox(f"{protocol_id}: {protocol_name}", key=f"proto_{protocol_id}"):
                        selected_protocols.append({
                            "protocol_id": protocol_id,
                            "protocol_name": protocol_name
                        })

        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            priority = st.selectbox("Priority*", ["Low", "Normal", "High", "Urgent"])
            completion_date = st.date_input("Requested Completion Date")

        with col2:
            confidentiality = st.selectbox(
                "Confidentiality Level",
                ["None", "Standard NDA", "Enhanced Confidentiality"]
            )
            witness_testing = st.checkbox("Customer Witness Required?")

        special_requirements = st.text_area(
            "Special Requirements/Notes",
            placeholder="Any special handling, environmental conditions, safety concerns, etc."
        )

        submit_button = st.form_submit_button("Create Service Request", use_container_width=True)

        if submit_button:
            # Validate required fields
            if not all([requester_name, requester_email, requester_dept, project_name, sample_type, quantity]):
                st.error("Please fill all required fields marked with *")
            elif not selected_protocols:
                st.error("Please select at least one protocol")
            else:
                # Create service request
                service_request_data = {
                    "requested_by": {
                        "name": requester_name,
                        "email": requester_email,
                        "phone": requester_phone,
                        "department": requester_dept
                    },
                    "project_customer": {
                        "type": project_type,
                        "name": project_name,
                        "project_code": project_code,
                        "purchase_order": purchase_order
                    },
                    "sample_details": {
                        "sample_type": sample_type,
                        "sample_description": sample_description,
                        "quantity": quantity,
                        "manufacturer": manufacturer,
                        "model_number": model_number,
                        "batch_lot_number": batch_lot
                    },
                    "protocols_requested": selected_protocols,
                    "priority": priority,
                    "requested_completion_date": str(completion_date),
                    "special_requirements": {
                        "confidentiality": confidentiality,
                        "witness_testing": witness_testing,
                        "custom_reporting": special_requirements
                    }
                }

                success, message, request = st.session_state.service_request_handler.create_service_request(
                    service_request_data
                )

                if success:
                    st.success(f"✅ {message}")

                    # Record traceability event
                    st.session_state.traceability_engine.record_event(
                        event_type="create",
                        entity_type="service_request",
                        entity_id=request["request_id"],
                        action="Service request created",
                        user=requester_name,
                        data={"status": "Draft"}
                    )

                    st.balloons()

                    # Display request details
                    with st.expander("View Request Details"):
                        st.json(request)

                    # Offer to submit for approval
                    if st.button("Submit for Approval"):
                        success, msg = st.session_state.service_request_handler.submit_service_request(
                            request["request_id"]
                        )
                        if success:
                            st.success(msg)

                            # Record traceability event
                            st.session_state.traceability_engine.record_event(
                                event_type="submit",
                                entity_type="service_request",
                                entity_id=request["request_id"],
                                action="Service request submitted for approval",
                                user=requester_name
                            )
                        else:
                            st.error(msg)
                else:
                    st.error(f"❌ {message}")

# Tab 2: View Requests
with tabs[1]:
    st.subheader("All Service Requests")

    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "Draft", "Submitted", "Approved", "Rejected", "In Progress", "Completed"],
            key="view_status_filter"
        )

    requests = st.session_state.service_request_handler.list_service_requests()

    if status_filter != "All":
        requests = [r for r in requests if r["status"] == status_filter]

    if requests:
        for request in requests:
            with st.expander(f"**{request['request_id']}** - {request['project_customer']} ({request['status']})"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown(f"**Requested By:** {request['requested_by']}")
                    st.markdown(f"**Date:** {request['request_date']}")

                with col2:
                    st.markdown(f"**Priority:** {request['priority']}")
                    st.markdown(f"**Protocols:** {request['protocols_count']}")

                with col3:
                    st.markdown(f"**Status:** {request['status']}")

                # View full details
                if st.button("View Full Details", key=f"view_{request['request_id']}"):
                    full_request = st.session_state.service_request_handler.get_service_request(
                        request['request_id']
                    )
                    st.json(full_request)
    else:
        st.info("No service requests found")

# Tab 3: Approve Requests
with tabs[2]:
    st.subheader("Approve/Reject Service Requests")

    # Get submitted requests
    submitted_requests = st.session_state.service_request_handler.list_service_requests(
        status_filter="Submitted"
    )

    if submitted_requests:
        for request in submitted_requests:
            with st.expander(f"**{request['request_id']}** - {request['project_customer']}"):
                full_request = st.session_state.service_request_handler.get_service_request(
                    request['request_id']
                )

                # Display request details
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Request Details:**")
                    st.markdown(f"- Requested by: {request['requested_by']}")
                    st.markdown(f"- Project: {request['project_customer']}")
                    st.markdown(f"- Priority: {request['priority']}")
                    st.markdown(f"- Protocols: {request['protocols_count']}")

                with col2:
                    st.markdown("**Sample Details:**")
                    st.json(full_request.get("sample_details", {}))

                st.markdown("---")

                # Approval actions
                col1, col2 = st.columns(2)

                with col1:
                    approver_name = st.text_input(
                        "Approver Name",
                        key=f"approver_{request['request_id']}"
                    )

                    if st.button("✅ Approve", key=f"approve_{request['request_id']}"):
                        if approver_name:
                            success, msg, work_orders = st.session_state.service_request_handler.approve_service_request(
                                request['request_id'],
                                approver_name
                            )

                            if success:
                                st.success(msg)

                                # Record traceability event
                                st.session_state.traceability_engine.record_event(
                                    event_type="approve",
                                    entity_type="service_request",
                                    entity_id=request['request_id'],
                                    action="Service request approved",
                                    user=approver_name,
                                    data={"work_orders": work_orders}
                                )

                                # Initiate workflow
                                workflow = st.session_state.orchestrator.initiate_workflow(full_request)
                                st.info(f"Workflow {workflow['workflow_id']} initiated")
                            else:
                                st.error(msg)
                        else:
                            st.warning("Please enter approver name")

                with col2:
                    rejection_reason = st.text_area(
                        "Rejection Reason",
                        key=f"reject_reason_{request['request_id']}"
                    )

                    if st.button("❌ Reject", key=f"reject_{request['request_id']}"):
                        if approver_name and rejection_reason:
                            success, msg = st.session_state.service_request_handler.reject_service_request(
                                request['request_id'],
                                approver_name,
                                rejection_reason
                            )

                            if success:
                                st.warning(msg)

                                # Record traceability event
                                st.session_state.traceability_engine.record_event(
                                    event_type="reject",
                                    entity_type="service_request",
                                    entity_id=request['request_id'],
                                    action="Service request rejected",
                                    user=approver_name,
                                    data={"reason": rejection_reason}
                                )
                            else:
                                st.error(msg)
                        else:
                            st.warning("Please enter approver name and rejection reason")
    else:
        st.info("No pending approvals")
