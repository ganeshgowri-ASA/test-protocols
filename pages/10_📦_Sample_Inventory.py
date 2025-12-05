"""
Sample Inventory Module - Warehouse & Location Management
==========================================================
Comprehensive warehouse management with location tracking, barcode scanning, and inventory reports.
"""

import streamlit as st
from datetime import datetime, timedelta
import sys
from pathlib import Path
import pandas as pd
import io

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import setup_page_config
from config.database import get_db
from components.navigation import render_header, render_sidebar_navigation
from database import (
    Sample, SampleInventory, StorageLocation, InventoryStatus, SampleStatus
)
from sqlalchemy import select, desc, func, or_, and_

# Page configuration
setup_page_config(page_title="Sample Inventory", page_icon="📦")

# Render navigation
render_header("Sample Inventory - Warehouse Management", "Comprehensive warehouse & location tracking")
render_sidebar_navigation()


def main():
    """Main inventory management page"""

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Inventory Overview",
        "🔍 Search & Locate",
        "📦 Transfer Samples",
        "📈 Reports"
    ])

    with tab1:
        render_inventory_overview()

    with tab2:
        render_search_locate()

    with tab3:
        render_transfer_samples()

    with tab4:
        render_reports()


def render_inventory_overview():
    """Render real-time inventory dashboard with stats"""
    
    st.markdown("### 📊 Real-Time Inventory Dashboard")
    
    with get_db() as db:
        # Get comprehensive stats
        total_samples = db.execute(
            select(func.count(Sample.id))
        ).scalar() or 0
        
        in_stock = db.execute(
            select(func.count(SampleInventory.id))
            .where(SampleInventory.inventory_status == InventoryStatus.IN_STOCK)
        ).scalar() or 0
        
        in_test = db.execute(
            select(func.count(SampleInventory.id))
            .where(SampleInventory.inventory_status == InventoryStatus.IN_TEST)
        ).scalar() or 0
        
        checked_out = db.execute(
            select(func.count(SampleInventory.id))
            .where(SampleInventory.checked_out == True)
        ).scalar() or 0
        
        # Storage locations stats
        total_locations = db.execute(
            select(func.count(StorageLocation.id))
            .where(StorageLocation.is_active == True)
        ).scalar() or 0
        
        # Calculate total capacity and utilization
        location_stats = db.execute(
            select(
                func.sum(StorageLocation.capacity),
                func.sum(StorageLocation.current_count)
            )
        ).first()
        
        total_capacity = location_stats[0] or 0
        total_used = location_stats[1] or 0
        utilization = (total_used / total_capacity * 100) if total_capacity > 0 else 0

    # Metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    col1.metric("Total Samples", total_samples)
    col2.metric("In Storage", in_stock, delta=None)
    col3.metric("In Testing", in_test)
    col4.metric("Checked Out", checked_out)
    col5.metric("Locations", total_locations)
    
    st.divider()
    
    # Capacity utilization
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("#### 📦 Storage Capacity Utilization")
        st.progress(utilization / 100, text=f"{utilization:.1f}% Utilized ({total_used}/{total_capacity})")
        
        if utilization > 90:
            st.error("⚠️ Warning: Storage capacity is critically high!")
        elif utilization > 75:
            st.warning("⚠️ Alert: Storage capacity is getting full")
        else:
            st.success("✓ Storage capacity is within normal range")
    
    with col2:
        st.metric("Utilization", f"{utilization:.1f}%")
    
    st.divider()
    
    # Storage locations summary
    st.markdown("#### 🏢 Storage Locations Status")
    
    with get_db() as db:
        locations = db.execute(
            select(StorageLocation)
            .where(StorageLocation.is_active == True)
            .order_by(StorageLocation.building, StorageLocation.room)
        ).scalars().all()
        
        if locations:
            # Group by building
            buildings = {}
            for loc in locations:
                building = loc.building or "Unknown"
                if building not in buildings:
                    buildings[building] = []
                buildings[building].append(loc)
            
            for building, locs in buildings.items():
                with st.expander(f"🏢 {building} ({len(locs)} locations)", expanded=True):
                    cols = st.columns(3)
                    for idx, loc in enumerate(locs):
                        col_idx = idx % 3
                        with cols[col_idx]:
                            capacity_pct = loc.utilization_percentage
                            color = "🔴" if capacity_pct > 90 else "🟡" if capacity_pct > 75 else "🟢"
                            
                            temp_info = ""
                            if loc.temperature_controlled:
                                temp_info = f"🌡️ {loc.min_temperature}°C - {loc.max_temperature}°C"
                            
                            st.markdown(f"""
                            <div style="border: 1px solid #ddd; border-radius: 8px; padding: 12px; margin: 5px;">
                                <h5>{color} {loc.location_code}</h5>
                                <p style="font-size: 11px; color: #666;">{loc.room}/{loc.rack}/{loc.shelf}</p>
                                <p><strong>{loc.current_count}/{loc.capacity}</strong> samples</p>
                                <small>{temp_info}</small>
                            </div>
                            """, unsafe_allow_html=True)
        else:
            st.info("No storage locations configured. Set up locations in the Transfer Samples tab.")
    
    st.divider()
    
    # Recent inventory activity
    st.markdown("#### 🔄 Recent Inventory Activity")
    
    with get_db() as db:
        recent_inventory = db.execute(
            select(SampleInventory)
            .order_by(desc(SampleInventory.updated_at))
            .limit(10)
        ).scalars().all()
        
        if recent_inventory:
            for inv in recent_inventory:
                col1, col2, col3, col4, col5 = st.columns([2, 2, 1.5, 1, 1])
                col1.markdown(f"**{inv.sample_id_code or 'N/A'}**")
                col2.markdown(f"📍 {inv.full_location_path or 'Unknown'}")
                col3.markdown(f"{inv.inventory_status.value if inv.inventory_status else 'N/A'}")
                col4.markdown(f"{inv.condition or 'N/A'}")
                col5.markdown(f"{inv.updated_at.strftime('%m-%d %H:%M') if inv.updated_at else 'N/A'}")
        else:
            st.info("No recent inventory activity")


def render_search_locate():
    """Render search and locate interface with barcode scanning support"""
    
    st.markdown("### 🔍 Search & Locate Samples")
    
    # Search options
    st.markdown("#### Search Methods")
    
    search_method = st.radio(
        "Select Search Method:",
        ["Sample ID", "QR/Barcode Scan", "Client Name", "Location", "Status"],
        horizontal=True
    )
    
    st.divider()
    
    # Search input based on method
    search_results = None
    
    if search_method == "Sample ID":
        sample_id = st.text_input("🔍 Enter Sample ID", placeholder="e.g., SAMPLE-2024-00001")
        
        if sample_id:
            with get_db() as db:
                # Search in both Sample and SampleInventory
                sample = db.execute(
                    select(Sample)
                    .where(Sample.sample_id.ilike(f"%{sample_id}%"))
                ).scalar()
                
                if sample:
                    inventory = db.execute(
                        select(SampleInventory)
                        .where(SampleInventory.sample_id == sample.id)
                    ).scalar()
                    
                    search_results = [(sample, inventory)]
    
    elif search_method == "QR/Barcode Scan":
        st.markdown("#### 📷 Barcode/QR Scanner")
        
        qr_input = st.text_input(
            "Scan or Enter QR/Barcode",
            placeholder="Scan barcode or enter code manually",
            help="Use a barcode scanner or manually type the code"
        )
        
        if qr_input:
            with get_db() as db:
                # Search by QR code
                sample = db.execute(
                    select(Sample)
                    .where(Sample.qr_code == qr_input)
                ).scalar()
                
                if not sample:
                    # Try searching by sample ID as fallback
                    sample = db.execute(
                        select(Sample)
                        .where(Sample.sample_id == qr_input)
                    ).scalar()
                
                if sample:
                    inventory = db.execute(
                        select(SampleInventory)
                        .where(SampleInventory.sample_id == sample.id)
                    ).scalar()
                    
                    search_results = [(sample, inventory)]
                else:
                    st.error(f"❌ No sample found with code: {qr_input}")
    
    elif search_method == "Client Name":
        # Get service request to find client
        client_name = st.text_input("🏢 Enter Client Name", placeholder="e.g., Solar Corp")
        
        if client_name:
            with get_db() as db:
                samples = db.execute(
                    select(Sample)
                    .join(Sample.receipt)
                    .where(Sample.receipt.has())
                ).scalars().all()
                
                # Filter by matching samples (simplified)
                search_results = []
                for sample in samples:
                    inventory = db.execute(
                        select(SampleInventory)
                        .where(SampleInventory.sample_id == sample.id)
                    ).scalar()
                    search_results.append((sample, inventory))
    
    elif search_method == "Location":
        with get_db() as db:
            locations = db.execute(
                select(StorageLocation)
                .where(StorageLocation.is_active == True)
            ).scalars().all()
            
            location_options = {loc.location_code: loc for loc in locations}
        
        if location_options:
            selected_location = st.selectbox(
                "📍 Select Storage Location",
                options=list(location_options.keys())
            )
            
            if selected_location:
                with get_db() as db:
                    inventories = db.execute(
                        select(SampleInventory)
                        .where(SampleInventory.full_location_path.ilike(f"%{selected_location}%"))
                    ).scalars().all()
                    
                    search_results = []
                    for inv in inventories:
                        sample = db.execute(
                            select(Sample)
                            .where(Sample.id == inv.sample_id)
                        ).scalar()
                        if sample:
                            search_results.append((sample, inv))
        else:
            st.info("No storage locations configured yet.")
    
    elif search_method == "Status":
        status = st.selectbox(
            "📊 Select Status",
            options=[s.value for s in InventoryStatus]
        )
        
        with get_db() as db:
            inventories = db.execute(
                select(SampleInventory)
                .where(SampleInventory.inventory_status == status)
            ).scalars().all()
            
            search_results = []
            for inv in inventories:
                sample = db.execute(
                    select(Sample)
                    .where(Sample.id == inv.sample_id)
                ).scalar()
                if sample:
                    search_results.append((sample, inv))
    
    # Display search results
    if search_results:
        st.divider()
        st.markdown("#### 📋 Search Results")
        
        for sample, inventory in search_results:
            with st.expander(f"📦 {sample.sample_id} - {sample.sample_type or 'Unknown Type'}", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Sample Information**")
                    st.markdown(f"- **ID:** {sample.sample_id}")
                    st.markdown(f"- **Type:** {sample.sample_type or 'N/A'}")
                    st.markdown(f"- **Manufacturer:** {sample.manufacturer or 'N/A'}")
                    st.markdown(f"- **Model:** {sample.model_number or 'N/A'}")
                    st.markdown(f"- **Serial:** {sample.serial_number or 'N/A'}")
                    st.markdown(f"- **Status:** {sample.status.value if sample.status else 'N/A'}")
                
                with col2:
                    if inventory:
                        st.markdown("**Location & Storage**")
                        st.markdown(f"- **Location:** {inventory.full_location_path or 'Not assigned'}")
                        st.markdown(f"- **Storage Status:** {inventory.inventory_status.value if inventory.inventory_status else 'N/A'}")
                        st.markdown(f"- **Condition:** {inventory.condition or 'N/A'}")
                        st.markdown(f"- **Checked Out:** {'Yes ⚠️' if inventory.checked_out else 'No ✓'}")
                        
                        if inventory.checked_out and inventory.expected_return:
                            days_diff = (inventory.expected_return - datetime.utcnow()).days
                            if days_diff < 0:
                                st.error(f"⚠️ OVERDUE by {abs(days_diff)} days")
                            else:
                                st.info(f"Return due in {days_diff} days")
                    else:
                        st.warning("No inventory record found")
                
                # Quick actions
                st.markdown("**Quick Actions**")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📍 View Location Map", key=f"map_{sample.id}"):
                        st.info("Location visualization feature coming soon")
                
                with col2:
                    if st.button("🔄 Transfer Location", key=f"transfer_{sample.id}"):
                        st.session_state[f"transfer_sample_{sample.id}"] = True
                        st.info("Go to Transfer Samples tab to move this sample")
                
                with col3:
                    if st.button("📊 View History", key=f"history_{sample.id}"):
                        st.info("Sample history feature coming soon")


def render_transfer_samples():
    """Render sample transfer interface with batch operations"""
    
    st.markdown("### 📦 Transfer Samples Between Locations")
    
    # Tabs for different operations
    transfer_tab1, transfer_tab2, transfer_tab3 = st.tabs([
        "Single Transfer",
        "Batch Transfer",
        "Manage Locations"
    ])
    
    with transfer_tab1:
        render_single_transfer()
    
    with transfer_tab2:
        render_batch_transfer()
    
    with transfer_tab3:
        render_manage_locations()


def render_single_transfer():
    """Render single sample transfer form"""
    
    st.markdown("#### Transfer Single Sample")
    
    with st.form("single_transfer_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Select sample to transfer
            with get_db() as db:
                inventories = db.execute(
                    select(SampleInventory)
                    .where(SampleInventory.inventory_status == InventoryStatus.IN_STOCK)
                    .where(SampleInventory.checked_out == False)
                ).scalars().all()
                
                sample_options = {
                    f"{inv.sample_id_code} - {inv.full_location_path or 'No location'}": inv 
                    for inv in inventories
                }
            
            selected_sample = st.selectbox(
                "Select Sample to Transfer",
                options=["-- Select Sample --"] + list(sample_options.keys())
            )
        
        with col2:
            # Select destination location
            with get_db() as db:
                locations = db.execute(
                    select(StorageLocation)
                    .where(StorageLocation.is_active == True)
                ).scalars().all()
                
                location_options = {
                    f"{loc.location_code} ({loc.current_count}/{loc.capacity})": loc 
                    for loc in locations
                }
            
            destination = st.selectbox(
                "Destination Location",
                options=["-- Select Destination --"] + list(location_options.keys())
            )
        
        # Transfer reason and notes
        reason = st.selectbox(
            "Transfer Reason",
            options=["Reorganization", "Testing Required", "Return to Storage", "Quality Hold", "Other"]
        )
        
        notes = st.text_area("Transfer Notes", placeholder="Optional notes about this transfer...")
        
        submitted = st.form_submit_button("📦 Transfer Sample", type="primary")
        
        if submitted and selected_sample != "-- Select Sample --" and destination != "-- Select Destination --":
            try:
                inventory = sample_options[selected_sample]
                location = location_options[destination]
                
                # Check capacity
                if location.is_full:
                    st.error(f"❌ Destination location {location.location_code} is at full capacity!")
                else:
                    with get_db() as db:
                        # Update inventory record
                        inv = db.execute(
                            select(SampleInventory)
                            .where(SampleInventory.id == inventory.id)
                        ).scalar()
                        
                        if inv:
                            # Store old location for audit
                            old_location = inv.full_location_path
                            
                            # Update location
                            inv.storage_area = location.building
                            inv.storage_zone = location.room
                            inv.storage_rack = location.rack
                            inv.storage_shelf = location.shelf
                            inv.full_location_path = location.full_path
                            inv.updated_at = datetime.utcnow()
                            
                            # Add transfer note
                            if not inv.condition_notes:
                                inv.condition_notes = ""
                            inv.condition_notes += f"\n[{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}] Transferred from {old_location} to {location.full_path}. Reason: {reason}. {notes}"
                            
                            # Update location counts
                            # Decrease old location count (if it exists)
                            if old_location:
                                old_loc = db.execute(
                                    select(StorageLocation)
                                    .where(StorageLocation.full_path == old_location)
                                ).scalar()
                                if old_loc and old_loc.current_count > 0:
                                    old_loc.current_count -= 1
                            
                            # Increase new location count
                            location_obj = db.execute(
                                select(StorageLocation)
                                .where(StorageLocation.id == location.id)
                            ).scalar()
                            if location_obj:
                                location_obj.current_count += 1
                            
                            db.commit()
                            
                            st.success(f"✅ Sample {inventory.sample_id_code} transferred to {location.location_code}")
                            st.balloons()
                            st.rerun()
            
            except Exception as e:
                st.error(f"❌ Transfer failed: {str(e)}")


def render_batch_transfer():
    """Render batch transfer for multiple samples"""
    
    st.markdown("#### Batch Transfer Multiple Samples")
    
    st.info("💡 Select multiple samples to transfer them all to the same location at once")
    
    with get_db() as db:
        inventories = db.execute(
            select(SampleInventory)
            .where(SampleInventory.inventory_status == InventoryStatus.IN_STOCK)
            .where(SampleInventory.checked_out == False)
        ).scalars().all()
    
    if not inventories:
        st.warning("No samples available for transfer")
        return
    
    # Create a dataframe for selection
    sample_data = []
    for inv in inventories:
        sample_data.append({
            "Select": False,
            "Sample ID": inv.sample_id_code,
            "Current Location": inv.full_location_path or "Not assigned",
            "Status": inv.inventory_status.value if inv.inventory_status else "N/A",
            "Condition": inv.condition or "N/A"
        })
    
    df = pd.DataFrame(sample_data)
    
    # Display editable dataframe
    st.markdown("**Select Samples to Transfer:**")
    edited_df = st.data_editor(
        df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Select": st.column_config.CheckboxColumn("Select", default=False)
        }
    )
    
    # Count selected samples
    selected_count = edited_df['Select'].sum()
    st.info(f"📦 {selected_count} sample(s) selected")
    
    if selected_count > 0:
        with st.form("batch_transfer_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Select destination location
                with get_db() as db:
                    locations = db.execute(
                        select(StorageLocation)
                        .where(StorageLocation.is_active == True)
                    ).scalars().all()
                    
                    location_options = {
                        f"{loc.location_code} ({loc.current_count}/{loc.capacity}) - Available: {loc.capacity - loc.current_count}": loc 
                        for loc in locations
                    }
                
                destination = st.selectbox(
                    "Destination Location",
                    options=["-- Select Destination --"] + list(location_options.keys())
                )
            
            with col2:
                reason = st.selectbox(
                    "Transfer Reason",
                    options=["Reorganization", "Testing Required", "Return to Storage", "Quality Hold", "Other"]
                )
            
            notes = st.text_area("Batch Transfer Notes", placeholder="Notes for all transfers...")
            
            submitted = st.form_submit_button(f"📦 Transfer {selected_count} Sample(s)", type="primary")
            
            if submitted and destination != "-- Select Destination --":
                try:
                    location = location_options[destination]
                    
                    # Check if there's enough capacity
                    available_capacity = location.capacity - location.current_count if location.capacity else 999
                    if selected_count > available_capacity:
                        st.error(f"❌ Not enough capacity! Destination has space for {available_capacity} samples, but {selected_count} selected.")
                    else:
                        # Perform batch transfer
                        selected_sample_ids = edited_df[edited_df['Select'] == True]['Sample ID'].tolist()
                        
                        transferred = 0
                        with get_db() as db:
                            for sample_id in selected_sample_ids:
                                inv = db.execute(
                                    select(SampleInventory)
                                    .where(SampleInventory.sample_id_code == sample_id)
                                ).scalar()
                                
                                if inv:
                                    old_location = inv.full_location_path
                                    
                                    # Update location
                                    inv.storage_area = location.building
                                    inv.storage_zone = location.room
                                    inv.storage_rack = location.rack
                                    inv.storage_shelf = location.shelf
                                    inv.full_location_path = location.full_path
                                    inv.updated_at = datetime.utcnow()
                                    
                                    # Add transfer note
                                    if not inv.condition_notes:
                                        inv.condition_notes = ""
                                    inv.condition_notes += f"\n[{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}] BATCH TRANSFER from {old_location} to {location.full_path}. Reason: {reason}. {notes}"
                                    
                                    transferred += 1
                            
                            # Update location count
                            location_obj = db.execute(
                                select(StorageLocation)
                                .where(StorageLocation.id == location.id)
                            ).scalar()
                            if location_obj:
                                location_obj.current_count += transferred
                            
                            db.commit()
                        
                        st.success(f"✅ Successfully transferred {transferred} samples to {location.location_code}")
                        st.balloons()
                        st.rerun()
                
                except Exception as e:
                    st.error(f"❌ Batch transfer failed: {str(e)}")


def render_manage_locations():
    """Render storage location management"""
    
    st.markdown("#### Manage Storage Locations")
    
    # Add new location
    with st.expander("➕ Add New Storage Location", expanded=False):
        with st.form("new_location_form"):
            st.markdown("**Location Details**")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                building = st.text_input("Building *", placeholder="e.g., Building A")
                room = st.text_input("Room *", placeholder="e.g., Room 101")
            
            with col2:
                rack = st.text_input("Rack *", placeholder="e.g., R1")
                shelf = st.text_input("Shelf *", placeholder="e.g., S1")
            
            with col3:
                capacity = st.number_input("Capacity", min_value=1, max_value=1000, value=50)
            
            # Auto-generate location code
            if building and room and rack and shelf:
                location_code = f"{building}-{room}-{rack}-{shelf}".replace(" ", "")
                st.info(f"📍 Location Code: **{location_code}**")
            else:
                location_code = ""
            
            col1, col2 = st.columns(2)
            
            with col1:
                temp_controlled = st.checkbox("Temperature Controlled")
                if temp_controlled:
                    min_temp = st.number_input("Min Temperature (°C)", value=20.0)
                    max_temp = st.number_input("Max Temperature (°C)", value=25.0)
                else:
                    min_temp = None
                    max_temp = None
            
            with col2:
                humidity_controlled = st.checkbox("Humidity Controlled")
            
            description = st.text_area("Description", placeholder="Optional description of this location...")
            
            submitted = st.form_submit_button("➕ Add Location", type="primary")
            
            if submitted and building and room and rack and shelf:
                try:
                    full_path = f"{building}/{room}/{rack}/{shelf}"
                    
                    with get_db() as db:
                        # Check if location code already exists
                        existing = db.execute(
                            select(StorageLocation)
                            .where(StorageLocation.location_code == location_code)
                        ).scalar()
                        
                        if existing:
                            st.error(f"❌ Location {location_code} already exists!")
                        else:
                            new_location = StorageLocation(
                                location_code=location_code,
                                building=building,
                                room=room,
                                rack=rack,
                                shelf=shelf,
                                full_path=full_path,
                                capacity=capacity,
                                current_count=0,
                                temperature_controlled=temp_controlled,
                                min_temperature=min_temp if temp_controlled else None,
                                max_temperature=max_temp if temp_controlled else None,
                                humidity_controlled=humidity_controlled,
                                description=description,
                                is_active=True
                            )
                            
                            db.add(new_location)
                            db.commit()
                            
                            st.success(f"✅ Location {location_code} created successfully!")
                            st.rerun()
                
                except Exception as e:
                    st.error(f"❌ Failed to create location: {str(e)}")
    
    st.divider()
    
    # List existing locations
    st.markdown("**Existing Storage Locations**")
    
    with get_db() as db:
        locations = db.execute(
            select(StorageLocation)
            .order_by(StorageLocation.building, StorageLocation.room, StorageLocation.rack, StorageLocation.shelf)
        ).scalars().all()
        
        if locations:
            for loc in locations:
                status_icon = "🟢" if loc.is_active else "🔴"
                capacity_pct = loc.utilization_percentage
                capacity_color = "🔴" if capacity_pct > 90 else "🟡" if capacity_pct > 75 else "🟢"
                
                with st.expander(f"{status_icon} {loc.location_code} - {capacity_color} {capacity_pct:.1f}% Full"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("**Location**")
                        st.markdown(f"- Building: {loc.building}")
                        st.markdown(f"- Room: {loc.room}")
                        st.markdown(f"- Rack: {loc.rack}")
                        st.markdown(f"- Shelf: {loc.shelf}")
                    
                    with col2:
                        st.markdown("**Capacity**")
                        st.markdown(f"- Total: {loc.capacity}")
                        st.markdown(f"- Current: {loc.current_count}")
                        st.markdown(f"- Available: {loc.capacity - loc.current_count}")
                        st.progress(capacity_pct / 100)
                    
                    with col3:
                        st.markdown("**Environmental**")
                        if loc.temperature_controlled:
                            st.markdown(f"🌡️ Temp: {loc.min_temperature}°C - {loc.max_temperature}°C")
                        if loc.humidity_controlled:
                            st.markdown("💧 Humidity Controlled")
                        st.markdown(f"Status: {'Active ✓' if loc.is_active else 'Inactive ✗'}")
                    
                    # Actions
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🔄 Toggle Status", key=f"toggle_{loc.id}"):
                            try:
                                with get_db() as db:
                                    location = db.execute(
                                        select(StorageLocation).where(StorageLocation.id == loc.id)
                                    ).scalar()
                                    location.is_active = not location.is_active
                                    db.commit()
                                    st.success(f"✅ Status updated")
                                    st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                    
                    with col2:
                        if st.button("🗑️ Delete", key=f"delete_{loc.id}"):
                            if loc.current_count > 0:
                                st.error("❌ Cannot delete location with samples!")
                            else:
                                try:
                                    with get_db() as db:
                                        location = db.execute(
                                            select(StorageLocation).where(StorageLocation.id == loc.id)
                                        ).scalar()
                                        db.delete(location)
                                        db.commit()
                                        st.success("✅ Location deleted")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error: {str(e)}")
        else:
            st.info("No storage locations configured yet. Add your first location above.")


def render_reports():
    """Render inventory reports with export functionality"""
    
    st.markdown("### 📈 Inventory Reports & Analytics")
    
    # Report type selection
    report_type = st.selectbox(
        "Select Report Type",
        options=[
            "Current Inventory Summary",
            "Location Utilization",
            "Sample Movement History",
            "Overdue Check-outs",
            "Storage Capacity Analysis",
            "Environmental Conditions"
        ]
    )
    
    st.divider()
    
    # Generate button
    if st.button("📊 Generate Report", type="primary"):
        with get_db() as db:
            if report_type == "Current Inventory Summary":
                st.markdown("#### 📦 Current Inventory Summary Report")
                st.markdown(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Get all inventory items
                inventories = db.execute(
                    select(SampleInventory)
                ).scalars().all()
                
                # Create report data
                report_data = []
                for inv in inventories:
                    report_data.append({
                        "Sample ID": inv.sample_id_code,
                        "Location": inv.full_location_path or "Not assigned",
                        "Status": inv.inventory_status.value if inv.inventory_status else "N/A",
                        "Condition": inv.condition or "N/A",
                        "Checked Out": "Yes" if inv.checked_out else "No",
                        "Last Updated": inv.updated_at.strftime('%Y-%m-%d %H:%M') if inv.updated_at else "N/A"
                    })
                
                if report_data:
                    df = pd.DataFrame(report_data)
                    st.dataframe(df, use_container_width=True)
                    
                    # Export options
                    st.markdown("**📥 Export Options:**")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Excel export
                        excel_buffer = io.BytesIO()
                        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                            df.to_excel(writer, sheet_name='Inventory Summary', index=False)
                        excel_buffer.seek(0)
                        
                        st.download_button(
                            label="📥 Download Excel",
                            data=excel_buffer,
                            file_name=f"inventory_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    
                    with col2:
                        # CSV export
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download CSV",
                            data=csv,
                            file_name=f"inventory_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                else:
                    st.info("No inventory data available")
            
            elif report_type == "Location Utilization":
                st.markdown("#### 📊 Location Utilization Report")
                st.markdown(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                locations = db.execute(
                    select(StorageLocation)
                    .where(StorageLocation.is_active == True)
                ).scalars().all()
                
                report_data = []
                for loc in locations:
                    report_data.append({
                        "Location Code": loc.location_code,
                        "Building": loc.building,
                        "Room": loc.room,
                        "Rack": loc.rack,
                        "Shelf": loc.shelf,
                        "Capacity": loc.capacity,
                        "Current Count": loc.current_count,
                        "Available": loc.capacity - loc.current_count,
                        "Utilization %": f"{loc.utilization_percentage:.1f}%",
                        "Status": "At Capacity" if loc.is_full else "Available"
                    })
                
                if report_data:
                    df = pd.DataFrame(report_data)
                    st.dataframe(df, use_container_width=True)
                    
                    # Visualization
                    st.markdown("**📊 Utilization Chart:**")
                    import plotly.express as px
                    
                    fig = px.bar(
                        df,
                        x="Location Code",
                        y="Current Count",
                        color="Utilization %",
                        title="Storage Location Utilization",
                        labels={"Current Count": "Sample Count"},
                        color_continuous_scale="RdYlGn_r"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Export
                    excel_buffer = io.BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                        df.to_excel(writer, sheet_name='Location Utilization', index=False)
                    excel_buffer.seek(0)
                    
                    st.download_button(
                        label="📥 Download Report (Excel)",
                        data=excel_buffer,
                        file_name=f"location_utilization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.info("No location data available")
            
            elif report_type == "Overdue Check-outs":
                st.markdown("#### ⚠️ Overdue Check-outs Report")
                st.markdown(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                overdue = db.execute(
                    select(SampleInventory)
                    .where(SampleInventory.checked_out == True)
                    .where(SampleInventory.expected_return < datetime.utcnow())
                ).scalars().all()
                
                if overdue:
                    report_data = []
                    for inv in overdue:
                        days_overdue = (datetime.utcnow() - inv.expected_return).days
                        report_data.append({
                            "Sample ID": inv.sample_id_code,
                            "Location": inv.full_location_path or "N/A",
                            "Checked Out Date": inv.checked_out_at.strftime('%Y-%m-%d') if inv.checked_out_at else "N/A",
                            "Expected Return": inv.expected_return.strftime('%Y-%m-%d') if inv.expected_return else "N/A",
                            "Days Overdue": days_overdue,
                            "Reason": inv.checked_out_reason or "N/A"
                        })
                    
                    df = pd.DataFrame(report_data)
                    st.error(f"⚠️ {len(overdue)} sample(s) overdue")
                    st.dataframe(df, use_container_width=True)
                    
                    # Export
                    excel_buffer = io.BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                        df.to_excel(writer, sheet_name='Overdue Checkouts', index=False)
                    excel_buffer.seek(0)
                    
                    st.download_button(
                        label="📥 Download Report (Excel)",
                        data=excel_buffer,
                        file_name=f"overdue_checkouts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.success("✅ No overdue check-outs")
            
            elif report_type == "Storage Capacity Analysis":
                st.markdown("#### 📊 Storage Capacity Analysis")
                st.markdown(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                locations = db.execute(
                    select(StorageLocation)
                ).scalars().all()
                
                total_capacity = sum(loc.capacity for loc in locations if loc.capacity)
                total_used = sum(loc.current_count for loc in locations if loc.current_count)
                total_available = total_capacity - total_used
                overall_utilization = (total_used / total_capacity * 100) if total_capacity > 0 else 0
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Capacity", total_capacity)
                col2.metric("Used", total_used)
                col3.metric("Available", total_available)
                col4.metric("Utilization", f"{overall_utilization:.1f}%")
                
                # Warnings
                if overall_utilization > 90:
                    st.error("⚠️ Critical: Storage capacity is above 90%!")
                elif overall_utilization > 75:
                    st.warning("⚠️ Warning: Storage capacity is above 75%")
                else:
                    st.success("✓ Storage capacity is healthy")
                
                # Detailed breakdown
                st.markdown("**Capacity by Building:**")
                
                # Group by building
                buildings = {}
                for loc in locations:
                    building = loc.building or "Unknown"
                    if building not in buildings:
                        buildings[building] = {"capacity": 0, "used": 0}
                    buildings[building]["capacity"] += loc.capacity or 0
                    buildings[building]["used"] += loc.current_count or 0
                
                building_data = []
                for building, stats in buildings.items():
                    building_data.append({
                        "Building": building,
                        "Capacity": stats["capacity"],
                        "Used": stats["used"],
                        "Available": stats["capacity"] - stats["used"],
                        "Utilization %": f"{(stats['used'] / stats['capacity'] * 100) if stats['capacity'] > 0 else 0:.1f}%"
                    })
                
                df = pd.DataFrame(building_data)
                st.dataframe(df, use_container_width=True)


if __name__ == "__main__":
    main()
