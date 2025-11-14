# PV Test Protocol Framework Documentation

## Overview

The PV Test Protocol Framework is a modular, JSON-based system for managing and executing photovoltaic module test protocols according to international standards (IEC 61215, UL 1703, ASTM, etc.).

## Table of Contents

1. [Architecture](#architecture)
2. [Getting Started](#getting-started)
3. [Protocol Development](#protocol-development)
4. [Test Execution](#test-execution)
5. [Database Schema](#database-schema)
6. [UI Guide](#ui-guide)
7. [API Reference](#api-reference)
8. [Examples](#examples)

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     GenSpark/Streamlit UI                    │
│  Protocol Selection │ Test Runner │ Monitoring │ Reports    │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────┐
│                     Python Core Framework                    │
│  ProtocolLoader │ TestExecutor │ ResultAnalyzer            │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────┐
│                      Database Layer (PostgreSQL)             │
│  Protocols │ TestRuns │ Measurements │ Results              │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────┐
│                        Integrations                          │
│  LIMS │ QMS │ Project Management │ Email Notifications     │
└─────────────────────────────────────────────────────────────┘
```

### Key Features

- **JSON-Based Protocols**: Human-readable, version-controlled protocol definitions
- **Real-Time Data Collection**: Continuous measurement logging and monitoring
- **Automated Analysis**: Statistical analysis and pass/fail determination
- **Flexible UI**: GenSpark/Streamlit-based web interface
- **Database-Backed**: PostgreSQL for robust data storage
- **Standards Compliance**: Built for IEC 61215, UL 1703, and other standards
- **Integration Ready**: LIMS, QMS, and project management integrations

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- pip or conda

### Installation

```bash
# Clone repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Install dependencies
pip install -r requirements.txt

# Set up database
python scripts/setup_database.py

# Run tests
pytest tests/

# Start UI
streamlit run src/test_protocols/ui/streamlit_app.py
```

### Configuration

1. **Database Configuration** (`config/database_config.yaml`)
```yaml
database:
  host: localhost
  port: 5432
  name: test_protocols
  user: postgres
  password: ${DB_PASSWORD}
```

2. **UI Configuration** (`config/genspark_ui_config.yaml`)
```yaml
app:
  title: "PV Test Protocol Suite"
  theme: "light"
database:
  connection_string_env: "DATABASE_URL"
```

## Protocol Development

### Protocol Structure

A protocol is defined in JSON format following this structure:

```json
{
  "protocol_id": "ML-001",
  "version": "1.0.0",
  "name": "Mechanical Load Static Test",
  "category": "mechanical",
  "standard": {
    "name": "IEC",
    "code": "IEC 61215 MQT 16"
  },
  "tests": [
    {
      "step_id": "ML-001-S01",
      "name": "Pre-Test Inspection",
      "sequence": 1,
      "parameters": {...},
      "measurements": [...]
    }
  ]
}
```

### Creating a New Protocol

1. **Define Protocol JSON**
   - Create file in `protocols/<category>/<id>_protocol.json`
   - Follow schema defined in `src/test_protocols/schemas/protocol_schema.json`

2. **Validate Protocol**
```python
from test_protocols.core.protocol_loader import ProtocolLoader

loader = ProtocolLoader()
protocol = loader.load_protocol("protocols/mechanical_load/ml_001_protocol.json")
is_valid, errors = protocol.validate()
```

3. **Add to Database**
```python
from test_protocols.database.models import Protocol as ProtocolModel

# Save to database
# (Implementation depends on your DB setup)
```

## Test Execution

### Running a Test

```python
from test_protocols.core.protocol_loader import ProtocolLoader
from test_protocols.core.test_executor import TestExecutor

# Load protocol
loader = ProtocolLoader()
protocol = loader.load_protocol("protocols/mechanical_load/ml_001_protocol.json")

# Create executor
executor = TestExecutor(protocol)

# Create test run
test_run = executor.create_test_run(
    sample_id="PV-2025-001",
    operator_id="operator1"
)

# Start test
executor.start_test()

# Execute steps
for step in protocol.tests:
    executor.start_step(step.step_id)

    # Record measurements
    executor.record_measurement(
        step_id=step.step_id,
        measurement_type="pressure",
        value=2400.0,
        unit="Pa"
    )

    # Complete step
    executor.complete_step(step.step_id, passed=True)

# Complete test
executor.complete_test()
```

### Analyzing Results

```python
from test_protocols.core.result_analyzer import ResultAnalyzer

# Analyze results
analyzer = ResultAnalyzer(test_run)
analysis = analyzer.analyze_test()

# Generate report
markdown_report = analyzer.generate_report_markdown()

# Export data
data_dict = analyzer.export_to_dict()
```

## Database Schema

### Tables

#### `protocols`
Stores protocol definitions

| Column | Type | Description |
|--------|------|-------------|
| protocol_id | VARCHAR(20) | Primary key |
| version | VARCHAR(20) | Protocol version |
| name | VARCHAR(255) | Protocol name |
| category | ENUM | Test category |
| definition | JSONB | Full protocol JSON |

#### `test_runs`
Stores test execution instances

| Column | Type | Description |
|--------|------|-------------|
| test_run_id | VARCHAR(100) | Primary key |
| protocol_id | VARCHAR(20) | Foreign key to protocols |
| sample_id | VARCHAR(100) | Sample identifier |
| status | ENUM | Test status |
| start_time | TIMESTAMP | Test start time |

#### `measurements`
Stores measurement data points

| Column | Type | Description |
|--------|------|-------------|
| measurement_id | VARCHAR(36) | Primary key |
| test_run_id | VARCHAR(100) | Foreign key to test_runs |
| measurement_type | VARCHAR(100) | Type of measurement |
| value | FLOAT | Measured value |
| unit | VARCHAR(50) | Unit of measurement |
| timestamp | TIMESTAMP | Measurement timestamp |

See [`database/schema.sql`](../src/test_protocols/database/schema.sql) for complete schema.

## UI Guide

### Starting the UI

```bash
streamlit run src/test_protocols/ui/streamlit_app.py
```

Access at: `http://localhost:8501`

### Main Pages

1. **Protocol Selection**: Browse and select protocols
2. **Test Runner**: Execute tests with real-time monitoring
3. **Live Monitoring**: View measurement data and charts
4. **Results Analysis**: Analyze completed tests
5. **Report Generation**: Generate and download reports
6. **Equipment Management**: Track calibration and maintenance
7. **Admin Panel**: System administration

## API Reference

### Core Classes

#### `Protocol`
Represents a test protocol

```python
from test_protocols.core.protocol import Protocol

protocol = Protocol(
    protocol_id="ML-001",
    version="1.0.0",
    name="Mechanical Load Test",
    category="mechanical",
    standard=Standard(name="IEC", code="61215"),
    tests=[...]
)

# Validate protocol
is_valid, errors = protocol.validate()

# Get step by ID
step = protocol.get_step("ML-001-S01")

# Calculate duration
total_duration = protocol.get_total_duration()
```

#### `ProtocolLoader`
Loads protocols from JSON

```python
from test_protocols.core.protocol_loader import ProtocolLoader

loader = ProtocolLoader()
protocol = loader.load_protocol("path/to/protocol.json")
```

#### `TestExecutor`
Executes test protocols

```python
from test_protocols.core.test_executor import TestExecutor

executor = TestExecutor(protocol)
test_run = executor.create_test_run("sample_id", "operator_id")
executor.start_test()
```

#### `ResultAnalyzer`
Analyzes test results

```python
from test_protocols.core.result_analyzer import ResultAnalyzer

analyzer = ResultAnalyzer(test_run)
analysis = analyzer.analyze_test()
report = analyzer.generate_report_markdown()
```

## Examples

### Example 1: ML-001 Mechanical Load Test

See [`ml_001_mechanical_load_test.md`](ml_001_mechanical_load_test.md) for detailed protocol documentation.

**Quick Start:**
```python
# Load and run ML-001 protocol
from test_protocols.core.protocol_loader import ProtocolLoader
from test_protocols.core.test_executor import TestExecutor

loader = ProtocolLoader()
protocol = loader.load_protocol("protocols/mechanical_load/ml_001_protocol.json")

executor = TestExecutor(protocol)
test_run = executor.create_test_run("PV-2025-001", "operator1")
executor.start_test()

# Execute test steps...
```

### Example 2: Custom Protocol

```python
# Create custom protocol programmatically
from test_protocols.core.protocol import Protocol, TestStep, Standard

protocol = Protocol(
    protocol_id="CUSTOM-001",
    version="1.0.0",
    name="Custom Test Protocol",
    category="electrical",
    standard=Standard(name="Custom", code="CUSTOM-STD-001"),
    tests=[
        TestStep(
            step_id="CUSTOM-001-S01",
            name="Test Step 1",
            sequence=1,
            parameters={"param1": "value1"}
        )
    ]
)

# Validate and save
is_valid, errors = protocol.validate()
if is_valid:
    loader = ProtocolLoader()
    loader.save_protocol(protocol, "protocols/custom/custom_001_protocol.json")
```

## Support

For issues or questions:
- GitHub Issues: https://github.com/ganeshgowri-ASA/test-protocols/issues
- Documentation: https://docs.test-protocols.example.com
- Email: support@example.com

## License

MIT License - See LICENSE file for details
