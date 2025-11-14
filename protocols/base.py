"""Base Protocol Class

Provides foundation for all test protocols with common functionality.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import json

from pydantic import BaseModel, Field


class ProtocolMetadata(BaseModel):
    """Protocol metadata model"""
    protocol_id: str
    name: str
    version: str
    standard: str
    category: str
    description: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class MeasurementPoint(BaseModel):
    """Single measurement data point"""
    timestamp: datetime
    parameter: str
    value: float
    unit: str
    notes: Optional[str] = None


class TestResult(BaseModel):
    """Test result container"""
    test_id: str
    protocol_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str  # running, completed, failed, aborted
    measurements: List[MeasurementPoint] = []
    pass_fail: Optional[bool] = None
    notes: Optional[str] = None


class BaseProtocol(ABC):
    """Base class for all test protocols"""

    def __init__(self, template_path: Path):
        """Initialize protocol from JSON template

        Args:
            template_path: Path to JSON template file
        """
        self.template_path = template_path
        self.template = self._load_template()
        self.metadata = self._parse_metadata()
        self.current_test: Optional[TestResult] = None

    def _load_template(self) -> Dict[str, Any]:
        """Load protocol template from JSON file"""
        with open(self.template_path, 'r') as f:
            return json.load(f)

    def _parse_metadata(self) -> ProtocolMetadata:
        """Parse metadata from template"""
        return ProtocolMetadata(**self.template['metadata'])

    @abstractmethod
    def validate_equipment(self) -> bool:
        """Validate required equipment is available and calibrated"""
        pass

    @abstractmethod
    def validate_sample(self, sample_data: Dict[str, Any]) -> bool:
        """Validate sample meets protocol requirements"""
        pass

    @abstractmethod
    def run_test(self, sample_id: str, **kwargs) -> TestResult:
        """Execute the test protocol"""
        pass

    @abstractmethod
    def analyze_results(self, test_result: TestResult) -> Dict[str, Any]:
        """Analyze test results and determine pass/fail"""
        pass

    def generate_report(self, test_result: TestResult, output_path: Path) -> Path:
        """Generate test report

        Args:
            test_result: Test result to report on
            output_path: Path for output report

        Returns:
            Path to generated report
        """
        # Base implementation - can be overridden
        report_data = {
            'metadata': self.metadata.model_dump(),
            'test_result': test_result.model_dump(),
            'analysis': self.analyze_results(test_result)
        }

        report_file = output_path / f"{test_result.test_id}_report.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)

        return report_file

    def get_parameter(self, key: str, default: Any = None) -> Any:
        """Get parameter from template"""
        return self.template.get('parameters', {}).get(key, default)

    def get_test_steps(self) -> List[Dict[str, Any]]:
        """Get test steps from template"""
        return self.template.get('test_steps', [])

    def get_qc_criteria(self) -> Dict[str, Any]:
        """Get QC criteria from template"""
        return self.template.get('qc_criteria', {})
