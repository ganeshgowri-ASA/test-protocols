# Modular PV Testing Protocol Framework

A comprehensive, JSON-based dynamic testing framework for photovoltaic (PV) modules with automated analysis, quality control, and reporting capabilities.

## Overview

The Test Protocols Framework provides a modular, extensible platform for managing and executing PV module test protocols. Built with Streamlit/GenSpark UI, it offers real-time data visualization, automated QC checks, and seamless integration with LIMS, QMS, and project management systems.

## Features

- ✅ **JSON-based Protocol Definitions**: Flexible, version-controlled test specifications
- 📊 **Interactive UI**: Streamlit-powered interface for data entry and visualization
- 🔬 **Automated Analysis**: Built-in calculations and statistical analysis
- ✅ **Real-time QC**: Automated quality control checks with configurable rules
- 📈 **Interactive Charts**: Plotly-based visualization for degradation curves, I-V curves, and environmental monitoring
- 📄 **Report Generation**: Automated PDF and Excel report creation
- 🔗 **System Integration**: LIMS, QMS, and project management connectors
- 🧪 **Comprehensive Testing**: Full pytest suite with >80% coverage

## Currently Implemented Protocols

### LID-001: Light-Induced Degradation

Complete implementation of IEC 61215-2:2021 compliant LID testing:
- Initial characterization with baseline establishment
- Continuous light exposure monitoring (up to 168 hours)
- Automated degradation analysis and stabilization detection
- Optional recovery testing
- Compliance with IEC 61215-2:2021 and IEC TS 63202-1:2019

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run ui/app.py
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=protocols --cov=analysis --cov-report=html
```

## Project Structure

```
test-protocols/
├── protocols/              # Protocol definitions and implementations
│   ├── schemas/           # JSON schemas for validation
│   ├── definitions/       # Protocol configuration files (JSON)
│   └── implementations/   # Python protocol handlers
├── database/              # SQLAlchemy models and database layer
├── analysis/              # Analysis and calculations
├── ui/                    # Streamlit/GenSpark interface
├── tests/                 # Comprehensive test suite
├── docs/                  # Documentation
└── config/                # Configuration files
```

## Documentation

- [LID-001 Protocol Documentation](docs/protocols/LID-001.md)
- [Installation & Setup Guide](docs/installation.md)
- [User Guide](docs/user_guide.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- Issues: [GitHub Issues](https://github.com/ganeshgowri-ASA/test-protocols/issues)
- Documentation: [Wiki](https://github.com/ganeshgowri-ASA/test-protocols/wiki)
