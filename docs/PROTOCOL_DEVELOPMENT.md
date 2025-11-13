# Protocol Development Guide

## Creating New Testing Protocols

This guide explains how to create new testing protocols for the PV Testing Protocol Framework.

## Protocol Structure

Each protocol consists of four main components:

1. **JSON Schema** - Defines protocol metadata, parameters, and validation rules
2. **Implementation** - Python code for protocol logic and execution
3. **Template** - Default parameter values
4. **Tests** - Unit and integration tests

## Step-by-Step Guide

### 1. Create Protocol Directory

```bash
mkdir -p protocols/pid-XXX/tests
cd protocols/pid-XXX
```

### 2. Define JSON Schema

Create `schema.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "metadata": {
    "pid": "pid-XXX",
    "name": "Your Protocol Name",
    "version": "1.0.0",
    "standard": "IEC XXXXX",
    "description": "Protocol description",
    "created_date": "2025-11-13",
    "status": "active",
    "author": "Your Name",
    "tags": ["tag1", "tag2"]
  },
  "test_parameters": {
    "type": "object",
    "properties": {
      "test_name": {
        "type": "string",
        "description": "Test identifier",
        "minLength": 1
      },
      "your_parameter": {
        "type": "number",
        "description": "Parameter description",
        "minimum": 0,
        "maximum": 100,
        "default": 50
      }
    },
    "required": ["test_name"]
  },
  "measurements": {
    "type": "object",
    "properties": {
      "timestamp": {"type": "string", "format": "date-time"},
      "your_measurement": {"type": "number"}
    },
    "required": ["timestamp"]
  },
  "validation_rules": {
    "your_check": {
      "warning_threshold": 10,
      "critical_threshold": 20,
      "unit": "unit"
    }
  },
  "results": {
    "type": "object",
    "properties": {
      "test_id": {"type": "string"},
      "status": {"type": "string"},
      "measurements": {"type": "array"},
      "summary": {"type": "object"}
    },
    "required": ["test_id", "status"]
  }
}
```

### 3. Create Implementation

Create `implementation.py`:

```python
"""PID-XXX Protocol Implementation."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import uuid

from src.models.protocol import (
    TestExecution,
    Measurement,
    QCCheck,
    TestExecutionStatus,
    QCStatus,
)


class PIDXXXProtocol:
    """PID-XXX Protocol Implementation."""

    def __init__(self, schema_path: Optional[Path] = None):
        """Initialize protocol."""
        if schema_path is None:
            schema_path = Path(__file__).parent / "schema.json"

        with open(schema_path) as f:
            self.schema = json.load(f)

        self.metadata = self.schema["metadata"]
        self.validation_rules = self.schema["validation_rules"]

    def validate_parameters(
        self, parameters: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate test parameters.

        Args:
            parameters: Test parameters

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        required = self.schema["test_parameters"]["required"]

        # Check required fields
        for field in required:
            if field not in parameters:
                errors.append(f"Missing required field: {field}")

        # Add custom validation logic here

        return len(errors) == 0, errors

    def create_test_execution(
        self, protocol_id: str, parameters: Dict[str, Any]
    ) -> TestExecution:
        """
        Create test execution.

        Args:
            protocol_id: Protocol database ID
            parameters: Test parameters

        Returns:
            TestExecution instance
        """
        return TestExecution(
            id=str(uuid.uuid4()),
            protocol_id=protocol_id,
            test_name=parameters.get("test_name"),
            input_parameters=parameters,
            status=TestExecutionStatus.PENDING,
        )

    def process_measurement(
        self,
        test_execution: TestExecution,
        measurement_data: Dict[str, Any]
    ) -> Measurement:
        """
        Process a measurement.

        Args:
            test_execution: Test execution instance
            measurement_data: Measurement data

        Returns:
            Measurement instance
        """
        return Measurement(
            test_execution_id=test_execution.id,
            timestamp=measurement_data["timestamp"],
            elapsed_time=measurement_data.get("elapsed_time", 0),
            # Add your measurement fields
        )

    def perform_qc_checks(
        self,
        measurements: List[Measurement],
        parameters: Dict[str, Any]
    ) -> Tuple[QCStatus, List[QCCheck]]:
        """
        Perform quality control checks.

        Args:
            measurements: List of measurements
            parameters: Test parameters

        Returns:
            Tuple of (overall_status, qc_checks)
        """
        qc_checks = []

        # Implement your QC checks here

        # Example check
        # values = [m.your_field for m in measurements]
        # avg_value = sum(values) / len(values)

        # if avg_value > critical_threshold:
        #     status = QCStatus.FAIL
        # elif avg_value > warning_threshold:
        #     status = QCStatus.WARNING
        # else:
        #     status = QCStatus.PASS

        # qc_checks.append(QCCheck(...))

        # Determine overall status
        overall_status = QCStatus.PASS
        for check in qc_checks:
            if check.status == QCStatus.FAIL:
                overall_status = QCStatus.FAIL
                break
            elif check.status == QCStatus.WARNING:
                overall_status = QCStatus.WARNING

        return overall_status, qc_checks

    def generate_results_summary(
        self,
        measurements: List[Measurement],
        qc_checks: List[QCCheck],
        qc_status: QCStatus
    ) -> Dict[str, Any]:
        """
        Generate results summary.

        Args:
            measurements: List of measurements
            qc_checks: List of QC checks
            qc_status: Overall QC status

        Returns:
            Results summary dictionary
        """
        summary = {
            "total_measurements": len(measurements),
            "qc_status": qc_status.value,
            "qc_details": [
                {
                    "check": check.check_name,
                    "status": check.status.value,
                    "message": check.message,
                }
                for check in qc_checks
            ],
        }

        return summary
```

### 4. Create Template

Create `template.json`:

```json
{
  "test_name": "PID-XXX-TEST-001",
  "your_parameter": 50
}
```

### 5. Create Tests

Create `tests/test_schema.py`:

```python
"""Tests for PID-XXX schema."""

import pytest
from pathlib import Path


def test_schema_exists():
    """Test that schema file exists."""
    schema_path = Path(__file__).parent.parent / "schema.json"
    assert schema_path.exists()


def test_schema_metadata():
    """Test schema metadata."""
    import json
    schema_path = Path(__file__).parent.parent / "schema.json"
    with open(schema_path) as f:
        schema = json.load(f)

    assert schema["metadata"]["pid"] == "pid-XXX"
    assert "name" in schema["metadata"]
    assert "version" in schema["metadata"]
```

Create `tests/test_implementation.py`:

```python
"""Tests for PID-XXX implementation."""

import pytest
from protocols.pid_XXX.implementation import PIDXXXProtocol


class TestPIDXXXProtocol:
    """Test protocol implementation."""

    def test_initialization(self):
        """Test protocol initialization."""
        protocol = PIDXXXProtocol()
        assert protocol.metadata["pid"] == "pid-XXX"

    def test_validate_parameters(self):
        """Test parameter validation."""
        protocol = PIDXXXProtocol()
        params = {"test_name": "TEST-001"}
        is_valid, errors = protocol.validate_parameters(params)
        assert is_valid is True
```

### 6. Register Protocol

Add protocol to database:

```python
# In scripts/init_db.py

protocol_path = Path(__file__).parent.parent / "protocols" / "pid-XXX" / "schema.json"

with open(protocol_path) as f:
    schema = json.load(f)

protocol = Protocol(
    pid="pid-XXX",
    name=schema["metadata"]["name"],
    version=schema["metadata"]["version"],
    schema=schema,
    status=ProtocolStatus.ACTIVE
)
session.add(protocol)
session.commit()
```

## Best Practices

### Schema Design

1. **Use descriptive names**: Clear parameter and field names
2. **Include descriptions**: Help text for all parameters
3. **Set reasonable limits**: Min/max values for numeric parameters
4. **Define required fields**: Clearly mark mandatory parameters
5. **Include units**: Specify units for all measurements

### Implementation

1. **Type hints**: Use Python type hints throughout
2. **Documentation**: Docstrings for all methods
3. **Error handling**: Validate inputs and handle errors gracefully
4. **Modularity**: Break complex logic into smaller methods
5. **Testability**: Design for easy testing

### Testing

1. **Test coverage**: Aim for >80% code coverage
2. **Edge cases**: Test boundary conditions
3. **Integration tests**: Test database interactions
4. **Mock data**: Use realistic test data

### Validation Rules

1. **Reasonable thresholds**: Based on standards and experience
2. **Warning levels**: Provide early warning before failure
3. **Clear messages**: Helpful QC check messages
4. **Configurable**: Allow threshold customization

## Example: Implementing a Custom Check

```python
def perform_voltage_stability_check(
    self,
    measurements: List[Measurement]
) -> QCCheck:
    """Check voltage stability throughout test."""
    voltages = [m.voltage for m in measurements]
    voltage_range = max(voltages) - min(voltages)

    # Threshold: voltage should not vary more than 5V
    threshold = 5.0

    if voltage_range > threshold:
        status = QCStatus.FAIL
        message = f"Voltage instability detected: {voltage_range:.2f}V variation"
    else:
        status = QCStatus.PASS
        message = f"Voltage stable: {voltage_range:.2f}V variation"

    return QCCheck(
        check_name="Voltage Stability",
        check_type="voltage_stability",
        status=status,
        measured_value=voltage_range,
        threshold_value=threshold,
        message=message,
        passed=1 if status == QCStatus.PASS else 0
    )
```

## Testing Your Protocol

```bash
# Run protocol tests
pytest protocols/pid-XXX/tests/ -v

# Run with coverage
pytest protocols/pid-XXX/tests/ --cov=protocols.pid_XXX

# Test in Streamlit
streamlit run src/ui/streamlit_app.py
```

## Next Steps

1. Review existing protocols for examples
2. Follow IEC or industry standards
3. Collaborate with domain experts
4. Iterate based on feedback
5. Document thoroughly

For questions or assistance, please open an issue on GitHub.
