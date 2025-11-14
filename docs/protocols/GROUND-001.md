# GROUND-001: Ground Continuity Test

## Overview

**Protocol ID**: GROUND-001
**Protocol Name**: Ground Continuity Test (Equipotential Bonding)
**Version**: 1.0.0
**Category**: Safety
**Standard**: IEC 61730-2:2023 MST 13

## Purpose

This test verifies the continuity of equipotential bonding between the PV module frame and all accessible conductive parts. It ensures that protective grounding connections are adequate to:

1. Prevent electric shock hazards
2. Provide a safe path for fault currents
3. Maintain equipotential bonding under rated current conditions

## Standard Reference

**IEC 61730-2:2023 - MST 13: Continuity Test of Equipotential Bonding**

This test is part of the Module Safety Test (MST) series defined in IEC 61730-2, which specifies safety requirements for photovoltaic modules to protect against electric shock, fire, and personal injury.

## Test Principles

The ground continuity test applies a high DC current (typically 2.5 times the maximum overcurrent protection rating) through the bonding path for a specified duration. The resistance is calculated from the measured voltage drop using Ohm's law:

```
R = V / I

Where:
- R = Resistance (Ω)
- V = Voltage drop (V)
- I = Test current (A)
```

## Test Parameters

### Input Parameters

| Parameter | Description | Unit | Required | Typical Range |
|-----------|-------------|------|----------|---------------|
| Max Overcurrent Protection | Maximum overcurrent protection device rating | A | Yes | 0.1 - 100 |
| Ambient Temperature | Temperature during test | °C | No | -10 to 50 |
| Relative Humidity | Humidity during test | % | No | 0 to 95 |

### Calculated Parameters

| Parameter | Formula | Unit | Typical Value |
|-----------|---------|------|---------------|
| Test Current | 2.5 × Max Overcurrent Protection | A | 37.5 (for 15A OCP) |
| Test Duration | Constant | s | 120 |
| Voltage Limit | Constant | V | 12 |
| Max Resistance | Constant | Ω | 0.1 |

## Measurements

The following measurements are recorded during the test:

1. **Voltage Drop** (V): Measured across the bonding connection under test current
2. **Actual Test Current** (A): The actual current applied during the test
3. **Measured Resistance** (Ω): Calculated from voltage and current (R = V/I)
4. **Test Duration** (s): Actual duration of current application
5. **Ambient Temperature** (°C): Environmental condition
6. **Relative Humidity** (%): Environmental condition

## Pass/Fail Criteria

The test PASSES if all of the following criteria are met:

### Critical Criteria

1. **Measured Resistance ≤ 0.1 Ω**
   - The resistance of the equipotential bonding must not exceed 0.1 Ω
   - This ensures low impedance path for fault currents

2. **Voltage Drop ≤ 12 V**
   - The voltage drop across the bonding connection must not exceed 12 V
   - This ensures adequate bonding even at high currents

3. **Test Duration ≥ 120 seconds**
   - The test must be conducted for at least 120 seconds
   - This verifies the bonding remains intact under sustained current

### Major Criteria

4. **Actual Test Current within ±5% of Calculated Test Current**
   - Ensures the test was conducted at the correct current level
   - Allows for small instrument tolerances

## Safety Limits

The following safety limits trigger automatic test abort:

| Limit | Value | Action | Description |
|-------|-------|--------|-------------|
| Max Voltage | 15 V | STOP | Emergency stop if voltage exceeds 15V |
| Max Current | 300 A | STOP | Emergency stop if current exceeds 300A |
| Max Temperature | 100 °C | ALARM | Alarm if connection temperature exceeds 100°C |

## Test Procedure

### Pre-Test Preparation

1. **Safety Verification**
   - Verify module is disconnected from all power sources
   - Use lockout/tagout procedures
   - Confirm module is properly grounded

2. **Environmental Recording**
   - Record ambient temperature
   - Record relative humidity
   - Verify conditions are within acceptable range

3. **Visual Inspection**
   - Identify all accessible conductive parts requiring bonding
   - Inspect bonding connections for damage or corrosion
   - Clean all test contact points

### Test Execution

4. **Equipment Setup**
   - Connect ground continuity tester positive terminal to module frame ground point
   - Connect negative terminal to accessible conductive part under test
   - Ensure secure, low-resistance connections

5. **Parameter Configuration**
   - Calculate test current: I_test = 2.5 × I_ocp
   - Set tester to calculated current
   - Configure test duration to 120 seconds

6. **Current Application**
   - Apply test current for 120 seconds
   - Monitor for signs of overheating or arcing
   - Record voltage drop continuously

7. **Measurement Recording**
   - Measure voltage drop across bonding connection
   - Verify actual current matches target
   - Calculate resistance: R = V / I

8. **Multi-Point Testing**
   - Repeat for all bonding points on the module
   - Document each measurement point

### Post-Test

9. **Data Analysis**
   - Compare measured resistance against 0.1 Ω limit
   - Evaluate all pass/fail criteria
   - Generate test report

10. **Documentation**
    - Record all measurements
    - Note any anomalies
    - Complete test report

## Equipment Requirements

### Ground Continuity Tester

**Specifications:**
- Current Range: 0.1 A - 300 A DC
- Voltage Measurement Range: 0 - 15 V
- Resistance Measurement Range: 0.001 Ω - 1 Ω
- Accuracy: ±1% of reading
- **Calibration**: Required (annual recommended)

### Digital Multimeter (Verification)

**Specifications:**
- Voltage Range: 0 - 1000 V
- Current Range: 0 - 10 A
- Resistance Range: 0 - 100 Ω
- **Calibration**: Required

### Environmental Monitors

**Temperature Sensor:**
- Range: -20°C to 150°C
- Accuracy: ±0.5°C
- **Calibration**: Required

**Humidity Sensor:**
- Range: 0% to 100% RH
- Accuracy: ±2% RH
- **Calibration**: Recommended

## Typical Measurement Points

For a standard PV module, test the following bonding connections:

1. **Frame to Junction Box**: Primary bonding connection
2. **Frame to Grounding Holes**: All designated grounding points
3. **Frame to Connector Ground Pin**: If module uses MC4 or similar connectors with ground pins
4. **Frame to Mounting Clips**: If clips are considered accessible conductive parts
5. **Between Frame Sections**: For multi-section frames

## Common Failure Modes

| Failure Mode | Likely Cause | Remediation |
|--------------|--------------|-------------|
| High Resistance (>0.1 Ω) | Oxidation at connection points | Clean and tighten connections |
| | Poor bonding wire gauge | Replace with adequate wire |
| | Damaged bonding path | Repair or replace bonding system |
| Excessive Voltage Drop | Loose connections | Tighten all bonding connections |
| | Undersized bonding conductor | Replace with larger conductor |
| Test Abort (Safety Limit) | Damaged insulation | Investigate and repair |
| | Short circuit | Locate and clear fault |

## Quality Control Notes

### Requires Review If:

- Measured resistance is >0.08 Ω (approaching limit)
- Multiple measurement attempts needed
- Unusual heating observed during test
- Inconsistent results across measurement points

### Best Practices

1. Always clean contact surfaces before testing
2. Use calibrated equipment within calibration period
3. Apply test current for full 120 seconds
4. Test all designated bonding points
5. Document environmental conditions
6. Record equipment serial numbers and calibration dates

## Report Generation

The test report should include:

1. **Test Identification**
   - Test number
   - Date and time
   - Operator name

2. **Sample Information**
   - Module serial number
   - Model and type
   - Electrical ratings

3. **Test Conditions**
   - Ambient temperature
   - Relative humidity
   - Equipment used (with calibration dates)

4. **Results**
   - All measurement point data
   - Calculated resistances
   - Pass/fail determination
   - Pass/fail criteria evaluation

5. **Notes**
   - Any anomalies observed
   - Deviations from procedure
   - Recommendations

## References

1. IEC 61730-2:2023, Photovoltaic (PV) module safety qualification - Part 2: Requirements for testing
2. IEC 60364-6, Low-voltage electrical installations - Part 6: Verification
3. IEC 60950-1, Information technology equipment - Safety - Part 1: General requirements

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-11-14 | PV Test Protocol Framework | Initial release |

---

**Document ID**: GROUND-001-DOC-v1.0.0
**Approval Status**: Approved
**Next Review Date**: 2026-11-14
