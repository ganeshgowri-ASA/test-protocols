"""
Sample Inventory Module
=======================
Track sample storage locations, check-in/out, and inventory management.
"""

import streamlit as st
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import setup_page_config
from config.database import get_db
from components.navigation import render_header, render_sidebar_navigation
from database import (
    Sample, SampleInventory, InventoryStatus, SampleStatus
)
from sqlalchemy import select, desc, func

# Page configuration
setup_page_config(page_title="Sample Inventory", page_icon="📦")

# Render navigation
render_header("Sample Inventory", "Manage sample storage and inventory")
render_sidebar_navigation()


def main():
    """Main inventory management page"""

    tab1, tab2, tab3, tab4 = st.tabs([
        "📦 Inventory Overview",
        "📍 Storage Locations",
        "🔄 Check In/Out",
        "📊 Inventory Report"
    ])

    with tab1:
        render_inventory_overview()

    with tab2:
        render_storage_locations()

    with tab3:
        render_check_in_out()

    with tab4:
        render_inventory_report()


def render_inventory_overview():
    """Render inventory overview dashboard"""

    st.markdown("### 📦 Inventory Overview")

    with get_db() as db:
        # Get inventory stats
        total_samples = db.execute(
            select(func.count(Sample.id))
        ).scalar()

        in_stock = db.execute(
            select(func.count(SampleInventory.id))
            .where(SampleInventory.inventory_status == InventoryStatus.IN_STOCK)
        ).scalar()

        in_test = db.execute(
            select(func.count(SampleInventory.id))
            .where(SampleInventory.inventory_status == InventoryStatus.IN_TEST)
        ).scalar()

        checked_out = db.execute(
            select(func.count(SampleInventory.id))
            .where(SampleInventory.checked_out == True)
        ).scalar()

    # Metrics row
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Samples", total_samples or 0)
    col2.metric("In Storage", in_stock or 0)
    col3.metric("In Testing", in_test or 0)
    col4.metric("Checked Out", checked_out or 0)

    st.divider()

    # Storage areas summary
    st.markdown("#### Storage Areas")

    storage_areas = [
        ("Storage Room A", "📦", "Climate controlled, 20-25°C"),
        ("Storage Room B", "📦", "Standard storage"),
        ("Lab Prep Area", "🔧", "Pre-testing preparation"),
        ("Environmental Chamber", "🌡️", "Temperature/humidity controlled"),
        ("Completed Storage", "✅", "Tested samples awaiting return")
    ]

    cols = st.columns(3)

    for idx, (area, icon, desc) in enumerate(storage_areas):
        col_idx = idx % 3

        with get_db() as db:
            count = db.execute(
                select(func.count(Sample.id))
                .where(Sample.storage_location == area)
            ).scalar() or 0

        with cols[col_idx]:
            st.markdown(f"""
            <div style="border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin: 5px;">
                <h4>{icon} {area}</h4>
                <p style="color: #666; font-size: 12px;">{desc}</p>
                <h2>{count}</h2>
                <p style="color: #666;">samples</p>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # Recent inventory activity
    st.markdown("#### Recent Inventory Activity")

    with get_db() as db:
        recent_inventory = db.execute(
            select(SampleInventory)
            .order_by(desc(SampleInventory.updated_at))
            .limit(10)
        ).scalars().all()

        if recent_inventory:
            for inv in recent_inventory:
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                col1.markdown(f"**{inv.sample_id_code or 'N/A'}**")
                col2.markdown(f"{inv.full_location_path or 'Unknown'}")
                col3.markdown(f"{inv.inventory_status.value if inv.inventory_status else 'N/A'}")
                col4.markdown(f"{inv.updated_at.strftime('%m-%d %H:%M') if inv.updated_at else 'N/A'}")
        else:
            st.info("No recent inventory activity")


def render_storage_locations():
    """Render storage location management"""

    st.markdown("### 📍 Storage Location Management")

    # Define storage hierarchy
    storage_hierarchy = {
        "Storage Room A": {
            "zones": ["A", "B", "C"],
            "racks": ["R1", "R2", "R3", "R4"],
            "shelves": ["S1", "S2", "S3", "S4", "S5"]
        },
        "Storage Room B": {
            "zones": ["A", "B"],
            "racks": ["R1", "R2", "R3"],
            "shelves": ["S1", "S2", "S3", "S4"]
        },
        "Lab Prep Area": {
            "zones": ["Prep1", "Prep2"],
            "racks": ["Bench1", "Bench2"],
            "shelves": ["Top", "Middle", "Bottom"]
        },
        "Environmental Chamber": {
            "zones": ["Chamber1", "Chamber2", "Chamber3"],
            "racks": ["Slot1", "Slot2", "Slot3", "Slot4"],
            "shelves": ["Level1", "Level2"]
        },
        "Completed Storage": {
            "zones": ["A", "B"],
            "racks": ["R1", "R2"],
            "shelves": ["S1", "S2", "S3"]
        }
    }

    # Location assignment form
    st.markdown("#### Assign Sample to Location")

    with st.form("assign_location"):
        col1, col2 = st.columns(2)

        with col1:
            # Select sample
            with get_db() as db:
                samples = db.execute(
                    select(Sample)
                    .where(Sample.status.in_([SampleStatus.ALLOCATED, SampleStatus.COMPLETED]))
                    .order_by(desc(Sample.created_at))
                    .limit(50)
                ).scalars().all()

                sample_options = {f"{s.sample_id}": s for s in samples}

            selected_sample = st.selectbox(
                "Select Sample",
                options=["-- Select --"] + list(sample_options.keys())
            )

        with col2:
            storage_area = st.selectbox(
                "Storage Area",
                options=list(storage_hierarchy.keys())
            )

        col1, col2, col3 = st.columns(3)

        with col1:
            zone = st.selectbox(
                "Zone",
                options=storage_hierarchy[storage_area]["zones"]
            )

        with col2:
            rack = st.selectbox(
                "Rack",
                options=storage_hierarchy[storage_area]["racks"]
            )

        with col3:
            shelf = st.selectbox(
                "Shelf",
                options=storage_hierarchy[storage_area]["shelves"]
            )

        position = st.text_input("Position (optional)", placeholder="e.g., Pos-1")

        condition = st.selectbox(
            "Condition",
            options=["Excellent", "Good", "Fair", "Poor"]
        )

        notes = st.text_area("Notes", placeholder="Optional notes...")

        submit = st.form_submit_button("📍 Assign Location", type="primary")

        if submit and selected_sample != "-- Select --":
            try:
                sample = sample_options[selected_sample]
                full_path = f"{storage_area}/{zone}/{rack}/{shelf}"
                if position:
                    full_path += f"/{position}"

                with get_db() as db:
                    # Check if inventory record exists
                    existing = db.execute(
                        select(SampleInventory)
                        .where(SampleInventory.sample_id == sample.id)
                    ).scalar()

                    if existing:
                        existing.storage_area = storage_area
                        existing.storage_zone = zone
                        existing.storage_rack = rack
                        existing.storage_shelf = shelf
                        existing.storage_position = position
                        existing.full_location_path = full_path
                        existing.condition = condition.lower()
                        existing.condition_notes = notes
                        existing.inventory_status = InventoryStatus.IN_STOCK
                        existing.updated_at = datetime.utcnow()
                    else:
                        new_inventory = SampleInventory(
                            sample_id=sample.id,
                            sample_id_code=sample.sample_id,
                            storage_area=storage_area,
                            storage_zone=zone,
                            storage_rack=rack,
                            storage_shelf=shelf,
                            storage_position=position,
                            full_location_path=full_path,
                            condition=condition.lower(),
                            condition_notes=notes,
                            inventory_status=InventoryStatus.IN_STOCK
                        )
                        db.add(new_inventory)

                    # Update sample storage location
                    sample_record = db.execute(
                        select(Sample).where(Sample.id == sample.id)
                    ).scalar()
                    if sample_record:
                        sample_record.storage_location = storage_area
                        sample_record.current_location = storage_area

                    db.commit()

                st.success(f"✅ Sample {selected_sample} assigned to {full_path}")
                st.rerun()

            except Exception as e:
                st.error(f"Error: {str(e)}")

    st.divider()

    # View locations
    st.markdown("#### Current Sample Locations")

    with get_db() as db:
        inventory_items = db.execute(
            select(SampleInventory)
            .where(SampleInventory.inventory_status == InventoryStatus.IN_STOCK)
            .order_by(SampleInventory.storage_area, SampleInventory.storage_zone)
        ).scalars().all()

        if inventory_items:
            # Group by storage area
            by_area = {}
            for item in inventory_items:
                area = item.storage_area or "Unknown"
                if area not in by_area:
                    by_area[area] = []
                by_area[area].append(item)

            for area, items in by_area.items():
                with st.expander(f"📦 {area} ({len(items)} samples)"):
                    for item in items:
                        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                        col1.markdown(f"**{item.sample_id_code}**")
                        col2.markdown(f"{item.full_location_path}")
                        col3.markdown(f"{item.condition or 'N/A'}")

                        with col4:
                            if st.button("🔄", key=f"checkout_{item.id}"):
                                st.session_state[f"checkout_item_{item.id}"] = True
        else:
            st.info("No samples currently in storage")


def render_check_in_out():
    """Render check in/out interface"""

    st.markdown("### 🔄 Sample Check In/Out")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Check Out Sample")

        with st.form("checkout_form"):
            with get_db() as db:
                available_samples = db.execute(
                    select(SampleInventory)
                    .where(SampleInventory.checked_out == False)
                    .where(SampleInventory.inventory_status == InventoryStatus.IN_STOCK)
                ).scalars().all()

                sample_options = {f"{s.sample_id_code} ({s.full_location_path})": s for s in available_samples}

            checkout_sample = st.selectbox(
                "Select Sample",
                options=["-- Select --"] + list(sample_options.keys()),
                key="checkout_select"
            )

            checkout_reason = st.selectbox(
                "Reason",
                options=["Testing", "Inspection", "Client Return", "Disposal", "Other"]
            )

            checkout_notes = st.text_area("Notes", key="checkout_notes")

            expected_return = st.date_input(
                "Expected Return Date",
                value=datetime.now().date() + timedelta(days=7)
            )

            if st.form_submit_button("🔓 Check Out", type="primary"):
                if checkout_sample != "-- Select --":
                    try:
                        item = sample_options[checkout_sample]

                        with get_db() as db:
                            inv = db.execute(
                                select(SampleInventory)
                                .where(SampleInventory.id == item.id)
                            ).scalar()

                            if inv:
                                inv.checked_out = True
                                inv.checked_out_by_id = 1
                                inv.checked_out_at = datetime.utcnow()
                                inv.checked_out_reason = f"{checkout_reason}: {checkout_notes}"
                                inv.expected_return = datetime.combine(expected_return, datetime.min.time())
                                inv.inventory_status = InventoryStatus.IN_TEST if checkout_reason == "Testing" else InventoryStatus.IN_STOCK
                                db.commit()

                        st.success(f"✅ Sample checked out successfully!")
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    with col2:
        st.markdown("#### Check In Sample")

        with st.form("checkin_form"):
            with get_db() as db:
                checked_out_samples = db.execute(
                    select(SampleInventory)
                    .where(SampleInventory.checked_out == True)
                ).scalars().all()

                checkin_options = {f"{s.sample_id_code}": s for s in checked_out_samples}

            checkin_sample = st.selectbox(
                "Select Sample",
                options=["-- Select --"] + list(checkin_options.keys()),
                key="checkin_select"
            )

            new_condition = st.selectbox(
                "Condition After Return",
                options=["Excellent", "Good", "Fair", "Poor", "Damaged"]
            )

            checkin_notes = st.text_area("Return Notes", key="checkin_notes")

            if st.form_submit_button("🔒 Check In", type="primary"):
                if checkin_sample != "-- Select --":
                    try:
                        item = checkin_options[checkin_sample]

                        with get_db() as db:
                            inv = db.execute(
                                select(SampleInventory)
                                .where(SampleInventory.id == item.id)
                            ).scalar()

                            if inv:
                                inv.checked_out = False
                                inv.checked_in_by_id = 1
                                inv.checked_in_at = datetime.utcnow()
                                inv.condition = new_condition.lower()
                                inv.condition_notes = checkin_notes
                                inv.inventory_status = InventoryStatus.IN_STOCK
                                db.commit()

                        st.success(f"✅ Sample checked in successfully!")
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    st.divider()

    # Currently checked out
    st.markdown("#### Currently Checked Out Samples")

    with get_db() as db:
        checked_out = db.execute(
            select(SampleInventory)
            .where(SampleInventory.checked_out == True)
            .order_by(SampleInventory.checked_out_at)
        ).scalars().all()

        if checked_out:
            for item in checked_out:
                overdue = item.expected_return and item.expected_return < datetime.utcnow()

                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                col1.markdown(f"**{item.sample_id_code}**")
                col2.markdown(f"Checked out: {item.checked_out_at.strftime('%Y-%m-%d') if item.checked_out_at else 'N/A'}")
                col3.markdown(f"Expected: {item.expected_return.strftime('%Y-%m-%d') if item.expected_return else 'N/A'}")

                if overdue:
                    col4.error("⚠️ OVERDUE")
                else:
                    col4.success("✓ On time")
        else:
            st.info("No samples currently checked out")


def render_inventory_report():
    """Render inventory reports"""

    st.markdown("### 📊 Inventory Reports")

    report_type = st.selectbox(
        "Report Type",
        options=[
            "Current Inventory Status",
            "Samples by Location",
            "Samples by Condition",
            "Overdue Returns",
            "Inventory Movement History"
        ]
    )

    if st.button("📊 Generate Report", type="primary"):
        with get_db() as db:
            if report_type == "Current Inventory Status":
                st.markdown("#### Current Inventory Status Report")
                st.markdown(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")

                # Status counts
                status_counts = db.execute(
                    select(SampleInventory.inventory_status, func.count(SampleInventory.id))
                    .group_by(SampleInventory.inventory_status)
                ).all()

                st.markdown("**By Status:**")
                for status, count in status_counts:
                    st.markdown(f"- {status.value if status else 'Unknown'}: {count}")

            elif report_type == "Samples by Location":
                st.markdown("#### Samples by Location Report")

                location_counts = db.execute(
                    select(SampleInventory.storage_area, func.count(SampleInventory.id))
                    .group_by(SampleInventory.storage_area)
                ).all()

                for location, count in location_counts:
                    st.markdown(f"**{location or 'Unassigned'}:** {count} samples")

            elif report_type == "Samples by Condition":
                st.markdown("#### Samples by Condition Report")

                condition_counts = db.execute(
                    select(SampleInventory.condition, func.count(SampleInventory.id))
                    .group_by(SampleInventory.condition)
                ).all()

                for condition, count in condition_counts:
                    st.markdown(f"**{condition or 'Unknown'}:** {count} samples")

            elif report_type == "Overdue Returns":
                st.markdown("#### Overdue Returns Report")

                overdue = db.execute(
                    select(SampleInventory)
                    .where(SampleInventory.checked_out == True)
                    .where(SampleInventory.expected_return < datetime.utcnow())
                ).scalars().all()

                if overdue:
                    st.error(f"⚠️ {len(overdue)} overdue sample(s)")
                    for item in overdue:
                        days_overdue = (datetime.utcnow() - item.expected_return).days
                        st.markdown(f"- **{item.sample_id_code}**: {days_overdue} days overdue")
                else:
                    st.success("No overdue samples")

            elif report_type == "Inventory Movement History":
                st.markdown("#### Inventory Movement History")

                movements = db.execute(
                    select(SampleInventory)
                    .order_by(desc(SampleInventory.updated_at))
                    .limit(50)
                ).scalars().all()

                for item in movements:
                    st.markdown(
                        f"**{item.sample_id_code}** - {item.inventory_status.value if item.inventory_status else 'N/A'} "
                        f"at {item.full_location_path or 'Unknown'} "
                        f"({item.updated_at.strftime('%Y-%m-%d %H:%M') if item.updated_at else 'N/A'})"
                    )


if __name__ == "__main__":
    main()
