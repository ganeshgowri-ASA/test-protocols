"""Protocol model for storing protocol definitions."""

from sqlalchemy import Column, String, Text, JSON, Boolean
from .base import Base, IDMixin, TimestampMixin


class Protocol(Base, IDMixin, TimestampMixin):
    """
    Protocol model representing a test protocol definition.

    This stores metadata about protocols loaded from JSON definitions.
    """

    __tablename__ = "protocols"

    protocol_id = Column(String(50), unique=True, nullable=False, index=True)
    protocol_name = Column(String(200), nullable=False)
    version = Column(String(20), nullable=False)
    category = Column(String(50), nullable=False, index=True)
    description = Column(Text)

    # JSON fields for flexible schema
    parameters = Column(JSON, nullable=False)
    measurements = Column(JSON, nullable=False)
    qc_criteria = Column(JSON, nullable=False)
    test_procedure = Column(JSON)
    analysis_methods = Column(JSON)
    standards = Column(JSON)  # Array of standard names
    metadata = Column(JSON)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<Protocol(id={self.protocol_id}, name='{self.protocol_name}', version={self.version})>"

    def to_dict(self):
        """Convert protocol to dictionary."""
        return {
            "id": self.id,
            "protocol_id": self.protocol_id,
            "protocol_name": self.protocol_name,
            "version": self.version,
            "category": self.category,
            "description": self.description,
            "parameters": self.parameters,
            "measurements": self.measurements,
            "qc_criteria": self.qc_criteria,
            "test_procedure": self.test_procedure,
            "analysis_methods": self.analysis_methods,
            "standards": self.standards,
            "metadata": self.metadata,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
