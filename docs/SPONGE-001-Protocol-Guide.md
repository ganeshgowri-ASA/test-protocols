# SPONGE-001: Sponge Effect Testing Protocol

## Protocol Overview

**Protocol ID:** SPONGE-001
**Version:** 1.0.0
**Category:** Degradation Testing
**Subcategory:** Moisture Absorption

### Purpose

The SPONGE-001 protocol evaluates the reversible and irreversible effects of moisture absorption and desorption cycles on photovoltaic (PV) module performance. This test characterizes the "sponge effect" where modules absorb moisture under humid conditions and release it under dry conditions, potentially causing performance degradation.

### Standard References

- IEC 61215-2:2021 - Terrestrial photovoltaic (PV) modules - Design qualification and type approval
- IEC 61730 - Photovoltaic (PV) module safety qualification
- UL 1703 - Standard for Safety Flat-Plate Photovoltaic Modules and Panels

## Test Principles

### The Sponge Effect

PV modules can absorb moisture through:
1. **Edge seal penetration** - Moisture ingress through module edges
2. **Backsheet permeation** - Diffusion through polymeric backsheet
3. **Junction box seals** - Gaps in enclosure seals

This absorbed moisture can cause:
- **Reversible degradation**: Temporary performance loss when moisture is present
- **Irreversible degradation**: Permanent damage from corrosion, delamination, or EVA degradation

### Test Methodology

The protocol cycles modules between humid and dry phases to:
1. Quantify moisture absorption/desorption rates
2. Measure reversible vs. irreversible performance losses
3. Assess module encapsulation quality
4. Identify failure modes related to moisture ingress

## Equipment Requirements

### Essential Equipment

1. **Climate Chamber**
   - Temperature range: 20-95°C (±2°C stability)
   - Humidity range: 5-95% RH (±3% stability)
   - Programmable cycle control
   - Data logging capability

2. **IV Curve Tracer / Solar Simulator**
   - Class AAA solar simulator (IEC 60904-9)
   - STC capability (1000 W/m², 25°C, AM1.5G)
   - Measurement accuracy: ±2%

3. **Precision Balance**
   - Capacity: 50 kg
   - Resolution: 0.01 g
   - Repeatability: ±0.01 g

4. **Environmental Sensors**
   - Type K thermocouples (±0.1°C)
   - Capacitive humidity sensors (±0.5% RH)
   - Data acquisition system (1 Hz minimum)

### Additional Equipment

- Electroluminescence (EL) imaging system
- Megohmmeter (insulation resistance testing)
- Visual inspection tools (microscope, UV lamp)

## Test Parameters

### Default Configuration

| Parameter | Default Value | Range | Unit |
|-----------|--------------|-------|------|
| Humidity Cycles | 10 | 5-50 | cycles |
| Humid Phase Temperature | 85.0 | 60-95 | °C |
| Humid Phase RH | 85.0 | 60-95 | % |
| Humid Phase Duration | 24 | 12-168 | hours |
| Dry Phase Temperature | 25.0 | 20-40 | °C |
| Dry Phase RH | 10.0 | 5-30 | % |
| Dry Phase Duration | 24 | 12-168 | hours |
| Measurement Interval | 60 | 1-1440 | minutes |

### Sample Requirements

- **Minimum sample size:** 3 modules
- **Sample condition:** New or field-aged modules
- **Pre-conditioning:** Stabilize at room temperature for 24 hours

## Test Procedure

### Phase 1: Initial Characterization

1. **Visual Inspection**
   - Photograph all modules
   - Document any pre-existing defects
   - Perform EL imaging

2. **Weight Measurement**
   - Weigh each module 3 times
   - Calculate average initial weight
   - Record ambient conditions

3. **Electrical Characterization**
   - Perform IV curve measurement at STC
   - Record Pmax, Voc, Isc, FF
   - Repeat 3 times for each module
   - Allow 5-minute stabilization between measurements

4. **Insulation Resistance**
   - Measure at 1000 VDC
   - Must be >40 MΩ

### Phase 2: Cycling

For each cycle (1 to N):

#### Humid Phase

1. **Chamber Setup**
   - Set temperature to configured value (default 85°C)
   - Set humidity to configured value (default 85% RH)
   - Allow chamber to stabilize (±2°C, ±3% RH)

2. **Module Exposure**
   - Place modules in chamber
   - Duration: configured hours (default 24h)
   - Monitor T and RH continuously

3. **Post-Humid Measurements**
   - Remove modules carefully
   - Weigh immediately (within 2 minutes)
   - Record environmental conditions
   - Return to chamber if not moving to dry phase

#### Dry Phase

1. **Chamber Setup**
   - Set temperature to configured value (default 25°C)
   - Set humidity to configured value (default 10% RH)
   - Allow chamber to stabilize

2. **Module Exposure**
   - Transfer modules to dry chamber
   - Duration: configured hours (default 24h)
   - Monitor T and RH continuously

3. **Post-Dry Measurements**
   - Weigh modules
   - Perform IV curve measurement
   - Record Pmax, Voc, Isc, FF
   - Document any visual changes

### Phase 3: Final Characterization

1. **Final Weight Measurement**
   - Weigh 3 times, record average
   - Compare to initial weight

2. **Final Electrical Test**
   - Complete IV curve at STC
   - Record all parameters
   - Calculate degradation

3. **Final Inspection**
   - Visual inspection for defects
   - EL imaging
   - Document changes from initial

4. **Insulation Resistance**
   - Measure at 1000 VDC
   - Compare to initial value

## Data Analysis

### Moisture Metrics

#### Moisture Absorption Rate
```
Absorption (%) = ((W_humid - W_initial) / W_initial) × 100
```
Where:
- W_humid = weight after humid phase
- W_initial = initial weight

#### Moisture Desorption Rate
```
Desorption (%) = ((W_humid - W_dry) / W_humid) × 100
```
Where:
- W_dry = weight after dry phase

#### Sponge Coefficient
```
Sponge Coefficient = Absorption (%) / Desorption (%)
```
A value close to 1.0 indicates good reversibility.
Values >1.0 indicate moisture retention (hysteresis).

### Performance Degradation

#### Maximum Power Degradation
```
ΔPmax (%) = ((Pmax_initial - Pmax_final) / Pmax_initial) × 100
```

#### Reversible Degradation
```
Reversible (%) = ((Pmax_post_humid - Pmax_post_dry) / Pmax_initial) × 100
```
Performance loss that recovers after drying.

#### Irreversible Degradation
```
Irreversible (%) = ((Pmax_initial - Pmax_dry_equilibrium) / Pmax_initial) × 100
```
Permanent performance loss after moisture removal.

### Statistical Analysis

1. **Descriptive Statistics**
   - Mean, standard deviation, min, max for each metric
   - Coefficient of variation (CV)

2. **Trend Analysis**
   - Linear regression of Pmax vs. cycle number
   - Correlation: moisture content vs. performance

3. **ANOVA**
   - Compare degradation between samples
   - Identify significant differences

## Quality Control

### Acceptance Criteria

| Parameter | Threshold | Comparison | Severity |
|-----------|-----------|------------|----------|
| Pmax Degradation | 5.0% | < | FAIL |
| Moisture Absorption | 2.0% | < | WARNING |
| Insulation Resistance | 40 MΩ | > | FAIL |
| Visual Defects | 0 | = | WARNING |

### Data Validation Checks

1. **Temperature Stability**
   - Standard deviation < 2.0°C during each phase
   - Flag excursions for review

2. **Humidity Stability**
   - Standard deviation < 3.0% RH during each phase
   - Flag excursions for review

3. **Measurement Completeness**
   - <5% missing data points allowed
   - Document reasons for missing data

4. **Weight Monotonicity**
   - Weight should increase during humid phase
   - Weight should decrease during dry phase
   - Flag anomalies for investigation

## Reporting

### Report Sections

1. **Executive Summary**
   - Test overview
   - Key findings
   - Pass/fail status
   - Recommendations

2. **Test Configuration**
   - Protocol details
   - Test parameters
   - Sample information
   - Equipment list

3. **Environmental Data**
   - Temperature/humidity plots
   - Stability analysis
   - Deviations log

4. **Performance Results**
   - IV curves (initial vs. final)
   - Pmax degradation analysis
   - Electrical parameters table
   - Trend plots

5. **Moisture Analysis**
   - Weight change plots
   - Absorption/desorption rates
   - Sponge coefficient analysis
   - Correlation plots

6. **Quality Control**
   - Acceptance criteria check
   - Data validation results
   - Identified anomalies

7. **Visual Inspection**
   - EL images comparison
   - Defect documentation
   - Degradation modes

8. **Conclusions**
   - Summary of findings
   - Compliance statement
   - Failure modes identified
   - Recommendations

### Export Formats

- **PDF** - Complete formatted report
- **HTML** - Interactive web report
- **CSV** - Raw measurement data
- **JSON** - Structured data with metadata

## Usage Examples

### Python API

```python
from protocols.sponge_effect.implementation import SpongeProtocol, TestParameters

# Initialize protocol
protocol = SpongeProtocol()

# Configure test parameters
params = TestParameters(
    humidity_cycles=10,
    humid_phase_temperature=85.0,
    humid_phase_rh=85.0,
    humid_phase_duration=24,
    dry_phase_temperature=25.0,
    dry_phase_rh=10.0,
    dry_phase_duration=24
)

# Create test plan
sample_ids = ['MODULE-001', 'MODULE-002', 'MODULE-003']
test_plan = protocol.create_test_plan(params, sample_ids)

# Record measurements
protocol.record_measurement(
    sample_id='MODULE-001',
    cycle=0,
    phase=TestPhase.INITIAL,
    weight_g=18000.0,
    pmax_w=300.0,
    voc_v=38.5,
    isc_a=9.0,
    ff_percent=76.5
)

# Analyze results
analysis = protocol.analyze_sample('MODULE-001')
print(f"Pmax Degradation: {analysis.pmax_degradation_percent:.2f}%")
print(f"Moisture Absorption: {analysis.moisture_absorption_percent:.3f}%")
print(f"Status: {analysis.pass_fail}")

# Generate report
report = protocol.generate_report(output_path='./reports/sponge_001_report.json')

# Export data
protocol.export_data('./data', formats=['csv', 'json', 'excel'])
```

### Streamlit UI

```bash
# Launch UI
streamlit run protocols/sponge-effect/ui_components.py
```

Navigate through:
1. **Configuration** - Set test parameters
2. **Data Entry** - Record measurements
3. **Monitoring** - Real-time dashboard
4. **Analysis** - View results
5. **Export** - Generate reports

## Database Integration

### Connection Setup

```python
from database.models import DatabaseManager, SpongeDataAccess

# Initialize database
db = DatabaseManager('postgresql://user:pass@localhost/testdb')
db.create_tables()

# Create session
session = db.get_session()
dao = SpongeDataAccess(session)

# Create test
test = dao.create_test(
    protocol_version='1.0.0',
    operator_id='operator@example.com',
    chamber_id='CHAMBER-01',
    test_parameters={'cycles': 10}
)

# Create samples
sample = dao.create_sample(
    test_id=test.test_id,
    sample_serial='MODULE-001',
    manufacturer='Example Corp',
    model='EX-300'
)

# Record measurement
measurement = dao.create_measurement(
    sample_id=sample.sample_id,
    cycle_number=0,
    phase='initial',
    weight_g=18000.0,
    pmax_w=300.0
)
```

### Views and Queries

```sql
-- Get test summary
SELECT * FROM vw_sponge_test_summary WHERE test_id = 'xxx';

-- Get sample performance
SELECT * FROM vw_sponge_sample_performance WHERE sample_serial = 'MODULE-001';

-- Get cycle data
SELECT * FROM vw_sponge_cycle_data
WHERE sample_id = 'xxx'
ORDER BY cycle_number;
```

## Troubleshooting

### Common Issues

**Issue:** Weight measurements inconsistent
- **Cause:** Temperature variations affecting balance
- **Solution:** Allow modules to equilibrate to room temperature before weighing

**Issue:** Humidity chamber not stabilizing
- **Cause:** Overloading or poor air circulation
- **Solution:** Reduce sample count, ensure proper spacing

**Issue:** IV curve measurements noisy
- **Cause:** Module temperature not stabilized
- **Solution:** Allow longer stabilization time at STC

**Issue:** Large reversible degradation
- **Cause:** Normal moisture presence in encapsulant
- **Solution:** Extend dry phase duration for complete drying

## References

1. IEC 61215-2:2021, *Terrestrial photovoltaic (PV) modules - Design qualification and type approval - Part 2: Test procedures*
2. IEC 61730, *Photovoltaic (PV) module safety qualification*
3. Kempe, M.D. (2006). "Modeling of rates of moisture ingress into photovoltaic modules." *Solar Energy Materials and Solar Cells*, 90(16), 2720-2738.
4. Jiang, S. et al. (2018). "Sponge effect in photovoltaic modules: The moisture absorption and desorption." *Solar Energy*, 162, 455-463.

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-11-14 | Test Protocols Team | Initial release |

## Contact

For questions or support:
- **Email:** protocols@example.com
- **Documentation:** https://docs.example.com/protocols/sponge-001
- **Issue Tracker:** https://github.com/example/test-protocols/issues
