"""
Test Session Model

Data model for test execution sessions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum

from .base import BaseModel


class TestStatus(str, Enum):
    """Test session status enumeration."""
    INITIATED = "INITIATED"
    IN_PROGRESS = "IN_PROGRESS"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass
class TestSession(BaseModel):
    """
    Test session data model.

    Represents a single execution instance of a test protocol.
    """

    session_id: str
    protocol_id: str
    protocol_version: str
    test_status: str = TestStatus.INITIATED.value
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    operator_id: Optional[str] = None
    operator_name: Optional[str] = None
    samples: List[str] = field(default_factory=list)
    test_conditions: Dict[str, Any] = field(default_factory=dict)
    measurements_count: int = 0
    qc_checks_count: int = 0
    qc_failures: int = 0
    overall_result: Optional[str] = None  # PASS, FAIL, WARNING
    notes: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def start_test(self):
        """Mark test as in progress."""
        self.test_status = TestStatus.IN_PROGRESS.value
        self.started_at = datetime.now()

    def complete_test(self, result: str):
        """
        Mark test as completed.

        Args:
            result: Overall test result (PASS, FAIL, WARNING)
        """
        self.test_status = TestStatus.COMPLETED.value
        self.completed_at = datetime.now()
        self.overall_result = result
        self.update()

    def fail_test(self, reason: Optional[str] = None):
        """
        Mark test as failed.

        Args:
            reason: Failure reason
        """
        self.test_status = TestStatus.FAILED.value
        self.completed_at = datetime.now()
        if reason:
            self.notes = f"{self.notes or ''}\nFailure: {reason}"
        self.update()

    def pause_test(self):
        """Mark test as paused."""
        self.test_status = TestStatus.PAUSED.value
        self.update()

    def resume_test(self):
        """Resume paused test."""
        if self.test_status == TestStatus.PAUSED.value:
            self.test_status = TestStatus.IN_PROGRESS.value
            self.update()

    def get_duration_hours(self) -> Optional[float]:
        """
        Get test duration in hours.

        Returns:
            Duration in hours, or None if not completed
        """
        if not self.completed_at:
            return None

        duration = self.completed_at - self.started_at
        return duration.total_seconds() / 3600

    def is_active(self) -> bool:
        """Check if test is currently active."""
        return self.test_status in [TestStatus.IN_PROGRESS.value, TestStatus.PAUSED.value]

    def is_completed(self) -> bool:
        """Check if test is completed."""
        return self.test_status == TestStatus.COMPLETED.value

    def add_sample(self, sample_id: str):
        """Add sample to test session."""
        if sample_id not in self.samples:
            self.samples.append(sample_id)
            self.update()
