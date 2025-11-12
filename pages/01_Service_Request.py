"""
Service Request Page
Create and manage service requests for PV testing
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, date, timedelta
import json

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.database.db_manager import DatabaseManager

st.set_page_config(page_title="Service Request", page_icon="📝", layout="wide")

# Initialize database
if 'db' not in st.session_state:
    st.session_state.db = DatabaseManager()

# ============================================
# PAGE CONTENT
# ============================================

st.title("📝 Service Request Form")
st.markdown("### Create New Testing Service Request")

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["📝 New Request", "📋 My Requests", "🔍 Search"])

# ============================================
# TAB 1: NEW REQUEST
# ============================================

with tab1:
    st.subheader("Create New Service Request")

    with st.form("service_request_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Customer Information")

            customer_name = st.text_input(
                "Customer Name *",
                placeholder="Enter customer or company name"
            )

            customer_email = st.text_input(
                "Email Address *",
                placeholder="customer@example.com"
            )

            customer_phone = st.text_input(
                "Phone Number",
                placeholder="+1 (555) 123-4567"
            )

            project_name = st.text_input(
                "Project Name *",
                placeholder="e.g., Solar Farm Phase 2 Quality Audit"
            )

        with col2:
            st.markdown("#### Request Details")

            priority = st.selectbox(
                "Priority *",
                options=["low", "medium", "high", "urgent"],
                index=1
            )

            due_date = st.date_input(
                "Due Date *",
                value=date.today() + timedelta(days=30),
                min_value=date.today()
            )

            sample_description = st.text_area(
                "Sample Description *",
                placeholder="Describe the samples to be tested (type, quantity, specifications...)",
                height=100
            )

        st.markdown("#### Testing Requirements")

        # Protocol Categories
        col1, col2, col3 = st.columns(3)

        protocols_selected = []

        with col1:
            st.markdown("**Electrical Tests**")
            if st.checkbox("LID/LIS Testing (PVTP-001)"):
                protocols_selected.append("PVTP-001")
            if st.checkbox("I-V Curve Measurement (PVTP-026)"):
                protocols_selected.append("PVTP-026")
            if st.checkbox("STC Power Rating (PVTP-027)"):
                protocols_selected.append("PVTP-027")
            if st.checkbox("Temperature Coefficients (PVTP-022)"):
                protocols_selected.append("PVTP-022")

        with col2:
            st.markdown("**Reliability Tests**")
            if st.checkbox("Thermal Cycling (PVTP-002)"):
                protocols_selected.append("PVTP-002")
            if st.checkbox("Damp Heat (PVTP-003)"):
                protocols_selected.append("PVTP-003")
            if st.checkbox("Humidity Freeze (PVTP-004)"):
                protocols_selected.append("PVTP-004")
            if st.checkbox("PID Testing (PVTP-030)"):
                protocols_selected.append("PVTP-030")

        with col3:
            st.markdown("**Mechanical Tests**")
            if st.checkbox("Mechanical Load (PVTP-011)"):
                protocols_selected.append("PVTP-011")
            if st.checkbox("Hail Impact (PVTP-012)"):
                protocols_selected.append("PVTP-012")
            if st.checkbox("Twist Test (PVTP-014)"):
                protocols_selected.append("PVTP-014")

        st.markdown("**Quality Control**")
        qc_col1, qc_col2, qc_col3, qc_col4 = st.columns(4)
        with qc_col1:
            if st.checkbox("EL Imaging (PVTP-034)"):
                protocols_selected.append("PVTP-034")
        with qc_col2:
            if st.checkbox("Thermography (PVTP-035)"):
                protocols_selected.append("PVTP-035")
        with qc_col3:
            if st.checkbox("Visual Inspection (PVTP-036)"):
                protocols_selected.append("PVTP-036")
        with qc_col4:
            if st.checkbox("Flash Testing (PVTP-051)"):
                protocols_selected.append("PVTP-051")

        st.info(f"**Selected Protocols:** {len(protocols_selected)}")

        notes = st.text_area(
            "Additional Notes",
            placeholder="Any special requirements, constraints, or additional information...",
            height=100
        )

        # Submit button
        col1, col2, col3 = st.columns([2, 1, 1])

        with col2:
            submitted = st.form_submit_button("✅ Submit Request", use_container_width=True)

        with col3:
            clear = st.form_submit_button("🔄 Clear Form", use_container_width=True)

    # Handle form submission
    if submitted:
        # Validation
        if not customer_name or not customer_email or not project_name or not sample_description:
            st.error("❌ Please fill all required fields marked with *")
        elif len(protocols_selected) == 0:
            st.error("❌ Please select at least one testing protocol")
        else:
            try:
                # Create service request
                request_data = {
                    'customer_name': customer_name,
                    'customer_email': customer_email,
                    'customer_phone': customer_phone,
                    'project_name': project_name,
                    'sample_description': sample_description,
                    'requested_protocols': protocols_selected,
                    'priority': priority,
                    'due_date': due_date.isoformat(),
                    'notes': notes,
                    'requested_by': 1  # Current user
                }

                request_id = st.session_state.db.create_service_request(request_data)

                st.success(f"✅ Service Request Created Successfully!")
                st.info(f"**Request ID:** {request_id}")

                # Store in session state
                st.session_state.current_request_id = request_id

                # Show next steps
                st.markdown("### 🎯 Next Steps")
                st.markdown(f"""
                1. **Request ID:** `{request_id}` has been created
                2. Navigate to **Incoming Inspection** to log samples
                3. Use **Equipment Planning** to allocate resources
                4. Start testing with **Protocol Selector**
                """)

                # Quick action buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("➡️ Go to Incoming Inspection", use_container_width=True):
                        st.switch_page("pages/02_Incoming_Inspection.py")
                with col2:
                    if st.button("📄 View Request Details", use_container_width=True):
                        st.rerun()

            except Exception as e:
                st.error(f"❌ Error creating service request: {e}")

# ============================================
# TAB 2: MY REQUESTS
# ============================================

with tab2:
    st.subheader("My Service Requests")

    # Filter options
    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            options=["All", "pending", "approved", "in_progress", "completed", "cancelled"]
        )

    with col2:
        sort_by = st.selectbox(
            "Sort By",
            options=["Most Recent", "Oldest", "Priority", "Due Date"]
        )

    with col3:
        st.write("")  # Spacing
        st.write("")
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    # Fetch requests
    try:
        if status_filter == "All":
            requests = st.session_state.db.get_service_requests()
        else:
            requests = st.session_state.db.get_service_requests(status=status_filter)

        if requests:
            st.markdown(f"**Found {len(requests)} request(s)**")

            # Display requests as cards
            for req in requests:
                with st.expander(f"📋 {req['request_id']} - {req['project_name']}", expanded=False):
                    col1, col2, col3 = st.columns([2, 1, 1])

                    with col1:
                        st.markdown(f"**Customer:** {req['customer_name']}")
                        st.markdown(f"**Email:** {req.get('customer_email', 'N/A')}")
                        st.markdown(f"**Description:** {req.get('sample_description', 'N/A')}")

                    with col2:
                        # Status badge
                        status = req['status']
                        if status == 'completed':
                            st.success(f"✅ {status.upper()}")
                        elif status == 'in_progress':
                            st.warning(f"⏳ {status.upper()}")
                        elif status == 'approved':
                            st.info(f"👍 {status.upper()}")
                        else:
                            st.info(f"📋 {status.upper()}")

                        st.markdown(f"**Priority:** {req['priority'].upper()}")

                    with col3:
                        st.markdown(f"**Requested:** {req['requested_date'][:10]}")
                        st.markdown(f"**Due:** {req.get('due_date', 'N/A')}")

                        # Protocols
                        protocols = json.loads(req.get('requested_protocols', '[]'))
                        st.markdown(f"**Protocols:** {len(protocols)}")

                    # Actions
                    st.markdown("---")
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        if st.button("📝 View Details", key=f"view_{req['request_id']}"):
                            st.session_state.current_request_id = req['request_id']
                            st.info(f"Selected: {req['request_id']}")

                    with col2:
                        if st.button("🔍 Inspection", key=f"insp_{req['request_id']}"):
                            st.session_state.current_request_id = req['request_id']
                            st.switch_page("pages/02_Incoming_Inspection.py")

                    with col3:
                        if st.button("⚙️ Equipment", key=f"equip_{req['request_id']}"):
                            st.session_state.current_request_id = req['request_id']
                            st.switch_page("pages/03_Equipment_Planning.py")

                    with col4:
                        if st.button("🔗 Trace", key=f"trace_{req['request_id']}"):
                            st.session_state.current_request_id = req['request_id']
                            st.switch_page("pages/81_Traceability.py")
        else:
            st.info("📭 No service requests found")

    except Exception as e:
        st.error(f"Error loading requests: {e}")

# ============================================
# TAB 3: SEARCH
# ============================================

with tab3:
    st.subheader("🔍 Search Service Requests")

    search_term = st.text_input("Search by Request ID, Customer Name, or Project Name")

    if search_term:
        # Simple search implementation
        try:
            all_requests = st.session_state.db.get_service_requests()
            results = [
                req for req in all_requests
                if search_term.lower() in req['request_id'].lower()
                or search_term.lower() in req['customer_name'].lower()
                or search_term.lower() in req.get('project_name', '').lower()
            ]

            if results:
                st.success(f"Found {len(results)} matching request(s)")

                for req in results:
                    st.markdown(f"**{req['request_id']}** - {req['project_name']}")
                    st.caption(f"Customer: {req['customer_name']} | Status: {req['status']}")
                    if st.button("View Details", key=f"search_{req['request_id']}"):
                        st.session_state.current_request_id = req['request_id']
                        st.rerun()
                    st.markdown("---")
            else:
                st.warning("No matching requests found")

        except Exception as e:
            st.error(f"Search error: {e}")

# ============================================
# SIDEBAR INFO
# ============================================

with st.sidebar:
    st.markdown("---")
    st.subheader("ℹ️ Page Info")
    st.info("""
    **Service Request Form**

    Use this page to:
    - Create new testing requests
    - View existing requests
    - Track request status
    - Search and filter requests

    **Workflow:**
    1. Fill customer info
    2. Select protocols
    3. Submit request
    4. Proceed to inspection
    """)

    if st.session_state.get('current_request_id'):
        st.success(f"**Active Request:**\n{st.session_state.current_request_id}")
