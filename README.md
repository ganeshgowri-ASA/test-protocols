# Test Protocols Framework

**Modular PV Testing Protocol Framework** - JSON-based dynamic templates for Streamlit/GenSpark UI with automated analysis, charting, QC, and report generation. Integrated with LIMS, QMS, and Project Management systems.

## 🎯 Overview

This framework provides a comprehensive, standards-compliant testing infrastructure for photovoltaic (PV) modules and components. Built with modularity, traceability, and real-time monitoring at its core.

## ✨ Features

- 📋 **JSON-Based Protocol Templates**: Dynamic, configurable test definitions
- 🖥️ **GenSpark UI**: Interactive Streamlit dashboards with real-time monitoring
- 🔬 **Advanced Instrumentation**: Real-time particle tracking and environmental monitoring
- 💾 **Comprehensive Database**: Full traceability with time-series data storage
- 📊 **Automated Analysis**: Built-in acceptance criteria evaluation
- 🔄 **System Integration**: LIMS, QMS, and project management connectivity
- ✅ **Standards Compliance**: IEC, ASTM, ISO standard implementations
- 🧪 **Extensive Testing**: Unit, integration, and workflow tests

## 📦 Implemented Protocols

### SAND-001: Sand and Dust Resistance Test

**Standard**: IEC 60068-2-68

Complete implementation for sand and dust resistance testing including:
- Real-time particle tracking with multi-point spatial monitoring
- Environmental condition monitoring (temperature, humidity, airflow)
- Automated dust ingress severity assessment
- Electrical performance evaluation
- Physical integrity checks
- Surface degradation analysis

[📖 Full Documentation](docs/SAND-001-README.md) | [🔧 API Reference](docs/API_REFERENCE.md)

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Install dependencies
pip install -r requirements.txt

# Set up database (optional)
mysql -u username -p database_name < database/schemas/sand_dust_test_schema.sql
```

### Basic Usage

```python
from protocols.sand_dust_test import (
    SandDustResistanceTest,
    TestConfiguration,
    SpecimenData,
    create_test_from_protocol
)

# Load test from protocol
specimen = SpecimenData(
    specimen_id="PV-001",
    specimen_type="PV Module",
    manufacturer="Example Corp",
    model="EX-300W",
    serial_number="SN123",
    initial_weight=5000.0,
    initial_dimensions=(1000.0, 600.0, 40.0),
    initial_surface_roughness=0.5
)

test = create_test_from_protocol(
    "TEST-001",
    "protocols/SAND-001.json",
    specimen
)

# Run test
test.start_test()
test.initialize_particle_tracking(measurement_points)
# ... test execution ...
test.complete_test()
test.export_results('./results')
```

### Launch UI

```bash
streamlit run ui/components/sand_dust_monitor.py
```

## 📁 Project Structure

```
test-protocols/
├── protocols/              # Protocol JSON definitions
│   └── SAND-001.json
├── src/
│   └── python/
│       └── protocols/      # Python implementations
│           ├── __init__.py
│           └── sand_dust_test.py
├── ui/
│   └── components/         # Streamlit UI components
│       └── sand_dust_monitor.py
├── database/
│   └── schemas/           # Database schemas
│       └── sand_dust_test_schema.sql
├── tests/                 # Test suite
│   ├── __init__.py
│   └── test_sand_dust_protocol.py
├── docs/                  # Documentation
│   ├── SAND-001-README.md
│   └── API_REFERENCE.md
├── requirements.txt       # Python dependencies
├── LICENSE
└── README.md             # This file
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
cd tests
python test_sand_dust_protocol.py
```

Or with pytest:

```bash
pytest tests/ -v --cov=src/python/protocols
```

### Test Coverage

- ✅ 45+ unit tests
- ✅ Integration tests
- ✅ End-to-end workflow tests
- ✅ Data validation tests
- ✅ Acceptance criteria tests

## 📊 Database Schema

Comprehensive schema supporting:

- Test session management
- Specimen tracking
- Real-time environmental monitoring (time-series)
- High-frequency particle tracking
- Electrical measurements
- Equipment calibration records
- Image and document storage
- Deviation and observation logging
- Acceptance criteria results
- Complete audit trail

[View Schema](database/schemas/sand_dust_test_schema.sql)

## 🔗 System Integration

### LIMS Integration

```python
from lims_connector import LIMSClient

lims = LIMSClient(api_url="https://lims.example.com/api")
lims.submit_test_results(
    protocol="SAND-001",
    specimen_id=test.specimen.specimen_id,
    results=test.generate_report_data()
)
```

### QMS Integration

```python
from qms_connector import QMSClient

qms = QMSClient()
qms.create_test_record(
    test_id=test.test_id,
    protocol="SAND-001",
    result="PASS" if test.test_passed else "FAIL",
    traceability_data=test.results
)
```

## 📝 Protocol Development

### Creating New Protocols

1. Define protocol JSON in `protocols/`
2. Implement Python class in `src/python/protocols/`
3. Create UI component in `ui/components/`
4. Define database schema in `database/schemas/`
5. Write tests in `tests/`
6. Document in `docs/`

### Protocol Template Structure

```json
{
  "protocol_id": "PROTO-XXX",
  "protocol_name": "Protocol Name",
  "version": "1.0.0",
  "category": "Environmental",
  "standard": {...},
  "test_parameters": {...},
  "measurement_sequence": [...],
  "acceptance_criteria": {...},
  "data_collection": {...},
  "reporting": {...}
}
```

## 🔐 Quality and Traceability

### Data Integrity

- Immutable test records
- Complete audit trail
- Timestamp on all data points
- Equipment calibration tracking
- Operator identification

### Compliance Features

- Standards-based protocols
- Calibration certificate management
- Measurement uncertainty tracking
- Deviation documentation
- Regulatory report generation

## 📚 Documentation

- **User Guides**: Protocol-specific instructions
- **API Reference**: Complete class and method documentation
- **Database Schema**: Table structures and relationships
- **Integration Guides**: LIMS, QMS, PM system connectivity
- **Best Practices**: Testing and quality guidelines

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Implement with tests
4. Document thoroughly
5. Submit pull request

## 📄 License

See [LICENSE](LICENSE) file for details.

## 🎓 Standards Compliance

Current implementations:

- ✅ IEC 60068-2-68: Sand and dust resistance

Planned:

- 🔄 IEC 61215: Terrestrial PV modules design qualification
- 🔄 IEC 61646: Thin-film PV modules design qualification
- 🔄 IEC 62716: Ammonia corrosion testing
- 🔄 ASTM E1171: Solar cell temperature measurement

## 📞 Support

For questions, issues, or feature requests:

- 📧 Open an issue on GitHub
- 📖 Check documentation in `/docs`
- 🔍 Review test examples in `/tests`

## 🗺️ Roadmap

### Version 1.x

- ✅ SAND-001 implementation
- 🔄 SALT-001: Salt mist testing
- 🔄 HUMIDITY-001: Damp heat testing
- 🔄 THERMAL-CYCLE-001: Temperature cycling

### Version 2.x

- Advanced ML-based anomaly detection
- Predictive maintenance integration
- Multi-site test coordination
- Enhanced visualization and analytics

## 🙏 Acknowledgments

Built with:

- Python 3.7+
- Streamlit
- Plotly
- NumPy & Pandas
- SQLAlchemy

Standards references:

- IEC (International Electrotechnical Commission)
- ASTM International
- ISO (International Organization for Standardization)

---

**Version**: 1.0.0
**Last Updated**: 2025-11-14
**Maintained by**: Test Protocols Development Team
