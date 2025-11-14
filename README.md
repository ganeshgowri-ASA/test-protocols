# Test Protocols Framework

Modular PV Testing Protocol Framework with JSON-based dynamic templates for Streamlit/GenSpark UI with automated analysis, charting, QC, and report generation.

## Overview

This framework provides a comprehensive solution for executing, tracking, and analyzing photovoltaic module testing protocols. It features:

- **JSON-based Protocol Templates**: Flexible, version-controlled test definitions
- **Python Protocol Classes**: Automated test execution and data collection
- **Interactive UI**: Streamlit-based interface with real-time visualization
- **Database Integration**: Full traceability and data persistence
- **Automated QC**: Pass/fail determination based on industry standards
- **Report Generation**: Automated PDF, JSON, and CSV reports

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Install dependencies
pip install -r requirements.txt

# Initialize database
cd database/migrations
alembic upgrade head
cd ../..
```

### Running a Test

```python
from protocols.environmental.hf_001 import HumidityFreezeProtocol

# Initialize protocol
protocol = HumidityFreezeProtocol()

# Run test
result = protocol.run_test(
    sample_id="MODULE-12345",
    operator_id="OP001"
)

# Analyze results
analysis = protocol.analyze_results(result)
print(f"Test Result: {'PASS' if analysis['pass_fail'] else 'FAIL'}")
print(f"Power Degradation: {analysis['power_degradation']:.2f}%")
```

### Running the UI

```bash
streamlit run ui/pages/hf001_protocol_page.py
```

## Project Structure

```
test-protocols/
├── protocols/                      # Protocol implementations
│   ├── base.py                    # Base protocol class
│   └── environmental/             # Environmental test protocols
│       ├── hf_001.py             # HF-001 Humidity Freeze protocol
│       └── __init__.py
│
├── templates/                      # JSON protocol templates
│   └── protocols/
│       └── hf-001.json           # HF-001 template
│
├── ui/                            # Streamlit UI components
│   ├── components/
│   │   └── hf001_visualizations.py
│   └── pages/
│       └── hf001_protocol_page.py
│
├── database/                      # Database layer
│   ├── models.py                 # SQLAlchemy models
│   ├── connection.py             # Database connection
│   └── migrations/               # Alembic migrations
│       ├── alembic.ini
│       ├── env.py
│       └── versions/
│           └── 20250114_0100_001_initial_schema.py
│
├── tests/                         # Test suite
│   ├── conftest.py
│   ├── test_protocols/
│   │   └── test_hf_001.py
│   └── test_database/
│       └── test_models.py
│
├── docs/                          # Documentation
│   └── protocols/
│       └── HF-001_PROTOCOL_GUIDE.md
│
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Available Protocols

### HF-001: Humidity Freeze Test Protocol

**Standard:** IEC 61215 MQT 12
**Category:** Environmental Testing

Evaluates module performance under combined thermal cycling (-40°C to +85°C) and humidity stress (85% RH).

**Key Features:**
- 10 thermal-humidity cycles
- Automated cycle execution and monitoring
- Real-time temperature/humidity visualization
- I-V curve comparison (before/after)
- Insulation resistance testing
- Visual inspection tracking
- QR code traceability

**Documentation:** [HF-001 Protocol Guide](docs/protocols/HF-001_PROTOCOL_GUIDE.md)

**Usage:**
```python
from protocols.environmental.hf_001 import HumidityFreezeProtocol

protocol = HumidityFreezeProtocol()
result = protocol.run_test(sample_id="MOD-001", operator_id="OP001")
```

## Architecture

### Protocol Template (JSON)

Each protocol is defined by a JSON template containing:
- Metadata (ID, name, version, standard)
- Test parameters (cycles, temperatures, tolerances)
- Equipment requirements and specifications
- Step-by-step test procedures
- QC pass/fail criteria
- Data traceability requirements

### Protocol Class (Python)

Each protocol has a corresponding Python class that:
- Loads the JSON template
- Validates equipment and samples
- Executes test procedures
- Logs measurements to database
- Analyzes results against QC criteria
- Generates reports and QR codes

### Database Schema

The database stores:
- **Protocols**: Template definitions and versions
- **Test Runs**: Execution records with metadata
- **Measurements**: Time-series data points
- **Visual Inspections**: Defect tracking
- **Cycle Logs**: Environmental chamber data
- **Equipment**: Calibration tracking

### User Interface

Interactive Streamlit interface featuring:
- Protocol selection and configuration
- Real-time test monitoring
- Plotly charts for temperature/humidity/I-V curves
- Pass/fail status indicators
- Report export (PDF/JSON/CSV)
- QR code generation

## Development

### Adding a New Protocol

1. **Create JSON Template** (`templates/protocols/your-protocol.json`)
   ```json
   {
     "metadata": {
       "protocol_id": "XX-001",
       "name": "Your Protocol Name",
       "version": "1.0.0",
       "standard": "IEC XXXXX",
       "category": "Testing Category"
     },
     "parameters": { ... },
     "equipment": { ... },
     "test_steps": [ ... ],
     "qc_criteria": { ... }
   }
   ```

2. **Implement Protocol Class** (`protocols/category/your_protocol.py`)
   ```python
   from protocols.base import BaseProtocol

   class YourProtocol(BaseProtocol):
       def validate_equipment(self) -> bool:
           # Implement equipment validation
           pass

       def run_test(self, sample_id: str, **kwargs):
           # Implement test execution
           pass

       def analyze_results(self, test_result):
           # Implement results analysis
           pass
   ```

3. **Create UI Components** (`ui/pages/your_protocol_page.py`)

4. **Write Tests** (`tests/test_protocols/test_your_protocol.py`)

5. **Update Documentation** (`docs/protocols/YOUR_PROTOCOL_GUIDE.md`)

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=protocols --cov=database --cov-report=html

# Run specific test file
pytest tests/test_protocols/test_hf_001.py -v
```

### Database Migrations

```bash
# Create new migration
cd database/migrations
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/test_protocols
# or use SQLite (default)
DATABASE_URL=sqlite:///test_protocols.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/test_protocols.log

# UI
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
```

## Data Traceability

All test data includes:
- Unique test ID
- Module serial number
- Timestamp (start/end)
- Operator ID
- Equipment IDs and calibration status
- QR code for mobile access
- 25-year data retention compliance

## QC and Compliance

The framework ensures:
- Adherence to IEC 61215 and related standards
- Automated pass/fail determination
- Equipment calibration tracking
- Measurement uncertainty analysis
- Complete audit trail

## API Reference

### BaseProtocol

Base class for all protocols.

**Methods:**
- `validate_equipment() -> bool`: Validate required equipment
- `validate_sample(sample_data) -> bool`: Validate sample
- `run_test(sample_id, **kwargs) -> TestResult`: Execute test
- `analyze_results(test_result) -> dict`: Analyze results
- `generate_report(test_result, output_path) -> Path`: Generate report

### HumidityFreezeProtocol

HF-001 implementation.

**Additional Methods:**
- `measure_iv_curve(module_temp, irradiance) -> IVCurveData`
- `measure_insulation_resistance(test_voltage) -> float`
- `execute_cycle(cycle_number, duration_minutes) -> CycleData`
- `export_cycle_data(output_path) -> Path`
- `generate_qr_code() -> str`

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-protocol`)
3. Make your changes
4. Write tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Commit your changes (`git commit -m 'Add new protocol'`)
7. Push to the branch (`git push origin feature/new-protocol`)
8. Create a Pull Request

## License

[Add your license here]

## Support

For questions or issues:
- Create an issue on GitHub
- Contact: [your-email@example.com]

## Roadmap

### Planned Features
- [ ] Additional protocols (Thermal Cycling, Damp Heat, UV Exposure)
- [ ] LIMS integration (Laboratory Information Management System)
- [ ] Real-time equipment interface via MODBUS/TCP
- [ ] Machine learning for failure prediction
- [ ] Mobile app for QR code scanning
- [ ] Multi-language support

### Current Implementation
- [x] HF-001 Humidity Freeze protocol
- [x] JSON template system
- [x] SQLAlchemy database layer
- [x] Streamlit UI with Plotly visualization
- [x] Automated QC and reporting
- [x] Unit test suite

## Acknowledgments

- IEC 61215 standard committee
- Photovoltaic testing community
- Open source contributors

## Version

**Current Version:** 1.0.0
**Release Date:** 2025-01-14

---

**Built for solar testing laboratories worldwide** ☀️
