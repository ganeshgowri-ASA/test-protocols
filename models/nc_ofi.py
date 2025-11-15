"""
NC/OFI Model
============
Non-Conformance and Opportunity for Improvement tracking.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from config.database import Base
import enum


class FindingType(str, enum.Enum):
    """Type of finding"""
    NC = "nc"  # Non-Conformance
    OFI = "ofi"  # Opportunity for Improvement
    OBSERVATION = "observation"


class Severity(str, enum.Enum):
    """Severity level"""
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    OBSERVATION = "observation"


class NCStatus(str, enum.Enum):
    """NC/OFI status"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING_VERIFICATION = "pending_verification"
    CLOSED = "closed"
    REJECTED = "rejected"


class NC_OFI(Base):
    """Non-Conformance and Opportunity for Improvement"""
    __tablename__ = "nc_ofi"

    id = Column(Integer, primary_key=True, index=True)
    nc_number = Column(String(50), unique=True, nullable=False, index=True)

    # Link to audit
    audit_id = Column(Integer, ForeignKey("audits.id"), nullable=False)

    # Finding details
    type = Column(Enum(FindingType), nullable=False)
    category = Column(String(100))  # Documentation, Process, Product, etc.
    clause = Column(String(50))  # Standard clause reference
    description = Column(Text, nullable=False)
    severity = Column(Enum(Severity), nullable=False)

    # Assignment
    assignee_id = Column(Integer, ForeignKey("users.id"))
    due_date = Column(DateTime)

    # Status
    status = Column(Enum(NCStatus), default=NCStatus.OPEN)

    # Evidence
    evidence_description = Column(Text)
    attachments = Column(JSON)  # List of file paths

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = Column(DateTime)

    # Relationships
    audit = relationship("Audit", back_populates="nc_ofis")
    assignee = relationship("User", back_populates="assigned_nc_ofi")
    corrective_actions = relationship("CorrectiveAction", back_populates="nc_ofi")

    def __repr__(self):
        return f"<NC_OFI(number='{self.nc_number}', type='{self.type}', severity='{self.severity}')>"
