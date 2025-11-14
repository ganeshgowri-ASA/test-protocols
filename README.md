# Test Protocols Framework

Modular PV Testing Protocol Framework - JSON-based dynamic templates for Streamlit/GenSpark UI with automated analysis, charting, QC, and report generation. Integrated with LIMS, QMS, and Project Management systems.

## Overview

The Test Protocols Framework provides a comprehensive solution for managing and executing photovoltaic (PV) module testing protocols. Built with modularity and extensibility in mind, it enables laboratories to:

- Define testing protocols using JSON templates
- Execute automated test sequences with real-time monitoring
- Collect and analyze test data with built-in QC checks
- Generate professional reports in multiple formats
- Integrate with existing laboratory systems (LIMS, QMS, PM)

## Features

- **JSON-Based Protocol Definitions**: Easy to create, version control, and share
- **Streamlit/GenSpark UI**: Intuitive web interface for test management
- **Real-Time Monitoring**: Live data visualization and QC alerts
- **Automated QC Checks**: Continuous and periodic quality control validation
- **Comprehensive Reporting**: PDF, HTML, and Excel export formats
- **Database Integration**: PostgreSQL/SQLite with full audit trail
- **Modular Architecture**: Easy to extend with new protocols and integrations

## Implemented Protocols

### Environmental Testing

- **DESERT-001**: Desert Climate Test (P39/54)
  - 200 thermal cycles simulating desert conditions
  - Temperature range: -10°C to 85°C
  - Low daytime humidity (15%) with UV exposure
  - Automated degradation tracking
  - Comprehensive pass/fail criteria

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from database import init_db; init_db()"
```

### Running the UI

```bash
# Start Streamlit application
streamlit run ui/app.py
```

The application will open in your browser at http://localhost:8501

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific protocol tests
pytest -m desert
```

## Project Structure

```
test-protocols/
├── protocols/              # Protocol definitions and implementations
│   ├── environmental/      # Environmental testing protocols
│   │   ├── desert-001.json # DESERT-001 protocol definition
│   │   └── environmental.py # Environmental protocol classes
│   ├── base.py            # Base protocol class
│   └── schema.py          # JSON schema validation
│
├── ui/                    # User interface components
│   ├── app.py            # Main Streamlit application
│   ├── protocol_selector.py
│   ├── parameter_input.py
│   └── results_display.py
│
├── database/             # Database layer
│   ├── models.py        # SQLAlchemy ORM models
│   ├── session.py       # Database session management
│   └── schema.sql       # PostgreSQL schema
│
├── tests/               # Test suite
│   ├── test_protocols.py
│   ├── test_database.py
│   └── conftest.py
│
└── docs/                # Documentation
    ├── README.md
    ├── architecture.md
    └── desert_climate_protocol.md
```

## Usage Example

```python
from protocols.environmental import DesertClimateProtocol

# Initialize protocol
protocol = DesertClimateProtocol()

# Configure parameters
parameters = {
    "daytime_temperature": 65,
    "nighttime_temperature": 5,
    "daytime_humidity": 15,
    "nighttime_humidity": 40,
    "total_cycles": 200
}

# Validate parameters
is_valid, errors = protocol.validate_parameters(parameters)

if is_valid:
    # Execute protocol
    protocol.execute(parameters)

    # Generate report
    report = protocol.generate_report()
```

## Database Schema

The framework uses a relational database to store:

- **Protocols**: Protocol definitions and versions
- **Test Runs**: Execution records and status
- **Data Points**: Time-series measurement data
- **QC Results**: Quality control check results
- **Interim Tests**: Periodic test measurements

See [docs/database.md](docs/database.md) for detailed schema documentation.

## Configuration

Create a `.env` file based on `.env.example`:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/test_protocols

# LIMS Integration
LIMS_API_URL=https://api.lims.example.com
LIMS_API_KEY=your_api_key

# QMS Integration
QMS_API_URL=https://api.qms.example.com
QMS_API_KEY=your_api_key
```

## Documentation

- [System Architecture](docs/architecture.md)
- [DESERT-001 Protocol Guide](docs/desert_climate_protocol.md)
- [API Documentation](docs/api.md)
- [Contributing Guidelines](CONTRIBUTING.md)

## Testing

The project includes comprehensive test coverage:

```bash
# Unit tests
pytest tests/test_protocols.py

# Database tests
pytest tests/test_database.py

# Integration tests
pytest tests/integration/

# All tests with coverage
pytest --cov=protocols --cov=database --cov=ui --cov-report=html
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

- ganeshgowri-ASA

## Acknowledgments

- Based on IEC 61215, IEC 61730, UL 1703, and IEC TS 63126 standards
- Inspired by industry best practices in PV module testing

## Support

For issues, questions, or contributions, please visit:
https://github.com/ganeshgowri-ASA/test-protocols/issues
