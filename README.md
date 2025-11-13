# PV Testing Protocol Framework

Modular PV Testing Protocol Framework - JSON-based dynamic templates for Streamlit/GenSpark UI with automated analysis, charting, QC, and report generation. Integrated with LIMS, QMS, and Project Management systems.

## Features

- **Standards Compliant**: IEC 61215-1:2021, IEC 61730
- **Interactive UI**: Streamlit-based GenSpark interface
- **Automated Analysis**: Real-time calculations and validation
- **Data Visualization**: Interactive Plotly charts
- **Data Traceability**: SHA256 hashing and audit trails
- **Modular Design**: Easy to extend with new protocols
- **Quality Assurance**: Comprehensive test suite
- **System Integration**: LIMS, QMS, and PM connectors

## Implemented Protocols

### LIC-001: Low Irradiance Conditions Test

Performance testing at multiple low irradiance levels (200, 400, 600, 800 W/m²) at 25°C.

**Standard**: IEC 61215-1:2021
**Category**: PERFORMANCE
**Version**: 1.0.0

**Key Features**:
- I-V curve measurements at 4 irradiance levels
- Automated Pmax, Fill Factor, and Efficiency calculations
- Interactive Plotly visualizations
- Real-time data validation
- Quality scoring and assessment
- Complete data traceability

[Full Documentation](docs/protocols/LIC-001.md)

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Install from Source

```bash
# Clone the repository
git clone https://github.com/your-org/test-protocols.git
cd test-protocols

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### Install Dependencies Only

```bash
pip install -r requirements.txt
```

## Quick Start

### Using the Interactive UI

Launch the GenSpark Streamlit interface:

```bash
streamlit run ui/genspark.py
```

Then navigate to `http://localhost:8501` in your browser.

### Using the Python API

```python
from protocols.lic_001 import LIC001Protocol

# Initialize protocol
protocol = LIC001Protocol()

# Create test run
test_run = protocol.create_test_run(
    sample_id="SAMPLE-001",
    sample_info={
        "module_type": "Example 100W",
        "manufacturer": "Example Corp",
        "module_area": 0.65,
        "cell_technology": "mono-Si",
        "rated_power": 100.0,
        "num_cells": 60
    },
    operator="John Doe"
)

# Add measurements
test_run["measurements"]["200"] = {
    "actual_irradiance": 200.0,
    "actual_temperature": 25.0,
    "iv_curve": {
        "voltage": [0, 0.1, 0.2, ..., 0.6],
        "current": [8.5, 8.4, 8.2, ..., 0.0]
    }
}

# Continue for 400, 600, 800 W/m²...

# Validate and analyze
is_valid, errors = protocol.validate_inputs(test_run)
if is_valid:
    results = protocol.calculate_results(test_run)
    print(f"Test Passed: {results['summary']['test_passed']}")
    print(f"Quality Score: {results['summary']['quality_score']}")
```

## Project Structure

```
test-protocols/
├── core/                      # Core framework
│   ├── base_protocol.py       # Base protocol class
│   ├── models.py              # Database models
│   ├── validators.py          # Validation framework
│   └── utils.py               # Utility functions
├── protocols/                 # Protocol implementations
│   └── lic_001/              # LIC-001 protocol
│       ├── schema.json        # JSON schema
│       ├── protocol.py        # Protocol implementation
│       ├── analysis.py        # Analysis functions
│       ├── validation.py      # Validation rules
│       └── visualization.py   # Plotly charts
├── ui/                        # User interface
│   ├── genspark.py           # Main Streamlit app
│   └── components.py         # Reusable UI components
├── tests/                     # Test suite
│   ├── conftest.py           # Pytest fixtures
│   └── test_lic_001.py       # LIC-001 tests
├── docs/                      # Documentation
│   └── protocols/            # Protocol documentation
│       └── LIC-001.md
├── requirements.txt           # Dependencies
├── setup.py                  # Package setup
└── README.md                 # This file
```

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_lic_001.py -v

# Run with coverage report
pytest --cov=protocols --cov=core --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Development

### Adding a New Protocol

1. Create protocol directory: `protocols/NEW_PROTOCOL/`
2. Implement required files:
   - `schema.json` - JSON schema definition
   - `protocol.py` - Protocol class (inherit from BaseProtocol)
   - `analysis.py` - Analysis functions
   - `validation.py` - Validation rules
   - `visualization.py` - Plotly visualizations (optional)

3. Add tests: `tests/test_NEW_PROTOCOL.py`
4. Add documentation: `docs/protocols/NEW_PROTOCOL.md`
5. Update UI to include new protocol

### Code Style

```bash
# Format code
black .

# Lint
flake8 .

# Type checking
mypy .
```

## Configuration

### Database

Configure database connection in `.env`:

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/pv_testing
```

### LIMS/QMS Integration

Configure integration endpoints in `.env`:

```bash
LIMS_API_URL=https://lims.example.com/api
LIMS_API_KEY=your_api_key

QMS_API_URL=https://qms.example.com/api
QMS_API_KEY=your_api_key
```

## Documentation

- [LIC-001 Protocol Guide](docs/protocols/LIC-001.md)
- [API Reference](docs/api/)
- [Development Guide](docs/development.md)

## Standards Compliance

This framework implements testing protocols according to:

- **IEC 61215-1:2021** - Terrestrial photovoltaic (PV) modules - Design qualification and type approval
- **IEC 61730** - Photovoltaic (PV) module safety qualification
- **IEC 60904** - Photovoltaic devices measurement standards

## License

[Your License Here]

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

- **Issues**: [GitHub Issues](https://github.com/your-org/test-protocols/issues)
- **Email**: support@pv-testing.example.com
- **Documentation**: https://docs.pv-testing.example.com

## Acknowledgments

- IEC Technical Committee for PV standards
- Open-source community for tools and libraries
- PV testing laboratories for feedback and validation

## Roadmap

### Planned Protocols

- [ ] STC-001 - Standard Test Conditions
- [ ] TC-001 - Thermal Cycling
- [ ] HF-001 - Humidity Freeze
- [ ] DH-001 - Damp Heat
- [ ] UV-001 - UV Preconditioning
- [ ] HL-001 - Hot Spot Endurance
- [ ] ML-001 - Mechanical Load

### Planned Features

- [ ] Advanced statistical analysis
- [ ] Machine learning-based anomaly detection
- [ ] Automated report generation (PDF)
- [ ] Multi-language support
- [ ] Cloud deployment
- [ ] Real-time collaboration
- [ ] Mobile app

---

**Version**: 0.1.0
**Last Updated**: 2024-01-15
**Maintainer**: PV Testing Team
