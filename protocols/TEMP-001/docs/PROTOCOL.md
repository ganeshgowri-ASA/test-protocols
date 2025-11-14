# TEMP-001: Temperature Coefficient Testing Protocol

## Protocol Information

- **Protocol ID:** TEMP-001
- **Version:** 1.0.0
- **Category:** Performance Testing
- **Standard:** IEC 60891:2021
- **Author:** ASA PV Testing
- **Date:** 2025-11-14

## Overview

This protocol defines procedures for measuring the temperature coefficients of photovoltaic (PV) modules according to IEC 60891:2021. Temperature coefficients are critical parameters that describe how a module's electrical performance varies with operating temperature.

## Objectives

1. Measure temperature coefficient of maximum power (α_Pmp or γ)
2. Measure temperature coefficient of open circuit voltage (β_Voc)
3. Measure temperature coefficient of short circuit current (α_Isc)
4. Determine temperature-corrected performance characteristics at STC
5. Validate module performance under varying temperature conditions

## Standard Test Conditions (STC)

- **Temperature:** 25°C
- **Irradiance:** 1000 W/m²
- **Air Mass:** AM 1.5

## Equipment Requirements

### Required Equipment

1. **Solar Simulator**
   - Classification: Class AAA (per IEC 60904-9)
   - Irradiance: 1000 W/m² ± 2%
   - Spectral match: Class A
   - Uniformity: Class A
   - Temporal stability: Class A

2. **Temperature Control Chamber**
   - Temperature range: -20°C to +80°C (minimum)
   - Temperature uniformity: ±2°C across test area
   - Temperature stability: ±1°C during measurement
   - Controlled humidity recommended

3. **I-V Curve Tracer**
   - Voltage range: 0-100 V (minimum)
   - Current range: 0-20 A (minimum)
   - Measurement accuracy: ±0.5% or better
   - Sampling rate: >100 points per I-V curve

4. **Temperature Sensors**
   - Type: PT100 RTD or K-type thermocouple
   - Accuracy: ±0.1°C
   - Response time: <1 second
   - Quantity: Minimum 4 sensors for module back-surface

5. **Reference Cell / Pyranometer**
   - Spectral match to test module technology
   - Calibration: Traceable to recognized standard
   - Accuracy: ±1%

### Calibration Requirements

All critical equipment must be calibrated and within the calibration period:

- Solar simulator: Annual calibration
- Temperature chamber: Annual calibration
- I-V curve tracer: Semi-annual calibration
- Temperature sensors: Annual calibration
- Reference cell: Annual calibration

## Test Parameters

### Temperature Range

- **Minimum range:** 30°C (IEC 60891 requirement)
- **Recommended range:** 50°C (e.g., 20°C to 70°C)
- **Temperature step:** 10°C recommended
- **Extended range option:** 15°C to 75°C

### Measurement Points

- **Minimum:** 5 temperature points
- **Recommended:** 6-7 temperature points
- **Optimal:** 8-10 temperature points (for high precision)

### Environmental Conditions

- **Irradiance:** 1000 W/m² ± 2%
- **Stabilization time:** 30 minutes minimum at each temperature
- **Temperature stability:** ±1°C for 5 minutes before measurement

## Test Procedure

### 1. Pre-Test Preparation

#### 1.1 Module Preparation
- Clean module surface per IEC 61215 cleaning procedure
- Inspect for physical damage or defects
- Record module nameplate information
- Photograph module (front and back)

#### 1.2 Sensor Installation
- Attach temperature sensors to module back surface:
  - Position sensors at center and near corners
  - Use thermally conductive adhesive or tape
  - Ensure good thermal contact
  - Insulate sensors from ambient air

#### 1.3 Equipment Setup
- Mount module in temperature chamber
- Connect I-V tracer leads (observe polarity)
- Position solar simulator or reference cell
- Verify all sensor connections
- Check data acquisition system

#### 1.4 System Verification
- Verify equipment calibration status
- Check solar simulator output uniformity
- Test temperature chamber functionality
- Validate data logging system

### 2. Initial Stabilization

- Set temperature chamber to starting temperature (e.g., 20°C)
- Allow module to stabilize for minimum 30 minutes
- Monitor temperature at all sensor locations
- Verify temperature uniformity: ±2°C maximum difference
- Ensure temperature stability: ±1°C for 5 minutes

### 3. Measurement Sequence

For each temperature point (repeat at 10°C increments):

#### 3.1 Temperature Stabilization
- Set chamber to target temperature
- Wait for thermal equilibrium (minimum 30 minutes)
- Verify all temperature sensors read within ±1°C
- Confirm temperature stability for 5 minutes

#### 3.2 Pre-Measurement Checks
- Verify irradiance at 1000 W/m² ± 2%
- Check module surface temperature uniformity
- Ensure no condensation on module (if testing below ambient)

#### 3.3 I-V Curve Measurement
- Record timestamp
- Measure ambient conditions
- Record module temperature (average of all sensors)
- Measure irradiance
- Acquire complete I-V curve
- Extract parameters:
  - Open circuit voltage (Voc)
  - Short circuit current (Isc)
  - Maximum power point voltage (Vmp)
  - Maximum power point current (Imp)
  - Maximum power (Pmax)
  - Fill factor (FF)

#### 3.4 Measurement Repetition
- Repeat I-V curve measurement 2-3 times
- Average results if variation is <1%
- If variation >1%, investigate and resolve issue

### 4. Data Collection Summary

Record the following for each temperature point:

**Environmental:**
- Measurement timestamp
- Module temperature (°C)
- Ambient temperature (°C)
- Irradiance (W/m²)
- Relative humidity (if available)

**I-V Parameters:**
- Voc (V)
- Isc (A)
- Vmp (V)
- Imp (A)
- Pmax (W)
- Fill Factor (%)

**Optional:**
- Complete I-V curve (voltage, current pairs)
- Series resistance (Rs)
- Shunt resistance (Rsh)

### 5. Post-Test Procedures

- Return chamber to ambient temperature
- Remove module and sensors carefully
- Download and back up all data
- Document any anomalies or deviations
- Clean and store equipment

## Data Analysis

### 1. Data Validation

Before analysis, verify:

✓ All required fields populated
✓ Minimum 5 temperature measurements
✓ Temperature range ≥ 30°C
✓ Irradiance stability within ±2%
✓ No obvious outliers or errors

### 2. Irradiance Normalization

If irradiance varies, normalize measurements to 1000 W/m²:

- **Current:** Isc_norm = Isc × (1000 / G_measured)
- **Power:** Pmax_norm = Pmax × (1000 / G_measured)
- **Voltage:** Minimal correction typically needed

### 3. Linear Regression Analysis

For each parameter (Pmax, Voc, Isc), perform linear regression against temperature:

**General form:** Y = a × T + b

Where:
- Y = Parameter (Pmax, Voc, or Isc)
- T = Module temperature (°C)
- a = Slope (change per °C)
- b = Y-intercept

**Quality metric:** R² ≥ 0.95 (IEC 60891 recommendation)

### 4. Temperature Coefficient Calculation

#### 4.1 Power Temperature Coefficient (α_Pmp)

**Relative (per IEC 60891):**
```
α_Pmp = (slope_Pmax / Pmax_ref) × 100  [%/°C]
```

**Absolute:**
```
α_Pmp_abs = slope_Pmax  [W/°C]
```

**Typical range for c-Si:** -0.65 to -0.25 %/°C

#### 4.2 Voltage Temperature Coefficient (β_Voc)

**Relative:**
```
β_Voc = (slope_Voc / Voc_ref) × 100  [%/°C]
```

**Absolute:**
```
β_Voc_abs = slope_Voc  [V/°C]
```

**Typical range for c-Si:** -0.50 to -0.20 %/°C

#### 4.3 Current Temperature Coefficient (α_Isc)

**Relative:**
```
α_Isc = (slope_Isc / Isc_ref) × 100  [%/°C]
```

**Absolute:**
```
α_Isc_abs = slope_Isc  [A/°C]
```

**Typical range for c-Si:** 0.00 to 0.10 %/°C

### 5. STC Correction

Using calculated coefficients, correct any measurement to STC (25°C, 1000 W/m²):

**Power:**
```
Pmax_STC = Pmax_measured × (G_STC / G_measured) × [1 + α_Pmp × (T_STC - T_measured)]
```

**Voltage:**
```
Voc_STC = Voc_measured + β_Voc_abs × (T_STC - T_measured)
```

**Current:**
```
Isc_STC = Isc_measured × (G_STC / G_measured) × [1 + α_Isc × (T_STC - T_measured)]
```

## Quality Acceptance Criteria

### Critical Checks (Must Pass)

| Check | Requirement | Action if Failed |
|-------|-------------|------------------|
| Data completeness | All required fields present | Cannot proceed with analysis |
| Temperature range | ≥ 30°C span | Repeat test with wider range |
| Measurement count | ≥ 5 temperature points | Acquire additional measurements |
| Equipment calibration | All equipment in calibration | Recalibrate equipment, may need to repeat test |

### Warning Checks (Recommend Review)

| Check | Requirement | Action if Failed |
|-------|-------------|------------------|
| Irradiance stability | Variation < 2% | Review data, consider normalizing |
| Linear fit quality | R² ≥ 0.95 | Review for outliers, check measurement quality |
| Coefficient ranges | Within typical values | Verify measurements, check for equipment issues |
| Temperature uniformity | ±2°C across module | Improve chamber uniformity settings |

## Expected Results

### Crystalline Silicon Modules

| Parameter | Typical Range | Notes |
|-----------|---------------|-------|
| α_Pmp | -0.65 to -0.25 %/°C | Negative (power decreases with temperature) |
| β_Voc | -0.50 to -0.20 %/°C | Negative (voltage decreases with temperature) |
| α_Isc | 0.00 to 0.10 %/°C | Positive (current increases with temperature) |

### Thin-Film Modules

Temperature coefficients may vary significantly from crystalline silicon. Consult manufacturer specifications.

## Uncertainty Analysis

Sources of uncertainty:
- Temperature measurement: ±0.1°C
- Irradiance measurement: ±1%
- I-V curve measurement: ±0.5%
- Temperature non-uniformity: ±2°C
- Regression fit: Depends on R²

**Combined uncertainty:** Typically ±5-10% for temperature coefficients

## Troubleshooting

### Issue: Poor Linear Fit (R² < 0.95)

**Possible causes:**
- Measurement outliers
- Insufficient temperature range
- Temperature not fully stabilized
- Irradiance variation during test

**Solutions:**
- Review data for anomalies
- Extend temperature range
- Increase stabilization time
- Improve irradiance control

### Issue: Coefficients Outside Expected Range

**Possible causes:**
- Equipment calibration error
- Module degradation or damage
- Incorrect measurement settings
- Data processing error

**Solutions:**
- Verify equipment calibration
- Inspect module for damage
- Review measurement procedure
- Check calculations

### Issue: Temperature Non-Uniformity

**Possible causes:**
- Poor chamber air circulation
- Sensor placement issues
- Module size too large for chamber

**Solutions:**
- Improve air circulation
- Reposition temperature sensors
- Use larger chamber or reduce temperature range

## Safety Considerations

- **Electrical safety:** Work with qualified personnel only
- **Temperature extremes:** Use caution when handling cold or hot modules
- **Light exposure:** Use appropriate eye protection with solar simulator
- **Condensation risk:** Monitor humidity when testing below ambient temperature
- **Equipment hazards:** Follow all equipment safety procedures

## References

1. **IEC 60891:2021** - Photovoltaic devices - Procedures for temperature and irradiance corrections to measured I-V characteristics

2. **IEC 61215-2:2021** - Terrestrial photovoltaic (PV) modules - Design qualification and type approval - Part 2: Test procedures

3. **IEC 60904-9:2020** - Photovoltaic devices - Part 9: Classification of solar simulator characteristics

4. **IEC 61853-1:2011** - Photovoltaic (PV) module performance testing and energy rating - Part 1: Irradiance and temperature performance measurements and power rating

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-11-14 | ASA PV Testing | Initial release |

## Appendices

### Appendix A: Data Sheet Template

[See separate data collection template]

### Appendix B: Calculation Spreadsheet

[See Excel calculation template]

### Appendix C: Equipment Specifications

[See equipment specification document]

---

**Document Control:**
- **Classification:** Internal Use
- **Review Frequency:** Annual
- **Next Review Date:** 2026-11-14
- **Approved By:** Technical Director
