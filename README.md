# PV Test Protocol System

**Modular PV Testing Protocol Framework** - A JSON-based dynamic templates system for executing photovoltaic module test protocols with automated analysis, charting, quality control, and report generation.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)

## Overview

The PV Test Protocol System provides a comprehensive framework for defining, executing, and analyzing photovoltaic module test protocols. Built with flexibility and extensibility in mind, the system supports JSON-based protocol definitions, automated data validation, real-time quality control, and seamless integration with LIMS, QMS, and project management systems.

## Key Features

- **Dynamic Protocol Templates** - JSON-based protocol definitions with full configurability
- **Streamlit UI** - Interactive web interface for test execution and monitoring
- **Automated QC** - Real-time quality control checks and alerts
- **Data Validation** - Comprehensive input validation and error checking
- **Database Integration** - SQLAlchemy ORM with support for SQLite, PostgreSQL, MySQL
- **Progress Tracking** - Real-time test progress monitoring
- **Flexible Analysis** - Configurable charts, statistics, and calculations
- **Report Generation** - Automated comprehensive test reports
- **Equipment Management** - Calibration tracking and equipment registry
- **Sample Tracking** - Complete sample lifecycle management
- **API-First Design** - RESTful integration capabilities

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from src.database import init_database; init_database()"
```

### Running the Application

```bash
# Start the Streamlit UI
streamlit run src/ui/app.py
```

Access the application at `http://localhost:8501`

## Project Structure

```
test-protocols/
├── protocols/              # Protocol definitions
│   ├── templates/         # JSON protocol templates
│   │   └── degradation/   # Degradation test protocols
│   │       └── pid-002.json
│   └── schemas/           # JSON validation schemas
├── src/                   # Source code
│   ├── core/             # Core protocol engine
│   ├── ui/               # Streamlit UI components
│   ├── database/         # Database models
│   ├── analysis/         # Data analysis modules
│   └── integrations/     # External system integrations
├── tests/                # Test suite
│   ├── unit/            # Unit tests
│   └── integration/     # Integration tests
├── docs/                # Documentation
│   ├── protocols/       # Protocol user guides
│   └── api/            # API documentation
└── data/               # Database and data files
```

## Available Protocols

### PID-002: Potential-Induced Degradation (Polarization)

**Standard:** IEC 62804-1
**Category:** Degradation Testing
**Duration:** ~12 days (192h stress + 96h recovery)

Evaluates PV module susceptibility to potential-induced degradation caused by high voltage stress under elevated temperature and humidity conditions.

**Key Parameters:**
- Voltage stress: -1000V (configurable)
- Temperature: 85°C ± 2°C
- Relative humidity: 85% ± 5%
- Test duration: 192 hours (configurable)
- Recovery period: 96 hours

See [PID-002 User Guide](docs/protocols/PID-002-User-Guide.md) for detailed information.

## Usage Examples

### Loading a Protocol

```python
from src.core import ProtocolLoader

loader = ProtocolLoader()
protocol = loader.load_protocol("PID-002")
print(f"Loaded: {protocol['name']}")
```

### Validating a Protocol

```python
from src.core import ProtocolValidator

validator = ProtocolValidator()
is_valid, errors = validator.validate_protocol_structure(protocol)

if is_valid:
    print("Protocol is valid!")
else:
    print(f"Validation errors: {errors}")
```

### Executing a Test

```python
from src.core import ProtocolExecutor, StepStatus

# Create executor
executor = ProtocolExecutor(protocol, "TEST-RUN-001")

# Start test
executor.start_test(metadata={
    "operator": "John Doe",
    "facility": "Lab A",
    "sample_id": "MODULE-001"
})

# Execute a step
executor.start_step(step_id=1, substep_id=1.1)
executor.record_data(1, 1.1, {"test_value": 42.5})
executor.complete_step(1, 1.1, StepStatus.COMPLETED)

# Get progress
progress = executor.get_progress()
print(f"Progress: {progress['progress_percent']:.1f}%")

# Complete test
executor.complete_test(StepStatus.COMPLETED)
```

## Testing

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/unit/test_protocol_loader.py
```

## Documentation

- [Getting Started Guide](docs/Getting-Started.md)
- [PID-002 Protocol User Guide](docs/protocols/PID-002-User-Guide.md)
- [API Reference](docs/api/) (coming soon)
- [Integration Guide](docs/integration/) (coming soon)

## Technology Stack

- **Backend:** Python 3.8+
- **Web Framework:** Streamlit
- **Database:** SQLAlchemy ORM (SQLite/PostgreSQL/MySQL)
- **Data Processing:** Pandas, NumPy
- **Visualization:** Plotly, Matplotlib
- **Testing:** Pytest
- **Validation:** JSON Schema, Pydantic

## System Requirements

- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended)
- 1GB free disk space
- Modern web browser (Chrome, Firefox, Safari, Edge)

## Configuration

### Database Configuration

Default configuration uses SQLite:
```python
DATABASE_URL=sqlite:///data/test_protocols.db
```

For PostgreSQL:
```python
DATABASE_URL=postgresql://user:password@localhost/test_protocols
```

### Environment Variables

Create a `.env` file:
```bash
DATABASE_URL=sqlite:///data/test_protocols.db
LOG_LEVEL=INFO
UI_PORT=8501
```

## Development

### Setting Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt

# Install pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Roadmap

- [ ] Additional test protocols (TC-200, HF-200, etc.)
- [ ] Advanced charting and visualization
- [ ] PDF report generation
- [ ] Email notifications
- [ ] LIMS integration
- [ ] REST API
- [ ] Mobile-responsive UI
- [ ] Multi-user support
- [ ] Role-based access control

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation:** See [docs/](docs/) directory
- **Issues:** [GitHub Issues](https://github.com/ganeshgowri-ASA/test-protocols/issues)
- **Email:** support@example.com

## Acknowledgments

- Based on international standards (IEC 62804-1, IEC 61215, IEC 61730)
- Built with modern Python best practices
- Inspired by industry needs for standardized PV testing

---

**Made with ❤️ for the PV testing community**
