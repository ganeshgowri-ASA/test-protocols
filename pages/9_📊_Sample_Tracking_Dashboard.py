"""
Sample Tracking Dashboard
=========================
Comprehensive dashboard for tracking samples through the testing lifecycle.
Includes QR scanning, status updates, and analytics.
"""

import streamlit as st
from datetime import datetime, timedelta
import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import setup_page_config
from config.database import get_db
from components.navigation import render_header, render_sidebar_navigation
from components.sample_management import (
    decode_sample_qr_code,
    get_sample_by_qr_code,
    update_sample_status,
    get_sample_status_history,
    get_sample_dashboard_stats,
    SAMPLE_STATUS_WORKFLOW
)
from database import (
    Sample, SampleStatusHistory, SampleReceipt, ServiceRequest,
    IncomingInspection, SampleTestAssignment, QRScanLog, SampleStatus
)
from sqlalchemy import select, desc, func
from sqlalchemy.orm import load_only

# Page configuration
setup_page_config(page_title="Sample Tracking", page_icon="📊")

# Render navigation
render_header("Sample Tracking Dashboard", "Track samples through their lifecycle")
render_sidebar_navigation()


def main():
    """Main sample tracking dashboard"""

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard",
        "🔍 QR Scanner",
        "📍 Track Sample",
        "📜 Status History",
        "🗺️ Location Map"
    ])

    with tab1:
        render_dashboard()

    with tab2:
        render_qr_scanner()

    with tab3:
        render_sample_tracker()

    with tab4:
        render_status_history()

    with tab5:
        render_location_map()


def render_dashboard():
    """Render main tracking dashboard with metrics and visualizations"""

    st.markdown("### 📊 Sample Tracking Overview")

    # Get dashboard stats
    stats = get_sample_dashboard_stats()

    # Top metrics row
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Total Samples",
        stats['total'],
        delta=f"+{stats['created_today']} today"
    )
    col2.metric(
        "In Progress",
        stats['in_progress'],
        help="Samples in ASSIGNED or IN_TEST status"
    )
    col3.metric(
        "Completed",
        stats['completed'],
        help="Samples in COMPLETED, ANALYZED, or REPORTED status"
    )
    col4.metric(
        "Awaiting Inspection",
        stats['by_status'].get('received', 0)
    )
    col5.metric(
        "Ready for Testing",
        stats['by_status'].get('allocated', 0)
    )

    st.divider()

    # Status distribution chart
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Sample Status Distribution")

        # Create status data for chart
        status_data = {
            'Status': [],
            'Count': [],
            'Color': []
        }

        status_colors = {
            'received': '#ffd93d',
            'inspected': '#ffb347',
            'allocated': '#6c5ce7',
            'assigned': '#74b9ff',
            'in_test': '#ff7675',
            'completed': '#55efc4',
            'analyzed': '#00cec9',
            'reported': '#00b894',
            'rejected': '#d63031',
            'on_hold': '#636e72'
        }

        for status, count in stats['by_status'].items():
            status_data['Status'].append(status.upper())
            status_data['Count'].append(count)
            status_data['Color'].append(status_colors.get(status, '#dfe6e9'))

        if sum(status_data['Count']) > 0:
            import pandas as pd
            df = pd.DataFrame(status_data)
            st.bar_chart(df.set_index('Status')['Count'])
        else:
            st.info("No samples to display")

    with col2:
        st.markdown("#### Workflow Progress")

        # Pipeline visualization
        workflow_stages = [
            ('RECEIVED', stats['by_status'].get('received', 0), '📥'),
            ('INSPECTED', stats['by_status'].get('inspected', 0), '🔍'),
            ('ALLOCATED', stats['by_status'].get('allocated', 0), '🏷️'),
            ('ASSIGNED', stats['by_status'].get('assigned', 0), '📋'),
            ('IN_TEST', stats['by_status'].get('in_test', 0), '🔬'),
            ('COMPLETED', stats['by_status'].get('completed', 0), '✅'),
            ('ANALYZED', stats['by_status'].get('analyzed', 0), '📊'),
            ('REPORTED', stats['by_status'].get('reported', 0), '📄')
        ]

        for stage, count, icon in workflow_stages:
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.markdown(f"{icon} **{stage}**")
            with col_b:
                st.markdown(f"**{count}**")

    st.divider()

    # Recent activity
    st.markdown("#### Recent Sample Activity")

    with get_db() as db:
        recent_samples = db.execute(
            select(Sample)
            .options(load_only(
                Sample.id, Sample.sample_id, Sample.status,
                Sample.current_location, Sample.updated_at
            ))
            .order_by(desc(Sample.updated_at))
            .limit(10)
        ).scalars().all()

        if recent_samples:
            for sample in recent_samples:
                status_icons = {
                    SampleStatus.RECEIVED: '📥',
                    SampleStatus.INSPECTED: '🔍',
                    SampleStatus.ALLOCATED: '🏷️',
                    SampleStatus.ASSIGNED: '📋',
                    SampleStatus.IN_TEST: '🔬',
                    SampleStatus.COMPLETED: '✅',
                    SampleStatus.ANALYZED: '📊',
                    SampleStatus.REPORTED: '📄',
                    SampleStatus.REJECTED: '❌',
                    SampleStatus.ON_HOLD: '⏸️'
                }
                icon = status_icons.get(sample.status, '⚪')

                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                col1.markdown(f"{icon} **{sample.sample_id}**")
                col2.markdown(f"{sample.current_location or 'Unknown'}")
                col3.markdown(f"{sample.status.value.upper()}")
                col4.markdown(f"{sample.updated_at.strftime('%H:%M') if sample.updated_at else 'N/A'}")
        else:
            st.info("No recent activity")

    # Alerts
    st.markdown("#### Alerts & Notifications")

    with get_db() as db:
        # Samples on hold
        on_hold = db.execute(
            select(func.count(Sample.id))
            .where(Sample.status == SampleStatus.ON_HOLD)
        ).scalar()

        if on_hold > 0:
            st.warning(f"⏸️ {on_hold} sample(s) on hold")

        # Samples stuck in status for more than 7 days
        week_ago = datetime.utcnow() - timedelta(days=7)
        stuck_samples = db.execute(
            select(func.count(Sample.id))
            .where(Sample.status.in_([SampleStatus.ALLOCATED, SampleStatus.ASSIGNED]))
            .where(Sample.updated_at < week_ago)
        ).scalar()

        if stuck_samples > 0:
            st.warning(f"⚠️ {stuck_samples} sample(s) haven't progressed in 7+ days")

        # Rejected samples
        rejected = db.execute(
            select(func.count(Sample.id))
            .where(Sample.status == SampleStatus.REJECTED)
        ).scalar()

        if rejected > 0:
            st.error(f"❌ {rejected} sample(s) rejected")


def render_qr_scanner():
    """Render QR code scanner interface"""

    st.markdown("### 🔍 QR Code Scanner")

    st.info("""
    Scan a sample QR code to:
    - View sample details
    - Update sample status
    - Update sample location
    - Log the scan event
    """)

    # Manual QR code input (for demo - real implementation would use camera)
    col1, col2 = st.columns([3, 1])

    with col1:
        qr_input = st.text_input(
            "Enter QR Code Data",
            placeholder="SAMPLE-2024-00001|PROJECT-2024-00001|2024-01-01T00:00:00",
            help="Format: sample_id|project_id|timestamp"
        )

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        scan_button = st.button("🔍 Lookup", type="primary")

    # Camera input option
    st.markdown("#### Or scan with camera:")
    camera_input = st.camera_input("Capture QR Code", disabled=True, help="Camera scanning coming soon")

    if scan_button and qr_input:
        # Decode QR data
        decoded = decode_sample_qr_code(qr_input)

        if decoded:
            st.success(f"✅ QR Code decoded successfully!")

            # Look up sample
            with get_db() as db:
                sample = db.execute(
                    select(Sample)
                    .options(load_only(
                        Sample.id, Sample.sample_id, Sample.project_id, Sample.sample_type,
                        Sample.manufacturer, Sample.model_number, Sample.serial_number,
                        Sample.status, Sample.current_location, Sample.tests_completed,
                        Sample.tests_total, Sample.qr_code_image_path, Sample.updated_at
                    ))
                    .where(Sample.sample_id == decoded['sample_id'])
                ).scalar()

                if sample:
                    st.markdown("---")
                    st.markdown(f"### Sample: {sample.sample_id}")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.markdown(f"**Sample ID:** {sample.sample_id}")
                        st.markdown(f"**Project ID:** {sample.project_id}")
                        st.markdown(f"**Type:** {sample.sample_type or 'N/A'}")
                        st.markdown(f"**Manufacturer:** {sample.manufacturer or 'N/A'}")

                    with col2:
                        st.markdown(f"**Current Status:** {sample.status.value.upper()}")
                        st.markdown(f"**Current Location:** {sample.current_location or 'Unknown'}")
                        st.markdown(f"**Tests Progress:** {sample.tests_completed or 0}/{sample.tests_total or 0}")

                    with col3:
                        if sample.qr_code_image_path and Path(sample.qr_code_image_path).exists():
                            st.image(sample.qr_code_image_path, width=100)

                    st.divider()

                    # Action options
                    st.markdown("#### Quick Actions")

                    col1, col2 = st.columns(2)

                    with col1:
                        # Status update
                        st.markdown("**Update Status:**")
                        current_status = sample.status.value

                        # Get allowed transitions
                        allowed_transitions = SAMPLE_STATUS_WORKFLOW.get(current_status, [])

                        if allowed_transitions:
                            new_status = st.selectbox(
                                "New Status",
                                options=allowed_transitions,
                                format_func=lambda x: x.upper()
                            )

                            status_reason = st.text_input("Reason for change", placeholder="Optional")

                            if st.button("📝 Update Status", key="update_status"):
                                success, message = update_sample_status(
                                    sample_id=sample.id,
                                    new_status=new_status,
                                    changed_by_id=1,
                                    changed_by_name="Admin User",
                                    change_source="qr_scan",
                                    reason=status_reason or None
                                )
                                if success:
                                    st.success(message)

                                    # Log the scan
                                    scan_log = QRScanLog(
                                        qr_code=qr_input,
                                        decoded_data=decoded,
                                        entity_type='sample',
                                        entity_id=sample.id,
                                        scanned_by_id=1,
                                        scanned_by_name='Admin User',
                                        action_type='status_update',
                                        action_result='success',
                                        status_changed=True,
                                        previous_status=current_status,
                                        new_status=new_status
                                    )
                                    db.add(scan_log)
                                    db.commit()
                                    st.rerun()
                                else:
                                    st.error(message)
                        else:
                            st.info("No further status transitions available")

                    with col2:
                        # Location update
                        st.markdown("**Update Location:**")

                        new_location = st.selectbox(
                            "New Location",
                            options=[
                                "Receiving Area",
                                "Storage Room A",
                                "Storage Room B",
                                "Lab Prep Area",
                                "Testing Lab - Station 1",
                                "Testing Lab - Station 2",
                                "Environmental Chamber",
                                "Analysis Lab",
                                "Completed Storage",
                                "Shipping Area"
                            ],
                            index=0 if not sample.current_location else None
                        )

                        if st.button("📍 Update Location", key="update_location"):
                            sample.current_location = new_location
                            sample.updated_at = datetime.utcnow()

                            # Log location change in history
                            history = SampleStatusHistory(
                                sample_id=sample.id,
                                previous_status=sample.status.value,
                                new_status=sample.status.value,
                                previous_location=sample.current_location,
                                new_location=new_location,
                                changed_by_id=1,
                                changed_by_name="Admin User",
                                change_source="qr_scan",
                                notes="Location update via QR scan"
                            )
                            db.add(history)

                            # Log the scan
                            scan_log = QRScanLog(
                                qr_code=qr_input,
                                decoded_data=decoded,
                                entity_type='sample',
                                entity_id=sample.id,
                                scanned_by_id=1,
                                scanned_by_name='Admin User',
                                scan_location=new_location,
                                action_type='location_update',
                                action_result='success'
                            )
                            db.add(scan_log)
                            db.commit()

                            st.success(f"Location updated to: {new_location}")
                            st.rerun()

                else:
                    st.warning("Sample not found in database")
        else:
            st.error("Invalid QR code format")

    # Recent scan log
    st.markdown("---")
    st.markdown("#### Recent Scan Log")

    with get_db() as db:
        recent_scans = db.execute(
            select(QRScanLog)
            .order_by(desc(QRScanLog.scan_timestamp))
            .limit(10)
        ).scalars().all()

        if recent_scans:
            for scan in recent_scans:
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                col1.markdown(f"**{scan.qr_code[:30]}...**" if len(scan.qr_code) > 30 else f"**{scan.qr_code}**")
                col2.markdown(f"{scan.action_type or 'N/A'}")
                col3.markdown(f"{scan.action_result or 'N/A'}")
                col4.markdown(f"{scan.scan_timestamp.strftime('%H:%M')}")
        else:
            st.info("No recent scans")


def render_sample_tracker():
    """Render individual sample tracking interface"""

    st.markdown("### 📍 Track Individual Sample")

    # Search options
    col1, col2 = st.columns(2)

    with col1:
        search_type = st.radio(
            "Search by",
            ["Sample ID", "Project ID", "Serial Number"],
            horizontal=True
        )

    with col2:
        search_value = st.text_input(
            f"Enter {search_type}",
            placeholder=f"Enter {search_type.lower()}..."
        )

    if search_value:
        with get_db() as db:
            # Define columns to load - exclude specifications which may not exist in DB
            sample_columns = load_only(
                Sample.id, Sample.sample_id, Sample.project_id, Sample.sample_type,
                Sample.manufacturer, Sample.model_number, Sample.serial_number,
                Sample.status, Sample.current_location, Sample.tests_completed,
                Sample.tests_total, Sample.overall_result, Sample.qr_code_image_path,
                Sample.created_at, Sample.updated_at
            )
            if search_type == "Sample ID":
                sample = db.execute(
                    select(Sample)
                    .options(sample_columns)
                    .where(Sample.sample_id.contains(search_value.upper()))
                ).scalar()
            elif search_type == "Project ID":
                sample = db.execute(
                    select(Sample)
                    .options(sample_columns)
                    .where(Sample.project_id.contains(search_value.upper()))
                ).scalar()
            else:
                sample = db.execute(
                    select(Sample)
                    .options(sample_columns)
                    .where(Sample.serial_number.contains(search_value))
                ).scalar()

            if sample:
                render_sample_details(sample, db)
            else:
                st.warning("No sample found matching your search")


def render_sample_details(sample, db):
    """Render detailed sample information"""

    st.markdown("---")
    st.markdown(f"## Sample: {sample.sample_id}")

    # Status indicator
    status_colors = {
        SampleStatus.RECEIVED: '#ffd93d',
        SampleStatus.INSPECTED: '#ffb347',
        SampleStatus.ALLOCATED: '#6c5ce7',
        SampleStatus.ASSIGNED: '#74b9ff',
        SampleStatus.IN_TEST: '#ff7675',
        SampleStatus.COMPLETED: '#55efc4',
        SampleStatus.ANALYZED: '#00cec9',
        SampleStatus.REPORTED: '#00b894',
        SampleStatus.REJECTED: '#d63031',
        SampleStatus.ON_HOLD: '#636e72'
    }

    status_color = status_colors.get(sample.status, '#dfe6e9')
    st.markdown(
        f'<div style="background-color: {status_color}; padding: 10px; border-radius: 5px; text-align: center;">'
        f'<strong>Current Status: {sample.status.value.upper()}</strong></div>',
        unsafe_allow_html=True
    )

    # Main info
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### Sample Information")
        st.markdown(f"**Sample ID:** {sample.sample_id}")
        st.markdown(f"**Project ID:** {sample.project_id or 'N/A'}")
        st.markdown(f"**Type:** {sample.sample_type or 'N/A'}")
        st.markdown(f"**Manufacturer:** {sample.manufacturer or 'N/A'}")
        st.markdown(f"**Model:** {sample.model_number or 'N/A'}")
        st.markdown(f"**Serial Number:** {sample.serial_number or 'N/A'}")

    with col2:
        st.markdown("### Current State")
        st.markdown(f"**Status:** {sample.status.value.upper()}")
        st.markdown(f"**Location:** {sample.current_location or 'Unknown'}")
        st.markdown(f"**Tests Completed:** {sample.tests_completed or 0}/{sample.tests_total or 0}")
        st.markdown(f"**Overall Result:** {sample.overall_result or 'Pending'}")

        # Progress bar
        if sample.tests_total and sample.tests_total > 0:
            progress = (sample.tests_completed or 0) / sample.tests_total
            st.progress(progress)

    with col3:
        st.markdown("### QR Code")
        if sample.qr_code_image_path and Path(sample.qr_code_image_path).exists():
            st.image(sample.qr_code_image_path, width=150)
            with open(sample.qr_code_image_path, 'rb') as f:
                st.download_button(
                    "📥 Download QR",
                    data=f.read(),
                    file_name=f"{sample.sample_id}_qr.png",
                    mime="image/png"
                )

    # Timeline / History
    st.markdown("---")
    st.markdown("### Sample Journey Timeline")

    history = get_sample_status_history(sample.id)

    if history:
        for idx, event in enumerate(history):
            col1, col2, col3 = st.columns([1, 2, 2])

            with col1:
                st.markdown(f"**{event['changed_at'][:10] if event['changed_at'] else 'N/A'}**")
                st.caption(event['changed_at'][11:16] if event['changed_at'] else '')

            with col2:
                st.markdown(f"**{event['previous_status'] or 'Initial'} → {event['new_status'].upper()}**")
                if event['change_source']:
                    st.caption(f"Source: {event['change_source']}")

            with col3:
                if event['new_location']:
                    st.markdown(f"📍 {event['new_location']}")
                if event['reason']:
                    st.caption(event['reason'])
                if event['changed_by']:
                    st.caption(f"By: {event['changed_by']}")

            if idx < len(history) - 1:
                st.markdown("---")
    else:
        st.info("No history available")


def render_status_history():
    """Render comprehensive status history view"""

    st.markdown("### 📜 Status Change History")

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All"] + [s.value.upper() for s in SampleStatus]
        )

    with col2:
        date_range = st.date_input(
            "Date Range",
            value=(datetime.now() - timedelta(days=7), datetime.now())
        )

    with col3:
        source_filter = st.selectbox(
            "Change Source",
            ["All", "manual", "qr_scan", "system", "workflow"]
        )

    with get_db() as db:
        query = select(SampleStatusHistory).order_by(desc(SampleStatusHistory.changed_at)).limit(100)

        if status_filter != "All":
            query = query.where(SampleStatusHistory.new_status == status_filter.lower())

        if source_filter != "All":
            query = query.where(SampleStatusHistory.change_source == source_filter)

        history_records = db.execute(query).scalars().all()

        if history_records:
            for record in history_records:
                with st.expander(
                    f"{record.changed_at.strftime('%Y-%m-%d %H:%M') if record.changed_at else 'N/A'} | "
                    f"Sample {record.sample_id} | {record.previous_status or 'Initial'} → {record.new_status.upper()}"
                ):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown(f"**Previous Status:** {record.previous_status or 'Initial'}")
                        st.markdown(f"**New Status:** {record.new_status.upper()}")
                        st.markdown(f"**Change Source:** {record.change_source or 'N/A'}")
                        st.markdown(f"**Changed By:** {record.changed_by_name or 'System'}")

                    with col2:
                        st.markdown(f"**Previous Location:** {record.previous_location or 'N/A'}")
                        st.markdown(f"**New Location:** {record.new_location or 'N/A'}")
                        if record.reason:
                            st.markdown(f"**Reason:** {record.reason}")
                        if record.notes:
                            st.markdown(f"**Notes:** {record.notes}")
        else:
            st.info("No history records found")


def render_location_map():
    """Render sample location map view"""

    st.markdown("### 🗺️ Sample Location Map")

    st.info("Visual representation of sample locations in the facility")

    # Get location counts
    with get_db() as db:
        locations = db.execute(
            select(Sample.current_location, func.count(Sample.id))
            .group_by(Sample.current_location)
        ).all()

        location_counts = {loc or 'Unknown': count for loc, count in locations}

    # Define facility layout
    facility_locations = [
        ("Receiving Area", "📥"),
        ("Storage Room A", "📦"),
        ("Storage Room B", "📦"),
        ("Lab Prep Area", "🔧"),
        ("Testing Lab - Station 1", "🔬"),
        ("Testing Lab - Station 2", "🔬"),
        ("Environmental Chamber", "🌡️"),
        ("Analysis Lab", "📊"),
        ("Completed Storage", "✅"),
        ("Shipping Area", "📤")
    ]

    # Display as grid
    cols = st.columns(3)

    for idx, (location, icon) in enumerate(facility_locations):
        col_idx = idx % 3
        count = location_counts.get(location, 0)

        with cols[col_idx]:
            st.markdown(
                f"""
                <div style="
                    border: 2px solid {'#00b894' if count > 0 else '#dfe6e9'};
                    border-radius: 10px;
                    padding: 15px;
                    margin: 5px;
                    text-align: center;
                    background-color: {'#f8f9fa' if count > 0 else '#fff'};
                ">
                    <h3>{icon}</h3>
                    <p><strong>{location}</strong></p>
                    <h2 style="color: {'#00b894' if count > 0 else '#636e72'};">{count}</h2>
                    <p style="color: #636e72;">samples</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    # Samples by location table
    st.markdown("---")
    st.markdown("### Samples by Location")

    for location, icon in facility_locations:
        count = location_counts.get(location, 0)
        if count > 0:
            with st.expander(f"{icon} {location} ({count} samples)"):
                with get_db() as db:
                    samples = db.execute(
                        select(Sample)
                        .options(load_only(
                            Sample.id, Sample.sample_id, Sample.status, Sample.updated_at
                        ))
                        .where(Sample.current_location == location)
                        .limit(20)
                    ).scalars().all()

                    for sample in samples:
                        col1, col2, col3 = st.columns([2, 1, 1])
                        col1.markdown(f"**{sample.sample_id}**")
                        col2.markdown(f"{sample.status.value.upper()}")
                        col3.markdown(f"{sample.updated_at.strftime('%Y-%m-%d') if sample.updated_at else 'N/A'}")


if __name__ == "__main__":
    main()
