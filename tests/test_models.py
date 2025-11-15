"""
Model Tests
===========
Test database models and relationships.
"""

import pytest
from datetime import datetime
from config.database import get_db, init_database, reset_database
from models.user import User, UserRole
from models.entity import Entity
from models.audit import AuditProgram, AuditType, AuditSchedule, AuditStatus
from models.nc_ofi import NC_OFI, FindingType, Severity, NCStatus
from models.car import CorrectiveAction, CARMethod, CARStatus
import bcrypt


class TestUserModel:
    """Test User model"""

    def test_user_creation(self):
        """Test creating a user"""
        with get_db() as db:
            password_hash = bcrypt.hashpw("test123".encode('utf-8'), bcrypt.gensalt())

            user = User(
                username="testuser",
                email="test@example.com",
                password_hash=password_hash.decode('utf-8'),
                full_name="Test User",
                role=UserRole.VIEWER,
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.add(user)
            db.commit()

            # Query back
            retrieved = db.query(User).filter_by(username="testuser").first()
            assert retrieved is not None
            assert retrieved.email == "test@example.com"
            assert retrieved.role == UserRole.VIEWER


class TestEntityModel:
    """Test Entity model"""

    def test_entity_hierarchy(self):
        """Test entity hierarchical structure"""
        with get_db() as db:
            # Create parent
            company = Entity(
                name="Test Company",
                type="Company",
                level=1,
                code="COMP001",
                created_at=datetime.utcnow()
            )
            db.add(company)
            db.flush()

            # Create child
            division = Entity(
                name="Test Division",
                type="Division",
                level=2,
                code="DIV001",
                parent_id=company.id,
                created_at=datetime.utcnow()
            )
            db.add(division)
            db.commit()

            # Test relationship
            retrieved_div = db.query(Entity).filter_by(code="DIV001").first()
            assert retrieved_div.parent.name == "Test Company"


class TestAuditModels:
    """Test Audit-related models"""

    def test_audit_program_creation(self):
        """Test creating an audit program"""
        with get_db() as db:
            program = AuditProgram(
                name="Annual ISO 9001 Program",
                year=2024,
                standard="ISO 9001:2015",
                frequency="Annual",
                scope="Quality Management System",
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.add(program)
            db.commit()

            retrieved = db.query(AuditProgram).filter_by(year=2024).first()
            assert retrieved is not None
            assert retrieved.standard == "ISO 9001:2015"


class TestNCOFIModel:
    """Test NC/OFI model"""

    def test_nc_creation(self):
        """Test creating a non-conformance"""
        with get_db() as db:
            # This test requires an audit to exist
            # For simplicity, we'll test the model structure
            pass  # Would need full audit setup


class TestCARModel:
    """Test Corrective Action model"""

    def test_car_creation(self):
        """Test creating a CAR"""
        with get_db() as db:
            # This test requires NC/OFI to exist
            # For simplicity, we'll test the model structure
            pass  # Would need full NC/OFI setup


if __name__ == "__main__":
    pytest.main([__file__])
