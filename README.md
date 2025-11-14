# Test Protocols Framework

Modular PV Testing Protocol Framework - JSON-based dynamic templates for Streamlit/GenSpark UI with automated analysis, charting, QC, and report generation. Integrated with LIMS, QMS, and Project Management systems.

## Overview

This framework provides a comprehensive solution for managing and executing photovoltaic module testing protocols according to international standards (IEC 61215, IEC 61730, etc.).

## Features

- **JSON-Based Protocol Definitions**: Define test protocols declaratively using JSON templates
- **Dynamic UI Generation**: Streamlit-based UI automatically generated from protocol definitions
- **Automated Data Collection**: Real-time data acquisition and validation
- **Quality Control**: Built-in QC checks with outlier detection and range validation
- **Statistical Analysis**: Comprehensive statistical analysis including degradation calculations
- **Interactive Visualization**: Plotly-based charts for data exploration
- **Database Integration**: SQLAlchemy ORM with support for SQLite and PostgreSQL
- **Report Generation**: Automated report generation with customizable templates
- **Extensible Architecture**: Modular design for easy protocol addition

## Implemented Protocols

### BYPASS-001: Bypass Diode Testing
- **Standard**: IEC 61215 MQT 18
- **Category**: Safety
- **Duration**: ~33 hours
- **Description**: Comprehensive bypass diode testing including thermal stress and cycling

## Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Setup

```bash
# Clone the repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from src.database.connection import DatabaseManager; db = DatabaseManager(); db.init_db()"
```

## Quick Start

### Running the Streamlit UI

```bash
streamlit run src/ui/app.py
```

Then navigate to http://localhost:8501 in your browser.

### Using the Framework Programmatically

```python
from src.core.protocol_loader import ProtocolLoader
from src.core.data_processor import DataProcessor, Measurement
from datetime import datetime

# Load a protocol
loader = ProtocolLoader()
protocol = loader.load_protocol("bypass-diode-testing")

# Process measurements
processor = DataProcessor(protocol)
measurement = Measurement(
    measurement_id="diode_forward_voltage",
    phase_id="p2_initial_electrical",
    timestamp=datetime.now(),
    value=0.65,
    unit="V"
)
processor.add_measurement(measurement)

# Get statistics
stats = processor.get_statistics()
print(f"Mean: {stats['mean']:.3f}V")
```

## Project Structure

```
test-protocols/
├── src/
│   ├── core/               # Core framework logic
│   │   ├── protocol_loader.py
│   │   ├── data_processor.py
│   │   └── validators.py
│   ├── protocols/          # Protocol definitions
│   │   └── bypass-diode-testing/
│   │       ├── protocol.json
│   │       ├── schema.json
│   │       ├── metadata.json
│   │       └── README.md
│   ├── database/           # Database models and connections
│   │   ├── models.py
│   │   ├── connection.py
│   │   └── schema.py
│   ├── analysis/           # Analysis and QC modules
│   │   ├── qc_checks.py
│   │   ├── statistical_analysis.py
│   │   └── charting.py
│   └── ui/                 # Streamlit UI
│       └── app.py
├── tests/                  # Test suite
│   ├── unit/
│   └── integration/
├── docs/                   # Documentation
├── config/                 # Configuration files
└── requirements.txt        # Python dependencies
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_protocol_loader.py -v
```

## Configuration

Configuration files are in the `config/` directory:
- `development.yaml`: Development environment settings
- `production.yaml`: Production environment settings

Edit these files to configure:
- Database connection
- UI settings
- Logging preferences
- Integration endpoints (LIMS, QMS)

## Documentation

- [BYPASS-001 Protocol Specification](src/protocols/bypass-diode-testing/README.md)
- [BYPASS-001 Implementation Guide](docs/BYPASS-001-implementation.md)
- [Protocol Definition Guide](docs/protocol_definition.md) *(coming soon)*
- [API Reference](docs/api_reference.md) *(coming soon)*

## Adding New Protocols

1. Create a new directory in `src/protocols/`
2. Define your protocol in `protocol.json`
3. Create `schema.json` for validation
4. Add `metadata.json` with protocol information
5. Write documentation in `README.md`
6. The UI will automatically detect and load the new protocol

See existing protocols for examples.

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Standards Compliance

This framework supports the following standards:
- IEC 61215: Terrestrial photovoltaic modules - Design qualification
- IEC 61730: Photovoltaic module safety qualification
- IEC 62804: Test methods for detection of PID
- UL 1703: Flat-Plate Photovoltaic Modules and Panels

## License

MIT License - see LICENSE file for details

## Support

- Issues: https://github.com/ganeshgowri-ASA/test-protocols/issues
- Documentation: See `docs/` directory

## Roadmap

- [ ] Additional protocols (Humidity-Freeze, Hot-Spot Endurance, etc.)
- [ ] Real-time instrument integration
- [ ] PDF report generation
- [ ] Multi-user authentication
- [ ] REST API for external integrations
- [ ] Advanced statistical process control (SPC) charts
- [ ] Machine learning for predictive maintenance
