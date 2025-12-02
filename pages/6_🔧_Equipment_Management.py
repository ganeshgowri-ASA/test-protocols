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

# Initialize calibration table if it doesn't exist
def init_calibration_table():
    """Create calibration_records table if it doesn't exist."""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS calibration_records (
                    id SERIAL PRIMARY KEY,
                    equipment_id INTEGER NOT NULL,
                    calibration_date DATE NOT NULL,
                    calibration_due_date DATE NOT NULL,
                    calibrated_by VARCHAR(150) NOT NULL,
                    calibration_agency VARCHAR(200),
                    certificate_number VARCHAR(150),
                    calibration_result VARCHAR(50) NOT NULL,
                    remarks TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by VARCHAR(100)
                );
                
                CREATE INDEX IF NOT EXISTS idx_calibration_equipment_id 
                ON calibration_records(equipment_id);
            """)
            conn.commit()
            cursor.close()
        except Exception as e:
            st.error(f"Failed to initialize calibration table: {str(e)}")
        finally:
            conn.close()

# Initialize on page load
init_calibration_table()

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
            ["All", "Testing Equipment", "Imaging Equipment", "Environmental Testing", "Measurement Device", "Calibration Standard", "chamber", "tester"]
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
            query = "SELECT * FROM equipment WHERE 1=1"
            params = []
            
            if category_filter != "All":
                query += " AND category = %s"
                params.append(category_filter)
            
            if status_filter != "All":
                query += " AND status = %s"
                params.append(status_filter)
            
            if search:
                query += " AND (name ILIKE %s OR equipment_code ILIKE %s)"
                params.extend([f"%{search}%", f"%{search}%"])
            
            query += " ORDER BY equipment_code"
            
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
                    active_count = len(df[df.get('status', pd.Series()) == 'Active']) if 'status' in df.columns else 0
                    st.metric("Active", active_count)
                with col3:
                    st.metric("Total Items", len(df))
                with col4:
                    st.metric("Categories", df['category'].nunique() if 'category' in df.columns else 0)
                
                st.markdown("---")
                
                # Display equipment table
                display_cols = [col for col in ['equipment_code', 'name', 'category', 'manufacturer', 'model'] if col in df.columns]
                if display_cols:
                    st.dataframe(
                        df[display_cols],
                        use_container_width=True,
                        hide_index=True
                    )
                
                # Equipment details
                st.markdown("### Equipment Details")
                equipment_codes = df['equipment_code'].tolist() if 'equipment_code' in df.columns else []
                if equipment_codes:
                    selected_equipment = st.selectbox(
                        "Select equipment for details",
                        options=equipment_codes,
                        format_func=lambda x: f"{x} - {df[df['equipment_code'] == x]['name'].values[0]}" if 'name' in df.columns else x
                    )
                    
                    if selected_equipment:
                        eq_data = df[df['equipment_code'] == selected_equipment].iloc[0]
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Equipment Code:** {eq_data.get('equipment_code', 'N/A')}")
                            st.markdown(f"**Name:** {eq_data.get('name', 'N/A')}")
                            st.markdown(f"**Category:** {eq_data.get('category', 'N/A')}")
                            st.markdown(f"**Manufacturer:** {eq_data.get('manufacturer', 'N/A')}")
                        
                        with col2:
                            st.markdown(f"**Model:** {eq_data.get('model', 'N/A')}")
                            if 'status' in eq_data:
                                st.markdown(f"**Status:** {eq_data.get('status', 'N/A')}")
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
            
            # Get calibration records with equipment details
            cursor.execute("""
                SELECT 
                    e.id,
                    e.equipment_code,
                    e.name,
                    e.category,
                    cr.calibration_date,
                    cr.calibration_due_date,
                    cr.calibration_result,
                    cr.calibrated_by
                FROM equipment e
                LEFT JOIN calibration_records cr ON e.id = cr.equipment_id
                ORDER BY cr.calibration_due_date DESC NULLS LAST
            """)
            cal_data = cursor.fetchall()
            
            if cal_data:
                df_cal = pd.DataFrame(cal_data)
                st.markdown("#### Complete Calibration Schedule")
                st.dataframe(df_cal, use_container_width=True, hide_index=True)
            else:
                st.info("No calibration records found.")
            
            # Add calibration record
            st.markdown("---")
            st.markdown("#### Add Calibration Record")
            
            with st.form("calibration_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    # Get equipment list for dropdown
                    cursor.execute("SELECT id, equipment_code, name FROM equipment ORDER BY equipment_code")
                    equipment_list = cursor.fetchall()
                    equipment_options = {f"{eq['equipment_code']} - {eq['name']}": eq['id'] for eq in equipment_list}
                    
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
            equipment_code = st.text_input("Equipment Code *", placeholder="EQP-XXX")
            name = st.text_input("Equipment Name *")
            category = st.selectbox(
                "Category *",
                ["Testing Equipment", "Imaging Equipment", "Environmental Testing", 
                 "Measurement Device", "Calibration Standard", "chamber", "tester", "Other"]
            )
            manufacturer = st.text_input("Manufacturer")
            model_number = st.text_input("Model Number")
        
        with col2:
            status = st.selectbox(
                "Status",
                ["Active", "Inactive", "Under Maintenance"]
            )
            notes = st.text_area("Notes")
        
        submitted = st.form_submit_button("Add Equipment")
        
        if submitted:
            if not equipment_code or not name or not category:
                st.error("Please fill all required fields marked with *")
            else:
                conn = get_db_connection()
                if conn:
                    try:
                        cursor = conn.cursor()
                        cursor.execute(
                            """
                            INSERT INTO equipment 
                            (equipment_code, name, category, manufacturer, model, status)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            """,
                            (equipment_code, name, category, manufacturer, model_number, status)
                        )
                        conn.commit()
                        cursor.close()
                        conn.close()
                        st.success(f"✅ Equipment {equipment_code} added successfully!")
                        st.rerun()
                    except psycopg2.IntegrityError:
                        st.error(f"Equipment Code '{equipment_code}' already exists. Please use a unique code.")
                    except Exception as e:
                        st.error(f"Error adding equipment: {str(e)}")
                    finally:
                        if conn:
                            conn.close()
