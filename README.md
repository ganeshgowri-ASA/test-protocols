# PV Testing Protocol Framework

Modular PV Testing Protocol Framework - JSON-based dynamic templates for Streamlit/GenSpark UI with automated analysis, charting, QC, and report generation. Integrated with LIMS, QMS, and Project Management systems.

## Overview

This repository provides a comprehensive framework for photovoltaic (PV) module testing protocols with complete data traceability, real-time monitoring, and automated analysis capabilities.

## Implemented Protocols

### UV-001: UV Preconditioning Protocol (IEC 61215 MQT 10)

Complete implementation of UV exposure testing for PV module qualification.

**Features:**
- ☀️ Real-time UV dosage tracking (15 kWh/m² target)
- 📊 Live irradiance monitoring and spectral analysis
- 🌡️ Temperature and environmental condition tracking
- ⚡ Pre/post electrical characterization
- 📈 Interactive Plotly visualizations
- 🗄️ Complete database schema with traceability
- ✅ Automated acceptance criteria checking
- 📝 Comprehensive documentation

**Quick Start:**
```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python migrations/001_initial_setup.py upgrade sqlite:///uv001_test_data.db

# Run UI
streamlit run ui/components/uv_preconditioning_ui.py

# Run tests
python -m pytest tests/protocols/environmental/test_uv_preconditioning.py -v
```

**Documentation:** [UV-001 Full Documentation](docs/protocols/UV-001_Documentation.md)

## Repository Structure

```
test-protocols/
├── protocols/               # JSON protocol templates
│   └── environmental/
│       └── UV-001_preconditioning.json
├── src/                    # Python implementation
│   ├── protocols/
│   │   └── environmental/
│   │       └── uv_preconditioning.py
│   └── database/
│       └── models.py
├── ui/                     # GenSpark/Streamlit UI components
│   └── components/
│       └── uv_preconditioning_ui.py
├── migrations/            # Database migrations
│   ├── schema_uv001.sql
│   └── 001_initial_setup.py
├── tests/                 # Unit tests
│   └── protocols/
│       └── environmental/
│           └── test_uv_preconditioning.py
├── docs/                  # Documentation
│   └── protocols/
│       └── UV-001_Documentation.md
└── requirements.txt       # Python dependencies
```

## Key Features

### 1. JSON Protocol Templates
- Standardized protocol definitions
- Complete parameter specifications
- Test procedure documentation
- Equipment requirements
- Acceptance criteria

### 2. Python Protocol Classes
- Object-oriented implementation
- Real-time data processing
- Automated calculations
- Compliance checking
- Data validation

### 3. GenSpark UI with Plotly
- Live monitoring dashboards
- Interactive graphs and charts
- Cumulative dose tracking
- Temperature monitoring
- Spectral analysis
- Degradation analysis

### 4. Database Integration
- Complete data traceability
- SQLAlchemy ORM models
- MySQL/SQLite support
- Automated migrations
- Data quality tracking

### 5. Quality Control
- Comprehensive unit tests
- Data validation
- Calibration tracking
- Event logging
- Audit trails

## Usage Example

```python
from protocols.environmental import UVPreconditioningProtocol

# Initialize protocol
protocol = UVPreconditioningProtocol()

# Start test session
session = protocol.start_test_session(
    session_id="UV001_20250114_001",
    sample_id="MODULE_12345",
    operator="Test Engineer"
)

# Add real-time measurements
protocol.add_irradiance_measurement(uv_irradiance=300.0)
protocol.add_environmental_measurement(
    module_temperature=60.0,
    ambient_temperature=25.0,
    relative_humidity=50.0
)

# Monitor progress
completion = protocol.get_dose_completion_percentage()
remaining_time = protocol.estimate_remaining_time()

# Check results
acceptance = protocol.check_acceptance_criteria()
print(f"Test Result: {'PASS' if acceptance['overall_pass'] else 'FAIL'}")
```

## Testing

Run the complete test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific protocol tests
python -m pytest tests/protocols/environmental/test_uv_preconditioning.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

## Standards Compliance

- **IEC 61215:2021** - PV module design qualification
- **IEC 60904-9:2020** - Solar simulator requirements
- **ISO 9060:2018** - Solar irradiance classification

## Data Traceability

All test data includes:
- Unique session identifiers
- ISO 8601 timestamps
- Operator identification
- Equipment serial numbers
- Calibration dates
- Complete audit trail

## Integration

The framework supports integration with:
- Laboratory Information Management Systems (LIMS)
- Quality Management Systems (QMS)
- Project Management tools
- Automated report generation
- Data export (JSON, CSV, PDF)

## License

See LICENSE file for details.

## Contributing

1. Follow existing code structure
2. Maintain consistent documentation
3. Add unit tests for new features
4. Update protocol templates as needed

## Support

For detailed protocol documentation, see:
- [UV-001 Documentation](docs/protocols/UV-001_Documentation.md)

## Version

Current version: 1.0.0
