"""
Sample Receipt Module
=====================
Record and manage sample receipts from clients/couriers.
First step in the sample management workflow.
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
from components.navigation import render_header, render_sidebar_navigation
from components.sample_management import generate_receipt_number
from database import (
    SampleReceipt, ServiceRequest, User, RequestStatus
)
from sqlalchemy import select, desc

# Page configuration
setup_page_config(page_title="Sample Receipt", page_icon="📥")

# Render navigation
render_header("Sample Receipt", "Record incoming sample deliveries")
render_sidebar_navigation()


def main():
    """Main sample receipt page"""

    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["➕ New Receipt", "📋 View Receipts", "⏳ Pending Approvals"])

    with tab1:
        render_new_receipt_form()

    with tab2:
        render_receipts_list()

    with tab3:
        render_pending_approvals()


def render_new_receipt_form():
    """Render form to create new sample receipt"""

    st.markdown("### Record New Sample Receipt")

    # Get service requests for linking
    with get_db() as db:
        service_requests = db.execute(
            select(ServiceRequest)
            .where(ServiceRequest.status.in_([RequestStatus.SUBMITTED, RequestStatus.APPROVED]))
            .order_by(desc(ServiceRequest.created_at))
        ).scalars().all()

        sr_options = {f"{sr.request_number} - {sr.client_name}": sr for sr in service_requests}

    with st.form("new_sample_receipt"):
        # Service Request Selection
        st.markdown("#### 🔗 Link to Service Request")

        col1, col2 = st.columns(2)

        with col1:
            selected_sr = st.selectbox(
                "Service Request *",
                options=["-- Select Service Request --"] + list(sr_options.keys()),
                help="Link this receipt to an existing service request"
            )

        with col2:
            if selected_sr and selected_sr != "-- Select Service Request --":
                sr = sr_options[selected_sr]
                st.info(f"**Expected Samples:** {sr.sample_count}")

        st.divider()

        # Receipt Details
        st.markdown("#### 📦 Package Information")

        col1, col2, col3 = st.columns(3)

        with col1:
            received_date = st.date_input(
                "Received Date *",
                value=datetime.now().date()
            )
            received_time = st.time_input(
                "Received Time *",
                value=datetime.now().time()
            )

        with col2:
            package_count = st.number_input(
                "Package Count *",
                min_value=1,
                max_value=100,
                value=1
            )

            package_condition = st.selectbox(
                "Package Condition *",
                options=["Good", "Sealed", "Opened", "Damaged"],
                index=0
            )

        with col3:
            courier_name = st.text_input(
                "Courier/Carrier Name",
                placeholder="e.g., FedEx, DHL, Hand Delivery"
            )

            tracking_number = st.text_input(
                "Tracking Number",
                placeholder="Enter tracking number"
            )

        st.divider()

        # Sample Count Verification
        st.markdown("#### 🔢 Sample Count Verification")

        col1, col2 = st.columns(2)

        with col1:
            expected_count = st.number_input(
                "Expected Sample Count *",
                min_value=1,
                max_value=100,
                value=sr.sample_count if selected_sr and selected_sr != "-- Select Service Request --" else 1
            )

        with col2:
            actual_count = st.number_input(
                "Actual Sample Count *",
                min_value=0,
                max_value=100,
                value=expected_count
            )

        # Show mismatch warning
        if expected_count != actual_count:
            st.warning("⚠️ Sample count mismatch detected! Supervisor approval will be required.")

            mismatch_notes = st.text_area(
                "Mismatch Notes *",
                placeholder="Explain the discrepancy in sample count...",
                help="Required when there is a mismatch between expected and actual counts"
            )
        else:
            mismatch_notes = ""

        st.divider()

        # Client/Source Information
        st.markdown("#### 👤 Source Information")

        col1, col2 = st.columns(2)

        with col1:
            client_name = st.text_input(
                "Client Name",
                value=sr.client_name if selected_sr and selected_sr != "-- Select Service Request --" else "",
                placeholder="Enter client name"
            )

        with col2:
            client_reference = st.text_input(
                "Client Reference Number",
                placeholder="Client's internal reference"
            )

        st.divider()

        # Package Photos
        st.markdown("#### 📷 Package Photos")

        package_photos = st.file_uploader(
            "Upload package photos (optional)",
            accept_multiple_files=True,
            type=['jpg', 'jpeg', 'png'],
            help="Document package condition with photos"
        )

        # Remarks
        remarks = st.text_area(
            "Remarks/Notes",
            placeholder="Any additional notes about the receipt...",
            height=100
        )

        st.divider()

        # Form submission
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.caption("* Required fields")

        with col3:
            submit = st.form_submit_button("📥 Record Receipt", type="primary", use_container_width=True)

        # Process form submission
        if submit:
            # Validate required fields
            if selected_sr == "-- Select Service Request --":
                st.error("❌ Please select a Service Request")
                return

            if expected_count != actual_count and not mismatch_notes:
                st.error("❌ Please provide mismatch notes when counts differ")
                return

            try:
                # Generate receipt number
                receipt_number = generate_receipt_number()

                # Determine if supervisor approval is needed
                requires_approval = expected_count != actual_count or package_condition == "Damaged"

                # Save uploaded photos
                photo_paths = []
                if package_photos:
                    photos_dir = Path("static/receipt_photos")
                    photos_dir.mkdir(parents=True, exist_ok=True)

                    for photo in package_photos:
                        photo_path = photos_dir / f"{receipt_number}_{photo.name}"
                        with open(photo_path, "wb") as f:
                            f.write(photo.getvalue())
                        photo_paths.append(str(photo_path))

                # Create receipt record
                received_datetime = datetime.combine(received_date, received_time)
                sr_obj = sr_options[selected_sr]

                new_receipt = SampleReceipt(
                    receipt_number=receipt_number,
                    service_request_id=sr_obj.id,
                    received_date=received_datetime,
                    received_by_id=1,  # Demo user
                    client_name=client_name,
                    client_reference=client_reference,
                    courier_name=courier_name,
                    tracking_number=tracking_number,
                    package_count=package_count,
                    package_condition=package_condition.lower(),
                    package_photos=photo_paths if photo_paths else None,
                    expected_sample_count=expected_count,
                    actual_sample_count=actual_count,
                    quantity_mismatch=expected_count != actual_count,
                    mismatch_notes=mismatch_notes if mismatch_notes else None,
                    requires_supervisor_approval=requires_approval,
                    status="pending" if requires_approval else "approved",
                    remarks=remarks
                )

                with get_db() as db:
                    db.add(new_receipt)
                    db.commit()

                    # Store receipt info in session state
                    st.session_state.last_receipt = {
                        'receipt_number': receipt_number,
                        'service_request': sr_obj.request_number,
                        'actual_count': actual_count,
                        'status': new_receipt.status
                    }

                if requires_approval:
                    st.warning(f"📋 Receipt {receipt_number} recorded - Pending supervisor approval")
                else:
                    st.success(f"✅ Receipt {receipt_number} recorded and approved!")

                st.info(f"📋 Receipt Number: **{receipt_number}**")

                # Show next steps
                with st.expander("📝 Next Steps"):
                    if requires_approval:
                        st.markdown("""
                        1. ⏳ Wait for supervisor approval
                        2. 📦 Once approved, proceed to Incoming Inspection
                        3. ✅ After inspection passes, samples will be allocated
                        """)
                    else:
                        st.markdown("""
                        1. ✅ Receipt approved
                        2. 📦 Proceed to Incoming Inspection
                        3. ✅ After inspection passes, samples will be allocated
                        """)

            except Exception as e:
                st.error(f"❌ Error creating receipt: {str(e)}")


def render_receipts_list():
    """Render list of sample receipts"""

    st.markdown("### 📋 Sample Receipts")

    try:
        with get_db() as db:
            receipts = db.execute(
                select(SampleReceipt)
                .order_by(desc(SampleReceipt.received_date))
                .limit(50)
            ).scalars().all()

            if not receipts:
                st.info("No sample receipts found")
                return

            # Filters
            col1, col2, col3 = st.columns(3)

            with col1:
                status_filter = st.selectbox(
                    "Filter by Status",
                    ["All", "Pending", "Approved", "Processed", "Rejected"]
                )

            with col2:
                date_filter = st.date_input(
                    "Filter by Date",
                    value=None
                )

            # Summary stats
            total = len(receipts)
            pending = len([r for r in receipts if r.status == "pending"])
            approved = len([r for r in receipts if r.status == "approved"])

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Receipts", total)
            col2.metric("Pending", pending)
            col3.metric("Approved", approved)
            col4.metric("With Mismatches", len([r for r in receipts if r.quantity_mismatch]))

            st.divider()

            # Display receipts
            for receipt in receipts:
                # Apply filters
                if status_filter != "All" and receipt.status != status_filter.lower():
                    continue

                if date_filter and receipt.received_date.date() != date_filter:
                    continue

                # Status badge color
                status_colors = {
                    "pending": "🟡",
                    "approved": "🟢",
                    "processed": "🔵",
                    "rejected": "🔴"
                }
                status_badge = status_colors.get(receipt.status, "⚪")

                with st.expander(
                    f"{status_badge} {receipt.receipt_number} - {receipt.client_name or 'N/A'} ({receipt.received_date.strftime('%Y-%m-%d')})",
                    expanded=False
                ):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.markdown(f"**Receipt Number:** {receipt.receipt_number}")
                        st.markdown(f"**Received Date:** {receipt.received_date.strftime('%Y-%m-%d %H:%M')}")
                        st.markdown(f"**Client:** {receipt.client_name or 'N/A'}")
                        st.markdown(f"**Client Ref:** {receipt.client_reference or 'N/A'}")

                    with col2:
                        st.markdown(f"**Packages:** {receipt.package_count}")
                        st.markdown(f"**Condition:** {receipt.package_condition.title() if receipt.package_condition else 'N/A'}")
                        st.markdown(f"**Courier:** {receipt.courier_name or 'N/A'}")
                        st.markdown(f"**Tracking:** {receipt.tracking_number or 'N/A'}")

                    with col3:
                        st.markdown(f"**Expected Samples:** {receipt.expected_sample_count}")
                        st.markdown(f"**Actual Samples:** {receipt.actual_sample_count}")

                        if receipt.quantity_mismatch:
                            st.error("⚠️ Quantity Mismatch")
                            if receipt.mismatch_notes:
                                st.caption(receipt.mismatch_notes)

                        st.markdown(f"**Status:** {receipt.status.upper()}")

                    # Show photos if available
                    if receipt.package_photos:
                        st.markdown("**Package Photos:**")
                        photo_cols = st.columns(min(len(receipt.package_photos), 4))
                        for idx, photo_path in enumerate(receipt.package_photos[:4]):
                            if Path(photo_path).exists():
                                with photo_cols[idx]:
                                    st.image(photo_path, width=150)

                    # Remarks
                    if receipt.remarks:
                        st.markdown(f"**Remarks:** {receipt.remarks}")

                    # Action buttons
                    if receipt.status == "approved":
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("📦 Go to Inspection", key=f"inspect_{receipt.id}"):
                                st.session_state.receipt_for_inspection = receipt.id
                                st.info("Navigate to Incoming Inspection page")

    except Exception as e:
        st.error(f"Error loading receipts: {str(e)}")


def render_pending_approvals():
    """Render pending approval queue for supervisors"""

    st.markdown("### ⏳ Pending Supervisor Approvals")

    # Check user role (simplified - in production would check actual role)
    user_role = st.session_state.get('user', {}).get('role', 'admin')

    if user_role not in ['admin', 'supervisor']:
        st.warning("Only supervisors can approve receipts")
        return

    try:
        with get_db() as db:
            pending_receipts = db.execute(
                select(SampleReceipt)
                .where(SampleReceipt.requires_supervisor_approval == True)
                .where(SampleReceipt.supervisor_approved == None)
                .order_by(SampleReceipt.received_date)
            ).scalars().all()

            if not pending_receipts:
                st.success("No pending approvals")
                return

            st.warning(f"⏳ {len(pending_receipts)} receipt(s) awaiting approval")

            for receipt in pending_receipts:
                with st.container():
                    st.markdown(f"### {receipt.receipt_number}")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.markdown(f"**Client:** {receipt.client_name or 'N/A'}")
                        st.markdown(f"**Received:** {receipt.received_date.strftime('%Y-%m-%d %H:%M')}")

                    with col2:
                        st.markdown(f"**Expected:** {receipt.expected_sample_count}")
                        st.markdown(f"**Actual:** {receipt.actual_sample_count}")

                        if receipt.quantity_mismatch:
                            st.error(f"⚠️ Mismatch: {receipt.expected_sample_count - receipt.actual_sample_count}")

                    with col3:
                        st.markdown(f"**Condition:** {receipt.package_condition}")

                    # Mismatch details
                    if receipt.mismatch_notes:
                        st.info(f"**Mismatch Notes:** {receipt.mismatch_notes}")

                    # Approval actions
                    col1, col2, col3 = st.columns([1, 1, 2])

                    approval_notes = st.text_input(
                        "Approval Notes",
                        key=f"notes_{receipt.id}",
                        placeholder="Optional notes..."
                    )

                    with col1:
                        if st.button("✅ Approve", key=f"approve_{receipt.id}", type="primary"):
                            receipt.supervisor_approved = True
                            receipt.supervisor_id = 1  # Demo user
                            receipt.approval_date = datetime.utcnow()
                            receipt.approval_notes = approval_notes
                            receipt.status = "approved"
                            db.commit()
                            st.success(f"Receipt {receipt.receipt_number} approved!")
                            st.rerun()

                    with col2:
                        if st.button("❌ Reject", key=f"reject_{receipt.id}"):
                            if not approval_notes:
                                st.error("Please provide rejection reason in notes")
                            else:
                                receipt.supervisor_approved = False
                                receipt.supervisor_id = 1
                                receipt.approval_date = datetime.utcnow()
                                receipt.approval_notes = approval_notes
                                receipt.status = "rejected"
                                db.commit()
                                st.warning(f"Receipt {receipt.receipt_number} rejected")
                                st.rerun()

                    st.divider()

    except Exception as e:
        st.error(f"Error loading pending approvals: {str(e)}")


if __name__ == "__main__":
    main()
