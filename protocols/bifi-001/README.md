# BIFI-001 Bifacial Performance Protocol

IEC 60904-1-2 compliant protocol for measuring bifacial photovoltaic device performance.

## Overview

This protocol provides a comprehensive framework for testing and analyzing bifacial solar modules, including:

- **Front and rear side I-V characterization**
- **Bifaciality factor measurement**
- **Performance validation and quality control**
- **Database integration for LIMS/QMS**
- **Interactive Streamlit UI**
- **Automated analysis and reporting**

## Structure

```
protocols/bifi-001/
├── schemas/              # JSON schemas and data templates
│   ├── protocol_config.json
│   └── data_template.json
├── python/              # Core Python modules
│   ├── __init__.py
│   ├── validator.py     # Data validation
│   ├── calculator.py    # Performance calculations
│   └── protocol.py      # Main protocol handler
├── db/                  # Database models and integration
│   ├── __init__.py
│   ├── models.py        # SQLAlchemy models
│   └── database.py      # Database manager
├── ui/                  # User interface components
│   └── streamlit_app.py # Streamlit application
├── tests/               # Unit tests
│   ├── test_validator.py
│   ├── test_calculator.py
│   ├── test_protocol.py
│   └── test_database.py
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Using Python API

```python
from protocols.bifi001.python import BifacialProtocol

# Initialize protocol
protocol = BifacialProtocol()

# Create test
metadata = {
    "operator": "John Doe",
    "test_date": "2025-11-13T10:00:00Z"
}

device_info = {
    "device_id": "MODULE-001",
    "manufacturer": "Solar Inc.",
    "model": "BiModule-500",
    "rated_power_front": 500,
    "rated_power_rear": 350,
    "bifaciality_factor": 0.70
}

test_conditions = {
    "front_irradiance": {"value": 1000, "spectrum": "AM1.5G"},
    "rear_irradiance": {"value": 150, "spectrum": "AM1.5G"},
    "temperature": {"value": 25},
    "stc_conditions": True
}

protocol.create_test(metadata, device_info, test_conditions)

# Add measurements
front_iv_data = [...]  # Your I-V curve data
protocol.add_iv_measurement("front", front_iv_data, 1000, 25000)

rear_iv_data = [...]
protocol.add_iv_measurement("rear", rear_iv_data, 150, 25000)

# Calculate bifacial parameters
bifacial_results = protocol.calculate_bifacial_parameters()

# Run validation
validation_results = protocol.run_validation()

# Analyze performance
analysis = protocol.analyze_performance()

# Generate report
report = protocol.generate_report_data()

# Save to file
protocol.save("test_results.json")
```

### Using Streamlit UI

```bash
# Run the interactive UI
streamlit run protocols/bifi-001/ui/streamlit_app.py
```

The UI provides:
- Step-by-step test creation
- I-V curve data entry (manual, CSV upload, or simulation)
- Real-time visualization
- Validation and analysis
- Database integration
- Report generation and export

## Features

### Validation

The protocol includes comprehensive validation:

- **Schema validation**: Ensures data conforms to IEC 60904-1-2 requirements
- **Irradiance validation**: Checks test conditions are appropriate
- **I-V curve quality**: Validates curve monotonicity and data quality
- **Parameter consistency**: Verifies calculated parameters are consistent
- **Calibration status**: Checks equipment calibration currency

### Calculations

Automated calculations include:

- **I-V parameters**: Isc, Voc, Pmax, Imp, Vmp, Fill Factor
- **Efficiency**: Front, rear, and equivalent bifacial efficiency
- **Bifaciality factor**: Measured bifaciality (rear Pmax / front Pmax)
- **Bifacial gain**: Performance gain from rear illumination
- **Uncertainty analysis**: Measurement uncertainty per IEC standards
- **Temperature coefficients**: Optional temp coefficient determination
- **STC interpolation**: Correct measurements to Standard Test Conditions

### Database Integration

SQLAlchemy models for LIMS/QMS integration:

- **BifacialTest**: Main test records
- **IVMeasurement**: Front/rear I-V measurements
- **BifacialResult**: Bifacial-specific results
- **QualityCheck**: Validation and QC records
- **CalibrationRecord**: Equipment calibration tracking
- **UncertaintyAnalysis**: Uncertainty analysis results

Supports SQLite, PostgreSQL, MySQL, and other SQLAlchemy-compatible databases.

## Testing

Run the test suite:

```bash
# Run all tests
python -m pytest protocols/bifi-001/tests/

# Run with coverage
python -m pytest protocols/bifi-001/tests/ --cov=protocols.bifi-001.python --cov=protocols.bifi-001.db

# Run specific test file
python -m pytest protocols/bifi-001/tests/test_validator.py -v
```

## API Reference

### BifacialValidator

Validates test data according to IEC 60904-1-2.

```python
from protocols.bifi001.python import BifacialValidator

validator = BifacialValidator()
results = validator.validate_all(test_data)
```

### BifacialCalculator

Performs bifacial performance calculations.

```python
from protocols.bifi001.python import BifacialCalculator

calculator = BifacialCalculator()
params = calculator.calculate_iv_parameters(iv_curve, area, irradiance)
bifaciality = calculator.calculate_bifaciality(front_pmax, rear_pmax)
```

### BifacialProtocol

Main protocol handler integrating all functionality.

```python
from protocols.bifi001.python import BifacialProtocol

protocol = BifacialProtocol()
protocol.create_test(metadata, device_info, test_conditions)
protocol.add_iv_measurement("front", iv_data, irradiance, area)
```

### DatabaseManager

Manages database operations for test data.

```python
from protocols.bifi001.db import DatabaseManager

db = DatabaseManager("postgresql://user:pass@localhost/testdb")
db.create_tables()
test = db.create_test(test_data)
```

## Standards Compliance

This protocol implements:

- **IEC 60904-1-2**: Measurement principles for bifacial photovoltaic devices
- **IEC 60904-1**: Measurement of photovoltaic current-voltage characteristics
- **IEC 60904-3**: Measurement principles for terrestrial PV solar devices

## Data Format

Test data is stored in JSON format according to the schema defined in `schemas/protocol_config.json`. See `schemas/data_template.json` for an example structure.

## Contributing

When contributing to this protocol:

1. Maintain IEC 60904-1-2 compliance
2. Add tests for new functionality
3. Update documentation
4. Follow existing code style

## License

See LICENSE file in repository root.

## References

- IEC 60904-1-2: Measurement principles for bifacial photovoltaic (PV) solar devices
- IEC 60904-1: Measurement of photovoltaic current-voltage characteristics
- ISO/IEC Guide 98-3: Uncertainty of measurement
