# SAND-001: Sand and Dust Resistance Test Protocol

## Overview

The SAND-001 protocol implements sand and dust resistance testing for photovoltaic (PV) modules and components according to **IEC 60068-2-68** standard. This comprehensive testing framework provides real-time particle tracking, environmental monitoring, and automated acceptance criteria evaluation with full traceability.

## Standard Reference

- **Standard**: IEC 60068-2-68
- **Title**: Environmental testing - Part 2-68: Tests - Test L: Dust and sand
- **Category**: Environmental Testing
- **Protocol Version**: 1.0.0

## Features

### Core Capabilities

- ✅ **JSON-Based Protocol Template**: Dynamic, configurable test parameters
- ✅ **Real-Time Particle Tracking**: Multi-point spatial distribution monitoring
- ✅ **Environmental Monitoring**: Continuous temperature, humidity, and airflow tracking
- ✅ **Automated Data Collection**: High-frequency sensor data acquisition
- ✅ **GenSpark UI Integration**: Interactive Streamlit dashboard
- ✅ **Database Storage**: Comprehensive schema for long-term data retention
- ✅ **Acceptance Criteria Evaluation**: Automated pass/fail determination
- ✅ **Full Traceability**: Complete audit trail and data lineage

### Particle Tracking Features

- Multiple measurement point configuration
- Real-time concentration monitoring
- Particle size distribution analysis
- Spatial uniformity calculation
- Deposition rate tracking
- 3D visualization support

### Test Phases

1. **Pre-conditioning**: Initial specimen inspection and characterization
2. **Chamber Preparation**: Setup and calibration
3. **Environmental Stabilization**: Achieve target conditions
4. **Dust Exposure**: Controlled particle exposure
5. **Settling Period**: Particle settlement monitoring
6. **Post-Exposure Assessment**: Final evaluation and measurements

## Installation

### Requirements

```bash
# Core dependencies
pip install numpy pandas
pip install streamlit plotly
pip install dataclasses  # Python 3.6 compatibility

# Optional for database integration
pip install sqlalchemy mysql-connector-python
```

### Directory Structure

```
test-protocols/
├── protocols/
│   └── SAND-001.json           # Protocol definition
├── src/
│   └── python/
│       └── protocols/
│           ├── __init__.py
│           └── sand_dust_test.py  # Main implementation
├── ui/
│   └── components/
│       └── sand_dust_monitor.py   # Streamlit UI
├── database/
│   └── schemas/
│       └── sand_dust_test_schema.sql  # Database schema
├── tests/
│   ├── __init__.py
│   └── test_sand_dust_protocol.py    # Comprehensive tests
└── docs/
    └── SAND-001-README.md            # This file
```

## Quick Start

### 1. Basic Test Setup

```python
from protocols.sand_dust_test import (
    SandDustResistanceTest,
    TestConfiguration,
    SpecimenData,
    SeverityLevel
)

# Configure test parameters
config = TestConfiguration(
    dust_type="Arizona Test Dust",
    particle_size_range=(0.1, 200.0, 50.0),
    dust_concentration=0.01,  # kg/m³
    target_temperature=25.0,   # °C
    target_humidity=50.0,      # %
    target_air_velocity=2.0,   # m/s
    exposure_time_hours=8.0,
    cycles=1,
    settling_time_hours=1.0
)

# Define specimen
specimen = SpecimenData(
    specimen_id="PV-MOD-001",
    specimen_type="PV Module",
    manufacturer="Example Solar Co.",
    model="ESC-300W",
    serial_number="SN123456",
    initial_weight=5000.0,
    initial_dimensions=(1000.0, 600.0, 40.0),
    initial_surface_roughness=0.5
)

# Create test instance
test = SandDustResistanceTest("TEST-001", config, specimen)
```

### 2. Run Test with Particle Tracking

```python
# Start test
test.start_test()

# Initialize particle tracking
measurement_points = [
    {'point_id': 'P001', 'location': (100, 200, 300)},
    {'point_id': 'P002', 'location': (400, 200, 300)},
    {'point_id': 'P003', 'location': (700, 200, 300)}
]
test.initialize_particle_tracking(measurement_points)

# Advance through phases
test.advance_phase(TestPhase.CHAMBER_PREP)
test.advance_phase(TestPhase.STABILIZATION)
test.advance_phase(TestPhase.DUST_EXPOSURE)

# Record environmental data
test.record_environmental_conditions(
    temperature=25.5,
    humidity=51.0,
    air_velocity=2.1,
    atmospheric_pressure=101.325,
    dust_concentration=0.0102
)

# Record particle measurements
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

# Check uniformity
is_uniform, uniformity = test.check_particle_uniformity(threshold=0.7)
print(f"Particle distribution uniformity: {uniformity:.2%}")
```

### 3. Post-Test Evaluation

```python
# Complete exposure phase
test.complete_exposure_phase()
test.advance_phase(TestPhase.POST_ASSESSMENT)

# Record post-test measurements
test.record_post_test_measurements(
    weight=5002.5,
    dimensions=(1000.0, 600.0, 40.0),
    surface_roughness=1.2,
    deposited_dust_weight=2.5,
    ingress_severity=SeverityLevel.LEVEL_2,
    electrical_params={
        'power': 297,
        'Isc': 9.9,
        'Voc': 39.5,
        'FF': 0.74
    }
)

# Evaluate acceptance criteria
evaluation = test.evaluate_acceptance_criteria()
print(f"Test Result: {'PASS' if evaluation['overall_pass'] else 'FAIL'}")

# Complete test
test.complete_test()

# Export results
test.export_results('./results')
```

## Streamlit UI Usage

### Launch Real-Time Monitor

```bash
streamlit run ui/components/sand_dust_monitor.py
```

### UI Features

- **Test Control Panel**: Start, pause, and stop test execution
- **Real-Time Environmental Monitoring**: Live charts and metrics
- **Particle Tracking Visualization**: 3D distribution maps
- **Phase Progress Indicator**: Visual test timeline
- **Alerts and Deviations**: Automatic out-of-tolerance notifications
- **Data Export**: Generate reports and export data

## Database Schema

### Key Tables

#### `test_sessions`
Stores main test session information with full traceability.

```sql
session_id, protocol_id, started_at, completed_at, test_status,
test_result, operator_id, configuration_json
```

#### `environmental_data`
Time-series environmental monitoring data.

```sql
session_id, timestamp, temperature_c, humidity_percent,
air_velocity_m_s, dust_concentration_kg_m3, in_tolerance
```

#### `particle_measurements`
High-frequency particle tracking measurements.

```sql
session_id, point_id, timestamp, particle_size_microns,
particle_count, concentration_kg_m3, velocity_x_m_s,
velocity_y_m_s, velocity_z_m_s
```

#### `acceptance_results`
Final test results and acceptance criteria evaluation.

```sql
session_id, dust_ingress_pass, electrical_performance_pass,
physical_integrity_pass, surface_degradation_pass, overall_pass
```

### Database Setup

```bash
# MySQL/MariaDB
mysql -u username -p database_name < database/schemas/sand_dust_test_schema.sql

# PostgreSQL (with modifications)
psql -U username -d database_name -f database/schemas/sand_dust_test_schema.sql
```

## Protocol JSON Structure

The protocol definition in `protocols/SAND-001.json` includes:

### Test Parameters

- **Dust Chamber**: Volume, type, configuration
- **Test Dust**: Type, particle size, concentration, composition
- **Environmental Conditions**: Temperature, humidity, air velocity, pressure
- **Test Duration**: Exposure time, cycles, settling time
- **Particle Tracking**: Sampling intervals, measurement points

### Measurement Sequence

1. Pre-conditioning (2 hours)
2. Chamber preparation (0.5 hours)
3. Environmental stabilization (1 hour)
4. Dust exposure (variable)
5. Settling period (variable)
6. Post-exposure assessment (2 hours)

### Acceptance Criteria

#### Dust Ingress
- **Level ≤ 3**: Pass
- **Level > 3**: Fail

Severity Levels:
- Level 1: No visible dust ingress
- Level 2: Superficial dust, no functional impact
- Level 3: Dust ingress but no impairment
- Level 4: Partial functional impairment
- Level 5: Complete functional failure

#### Electrical Performance
- Power degradation: ≤ 5%
- Isc change: ≤ 3%
- Voc change: ≤ 3%
- FF change: ≤ 5%
- Insulation resistance: ≥ 40 MΩ @ 500V DC

#### Physical Integrity
- No cracks in protective covers
- No delamination
- No corrosion of metallic parts
- Seals remain intact
- Abrasion within acceptable limits

#### Surface Degradation
- Surface roughness increase: ≤ 2 μm
- Transmittance loss: ≤ 2%

## Testing

### Run Unit Tests

```bash
cd tests
python test_sand_dust_protocol.py
```

### Test Coverage

- ✅ Severity level definitions
- ✅ Particle data handling
- ✅ Environmental conditions
- ✅ Specimen data management
- ✅ Test configuration
- ✅ Particle tracker functionality
- ✅ Main test class operations
- ✅ Acceptance criteria evaluation
- ✅ Complete workflow integration

### Expected Output

```
test_advance_phase (test_sand_dust_protocol.TestSandDustResistanceTest) ... ok
test_check_particle_uniformity (test_sand_dust_protocol.TestSandDustResistanceTest) ... ok
test_complete_test (test_sand_dust_protocol.TestSandDustResistanceTest) ... ok
...
----------------------------------------------------------------------
Ran 45 tests in 0.523s

OK
```

## API Reference

### Main Classes

#### `SandDustResistanceTest`

Main test orchestration class.

**Methods:**
- `start_test()`: Initialize and start test
- `advance_phase(phase)`: Move to next test phase
- `initialize_particle_tracking(points)`: Setup particle tracking
- `record_environmental_conditions(...)`: Log environmental data
- `record_particle_measurement(...)`: Log particle data
- `check_particle_uniformity(threshold)`: Evaluate distribution
- `record_post_test_measurements(...)`: Final measurements
- `evaluate_acceptance_criteria()`: Assess pass/fail
- `complete_test()`: Finalize test
- `export_results(path)`: Save results to files
- `generate_report_data()`: Create report structure

#### `ParticleTracker`

Real-time particle tracking and analysis.

**Methods:**
- `record_measurement(...)`: Log particle measurement
- `get_particle_distribution()`: Get measurements by point
- `calculate_uniformity()`: Compute spatial uniformity
- `get_deposition_rate()`: Calculate deposition rates
- `export_data(filepath)`: Export tracking data

#### `TestConfiguration`

Test parameter configuration.

**Class Method:**
- `from_protocol(path)`: Load from JSON protocol

#### Data Classes

- `ParticleData`: Particle measurement record
- `EnvironmentalConditions`: Environmental snapshot
- `SpecimenData`: Specimen information and measurements

### Enums

#### `TestPhase`
- `INITIALIZATION`
- `PRE_CONDITIONING`
- `CHAMBER_PREP`
- `STABILIZATION`
- `DUST_EXPOSURE`
- `SETTLING`
- `POST_ASSESSMENT`
- `COMPLETE`
- `FAILED`

#### `SeverityLevel`
- `LEVEL_1` through `LEVEL_5`

## Integration Examples

### With LIMS System

```python
# Import test data to LIMS
from lims_connector import LIMSClient

lims = LIMSClient(api_url="https://lims.example.com/api")

# After test completion
test_data = test.generate_report_data()
lims.submit_test_results(
    protocol="SAND-001",
    specimen_id=test.specimen.specimen_id,
    results=test_data
)
```

### With QMS Integration

```python
# Record test in Quality Management System
from qms_connector import QMSClient

qms = QMSClient()
qms.create_test_record(
    test_id=test.test_id,
    protocol="SAND-001",
    standard="IEC 60068-2-68",
    operator=operator_id,
    result="PASS" if test.test_passed else "FAIL",
    traceability_data=test.results
)
```

### Automated Reporting

```python
# Generate PDF report
from report_generator import PDFReportGenerator

report_gen = PDFReportGenerator()
report_data = test.generate_report_data()

pdf_file = report_gen.create_report(
    template="sand_dust_test_report",
    data=report_data,
    output_path=f"./reports/{test.test_id}_report.pdf"
)
```

## Traceability Features

### Complete Audit Trail

- Test session creation timestamp
- Operator identification
- Equipment calibration records
- Dust lot number and certification
- Environmental condition history
- Particle tracking data
- Measurement timestamps
- Deviation logging
- Result evaluation chain

### Data Retention

- Raw data: Time-series storage
- Processed results: JSON export
- Images: File system with database references
- Reports: Generated on demand

### Compliance Documentation

- IEC 60068-2-68 standard reference
- Test method documentation
- Equipment calibration certificates
- Dust certification documentation
- Operator qualifications
- Measurement uncertainty analysis

## Troubleshooting

### Common Issues

#### 1. Out-of-Tolerance Conditions

**Issue**: Environmental parameters exceed tolerances
**Solution**:
- Check chamber calibration
- Verify sensor accuracy
- Adjust control systems
- Document deviations

#### 2. Non-Uniform Particle Distribution

**Issue**: Uniformity coefficient < 0.7
**Solution**:
- Adjust air circulation
- Check dust dispersion system
- Verify measurement point placement
- Increase stabilization time

#### 3. Database Connection Errors

**Issue**: Cannot store test data
**Solution**:
- Verify database credentials
- Check network connectivity
- Ensure schema is initialized
- Review connection pool settings

## Best Practices

### Test Preparation

1. Calibrate all sensors within 30 days of test
2. Verify dust certification and expiration
3. Clean chamber thoroughly before test
4. Document pre-test specimen condition
5. Verify measurement equipment functionality

### During Test

1. Monitor environmental parameters continuously
2. Check particle uniformity every 30 minutes
3. Document any deviations immediately
4. Maintain operator logbook
5. Capture images at each phase

### Post-Test

1. Allow adequate settling time
2. Follow standard cleaning procedures
3. Document all observations
4. Perform electrical testing promptly
5. Compare pre/post measurements carefully

## Support and Contribution

### Documentation

- Protocol JSON: `/protocols/SAND-001.json`
- Code documentation: In-line docstrings
- API reference: This document
- Test examples: `/tests/test_sand_dust_protocol.py`

### Contact

For questions, issues, or contributions, please refer to the project repository.

## Version History

### Version 1.0.0 (2025-11-14)
- Initial implementation
- IEC 60068-2-68 compliance
- Real-time particle tracking
- GenSpark UI integration
- Comprehensive test suite
- Full database schema
- Complete documentation

## License

See LICENSE file in repository root.

## References

1. IEC 60068-2-68: Environmental testing - Part 2-68: Tests - Test L: Dust and sand
2. ISO 12103-1: Test dust for filter evaluation
3. ASTM G154: Standard Practice for Operating Fluorescent Ultraviolet (UV) Lamp Apparatus
4. IEC 61215: Terrestrial photovoltaic (PV) modules - Design qualification and type approval

---

**Document Version**: 1.0.0
**Last Updated**: 2025-11-14
**Protocol**: SAND-001
**Standard**: IEC 60068-2-68
