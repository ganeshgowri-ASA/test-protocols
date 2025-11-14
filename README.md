# PV Test Protocol Framework

A comprehensive, modular framework for photovoltaic (PV) module testing protocols with integrated data management, analysis, and reporting capabilities.

## 🌟 Features

- **📋 JSON-Based Protocols**: Flexible, version-controlled test specifications
- **🔬 Automated Execution**: Guided test workflows with built-in quality control
- **💾 Structured Data Storage**: SQLite/PostgreSQL database with full traceability
- **📊 Real-Time Analysis**: Automated calculations and statistical analysis
- **🎨 Interactive UI**: Streamlit-based interface for test execution and visualization
- **🔗 System Integration**: LIMS and QMS integration capabilities
- **✅ Complete Traceability**: From requirements through testing to results

## 📦 Implemented Protocols

### P37-54: H2S-001 - Hydrogen Sulfide Exposure Test
- **Category**: Environmental / Chemical Exposure
- **Purpose**: Evaluate PV module resistance to H2S gas exposure
- **Standards**: IEC 60068-2-42, IEC 61701
- **Status**: ✅ Complete with full implementation

## 🚀 Quick Start

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

### Initialize Database

```python
from database.session import init_db

# Initialize database (creates SQLite in ~/.test_protocols/)
init_db()
```

### Run the UI

```bash
streamlit run ui/app.py
```

### Command-Line Usage

```python
from pathlib import Path
from protocols.environmental.h2s_001 import H2S001Protocol

# Load protocol
protocol_path = Path("protocols/environmental/P37-54_H2S-001.json")
protocol = H2S001Protocol(protocol_path)

# Set module information
protocol.set_module_info({
    "module_id": "TEST-001",
    "manufacturer": "Test Manufacturer",
    "model": "TEST-MODEL-100",
    "technology": "mono-Si",
    "nameplate_power": 400.0,
    "operator": "John Doe",
    "severity_level": 2
})

# Start test
protocol.start_protocol()

# Record measurements
protocol.record_baseline_electrical(
    voc=47.5, isc=10.8, vmp=39.2,
    imp=10.2, pmax=400.0, ff=0.78
)

# ... perform test ...

protocol.record_post_test_electrical(
    voc=47.2, isc=10.6, vmp=38.8,
    imp=10.0, pmax=388.0, ff=0.77
)

# Analyze results
results = protocol.analyze_results()
print(results)

# Generate report
report = protocol.generate_report()
```

## 📁 Project Structure

```
test-protocols/
├── protocols/                  # Protocol definitions and implementations
│   ├── environmental/         # Environmental test protocols
│   │   ├── P37-54_H2S-001.json  # H2S protocol definition
│   │   └── h2s_001.py         # H2S protocol implementation
│   ├── base.py                # Base protocol classes
│   └── loader.py              # Protocol loader utility
├── database/                   # Database layer
│   ├── models.py              # SQLAlchemy models
│   ├── session.py             # Database session management
│   └── migrations/            # SQL migration scripts
├── ui/                         # Streamlit UI components
│   ├── app.py                 # Main application entry
│   ├── pages.py               # UI page components
│   └── components/            # Reusable UI components
├── analysis/                   # Analysis and reporting
│   └── [Future implementation]
├── tests/                      # Test suite
│   ├── unit/                  # Unit tests
│   └── integration/           # Integration tests
├── docs/                       # Documentation
│   ├── protocols/             # Protocol specifications
│   ├── api/                   # API documentation
│   └── TRACEABILITY_MATRIX.md # Complete traceability
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=protocols --cov=database --cov=ui

# Run specific test file
pytest tests/unit/test_h2s_protocol.py

# Run with verbose output
pytest -v
```

## 📊 Database Schema

The framework uses SQLAlchemy ORM with the following main entities:

- **Protocol**: Protocol metadata and definitions
- **Module**: PV module information
- **TestExecution**: Test execution records with measurements
- **Measurement**: Individual measurement records
- **EnvironmentalLog**: Environmental chamber condition logs
- **CalibrationRecord**: Equipment calibration tracking
- **QualityEvent**: QMS event tracking

## 🔌 Integration

### LIMS Integration

```python
# Export data in LIMS-compatible format
data = protocol.export_data(format="json")

# Required fields for LIMS
# - protocol_id
# - module_id
# - test_date
# - pass_fail
# - pmax_degradation
```

### QMS Integration

Quality events are automatically tracked in the `QualityEvent` model:
- Non-conformances
- Calibration due dates
- Safety incidents

## 📖 Documentation

- **Protocol Specification**: [H2S-001 Protocol Specification](docs/protocols/H2S-001_Protocol_Specification.md)
- **Traceability Matrix**: [Complete Traceability](docs/TRACEABILITY_MATRIX.md)
- **API Documentation**: Inline docstrings (use `help()` or IDE documentation)

## 🛡️ Safety

The H2S-001 protocol involves hazardous materials. Always follow safety protocols:
- H2S is toxic - use in ventilated areas only
- Gas detection systems required (10 ppm threshold)
- Emergency eyewash within 10 seconds
- Proper PPE required
- See protocol documentation for complete safety requirements

## 🤝 Contributing

Contributions are welcome! To add a new protocol:

1. Create protocol JSON definition in `protocols/[category]/`
2. Implement protocol class extending `BaseProtocol`
3. Register protocol with `ProtocolLoader`
4. Add comprehensive tests
5. Update documentation and traceability matrix

## 📝 License

MIT License - See LICENSE file for details

## 👥 Authors

- Test Protocol Framework Development Team
- ganeshgowri-ASA

## 🔄 Version History

### Version 1.0.0 (2025-11-14)
- Initial implementation
- P37-54 H2S-001 protocol complete
- Database schema and migrations
- Streamlit UI
- Comprehensive test suite
- Complete documentation and traceability

## 📧 Support

For issues, questions, or contributions, please open an issue on GitHub.

## 🙏 Acknowledgments

- IEC standards committee for test specifications
- PV testing community for best practices
- Open source contributors

---

**Status**: Production Ready
**Version**: 1.0.0
**Last Updated**: 2025-11-14
