"""
Audit Flow Tests
================
Test complete audit workflow from scheduling to completion.
"""

import pytest
from datetime import datetime, timedelta
from config.database import get_db
from models.user import User, UserRole
from models.entity import Entity
from models.audit import AuditProgram, AuditType, AuditSchedule, Audit, AuditStatus
import bcrypt


class TestAuditWorkflow:
    """Test complete audit workflow"""

    def test_schedule_to_execution(self):
        """Test workflow from scheduling to audit execution"""
        with get_db() as db:
            # Create auditor
            password_hash = bcrypt.hashpw("auditor123".encode('utf-8'), bcrypt.gensalt())
            auditor = User(
                username="auditor1",
                email="auditor@example.com",
                password_hash=password_hash.decode('utf-8'),
                full_name="Lead Auditor",
                role=UserRole.AUDITOR,
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.add(auditor)
            db.flush()

            # Create entity
            entity = Entity(
                name="Manufacturing Plant",
                type="Plant",
                level=3,
                code="PLT001",
                created_at=datetime.utcnow()
            )
            db.add(entity)
            db.flush()

            # Create audit program
            program = AuditProgram(
                name="2024 ISO 9001 Program",
                year=2024,
                standard="ISO 9001:2015",
                frequency="Annual",
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.add(program)
            db.flush()

            # Create audit type
            audit_type = AuditType(
                name="Internal Quality Audit",
                description="Quality management system audit",
                default_duration_hours=4.0,
                default_team_size=2
            )
            db.add(audit_type)
            db.flush()

            # Create schedule
            schedule = AuditSchedule(
                schedule_number="AUD-2024-0001",
                program_id=program.id,
                audit_type_id=audit_type.id,
                auditee_entity_id=entity.id,
                auditor_id=auditor.id,
                planned_date=datetime.now() + timedelta(days=7),
                planned_duration_hours=4.0,
                status=AuditStatus.SCHEDULED,
                created_at=datetime.utcnow()
            )
            db.add(schedule)
            db.flush()

            # Start audit
            audit = Audit(
                audit_number="AUD-EX-2024-0001",
                schedule_id=schedule.id,
                actual_date=datetime.now(),
                start_time=datetime.now(),
                status=AuditStatus.IN_PROGRESS,
                created_at=datetime.utcnow()
            )
            db.add(audit)
            db.commit()

            # Verify workflow
            retrieved_audit = db.query(Audit).filter_by(audit_number="AUD-EX-2024-0001").first()
            assert retrieved_audit is not None
            assert retrieved_audit.schedule.auditor.username == "auditor1"
            assert retrieved_audit.schedule.auditee_entity.name == "Manufacturing Plant"
            assert retrieved_audit.status == AuditStatus.IN_PROGRESS


if __name__ == "__main__":
    pytest.main([__file__])
