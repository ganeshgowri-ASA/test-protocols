# PERF-001: Performance Testing at Different Temperatures

## Overview

PERF-001 is a comprehensive testing protocol for measuring the temperature-dependent performance characteristics of photovoltaic (PV) modules in accordance with IEC 61853 standards. This protocol enables accurate determination of temperature coefficients for power, voltage, and current parameters.

## Features

- ✅ **IEC 61853 Compliant**: Full compliance with international testing standards
- 📊 **Interactive UI**: Streamlit-based interface with real-time data entry and visualization
- 📈 **Advanced Analytics**: Temperature coefficient calculation with statistical analysis
- 🔍 **Quality Assurance**: Comprehensive validation and QA checks
- 📉 **Plotly Visualizations**: Interactive temperature-power curves and multi-parameter analysis
- 💾 **Database Integration**: PostgreSQL/SQLite support with full traceability
- 🧪 **Extensive Testing**: Comprehensive unit test coverage
- 📋 **JSON Schema**: Structured data format for interoperability

## Directory Structure

```
protocols/perf-001-temp/
├── schema/
│   └── perf-001-schema.json          # JSON schema definition
├── python/
│   ├── perf_001_engine.py            # Calculation engine
│   └── validation.py                 # Validation module
├── database/
│   ├── schema.sql                    # PostgreSQL schema
│   └── models.py                     # SQLAlchemy ORM models
├── ui/
│   ├── streamlit_app.py              # Interactive Streamlit UI
│   └── visualizations.py             # Plotly visualization module
├── tests/
│   ├── test_perf_001_engine.py       # Engine tests
│   ├── test_validation.py            # Validation tests
│   └── requirements-test.txt         # Test dependencies
├── docs/
│   ├── user_guide.md                 # User documentation
│   ├── api_reference.md              # API documentation
│   └── examples.md                   # Usage examples
├── examples/
│   ├── example_test_data.json        # Sample test data
│   └── quickstart.py                 # Quick start script
└── README.md                          # This file
```

## Quick Start

### 1. Installation

```bash
# Install dependencies
pip install numpy scipy pandas plotly streamlit sqlalchemy

# Install testing dependencies (optional)
pip install -r tests/requirements-test.txt
```

### 2. Run Interactive UI

```bash
# Navigate to the UI directory
cd protocols/perf-001-temp/ui

# Launch Streamlit app
streamlit run streamlit_app.py
```

### 3. Programmatic Usage

```python
from perf_001_engine import PERF001Calculator, Measurement

# Create calculator
calc = PERF001Calculator(reference_temperature=25.0)

# Add measurements
measurements = [
    Measurement(temperature=15.0, pmax=330.5, voc=46.8, isc=9.12, vmp=38.2, imp=8.65),
    Measurement(temperature=25.0, pmax=320.0, voc=45.2, isc=9.18, vmp=37.0, imp=8.65),
    Measurement(temperature=50.0, pmax=290.0, voc=41.5, isc=9.30, vmp=34.2, imp=8.48),
    Measurement(temperature=75.0, pmax=260.5, voc=38.0, isc=9.42, vmp=31.5, imp=8.27),
]
calc.add_measurements(measurements)

# Calculate temperature coefficients
results = calc.calculate_all_coefficients()

# Print results
print(f"Pmax coefficient: {results['temp_coefficient_pmax']['value']:.4f} %/°C")
print(f"Voc coefficient: {results['temp_coefficient_voc']['value']:.4f} %/°C")
print(f"Isc coefficient: {results['temp_coefficient_isc']['value']:.4f} %/°C")
```

### 4. Validation

```python
from validation import validate_test_data

# Load test data
with open('test_data.json') as f:
    test_data = json.load(f)

# Validate
report = validate_test_data(test_data)

# Check results
if report.overall_passed:
    print("✓ Test data is valid")
else:
    print("✗ Validation failed")
    for error in report.get_errors():
        print(f"  - {error.message}")
```

## Test Procedure

### IEC 61853 Requirements

1. **Temperature Points**: Minimum 4 temperature points required
2. **Irradiance**: Fixed at 1000 W/m²
3. **Spectrum**: AM1.5G standard solar spectrum
4. **Temperature Range**: Recommend >30°C for accuracy

### Typical Test Sequence

1. **Setup**
   - Configure solar simulator at 1000 W/m² (±2%)
   - Calibrate temperature control system (±0.5°C)
   - Prepare IV curve tracer

2. **Measurements** (at each temperature point)
   - Set module temperature and stabilize (15-30 minutes)
   - Verify temperature uniformity across module
   - Record full IV curve
   - Extract key parameters: Pmax, Voc, Isc, Vmp, Imp

3. **Recommended Test Points**
   - 15°C (or lower if testing for cold climates)
   - 25°C (standard reference condition)
   - 50°C (typical operating condition)
   - 75°C (hot climate condition)

4. **Data Analysis**
   - Calculate fill factors
   - Perform linear regression for each parameter
   - Determine temperature coefficients
   - Validate data quality (R² > 0.95)

## Temperature Coefficients

### Physical Interpretation

- **Pmax Coefficient** (αPmax): Change in maximum power per degree Celsius
  - Typical range for c-Si: -0.35 to -0.50 %/°C
  - Negative value indicates power decreases with temperature

- **Voc Coefficient** (βVoc): Change in open circuit voltage per degree Celsius
  - Typical range for c-Si: -0.25 to -0.35 %/°C
  - Negative value due to semiconductor physics

- **Isc Coefficient** (γIsc): Change in short circuit current per degree Celsius
  - Typical range for c-Si: +0.03 to +0.08 %/°C
  - Positive value due to increased carrier generation

### Unit Conversions

Coefficients can be expressed in multiple units:
- **Absolute**: V/°C, A/°C, W/°C
- **Relative**: %/°C (normalized to STC value)
- **Per Kelvin**: Same magnitude as per Celsius

## Data Quality Checks

The protocol includes comprehensive quality validation:

### Critical Checks (Must Pass)
- ✓ Minimum 4 temperature measurements
- ✓ Irradiance at 1000 W/m²
- ✓ All required parameters present
- ✓ Power equation consistency (Pmax ≈ Vmp × Imp)

### Linearity Checks
- ✓ R² > 0.95 for Pmax vs Temperature
- ✓ R² > 0.90 for Voc and Isc (recommended)

### Physical Range Validation
- ✓ Fill factor: 0.50 - 0.90
- ✓ Voc: 0 - 100V (typical)
- ✓ Isc: 0 - 50A (typical)
- ✓ Pmax: 0 - 1000W (typical)

### Warnings
- ⚠️ Temperature range < 30°C (may reduce accuracy)
- ⚠️ Unusual coefficient values (outside typical ranges)
- ⚠️ Poor linearity (R² < 0.95)

## Database Schema

The protocol includes a complete PostgreSQL/SQLite schema with:

- **Test Records**: Main test information and results
- **Measurements**: Individual temperature point data
- **IV Curves**: Full I-V curve data storage
- **Traceability**: Links to related tests and QMS systems
- **Revision History**: Complete audit trail

### Key Features
- Foreign key constraints for data integrity
- Automatic timestamp tracking
- Calculated fields (fill factor, efficiency)
- Indexed for query performance
- Views for common queries

## API Reference

### Core Classes

#### `Measurement`
Represents a single temperature measurement point.

```python
Measurement(
    temperature: float,      # °C
    pmax: float,            # W
    voc: float,             # V
    isc: float,             # A
    vmp: float,             # V
    imp: float              # A
)
```

#### `PERF001Calculator`
Main calculation engine for temperature coefficients.

```python
calc = PERF001Calculator(reference_temperature=25.0)
calc.add_measurement(measurement)
calc.calculate_temp_coefficient_pmax()
calc.calculate_all_coefficients()
calc.validate_data_quality()
```

#### `PERF001Validator`
Validation and quality assurance.

```python
validator = PERF001Validator()
report = validator.validate_complete_test(test_data)
```

See [API Reference](docs/api_reference.md) for complete documentation.

## Testing

### Run Unit Tests

```bash
# Run all tests
cd tests/
python -m pytest test_perf_001_engine.py -v
python -m pytest test_validation.py -v

# Run with coverage
pytest --cov=../python --cov-report=html

# Run specific test
python test_perf_001_engine.py
```

### Test Coverage

- ✓ Measurement data structures
- ✓ Temperature coefficient calculations
- ✓ Unit conversions
- ✓ Data validation
- ✓ Quality checks
- ✓ Edge cases and error handling
- ✓ Numerical accuracy

## Visualization Examples

The protocol includes advanced Plotly visualizations:

1. **Temperature-Power Curve**
   - Scatter plot of measured data
   - Linear regression fit line
   - 95% confidence intervals
   - R² annotation

2. **Multi-Parameter Grid**
   - Pmax, Voc, Isc, and FF vs temperature
   - Individual regression lines
   - Subplots for comparison

3. **Normalized Comparison**
   - All parameters on 0-100% scale
   - Reference line at 100%
   - Easy visual comparison

4. **Coefficient Comparison**
   - Bar chart of calculated coefficients
   - Industry benchmark ranges
   - Pass/fail indicators

## Integration

### LIMS Integration
- JSON export compatible with most LIMS systems
- Unique test IDs for traceability
- Metadata fields for project tracking

### QMS Integration
- Revision history tracking
- Quality check documentation
- Audit trail maintenance

### Database Integration
- SQLAlchemy ORM for easy integration
- PostgreSQL recommended for production
- SQLite for development/testing

## Standards Compliance

### IEC 61853-1
- ✓ Temperature coefficient measurement procedures
- ✓ Minimum 4 temperature points
- ✓ Irradiance level (1000 W/m²)
- ✓ Data quality requirements (R² > 0.95)

### IEC 60904-1
- ✓ I-V characteristic measurement
- ✓ Parameter extraction methods

## Best Practices

1. **Temperature Stabilization**: Allow 15-30 minutes at each temperature point
2. **Temperature Uniformity**: Verify uniform temperature across module (±1°C)
3. **Irradiance Stability**: Maintain ±2% during measurement
4. **Multiple Sweeps**: Average 3-5 I-V sweeps per temperature
5. **Dark Resistance**: Check for shunts between measurements
6. **Data Quality**: Review R² values immediately after test

## Troubleshooting

### Poor Linearity (R² < 0.95)
- Check temperature sensor calibration
- Verify temperature stabilization at each point
- Review IV curve quality
- Check for module degradation

### Unusual Coefficients
- Verify module technology (different techs have different ranges)
- Check for measurement errors
- Review environmental conditions
- Consider module defects

### Data Validation Errors
- Review schema requirements
- Check for missing required fields
- Verify data types and units
- Ensure power equation consistency

## Contributing

Contributions are welcome! Please ensure:
- All tests pass
- Code follows PEP 8 style guide
- Documentation is updated
- Examples are provided

## License

This protocol implementation is part of the Test Protocols Framework.
See LICENSE file for details.

## References

1. IEC 61853-1:2011 - Photovoltaic (PV) module performance testing and energy rating - Part 1: Irradiance and temperature performance measurements and power rating
2. IEC 60904-1:2020 - Photovoltaic devices - Part 1: Measurement of photovoltaic current-voltage characteristics
3. King, D. L., et al. "Temperature coefficients for PV modules and arrays: measurement methods, difficulties, and results." NREL (1997)

## Support

For questions, issues, or contributions:
- Create an issue in the repository
- Refer to documentation in `docs/` directory
- Check examples in `examples/` directory

## Version History

- **1.0.0** (2025-11-13): Initial release
  - Complete IEC 61853 implementation
  - Interactive Streamlit UI
  - Comprehensive validation
  - Full test coverage
  - Production-ready database schema
