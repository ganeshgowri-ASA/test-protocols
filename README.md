# Test Protocols Framework

**Modular PV Testing Protocol Framework** - JSON-based dynamic templates for Streamlit/GenSpark UI with automated analysis, charting, QC, and report generation. Integrated with LIMS, QMS, and Project Management systems.

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()

## Overview

The Test Protocols Framework is a comprehensive, modular system for managing and executing standardized test protocols for photovoltaic (PV) module components and materials. The framework provides:

- **JSON-based Protocol Definitions** - Flexible, version-controlled test specifications
- **Python Implementation Layer** - Robust protocol execution and data analysis
- **Web-based UI (GenSpark)** - Streamlit-powered interface for test execution and monitoring
- **Database Integration** - Structured data storage with SQLite/PostgreSQL support
- **Automated QC** - Built-in quality control checks and validation
- **Report Generation** - Multi-format reports (PDF, Excel, JSON, HTML)
- **External System Integration** - LIMS, QMS, and project management connectivity

## Current Protocols

### YELLOW-001: EVA Yellowing Assessment

**Status:** ✅ Active | **Version:** 1.0.0 | **Category:** Degradation

Accelerated aging test for EVA (Ethylene-Vinyl Acetate) encapsulant yellowing assessment.

- **Test Duration:** 1000 hours
- **Conditions:** 85°C, 60% RH, 100 mW/cm² UV-A
- **Measurements:** Yellowness Index (YI), Color Shift (ΔE), Light Transmittance
- **Pass Criteria:** YI ≤15, ΔE ≤8, Transmittance ≥75%

📚 [Full Documentation](docs/protocols/YELLOW-001.md)

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

# Or install in development mode
pip install -e .
```

### Running the Web UI

```bash
# Start the Streamlit app
streamlit run app.py
```

The GenSpark UI will open in your browser at `http://localhost:8501`

### Running Tests Programmatically

```python
from protocols.yellow.yellow_001 import Yellow001Protocol, Sample

# Create protocol instance
protocol = Yellow001Protocol()

# Define samples
samples = [
    Sample(sample_id='EVA_001', material_type='EVA',
           dimensions={'length_mm': 100, 'width_mm': 100, 'thickness_mm': 3})
]

# Execute test
results = protocol.execute_test(samples)

# Analyze results
analysis = protocol.analyze_results()

# Check status
print(f"Overall Status: {analysis['overall_status']}")
```

## Architecture

```
test-protocols/
├── protocols/              # JSON protocol definitions
│   └── yellow/
│       └── YELLOW-001.json
├── src/                    # Python source code
│   ├── core/               # Core framework
│   ├── models/             # Data models
│   ├── protocols/          # Protocol implementations
│   │   └── yellow/
│   │       ├── yellow_001.py
│   │       ├── analyzer.py
│   │       └── qc_checks.py
│   ├── ui/                 # Streamlit UI components
│   ├── database/           # Database layer
│   └── utils/              # Utilities
├── tests/                  # Test suite
├── docs/                   # Documentation
├── app.py                  # Main Streamlit app
└── requirements.txt
```

## Features

### ✨ Protocol Management

- **JSON-based Definitions** - Easy to create, version, and maintain
- **Protocol Loader** - Automatic discovery and validation
- **Version Control** - Track protocol revisions and approvals

### 🧪 Test Execution

- **Automated Workflows** - Step-by-step test execution
- **Real-time Monitoring** - Track progress and environmental conditions
- **Multi-sample Support** - Test multiple samples in parallel
- **Data Validation** - Input validation and error checking

### 📊 Data Analysis

- **Statistical Analysis** - Mean, std dev, confidence intervals
- **Trend Analysis** - Exponential curve fitting and kinetic modeling
- **Comparative Analysis** - Sample-to-sample and batch comparisons
- **Extrapolation** - Predict long-term behavior

### ✅ Quality Control

- **Automated QC Checks** - Baseline, calibration, reference samples
- **Environmental Monitoring** - Continuous tracking of test conditions
- **Equipment Validation** - Calibration verification
- **Audit Trail** - Complete test history and traceability

### 📈 Visualization

- **Time-series Charts** - Track parameter changes over time
- **Comparative Plots** - Sample and batch comparisons
- **Color Trajectories** - L*a*b* color space visualization
- **Statistical Dashboards** - Summary metrics and KPIs

### 📄 Reporting

- **Multi-format Export** - PDF, Excel, JSON, HTML
- **Automated Generation** - One-click report creation
- **Customizable Templates** - Adapt reports to requirements
- **Data Archival** - Long-term storage and retrieval

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test module
pytest tests/protocols/yellow/test_yellow_001.py

# Run with verbose output
pytest -v
```

## Documentation

- **Protocol Documentation:** [docs/protocols/](docs/protocols/)
- **API Reference:** (Coming soon)
- **User Guide:** (Coming soon)
- **Developer Guide:** (Coming soon)

## Database Schema

The framework uses SQLite by default (easily adaptable to PostgreSQL/MySQL):

- **protocols** - Protocol definitions
- **test_sessions** - Test execution instances
- **samples** - Sample/specimen information
- **measurements** - Measurement data points
- **qc_checks** - Quality control results
- **analysis_results** - Analysis outputs
- **reports** - Generated reports

See [src/database/schema.py](src/database/schema.py) for complete schema.

## Integration

### LIMS Integration

Connect to Laboratory Information Management Systems:

```python
# Example LIMS integration
from integrations.lims import LIMSConnector

lims = LIMSConnector()
lims.upload_test_results(test_session_id, results)
```

### QMS Integration

Link to Quality Management Systems for compliance:

```python
# Example QMS integration
from integrations.qms import QMSConnector

qms = QMSConnector()
qms.create_qc_document(test_session_id, report_data)
```

## Adding New Protocols

### 1. Create Protocol JSON

Create a new JSON file in `protocols/<category>/<PROTOCOL-ID>.json`:

```json
{
  "protocol_id": "NEW-001",
  "protocol_name": "New Test Protocol",
  "version": "1.0.0",
  "test_parameters": { ... },
  "measurements": [ ... ],
  "quality_controls": [ ... ],
  "pass_fail_criteria": [ ... ]
}
```

### 2. Implement Protocol Class

Create Python implementation in `src/protocols/<category>/<protocol_id>.py`:

```python
from core.base_protocol import BaseProtocol

class New001Protocol(BaseProtocol):
    def validate_inputs(self, inputs):
        # Implement validation
        pass

    def execute_test(self, samples):
        # Implement test execution
        pass

    def analyze_results(self):
        # Implement analysis
        pass
```

### 3. Add Tests

Create tests in `tests/protocols/<category>/test_<protocol_id>.py`

### 4. Document Protocol

Create documentation in `docs/protocols/<PROTOCOL-ID>.md`

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions, issues, or feature requests:

- **GitHub Issues:** [github.com/ganeshgowri-ASA/test-protocols/issues](https://github.com/ganeshgowri-ASA/test-protocols/issues)
- **Email:** protocols@example.com

## Acknowledgments

- Based on IEC 61215 and IEC 61730 standards
- ASTM E313 for yellowness index calculations
- CIE standards for color measurement

---

**Version:** 1.0.0 | **Last Updated:** 2025-11-14 | **Status:** Active Development
