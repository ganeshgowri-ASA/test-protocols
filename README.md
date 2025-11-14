# PV Testing Protocol Framework

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)

Modular PV Testing Protocol Framework - JSON-based dynamic templates for Streamlit/GenSpark UI with automated analysis, charting, QC, and report generation. Integrated with LIMS, QMS, and Project Management systems.

## 🎯 Overview

This framework provides a comprehensive, modular system for executing and managing photovoltaic (PV) module testing protocols according to international standards. Built with flexibility and extensibility in mind, it enables testing facilities to:

- Execute standardized test protocols with guided workflows
- Automatically analyze test data and evaluate pass/fail criteria
- Generate comprehensive test reports
- Store and retrieve test data from integrated databases
- Integrate with existing LIMS, QMS, and project management systems

## ✨ Features

- **📋 JSON-Driven Protocols** - Define test procedures, parameters, and acceptance criteria in easy-to-edit JSON files
- **🖥️ Interactive UI** - Streamlit-based web interface for guided test execution
- **📊 Automated Analysis** - Built-in calculations, statistical analysis, and pass/fail evaluation
- **💾 Database Integration** - Comprehensive data storage with SQLite and PostgreSQL support
- **📈 Report Generation** - Automated generation of test reports in JSON and Markdown formats
- **🔬 Extensible Architecture** - Easy to add new test protocols
- **✅ Comprehensive Testing** - Full unit and integration test coverage
- **📚 Well-Documented** - Detailed documentation for protocols and framework usage

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Install dependencies
pip install -r requirements.txt

# Initialize database
python scripts/init_database.py

# Run the HAIL-001 test interface
streamlit run src/ui/hail_001_ui.py
```

### Running Your First Test

1. Navigate to `http://localhost:8501` in your browser
2. Complete the **Test Setup** tab with module information
3. Record **Pre-Test** measurements
4. Execute the **Impact Test** (11 impacts)
5. Record **Post-Test** measurements
6. View **Results** and generate reports

## 📦 Implemented Protocols

### HAIL-001: Hail Impact Test

**Standard**: IEC 61215 MQT 17
**Status**: ✅ Fully Implemented

Tests the ability of PV modules to withstand hailstone impacts according to IEC 61215-2:2021.

**Key Features**:
- 11 impact locations (center, corners, edges, quarters)
- 25mm ice balls at 80 km/h ±2 km/h
- Temperature: -4°C ±2°C
- Automated pass/fail evaluation
- Comprehensive data analysis and reporting

**Pass Criteria**:
- ✅ Power degradation ≤ 5%
- ✅ No major visual defects
- ✅ Insulation resistance ≥ 400 MΩ
- ✅ No intermittent open-circuit during test

[📖 Full Documentation](docs/protocols/HAIL-001.md)

## 📁 Project Structure

```
test-protocols/
├── protocols/              # JSON protocol definitions
│   └── HAIL-001.json      # Hail impact test protocol
├── src/                   # Python source code
│   ├── protocols/         # Protocol loading and handling
│   │   ├── loader.py      # Protocol JSON loader
│   │   ├── base.py        # Base protocol class
│   │   └── hail_001.py    # HAIL-001 implementation
│   ├── analysis/          # Data analysis modules
│   │   ├── calculations.py # Analysis calculations
│   │   ├── reporting.py   # Report generation
│   │   └── database.py    # Database operations
│   └── ui/                # Streamlit UI components
│       └── hail_001_ui.py # HAIL-001 interface
├── db/                    # Database schemas
│   ├── schemas/           # SQL schema definitions
│   │   └── hail_001_schema.sql
│   └── migrations/        # Database migrations
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   │   └── test_hail_001_protocol.py
│   └── integration/      # Integration tests
│       └── test_hail_001_workflow.py
├── docs/                  # Documentation
│   ├── protocols/        # Protocol-specific documentation
│   │   └── HAIL-001.md
│   └── guides/           # User guides
│       └── getting-started.md
└── config/               # Configuration files
```

## 🛠️ Technology Stack

- **Backend**: Python 3.8+
- **UI Framework**: Streamlit
- **Database**: SQLite (development), PostgreSQL (production)
- **Data Analysis**: NumPy, Pandas, Statistics
- **Visualization**: Plotly
- **Testing**: unittest, pytest
- **Documentation**: Markdown

## 📊 Usage Example

### Python API

```python
from src.protocols.loader import ProtocolLoader
from src.protocols.hail_001 import HAIL001Protocol
from src.analysis.database import TestDatabase

# Load protocol
loader = ProtocolLoader("protocols")
protocol_data = loader.load_protocol("HAIL-001")
protocol = HAIL001Protocol(protocol_data)

# Prepare test data
test_data = {
    'pre_test_data': {
        'Pmax_initial': 300.0,
        'insulation_resistance_initial': 500.0
    },
    'test_execution_data': {
        'impacts': [...]  # 11 impact records
    },
    'post_test_data': {
        'Pmax_final': 295.0,
        'insulation_resistance_final': 490.0,
        'visual_defects': {...}
    }
}

# Validate data
is_valid, errors = protocol.validate_test_data(test_data)

# Analyze results
analysis_results = protocol.analyze_results(test_data)

# Evaluate pass/fail
pass_fail_results = protocol.evaluate_pass_fail(analysis_results)

print(f"Test Result: {pass_fail_results['overall_result']}")
# Output: Test Result: PASS
```

## 🧪 Testing

Run the complete test suite:

```bash
# All tests
python -m pytest tests/

# Unit tests only
python -m pytest tests/unit/

# Integration tests only
python -m pytest tests/integration/

# With coverage
python -m pytest --cov=src tests/
```

## 📖 Documentation

- [Getting Started Guide](docs/guides/getting-started.md)
- [HAIL-001 Protocol Documentation](docs/protocols/HAIL-001.md)
- [API Reference](docs/api/)
- [Contributing Guidelines](CONTRIBUTING.md)

## 🔧 Creating New Protocols

The framework is designed to be easily extensible. To add a new protocol:

1. **Create JSON definition** in `protocols/YOUR-PROTOCOL.json`
2. **Implement protocol class** in `src/protocols/your_protocol.py`
3. **Create database schema** in `db/schemas/your_protocol_schema.sql`
4. **Build UI component** in `src/ui/your_protocol_ui.py`
5. **Write tests** in `tests/unit/` and `tests/integration/`
6. **Document** in `docs/protocols/YOUR-PROTOCOL.md`

See [Getting Started Guide](docs/guides/getting-started.md) for detailed instructions.

## 🤝 Integration

### LIMS Integration

The framework supports integration with Laboratory Information Management Systems (LIMS):

- Export test data in standardized JSON format
- Import module information from LIMS
- Update LIMS with test results via API

### QMS Integration

Quality Management System integration capabilities:

- Track equipment calibration
- Document deviations and non-conformances
- Generate audit trails

### Project Management

- Link tests to specific projects
- Track testing progress
- Generate project-level reports

## 🎯 Roadmap

### Planned Protocols

- [ ] **DH-001**: Damp Heat Test (IEC 61215 MQT 13)
- [ ] **TC-001**: Thermal Cycling Test (IEC 61215 MQT 12)
- [ ] **HF-001**: Humidity Freeze Test (IEC 61215 MQT 14)
- [ ] **ML-001**: Mechanical Load Test (IEC 61215 MQT 16)
- [ ] **UV-001**: UV Preconditioning Test (IEC 61215 MQT 10)

### Framework Enhancements

- [ ] Real-time data acquisition from test equipment
- [ ] Advanced data visualization and trending
- [ ] Multi-user support with role-based access control
- [ ] Cloud deployment options
- [ ] Mobile app for test execution
- [ ] AI-powered anomaly detection

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Contributors

- Claude - Initial framework implementation and HAIL-001 protocol

## 🙏 Acknowledgments

- IEC 61215 standards committee
- PV testing community
- Open source contributors

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/ganeshgowri-ASA/test-protocols/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ganeshgowri-ASA/test-protocols/discussions)
- **Email**: support@example.com

## 🔬 Research & Development

This framework was developed to support photovoltaic module testing and quality assurance. It is actively maintained and welcomes contributions from the PV testing community.

### Citation

If you use this framework in your research, please cite:

```bibtex
@software{pv_testing_framework,
  title = {PV Testing Protocol Framework},
  author = {Test Protocols Team},
  year = {2025},
  url = {https://github.com/ganeshgowri-ASA/test-protocols}
}
```

---

**Made with ❤️ for the PV testing community**
