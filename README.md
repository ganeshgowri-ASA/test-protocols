# PV Testing Protocol Framework

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A modular, JSON-based framework for photovoltaic module testing with automated analysis, charting, QC validation, and report generation.

## Features

- 📋 **JSON-Based Protocol Definitions**: Define test protocols using structured JSON schemas
- 🔄 **Dynamic UI Generation**: Automatically generate Streamlit UIs from protocol schemas
- 📊 **Real-Time Visualization**: Interactive charts for leakage current, power degradation, and environmental conditions
- ✅ **Automated QC Validation**: Built-in quality control checks with configurable thresholds
- 📈 **Leakage Tracking**: Advanced anomaly detection and event tracking for leakage currents
- 🗄️ **Database Integration**: SQLAlchemy-based persistence for protocols, tests, and measurements
- 🔌 **LIMS/QMS Ready**: Integration-ready architecture for external systems
- 📄 **Automated Reports**: Generate compliance reports for test results

## Available Protocols

### PID-001: PID Shunting Test (IEC 62804)

Potential-Induced Degradation (PID) test for photovoltaic modules following IEC 62804 standard.

**Key Features:**
- Leakage current monitoring with real-time anomaly detection
- Power degradation tracking
- Environmental condition monitoring (temperature, humidity)
- Automated IEC 62804 compliance validation
- Warning and critical threshold alerting

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Install dependencies
pip install -r requirements.txt

# Initialize database
python scripts/init_db.py
```

### Running the Application

```bash
# Start Streamlit UI
streamlit run src/ui/streamlit_app.py

# Or with custom port
streamlit run src/ui/streamlit_app.py --server.port 8502
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov=protocols --cov-report=html

# Run specific test file
pytest protocols/pid-001/tests/test_implementation.py

# Run with verbose output
pytest -v
```

## Project Structure

```
test-protocols/
├── protocols/                  # Protocol implementations
│   └── pid-001/               # PID-001 Protocol
│       ├── schema.json        # JSON schema definition
│       ├── template.json      # Default parameter template
│       ├── implementation.py  # Protocol logic
│       └── tests/             # Protocol-specific tests
├── src/                       # Source code
│   ├── core/                  # Core engine components
│   │   ├── protocol_engine.py # Protocol execution engine
│   │   └── schema_validator.py# Schema validation
│   ├── models/                # Database models
│   │   ├── database.py        # Database configuration
│   │   └── protocol.py        # SQLAlchemy models
│   ├── ui/                    # User interface
│   │   ├── streamlit_app.py   # Main Streamlit app
│   │   └── components/        # UI components
│   ├── integrations/          # External system integrations
│   └── analysis/              # Analysis modules
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests
│   └── integration/           # Integration tests
├── config/                    # Configuration
├── docs/                      # Documentation
└── scripts/                   # Utility scripts
```

## Usage Examples

### 1. Running a PID-001 Test

```python
from src.core.protocol_engine import ProtocolEngine
from protocols.pid_001.implementation import PID001Protocol, LeakageTracker

# Initialize engine
engine = ProtocolEngine()

# Define test parameters
parameters = {
    "test_name": "PID-TEST-001",
    "module_id": "PV-MODULE-12345",
    "test_voltage": -1000,
    "test_duration": 96,
    "temperature": 85,
    "relative_humidity": 85,
    "sampling_interval": 60,
    "leakage_current_threshold": 10,
    "operator": "Test Engineer",
    "notes": "Standard IEC 62804 test"
}

# Create test execution
test_execution = engine.create_test_execution("pid-001", parameters)
print(f"Test created: {test_execution.id}")
```

### 2. Processing Measurements with Leakage Tracking

```python
from protocols.pid_001.implementation import PID001Protocol, LeakageTracker
from datetime import datetime

# Initialize protocol and tracker
protocol = PID001Protocol()
tracker = LeakageTracker(threshold_warning=5.0, threshold_critical=10.0)

# Process measurement
measurement_data = {
    "timestamp": datetime.utcnow(),
    "elapsed_time": 10.0,
    "leakage_current": 3.5,
    "voltage": -1000,
    "temperature": 85.0,
    "humidity": 85.0,
    "power_degradation": 0.8
}

measurement, event = protocol.process_measurement(
    test_execution,
    measurement_data,
    tracker
)

if event:
    print(f"Leakage anomaly detected: {event['description']}")
```

### 3. Performing QC Checks

```python
# Perform QC validation
qc_status, qc_checks = protocol.perform_qc_checks(measurements, parameters)

print(f"QC Status: {qc_status}")
for check in qc_checks:
    print(f"- {check.check_name}: {check.status} ({check.message})")

# Generate results summary
summary = protocol.generate_results_summary(measurements, qc_checks, qc_status)
print(f"IEC 62804 Compliant: {summary['compliance']['iec_62804_compliant']}")
```

## Configuration

Create a `.env` file in the project root:

```bash
# Database
DATABASE_URL=sqlite:///./test_protocols.db

# LIMS Integration (Optional)
LIMS_API_URL=https://lims.example.com/api
LIMS_API_KEY=your-api-key

# QMS Integration (Optional)
QMS_API_URL=https://qms.example.com/api
QMS_API_KEY=your-api-key

# Application
DEBUG=True
LOG_LEVEL=INFO
```

## Documentation

- [Usage Guide](docs/USAGE.md) - Detailed usage instructions
- [Protocol Development Guide](docs/PROTOCOL_DEVELOPMENT.md) - Creating new protocols
- [API Reference](docs/API.md) - API documentation
- [Architecture Overview](docs/ARCHITECTURE.md) - System architecture

## Testing

The framework includes comprehensive test coverage:

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest protocols/pid-001/tests/

# Generate coverage report
pytest --cov=src --cov=protocols --cov-report=html
open htmlcov/index.html
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-protocol`)
3. Commit your changes (`git commit -am 'Add new protocol'`)
4. Push to the branch (`git push origin feature/new-protocol`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Roadmap

- [ ] Additional protocol implementations (IEC 61215, IEC 61730)
- [ ] REST API for programmatic access
- [ ] Enhanced LIMS/QMS integrations
- [ ] Real-time monitoring dashboard
- [ ] Automated report generation (PDF/Excel)
- [ ] Multi-user support with authentication
- [ ] Cloud deployment support

## Authors

- GenSpark Team

## Acknowledgments

- IEC 62804 Standard for PID testing methodology
- Streamlit for the UI framework
- SQLAlchemy for database ORM
