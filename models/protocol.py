"""
Data models for Test Protocols
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class ProtocolStatus(Enum):
    """Protocol execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"


class ProtocolType(Enum):
    """Types of protocols"""
    ELECTRICAL = "Electrical Testing"
    MECHANICAL = "Mechanical Testing"
    ENVIRONMENTAL = "Environmental Testing"
    PERFORMANCE = "Performance Testing"
    SAFETY = "Safety & Compliance"
    QC = "Quality Control"
    CALIBRATION = "Calibration"
    MATERIAL = "Material Analysis"


class QCResult(Enum):
    """Quality Control results"""
    PASS = "pass"
    FAIL = "fail"
    CONDITIONAL = "conditional"
    PENDING = "pending"


@dataclass
class ServiceRequest:
    """Service request model"""
    request_id: str
    customer_name: str
    sample_id: str
    request_date: datetime
    required_protocols: List[str]
    priority: str = "normal"  # low, normal, high, urgent
    status: str = "active"
    assigned_to: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Protocol:
    """Protocol execution model"""
    protocol_id: str
    protocol_name: str
    protocol_type: ProtocolType
    service_request_id: str
    sample_id: str
    status: ProtocolStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    operator: Optional[str] = None
    equipment_id: Optional[str] = None
    qc_result: QCResult = QCResult.PENDING
    nc_number: Optional[str] = None  # Non-conformance number
    test_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration_hours(self) -> Optional[float]:
        """Calculate protocol duration in hours"""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return delta.total_seconds() / 3600
        return None

    @property
    def is_overdue(self) -> bool:
        """Check if protocol is overdue"""
        if self.start_time and not self.end_time:
            delta = datetime.now() - self.start_time
            return delta.total_seconds() / 3600 > 48  # 48 hour threshold
        return False


@dataclass
class Inspection:
    """Inspection record model"""
    inspection_id: str
    service_request_id: str
    sample_id: str
    inspection_date: datetime
    inspector: str
    protocols_triggered: List[str]
    findings: str
    status: str = "completed"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Equipment:
    """Equipment model"""
    equipment_id: str
    equipment_name: str
    equipment_type: str
    status: str = "available"  # available, in_use, maintenance, offline
    last_calibration: Optional[datetime] = None
    next_calibration: Optional[datetime] = None
    utilization_rate: float = 0.0
    total_hours: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def calibration_due_soon(self) -> bool:
        """Check if calibration is due within 30 days"""
        if self.next_calibration:
            days_until = (self.next_calibration - datetime.now()).days
            return 0 < days_until <= 30
        return False


@dataclass
class QCRecord:
    """Quality Control record"""
    qc_id: str
    protocol_id: str
    sample_id: str
    qc_date: datetime
    qc_result: QCResult
    qc_officer: str
    nc_number: Optional[str] = None
    corrective_action: Optional[str] = None
    notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Report:
    """Test report model"""
    report_id: str
    protocol_id: str
    service_request_id: str
    sample_id: str
    report_type: str
    generated_date: datetime
    generated_by: str
    status: str = "draft"  # draft, approved, issued
    file_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KPIMetrics:
    """KPI metrics model"""
    date: datetime
    total_samples: int = 0
    completed_protocols: int = 0
    pending_protocols: int = 0
    failed_protocols: int = 0
    average_tat: float = 0.0
    pass_rate: float = 0.0
    first_time_pass_rate: float = 0.0
    equipment_utilization: float = 0.0
    throughput_daily: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Notification:
    """Notification model"""
    notification_id: str
    notification_type: str  # alert, warning, info, success
    title: str
    message: str
    created_at: datetime
    priority: str = "normal"  # low, normal, high, critical
    read: bool = False
    action_url: Optional[str] = None
    related_entity_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
