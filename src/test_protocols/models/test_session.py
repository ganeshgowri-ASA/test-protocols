"""Test session database model."""

from sqlalchemy import Column, String, Integer, JSON, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional

from .base import Base


class TestSession(Base):
    """Database model for test execution sessions."""

    __tablename__ = "test_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)

    # Foreign key to protocol
    protocol_id = Column(Integer, ForeignKey("protocols.id"), nullable=False)

    # Test metadata
    test_name = Column(String(200))
    operator = Column(String(100))
    location = Column(String(200))
    device_under_test = Column(String(200))  # e.g., module serial number

    # Status: pending, running, completed, completed_with_errors, failed
    status = Column(String(20), nullable=False, default="pending", index=True)

    # Timestamps
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)

    # Test data and results stored as JSON
    test_data = Column(JSON)  # Input measurement data
    results = Column(JSON)  # Test results including analysis
    qc_results = Column(JSON)  # Quality check results

    # Error information
    error_message = Column(Text)

    # Additional notes
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    protocol = relationship("Protocol", back_populates="test_sessions")
    measurements = relationship(
        "Measurement",
        back_populates="session",
        cascade="all, delete-orphan",
    )
    reports = relationship(
        "Report",
        back_populates="session",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<TestSession(id={self.id}, session_id='{self.session_id}', status='{self.status}')>"

    def to_dict(self, include_data: bool = False) -> dict:
        """
        Convert to dictionary.

        Args:
            include_data: Whether to include full test data and results

        Returns:
            Dictionary representation
        """
        data = {
            "id": self.id,
            "session_id": self.session_id,
            "protocol_id": self.protocol_id,
            "test_name": self.test_name,
            "operator": self.operator,
            "location": self.location,
            "device_under_test": self.device_under_test,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "error_message": self.error_message,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_data:
            data["test_data"] = self.test_data
            data["results"] = self.results
            data["qc_results"] = self.qc_results

        return data

    def update_status(self, status: str, error: Optional[str] = None) -> None:
        """
        Update session status.

        Args:
            status: New status
            error: Error message if status is 'failed'
        """
        self.status = status
        self.updated_at = datetime.utcnow()

        if status == "running" and not self.started_at:
            self.started_at = datetime.utcnow()

        if status in ["completed", "completed_with_errors", "failed"]:
            self.completed_at = datetime.utcnow()
            if self.started_at:
                self.duration_seconds = (
                    self.completed_at - self.started_at
                ).total_seconds()

        if error:
            self.error_message = error

    def get_summary(self) -> dict:
        """
        Get summary of test session.

        Returns:
            Summary dictionary
        """
        summary = {
            "session_id": self.session_id,
            "protocol": self.protocol.name if self.protocol else None,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "duration_seconds": self.duration_seconds,
        }

        # Add result summary if available
        if self.results:
            if "analysis" in self.results:
                summary["analysis_summary"] = {
                    k: v
                    for k, v in self.results["analysis"].items()
                    if k in ["energy_rating", "stc_performance"]
                }

            if "qc_results" in self.results:
                qc_results = self.results["qc_results"]
                summary["qc_summary"] = {
                    "total_checks": len(qc_results),
                    "passed": sum(1 for qc in qc_results if qc.get("passed")),
                    "failed": sum(
                        1 for qc in qc_results if not qc.get("passed") and qc.get("severity") == "error"
                    ),
                }

        return summary
