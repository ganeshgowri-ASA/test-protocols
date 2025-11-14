# Test Protocols Framework

Modular PV Testing Protocol Framework for photovoltaic module testing and quality control.

## Overview

This framework provides a comprehensive, modular system for defining, executing, and analyzing test protocols for photovoltaic modules. Each protocol is self-contained with its own JSON definition, implementation, analysis tools, UI components, and documentation.

## Current Protocols

### ML-002: Mechanical Load Dynamic Test (1000Pa Cyclic)

**Status**: ✅ Implemented

A comprehensive mechanical load test protocol implementing IEC 61215-2:2021 MQT 16 with 1000Pa cyclic loading.

**Features**:
- Automated cyclic load application
- Real-time monitoring and data collection
- Comprehensive statistical and linearity analysis
- Interactive Streamlit UI
- Database integration
- Automated QC evaluation and reporting

**Quick Start**:
```bash
cd protocols/ml_002
streamlit run ui/streamlit_app.py
```

See [ML-002 README](protocols/ml_002/README.md) for details.

## Framework Features

### 🎯 Protocol Definition
- JSON-based protocol specification
- JSON Schema validation
- Flexible parameter configuration
- Standards compliance tracking

### ⚙️ Implementation
- Modular Python implementation
- Equipment abstraction layer
- Automated test execution
- Real-time monitoring
- Safety interlocks

### 📊 Data Analysis
- Statistical analysis
- Regression and correlation
- Quality control evaluation
- Automated pass/fail determination

### 🖥️ User Interface
- GenSpark UI components
- Streamlit web application
- Live monitoring dashboards
- Interactive visualizations
- Report generation

### 💾 Data Management
- SQLAlchemy database models
- Comprehensive data storage
- LIMS/QMS integration ready
- Data export (JSON, CSV, PDF)

### ✅ Testing
- Comprehensive unit tests
- Integration tests
- Protocol validation
- >80% code coverage goal

## Installation

```bash
# Clone repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Install dependencies
pip install -r requirements.txt
```

## Repository Structure

```
test-protocols/
├── protocols/               # Test protocol implementations
│   └── ml_002/             # ML-002 Mechanical Load Test
│       ├── protocol.json   # Protocol definition
│       ├── schema.json     # Validation schema
│       ├── implementation.py
│       ├── analyzer.py
│       ├── ui/
│       │   ├── components.py
│       │   └── streamlit_app.py
│       ├── tests/
│       └── README.md
│
├── integrations/           # External system integrations
│   └── database.py         # Database models
│
├── docs/                   # Documentation
│   └── ml-002-design.md
│
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Usage

### Running Tests

```bash
# Run all tests
pytest

# Run specific protocol tests
pytest protocols/ml_002/tests/ -v

# Run with coverage
pytest --cov=protocols protocols/ml_002/tests/
```

### Using ML-002 Protocol

#### Via Python API

```python
from protocols.ml_002 import ML002MechanicalLoadTest, TestSample

# Initialize test
test = ML002MechanicalLoadTest("protocols/ml_002/protocol.json")

# Create sample
sample = TestSample(
    sample_id="MODULE-001",
    module_type="Crystalline Silicon",
    serial_number="SN123456"
)

# Execute test
results = test.execute_test(sample)

# Check results
if results.passed:
    print("✅ TEST PASSED")
else:
    print(f"❌ TEST FAILED: {results.failure_reason}")
```

#### Via Web UI

```bash
streamlit run protocols/ml_002/ui/streamlit_app.py
```

### Database Setup

```python
from sqlalchemy import create_engine
from integrations.database import create_tables

# Create database
engine = create_engine('sqlite:///test_data.db')
create_tables(engine)
```

## Adding New Protocols

To add a new test protocol:

1. **Create Protocol Directory**
   ```bash
   mkdir -p protocols/your_protocol/{ui,tests}
   ```

2. **Define Protocol** (`protocol.json`)
   - Metadata
   - Parameters
   - Data collection
   - Quality control
   - Reporting

3. **Implement Test Logic** (`implementation.py`)
   - Test execution
   - Equipment control
   - Data collection

4. **Create Analyzer** (`analyzer.py`)
   - Data processing
   - Statistical analysis
   - QC evaluation

5. **Build UI** (`ui/components.py`, `ui/streamlit_app.py`)
   - Input forms
   - Live monitoring
   - Results display

6. **Add Tests** (`tests/`)
   - Protocol validation
   - Implementation tests
   - Analysis tests

7. **Write Documentation** (`README.md`, design docs)

## Standards Compliance

The framework supports implementing protocols for:

- **IEC 61215-2:2021**: PV module design qualification
- **IEC 61730**: PV module safety qualification
- **IEC 61853**: PV module performance testing
- **ISO 17025**: Laboratory competence requirements

## Integrations

### Supported Integrations

- **LIMS** (Laboratory Information Management System)
- **QMS** (Quality Management System)
- **Project Management** tools
- **Equipment Management** systems

### Database Support

- SQLite (development)
- PostgreSQL (production)
- MySQL/MariaDB (production)

## Development

### Code Style

Follow PEP 8 guidelines. Use tools:
```bash
black .
flake8 .
mypy .
```

### Testing Requirements

- Unit tests for all new code
- Integration tests for protocols
- Minimum 80% coverage
- All tests must pass before merge

### Documentation

- README for each protocol
- Design documents for complex features
- API documentation
- User guides

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests
5. Update documentation
6. Submit a pull request

## License

MIT License - See LICENSE file for details

## Authors

- ganeshgowri-ASA

## Version History

- **v1.0.0** (2025-11-14): Initial release
  - ML-002 protocol implementation
  - Framework architecture
  - Database integration
  - UI components

## Support

For questions or issues:
- Review protocol-specific README files
- Check documentation in `docs/`
- Review test examples in `tests/`
- Open an issue on GitHub

## Roadmap

### Upcoming Protocols

- **TH-001**: Thermal cycling test
- **HF-001**: Humidity-freeze test
- **UV-001**: UV preconditioning test
- **EL-001**: Electroluminescence imaging
- **IV-001**: I-V curve characterization

### Framework Enhancements

- [ ] Multi-protocol test sequencing
- [ ] Cloud data storage
- [ ] Advanced analytics and ML
- [ ] Mobile app interface
- [ ] Real-time collaboration features
- [ ] Enhanced LIMS/QMS integration

## References

1. IEC 61215-2:2021 - Terrestrial PV modules - Design qualification
2. IEC 61730 - PV module safety qualification
3. ISO 17025 - Testing and calibration laboratories
4. IEC 61853 - PV module performance testing

---

**Built for reliable, standards-compliant PV module testing** 🌞
