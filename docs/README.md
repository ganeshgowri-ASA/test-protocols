# PV Testing Protocol Framework - Documentation

## Overview

This directory contains comprehensive documentation for the PV Testing Protocol Framework, including detailed protocol specifications, user guides, and technical references.

## Documentation Structure

### Protocol Documentation

Each test protocol has detailed documentation including:
- Protocol overview and objectives
- Test specimen requirements
- Environmental conditions
- Detailed test procedures
- Acceptance criteria
- Data collection requirements
- Equipment specifications
- Safety requirements

### Available Protocol Documents

- **[TWIST-001: Module Twist Test](TWIST-001_Module_Twist_Test.md)** - Mechanical twist test for PV modules per IEC 61215-2

## Quick Links

### User Guides

1. **Getting Started**
   - [Installation Guide](#installation)
   - [Quick Start Tutorial](#quick-start)
   - [Basic Concepts](#basic-concepts)

2. **Using the Framework**
   - [Loading Protocols](#loading-protocols)
   - [Running Tests](#running-tests)
   - [Viewing Results](#viewing-results)
   - [Generating Reports](#generating-reports)

3. **Creating Custom Protocols**
   - [Protocol JSON Format](#protocol-format)
   - [Schema Validation](#schema-validation)
   - [Best Practices](#best-practices)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Installation Steps

```bash
# Clone the repository
git clone <repository-url>
cd test-protocols

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from src.models.base import get_engine, init_db; engine = get_engine(); init_db(engine)"

# Load protocols
python -c "from src.parsers import ProtocolLoader; from pathlib import Path; loader = ProtocolLoader(); loader.load_protocol_directory(Path('protocols'))"
```

## Quick Start

### Running the Streamlit UI

```bash
streamlit run src/ui/app.py
```

The application will open in your default web browser at `http://localhost:8501`.

### Using the Python API

```python
from src.models.base import get_engine, init_db, get_session
from src.parsers import ProtocolLoader, ProtocolExecutor

# Initialize database
engine = get_engine()
init_db(engine)
session = get_session(engine)

# Load a protocol
loader = ProtocolLoader()
protocol = loader.get_protocol_by_id("TWIST-001", session)

# Create a test run
executor = ProtocolExecutor(session)
test_run = executor.create_test_run(
    protocol=protocol,
    specimen_id="MODULE-001",
    operator_name="John Doe"
)

# Start the test
executor.start_test_run(test_run)

# Record measurements
executor.record_measurement(
    test_run=test_run,
    measurement_id="M-001",
    parameter="Maximum Power",
    value=350.5,
    unit="W"
)

# Complete the test
executor.complete_test_run(test_run, TestResult.PASS)
```

## Basic Concepts

### Protocols

Protocols are JSON-based definitions that describe:
- Test parameters and conditions
- Sequential test steps
- Acceptance criteria
- Required measurements
- Equipment specifications

### Test Runs

A test run is an execution instance of a protocol on a specific specimen. It includes:
- Specimen information
- Test operator and facility details
- Step-by-step progress tracking
- Measurement data collection
- Final results and evaluation

### Measurements

Measurements are data points collected during testing:
- Numeric values (power, voltage, current, etc.)
- Boolean values (pass/fail flags)
- Text observations
- Complex data (arrays, time series)

## Loading Protocols

### From JSON File

```python
from pathlib import Path
from src.parsers import ProtocolLoader

loader = ProtocolLoader()
protocol_data = loader.load_and_validate(Path("protocols/mechanical/TWIST-001.json"))
```

### Importing to Database

```python
from src.models.base import get_session

session = get_session(engine)
protocol = loader.import_to_database(protocol_data, session)
session.close()
```

### Bulk Import

```python
protocols = loader.load_protocol_directory(Path("protocols"))
```

## Running Tests

### Via UI

1. Navigate to "🧪 Run Test" page
2. Select a protocol from the dropdown
3. Fill in specimen information
4. Click "Start Test Run"
5. Progress through test steps
6. Record measurements and observations
7. Complete the test with final result

### Via Python API

See the Quick Start section above for a complete example.

## Viewing Results

### In the UI

1. Navigate to "📊 Results" page
2. Use filters to find specific test runs
3. Click on a test run to view details
4. Export data or generate reports

### Programmatically

```python
from src.models import TestRun

# Get all completed test runs
completed_runs = session.query(TestRun).filter_by(
    status=TestStatus.COMPLETED
).all()

# Get summary
summary = executor.get_test_run_summary(test_run)
print(summary)
```

## Protocol Format

Protocols are defined in JSON format following the schema in `schemas/protocol_schema.json`.

### Required Fields

- `protocol_id`: Unique identifier (e.g., "TWIST-001")
- `protocol_name`: Human-readable name
- `version`: Semantic version number
- `category`: Test category (Mechanical, Electrical, etc.)
- `description`: Detailed description
- `standard_reference`: Industry standards referenced
- `test_parameters`: Configurable parameters
- `test_steps`: Sequential test procedure
- `acceptance_criteria`: Pass/fail criteria
- `data_collection`: Measurement specifications

### Example Protocol Structure

```json
{
  "protocol_id": "EXAMPLE-001",
  "protocol_name": "Example Test Protocol",
  "version": "1.0.0",
  "category": "Mechanical",
  "description": "Example protocol description",
  "test_steps": [
    {
      "step_number": 1,
      "description": "First test step",
      "action": "measurement"
    }
  ],
  "acceptance_criteria": [
    {
      "criterion_id": "AC-001",
      "description": "Criterion description",
      "evaluation_method": "measurement",
      "threshold": {
        "parameter": "power",
        "operator": "<=",
        "value": 5.0
      }
    }
  ]
}
```

## Schema Validation

All protocols are validated against the JSON schema before import:

```python
loader = ProtocolLoader()
try:
    loader.validate_protocol(protocol_data)
    print("Protocol is valid!")
except jsonschema.ValidationError as e:
    print(f"Validation error: {e}")
```

## Best Practices

### Protocol Design

1. **Clear Descriptions**: Write clear, unambiguous step descriptions
2. **Automation Flags**: Mark steps as automation-capable when possible
3. **Safety First**: Include comprehensive safety requirements
4. **Measurable Criteria**: Define objective, measurable acceptance criteria
5. **Standard Compliance**: Reference applicable industry standards

### Test Execution

1. **Documentation**: Photograph specimens before and after testing
2. **Environmental Control**: Maintain consistent test conditions
3. **Calibration**: Ensure all instruments are calibrated
4. **Repeatability**: Follow procedures exactly as written
5. **Data Integrity**: Record all measurements accurately

### Data Management

1. **Backup**: Regularly backup the database
2. **Versioning**: Use protocol versions for traceability
3. **Metadata**: Include comprehensive test metadata
4. **Archiving**: Archive completed test data appropriately

## API Reference

For detailed API documentation, see:
- [Database Models](../src/models/)
- [Protocol Parsers](../src/parsers/)
- [Analysis Tools](../src/analysis/)

## Contributing

To contribute new protocols or features:

1. Fork the repository
2. Create a feature branch
3. Add your protocol or feature
4. Write tests
5. Submit a pull request

## Support

For issues, questions, or contributions:
- GitHub Issues: [Project Issues](https://github.com/your-org/test-protocols/issues)
- Documentation: This directory
- Email: support@example.com

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

**Last Updated:** 2025-11-14
