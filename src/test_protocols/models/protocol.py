"""Protocol database model."""

from sqlalchemy import Column, String, Integer, JSON, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


class Protocol(Base):
    """Database model for test protocols."""

    __tablename__ = "protocols"

    id = Column(Integer, primary_key=True, autoincrement=True)
    protocol_id = Column(String(50), unique=True, nullable=False, index=True)
    version = Column(String(20), nullable=False)
    name = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False, index=True)
    description = Column(Text)

    # Store full protocol configuration as JSON
    config = Column(JSON, nullable=False)

    # Metadata
    author = Column(String(200))
    standards = Column(JSON)  # List of standard names
    equipment_required = Column(JSON)  # List of equipment

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    test_sessions = relationship(
        "TestSession",
        back_populates="protocol",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Protocol(id={self.id}, protocol_id='{self.protocol_id}', version='{self.version}')>"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "protocol_id": self.protocol_id,
            "version": self.version,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "author": self.author,
            "standards": self.standards,
            "equipment_required": self.equipment_required,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_config(cls, config: dict) -> "Protocol":
        """
        Create Protocol instance from configuration dictionary.

        Args:
            config: Protocol configuration dictionary

        Returns:
            Protocol instance
        """
        metadata = config.get("metadata", {})

        return cls(
            protocol_id=config["protocol_id"],
            version=config["version"],
            name=config["name"],
            category=config["category"],
            description=config.get("description", ""),
            config=config,
            author=metadata.get("author"),
            standards=metadata.get("standards", []),
            equipment_required=metadata.get("equipment_required", []),
        )
