# IEC 61730 Test Protocol Framework

Modular PV Testing Protocol Framework - JSON-based dynamic templates for Streamlit/GenSpark UI with automated analysis, charting, QC, and report generation. Integrated with LIMS, QMS, and Project Management systems.

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Framework](https://img.shields.io/badge/UI-Streamlit-red)](https://streamlit.io)

## 🌟 Features

- **Dynamic JSON-based Protocol Templates**: Flexible, version-controlled test definitions
- **Interactive Streamlit UI**: User-friendly interface for test execution and monitoring
- **Automated Data Analysis**: Real-time statistical analysis and pass/fail determination
- **Comprehensive Reporting**: Automated HTML/PDF report generation
- **Database Integration**: SQLite/PostgreSQL support for data persistence
- **Quality Control**: Built-in QC checks and anomaly detection
- **Extensible Architecture**: Easy addition of new test protocols
- **LIMS Integration Ready**: API endpoints for laboratory information systems

## 📋 Available Protocols

### WET-001: Wet Leakage Current Test
**Standard**: IEC 61730 MST 02
**Category**: Safety
**Status**: ✅ Implemented

Tests PV modules for electrical safety under humid conditions by measuring leakage current during exposure to high humidity and test voltage.

**Key Features**:
- Automated data collection and analysis
- Real-time trending and anomaly detection
- Statistical pass/fail determination
- Comprehensive HTML reports with charts

[📖 Protocol Documentation](docs/WET-001.md)

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Initialize database**:
```bash
python -c "from database.session import init_database; init_database()"
```

### Running the Application

**Start Streamlit UI**:
```bash
streamlit run ui/streamlit_app.py
```

The application will open in your default browser at `http://localhost:8501`

## 📖 Usage Guide

### Running a Test

1. **Navigate to "Run Test"** page
2. **Select protocol** (e.g., WET-001)
3. **Enter sample information**:
   - Sample ID
   - Module type
   - Manufacturer details
4. **Configure test conditions**:
   - Test voltage
   - Duration
   - Environmental parameters
5. **Set acceptance criteria** (or use defaults)
6. **Start test** and add measurements
7. **Analyze results** when complete
8. **Generate report**

### Adding Measurements

#### Manual Entry
```python
protocol.add_measurement(
    leakage_current=0.15,  # mA
    voltage=1500.0,        # V
    temperature=25.0,      # °C
    humidity=90.0,         # %
    notes="Optional observation"
)
```

#### Programmatic API
```python
from protocols.wet_leakage_current import WETLeakageCurrentProtocol

# Initialize protocol
protocol = WETLeakageCurrentProtocol()

# Configure parameters
params = {
    "sample_information": {...},
    "test_conditions": {...},
    "environmental_conditions": {...}
}

# Validate parameters
protocol.validate_parameters(params)

# Add measurements (from equipment interface)
for measurement in equipment.get_measurements():
    protocol.add_measurement(**measurement)

# Analyze results
results = protocol.analyze_results()

# Generate report
report_path = protocol.generate_report(test_result)
```

## 🏗️ Architecture

```
test-protocols/
├── config/              # Configuration files
├── database/            # Database models and session management
├── docs/                # Documentation
├── protocols/           # Test protocol implementations
│   ├── base.py         # Base protocol class
│   ├── registry.py     # Protocol registry
│   └── wet_leakage_current/  # WET-001 implementation
│       ├── schema.json
│       ├── protocol.py
│       ├── analysis.py
│       └── report_template.html
├── tests/               # Test suite
├── ui/                  # Streamlit UI components
│   ├── streamlit_app.py
│   └── pages/
└── utils/               # Utility modules
```

[📖 Detailed Architecture Documentation](docs/ARCHITECTURE.md)

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=protocols --cov=database --cov=analysis

# Run specific test file
pytest tests/unit/test_wet_protocol.py

# Run with verbose output
pytest -v
```

## 📊 Database Schema

The framework uses SQLAlchemy ORM with support for SQLite (development) and PostgreSQL (production).

**Core Tables**:
- `test_protocols`: Protocol definitions
- `sample_information`: Sample/module metadata
- `test_runs`: Test execution instances
- `measurements`: Individual measurement points
- `test_results`: Analysis results

## 🔧 Configuration

Edit `config/config.yaml` to customize:

```yaml
database:
  type: sqlite  # or postgresql
  path: test_protocols.db

ui:
  title: "Test Protocol Framework"
  layout: wide

wet_leakage_current:
  max_leakage_current: 0.25  # mA
  min_insulation_resistance: 400  # MΩ
```

## 📝 Adding New Protocols

1. **Create protocol directory**:
```bash
mkdir -p protocols/new_protocol
```

2. **Define JSON schema** (`schema.json`):
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "New Protocol",
  "properties": { ... }
}
```

3. **Implement protocol class**:
```python
from protocols.base import BaseProtocol

class NewProtocol(BaseProtocol):
    def validate_parameters(self, params): ...
    def run_test(self, params, sample_id): ...
    def analyze_results(self): ...
    def generate_report(self, test_result): ...
```

4. **Register protocol**:
```python
from protocols.registry import register_protocol

register_protocol("NEW-001", NewProtocol)
```

5. **Add tests**:
```python
# tests/unit/test_new_protocol.py
def test_new_protocol():
    protocol = NewProtocol()
    assert protocol.protocol_id == "NEW-001"
```

## 🔌 Integration

### LIMS Integration

```python
from integrations.lims import LIMSClient

lims = LIMSClient(api_url, api_key)
lims.submit_test_result(test_result)
```

### Equipment Interface

```python
# Custom equipment interface
class EquipmentInterface:
    def get_measurement(self):
        # Read from equipment
        return {
            'leakage_current': ...,
            'voltage': ...,
            'temperature': ...,
            'humidity': ...
        }
```

## 📚 Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [WET-001 Protocol Guide](docs/WET-001.md)
- [API Reference](docs/API.md) *(coming soon)*
- [Contributing Guidelines](docs/CONTRIBUTING.md) *(coming soon)*

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-protocol`)
3. Commit your changes (`git commit -m 'Add new protocol'`)
4. Push to the branch (`git push origin feature/new-protocol`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- IEC 61730 standards committee
- Open-source community
- Streamlit team for the excellent UI framework

## 📧 Contact

- **GitHub**: [ganeshgowri-ASA/test-protocols](https://github.com/ganeshgowri-ASA/test-protocols)
- **Issues**: [Report a bug](https://github.com/ganeshgowri-ASA/test-protocols/issues)
- **Discussions**: [Community discussions](https://github.com/ganeshgowri-ASA/test-protocols/discussions)

## 🗺️ Roadmap

- [ ] Additional IEC 61730 protocols (MST 01, 03, 04...)
- [ ] REST API for programmatic access
- [ ] Advanced ML-based anomaly detection
- [ ] Mobile application
- [ ] Cloud deployment support
- [ ] Equipment automation interfaces
- [ ] Multi-language support
- [ ] Advanced statistical process control (SPC)

## 📊 Project Status

**Current Version**: 1.0.0
**Status**: Active Development
**Last Updated**: 2025-11-14

### Implementation Status

| Protocol | Status | Version | Documentation |
|----------|--------|---------|---------------|
| WET-001  | ✅ Complete | 1.0.0 | [View](docs/WET-001.md) |
| HF-001   | 🚧 Planned | - | - |
| UV-001   | 🚧 Planned | - | - |

---

**Built with ❤️ for the solar industry**
