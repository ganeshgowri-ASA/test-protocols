"""
Protocol Model

Data model for test protocol definitions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum

from .base import BaseModel


class ProtocolStatus(str, Enum):
    """Protocol status enumeration."""
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    ARCHIVED = "ARCHIVED"


class ProtocolCategory(str, Enum):
    """Protocol category enumeration."""
    EVA_DEGRADATION = "EVA_DEGRADATION"
    MECHANICAL_STRESS = "MECHANICAL_STRESS"
    THERMAL_CYCLING = "THERMAL_CYCLING"
    HUMIDITY_FREEZE = "HUMIDITY_FREEZE"
    UV_EXPOSURE = "UV_EXPOSURE"
    ELECTRICAL = "ELECTRICAL"
    OTHER = "OTHER"


@dataclass
class Protocol(BaseModel):
    """
    Protocol data model.

    Represents a test protocol definition with all metadata and parameters.
    """

    protocol_id: str
    protocol_name: str
    version: str
    description: str
    category: str
    test_parameters: Dict[str, Any]
    measurements: List[Dict[str, Any]]
    quality_controls: List[Dict[str, Any]] = field(default_factory=list)
    pass_fail_criteria: List[Dict[str, Any]] = field(default_factory=list)
    status: str = ProtocolStatus.ACTIVE.value
    author: Optional[str] = None
    approved_by: Optional[str] = None
    approval_date: Optional[datetime] = None
    review_date: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    standards_reference: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_duration_hours(self) -> Optional[int]:
        """Get test duration in hours."""
        return self.test_parameters.get('duration_hours')

    def get_measurement_parameters(self) -> List[str]:
        """Get list of measurement parameter names."""
        return [m.get('name') for m in self.measurements if 'name' in m]

    def get_qc_types(self) -> List[str]:
        """Get list of QC check types."""
        return [qc.get('type') for qc in self.quality_controls if 'type' in qc]

    def is_active(self) -> bool:
        """Check if protocol is active."""
        return self.status == ProtocolStatus.ACTIVE.value

    def requires_review(self) -> bool:
        """Check if protocol requires review."""
        if not self.review_date:
            return False
        return datetime.now() >= self.review_date
