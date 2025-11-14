"""Base Protocol Class

Provides foundation for all test protocols with common functionality.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import csv
import qrcode
from io import BytesIO
import base64

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

    def __init__(self, protocol_json_path: str):
        """Initialize protocol from JSON template

        Args:
            protocol_json_path: Path to protocol JSON definition file
        """
        self.protocol_path = Path(protocol_json_path)
        with open(protocol_json_path, 'r') as f:
            self.config = json.load(f)

        self.metadata = ProtocolMetadata(**self.config['metadata'])
        self.parameters = self.config['parameters']
        self.equipment = self.config['equipment']
        self.test_procedure = self.config['test_procedure']
        self.pass_fail_criteria = self.config['pass_fail_criteria']

        self.current_test: Optional[TestResult] = None
        self.measurements: List[MeasurementPoint] = []

    @abstractmethod
    def execute(self, **kwargs) -> TestResult:
        """Execute the protocol

        Returns:
            TestResult object containing test results
        """
        pass

    @abstractmethod
    def validate_inputs(self, **kwargs) -> bool:
        """Validate input parameters

        Returns:
            True if inputs are valid, False otherwise
        """
        pass

    def start_test(self, test_id: str) -> TestResult:
        """Start a new test run

        Args:
            test_id: Unique identifier for this test run

        Returns:
            TestResult object initialized for this run
        """
        self.current_test = TestResult(
            test_id=test_id,
            protocol_id=self.metadata.protocol_id,
            start_time=datetime.now(),
            status="running"
        )
        self.measurements = []
        return self.current_test

    def record_measurement(
        self,
        parameter: str,
        value: float,
        unit: str,
        notes: Optional[str] = None
    ) -> MeasurementPoint:
        """Record a measurement point

        Args:
            parameter: Name of measured parameter
            value: Measured value
            unit: Unit of measurement
            notes: Optional notes about measurement

        Returns:
            MeasurementPoint object
        """
        measurement = MeasurementPoint(
            timestamp=datetime.now(),
            parameter=parameter,
            value=value,
            unit=unit,
            notes=notes
        )
        self.measurements.append(measurement)
        if self.current_test:
            self.current_test.measurements.append(measurement)
        return measurement

    def complete_test(
        self,
        pass_fail: bool,
        notes: Optional[str] = None
    ) -> TestResult:
        """Complete the current test

        Args:
            pass_fail: Test result (True=pass, False=fail)
            notes: Optional notes about test completion

        Returns:
            Completed TestResult object
        """
        if not self.current_test:
            raise ValueError("No active test to complete")

        self.current_test.end_time = datetime.now()
        self.current_test.status = "completed"
        self.current_test.pass_fail = pass_fail
        if notes:
            self.current_test.notes = notes

        return self.current_test

    def abort_test(self, reason: str) -> TestResult:
        """Abort the current test

        Args:
            reason: Reason for aborting test

        Returns:
            Aborted TestResult object
        """
        if not self.current_test:
            raise ValueError("No active test to abort")

        self.current_test.end_time = datetime.now()
        self.current_test.status = "aborted"
        self.current_test.notes = f"Aborted: {reason}"

        return self.current_test

    def export_to_json(self, filepath: str) -> str:
        """Export test results to JSON

        Args:
            filepath: Path to save JSON file

        Returns:
            Path to saved file
        """
        if not self.current_test:
            raise ValueError("No test results to export")

        data = {
            'protocol': self.metadata.dict(),
            'test_result': self.current_test.dict(),
            'measurements': [m.dict() for m in self.measurements]
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        return filepath

    def export_to_csv(self, filepath: str) -> str:
        """Export measurements to CSV

        Args:
            filepath: Path to save CSV file

        Returns:
            Path to saved file
        """
        if not self.measurements:
            raise ValueError("No measurements to export")

        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Parameter', 'Value', 'Unit', 'Notes'])
            for m in self.measurements:
                writer.writerow([
                    m.timestamp.isoformat(),
                    m.parameter,
                    m.value,
                    m.unit,
                    m.notes or ''
                ])

        return filepath

    def generate_qr_code(self, data: str) -> str:
        """Generate QR code for test traceability

        Args:
            data: Data to encode in QR code

        Returns:
            Base64 encoded QR code image
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        return base64.b64encode(buffer.getvalue()).decode()

    def get_parameter_value(self, parameter_name: str) -> Any:
        """Get parameter value from protocol configuration

        Args:
            parameter_name: Name of parameter

        Returns:
            Parameter value
        """
        if parameter_name not in self.parameters:
            raise KeyError(f"Parameter '{parameter_name}' not found in protocol")

        param = self.parameters[parameter_name]
        if isinstance(param, dict) and 'value' in param:
            return param['value']
        return param

    def check_pass_fail(self, results: Dict[str, float]) -> tuple[bool, List[str]]:
        """Check if test results meet pass/fail criteria

        Args:
            results: Dictionary of parameter names to measured values

        Returns:
            Tuple of (pass_status, list_of_failures)
        """
        failures = []

        for criterion_name, criterion in self.pass_fail_criteria.items():
            if not criterion.get('critical', True):
                continue

            parameter = criterion['parameter']
            if parameter not in results:
                failures.append(f"Missing required measurement: {parameter}")
                continue

            # This is a simplified check - real implementation would need
            # more sophisticated comparison logic
            condition = criterion['condition']
            value = results[parameter]

            # Example: check if value meets condition
            # Real implementation would parse condition string
            if 'calculation' in criterion:
                # Handle calculated values
                pass

        return len(failures) == 0, failures
