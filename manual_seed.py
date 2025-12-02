#!/usr/bin/env python3
"""
MANUAL SEED SCRIPT - Run this once to seed all 54 protocols
Usage: python manual_seed.py
"""

if __name__ == "__main__":
    from config.database import get_session_local
    from database.seed_data import seed_test_protocols
    
    print("Starting manual seeding of 54 test protocols...")
    
    # Get database session
    db = get_session_local()()
    
    try:
        # Seed all 54 protocols
        count = seed_test_protocols(db)
        print(f"✅ SUCCESS: Seeded {count} protocols")
    except Exception as e:
        print(f"❌ ERROR: {e}")
        raise
    finally:
        db.close()
        print("Database session closed.")
