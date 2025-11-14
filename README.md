# Test Protocols Framework

Modular PV Testing Protocol Framework with JSON-based dynamic templates for Streamlit UI, featuring automated analysis, real-time monitoring, charting, QC, and report generation.

## Overview

This framework provides a comprehensive solution for managing photovoltaic (PV) module testing protocols with a focus on:

- **IEC 61701 Compliance**: Full implementation of salt mist corrosion testing standard
- **Real-time Monitoring**: Live chamber conditions tracking and QC validation
- **Automated Analysis**: I-V curve analysis with degradation tracking
- **Visual Documentation**: Image capture and corrosion progression logging
- **Database Integration**: SQLAlchemy-based persistence with complete audit trail
- **Extensible Architecture**: Easy to add new protocols and testing methods

## Features

### SALT-001: Salt Mist Corrosion Test

Complete implementation of IEC 61701 standard for PV module salt mist corrosion testing:

- **Automated Cycle Management**: Spray/dry cycle tracking with phase logging
- **Real-time Environmental Monitoring**: Temperature, humidity, salt concentration tracking
- **I-V Curve Measurements**: Automated power degradation analysis
- **Visual Inspection Logging**: Image capture with corrosion rating assessment
- **Quality Control**: Automated IEC 61701 compliance checks
- **Comprehensive Reporting**: PDF, Excel, HTML, and JSON report generation

#### IEC 61701 Severity Levels

- **Level 1**: 60 hours exposure
- **Level 2**: 120 hours exposure
- **Level 3**: 240 hours exposure (default)
- **Level 4**: 480 hours exposure
- **Level 5**: 840 hours exposure

#### Environmental Specifications

- **Salt Concentration**: 5.0 ± 0.5% NaCl
- **Temperature**: 35 ± 1°C
- **Relative Humidity**: 95 ± 2%
- **Cycle**: 2 hours spray + 22 hours dry (24-hour cycle)

## Installation

### Requirements

- Python 3.9+
- SQLite or PostgreSQL
- Required packages (see `requirements.txt`)

### Setup

```bash
# Clone repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .

# Initialize database
python scripts/setup_db.py

# Configure environment (copy and edit)
cp .env.example .env
```

### Configuration

Edit `.env` file to configure:

```bash
# Database
DATABASE_URL=sqlite:///test_protocols.db

# Storage
REPORT_OUTPUT_DIR=./reports
IMAGE_STORAGE_DIR=./images

# Logging
LOG_LEVEL=INFO
DEBUG=False

# Optional integrations
LIMS_API_URL=
QMS_API_URL=
```

## Quick Start

### Start the UI

```bash
streamlit run src/test_protocols/ui/app.py
```

Access the application at `http://localhost:8501`

### Programmatic Usage

```python
from test_protocols.protocols.registry import protocol_registry
from test_protocols.database.connection import db

# Initialize database
db.connect()

# Get SALT-001 protocol
protocol = protocol_registry.get_protocol("SALT-001")

# Configure test parameters
parameters = {
    "specimen_id": "PV-MOD-2024-001",
    "module_type": "Crystalline Silicon",
    "severity_level": "Level 3 - 240 hours",
    "salt_concentration": 5.0,
    "chamber_temperature": 35.0,
    "relative_humidity": 95.0,
    "spray_duration": 2.0,
    "dry_duration": 22.0,
}

# Execute protocol
results = protocol.execute(parameters)

# Log environmental data
protocol.update_cycle(
    cycle_number=1,
    phase="spray",
    temperature=35.0,
    humidity=95.0,
    salt_concentration=5.0,
)

# Record I-V measurement
protocol.record_iv_measurement(
    elapsed_hours=0.0,
    voltage=[0, 5, 10, 15, 20, 25, 30, 35, 40],
    current=[8.5, 8.4, 8.3, 8.1, 7.5, 6.0, 3.0, 1.0, 0],
)

# Record visual inspection
protocol.record_visual_inspection(
    elapsed_hours=24.0,
    corrosion_rating="1 - Slight corrosion, <1% of area",
    affected_area_percent=0.5,
)

# Perform QC checks
qc_status = protocol.quality_check(results)

# Get summary
summary = protocol.get_test_summary()
```

## Project Structure

```
test-protocols/
├── src/test_protocols/
│   ├── protocols/          # Protocol implementations
│   │   ├── base.py         # Abstract base protocol
│   │   ├── salt_001.py     # SALT-001 implementation
│   │   └── registry.py     # Protocol registry
│   ├── models/             # Database models
│   │   └── schema.py       # SQLAlchemy models
│   ├── database/           # Database management
│   │   └── connection.py   # Connection handling
│   ├── ui/                 # Streamlit UI
│   │   ├── app.py          # Main application
│   │   └── pages/          # UI pages
│   │       ├── home.py
│   │       ├── new_test.py
│   │       ├── active_tests.py
│   │       ├── analysis.py
│   │       ├── reports.py
│   │       └── settings.py
│   ├── config.py           # Configuration
│   ├── constants.py        # Constants and enums
│   └── logger.py           # Logging setup
├── templates/
│   └── protocols/
│       └── salt-001.json   # SALT-001 protocol template
├── tests/                  # Test suite
│   ├── unit/
│   └── integration/
├── scripts/
│   └── setup_db.py         # Database initialization
└── docs/                   # Documentation
    └── protocols/
        └── SALT-001.md     # SALT-001 documentation
```

## Usage Guide

### 1. Starting a New Test

1. Navigate to "New Test" in the sidebar
2. Select protocol (SALT-001)
3. Enter specimen information and test parameters
4. Configure environmental conditions
5. Click "Start Test"

### 2. Monitoring Active Tests

1. Navigate to "Active Tests"
2. Select test from dropdown
3. View real-time chamber conditions
4. Log measurements:
   - Environmental data (temperature, humidity, salt concentration)
   - I-V curve measurements
   - Visual inspections with images

### 3. Analyzing Results

1. Navigate to "Analysis"
2. Select completed or active test
3. View:
   - I-V curves overlay (time progression)
   - Power degradation charts
   - Corrosion progression
   - Environmental stability plots
   - Inspection image gallery

### 4. Generating Reports

1. Navigate to "Reports"
2. Select completed test
3. Choose report format (PDF, Excel, HTML, JSON)
4. Configure options (include images, raw data)
5. Generate report

## Database Schema

### Main Tables

- **protocols**: Protocol templates and definitions
- **test_runs**: Test execution instances
- **iv_measurements**: I-V curve measurement data
- **visual_inspections**: Visual inspection records with images
- **environmental_logs**: Environmental conditions log
- **qc_checks**: Quality control check results
- **reports**: Generated report metadata

### Relationships

- One Protocol → Many Test Runs
- One Test Run → Many I-V Measurements
- One Test Run → Many Visual Inspections
- One Test Run → Many Environmental Logs
- One Test Run → Many QC Checks
- One Test Run → Many Reports

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/test_protocols --cov-report=html

# Run specific test file
pytest tests/unit/test_protocols.py

# Run specific test
pytest tests/unit/test_protocols.py::TestSALT001Protocol::test_execute_success
```

## Development

### Adding a New Protocol

1. Create protocol class in `src/test_protocols/protocols/`
2. Inherit from `BaseProtocol`
3. Implement required methods:
   - `validate_inputs()`
   - `execute()`
   - `quality_check()`
4. Create JSON template in `templates/protocols/`
5. Register in `registry.py`
6. Add tests in `tests/unit/`
7. Add documentation in `docs/protocols/`

### Code Style

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

## Documentation

- [SALT-001 Protocol Details](docs/protocols/SALT-001.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [API Reference](docs/API.md)
- [Contributing Guide](CONTRIBUTING.md)

## Standards Compliance

- **IEC 61701:2020**: Photovoltaic (PV) modules - Salt mist corrosion testing
- **ASTM B117**: Standard Practice for Operating Salt Spray (Fog) Apparatus
- **ISO 12944**: Paints and coatings - Corrosion protection of steel structures

## License

MIT License - see [LICENSE](LICENSE) file for details

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/ganeshgowri-ASA/test-protocols/issues
- Documentation: https://github.com/ganeshgowri-ASA/test-protocols/wiki

## Acknowledgments

- IEC 61701:2020 standard for salt mist corrosion testing
- Streamlit team for the UI framework
- SQLAlchemy for database ORM
- Plotly for interactive charting

## Roadmap

- [ ] Additional protocols (thermal cycling, humidity-freeze, UV exposure)
- [ ] Advanced reporting with customizable templates
- [ ] LIMS/QMS integration
- [ ] Multi-user support with authentication
- [ ] Automated email notifications
- [ ] REST API for external integrations
- [ ] Mobile app for field inspections
- [ ] Machine learning for predictive analysis
