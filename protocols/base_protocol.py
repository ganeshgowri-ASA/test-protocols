"""
Base Protocol Class for PV Testing Framework
============================================
All protocol implementations inherit from this base class to ensure
consistency, modularity, and scalability across 50+ protocols.

Author: GenSpark PV Testing Team
Version: 1.0.0
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum
import json
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import logging
from dataclasses import dataclass, field, asdict
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProtocolStatus(Enum):
    """Protocol execution status"""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    DATA_ACQUISITION = "data_acquisition"
    ANALYSIS = "analysis"
    VALIDATION = "validation"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ValidationLevel(Enum):
    """Data validation severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Container for validation results"""
    level: ValidationLevel
    field: str
    message: str
    value: Any = None
    expected: Any = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        return {
            "level": self.level.value,
            "field": self.field,
            "message": self.message,
            "value": self.value,
            "expected": self.expected,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class ProtocolMetadata:
    """Protocol metadata and configuration"""
    protocol_id: str
    protocol_name: str
    version: str
    category: str
    standard_reference: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    author: Optional[str] = None

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data


class BaseProtocol(ABC):
    """
    Abstract base class for all PV testing protocols.

    This class provides the foundational structure and common functionality
    that all specific protocol implementations must follow.

    Key Features:
    - Modular and extensible architecture
    - Built-in data validation and QA
    - Interactive UI support with conditional logic
    - Real-time data visualization
    - Complete audit trail and traceability
    - Multi-format report generation (PDF, Excel, JSON)
    - Integration with LIMS/QMS systems
    """

    def __init__(self, metadata: ProtocolMetadata):
        """
        Initialize base protocol.

        Args:
            metadata: Protocol metadata and configuration
        """
        self.metadata = metadata
        self.execution_id = str(uuid.uuid4())
        self.status = ProtocolStatus.DRAFT
        self.validation_results: List[ValidationResult] = []
        self.test_data: Dict[str, Any] = {}
        self.analysis_results: Dict[str, Any] = {}
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

        # Load protocol template
        self.template = self._load_template()

        logger.info(f"Initialized protocol {self.metadata.protocol_id} "
                   f"with execution ID {self.execution_id}")

    @abstractmethod
    def get_protocol_id(self) -> str:
        """Return unique protocol identifier (e.g., 'STC-001')"""
        pass

    @abstractmethod
    def get_protocol_name(self) -> str:
        """Return human-readable protocol name"""
        pass

    @abstractmethod
    def get_category(self) -> str:
        """Return protocol category (performance, degradation, etc.)"""
        pass

    @abstractmethod
    def get_standard_reference(self) -> str:
        """Return applicable standard (IEC, ASTM, etc.)"""
        pass

    @abstractmethod
    def setup_test_parameters(self) -> Dict[str, Any]:
        """
        Define test setup parameters and configuration.

        Returns:
            Dictionary of setup parameters with validation rules
        """
        pass

    @abstractmethod
    def acquire_data(self, setup_params: Dict[str, Any]) -> pd.DataFrame:
        """
        Acquire test data based on setup parameters.

        Args:
            setup_params: Test setup configuration

        Returns:
            DataFrame containing raw test data
        """
        pass

    @abstractmethod
    def analyze_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze acquired data and calculate results.

        Args:
            data: Raw test data

        Returns:
            Dictionary containing analysis results
        """
        pass

    @abstractmethod
    def validate_results(self, results: Dict[str, Any]) -> List[ValidationResult]:
        """
        Validate analysis results against standards and acceptance criteria.

        Args:
            results: Analysis results to validate

        Returns:
            List of validation results
        """
        pass

    @abstractmethod
    def generate_visualizations(self, data: pd.DataFrame,
                               results: Dict[str, Any]) -> List[go.Figure]:
        """
        Generate interactive Plotly visualizations.

        Args:
            data: Test data
            results: Analysis results

        Returns:
            List of Plotly figure objects
        """
        pass

    def _load_template(self) -> Dict[str, Any]:
        """Load protocol JSON template"""
        template_path = Path("templates/protocols") / f"{self.metadata.protocol_id}.json"

        if template_path.exists():
            with open(template_path, 'r') as f:
                return json.load(f)
        else:
            logger.warning(f"Template not found: {template_path}")
            return self._get_default_template()

    def _get_default_template(self) -> Dict[str, Any]:
        """Return default template structure"""
        return {
            "protocol_id": self.metadata.protocol_id,
            "protocol_name": self.metadata.protocol_name,
            "version": self.metadata.version,
            "category": self.metadata.category,
            "sections": {
                "setup": {},
                "data_acquisition": {},
                "analysis": {},
                "validation": {},
                "report": {}
            }
        }

    def start_execution(self) -> None:
        """Start protocol execution"""
        self.status = ProtocolStatus.IN_PROGRESS
        self.started_at = datetime.now()
        logger.info(f"Started execution of {self.metadata.protocol_id}")

    def complete_execution(self) -> None:
        """Complete protocol execution"""
        self.status = ProtocolStatus.COMPLETED
        self.completed_at = datetime.now()
        duration = (self.completed_at - self.started_at).total_seconds()
        logger.info(f"Completed execution of {self.metadata.protocol_id} "
                   f"in {duration:.2f} seconds")

    def fail_execution(self, error: str) -> None:
        """Mark execution as failed"""
        self.status = ProtocolStatus.FAILED
        self.completed_at = datetime.now()
        logger.error(f"Execution failed for {self.metadata.protocol_id}: {error}")

    def add_validation_result(self, result: ValidationResult) -> None:
        """Add validation result"""
        self.validation_results.append(result)

        if result.level in [ValidationLevel.ERROR, ValidationLevel.CRITICAL]:
            logger.error(f"Validation {result.level.value}: {result.message}")
        elif result.level == ValidationLevel.WARNING:
            logger.warning(f"Validation warning: {result.message}")

    def has_critical_errors(self) -> bool:
        """Check if there are any critical validation errors"""
        return any(r.level == ValidationLevel.CRITICAL
                  for r in self.validation_results)

    def get_validation_summary(self) -> Dict[str, int]:
        """Get summary of validation results by level"""
        summary = {level.value: 0 for level in ValidationLevel}
        for result in self.validation_results:
            summary[result.level.value] += 1
        return summary

    def execute(self, setup_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute complete protocol workflow.

        Args:
            setup_params: Optional test setup parameters

        Returns:
            Complete execution results including data, analysis, and validation
        """
        try:
            self.start_execution()

            # Step 1: Setup
            if setup_params is None:
                setup_params = self.setup_test_parameters()
            self.test_data['setup'] = setup_params

            # Step 2: Data Acquisition
            self.status = ProtocolStatus.DATA_ACQUISITION
            data = self.acquire_data(setup_params)
            self.test_data['raw_data'] = data

            # Step 3: Analysis
            self.status = ProtocolStatus.ANALYSIS
            results = self.analyze_data(data)
            self.analysis_results = results

            # Step 4: Validation
            self.status = ProtocolStatus.VALIDATION
            validation_results = self.validate_results(results)
            self.validation_results = validation_results

            # Step 5: Generate Visualizations
            figures = self.generate_visualizations(data, results)

            # Complete execution
            if not self.has_critical_errors():
                self.complete_execution()
            else:
                self.fail_execution("Critical validation errors detected")

            return {
                "execution_id": self.execution_id,
                "protocol_id": self.metadata.protocol_id,
                "status": self.status.value,
                "setup": setup_params,
                "data": data.to_dict() if isinstance(data, pd.DataFrame) else data,
                "results": results,
                "validation": [r.to_dict() for r in validation_results],
                "validation_summary": self.get_validation_summary(),
                "figures": figures,
                "metadata": self.metadata.to_dict(),
                "timing": {
                    "started_at": self.started_at.isoformat() if self.started_at else None,
                    "completed_at": self.completed_at.isoformat() if self.completed_at else None,
                    "duration_seconds": (
                        (self.completed_at - self.started_at).total_seconds()
                        if self.started_at and self.completed_at else None
                    )
                }
            }

        except Exception as e:
            logger.exception(f"Error executing protocol: {e}")
            self.fail_execution(str(e))
            raise

    def generate_report(self, format: str = "pdf") -> Union[bytes, str]:
        """
        Generate test report in specified format.

        Args:
            format: Output format (pdf, excel, json, html)

        Returns:
            Report data in requested format
        """
        if format == "json":
            return self._generate_json_report()
        elif format == "excel":
            return self._generate_excel_report()
        elif format == "pdf":
            return self._generate_pdf_report()
        elif format == "html":
            return self._generate_html_report()
        else:
            raise ValueError(f"Unsupported report format: {format}")

    def _generate_json_report(self) -> str:
        """Generate JSON report"""
        report = {
            "protocol": self.metadata.to_dict(),
            "execution_id": self.execution_id,
            "status": self.status.value,
            "test_data": self.test_data,
            "results": self.analysis_results,
            "validation": [r.to_dict() for r in self.validation_results],
            "timing": {
                "created_at": self.created_at.isoformat(),
                "started_at": self.started_at.isoformat() if self.started_at else None,
                "completed_at": self.completed_at.isoformat() if self.completed_at else None
            }
        }
        return json.dumps(report, indent=2, default=str)

    def _generate_excel_report(self) -> bytes:
        """Generate Excel report"""
        # Implementation would use openpyxl or xlsxwriter
        logger.info("Generating Excel report")
        # Placeholder - actual implementation would create Excel file
        return b""

    def _generate_pdf_report(self) -> bytes:
        """Generate PDF report"""
        # Implementation would use reportlab
        logger.info("Generating PDF report")
        # Placeholder - actual implementation would create PDF file
        return b""

    def _generate_html_report(self) -> str:
        """Generate HTML report"""
        logger.info("Generating HTML report")
        # Placeholder - actual implementation would create HTML file
        return "<html><body>Report</body></html>"

    def save_to_database(self, db_connection) -> str:
        """
        Save protocol execution to database.

        Args:
            db_connection: Database connection object

        Returns:
            Database record ID
        """
        # Implementation would use SQLAlchemy
        logger.info(f"Saving {self.metadata.protocol_id} to database")
        return self.execution_id

    def get_audit_trail(self) -> List[Dict[str, Any]]:
        """
        Get complete audit trail of protocol execution.

        Returns:
            List of audit events with timestamps
        """
        trail = [
            {
                "event": "protocol_created",
                "timestamp": self.created_at.isoformat(),
                "details": {"protocol_id": self.metadata.protocol_id}
            }
        ]

        if self.started_at:
            trail.append({
                "event": "execution_started",
                "timestamp": self.started_at.isoformat(),
                "details": {"execution_id": self.execution_id}
            })

        if self.completed_at:
            trail.append({
                "event": "execution_completed",
                "timestamp": self.completed_at.isoformat(),
                "details": {
                    "status": self.status.value,
                    "validation_summary": self.get_validation_summary()
                }
            })

        return trail

    def to_dict(self) -> Dict[str, Any]:
        """Convert protocol instance to dictionary"""
        return {
            "execution_id": self.execution_id,
            "metadata": self.metadata.to_dict(),
            "status": self.status.value,
            "validation_results": [r.to_dict() for r in self.validation_results],
            "test_data": self.test_data,
            "analysis_results": self.analysis_results,
            "audit_trail": self.get_audit_trail()
        }


class ProtocolFactory:
    """Factory class for creating protocol instances"""

    _protocols: Dict[str, type] = {}

    @classmethod
    def register(cls, protocol_id: str, protocol_class: type) -> None:
        """Register a protocol class"""
        cls._protocols[protocol_id] = protocol_class
        logger.info(f"Registered protocol: {protocol_id}")

    @classmethod
    def create(cls, protocol_id: str, **kwargs) -> BaseProtocol:
        """Create protocol instance by ID"""
        if protocol_id not in cls._protocols:
            raise ValueError(f"Unknown protocol ID: {protocol_id}")

        protocol_class = cls._protocols[protocol_id]
        return protocol_class(**kwargs)

    @classmethod
    def list_protocols(cls) -> List[str]:
        """List all registered protocols"""
        return list(cls._protocols.keys())
