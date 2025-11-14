# TEMP-001 API Documentation

## Overview

This document provides comprehensive API documentation for the TEMP-001 Temperature Coefficient Testing Protocol implementation.

## Table of Contents

- [Python Modules](#python-modules)
  - [Analyzer](#analyzer-module)
  - [Validator](#validator-module)
  - [Report Generator](#report-generator-module)
- [Database Schema](#database-schema)
- [REST API](#rest-api-future)
- [Data Formats](#data-formats)

---

## Python Modules

### Analyzer Module

**File:** `protocols/TEMP-001/python/analyzer.py`

#### Class: `TemperatureCoefficientAnalyzer`

Main class for calculating temperature coefficients according to IEC 60891:2021.

##### Initialization

```python
analyzer = TemperatureCoefficientAnalyzer(protocol_config_path: Optional[str] = None)
```

**Parameters:**
- `protocol_config_path` (str, optional): Path to protocol.json configuration file

##### Methods

###### `load_data(data: Union[pd.DataFrame, Dict, str, Path]) -> pd.DataFrame`

Load measurement data from various sources.

**Parameters:**
- `data`: DataFrame, dictionary, or path to CSV/JSON file

**Returns:**
- `pd.DataFrame`: Loaded measurement data

**Example:**
```python
# From DataFrame
df = pd.DataFrame({...})
analyzer.load_data(df)

# From CSV file
analyzer.load_data("measurements.csv")

# From dictionary
data_dict = {'module_temperature': [20, 30, 40], ...}
analyzer.load_data(data_dict)
```

###### `normalize_to_irradiance(target_irradiance: float = 1000.0) -> pd.DataFrame`

Normalize measurements to target irradiance level.

**Parameters:**
- `target_irradiance` (float): Target irradiance in W/m² (default: 1000.0)

**Returns:**
- `pd.DataFrame`: Data with normalized columns added

**Example:**
```python
normalized_data = analyzer.normalize_to_irradiance(1000.0)
```

###### `calculate_temperature_coefficients() -> TemperatureCoefficients`

Calculate all temperature coefficients using linear regression.

**Returns:**
- `TemperatureCoefficients`: Object containing all calculated coefficients

**Example:**
```python
results = analyzer.calculate_temperature_coefficients()

print(f"Power coefficient: {results.alpha_pmp_relative} %/°C")
print(f"Voltage coefficient: {results.beta_voc_relative} %/°C")
print(f"Current coefficient: {results.alpha_isc_relative} %/°C")
```

###### `calculate_linear_regression(x: np.ndarray, y: np.ndarray) -> Tuple`

Perform linear regression and calculate statistics.

**Parameters:**
- `x` (np.ndarray): Independent variable (temperature)
- `y` (np.ndarray): Dependent variable (Pmp, Voc, or Isc)

**Returns:**
- `Tuple[float, float, float, float, float]`: (slope, intercept, r_squared, std_err, p_value)

###### `correct_to_stc(...) -> Dict[str, float]`

Correct a single measurement to STC conditions.

**Parameters:**
- `temperature` (float): Module temperature in °C
- `pmax` (float): Maximum power in W
- `voc` (float): Open circuit voltage in V
- `isc` (float): Short circuit current in A
- `irradiance` (float): Irradiance in W/m² (default: 1000)

**Returns:**
- `Dict`: Dictionary with STC-corrected values

**Example:**
```python
corrected = analyzer.correct_to_stc(
    temperature=50.0,
    pmax=236.0,
    voc=36.4,
    isc=9.35,
    irradiance=1000.0
)
print(f"Power at STC: {corrected['pmax_stc']} W")
```

###### `export_results(output_path: Union[str, Path], format: str = 'json') -> None`

Export analysis results to file.

**Parameters:**
- `output_path`: Output file path
- `format`: Export format ('json', 'csv', or 'excel')

**Example:**
```python
analyzer.export_results("results.json", format='json')
analyzer.export_results("results.xlsx", format='excel')
```

#### Class: `TemperatureCoefficients`

Data class containing temperature coefficient results.

##### Attributes

| Attribute | Type | Unit | Description |
|-----------|------|------|-------------|
| `alpha_pmp_relative` | float | %/°C | Relative power temperature coefficient |
| `alpha_pmp_absolute` | float | W/°C | Absolute power temperature coefficient |
| `r_squared_pmp` | float | - | R² for power regression |
| `beta_voc_relative` | float | %/°C | Relative voltage temperature coefficient |
| `beta_voc_absolute` | float | V/°C | Absolute voltage temperature coefficient |
| `r_squared_voc` | float | - | R² for voltage regression |
| `alpha_isc_relative` | float | %/°C | Relative current temperature coefficient |
| `alpha_isc_absolute` | float | A/°C | Absolute current temperature coefficient |
| `r_squared_isc` | float | - | R² for current regression |
| `pmp_at_stc` | float | W | Maximum power at STC |
| `voc_at_stc` | float | V | Open circuit voltage at STC |
| `isc_at_stc` | float | A | Short circuit current at STC |

##### Methods

###### `to_dict() -> Dict`

Convert results to dictionary.

###### `to_json(indent: int = 2) -> str`

Convert results to JSON string.

---

### Validator Module

**File:** `protocols/TEMP-001/python/validator.py`

#### Class: `TEMP001Validator`

Validates measurement data and quality checks.

##### Initialization

```python
validator = TEMP001Validator(protocol_config_path: Optional[str] = None)
```

##### Methods

###### `validate_field_value(field_id: str, value: Any) -> ValidationResult`

Validate a single field value.

**Example:**
```python
result = validator.validate_field_value('module_temperature', 25.0)
if result.status == 'pass':
    print("Temperature is valid")
```

###### `validate_record(record: Dict) -> List[ValidationResult]`

Validate a complete measurement record.

**Example:**
```python
record = {
    'module_temperature': 25.0,
    'pmax': 250.0,
    'voc': 37.5,
    'isc': 9.25
}
results = validator.validate_record(record)
```

###### `validate_dataset(data: pd.DataFrame) -> ValidationReport`

Validate entire measurement dataset.

**Example:**
```python
report = validator.validate_dataset(df)
print(f"Overall status: {report.overall_status}")
print(f"Passed: {report.num_passed}")
print(f"Warnings: {report.num_warnings}")
print(f"Failures: {report.num_critical_failures}")
```

###### `validate_coefficients(...) -> List[ValidationResult]`

Validate calculated temperature coefficients.

**Parameters:**
- `alpha_pmp` (float): Power temperature coefficient (%/°C)
- `beta_voc` (float): Voltage temperature coefficient (%/°C)
- `alpha_isc` (float): Current temperature coefficient (%/°C)
- `r_squared_pmp` (float): R² for power regression
- `r_squared_voc` (float): R² for voltage regression
- `r_squared_isc` (float): R² for current regression

**Example:**
```python
results = validator.validate_coefficients(
    alpha_pmp=-0.40,
    beta_voc=-0.32,
    alpha_isc=0.05,
    r_squared_pmp=0.998,
    r_squared_voc=0.999,
    r_squared_isc=0.997
)
```

#### Class: `ValidationResult`

Data class for individual validation check result.

##### Attributes

- `check_id` (str): Unique check identifier
- `check_name` (str): Human-readable check name
- `status` (str): 'pass', 'warning', or 'fail'
- `severity` (Severity): Severity level
- `message` (str): Validation message
- `details` (Dict, optional): Additional details

#### Class: `ValidationReport`

Comprehensive validation report.

##### Attributes

- `overall_status` (str): Overall validation status
- `num_critical_failures` (int): Count of critical failures
- `num_warnings` (int): Count of warnings
- `num_passed` (int): Count of passed checks
- `results` (List[ValidationResult]): All validation results

##### Methods

###### `to_dict() -> Dict`

Convert report to dictionary.

###### `to_json(indent: int = 2) -> str`

Convert report to JSON string.

---

### Report Generator Module

**File:** `protocols/TEMP-001/python/report_generator.py`

#### Class: `TEMP001ReportGenerator`

Generates comprehensive test reports in various formats.

##### Initialization

```python
generator = TEMP001ReportGenerator(
    protocol_config_path: Optional[str] = None,
    template_dir: Optional[str] = None
)
```

##### Methods

###### `generate_report(...) -> None`

Generate comprehensive test report.

**Parameters:**
- `test_info` (Dict): Test metadata
- `measurement_data` (pd.DataFrame): Raw measurement data
- `analysis_results` (Dict): Results from analyzer
- `validation_report` (Dict): Validation results
- `output_path`: Output file path
- `format` (str): Report format ('pdf', 'html', 'json', 'excel')

**Example:**
```python
generator.generate_report(
    test_info={
        'module_id': 'TEST-001',
        'test_date': '2025-11-14',
        'operator': 'John Doe'
    },
    measurement_data=df,
    analysis_results=results.to_dict(),
    validation_report=report.to_dict(),
    output_path='report.pdf',
    format='pdf'
)
```

---

## Database Schema

### Tables

#### `protocols`

Registry of all testing protocols.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| protocol_id | VARCHAR(50) | Unique protocol identifier |
| protocol_name | VARCHAR(255) | Protocol name |
| version | VARCHAR(20) | Protocol version |
| category | VARCHAR(100) | Protocol category |
| standard_reference | VARCHAR(255) | Reference standard |
| description | TEXT | Protocol description |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

#### `tests`

Individual test sessions.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| protocol_id | VARCHAR(50) | Foreign key to protocols |
| test_number | VARCHAR(100) | Unique test identifier |
| test_date | TIMESTAMP | Test date and time |
| operator | VARCHAR(100) | Test operator name |
| laboratory | VARCHAR(255) | Testing facility |
| module_id | VARCHAR(100) | Module identifier |
| module_manufacturer | VARCHAR(255) | Manufacturer name |
| module_model | VARCHAR(255) | Module model |
| status | VARCHAR(50) | Test status |
| notes | TEXT | Additional notes |

#### `temp_001_measurements`

Raw measurement data for TEMP-001 tests.

| Column | Type | Unit | Description |
|--------|------|------|-------------|
| id | SERIAL | - | Primary key |
| test_id | INT | - | Foreign key to tests |
| measurement_number | INT | - | Measurement sequence number |
| module_temperature | DECIMAL(6,2) | °C | Module temperature |
| ambient_temperature | DECIMAL(6,2) | °C | Ambient temperature |
| irradiance | DECIMAL(8,2) | W/m² | Irradiance |
| voc | DECIMAL(8,4) | V | Open circuit voltage |
| isc | DECIMAL(8,4) | A | Short circuit current |
| vmp | DECIMAL(8,4) | V | Voltage at max power |
| imp | DECIMAL(8,4) | A | Current at max power |
| pmax | DECIMAL(10,3) | W | Maximum power |
| fill_factor | DECIMAL(6,3) | % | Fill factor |

#### `temp_001_calculations`

Calculated temperature coefficients.

| Column | Type | Unit | Description |
|--------|------|------|-------------|
| id | SERIAL | - | Primary key |
| test_id | INT | - | Foreign key to tests |
| alpha_pmp_relative | DECIMAL(10,6) | %/°C | Power coefficient (relative) |
| alpha_pmp_absolute | DECIMAL(10,6) | W/°C | Power coefficient (absolute) |
| beta_voc_relative | DECIMAL(10,6) | %/°C | Voltage coefficient (relative) |
| beta_voc_absolute | DECIMAL(10,7) | V/°C | Voltage coefficient (absolute) |
| alpha_isc_relative | DECIMAL(10,6) | %/°C | Current coefficient (relative) |
| alpha_isc_absolute | DECIMAL(10,7) | A/°C | Current coefficient (absolute) |
| pmp_at_stc | DECIMAL(10,3) | W | Power at STC |
| voc_at_stc | DECIMAL(8,4) | V | Voltage at STC |
| isc_at_stc | DECIMAL(8,4) | A | Current at STC |
| r_squared_pmp | DECIMAL(8,6) | - | R² for power |
| r_squared_voc | DECIMAL(8,6) | - | R² for voltage |
| r_squared_isc | DECIMAL(8,6) | - | R² for current |

---

## Data Formats

### Input Data Format (JSON)

```json
{
  "test_info": {
    "test_number": "TEMP-001-2025-001",
    "test_date": "2025-11-14T10:00:00Z",
    "operator": "John Doe",
    "module_id": "TEST-MODULE-001"
  },
  "measurements": [
    {
      "measurement_number": 1,
      "module_temperature": 20.0,
      "irradiance": 1000.0,
      "voc": 38.50,
      "isc": 9.20,
      "pmax": 259.88
    }
  ]
}
```

### Output Results Format (JSON)

```json
{
  "alpha_pmp_relative": -0.4015,
  "alpha_pmp_absolute": -1.603,
  "beta_voc_relative": -0.3200,
  "beta_voc_absolute": -0.0700,
  "alpha_isc_relative": 0.0543,
  "alpha_isc_absolute": 0.0050,
  "r_squared_pmp": 0.9998,
  "r_squared_voc": 0.9999,
  "r_squared_isc": 0.9997,
  "pmp_at_stc": 244.02,
  "voc_at_stc": 37.10,
  "isc_at_stc": 9.325
}
```

---

## Usage Examples

### Complete Workflow Example

```python
from protocols.TEMP_001.python.analyzer import TemperatureCoefficientAnalyzer
from protocols.TEMP_001.python.validator import TEMP001Validator
from protocols.TEMP_001.python.report_generator import TEMP001ReportGenerator
import pandas as pd

# 1. Load measurement data
data = pd.read_csv("measurements.csv")

# 2. Validate data
validator = TEMP001Validator()
validation_report = validator.validate_dataset(data)

if validation_report.overall_status == 'fail':
    print("Data validation failed!")
    print(validation_report.to_json())
    exit(1)

# 3. Analyze data
analyzer = TemperatureCoefficientAnalyzer()
analyzer.load_data(data)
results = analyzer.calculate_temperature_coefficients()

# 4. Validate coefficients
coeff_validation = validator.validate_coefficients(
    results.alpha_pmp_relative,
    results.beta_voc_relative,
    results.alpha_isc_relative,
    results.r_squared_pmp,
    results.r_squared_voc,
    results.r_squared_isc
)

# 5. Generate report
test_info = {
    'module_id': 'TEST-001',
    'test_date': '2025-11-14',
    'operator': 'John Doe',
    'laboratory': 'ASA PV Testing Lab'
}

generator = TEMP001ReportGenerator()
generator.generate_report(
    test_info=test_info,
    measurement_data=data,
    analysis_results=results.to_dict(),
    validation_report=validation_report.to_dict(),
    output_path='temp_001_report.pdf',
    format='pdf'
)

print("Analysis complete!")
print(f"Power coefficient: {results.alpha_pmp_relative:.4f} %/°C")
print(f"Voltage coefficient: {results.beta_voc_relative:.4f} %/°C")
print(f"Current coefficient: {results.alpha_isc_relative:.4f} %/°C")
```

---

## Error Handling

### Common Exceptions

- `ValueError`: Raised for invalid input data or missing required fields
- `FileNotFoundError`: Raised when configuration or data files are not found
- `TypeError`: Raised for incorrect data types

### Example Error Handling

```python
try:
    analyzer = TemperatureCoefficientAnalyzer()
    analyzer.load_data("measurements.csv")
    results = analyzer.calculate_temperature_coefficients()
except ValueError as e:
    print(f"Data validation error: {e}")
except FileNotFoundError as e:
    print(f"File not found: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-14 | Initial API release |
