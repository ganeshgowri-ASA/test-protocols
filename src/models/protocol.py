"""
Protocol and ProtocolVersion models
"""

from sqlalchemy import Column, Integer, String, JSON, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class Protocol(Base):
    """
    Main protocol definition table
    """
    __tablename__ = "protocols"

    id = Column(Integer, primary_key=True, index=True)
    protocol_id = Column(String(50), unique=True, nullable=False, index=True)
    protocol_name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False, index=True)
    standard_name = Column(String(100), nullable=False)
    standard_section = Column(String(50), nullable=False)
    standard_edition = Column(String(50))
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    versions = relationship("ProtocolVersion", back_populates="protocol")
    test_executions = relationship("TestExecution", back_populates="protocol")

    def __repr__(self):
        return f"<Protocol(protocol_id='{self.protocol_id}', name='{self.protocol_name}')>"


class ProtocolVersion(Base):
    """
    Protocol version history and JSON definitions
    """
    __tablename__ = "protocol_versions"

    id = Column(Integer, primary_key=True, index=True)
    protocol_id = Column(Integer, ForeignKey("protocols.id"), nullable=False)
    version = Column(String(20), nullable=False)
    json_definition = Column(JSON, nullable=False)

    # Metadata
    author = Column(String(255))
    reviewer = Column(String(255))
    approved_by = Column(String(255))
    approval_date = Column(DateTime)
    is_current = Column(Boolean, default=False)
    change_notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    protocol = relationship("Protocol", back_populates="versions")

    def __repr__(self):
        return f"<ProtocolVersion(protocol_id={self.protocol_id}, version='{self.version}')>"
