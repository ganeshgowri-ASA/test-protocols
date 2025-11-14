# PV Test Protocol Framework - User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Using the Web Interface](#using-the-web-interface)
5. [Protocol Management](#protocol-management)
6. [Test Execution](#test-execution)
7. [Data Analysis](#data-analysis)
8. [Report Generation](#report-generation)
9. [Troubleshooting](#troubleshooting)

## Introduction

The PV Test Protocol Framework is a comprehensive system for executing standardized tests on photovoltaic modules. This guide will help you get started with the system and understand how to perform common tasks.

### Key Features

- Standardized test protocol definitions
- Guided test execution workflow
- Automatic pass/fail evaluation
- Interactive data visualization
- Comprehensive report generation
- Quality control tracking

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager
- PostgreSQL 12+ (optional, for database features)

### Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/your-org/test-protocols.git
cd test-protocols
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Set up database:
```bash
psql -U postgres -f database/schema.sql
```

4. Launch the application:
```bash
streamlit run src/ui/app.py
```

The application will open in your default web browser at `http://localhost:8501`.

## Quick Start

### Running Your First Test

1. **Launch the Application**
   ```bash
   streamlit run src/ui/app.py
   ```

2. **Select a Protocol**
   - Browse available protocols on the main page
   - Click "Select" on VIBR-001 (Transportation Vibration Test)

3. **Review Protocol Details**
   - Read the protocol overview
   - Check required equipment
   - Review safety notes

4. **Start a Test Session**
   - Enter operator information
   - Configure test parameters
   - Add sample information
   - Click "Start Test Session"

5. **Collect Data**
   - Follow the test sequence
   - Enter measurements as prompted
   - Save each measurement

6. **Complete and Evaluate**
   - Click "Complete Test"
   - Review pass/fail results
   - Export results if needed

## Using the Web Interface

### Main Navigation

The application has four main pages:

1. **Protocol Selection**: Choose which test to run
2. **Protocol Details**: View protocol information and start tests
3. **Test Execution**: Collect measurements during test
4. **Results**: View and export test results

### Sidebar

The sidebar shows:
- Current protocol information
- Active session status
- Application version and info

## Protocol Management

### Understanding Protocols

Each protocol defines:
- Test objectives and scope
- Required parameters and limits
- Measurement procedures
- Pass/fail criteria
- Reporting requirements

### VIBR-001: Transportation Vibration Test

#### Overview
- **Standard**: IEC 62759-1:2022
- **Purpose**: Evaluate module resistance to shipping vibration
- **Duration**: ~3.5 hours
- **Sample Size**: Minimum 2 modules

#### Key Parameters
- **Frequency Range**: 5-200 Hz
- **Vibration Severity**: ≥ 0.49 g RMS
- **Test Duration**: ≥ 180 minutes
- **Axis**: Vertical (primary)

#### Test Sequence
1. Sample conditioning (24 hours)
2. Pre-test visual inspection
3. Pre-test electrical performance
4. Vibration test execution
5. Post-test visual inspection
6. Post-test electrical performance
7. Insulation resistance test

#### Pass Criteria
- Power degradation ≤ 5%
- No critical visual defects
- Insulation resistance ≥ 40 MΩ
- Individual parameter degradation within limits

### Loading Protocols

Protocols are automatically loaded from the `protocols/` directory:

```
protocols/
├── mechanical/
│   └── VIBR-001.json
├── environmental/
└── electrical/
```

### Creating Custom Protocols

1. Create a new JSON file in the appropriate category directory
2. Follow the protocol schema structure
3. Validate using the framework:

```python
from src.core.protocol_loader import ProtocolLoader

loader = ProtocolLoader()
is_valid, error = loader.validate_protocol_file('path/to/protocol.json')

if is_valid:
    print("Protocol is valid!")
else:
    print(f"Validation error: {error}")
```

## Test Execution

### Starting a Test Session

1. **Enter Operator Information**
   - Operator Name: Your full name
   - Operator ID: Your employee/operator ID

2. **Configure Samples**
   - Number of Samples: Enter count (minimum from protocol)
   - For each sample:
     - Sample ID: Unique identifier
     - Manufacturer: Module manufacturer
     - Model: Module model number
     - Serial Number: Module serial number

3. **Set Test Parameters**
   - The system displays parameters from the protocol
   - Adjust values if needed (within protocol limits)
   - Default values are automatically populated

### Collecting Measurements

#### Pre-Test Measurements

**Visual Inspection**
- Check all items in the checklist
- Document any existing defects
- Add notes if needed

**Electrical Performance**
- Measure at Standard Test Conditions (STC):
  - Irradiance: 1000 W/m²
  - Temperature: 25°C
  - Spectrum: AM1.5
- Enter all I-V parameters:
  - Pmax (Maximum Power)
  - Voc (Open Circuit Voltage)
  - Isc (Short Circuit Current)
  - Vmp (Voltage at MPP)
  - Imp (Current at MPP)
  - FF (Fill Factor)

#### During Test

**Vibration Monitoring**
- System records time-series data
- Monitor acceleration in X, Y, Z axes
- Verify RMS acceleration meets requirements
- Check that fixture remains secure

#### Post-Test Measurements

**Visual Inspection**
- Carefully inspect for new defects
- Compare with pre-test condition
- Document all changes

**Electrical Performance**
- Repeat measurements at STC
- Use same test conditions as pre-test
- Enter all parameters

**Insulation Resistance**
- Test at 1000 V DC
- Minimum 40 MΩ required
- Record value in MΩ

### Quality Control Checks

Throughout testing, complete QC checks:

1. **Pre-test**
   - Vibration system calibration verification
   - Accelerometer calibration verification
   - Solar simulator verification

2. **During test**
   - Fixture integrity check
   - Data acquisition monitoring

3. **Post-test**
   - Data integrity verification
   - Equipment condition check

### Completing a Test

1. Verify all required measurements are collected
2. Review data for completeness
3. Click "Complete Test"
4. System automatically evaluates pass/fail criteria

## Data Analysis

### Automatic Evaluations

The system automatically evaluates:

1. **Power Degradation**
   ```
   Degradation = ((Pre_Pmax - Post_Pmax) / Pre_Pmax) × 100%
   Pass if: Degradation ≤ 5%
   ```

2. **Visual Defects**
   - Pass if: No critical defects found
   - Critical defects: cracks, delamination, glass breakage, frame detachment

3. **Insulation Resistance**
   - Pass if: R_insulation ≥ 40 MΩ

4. **Electrical Parameters**
   - Voc degradation ≤ 2%
   - Isc degradation ≤ 2%
   - FF degradation ≤ 3%

### Understanding Results

**Overall Status:**
- **PASS**: All criteria met
- **FAIL**: One or more criteria failed
- **CONDITIONAL PASS**: Marginal performance, review required
- **NOT EVALUATED**: Incomplete data

**Criterion Evaluations:**
Each criterion shows:
- Status (Pass/Fail)
- Measured value
- Limit value
- Description
- Supporting details

### Visualization

The system generates interactive charts:

1. **I-V Curves**: Pre-test vs post-test overlay
2. **Power Comparison**: Bar chart of power values
3. **Degradation Summary**: All parameters with limits
4. **PSD Plot**: Vibration spectrum (log-log scale)
5. **Time Series**: Acceleration vs time

## Report Generation

### Export Formats

**JSON Export**
- Complete test session data
- All measurements and metadata
- Evaluation results
- Machine-readable format

**PDF Report** (Coming Soon)
- Executive summary
- Test conditions
- Results and analysis
- Charts and visualizations
- Pass/fail evaluation

**Excel Report** (Coming Soon)
- Data tables
- Charts
- Summary statistics
- QC check records

### Report Contents

Standard reports include:

1. **Executive Summary**
   - Test overview
   - Overall result
   - Key findings

2. **Sample Description**
   - Module specifications
   - Sample condition

3. **Test Setup**
   - Equipment used
   - Calibration status
   - Test parameters

4. **Test Procedure**
   - Sequence followed
   - Deviations (if any)

5. **Results**
   - All measurements
   - Calculated values
   - Charts

6. **Analysis**
   - Statistical analysis
   - Degradation calculations
   - Comparisons

7. **Pass/Fail Evaluation**
   - Criterion-by-criterion results
   - Overall determination

8. **Appendices**
   - Raw data
   - Equipment certificates
   - Photos

## Troubleshooting

### Common Issues

#### Protocol Not Loading

**Problem**: Error when loading protocol

**Solutions**:
1. Check JSON syntax validity
2. Verify protocol file location
3. Validate against schema:
   ```bash
   python -c "from src.core.protocol_loader import ProtocolLoader; \
   loader = ProtocolLoader(); \
   print(loader.validate_protocol_file('protocols/mechanical/VIBR-001.json'))"
   ```

#### Invalid Parameter Values

**Problem**: "Invalid parameters" error when starting session

**Solutions**:
1. Check parameter values against protocol limits
2. Ensure all required parameters are provided
3. Verify parameter types (numeric vs select)

#### Missing Measurements

**Problem**: Cannot complete test due to missing measurements

**Solutions**:
1. Check which measurements are required (marked with "Required")
2. Ensure all pre-test measurements are collected before during-test
3. Complete all stages before finishing test

#### Evaluation Errors

**Problem**: Error during results evaluation

**Solutions**:
1. Verify all required measurements have data
2. Check data format matches expected structure
3. Ensure numeric values where expected

### Getting Help

For additional support:

1. Check the [Architecture Documentation](architecture.md)
2. Review the [API Reference](api_reference.md)
3. Consult protocol-specific notes in JSON files
4. Contact your system administrator

## Best Practices

### Test Preparation

1. **Equipment Verification**
   - Verify all equipment calibrations current
   - Check equipment functionality before test
   - Prepare all necessary tools and fixtures

2. **Sample Handling**
   - Follow conditioning requirements strictly
   - Handle samples carefully to prevent damage
   - Document pre-existing conditions

3. **Documentation**
   - Take photos before and after test
   - Record environmental conditions
   - Note any deviations from protocol

### During Testing

1. **Data Entry**
   - Enter data immediately after measurement
   - Double-check values for transcription errors
   - Add notes for unusual observations

2. **Monitoring**
   - Continuously monitor test progress
   - Watch for equipment issues
   - Verify data is being recorded

3. **Safety**
   - Follow all safety notes in protocol
   - Use appropriate PPE
   - Stop test if unsafe conditions develop

### After Testing

1. **Data Review**
   - Review all data for completeness
   - Check for outliers or unusual values
   - Verify calculations

2. **Sample Inspection**
   - Thoroughly inspect samples
   - Document all changes
   - Store samples appropriately

3. **Report Generation**
   - Generate reports promptly
   - Review reports for accuracy
   - Archive all data and reports

## Appendix

### Glossary

- **STC**: Standard Test Conditions (1000 W/m², 25°C, AM1.5)
- **PSD**: Power Spectral Density
- **RMS**: Root Mean Square
- **MPP**: Maximum Power Point
- **FF**: Fill Factor
- **QC**: Quality Control
- **IEC**: International Electrotechnical Commission

### Reference Standards

- **IEC 62759-1:2022**: Transportation testing of photovoltaic modules
- **IEC 61215-1:2021**: PV modules - Design qualification and type approval
- **IEC 60904-9:2020**: Solar simulator performance requirements
- **ASTM D4169**: Performance testing of shipping containers

### Keyboard Shortcuts

(Streamlit standard shortcuts)
- **R**: Rerun application
- **C**: Clear cache
- **?**: Show keyboard shortcuts

### Support Resources

- Documentation: `/docs`
- Examples: `/examples`
- Tests: `/tests`
- Issues: GitHub Issues page
