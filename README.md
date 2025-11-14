# Test Protocols Framework

**Modular PV Testing Protocol Framework** - JSON-based dynamic templates for Streamlit/GenSpark UI with automated analysis, charting, QC, and report generation. Integrated with LIMS, QMS, and Project Management systems.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

## Overview

A comprehensive framework for managing and executing photovoltaic (PV) module testing protocols. Features include:

- 🧪 **Modular Protocol System**: Easy-to-extend protocol architecture
- 📊 **Real-time Monitoring**: Live test data visualization
- 🎯 **Automated Analysis**: Built-in data analysis and QC checks
- 📄 **Report Generation**: Automated test report generation
- 💾 **Database Persistence**: SQLAlchemy-based data storage
- 🖥️ **Modern UI**: Streamlit-based GenSpark interface
- 🔌 **Integration Ready**: LIMS/QMS integration support

## Implemented Protocols

### Mechanical Testing
- ✅ **SNOW-001**: Snow Load Test (IEC 61215-1:2016)

### Coming Soon
- **WIND-001**: Wind Load Test
- **HF-001**: Humidity-Freeze Test
- **TC-001**: Thermal Cycling Test
- **IV-001**: IV Curve Characterization

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=protocols --cov-report=html

# Run specific test markers
pytest -m unit
pytest -m snow_load
```

### Launching the UI

```bash
# Start the Streamlit UI
streamlit run ui/streamlit_app.py
```

## Project Structure

```
test-protocols/
├── protocols/              # Protocol implementations
│   ├── base/              # Base classes and validators
│   ├── mechanical/        # Mechanical test protocols
│   │   └── snow_load/    # SNOW-001 implementation
│   ├── environmental/     # Environmental protocols
│   └── electrical/        # Electrical protocols
├── schemas/               # JSON schema definitions
├── database/              # Database models and migrations
├── ui/                    # Streamlit UI components
├── analysis/              # Data analysis utilities
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── docs/                  # Documentation
│   └── protocols/        # Protocol-specific docs
└── config/               # Configuration files
```

## Usage Example

### Python API

```python
from protocols.mechanical.snow_load import (
    SnowLoadTestProtocol,
    SnowLoadTestConfig,
    ModuleSpecs
)

# Define module specifications
module_specs = ModuleSpecs(
    module_id="TEST-001",
    length_mm=1650,
    width_mm=992,
    thickness_mm=35,
    mass_kg=18.5,
    frame_type="aluminum"
)

# Configure test parameters
test_config = SnowLoadTestConfig(
    snow_load_pa=2400,  # 2400 Pa ≈ 245 kg/m²
    hold_duration_hours=1.0,
    cycles=1,
    max_deflection_mm=50.0,
    max_permanent_deflection_mm=5.0
)

# Execute test
protocol = SnowLoadTestProtocol(test_config, module_specs)
result = protocol.execute()

# Generate report
report = protocol.get_report_data()
print(f"Test Result: {'PASS' if result else 'FAIL'}")
```

## Documentation

- [SNOW-001 Protocol Documentation](docs/protocols/SNOW-001.md)
- [API Reference](docs/api-reference.md) *(Coming Soon)*
- [Integration Guide](docs/integration-guide.md) *(Coming Soon)*

## Development

### Running Tests

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Specific protocol tests
pytest tests/unit/test_protocols/test_snow_load.py -v
```

### Code Quality

```bash
# Format code
black protocols/ tests/

# Sort imports
isort protocols/ tests/

# Type checking
mypy protocols/

# Linting
flake8 protocols/ tests/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- IEC 61215-1:2016 - Terrestrial photovoltaic (PV) modules - Design qualification and type approval
- IEC 61730 - Photovoltaic (PV) module safety qualification

## Contact

Project Link: [https://github.com/ganeshgowri-ASA/test-protocols](https://github.com/ganeshgowri-ASA/test-protocols)
