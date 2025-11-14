"""TestRun model for storing test execution instances."""

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base, IDMixin, TimestampMixin


class TestRun(Base, IDMixin, TimestampMixin):
    """
    TestRun model representing an instance of a protocol being executed.

    This tracks the execution of a specific protocol on a specific sample.
    """

    __tablename__ = "test_runs"

    test_run_id = Column(String(100), unique=True, nullable=False, index=True)

    # Foreign keys
    protocol_id = Column(Integer, ForeignKey("protocols.id"), nullable=False)
    sample_id = Column(Integer, ForeignKey("samples.id"), nullable=False)

    # Relationships
    protocol = relationship("Protocol", backref="test_runs")
    sample = relationship("Sample", backref="test_runs")
    measurements = relationship("Measurement", back_populates="test_run", cascade="all, delete-orphan")
    qc_results = relationship("QCResult", back_populates="test_run", cascade="all, delete-orphan")

    # Test execution info
    operator = Column(String(100))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)

    # Status tracking
    status = Column(String(50), default="pending")  # pending, in_progress, completed, failed, cancelled
    progress_percent = Column(Integer, default=0)

    # Test configuration (can override protocol defaults)
    test_parameters = Column(JSON)

    # Results summary
    results_summary = Column(JSON)  # Store calculated results, degradation %, etc.

    # Notes and metadata
    notes = Column(Text)
    metadata = Column(JSON)

    def __repr__(self):
        return f"<TestRun(id={self.test_run_id}, protocol={self.protocol_id}, status='{self.status}')>"

    def to_dict(self):
        """Convert test run to dictionary."""
        return {
            "id": self.id,
            "test_run_id": self.test_run_id,
            "protocol_id": self.protocol_id,
            "sample_id": self.sample_id,
            "operator": self.operator,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
            "progress_percent": self.progress_percent,
            "test_parameters": self.test_parameters,
            "results_summary": self.results_summary,
            "notes": self.notes,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def calculate_duration(self):
        """Calculate test duration in hours."""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return delta.total_seconds() / 3600
        return None
