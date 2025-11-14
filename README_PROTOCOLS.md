# PV Testing Protocol Framework - Electrical Performance Protocols (Batch 1)

## Overview

This repository contains a comprehensive, modular PV testing protocol framework with JSON-based dynamic templates for Streamlit UI, featuring automated analysis, charting, QC checks, and report generation. This batch implements 6 electrical performance characterization protocols.

## Implemented Protocols

### Session 7-12: Electrical Performance & Characterization

| Protocol ID | Name | Key Features |
|------------|------|--------------|
| **PVTP-010** | Flash Test / STC Performance | STC correction algorithms, uncertainty analysis (GUM method) |
| **PVTP-011** | I-V Curve Characterization | Automated parameter extraction (Voc, Isc, Pmax, FF, Rs, Rsh), single/two-diode model fitting |
| **PVTP-012** | Low Irradiance Performance | Low-light behavior (200W/m², 500W/m²), bifacial corrections, WLRF calculation |
| **PVTP-013** | Temperature Coefficient | Automated temperature sweep, coefficient calculation (α, β, γ), regression analysis |
| **PVTP-014** | Spectral Response / QE | Wavelength-dependent response, EQE/IQE curves, integrated Jsc |
| **PVTP-015** | Dark I-V / Shunt Analysis | Recombination analysis, defect identification, diode parameter extraction |

## Project Structure

```
test-protocols/
├── config.py                      # Global configuration
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
│
├── protocols/                     # Protocol templates
│   ├── templates/                 # JSON protocol definitions
│   │   ├── PVTP-010_flash_test_stc.json
│   │   ├── PVTP-011_iv_curve_characterization.json
│   │   ├── PVTP-012_low_irradiance_performance.json
│   │   ├── PVTP-013_temperature_coefficient.json
│   │   ├── PVTP-014_spectral_response.json
│   │   └── PVTP-015_dark_iv_analysis.json
│   └── schemas/                   # JSON schemas for validation
│
├── backend/                       # Backend processing
│   ├── database.py                # Database configuration
│   ├── models/                    # SQLAlchemy models
│   │   └── protocol.py            # Protocol, TestExecution, QC models
│   ├── validators/                # Pydantic validators
│   │   ├── base.py                # Base validation models
│   │   └── electrical.py          # Electrical protocol validators
│   ├── protocols/                 # Protocol handlers
│   │   ├── base.py                # Base handler & analysis mixins
│   │   ├── electrical_pvtp010.py  # PVTP-010 handler
│   │   ├── electrical_pvtp011.py  # PVTP-011 handler
│   │   ├── electrical_pvtp012.py  # PVTP-012 handler
│   │   ├── electrical_pvtp013.py  # PVTP-013 handler
│   │   ├── electrical_pvtp014.py  # PVTP-014 handler
│   │   └── electrical_pvtp015.py  # PVTP-015 handler
│   ├── reports/                   # Report generation
│   └── api/                       # REST API endpoints
│
└── streamlit_app/                 # Streamlit UI
    ├── app.py                     # Main application & dashboard
    ├── pages/                     # Protocol-specific pages
    │   ├── test_pvtp_010.py       # PVTP-010 UI
    │   ├── test_pvtp_011.py       # PVTP-011 UI
    │   ├── test_pvtp_012.py       # PVTP-012 UI
    │   ├── test_pvtp_013.py       # PVTP-013 UI
    │   ├── test_pvtp_014.py       # PVTP-014 UI
    │   └── test_pvtp_015.py       # PVTP-015 UI
    ├── components/                # Reusable UI components
    └── utils/                     # Utility functions

```

## Features

### 1. JSON-Based Protocol Templates

Each protocol is defined in a comprehensive JSON template that includes:
- **Metadata**: Version control, standards references, revision history
- **Inputs**: Required and optional input fields with validation rules
- **Measurements**: Structured measurement data with uncertainties
- **Analysis**: Automated calculations and algorithms
- **Charts**: Chart specifications for data visualization
- **QC Checks**: Automatic and manual quality control checks
- **Maintenance**: Equipment calibration and PM schedules
- **Project Management**: Duration estimates, skills required, deliverables
- **Nonconformance**: NC triggers and workflow definitions

### 2. Backend Processing

#### Protocol Handlers
- **Base Handler**: Common functionality for all protocols
- **IVAnalysisMixin**: I-V curve parameter extraction and model fitting
- **StatisticalAnalysisMixin**: Regression, uncertainty analysis
- **Specialized Handlers**: Protocol-specific analysis (STC correction, temperature coefficients, etc.)

#### Data Validation
- **Pydantic Models**: Runtime validation with type checking
- **Business Logic**: Range validation, consistency checks
- **Error Reporting**: Clear validation error messages

#### Database Models
- **Protocol**: Template definitions
- **TestExecution**: Test instances
- **Measurement**: Individual measurements
- **QCResult**: Quality control results
- **Report**: Generated reports
- **Nonconformance**: Issue tracking
- **Equipment**: Calibration tracking
- **User**: Operator management

### 3. Streamlit UI

#### Main Dashboard
- Active test monitoring
- Recent test activity
- Protocol distribution charts
- Quick access to protocols

#### Protocol-Specific Pages
- Step-by-step workflow (Sample Info → Measurements → Analysis → QC/Reports)
- Real-time data validation
- Interactive charts
- Automated QC checks
- Report generation

### 4. Analysis Capabilities

#### PVTP-010: Flash Test
- IEC 60891 STC correction
- GUM uncertainty analysis
- Performance ratio calculation

#### PVTP-011: I-V Characterization
- Voc, Isc, Pmax, FF extraction
- Series resistance (Rs) calculation
- Shunt resistance (Rsh) calculation
- Single/two-diode model fitting

#### PVTP-012: Low Irradiance
- Weak Light Response Factor (WLRF)
- Current-irradiance linearity
- Relative efficiency at 200/500/800 W/m²
- Bifacial performance analysis

#### PVTP-013: Temperature Coefficients
- α (Isc), β (Voc), γ (Pmax) calculation
- Linear regression with R² quality metrics
- Comparison to datasheet values
- Bandgap estimation

#### PVTP-014: Spectral Response
- EQE/IQE spectrum calculation
- Integrated Jsc from spectrum
- Loss analysis (reflection, recombination)
- Band edge determination

#### PVTP-015: Dark I-V
- Diode parameter extraction (I0, n, Rs, Rsh)
- Recombination mechanism analysis
- Defect identification (shunt type, breakdown)
- Comparison to light I-V

## Installation & Setup

### Prerequisites
- Python 3.9+
- PostgreSQL (optional, SQLite by default)

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
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

4. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize database:**
```bash
python -c "from backend.database import init_db; init_db()"
```

### Running the Application

#### Streamlit UI
```bash
streamlit run streamlit_app/app.py
```
Access at: http://localhost:8501

#### Backend API (optional)
```bash
uvicorn backend.api.main:app --reload
```
Access at: http://localhost:8000

## Usage Guide

### 1. Running a Test

1. Navigate to **Dashboard** → Select protocol
2. Enter **Sample Information** (required fields marked with *)
3. Input **Measurement Data**
4. Click **Process Measurements**
5. Review **Analysis Results**
6. Check **QC Status**
7. Generate **Reports**

### 2. Quality Control

Automated QC checks run after analysis:
- **Critical**: Must pass for test acceptance
- **Warning**: Requires review but may be acceptable
- **Info**: Informational only

Manual QC checks must be completed by operator.

### 3. Report Generation

Available formats:
- **Test Report (PDF)**: Complete test documentation
- **Certificate (PDF)**: Certified results for passing tests
- **Data Export (Excel)**: Full data with charts
- **Raw Data (CSV)**: Measurement data only

## Integration

### LIMS Integration
Set `LIMS_API_URL` and `LIMS_API_KEY` in environment

### QMS Integration
Set `QMS_API_URL` and `QMS_API_KEY` in environment

### Project Management Dashboard
Set `PM_DASHBOARD_URL` and `PM_API_KEY` in environment

## Protocol Standards

All protocols comply with:
- **IEC 60904 series**: PV device measurement standards
- **IEC 61215 series**: PV module design qualification
- **IEC 61853 series**: PV module performance testing
- **ASTM E standards**: American testing standards
- **GUM**: Guide to Uncertainty in Measurement

## Data Traceability

Complete traceability chain:
1. **Raw Measurements** → Stored with timestamps and uncertainties
2. **Analysis Results** → Linked to measurement data
3. **QC Checks** → Tracked with operator and timestamp
4. **Reports** → Version controlled with test execution reference
5. **Nonconformances** → Root cause and corrective actions documented

## Equipment Management

### Calibration Tracking
- Automatic calibration expiry warnings
- Traceability to calibration lab
- Calibration certificate storage

### Preventive Maintenance
- Scheduled PM tasks
- Maintenance history logging
- Equipment availability status

## Development

### Adding a New Protocol

1. **Create JSON template** in `protocols/templates/`
2. **Create Pydantic validators** in `backend/validators/`
3. **Implement handler** in `backend/protocols/`
4. **Create Streamlit page** in `streamlit_app/pages/`
5. **Add to navigation** in `streamlit_app/app.py`

### Database Migrations

Using Alembic:
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Testing

```bash
# Run unit tests
pytest tests/unit

# Run integration tests
pytest tests/integration

# Generate coverage report
pytest --cov=backend --cov-report=html
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-protocol`)
3. Commit changes (`git commit -am 'Add new protocol'`)
4. Push to branch (`git push origin feature/new-protocol`)
5. Create Pull Request

## License

[MIT License](LICENSE)

## Authors

PV Testing Lab Development Team

## Version History

- **v1.0.0** (2025-01-12): Initial release with 6 electrical protocols (PVTP-010 through PVTP-015)

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Contact: support@pvtestinglab.com

## Acknowledgments

- IEC Technical Committee 82: Solar photovoltaic energy systems
- NREL: National Renewable Energy Laboratory
- PTB: Physikalisch-Technische Bundesanstalt (German National Metrology Institute)
