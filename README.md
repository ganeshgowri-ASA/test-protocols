# PV Testing Protocol Framework

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Modular PV Testing Protocol Framework - JSON-based dynamic templates for Streamlit/GenSpark UI with automated analysis, charting, QC, and report generation. Integrated with LIMS, QMS, and Project Management systems.

## Overview

The PV Testing Protocol Framework provides a comprehensive solution for defining, executing, and analyzing photovoltaic module testing protocols. Built with flexibility and automation in mind, it enables testing laboratories to:

- **Define protocols dynamically** using JSON templates
- **Execute tests** with real-time progress tracking
- **Collect data** systematically with validation
- **Analyze results** against acceptance criteria
- **Generate reports** automatically
- **Visualize trends** and performance metrics

## Features

### 🔬 Dynamic Protocol Definition
- JSON-based protocol templates
- Schema validation for consistency
- Support for multiple test categories (Mechanical, Electrical, Environmental, etc.)
- Standards-compliant (IEC 61215, IEC 61730, etc.)

### 🧪 Test Execution
- Step-by-step guided testing
- Real-time progress tracking
- Automated and manual test steps
- Measurement recording and validation
- Photographic documentation support

### 📊 Data Management
- SQLAlchemy-based database backend
- Structured data storage
- Historical test tracking
- Specimen management
- Operator and facility tracking

### 📈 Analytics & Reporting
- Test result analysis
- Pass/fail rate statistics
- Trend analysis over time
- Protocol performance metrics
- Interactive visualizations with Plotly

### 🖥️ Modern UI
- Streamlit-based web interface
- Intuitive navigation
- Real-time updates
- Mobile-responsive design
- Protocol browsing and management

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/test-protocols.git
cd test-protocols

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database and load protocols
make setup-dev
```

### Run the Application

```bash
# Start the Streamlit UI
make run

# Or directly:
streamlit run src/ui/app.py
```

The application will open at `http://localhost:8501`

## Available Protocols

### Mechanical Tests

- **TWIST-001: Module Twist Test** - Evaluates module resistance to torsional stress
  - Standard: IEC 61215-2 MQT 20
  - Test cycles: 3 cycles per corner
  - Acceptance: ≤5% power degradation

## Project Structure

```
test-protocols/
├── protocols/              # JSON protocol definitions
│   ├── mechanical/        # Mechanical test protocols
│   │   └── TWIST-001.json
│   ├── electrical/        # Electrical test protocols
│   └── environmental/     # Environmental test protocols
├── src/                   # Source code
│   ├── models/           # Database models
│   ├── parsers/          # Protocol parsers and executors
│   ├── analysis/         # Analysis engines
│   └── ui/               # Streamlit UI components
├── schemas/              # JSON schemas
│   └── protocol_schema.json
├── tests/                # Unit and integration tests
│   ├── unit/
│   └── integration/
├── docs/                 # Documentation
│   ├── README.md
│   └── TWIST-001_Module_Twist_Test.md
├── requirements.txt      # Python dependencies
├── setup.py             # Package setup
├── pyproject.toml       # Project configuration
└── Makefile             # Development tasks
```

## Usage Examples

### Load a Protocol

```python
from src.parsers import ProtocolLoader
from src.models.base import get_engine, get_session

# Initialize
engine = get_engine()
session = get_session(engine)
loader = ProtocolLoader()

# Load protocol
protocol = loader.get_protocol_by_id("TWIST-001", session)
print(f"Loaded: {protocol.protocol_name}")
```

### Create and Run a Test

```python
from src.parsers import ProtocolExecutor
from src.models.test_run import TestResult

# Create executor
executor = ProtocolExecutor(session)

# Create test run
test_run = executor.create_test_run(
    protocol=protocol,
    specimen_id="MODULE-12345",
    operator_name="John Doe",
    manufacturer="SolarTech Inc.",
    model_number="ST-350-72M"
)

# Start test
executor.start_test_run(test_run)

# Record measurements
executor.record_measurement(
    test_run=test_run,
    measurement_id="M-001",
    parameter="Maximum Power",
    value=350.5,
    unit="W",
    measurement_type="pre_test"
)

# Complete test
executor.complete_test_run(test_run, TestResult.PASS)
```

### Analyze Results

```python
# Get test summary
summary = executor.get_test_run_summary(test_run)
print(f"Progress: {summary['progress']['percentage']}%")
print(f"Measurements: {len(summary['measurements'])}")

# Evaluate acceptance criteria
result = executor.evaluate_acceptance_criteria(test_run, protocol)
print(f"Test result: {result.value}")
```

## Development

### Running Tests

```bash
# Run all tests with coverage
make test

# Run specific test file
pytest tests/unit/test_twist_001.py -v

# Run quick tests (no coverage)
make test-quick
```

### Code Quality

```bash
# Run linter and type checking
make lint

# Format code
make format
```

### Database Management

```bash
# Initialize database
make db-init

# Reset database (WARNING: deletes all data)
make db-reset

# Load protocols from files
make load-protocols
```

## Creating Custom Protocols

1. Create a JSON file following the schema in `schemas/protocol_schema.json`
2. Validate the protocol structure
3. Place in appropriate category directory under `protocols/`
4. Load into database using the UI or `make load-protocols`

See `docs/README.md` for detailed protocol creation guidelines.

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- [User Guide](docs/README.md)
- [TWIST-001 Protocol Specification](docs/TWIST-001_Module_Twist_Test.md)
- [API Reference](docs/README.md#api-reference)
- [Contributing Guide](CONTRIBUTING.md)

## Technology Stack

- **Backend:** Python 3.8+
- **Database:** SQLAlchemy with SQLite (PostgreSQL compatible)
- **Web Framework:** Streamlit
- **Data Analysis:** Pandas, NumPy
- **Visualization:** Plotly
- **Testing:** pytest
- **Code Quality:** ruff, mypy

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or contributions:
- **Issues:** [GitHub Issues](https://github.com/your-org/test-protocols/issues)
- **Documentation:** [docs/](docs/)
- **Email:** testing@example.com

## Acknowledgments

This framework supports testing protocols based on:
- IEC 61215 (Terrestrial PV modules - Design qualification)
- IEC 61730 (PV module safety qualification)
- IEC 62716 (Ammonia corrosion testing)
- And other industry standards

---

**Developed for PV Testing and Quality Assurance**
