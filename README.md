# PV Testing Protocol Framework

A modular, extensible framework for photovoltaic testing protocols with JSON-based dynamic templates, Streamlit/GenSpark UI, automated analysis, charting, quality control, and report generation.

## Overview

This framework provides a standardized approach to defining and executing photovoltaic cell and module testing protocols. It combines:

- **JSON-based protocol definitions** for flexibility and version control
- **Python implementation** with extensible base classes
- **Streamlit web interface** for protocol execution and results viewing
- **SQLAlchemy database** for data persistence
- **Automated analysis** modules for common PV measurements
- **Comprehensive reporting** with charts, tables, and exports

## Features

- 📋 **Protocol Management**: JSON-based protocol definitions
- 🔬 **Automated Testing**: Streamlined execution workflows
- 📊 **Real-time Analysis**: Crack detection, IV analysis, degradation tracking
- ✅ **Quality Control**: Built-in pass/fail criteria validation
- 📈 **Reporting**: Automated PDF/HTML report generation
- 🗄️ **Database Integration**: SQLAlchemy models for data persistence
- 🔗 **Extensible**: Easy to add new protocols and analysis modules

## Available Protocols

### CRACK-001: Cell Crack Propagation

**Category:** Degradation
**Standard:** IEC 61215-2:2021

Monitor and quantify crack propagation in PV cells under thermal and mechanical stress.

- Thermal cycling (-40°C to +85°C)
- Mechanical load testing (0-5400 Pa)
- EL imaging for crack detection
- IV curve performance tracking
- Automated pass/fail evaluation

**Documentation:** [docs/protocols/CRACK-001.md](docs/protocols/CRACK-001.md)

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python src/database/init_db.py
```

## Quick Start

### Running the Web UI

```bash
streamlit run src/ui/app.py
```

Navigate to `http://localhost:8501` in your browser.

### Using the Python API

```python
from pathlib import Path
from src.protocols.base import ProtocolDefinition, SampleMetadata
from src.protocols.degradation.crack_001 import CrackPropagationProtocol

# Load protocol
protocol_path = Path("protocols/degradation/crack-001/protocol.json")
definition = ProtocolDefinition(protocol_path)
protocol = CrackPropagationProtocol(definition)

# Configure test
parameters = {
    'stress_type': 'thermal_cycling',
    'thermal_cycles': 200,
    'measurement_interval': 50
}

# Define sample
sample = SampleMetadata(
    sample_id="SAMPLE-001",
    manufacturer="SunPower",
    cell_type="mono-PERC",
    cell_efficiency=22.0,
    cell_area=243.36,
    manufacturing_date="2025-11-14",
    initial_pmax=5.0,
    initial_voc=0.68,
    initial_isc=9.5,
    initial_ff=0.80
)

# Validate and execute
errors = protocol.validate_setup([sample], parameters)
if not errors:
    results = protocol.execute([sample], parameters)
```

## Project Structure

```
test-protocols/
├── protocols/              # Protocol definitions (JSON)
│   └── degradation/
│       └── crack-001/
│           └── protocol.json
├── src/                   # Python source code
│   ├── protocols/        # Protocol implementations
│   │   ├── base.py      # Base classes
│   │   └── degradation/
│   │       └── crack_001.py
│   ├── analysis/         # Analysis modules
│   │   ├── crack_detection.py
│   │   └── iv_analysis.py
│   ├── database/         # Database models
│   │   ├── models.py
│   │   └── init_db.py
│   └── ui/              # Streamlit UI
│       ├── app.py
│       └── pages/
├── tests/               # Test suite
│   ├── unit/
│   └── integration/
├── docs/                # Documentation
│   └── protocols/
├── data/                # Data storage
│   └── schemas/
├── requirements.txt     # Python dependencies
├── LICENSE
└── README.md
```

## Running Tests

Execute the test suite:

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/unit/protocols/test_crack_001.py -v
```

## Creating Custom Protocols

### 1. Define Protocol JSON

Create a JSON file in `protocols/<category>/<protocol-id>/protocol.json`:

```json
{
  "protocol_id": "MY-PROTOCOL-001",
  "name": "My Custom Protocol",
  "version": "1.0.0",
  "category": "performance",
  "test_parameters": { ... },
  "measurements": { ... },
  "pass_fail_criteria": { ... }
}
```

### 2. Implement Protocol Class

Create a Python implementation in `src/protocols/<category>/`:

```python
from src.protocols.base import BaseProtocol, ProtocolDefinition

class MyProtocol(BaseProtocol):
    def validate_setup(self, samples, parameters):
        # Validation logic
        pass

    def execute(self, samples, parameters):
        # Execution logic
        pass

    def analyze(self, measurements):
        # Analysis logic
        pass

    def evaluate_pass_fail(self, analysis_results):
        # Pass/fail evaluation
        pass
```

### 3. Register Protocol

```python
from src.protocols.base import protocol_registry

protocol_registry.register("MY-PROTOCOL-001", MyProtocol)
```

## Database Schema

The framework uses SQLAlchemy with support for SQLite, PostgreSQL, and MySQL.

Key tables:
- `protocols`: Protocol definitions
- `samples`: PV sample metadata
- `test_runs`: Test execution records
- `measurements`: Measurement data (IV, EL, etc.)
- `crack_data`: Crack detection results
- `degradation_analysis`: Analysis results

See [src/database/models.py](src/database/models.py) for full schema.

## API Reference

### Core Classes

- `BaseProtocol`: Abstract base class for all protocols
- `ProtocolDefinition`: JSON protocol definition loader
- `ProtocolResult`: Container for execution results
- `SampleMetadata`: PV sample metadata
- `CrackDetector`: EL image crack detection
- `IVAnalyzer`: IV curve analysis

### Analysis Modules

- **Crack Detection**: `src/analysis/crack_detection.py`
  - Crack area and length measurement
  - Cell isolation detection
  - Severity classification

- **IV Analysis**: `src/analysis/iv_analysis.py`
  - Parameter extraction (Pmax, Voc, Isc, FF)
  - Degradation rate calculation
  - Temperature correction

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/ganeshgowri-ASA/test-protocols/issues)
- **Email**: support@genspark.com

## Acknowledgments

- IEC 61215-2:2021 standard for PV module testing
- Open-source Python scientific computing ecosystem
- Streamlit for rapid UI development
