"""Phase 1 Test Suite - Equipment Management
Tests for equipment and calibration tables
"""
import pytest
import psycopg2
import os

@pytest.fixture
def db_connection():
    """Provide database connection for tests"""
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    yield conn
    conn.close()

@pytest.fixture
def db_cursor(db_connection):
    """Provide database cursor"""
    cursor = db_connection.cursor()
    yield cursor
    cursor.close()

# Test 1: Verify equipment table exists
def test_equipment_table_exists(db_cursor):
    """Test that equipment table was created successfully"""
    db_cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'equipment'
        )
    """)
    exists = db_cursor.fetchone()[0]
    assert exists, "Equipment table does not exist"

# Test 2: Verify equipment_calibration table exists
def test_calibration_table_exists(db_cursor):
    """Test that equipment_calibration table was created successfully"""
    db_cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'equipment_calibration'
        )
    """)
    exists = db_cursor.fetchone()[0]
    assert exists, "Equipment_calibration table does not exist"

# Test 3: Verify indexes were created
def test_equipment_indexes_exist(db_cursor):
    """Test that required indexes exist"""
    expected_indexes = [
        'idx_equipment_code',
        'idx_equipment_status',
        'idx_equipment_next_cal_date'
    ]
    
    for index_name in expected_indexes:
        db_cursor.execute("""
            SELECT EXISTS (
                SELECT FROM pg_indexes 
                WHERE indexname = %s
            )
        """, (index_name,))
        exists = db_cursor.fetchone()[0]
        assert exists, f"Index {index_name} does not exist"

# Test 4: Verify existing tables intact (regression test)
def test_existing_tables_intact(db_cursor):
    """Test that existing tables are not affected"""
    essential_tables = ['companies', 'service_requests', 'test_executions']
    
    for table_name in essential_tables:
        db_cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            )
        """, (table_name,))
        exists = db_cursor.fetchone()[0]
        assert exists, f"Essential table {table_name} is missing - migration broke existing functionality!"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])