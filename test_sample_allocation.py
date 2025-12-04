#!/usr/bin/env python3
"""
Simple test script to verify Sample Allocation page components
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        from database import SampleAllocation, AllocationStatus
        print("✅ Database models import successfully")
        print(f"   AllocationStatus values: {[s.value for s in AllocationStatus]}")
    except Exception as e:
        print(f"❌ Failed to import database models: {e}")
        return False
    
    try:
        from config.database import get_db
        print("✅ Database connection module imports")
    except Exception as e:
        print(f"❌ Failed to import database config: {e}")
        return False
    
    try:
        from config.protocols_registry import get_cached_protocol_registry
        print("✅ Protocol registry imports")
    except Exception as e:
        print(f"❌ Failed to import protocol registry: {e}")
        return False
    
    try:
        import plotly.figure_factory as ff
        import plotly.graph_objects as go
        print("✅ Plotly libraries available for Gantt charts")
    except Exception as e:
        print(f"❌ Failed to import Plotly: {e}")
        return False
    
    return True

def test_model_structure():
    """Test SampleAllocation model structure"""
    print("\nTesting SampleAllocation model...")
    
    try:
        from database import SampleAllocation
        from sqlalchemy import inspect
        
        # Get columns
        mapper = inspect(SampleAllocation)
        columns = [col.key for col in mapper.columns]
        
        required_columns = [
            'id', 'allocation_number', 'sample_id', 'protocol_id',
            'equipment_id', 'technician_id', 'scheduled_start', 'scheduled_end',
            'status', 'priority', 'notes', 'created_at', 'updated_at'
        ]
        
        missing = [col for col in required_columns if col not in columns]
        if missing:
            print(f"❌ Missing columns: {missing}")
            return False
        
        print(f"✅ Model has all required columns: {len(columns)} total")
        return True
        
    except Exception as e:
        print(f"❌ Failed to inspect model: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Sample Allocation Page - Component Tests")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Model Structure", test_model_structure()))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
