# PV Testing Protocol Framework

**Modular, JSON-based testing framework for photovoltaic device characterization**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Overview

The PV Testing Protocol Framework is a comprehensive, modular system for defining, executing, and analyzing photovoltaic device testing protocols. Built on JSON-based protocol definitions, it provides:

- 📋 **Standardized Test Protocols** following industry standards (IEC, ASTM)
- 🔬 **Automated Test Execution** with real-time data acquisition and analysis
- 📊 **Interactive Visualization** via Streamlit/GenSpark UI
- ✅ **Quality Control** with automated QC checks and pass/fail criteria
- 📈 **Advanced Analysis** with spectral response, EQE, and performance metrics
- 🗄️ **Database Integration** for test tracking and data management
- 📄 **Report Generation** with customizable templates
- 🔌 **Extensible Architecture** for custom protocols and integrations

## Current Protocols

### SPEC-001: Spectral Response Test
**Standard:** IEC 60904-8

Measures the wavelength-dependent photocurrent response of photovoltaic devices, providing:
- Spectral Response (SR) in A/W
- External Quantum Efficiency (EQE) in %
- Integrated short-circuit current density (Jsc) under AM1.5G spectrum
- Peak response wavelength and efficiency

**Supported Technologies:** c-Si, mc-Si, CdTe, CIGS, Perovskite, GaAs, Organic PV

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from src.database import init_db; init_db()"
```

### Running Your First Test

#### Option 1: Python API

```python
from src.protocols import Protocol, SpectralResponseTest

# Load protocol
protocol = Protocol("protocols/SPEC-001.json")

# Initialize test
test = SpectralResponseTest(protocol=protocol)

# Configure parameters
test_params = {
    "wavelength": {"start": 300, "end": 1200, "step_size": 10},
    "temperature": 25,
    "integration_time": 100,
    "averaging": 3
}

sample_info = {
    "sample_id": "CELL-001",
    "sample_type": "Solar Cell",
    "technology": "c-Si",
    "area": 2.0
}

# Run complete workflow
test_id = test.initialize(test_params, sample_info)
test.run()
test.load_reference_calibration()
test.analyze()
test.run_qc()
test.export_results()
test.complete()

# View results
print(f"Peak EQE: {test.results['peak_eqe']:.1f}%")
print(f"Jsc: {test.results['integrated_jsc']:.2f} mA/cm²")
```

#### Option 2: Streamlit UI

```bash
streamlit run src/ui/app.py
```

Then navigate through the UI tabs:
1. **Test Setup** - Configure test parameters
2. **Run Test** - Execute measurement
3. **Results** - View interactive plots and data
4. **Reports** - Generate and download reports

### Running Examples

```bash
# Basic spectral response test
python examples/basic_spectral_response.py

# Batch testing multiple samples
python examples/batch_testing.py

# Database integration
python examples/database_integration.py
```

## Features

### JSON Protocol Definitions

Protocols are defined in human-readable JSON format:

```json
{
  "protocol_id": "SPEC-001",
  "protocol_name": "Spectral Response Test",
  "standard": "IEC 60904-8",
  "test_parameters": {
    "wavelength": {
      "type": "range",
      "min": 300,
      "max": 1200,
      "default_start": 300,
      "default_end": 1200
    }
  },
  "qc_criteria": {
    "noise_level": {
      "threshold": 0.02,
      "action_on_fail": "warning"
    }
  }
}
```

### Automated Quality Control

Built-in QC checks ensure data quality:
- Noise level monitoring
- Reference detector stability
- Temperature stability
- Data completeness verification
- Parameter range validation

### Interactive Visualizations

Real-time, interactive plots using Plotly:
- Spectral Response vs Wavelength
- External Quantum Efficiency (EQE)
- Raw photocurrent data
- Temperature monitoring

### Database Schema

SQLAlchemy-based models for:
- Protocol definitions
- Sample tracking
- Equipment management
- Test execution records
- Measurement data
- QC results

## Project Structure

```
test-protocols/
├── protocols/              # JSON protocol definitions
│   ├── SPEC-001.json      # Spectral Response Test
│   └── protocol_schema.json
├── src/
│   ├── protocols/         # Protocol execution engine
│   │   ├── base.py       # Base Protocol, ProtocolExecutor classes
│   │   └── spec_001.py   # SPEC-001 implementation
│   ├── database/          # Database models (SQLAlchemy)
│   │   └── models.py
│   └── ui/                # Streamlit UI components
│       ├── app.py        # Main application
│       └── spec_001_ui.py
├── tests/
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
├── docs/                  # Documentation
│   ├── README.md         # Main documentation
│   └── SPEC-001.md       # SPEC-001 protocol guide
├── examples/              # Example scripts
├── database/              # Database files and migrations
└── requirements.txt       # Python dependencies
```

## Documentation

- [Full Documentation](docs/README.md)
- [SPEC-001 Protocol Guide](docs/SPEC-001.md)
- [API Reference](docs/api/)
- [Examples](examples/)

## Running Tests

```bash
# Run all tests
pytest

# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run with coverage
pytest --cov=src --cov-report=html
```

## Technology Stack

- **Python 3.8+**
- **NumPy & SciPy** - Scientific computing
- **Pandas** - Data manipulation
- **Matplotlib & Plotly** - Visualization
- **Streamlit** - Web UI
- **SQLAlchemy** - Database ORM
- **pytest** - Testing framework

## Roadmap

### Upcoming Protocols

- **IV-001**: I-V Curve Measurement (IEC 60904-1)
- **EL-001**: Electroluminescence Imaging
- **PL-001**: Photoluminescence Imaging
- **SUN-001**: Sun Simulator Calibration
- **THERMAL-001**: Thermal Imaging

### Planned Features

- Hardware integration (DAQ, monochromators, source meters)
- Advanced data analysis (machine learning, defect detection)
- Cloud deployment and remote access
- Multi-user collaboration
- LIMS integration (LabVantage, Thermo Scientific)
- Custom report templates
- Real-time monitoring dashboard

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

- **ganeshgowri-ASA** - Initial work

## Acknowledgments

- IEC 60904 series standards
- ASTM photovoltaic testing standards
- Open-source scientific Python community

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact: [Your contact information]

---

**Built for the photovoltaic research and manufacturing community**
