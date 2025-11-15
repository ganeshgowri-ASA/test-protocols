"""
Base Models - AuditReport and AuditLog
=======================================
Common models used across the application.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from config.database import Base


class AuditReport(Base):
    """Audit report generation tracking"""
    __tablename__ = "audit_reports"

    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(Integer, ForeignKey("audits.id"), nullable=False)

    # Report metadata
    report_number = Column(String(50), unique=True, nullable=False, index=True)
    report_type = Column(String(50))  # executive_summary, detailed, nc_summary
    generated_at = Column(DateTime, default=datetime.utcnow)
    generated_by_id = Column(Integer, ForeignKey("users.id"))

    # Report content
    summary = Column(Text)
    pdf_path = Column(String(200))
    excel_path = Column(String(200))

    # Report data snapshot
    data_snapshot = Column(JSON)  # Snapshot of audit data at report generation

    # Relationships
    audit = relationship("Audit", back_populates="reports")
    generated_by = relationship("User")

    def __repr__(self):
        return f"<AuditReport(number='{self.report_number}', type='{self.report_type}')>"


class AuditLog(Base):
    """Audit trail for all system changes"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Who did what
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)  # create, update, delete, login, etc.

    # What was affected
    table_name = Column(String(50))
    record_id = Column(Integer)

    # Change details
    old_values = Column(JSON)
    new_values = Column(JSON)
    changes_summary = Column(Text)

    # Context
    ip_address = Column(String(50))
    session_id = Column(String(100))

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(action='{self.action}', table='{self.table_name}')>"
