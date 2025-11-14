# Test Protocols Framework

Modular PV Testing Protocol Framework - JSON-based dynamic templates for Streamlit/GenSpark UI with automated analysis, charting, QC, and report generation. Integrated with LIMS, QMS, and Project Management systems.

## Overview

A comprehensive framework for managing and executing photovoltaic (PV) testing protocols with built-in validation, analysis, and reporting capabilities.

## Features

- **Modular Protocol System**: Define protocols using JSON schemas
- **Dynamic UI Generation**: Streamlit-based forms generated from protocol definitions
- **Automated Validation**: JSON schema validation + custom QC criteria
- **Data Processing**: Statistical analysis, outlier detection, coefficient calculations
- **Visualization**: Interactive charts using Plotly
- **Database Integration**: SQLAlchemy ORM with support for multiple databases
- **Report Generation**: Automated report creation in multiple formats
- **Comprehensive Testing**: Unit and integration tests with pytest

## Implemented Protocols

### CONC-001 - Concentration Testing

Complete implementation including:
- ✅ JSON schema with validation rules
- ✅ Default configuration
- ✅ UI form templates
- ✅ Python core modules (ProtocolManager, SchemaValidator, DataProcessor)
- ✅ Database models and schema
- ✅ Streamlit UI components
- ✅ Comprehensive tests (unit + integration)
- ✅ Complete documentation

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Install dependencies
pip install -r requirements.txt

# Initialize database
python scripts/setup_db.py
```

### Running the UI

```bash
streamlit run src/ui/streamlit_app.py
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

## Project Structure

```
test-protocols/
├── protocols/              # Protocol definitions
│   └── conc-001/           # CONC-001 Concentration Testing
│       ├── schema/         # JSON schemas
│       ├── config/         # Default configurations
│       └── templates/      # UI templates
├── src/                    # Source code
│   ├── core/               # Core modules
│   │   ├── protocol_manager.py
│   │   ├── schema_validator.py
│   │   └── data_processor.py
│   ├── database/           # Database models
│   │   ├── models.py
│   │   └── schema.py
│   └── ui/                 # UI components
│       ├── streamlit_app.py
│       └── components/
├── tests/                  # Test suite
│   ├── unit/
│   └── integration/
├── docs/                   # Documentation
│   ├── architecture.md
│   └── examples/
└── scripts/                # Utility scripts
```

## Usage Example

```python
from src.core import ProtocolManager, SchemaValidator, DataProcessor

# Load protocol
pm = ProtocolManager()
protocol = pm.get_protocol('conc-001')

# Validate data
validator = SchemaValidator(pm)
result = validator.validate_data('conc-001', test_data)

# Process and analyze
processor = DataProcessor(pm)
df = processor.process_raw_data('conc-001', test_data)
report = processor.generate_summary_report('conc-001', test_data)
```

## Documentation

- [Architecture Overview](docs/architecture.md)
- [CONC-001 Walkthrough](docs/examples/conc-001-walkthrough.md)
- [Protocol README](protocols/conc-001/README.md)

## Testing

The framework includes comprehensive test coverage:

- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **Database Tests**: ORM and schema validation
- **Fixtures**: Sample data for testing

Run tests with:
```bash
pytest -v
```

## Technology Stack

- **Backend**: Python 3.8+, SQLAlchemy, Pandas, NumPy
- **Frontend**: Streamlit, Plotly
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Testing**: pytest, pytest-cov
- **Validation**: jsonschema

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For questions or issues:
- Open an issue on GitHub
- Refer to documentation in `docs/`
- Check protocol-specific README files

## Version

1.0.0 - Initial release with CONC-001 protocol
