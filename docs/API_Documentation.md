# Test Protocols Framework - API Documentation

## Overview

This document provides API documentation for the Test Protocols Framework, covering the core classes, protocol implementations, and database models.

## Core Classes

### ProtocolBase

Base class for all test protocols.

```python
from protocols.core.protocol_base import ProtocolBase

class ProtocolBase(ABC):
    """Abstract base class for all test protocols"""

    def __init__(self, protocol_definition: Dict[str, Any])
    def generate_execution_id(self) -> str
    def start_test(self, sample_info: Dict[str, Any], test_conditions: Dict[str, Any]) -> str
    def add_measurement(self, measurement: Dict[str, Any]) -> None
    def calculate_results(self) -> Dict[str, Any]  # Abstract
    def evaluate_pass_fail(self) -> Dict[str, Any]  # Abstract
    def complete_test(self) -> Dict[str, Any]
    def get_full_results(self) -> Dict[str, Any]
    def export_to_json(self, file_path: str) -> None
```

**Example Usage:**

```python
# Load protocol definition
protocol_def = load_protocol_definition("protocols/templates/backsheet_chalking/protocol.json")

# Create protocol instance
protocol = BacksheetChalkingProtocol(protocol_def)

# Start test
sample_info = {
    "sample_id": "MOD-001",
    "module_type": "Monocrystalline 400W",
    "backsheet_material": "PET"
}

test_conditions = {
    "temperature": 25.0,
    "humidity": 50.0,
    "operator_id": "OP-001",
    "measurement_locations": 9
}

execution_id = protocol.start_test(sample_info, test_conditions)

# Add measurements
for i in range(9):
    measurement = {
        "location_id": f"LOC-{i+1:02d}",
        "chalking_rating": 2.5,
        "location_x": float(i * 100),
        "location_y": 100.0
    }
    protocol.add_measurement(measurement)

# Complete test and get results
results = protocol.complete_test()

# Export to JSON
protocol.export_to_json("results.json")
```

### ProtocolValidator

Validates protocol definitions and test data against JSON schemas.

```python
from protocols.core.protocol_validator import ProtocolValidator

class ProtocolValidator:
    """Validates protocol definitions and test data"""

    def __init__(self, schema_path: str = None)
    def load_schema(self, schema_path: str) -> None
    def validate_data(self, data: Dict[str, Any], schema: Dict[str, Any] = None) -> Tuple[bool, List[str]]
    def validate_protocol_definition(self, protocol_def: Dict[str, Any]) -> Tuple[bool, List[str]]
    def validate_test_results(self, results: Dict[str, Any], protocol_id: str) -> Tuple[bool, List[str]]
```

**Example Usage:**

```python
# Validate protocol definition
validator = ProtocolValidator()
is_valid, errors = validator.validate_protocol_definition(protocol_def)

if not is_valid:
    print("Validation errors:", errors)

# Validate test results against schema
validator.load_schema("protocols/templates/backsheet_chalking/schema.json")
is_valid, errors = validator.validate_data(test_results)
```

### ProtocolRegistry

Registry for managing and discovering test protocols.

```python
from protocols.core.protocol_registry import ProtocolRegistry, registry

class ProtocolRegistry:
    """Registry for managing test protocols (Singleton)"""

    def register(self, protocol_id: str, protocol_class: Type[ProtocolBase],
                 definition: Dict[str, Any] = None) -> None
    def get_protocol_class(self, protocol_id: str) -> Optional[Type[ProtocolBase]]
    def get_protocol_definition(self, protocol_id: str) -> Optional[Dict[str, Any]]
    def create_protocol(self, protocol_id: str) -> Optional[ProtocolBase]
    def list_protocols(self) -> List[str]
    def get_protocols_by_category(self, category: str) -> List[str]
    def load_protocols_from_directory(self, templates_dir: str) -> None
```

**Example Usage:**

```python
# Register a protocol
from protocols.implementations.backsheet_chalking import BacksheetChalkingProtocol

registry.register("CHALK-001", BacksheetChalkingProtocol, protocol_def)

# Create protocol instance from registry
protocol = registry.create_protocol("CHALK-001")

# List all protocols
all_protocols = registry.list_protocols()

# Get protocols by category
degradation_protocols = registry.get_protocols_by_category("Degradation")

# Load all protocols from directory
registry.load_protocols_from_directory("protocols/templates")
```

## Protocol Implementations

### BacksheetChalkingProtocol

Implementation of CHALK-001 Backsheet Chalking Protocol.

```python
from protocols.implementations.backsheet_chalking import BacksheetChalkingProtocol

class BacksheetChalkingProtocol(ProtocolBase):
    """CHALK-001 implementation"""

    def calculate_results(self) -> Dict[str, Any]
    def evaluate_pass_fail(self) -> Dict[str, Any]
    def generate_spatial_analysis(self) -> Dict[str, Any]
    def get_recommendations(self) -> List[str]
```

**Calculated Metrics:**

- `average_chalking_rating`: Mean chalking rating
- `chalking_std_dev`: Standard deviation
- `max_chalking_rating`: Maximum rating observed
- `min_chalking_rating`: Minimum rating observed
- `coefficient_of_variation`: CV in percent
- `chalking_uniformity_index`: Uniformity measure (0-100%)

**Example:**

```python
protocol = BacksheetChalkingProtocol(protocol_def)
protocol.start_test(sample_info, test_conditions)

# Add measurements...

# Calculate results
calc_results = protocol.calculate_results()
print(f"Average: {calc_results['average_chalking_rating']:.2f}")

# Get spatial analysis
spatial = protocol.generate_spatial_analysis()
if spatial['has_spatial_data']:
    print(f"Hotspots: {spatial['hotspot_count']}")

# Get recommendations
recommendations = protocol.get_recommendations()
for rec in recommendations:
    print(f"- {rec}")
```

## Database Models

### Protocol Model

```python
from database.models.protocol_model import Protocol

class Protocol(Base):
    """Protocol definition database model"""

    protocol_id: str (PK)
    name: str
    version: str
    category: str
    description: str
    definition_json: JSON
    metadata_json: JSON
    status: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

### TestExecution Model

```python
from database.models.test_execution_model import TestExecution

class TestExecution(Base):
    """Test execution database model"""

    id: int (PK)
    test_execution_id: str (Unique)
    protocol_id: str (FK)
    protocol_version: str
    sample_id: str
    sample_info_json: JSON
    test_conditions_json: JSON
    started_at: datetime
    completed_at: datetime
    operator_id: str
    status: str
```

### Measurement Model

```python
from database.models.test_results_model import Measurement

class Measurement(Base):
    """Individual measurement database model"""

    id: int (PK)
    test_execution_id: str (FK)
    location_id: str
    measurement_data_json: JSON
    chalking_rating: float
    location_x: float
    location_y: float
    measurement_timestamp: datetime
```

### TestResult Model

```python
from database.models.test_results_model import TestResult

class TestResult(Base):
    """Test results database model"""

    id: int (PK)
    test_execution_id: str (FK, Unique)
    calculated_results_json: JSON
    pass_fail_assessment_json: JSON
    overall_result: str
    average_chalking_rating: float
    calculated_at: datetime
```

### QCReview Model

```python
from database.models.qc_model import QCReview

class QCReview(Base):
    """QC review database model"""

    id: int (PK)
    test_execution_id: str (FK)
    reviewer_id: str
    review_date: datetime
    calibration_verified: bool
    qc_decision: str
    qc_notes: str
```

## JSON Schema Specification

### Protocol Definition Schema

```json
{
  "protocol_id": "string",
  "name": "string",
  "version": "semver string",
  "category": "string",
  "description": "string",
  "test_parameters": {
    "category_name": {
      "param_name": {
        "type": "number|string|integer",
        "unit": "string",
        "range": {"min": number, "max": number},
        "required": boolean
      }
    }
  },
  "test_steps": [...],
  "data_collection": {
    "measurements": [...],
    "calculated_metrics": [...]
  },
  "pass_fail_criteria": {
    "acceptance_thresholds": {...}
  }
}
```

### Test Results Schema

See `protocols/templates/backsheet_chalking/schema.json` for the complete JSON Schema definition.

## Error Handling

### Common Exceptions

```python
# Protocol not found
protocol = registry.create_protocol("INVALID-ID")
# Returns: None

# Validation errors
is_valid, errors = validator.validate_data(invalid_data)
# Returns: (False, ["error message 1", "error message 2"])

# Missing required parameters
protocol.validate_parameter("invalid.path", value)
# Returns: False
```

### Best Practices

1. Always validate protocol definitions before use
2. Check return values from registry methods
3. Handle validation errors gracefully
4. Log all protocol executions for audit trail
5. Use try-except blocks for file operations

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_backsheet_chalking.py

# Run with coverage
pytest --cov=protocols --cov=database tests/
```

### Test Fixtures

Common fixtures available in `tests/conftest.py`:

- `protocol_definition`: CHALK-001 protocol definition
- `chalking_protocol`: BacksheetChalkingProtocol instance
- `sample_info`: Sample information dict
- `test_conditions`: Test conditions dict
- `sample_measurements`: Sample measurement data
- `passing_measurements`: Measurements that pass criteria
- `failing_measurements`: Measurements that fail criteria

## Changelog

### Version 1.0.0 (2025-11-14)
- Initial release
- CHALK-001 protocol implementation
- Core framework classes
- Database models
- Streamlit UI
- Comprehensive test suite
