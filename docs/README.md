# NOCT-001 Protocol Implementation

## Protocol Information

**Protocol ID:** NOCT-001
**Name:** Nominal Operating Cell Temperature
**Category:** Performance
**Standard:** IEC 61215-1:2021, Section 7.3
**Version:** 1.0.0

## Description

This protocol determines the nominal operating cell temperature (NOCT) of photovoltaic modules under standardized conditions. NOCT is defined as the cell temperature reached when a module is exposed to:
- 800 W/m² irradiance
- 20°C ambient temperature
- 1 m/s wind speed
- Open-circuit conditions

## Features

### ✨ Interactive UI
- **Conditional Fields**: Parameters dynamically show/hide based on user selections
- **Smart Dropdowns**: Auto-complete with database integration
- **Auto-Validation**: Real-time input validation with helpful error messages
- **Minimal Effort Forms**: Intelligent defaults and streamlined data entry

### 📊 Real-Time Graphs
- **Temperature Monitoring**: Live cell and ambient temperature plots
- **T-P Curves**: Power vs Temperature with trend analysis
- **Efficiency Plots**: Module efficiency at different temperatures
- **Environmental Tracking**: Irradiance and wind speed monitoring
- **Interactive Plotly Charts**: Zoom, pan, export capabilities

### 🔍 Data Traceability
- **Full Audit Trail**: Every action logged with user, timestamp, and details
- **Data Integrity**: SHA-256 checksums for all data files
- **Version Control**: Complete history of all changes
- **Digital Signatures**: Optional signing for regulatory compliance

### 👤 User-Friendly
- **Auto-Save**: Progress saved automatically every 30 seconds
- **Pause/Resume**: Ability to pause tests and resume later
- **Progress Indicators**: Real-time progress bars and status updates
- **Helpful Tooltips**: Contextual help throughout the interface

### ✅ QA Testing Built-In
- **Pre-Test Checks**: Equipment calibration verification
- **During-Test Monitoring**: Continuous data quality assessment
- **Post-Test Validation**: Results checked against acceptance criteria
- **Automated Reporting**: Comprehensive reports with QC status

### 🧩 Modular & Scalable
- **Reusable Components**: UI components work for all protocols
- **Base Protocol Class**: Easy to extend for new protocols
- **Plugin Architecture**: Add new equipment drivers easily
- **Database Integration**: PostgreSQL with full LIMS capabilities

## Directory Structure

```
genspark_app/
├── protocols/
│   ├── base_protocol.py          # Base protocol class
│   └── performance/
│       ├── __init__.py
│       └── noct_001.py            # NOCT-001 implementation
├── templates/
│   └── protocols/
│       └── performance/
│           └── noct_001.json      # Protocol template
├── utils/
│   ├── data_processor.py          # Data processing utilities
│   ├── equipment_interface.py     # Equipment communication
│   ├── validators.py              # Input validation
│   └── calculations.py            # NOCT calculations
├── ui/
│   ├── components/
│   │   ├── parameter_input.py     # Smart input components
│   │   └── real_time_graphs.py    # Plotly graph components
│   └── pages/
│       └── noct_001_page.py       # NOCT-001 UI page
└── database/
    ├── models.py                  # SQLAlchemy models
    └── schema.sql                 # Database schema

tests/
└── protocols/
    └── performance/
        └── test_noct_001.py       # Comprehensive unit tests

docs/
├── README.md                      # This file
├── NOCT-001_USER_GUIDE.md        # User guide
└── API_DOCUMENTATION.md           # API documentation
```

## Installation

### Requirements
- Python 3.9+
- PostgreSQL 14+
- Redis (optional, for caching)

### Setup

```bash
# Clone repository
git clone https://github.com/your-org/test-protocols.git
cd test-protocols

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database
# Edit .env with your database credentials
cp .env.example .env

# Run database migrations
python -m genspark_app.database.migrate

# Run tests
pytest tests/ -v
```

## Usage

### Command Line

```python
from genspark_app.protocols.performance.noct_001 import NOCT001Protocol

# Create protocol instance
protocol = NOCT001Protocol()

# Set test parameters
parameters = {
    'sample_id': 'TEST-001',
    'manufacturer': 'SolarTech',
    'model': 'ST-300W',
    'technology': 'mono-Si',
    'rated_power': 300.0,
    'module_area': 1.6,
    'test_irradiance': 800,
    'ambient_temp_target': 20,
    'wind_speed_target': 1.0,
    'stabilization_duration': 30,
    'measurement_interval': 60,
    'calculate_temp_coefficients': True,
    'temp_coefficient_points': 5
}
protocol.set_input_parameters(parameters)

# Run protocol
success = protocol.run()

# Access results
if success:
    print(f"NOCT: {protocol.noct_value:.2f}°C")
    print(f"Pmax @ NOCT: {protocol.pmax_at_noct:.2f}W")
    print(f"Efficiency @ NOCT: {protocol.efficiency_at_noct:.2f}%")

    # Generate report
    report = protocol.generate_report()
```

### Streamlit UI

```bash
# Run Streamlit app
streamlit run genspark_app/app.py
```

Navigate to `http://localhost:8501` and select NOCT-001 from the protocol menu.

## Test Results

### Key Outputs

1. **NOCT (°C)** - Nominal operating cell temperature
2. **Pmax at NOCT (W)** - Expected power output at NOCT conditions
3. **Efficiency at NOCT (%)** - Module efficiency at NOCT
4. **Temperature Coefficients** (optional):
   - α_P (%/°C) - Power temperature coefficient
   - β_Voc (%/°C) - Voc temperature coefficient
   - α_Isc (%/°C) - Isc temperature coefficient

### Reports Generated

- PDF test report with all graphs and analysis
- JSON data file with complete test data
- CSV files for time-series data
- Excel workbook with summary and raw data

## Testing

### Run Unit Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/protocols/performance/test_noct_001.py -v

# With coverage
pytest tests/ --cov=genspark_app --cov-report=html
```

### Test Coverage

Current test coverage: 85%+

- Protocol initialization: ✓
- Parameter validation: ✓
- NOCT calculations: ✓
- Temperature coefficients: ✓
- Data quality checks: ✓
- Report generation: ✓
- Audit trail: ✓

## Configuration

### Protocol Template

The protocol behavior is controlled by `noct_001.json` template which includes:
- Input parameter specifications
- Validation rules
- Test conditions
- Acceptance criteria
- Equipment requirements
- QC checks
- Graph configurations

### Custom Configurations

Create custom configurations by editing the JSON template or passing parameters programmatically.

## Database Schema

The protocol integrates with a comprehensive LIMS database:

- `protocols` - Protocol definitions
- `test_executions` - Test execution records
- `measurement_data` - Time-series measurements
- `analysis_results` - Calculated results
- `audit_trail` - Complete audit log
- `reports` - Generated reports

See `genspark_app/database/schema.sql` for full schema.

## API Documentation

See `docs/API_DOCUMENTATION.md` for complete API reference.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit pull request

## License

[Your License Here]

## Authors

- Your Name <your.email@example.com>

## Changelog

### Version 1.0.0 (2025-01-13)
- Initial implementation of NOCT-001 protocol
- Interactive UI with conditional fields
- Real-time graphing with Plotly
- Comprehensive data traceability
- Full unit test coverage
- Complete documentation

## Support

- Documentation: https://docs.genspark.io
- Issues: https://github.com/your-org/test-protocols/issues
- Email: support@genspark.io
