# PV Testing Protocol Framework

**Modular PV Testing Protocol Framework** - JSON-based dynamic templates for Streamlit/GenSpark UI with automated analysis, charting, QC, and report generation. Integrated with LIMS, QMS, and Project Management systems.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Overview

This framework provides a comprehensive, modular approach to PV (photovoltaic) module testing with:

- **JSON-based Protocol Definitions**: Flexible, version-controlled test protocols
- **Automated Analysis**: Built-in calculations for energy rating, temperature coefficients, and performance parameters
- **Quality Control**: Configurable QC checks with automatic validation
- **Interactive UI**: Streamlit-based GenSpark UI for test execution and visualization
- **Database Integration**: SQLAlchemy-based storage for test sessions and results
- **Standards Compliance**: IEC 61853, IEC 61215, and other international standards

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Install dependencies
pip install -r requirements.txt

# Or install with development dependencies
pip install -e ".[dev]"
```

### Running the UI

```bash
# Start the Streamlit application
streamlit run src/test_protocols/ui/app.py
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=test_protocols --cov-report=html
```

## 📦 Available Protocols

### ENER-001: Energy Rating Test

Energy rating test protocol according to IEC 61853 standards for measuring PV module energy output under various irradiance and temperature conditions.

**Features:**
- Complete irradiance-temperature matrix testing
- Automatic IV curve extraction and analysis
- Temperature coefficient calculation
- Energy rating calculation for different climate zones
- Interactive charts (IV curves, PV curves, efficiency maps)
- Comprehensive quality checks

**Documentation:** [docs/protocols/ENER-001.md](docs/protocols/ENER-001.md)

## 🏗️ Architecture

```
test-protocols/
├── protocols/              # JSON protocol definitions
│   ├── schema.json        # JSON schema for validation
│   └── ENER-001.json      # Energy Rating Test protocol
│
├── src/test_protocols/
│   ├── core/              # Core framework
│   │   ├── protocol_loader.py
│   │   ├── test_runner.py
│   │   └── data_validator.py
│   │
│   ├── models/            # Database models
│   │   ├── protocol.py
│   │   ├── test_session.py
│   │   ├── measurement.py
│   │   └── report.py
│   │
│   ├── protocols/         # Protocol implementations
│   │   └── ener_001/
│   │       ├── protocol.py
│   │       ├── analysis.py
│   │       ├── charts.py
│   │       └── qc.py
│   │
│   └── ui/                # Streamlit UI
│       ├── app.py
│       └── pages/
│
├── tests/                 # Test suite
└── docs/                  # Documentation
```

## 📊 Usage Examples

### Python API

```python
from test_protocols.protocols.ener_001 import ENER001Protocol
from test_protocols.core.test_runner import TestRunner
import pandas as pd

# Load test data
data = pd.read_csv("test_data.csv")

# Initialize protocol
protocol = ENER001Protocol()

# Create test runner
runner = TestRunner(protocol)

# Execute test
results = runner.run(data)

# Access results
print(f"Energy Rating: {results['analysis']['energy_rating']['energy_rating_kWh_per_kWp']:.0f} kWh/kWp")
print(f"Status: {results['status']}")

# Export results
protocol.export_results("results.json", format="json")
```

### Adding a New Protocol

1. Create JSON protocol definition in `protocols/`:

```json
{
  "protocol_id": "YOUR-001",
  "version": "1.0.0",
  "name": "Your Test Protocol",
  "category": "performance",
  ...
}
```

2. Implement protocol class inheriting from `BaseProtocol`:

```python
from test_protocols.protocols.base_protocol import BaseProtocol

class YOUR001Protocol(BaseProtocol):
    PROTOCOL_ID = "YOUR-001"
    VERSION = "1.0.0"

    def validate_inputs(self, data):
        # Validation logic
        pass

    def run_test(self, data):
        # Test execution logic
        pass
```

3. Add tests in `tests/unit/`

4. Document in `docs/protocols/`

## 🔬 Testing

The framework includes comprehensive unit and integration tests:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_ener_001.py

# Run with coverage
pytest --cov=test_protocols --cov-report=html

# Run only ENER-001 tests
pytest -k "ener_001"
```

## 📚 Documentation

- [Architecture Overview](docs/architecture.md)
- [Protocol Guide](docs/protocol-guide.md)
- [ENER-001 Protocol](docs/protocols/ENER-001.md)
- [API Reference](docs/api-reference.md)

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Standards References

- **IEC 61853-1**: Performance testing and energy rating of terrestrial PV modules
- **IEC 61853-2**: Spectral responsivity, incidence angle and module operating temperature measurements
- **IEC 61853-3**: Energy rating of PV modules
- **IEC 61215**: Terrestrial photovoltaic (PV) modules - Design qualification and type approval

## 📧 Contact

For questions or support, please contact the development team or open an issue on GitHub.

## 🙏 Acknowledgments

This framework was developed for photovoltaic testing laboratories to streamline test execution, analysis, and reporting while ensuring compliance with international standards.
