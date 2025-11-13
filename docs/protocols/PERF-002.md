# PERF-002: Performance Testing at Different Irradiances

## Overview

The PERF-002 protocol provides comprehensive performance testing for PV modules across multiple irradiance levels in accordance with IEC 61853 standards. This protocol measures I-V characteristics, power output, and efficiency at seven different irradiance levels ranging from 100 to 1100 W/m².

## Purpose

- Characterize PV module performance across the full range of operating irradiances
- Verify linearity of power output vs irradiance
- Measure efficiency variation with irradiance
- Ensure spatial uniformity of test conditions
- Provide data for energy rating and performance modeling

## Standards Compliance

- **IEC 61853-1:2011**: PV module performance testing and energy rating - Part 1: Irradiance and temperature performance measurements and power rating
- **IEC 61853-2:2016**: Part 2: Spectral responsivity, incidence angle and module operating temperature measurements
- **IEC 60904-9:2020**: Solar simulator performance requirements
- **IEC 60904-1:2020**: Measurement of photovoltaic current-voltage characteristics

## Test Configuration

### Irradiance Levels

The protocol tests at seven irradiance levels:

| Level | Irradiance (W/m²) | Tolerance | Description |
|-------|------------------|-----------|-------------|
| 1 | 100 | ±2% | Low irradiance condition |
| 2 | 200 | ±2% | Low-medium irradiance |
| 3 | 400 | ±2% | Medium irradiance |
| 4 | 600 | ±2% | Medium-high irradiance |
| 5 | 800 | ±2% | High irradiance |
| 6 | 1000 | ±2% | Standard Test Condition (STC) |
| 7 | 1100 | ±2% | Peak irradiance |

### Required Equipment

1. **Solar Simulator**
   - Classification: Class AAA (IEC 60904-9)
   - Calibration interval: 12 months
   - Required for: Controlled irradiance conditions

2. **Reference Cell**
   - Specification: Calibrated reference cell with temperature sensor
   - Calibration interval: 12 months
   - Required for: Accurate irradiance measurement

3. **I-V Tracer**
   - Specification: 4-wire measurement, ≤1% accuracy
   - Calibration interval: 12 months
   - Required for: I-V characteristic measurement

4. **Pyranometer**
   - Specification: Secondary standard, ISO 9060:2018
   - Calibration interval: 24 months
   - Required for: Irradiance monitoring

5. **Temperature Sensors**
   - Specification: Type-T thermocouple or PT100, ±0.5°C
   - Calibration interval: 12 months
   - Required for: Module temperature measurement

6. **Data Acquisition System**
   - Specification: ≥16-bit resolution, ≥100 samples/sec
   - Calibration interval: 12 months
   - Required for: Data collection

### Environmental Conditions

- **Module Temperature**: 25 ± 2°C (STC)
- **Ambient Temperature**: 20-30°C
- **Relative Humidity**: 30-70%
- **Wind Speed**: ≤1 m/s (indoor environment)
- **Spectrum**: AM1.5G (IEC 60904-3)

### Stabilization Requirements

- **Preconditioning time**: 30 minutes
- **Temperature stabilization**: ±0.5°C
- **Irradiance stabilization**: ±1.0%
- **Stabilization duration**: 5 minutes

## Measurement Grid

A 5×5 uniform grid is used to assess spatial uniformity:

- **Grid dimensions**: 5 rows × 5 columns = 25 measurement points
- **Spacing**: 150 mm horizontal × 150 mm vertical
- **Coverage**: Entire module active area with 50 mm edge margin
- **Purpose**: Verify irradiance uniformity across test plane

## Data Collection

### Required Fields

| Field | Type | Unit | Range | Description |
|-------|------|------|-------|-------------|
| timestamp | datetime | - | - | Measurement timestamp (ISO 8601) |
| irradiance | float | W/m² | 50-1200 | Measured irradiance |
| target_irradiance | float | W/m² | 100/200/400/600/800/1000/1100 | Target irradiance level |
| module_temperature | float | °C | 15-85 | Module back-surface temperature |
| voltage | float | V | 0-1500 | Module terminal voltage |
| current | float | A | 0-50 | Module output current |
| power | float | W | 0-* | Instantaneous power (calculated) |
| position_x | integer | - | 1-5 | Grid X coordinate (optional) |
| position_y | integer | - | 1-5 | Grid Y coordinate (optional) |

### I-V Curve Data

- **Required**: Yes
- **Points per curve**: ≥100
- **Voltage range**: 0 to Voc
- **Sweep rate**: Fast sweep
- **Sweep direction**: Forward (short-circuit to open-circuit)

## Analysis Calculations

### Per-Irradiance Level Calculations

For each irradiance level, the following parameters are calculated:

1. **Pmax (W)**: Maximum power point
   - Formula: max(V × I)

2. **Vmp (V)**: Voltage at maximum power point
   - Formula: V at Pmax

3. **Imp (A)**: Current at maximum power point
   - Formula: I at Pmax

4. **Voc (V)**: Open circuit voltage
   - Formula: V at I=0

5. **Isc (A)**: Short circuit current
   - Formula: I at V=0

6. **Fill Factor (%)**: Measure of I-V curve quality
   - Formula: (Vmp × Imp) / (Voc × Isc) × 100

7. **Efficiency (%)**: Conversion efficiency
   - Formula: (Pmax / (Irradiance × Area)) × 100

8. **Irradiance Uniformity (%)**: Spatial uniformity
   - Formula: (1 - (σ / μ)) × 100

9. **Normalized Pmax (W)**: Power normalized to STC
   - Formula: Pmax × (1000 / Irradiance_actual)

### Overall Analysis

1. **Linearity Coefficient (W/(W/m²))**: Linear regression slope of power vs irradiance
2. **R² Value**: Coefficient of determination for linearity
3. **Performance Summary**: Statistics across all irradiance levels

## Quality Control Checks

### Critical QC Checks

1. **Irradiance Tolerance**
   - Type: Range check
   - Requirement: Measured irradiance within ±2% of target
   - Severity: Critical
   - Per measurement: Yes

2. **Temperature Tolerance**
   - Type: Range check
   - Requirement: Module temperature 25 ± 2°C
   - Severity: High
   - Per measurement: Yes

3. **I-V Curve Quality**
   - Type: Custom validation
   - Requirements:
     - ≥10 data points
     - Monotonic current decrease
     - No negative values
     - Reasonable Voc and Isc ranges
   - Severity: Critical

4. **Data Completeness**
   - Type: Completeness check
   - Requirement: All 175 measurements present (25 points × 7 levels)
   - Severity: Critical

### High Priority QC Checks

5. **Uniformity Threshold**
   - Type: Threshold check
   - Requirement: Spatial uniformity ≥95%
   - Severity: High

6. **Efficiency Minimum**
   - Type: Threshold check
   - Requirement: Efficiency ≥15%
   - Severity: High

### Normal Priority QC Checks

7. **Fill Factor Range**
   - Type: Range check
   - Requirement: Fill factor 65-85%
   - Severity: Normal

8. **Linearity Check**
   - Type: Correlation check
   - Requirement: R² ≥0.98 for power vs irradiance
   - Severity: Normal

## Visualization

### Interactive Charts

1. **I-V Curves**: Line plot showing current vs voltage for all irradiance levels
2. **P-V Curves**: Line plot showing power vs voltage for all irradiance levels
3. **Power vs Irradiance**: Scatter plot with linear trendline and R² value
4. **Efficiency vs Irradiance**: Bar chart comparing efficiency at each level
5. **Fill Factor vs Irradiance**: Line plot showing fill factor variation
6. **Uniformity Heatmaps**: 2D heatmap showing spatial irradiance distribution
7. **Parameters Summary Table**: Tabular display of all key parameters

### Dashboard Layout

- **Page 1 - Overview**: Summary table and power vs irradiance
- **Page 2 - I-V Characteristics**: I-V and P-V curves
- **Page 3 - Performance Analysis**: Efficiency and fill factor charts
- **Page 4 - Uniformity**: Spatial distribution heatmaps

## Report Generation

### Report Formats

- **PDF**: Professional formatted report with all charts
- **HTML**: Interactive web-based report
- **JSON**: Machine-readable data export
- **Excel**: Multi-sheet workbook with raw data and analysis

### Report Sections

1. **Executive Summary**
   - Test date and identification
   - Module information
   - Overall result (Pass/Fail)
   - Key findings

2. **Test Conditions**
   - Environmental conditions
   - Equipment list with calibration status
   - Operator information

3. **Measurements**
   - Raw data tables
   - I-V curves
   - Measurement grid data

4. **Analysis Results**
   - Calculated parameters table
   - Performance charts
   - Statistical summary
   - Linearity analysis

5. **QC Status**
   - QC checks summary
   - Pass/fail status for each check
   - Deviations and corrective actions

6. **Conclusions**
   - Compliance statement
   - Performance rating
   - Recommendations

7. **Appendices** (optional)
   - Calibration certificates
   - Raw data export
   - Calculation methodology

## Traceability

### Required Traceability Information

- Module serial number
- Batch number
- Project code
- Operator name
- Test date and time
- Equipment IDs
- Calibration due dates

### Audit Trail

- All changes logged with timestamp
- Change justification required
- Version control for protocol definitions
- Digital signatures (optional)

## Test Procedure

### Pre-Test Preparation

1. Verify equipment calibration status
2. Clean module surface
3. Install temperature sensors on module back surface
4. Position module in solar simulator
5. Allow thermal stabilization (30 minutes)

### Test Execution

For each irradiance level (100, 200, 400, 600, 800, 1000, 1100 W/m²):

1. Adjust solar simulator to target irradiance
2. Verify irradiance stability (±1% for 5 minutes)
3. Verify module temperature (25 ± 2°C)
4. Measure spatial uniformity across 5×5 grid
5. Perform full I-V curve sweep (≥100 points)
6. Record all measurements with timestamps
7. Proceed to next irradiance level

### Post-Test

1. Save all raw data
2. Perform automated analysis
3. Run QC checks
4. Generate reports
5. Archive data with traceability information

## Data Analysis Workflow

1. **Data Validation**: Verify all measurements against protocol schema
2. **I-V Analysis**: Extract key parameters (Pmax, Voc, Isc, FF) for each level
3. **Efficiency Calculation**: Compute efficiency at each irradiance level
4. **Uniformity Analysis**: Calculate spatial uniformity from grid measurements
5. **Linearity Analysis**: Perform linear regression of power vs irradiance
6. **QC Checks**: Execute all quality control checks
7. **Visualization**: Generate all charts and graphs
8. **Report Generation**: Create comprehensive test report

## Integration

### LIMS Integration (Optional)

- Automatic upload of test results
- JSON format data transfer
- Custom field mapping configuration

### QMS Integration (Optional)

- Automatic NCR creation on QC failure
- Defect tracking and resolution
- Audit trail integration

### Project Management Integration (Optional)

- Test status updates
- Milestone tracking
- Resource allocation

## References

1. IEC 61853-1:2011, Photovoltaic (PV) module performance testing and energy rating - Part 1
2. IEC 60904-9:2020, Photovoltaic devices - Part 9: Solar simulator performance requirements
3. IEC 60904-1:2020, Photovoltaic devices - Part 1: Measurement of photovoltaic current-voltage characteristics
4. ISO 9060:2018, Solar energy - Specification and classification of instruments for measuring hemispherical solar and direct solar radiation

## Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2025-11-13 | Initial release | ganeshgowri-ASA |
