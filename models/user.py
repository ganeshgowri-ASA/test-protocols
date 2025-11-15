"""
User Model
==========
User authentication and authorization model.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from config.database import Base
import enum


class UserRole(str, enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"
    AUDITOR = "auditor"
    AUDITEE = "auditee"
    VIEWER = "viewer"


class User(Base):
    """User model for authentication and authorization"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.VIEWER)

    # Additional information
    phone = Column(String(20))
    department = Column(String(100))

    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

    # Relationships
    audit_logs = relationship("AuditLog", back_populates="user")
    scheduled_audits = relationship("AuditSchedule", back_populates="auditor")
    assigned_nc_ofi = relationship("NC_OFI", foreign_keys="NC_OFI.assignee_id", back_populates="assignee")
    assigned_cars = relationship("CorrectiveAction", foreign_keys="CorrectiveAction.assigned_to_id", back_populates="assigned_to")

    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"
