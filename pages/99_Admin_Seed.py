"""Admin Seed Page - ONE-TIME USE to seed 54 protocols"""
import streamlit as st
from config.database import get_session_local
from database.seed_data import seed_test_protocols

st.set_page_config(page_title="Database Seeding", page_icon="🌱")

st.title("🌱 Database Seeding Admin")
st.warning("⚠️ This is a one-time admin page. Use only once to seed the database.")

if st.button("🚀 SEED ALL 54 PROTOCOLS NOW", type="primary", use_container_width=True):
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
