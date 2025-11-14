# FIRE-001: Fire Resistance Testing Protocol - User Guide

## Protocol Information

- **Protocol ID:** FIRE-001
- **Protocol Name:** Fire Resistance Testing Protocol
- **Version:** 1.0.0
- **Category:** Safety
- **Standard:** IEC 61730-2 MST 23
- **Status:** Active

## Table of Contents

1. [Overview](#overview)
2. [Safety Requirements](#safety-requirements)
3. [Equipment Requirements](#equipment-requirements)
4. [Test Procedure](#test-procedure)
5. [Data Collection](#data-collection)
6. [Acceptance Criteria](#acceptance-criteria)
7. [Using the System](#using-the-system)
8. [Troubleshooting](#troubleshooting)
9. [References](#references)

## Overview

### Purpose

The Fire Resistance Testing Protocol (FIRE-001) evaluates the fire resistance and flame propagation characteristics of photovoltaic (PV) modules when exposed to external fire sources, in accordance with IEC 61730-2 MST 23.

### Scope

This protocol applies to all PV modules intended for:
- Roof-mounted applications
- Building-integrated photovoltaic (BIPV) systems
- Any application where fire safety is a concern

### Test Duration

- **Sample Conditioning:** Minimum 24 hours
- **Test Execution:** 4-6 hours per sample
- **Post-test Analysis:** 2-3 hours

## Safety Requirements

### Personal Protective Equipment (PPE)

All personnel must wear:
- Fire-resistant lab coat
- Safety goggles with side shields
- Heat-resistant gloves
- Closed-toe shoes
- Face shield (recommended during flame application)

### Safety Procedures

1. Conduct test in well-ventilated area or fume hood
2. Have fire extinguisher readily available (Class ABC)
3. Ensure emergency stop procedures are in place
4. Keep flammable materials at least 3 meters from test area
5. Minimum 2 personnel required during testing
6. Review all Material Safety Data Sheets (MSDS) before testing

### Emergency Contacts

- Fire Department: [Emergency Services]
- Safety Officer: [Contact Information Required]
- Facility Manager: [Contact Information Required]

## Equipment Requirements

### Required Equipment

| Equipment ID | Name | Calibration Required | Interval |
|-------------|------|---------------------|----------|
| EQ-FIRE-001 | Fire Test Apparatus | Yes | 180 days |
| EQ-FIRE-002 | Propane Gas Supply | No | N/A |
| EQ-FIRE-003 | Temperature Measurement System | Yes | 365 days |
| EQ-FIRE-004 | Timer System | Yes | 365 days |
| EQ-FIRE-005 | Mounting Fixture | No | N/A |
| EQ-FIRE-006 | Video Recording System | No | N/A |
| EQ-FIRE-007 | Measuring Tape | Yes | 730 days |

### Calibration Requirements

All equipment requiring calibration must have:
- Valid NIST-traceable calibration certificate
- Calibration within specified interval
- Documentation accessible during test

## Test Procedure

### Phase 1: Preparation

#### Step 1: Sample Reception
1. Receive module samples
2. Verify identification:
   - Module serial number
   - Manufacturer
   - Model number
   - Date of manufacture
3. Inspect for visible damage
4. Document condition with photographs

#### Step 2: Conditioning
1. Place samples in controlled environment:
   - Temperature: 23 ± 5°C
   - Relative Humidity: 50 ± 20%
   - Duration: Minimum 24 hours
2. Record environmental conditions hourly
3. Verify conditioning completion before testing

#### Step 3: Pre-Test Inspection
1. Document initial condition:
   - Photograph front surface
   - Photograph back surface
   - Photograph edges and frame
2. Record dimensional measurements
3. Complete pre-test checklist

#### Step 4: Equipment Setup
1. Set up fire test apparatus
2. Verify all calibrations current
3. Test gas flow rate
4. Position thermocouples
5. Set up video recording

### Phase 2: Test Execution

#### Step 5: Module Mounting
1. Mount module in test fixture
2. Angle: 20° from horizontal
3. Orientation: Front surface facing up
4. Secure in non-combustible mounting frame

#### Step 6: Flame Application Setup
1. Position flame source:
   - Distance: 125 ± 10 mm from module surface
   - Angle: 20° from horizontal
2. Verify flame temperature: 650 ± 50°C
3. Set gas flow rate per IEC 61730-2
4. Start video recording

#### Step 7: Ignition Test
1. Start timer
2. Apply flame to module surface
3. Duration: 600 seconds (10 minutes)
4. Monitor and record every 30 seconds:
   - Flame spread distance
   - Ignition observation
   - Smoke generation
   - Dripping/falling materials
   - Surface temperature
5. Document all events with timestamps

#### Step 8: Post-Flame Observation
1. Remove flame source
2. Monitor for 600 seconds (10 minutes)
3. Record:
   - Self-extinguishing time
   - Continued smoldering
   - Flame spread progression
   - Material integrity

### Phase 3: Post-Test

#### Step 9: Cooling Period
1. Allow sample to cool (minimum 30 minutes)
2. Do not touch until completely cool
3. Monitor for delayed ignition or smoldering

#### Step 10: Post-Test Inspection
1. Measure damage:
   - Flame spread distance (mm)
   - Burned area dimensions
   - Depth of damage
   - Material loss
2. Document with photographs
3. Complete post-test checklist

## Data Collection

### Real-Time Measurements

Record at 30-second intervals:

1. **Surface Temperature**
   - Unit: °C
   - Range: 0-1200°C
   - Accuracy: ± 2°C

2. **Flame Spread Distance**
   - Unit: mm
   - Measurement method: Measuring tape
   - Record maximum extent

3. **Time to Ignition**
   - Unit: seconds
   - Note exact time if ignition occurs

4. **Burning Duration**
   - Unit: seconds
   - From ignition to self-extinguishing

### Qualitative Observations

1. **Ignition Occurrence:** Yes/No
2. **Self-Extinguishing:** Yes/No
3. **Dripping Materials:** Yes/No
4. **Smoke Generation:** None/Light/Moderate/Heavy
5. **Material Integrity:** Intact/Minor Damage/Moderate Damage/Severe Damage/Failure

## Acceptance Criteria

### Critical Criteria (Must Pass All)

| Criterion | Requirement | Pass Condition |
|-----------|------------|----------------|
| No Sustained Burning | Module must self-extinguish within 60 seconds after flame removal | ≤ 60 seconds |
| Limited Flame Spread | Flame spread must not exceed 100 mm from application point | ≤ 100 mm |
| No Flaming Drips | No flaming material shall drip from the module | No flaming drips observed |

### Major Criteria

| Criterion | Requirement | Pass Condition |
|-----------|------------|----------------|
| Material Integrity | Module structure must remain substantially intact | No through-penetration or structural failure |
| No External Ignition | Module must not cause ignition of adjacent materials | No secondary ignitions |

### Overall Pass Requirement

- **PASS:** All critical criteria met, all major criteria met
- **CONDITIONAL:** All critical criteria met, one or more major criteria failures (requires engineering review)
- **FAIL:** Any critical criterion failure

## Using the System

### Web Interface (Streamlit)

#### 1. Starting the Application

```bash
streamlit run src/ui/fire_resistance_ui.py
```

#### 2. Sample Registration

1. Navigate to "Sample Registration"
2. Fill in required fields:
   - Sample ID
   - Manufacturer
   - Model Number
   - Serial Number
3. Enter optional information:
   - Batch number
   - Dimensions
   - Weight
4. Click "Register Sample"

#### 3. Test Execution

1. Navigate to "Test Execution"
2. Click "Create New Test Session"
3. Enter test personnel names
4. Record environmental conditions
5. Click "Start Test Session"
6. Record measurements during test
7. Complete test observations
8. Click "Finalize Test"

#### 4. Generating Reports

1. Navigate to "Test Reports"
2. Enter report information
3. Provide required signatures
4. Click "Generate Report"
5. Export in desired format (JSON/CSV)

### Python API

#### Basic Usage

```python
from handlers.fire_resistance_handler import FireResistanceProtocolHandler
from models.fire_resistance_model import SampleInformation, TestObservations

# Initialize handler
handler = FireResistanceProtocolHandler()

# Create sample
sample = SampleInformation(
    sample_id="SMP-001",
    manufacturer="Solar Tech Inc",
    model_number="ST-400",
    serial_number="SN123456"
)

# Create test session
test = handler.create_test_session(
    sample=sample,
    test_personnel=["Tech A", "Engineer B"]
)

# Record measurements
handler.record_measurement(
    elapsed_time_seconds=30.0,
    surface_temperature_c=150.5,
    flame_spread_mm=25.0
)

# Finalize test
observations = TestObservations(
    ignition_occurred=True,
    self_extinguishing_time_seconds=45.0,
    max_flame_spread_mm=75.0
)

results = handler.finalize_test(observations)

# Generate report
report = handler.generate_report(
    test_results=results,
    prepared_by="Tech A",
    reviewed_by="Engineer B",
    approved_by="Quality Manager"
)
```

### Database Integration

The system uses SQLAlchemy ORM for database operations:

```python
from db.models import DatabaseManager, TestSession, Sample

# Initialize database
db = DatabaseManager("sqlite:///fire_resistance_lims.db")
db.create_all_tables()

# Get session
session = db.get_session()

# Query tests
tests = session.query(TestSession).filter_by(test_status='Test Complete').all()
```

## Troubleshooting

### Common Issues

#### Issue: Calibration Expired

**Symptom:** System rejects equipment due to expired calibration

**Solution:**
1. Check calibration due dates in Equipment Calibration page
2. Schedule recalibration with metrology lab
3. Update calibration records in system
4. Verify calibration before retrying test

#### Issue: Environmental Conditions Out of Spec

**Symptom:** Temperature or humidity outside acceptable range

**Solution:**
1. Allow conditioning environment to stabilize
2. Check HVAC system operation
3. Wait for conditions to return to specification
4. Extend conditioning period if necessary

#### Issue: Data Acquisition Failure

**Symptom:** Measurements not recording properly

**Solution:**
1. Verify thermocouple connections
2. Check data logger power and configuration
3. Test measurement system with known calibration source
4. If problem persists, issue nonconformance report

#### Issue: Inconsistent Results

**Symptom:** Results vary significantly between samples

**Solution:**
1. Review test setup for consistency
2. Verify flame positioning and temperature
3. Check sample orientation
4. Review operator technique
5. Consider material variability
6. Consult with engineering team

## Quality Control

### Pre-Test QC Checks

- [ ] Equipment calibrations current
- [ ] Environmental conditions within spec
- [ ] Sample conditioning complete (≥ 24 hours)
- [ ] Pre-test photos taken
- [ ] All personnel trained and competent
- [ ] Safety equipment available

### During Test QC Checks

- [ ] Data acquisition system functioning
- [ ] Video recording active
- [ ] Measurements recorded at specified intervals
- [ ] Observations documented in real-time

### Post-Test QC Checks

- [ ] All data collected completely
- [ ] Measurements validated
- [ ] Photos documented
- [ ] Equipment inspected for damage
- [ ] Test area cleaned and secured

## Data Retention

- **Raw Data:** 10 years
- **Test Reports:** Permanent
- **Sample Retention:** 90 days (unless failure)
- **Failed Samples:** 1 year or until resolution
- **Calibration Records:** Life of equipment + 5 years

## References

1. IEC 61730-2:2023 - Photovoltaic (PV) module safety qualification - Part 2: Requirements for testing
2. IEC 61730-1:2023 - Photovoltaic (PV) module safety qualification - Part 1: Requirements for construction
3. ISO/IEC 17025:2017 - General requirements for the competence of testing and calibration laboratories
4. 21 CFR Part 11 - Electronic Records; Electronic Signatures (if applicable)

## Training Requirements

### Initial Training

Personnel must complete:
1. IEC 61730-2 standard review
2. Fire safety procedures
3. Equipment operation training
4. Data collection procedures
5. Emergency response training
6. Competency assessment

### Refresher Training

- **Frequency:** Annual
- **Content:** Protocol updates, safety review, equipment changes
- **Assessment:** Competency verification required

## Contact Information

**Protocol Owner:** [Name and Contact]

**Quality Manager:** [Name and Contact]

**Technical Support:** [Contact Information]

**Emergency Contact:** [24/7 Contact Number]

---

**Document Control:**
- Version: 1.0.0
- Last Updated: 2025-11-14
- Next Review: 2026-11-14
- Approval: Quality Manager
