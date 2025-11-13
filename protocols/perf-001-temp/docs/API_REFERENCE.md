# PERF-001 API Reference

## Overview

This document provides complete API documentation for the PERF-001 temperature performance testing protocol.

## Python Modules

### `perf_001_engine.py`

Main calculation engine for temperature coefficient analysis.

#### Classes

##### `Measurement`

Represents a single temperature measurement point.

**Constructor:**
```python
Measurement(
    temperature: float,           # Module temperature in °C
    pmax: float,                 # Maximum power in W
    voc: float,                  # Open circuit voltage in V
    isc: float,                  # Short circuit current in A
    vmp: float,                  # Voltage at MPP in V
    imp: float,                  # Current at MPP in A
    fill_factor: Optional[float] = None,  # Auto-calculated if None
    efficiency: Optional[float] = None,   # Must call calculate_efficiency()
    iv_curve: Optional[Dict] = None,      # IV curve data
    timestamp: Optional[str] = None       # ISO 8601 timestamp
)
```

**Methods:**

- `calculate_efficiency(module_area: float, irradiance: float = 1000) -> float`
  - Calculate module efficiency
  - Returns: Efficiency in percent

- `to_dict() -> Dict[str, Any]`
  - Convert measurement to dictionary
  - Returns: Dictionary representation

**Properties:**
- `fill_factor`: Automatically calculated as Pmax / (Voc × Isc)
- `timestamp`: Auto-generated if not provided

---

##### `TemperatureCoefficient`

Stores temperature coefficient with statistical metrics.

**Constructor:**
```python
TemperatureCoefficient(
    value: float,                    # Coefficient value
    unit: str,                       # Unit (e.g., "%/°C", "V/°C")
    r_squared: float,                # R² of linear fit
    std_error: Optional[float] = None,
    confidence_interval_95: Optional[Tuple[float, float]] = None
)
```

**Methods:**
- `to_dict() -> Dict[str, Any]`: Convert to dictionary

---

##### `PERF001Calculator`

Main calculation engine for temperature coefficients.

**Constructor:**
```python
PERF001Calculator(reference_temperature: float = 25.0)
```

**Methods:**

- `add_measurement(measurement: Measurement) -> None`
  - Add single measurement to calculator

- `add_measurements(measurements: List[Measurement]) -> None`
  - Add multiple measurements

- `calculate_temp_coefficient_pmax() -> TemperatureCoefficient`
  - Calculate Pmax temperature coefficient
  - Returns: TemperatureCoefficient in %/°C
  - Raises: ValueError if < 4 measurements

- `calculate_temp_coefficient_voc(unit: str = "V/°C") -> TemperatureCoefficient`
  - Calculate Voc temperature coefficient
  - Args:
    - `unit`: "V/°C", "mV/°C", or "%/°C"
  - Returns: TemperatureCoefficient in specified unit

- `calculate_temp_coefficient_isc(unit: str = "A/°C") -> TemperatureCoefficient`
  - Calculate Isc temperature coefficient
  - Args:
    - `unit`: "A/°C", "mA/°C", or "%/°C"
  - Returns: TemperatureCoefficient in specified unit

- `calculate_normalized_power_at_temp(target_temp: float) -> float`
  - Calculate predicted power at any temperature
  - Returns: Predicted power in W

- `calculate_all_coefficients() -> Dict[str, Any]`
  - Calculate all temperature coefficients
  - Returns: Complete results dictionary

- `validate_data_quality() -> Dict[str, Any]`
  - Perform quality checks on data
  - Returns: Quality check results

- `generate_report_data() -> Dict[str, Any]`
  - Generate complete test report
  - Returns: Full report data

---

##### `PERF001Validator`

Validates test data against schema and physical constraints.

**Static Methods:**

- `validate_against_schema(data: Dict, schema: Dict) -> Tuple[bool, List[str]]`
  - Validate data against JSON schema
  - Returns: (is_valid, error_messages)

- `validate_physical_constraints(measurements: List[Measurement]) -> Tuple[bool, List[str]]`
  - Validate physical constraints
  - Checks: Power equation, FF range, Vmp < Voc, Imp < Isc
  - Returns: (is_valid, error_messages)

**Functions:**

- `create_sample_data() -> Dict[str, Any]`
  - Generate sample test data for demonstration
  - Returns: Complete test data dictionary

---

### `validation.py`

Comprehensive validation and quality assurance module.

#### Enums

##### `ValidationLevel`

Validation severity levels.

```python
class ValidationLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
```

#### Classes

##### `ValidationResult`

Single validation check result.

**Attributes:**
- `check_name: str` - Name of the check
- `passed: bool` - Whether check passed
- `level: ValidationLevel` - Severity level
- `message: str` - Human-readable message
- `details: Optional[Dict]` - Additional details

**Methods:**
- `to_dict() -> Dict[str, Any]`: Convert to dictionary

---

##### `ValidationReport`

Complete validation report.

**Attributes:**
- `test_id: str` - Test identifier
- `overall_passed: bool` - Overall pass/fail status
- `results: List[ValidationResult]` - All check results
- `summary: Dict[str, int]` - Summary statistics

**Methods:**

- `to_dict() -> Dict[str, Any]`
  - Convert report to dictionary

- `get_errors() -> List[ValidationResult]`
  - Get all error-level failures
  - Returns: List of failed ERROR or CRITICAL checks

- `get_warnings() -> List[ValidationResult]`
  - Get all warning-level failures
  - Returns: List of failed WARNING checks

---

##### `PERF001Validator`

Complete test data validator.

**Methods:**

- `validate_complete_test(test_data: Dict[str, Any]) -> ValidationReport`
  - Perform complete validation
  - Runs all checks: protocol info, specimen, conditions, measurements, results, metadata
  - Returns: ValidationReport

**Functions:**

- `validate_test_data(test_data: Dict[str, Any]) -> ValidationReport`
  - Convenience function for complete validation
  - Returns: ValidationReport

---

### `visualizations.py`

Advanced Plotly visualization module.

#### Classes

##### `PlotConfig`

Configuration for plot styling.

**Attributes:**
- `template: str = "plotly_white"`
- `color_scheme: List[str]` - Color palette
- `font_family: str = "Arial, sans-serif"`
- `title_font_size: int = 18`
- `axis_font_size: int = 12`

---

##### `PERF001Visualizer`

Visualization generator for test data.

**Constructor:**
```python
PERF001Visualizer(config: Optional[PlotConfig] = None)
```

**Methods:**

- `plot_temp_power_regression(temperatures, pmax_values, show_confidence=True) -> go.Figure`
  - Temperature vs power with regression and confidence intervals
  - Returns: Plotly Figure

- `plot_all_parameters_grid(temperatures, pmax, voc, isc, fill_factors, efficiency=None) -> go.Figure`
  - Multi-parameter grid plot
  - Returns: Plotly Figure with subplots

- `plot_normalized_comparison(temperatures, pmax, voc, isc, reference_temp=25.0) -> go.Figure`
  - Normalized comparison (all on 0-100% scale)
  - Returns: Plotly Figure

- `plot_coefficient_comparison(coef_pmax, coef_voc, coef_isc, industry_benchmarks=None) -> go.Figure`
  - Bar chart comparing coefficients with benchmarks
  - Returns: Plotly Figure

- `plot_3d_surface(temperatures, irradiances, power_matrix) -> go.Figure`
  - 3D surface plot for temperature and irradiance
  - Returns: Plotly Figure with 3D surface

- `create_dashboard(test_data: Dict[str, Any]) -> go.Figure`
  - Comprehensive dashboard with multiple visualizations
  - Returns: Plotly Figure

---

## Database Models

### `models.py`

SQLAlchemy ORM models.

#### Classes

##### `PERF001Test`

Main test record.

**Key Columns:**
- `test_id` (PK): Test identifier
- `protocol_id`: "PERF-001"
- `module_id`: Module serial number
- `manufacturer`, `model`, `technology`: Module info
- `temp_coef_*`: Calculated coefficients
- `test_date`, `test_facility`, `operator`: Metadata
- `project_id`, `lims_id`: Traceability

**Relationships:**
- `measurements`: One-to-many with PERF001Measurement
- `related_tests`: One-to-many with PERF001RelatedTest
- `revisions`: One-to-many with PERF001Revision

---

##### `PERF001Measurement`

Individual temperature measurement.

**Key Columns:**
- `measurement_id` (PK): Auto-increment
- `test_id` (FK): Parent test
- `temperature`: Test temperature
- `pmax`, `voc`, `isc`, `vmp`, `imp`: Electrical parameters
- `fill_factor`, `efficiency`: Calculated values

---

##### `PERF001IVCurve`

IV curve data storage.

**Key Columns:**
- `curve_id` (PK)
- `measurement_id` (FK)
- `voltage_data`: JSON array of voltage points
- `current_data`: JSON array of current points

**Methods:**
- `set_voltage_data(data: List[float])`
- `get_voltage_data() -> List[float]`
- `set_current_data(data: List[float])`
- `get_current_data() -> List[float]`

---

## JSON Schema

See `schema/perf-001-schema.json` for complete JSON schema definition.

### Top-Level Structure

```json
{
  "protocol_info": { ... },
  "test_specimen": { ... },
  "test_conditions": { ... },
  "measurements": [ ... ],
  "calculated_results": { ... },
  "quality_checks": { ... },
  "metadata": { ... }
}
```

### Required Fields

**Protocol Info:**
- `protocol_id`: "PERF-001"
- `protocol_name`: "Performance at Different Temperatures"
- `standard`: "IEC 61853"
- `version`: Semantic version

**Test Specimen:**
- `module_id`: Unique identifier
- `manufacturer`: Manufacturer name
- `model`: Model number
- `technology`: PV technology type

**Test Conditions:**
- `temperature_points`: Array of ≥4 temperatures
- `irradiance`: 1000 W/m²
- `spectrum`: Solar spectrum reference

**Measurements:**
- Array of ≥4 measurement objects
- Each must have: temperature, pmax, voc, isc, vmp, imp

**Metadata:**
- `test_date`: ISO 8601 date
- `test_facility`: Facility name
- `operator`: Operator name

---

## REST API Endpoints

If implementing a web service, recommended endpoints:

### Tests

- `GET /api/v1/tests` - List all tests
- `GET /api/v1/tests/{test_id}` - Get test details
- `POST /api/v1/tests` - Create new test
- `PUT /api/v1/tests/{test_id}` - Update test
- `DELETE /api/v1/tests/{test_id}` - Delete test

### Validation

- `POST /api/v1/validate` - Validate test data

### Calculations

- `POST /api/v1/calculate` - Calculate coefficients

### Export

- `GET /api/v1/tests/{test_id}/export` - Export as JSON
- `GET /api/v1/tests/{test_id}/report` - Generate PDF report

---

## Error Handling

### Common Exceptions

**ValueError:**
- Raised when insufficient measurements (< 4)
- Invalid parameter values

**ValidationError:**
- Schema validation failures
- Physical constraint violations

**Example:**
```python
try:
    coef = calc.calculate_temp_coefficient_pmax()
except ValueError as e:
    print(f"Error: {e}")
```

---

## Usage Examples

### Basic Coefficient Calculation

```python
from perf_001_engine import PERF001Calculator, Measurement

calc = PERF001Calculator(reference_temperature=25.0)

measurements = [
    Measurement(15.0, 330.5, 46.8, 9.12, 38.2, 8.65),
    Measurement(25.0, 320.0, 45.2, 9.18, 37.0, 8.65),
    Measurement(50.0, 290.0, 41.5, 9.30, 34.2, 8.48),
    Measurement(75.0, 260.5, 38.0, 9.42, 31.5, 8.27),
]

calc.add_measurements(measurements)
results = calc.calculate_all_coefficients()

print(f"Pmax coefficient: {results['temp_coefficient_pmax']['value']:.4f} %/°C")
```

### Complete Validation

```python
from validation import validate_test_data

report = validate_test_data(test_data)

if report.overall_passed:
    print("✓ Validation passed")
else:
    for error in report.get_errors():
        print(f"✗ {error.message}")
```

### Visualization

```python
from visualizations import PERF001Visualizer

viz = PERF001Visualizer()

# Temperature-power curve
fig = viz.plot_temp_power_regression(temperatures, pmax_values)
fig.show()

# Complete dashboard
fig = viz.create_dashboard(test_data)
fig.write_html("dashboard.html")
```

### Database Operations

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, PERF001Test, PERF001Measurement

engine = create_engine('postgresql://user:pass@localhost/testdb')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Create test record
test = PERF001Test(
    test_id="TEST-001",
    module_id="MODULE-001",
    manufacturer="Example Inc",
    model="EX-320",
    test_date="2025-11-13"
)

session.add(test)
session.commit()
```

---

## Type Hints

All modules use Python type hints for better IDE support and type checking:

```python
from typing import List, Dict, Optional, Tuple, Any

def calculate_coefficient(
    temps: List[float],
    values: List[float]
) -> Tuple[float, float]:
    ...
```

---

## Dependencies

Core dependencies:
- `numpy>=1.20.0` - Numerical computing
- `scipy>=1.7.0` - Statistical functions
- `pandas>=1.3.0` - Data structures
- `plotly>=5.0.0` - Visualizations
- `streamlit>=1.20.0` - Web UI
- `sqlalchemy>=1.4.0` - Database ORM
- `jsonschema>=4.0.0` - Schema validation

---

## Version Compatibility

- **Python**: 3.8+
- **NumPy**: 1.20+
- **SciPy**: 1.7+
- **Plotly**: 5.0+
- **Streamlit**: 1.20+

---

## References

1. IEC 61853-1:2011 - Temperature coefficient testing
2. IEC 60904-1:2020 - I-V characteristic measurement
3. Python documentation: https://docs.python.org/3/
4. NumPy documentation: https://numpy.org/doc/
5. Plotly documentation: https://plotly.com/python/

---

## Support

For API questions or issues:
- Review examples in `examples/` directory
- Check test cases in `tests/` directory
- Refer to inline docstrings in source code
- Create an issue in the repository
