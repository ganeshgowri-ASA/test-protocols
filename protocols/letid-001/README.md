# LETID-001: Light and Elevated Temperature Induced Degradation Test

## Overview

**Protocol ID:** LETID-001
**Version:** 1.0.0
**Standard:** IEC 61215-2:2021
**Category:** Reliability Testing
**Test Type:** Degradation Analysis

This protocol implements the Light and Elevated Temperature Induced Degradation (LeTID) test for photovoltaic modules according to IEC 61215-2:2021 standards. LeTID is a reversible degradation mechanism observed primarily in PERC (Passivated Emitter and Rear Cell) technology solar modules when exposed to light and elevated temperature.

## Test Description

### Purpose

To evaluate the susceptibility of PV modules to light and elevated temperature induced degradation and to quantify power loss during extended exposure.

### Test Conditions

- **Module Temperature:** 75°C ± 3°C
- **Irradiance:** 1000 W/m² ± 50 W/m² (AM1.5G spectrum)
- **Duration:** 300 hours
- **Measurement Interval:** Every 24 hours

### Acceptance Criteria

| Criterion | Threshold | Severity |
|-----------|-----------|----------|
| Maximum Power Degradation | ≤ 5.0% | Fail |
| Stabilized Degradation | ≤ 3.0% | Warning |
| Minimum Recovery | ≥ 95.0% | Info |

## Directory Structure

```
protocols/letid-001/
├── schemas/
│   └── protocol.json          # JSON schema defining test protocol
├── python/
│   ├── validation.py          # Data validation module
│   └── processor.py           # Data processing and analysis
├── sql/
│   └── schema.sql             # Database schema for time-series data
├── ui/
│   └── ui_config.json         # Streamlit/GenSpark UI configuration
├── tests/
│   └── test_letid001.py       # Comprehensive test suite
└── README.md                  # This file
```

## Quick Start

### 1. Installation

```bash
# Install required Python packages
pip install numpy pandas pytest

# If using database integration
pip install psycopg2-binary  # PostgreSQL
# or
pip install mysql-connector-python  # MySQL
```

### 2. Database Setup

```bash
# Initialize database schema (PostgreSQL example)
psql -U your_user -d your_database -f sql/schema.sql
```

### 3. Running Tests

```bash
# Run the test suite
cd tests
pytest test_letid001.py -v

# Run with coverage
pytest test_letid001.py --cov=../python --cov-report=html
```

## Usage Examples

### Validating Sample Information

```python
from validation import LETID001Validator

# Create validator
validator = LETID001Validator('schemas/protocol.json')

# Sample information
sample_info = {
    'module_id': 'MOD-12345',
    'manufacturer': 'SampleSolar Inc.',
    'model': 'SS-360-PERC',
    'serial_number': 'SN-2025-001',
    'cell_technology': 'mono-PERC',
    'rated_power': 360.0
}

# Validate
if validator.validate_sample_info(sample_info):
    print("Sample information is valid")
else:
    print("Validation errors:", validator.errors)
```

### Processing Time Series Data

```python
from processor import LETID001Processor
import pandas as pd

# Create processor
processor = LETID001Processor('schemas/protocol.json')

# Time series data (example)
time_series = [
    {'elapsed_hours': 0, 'pmax': 360.5, 'module_temp': 75.0, 'irradiance': 1000},
    {'elapsed_hours': 24, 'pmax': 359.8, 'module_temp': 75.2, 'irradiance': 1005},
    # ... more measurements
]

# Process data
initial_pmax = 360.5
df = processor.process_time_series(time_series, initial_pmax)

# Calculate statistics
stats = processor.calculate_statistics(df)
print("Test Statistics:", stats)

# Fit degradation model
model = processor.fit_degradation_model(df)
print("Degradation Model:", model)
```

### Complete Test Validation

```python
from validation import LETID001Validator

validator = LETID001Validator('schemas/protocol.json')

test_data = {
    'sample_info': {...},
    'initial_characterization': {...},
    'time_series': [...],
    'final_characterization': {...}
}

is_valid, report = validator.validate_complete_test(test_data)

if is_valid:
    print("Test data is valid")
    print("Validated sections:", report['sections_validated'])
else:
    print("Validation failed")
    print("Errors:", report['errors'])
```

### Generating Analysis Report

```python
from processor import LETID001Processor

processor = LETID001Processor('schemas/protocol.json')

# Complete test data
test_data = {
    'sample_info': sample_info,
    'initial_characterization': initial_measurement,
    'time_series': time_series_data,
    'final_characterization': final_measurement
}

# Generate report
report = processor.generate_analysis_report(test_data)

# Export to JSON
processor.export_to_json(report, 'letid_analysis_report.json')

# Export time series to CSV
df = processor.process_time_series(test_data['time_series'], initial_pmax)
processor.export_to_csv(df, 'letid_time_series.csv')
```

## Data Format Specifications

### Sample Information

```json
{
  "module_id": "MOD-12345",
  "manufacturer": "SampleSolar Inc.",
  "model": "SS-360-PERC",
  "serial_number": "SN-2025-001",
  "cell_technology": "mono-PERC",
  "rated_power": 360.0
}
```

### Initial/Final Characterization

```json
{
  "pmax": 360.5,
  "voc": 48.2,
  "isc": 9.8,
  "vmp": 40.1,
  "imp": 8.99,
  "fill_factor": 76.5
}
```

### Periodic Measurement

```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "elapsed_hours": 24.0,
  "pmax": 358.2,
  "voc": 48.1,
  "isc": 9.75,
  "module_temp": 75.5,
  "irradiance": 1005.0
}
```

## Database Schema

### Tables

1. **letid001_test_sessions** - Main test session information
2. **letid001_initial_characterization** - Initial I-V measurements
3. **letid001_time_series** - Periodic monitoring data
4. **letid001_final_characterization** - Final I-V measurements
5. **letid001_results** - Calculated results and analysis
6. **letid001_audit_log** - Audit trail

### Key Features

- Automatic timestamp updates
- Calculated fields via triggers
- Data integrity constraints
- Comprehensive indexing
- Audit logging

## UI Configuration

The `ui/ui_config.json` file defines the Streamlit/GenSpark interface:

### Main Sections

1. **Test Overview** - Dashboard and status
2. **Test Setup** - Sample information and configuration
3. **Data Entry** - Manual measurement entry
4. **Live Monitoring** - Real-time charts and metrics
5. **Analysis** - Post-test analysis and reporting
6. **Reports** - Export and documentation

### Key Features

- Real-time validation
- Interactive charts (degradation curve, environmental conditions)
- Metric cards with threshold alerts
- Customizable dashboards
- Multiple export formats (CSV, JSON, Excel, PDF)

## Validation Rules

### Automatic Validation

- **Type checking** - Ensures correct data types
- **Required fields** - Validates all mandatory fields present
- **Range validation** - Checks values within acceptable ranges
- **Enum validation** - Validates against allowed values
- **Temporal ordering** - Ensures chronological measurements

### Test Conditions Validation

- Temperature: 75°C ± 3°C
- Irradiance: 1000 W/m² ± 50 W/m²
- Measurement intervals: ±50% tolerance

## Analysis Features

### Calculated Metrics

- **Power Degradation (%)** = ((Final_Pmax - Initial_Pmax) / Initial_Pmax) × 100
- **Degradation Rate (%/hour)** = Power_Degradation / Exposure_Hours
- **Normalized Power (%)** = (Current_Pmax / Initial_Pmax) × 100

### Statistical Analysis

- Mean, standard deviation, min/max for all parameters
- Environmental condition stability
- Measurement quality assessment

### Degradation Modeling

- Linear model fitting
- Exponential decay model (when applicable)
- R² goodness-of-fit
- Prediction at 300 hours

### Stabilization Detection

Automatically detects when degradation has stabilized based on:
- Configurable time window (default: 48 hours)
- Maximum variation threshold (default: 0.5%)

## Testing

### Test Coverage

The test suite (`tests/test_letid001.py`) includes:

- **Validation Tests**
  - Sample information validation
  - Measurement validation
  - Time series validation
  - Acceptance criteria checking
  - Complete test validation
  - Format validation (module ID, serial number)

- **Processing Tests**
  - Degradation calculations
  - Time series processing
  - Statistical calculations
  - Model fitting
  - Report generation

- **Integration Tests**
  - Complete workflow validation
  - End-to-end processing

### Running Tests

```bash
# Run all tests
pytest tests/test_letid001.py -v

# Run specific test class
pytest tests/test_letid001.py::TestSampleInfoValidation -v

# Run with coverage
pytest tests/test_letid001.py --cov=python --cov-report=term-missing
```

## Integration

### LIMS Integration

Configure in `ui_config.json`:

```json
"integrations": {
  "lims": {
    "enabled": true,
    "endpoint": "/api/lims/v1",
    "sync_on_complete": true
  }
}
```

### QMS Integration

```json
"qms": {
  "enabled": true,
  "endpoint": "/api/qms/v1"
}
```

### Database Auto-Save

```json
"database": {
  "enabled": true,
  "auto_save": true,
  "save_interval": 300
}
```

## Reporting

### Supported Formats

- **CSV** - Time series data export
- **JSON** - Complete test data and analysis
- **Excel** - Formatted workbooks with charts
- **PDF** - Professional test reports (IEC 61215 template)

### Report Sections

1. Test Summary
2. Sample Information
3. Test Conditions
4. Measurement Results
5. Degradation Analysis
6. Pass/Fail Criteria
7. Time Series Plots
8. Conclusions

## Best Practices

### Test Execution

1. Perform visual inspection before test
2. Allow module to stabilize at test temperature
3. Verify light source spectrum
4. Take initial I-V curve at STC
5. Monitor environmental conditions continuously
6. Perform periodic measurements at consistent intervals
7. Document any anomalies
8. Take final I-V curve at STC

### Data Quality

- Maintain temperature within ±3°C
- Maintain irradiance within ±50 W/m²
- Verify measurement equipment calibration
- Check for data outliers
- Document measurement conditions
- Review data in real-time

### Analysis

- Review degradation curve for anomalies
- Check for stabilization
- Compare against similar modules
- Document environmental variations
- Include uncertainty analysis

## Troubleshooting

### Common Issues

**Issue:** Validation fails for sample info
**Solution:** Check all required fields are present and cell_technology is valid

**Issue:** Time series validation warnings
**Solution:** Ensure measurements are in chronological order and intervals are consistent

**Issue:** Model fitting fails
**Solution:** Check for sufficient data points (minimum 3, recommended 10+)

**Issue:** Database insertion errors
**Solution:** Verify schema is initialized and constraints are met

## References

1. IEC 61215-2:2021 - Terrestrial photovoltaic (PV) modules - Design qualification and type approval - Part 2: Test procedures
2. IEC 61853 series - Photovoltaic module performance testing and energy rating
3. IEEE Std 1547-2018 - Standard for Interconnection and Interoperability of Distributed Energy Resources

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-01-15 | Initial release |

## License

See LICENSE file in repository root.

## Contact

For questions or issues, please refer to the project repository.
