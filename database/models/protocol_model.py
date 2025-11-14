"""Protocol database model"""

from sqlalchemy import Column, String, Text, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Protocol(Base):
    """Protocol definition model"""

    __tablename__ = "protocols"

    protocol_id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    version = Column(String(20), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text)

    # Store full JSON definition
    definition_json = Column(JSON, nullable=False)
    metadata_json = Column(JSON)

    # Status and tracking
    status = Column(String(20), default="active")  # active, deprecated, draft
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100))
    updated_by = Column(String(100))

    # Approval tracking
    approval_status = Column(String(20), default="draft")  # draft, approved, rejected
    approved_by = Column(String(100))
    approved_at = Column(DateTime)

    def __repr__(self):
        return f"<Protocol(id='{self.protocol_id}', name='{self.name}', version='{self.version}')>"
