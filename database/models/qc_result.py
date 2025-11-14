"""QCResult model for storing quality control check results."""

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base, IDMixin, TimestampMixin


class QCResult(Base, IDMixin, TimestampMixin):
    """
    QCResult model representing quality control check results.

    This stores the results of automated QC checks performed on test data.
    """

    __tablename__ = "qc_results"

    # Foreign key
    test_run_id = Column(Integer, ForeignKey("test_runs.id"), nullable=False, index=True)

    # Relationship
    test_run = relationship("TestRun", back_populates="qc_results")

    # QC check identification
    check_name = Column(String(100), nullable=False)
    check_category = Column(String(50))  # e.g., "measurement_validation", "environmental", "degradation"
    check_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # QC result
    passed = Column(Boolean, nullable=False)
    severity = Column(String(20))  # info, warning, error, critical

    # Details
    expected_value = Column(String(200))
    actual_value = Column(String(200))
    threshold = Column(String(200))

    message = Column(Text)  # Human-readable message
    details = Column(JSON)  # Additional structured data

    # Recommendations
    recommendation = Column(Text)  # Suggested action

    # Resolution tracking
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(100))
    acknowledged_at = Column(DateTime)
    resolution_notes = Column(Text)

    def __repr__(self):
        status = "PASS" if self.passed else "FAIL"
        return f"<QCResult(check='{self.check_name}', status={status}, severity='{self.severity}')>"

    def to_dict(self):
        """Convert QC result to dictionary."""
        return {
            "id": self.id,
            "test_run_id": self.test_run_id,
            "check_name": self.check_name,
            "check_category": self.check_category,
            "check_timestamp": self.check_timestamp.isoformat() if self.check_timestamp else None,
            "passed": self.passed,
            "severity": self.severity,
            "expected_value": self.expected_value,
            "actual_value": self.actual_value,
            "threshold": self.threshold,
            "message": self.message,
            "details": self.details,
            "recommendation": self.recommendation,
            "acknowledged": self.acknowledged,
            "acknowledged_by": self.acknowledged_by,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolution_notes": self.resolution_notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
