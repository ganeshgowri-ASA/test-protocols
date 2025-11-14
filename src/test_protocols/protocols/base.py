"""Base protocol abstract class for all test protocols."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from test_protocols.constants import ProtocolCategory, QCStatus


@dataclass
class ProtocolMetadata:
    """Metadata for a test protocol."""

    code: str
    name: str
    version: str
    description: str
    category: ProtocolCategory
    standard: Optional[str] = None
    created_date: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    author: str = "ASA"


@dataclass
class QualityCheckResult:
    """Result of a quality control check."""

    check_name: str
    parameter: str
    expected_range: List[float]
    actual_value: float
    passed: bool
    tolerance: float
    unit: str
    message: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ValidationError:
    """Validation error details."""

    field: str
    value: Any
    message: str
    code: str


class BaseProtocol(ABC):
    """Abstract base class for all test protocols.

    All protocol implementations must inherit from this class and implement
    the abstract methods for validation, execution, and quality control.
    """

    def __init__(self, metadata: ProtocolMetadata):
        """Initialize protocol with metadata.

        Args:
            metadata: Protocol metadata
        """
        self.metadata = metadata
        self.results: Dict[str, Any] = {}
        self.qc_results: List[QualityCheckResult] = []
        self.validation_errors: List[ValidationError] = []

    @abstractmethod
    def validate_inputs(self, data: Dict[str, Any]) -> bool:
        """Validate input parameters for the protocol.

        Args:
            data: Input parameters to validate

        Returns:
            bool: True if validation passes, False otherwise

        Note:
            Validation errors should be stored in self.validation_errors
        """
        pass

    @abstractmethod
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the protocol with given parameters.

        Args:
            data: Protocol execution parameters

        Returns:
            Dict[str, Any]: Execution results

        Raises:
            ValueError: If inputs are invalid
            RuntimeError: If execution fails
        """
        pass

    @abstractmethod
    def quality_check(self, results: Dict[str, Any]) -> QCStatus:
        """Perform quality control checks on results.

        Args:
            results: Test results to check

        Returns:
            QCStatus: Overall quality control status

        Note:
            Individual check results should be stored in self.qc_results
        """
        pass

    def calculate_metrics(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate derived metrics from measurement data.

        Args:
            data: Measurement data

        Returns:
            Dict[str, float]: Calculated metrics

        Note:
            Override this method in subclasses for protocol-specific calculations
        """
        return {}

    def to_dict(self) -> Dict[str, Any]:
        """Export protocol instance as dictionary.

        Returns:
            Dict[str, Any]: Protocol representation as dictionary
        """
        return {
            "metadata": {
                "code": self.metadata.code,
                "name": self.metadata.name,
                "version": self.metadata.version,
                "description": self.metadata.description,
                "category": self.metadata.category.value,
                "standard": self.metadata.standard,
                "created_date": self.metadata.created_date.isoformat(),
                "last_modified": self.metadata.last_modified.isoformat(),
                "author": self.metadata.author,
            },
            "results": self.results,
            "qc_results": [
                {
                    "check_name": qc.check_name,
                    "parameter": qc.parameter,
                    "expected_range": qc.expected_range,
                    "actual_value": qc.actual_value,
                    "passed": qc.passed,
                    "tolerance": qc.tolerance,
                    "unit": qc.unit,
                    "message": qc.message,
                    "timestamp": qc.timestamp.isoformat(),
                }
                for qc in self.qc_results
            ],
            "validation_errors": [
                {
                    "field": err.field,
                    "value": err.value,
                    "message": err.message,
                    "code": err.code,
                }
                for err in self.validation_errors
            ],
        }

    def get_validation_summary(self) -> str:
        """Get human-readable validation summary.

        Returns:
            str: Validation summary message
        """
        if not self.validation_errors:
            return "All validations passed"

        messages = [f"Found {len(self.validation_errors)} validation error(s):"]
        for err in self.validation_errors:
            messages.append(f"  - {err.field}: {err.message}")

        return "\n".join(messages)

    def get_qc_summary(self) -> str:
        """Get human-readable QC summary.

        Returns:
            str: QC summary message
        """
        if not self.qc_results:
            return "No QC checks performed"

        passed = sum(1 for qc in self.qc_results if qc.passed)
        total = len(self.qc_results)

        messages = [f"QC Results: {passed}/{total} checks passed"]
        for qc in self.qc_results:
            status = "✓" if qc.passed else "✗"
            messages.append(f"  {status} {qc.check_name}: {qc.message}")

        return "\n".join(messages)

    def __repr__(self) -> str:
        """String representation of protocol."""
        return (
            f"{self.__class__.__name__}("
            f"code='{self.metadata.code}', "
            f"version='{self.metadata.version}')"
        )
