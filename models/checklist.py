"""
Checklist Models
================
Models for audit checklists, items, and responses.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from config.database import Base
import enum


class ResponseStatus(str, enum.Enum):
    """Checklist item response status"""
    NOT_CHECKED = "not_checked"
    CONFORMING = "conforming"
    NON_CONFORMING = "non_conforming"
    NOT_APPLICABLE = "not_applicable"
    OBSERVATION = "observation"


class Checklist(Base):
    """Audit checklist template"""
    __tablename__ = "checklists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    version = Column(String(20), nullable=False)
    standard = Column(String(100))  # ISO 9001, ISO 14001, etc.
    description = Column(Text)

    # Metadata
    is_template = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    items = relationship("ChecklistItem", back_populates="checklist", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Checklist(name='{self.name}', version='{self.version}')>"


class ChecklistItem(Base):
    """Individual checklist item/question"""
    __tablename__ = "checklist_items"

    id = Column(Integer, primary_key=True, index=True)
    checklist_id = Column(Integer, ForeignKey("checklists.id"), nullable=False)

    # Item details
    clause_no = Column(String(50))  # e.g., "4.1", "7.1.5.1"
    requirement = Column(Text, nullable=False)
    verification_method = Column(String(100))  # document_review, interview, observation
    guidance = Column(Text)

    # Ordering
    sequence_number = Column(Integer, default=0)

    # Relationships
    checklist = relationship("Checklist", back_populates="items")
    responses = relationship("AuditResponse", back_populates="checklist_item")

    def __repr__(self):
        return f"<ChecklistItem(clause='{self.clause_no}', requirement='{self.requirement[:50]}...')>"


class AuditResponse(Base):
    """Auditor's response to a checklist item during audit"""
    __tablename__ = "audit_responses"

    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(Integer, ForeignKey("audits.id"), nullable=False)
    checklist_item_id = Column(Integer, ForeignKey("checklist_items.id"), nullable=False)

    # Response
    status = Column(Enum(ResponseStatus), default=ResponseStatus.NOT_CHECKED)
    evidence = Column(Text)
    remarks = Column(Text)

    # Links to NC/OFI if applicable
    nc_ofi_id = Column(Integer, ForeignKey("nc_ofi.id"))

    # Attachments (photos, documents)
    attachments = Column(JSON)  # List of file paths

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    audit = relationship("Audit", back_populates="responses")
    checklist_item = relationship("ChecklistItem", back_populates="responses")
    nc_ofi = relationship("NC_OFI")

    def __repr__(self):
        return f"<AuditResponse(audit_id={self.audit_id}, status='{self.status}')>"
