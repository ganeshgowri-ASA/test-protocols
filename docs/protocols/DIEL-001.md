# DIEL-001: Dielectric Withstand Test

## Overview

The Dielectric Withstand Test (DIEL-001) verifies the electrical insulation integrity of PV modules under high voltage stress conditions. This test is based on IEC 61730-2:2016 MST 15 requirements.

## Test Objective

To verify that the electrical insulation of a PV module can withstand the specified test voltage without breakdown or excessive leakage current.

## Standard Reference

- **Primary Standard**: IEC 61730-2:2016, MST 15 - Dielectric Withstand Test
- **Related Standards**:
  - IEC 61215-2:2016 - Design qualification and type approval
  - IEC 60664-1 - Insulation coordination
  - IEC 61140 - Protection against electric shock

## Test Parameters

### Test Voltage Calculation

The test voltage is calculated using the formula:

```
Test Voltage (V) = 1000 + (2 × Maximum System Voltage)
```

**Examples:**
- For 600V system: 1000 + (2 × 600) = 2200V
- For 1000V system: 1000 + (2 × 1000) = 3000V
- For 1500V system: 1000 + (2 × 1500) = 4000V

### Test Duration

- **Required**: 60 seconds minimum
- Voltage must be maintained steady throughout duration

### Voltage Application

- **Ramp-up rate**: ≤ 500 V/s
- **Ramp-down rate**: ≤ 1000 V/s
- **Voltage type**: AC sinusoidal, 50 Hz or 60 Hz
- **Tolerance**: ±50V or ±3%, whichever is greater

## Acceptance Criteria

### 1. Insulation Resistance

- **Initial measurement** (before test): ≥ 40 MΩ/m²
- **Final measurement** (after test): ≥ 40 MΩ/m²
- **Test voltage**: 500-1000 V DC

### 2. Leakage Current

- **Maximum allowed**: 50 mA during withstand test
- Current trip or alarm typically set at this level

### 3. Dielectric Breakdown

- **Requirement**: No dielectric breakdown or flashover during test
- **Indicator**: Sudden current spike, visible arcing

### 4. Visual Inspection

After test completion, module must show:
- No visible damage
- No burn marks or tracking
- No delamination or bubbling
- No damage to junction box or connectors

## Test Procedure

### 1. Pre-Test Inspection (Step 1)

- Inspect module for pre-existing damage
- Verify module identification
- Document any defects

### 2. Environmental Verification (Step 2)

- **Temperature**: 15-35°C
- **Relative humidity**: 25-75%
- Record actual conditions

### 3. Equipment Setup (Step 3)

- Verify equipment calibration is current
- Place module on grounded metal test plate
- Short-circuit all electrically active parts together
- Connect test leads

### 4. Initial Insulation Resistance (Step 5)

- Measure using 500-1000 V DC
- Calculate resistance per area
- Verify ≥ 40 MΩ/m²

### 5. Dielectric Withstand Test (Step 6)

1. Calculate test voltage
2. Clear personnel from test area
3. Ramp up voltage at ≤ 500 V/s
4. Maintain voltage for 60 seconds
5. Monitor leakage current continuously
6. Ramp down voltage at ≤ 1000 V/s
7. Note any breakdown events

### 6. Final Insulation Resistance (Step 7)

- Allow module to discharge (minimum 5 minutes)
- Measure using same method as initial
- Compare with initial measurement

### 7. Post-Test Inspection (Step 8)

- Visual inspection for damage
- Check for tracking, burning, arcing
- Document any new defects

## Safety Requirements

### Personal Protective Equipment (PPE)

- Insulated gloves rated for test voltage
- Safety glasses or face shield
- Insulated footwear
- Flame-resistant clothing (recommended)

### Test Area Safety

- Restricted access during energized testing
- High voltage warning signs posted
- Safety interlocks functional
- Emergency stop accessible
- Non-conductive flooring or mats

### Safety Procedures

- Lock out/tag out procedures
- Two-person rule (recommended)
- Verify de-energized before touching
- Ground and discharge before and after test
- Never touch module during energized test

## Equipment Requirements

### Dielectric Strength Tester

- **Voltage range**: 0 to 5000 V AC minimum
- **Accuracy**: ±5% or better
- **Current measurement**: 0.1-100 mA range
- **Frequency**: 50/60 Hz ±1%
- **Safety features**: Emergency stop, automatic discharge

### Insulation Resistance Tester

- **Test voltages**: 500 V, 1000 V DC
- **Measurement range**: 0.1 MΩ to 10 GΩ minimum
- **Accuracy**: ±10% or better

### Calibration

- **Frequency**: Annual minimum
- **Traceability**: National/international standards
- **Documentation**: Current certificates required

## Data Collection

### Required Data Points

1. Module identification (ID, manufacturer, model, serial number)
2. Module dimensions and area
3. Maximum system voltage rating
4. Test voltage (calculated and applied)
5. Test duration
6. Initial insulation resistance
7. Final insulation resistance
8. Maximum leakage current during test
9. Breakdown occurrence (yes/no)
10. Environmental conditions (temperature, humidity)
11. Equipment IDs and calibration dates
12. Operator name and date
13. Visual inspection results

## Results Interpretation

### PASS Criteria

All of the following must be true:
- Initial insulation resistance ≥ 40 MΩ/m²
- Final insulation resistance ≥ 40 MΩ/m²
- No dielectric breakdown occurred
- Leakage current ≤ 50 mA
- Test voltage within tolerance
- Test duration ≥ 60 seconds
- Visual inspection passed

### FAIL Criteria

Any of the following:
- Insulation resistance < 40 MΩ/m²
- Dielectric breakdown occurred
- Leakage current > 50 mA
- Visible damage after test

## Common Issues and Troubleshooting

### High Leakage Current

**Possible causes:**
- Surface contamination
- Internal moisture
- Damaged insulation

**Actions:**
- Clean module surface
- Ensure proper conditioning
- Inspect for physical damage

### Low Insulation Resistance

**Possible causes:**
- Moisture ingress
- Delamination
- Manufacturing defect

**Actions:**
- Check environmental conditions
- Verify module storage conditions
- Consider thermal cycling or drying

### Breakdown During Test

**Possible causes:**
- Insulation defect
- Sharp edges or stress points
- Excessive voltage

**Actions:**
- Stop test immediately
- Document failure location
- Perform root cause analysis

## Quality Control

### Critical QC Checks

1. Equipment calibration valid
2. Environmental conditions within limits
3. Test voltage accuracy (±50V)
4. Test duration ≥ 60 seconds
5. Insulation resistance measurements valid

### Data Validation

- All required fields completed
- Values within reasonable ranges
- Calculations verified
- Operator signatures obtained

## Related Tests

Typically performed with or after:
- Visual inspection
- Electrical performance characterization
- Wet leakage current test
- Damp heat test (if part of qualification sequence)

## References

1. IEC 61730-2:2016 - Photovoltaic module safety qualification - Part 2: Requirements for testing
2. IEC 61215-2:2016 - Terrestrial photovoltaic modules - Design qualification and type approval
3. IEC 60664-1 - Insulation coordination for equipment within low-voltage systems
4. IEC 61140 - Protection against electric shock

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-11-14 | Test Protocol Team | Initial release |

---

**Document Control:**
- Next Review Date: 2026-11-14
- Document Owner: Lab Manager
- Approval Required: Yes
