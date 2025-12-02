# Equipment Management - Solar PV LIMS
# Phase 1: Equipment lifecycle and calibration tracking

import streamlit as st
import psycopg2
import os
from datetime import datetime, timedelta
import pandas as pd

# Page config
st.set_page_config(
    page_title="Equipment Management",
    page_icon="🔧",
    layout="wide"
)

# Database connection
def get_db_connection():
    try:
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {str(e)}")
        return None

# Main page
st.title("🔧 Equipment Management")
st.markdown("---")

# Create tabs
tab1, tab2, tab3 = st.tabs(["📋 Equipment List", "⚠️ Calibration Due", "➕ Add Equipment"])

# TAB 1: Equipment List
with tab1:
    st.subheader("Equipment Inventory")
    
    try:
        conn = get_db_connection()
        if conn:
            query = """
                SELECT 
                    equipment_id, equipment_name, equipment_code, category,
                    manufacturer, model_number, status, location,
                    DATE(last_calibration_date) as last_calibration,
                    DATE(next_calibration_date) as next_calibration,
                    calibration_frequency_days,
                    CASE 
                        WHEN next_calibration_date < CURRENT_DATE THEN '🔴 Overdue'
                        WHEN next_calibration_date <= CURRENT_DATE + INTERVAL '30 days' THEN '🟡 Due Soon'
                        ELSE '🟢 Current'
                    END as calibration_status
                FROM equipment
                ORDER BY next_calibration_date ASC
            """
            df = pd.read_sql(query, conn)
            
            if not df.empty:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Equipment", len(df))
                with col2:
                    active = len(df[df['status'] == 'Active'])
                    st.metric("Active", active)
                with col3:
                    overdue = len(df[df['calibration_status'] == '🔴 Overdue'])
                    st.metric("Overdue Calibration", overdue)
                with col4:
                    due_soon = len(df[df['calibration_status'] == '🟡 Due Soon'])
                    st.metric("Due Within 30 Days", due_soon)
                
                st.markdown("---")
                
                # Filters
                col1, col2, col3 = st.columns(3)
                with col1:
                    category_filter = st.selectbox("Filter by Category", ["All"] + sorted(df['category'].unique().tolist()))
                with col2:
                    status_filter = st.selectbox("Filter by Status", ["All"] + sorted(df['status'].unique().tolist()))
                with col3:
                    cal_filter = st.selectbox("Filter by Calibration", ["All", "🔴 Overdue", "🟡 Due Soon", "🟢 Current"])
                
                # Apply filters
                filtered_df = df.copy()
                if category_filter != "All":
                    filtered_df = filtered_df[filtered_df['category'] == category_filter]
                if status_filter != "All":
                    filtered_df = filtered_df[filtered_df['status'] == status_filter]
                if cal_filter != "All":
                    filtered_df = filtered_df[filtered_df['calibration_status'] == cal_filter]
                
                st.dataframe(filtered_df, use_container_width=True, height=400)
            else:
                st.info("No equipment found. Add equipment using 'Add Equipment' tab.")
            
            conn.close()
    except Exception as e:
        st.error(f"Error loading equipment: {str(e)}")

# TAB 2: Calibration Due Tracker
with tab2:
    st.subheader("Calibration Due Tracker")
    
    try:
        conn = get_db_connection()
        if conn:
            query = """
                SELECT 
                    equipment_id, equipment_name, equipment_code, category,
                    DATE(last_calibration_date) as last_calibration,
                    DATE(next_calibration_date) as next_calibration,
                    calibration_frequency_days,
                    (next_calibration_date - CURRENT_DATE) as days_until_due,
                    CASE 
                        WHEN next_calibration_date < CURRENT_DATE THEN '🔴 Overdue'
                        WHEN next_calibration_date <= CURRENT_DATE + INTERVAL '7 days' THEN '🔴 Critical (< 7 days)'
                        WHEN next_calibration_date <= CURRENT_DATE + INTERVAL '30 days' THEN '🟡 Due Soon (< 30 days)'
                        WHEN next_calibration_date <= CURRENT_DATE + INTERVAL '60 days' THEN '🟢 Upcoming (< 60 days)'
                        ELSE '🟢 Current'
                    END as priority
                FROM equipment
                WHERE status = 'Active' AND next_calibration_date <= CURRENT_DATE + INTERVAL '60 days'
                ORDER BY next_calibration_date ASC
            """
            df = pd.read_sql(query, conn)
            
            if not df.empty:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    overdue = len(df[df['priority'].str.contains('Overdue')])
                    st.metric("🔴 Overdue", overdue)
                with col2:
                    critical = len(df[df['priority'].str.contains('Critical')])
                    st.metric("🔴 Critical (< 7d)", critical)
                with col3:
                    due_soon = len(df[df['priority'].str.contains('Due Soon')])
                    st.metric("🟡 Due Soon (< 30d)", due_soon)
                with col4:
                    upcoming = len(df[df['priority'].str.contains('Upcoming')])
                    st.metric("🟢 Upcoming (< 60d)", upcoming)
                
                st.markdown("---")
                st.dataframe(df, use_container_width=True, height=450)
            else:
                st.success("✅ All equipment calibrations are current (no items due within 60 days)")
            
            conn.close()
    except Exception as e:
        st.error(f"Error loading calibration tracker: {str(e)}")

# TAB 3: Add Equipment
with tab3:
    st.subheader("Add New Equipment")
    
    with st.form("add_equipment_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            equipment_name = st.text_input("Equipment Name *", placeholder="e.g., Solar Simulator ABC-3000")
            equipment_code = st.text_input("Equipment Code *", placeholder="e.g., SS-001")
            category = st.selectbox("Category *", ["Solar Simulator", "Climate Chamber", "Multimeter", "IV Tracer", "EL Camera", "IR Camera", "Visual Inspection", "Other"])
            manufacturer = st.text_input("Manufacturer", placeholder="e.g., PASAN")
            model_number = st.text_input("Model Number", placeholder="e.g., SunSim 3c")
            serial_number = st.text_input("Serial Number")
        
        with col2:
            purchase_date = st.date_input("Purchase Date")
            status = st.selectbox("Status *", ["Active", "Inactive", "Maintenance", "Retired"])
            location = st.text_input("Location", placeholder="e.g., Lab 1, Shelf A3")
            calibration_frequency = st.number_input("Calibration Frequency (Days) *", min_value=1, value=365)
            last_calibration = st.date_input("Last Calibration Date")
        
        specifications = st.text_area("Specifications / Technical Details", placeholder="Enter specifications, ranges, accuracy, etc.", height=100)
        remarks = st.text_area("Remarks / Notes", placeholder="Any additional notes", height=80)
        
        submitted = st.form_submit_button("➕ Add Equipment", type="primary")
        
        if submitted:
            if not equipment_name or not equipment_code or not category:
                st.error("❌ Please fill in all required fields (marked with *)")
            else:
                try:
                    conn = get_db_connection()
                    if conn:
                        cursor = conn.cursor()
                        next_cal_date = last_calibration + timedelta(days=calibration_frequency)
                        
                        insert_query = """
                            INSERT INTO equipment (
                                equipment_name, equipment_code, category, manufacturer,
                                model_number, serial_number, purchase_date, status,
                                location, last_calibration_date, next_calibration_date,
                                calibration_frequency_days, specifications, remarks
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING equipment_id
                        """
                        
                        cursor.execute(insert_query, (
                            equipment_name, equipment_code, category, manufacturer,
                            model_number, serial_number, purchase_date, status,
                            location, last_calibration, next_cal_date,
                            calibration_frequency, specifications, remarks
                        ))
                        
                        equipment_id = cursor.fetchone()[0]
                        conn.commit()
                        
                        # Log initial calibration
                        cal_query = """
                            INSERT INTO equipment_calibration (
                                equipment_id, calibration_date, next_calibration_date,
                                calibration_status, performed_by, remarks
                            ) VALUES (%s, %s, %s, %s, %s, %s)
                        """
                        cursor.execute(cal_query, (
                            equipment_id, last_calibration, next_cal_date,
                            'Passed', 'System (Initial Entry)', 'Initial equipment registration'
                        ))
                        conn.commit()
                        
                        cursor.close()
                        conn.close()
                        
                        st.success(f"✅ Equipment added successfully! Equipment ID: {equipment_id}")
                        st.info("Next calibration due: " + next_cal_date.strftime('%Y-%m-%d'))
                        st.balloons()
                        
                except psycopg2.IntegrityError:
                    st.error("❌ Equipment code already exists. Please use a unique code.")
                except Exception as e:
                    st.error(f"❌ Error adding equipment: {str(e)}")

# Footer
st.markdown("---")
st.caption("💡 Tip: Regularly monitor calibration due dates to ensure compliance with ISO 17025 and testing standards.")