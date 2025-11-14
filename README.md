# PV Test Protocol Framework

Modular PV Testing Protocol Framework - JSON-based dynamic templates for Streamlit/GenSpark UI with automated analysis, charting, QC, and report generation. Integrated with LIMS, QMS, and Project Management systems.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

## 📋 Overview

This framework provides a comprehensive, modular system for executing, tracking, and documenting photovoltaic (PV) module safety and performance tests according to international standards (IEC 61730, IEC 61215, etc.).

### Key Features

- **JSON-Based Protocol Definitions**: Define test protocols using structured JSON schemas
- **Database-Backed Tracking**: Full test execution history with SQLAlchemy ORM
- **Streamlit UI**: Interactive web interface for test execution and results visualization
- **Extensible Architecture**: Easy to add new test protocols
- **Standards Compliance**: Built-in support for IEC 61730, IEC 61215
- **Automated Pass/Fail Evaluation**: Configurable criteria with severity levels
- **Safety Monitoring**: Real-time safety limit checking with automatic abort
- **Equipment Calibration Tracking**: Manage equipment and calibration schedules
- **Sample Management**: Track PV modules through their testing lifecycle

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ganeshgowri-ASA/test-protocols.git
cd test-protocols

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (optional)
export DATABASE_URL="postgresql://user:pass@localhost/pv_tests"
# Or use SQLite for development:
export ENV="development"

# Initialize database
python -c "from src.models import init_db; init_db()"
```

### Running the Application

```bash
# Start the Streamlit UI
streamlit run src/ui/app.py
```

Navigate to `http://localhost:8501` in your web browser.

## 📚 Implemented Protocols

### GROUND-001: Ground Continuity Test

**Standard**: IEC 61730-2 MST 13 (Continuity of Equipotential Bonding)

**Purpose**: Verify the continuity of equipotential bonding between the module frame and accessible conductive parts to ensure adequate protective grounding.

**Test Parameters**:
- Test Current: 2.5 × Maximum Overcurrent Protection Rating
- Test Duration: 120 seconds
- Maximum Allowed Resistance: ≤ 0.1 Ω
- Voltage Limit: ≤ 12 V

**Location**: `protocols/ground-001/`

## 🏗️ Architecture

### Directory Structure

```
test-protocols/
├── protocols/                  # Protocol definitions
│   └── ground-001/
│       └── protocol.json       # GROUND-001 protocol definition
├── schemas/                    # JSON schemas
│   └── protocol_schema.json    # Protocol validation schema
├── src/
│   ├── models/                 # Database models
│   │   ├── base.py            # Database configuration
│   │   ├── protocol.py        # Protocol models
│   │   ├── test_execution.py  # Test execution models
│   │   ├── equipment.py       # Equipment models
│   │   └── sample.py          # Sample models
│   ├── runners/               # Test execution logic
│   │   ├── base_runner.py     # Base runner class
│   │   └── ground_continuity_runner.py
│   └── ui/                    # Streamlit UI
│       ├── app.py             # Main application
│       ├── components/        # Reusable UI components
│       └── pages/             # Application pages
├── tests/                     # Unit and integration tests
│   ├── unit/
│   └── integration/
└── docs/                      # Documentation
```

### Database Schema

The framework uses the following main entities:

- **Protocol**: Test protocol definitions
- **ProtocolVersion**: Version history of protocols
- **Sample**: PV modules under test
- **Equipment**: Test equipment and instruments
- **TestExecution**: Individual test runs
- **TestMeasurement**: Measurements taken during tests
- **TestResult**: Pass/fail criteria evaluation results
- **EquipmentCalibration**: Calibration records

## 📖 Usage Guide

### 1. Adding a Sample

1. Navigate to "Sample Management" in the UI
2. Click "Add New Sample" tab
3. Fill in required fields:
   - Sample ID (required)
   - Serial Number
   - Electrical ratings (Pmax, Vmp, Imp, Voc, Isc)
   - **Max Overcurrent Protection** (required for ground continuity test)
4. Click "Add Sample"

### 2. Running a Test

1. Navigate to "Test Execution"
2. Select protocol (e.g., GROUND-001)
3. Select sample
4. Configure test parameters
5. Enter operator information
6. Define measurement points
7. Click "Start Test"

### 3. Viewing Results

1. Navigate to "Test Results"
2. Select a test from the dropdown
3. Review:
   - Test summary
   - Measurements
   - Pass/fail criteria evaluation
   - Notes and anomalies

## 🔧 Creating Custom Protocols

### Step 1: Define Protocol JSON

Create a new protocol file in `protocols/your-protocol-id/protocol.json`:

```json
{
  "protocol_id": "YOUR-001",
  "protocol_name": "Your Test Name",
  "version": "1.0.0",
  "category": "Safety",
  "standard": {
    "name": "IEC XXXXX",
    "section": "MST XX"
  },
  "parameters": { ... },
  "measurements": [ ... ],
  "pass_criteria": [ ... ]
}
```

See `schemas/protocol_schema.json` for the complete schema definition.

### Step 2: Create Test Runner

Create a new runner in `src/runners/`:

```python
from .base_runner import BaseTestRunner
from ..models import TestExecution, TestOutcome

class YourTestRunner(BaseTestRunner):
    def __init__(self, db_session):
        super().__init__(
            protocol_id="YOUR-001",
            db_session=db_session
        )

    def calculate_parameters(self, input_params):
        # Calculate test parameters
        pass

    def run_test(self, test_execution, **kwargs):
        # Execute the test
        pass
```

### Step 3: Add to UI

Update `src/ui/pages/test_execution.py` to include your new protocol.

## 🧪 Testing

### Run Unit Tests

```bash
pytest tests/unit/ -v
```

### Run Integration Tests

```bash
pytest tests/integration/ -v
```

### Run All Tests with Coverage

```bash
pytest --cov=src --cov-report=html
```

## 📊 Database Configuration

### PostgreSQL (Production)

```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/pv_test_protocols"
```

### SQLite (Development)

```bash
export ENV="development"
# Database will be created as pv_test_protocols.db
```

## 🔒 Safety Features

- **Real-time Safety Monitoring**: Continuous checking against safety limits
- **Automatic Test Abort**: Stops test if safety limits are exceeded
- **Operator Tracking**: Full audit trail of who performed each test
- **Equipment Calibration Alerts**: Warnings for expired calibrations
- **QC Review Flags**: Mark tests requiring additional review

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Contact

For questions or support, please open an issue on GitHub.

## 🙏 Acknowledgments

- IEC 61730-2:2023 - Photovoltaic (PV) module safety qualification
- IEC 61215 series - Terrestrial photovoltaic (PV) modules - Design qualification and type approval

---

**Version**: 1.0.0
**Last Updated**: 2025-11-14
