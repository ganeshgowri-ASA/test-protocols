"""
Audit Models
============
Models for audit programs, types, schedules, and execution.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from config.database import Base
import enum


class AuditStatus(str, enum.Enum):
    """Audit status enumeration"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    PENDING_REVIEW = "pending_review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AuditProgram(Base):
    """Annual audit program/plan"""
    __tablename__ = "audit_programs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    year = Column(Integer, nullable=False)
    standard = Column(String(100))  # ISO 9001, ISO 14001, etc.
    frequency = Column(String(50))  # Annual, Semi-Annual, Quarterly, Monthly
    scope = Column(Text)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    schedules = relationship("AuditSchedule", back_populates="program")

    def __repr__(self):
        return f"<AuditProgram(name='{self.name}', year={self.year})>"


class AuditType(Base):
    """Audit type/category definition"""
    __tablename__ = "audit_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    checklist_template_id = Column(Integer, ForeignKey("checklists.id"))

    # Default configuration
    default_duration_hours = Column(Float)
    default_team_size = Column(Integer)

    # Relationships
    checklist_template = relationship("Checklist")
    schedules = relationship("AuditSchedule", back_populates="audit_type")

    def __repr__(self):
        return f"<AuditType(name='{self.name}')>"


class AuditSchedule(Base):
    """Scheduled audit instance"""
    __tablename__ = "audit_schedules"

    id = Column(Integer, primary_key=True, index=True)
    schedule_number = Column(String(50), unique=True, nullable=False, index=True)

    # Links
    program_id = Column(Integer, ForeignKey("audit_programs.id"), nullable=False)
    audit_type_id = Column(Integer, ForeignKey("audit_types.id"), nullable=False)
    auditee_entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False)
    auditor_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Schedule details
    planned_date = Column(DateTime, nullable=False)
    planned_duration_hours = Column(Float)
    objectives = Column(Text)
    scope = Column(Text)

    # Status
    status = Column(Enum(AuditStatus), default=AuditStatus.SCHEDULED)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    program = relationship("AuditProgram", back_populates="schedules")
    audit_type = relationship("AuditType", back_populates="schedules")
    auditee_entity = relationship("Entity", back_populates="audit_schedules")
    auditor = relationship("User", back_populates="scheduled_audits")
    audit = relationship("Audit", uselist=False, back_populates="schedule")

    def __repr__(self):
        return f"<AuditSchedule(number='{self.schedule_number}', status='{self.status}')>"


class Audit(Base):
    """Actual audit execution"""
    __tablename__ = "audits"

    id = Column(Integer, primary_key=True, index=True)
    audit_number = Column(String(50), unique=True, nullable=False, index=True)

    # Link to schedule
    schedule_id = Column(Integer, ForeignKey("audit_schedules.id"), nullable=False)

    # Execution details
    actual_date = Column(DateTime)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration_hours = Column(Float)

    # Team members (JSON array of user IDs)
    audit_team = Column(JSON)
    auditees_present = Column(JSON)

    # Results summary
    score = Column(Float)
    findings_count = Column(Integer, default=0)
    nc_count = Column(Integer, default=0)
    ofi_count = Column(Integer, default=0)
    observations_count = Column(Integer, default=0)

    # Status
    status = Column(Enum(AuditStatus), default=AuditStatus.IN_PROGRESS)
    completion_percentage = Column(Float, default=0.0)

    # Summary
    executive_summary = Column(Text)
    strengths = Column(Text)
    opportunities = Column(Text)
    overall_conclusion = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)

    # Relationships
    schedule = relationship("AuditSchedule", back_populates="audit")
    responses = relationship("AuditResponse", back_populates="audit")
    nc_ofis = relationship("NC_OFI", back_populates="audit")
    reports = relationship("AuditReport", back_populates="audit")

    def __repr__(self):
        return f"<Audit(number='{self.audit_number}', status='{self.status}')>"
