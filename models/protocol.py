"""
Protocol database models
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import BaseModel


class Protocol(BaseModel):
    """Protocol definition model"""

    __tablename__ = 'protocols'

    protocol_id = Column(String(50), unique=True, nullable=False, index=True)
    protocol_name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50), nullable=False)
    standard_name = Column(String(100), nullable=False)
    standard_version = Column(String(50))
    standard_section = Column(String(100))
    is_active = Column(Boolean, default=True, nullable=False)
    tags = Column(JSON)  # Array of tags

    # Relationships
    versions = relationship("ProtocolVersion", back_populates="protocol", cascade="all, delete-orphan")
    tests = relationship("TestExecution", back_populates="protocol")

    def __repr__(self):
        return f"<Protocol(id={self.id}, protocol_id='{self.protocol_id}', name='{self.protocol_name}')>"


class ProtocolVersion(BaseModel):
    """Protocol version model"""

    __tablename__ = 'protocol_versions'

    protocol_id = Column(Integer, ForeignKey('protocols.id'), nullable=False, index=True)
    version = Column(String(20), nullable=False)
    configuration = Column(JSON, nullable=False)  # Full protocol configuration
    is_current = Column(Boolean, default=False, nullable=False)
    release_date = Column(DateTime, default=datetime.utcnow)
    release_notes = Column(Text)

    # Relationships
    protocol = relationship("Protocol", back_populates="versions")

    def __repr__(self):
        return f"<ProtocolVersion(id={self.id}, version='{self.version}', current={self.is_current})>"
