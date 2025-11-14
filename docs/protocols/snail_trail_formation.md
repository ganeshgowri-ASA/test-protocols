# SNAIL-001: Snail Trail Formation Test Protocol

## Overview

**Protocol ID:** SNAIL-001
**Version:** 1.0.0
**Category:** Degradation
**Standard Reference:** IEC 61215-2:2021 MQT 13 (modified)

### Purpose

The Snail Trail Formation Test assesses the susceptibility of photovoltaic (PV) modules to snail trail defects under accelerated environmental exposure conditions. Snail trails are visible discoloration patterns that appear on the cell surface, typically caused by silver migration from cell contacts. These defects can indicate potential long-term reliability issues and may correlate with power degradation.

### Background

Snail trails are a field-observed degradation mode that appears as brownish discoloration on silicon solar cells, resembling the trail left by a snail. This phenomenon is primarily associated with:

- Silver migration from metallization
- Moisture ingress and humidity exposure
- Electrochemical corrosion processes
- Manufacturing defects in cell contacts

While snail trails are primarily a visual defect, severe cases can be correlated with electrical performance degradation.

## Test Conditions

### Environmental Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| Temperature Range | 20°C - 85°C | Cycling between ambient and elevated temperature |
| Humidity | 85% RH | Target humidity during exposure |
| Duration | 1000 hours | Standard test duration |
| Inspection Intervals | 0, 168, 336, 504, 672, 840, 1000 hours | Weekly intervals |

### Sample Requirements

- **Minimum Samples:** 3 modules
- **Recommended Samples:** 5 modules
- **Sample Condition:** As-received or pre-conditioned per IEC 61215

### Equipment Required

1. **Environmental Chamber**
   - Temperature control: ±2°C
   - Humidity control: ±5% RH
   - Chamber volume sufficient for test samples

2. **Electrical Testing Equipment**
   - Solar simulator (Class A, AM1.5G spectrum)
   - IV curve tracer
   - Temperature measurement (module and ambient)

3. **Imaging Equipment**
   - Electroluminescence (EL) imaging system
   - High-resolution visual imaging
   - Calibrated lighting for visual inspection (1000 lux minimum)

## Test Procedure

### 1. Initial Characterization (Hour 0)

1. **Visual Inspection**
   - Photograph module front and back
   - Document any pre-existing defects
   - Record module serial numbers and identification

2. **Electrical Characterization**
   - Perform IV curve measurement at STC
   - Record: Pmax, Isc, Voc, FF, Impp, Vmpp
   - Perform EL imaging

3. **Data Entry**
   - Enter module information into system
   - Record all initial measurements
   - Upload images to database

### 2. Environmental Exposure

1. **Chamber Setup**
   - Place modules in environmental chamber
   - Ensure adequate spacing for air circulation
   - Position temperature/humidity sensors

2. **Exposure Cycle**
   - Ramp to 85°C/85% RH
   - Maintain conditions per test schedule
   - Daily monitoring of chamber conditions

### 3. Interim Inspections (168h, 336h, 504h, 672h, 840h)

At each inspection interval:

1. **Remove from Chamber**
   - Allow modules to stabilize at room temperature (2-4 hours)

2. **Visual Inspection**
   - Assess snail trail severity: none, minor, moderate, severe
   - Count affected cells
   - Estimate affected area percentage
   - Photograph any changes

3. **Electrical Testing**
   - Perform IV curve measurement
   - Record all electrical parameters

4. **Data Recording**
   - Enter all measurements into system
   - Upload images
   - Add observation notes

5. **Return to Chamber**
   - Resume environmental exposure

### 4. Final Characterization (Hour 1000)

1. **Complete Visual Assessment**
   - Comprehensive photography
   - Detailed severity grading
   - Final affected area calculation

2. **Complete Electrical Testing**
   - IV curve measurement
   - EL imaging
   - Comparison with initial values

3. **Analysis Execution**
   - Run automated analysis
   - Review QC checks
   - Generate test report

## Acceptance Criteria

### Pass/Fail Thresholds

| Criterion | Threshold | Status |
|-----------|-----------|---------|
| Power Degradation | ≤ 5% | Critical |
| Affected Area | ≤ 10% | Critical |
| QC Checks | All critical checks pass | Critical |

### Severity Grading

| Grade | Description | Affected Area | Visual Impact |
|-------|-------------|---------------|---------------|
| None | No visible snail trails | 0% | No discoloration |
| Minor | Faint trails on few cells | < 5% | Light brown discoloration |
| Moderate | Visible trails on multiple cells | 5-15% | Clear brown patterns |
| Severe | Extensive trail coverage | > 15% | Dark, widespread discoloration |

## Data Analysis

### Calculated Metrics

The protocol automatically calculates:

1. **Power Degradation**
   - Formula: `((P_initial - P_current) / P_initial) × 100`
   - Tracked at each interval

2. **Snail Trail Progression Rate**
   - Formula: `Affected Area (%) / Test Hours`
   - Linear regression fit

3. **Correlation Analysis**
   - Pearson correlation between affected area and power loss
   - Statistical significance testing

4. **Electrical Parameter Trends**
   - Isc, Voc, and FF degradation over time
   - Rate of change analysis

### Quality Control Checks

1. **Data Completeness** (Critical)
   - All required measurements present
   - Minimum 85% of planned intervals completed

2. **Measurement Consistency** (Critical)
   - Pmax ≤ Isc × Voc
   - 50% ≤ FF ≤ 100%
   - Physical constraints satisfied

3. **Monotonic Degradation** (Warning)
   - Power should not improve significantly
   - Flags unexpected improvements > 2%

4. **Visual-Electrical Correlation** (Warning)
   - Severe visual degradation should correlate with power loss
   - Alerts on mismatches

## Report Generation

### Automated Report Sections

1. **Executive Summary**
   - Overall pass/fail result
   - Key metrics
   - Test duration and conditions

2. **Module Specifications**
   - Manufacturer and model
   - Technology type
   - Initial electrical parameters

3. **Visual Inspection Results**
   - Severity progression
   - Photographic evidence
   - Affected area trends

4. **Electrical Performance Analysis**
   - Power degradation trends
   - IV parameter evolution
   - Statistical analysis

5. **Quality Control Results**
   - QC check status
   - Warnings and flags
   - Data quality assessment

6. **Conclusions and Recommendations**
   - Test outcome
   - Reliability assessment
   - Recommended actions

### Visualizations

Generated charts include:

- Power degradation vs. time (line plot)
- Snail trail area progression (line plot)
- Correlation: affected area vs. power loss (scatter plot)
- Affected cells distribution (bar chart)
- Multi-parameter degradation comparison (multi-line plot)

## Database Integration

### Stored Data

All test data is automatically stored in the database:

- Protocol configuration
- Module information
- Test run metadata
- Measurement time series
- Analysis results
- QC check details
- Images and annotations

### LIMS Integration

The protocol supports integration with Laboratory Information Management Systems (LIMS):

- Automatic sample tracking
- Test status updates
- Result synchronization
- Report delivery

## Usage Example

### Via Streamlit UI

1. Launch application: `streamlit run ui/streamlit_app.py`
2. Select "SNAIL-001: Snail Trail Formation" protocol
3. Enter module information in Setup tab
4. Add measurements at each inspection interval
5. Run analysis when complete
6. Generate and download PDF report

### Via Python API

```python
from protocols.degradation.snail_trail_formation import SnailTrailFormationProtocol

# Initialize protocol
protocol = SnailTrailFormationProtocol()

# Prepare test data
test_data = {
    'input_params': {
        'module_id': 'MOD-001',
        'manufacturer': 'Solar Inc.',
        # ... other parameters
    },
    'measurements': [
        {
            'inspection_hour': 0,
            'visual_snail_trail_severity': 'none',
            # ... other measurements
        },
        # ... more measurement intervals
    ]
}

# Run protocol
result = protocol.run(test_data)

# Generate report
report_path = protocol.generate_report(Path('./reports'))
```

## Best Practices

### Testing

1. **Sample Handling**
   - Handle modules carefully to avoid mechanical damage
   - Use clean gloves to prevent contamination
   - Document any handling incidents

2. **Measurement Consistency**
   - Use same equipment for all measurements
   - Maintain consistent lighting conditions
   - Allow adequate thermal stabilization

3. **Documentation**
   - Take high-quality photographs at each interval
   - Record environmental conditions
   - Note any anomalies or unexpected observations

### Data Quality

1. **Real-Time Entry**
   - Enter data immediately after measurement
   - Review for obvious errors
   - Save backups regularly

2. **Image Management**
   - Use consistent naming conventions
   - Store high-resolution images
   - Annotate key features

3. **Review Process**
   - Verify data completeness before final analysis
   - Review QC warnings
   - Cross-check calculations

## Troubleshooting

### Common Issues

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| Inconsistent measurements | Equipment calibration | Recalibrate and repeat |
| Unexpected power gain | Measurement error | Verify conditions, remeasure |
| QC check failures | Data entry error | Review and correct data |
| Missing intervals | Scheduling conflict | Document and justify gaps |

## References

1. IEC 61215-2:2021 - Terrestrial photovoltaic (PV) modules - Design qualification and type approval - Part 2: Test procedures
2. Köntges, M., et al. (2014). "Review of Failures of Photovoltaic Modules." IEA PVPS Task 13.
3. Berghold, J., et al. (2011). "Snail Trails in Crystalline Silicon Modules." 26th EU PVSEC.

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-01-14 | PV Testing Team | Initial release |

---

**Document Owner:** Quality Assurance Team
**Next Review Date:** 2026-01-14
**Classification:** Internal Use
