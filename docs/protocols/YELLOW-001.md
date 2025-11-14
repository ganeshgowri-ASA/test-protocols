# YELLOW-001: EVA Yellowing Assessment Protocol

## Protocol Information

**Protocol ID:** YELLOW-001
**Version:** 1.0.0
**Category:** EVA Degradation
**Status:** Active
**Last Updated:** 2025-11-14

## Overview

The YELLOW-001 protocol is an accelerated aging test designed to assess yellowing and color degradation of EVA (Ethylene-Vinyl Acetate) encapsulant material used in photovoltaic (PV) modules. This test simulates long-term outdoor exposure under controlled laboratory conditions to evaluate the optical stability of EVA materials.

## Purpose

- Evaluate the yellowing resistance of EVA encapsulant materials
- Assess color stability under accelerated UV and thermal exposure
- Determine optical transmittance degradation over time
- Compare performance across different EVA formulations or batches
- Support material qualification for PV module production

## Standards Reference

This protocol is based on the following industry standards:

- **IEC 61215-2:2021** - Terrestrial photovoltaic (PV) modules - Design qualification and type approval - Part 2: Test procedures
- **IEC 61730-2:2016** - Photovoltaic (PV) module safety qualification - Part 2: Requirements for testing
- **ASTM E313-20** - Standard Practice for Calculating Yellowness and Whiteness Indices from Instrumentally Measured Color Coordinates

## Test Conditions

### Environmental Parameters

| Parameter | Target Value | Tolerance |
|-----------|-------------|-----------|
| Temperature | 85°C | ±2°C |
| Relative Humidity | 60% | ±5% |
| UV Intensity | 100 mW/cm² | ±10% |
| UV Spectrum | UV-A (315-400 nm) | A-1A or equivalent |
| Test Duration | 1000 hours | - |

### Chamber Configuration

- **Air Circulation:** Forced convection
- **Sample Orientation:** Horizontal, facing UV source
- **Distance from UV Source:** 300 mm ±20 mm
- **Sample Size:** 100 mm × 100 mm × 3 mm (typical)

## Sample Requirements

### Sample Specifications

- **Material Type:** EVA (Ethylene-Vinyl Acetate) encapsulant
- **Minimum Sample Size:** 100 mm × 100 mm
- **Thickness:** As manufactured (typically 0.4-0.8 mm for PV modules, or 3 mm for test coupons)
- **Minimum Samples per Test:** 3
- **Surface Condition:** Clean, free of contamination, no scratches or defects

### Sample Preparation

1. Clean samples with isopropyl alcohol and lint-free cloth
2. Allow samples to equilibrate to room temperature (23°C ±2°C) for at least 2 hours
3. Record sample dimensions, batch code, and manufacturing information
4. Take baseline measurements before exposure

## Measurements

### Primary Measurements

#### 1. Yellowness Index (YI)

- **Method:** ASTM E313-20
- **Unit:** YI units
- **Measurement Equipment:** Color measurement spectrometer (e.g., X-Rite Ci7800)
- **Illuminant:** D65
- **Observer:** 10-degree
- **Frequency:** Every 100 hours
- **Acceptance Criteria:**
  - Warning Threshold: YI ≤ 10
  - Failure Threshold: YI ≤ 15

#### 2. Color Shift (ΔE)

- **Method:** CIE DE2000 (or CIE76 for simplified analysis)
- **Unit:** Delta E units
- **Calculation:** Color difference from baseline in L\*a\*b\* color space
- **Frequency:** Every 100 hours
- **Acceptance Criteria:**
  - Warning Threshold: ΔE ≤ 5
  - Failure Threshold: ΔE ≤ 8

#### 3. Light Transmittance

- **Wavelength:** 550 nm (visible green light)
- **Unit:** Percentage (%)
- **Measurement Equipment:** UV-Vis spectrophotometer
- **Frequency:** Every 100 hours
- **Acceptance Criteria:**
  - Warning Threshold: ≥80%
  - Failure Threshold: ≥75%

### Secondary Measurements

#### 4. CIE L*a*b* Color Coordinates

- **L\* (Lightness):** 0 (black) to 100 (white)
- **a\* (Red-Green):** Negative values = green, positive values = red
- **b\* (Yellow-Blue):** Negative values = blue, positive values = yellow

These measurements are used to calculate YI and ΔE values.

## Measurement Schedule

| Time Point (hours) | Measurements Required | Special Notes |
|-------------------|-----------------------|---------------|
| 0 (Baseline) | All measurements | Mandatory; establish reference |
| 100 | All measurements | First degradation check |
| 200 | All measurements | - |
| 300 | All measurements | - |
| 400 | All measurements | - |
| 500 | All measurements | Mid-test checkpoint |
| 600 | All measurements | - |
| 700 | All measurements | - |
| 800 | All measurements | - |
| 900 | All measurements | - |
| 1000 (Final) | All measurements | Final evaluation |

**Total Measurement Points:** 11 (including baseline)

## Quality Control Requirements

### 1. Baseline Control (QC-001)

- **Type:** Initial Reference
- **Frequency:** Once at test start
- **Requirement:** All baseline measurements must be completed before exposure begins
- **Acceptance Criteria:**
  - YI < 2.0 for fresh EVA
  - Transmittance > 90%
  - L\* > 90

### 2. Equipment Calibration (QC-002)

- **Type:** Calibration
- **Frequency:** Every 168 hours (weekly)
- **Requirement:** Verify calibration using certified reference standards
- **Reference Standards:**
  - White tile
  - Green tile
  - Gray tile
- **Acceptance Criteria:** Deviation within ±2% of certified values

### 3. Reference Sample Stability (QC-003)

- **Type:** Reference
- **Frequency:** Every 100 hours (with regular measurements)
- **Requirement:** Maintain unexposed reference sample measured at same intervals
- **Acceptance Criteria:** Reference sample deviation <5% from baseline

### 4. Environmental Monitoring (QC-004)

- **Type:** Environmental
- **Frequency:** Continuous (logged every 15 minutes)
- **Requirement:** Monitor chamber temperature, humidity, and UV intensity
- **Acceptance Criteria:**
  - Temperature: 85°C ±2°C
  - Humidity: 60% ±5%
  - UV Intensity: 100 mW/cm² ±10%

### 5. Sample Position Verification (QC-005)

- **Type:** Setup
- **Frequency:** At start and after any chamber opening
- **Requirement:** Verify sample placement and orientation
- **Acceptance Criteria:** Samples positioned per specifications (300 mm ±20 mm from UV source, horizontal orientation)

## Pass/Fail Criteria

### Final Evaluation (at 1000 hours)

| Parameter | Pass Criterion | Warning Level | Fail Criterion |
|-----------|---------------|---------------|----------------|
| Yellowness Index | ≤15 YI | >10 YI | >15 YI |
| Color Shift | ≤8 ΔE | >5 ΔE | >8 ΔE |
| Light Transmittance | ≥75% | <80% | <75% |

### Overall Result Determination

- **PASS:** All parameters meet pass criteria at end of test
- **WARNING:** One or more parameters exceed warning level but not fail level
- **FAIL:** One or more parameters exceed fail criteria

## Data Analysis

### Statistical Analysis

For each measured parameter, calculate:

- **Mean** (average across all samples)
- **Standard Deviation** (variation between samples)
- **Coefficient of Variation** (CV%) - measure of consistency
- **95% Confidence Interval** - statistical confidence range

### Trend Analysis

Perform exponential curve fitting for degradation kinetics:

**Model:** Y(t) = A + B × (1 - e^(-t/τ))

Where:
- Y(t) = measured value at time t
- A = baseline value
- B = maximum change
- τ = time constant
- t = time in hours

### Comparative Analysis

- **Baseline Comparison:** Compare all time points to baseline
- **Sample-to-Sample Comparison:** Identify outliers and rank samples by performance
- **Batch Comparison:** If multiple batches tested, compare batch statistics

### Extrapolation

Based on fitted kinetic model, extrapolate to:
- **2000 hours** - predict extended exposure performance
- **Time to Threshold** - estimate when fail criteria will be reached

## Safety Requirements

### Personal Protective Equipment (PPE)

- **UV Protection:** UV-blocking safety glasses required when accessing chamber
- **Thermal Protection:** Heat-resistant gloves for handling hot samples
- **General PPE:** Laboratory coat, closed-toe shoes

### Hazards

- **UV Radiation:** Do not look directly at UV source; ensure chamber door is closed during operation
- **High Temperature:** Allow chamber cool-down before accessing samples
- **Electrical:** Follow lockout/tagout procedures for equipment maintenance

## Equipment Requirements

### Required Equipment

1. **Environmental Chamber with UV Capability**
   - Temperature range: Room temperature to 100°C
   - Humidity control: 10-95% RH
   - Integrated UV-A lamps or external UV simulator

2. **UV Simulator**
   - Spectrum: UV-A (A-1A or equivalent)
   - Intensity: Adjustable, minimum 100 mW/cm²
   - Uniformity: ±10% across sample area

3. **Color Measurement Spectrometer**
   - Example: X-Rite Ci7800, Konica Minolta CM-5
   - Measurement geometry: d/8° (diffuse/8-degree viewing)
   - Wavelength range: 360-740 nm
   - Calibrated to industry standards

4. **UV-Vis Spectrophotometer**
   - Wavelength range: 200-800 nm
   - Transmittance measurement capability
   - Sample holder for solid samples

5. **Data Logging System**
   - Continuous monitoring of environmental conditions
   - 15-minute logging interval minimum
   - Data export capability

### Calibration Requirements

All measurement equipment must be calibrated:
- **Frequency:** Annually (minimum) or per manufacturer recommendations
- **Standards:** NIST-traceable or equivalent
- **Documentation:** Maintain calibration certificates

## Test Procedure

### Pre-Test

1. Review protocol and safety requirements
2. Verify equipment calibration status
3. Prepare and clean samples
4. Measure sample dimensions
5. Take baseline measurements (all parameters, 3 readings per sample)
6. Record environmental conditions
7. Set up environmental chamber (temperature, humidity, UV)
8. Position samples in chamber

### During Test

1. Monitor environmental conditions continuously
2. Perform measurements every 100 hours:
   - Remove samples from chamber
   - Allow cooling to room temperature (30 minutes minimum)
   - Clean sample surfaces
   - Take measurements (3 readings per sample)
   - Return samples to chamber
3. Perform weekly calibration checks (QC-002)
4. Measure reference sample every 100 hours (QC-003)
5. Document any deviations or issues

### Post-Test

1. Remove samples from chamber
2. Perform final measurements (1000 hours)
3. Analyze data and calculate statistics
4. Evaluate pass/fail criteria
5. Generate test report
6. Archive samples and data per retention requirements

## Reporting

### Report Sections

1. **Executive Summary**
   - Overall pass/fail status
   - Key findings
   - Recommendations

2. **Test Conditions**
   - Environmental parameters (actual vs. target)
   - Deviations or issues encountered

3. **Sample Information**
   - Sample IDs, batch codes, dimensions
   - Material specifications

4. **Measurement Results**
   - Tables of all measurement data
   - Time-series plots for each parameter
   - Baseline vs. final comparison

5. **Data Analysis**
   - Statistical analysis results
   - Kinetic modeling and curve fits
   - Comparative analysis across samples

6. **QC Results**
   - Summary of all QC checks
   - Equipment calibration status
   - Reference sample stability

7. **Pass/Fail Determination**
   - Criteria evaluation for each sample
   - Overall test result

8. **Conclusions**
   - Summary of test outcome
   - Material performance evaluation
   - Recommendations for use

9. **Appendices**
   - Raw data tables
   - Environmental monitoring logs
   - Equipment calibration certificates
   - Sample photographs

### Report Formats

- **PDF:** Final report for distribution
- **Excel:** Data tables and charts for further analysis
- **JSON:** Structured data for database integration
- **HTML:** Web-viewable interactive report

## Data Retention

- **Test Data:** 10 years minimum
- **Reports:** 10 years minimum
- **Sample Archive:** Per company policy
- **Electronic Records:** Secure backup with audit trail

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-11-14 | Test Protocols Framework | Initial protocol definition |

## Approval

**Reviewed by:** Quality Assurance
**Next Review Date:** 2026-11-14
**Protocol Status:** ACTIVE

---

## Quick Reference Card

### Critical Parameters

✓ Temperature: 85°C ±2°C
✓ Humidity: 60% ±5%
✓ UV: 100 mW/cm² ±10%
✓ Duration: 1000 hours
✓ Measurements: Every 100 hours

### Pass Criteria (at 1000 hours)

✓ YI ≤ 15
✓ ΔE ≤ 8
✓ Transmittance ≥ 75%

### Safety

⚠ UV protection required
⚠ High temperature hazard
⚠ Allow cool-down before handling

---

**For questions or support, contact the Test Protocols Framework team.**
