"""
Corrective Action Model (CAR/8D)
=================================
Corrective and preventive action tracking with 8D methodology support.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from config.database import Base
import enum


class CARStatus(str, enum.Enum):
    """Corrective Action status"""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    PENDING_VERIFICATION = "pending_verification"
    VERIFIED = "verified"
    CLOSED = "closed"
    REJECTED = "rejected"


class CARMethod(str, enum.Enum):
    """CAR methodology"""
    EIGHT_D = "8d"
    FIVE_WHY = "5why"
    FISHBONE = "fishbone"
    PDCA = "pdca"
    OTHER = "other"


class CorrectiveAction(Base):
    """Corrective Action Request (CAR) with 8D support"""
    __tablename__ = "corrective_actions"

    id = Column(Integer, primary_key=True, index=True)
    car_number = Column(String(50), unique=True, nullable=False, index=True)

    # Link to NC/OFI
    nc_ofi_id = Column(Integer, ForeignKey("nc_ofi.id"), nullable=False)

    # CAR details
    method = Column(Enum(CARMethod), default=CARMethod.EIGHT_D)
    problem_description = Column(Text, nullable=False)

    # 8D Steps
    # D1: Team
    team_members = Column(JSON)  # List of user IDs

    # D2: Problem Description (covered by problem_description above)

    # D3: Interim Containment Actions
    containment_actions = Column(Text)
    containment_completed_at = Column(DateTime)

    # D4: Root Cause Analysis
    root_cause = Column(Text)
    root_cause_method = Column(String(50))  # 5why, fishbone, etc.
    root_cause_diagram = Column(String(200))  # Path to diagram file

    # D5: Permanent Corrective Actions
    action_plan = Column(Text)
    responsible_person_id = Column(Integer, ForeignKey("users.id"))
    assigned_to_id = Column(Integer, ForeignKey("users.id"))

    # D6: Implementation
    implementation_date = Column(DateTime)
    implementation_evidence = Column(Text)
    implementation_attachments = Column(JSON)

    # D7: Prevent Recurrence
    preventive_actions = Column(Text)
    system_changes = Column(Text)

    # D8: Team Recognition
    team_recognition = Column(Text)
    lessons_learned = Column(Text)

    # Scheduling
    due_date = Column(DateTime)
    actual_completion_date = Column(DateTime)

    # Status
    status = Column(Enum(CARStatus), default=CARStatus.DRAFT)
    effectiveness_verified = Column(Boolean, default=False)
    verification_date = Column(DateTime)
    verification_notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = Column(DateTime)

    # Relationships
    nc_ofi = relationship("NC_OFI", back_populates="corrective_actions")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id], back_populates="assigned_cars")

    def __repr__(self):
        return f"<CorrectiveAction(number='{self.car_number}', method='{self.method}', status='{self.status}')>"
