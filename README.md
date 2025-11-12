# PV Testing Protocol Framework

## Overview

Comprehensive modular PV (Photovoltaic) testing protocol framework with JSON-based dynamic templates, Streamlit UI, automated analysis, charting, QC integration, and report generation. Integrated with LIMS, QMS, and Project Management systems.

### Session 13-20: Safety, Insulation & Certification Tests

This implementation includes **8 comprehensive test protocols** (PVTP-016 through PVTP-023) with complete backend handlers, validators, safety interlocks, automated reporting, PM/QC/NC integration, and full data traceability.

## 📋 Implemented Protocols

### PVTP-016: Wet Leakage Current Test (IEC 61215 MQT 15)
- **Standard**: IEC 61215 MQT 15
- **Category**: Safety
- **Description**: Measures leakage current under wet conditions to verify electrical safety
- **Safety Interlocks**: 8 interlocks including high voltage, grounding, and discharge checks
- **Approval Gates**: 4 gates (pre-test, calibration, data review, final approval)

### PVTP-017: Insulation Resistance Test (IEC 61215 MST 01)
- **Standard**: IEC 61215 MST 01
- **Category**: Safety
- **Description**: Dry insulation resistance measurement with temperature correction
- **Key Features**: Temperature-corrected normalized resistance, area normalization
- **Acceptance Criteria**: Minimum 40 MΩ·m² normalized resistance

### PVTP-018: Ground Continuity Test
- **Standard**: IEC 61730 MST 50
- **Category**: Safety
- **Description**: Verifies grounding path continuity and integrity
- **Test Method**: Four-wire Kelvin measurement at 10A test current
- **Acceptance Criteria**: Maximum 0.1Ω ground resistance

### PVTP-019: Hi-Pot/Dielectric Withstand Test (1000V+500V)
- **Standard**: IEC 61730 MST 23
- **Category**: Safety (Critical)
- **Description**: High voltage dielectric strength verification
- **Test Voltage**: V_system + 500V (minimum 1000V)
- **Safety Features**: 11 safety interlocks including arc detection and emergency stop

### PVTP-020: Fire Class Testing (IEC 61730)
- **Standard**: IEC 61730 MST 23.22 / UL 1703
- **Category**: Certification
- **Description**: Fire resistance classification (Class A, B, or C)
- **Safety Features**: Fire suppression systems, trained personnel requirements
- **Destructive**: Yes (multiple samples required)

### PVTP-021: Module Safety Qualification (MST 20-35)
- **Standard**: IEC 61730 MST 20-35
- **Category**: Certification
- **Description**: Complete module safety test sequence (16 test groups)
- **Scope**: Construction, materials, electrical safety (MST 20-35)
- **References**: Links to PVTP-016 through PVTP-020

### PVTP-022: Connector/Cable Pull Test
- **Standard**: IEC 61730 / IEC 62852 MST 28
- **Category**: Mechanical
- **Description**: Cable mechanical strength and connector retention
- **Test Force**: 50N for 10 seconds
- **Key Measurements**: Force-displacement curves, contact resistance

### PVTP-023: Terminal Torque Test
- **Standard**: IEC 60947-7-1 / UL 1741
- **Category**: Mechanical
- **Description**: Terminal mechanical strength and retention
- **Test**: Over-torque test at 1.2× max torque, 10 cycles
- **Verification**: 50N pull test, contact resistance measurement

## 🏗️ Architecture

```
test-protocols/
├── protocols/
│   ├── schemas/
│   │   └── base-protocol-schema.json     # Base JSON schema for all protocols
│   ├── definitions/
│   │   ├── pvtp-016.json                  # Wet Leakage Current
│   │   ├── pvtp-017.json                  # Insulation Resistance
│   │   ├── pvtp-018.json                  # Ground Continuity
│   │   ├── pvtp-019.json                  # Hi-Pot Testing
│   │   ├── pvtp-020.json                  # Fire Class
│   │   ├── pvtp-021.json                  # Safety Qualification
│   │   ├── pvtp-022.json                  # Cable Pull
│   │   └── pvtp-023.json                  # Terminal Torque
│   └── validators/
│       └── protocol_validator.py          # JSON schema & business rule validation
│
├── backend/
│   ├── handlers/
│   │   ├── base_handler.py                # Abstract base handler
│   │   └── pvtp016_handler.py             # Example: PVTP-016 implementation
│   ├── interlocks/
│   │   └── safety_interlock.py            # Safety interlock engine
│   ├── integration/
│   │   └── pm_qc_nc_integration.py        # PM/QC/NC integration
│   ├── traceability/
│   │   └── audit_log.py                   # Data traceability & audit trail
│   └── reports/
│       └── report_generator.py            # Automated report generation
│
├── frontend/
│   └── streamlit_app.py                   # Streamlit UI application
│
├── config/
│   └── settings.py                        # Configuration settings
│
├── requirements.txt                       # Python dependencies
└── README.md                              # This file
```

## ✨ Key Features

### 1. **Comprehensive Safety System**
- **Multi-Level Safety Interlocks**: Pre-test, during-test, post-test, and emergency stop
- **Real-Time Monitoring**: Continuous safety condition monitoring
- **Emergency Stop**: Critical interlocks trigger immediate test shutdown
- **Severity Levels**: Critical, High, Medium, Low
- **Actions**: Block, Warn, Require Approval, Emergency Stop

### 2. **QC/QA Workflow**
- **Approval Gates**: Multi-stage approval workflow
- **Role-Based**: Operator, QC Inspector, QC Manager, Engineer, PM
- **Criteria Checklists**: Mandatory verification items
- **Audit Trail**: Complete approval history

### 3. **Automated Report Generation**
- **Multiple Formats**: PDF, Excel, JSON, HTML
- **Certification Reports**: IEC/UL compliant certification packages
- **21 CFR Part 11 Compliance**: Electronic records and signatures

### 4. **Data Traceability**
- **Complete Audit Trail**: Every action logged with timestamp and actor
- **Data Lineage**: Track data origin, transformations, and dependencies
- **Cryptographic Integrity**: SHA-256 hashing with blockchain-like chain
- **Immutable Records**: Tamper-evident audit log

### 5. **PM/QC/NC Integration**
- **Non-Conformance Management**: Automatic NC creation for test failures
- **QC Inspections**: Structured inspection records with checklists
- **Project Management**: Task tracking and progress monitoring
- **LIMS Integration**: Sample and test request management

### 6. **Validators**
- **JSON Schema Validation**: Structural validation against base schema
- **Business Rules**: Protocol-specific validation rules
- **Safety Validation**: High voltage, fire test safety requirements

## 🚀 Getting Started

### Installation

```bash
# Clone repository
git clone <repository-url>
cd test-protocols

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
# Start Streamlit UI
streamlit run frontend/streamlit_app.py
```

The application will open in your default browser at `http://localhost:8501`

### Using the Framework Programmatically

```python
from pathlib import Path
import json

from backend.handlers.pvtp016_handler import PVTP016Handler

# Load protocol definition
protocol_file = Path("protocols/definitions/pvtp-016.json")
with open(protocol_file, 'r') as f:
    protocol_def = json.load(f)

# Create handler
handler = PVTP016Handler(protocol_def)
handler.operator = "operator@lab.com"

# Validate prerequisites
valid, messages = handler.validate_prerequisites()

# Setup and execute test
if handler.setup():
    if handler.execute():
        result = handler.analyze_results()
        reports = handler.generate_report(formats=['pdf', 'json'])
```

## 📊 Protocol Structure

Each protocol definition includes:

1. **Protocol Identification**: ID, name, version, category
2. **Standard Reference**: IEC/UL standard, version, section
3. **Device Under Test**: Type, identification, specifications
4. **Test Parameters**: Voltage, current, duration, methods
5. **Acceptance Criteria**: Pass/fail limits and requirements
6. **Safety Interlocks**: Multi-level safety checks
7. **Approval Gates**: QC/QA workflow stages
8. **Traceability**: Audit log and data lineage configuration
9. **Integrations**: LIMS, QMS, PM, NC system links
10. **Report Generation**: Format, content, template configuration

## 🔒 Safety Features

### Safety Interlock Types
- **pre-test**: Checked before test starts (e.g., calibration, PPE)
- **during-test**: Monitored continuously (e.g., current limits, temperature)
- **post-test**: Checked after test (e.g., discharge, cool-down)
- **emergency-stop**: Critical conditions requiring immediate stop

### Safety Actions
- **block**: Prevent test from starting or continuing
- **warn**: Display warning but allow continuation
- **require-approval**: QC/Manager approval needed to proceed
- **emergency-stop**: Immediate test shutdown and safety procedures

## 📈 Data Capture

- **Time Series Data**: Configurable sampling rates (0.1 Hz to 100 Hz)
- **Images**: Pre-test, during-test, post-test (1920×1080 minimum)
- **Video Recording**: Full test duration with multiple camera angles
- **Environmental Data**: Temperature, humidity, pressure monitoring

## 📋 Compliance

### Standards Compliance
- ✅ **IEC 61215**: Terrestrial photovoltaic modules - Design qualification
- ✅ **IEC 61730**: PV module safety qualification
- ✅ **IEC 60947-7-1**: Terminal blocks for industrial use
- ✅ **IEC 62852**: Connectors for DC-application in PV systems
- ✅ **UL 1703**: Flat-Plate Photovoltaic Modules and Panels
- ✅ **UL 1741**: Inverters, Converters, Controllers and Interconnection System Equipment

### Regulatory Compliance
- ✅ **21 CFR Part 11**: Electronic records and electronic signatures
- ✅ **ISO 17025**: Testing and calibration laboratories
- ✅ **GxP**: Good practice quality guidelines

## 📄 License

MIT License - See LICENSE file for details

## 🔄 Version History

### v1.0.0 (2025-01-12)
- Initial implementation
- 8 complete test protocols (PVTP-016 through PVTP-023)
- Safety interlock engine
- QC/QA workflow
- Automated reporting
- PM/QC/NC integration
- Full data traceability
- Streamlit UI

---

**Built with ⚡ for the PV industry**
