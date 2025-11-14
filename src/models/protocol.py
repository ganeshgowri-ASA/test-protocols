"""Protocol model for storing test protocol definitions."""

from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, Any

from .base import Base, TimestampMixin


class Protocol(Base, TimestampMixin):
    """Model representing a test protocol definition.

    This model stores the complete protocol definition loaded from JSON,
    including all test parameters, steps, and acceptance criteria.
    """

    __tablename__ = "protocols"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    protocol_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    protocol_name: Mapped[str] = mapped_column(String(200), nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Store complete protocol definition as JSON
    protocol_data: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Metadata
    author: Mapped[Optional[str]] = mapped_column(String(100))
    tags: Mapped[Optional[str]] = mapped_column(String(500))  # Comma-separated tags
    is_active: Mapped[bool] = mapped_column(default=True)

    # Relationships
    test_runs: Mapped[List["TestRun"]] = relationship(
        "TestRun",
        back_populates="protocol",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of Protocol."""
        return f"<Protocol(id={self.id}, protocol_id='{self.protocol_id}', name='{self.protocol_name}')>"

    def to_dict(self) -> dict:
        """Convert protocol to dictionary format.

        Returns:
            Dictionary representation of the protocol.
        """
        return {
            "id": self.id,
            "protocol_id": self.protocol_id,
            "protocol_name": self.protocol_name,
            "version": self.version,
            "category": self.category,
            "description": self.description,
            "protocol_data": self.protocol_data,
            "author": self.author,
            "tags": self.tags.split(",") if self.tags else [],
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
