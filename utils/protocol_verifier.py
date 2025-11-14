"""
Protocol Verification Utility
==============================
Verify that all 54 protocols are properly registered and accessible.

Usage:
    python -m utils.protocol_verifier
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.protocols_registry import get_protocol_registry


def verify_protocols():
    """
    Verify all protocols are registered and accessible

    Returns:
        tuple: (success: bool, report: str)
    """
    print("=" * 70)
    print("SOLAR PV TESTING PROTOCOL VERIFICATION")
    print("=" * 70)
    print()

    # Initialize registry
    print("Loading protocol registry...")
    registry = get_protocol_registry()

    # Get protocol count
    total_protocols = registry.get_protocol_count()
    print(f"✓ Protocol registry initialized")
    print(f"✓ Total protocols loaded: {total_protocols}")
    print()

    # Expected protocol distribution
    expected_protocols = {
        "performance": {"range": "P1-P12", "count": 12},
        "degradation": {"range": "P13-P27", "count": 15},
        "environmental": {"range": "P28-P39", "count": 12},
        "mechanical": {"range": "P40-P47", "count": 8},
        "safety": {"range": "P48-P54", "count": 7}
    }

    total_expected = sum(cat["count"] for cat in expected_protocols.values())

    # Verify by category
    print("-" * 70)
    print("PROTOCOL CATEGORY VERIFICATION")
    print("-" * 70)

    category_summary = registry.get_category_summary()
    all_passed = True

    for category, expected in expected_protocols.items():
        actual_count = category_summary.get(category, 0)
        expected_count = expected["count"]
        protocol_range = expected["range"]

        status = "✓" if actual_count >= expected_count else "✗"
        if actual_count < expected_count:
            all_passed = False

        # Get actual protocols in this category
        protocols = registry.get_protocols_by_category(category)
        protocol_ids = sorted([p.protocol_id for p in protocols])

        print(f"\n{category.upper()}")
        print(f"  Expected: {expected_count} protocols ({protocol_range})")
        print(f"  Actual:   {actual_count} protocols")
        print(f"  Status:   {status}")

        if protocol_ids:
            print(f"  Loaded:   {', '.join(protocol_ids)}")
        else:
            print(f"  Loaded:   None")

    print()
    print("-" * 70)

    # Overall summary
    print("\nOVERALL SUMMARY")
    print("-" * 70)
    print(f"Expected protocols: {total_expected}")
    print(f"Loaded protocols:   {total_protocols}")

    if total_protocols == 0:
        print("\n⚠️  WARNING: No protocols loaded!")
        print("   Using sample protocol definitions from registry.")
        print("   This is normal if protocol files haven't been created yet.")
        all_passed = False
    elif total_protocols < total_expected:
        print(f"\n⚠️  WARNING: Only {total_protocols}/{total_expected} protocols loaded")
        print("   Some protocols are missing.")
        all_passed = False
    else:
        print(f"\n✓ All {total_protocols} protocols successfully loaded!")

    # Test protocol access
    print("\n" + "-" * 70)
    print("SAMPLE PROTOCOL ACCESS TEST")
    print("-" * 70)

    test_protocols = ["P1", "P13", "P28", "P40", "P48"]

    for protocol_id in test_protocols:
        protocol = registry.get_protocol(protocol_id)
        if protocol:
            print(f"✓ {protocol_id}: {protocol.name}")
        else:
            print(f"✗ {protocol_id}: NOT FOUND")
            all_passed = False

    # List all registered protocols
    print("\n" + "-" * 70)
    print("ALL REGISTERED PROTOCOLS")
    print("-" * 70)

    all_protocols = registry.get_all_protocols()

    if all_protocols:
        # Group by category
        for category in ["performance", "degradation", "environmental", "mechanical", "safety"]:
            protocols = [p for p in all_protocols if p.category == category]
            if protocols:
                print(f"\n{category.upper()}:")
                for protocol in sorted(protocols, key=lambda p: p.protocol_id):
                    active_status = "✓" if protocol.is_active else "✗"
                    print(f"  {active_status} {protocol.protocol_id}: {protocol.name}")
    else:
        print("No protocols registered!")

    # Final status
    print("\n" + "=" * 70)
    if all_passed and total_protocols >= total_expected:
        print("STATUS: ✓ ALL CHECKS PASSED")
        print("System is ready for deployment!")
    elif total_protocols > 0:
        print("STATUS: ⚠️  PARTIAL - System functional with sample protocols")
        print("Deployment can proceed. Full protocols can be added later.")
    else:
        print("STATUS: ✗ FAILED - No protocols loaded")
        print("System may not function correctly!")
    print("=" * 70)

    return all_passed, total_protocols


def main():
    """Main entry point"""
    try:
        success, count = verify_protocols()

        # Exit with appropriate code
        if count == 0:
            sys.exit(2)  # Warning: no protocols
        elif not success:
            sys.exit(1)  # Error: checks failed
        else:
            sys.exit(0)  # Success

    except Exception as e:
        print(f"\n✗ ERROR: Protocol verification failed!")
        print(f"  {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
