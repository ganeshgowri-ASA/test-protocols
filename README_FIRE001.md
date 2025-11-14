# FIRE-001: Fire Resistance Testing Protocol

**Complete LIMS-QMS Implementation for Photovoltaic Module Fire Safety Testing**

[![Protocol Status](https://img.shields.io/badge/status-active-green)]() [![Version](https://img.shields.io/badge/version-1.0.0-blue)]() [![Standard](https://img.shields.io/badge/standard-IEC%2061730--2%20MST%2023-orange)]()

## Overview

This repository contains the complete implementation of the Fire Resistance Testing Protocol (FIRE-001) according to IEC 61730-2 MST 23 standard. It provides a comprehensive Laboratory Information Management System (LIMS) and Quality Management System (QMS) integration for conducting, managing, and reporting fire resistance tests on photovoltaic modules.

### Key Features

- **JSON-based Protocol Definition** - Structured, machine-readable test protocol
- **Python Handler & Models** - Complete API for test execution and data management
- **Streamlit/GenSpark UI** - Interactive web interface for test execution
- **Database Integration** - Full LIMS/QMS database schema with SQLAlchemy ORM
- **Automated Analysis** - Real-time data analysis and acceptance criteria evaluation
- **Comprehensive Testing** - Unit and integration test suites
- **Report Generation** - Automated test report creation in multiple formats
- **Compliance Ready** - Built for regulatory compliance and audit trails

## Protocol Information

| Attribute | Value |
|-----------|-------|
| **Protocol ID** | FIRE-001 |
| **Protocol Name** | Fire Resistance Testing Protocol |
| **Version** | 1.0.0 |
| **Category** | Safety |
| **Standard** | IEC 61730-2 MST 23 |
| **Status** | Active |
| **Test Type** | Fire Resistance & Flame Propagation |
| **Application** | PV Module Safety Qualification |

## Project Structure

```
test-protocols/
├── protocols/
│   └── FIRE-001/
│       └── json/
│           └── fire_resistance_protocol.json    # Protocol definition
├── src/
│   ├── models/
│   │   └── fire_resistance_model.py            # Data models
│   ├── handlers/
│   │   └── fire_resistance_handler.py          # Protocol handler
│   ├── ui/
│   │   └── fire_resistance_ui.py               # Streamlit UI
│   └── db/
│       ├── schema.sql                           # Database schema
│       └── models.py                            # SQLAlchemy ORM
├── tests/
│   ├── unit/
│   │   └── test_fire_resistance_model.py       # Unit tests
│   └── integration/
│       └── test_fire_resistance_integration.py # Integration tests
├── docs/
│   └── protocols/
│       └── FIRE-001_USER_GUIDE.md              # User guide
└── README_FIRE001.md                            # This file
```

## Quick Start

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd test-protocols
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Initialize the database:**
```bash
python -c "from src.db.models import DatabaseManager; db = DatabaseManager(); db.create_all_tables()"
```

### Running the Web Interface

Launch the Streamlit UI:
```bash
streamlit run src/ui/fire_resistance_ui.py
```

Access the interface at: `http://localhost:8501`

### Using the Python API

```python
from src.handlers.fire_resistance_handler import FireResistanceProtocolHandler
from src.models.fire_resistance_model import SampleInformation, TestObservations

# Initialize
handler = FireResistanceProtocolHandler()

# Register sample
sample = SampleInformation(
    sample_id="SMP-2025-001",
    manufacturer="Solar Tech Inc",
    model_number="ST-400-BF",
    serial_number="SN123456"
)

# Create test
test = handler.create_test_session(
    sample=sample,
    test_personnel=["John Doe", "Jane Smith"]
)

# Record measurements
handler.record_measurement(
    elapsed_time_seconds=30.0,
    surface_temperature_c=150.5,
    flame_spread_mm=25.0,
    observations="Normal test progression"
)

# Finalize and generate report
observations = TestObservations(
    ignition_occurred=True,
    self_extinguishing_time_seconds=45.0,
    max_flame_spread_mm=75.0
)

results = handler.finalize_test(observations)
report = handler.generate_report(results)
```

## Features

### 1. Protocol Definition (JSON)

Comprehensive JSON schema including:
- Test overview and objectives
- Equipment requirements
- Safety procedures
- Step-by-step test procedure
- Data collection parameters
- Acceptance criteria
- Quality control requirements
- LIMS/QMS integration points

### 2. Data Models

Complete Python data models:
- `SampleInformation` - PV module sample data
- `EnvironmentalConditions` - Test environment tracking
- `EquipmentCalibration` - Calibration management
- `RealTimeMeasurement` - Time-series data
- `TestObservations` - Qualitative observations
- `TestResults` - Complete test results
- `TestReport` - Report generation

### 3. Protocol Handler

Full-featured test management:
- Test session creation and management
- Real-time measurement recording
- Environmental condition validation
- Equipment calibration verification
- Acceptance criteria evaluation
- Report generation
- Multi-format export (JSON, CSV)

### 4. Web Interface (Streamlit)

Interactive UI with pages for:
- Protocol overview
- Sample registration
- Test execution with real-time data entry
- Live data visualization
- Acceptance criteria evaluation
- Report generation
- Quality management
- Equipment calibration tracking
- Help and documentation

### 5. Database Integration

Complete LIMS/QMS database:
- Protocols and samples
- Equipment and calibrations
- Personnel and training
- Test sessions and measurements
- Observations and results
- Reports and signatures
- Nonconformance tracking
- Change control
- Audit trail
- Notifications

### 6. Testing Suite

Comprehensive test coverage:
- **Unit Tests** - Model validation, data conversion
- **Integration Tests** - Complete workflows, validation logic
- **Test Scenarios** - Pass/fail conditions, edge cases

### 7. Quality Management

Built-in QMS features:
- Nonconformance reporting
- Change control
- Training records
- Audit trail
- Document control
- Calibration management
- Electronic signatures

## Test Procedure Summary

### Phase 1: Preparation (2-3 hours)
1. Sample reception and inspection
2. Conditioning (24+ hours)
3. Pre-test inspection and documentation
4. Equipment setup and verification

### Phase 2: Test Execution (1-2 hours)
1. Module mounting
2. Flame application setup
3. 10-minute ignition test with real-time monitoring
4. 10-minute post-flame observation

### Phase 3: Post-Test (1-2 hours)
1. Cooling period
2. Post-test inspection and measurement
3. Documentation and sample disposal

## Acceptance Criteria

### Critical Criteria (Must ALL Pass)

✅ **No Sustained Burning** - Self-extinguish ≤ 60 seconds
✅ **Limited Flame Spread** - Spread ≤ 100 mm
✅ **No Flaming Drips** - No flaming material drips

### Major Criteria

⚠️ **Material Integrity** - No through-penetration
⚠️ **No External Ignition** - No secondary ignitions

## Data Management

### Real-Time Measurements
- Surface temperature (1 Hz sampling)
- Flame spread distance (30s intervals)
- Time to ignition (event-based)
- Burning duration (continuous)

### Data Retention
- Raw data: 10 years
- Test reports: Permanent
- Samples: 90 days (1 year if failed)
- Calibration records: Equipment life + 5 years

## Safety

### Required PPE
- Fire-resistant lab coat
- Safety goggles
- Heat-resistant gloves
- Closed-toe shoes
- Face shield (recommended)

### Safety Procedures
- Well-ventilated area required
- Fire extinguisher ready
- Minimum 2 personnel
- Emergency stop procedures in place

## Compliance

This implementation supports:
- IEC 61730-2:2023 compliance
- ISO/IEC 17025:2017 requirements
- 21 CFR Part 11 (electronic records/signatures)
- GLP/cGMP practices
- Audit trail requirements
- Data integrity (ALCOA+ principles)

## Documentation

- **User Guide**: [`docs/protocols/FIRE-001_USER_GUIDE.md`](docs/protocols/FIRE-001_USER_GUIDE.md)
- **Protocol JSON**: [`protocols/FIRE-001/json/fire_resistance_protocol.json`](protocols/FIRE-001/json/fire_resistance_protocol.json)
- **API Documentation**: See docstrings in source files

## Testing

Run all tests:
```bash
# Unit tests
python -m pytest tests/unit/ -v

# Integration tests
python -m pytest tests/integration/ -v

# All tests with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

## API Examples

### Complete Test Workflow

```python
from src.handlers.fire_resistance_handler import FireResistanceProtocolHandler
from src.models.fire_resistance_model import *

# 1. Initialize handler
handler = FireResistanceProtocolHandler()

# 2. Create and register sample
sample = SampleInformation(
    sample_id="SMP-001",
    manufacturer="Solar Tech Inc",
    model_number="ST-400",
    serial_number="SN123456",
    dimensions={"length_mm": 1956, "width_mm": 992, "thickness_mm": 40}
)

# 3. Create test session
test = handler.create_test_session(
    sample=sample,
    test_personnel=["Technician A", "Engineer B"]
)

# 4. Set environmental conditions
test.environmental_conditions = EnvironmentalConditions(
    temperature_c=23.5,
    relative_humidity=48.0
)

# 5. Add equipment calibrations
equipment = [
    EquipmentCalibration(
        equipment_id="EQ-FIRE-003",
        equipment_name="Temperature Sensor",
        calibration_date=datetime.now(),
        calibration_due_date=datetime.now() + timedelta(days=365),
        calibration_certificate="CAL-2025-001",
        calibrated_by="Cal Lab"
    )
]
test.equipment_used = equipment

# 6. Record measurements during test
for t in range(0, 601, 30):  # Every 30 seconds
    handler.record_measurement(
        elapsed_time_seconds=float(t),
        surface_temperature_c=25.0 + (t / 10),
        flame_spread_mm=min(t / 10, 75.0)
    )

# 7. Finalize with observations
observations = TestObservations(
    ignition_occurred=True,
    time_to_ignition_seconds=35.0,
    self_extinguishing=True,
    self_extinguishing_time_seconds=45.0,
    max_flame_spread_mm=75.0,
    flaming_drips=False,
    smoke_generation=SmokeLevel.LIGHT,
    material_integrity=MaterialIntegrity.MINOR_DAMAGE
)

results = handler.finalize_test(observations)

# 8. Generate report
report = handler.generate_report(
    test_results=results,
    prepared_by="Technician A",
    reviewed_by="Engineer B",
    approved_by="Quality Manager"
)

# 9. Export results
handler.export_results(
    test_results=results,
    output_dir="./output",
    formats=['json', 'csv']
)

print(f"Test Result: {results.overall_result.value}")
print(f"Report ID: {report.report_id}")
```

## Database Schema

The system includes comprehensive database schema with:
- 18+ tables for complete LIMS/QMS functionality
- Foreign key relationships
- Indexes for performance
- Views for common queries
- Stored procedures for workflows
- Audit trail triggers

Initialize database:
```python
from src.db.models import DatabaseManager

db = DatabaseManager("sqlite:///fire_resistance_lims.db")
db.create_all_tables()
session = db.get_session()
```

## Contributing

1. Follow existing code structure and style
2. Add tests for new features
3. Update documentation
4. Ensure all tests pass
5. Submit pull request with description

## Version History

- **1.0.0** (2025-11-14) - Initial release
  - Complete protocol implementation
  - Full LIMS/QMS integration
  - Web UI
  - Comprehensive testing
  - Documentation

## License

See [LICENSE](LICENSE) file for details.

## Support

For technical support, questions, or bug reports:
- Create an issue in the repository
- Contact: [Support Contact Information]

## Acknowledgments

- IEC 61730-2 Standard Committee
- Testing laboratory personnel
- Quality management team

---

**Status**: Production Ready
**Last Updated**: 2025-11-14
**Maintained By**: LIMS-QMS Development Team
