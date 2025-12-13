"""
Sample Allocation to Test Protocols Module
==========================================
Allocate received samples to specific test protocols and testing schedules.
Bridge between sample receipt and test execution with resource management.
"""

import streamlit as st
from datetime import datetime, timedelta
import sys
from pathlib import Path
import plotly.figure_factory as ff
import plotly.graph_objects as go
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import setup_page_config
from config.database import get_db
from config.protocols_registry import get_cached_protocol_registry
from components.navigation import render_header, render_sidebar_navigation
from database import (
    Sample, SampleAllocation, TestProtocol, Equipment, User,
    SampleStatus, AllocationStatus, EquipmentStatus, UserRole
)
from sqlalchemy import select, desc, and_, or_, func

# Page configuration
setup_page_config(page_title="Sample Allocation", page_icon="🎯")

# Render navigation
render_header("Sample Allocation", "Assign samples to test protocols with resource scheduling")
render_sidebar_navigation()


def generate_allocation_number():
    """Generate unique allocation number"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"ALLOC-{timestamp}"


def check_equipment_availability(equipment_id, start, end, exclude_allocation_id=None):
    """
    Check if equipment is available during the specified time period.
    Returns (is_available, conflicts)
    """
    with get_db() as db:
        query = select(SampleAllocation).where(
            and_(
                SampleAllocation.equipment_id == equipment_id,
                SampleAllocation.scheduled_start < end,
                SampleAllocation.scheduled_end > start,
                SampleAllocation.status.in_([AllocationStatus.SCHEDULED, AllocationStatus.IN_PROGRESS])
            )
        )
        
        if exclude_allocation_id:
            query = query.where(SampleAllocation.id != exclude_allocation_id)
        
        conflicts = db.execute(query).scalars().all()
        return len(conflicts) == 0, conflicts


def check_technician_availability(technician_id, start, end, exclude_allocation_id=None):
    """
    Check if technician is available during the specified time period.
    Returns (is_available, conflicts, workload_count)
    """
    with get_db() as db:
        query = select(SampleAllocation).where(
            and_(
                SampleAllocation.technician_id == technician_id,
                SampleAllocation.scheduled_start < end,
                SampleAllocation.scheduled_end > start,
                SampleAllocation.status.in_([AllocationStatus.SCHEDULED, AllocationStatus.IN_PROGRESS])
            )
        )
        
        if exclude_allocation_id:
            query = query.where(SampleAllocation.id != exclude_allocation_id)
        
        conflicts = db.execute(query).scalars().all()
        
        # Count total workload for the technician
        workload_query = select(func.count()).select_from(SampleAllocation).where(
            and_(
                SampleAllocation.technician_id == technician_id,
                SampleAllocation.status.in_([AllocationStatus.SCHEDULED, AllocationStatus.IN_PROGRESS])
            )
        )
        workload_count = db.execute(workload_query).scalar()
        
        return len(conflicts) == 0, conflicts, workload_count


def main():
    """Main sample allocation page"""

    # Tabs for different views
    tab1, tab2, tab3 = st.tabs([
        "🎯 Allocate Sample",
        "📊 Allocation Schedule",
        "🔍 Search Allocations"
    ])

    with tab1:
        render_allocation_form()

    with tab2:
        render_allocation_schedule()

    with tab3:
        render_search_allocations()


def render_allocation_form():
    """Render form to allocate samples to test protocols"""

    st.markdown("### 🎯 Allocate Sample to Test Protocols")

    st.info("""
    **Workflow:** Assign received samples to specific test protocols with resource allocation.
    - Select sample with status "Received" or "Allocated"
    - Choose one or multiple test protocols
    - Assign equipment and technician
    - Schedule start and end dates
    - System checks for resource conflicts
    """)

    with get_db() as db:
        # Get samples available for allocation (Received or Allocated status)
        samples = db.execute(
            select(Sample)
            .where(Sample.status.in_([SampleStatus.RECEIVED, SampleStatus.ALLOCATED, SampleStatus.ASSIGNED]))
            .order_by(desc(Sample.allocation_date))
        ).scalars().all()

        if not samples:
            st.warning("No samples available for allocation. Please ensure samples are received first.")
            return

        # Sample selection
        st.markdown("#### 1. Select Sample")
        
        col1, col2 = st.columns(2)
        
        with col1:
            sample_options = {
                f"{s.sample_id} - {s.sample_type or 'Unknown'} ({s.status.value})": s 
                for s in samples
            }
            
            selected_sample_key = st.selectbox(
                "Sample",
                options=list(sample_options.keys()),
                help="Select a sample to allocate to test protocols"
            )
            
            selected_sample = sample_options[selected_sample_key]

        with col2:
            # Display sample details
            st.markdown("**Sample Details:**")
            st.caption(f"ID: {selected_sample.sample_id}")
            st.caption(f"Type: {selected_sample.sample_type or 'N/A'}")
            st.caption(f"Manufacturer: {selected_sample.manufacturer or 'N/A'}")
            st.caption(f"Status: {selected_sample.status.value}")
            st.caption(f"Location: {selected_sample.current_location or 'N/A'}")

        st.divider()

        # Protocol selection
        st.markdown("#### 2. Select Test Protocol(s)")
        
        registry = get_cached_protocol_registry()
        protocols = registry.get_all_protocols()
        
        # Group protocols by category
        protocols_by_category = {}
        for protocol in protocols:
            category = protocol.category or "Other"
            if category not in protocols_by_category:
                protocols_by_category[category] = []
            protocols_by_category[category].append(protocol)

        # Multi-select with category grouping
        selected_protocols = []
        
        for category, cat_protocols in sorted(protocols_by_category.items()):
            with st.expander(f"📁 {category.title()} ({len(cat_protocols)} protocols)", expanded=True):
                cols = st.columns(2)
                for idx, protocol in enumerate(cat_protocols):
                    with cols[idx % 2]:
                        if st.checkbox(
                            f"{protocol.protocol_id}: {protocol.name}",
                            key=f"protocol_{protocol.protocol_id}",
                            help=f"Duration: {protocol.estimated_duration_hours or 'N/A'}h"
                        ):
                            selected_protocols.append(protocol)

        if not selected_protocols:
            st.warning("⚠️ Please select at least one test protocol")
            return

        st.success(f"✅ Selected {len(selected_protocols)} protocol(s)")
        
        # Show selected protocols summary
        total_duration = sum(p.estimated_duration_hours or 0 for p in selected_protocols)
        st.metric("Total Estimated Duration", f"{total_duration:.1f} hours")

        st.divider()

        # Resource allocation
        st.markdown("#### 3. Resource Allocation")

        # Get available equipment and technicians
        equipment_list = db.execute(
            select(Equipment)
            .where(Equipment.status.in_([EquipmentStatus.AVAILABLE, EquipmentStatus.IN_USE]))
        ).scalars().all()

        technicians = db.execute(
            select(User)
            .where(User.role == UserRole.TECHNICIAN)
        ).scalars().all()

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Equipment Assignment**")
            
            equipment_options = {
                f"{eq.equipment_code} - {eq.name} ({eq.status.value})": eq
                for eq in equipment_list
            }
            
            if equipment_options:
                selected_equipment_key = st.selectbox(
                    "Equipment",
                    options=["-- No Equipment --"] + list(equipment_options.keys()),
                    help="Select equipment for these tests"
                )
                selected_equipment = equipment_options.get(selected_equipment_key)
            else:
                st.warning("No equipment available")
                selected_equipment = None

        with col2:
            st.markdown("**Technician Assignment**")
            
            tech_options = {
                f"{tech.name} - {tech.email}": tech
                for tech in technicians
            }
            
            if tech_options:
                selected_tech_key = st.selectbox(
                    "Technician",
                    options=["-- No Technician --"] + list(tech_options.keys()),
                    help="Assign a technician for these tests"
                )
                selected_technician = tech_options.get(selected_tech_key)
            else:
                st.warning("No technicians available")
                selected_technician = None

        st.divider()

        # Scheduling
        st.markdown("#### 4. Schedule")

        col1, col2, col3 = st.columns(3)

        with col1:
            scheduled_start_date = st.date_input(
                "Start Date",
                value=datetime.now().date(),
                min_value=datetime.now().date()
            )
            scheduled_start_time = st.time_input(
                "Start Time",
                value=datetime.now().time()
            )

        with col2:
            # Calculate default end time based on total duration
            default_end = datetime.now() + timedelta(hours=total_duration)
            scheduled_end_date = st.date_input(
                "End Date",
                value=default_end.date(),
                min_value=scheduled_start_date
            )
            scheduled_end_time = st.time_input(
                "End Time",
                value=default_end.time()
            )

        with col3:
            priority = st.selectbox(
                "Priority",
                options=[1, 2, 3],
                format_func=lambda x: {1: "🔴 High", 2: "🟡 Medium", 3: "🟢 Low"}[x],
                index=1
            )

        # Combine date and time
        scheduled_start = datetime.combine(scheduled_start_date, scheduled_start_time)
        scheduled_end = datetime.combine(scheduled_end_date, scheduled_end_time)

        # Validation
        if scheduled_end <= scheduled_start:
            st.error("❌ End time must be after start time")
            return

        # Check for conflicts
        conflicts_found = False
        
        if selected_equipment:
            eq_available, eq_conflicts = check_equipment_availability(
                selected_equipment.id, scheduled_start, scheduled_end
            )
            if not eq_available:
                st.error(f"❌ Equipment conflict detected! {len(eq_conflicts)} overlapping allocation(s)")
                conflicts_found = True
                for conflict in eq_conflicts:
                    st.caption(f"- {conflict.allocation_number}: {conflict.scheduled_start} to {conflict.scheduled_end}")

        if selected_technician:
            tech_available, tech_conflicts, workload = check_technician_availability(
                selected_technician.id, scheduled_start, scheduled_end
            )
            if not tech_available:
                st.warning(f"⚠️ Technician conflict detected! {len(tech_conflicts)} overlapping allocation(s)")
                st.caption(f"Current workload: {workload} active allocations")

        # Notes
        notes = st.text_area(
            "Notes (optional)",
            placeholder="Add any additional notes about this allocation..."
        )

        st.divider()

        # Submit allocation
        if conflicts_found:
            st.error("⚠️ Cannot create allocation due to resource conflicts. Please adjust schedule or select different resources.")
        else:
            if st.button("🎯 Create Allocation(s)", type="primary", use_container_width=True):
                try:
                    created_count = 0
                    
                    for protocol in selected_protocols:
                        allocation = SampleAllocation(
                            allocation_number=generate_allocation_number(),
                            sample_id=selected_sample.id,
                            protocol_id=protocol.id,
                            equipment_id=selected_equipment.id if selected_equipment else None,
                            technician_id=selected_technician.id if selected_technician else None,
                            scheduled_start=scheduled_start,
                            scheduled_end=scheduled_end,
                            status=AllocationStatus.SCHEDULED,
                            priority=priority,
                            notes=notes,
                            created_by_id=1  # Demo user
                        )
                        db.add(allocation)
                        created_count += 1

                    # Update sample status
                    sample_obj = db.execute(
                        select(Sample).where(Sample.id == selected_sample.id)
                    ).scalar()
                    if sample_obj:
                        sample_obj.status = SampleStatus.ASSIGNED
                    
                    db.commit()

                    st.success(f"✅ Successfully created {created_count} allocation(s)!")
                    st.balloons()
                    
                    # Show summary
                    st.markdown("**Allocation Summary:**")
                    st.info(f"""
                    - Sample: {selected_sample.sample_id}
                    - Protocols: {len(selected_protocols)}
                    - Start: {scheduled_start.strftime('%Y-%m-%d %H:%M')}
                    - End: {scheduled_end.strftime('%Y-%m-%d %H:%M')}
                    - Duration: {(scheduled_end - scheduled_start).total_seconds() / 3600:.1f}h
                    """)

                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error creating allocation: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())


def render_allocation_schedule():
    """Render Gantt chart schedule view of allocations"""

    st.markdown("### 📊 Allocation Schedule - Gantt Chart View")

    with get_db() as db:
        # Get all allocations
        allocations = db.execute(
            select(SampleAllocation)
            .where(SampleAllocation.status != AllocationStatus.CANCELLED)
            .order_by(SampleAllocation.scheduled_start)
        ).scalars().all()

        if not allocations:
            st.info("No allocations scheduled yet. Create allocations in the 'Allocate Sample' tab.")
            return

        # Filters
        col1, col2, col3 = st.columns(3)

        with col1:
            status_filter = st.multiselect(
                "Filter by Status",
                options=[s.value for s in AllocationStatus],
                default=[AllocationStatus.SCHEDULED.value, AllocationStatus.IN_PROGRESS.value]
            )

        with col2:
            date_from = st.date_input(
                "From Date",
                value=datetime.now().date() - timedelta(days=7)
            )

        with col3:
            date_to = st.date_input(
                "To Date",
                value=datetime.now().date() + timedelta(days=30)
            )

        # Filter allocations
        filtered_allocations = [
            a for a in allocations
            if a.status.value in status_filter
            and a.scheduled_start.date() >= date_from
            and a.scheduled_start.date() <= date_to
        ]

        if not filtered_allocations:
            st.warning("No allocations match the selected filters")
            return

        st.markdown(f"**Showing {len(filtered_allocations)} allocation(s)**")

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total", len(filtered_allocations))
        col2.metric("Scheduled", len([a for a in filtered_allocations if a.status == AllocationStatus.SCHEDULED]))
        col3.metric("In Progress", len([a for a in filtered_allocations if a.status == AllocationStatus.IN_PROGRESS]))
        col4.metric("Completed", len([a for a in filtered_allocations if a.status == AllocationStatus.COMPLETED]))

        st.divider()

        # Prepare data for Gantt chart
        gantt_data = []
        
        for alloc in filtered_allocations:
            # Get related data
            sample = db.execute(select(Sample).where(Sample.id == alloc.sample_id)).scalar()
            protocol = db.execute(select(TestProtocol).where(TestProtocol.id == alloc.protocol_id)).scalar()
            
            task_name = f"{sample.sample_id if sample else 'Unknown'} - {protocol.protocol_id if protocol else 'Unknown'}"
            
            # Color by status
            color_map = {
                AllocationStatus.SCHEDULED: '#FFA500',
                AllocationStatus.IN_PROGRESS: '#1E90FF',
                AllocationStatus.COMPLETED: '#32CD32',
                AllocationStatus.ON_HOLD: '#FFD700',
                AllocationStatus.CANCELLED: '#DC143C'
            }
            
            gantt_data.append({
                'Task': task_name,
                'Start': alloc.scheduled_start,
                'Finish': alloc.scheduled_end,
                'Resource': f"Priority {alloc.priority}",
                'Status': alloc.status.value,
                'Color': color_map.get(alloc.status, '#808080')
            })

        # Create Gantt chart
        df_gantt = pd.DataFrame(gantt_data)
        
        fig = ff.create_gantt(
            df_gantt,
            colors=[row['Color'] for _, row in df_gantt.iterrows()],
            index_col='Resource',
            show_colorbar=True,
            group_tasks=True,
            showgrid_x=True,
            showgrid_y=True,
            title='Sample Allocation Timeline'
        )
        
        fig.update_layout(
            height=max(400, len(filtered_allocations) * 30),
            xaxis_title="Timeline",
            yaxis_title="Allocations"
        )
        
        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # Resource utilization view
        st.markdown("### 📈 Resource Utilization")

        # Equipment utilization
        equipment_usage = {}
        for alloc in filtered_allocations:
            if alloc.equipment_id:
                equipment = db.execute(select(Equipment).where(Equipment.id == alloc.equipment_id)).scalar()
                if equipment:
                    eq_name = equipment.name
                    if eq_name not in equipment_usage:
                        equipment_usage[eq_name] = 0
                    # Calculate duration in hours
                    duration = (alloc.scheduled_end - alloc.scheduled_start).total_seconds() / 3600
                    equipment_usage[eq_name] += duration

        if equipment_usage:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Equipment Usage (Hours)**")
                for eq_name, hours in sorted(equipment_usage.items(), key=lambda x: x[1], reverse=True):
                    st.metric(eq_name, f"{hours:.1f}h")
            
            with col2:
                # Create bar chart
                fig_eq = go.Figure(data=[
                    go.Bar(
                        x=list(equipment_usage.keys()),
                        y=list(equipment_usage.values()),
                        marker_color='lightblue'
                    )
                ])
                fig_eq.update_layout(
                    title="Equipment Utilization",
                    xaxis_title="Equipment",
                    yaxis_title="Hours Allocated",
                    height=300
                )
                st.plotly_chart(fig_eq, use_container_width=True)


def render_search_allocations():
    """Render search and filter allocations interface"""

    st.markdown("### 🔍 Search & Manage Allocations")

    with get_db() as db:
        allocations = db.execute(
            select(SampleAllocation)
            .order_by(desc(SampleAllocation.created_at))
        ).scalars().all()

        if not allocations:
            st.info("No allocations found")
            return

        # Search filters
        col1, col2, col3 = st.columns(3)

        with col1:
            search_sample = st.text_input(
                "Search by Sample ID",
                placeholder="SAMPLE-2024-..."
            )

        with col2:
            status_filter = st.selectbox(
                "Filter by Status",
                options=["All"] + [s.value for s in AllocationStatus]
            )

        with col3:
            priority_filter = st.selectbox(
                "Filter by Priority",
                options=["All", 1, 2, 3],
                format_func=lambda x: {
                    "All": "All Priorities",
                    1: "🔴 High",
                    2: "🟡 Medium",
                    3: "🟢 Low"
                }[x]
            )

        st.divider()

        # Display allocations
        displayed_count = 0
        
        for alloc in allocations:
            # Get related data
            sample = db.execute(select(Sample).where(Sample.id == alloc.sample_id)).scalar()
            protocol = db.execute(select(TestProtocol).where(TestProtocol.id == alloc.protocol_id)).scalar()
            equipment = db.execute(select(Equipment).where(Equipment.id == alloc.equipment_id)).scalar() if alloc.equipment_id else None
            technician = db.execute(select(User).where(User.id == alloc.technician_id)).scalar() if alloc.technician_id else None

            # Apply filters
            if search_sample and (not sample or search_sample.upper() not in sample.sample_id.upper()):
                continue
            
            if status_filter != "All" and alloc.status.value != status_filter:
                continue
            
            if priority_filter != "All" and alloc.priority != priority_filter:
                continue

            displayed_count += 1

            # Status icons
            status_icons = {
                AllocationStatus.SCHEDULED: "📅",
                AllocationStatus.IN_PROGRESS: "⚙️",
                AllocationStatus.COMPLETED: "✅",
                AllocationStatus.ON_HOLD: "⏸️",
                AllocationStatus.CANCELLED: "❌"
            }
            status_icon = status_icons.get(alloc.status, "⚪")

            priority_icons = {1: "🔴", 2: "🟡", 3: "🟢"}
            priority_icon = priority_icons.get(alloc.priority, "⚪")

            with st.expander(
                f"{status_icon} {alloc.allocation_number} | {sample.sample_id if sample else 'N/A'} | {protocol.protocol_id if protocol else 'N/A'} | {priority_icon}",
                expanded=False
            ):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown("**Allocation Details**")
                    st.caption(f"Number: {alloc.allocation_number}")
                    st.caption(f"Sample: {sample.sample_id if sample else 'N/A'}")
                    st.caption(f"Protocol: {protocol.name if protocol else 'N/A'}")
                    st.caption(f"Status: {alloc.status.value.upper()}")

                with col2:
                    st.markdown("**Resources**")
                    st.caption(f"Equipment: {equipment.name if equipment else 'Not assigned'}")
                    st.caption(f"Technician: {technician.name if technician else 'Not assigned'}")
                    st.caption(f"Priority: {['High', 'Medium', 'Low'][alloc.priority - 1]}")

                with col3:
                    st.markdown("**Schedule**")
                    st.caption(f"Start: {alloc.scheduled_start.strftime('%Y-%m-%d %H:%M')}")
                    st.caption(f"End: {alloc.scheduled_end.strftime('%Y-%m-%d %H:%M')}")
                    duration = (alloc.scheduled_end - alloc.scheduled_start).total_seconds() / 3600
                    st.caption(f"Duration: {duration:.1f}h")

                if alloc.notes:
                    st.markdown(f"**Notes:** {alloc.notes}")

                # Action buttons
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    if alloc.status == AllocationStatus.SCHEDULED and st.button(
                        "▶️ Start", key=f"start_{alloc.id}"
                    ):
                        alloc.status = AllocationStatus.IN_PROGRESS
                        alloc.actual_start = datetime.now()
                        db.commit()
                        st.success("Started!")
                        st.rerun()

                with col2:
                    if alloc.status == AllocationStatus.IN_PROGRESS and st.button(
                        "✅ Complete", key=f"complete_{alloc.id}"
                    ):
                        alloc.status = AllocationStatus.COMPLETED
                        alloc.actual_end = datetime.now()
                        db.commit()
                        st.success("Completed!")
                        st.rerun()

                with col3:
                    if alloc.status in [AllocationStatus.SCHEDULED, AllocationStatus.IN_PROGRESS] and st.button(
                        "⏸️ Hold", key=f"hold_{alloc.id}"
                    ):
                        alloc.status = AllocationStatus.ON_HOLD
                        db.commit()
                        st.warning("On hold")
                        st.rerun()

                with col4:
                    if st.button("❌ Cancel", key=f"cancel_{alloc.id}"):
                        alloc.status = AllocationStatus.CANCELLED
                        db.commit()
                        st.error("Cancelled")
                        st.rerun()

        if displayed_count == 0:
            st.info("No allocations match the search criteria")
        else:
            st.caption(f"Showing {displayed_count} of {len(allocations)} allocations")


if __name__ == "__main__":
    main()
