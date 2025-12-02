#!/usr/bin/env python
"""
Database Migration Runner
==========================
Initializes database tables on Railway deployment.
Run this automatically on app startup.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    print("Starting database initialization...")
    
    try:
        # Import after path is set
        from config.database import init_database
        
        print("Initializing database...")
        SessionLocal = init_database()
        
        print("✅ Database initialization completed successfully!")
        print("✅ All tables created and seeding completed.")
        
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
