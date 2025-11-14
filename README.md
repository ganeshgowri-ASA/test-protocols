# PV Testing Protocol Framework

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Modular PV Testing Protocol Framework - JSON-based dynamic templates for Streamlit/GenSpark UI with automated analysis, charting, QC, and report generation. Integrated with LIMS, QMS, and Project Management systems.

## Features

- **JSON-Based Protocol Templates** - Define test protocols using standardized JSON schemas
- **Streamlit/GenSpark UI** - Interactive web-based interface for test execution
- **Automated Analysis** - Built-in statistical analysis and degradation calculations
- **Dynamic Charting** - Real-time data visualization with Plotly
- **Quality Control** - Automated QC criteria evaluation with pass/fail reporting
- **Database Integration** - PostgreSQL backend for data persistence
- **Comprehensive Testing** - Full unit and integration test coverage
- **Extensible Architecture** - Easy to add new protocols and measurements

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Install dependencies
pip install -r requirements.txt

# Optional: Setup database
createdb pv_testing
psql -d pv_testing -f database/schema.sql
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### Launch UI

```bash
# Main application
cd src/ui
streamlit run app.py

# JBOX-001 test runner
streamlit run pages/jbox001_test.py
```

### Python API Example

```python
from src.protocols.jbox001 import JBOX001Protocol

# Initialize protocol
protocol = JBOX001Protocol()

# Create test run
test_run = protocol.create_test_run(
    sample_id="MODULE-001",
    operator="Your Name"
)

# Start testing
protocol.runner.start_test_run(test_run.test_run_id)

# Run initial characterization
protocol.run_initial_characterization(
    test_run=test_run,
    visual_inspection={'defects_count': 0, 'notes': 'Clean'},
    contact_resistance=5.2,
    diode_voltage=[0.65, 0.64, 0.66],
    insulation_resistance=100.0,
    iv_curve_data={'pmax': 300.0, 'voc': 40.5, 'isc': 9.2}
)

# Save results
filepath = test_run.save()
print(f"Results saved to: {filepath}")
```

## Project Structure

```
test-protocols/
├── protocols/              # Protocol definitions
│   ├── templates/          # JSON protocol templates
│   │   └── jbox-001.json  # JBOX-001 protocol
│   └── schemas/            # JSON validation schemas
│       └── protocol-schema.json
├── src/                    # Source code
│   ├── core/              # Core framework
│   │   ├── protocol_loader.py
│   │   ├── test_runner.py
│   │   └── data_validator.py
│   ├── protocols/         # Protocol implementations
│   │   └── jbox001.py
│   ├── ui/                # Streamlit UI
│   │   ├── app.py
│   │   └── pages/
│   ├── analysis/          # Analysis modules
│   ├── integrations/      # External integrations
│   └── reports/           # Report generation
├── database/              # Database schemas
│   ├── schema.sql
│   └── migrations/
├── tests/                 # Test suite
│   ├── test_core.py
│   └── test_protocols/
├── docs/                  # Documentation
│   ├── protocols/         # Protocol docs
│   ├── api/              # API documentation
│   └── user_guide/       # User guides
├── requirements.txt       # Python dependencies
├── setup.py              # Package configuration
└── README.md             # This file
```

## Available Protocols

### JBOX-001: Junction Box Degradation Test

Comprehensive testing protocol for evaluating junction box reliability and degradation.

**Test Phases:**
1. Initial Characterization
2. Thermal Cycling (200 cycles, -40°C to 85°C)
3. Humidity-Freeze (10 cycles)
4. UV Exposure (15 kWh/m²)
5. Electrical Load Stress (168 hours)
6. Final Characterization

**Standards Compliance:**
- IEC 61215-2:2021
- IEC 61730-2:2016
- UL 1703

[Full JBOX-001 Documentation](docs/protocols/JBOX-001.md)

## Documentation

- [Getting Started Guide](docs/user_guide/getting_started.md)
- [JBOX-001 Protocol Specification](docs/protocols/JBOX-001.md)
- [API Documentation](docs/api/README.md)
- [Database Schema](database/schema.sql)

## Technology Stack

- **Backend:** Python 3.8+
- **UI Framework:** Streamlit
- **Database:** PostgreSQL
- **Data Processing:** NumPy, Pandas
- **Visualization:** Plotly
- **Testing:** pytest
- **Schema Validation:** jsonschema

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Testing

The framework includes comprehensive test coverage:

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_core.py

# Run with coverage report
python -m pytest tests/ --cov=src --cov-report=html
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- IEC TC82 for PV testing standards
- PV research community for testing methodologies
- Open source contributors

## Contact

For questions, issues, or contributions:
- **GitHub Issues:** [https://github.com/ganeshgowri-ASA/test-protocols/issues](https://github.com/ganeshgowri-ASA/test-protocols/issues)
- **Project Repository:** [https://github.com/ganeshgowri-ASA/test-protocols](https://github.com/ganeshgowri-ASA/test-protocols)

## Roadmap

- [ ] Additional protocols (Humidity-Freeze, Damp Heat, etc.)
- [ ] Advanced statistical analysis
- [ ] PDF report generation
- [ ] LIMS integration
- [ ] REST API
- [ ] Cloud deployment support
