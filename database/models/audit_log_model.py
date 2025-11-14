"""Audit log database model"""

from sqlalchemy import Column, String, DateTime, JSON, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class AuditLog(Base):
    """Audit trail model for tracking all system activities"""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Event information
    event_type = Column(
        String(50), nullable=False, index=True
    )  # create, update, delete, approve, reject, etc.
    entity_type = Column(
        String(50), nullable=False, index=True
    )  # protocol, test_execution, qc_review, etc.
    entity_id = Column(String(100), nullable=False, index=True)

    # User information
    user_id = Column(String(100), nullable=False, index=True)
    user_name = Column(String(255))
    user_role = Column(String(50))

    # Event details
    action_description = Column(Text, nullable=False)
    old_values = Column(JSON)  # Previous state (for updates)
    new_values = Column(JSON)  # New state
    metadata = Column(JSON)  # Additional context

    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Request information
    ip_address = Column(String(45))  # IPv4 or IPv6
    user_agent = Column(String(500))
    session_id = Column(String(100))

    def __repr__(self):
        return f"<AuditLog(id={self.id}, type='{self.event_type}', entity='{self.entity_type}:{self.entity_id}')>"
