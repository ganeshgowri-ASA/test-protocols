"""
Sample Data Seeding Script
===========================
Populate database with sample data for demonstration.

Usage:
    python seed_data.py
"""

from datetime import datetime, timedelta
import bcrypt
from config.database import init_database, get_db
from models.user import User, UserRole
from models.entity import Entity
from models.audit import AuditProgram, AuditType, AuditSchedule, Audit, AuditStatus
from models.checklist import Checklist, ChecklistItem
from models.nc_ofi import NC_OFI, FindingType, Severity, NCStatus
from models.car import CorrectiveAction, CARMethod, CARStatus


def seed_users():
    """Seed sample users"""
    print("Seeding users...")

    users_data = [
        ("admin", "admin@auditpro.com", "admin123", "System Administrator", UserRole.ADMIN),
        ("auditor1", "auditor1@auditpro.com", "auditor123", "John Smith", UserRole.AUDITOR),
        ("auditor2", "auditor2@auditpro.com", "auditor123", "Sarah Johnson", UserRole.AUDITOR),
        ("auditee1", "auditee1@auditpro.com", "auditee123", "Mike Wilson", UserRole.AUDITEE),
        ("viewer1", "viewer1@auditpro.com", "viewer123", "Jane Doe", UserRole.VIEWER),
    ]

    with get_db() as db:
        for username, email, password, full_name, role in users_data:
            existing = db.query(User).filter_by(username=username).first()
            if not existing:
                password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                user = User(
                    username=username,
                    email=email,
                    password_hash=password_hash.decode('utf-8'),
                    full_name=full_name,
                    role=role,
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                db.add(user)

        db.commit()

    print(f"✓ Created {len(users_data)} users")


def seed_entities():
    """Seed organizational entities"""
    print("Seeding entities...")

    with get_db() as db:
        # Company
        company = Entity(
            name="ABC Manufacturing Corp",
            type="Company",
            level=1,
            code="ABC-CORP",
            location="New York, USA",
            manager_name="CEO John Doe",
            contact_email="ceo@abcmanufacturing.com",
            created_at=datetime.utcnow()
        )
        db.add(company)
        db.flush()

        # Divisions
        div1 = Entity(
            name="North America Division",
            type="Division",
            level=2,
            code="NAM-DIV",
            parent_id=company.id,
            location="USA",
            manager_name="VP North America",
            created_at=datetime.utcnow()
        )
        db.add(div1)
        db.flush()

        # Plants
        plant1 = Entity(
            name="Detroit Manufacturing Plant",
            type="Plant",
            level=3,
            code="DET-PLT",
            parent_id=div1.id,
            location="Detroit, MI",
            manager_name="Plant Manager - Detroit",
            contact_email="detroit@abcmanufacturing.com",
            created_at=datetime.utcnow()
        )
        db.add(plant1)
        db.flush()

        plant2 = Entity(
            name="Chicago Manufacturing Plant",
            type="Plant",
            level=3,
            code="CHI-PLT",
            parent_id=div1.id,
            location="Chicago, IL",
            manager_name="Plant Manager - Chicago",
            contact_email="chicago@abcmanufacturing.com",
            created_at=datetime.utcnow()
        )
        db.add(plant2)
        db.flush()

        # Departments
        dept1 = Entity(
            name="Quality Department",
            type="Department",
            level=4,
            code="QUA-DEPT",
            parent_id=plant1.id,
            location="Detroit Plant - Building A",
            manager_name="QA Manager",
            created_at=datetime.utcnow()
        )
        db.add(dept1)

        dept2 = Entity(
            name="Production Department",
            type="Department",
            level=4,
            code="PRO-DEPT",
            parent_id=plant1.id,
            location="Detroit Plant - Building B",
            manager_name="Production Manager",
            created_at=datetime.utcnow()
        )
        db.add(dept2)

        db.commit()

    print("✓ Created organizational hierarchy (1 company, 1 division, 2 plants, 2 departments)")


def seed_audit_programs():
    """Seed audit programs"""
    print("Seeding audit programs...")

    programs_data = [
        ("2024 ISO 9001 Audit Program", 2024, "ISO 9001:2015", "Annual"),
        ("2024 ISO 14001 Audit Program", 2024, "ISO 14001:2015", "Semi-Annual"),
        ("2025 ISO 9001 Audit Program", 2025, "ISO 9001:2015", "Annual"),
    ]

    with get_db() as db:
        for name, year, standard, frequency in programs_data:
            program = AuditProgram(
                name=name,
                year=year,
                standard=standard,
                frequency=frequency,
                scope=f"Complete {standard} audit coverage",
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.add(program)

        db.commit()

    print(f"✓ Created {len(programs_data)} audit programs")


def seed_audit_types():
    """Seed audit types"""
    print("Seeding audit types...")

    types_data = [
        ("Internal Quality Audit", "ISO 9001 quality management system audit", 4.0, 2),
        ("Environmental Audit", "ISO 14001 environmental management audit", 6.0, 2),
        ("Process Audit", "Specific process or department audit", 3.0, 1),
        ("Supplier Audit", "Second-party supplier assessment", 8.0, 3),
    ]

    with get_db() as db:
        for name, desc, duration, team_size in types_data:
            audit_type = AuditType(
                name=name,
                description=desc,
                default_duration_hours=duration,
                default_team_size=team_size
            )
            db.add(audit_type)

        db.commit()

    print(f"✓ Created {len(types_data)} audit types")


def seed_checklists():
    """Seed sample checklists"""
    print("Seeding checklists...")

    with get_db() as db:
        checklist = Checklist(
            name="ISO 9001:2015 Checklist",
            version="1.0",
            standard="ISO 9001:2015",
            description="Standard ISO 9001:2015 audit checklist",
            is_template=True,
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.add(checklist)
        db.flush()

        # Add sample items
        items_data = [
            ("4.1", "Understanding the organization and its context", "interview"),
            ("4.2", "Understanding the needs and expectations of interested parties", "document_review"),
            ("5.1", "Leadership and commitment", "interview"),
            ("6.1", "Actions to address risks and opportunities", "document_review"),
            ("7.1.5", "Monitoring and measuring resources", "observation"),
            ("8.1", "Operational planning and control", "document_review"),
            ("9.1", "Monitoring, measurement, analysis and evaluation", "document_review"),
            ("10.1", "General improvement requirements", "interview"),
        ]

        for idx, (clause, requirement, method) in enumerate(items_data):
            item = ChecklistItem(
                checklist_id=checklist.id,
                clause_no=clause,
                requirement=requirement,
                verification_method=method,
                sequence_number=idx + 1
            )
            db.add(item)

        db.commit()

    print("✓ Created ISO 9001:2015 checklist with 8 items")


def seed_schedules_and_audits():
    """Seed audit schedules and sample audits"""
    print("Seeding audit schedules...")

    with get_db() as db:
        # Get references
        program = db.query(AuditProgram).filter_by(year=2024).first()
        audit_type = db.query(AuditType).filter_by(name="Internal Quality Audit").first()
        entities = db.query(Entity).filter_by(type="Department").all()
        auditor = db.query(User).filter_by(role=UserRole.AUDITOR).first()

        if not all([program, audit_type, entities, auditor]):
            print("⚠ Missing required data for schedules")
            return

        # Create schedules
        for idx, entity in enumerate(entities[:3]):
            schedule = AuditSchedule(
                schedule_number=f"AUD-2024-{idx + 1:04d}",
                program_id=program.id,
                audit_type_id=audit_type.id,
                auditee_entity_id=entity.id,
                auditor_id=auditor.id,
                planned_date=datetime.now() + timedelta(days=14 + idx * 7),
                planned_duration_hours=4.0,
                objectives="Verify compliance with ISO 9001:2015 requirements",
                scope=f"Quality management processes in {entity.name}",
                status=AuditStatus.SCHEDULED,
                created_at=datetime.utcnow()
            )
            db.add(schedule)
            db.flush()

            # Create one completed audit
            if idx == 0:
                audit = Audit(
                    audit_number=f"AUD-EX-2024-{idx + 1:04d}",
                    schedule_id=schedule.id,
                    actual_date=datetime.now() - timedelta(days=5),
                    start_time=datetime.now() - timedelta(days=5),
                    end_time=datetime.now() - timedelta(days=5, hours=-4),
                    duration_hours=4.0,
                    status=AuditStatus.COMPLETED,
                    completion_percentage=100.0,
                    score=85.5,
                    findings_count=3,
                    nc_count=1,
                    ofi_count=2,
                    observations_count=0,
                    executive_summary="Audit completed successfully. Overall compliance is good with minor findings.",
                    strengths="Strong documentation control, effective training program, good management commitment.",
                    opportunities="Improve internal communication, enhance risk assessment process.",
                    overall_conclusion="Recommend certification with minor corrective actions.",
                    created_at=datetime.utcnow() - timedelta(days=5),
                    completed_at=datetime.utcnow() - timedelta(days=4)
                )
                db.add(audit)
                db.flush()

                # Add sample NC/OFI
                nc = NC_OFI(
                    nc_number=f"NC-2024-0001",
                    audit_id=audit.id,
                    type=FindingType.NC,
                    severity=Severity.MINOR,
                    category="Documentation",
                    clause="4.2.3",
                    description="Training records for 3 employees are not up to date.",
                    assignee_id=auditor.id,
                    due_date=datetime.now() + timedelta(days=30),
                    status=NCStatus.OPEN,
                    created_at=datetime.utcnow() - timedelta(days=4)
                )
                db.add(nc)
                db.flush()

                ofi1 = NC_OFI(
                    nc_number=f"OFI-2024-0001",
                    audit_id=audit.id,
                    type=FindingType.OFI,
                    severity=Severity.OBSERVATION,
                    category="Process",
                    clause="8.1",
                    description="Consider implementing automated workflow for change requests.",
                    assignee_id=auditor.id,
                    status=NCStatus.OPEN,
                    created_at=datetime.utcnow() - timedelta(days=4)
                )
                db.add(ofi1)

                # Add CAR for NC
                car = CorrectiveAction(
                    car_number=f"CAR-2024-0001",
                    nc_ofi_id=nc.id,
                    method=CARMethod.EIGHT_D,
                    problem_description="Training records not maintained for 3 employees",
                    root_cause="Lack of automated reminder system for training renewals",
                    action_plan="Implement automated training tracking system with email reminders",
                    assigned_to_id=auditor.id,
                    due_date=datetime.now() + timedelta(days=30),
                    status=CARStatus.IN_PROGRESS,
                    created_at=datetime.utcnow() - timedelta(days=3)
                )
                db.add(car)

        db.commit()

    print("✓ Created 3 audit schedules, 1 completed audit with findings, and 1 CAR")


def main():
    """Main seeding function"""
    print("\n" + "=" * 60)
    print("AUDIT PRO ENTERPRISE - Sample Data Seeding")
    print("SESSION-APE-001")
    print("=" * 60 + "\n")

    # Initialize database
    print("Initializing database...")
    init_database()
    print("✓ Database initialized\n")

    # Seed data
    seed_users()
    seed_entities()
    seed_audit_programs()
    seed_audit_types()
    seed_checklists()
    seed_schedules_and_audits()

    print("\n" + "=" * 60)
    print("✅ Sample data seeding completed successfully!")
    print("=" * 60)
    print("\nDefault login credentials:")
    print("  Username: admin")
    print("  Password: admin123")
    print("\nOther test users:")
    print("  auditor1 / auditor123")
    print("  auditee1 / auditee123")
    print("  viewer1 / viewer123")
    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
