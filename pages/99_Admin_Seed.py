"""Admin Seed Page - ONE-TIME USE to seed 54 protocols"""
import streamlit as st
from config.database import get_session_local
from database.seed_data import seed_test_protocols
from sqlalchemy import text

st.set_page_config(page_title="Database Seeding", page_icon="🌱")

st.title("🌱 Database Seeding Admin")
st.warning("⚠️ This is a one-time admin page. Use only once to seed the database.")

if st.button("🚀 SEED ALL 54 PROTOCOLS NOW", type="primary", width="stretch"):
    with st.spinner("Seeding database with all 54 test protocols..."):
        try:
            # Get database session
            SessionLocal = get_session_local()
            db = SessionLocal()
            
            # Run the seeding
            count = seed_test_protocols(db)
            
            db.close()
            
            st.success(f"✅ SUCCESS! Seeded {count} protocols into the database!")
            st.balloons()
            
            # Show breakdown
            st.info("""
            **Protocol Breakdown:**
            - Performance: P1-P12 (12 protocols)
            - Degradation: P13-P27 (15 protocols)
            - Environmental: P28-P39 (12 protocols)
            - Mechanical: P40-P47 (8 protocols)
            - Safety: P48-P54 (7 protocols)
            
            **Total: 54 protocols**
            """)
            
            st.info("🛠️ You can now go to the Test Protocols page and start creating test executions!")
            
        except Exception as e:
            st.error(f"❌ ERROR: {str(e)}")
            st.exception(e)

st.divider()

# Show current state
if st.button("🔍 Check Current Protocol Count"):
    try:
        SessionLocal = get_session_local()
        db = SessionLocal()
        from database import TestProtocol
        
        count = db.query(TestProtocol).count()
        db.close()
        
        if count == 54:
            st.success(f"✅ Database is properly seeded: {count} protocols found")
        elif count == 0:
            st.warning(f"⚠️ Database is empty: {count} protocols. Click the button above to seed.")
        else:
            st.error(f"❌ Unexpected count: {count} protocols (expected 54). Click seed button to fix.")
            
    except Exception as e:
        st.error(f"Error checking database: {str(e)}")


# ==================== DATABASE MIGRATION RUNNER ====================
st.divider()
st.subheader("🔧 Database Migrations")

if st.button("⬆️ RUN MIGRATION 004 (Add Missing Columns)", type="secondary", use_container_width=True):
    try:
        import os
        SessionLocal = get_session_local()
        db = SessionLocal()
        
        # Read migration SQL file
        migration_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'migrations', '004_add_missing_columns_UP.sql')
        
        with open(migration_path, 'r') as f:
            migration_sql = f.read()
        
        # Split by semicolon and execute each statement
        statements = [s.strip() for s in migration_sql.split(';') if s.strip() and not s.strip().startswith('--')]
        
        for statement in statements:
            if statement and 'ALTER TABLE' in statement.upper():
                db.executetext(statement))
        
        db.commit()
        db.close()
        
        st.success("✅ Migration 004 completed successfully! All missing columns have been added.")
        st.balloons()
        st.info("🔄 Please refresh the Sample Receipt and Report Generation pages to verify the fix.")
        
    except Exception as e:
        st.error(f"❌ Migration failed: {str(e)}")
        st.exception(e)
