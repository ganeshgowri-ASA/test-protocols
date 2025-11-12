# PVTP-001: STC Power Measurement - User Manual

## Protocol Overview

**Protocol ID**: PVTP-001
**Protocol Name**: STC Power Measurement
**Standard**: IEC 61215-1:2021, IEC 60904-1:2020
**Category**: Module Performance Testing
**Duration**: 1-2 hours per module

## Purpose

This protocol measures the electrical performance of PV modules under Standard Test Conditions (STC):
- Irradiance: 1000 W/m²
- Spectrum: AM1.5G
- Cell Temperature: 25°C

## Equipment Required

1. **Solar Simulator**
   - Class A, B, or C per IEC 60904-9
   - Calibrated within last 6 months
   - Capable of providing 1000 W/m² ±2%

2. **I-V Curve Tracer**
   - High precision current and voltage measurement
   - Data acquisition rate: ≥100 points per curve
   - Calibrated within last 6 months

3. **Temperature Measurement**
   - Type K thermocouples or equivalent
   - Attached to module back surface
   - Accuracy: ±0.5°C

4. **Reference Cell**
   - Traceable to international standards
   - Same technology as test module preferred
   - Calibration current

## Safety Precautions

- Wear UV-protective eyewear when simulator is on
- Ensure proper grounding of all equipment
- Verify voltage ratings before testing
- Keep work area clean and dry
- Follow electrical safety procedures

## Pre-Test Procedure

### 1. Module Preparation

1. Allow module to stabilize at room temperature (minimum 2 hours)
2. Clean module surface with isopropyl alcohol and lint-free cloth
3. Inspect module for visible defects
4. Record module serial number and identification

### 2. Equipment Setup

1. Turn on solar simulator and allow warm-up (minimum 30 minutes)
2. Verify simulator irradiance using reference cell
3. Check temperature sensors for proper function
4. Verify I-V tracer calibration status
5. Prepare data logging system

### 3. Environmental Check

Verify test conditions:
- Ambient temperature: 15-35°C
- Relative humidity: 20-80%
- No direct airflow on module
- Stable electrical supply

## Test Procedure

### Step 1: Module Positioning

1. Place module on test platform
2. Ensure module is perpendicular to light source
3. Center module in illuminated area
4. Attach temperature sensors to module back (center and corners)

### Step 2: Electrical Connections

1. Connect positive lead from I-V tracer to module positive terminal
2. Connect negative lead from I-V tracer to module negative terminal
3. Verify proper polarity
4. Check for secure connections

### Step 3: Irradiance Verification

1. Place reference cell at module plane
2. Measure irradiance
3. Adjust simulator if needed to achieve 1000 W/m² ±2%
4. Record reference cell reading

### Step 4: Temperature Stabilization

1. Turn on simulator
2. Monitor module temperature
3. Wait until module reaches 25°C ±2°C
4. Maintain stable temperature for 2 minutes

### Step 5: I-V Curve Measurement

1. Initiate I-V curve sweep
2. Sweep from Voc to Isc (or reverse)
3. Capture minimum 100 data points
4. Complete sweep within 100ms to avoid heating
5. Record timestamp

### Step 6: Data Verification

1. Review I-V curve for anomalies:
   - Smooth curve with no steps
   - No negative conductance regions
   - Fill factor > 0.65
2. If curve is acceptable, proceed
3. If not, investigate and repeat measurement

### Step 7: Repeat Measurements

1. Take 3 consecutive measurements
2. Allow 1 minute between measurements for cooling
3. Verify consistency (all within 1% of each other)
4. Use average of measurements for final result

## Data Analysis

### Extracted Parameters

From the I-V curve, extract:

1. **Pmax** - Maximum power point (W)
2. **Voc** - Open circuit voltage (V)
3. **Isc** - Short circuit current (A)
4. **Vmp** - Voltage at maximum power (V)
5. **Imp** - Current at maximum power (A)

### Calculated Parameters

Calculate:

1. **Fill Factor (FF)**
   ```
   FF = (Pmax / (Voc × Isc)) × 100%
   ```

2. **Efficiency (η)**
   ```
   η = (Pmax / (Irradiance × Module Area)) × 100%
   ```

3. **Series Resistance (Rs)**
   - From slope at Voc

4. **Shunt Resistance (Rsh)**
   - From slope at Isc

### Temperature Correction

If measured at temperature ≠ 25°C, correct using:

```
Pmax(25°C) = Pmax(T) × [1 + γ(25 - T)]
```

Where γ is the temperature coefficient of power (%/°C)

## Pass/Fail Criteria

### Power Tolerance

Compare measured power to nameplate rating:

- **PASS**: Within manufacturer's specified tolerance (typically -3% to +5%)
- **FAIL**: Outside specified tolerance

### Quality Checks

Verify:
- [ ] Fill factor ≥ 0.65
- [ ] I-V curve is smooth
- [ ] No negative conductance
- [ ] Measurement repeatability within 1%
- [ ] All equipment calibrated

## Reporting

### Required Information

Report must include:

1. Module identification
2. Test date and time
3. Operator name
4. Equipment used (IDs and calibration dates)
5. Environmental conditions
6. Test conditions (irradiance, temperature, spectrum)
7. Measured values (Pmax, Voc, Isc, Vmp, Imp)
8. Calculated parameters (FF, efficiency)
9. I-V curve graph
10. Pass/fail result
11. Uncertainty statement

### Sample Report Format

```
PV MODULE PERFORMANCE TEST REPORT
Protocol: PVTP-001 (STC Power Measurement)
Standard: IEC 61215-1:2021

Module Information:
- Manufacturer: ABC Solar
- Model: ASM-400M-72
- Serial Number: AST2025M400001
- Nameplate Power: 400 W ±3%

Test Conditions:
- Irradiance: 999.8 W/m² (Target: 1000 W/m²)
- Spectrum: AM1.5G
- Module Temperature: 25.2°C (Target: 25°C)
- Date: 2025-11-13
- Operator: Alice Engineer

Results:
- Pmax: 402.5 W (±1.2 W)
- Voc: 49.52 V (±0.12 V)
- Isc: 10.24 A (±0.05 A)
- Vmp: 41.85 V (±0.10 V)
- Imp: 9.62 A (±0.04 A)
- Fill Factor: 79.45%
- Efficiency: 20.62%

Pass/Fail: PASS
Deviation from Nameplate: +0.625%
```

## Troubleshooting

### Problem: Unstable Measurements

**Possible Causes**:
- Simulator not warmed up
- Temperature fluctuations
- Electrical noise

**Solutions**:
- Allow longer warm-up time
- Check cooling system
- Check grounding and shielding

### Problem: Low Fill Factor

**Possible Causes**:
- High series resistance
- Low shunt resistance
- Cell damage

**Solutions**:
- Check connections
- Inspect module for defects
- Clean contacts

### Problem: Power Below Specification

**Possible Causes**:
- Incorrect irradiance
- Temperature not at 25°C
- Module degradation

**Solutions**:
- Verify reference cell calibration
- Adjust temperature control
- Apply temperature correction
- Document findings

## References

1. IEC 61215-1:2021 - Terrestrial photovoltaic (PV) modules - Design qualification and type approval - Part 1: Test requirements
2. IEC 60904-1:2020 - Photovoltaic devices - Part 1: Measurement of photovoltaic current-voltage characteristics
3. IEC 60904-9:2020 - Photovoltaic devices - Part 9: Classification of solar simulator characteristics

## Appendices

### Appendix A: Equipment Calibration Schedule

| Equipment | Calibration Interval | Last Calibrated | Next Due |
|-----------|---------------------|-----------------|----------|
| Solar Simulator | 6 months | YYYY-MM-DD | YYYY-MM-DD |
| I-V Tracer | 6 months | YYYY-MM-DD | YYYY-MM-DD |
| Reference Cell | 12 months | YYYY-MM-DD | YYYY-MM-DD |
| Temperature Sensors | 12 months | YYYY-MM-DD | YYYY-MM-DD |

### Appendix B: Measurement Uncertainty Budget

| Source | Type | Value | Contribution |
|--------|------|-------|--------------|
| Irradiance | B | ±2% | 40% |
| Temperature | B | ±0.5°C | 15% |
| I-V Tracer | B | ±0.5% | 30% |
| Repeatability | A | ±0.3% | 15% |
| **Combined** | - | **±1.2 W** | **100%** |

---

**Document Version**: 1.0
**Effective Date**: 2025-11-12
**Reviewed By**: Technical Team
**Approved By**: Quality Manager
