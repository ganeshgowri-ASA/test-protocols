# UV-001: UV Preconditioning Protocol

## Overview

The UV-001 UV Preconditioning Protocol implements the IEC 61215 MQT 10 standard for photovoltaic module qualification testing. This protocol exposes PV modules to controlled UV radiation to assess their resistance to degradation from ultraviolet exposure.

**Protocol ID:** UV-001
**Standard:** IEC 61215 MQT 10
**Category:** Environmental Testing
**Version:** 1.0
**Last Updated:** 2025-11-14

---

## Table of Contents

1. [Test Objectives](#test-objectives)
2. [Test Parameters](#test-parameters)
3. [Equipment Requirements](#equipment-requirements)
4. [Sample Preparation](#sample-preparation)
5. [Test Procedure](#test-procedure)
6. [Data Collection](#data-collection)
7. [Acceptance Criteria](#acceptance-criteria)
8. [Implementation Guide](#implementation-guide)
9. [API Reference](#api-reference)
10. [Database Schema](#database-schema)
11. [UI Components](#ui-components)
12. [Quality Control](#quality-control)

---

## Test Objectives

The UV preconditioning test determines:

- **Primary:** Module's ability to withstand UV radiation exposure
- **Secondary:** Material degradation characteristics
- **Tertiary:** Long-term reliability indicators

### Key Metrics

- Total UV dose exposure: **15 kWh/m²**
- Power degradation limit: **≤ 5%**
- Visual defects: **None major**
- Insulation resistance: **≥ 40 MΩ**

---

## Test Parameters

### UV Exposure Requirements

| Parameter | Value | Tolerance | Unit |
|-----------|-------|-----------|------|
| Total UV Dose | 15 | ± 2% | kWh/m² |
| Wavelength Range | 280-400 | - | nm |
| Peak Wavelength | 340 | ± 20 | nm |
| Irradiance Level | 300 (nominal) | 250-400 | W/m² |
| Module Temperature | 60 | ± 5 | °C |
| Ambient Temperature | 25 | ± 10 | °C |
| Relative Humidity | - | ≤ 75 | % |
| Air Velocity | 1.0 (nominal) | 0.5-2.0 | m/s |

### Spectral Distribution

- **UVB (280-320 nm):** 5-10% of total UV
- **UVA (320-400 nm):** 90-95% of total UV

### Exposure Duration

Typical exposure time: **50-60 hours** (at 300 W/m² nominal irradiance)

Calculated as:
```
Duration (hours) = Total Dose (kWh/m²) / (Irradiance (W/m²) / 1000)
                 = 15 / (300 / 1000)
                 = 50 hours
```

---

## Equipment Requirements

### Primary Equipment

1. **UV Exposure Chamber**
   - Type: Xenon arc or metal halide with UV filter
   - Uniformity: ± 10% across test plane
   - Temperature control: 25-70°C
   - Humidity control: 0-75% RH

2. **UV Radiometer**
   - Wavelength range: 280-400 nm
   - Accuracy: ± 3%
   - Calibration: Annually traceable

3. **Temperature Sensors**
   - Type: Thermocouples (Type K) or RTDs
   - Quantity: Minimum 4 per module
   - Accuracy: ± 1°C
   - Locations: Center + 4 corners

4. **Spectroradiometer**
   - Wavelength range: 280-400 nm
   - Resolution: ≤ 5 nm
   - For spectral distribution verification

5. **Solar Simulator (Class A)**
   - Standard: IEC 60904-9
   - For pre/post electrical characterization
   - Spectral match: Class A (0.75-1.25)
   - Irradiance uniformity: ± 2%
   - Temporal stability: ± 2%

6. **Data Acquisition System**
   - Minimum 8 channels
   - Sampling rate: ≥ 1 Hz
   - Automated logging capability

### Calibration Requirements

| Equipment | Frequency | Standard |
|-----------|-----------|----------|
| UV Radiometer | Annual | NIST traceable |
| Temperature Sensors | Annual | NIST traceable |
| Solar Simulator | Quarterly | IEC 60904-9 |
| Spectroradiometer | Annual | NIST traceable |

---

## Sample Preparation

### Sample Requirements

- **Type:** Complete PV module (as manufactured)
- **Quantity:** Minimum 1, recommended 2
- **Condition:** New, unaged modules

### Pre-Test Preparation Checklist

1. **Cleaning**
   - Clean module surface with isopropyl alcohol
   - Dry with lint-free cloth
   - Ensure no residues remain

2. **Initial Inspection**
   - Visual inspection for pre-existing defects
   - Photo documentation (all sides)
   - Document serial numbers and identification

3. **Electrical Characterization**
   - I-V curve measurement at STC
   - Record: Voc, Isc, Pmax, FF, efficiency
   - Measure insulation resistance
   - Document baseline performance

4. **Mounting Preparation**
   - Verify mounting fixtures are clean
   - Prepare edge support or back support
   - Ensure connectors are sealed/protected

### Mounting Configuration

- **Orientation:** Face-up (horizontal)
- **Tilt angle:** 0° (horizontal mounting)
- **Support:** Edge-supported or full-back support
- **Spacing:** Ensure uniform UV exposure
- **Sensor placement:** Center + 4 corners for temperature

---

## Test Procedure

### Phase 1: Pre-Test Characterization (3-4 hours)

1. **Equipment Calibration**
   - Verify UV radiometer calibration
   - Check temperature sensor calibration
   - Validate chamber functionality

2. **Initial Electrical Testing**
   - Measure I-V curves at STC (1000 W/m², 25°C, AM1.5)
   - Record all electrical parameters
   - Measure insulation resistance (≥ 40 MΩ)

3. **Visual Inspection**
   - Document initial condition
   - Photograph all surfaces
   - Note any pre-existing conditions

### Phase 2: Module Installation (1 hour)

1. Mount modules in UV chamber (face-up, horizontal)
2. Attach temperature sensors:
   - Center of module
   - Four corners
   - Use thermal paste for good contact
3. Position UV radiometer at module plane
4. Verify sensor connections
5. Initialize data acquisition system

### Phase 3: UV Exposure (50-60 hours)

1. **Chamber Setup**
   - Set chamber temperature to 60°C ± 5°C
   - Verify air circulation (0.5-2.0 m/s)
   - Start UV lamps

2. **Stabilization (30 minutes)**
   - Allow UV lamps to stabilize
   - Verify irradiance level (300 W/m² nominal)
   - Check spectral distribution compliance

3. **Exposure Sequence**
   - Begin automated data logging
   - Monitor parameters continuously:
     - UV irradiance (every 5 minutes)
     - Module temperature (every 5 minutes)
     - Chamber conditions (every 10 minutes)
     - Spectral data (every 60 minutes)

4. **Monitoring**
   - Track cumulative UV dose
   - Verify compliance with specifications
   - Document any out-of-spec conditions
   - Record interruptions or anomalies

5. **Completion**
   - Continue until 15 kWh/m² ± 2% achieved
   - Power off UV lamps
   - Allow chamber cool-down

### Phase 4: Post-Exposure Stabilization (4 hours)

1. Remove modules from chamber
2. Allow cooling to ambient temperature
3. Store in dark conditions
4. Wait minimum 4 hours before testing

### Phase 5: Post-Test Characterization (2-3 hours)

1. **Final Electrical Testing**
   - Measure I-V curves at STC
   - Record all electrical parameters
   - Measure insulation resistance
   - Compare to pre-test values

2. **Visual Inspection**
   - Inspect for defects:
     - Discoloration
     - Delamination
     - Bubbles/blisters
     - Edge seal degradation
     - Cell cracks
     - Junction box condition
   - Photograph all surfaces
   - Document findings

3. **Degradation Analysis**
   - Calculate power degradation: `(P_initial - P_final) / P_initial × 100%`
   - Analyze other parameter changes
   - Determine pass/fail status

### Phase 6: Data Analysis and Reporting (2-3 hours)

1. Analyze UV dose profiles
2. Verify data quality and completeness
3. Generate performance comparison charts
4. Complete test report
5. Obtain approvals

---

## Data Collection

### Real-Time Monitoring Data

| Parameter | Frequency | Unit | Storage |
|-----------|-----------|------|---------|
| UV Irradiance | 5 min | W/m² | Time-series |
| Module Temperature | 5 min | °C | Time-series |
| Ambient Temperature | 10 min | °C | Time-series |
| Relative Humidity | 10 min | % | Time-series |
| Spectral Distribution | 60 min | W/m²/nm | Snapshot |

### Calculated Metrics

- **Cumulative UV Dose:** Integrated irradiance over time (kWh/m²)
- **Average Irradiance:** Mean UV irradiance (W/m²)
- **Exposure Duration:** Total test time (hours)
- **Temperature Uniformity:** Max deviation across module (°C)
- **Dose Rate:** Instantaneous dose accumulation rate (kWh/m²/hr)

### Pre/Post Test Data

- **I-V Curve:** Voltage-current characteristics
- **Key Parameters:** Voc, Isc, Pmax, Vmp, Imp, FF, efficiency
- **Insulation Resistance:** Module-to-ground resistance (MΩ)
- **Visual Condition:** Photographic and written documentation

---

## Acceptance Criteria

### Pass Criteria

The module **PASSES** if all of the following are met:

1. **Power Degradation**
   - `ΔP ≤ 5%`
   - Where: `ΔP = (P_initial - P_final) / P_initial × 100%`

2. **UV Dose Completion**
   - Total dose: `15 kWh/m² ± 2%`
   - Range: `14.7 - 15.3 kWh/m²`

3. **Visual Inspection**
   - No major defects (delamination, broken cells, etc.)
   - Minor defects acceptable if no performance impact

4. **Insulation Resistance**
   - Post-test resistance ≥ 40 MΩ

### Fail Criteria

The module **FAILS** if any of the following occur:

- Power degradation > 5%
- Major visual defects (delamination, cell cracks)
- Insulation resistance < 40 MΩ
- Incomplete UV dose (< 14.7 kWh/m²)

### Conditional Pass

A **conditional pass** may be assigned if:

- Minor visual defects present but performance acceptable
- Power degradation 4.5-5.0% with excellent other metrics
- Requires engineering review and approval

---

## Implementation Guide

### Quick Start

1. **Install Dependencies**
   ```bash
   pip install numpy pandas plotly streamlit sqlalchemy
   ```

2. **Initialize Database**
   ```bash
   python migrations/001_initial_setup.py upgrade sqlite:///uv001_test_data.db
   ```

3. **Run UI Application**
   ```bash
   streamlit run ui/components/uv_preconditioning_ui.py
   ```

4. **Run Tests**
   ```bash
   python -m pytest tests/protocols/environmental/test_uv_preconditioning.py -v
   ```

### Python API Usage

```python
from protocols.environmental import UVPreconditioningProtocol

# Initialize protocol
protocol = UVPreconditioningProtocol()

# Start test session
session = protocol.start_test_session(
    session_id="UV001_20250114_001",
    sample_id="MODULE_12345",
    operator="John Doe",
    notes="Standard qualification test"
)

# Add measurements during test
protocol.add_irradiance_measurement(
    uv_irradiance=300.0,
    sensor_temperature=35.0
)

protocol.add_environmental_measurement(
    module_temperature=60.0,
    ambient_temperature=25.0,
    relative_humidity=50.0
)

# Add spectral data
protocol.add_spectral_measurement(
    wavelengths=[280, 290, ..., 400],
    irradiance_values=[10.5, 15.2, ..., 8.3]
)

# Pre-test characterization
protocol.add_electrical_characterization(
    voc=45.2,
    isc=9.8,
    pmax=350.0,
    ff=0.79,
    efficiency=18.5,
    is_pre_test=True
)

# Check progress
dose = protocol.get_cumulative_dose()
remaining = protocol.get_remaining_dose()
completion = protocol.get_dose_completion_percentage()

# Post-test characterization
protocol.add_electrical_characterization(
    voc=45.0,
    isc=9.75,
    pmax=340.0,
    ff=0.78,
    efficiency=18.0,
    is_pre_test=False
)

# Get results
degradation = protocol.calculate_power_degradation()
acceptance = protocol.check_acceptance_criteria()

# Complete session
protocol.complete_test_session()

# Export data
protocol.export_session_data(Path("session_data.json"))
```

### Configuration

Protocol configuration can be loaded from JSON:

```python
protocol = UVPreconditioningProtocol(
    protocol_file=Path("protocols/environmental/UV-001_preconditioning.json")
)
```

---

## API Reference

### Class: `UVPreconditioningProtocol`

Main protocol implementation class.

#### Methods

##### `start_test_session(session_id, sample_id, operator, notes="")`
Start a new test session.

**Parameters:**
- `session_id` (str): Unique session identifier
- `sample_id` (str): Module/sample identifier
- `operator` (str): Test operator name
- `notes` (str, optional): Test notes

**Returns:** `TestSession` object

**Raises:** `ValueError` if session already active

##### `add_irradiance_measurement(uv_irradiance, sensor_temperature=None, uniformity_measurements=None, timestamp=None)`
Add UV irradiance measurement and update cumulative dose.

**Parameters:**
- `uv_irradiance` (float): UV irradiance in W/m²
- `sensor_temperature` (float, optional): Sensor temperature in °C
- `uniformity_measurements` (list, optional): List of irradiance values at multiple points
- `timestamp` (datetime, optional): Measurement timestamp

**Returns:** `IrradianceData` object

##### `add_environmental_measurement(module_temperature, ambient_temperature, relative_humidity, air_velocity=None, barometric_pressure=None, timestamp=None)`
Add environmental conditions measurement.

**Parameters:**
- `module_temperature` (float): Module surface temperature in °C
- `ambient_temperature` (float): Chamber ambient temperature in °C
- `relative_humidity` (float): Relative humidity in %
- `air_velocity` (float, optional): Air velocity in m/s
- `barometric_pressure` (float, optional): Barometric pressure in kPa
- `timestamp` (datetime, optional): Measurement timestamp

**Returns:** `EnvironmentalData` object

##### `add_spectral_measurement(wavelengths, irradiance_values, timestamp=None)`
Add spectral irradiance measurement.

**Parameters:**
- `wavelengths` (list): Wavelengths in nm
- `irradiance_values` (list): Irradiance values in W/m²/nm
- `timestamp` (datetime, optional): Measurement timestamp

**Returns:** `SpectralData` object

##### `add_electrical_characterization(voc, isc, pmax, ff, efficiency=None, series_resistance=None, shunt_resistance=None, iv_curve=None, is_pre_test=True, timestamp=None)`
Add electrical characterization data.

**Parameters:**
- `voc` (float): Open circuit voltage in V
- `isc` (float): Short circuit current in A
- `pmax` (float): Maximum power in W
- `ff` (float): Fill factor
- `efficiency` (float, optional): Efficiency in %
- `series_resistance` (float, optional): Series resistance in Ω
- `shunt_resistance` (float, optional): Shunt resistance in Ω
- `iv_curve` (list, optional): I-V curve data as [(V, I), ...]
- `is_pre_test` (bool): True for pre-test, False for post-test
- `timestamp` (datetime, optional): Measurement timestamp

**Returns:** `ElectricalParameters` object

##### `get_cumulative_dose()`
Get current cumulative UV dose.

**Returns:** float (kWh/m²)

##### `get_remaining_dose()`
Get remaining UV dose to reach target.

**Returns:** float (kWh/m²)

##### `get_dose_completion_percentage()`
Get test completion percentage based on UV dose.

**Returns:** float (0-100%)

##### `estimate_remaining_time()`
Estimate remaining exposure time based on current irradiance.

**Returns:** float (hours) or None

##### `calculate_power_degradation()`
Calculate power degradation percentage.

**Returns:** float (%) or None

##### `check_acceptance_criteria()`
Check if test results meet acceptance criteria.

**Returns:** dict with pass/fail status and details

##### `complete_test_session()`
Complete the current test session.

**Returns:** `TestSession` object

##### `abort_test_session(reason="")`
Abort the current test session.

**Parameters:**
- `reason` (str): Reason for aborting

**Returns:** `TestSession` object

##### `export_session_data(output_path)`
Export session data to JSON file.

**Parameters:**
- `output_path` (Path): Output file path

**Returns:** Path to created file

##### `get_session_summary()`
Get summary of current test session.

**Returns:** dict with session summary metrics

---

## Database Schema

### Tables

1. **uv001_test_sessions** - Main session tracking
2. **uv001_irradiance_measurements** - UV irradiance data
3. **uv001_environmental_measurements** - Environmental conditions
4. **uv001_spectral_measurements** - Spectral distribution
5. **uv001_electrical_characterization** - I-V characterization
6. **uv001_visual_inspections** - Visual inspection findings
7. **uv001_test_events** - Events and incidents
8. **uv001_test_results** - Final results and analysis
9. **uv001_equipment_usage** - Equipment tracking
10. **uv001_data_quality** - Data quality metrics

### Key Relationships

- All measurement tables have foreign key to `uv001_test_sessions.session_id`
- Cascade delete ensures data integrity
- Indexes on `session_id` and `timestamp` for performance

### Views

- **uv001_session_summary** - Session summary with counts
- **uv001_compliance_monitoring** - Real-time compliance tracking
- **uv001_equipment_calibration_status** - Equipment calibration status

---

## UI Components

### Streamlit Application

The GenSpark UI provides real-time monitoring and visualization.

#### Features

1. **Live Monitoring Dashboard**
   - Real-time irradiance plot
   - Temperature monitoring
   - Current values display
   - Compliance indicators

2. **Cumulative Dose Tracking**
   - Dose accumulation graph
   - Target progress indicator
   - Estimated time remaining
   - Dose rate metrics

3. **Environmental Monitoring**
   - Temperature profiles
   - Humidity tracking
   - Temperature distribution histogram
   - Compliance statistics

4. **Spectral Analysis**
   - Spectral distribution plots
   - UVA/UVB percentage tracking
   - Peak wavelength monitoring
   - Compliance indicators

5. **Electrical Data Comparison**
   - Pre/post characterization
   - Degradation analysis
   - I-V curve comparison
   - Pass/fail determination

#### Running the UI

```bash
streamlit run ui/components/uv_preconditioning_ui.py
```

Access at: `http://localhost:8501`

---

## Quality Control

### Data Quality Checks

1. **Completeness**
   - Minimum measurement count verification
   - No gaps > 15 minutes in critical data
   - All required fields populated

2. **Consistency**
   - Timestamps in chronological order
   - No duplicate measurements
   - Parameter ranges validated

3. **Accuracy**
   - Sensor calibration verified
   - Out-of-range values flagged
   - Statistical outliers identified

### Documentation Requirements

1. **Test Records**
   - Complete measurement logs
   - Calibration certificates
   - Equipment usage records
   - Event logs

2. **Visual Documentation**
   - Pre-test photos (all sides)
   - Post-test photos (all sides)
   - Defect close-ups
   - Timestamped images

3. **Test Report**
   - Session summary
   - Measurement statistics
   - Compliance analysis
   - Pass/fail determination
   - Signatures (operator, reviewer, approver)

### Traceability

All data includes:
- Unique session ID
- Timestamps (ISO 8601 format)
- Operator identification
- Equipment serial numbers
- Calibration dates
- Audit trail

---

## References

1. **IEC 61215:2021** - Terrestrial photovoltaic (PV) modules - Design qualification and type approval
2. **IEC 60904-9:2020** - Photovoltaic devices - Part 9: Solar simulator performance requirements
3. **ISO 9060:2018** - Solar energy - Specification and classification of instruments for measuring hemispherical solar and direct solar radiation

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-14 | Protocol Development Team | Initial release |

---

## Support

For questions or issues:
- Review this documentation
- Check unit tests for usage examples
- Consult IEC 61215 standard
- Contact protocol development team

---

**Document End**
