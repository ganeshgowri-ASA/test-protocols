# API Reference - SAND-001 Protocol

## Module: `protocols.sand_dust_test`

### Classes

---

## `SandDustResistanceTest`

Main class for conducting Sand and Dust Resistance Tests according to IEC 60068-2-68.

### Constructor

```python
SandDustResistanceTest(test_id: str, config: TestConfiguration, specimen: SpecimenData)
```

**Parameters:**
- `test_id` (str): Unique test identifier
- `config` (TestConfiguration): Test configuration object
- `specimen` (SpecimenData): Specimen information object

**Example:**
```python
test = SandDustResistanceTest("TEST-001", config, specimen)
```

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `test_id` | str | Unique test identifier |
| `config` | TestConfiguration | Test configuration |
| `specimen` | SpecimenData | Specimen data |
| `phase` | TestPhase | Current test phase |
| `start_time` | Optional[datetime] | Test start timestamp |
| `end_time` | Optional[datetime] | Test end timestamp |
| `test_passed` | Optional[bool] | Test result (None until evaluated) |
| `deviations` | List[str] | List of deviations |
| `particle_tracker` | Optional[ParticleTracker] | Particle tracking instance |
| `environmental_history` | List[EnvironmentalConditions] | Environmental data |
| `results` | Dict | Complete results dictionary |

### Methods

#### `start_test()`

Start the test sequence.

**Returns:** None

**Side effects:**
- Sets `start_time` to current datetime
- Changes phase to `PRE_CONDITIONING`
- Initializes results dictionary

**Example:**
```python
test.start_test()
print(f"Test started at {test.start_time}")
```

---

#### `initialize_particle_tracking(measurement_points: List[Dict])`

Initialize particle tracking system.

**Parameters:**
- `measurement_points` (List[Dict]): List of measurement point configurations

**Example:**
```python
points = [
    {'point_id': 'P001', 'location': (100, 200, 300)},
    {'point_id': 'P002', 'location': (400, 200, 300)}
]
test.initialize_particle_tracking(points)
```

---

#### `advance_phase(new_phase: TestPhase)`

Advance to next test phase.

**Parameters:**
- `new_phase` (TestPhase): Target phase

**Example:**
```python
test.advance_phase(TestPhase.DUST_EXPOSURE)
```

---

#### `record_environmental_conditions(...)`

Record environmental conditions during test.

```python
record_environmental_conditions(
    temperature: float,
    humidity: float,
    air_velocity: float,
    atmospheric_pressure: float,
    dust_concentration: float
) -> EnvironmentalConditions
```

**Parameters:**
- `temperature` (float): Temperature in °C
- `humidity` (float): Relative humidity in %
- `air_velocity` (float): Air velocity in m/s
- `atmospheric_pressure` (float): Atmospheric pressure in kPa
- `dust_concentration` (float): Dust concentration in kg/m³

**Returns:** EnvironmentalConditions object

**Example:**
```python
conditions = test.record_environmental_conditions(
    temperature=25.5,
    humidity=51.0,
    air_velocity=2.1,
    atmospheric_pressure=101.325,
    dust_concentration=0.0102
)
```

---

#### `record_particle_measurement(...)`

Record particle measurement during test.

```python
record_particle_measurement(
    point_id: str,
    location: Tuple[float, float, float],
    particle_size: float,
    count: int,
    concentration: float,
    velocity: Tuple[float, float, float],
    temperature: float,
    humidity: float
)
```

**Parameters:**
- `point_id` (str): Measurement point identifier
- `location` (Tuple): (x, y, z) coordinates in mm
- `particle_size` (float): Particle size in microns
- `count` (int): Particle count
- `concentration` (float): Concentration in kg/m³
- `velocity` (Tuple): Velocity vector (vx, vy, vz) in m/s
- `temperature` (float): Temperature in °C
- `humidity` (float): Humidity in %

**Example:**
```python
test.record_particle_measurement(
    point_id='P001',
    location=(100.0, 200.0, 300.0),
    particle_size=50.0,
    count=1000,
    concentration=0.01,
    velocity=(1.5, 0.5, 0.2),
    temperature=25.0,
    humidity=50.0
)
```

---

#### `check_particle_uniformity(threshold: float = 0.7) -> Tuple[bool, float]`

Check if particle distribution is sufficiently uniform.

**Parameters:**
- `threshold` (float): Minimum acceptable uniformity (0-1), default 0.7

**Returns:** Tuple of (is_uniform, uniformity_value)

**Example:**
```python
is_uniform, uniformity = test.check_particle_uniformity(threshold=0.7)
if not is_uniform:
    print(f"Warning: Non-uniform distribution ({uniformity:.2%})")
```

---

#### `record_post_test_measurements(...)`

Record post-test measurements.

```python
record_post_test_measurements(
    weight: float,
    dimensions: Tuple[float, float, float],
    surface_roughness: float,
    deposited_dust_weight: float,
    ingress_severity: SeverityLevel,
    electrical_params: Optional[Dict[str, float]] = None
)
```

**Parameters:**
- `weight` (float): Post-test weight in grams
- `dimensions` (Tuple): Post-test dimensions (L, W, H) in mm
- `surface_roughness` (float): Surface roughness in μm
- `deposited_dust_weight` (float): Weight of deposited dust in grams
- `ingress_severity` (SeverityLevel): Dust ingress severity level
- `electrical_params` (Optional[Dict]): Electrical parameters

**Example:**
```python
test.record_post_test_measurements(
    weight=5002.5,
    dimensions=(1000.0, 600.0, 40.0),
    surface_roughness=1.2,
    deposited_dust_weight=2.5,
    ingress_severity=SeverityLevel.LEVEL_2,
    electrical_params={'power': 297, 'Isc': 9.9, 'Voc': 39.5, 'FF': 0.74}
)
```

---

#### `evaluate_acceptance_criteria() -> Dict[str, Any]`

Evaluate test results against acceptance criteria.

**Returns:** Dictionary with evaluation results

**Structure:**
```python
{
    'dust_ingress': {'pass': bool, 'severity_level': int, 'details': str},
    'electrical_performance': {'pass': bool, 'details': List[str]},
    'physical_integrity': {'pass': bool, 'details': List[str]},
    'surface_degradation': {'pass': bool, 'details': List[str]},
    'overall_pass': bool
}
```

**Example:**
```python
evaluation = test.evaluate_acceptance_criteria()
if evaluation['overall_pass']:
    print("Test PASSED")
else:
    print("Test FAILED")
    for category, results in evaluation.items():
        if isinstance(results, dict) and not results.get('pass'):
            print(f"  {category}: {results.get('details')}")
```

---

#### `complete_test()`

Complete the test and finalize results.

**Returns:** None

**Side effects:**
- Sets `end_time`
- Updates `phase` to COMPLETE or FAILED
- Finalizes results dictionary

**Example:**
```python
test.complete_test()
print(f"Test completed at {test.end_time}")
```

---

#### `export_results(output_dir: str)`

Export test results to files.

**Parameters:**
- `output_dir` (str): Directory to save results

**Generates:**
- `{test_id}_results.json`: Main results
- `{test_id}_particle_data.json`: Particle tracking data

**Example:**
```python
test.export_results('./results')
```

---

#### `generate_report_data() -> Dict[str, Any]`

Generate structured data for report generation.

**Returns:** Dictionary with all report data

**Example:**
```python
report_data = test.generate_report_data()
print(f"Test duration: {report_data['test_identification']['duration_hours']} hours")
```

---

## `ParticleTracker`

Real-time particle tracking system.

### Constructor

```python
ParticleTracker(measurement_points: List[Dict], sampling_interval: int = 60)
```

**Parameters:**
- `measurement_points` (List[Dict]): Measurement point configurations
- `sampling_interval` (int): Sampling interval in seconds, default 60

### Methods

#### `record_measurement(...) -> ParticleData`

Record a particle measurement.

#### `get_particle_distribution(...) -> Dict[str, List[ParticleData]]`

Get particle distribution by measurement point.

#### `calculate_uniformity() -> float`

Calculate spatial uniformity of particle distribution (0-1).

#### `get_deposition_rate(time_window_minutes: int = 60) -> Dict[str, float]`

Calculate deposition rate for each measurement point in g/m²/h.

#### `export_data(filepath: str)`

Export particle tracking data to JSON.

---

## Data Classes

### `TestConfiguration`

Test configuration parameters.

**Fields:**
- `dust_type` (str)
- `particle_size_range` (Tuple[float, float, float]): min, max, median in μm
- `dust_concentration` (float): kg/m³
- `target_temperature` (float): °C
- `target_humidity` (float): %
- `target_air_velocity` (float): m/s
- `exposure_time_hours` (float)
- `cycles` (int)
- `settling_time_hours` (float)
- `tracking_enabled` (bool): default True
- `sampling_interval_seconds` (int): default 60

**Class Methods:**
- `from_protocol(protocol_path: str) -> TestConfiguration`

---

### `SpecimenData`

Specimen information and measurements.

**Fields:**
- `specimen_id` (str)
- `specimen_type` (str)
- `manufacturer` (str)
- `model` (str)
- `serial_number` (str)
- `initial_weight` (float): grams
- `initial_dimensions` (Tuple[float, float, float]): mm
- `initial_surface_roughness` (float): μm
- `initial_electrical_params` (Optional[Dict[str, float]])
- `post_weight` (Optional[float])
- `post_dimensions` (Optional[Tuple[float, float, float]])
- `post_surface_roughness` (Optional[float])
- `post_electrical_params` (Optional[Dict[str, float]])
- `deposited_dust_weight` (Optional[float])
- `ingress_severity` (Optional[SeverityLevel])
- `photos` (List[str])

---

### `ParticleData`

Real-time particle tracking data.

**Fields:**
- `timestamp` (datetime)
- `point_id` (str)
- `location` (Tuple[float, float, float]): x, y, z in mm
- `particle_size_microns` (float)
- `particle_count` (int)
- `concentration` (float): kg/m³
- `velocity` (Tuple[float, float, float]): vx, vy, vz in m/s
- `temperature` (float): °C
- `humidity` (float): %

**Methods:**
- `to_dict() -> Dict`: Convert to dictionary for storage

---

### `EnvironmentalConditions`

Environmental conditions during test.

**Fields:**
- `timestamp` (datetime)
- `temperature` (float): °C
- `humidity` (float): %
- `air_velocity` (float): m/s
- `atmospheric_pressure` (float): kPa
- `dust_concentration` (float): kg/m³
- `in_tolerance` (bool): default True

**Methods:**
- `check_tolerance(target: Dict, tolerances: Dict) -> bool`

---

## Enumerations

### `TestPhase`

Test execution phases.

**Values:**
- `INITIALIZATION`
- `PRE_CONDITIONING`
- `CHAMBER_PREP`
- `STABILIZATION`
- `DUST_EXPOSURE`
- `SETTLING`
- `POST_ASSESSMENT`
- `COMPLETE`
- `FAILED`

---

### `SeverityLevel`

Dust ingress severity levels per IEC 60068-2-68.

**Values:**
- `LEVEL_1`: (1, "No visible dust ingress")
- `LEVEL_2`: (2, "Superficial dust, easily removable, no functional impact")
- `LEVEL_3`: (3, "Dust ingress but no impairment of function")
- `LEVEL_4`: (4, "Dust ingress causing partial functional impairment")
- `LEVEL_5`: (5, "Dust ingress causing complete functional failure")

**Attributes:**
- `level` (int): Numeric level
- `description` (str): Text description

---

## Utility Functions

### `create_test_from_protocol(test_id: str, protocol_path: str, specimen: SpecimenData) -> SandDustResistanceTest`

Convenience function to create test from protocol JSON.

**Parameters:**
- `test_id` (str): Unique test identifier
- `protocol_path` (str): Path to protocol JSON file
- `specimen` (SpecimenData): Specimen data

**Returns:** Configured SandDustResistanceTest instance

**Example:**
```python
specimen = SpecimenData(...)
test = create_test_from_protocol(
    "TEST-001",
    "protocols/SAND-001.json",
    specimen
)
test.start_test()
```

---

## Error Handling

### Common Exceptions

- `FileNotFoundError`: Protocol JSON file not found
- `json.JSONDecodeError`: Invalid JSON format
- `ValueError`: Invalid parameter values
- `AttributeError`: Missing required configuration

### Best Practices

```python
try:
    test = create_test_from_protocol(test_id, protocol_path, specimen)
    test.start_test()
except FileNotFoundError:
    print("Protocol file not found")
except ValueError as e:
    print(f"Invalid configuration: {e}")
```

---

## Type Hints

The module uses type hints for better IDE support and type checking:

```python
from typing import Dict, List, Optional, Tuple, Any
```

Use mypy for type checking:

```bash
mypy src/python/protocols/sand_dust_test.py
```

---

## Logging

The module uses Python's standard logging:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Test operations will log to logger
test = SandDustResistanceTest(...)
test.start_test()  # Logs: "Test TEST-001 started at ..."
```

---

**Document Version**: 1.0.0
**Last Updated**: 2025-11-14
**Module**: protocols.sand_dust_test
