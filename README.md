# PV Test Protocols

⚡ **Modular PV Testing Protocol Framework**

JSON-based dynamic templates for Streamlit/GenSpark UI with automated analysis, charting, QC, and report generation. Integrated with LIMS, QMS, and Project Management systems.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

The PV Test Protocol System provides a comprehensive framework for executing, analyzing, and reporting photovoltaic module test protocols. Built with flexibility and extensibility in mind, the system enables labs to:

- **Define protocols in JSON** - Schema-driven, version-controlled protocol definitions
- **Auto-generate UI** - Dynamic Streamlit interface from protocol specifications
- **Automated analysis** - Built-in statistical analysis and pass/fail evaluation
- **Quality assurance** - Comprehensive QC checks with configurable rules
- **Multi-format reports** - PDF, HTML, Excel, and JSON output
- **Enterprise integration** - Ready for LIMS, QMS, and project management systems

## Features

### 🎯 Protocol Management
- JSON-based protocol definitions with validation
- Protocol versioning and change tracking
- Protocol registry with category organization
- Dynamic parameter validation

### 📊 Data Analysis
- Automated statistical analysis
- Degradation trend calculation
- I-V curve analysis
- Retention and efficiency calculations
- Time-series data processing

### ✅ Quality Control
- Measurement repeatability checks
- Environmental stability monitoring
- Data completeness validation
- Outlier detection
- Configurable QC rules per protocol

### 📈 Visualization
- Interactive Plotly charts
- I-V curve comparisons
- Degradation trends over time
- Environmental condition monitoring
- Real-time test status dashboards

### 📄 Reporting
- Executive summary reports
- Detailed technical reports
- Data export (Excel, CSV, JSON)
- HTML and PDF generation
- Customizable report templates

### 🗄️ Data Management
- PostgreSQL database with SQLAlchemy ORM
- Complete test execution history
- Measurement data with timestamps
- Test results and QC records
- Specimen tracking

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the UI

```bash
streamlit run ui/streamlit_app.py
```

### Run Tests

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

## Implemented Protocols

### ✅ UVID-001: UV-Induced Degradation

**Status:** Production Ready
**Category:** Degradation
**Standard:** IEC 61215-2:2021 MQT 10

Evaluates PV module degradation under accelerated UV exposure conditions.

**Key Specifications:**
- UV Irradiance: 1.0 W/m² (280-400nm)
- Temperature: 60°C ±2°C
- Duration: 1000 hours
- Pass Criteria: ≥95% Pmax retention

**Implementation:**
- ✅ JSON protocol definition
- ✅ Python analysis engine
- ✅ GenSpark/Streamlit UI
- ✅ Database models
- ✅ Comprehensive tests (unit + integration)
- ✅ Complete documentation

📖 [View Full Protocol Documentation](docs/UVID-001_PROTOCOL.md)

## Project Structure

```
test-protocols/
├── protocols/              # Protocol definitions
│   ├── base/              # Base protocol classes
│   ├── degradation/       # UVID-001 and related protocols
│   │   ├── uvid_001.json # UV degradation protocol definition
│   │   └── __init__.py
│   └── __init__.py
├── database/              # Database models and schemas
│   ├── models.py         # SQLAlchemy ORM models
│   └── __init__.py
├── analysis/              # Data analysis modules
│   ├── analyzer.py       # Test result analyzer
│   ├── qc_checker.py     # Quality control checker
│   ├── degradation/      # Degradation-specific analysis
│   └── qc/              # QC modules
├── ui/                    # User interface
│   ├── streamlit_app.py  # Main Streamlit application
│   ├── pages/           # UI pages
│   │   └── degradation_viz.py
│   └── components/      # Reusable components
├── reports/               # Report generation
│   ├── generator.py      # Report generator
│   └── templates/       # HTML templates
├── tests/                 # Test suite
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests
│   ├── fixtures/        # Test fixtures
│   └── conftest.py      # Pytest configuration
├── docs/                  # Documentation
│   ├── README.md         # System documentation
│   └── UVID-001_PROTOCOL.md
├── config/               # Configuration files
├── scripts/              # Utility scripts
├── requirements.txt      # Python dependencies
├── pyproject.toml       # Project configuration
└── README.md            # This file
```

## Usage Examples

### Load and Validate Protocol

```python
from protocols.degradation import load_uvid_001

# Load protocol
protocol = load_uvid_001()

# Validate test parameters
params = {
    'uv_irradiance': 1.0,
    'chamber_temperature': 60.0,
    'exposure_duration': 1000
}
is_valid, errors = protocol.validate_parameters(params)
```

### Analyze Test Results

```python
from analysis.analyzer import TestAnalyzer

analyzer = TestAnalyzer(protocol)

# Evaluate results
measurements_by_point = {
    'initial': {'pmax': 250.5, 'voc': 38.2, 'isc': 8.95},
    'final': {'pmax': 241.2, 'voc': 37.8, 'isc': 8.78}
}

results = analyzer.evaluate_test_results(measurements_by_point)
print(f"Pass: {results['pass_fail']['overall_pass']}")
```

### Run QC Checks

```python
from analysis.qc_checker import QCChecker

qc_checker = QCChecker(protocol.definition)

# Check measurement repeatability
measurements = [250.1, 250.3, 250.2, 250.4]
result = qc_checker.check_measurement_repeatability(measurements, 'pmax')
print(f"QC Pass: {result['pass']}, CV: {result['cv']:.4f}")
```

### Generate Report

```python
from reports.generator import ReportGenerator

generator = ReportGenerator(protocol.definition)

# Generate HTML report
html = generator.generate_summary_report(test_execution, results)

# Save report
generator.save_report(html, 'report.html', format='html')

# Export data to JSON
generator.export_to_json(test_execution, results, measurements, 'data.json')
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/unit/test_protocol.py -v
```

### Code Quality

```bash
# Format code
black .

# Sort imports
isort .

# Lint
flake8 .

# Type checking
mypy .
```

## Documentation

- [System Documentation](docs/README.md) - Complete system documentation
- [UVID-001 Protocol](docs/UVID-001_PROTOCOL.md) - UV degradation protocol specification
- [API Reference](docs/README.md#api-reference) - Python API documentation

## Technology Stack

- **Backend:** Python 3.9+
- **Database:** PostgreSQL with SQLAlchemy ORM
- **UI:** Streamlit / GenSpark
- **Visualization:** Plotly
- **Testing:** Pytest
- **Data Processing:** NumPy, Pandas

## Roadmap

### Implemented ✅
- [x] UVID-001 UV Degradation Protocol
- [x] Core protocol framework
- [x] Analysis engine
- [x] QC checker
- [x] Report generation
- [x] Streamlit UI
- [x] Database models
- [x] Comprehensive tests
- [x] Documentation

### Planned 🚀
- [ ] Additional degradation protocols (HTID-001, TCID-001, HMID-001)
- [ ] LIMS integration implementation
- [ ] QMS document control integration
- [ ] PDF report generation (WeasyPrint)
- [ ] Real-time data acquisition
- [ ] Advanced charting and analytics
- [ ] Multi-language support
- [ ] Docker deployment

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

**PV Testing Laboratory**
- GitHub: [@ganeshgowri-ASA](https://github.com/ganeshgowri-ASA)

## Acknowledgments

- IEC 61215-2:2021 for test method standards
- Streamlit for the UI framework
- SQLAlchemy for ORM capabilities

## Support

- **Documentation:** [docs/](docs/)
- **Issues:** [GitHub Issues](https://github.com/ganeshgowri-ASA/test-protocols/issues)

---

**Version:** 1.0.0
**Last Updated:** 2025-11-14
