"""Database seed data for test protocols and initial setup"""
from database import TestProtocol
from config.protocols_registry import register_sample_protocols, ProtocolRegistry

def seed_test_protocols(db_session):
    """
    Seed all 54 test protocols from protocols_registry.py (single source of truth).
    This function ensures the test_protocols table contains exactly 54 protocol rows.
    
    Args:
        db_session: SQLAlchemy database session
    
    Returns:
        Number of protocols seeded
    """
    try:
        # Initialize protocol registry with all 54 protocols
        registry = ProtocolRegistry()
        register_sample_protocols(registry)
        
        # Check current state
        existing_count = db_session.query(TestProtocol).count()
        
        # If we already have exactly 54 protocols, skip seeding
        if existing_count == 54:
            print(f"✓ All 54 protocols already seeded")
            return 54
        
        # If we have a different count, clear and reseed to ensure consistency
        if existing_count > 0:
            print(f"⚠ Found {existing_count} protocols (expected 54). Reseeding for consistency...")
            db_session.query(TestProtocol).delete()
            db_session.commit()
        
        # Seed all 54 protocols from the registry
        protocols_added = []
        for protocol in registry.get_all_protocols():
            db_protocol = TestProtocol(
                protocol_id=protocol.protocol_id,  # String format: "P1", "P2", etc.
                name=protocol.name,
                category=protocol.category,
                description=protocol.description,
                standard_reference=protocol.standard_reference,
                estimated_duration_hours=protocol.estimated_duration_hours,
                is_active=protocol.is_active,
                required_equipment=protocol.required_equipment or [],
                input_parameters={},  # JSON field for dynamic params
                acceptance_criteria={}  # JSON field for criteria
            )
            db_session.add(db_protocol)
            protocols_added.append(protocol.protocol_id)
        
        db_session.commit()
        
        # Assert exactly 54 rows - CRITICAL for data integrity
        final_count = db_session.query(TestProtocol).count()
        assert final_count == 54, f"CRITICAL ERROR: Expected 54 protocols, got {final_count}"
        
        print(f"✓ Successfully seeded all 54 protocols")
        print(f"  Performance: {len([p for p in protocols_added if p.startswith('P') and int(p[1:]) <= 12])}")
        print(f"  Degradation: {len([p for p in protocols_added if p.startswith('P') and 13 <= int(p[1:]) <= 27])}")
        print(f"  Environmental: {len([p for p in protocols_added if p.startswith('P') and 28 <= int(p[1:]) <= 39])}")
        print(f"  Mechanical: {len([p for p in protocols_added if p.startswith('P') and 40 <= int(p[1:]) <= 47])}")
        print(f"  Safety: {len([p for p in protocols_added if p.startswith('P') and 48 <= int(p[1:]) <= 54])}")
        
        return final_count
        
    except Exception as e:
        db_session.rollback()
        print(f"✗ FATAL ERROR seeding protocols: {str(e)}")
        raise e
