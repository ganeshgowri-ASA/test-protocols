"""
Service Request Module
======================
Create and manage service requests for testing.
"""

import streamlit as st
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import setup_page_config, config
from config.database import get_db
from config.protocols_registry import get_cached_protocol_registry
from components.navigation import render_header, render_sidebar_navigation
from database import ServiceRequest, RequestStatus
from sqlalchemy import select, desc, asc, and_, or_, func
from sqlalchemy.orm import load_only

# Page configuration
setup_page_config(page_title="Service Request", page_icon="📋")

# Render navigation
render_header("Service Request Management", "Create and manage test service requests")
render_sidebar_navigation()


def main():
    """Main service request page"""

    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["➕ New Request", "📋 View Requests", "🔍 Search"])

    with tab1:
        render_new_request_form()

    with tab2:
        render_requests_list()

    with tab3:
        render_search_interface()


def render_new_request_form():
    """Render form to create new service request"""

    st.markdown("### Create New Service Request")

    with st.form("new_service_request"):
        # Client Information
        st.markdown("#### 👤 Client Information")

        col1, col2 = st.columns(2)

        with col1:
            client_name = st.text_input("Client Name *", placeholder="Enter client name")
            client_email = st.text_input("Email *", placeholder="client@example.com")

        with col2:
            client_phone = st.text_input("Phone", placeholder="+1 234 567 8900")
            client_org = st.text_input("Organization", placeholder="Company/Institution")

        st.divider()

        # Sample Information
        st.markdown("#### 📦 Sample Information")

        col1, col2, col3 = st.columns(3)

        with col1:
            sample_type = st.selectbox(
                "Sample Type *",
                ["Module", "Cell", "Array", "Component"]
            )

        with col2:
            sample_count = st.number_input(
                "Expected Sample Quantity *",
                min_value=1,
                max_value=100,
                value=1,
                help="Number of samples expected to be received"
            )

        with col3:
            priority = st.selectbox(
                "Priority",
                ["Normal", "High", "Urgent"],
                index=0
            )

        # Sample receipt workflow info
        st.info("""
        **Sample Workflow:**
        1. Submit service request with expected sample count
        2. Record sample receipt when samples arrive
        3. Inspect samples (visual inspection)
        4. If inspection passes, samples are allocated unique IDs and QR codes
        5. Samples proceed to testing
        """)

        col1, col2 = st.columns(2)

        with col1:
            manufacturer = st.text_input("Manufacturer", placeholder="e.g., SunPower")

        with col2:
            model_number = st.text_input("Model Number", placeholder="e.g., SPR-X22-360")

        # Serial numbers
        serial_numbers = st.text_area(
            "Serial Numbers (one per line)",
            placeholder="SN001\nSN002\nSN003",
            height=100
        )

        st.divider()

        # Protocol Selection
        st.markdown("#### 🔬 Testing Protocols")

        # Get available protocols
        registry = get_cached_protocol_registry()
        protocols_by_category = {
            "Performance": registry.get_protocols_by_category("performance"),
            "Degradation": registry.get_protocols_by_category("degradation"),
            "Environmental": registry.get_protocols_by_category("environmental"),
            "Mechanical": registry.get_protocols_by_category("mechanical"),
            "Safety": registry.get_protocols_by_category("safety")
        }

        selected_protocols = []

        for category, protocols in protocols_by_category.items():
            if protocols:
                st.markdown(f"**{category} Testing**")

                # Create checkboxes for each protocol
                cols = st.columns(3)
                for idx, protocol in enumerate(protocols):
                    col_idx = idx % 3
                    with cols[col_idx]:
                        if st.checkbox(
                            f"{protocol.protocol_id}: {protocol.name}",
                            key=f"protocol_{protocol.protocol_id}"
                        ):
                            selected_protocols.append(protocol.protocol_id)

        st.divider()

        # Additional Information
        st.markdown("#### 📝 Additional Information")

        expected_date = st.date_input(
            "Expected Completion Date",
            value=datetime.now() + timedelta(days=30),
            min_value=datetime.now()
        )

        notes = st.text_area(
            "Notes/Special Requirements",
            placeholder="Enter any special requirements or notes...",
            height=100
        )

        # File upload
        attachments = st.file_uploader(
            "Attachments (specifications, drawings, etc.)",
            accept_multiple_files=True,
            type=['pdf', 'jpg', 'png', 'xlsx', 'doc', 'docx']
        )

        # Form submission
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.caption("* Required fields")

        with col2:
            submit_draft = st.form_submit_button("💾 Save Draft", width="stretch")

        with col3:
            submit_final = st.form_submit_button("✅ Submit Request", width="stretch", type="primary")

        # Process form submission
        if submit_draft or submit_final:
            # Validate required fields
            if not client_name or not client_email:
                st.error("❌ Please fill in all required fields (Client Name, Email)")
                return

            if not selected_protocols:
                st.warning("⚠️ No testing protocols selected")

            # Parse serial numbers
            serial_list = [s.strip() for s in serial_numbers.split('\n') if s.strip()]

            # Create service request
            try:
                request_number = generate_request_number()

                new_request = {
                    'request_number': request_number,
                    'client_name': client_name,
                    'client_email': client_email,
                    'client_phone': client_phone,
                    'client_organization': client_org,
                    'sample_type': sample_type.lower(),
                    'sample_count': sample_count,
                    'manufacturer': manufacturer,
                    'model_number': model_number,
                    'serial_numbers': serial_list,
                    'requested_protocols': selected_protocols,
                    'priority': priority.lower(),
                    'expected_completion_date': datetime.combine(expected_date, datetime.min.time()),
                    'status': RequestStatus.SUBMITTED if submit_final else RequestStatus.DRAFT,
                    'notes': notes,
                    'created_by': 1,  # Demo user ID
                    'submitted_at': datetime.utcnow() if submit_final else None
                }

                # Save to database
                with get_db() as db:
                    sr = ServiceRequest(**new_request)
                    db.add(sr)
                    db.commit()

                    # Set as active context
                    st.session_state.active_service_request = {
                        'id': sr.id,
                        'request_number': sr.request_number,
                        'client_name': sr.client_name,
                        'status': sr.status.value
                    }

                if submit_final:
                    st.success(f"✅ Service Request {request_number} submitted successfully!")
                else:
                    st.success(f"💾 Service Request {request_number} saved as draft")

                st.info(f"📋 Request Number: **{request_number}**")

                # Show next steps
                with st.expander("📝 Next Steps"):
                    st.markdown("""
                    1. ✅ Service request created
                    2. ⏳ Awaiting supervisor approval
                    3. 📦 Proceed to Incoming Inspection
                    4. ⚙️ Book required equipment
                    5. 🔬 Execute testing protocols
                    """)

            except Exception as e:
                st.error(f"❌ Error creating service request: {str(e)}")


def render_requests_list():
    """Render list of existing service requests"""

    st.markdown("### 📋 Service Requests")

    try:
        with get_db() as db:
            requests = db.execute(
                select(ServiceRequest).order_by(
                    ServiceRequest.created_at.desc()
                ).limit(50)
            ).scalars().all()

            if not requests:
                st.info("No service requests found")
                return

            # Extract data while session is open to avoid DetachedInstanceError
            requests_data = []
            for req in requests:
                requests_data.append({
                    'id': req.id,
                    'request_number': req.request_number,
                    'client_name': req.client_name,
                    'client_email': req.client_email,
                    'client_organization': req.client_organization,
                    'sample_type': req.sample_type,
                    'sample_count': req.sample_count,
                    'priority': req.priority,
                    'status': req.status.value if hasattr(req.status, 'value') else str(req.status),
                    'status_enum': req.status,
                    'created_at': req.created_at,
                    'requested_protocols': req.requested_protocols or []
                })

        # Filters (outside session context - using extracted data)
        col1, col2, col3 = st.columns(3)

        with col1:
            status_filter = st.selectbox(
                "Filter by Status",
                ["All", "Draft", "Submitted", "Approved", "In Progress", "Completed"]
            )

        with col2:
            priority_filter = st.selectbox(
                "Filter by Priority",
                ["All", "Normal", "High", "Urgent"]
            )

        # Display requests as cards
        for req_data in requests_data:
            # Apply filters
            if status_filter != "All" and req_data['status'] != status_filter.lower().replace(" ", "_"):
                continue

            if priority_filter != "All" and req_data['priority'] != priority_filter.lower():
                continue

            with st.expander(
                f"🎫 {req_data['request_number']} - {req_data['client_name']} ({req_data['status'].upper()})",
                expanded=False
            ):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown(f"**Client:** {req_data['client_name']}")
                    st.markdown(f"**Email:** {req_data['client_email']}")
                    st.markdown(f"**Organization:** {req_data['client_organization'] or 'N/A'}")

                with col2:
                    st.markdown(f"**Sample Type:** {req_data['sample_type'].title() if req_data['sample_type'] else 'N/A'}")
                    st.markdown(f"**Quantity:** {req_data['sample_count']}")
                    st.markdown(f"**Priority:** {req_data['priority'].upper() if req_data['priority'] else 'N/A'}")

                with col3:
                    st.markdown(f"**Status:** {req_data['status'].upper()}")
                    st.markdown(f"**Created:** {req_data['created_at'].strftime('%Y-%m-%d')}")
                    st.markdown(f"**Protocols:** {len(req_data['requested_protocols'])}")

                if req_data['requested_protocols']:
                    st.markdown("**Selected Protocols:**")
                    protocol_text = ", ".join(req_data['requested_protocols'])
                    st.caption(protocol_text)

                # Action buttons
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    if st.button("👁️ View Details", key=f"view_{req_data['id']}"):
                        st.session_state.view_request_id = req_data['id']

                with col2:
                    if st.button("✏️ Edit", key=f"edit_{req_data['id']}"):
                        st.info("Edit functionality - Coming soon!")

                with col3:
                    if req_data['status'] == 'submitted':
                        if st.button("✅ Approve", key=f"approve_{req_data['id']}"):
                            with get_db() as db:
                                req_obj = db.execute(
                                    select(ServiceRequest).where(ServiceRequest.id == req_data['id'])
                                ).scalar_one_or_none()
                                if req_obj:
                                    req_obj.status = RequestStatus.APPROVED
                                    req_obj.approved_at = datetime.utcnow()
                                    db.commit()
                            st.success("Request approved!")
                            st.rerun()

                with col4:
                    if st.button("🗑️ Delete", key=f"delete_{req_data['id']}"):
                        if st.session_state.get(f"confirm_delete_{req_data['id']}", False):
                            with get_db() as db:
                                req_obj = db.execute(
                                    select(ServiceRequest).where(ServiceRequest.id == req_data['id'])
                                ).scalar_one_or_none()
                                if req_obj:
                                    db.delete(req_obj)
                                    db.commit()
                            st.success("Request deleted")
                            st.rerun()
                        else:
                            st.session_state[f"confirm_delete_{req_data['id']}"] = True
                            st.warning("Click again to confirm deletion")

    except Exception as e:
        st.error(f"Error loading service requests: {str(e)}")


def render_search_interface():
    """Render search interface"""

    st.markdown("### 🔍 Search Service Requests")

    search_query = st.text_input(
        "Search by request number, client name, or email",
        placeholder="Enter search term..."
    )

    if search_query:
        try:
            with get_db() as db:
                results = db.execute(
                    select(ServiceRequest).where(
                        (ServiceRequest.request_number.contains(search_query)) |
                        (ServiceRequest.client_name.contains(search_query)) |
                        (ServiceRequest.client_email.contains(search_query))
                    )
                ).scalars().all()

                # Extract data while session is open
                results_data = []
                for req in results:
                    results_data.append({
                        'request_number': req.request_number,
                        'client_name': req.client_name,
                        'status': req.status.value if hasattr(req.status, 'value') else str(req.status),
                        'created_at': req.created_at
                    })

            st.markdown(f"**Found {len(results_data)} result(s)**")

            for req_data in results_data:
                st.markdown(f"""
                **{req_data['request_number']}** - {req_data['client_name']}
                - Status: {req_data['status'].upper()}
                - Created: {req_data['created_at'].strftime('%Y-%m-%d')}
                """)
                st.divider()

        except Exception as e:
            st.error(f"Search error: {str(e)}")


def generate_request_number() -> str:
    """Generate unique request number"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"SR-{timestamp[-10:]}"


if __name__ == "__main__":
    main()
