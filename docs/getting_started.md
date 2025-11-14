# Getting Started with Test Protocols Framework

## Overview

The Test Protocols Framework is a comprehensive solution for managing and executing photovoltaic testing protocols with automated analysis, charting, QC, and report generation.

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Install Dependencies

```bash
# Install from requirements.txt
pip install -r requirements.txt

# Or install with development dependencies
pip install -e ".[dev]"
```

### Environment Setup

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Configure your environment variables in `.env`:
```
DATABASE_URL=sqlite:///./data/db/test_protocols.db
APP_ENV=development
LOG_LEVEL=INFO
```

### Database Initialization

Initialize the database schema:

```python
from src.utils.db import DatabaseManager

db_manager = DatabaseManager()
db_manager.init_database('data/db/schema.sql')
```

## Quick Start

### Running the Streamlit UI

Launch the web interface:

```bash
streamlit run src/ui/app.py
```

Navigate to http://localhost:8501 in your browser.

### Running a Test Programmatically

```python
from src.core.protocol import ProtocolEngine
from src.tests.track.track_001.protocol import TRACK001Protocol
from src.tests.track.track_001.test_runner import TRACK001TestRunner

# Load protocol from JSON
protocol = ProtocolEngine.from_json('schemas/examples/track_001_example.json')

# Create test runner
runner = TRACK001TestRunner(protocol)

# Run test
run_id = runner.run_test(
    data_source="simulated",
    operator="John Doe",
    sample_id="TRACKER-001",
    latitude=40.0,
    longitude=-105.0
)

print(f"Test completed: {run_id}")

# Analyze results
results = protocol.analyze_results()

# Get summary
summary = protocol.get_test_summary()
print(summary)
```

### Creating a Custom Protocol

1. Create a JSON configuration file following the schema:

```json
{
  "protocol_id": "CUSTOM-001",
  "name": "My Custom Test",
  "version": "1.0.0",
  "category": "Performance",
  "test_parameters": {
    "duration": {"value": 2, "unit": "hours"},
    "sample_interval": {"value": 10, "unit": "minutes"},
    "metrics": [
      {
        "name": "my_metric",
        "type": "angle",
        "unit": "degrees",
        "description": "Custom metric"
      }
    ]
  },
  "qc_criteria": {
    "data_completeness": 95
  },
  "analysis_methods": {
    "statistical_analysis": {
      "methods": ["mean", "std_dev"],
      "parameters": ["my_metric"]
    }
  }
}
```

2. Validate the protocol:

```python
from src.core.validator import ProtocolValidator

validator = ProtocolValidator()
is_valid = validator.validate_protocol(protocol_data)

if not is_valid:
    print("Validation errors:", validator.get_errors())
```

## Project Structure

```
test-protocols/
├── src/                    # Source code
│   ├── core/              # Core protocol engine
│   ├── tests/             # Test implementations
│   ├── ui/                # Streamlit interface
│   ├── integrations/      # External system integrations
│   └── utils/             # Utilities
├── schemas/               # JSON schemas
├── data/                  # Data and database
├── docs/                  # Documentation
├── tests/                 # Unit and integration tests
└── config/                # Configuration files
```

## Running Tests

Execute the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_protocol.py

# Run specific test
pytest tests/unit/test_protocol.py::test_protocol_initialization
```

## Configuration

The framework supports three environments:

- **Development** (`config/dev.yaml`)
- **Test** (`config/test.yaml`)
- **Production** (`config/prod.yaml`)

Set the environment via:
```bash
export APP_ENV=production
```

## Next Steps

- [TRACK-001 Protocol Documentation](track_001/overview.md)
- [Protocol Framework Guide](protocol_framework.md)
- [API Reference](api.md)
- [Database Schema](database.md)

## Support

For issues and feature requests, please contact the development team or refer to the project repository.
