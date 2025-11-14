"""Base protocol classes for test execution"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
import logging


logger = logging.getLogger(__name__)


class StepStatus(Enum):
    """Status of a protocol step"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StepResult:
    """Result of a step execution"""
    success: bool
    error: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Step:
    """Individual test step"""
    name: str
    step_type: str
    description: str = ""
    status: StepStatus = StepStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result: Optional[StepResult] = None

    def start(self):
        """Mark step as started"""
        self.status = StepStatus.IN_PROGRESS
        self.start_time = datetime.now()
        logger.info(f"Starting step: {self.name}")

    def mark_complete(self, success: bool, error: Optional[str] = None, data: Optional[Dict] = None):
        """Mark step as complete"""
        self.end_time = datetime.now()
        self.status = StepStatus.COMPLETED if success else StepStatus.FAILED
        self.result = StepResult(
            success=success,
            error=error,
            data=data or {},
            timestamp=self.end_time
        )

        duration = (self.end_time - self.start_time).total_seconds() if self.start_time else 0
        logger.info(f"Step '{self.name}' {'completed' if success else 'failed'} in {duration:.2f}s")

    @property
    def duration_seconds(self) -> float:
        """Calculate step duration"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0


class BaseProtocol(ABC):
    """
    Abstract base class for all test protocols.

    All protocol implementations should inherit from this class and implement
    the required abstract methods.
    """

    PROTOCOL_ID: str = "BASE-000"
    STANDARD: str = "N/A"

    def __init__(self):
        """Initialize base protocol"""
        self.steps: List[Step] = []
        self.test_start_time: Optional[datetime] = None
        self.test_end_time: Optional[datetime] = None
        self.test_result: Optional[bool] = None

    @abstractmethod
    def execute(self) -> bool:
        """
        Execute the full protocol.

        Returns:
            bool: True if test passed, False otherwise
        """
        pass

    @abstractmethod
    def evaluate_results(self) -> bool:
        """
        Evaluate test results against acceptance criteria.

        Returns:
            bool: True if criteria met, False otherwise
        """
        pass

    @abstractmethod
    def get_report_data(self) -> Dict:
        """
        Generate report data.

        Returns:
            Dict: Report data including results and measurements
        """
        pass

    def add_step(self, step: Step):
        """Add a step to the protocol"""
        self.steps.append(step)

    def get_total_duration(self) -> float:
        """Get total test duration in hours"""
        if self.test_start_time and self.test_end_time:
            return (self.test_end_time - self.test_start_time).total_seconds() / 3600
        return 0.0

    def get_step_summary(self) -> Dict[str, int]:
        """Get summary of step statuses"""
        summary = {status.value: 0 for status in StepStatus}
        for step in self.steps:
            summary[step.status.value] += 1
        return summary
