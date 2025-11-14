# Test Protocols Framework

Modular PV Testing Protocol Framework - JSON-based dynamic templates for Streamlit/GenSpark UI with automated analysis, charting, QC, and report generation. Integrated with LIMS, QMS, and Project Management systems.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Overview

A comprehensive, modular framework for conducting PV (photovoltaic) module testing protocols. The framework provides JSON-based protocol definitions, automated data collection, analysis, visualization, and reporting capabilities.

### Key Features

- 📋 **JSON-based Protocol Definitions** - Flexible, version-controlled test specifications
- 🖥️ **Interactive Streamlit UI** - User-friendly web interface for test execution
- 📊 **Automated Analysis** - Real-time calculations and pass/fail determination
- 📈 **Rich Visualizations** - Plotly-powered charts and graphs
- 🗄️ **Database Integration** - SQLAlchemy ORM with SQLite/PostgreSQL support
- 🔗 **System Integration** - LIMS, QMS, and Project Management system hooks
- 🧪 **Comprehensive Testing** - Full test coverage with pytest
- 📚 **Complete Documentation** - API docs, user guides, and protocol specs

## Implemented Protocols

### WIND-001: Wind Load Test

**Status:** ✅ Complete
**Category:** Mechanical
**Version:** 1.0.0

Wind load testing for PV modules according to IEC 61215-2:2021, IEC 61730-2, and UL 1703 standards.

**Features:**
- Pre-test and post-test electrical performance measurements
- Cyclic load testing with deflection monitoring
- Automated pass/fail determination
- Comprehensive reporting with visualizations

[📖 Full Protocol Documentation](docs/WIND-001.md)

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Initialize database
python -m src.db.database
```

[📖 Detailed Installation Guide](docs/INSTALLATION.md)

### Run the Streamlit UI

```bash
streamlit run src/ui/wind_001_ui.py
```

Open your browser to `http://localhost:8501` to access the interactive UI.

### Run Example Protocol

```bash
python -m src.protocols.wind_001
```

### Run Tests

```bash
pytest tests/
```

## Project Structure

```
test-protocols/
├── protocols/              # Protocol definitions
│   └── mechanical/
│       └── wind-001/
│           ├── schema.json    # JSON schema
│           └── config.json    # Protocol configuration
├── src/
│   ├── protocols/         # Protocol implementations
│   │   └── wind_001.py
│   ├── ui/                # Streamlit UI components
│   │   └── wind_001_ui.py
│   └── db/                # Database models
│       ├── models.py
│       ├── database.py
│       └── migrations/
├── tests/                 # Test suite
│   ├── test_wind_001.py
│   └── test_database.py
├── docs/                  # Documentation
│   ├── WIND-001.md
│   ├── API.md
│   └── INSTALLATION.md
├── requirements.txt       # Dependencies
├── setup.py              # Package setup
└── README.md
```

## Usage Examples

### Python API

```python
from protocols.wind_001 import WindLoadTest, ElectricalPerformance, CycleMeasurement

# Initialize protocol
protocol = WindLoadTest()

# Initialize test
protocol.initialize_test(
    test_metadata={
        "test_id": "WIND-001-2024-001",
        "operator": "John Doe",
        "standard": "IEC 61215-2:2021"
    },
    sample_info={
        "sample_id": "PV-MOD-12345",
        "manufacturer": "SolarTech Inc.",
        "model": "ST-400-M",
        "rated_power": 400
    },
    test_parameters={
        "load_type": "cyclic",
        "pressure": 2400,
        "duration": 60,
        "cycles": 3
    }
)

# Record pre-test measurements
protocol.record_pre_test_measurements(
    visual_inspection="No defects observed",
    electrical_performance=ElectricalPerformance(
        voc=48.5, isc=10.2, vmp=40.0, imp=10.0, pmax=400.0
    ),
    insulation_resistance=500.0
)

# Record cycle measurements
for cycle in range(1, 4):
    measurement = CycleMeasurement(
        cycle_number=cycle,
        timestamp=datetime.now().isoformat(),
        actual_pressure=2400.0,
        deflection_center=15.5,
        deflection_edges=[10.2, 11.5, 10.8, 11.0]
    )
    protocol.record_cycle_measurement(measurement)

# Record post-test measurements
protocol.record_post_test_measurements(
    visual_inspection="No defects after testing",
    electrical_performance=ElectricalPerformance(
        voc=48.3, isc=10.1, vmp=39.8, imp=9.9, pmax=394.0
    ),
    insulation_resistance=480.0,
    defects_observed=["none"]
)

# Calculate results
results = protocol.calculate_results()
print(f"Test Status: {results['test_status']}")
print(f"Power Degradation: {results['power_degradation']}%")

# Generate report
report = protocol.generate_summary_report()
print(report)

# Export data
protocol.export_test_data(Path("test_results.json"))
```

[📖 Full API Documentation](docs/API.md)

## Documentation

- [WIND-001 Protocol Specification](docs/WIND-001.md) - Complete test protocol documentation
- [API Reference](docs/API.md) - Python API and usage examples
- [Installation Guide](docs/INSTALLATION.md) - Setup and configuration
- [Documentation Index](docs/README.md) - All documentation

## Testing

The framework includes comprehensive test coverage:

```bash
# Run all tests
pytest tests/

# Run with coverage report
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_wind_001.py -v
```

### Test Coverage

- ✅ Protocol implementation (wind_001.py)
- ✅ Database models and operations
- ✅ Data validation
- ✅ Calculations and analysis
- ✅ Pass/fail determination

## Database

### SQLite (Default)

```python
from db.database import init_database

# Initialize SQLite database (creates test_protocols.db)
init_database()
```

### PostgreSQL

```bash
export DATABASE_URL="postgresql://user:password@localhost/test_protocols"
python -m src.db.database
```

### Schema

- `wind_load_tests` - Main test records
- `pre_test_measurements` - Baseline measurements
- `post_test_measurements` - Final measurements
- `cycle_measurements` - Per-cycle data
- `test_attachments` - Supporting files
- `protocol_configs` - Protocol versions
- `test_audit_logs` - Change tracking

## Integration

### LIMS Integration

Automatic synchronization of test results to LIMS systems:
- Sample ID linking
- Test status updates
- Results data transfer

### QMS Integration

Quality management system workflow triggers:
- Test completion notifications
- Non-conformance reporting
- Approval routing

### Project Management

Milestone tracking and stakeholder notifications:
- Test schedule updates
- Progress tracking
- Automated notifications

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-protocol`)
3. Commit your changes (`git commit -m 'Add new protocol'`)
4. Push to the branch (`git push origin feature/new-protocol`)
5. Open a Pull Request

### Adding New Protocols

1. Create protocol definition in `protocols/<category>/<protocol-id>/`
2. Add JSON schema and configuration
3. Implement protocol class in `src/protocols/`
4. Create Streamlit UI in `src/ui/`
5. Add database models if needed
6. Write comprehensive tests
7. Document in `docs/`

## Requirements

- Python 3.8+
- SQLAlchemy 1.4+
- Streamlit 1.28+
- Pandas 1.5+
- Plotly 5.0+
- Pytest 7.4+ (for testing)

See [requirements.txt](requirements.txt) for complete list.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Standards References

- **IEC 61215-2:2021** - Terrestrial photovoltaic (PV) modules - Design qualification and type approval - Part 2: Test procedures
- **IEC 61730-2** - Photovoltaic (PV) module safety qualification - Part 2: Requirements for testing
- **UL 1703** - Flat-Plate Photovoltaic Modules and Panels

## Support

- 📧 Email: test-protocols@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/ganeshgowri-ASA/test-protocols/issues)
- 📖 Documentation: [docs/](docs/)

## Roadmap

Future protocol implementations:
- [ ] THERMAL-001 - Thermal cycling test
- [ ] HUMIDITY-001 - Damp heat test
- [ ] MECHANICAL-001 - Hail impact test
- [ ] ELECTRICAL-001 - Hot spot endurance test
- [ ] UV-001 - UV preconditioning test

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-11-14 | Initial release with WIND-001 protocol |

## Acknowledgments

- Test protocols based on IEC and UL standards
- Built with Streamlit for interactive UI
- Uses Plotly for advanced visualizations
