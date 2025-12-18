"""
Sample Registration Module
===========================
Register samples after inspection by allocating unique Sample IDs and QR codes.
Generate route cards and prepare samples for testing workflow.
"""

import streamlit as st
from datetime import datetime
import sys
from pathlib import Path
import base64

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import setup_page_config
from config.database import get_db
from config.protocols_registry import get_cached_protocol_registry
from components.navigation import render_header, render_sidebar_navigation
from components.sample_management import (
    generate_sample_id,
    generate_project_id,
    generate_sample_qr_code,
    generate_route_card_pdf,
    generate_route_card_number,
    allocate_samples_from_inspection
)
from database import (
    Sample, SampleReceipt, ServiceRequest, IncomingInspection,
    RouteCard, SampleStatus, InspectionStatus
)
from sqlalchemy import select, desc, and_
from sqlalchemy.orm import load_only

# Page configuration
setup_page_config(page_title="Sample Registration", page_icon="🏷️")

# Render navigation
render_header("Sample Registration", "Register samples and generate QR codes")
render_sidebar_navigation()


def main():
    """Main sample allocation page"""

    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏷️ Allocate Samples",
        "📋 Allocated Samples",
        "📄 Route Cards",
        "📊 Batch Allocation"
    ])

    with tab1:
        render_allocation_form()

    with tab2:
        render_allocated_samples_list()

    with tab3:
        render_route_cards()

    with tab4:
        render_batch_allocation()


def render_allocation_form():
    """Render form to allocate samples from passed inspections"""

    st.markdown("### Allocate New Samples")

    st.info("""
    **Workflow Gate:** Only samples that have **PASSED** inspection can be allocated.
    Allocation triggers:
    - Generation of unique Sample ID (SAMPLE-YYYY-XXXXX)
    - Generation of unique Project ID (PROJECT-YYYY-XXXXX)
    - QR Code generation
    - Route Card creation
    """)

    # Get passed inspections that haven't been allocated
    with get_db() as db:
        passed_inspections = db.execute(
            select(IncomingInspection)
            .where(IncomingInspection.status == InspectionStatus.PASSED)
            .where(IncomingInspection.allocation_triggered == False)
            .order_by(desc(IncomingInspection.inspection_date))
        ).scalars().all()

        if not passed_inspections:
            st.success("All passed inspections have been allocated!")

            # Show option to view allocated samples
            if st.button("📋 View Allocated Samples"):
                st.session_state.show_allocated = True

            return

        st.warning(f"⏳ {len(passed_inspections)} inspection(s) pending allocation")

    # Display inspections ready for allocation
    for inspection in passed_inspections:
        with st.container():
            st.markdown(f"### Inspection: {inspection.inspection_number}")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"**Sample ID:** {inspection.sample_id}")
                st.markdown(f"**Inspection Date:** {inspection.inspection_date.strftime('%Y-%m-%d') if inspection.inspection_date else 'N/A'}")

            with col2:
                # Get service request details
                with get_db() as db:
                    sr = db.execute(
                        select(ServiceRequest)
                        .where(ServiceRequest.id == inspection.service_request_id)
                    ).scalar()

                if sr:
                    st.markdown(f"**Service Request:** {sr.request_number}")
                    st.markdown(f"**Client:** {sr.client_name}")
                    st.markdown(f"**Sample Type:** {sr.sample_type}")

            with col3:
                st.markdown(f"**Status:** ✅ PASSED")
                if inspection.remarks:
                    st.markdown(f"**Remarks:** {inspection.remarks}")

            # Physical measurements
            if any([inspection.length_mm, inspection.width_mm, inspection.weight_kg]):
                st.markdown("**Physical Measurements:**")
                measurements = []
                if inspection.length_mm:
                    measurements.append(f"L: {inspection.length_mm}mm")
                if inspection.width_mm:
                    measurements.append(f"W: {inspection.width_mm}mm")
                if inspection.thickness_mm:
                    measurements.append(f"T: {inspection.thickness_mm}mm")
                if inspection.weight_kg:
                    measurements.append(f"Weight: {inspection.weight_kg}kg")
                st.caption(" | ".join(measurements))

            st.divider()

            # Allocation options
            col1, col2 = st.columns(2)

            with col1:
                sample_count = st.number_input(
                    "Number of samples to allocate",
                    min_value=1,
                    max_value=sr.sample_count if sr else 10,
                    value=1,
                    key=f"count_{inspection.id}"
                )

            with col2:
                initial_location = st.selectbox(
                    "Initial Location",
                    options=["Receiving Area", "Storage Room A", "Storage Room B", "Lab Prep Area", "Testing Lab"],
                    key=f"location_{inspection.id}"
                )

            # Generate route card option
            generate_route_card = st.checkbox(
                "Generate Route Card PDF",
                value=True,
                key=f"route_card_{inspection.id}"
            )

            # Allocate button
            if st.button(f"🏷️ Allocate Sample(s)", key=f"allocate_{inspection.id}", type="primary"):
                try:
                    with get_db() as db:
                        # Generate Project ID for this batch
                        project_id = generate_project_id()

                        allocated_samples = []

                        for i in range(sample_count):
                            # Generate unique Sample ID
                            sample_id_code = generate_sample_id()

                            # Generate QR Code
                            qr_code_string, qr_bytes, qr_path = generate_sample_qr_code(
                                sample_id_code,
                                project_id,
                                additional_data={
                                    'service_request': sr.request_number if sr else None,
                                    'client': sr.client_name if sr else None,
                                    'inspection': inspection.inspection_number
                                }
                            )

                            # Create sample record
                            sample = Sample(
                                sample_id=sample_id_code,
                                project_id=project_id,
                                service_request_id=inspection.service_request_id,
                                inspection_id=inspection.id,
                                sample_type=sr.sample_type if sr else None,
                                manufacturer=sr.manufacturer if sr else None,
                                model_number=sr.model_number if sr else None,
                                serial_number=sr.serial_numbers[i] if sr and sr.serial_numbers and i < len(sr.serial_numbers) else None,
                                length_mm=inspection.length_mm,
                                width_mm=inspection.width_mm,
                                thickness_mm=inspection.thickness_mm,
                                weight_kg=inspection.weight_kg,
                                qr_code=qr_code_string,
                                qr_code_image_path=qr_path,
                                qr_data={
                                    'sample_id': sample_id_code,
                                    'project_id': project_id,
                                    'allocated_at': datetime.utcnow().isoformat()
                                },
                                status=SampleStatus.ALLOCATED,
                                current_location=initial_location,
                                storage_location=initial_location,
                                allocation_date=datetime.utcnow(),
                                allocated_by_id=1,  # Demo user
                                assigned_protocol_ids=sr.requested_protocols if sr else [],
                                tests_total=len(sr.requested_protocols) if sr and sr.requested_protocols else 0
                            )
                            db.add(sample)
                            db.flush()

                            allocated_samples.append({
                                'id': sample.id,
                                'sample_id': sample_id_code,
                                'qr_path': qr_path,
                                'qr_bytes': qr_bytes
                            })

                        # Mark inspection as allocated
                        inspection_record = db.execute(
                            select(IncomingInspection)
                            .where(IncomingInspection.id == inspection.id)
                        ).scalar()
                        if inspection_record:
                            inspection_record.allocation_triggered = True
                            inspection_record.allocated_sample_id = allocated_samples[0]['id']

                        # Generate route card if requested
                        route_card_path = None
                        if generate_route_card and allocated_samples:
                            # Get protocols for route card
                            registry = get_cached_protocol_registry()
                            protocols_list = []
                            if sr and sr.requested_protocols:
                                for pid in sr.requested_protocols:
                                    protocol = registry.get_protocol(pid)
                                    if protocol:
                                        protocols_list.append({
                                            'id': protocol.protocol_id,
                                            'name': protocol.name,
                                            'status': 'Pending'
                                        })

                            # Generate PDF
                            pdf_bytes, pdf_path = generate_route_card_pdf(
                                sample_id=allocated_samples[0]['sample_id'],
                                project_id=project_id,
                                service_request_number=sr.request_number if sr else "N/A",
                                client_name=sr.client_name if sr else "N/A",
                                sample_type=sr.sample_type if sr else "Unknown",
                                protocols=protocols_list,
                                qr_code_path=allocated_samples[0]['qr_path']
                            )

                            # Create route card record
                            route_card = RouteCard(
                                route_card_number=generate_route_card_number(),
                                sample_id=allocated_samples[0]['id'],
                                project_id=project_id,
                                service_request_id=sr.id if sr else None,
                                title=f"Route Card - {allocated_samples[0]['sample_id']}",
                                workflow_steps=[
                                    {'step': 1, 'name': 'Receipt', 'status': 'completed'},
                                    {'step': 2, 'name': 'Inspection', 'status': 'completed'},
                                    {'step': 3, 'name': 'Allocation', 'status': 'completed'},
                                    {'step': 4, 'name': 'Testing', 'status': 'pending'},
                                    {'step': 5, 'name': 'Analysis', 'status': 'pending'},
                                    {'step': 6, 'name': 'Reporting', 'status': 'pending'}
                                ],
                                current_step=4,
                                total_steps=6,
                                assigned_protocols=sr.requested_protocols if sr else [],
                                pdf_path=pdf_path,
                                pdf_generated_at=datetime.utcnow(),
                                status='active',
                                created_by_id=1
                            )
                            db.add(route_card)
                            route_card_path = pdf_path

                        db.commit()

                        # Success message
                        st.success(f"✅ Successfully allocated {len(allocated_samples)} sample(s)!")

                        # Display allocated sample info
                        for sample_info in allocated_samples:
                            st.markdown(f"""
                            **Sample ID:** `{sample_info['sample_id']}`
                            **Project ID:** `{project_id}`
                            """)

                            # Display QR code
                            if sample_info['qr_path'] and Path(sample_info['qr_path']).exists():
                                col1, col2 = st.columns([1, 2])
                                with col1:
                                    st.image(sample_info['qr_path'], caption="Sample QR Code", width=150)
                                with col2:
                                    # Download button for QR code
                                    with open(sample_info['qr_path'], 'rb') as f:
                                        qr_bytes = f.read()
                                    st.download_button(
                                        label="📥 Download QR Code",
                                        data=qr_bytes,
                                        file_name=f"{sample_info['sample_id']}_qr.png",
                                        mime="image/png"
                                    )

                        # Route card download
                        if route_card_path and Path(route_card_path).exists():
                            st.markdown("---")
                            st.markdown("**📄 Route Card Generated**")
                            with open(route_card_path, 'rb') as f:
                                pdf_bytes = f.read()
                            st.download_button(
                                label="📥 Download Route Card PDF",
                                data=pdf_bytes,
                                file_name=f"route_card_{allocated_samples[0]['sample_id']}.pdf",
                                mime="application/pdf"
                            )

                        st.rerun()

                except Exception as e:
                    st.error(f"❌ Error allocating samples: {str(e)}")

            st.markdown("---")


def render_allocated_samples_list():
    """Render list of allocated samples"""

    st.markdown("### 📋 Allocated Samples")

    try:
        with get_db() as db:
            # Use load_only to exclude notes column that may not exist in database
            samples = db.execute(
                select(Sample).options(
                    load_only(
                        Sample.id,
                        Sample.sample_id,
                        Sample.project_id,
                        Sample.sample_type,
                        Sample.manufacturer,
                        Sample.status,
                        Sample.current_location,
                        Sample.allocation_date,
                        Sample.tests_completed,
                        Sample.tests_total,
                        Sample.qr_code_image_path
                    )
                )
                .order_by(desc(Sample.allocation_date))
                .limit(100)
            ).scalars().all()

            if not samples:
                st.info("No samples have been allocated yet")
                return

            # Summary stats
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Samples", len(samples))
            col2.metric("Allocated", len([s for s in samples if s.status == SampleStatus.ALLOCATED]))
            col3.metric("In Testing", len([s for s in samples if s.status == SampleStatus.IN_TEST]))
            col4.metric("Completed", len([s for s in samples if s.status == SampleStatus.COMPLETED]))

            st.divider()

            # Filters
            col1, col2, col3 = st.columns(3)

            with col1:
                status_filter = st.selectbox(
                    "Filter by Status",
                    ["All"] + [s.value.title() for s in SampleStatus]
                )

            with col2:
                project_filter = st.text_input("Filter by Project ID", placeholder="PROJECT-2024-...")

            with col3:
                search_query = st.text_input("Search Sample ID", placeholder="SAMPLE-2024-...")

            # Display samples
            for sample in samples:
                # Apply filters
                if status_filter != "All" and sample.status.value != status_filter.lower():
                    continue
                if project_filter and project_filter not in (sample.project_id or ""):
                    continue
                if search_query and search_query.upper() not in sample.sample_id.upper():
                    continue

                status_colors = {
                    SampleStatus.RECEIVED: "🟡",
                    SampleStatus.INSPECTED: "🟡",
                    SampleStatus.ALLOCATED: "🔵",
                    SampleStatus.ASSIGNED: "🔵",
                    SampleStatus.IN_TEST: "🟠",
                    SampleStatus.COMPLETED: "🟢",
                    SampleStatus.ANALYZED: "🟢",
                    SampleStatus.REPORTED: "✅",
                    SampleStatus.REJECTED: "🔴",
                    SampleStatus.ON_HOLD: "⏸️"
                }
                status_icon = status_colors.get(sample.status, "⚪")

                with st.expander(
                    f"{status_icon} {sample.sample_id} | {sample.project_id or 'No Project'} | {sample.status.value.upper()}",
                    expanded=False
                ):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.markdown(f"**Sample ID:** {sample.sample_id}")
                        st.markdown(f"**Project ID:** {sample.project_id or 'N/A'}")
                        st.markdown(f"**Type:** {sample.sample_type or 'N/A'}")
                        st.markdown(f"**Manufacturer:** {sample.manufacturer or 'N/A'}")

                    with col2:
                        st.markdown(f"**Status:** {sample.status.value.upper()}")
                        st.markdown(f"**Location:** {sample.current_location or 'N/A'}")
                        st.markdown(f"**Allocated:** {sample.allocation_date.strftime('%Y-%m-%d') if sample.allocation_date else 'N/A'}")
                        st.markdown(f"**Tests:** {sample.tests_completed or 0}/{sample.tests_total or 0}")

                    with col3:
                        # QR Code
                        if sample.qr_code_image_path and Path(sample.qr_code_image_path).exists():
                            st.image(sample.qr_code_image_path, width=100)

                            with open(sample.qr_code_image_path, 'rb') as f:
                                st.download_button(
                                    "📥 QR Code",
                                    data=f.read(),
                                    file_name=f"{sample.sample_id}_qr.png",
                                    mime="image/png",
                                    key=f"qr_{sample.id}"
                                )

                    # Action buttons
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        if st.button("📍 Update Location", key=f"loc_{sample.id}"):
                            st.session_state[f"update_location_{sample.id}"] = True

                    with col2:
                        if st.button("🔬 Assign to Test", key=f"test_{sample.id}"):
                            st.info("Navigate to Test Assignment page")

                    # Location update form
                    if st.session_state.get(f"update_location_{sample.id}"):
                        new_location = st.selectbox(
                            "New Location",
                            ["Receiving Area", "Storage Room A", "Storage Room B", "Lab Prep Area",
                             "Testing Lab", "Environmental Chamber", "Completed Storage"],
                            key=f"new_loc_{sample.id}"
                        )
                        if st.button("Update", key=f"confirm_loc_{sample.id}"):
                            sample.current_location = new_location
                            db.commit()
                            st.success("Location updated!")
                            st.rerun()

    except Exception as e:
        st.error(f"Error loading samples: {str(e)}")


def render_route_cards():
    """Render route cards management"""

    st.markdown("### 📄 Route Cards")

    try:
        with get_db() as db:
            route_cards = db.execute(
                select(RouteCard)
                .order_by(desc(RouteCard.created_at))
                .limit(50)
            ).scalars().all()

            if not route_cards:
                st.info("No route cards have been generated yet")
                return

            for rc in route_cards:
                status_colors = {
                    'draft': '🟡',
                    'active': '🟢',
                    'completed': '✅',
                    'cancelled': '🔴'
                }
                status_icon = status_colors.get(rc.status, '⚪')

                with st.expander(
                    f"{status_icon} {rc.route_card_number} | Step {rc.current_step}/{rc.total_steps}",
                    expanded=False
                ):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown(f"**Route Card:** {rc.route_card_number}")
                        st.markdown(f"**Project ID:** {rc.project_id or 'N/A'}")
                        st.markdown(f"**Status:** {rc.status.upper()}")
                        st.markdown(f"**Created:** {rc.created_at.strftime('%Y-%m-%d') if rc.created_at else 'N/A'}")

                    with col2:
                        # Progress bar
                        if rc.total_steps:
                            progress = rc.current_step / rc.total_steps
                            st.progress(progress)
                            st.caption(f"Progress: {rc.current_step}/{rc.total_steps} steps")

                    # Workflow steps
                    if rc.workflow_steps:
                        st.markdown("**Workflow Steps:**")
                        for step in rc.workflow_steps:
                            step_status = step.get('status', 'pending')
                            step_icon = '✅' if step_status == 'completed' else '⏳' if step_status == 'in_progress' else '⬜'
                            st.markdown(f"{step_icon} Step {step.get('step', '?')}: {step.get('name', 'Unknown')}")

                    # Download PDF
                    if rc.pdf_path and Path(rc.pdf_path).exists():
                        with open(rc.pdf_path, 'rb') as f:
                            st.download_button(
                                "📥 Download Route Card PDF",
                                data=f.read(),
                                file_name=f"{rc.route_card_number}.pdf",
                                mime="application/pdf",
                                key=f"pdf_{rc.id}"
                            )

    except Exception as e:
        st.error(f"Error loading route cards: {str(e)}")


def render_batch_allocation():
    """Render batch allocation interface"""

    st.markdown("### 📊 Batch Allocation")

    st.info("""
    Use batch allocation to process multiple inspections at once.
    All selected inspections must have PASSED status.
    """)

    with get_db() as db:
        # Get all passed inspections pending allocation
        pending = db.execute(
            select(IncomingInspection)
            .where(IncomingInspection.status == InspectionStatus.PASSED)
            .where(IncomingInspection.allocation_triggered == False)
        ).scalars().all()

        if not pending:
            st.success("No inspections pending allocation")
            return

        st.markdown(f"**{len(pending)} inspection(s) ready for batch allocation**")

        # Selection checkboxes
        selected_ids = []
        for insp in pending:
            if st.checkbox(
                f"{insp.inspection_number} - {insp.sample_id}",
                key=f"batch_{insp.id}"
            ):
                selected_ids.append(insp.id)

        if selected_ids:
            st.markdown(f"**Selected: {len(selected_ids)} inspection(s)**")

            initial_location = st.selectbox(
                "Initial Location for All",
                ["Receiving Area", "Storage Room A", "Storage Room B", "Lab Prep Area"]
            )

            if st.button(f"🏷️ Allocate {len(selected_ids)} Sample(s)", type="primary"):
                success_count = 0
                for insp_id in selected_ids:
                    try:
                        insp = db.execute(
                            select(IncomingInspection)
                            .where(IncomingInspection.id == insp_id)
                        ).scalar()

                        if insp:
                            samples = allocate_samples_from_inspection(
                                inspection_id=insp_id,
                                service_request_id=insp.service_request_id,
                                allocated_by_id=1,
                                sample_count=1
                            )
                            if samples:
                                success_count += 1
                    except Exception as e:
                        st.error(f"Error allocating inspection {insp_id}: {str(e)}")

                st.success(f"✅ Successfully allocated {success_count} sample(s)")
                st.rerun()


if __name__ == "__main__":
    main()
