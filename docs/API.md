# WIND-001 API Documentation

## Python API

### Core Classes

#### `WindLoadTest`

Main protocol implementation class for WIND-001.

```python
from protocols.wind_001 import WindLoadTest

protocol = WindLoadTest()
```

**Methods:**

##### `initialize_test(test_metadata, sample_info, test_parameters)`

Initialize a new wind load test.

**Parameters:**
- `test_metadata` (dict): Test identification and operator information
- `sample_info` (dict): PV module sample information
- `test_parameters` (dict): Test execution parameters

**Returns:**
- dict: Initialized test data structure

**Example:**
```python
test_data = protocol.initialize_test(
    test_metadata={
        "test_id": "WIND-001-2024-001",
        "operator": "John Doe",
        "standard": "IEC 61215-2:2021",
        "equipment_id": "WT-001",
        "calibration_date": "2024-01-15"
    },
    sample_info={
        "sample_id": "PV-MOD-12345",
        "manufacturer": "SolarTech Inc.",
        "model": "ST-400-M",
        "serial_number": "SN123456",
        "technology": "mono-Si",
        "rated_power": 400
    },
    test_parameters={
        "load_type": "cyclic",
        "pressure": 2400,
        "duration": 60,
        "cycles": 3,
        "temperature": 25,
        "humidity": 50
    }
)
```

##### `record_pre_test_measurements(visual_inspection, electrical_performance, insulation_resistance)`

Record pre-test baseline measurements.

**Parameters:**
- `visual_inspection` (str): Visual inspection notes
- `electrical_performance` (ElectricalPerformance): Baseline electrical measurements
- `insulation_resistance` (float): Insulation resistance in MΩ

**Example:**
```python
from protocols.wind_001 import ElectricalPerformance

protocol.record_pre_test_measurements(
    visual_inspection="No defects observed",
    electrical_performance=ElectricalPerformance(
        voc=48.5, isc=10.2, vmp=40.0, imp=10.0, pmax=400.0
    ),
    insulation_resistance=500.0
)
```

##### `record_cycle_measurement(measurement)`

Record measurement data for a test cycle.

**Parameters:**
- `measurement` (CycleMeasurement): Cycle measurement data

**Example:**
```python
from protocols.wind_001 import CycleMeasurement
from datetime import datetime

measurement = CycleMeasurement(
    cycle_number=1,
    timestamp=datetime.now().isoformat(),
    actual_pressure=2400.0,
    deflection_center=15.5,
    deflection_edges=[10.2, 11.5, 10.8, 11.0],
    observations="Normal deflection observed"
)
protocol.record_cycle_measurement(measurement)
```

##### `record_post_test_measurements(visual_inspection, electrical_performance, insulation_resistance, defects_observed)`

Record post-test measurements.

**Parameters:**
- `visual_inspection` (str): Post-test visual inspection notes
- `electrical_performance` (ElectricalPerformance): Final electrical measurements
- `insulation_resistance` (float): Final insulation resistance in MΩ
- `defects_observed` (list): List of observed defects

**Example:**
```python
protocol.record_post_test_measurements(
    visual_inspection="No defects after testing",
    electrical_performance=ElectricalPerformance(
        voc=48.3, isc=10.1, vmp=39.8, imp=9.9, pmax=394.0
    ),
    insulation_resistance=480.0,
    defects_observed=["none"]
)
```

##### `calculate_results()`

Calculate test results and determine pass/fail status.

**Returns:**
- dict: Results dictionary with test status and analysis

**Example:**
```python
results = protocol.calculate_results()
print(f"Status: {results['test_status']}")
print(f"Power Degradation: {results['power_degradation']}%")
```

##### `validate_test_data()`

Validate test data against schema.

**Returns:**
- tuple: (is_valid: bool, errors: List[str])

**Example:**
```python
is_valid, errors = protocol.validate_test_data()
if not is_valid:
    for error in errors:
        print(f"Validation error: {error}")
```

##### `export_test_data(filepath)`

Export test data to JSON file.

**Parameters:**
- `filepath` (Path): Output file path

**Example:**
```python
from pathlib import Path

protocol.export_test_data(Path("test_results.json"))
```

##### `import_test_data(filepath)`

Import test data from JSON file.

**Parameters:**
- `filepath` (Path): Input file path

**Example:**
```python
protocol.import_test_data(Path("test_results.json"))
```

##### `generate_summary_report()`

Generate a text summary report.

**Returns:**
- str: Formatted summary report string

**Example:**
```python
report = protocol.generate_summary_report()
print(report)
```

---

#### `ElectricalPerformance`

Dataclass for electrical performance measurements.

**Attributes:**
- `voc` (float): Open circuit voltage (V)
- `isc` (float): Short circuit current (A)
- `vmp` (float): Voltage at max power (V)
- `imp` (float): Current at max power (A)
- `pmax` (float): Maximum power (W)

**Methods:**

##### `calculate_degradation(baseline)`

Calculate power degradation percentage.

**Parameters:**
- `baseline` (ElectricalPerformance): Baseline measurements

**Returns:**
- float: Degradation percentage

---

#### `CycleMeasurement`

Dataclass for measurement data from a single test cycle.

**Attributes:**
- `cycle_number` (int): Cycle number
- `timestamp` (str): ISO format timestamp
- `actual_pressure` (float): Measured pressure in Pa
- `deflection_center` (float): Center deflection in mm
- `deflection_edges` (List[float]): Edge deflection measurements in mm
- `observations` (str): Observation notes

---

### Database Models

#### `WindLoadTest` (SQLAlchemy Model)

Main test record in database.

**Fields:**
- `id` - Primary key
- `test_id` - Unique test identifier
- `protocol_id` - Protocol identifier (WIND-001)
- `test_date` - Test execution date
- `operator` - Operator name
- `standard` - Testing standard
- `sample_id` - Sample identifier
- `manufacturer` - Module manufacturer
- `model` - Module model
- `test_status` - Current test status
- `power_degradation` - Calculated power degradation
- And more...

**Relationships:**
- `pre_test_measurements` - One-to-one with PreTestMeasurement
- `post_test_measurements` - One-to-one with PostTestMeasurement
- `cycle_measurements` - One-to-many with CycleMeasurement
- `attachments` - One-to-many with TestAttachment

**Example:**
```python
from db.database import get_database
from db.models import WindLoadTest, TestStatus, LoadType

db = get_database()

with db.session_scope() as session:
    test = WindLoadTest(
        test_id="WIND-001-2024-001",
        operator="John Doe",
        standard="IEC 61215-2:2021",
        sample_id="PV-MOD-12345",
        manufacturer="SolarTech Inc.",
        model="ST-400-M",
        load_type=LoadType.CYCLIC,
        pressure=2400.0,
        duration=60,
        cycles=3,
        test_status=TestStatus.IN_PROGRESS
    )
    session.add(test)
```

---

## Streamlit UI

### Running the UI

```bash
streamlit run src/ui/wind_001_ui.py
```

### UI Features

1. **Test Initialization** - Form for entering test metadata and parameters
2. **Pre-test Measurements** - Record baseline measurements
3. **Load Testing** - Step-by-step cycle execution with real-time data entry
4. **Post-test Measurements** - Record final measurements
5. **Results Analysis** - Automated pass/fail determination with visualizations
6. **Report Generation** - Export options for JSON, PDF, and text formats

### Session State Variables

- `protocol` - WindLoadTest instance
- `test_initialized` - Boolean flag
- `current_step` - Current workflow step (0-5)
- `cycle_count` - Number of completed cycles

---

## JSON Schema

The protocol uses a JSON schema for data validation. See `protocols/mechanical/wind-001/schema.json`.

### Example Test Data Structure

```json
{
  "test_metadata": {
    "test_id": "WIND-001-2024-001",
    "operator": "John Doe",
    "standard": "IEC 61215-2:2021"
  },
  "sample_info": {
    "sample_id": "PV-MOD-12345",
    "manufacturer": "SolarTech Inc.",
    "model": "ST-400-M"
  },
  "test_parameters": {
    "load_type": "cyclic",
    "pressure": 2400,
    "duration": 60,
    "cycles": 3
  },
  "measurements": {
    "pre_test": {},
    "during_test": [],
    "post_test": {}
  },
  "results": {
    "test_status": "pass",
    "power_degradation": 1.5,
    "max_deflection_measured": 15.5
  }
}
```

---

## Command Line Usage

### Run Protocol Example

```bash
python -m src.protocols.wind_001
```

### Initialize Database

```bash
python -m src.db.database
```

### Run Tests

```bash
python -m pytest tests/
```

Or for specific tests:

```bash
python -m pytest tests/test_wind_001.py
python -m pytest tests/test_database.py
```

---

## Integration Examples

### LIMS Integration

```python
# After test completion
results = protocol.calculate_results()

lims_data = {
    "sample_id": protocol.test_data["sample_info"]["sample_id"],
    "test_id": protocol.test_data["test_metadata"]["test_id"],
    "test_status": results["test_status"],
    "test_date": protocol.test_data["test_metadata"]["test_date"]
}

# Send to LIMS API
# requests.post("https://lims.example.com/api/results", json=lims_data)
```

### QMS Integration

```python
# Trigger QMS workflow on test completion
if results["test_status"] == "fail":
    # Create non-conformance report
    qms_data = {
        "test_id": protocol.test_data["test_metadata"]["test_id"],
        "failure_modes": results["failure_modes"],
        "sample_id": protocol.test_data["sample_info"]["sample_id"]
    }
    # Send to QMS API
```

---

## Error Handling

### Common Exceptions

- `FileNotFoundError` - Configuration files not found
- `json.JSONDecodeError` - Invalid JSON in configuration
- `ValueError` - Invalid measurement values
- `KeyError` - Missing required fields

### Example Error Handling

```python
try:
    protocol = WindLoadTest()
    protocol.initialize_test(metadata, sample, parameters)
except FileNotFoundError as e:
    print(f"Configuration error: {e}")
except ValueError as e:
    print(f"Invalid value: {e}")
```

---

## Best Practices

1. **Always validate** test data before finalizing results
2. **Export data** regularly during long test sessions
3. **Check equipment calibration** before starting tests
4. **Document observations** thoroughly during each cycle
5. **Review data quality** before generating reports

---

## Version Compatibility

- Python: ≥ 3.8
- SQLAlchemy: ≥ 1.4
- Streamlit: ≥ 1.28
- Pandas: ≥ 1.5
- Plotly: ≥ 5.0
