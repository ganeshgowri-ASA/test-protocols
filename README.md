# PV Testing Protocol Framework

Modular PV Testing Protocol Framework - JSON-based dynamic templates for Streamlit/GenSpark UI with automated analysis, charting, QC, and report generation. Integrated with LIMS, QMS, and Project Management systems.

## Overview

This framework provides a comprehensive, standardized approach to photovoltaic (PV) module testing based on IEC 61215 and other international standards. It combines:

- **JSON Protocol Templates**: Structured, version-controlled test definitions
- **Python Protocol Engine**: Automated test execution and data collection
- **Interactive UI**: Streamlit-based interfaces for test execution and monitoring
- **Database Storage**: Complete traceability with 25-year data retention
- **Automated Reporting**: PDF, JSON, and CSV export with QR code traceability
- **Quality Control**: Built-in pass/fail criteria and compliance checking

## Implemented Protocols

### ✅ HOT-001: Hot Spot Endurance Test (IEC 61215 MQT 09)

**Status:** Complete Implementation

**Category:** Safety Testing

**Description:** Tests PV module ability to endure hot spot heating effects caused by non-uniform irradiance, cell cracking, or reverse bias conditions.

**Features:**
- 3-cell hot spot generation at 85°C ±5°C
- Automated I-V curve measurement and comparison
- Temperature profile monitoring and visualization
- Power degradation analysis (5% limit)
- Thermal imaging integration
- Insulation resistance testing
- Visual inspection documentation
- Complete test report generation

**Documentation:** [HOT-001 Protocol Guide](docs/protocols/HOT-001_PROTOCOL_GUIDE.md)

**Quick Start:**
```bash
# Run HOT-001 test interface
streamlit run ui/pages/hot001_protocol_page.py
```

---

## Architecture

### Directory Structure

```
test-protocols/
├── templates/
│   └── protocols/          # JSON protocol definitions
│       └── hot-001.json    # Hot Spot Endurance Test template
│
├── protocols/              # Python protocol implementations
│   ├── base.py            # Base protocol class
│   └── environmental/
│       └── hot_001.py     # HOT-001 implementation
│
├── ui/                    # Streamlit UI components
│   ├── components/        # Reusable visualization components
│   │   └── hot001_visualizations.py
│   └── pages/            # Protocol-specific pages
│       └── hot001_protocol_page.py
│
├── database/             # Database models and migrations
│   ├── models.py         # SQLAlchemy models
│   ├── connection.py     # Database connection
│   └── migrations/       # Alembic migrations
│
├── tests/               # Test suite
│   ├── test_protocols/  # Protocol unit tests
│   └── test_database/   # Database tests
│
└── docs/                # Documentation
    └── protocols/       # Protocol-specific guides
```

### Technology Stack

**Backend:**
- Python 3.9+
- SQLAlchemy (ORM)
- Pydantic (data validation)
- NumPy/Pandas (data analysis)

**UI:**
- Streamlit (web interface)
- Plotly (interactive charts)

**Database:**
- SQLite (default, development)
- PostgreSQL (production-ready)

**Testing:**
- Pytest (test framework)
- Coverage.py (code coverage)

---

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ganeshgowri-ASA/test-protocols.git
   cd test-protocols
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database:**
   ```bash
   python -c "from database.connection import init_db; init_db()"
   ```

5. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

---

## Usage

### Running Protocol Tests

#### HOT-001: Hot Spot Endurance Test

**Via UI (Recommended):**
```bash
streamlit run ui/pages/hot001_protocol_page.py
```

**Via Python API:**
```python
from protocols.environmental.hot_001 import HotSpotEnduranceProtocol
import numpy as np

# Initialize protocol
protocol = HotSpotEnduranceProtocol()

# Start test
protocol.start_test("HOT001_TEST_001")

# Perform initial visual inspection
protocol.perform_initial_visual_inspection(
    inspector="John Doe",
    defects=[],
    notes="Module in good condition"
)

# Measure initial I-V curve
voltage = np.linspace(0, 40, 100)
current = 9.0 * (1 - voltage / 40) ** 1.5
protocol.measure_initial_iv_curve(
    voltage=voltage,
    current=current,
    irradiance=1000.0,
    temperature=25.0
)

# Execute hot spot tests
for cell_id in ['A1', 'B5', 'C9']:
    protocol.execute_hot_spot_test(
        cell_id=cell_id,
        reverse_bias_voltage=50.0,
        current_limit=9.0,
        target_temperature=85.0,
        duration_hours=1.0,
        temperature_readings=temp_profile_data
    )

# Measure final I-V curve
protocol.measure_final_iv_curve(
    voltage=final_voltage,
    current=final_current,
    irradiance=1000.0,
    temperature=25.0
)

# Calculate degradation and determine pass/fail
degradation = protocol.calculate_power_degradation()
pass_status, failures = protocol.determine_pass_fail()

# Generate report
report = protocol.generate_test_report()
protocol.export_report_to_json("test_report.json")
```

### Creating Custom Protocols

1. **Define JSON template** in `templates/protocols/`:
   ```json
   {
     "metadata": {
       "protocol_id": "NEW-001",
       "name": "New Test Protocol",
       "version": "1.0.0",
       "standard": "IEC XXXXX",
       "category": "Test Category"
     },
     "parameters": { ... },
     "equipment": { ... },
     "test_procedure": { ... },
     "pass_fail_criteria": { ... }
   }
   ```

2. **Implement protocol class** in `protocols/`:
   ```python
   from protocols.base import BaseProtocol

   class NewProtocol(BaseProtocol):
       def execute(self, **kwargs):
           # Implementation
           pass
   ```

3. **Create UI page** in `ui/pages/`:
   ```python
   import streamlit as st
   from protocols.new_protocol import NewProtocol

   def main():
       st.title("New Test Protocol")
       # UI implementation
   ```

---

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test Suite

```bash
# Protocol tests only
pytest tests/test_protocols/

# Database tests only
pytest tests/test_database/

# With coverage report
pytest --cov=protocols --cov=database --cov-report=html
```

### Test Coverage

Current coverage: **>80%** across all modules

View detailed coverage:
```bash
pytest --cov --cov-report=html
open htmlcov/index.html
```

---

## Database Schema

### Core Tables

**protocols**
- Protocol definitions and metadata
- Stores JSON templates

**test_runs**
- Individual test executions
- Links to protocols
- Stores module info and results

**measurements**
- Time-series measurement data
- Parameters: temperature, voltage, current, etc.

**visual_inspections**
- Pre/post test visual inspection records
- Defect documentation

**hot_spot_tests** (HOT-001 specific)
- Per-cell hot spot test data
- Temperature profiles
- Thermal images

**equipment**
- Equipment registry

**equipment_calibrations**
- Calibration records and certificates

### Relationships

```
Protocol (1) ─→ (N) TestRun
TestRun (1) ─→ (N) Measurement
TestRun (1) ─→ (N) VisualInspection
TestRun (1) ─→ (N) HotSpotTest
Equipment (1) ─→ (N) EquipmentCalibration
```

---

## Data Export and Reporting

### Export Formats

**JSON:**
- Complete test data with metadata
- Machine-readable
- API integration ready

**CSV:**
- Measurement time-series data
- Easy import to Excel/analysis tools

**PDF** (planned):
- Formatted test reports
- Charts and images included
- Suitable for customer delivery

### QR Code Traceability

Each test generates a QR code containing:
- Test ID
- Protocol ID
- Module serial number
- Test date
- Operator

Scan QR code to retrieve complete test record from database.

---

## Integration

### LIMS Integration

```python
from protocols.environmental.hot_001 import HotSpotEnduranceProtocol
import requests

# Run test
protocol = HotSpotEnduranceProtocol()
# ... execute test ...

# Export to LIMS
report = protocol.generate_test_report()
response = requests.post(
    "https://lims.example.com/api/test-results",
    json=report,
    headers={"Authorization": "Bearer TOKEN"}
)
```

### QMS Integration

Test results can be pushed to Quality Management Systems for:
- Non-conformance tracking
- Statistical process control
- Supplier quality monitoring

---

## Compliance

### IEC 61215 Compliance

This framework implements test procedures according to:
- **IEC 61215-1:2021** (Test requirements)
- **IEC 61215-2:2021** (Test procedures)

### Data Retention

- **Duration:** 25 years (per IEC 61215)
- **Format:** JSON primary, PDF secondary
- **Backup:** Automated daily backups recommended

### Calibration Management

- Equipment calibration tracking
- Automatic expiry warnings
- Certificate storage and retrieval

---

## Development

### Code Style

**Python:**
- PEP 8 compliant
- Black formatter
- Type hints required

**Linting:**
```bash
black .
flake8 protocols/ database/ tests/
mypy protocols/ database/
```

### Adding New Protocols

1. Create JSON template
2. Implement protocol class (extend `BaseProtocol`)
3. Write unit tests (>80% coverage required)
4. Create UI page
5. Update documentation
6. Submit pull request

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Roadmap

### Planned Protocols

- [ ] HF-001: Humidity Freeze Test (IEC 61215 MQT 12)
- [ ] TC-001: Thermal Cycling Test (IEC 61215 MQT 11)
- [ ] DH-001: Damp Heat Test (IEC 61215 MQT 13)
- [ ] ML-001: Mechanical Load Test (IEC 61215 MQT 15)
- [ ] HL-001: Hail Impact Test (IEC 61215 MQT 17)

### Planned Features

- [ ] PDF report generation
- [ ] Real-time equipment integration
- [ ] Advanced analytics and trending
- [ ] Multi-user access control
- [ ] RESTful API
- [ ] Docker containerization
- [ ] Cloud deployment (AWS/Azure)

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-protocol`)
3. Write tests for new functionality
4. Ensure all tests pass (`pytest`)
5. Submit a pull request

### Code Review Checklist

- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code follows style guide
- [ ] No breaking changes (or documented)
- [ ] Database migrations included (if needed)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Support

For support, please:
- Open an issue on GitHub
- Email: support@example.com
- Documentation: [docs/](docs/)

---

## Acknowledgments

- IEC Technical Committee 82 for PV testing standards
- Streamlit team for excellent UI framework
- SQLAlchemy team for robust ORM

---

## Citation

If you use this framework in research or publications, please cite:

```
PV Testing Protocol Framework (2025)
https://github.com/ganeshgowri-ASA/test-protocols
Version 1.0.0
```

---

*Last Updated: 2025-11-14*
