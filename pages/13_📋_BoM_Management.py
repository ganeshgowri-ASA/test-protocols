"""
Bill of Materials (BoM) Management Module
=========================================
Manage consumables, materials, and supplies for testing.
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
from config.protocols_registry import get_cached_protocol_registry
from components.navigation import render_header, render_sidebar_navigation
from database import (
    BOMItem, BOMProtocolRequirement, BOMUsageLog, BOMItemType, TestProtocol
)
from sqlalchemy import select, desc, func

# Page configuration
setup_page_config(page_title="BoM Management", page_icon="📋")

# Render navigation
render_header("Bill of Materials Management", "Manage testing materials and consumables")
render_sidebar_navigation()


def generate_item_code():
    """Generate unique BOM item code"""
    with get_db() as db:
        count = db.execute(
            select(func.count(BOMItem.id))
        ).scalar() or 0
        return f"BOM-{count + 1:05d}"


def main():
    """Main BoM management page"""

    tab1, tab2, tab3, tab4 = st.tabs([
        "📦 Inventory",
        "➕ Add Item",
        "🔗 Protocol Requirements",
        "📊 Usage Report"
    ])

    with tab1:
        render_inventory()

    with tab2:
        render_add_item()

    with tab3:
        render_protocol_requirements()

    with tab4:
        render_usage_report()


def render_inventory():
    """Render BOM inventory management"""

    st.markdown("### 📦 Materials Inventory")

    # Summary stats
    with get_db() as db:
        total_items = db.execute(select(func.count(BOMItem.id))).scalar()

        low_stock_count = db.execute(
            select(func.count(BOMItem.id))
            .where(BOMItem.current_stock <= BOMItem.reorder_point)
            .where(BOMItem.is_active == True)
        ).scalar()

        total_value = db.execute(
            select(func.sum(BOMItem.current_stock * BOMItem.unit_cost))
        ).scalar()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Items", total_items or 0)
    col2.metric("Low Stock Alerts", low_stock_count or 0, delta_color="inverse" if low_stock_count else "off")
    col3.metric("Inventory Value", f"${total_value:,.2f}" if total_value else "$0.00")
    col4.metric("Active Items", db.execute(
        select(func.count(BOMItem.id)).where(BOMItem.is_active == True)
    ).scalar() or 0)

    st.divider()

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        search_query = st.text_input("🔍 Search", placeholder="Search by name or code...")

    with col2:
        type_filter = st.selectbox(
            "Item Type",
            options=["All"] + [t.value.title() for t in BOMItemType]
        )

    with col3:
        stock_filter = st.selectbox(
            "Stock Status",
            options=["All", "Low Stock", "In Stock", "Out of Stock"]
        )

    # Inventory list
    with get_db() as db:
        query = select(BOMItem).where(BOMItem.is_active == True)

        if search_query:
            query = query.where(
                (BOMItem.name.contains(search_query)) |
                (BOMItem.item_code.contains(search_query))
            )

        if type_filter != "All":
            query = query.where(BOMItem.item_type == BOMItemType(type_filter.lower()))

        items = db.execute(query.order_by(BOMItem.category, BOMItem.name)).scalars().all()

        # Apply stock filter
        if stock_filter == "Low Stock":
            items = [i for i in items if i.current_stock <= i.reorder_point]
        elif stock_filter == "Out of Stock":
            items = [i for i in items if i.current_stock <= 0]
        elif stock_filter == "In Stock":
            items = [i for i in items if i.current_stock > i.reorder_point]

        if items:
            # Group by category
            by_category = {}
            for item in items:
                cat = item.category or "Uncategorized"
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(item)

            for category, cat_items in by_category.items():
                st.markdown(f"#### 📁 {category.title()}")

                for item in cat_items:
                    # Determine stock status
                    if item.current_stock <= 0:
                        stock_icon = "🔴"
                        stock_status = "Out of Stock"
                    elif item.current_stock <= item.reorder_point:
                        stock_icon = "🟡"
                        stock_status = "Low Stock"
                    else:
                        stock_icon = "🟢"
                        stock_status = "In Stock"

                    with st.expander(
                        f"{stock_icon} {item.item_code} - {item.name} ({item.current_stock} {item.unit or 'units'})"
                    ):
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.markdown(f"**Item Code:** {item.item_code}")
                            st.markdown(f"**Name:** {item.name}")
                            st.markdown(f"**Type:** {item.item_type.value.title() if item.item_type else 'N/A'}")
                            st.markdown(f"**Category:** {item.category or 'N/A'}")

                        with col2:
                            st.markdown(f"**Current Stock:** {item.current_stock} {item.unit or ''}")
                            st.markdown(f"**Minimum Stock:** {item.minimum_stock}")
                            st.markdown(f"**Reorder Point:** {item.reorder_point}")
                            st.markdown(f"**Reorder Qty:** {item.reorder_quantity or 'N/A'}")

                        with col3:
                            st.markdown(f"**Unit Cost:** ${item.unit_cost:.2f} {item.currency or 'USD'}")
                            st.markdown(f"**Total Value:** ${(item.current_stock * item.unit_cost):.2f}")
                            st.markdown(f"**Supplier:** {item.supplier_name or 'N/A'}")
                            st.markdown(f"**Lead Time:** {item.lead_time_days or 'N/A'} days")

                        if item.description:
                            st.markdown(f"**Description:** {item.description}")

                        # Stock adjustment
                        st.markdown("---")
                        st.markdown("**Adjust Stock:**")

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            adjustment_type = st.selectbox(
                                "Type",
                                options=["Add", "Remove", "Set"],
                                key=f"adj_type_{item.id}"
                            )

                        with col2:
                            adjustment_qty = st.number_input(
                                "Quantity",
                                min_value=0.0,
                                value=1.0,
                                step=1.0,
                                key=f"adj_qty_{item.id}"
                            )

                        with col3:
                            st.markdown("<br>", unsafe_allow_html=True)
                            if st.button("📝 Apply", key=f"adj_apply_{item.id}"):
                                if adjustment_type == "Add":
                                    item.current_stock += adjustment_qty
                                elif adjustment_type == "Remove":
                                    item.current_stock = max(0, item.current_stock - adjustment_qty)
                                else:
                                    item.current_stock = adjustment_qty

                                db.commit()
                                st.success(f"Stock updated: {item.current_stock} {item.unit or 'units'}")
                                st.rerun()

                st.markdown("---")
        else:
            st.info("No items found")

    # Low stock alerts
    if low_stock_count and low_stock_count > 0:
        st.markdown("### ⚠️ Low Stock Alerts")

        with get_db() as db:
            low_items = db.execute(
                select(BOMItem)
                .where(BOMItem.current_stock <= BOMItem.reorder_point)
                .where(BOMItem.is_active == True)
            ).scalars().all()

            for item in low_items:
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                col1.markdown(f"**{item.name}** ({item.item_code})")
                col2.error(f"{item.current_stock} {item.unit or ''}")
                col3.markdown(f"Min: {item.reorder_point}")
                col4.markdown(f"Reorder: {item.reorder_quantity or 'N/A'}")


def render_add_item():
    """Render add BOM item form"""

    st.markdown("### ➕ Add New Item")

    with st.form("add_bom_item"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Item Name *", placeholder="e.g., Calibration Fluid 500ml")

            item_type = st.selectbox(
                "Item Type *",
                options=[t.value.title() for t in BOMItemType]
            )

            category = st.selectbox(
                "Category",
                options=["Chemicals", "Calibration", "Safety", "Electrical", "Mechanical", "Consumables", "Other"]
            )

            unit = st.selectbox(
                "Unit of Measure",
                options=["Each", "Liter", "mL", "Kg", "g", "Meter", "Roll", "Pack", "Box", "Set"]
            )

        with col2:
            initial_stock = st.number_input("Initial Stock", min_value=0.0, value=0.0)

            minimum_stock = st.number_input("Minimum Stock", min_value=0.0, value=5.0)

            reorder_point = st.number_input("Reorder Point", min_value=0.0, value=10.0)

            reorder_quantity = st.number_input("Reorder Quantity", min_value=1.0, value=25.0)

        st.markdown("#### Pricing")

        col1, col2, col3 = st.columns(3)

        with col1:
            unit_cost = st.number_input("Unit Cost ($)", min_value=0.0, value=0.0, step=0.01)

        with col2:
            currency = st.selectbox("Currency", options=["USD", "EUR", "GBP", "INR"])

        with col3:
            cost_center = st.text_input("Cost Center", placeholder="e.g., LAB-001")

        st.markdown("#### Supplier Information")

        col1, col2 = st.columns(2)

        with col1:
            supplier_name = st.text_input("Supplier Name", placeholder="Supplier company name")
            supplier_code = st.text_input("Supplier Code", placeholder="Supplier ID")

        with col2:
            supplier_part = st.text_input("Supplier Part Number", placeholder="Supplier's part #")
            lead_time = st.number_input("Lead Time (days)", min_value=0, value=7)

        description = st.text_area("Description", placeholder="Item description and specifications...")

        has_expiry = st.checkbox("Has Expiry Date")
        if has_expiry:
            shelf_life = st.number_input("Shelf Life (days)", min_value=1, value=365)
        else:
            shelf_life = None

        if st.form_submit_button("➕ Add Item", type="primary"):
            if not name:
                st.error("Item name is required")
            else:
                try:
                    item_code = generate_item_code()

                    with get_db() as db:
                        new_item = BOMItem(
                            item_code=item_code,
                            name=name,
                            description=description,
                            item_type=BOMItemType(item_type.lower()),
                            category=category.lower(),
                            unit=unit.lower(),
                            current_stock=initial_stock,
                            minimum_stock=minimum_stock,
                            reorder_point=reorder_point,
                            reorder_quantity=reorder_quantity,
                            unit_cost=unit_cost,
                            currency=currency,
                            cost_center=cost_center,
                            supplier_name=supplier_name,
                            supplier_code=supplier_code,
                            supplier_part_number=supplier_part,
                            lead_time_days=lead_time,
                            has_expiry=has_expiry,
                            shelf_life_days=shelf_life,
                            is_active=True
                        )
                        db.add(new_item)
                        db.commit()

                    st.success(f"✅ Item added: {item_code} - {name}")
                    st.rerun()

                except Exception as e:
                    st.error(f"Error: {str(e)}")


def render_protocol_requirements():
    """Render protocol material requirements"""

    st.markdown("### 🔗 Protocol Material Requirements")

    st.info("Define required materials for each test protocol")

    col1, col2 = st.columns(2)

    with col1:
        # Protocol selection
        registry = get_cached_protocol_registry()
        protocols = registry.get_all_protocols()

        protocol_options = {f"{p.protocol_id}: {p.name}": p.protocol_id for p in protocols}

        selected_protocol_display = st.selectbox(
            "Select Protocol",
            options=["-- Select --"] + list(protocol_options.keys())
        )

    with col2:
        # Item selection
        with get_db() as db:
            items = db.execute(
                select(BOMItem).where(BOMItem.is_active == True)
            ).scalars().all()

            item_options = {f"{i.item_code}: {i.name}": i for i in items}

        selected_item_display = st.selectbox(
            "Select Item",
            options=["-- Select --"] + list(item_options.keys())
        )

    # Add requirement form
    if selected_protocol_display != "-- Select --" and selected_item_display != "-- Select --":
        with st.form("add_requirement"):
            col1, col2 = st.columns(2)

            with col1:
                quantity = st.number_input("Quantity per Test", min_value=0.1, value=1.0, step=0.1)

            with col2:
                is_mandatory = st.checkbox("Mandatory", value=True)

            notes = st.text_input("Notes", placeholder="Usage notes...")

            if st.form_submit_button("➕ Add Requirement"):
                try:
                    protocol_id_str = protocol_options[selected_protocol_display]
                    item = item_options[selected_item_display]

                    with get_db() as db:
                        # Get protocol database ID
                        protocol = db.execute(
                            select(TestProtocol)
                            .where(TestProtocol.protocol_id == protocol_id_str)
                        ).scalar()

                        if protocol:
                            # Check if requirement exists
                            existing = db.execute(
                                select(BOMProtocolRequirement)
                                .where(BOMProtocolRequirement.protocol_id == protocol.id)
                                .where(BOMProtocolRequirement.bom_item_id == item.id)
                            ).scalar()

                            if existing:
                                existing.quantity_per_test = quantity
                                existing.is_mandatory = is_mandatory
                                existing.notes = notes
                            else:
                                new_req = BOMProtocolRequirement(
                                    protocol_id=protocol.id,
                                    bom_item_id=item.id,
                                    quantity_per_test=quantity,
                                    is_mandatory=is_mandatory,
                                    notes=notes
                                )
                                db.add(new_req)

                            db.commit()
                            st.success("Requirement saved!")
                            st.rerun()
                        else:
                            st.error("Protocol not found in database")

                except Exception as e:
                    st.error(f"Error: {str(e)}")

    st.divider()

    # View requirements by protocol
    st.markdown("#### Current Protocol Requirements")

    with get_db() as db:
        requirements = db.execute(
            select(BOMProtocolRequirement)
            .order_by(BOMProtocolRequirement.protocol_id)
        ).scalars().all()

        if requirements:
            # Group by protocol
            by_protocol = {}
            for req in requirements:
                protocol = db.execute(
                    select(TestProtocol).where(TestProtocol.id == req.protocol_id)
                ).scalar()

                if protocol:
                    key = f"{protocol.protocol_id}: {protocol.name}"
                    if key not in by_protocol:
                        by_protocol[key] = []
                    by_protocol[key].append(req)

            for protocol_name, reqs in by_protocol.items():
                with st.expander(f"📋 {protocol_name} ({len(reqs)} items)"):
                    for req in reqs:
                        item = db.execute(
                            select(BOMItem).where(BOMItem.id == req.bom_item_id)
                        ).scalar()

                        if item:
                            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                            col1.markdown(f"**{item.name}**")
                            col2.markdown(f"{req.quantity_per_test} {item.unit or 'units'}")
                            col3.markdown("✓ Required" if req.is_mandatory else "Optional")

                            with col4:
                                if st.button("🗑️", key=f"del_req_{req.id}"):
                                    db.delete(req)
                                    db.commit()
                                    st.rerun()
        else:
            st.info("No protocol requirements defined yet")


def render_usage_report():
    """Render usage tracking and reports"""

    st.markdown("### 📊 Material Usage Report")

    # Time period filter
    col1, col2 = st.columns(2)

    with col1:
        period = st.selectbox(
            "Time Period",
            options=["Last 7 days", "Last 30 days", "Last 90 days", "This Year", "All Time"]
        )

    with col2:
        item_filter = st.selectbox(
            "Item",
            options=["All Items"]  # Would add more options from database
        )

    # Calculate date range
    if period == "Last 7 days":
        start_date = datetime.utcnow() - timedelta(days=7)
    elif period == "Last 30 days":
        start_date = datetime.utcnow() - timedelta(days=30)
    elif period == "Last 90 days":
        start_date = datetime.utcnow() - timedelta(days=90)
    elif period == "This Year":
        start_date = datetime(datetime.utcnow().year, 1, 1)
    else:
        start_date = None

    with get_db() as db:
        query = select(BOMUsageLog)

        if start_date:
            query = query.where(BOMUsageLog.used_at >= start_date)

        usage_logs = db.execute(query.order_by(desc(BOMUsageLog.used_at))).scalars().all()

        if usage_logs:
            # Summary
            total_uses = len(usage_logs)
            total_cost = 0

            # Calculate costs
            for log in usage_logs:
                item = db.execute(
                    select(BOMItem).where(BOMItem.id == log.bom_item_id)
                ).scalar()
                if item:
                    total_cost += log.quantity_used * item.unit_cost

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Usage Events", total_uses)
            col2.metric("Total Cost", f"${total_cost:,.2f}")
            col3.metric("Unique Items Used", len(set([l.bom_item_id for l in usage_logs])))

            st.divider()

            # Usage details
            st.markdown("#### Usage Details")

            for log in usage_logs[:50]:  # Limit display
                item = db.execute(
                    select(BOMItem).where(BOMItem.id == log.bom_item_id)
                ).scalar()

                if item:
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    col1.markdown(f"**{item.name}**")
                    col2.markdown(f"{log.quantity_used} {item.unit or 'units'}")
                    col3.markdown(f"${(log.quantity_used * item.unit_cost):.2f}")
                    col4.markdown(f"{log.used_at.strftime('%Y-%m-%d') if log.used_at else 'N/A'}")
        else:
            st.info("No usage data for the selected period")

    # Log usage manually
    st.markdown("---")
    st.markdown("#### Log Manual Usage")

    with st.form("log_usage"):
        col1, col2 = st.columns(2)

        with col1:
            with get_db() as db:
                items = db.execute(
                    select(BOMItem).where(BOMItem.is_active == True)
                ).scalars().all()
                item_options = {f"{i.item_code}: {i.name}": i for i in items}

            usage_item = st.selectbox(
                "Item *",
                options=["-- Select --"] + list(item_options.keys())
            )

            quantity_used = st.number_input("Quantity Used", min_value=0.1, value=1.0, step=0.1)

        with col2:
            usage_type = st.selectbox(
                "Usage Type",
                options=["Consumed", "Returned", "Wasted"]
            )

            lot_number = st.text_input("Lot/Batch Number", placeholder="Optional")

        notes = st.text_input("Notes", placeholder="Usage notes...")

        if st.form_submit_button("📝 Log Usage"):
            if usage_item == "-- Select --":
                st.error("Please select an item")
            else:
                try:
                    item = item_options[usage_item]

                    with get_db() as db:
                        new_log = BOMUsageLog(
                            bom_item_id=item.id,
                            quantity_used=quantity_used,
                            usage_type=usage_type.lower(),
                            lot_number=lot_number,
                            notes=notes,
                            used_by_id=1
                        )
                        db.add(new_log)

                        # Update stock
                        item_record = db.execute(
                            select(BOMItem).where(BOMItem.id == item.id)
                        ).scalar()

                        if item_record and usage_type != "Returned":
                            item_record.current_stock = max(0, item_record.current_stock - quantity_used)

                        db.commit()

                    st.success("Usage logged and stock updated!")
                    st.rerun()

                except Exception as e:
                    st.error(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
