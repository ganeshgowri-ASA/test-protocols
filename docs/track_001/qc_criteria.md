# TRACK-001 Quality Control Criteria

## Overview

This document defines the quality control (QC) criteria and acceptance thresholds for TRACK-001 tracker performance testing. All test runs must satisfy these criteria to be considered valid.

## Data Quality Requirements

### 1. Data Completeness

**Requirement**: Minimum 95% of expected measurements must be collected with "good" quality flags.

**Calculation**:
```
Data Completeness (%) = (Good Measurements / Expected Measurements) × 100
```

**Expected Measurements**:
```
Expected = (Test Duration / Sample Interval) × Number of Metrics
```

**Example**:
- Test duration: 8 hours = 480 minutes
- Sample interval: 5 minutes
- Number of metrics: 5
- Expected measurements: (480 / 5) × 5 = 480

**Acceptance**: ≥ 95% (456 or more good measurements)

**Failure Actions**:
- < 95%: Flag for review
- < 90%: Retest required
- < 80%: Invalid test

### 2. Data Continuity

**Requirement**: No data gap shall exceed 10 minutes.

**Definition**: A data gap is the time interval between consecutive measurements for the same metric.

**Monitoring**:
```python
max_acceptable_gap = 2 × sample_interval  # 10 minutes for 5-min sampling
```

**Acceptance**: All gaps ≤ 10 minutes

**Flagging**:
- Gap > 10 min: Minor flag (document cause)
- Gap > 20 min: Major flag (may invalidate affected time period)
- Gap > 30 min: Critical flag (retest recommended)

### 3. Quality Flags

Each measurement receives a quality flag:

| Flag | Code | Criteria | Action |
|------|------|----------|--------|
| Good | 0 | No issues detected | Accept |
| Questionable | 1 | Minor anomaly | Review |
| Bad | 2 | Out of range or error | Reject |

**Quality Flag Limits**:
- Good: ≥ 95%
- Questionable: ≤ 5%
- Bad: ≤ 1%

## Performance Acceptance Criteria

### 1. Tracking Accuracy

**Primary Metric**: 95th percentile of tracking error

**Acceptance Threshold**: ≤ 2.0°

**Measurement**: Angular deviation between actual tracker position and theoretical sun position

**Grading**:
- Excellent: P₉₅ ≤ 1.0°
- Good: P₉₅ ≤ 2.0°
- Acceptable: P₉₅ ≤ 3.0°
- Fail: P₉₅ > 3.0°

**Additional Criteria**:
- Mean tracking error ≤ 1.0°
- Maximum instantaneous error ≤ 5.0°
- RMSE ≤ 1.5°

### 2. Response Time

**Requirement**: Tracker must respond to position changes within 30 seconds

**Measurement**: Time from movement initiation to position stabilization

**Acceptance**: Mean response time ≤ 30 seconds

**Monitoring**:
- 90% of movements ≤ 30 seconds
- No single movement > 60 seconds

### 3. Power Consumption

**Idle State**:
- Maximum: 10 W
- Typical: 5-10 W
- Acceptance: ≤ 15 W (with documentation)

**Active State**:
- Maximum: 150 W
- Typical: 100-150 W
- Acceptance: ≤ 200 W (with documentation)

**Peak Power**:
- Absolute maximum: 250 W
- Acceptance: Brief spikes only (< 5 seconds)

**Energy Consumption**:
- Daily energy < 1.2 kWh for 8-hour test
- Efficiency ratio > 100:1 (energy gained vs consumed)

### 4. Positioning Speed

**Azimuth Axis**:
- Maximum speed: 15°/second
- Typical speed: 5-15°/second
- Acceptance: ≤ 20°/second

**Elevation Axis**:
- Maximum speed: 15°/second
- Typical speed: 5-15°/second
- Acceptance: ≤ 20°/second

**Safety Limit**: Absolute maximum 30°/second (triggers emergency stop)

## Validation Rules

### Rule R001: Tracking Error Percentile

**Description**: 95th percentile of tracking error must not exceed 2.0°

**Parameter**: `tracking_error`
**Condition**: `percentile_95 ≤ 2.0`
**Unit**: degrees
**Severity**: Critical

**Implementation**:
```python
{
    'rule_id': 'R001',
    'description': 'Tracking error 95th percentile check',
    'parameter': 'tracking_error',
    'condition': 'percentile_95',
    'threshold': 2.0,
    'unit': 'degrees',
    'severity': 'critical'
}
```

### Rule R002: Power Consumption Limit

**Description**: Power consumption must remain within specified limits

**Parameter**: `power_consumption`
**Condition**: `max ≤ 200`
**Unit**: W
**Severity**: Major

**Sub-rules**:
- Idle power (movement < 0.1°/s): ≤ 15 W
- Active power (movement ≥ 0.1°/s): ≤ 200 W
- No sustained operation > 250 W

### Rule R003: Data Gap Check

**Description**: No data gap shall exceed 10 minutes

**Parameter**: `data_continuity`
**Condition**: `max_gap ≤ 10`
**Unit**: minutes
**Severity**: Major

**Exception**: Documented maintenance or calibration activities

### Rule R004: Position Deviation

**Description**: Actual position must not deviate from commanded position by more than 1.5°

**Parameter**: `position_deviation`
**Condition**: `max ≤ 1.5`
**Unit**: degrees
**Severity**: Major

**Note**: This is distinct from tracking error (deviation from sun)

### Rule R005: Motor Current

**Description**: Motor current must remain within safe operating range

**Parameter**: `motor_current`
**Condition**: `max ≤ 5.0`
**Unit**: A
**Severity**: Critical

**Sub-rules**:
- Normal operation: ≤ 3.0 A
- Peak (< 5 seconds): ≤ 5.0 A
- Sustained > 5.0 A: Emergency condition

## Environmental Conditions

### Valid Test Conditions

**Temperature Range**:
- Minimum: -10°C
- Maximum: 50°C
- Optimal: 15-35°C

**Irradiance Range**:
- Minimum: 100 W/m²
- Maximum: 1200 W/m²
- Optimal: > 800 W/m²

**Wind Speed**:
- Maximum: 15 m/s
- Stow threshold: 20 m/s

**Note**: Tests conducted outside optimal conditions must be flagged and may have relaxed acceptance criteria.

## Tolerance and Uncertainty

### Measurement Tolerances

| Parameter | Tolerance | Instrument Accuracy |
|-----------|-----------|---------------------|
| Angle | ± 0.1° | ≤ 0.05° |
| Current | ± 0.01 A | ≤ 0.01 A |
| Power | ± 1.0 W | ≤ 0.5 W |
| Temperature | ± 0.5°C | ≤ 0.2°C |
| Irradiance | ± 5% | ≤ 2% |

### Uncertainty Budget

Total measurement uncertainty must be propagated through calculations:

```
U_total = √(U_instrument² + U_method² + U_environment²)
```

**Acceptance**: Total uncertainty ≤ 10% of measured value

## Anomaly Classification

### Severity Levels

| Level | Description | Response |
|-------|-------------|----------|
| Info | Minor deviation, no impact | Log only |
| Warning | Notable deviation | Flag for review |
| Major | Exceeds limits | Investigate cause |
| Critical | Safety or validity concern | Stop test, investigate |

### Common Anomalies

**Data Anomalies**:
- Stuck values (no change over time)
- Sudden jumps or discontinuities
- Values outside physical limits
- Systematic bias or drift

**Performance Anomalies**:
- Gradual degradation over test
- Oscillation or hunting behavior
- Erratic movements
- Failure to reach commanded position

**Environmental Anomalies**:
- Unexpected cloud transients
- Sensor shading or obstruction
- Temperature extremes
- Strong wind gusts

## Pass/Fail Decision

### Overall Pass Criteria

A test run **passes** if ALL of the following are met:

1. ✓ Data completeness ≥ 95%
2. ✓ All critical validation rules pass
3. ✓ Tracking accuracy within limits (R001)
4. ✓ No critical anomalies
5. ✓ Environmental conditions valid

### Conditional Pass

A test may **conditionally pass** if:
- One major validation rule fails with documented justification
- Environmental conditions outside optimal but within acceptable range
- Minor anomalies present but explained

**Requirements**:
- Engineering review and approval
- Documentation of conditions and justification
- May require additional testing

### Fail Criteria

A test **fails** if ANY of the following occur:

1. ✗ Data completeness < 90%
2. ✗ Any critical validation rule fails
3. ✗ Critical anomalies detected
4. ✗ Safety limits exceeded
5. ✗ Invalid environmental conditions

**Required Actions**:
- Root cause analysis
- Corrective actions
- Retest

## Review and Approval

### Automatic Approval

Tests that clearly pass all criteria with no flags may be automatically approved.

### Manual Review Required

The following conditions require engineer review:

- Any QC flags present
- Conditional pass situations
- Test failures
- Unusual conditions or results
- First test of new tracker type

### Approval Authority

| Result | Approver |
|--------|----------|
| Clear pass | Automated system |
| Minor flags | Test Engineer |
| Conditional pass | Senior Engineer |
| Failure | Engineering Manager |

## Documentation Requirements

All QC decisions must be documented with:

1. Test run ID
2. QC results summary
3. Validation rule outcomes
4. Anomalies detected
5. Pass/fail decision and justification
6. Approver name and date
7. Any special conditions or notes

## Revision History

| Version | Date | Changes | Approver |
|---------|------|---------|----------|
| 1.0.0 | 2025-01-14 | Initial release | QA Team |
