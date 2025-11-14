# PV Test Protocols Framework

Modular PV Testing Protocol Framework - JSON-based dynamic templates for Streamlit/GenSpark UI with automated analysis, charting, QC, and report generation. Integrated with LIMS, QMS, and Project Management systems.

## Features

- **JSON-Based Protocols**: Define test protocols in human-readable JSON format
- **Automated Test Execution**: Execute tests with real-time data collection and monitoring
- **Standards Compliance**: Built for IEC 61215, UL 1703, ASTM, and other standards
- **Web-Based UI**: Streamlit/GenSpark interface for test management
- **Database-Backed**: PostgreSQL for robust data storage and retrieval
- **Automated Analysis**: Statistical analysis and pass/fail determination
- **Report Generation**: Automated PDF, HTML, and Markdown reports
- **Integration Ready**: LIMS, QMS, and project management integrations

## Implemented Protocols

### ML-001: Mechanical Load Static Test (2400Pa)
- **Standard**: IEC 61215 MQT 16
- **Category**: Mechanical
- **Duration**: 180 minutes
- **Purpose**: Evaluate module ability to withstand wind, snow, and static loads
- **Status**: ✅ Fully implemented with JSON schema, Python modules, tests, and documentation

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
make install-dev

# Run tests
make test
```

### Running a Test

```python
from test_protocols.core.protocol_loader import ProtocolLoader
from test_protocols.core.test_executor import TestExecutor

# Load protocol
loader = ProtocolLoader()
protocol = loader.load_protocol("protocols/mechanical_load/ml_001_protocol.json")

# Create and run test
executor = TestExecutor(protocol)
test_run = executor.create_test_run(
    sample_id="PV-2025-001",
    operator_id="operator1"
)
executor.start_test()
```

### Starting the UI

```bash
# Start Streamlit UI
make run-ui

# Or directly
streamlit run src/test_protocols/ui/streamlit_app.py
```

Access at: http://localhost:8501

## Project Structure

```
test-protocols/
├── src/test_protocols/          # Main package
│   ├── core/                    # Core modules (protocol, executor, analyzer)
│   ├── schemas/                 # JSON schemas
│   ├── database/                # Database models and schema
│   ├── ui/                      # Streamlit UI components
│   ├── integrations/            # External integrations (LIMS, QMS)
│   └── utils/                   # Utility functions
├── protocols/                   # Test protocol definitions
│   ├── mechanical_load/         # ML-001 protocol
│   └── templates/               # Protocol templates
├── tests/                       # Test suite
├── docs/                        # Documentation
├── config/                      # Configuration files
└── scripts/                     # Utility scripts
```

## Architecture

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

## Documentation

- **[Framework Documentation](docs/README.md)**: Comprehensive framework guide
- **[ML-001 Protocol Guide](docs/ml_001_mechanical_load_test.md)**: Detailed ML-001 protocol documentation
- **[API Reference](docs/README.md#api-reference)**: Python API documentation
- **[Database Schema](src/test_protocols/database/schema.sql)**: Database design

## Development

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
pytest tests/ -v --cov=test_protocols --cov-report=html
```

### Code Formatting

```bash
# Format code
make format

# Run linting
make lint
```

### Database Setup

```bash
# Initialize database
make setup-db

# Or manually
python scripts/setup_database.py
```

## Configuration

### Database Configuration

Set the `DATABASE_URL` environment variable:

```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/test_protocols"
```

### UI Configuration

Edit `config/genspark_ui_config.yaml` for UI customization.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-protocol`)
3. Implement changes with tests
4. Run tests and linting (`make test lint`)
5. Commit changes (`git commit -am 'Add new protocol'`)
6. Push to branch (`git push origin feature/new-protocol`)
7. Create Pull Request

## Standards Support

- **IEC 61215**: Terrestrial PV modules - Design qualification and type approval
- **UL 1703**: Flat-Plate Photovoltaic Modules and Panels
- **ASTM E1171**: Standard Test Method for Photovoltaic Modules in Cyclic Temperature and Humidity Environments
- **IEC 61730**: PV module safety qualification

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Contact

- **Repository**: https://github.com/ganeshgowri-ASA/test-protocols
- **Issues**: https://github.com/ganeshgowri-ASA/test-protocols/issues
- **Documentation**: https://github.com/ganeshgowri-ASA/test-protocols/docs
