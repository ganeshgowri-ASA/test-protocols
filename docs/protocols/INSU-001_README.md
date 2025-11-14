# INSU-001: Insulation Resistance Test - Implementation Guide

## Overview

This document provides implementation details for the INSU-001 - Insulation Resistance Test protocol in the PV Testing Protocol System.

**Protocol ID:** INSU-001
**Standard:** IEC 61730 MST 01
**Category:** Safety Testing
**Version:** 1.0.0

## Files Created

### 1. Protocol Definition (JSON)
**Location:** `/protocols/definitions/insu-001.json`

Comprehensive protocol definition including:
- Protocol metadata and standard references
- Device under test specifications
- Test parameters and configuration
- Safety interlocks (pre/during/post test)
- Acceptance criteria per IEC 61730
- Quality control validation rules
- Approval gates and workflow
- Traceability configuration
- System integrations (LIMS, QMS)
- Report generation settings

### 2. Streamlit UI Page
**Location:** `/pages/10_INSU-001.py`

Interactive web interface with 6 main tabs:

1. **General Data** - Test identification and module information
2. **Safety Checks** - Comprehensive pre-test safety checklist
3. **Test Setup** - Equipment configuration and test parameters
4. **Measurements** - Live data capture with visualization
5. **Analysis** - Statistical analysis and pass/fail determination
6. **QC/Reports** - Quality control and report generation

**Key Features:**
- Real-time measurement visualization
- Automatic specific resistance calculation
- IEC 61730 compliance checking
- Safety interlock enforcement
- Multi-level approval workflow
- Export to CSV, PDF, Excel

### 3. Test Suite
**Location:** `/tests/protocols/test_insu_001.py`

Comprehensive test coverage including:

- Protocol definition validation
- IEC 61730 requirements verification
- Calculation accuracy tests
- Pass/fail logic validation
- Safety checks verification
- Data validation rules
- Integration configuration tests

**Run tests:**
```bash
cd /home/user/test-protocols
pytest tests/protocols/test_insu_001.py -v
```

### 4. Documentation
**Location:** `/docs/protocols/INSU-001_Insulation_Resistance_Test.md`

Complete protocol documentation covering:
- Test principle and theory
- IEC 61730 acceptance criteria
- Equipment requirements
- Detailed test procedure
- Safety precautions
- Data analysis methods
- Troubleshooting guide
- Reporting requirements
- Compliance and traceability

## Quick Start

### 1. Access the Protocol

Navigate to the Streamlit application:
```bash
streamlit run streamlit_app.py
```

Then select: **Pages → 10_INSU-001**

### 2. Create New Test Execution

**Tab 1: General Data**
1. Fill in test identification:
   - Link service request (optional)
   - Link inspection record (optional)
   - Enter sample ID (required)
   - Enter test operator name (required)

2. Enter module information:
   - Manufacturer, model, serial number
   - **Module area (m²)** - Critical for specific resistance calculation
   - System voltage class
   - Cell technology and frame type

3. Record environmental conditions:
   - Ambient temperature (15-35°C)
   - Relative humidity (<75%)
   - Module temperature

4. Click **Save General Data**

### 3. Complete Safety Checks

**Tab 2: Safety Checks**

⚠️ **MANDATORY BEFORE TESTING** ⚠️

Complete all 8 safety checks:
- Module disconnected from power
- Surface dry and clean
- Equipment grounded
- PPE worn
- Area clear
- Equipment calibrated
- Emergency procedures understood
- Test leads inspected

Enter supervisor approval and click **Complete Safety Checklist**

### 4. Configure Test Setup

**Tab 3: Test Setup**

1. **Equipment Information:**
   - Equipment ID
   - Model (e.g., Fluke 1550C)
   - Calibration dates
   - Certificate number

2. **Test Parameters:**
   - Test voltage: 500V or 1000V DC
   - Test duration: ≥60 seconds
   - Number of measurements: 3 (typical)

3. **Test Configuration:**
   - Terminal configuration
   - Test points (Active to Frame, etc.)

4. Click **Ready for Test**

### 5. Capture Measurements

**Tab 4: Measurements**

For each measurement:
1. Click **Add Measurement** expander
2. Enter measurement data:
   - Test point (e.g., "Active to Frame")
   - Polarity (+ve or -ve to frame)
   - Actual test voltage applied (V)
   - Resistance reading (MΩ)
   - Stabilization time (s)

3. Click **Save Measurement**

**Automatic Calculations:**
- Specific resistance = Resistance × Module Area
- Real-time visualization updates
- IEC requirement comparison

**Repeat for all test points and polarities**

### 6. Review Analysis

**Tab 5: Analysis**

Automatically calculated:
- Mean, std dev, min, max resistance
- Specific resistances (MΩ·m²)
- Measurement repeatability (RSD%)
- **Pass/Fail determination:**
  - ✅ PASS: R_specific ≥ 40 MΩ·m²
  - ❌ FAIL: R_specific < 40 MΩ·m²

Acceptance criteria checked:
1. IEC 61730 requirement (≥40 MΩ·m²)
2. Safety requirement (≥1 MΩ)
3. Measurement quality (<20% RSD)

### 7. Generate Report

**Tab 6: QC/Reports**

1. Complete QC checkpoints
2. Select report type:
   - Test Report - Full (IEC 61730 Compliance)
   - Summary Report
   - Certificate of Testing
   - Data Package

3. Enter reviewer and approver names
4. Click **Generate Report**

Reports include:
- Complete test data
- Statistical analysis
- Charts and graphs
- Pass/fail determination
- Safety compliance
- Digital signatures

## Technical Details

### Database Schema

The protocol uses the existing database schema:

**Tables Used:**
- `protocol_executions` - Test execution tracking
- `measurements` - Live measurement data
- `analysis_results` - Calculated results
- `qc_records` - Quality control checkpoints
- `reports` - Generated reports
- `audit_trail` - Complete traceability

**No schema modifications required** - fully compatible with existing system.

### Calculation Engine

**Specific Insulation Resistance:**
```python
R_specific = R_measured × A

Where:
- R_measured: Measured resistance (MΩ)
- A: Module area (m²)
- R_specific: Specific resistance (MΩ·m²)
```

**Pass/Fail Logic:**
```python
# IEC 61730 requirement
pass_iec = (min_specific_resistance >= 40.0)

# Safety requirement
pass_safety = (min_absolute_resistance >= 1.0)

# Quality requirement
pass_quality = (std_dev / mean * 100 < 20.0)

# Overall result
result = "PASS" if (pass_iec and pass_safety) else "FAIL"
```

### Data Model

**Measurement Data Structure (JSON):**
```json
{
  "measurement_number": 1,
  "test_point": "Active to Frame",
  "polarity": "+ve to frame",
  "test_voltage_actual_v": 500.0,
  "resistance_reading_mohm": 120.0,
  "specific_resistance_mohm_m2": 232.8,
  "stabilization_time_actual_s": 5,
  "notes": ""
}
```

## Safety Considerations

### High Voltage Warning

⚠️ This test involves DC voltages up to **1000V** which can cause:
- Severe electric shock
- Cardiac arrest
- Death

**Only qualified personnel** should perform this test.

### Mandatory Safety Checks

1. **Before Test:**
   - Module disconnected
   - Surface dry
   - Equipment grounded
   - PPE worn
   - Area secured

2. **During Test:**
   - No contact with module or connections
   - Maintain safe distance
   - Monitor voltage stability

3. **After Test:**
   - Ensure complete discharge (≥5 seconds)
   - Verify voltage removed
   - Inspect for damage

### Emergency Procedures

In case of electric shock:
1. DO NOT touch victim if in contact with source
2. Disconnect power immediately
3. Call emergency services
4. Begin CPR if trained

## IEC 61730 Compliance

### Standard Requirements Met

✅ Test voltage: 500V or 1000V DC (configurable)
✅ Test duration: ≥60 seconds (configurable)
✅ Pass criterion: R_specific ≥ 40 MΩ·m² (enforced)
✅ Module condition: Dry, ambient temperature (verified)
✅ Equipment calibration: Tracked and validated
✅ Safety procedures: Comprehensive checklist
✅ Traceability: Complete audit trail
✅ Documentation: Auto-generated reports

### Certification Support

This protocol supports:
- **IEC 61730** Module Safety Qualification
- **UL 1703 / UL 61730** (if applicable)
- **CE Marking** Low Voltage Directive

## Integration

### LIMS Export

Automatic export of:
- Sample ID
- Test result (PASS/FAIL)
- Minimum specific resistance
- Test date and operator
- Complete dataset

### QMS Integration

- Auto-creation of Non-Conformance reports
- Links to QMS-IEC61730-MST01 procedure
- NC triggers:
  - R_specific < 40 MΩ·m²
  - Calibration overdue
  - Test voltage out of range
  - Safety violations

### Equipment Management

- Usage tracking
- Calibration alerts
- Maintenance scheduling

## Troubleshooting

### Common Issues

**Issue: Low resistance readings**
- Check for moisture on module
- Clean surface with isopropyl alcohol
- Verify module is dry
- Check for physical damage

**Issue: High measurement variability**
- Verify probe connections
- Clean contact points
- Allow temperature stabilization
- Check for intermittent faults

**Issue: Calibration overdue**
- System blocks test execution
- Equipment must be recalibrated
- Results invalid until recalibrated

**Issue: Safety checks not completing**
- All checks must be verified
- Supervisor approval required
- Cannot proceed to testing without completion

## Best Practices

1. **Pre-Test:**
   - Allow module to stabilize for 30+ minutes
   - Ensure completely dry (especially after cleaning)
   - Verify calibration status before starting

2. **During Test:**
   - Perform 3+ measurements per test point
   - Use both polarities (+ve and -ve to frame)
   - Monitor for stability before recording

3. **Post-Test:**
   - Always wait for complete discharge
   - Inspect module for any damage
   - Document all observations

4. **Quality:**
   - RSD should be <10% for good measurements
   - Re-test if variability is high
   - Compare with previous test data if available

## Maintenance

### Equipment Maintenance

- **Calibration:** Annual (required)
- **Functional Check:** Quarterly
- **Lead Inspection:** Monthly
- **Battery Replacement:** As needed

### Protocol Updates

- **Review Frequency:** Annual
- **Standard Updates:** Monitor IEC amendments
- **Procedure Refinement:** Based on user feedback

## Support

### Documentation

- Full procedure: `INSU-001_Insulation_Resistance_Test.md`
- Test suite: `tests/protocols/test_insu_001.py`
- Protocol definition: `protocols/definitions/insu-001.json`

### Training

Required training for operators:
1. High voltage safety
2. Insulation resistance testing principles
3. Equipment operation
4. Data analysis and interpretation
5. Emergency procedures

### References

- IEC 61730-2:2016+AMD1:2022
- ISO/IEC 17025:2017
- OSHA 29 CFR 1910 (Electrical Safety)

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2024 | System | Initial implementation |

---

**For questions or issues, contact:**
- Test Engineering Department
- Quality Assurance Manager
- System Administrator
