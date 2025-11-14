# PV Testing Protocol Framework Documentation

## Overview

The PV Testing Protocol Framework is a modular, JSON-based system for defining, executing, and analyzing photovoltaic device testing protocols. It provides a standardized approach to test execution with integrated quality control, automated analysis, and comprehensive reporting.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture](#architecture)
3. [Protocol Definitions](#protocol-definitions)
4. [Python API](#python-api)
5. [Database Integration](#database-integration)
6. [UI Components](#ui-components)
7. [Testing](#testing)
8. [Examples](#examples)

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from src.database import init_db; init_db()"
```

### Running a Test

```python
from src.protocols import Protocol, SpectralResponseTest

# Load protocol
protocol = Protocol("protocols/SPEC-001.json")

# Initialize test
test = SpectralResponseTest(protocol=protocol)

# Configure test parameters
test_params = {
    "wavelength": {"start": 300, "end": 1200, "step_size": 10},
    "temperature": 25,
    "integration_time": 100,
    "averaging": 3
}

sample_info = {
    "sample_id": "CELL-001",
    "sample_type": "Solar Cell",
    "technology": "c-Si",
    "area": 1.0
}

# Run test
test_id = test.initialize(test_params, sample_info)
test.run()
test.load_reference_calibration()
test.analyze()
test.run_qc()
test.export_results()
test.complete()
```

### Running the UI

```bash
streamlit run src/ui/app.py
```

## Architecture

### System Components

```
┌─────────────────────────────────────────────────┐
│              User Interface Layer               │
│  (Streamlit/GenSpark UI Components)            │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│           Protocol Engine Layer                 │
│  - Protocol Loading & Validation                │
│  - Test Execution & Control                     │
│  - Analysis & QC                                │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│              Data Layer                         │
│  - Database Models (SQLAlchemy)                 │
│  - File I/O (CSV, JSON, Images)                │
└─────────────────────────────────────────────────┘
```

### Directory Structure

```
test-protocols/
├── protocols/              # JSON protocol definitions
│   ├── SPEC-001.json      # Spectral Response Test
│   └── protocol_schema.json
├── src/                   # Source code
│   ├── protocols/         # Protocol execution engine
│   │   ├── base.py       # Base classes
│   │   └── spec_001.py   # SPEC-001 implementation
│   ├── database/          # Database models
│   │   └── models.py
│   └── ui/                # UI components
│       ├── app.py        # Main Streamlit app
│       └── spec_001_ui.py
├── tests/                 # Test suite
│   ├── unit/
│   └── integration/
├── docs/                  # Documentation
├── examples/              # Example scripts
└── database/              # Database files and migrations
```

## Protocol Definitions

### JSON Protocol Structure

Protocols are defined in JSON format following a standardized schema:

```json
{
  "protocol_id": "SPEC-001",
  "protocol_name": "Spectral Response Test",
  "version": "1.0.0",
  "standard": "IEC 60904-8",
  "category": "Performance",
  "description": "Protocol description",
  "equipment_required": [...],
  "test_parameters": {...},
  "procedure": [...],
  "data_outputs": {...},
  "qc_criteria": {...},
  "analysis": {...}
}
```

### Key Sections

#### Equipment Required
Defines all equipment needed for the test with specifications:

```json
"equipment_required": [
  {
    "id": "monochromator",
    "name": "Monochromator System",
    "type": "optical",
    "specifications": {
      "wavelength_range": [300, 1200],
      "wavelength_accuracy": "±1 nm"
    },
    "required": true
  }
]
```

#### Test Parameters
Defines configurable test parameters with validation:

```json
"test_parameters": {
  "wavelength": {
    "type": "range",
    "min": 300,
    "max": 1200,
    "default_start": 300,
    "default_end": 1200,
    "required": true
  }
}
```

#### QC Criteria
Quality control checks with thresholds:

```json
"qc_criteria": {
  "noise_level": {
    "description": "Maximum acceptable noise",
    "threshold": 0.02,
    "unit": "A/W",
    "action_on_fail": "warning"
  }
}
```

## Python API

### Protocol Class

```python
from src.protocols import Protocol

# Load protocol
protocol = Protocol("protocols/SPEC-001.json")

# Access protocol information
print(protocol.protocol_id)
print(protocol.protocol_name)
print(protocol.version)

# Get components
parameters = protocol.get_parameter("wavelength")
equipment = protocol.get_equipment()
procedure = protocol.get_procedure()
qc_criteria = protocol.get_qc_criteria()

# Validate parameters
is_valid, errors = protocol.validate_parameters(test_params)
```

### ProtocolExecutor Base Class

All test implementations extend `ProtocolExecutor`:

```python
from src.protocols.base import ProtocolExecutor

class MyTest(ProtocolExecutor):
    def run(self):
        # Implement measurement logic
        pass

    def analyze(self):
        # Implement analysis logic
        pass
```

### SpectralResponseTest Class

```python
from src.protocols import SpectralResponseTest

test = SpectralResponseTest(protocol=protocol)

# Initialize
test_id = test.initialize(test_params, sample_info)

# Run measurement
test.run()

# Load reference calibration
test.load_reference_calibration("path/to/calibration.csv")

# Analyze
test.analyze()

# QC checks
qc_results = test.run_qc()

# Generate plots
plot_paths = test.generate_plots()

# Export results
exported_files = test.export_results()

# Complete
test.complete()
```

## Database Integration

### Models

- **Protocol**: Protocol definitions
- **Sample**: Device under test information
- **Equipment**: Equipment/instrument records
- **TestExecution**: Test run instances
- **TestResult**: Individual measurement data points
- **QualityControl**: QC check results

### Usage

```python
from src.database import get_session, init_db
from src.database.models import add_sample_to_db

# Initialize database
init_db()

# Get session
session = get_session()

# Add sample
sample = add_sample_to_db({
    "sample_id": "CELL-001",
    "sample_type": "Solar Cell",
    "technology": "c-Si",
    "area": 1.0
}, session)
```

## UI Components

### Streamlit App

The framework includes a full-featured Streamlit UI:

**Features:**
- Protocol selection
- Test configuration
- Real-time test execution
- Interactive results visualization
- QC status monitoring
- Report generation
- Data export

**Running the UI:**
```bash
streamlit run src/ui/app.py
```

### UI Tabs

1. **Test Setup**: Configure test parameters and sample information
2. **Run Test**: Execute test with real-time progress
3. **Results**: View and analyze results with interactive plots
4. **Reports**: Generate and export test reports

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run integration tests only
pytest tests/integration/

# Run with coverage
pytest --cov=src --cov-report=html
```

### Test Structure

- `tests/unit/`: Unit tests for individual components
- `tests/integration/`: End-to-end workflow tests

## Examples

See `examples/` directory for:

- `basic_spectral_response.py`: Simple spectral response test
- `batch_testing.py`: Running multiple tests in batch
- `custom_analysis.py`: Custom analysis workflows
- `database_integration.py`: Database integration examples

## Advanced Topics

### Creating Custom Protocols

1. Create JSON protocol definition in `protocols/`
2. Implement protocol executor class extending `ProtocolExecutor`
3. Add UI components in `src/ui/`
4. Write tests in `tests/`

### Extending Analysis

Override the `analyze()` method in your executor:

```python
def analyze(self):
    # Custom analysis logic
    results = super().analyze()

    # Add custom calculations
    results["custom_metric"] = self.calculate_custom_metric()

    return results
```

### Custom QC Checks

Override the `run_qc()` method:

```python
def run_qc(self):
    qc_results = super().run_qc()

    # Add custom QC check
    qc_results["custom_check"] = {
        "passed": self.check_custom_condition(),
        "value": self.measured_value,
        "threshold": self.threshold
    }

    return qc_results
```

## API Reference

See `docs/api/` for complete API documentation.

## Contributing

See `CONTRIBUTING.md` for contribution guidelines.

## License

MIT License - see `LICENSE` file.
