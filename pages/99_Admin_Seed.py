"""Admin Seed Page - Database Administration and Migration Management"""
import streamlit as st
import os
from pathlib import Path
from datetime import datetime

from config.database import get_session_local, get_engine
from database.seed_data import seed_test_protocols

st.set_page_config(page_title="Database Admin", page_icon="🛠️")

# ============================================================================
# MIGRATIONS DEFINITION
# All available database migrations in order of execution
# ============================================================================

MIGRATIONS = [
    {
        "id": "001",
        "name": "Equipment Management",
        "description": "Create equipment and calibration tables for Phase 1",
        "file_path": "docs/migrations/001_equipment_management",
        "category": "core"
    },
    {
        "id": "002",
        "name": "Sample Management",
        "description": "Create comprehensive sample management tables (receipts, samples, tracking)",
        "file_path": "database/migrations/002_sample_management",
        "category": "sample"
    },
    {
        "id": "003",
        "name": "User Roles",
        "description": "Add role-based access control columns",
        "file_path": "database/migrations/003_user_roles",
        "category": "auth"
    },
    {
        "id": "004",
        "name": "Test Protocols Enhancement",
        "description": "Add protocol versioning and template fields",
        "file_path": "database/migrations/004_test_protocols_enhancement",
        "category": "testing"
    },
    {
        "id": "005",
        "name": "Equipment Booking Enhancement",
        "description": "Add recurring booking and conflict detection",
        "file_path": "database/migrations/005_equipment_booking_enhancement",
        "category": "equipment"
    },
    {
        "id": "006",
        "name": "Audit Trail Enhancement",
        "description": "Add comprehensive audit logging fields",
        "file_path": "database/migrations/006_audit_trail_enhancement",
        "category": "audit"
    },
    {
        "id": "007",
        "name": "Document Management",
        "description": "Add document versioning and approval workflow",
        "file_path": "database/migrations/007_document_management",
        "category": "documents"
    },
    {
        "id": "008",
        "name": "Training Records",
        "description": "Add staff training and certification tracking",
        "file_path": "database/migrations/008_training_records",
        "category": "training"
    },
    {
        "id": "009",
        "name": "BOM Management",
        "description": "Add bill of materials and inventory tracking",
        "file_path": "database/migrations/009_bom_management",
        "category": "inventory"
    },
    {
        "id": "010",
        "name": "QR Code Scanning",
        "description": "Add QR scan logging and tracking",
        "file_path": "database/migrations/010_qr_code_scanning",
        "category": "tracking"
    },
    {
        "id": "011",
        "name": "Report Generation",
        "description": "Add report templates and generation history",
        "file_path": "database/migrations/011_report_generation",
        "category": "reports"
    },
    {
        "id": "012",
        "name": "Data Analysis",
        "description": "Add analysis results and statistical data tables",
        "file_path": "database/migrations/012_data_analysis",
        "category": "analysis"
    },
    {
        "id": "013",
        "name": "Sample Traceability Fields",
        "description": "Add receipt_id, allocation tracking, and traceability columns to samples and inspections",
        "file_path": "database/migrations/013_sample_traceability_fields",
        "category": "sample"
    },
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_migration_status():
    """Check which migrations have been applied"""
    status = {}
    project_root = Path(__file__).parent.parent

    for migration in MIGRATIONS:
        up_file = project_root / f"{migration['file_path']}_UP.sql"
        down_file = project_root / f"{migration['file_path']}_DOWN.sql"

        status[migration['id']] = {
            'up_exists': up_file.exists(),
            'down_exists': down_file.exists(),
            'up_path': str(up_file),
            'down_path': str(down_file),
            'applied': False  # Would need migration tracking table to know this
        }

    return status


def run_migration(migration_id: str, direction: str = "UP"):
    """Run a specific migration"""
    project_root = Path(__file__).parent.parent

    migration = next((m for m in MIGRATIONS if m['id'] == migration_id), None)
    if not migration:
        return False, f"Migration {migration_id} not found"

    file_path = project_root / f"{migration['file_path']}_{direction}.sql"

    if not file_path.exists():
        return False, f"Migration file not found: {file_path}"

    try:
        # Read SQL content
        with open(file_path, 'r') as f:
            sql_content = f.read()

        # Execute migration
        engine = get_engine()

        # Check if using PostgreSQL or SQLite
        database_url = os.getenv('DATABASE_URL', 'sqlite:///lims_qms.db')

        if 'postgresql' in database_url:
            import psycopg2
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor()
            cursor.execute(sql_content)
            conn.commit()
            cursor.close()
            conn.close()
        else:
            # SQLite - need to handle differently as it doesn't support all PostgreSQL syntax
            import sqlite3
            conn = sqlite3.connect('lims_qms.db')
            cursor = conn.cursor()
            # SQLite doesn't support DO blocks or IF NOT EXISTS for columns
            # We'll use a simplified approach
            cursor.executescript(sql_content.replace('DO $$', '--').replace('$$ LANGUAGE plpgsql;', '--'))
            conn.commit()
            cursor.close()
            conn.close()

        return True, f"Migration {migration_id} ({direction}) executed successfully"

    except Exception as e:
        return False, f"Migration failed: {str(e)}"


# ============================================================================
# UI COMPONENTS
# ============================================================================

st.title("🛠️ Database Administration")

# Create tabs for different admin functions
tab1, tab2, tab3 = st.tabs(["🌱 Seed Data", "📦 Migrations", "🔍 Database Status"])

# ============================================================================
# TAB 1: SEED DATA
# ============================================================================

with tab1:
    st.markdown("### 🌱 Database Seeding")
    st.warning("⚠️ Use this to seed initial data. Safe to run multiple times (idempotent).")

    if st.button("🚀 SEED ALL 54 PROTOCOLS NOW", type="primary", key="seed_btn"):
        with st.spinner("Seeding database with all 54 test protocols..."):
            try:
                SessionLocal = get_session_local()
                db = SessionLocal()
                count = seed_test_protocols(db)
                db.close()

                st.success(f"✅ SUCCESS! Seeded {count} protocols into the database!")
                st.balloons()

                st.info("""
                **Protocol Breakdown:**
                - Performance: P1-P12 (12 protocols)
                - Degradation: P13-P27 (15 protocols)
                - Environmental: P28-P39 (12 protocols)
                - Mechanical: P40-P47 (8 protocols)
                - Safety: P48-P54 (7 protocols)

                **Total: 54 protocols**
                """)

            except Exception as e:
                st.error(f"❌ ERROR: {str(e)}")
                st.exception(e)

    st.divider()

    if st.button("🔍 Check Current Protocol Count", key="check_protocols_btn"):
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
                st.info(f"📊 Current count: {count} protocols")

        except Exception as e:
            st.error(f"Error checking database: {str(e)}")

# ============================================================================
# TAB 2: MIGRATIONS
# ============================================================================

with tab2:
    st.markdown("### 📦 Database Migrations")
    st.info(f"**{len(MIGRATIONS)} migrations defined** - Run migrations to update database schema")

    # Get migration status
    migration_status = get_migration_status()

    # Summary metrics
    col1, col2, col3 = st.columns(3)

    files_exist = sum(1 for s in migration_status.values() if s['up_exists'])
    col1.metric("Migrations Defined", len(MIGRATIONS))
    col2.metric("Files Available", files_exist)
    col3.metric("Pending Setup", len(MIGRATIONS) - files_exist)

    st.divider()

    # Filter by category
    categories = list(set(m['category'] for m in MIGRATIONS))
    selected_category = st.selectbox(
        "Filter by Category",
        ["All"] + sorted(categories)
    )

    # Display migrations
    for migration in MIGRATIONS:
        if selected_category != "All" and migration['category'] != selected_category:
            continue

        status = migration_status.get(migration['id'], {})

        # Status indicator
        if status.get('up_exists'):
            status_icon = "✅"
            status_text = "Ready"
        else:
            status_icon = "⚠️"
            status_text = "File Missing"

        with st.expander(
            f"{status_icon} Migration {migration['id']}: {migration['name']} ({migration['category']})",
            expanded=False
        ):
            st.markdown(f"**Description:** {migration['description']}")
            st.markdown(f"**Category:** `{migration['category']}`")
            st.markdown(f"**File Path:** `{migration['file_path']}`")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**UP File:** {'✅ Exists' if status.get('up_exists') else '❌ Missing'}")

            with col2:
                st.markdown(f"**DOWN File:** {'✅ Exists' if status.get('down_exists') else '❌ Missing'}")

            # Action buttons
            if status.get('up_exists'):
                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button(f"▶️ Run UP", key=f"up_{migration['id']}"):
                        with st.spinner(f"Running migration {migration['id']}..."):
                            success, message = run_migration(migration['id'], "UP")
                            if success:
                                st.success(message)
                            else:
                                st.error(message)

                with col2:
                    if status.get('down_exists'):
                        if st.button(f"⏪ Run DOWN", key=f"down_{migration['id']}"):
                            with st.spinner(f"Rolling back migration {migration['id']}..."):
                                success, message = run_migration(migration['id'], "DOWN")
                                if success:
                                    st.warning(message)
                                else:
                                    st.error(message)

                with col3:
                    if st.button(f"👁️ View SQL", key=f"view_{migration['id']}"):
                        try:
                            with open(status['up_path'], 'r') as f:
                                sql_content = f.read()
                            st.code(sql_content[:2000] + "..." if len(sql_content) > 2000 else sql_content, language="sql")
                        except Exception as e:
                            st.error(f"Could not read file: {e}")

    st.divider()

    # Batch operations
    st.markdown("### 🔄 Batch Operations")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("▶️ Run All Pending Migrations", type="primary"):
            results = []
            for migration in MIGRATIONS:
                status = migration_status.get(migration['id'], {})
                if status.get('up_exists'):
                    success, message = run_migration(migration['id'], "UP")
                    results.append((migration['id'], success, message))

            for mid, success, message in results:
                if success:
                    st.success(f"✅ {mid}: {message}")
                else:
                    st.error(f"❌ {mid}: {message}")

    with col2:
        st.caption("⚠️ Run migrations in order for best results")

# ============================================================================
# TAB 3: DATABASE STATUS
# ============================================================================

with tab3:
    st.markdown("### 🔍 Database Status")

    try:
        from config.database import check_database_health
        health = check_database_health()

        if health['connected']:
            st.success(f"✅ Database Connected")
            st.info(f"**Database:** {health.get('database_url', 'N/A')}")
        else:
            st.error(f"❌ Database Disconnected")
            st.error(f"**Error:** {health.get('error', 'Unknown error')}")

    except Exception as e:
        st.error(f"Could not check database health: {e}")

    st.divider()

    # Table counts
    st.markdown("### 📊 Table Record Counts")

    try:
        from config.database import get_session_local
        SessionLocal = get_session_local()
        db = SessionLocal()

        from database import (
            User, ServiceRequest, IncomingInspection, Equipment,
            EquipmentBooking, TestProtocol, TestExecution, Sample,
            SampleReceipt, RouteCard
        )

        tables = [
            ("Users", User),
            ("Service Requests", ServiceRequest),
            ("Incoming Inspections", IncomingInspection),
            ("Equipment", Equipment),
            ("Equipment Bookings", EquipmentBooking),
            ("Test Protocols", TestProtocol),
            ("Test Executions", TestExecution),
            ("Samples", Sample),
            ("Sample Receipts", SampleReceipt),
            ("Route Cards", RouteCard),
        ]

        col1, col2 = st.columns(2)

        for i, (name, model) in enumerate(tables):
            try:
                count = db.query(model).count()
                target_col = col1 if i % 2 == 0 else col2
                target_col.metric(name, count)
            except Exception as e:
                target_col = col1 if i % 2 == 0 else col2
                target_col.metric(name, "Error", help=str(e))

        db.close()

    except Exception as e:
        st.error(f"Error getting table counts: {e}")

    st.divider()

    # Database schema check
    st.markdown("### 🔧 Schema Verification")

    if st.button("🔍 Check Required Columns"):
        try:
            from sqlalchemy import inspect
            engine = get_engine()
            inspector = inspect(engine)

            # Check critical columns
            critical_checks = [
                ("samples", "receipt_id", "Links samples to receipts"),
                ("samples", "inspection_id", "Links samples to inspections"),
                ("incoming_inspections", "allocation_triggered", "Tracks allocation status"),
                ("incoming_inspections", "allocated_sample_id", "Links to allocated sample"),
            ]

            for table, column, description in critical_checks:
                try:
                    columns = [c['name'] for c in inspector.get_columns(table)]
                    if column in columns:
                        st.success(f"✅ `{table}.{column}` exists - {description}")
                    else:
                        st.error(f"❌ `{table}.{column}` MISSING - {description}")
                        st.info(f"➡️ Run migration 013 to add this column")
                except Exception as e:
                    st.warning(f"⚠️ Could not check `{table}.{column}`: {e}")

        except Exception as e:
            st.error(f"Schema check failed: {e}")

st.divider()
st.caption(f"Admin Panel | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
