import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
from datetime import datetime, timedelta
import os

# Page config
st.set_page_config(
    page_title="Equipment Management",
    page_icon="🔧",
    layout="wide"
)

# Database connection
def get_db_connection():
    """Create database connection."""
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {str(e)}")
        return None

# Page header
st.title("🔧 Equipment Management System")
st.markdown("### Manage laboratory equipment and calibration records")

# Create tabs
tab1, tab2, tab3 = st.tabs(["📋 Equipment List", "📅 Calibration Tracker", "➕ Add Equipment"])

# Tab 1: Equipment List
with tab1:
    st.subheader("Current Equipment Inventory")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        category_filter = st.selectbox(
            "Category",
            ["All", "Testing Equipment", "Imaging Equipment", "Environmental Testing", "Measurement Device", "Calibration Standard"]
        )
    with col2:
        status_filter = st.selectbox(
            "Status",
            ["All", "Active", "Inactive", "Under Maintenance", "Calibration Due", "Retired"]
        )
    with col3:
        search = st.text_input("Search Equipment", placeholder="Search by name or ID")
    
    # Fetch equipment data
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Build query with filters
            query = "SELECT *   FROM equipment_phase1 WHERE 1=1"
            params = []
            
            if category_filter != "All":
                query += " AND category = %s"
                params.append(category_filter)
            
            if status_filter != "All":
                query += " AND status = %s"
                params.append(status_filter)
            
            if search:
                query += " AND (name ILIKE %s OR equipment_id ILIKE %s)"
                params.extend([f"%{search}%", f"%{search}%"])
            
            query += " ORDER BY equipment_id"
            
            cursor.execute(query, params)
            equipment_data = cursor.fetchall()
            
            if equipment_data:
                # Convert to DataFrame
                df = pd.DataFrame(equipment_data)
                
                # Display statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Equipment", len(df))
                with col2:
                    active_count = len(df[df['status'] == 'Active'])
                    st.metric("Active", active_count)
                with col3:
                    due_count = len(df[df['status'] == 'Calibration Due'])
                    st.metric("Calibration Due", due_count, delta="-" if due_count > 0 else None)
                with col4:
                    maintenance_count = len(df[df['status'] == 'Under Maintenance'])
                    st.metric("Under Maintenance", maintenance_count)
                
                st.markdown("---")
                
                # Display equipment table
                display_cols = ['equipment_id', 'name', 'category', 'status', 'location', 'last_calibration_date', 'next_calibration_due']
                st.dataframe(
                    df[display_cols],
                    use_container_width=True,
                    hide_index=True
                )
                
                # Equipment details
                st.markdown("### Equipment Details")
                selected_equipment = st.selectbox(
                    "Select equipment for details",
                    options=df['equipment_id'].tolist(),
                    format_func=lambda x: f"{x} - {df[df['equipment_id'] == x]['name'].values[0]}"
                )
                
                if selected_equipment:
                    eq_data = df[df['equipment_id'] == selected_equipment].iloc[0]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Equipment ID:** {eq_data['equipment_id']}")
                        st.markdown(f"**Name:** {eq_data['name']}")
                        st.markdown(f"**Category:** {eq_data['category']}")
                        st.markdown(f"**Status:** {eq_data['status']}")
                        st.markdown(f"**Manufacturer:** {eq_data['manufacturer']}")
                        st.markdown(f"**Model:** {eq_data['model_number']}")
                    
                    with col2:
                        st.markdown(f"**Serial Number:** {eq_data['serial_number']}")
                        st.markdown(f"**Location:** {eq_data['location']}")
                        st.markdown(f"**Last Calibration:** {eq_data['last_calibration_date']}")
                        st.markdown(f"**Next Calibration Due:** {eq_data['next_calibration_due']}")
                        st.markdown(f"**Calibration Frequency:** {eq_data['calibration_frequency_days']} days")
                    
                    if eq_data['maintenance_notes']:
                        st.markdown("**Maintenance Notes:**")
                        st.info(eq_data['maintenance_notes'])
            else:
                st.info("No equipment found matching the filters.")
            
            cursor.close()
        except Exception as e:
            st.error(f"Error fetching equipment data: {str(e)}")
        finally:
            conn.close()

# Tab 2: Calibration Tracker
with tab2:
    st.subheader("Calibration Schedule & Records")
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get calibration status view
            cursor.execute("SELECT *  equipment_phase1 FROM equipment_phase1_calibration_status ORDER BY days_until_due NULLS LAST")
            cal_data = cursor.fetchall()
            
            if cal_data:
                df_cal = pd.DataFrame(cal_data)
                
                # Display upcoming calibrations
                st.markdown("#### ⚠️ Calibration Alerts")
                
                overdue = df_cal[df_cal['calibration_status'] == 'Overdue']
                due_soon = df_cal[df_cal['calibration_status'] == 'Due Soon']
                
                if len(overdue) > 0:
                    st.error(f"**{len(overdue)} equipment overdue for calibration!**")
                    st.dataframe(overdue[['equipment_id', 'name', 'category', 'next_calibration_due', 'days_until_due']], hide_index=True)
                
                if len(due_soon) > 0:
                    st.warning(f"**{len(due_soon)} equipment due for calibration soon**")
                    st.dataframe(due_soon[['equipment_id', 'name', 'category', 'next_calibration_due', 'days_until_due']], hide_index=True)
                
                st.markdown("---")
                st.markdown("#### Complete Calibration Schedule")
                st.dataframe(df_cal, use_container_width=True, hide_index=True)
            
            # Add calibration record
            st.markdown("---")
            st.markdown("#### Add Calibration Record")
            
            with st.form("calibration_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    # Get equipment list for dropdown
                    cursor.execute("SELECT id, equipment_id, name  equipment_phase1 FROM equipment_phase1 WHERE status != 'Retired' ORDER BY equipment_id")
                    equipment_list = cursor.fetchall()
                    equipment_options = {f"{eq['equipment_id']} - {eq['name']}": eq['id'] for eq in equipment_list}
                    
                    selected_eq = st.selectbox("Equipment", options=list(equipment_options.keys()))
                    cal_date = st.date_input("Calibration Date", value=datetime.now())
                    cal_due_date = st.date_input("Next Calibration Due", value=datetime.now() + timedelta(days=365))
                    calibrated_by = st.text_input("Calibrated By")
                
                with col2:
                    cal_agency = st.text_input("Calibration Agency")
                    certificate_num = st.text_input("Certificate Number")
                    cal_result = st.selectbox("Calibration Result", ["Pass", "Fail", "Conditional Pass"])
                    remarks = st.text_area("Remarks")
                
                submitted = st.form_submit_button("Add Calibration Record")
                
                if submitted:
                    try:
                        equipment_id = equipment_options[selected_eq]
                        
                        cursor.execute(
                            """
                            INSERT INTO calibration_records 
                            (equipment_id, calibration_date, calibration_due_date, calibrated_by, 
                             calibration_agency, certificate_number, calibration_result, remarks, created_by)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """,
                            (equipment_id, cal_date, cal_due_date, calibrated_by, cal_agency, 
                             certificate_num, cal_result, remarks, "System User")
                        )
                        conn.commit()
                        st.success("✅ Calibration record added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding calibration record: {str(e)}")
            
            cursor.close()
        except Exception as e:
            st.error(f"Error: {str(e)}")
        finally:
            conn.close()

# Tab 3: Add Equipment
with tab3:
    st.subheader("Add New Equipment")
    
    with st.form("add_equipment_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            equipment_id = st.text_input("Equipment ID *", placeholder="EQP-XXX")
            name = st.text_input("Equipment Name *")
            category = st.selectbox(
                "Category *",
                ["Testing Equipment", "Imaging Equipment", "Environmental Testing", 
                 "Measurement Device", "Calibration Standard", "Other"]
            )
            manufacturer = st.text_input("Manufacturer")
            model_number = st.text_input("Model Number")
            serial_number = st.text_input("Serial Number")
        
        with col2:
            purchase_date = st.date_input("Purchase Date")
            location = st.text_input("Location *")
            status = st.selectbox(
                "Status",
                ["Active", "Inactive", "Under Maintenance"]
            )
            cal_frequency = st.number_input("Calibration Frequency (days)", min_value=30, max_value=3650, value=365, step=30)
            maintenance_notes = st.text_area("Maintenance Notes")
        
        submitted = st.form_submit_button("Add Equipment")
        
        if submitted:
            if not equipment_id or not name or not category or not location:
                st.error("Please fill all required fields marked with *")
            else:
                conn = get_db_connection()
                if conn:
                    try:
                        cursor = conn.cursor()
                        cursor.execute(
                            """
                            INSERT INTO equipment 
                            (equipment_id, name, category, manufacturer, model_number, serial_number,
                             purchase_date, location, status, calibration_frequency_days, maintenance_notes, created_by)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """,
                            (equipment_id, name, category, manufacturer, model_number, serial_number,
                             purchase_date, location, status, cal_frequency, maintenance_notes, "System User")
                        )
                        conn.commit()
                        cursor.close()
                        conn.close()
                        st.success(f"✅ Equipment {equipment_id} added successfully!")
                        st.rerun()
                    except psycopg2.IntegrityError:
                        st.error(f"Equipment ID '{equipment_id}' already exists. Please use a unique ID.")
                    except Exception as e:
                        st.error(f"Error adding equipment: {str(e)}")
                    finally:
                        if conn:
                            conn.close()