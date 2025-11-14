# CORR-001: Corrosion Testing Protocol

## Overview

The CORR-001 protocol implements comprehensive corrosion testing for photovoltaic modules using accelerated salt spray and humidity exposure cycles. This protocol evaluates module resistance to corrosive environments including marine, coastal, and industrial atmospheres.

## Standards Compliance

This protocol complies with the following international standards:

- **IEC 61701:2020** - Salt Mist Corrosion Testing of Photovoltaic Modules
- **ASTM B117:2019** - Standard Practice for Operating Salt Spray (Fog) Apparatus
- **IEC 61215:2021** - Terrestrial Photovoltaic Modules - Design Qualification and Type Approval

## Test Summary

**Protocol ID:** CORR-001
**Version:** 1.0.0
**Category:** Degradation Testing
**Typical Duration:** 3-4 weeks per complete test cycle
**Complexity:** High

## Equipment Requirements

| Equipment | Type | Calibration Required |
|-----------|------|---------------------|
| Salt Spray Chamber | Environmental Chamber | Yes |
| Humidity Chamber | Environmental Chamber | Yes |
| Digital Thermometer | Temperature Sensor | Yes |
| Hygrometer | Humidity Sensor | Yes |
| pH Meter | Chemical Sensor | Yes |
| IV Curve Tracer | Electrical Tester | Yes |
| Visual Inspection Microscope | Optical | No |

## Sample Requirements

- **Quantity:** Minimum 3 samples recommended
- **Size:** Full modules (min 1000mm x 1000mm) or representative coupons
- **Preparation:** Clean with IPA, dry completely, document baseline condition

## Test Procedure

### Step 1: Initial Documentation and Inspection (30 minutes)

**Type:** Preparation
**Automated:** No

**Tasks:**
1. Photograph all samples from multiple angles
2. Record serial numbers and sample IDs
3. Perform visual inspection for pre-existing defects
4. Measure and document baseline dimensions

**Data Fields:**
- Sample ID (required)
- Serial Number (required)
- Operator Name (required)
- Test Date (required)
- Initial Photos
- Inspection Notes

**Quality Checks:**
- All samples photographed
- Serial numbers clearly visible
- No pre-existing damage that would invalidate test

### Step 2: Baseline Electrical Characterization (45 minutes)

**Type:** Measurement
**Automated:** Yes

**Tasks:**
1. Measure IV curves at STC conditions (1000 W/m², 25°C, AM1.5G)
2. Record Voc, Isc, Pmax, FF, Rs, Rsh
3. Perform electroluminescence imaging (if available)

**Data Fields:**
- Baseline Voc (V) - required, range: 0-100
- Baseline Isc (A) - required, range: 0-20
- Baseline Pmax (W) - required, range: 0-600
- Baseline Fill Factor (%) - required, range: 0-100
- Baseline Rs (Ω) - optional
- Baseline Rsh (Ω) - optional
- EL Images

**Quality Checks:**
- IV curves show expected behavior
- All parameters within datasheet specifications
- EL images show uniform emission (if applicable)

### Step 3: Prepare Salt Spray Solution (20 minutes)

**Type:** Preparation
**Automated:** No

**Tasks:**
1. Mix 5% ± 1% NaCl solution using distilled water
2. Verify pH is between 6.5-7.2
3. Filter solution to remove impurities
4. Preheat to 35°C

**Data Fields:**
- Salt Solution Concentration (%) - required, range: 4-6
- Salt Solution pH - required, range: 6.5-7.2

**Quality Checks:**
- Solution concentration verified
- pH within specified range
- Solution clear with no visible contaminants

### Step 4: Salt Spray Exposure - Cycle (48 hours)

**Type:** Conditioning
**Automated:** Yes

**Tasks:**
1. Place samples in salt spray chamber at 35°C
2. Ensure samples angled 15-30° from vertical
3. Expose to continuous salt fog for 48 hours
4. Monitor temperature and solution delivery rate

**Data Fields:**
- Salt Spray Temperature (°C) - required, range: 33-37
- Spray Duration (hours) - required

**Quality Checks:**
- Chamber temperature maintained at 35°C ± 2°C
- Salt fog uniformly distributed
- Solution fall rate within specification (1.0-2.0 ml/80cm²/h)

### Step 5: Post-Spray Recovery and Drying (24 hours)

**Type:** Preparation
**Automated:** No

**Tasks:**
1. Remove samples from chamber
2. Gently rinse with distilled water
3. Allow to air dry for 24 hours at ambient conditions

**Quality Checks:**
- All salt residue removed
- Samples completely dry
- No handling damage

### Step 6: Humidity Exposure - Cycle (96 hours)

**Type:** Conditioning
**Automated:** Yes

**Tasks:**
1. Place samples in humidity chamber at 85°C and 85% RH
2. Expose for 96 hours
3. Monitor temperature and humidity continuously

**Data Fields:**
- Humidity Chamber Temperature (°C) - required, range: 83-87
- Relative Humidity (%) - required, range: 80-90
- Humidity Duration (hours) - required

**Quality Checks:**
- Temperature maintained at 85°C ± 2°C
- Relative humidity at 85% ± 5%
- No condensation on samples

### Step 7: Post-Humidity Recovery (4 hours)

**Type:** Preparation
**Automated:** No

**Tasks:**
1. Allow samples to cool and equilibrate to ambient conditions
2. Minimum 4 hours at 23°C ± 5°C and 50% ± 10% RH

**Quality Checks:**
- Samples at room temperature
- No moisture condensation visible

### Step 8: Interim Visual Inspection (30 minutes)

**Type:** Measurement
**Automated:** No

**Tasks:**
1. Perform detailed visual inspection
2. Document any corrosion, discoloration, delamination, bubbles
3. Compare to baseline photos
4. Measure defect dimensions

**Data Fields:**
- Cycle Number (required)
- Visual Corrosion (required) - Options: None, Minor, Moderate, Severe
- Corrosion Location (multiselect) - Options: Frame, Junction Box, Connectors, Cell Interconnects, Backsheet, Edge Seal, None
- Delamination (boolean) - required
- Discoloration (boolean) - required
- Photos
- Notes

**Quality Checks:**
- All visible changes documented
- Defects measured and recorded
- Comparison to baseline completed

### Step 9: Interim Electrical Testing (45 minutes)

**Type:** Measurement
**Automated:** Yes

**Tasks:**
1. Measure IV curves and key electrical parameters
2. Compare to baseline
3. Calculate degradation percentages
4. Perform insulation resistance test

**Data Fields:**
- Interim Voc (V) - required
- Interim Isc (A) - required
- Interim Pmax (W) - required
- Insulation Resistance (MΩ) - required, min: 0

**Quality Checks:**
- IV measurements completed at STC
- Insulation resistance > 40 MΩ·m²
- Data logged and compared to baseline

### Step 10: Repeat Exposure Cycles

**Type:** Conditioning
**Automated:** Yes

**Tasks:**
1. Repeat steps 4-9 for a total of 3 complete cycles
2. Each cycle: 48h salt spray, 24h recovery, 96h humidity, 4h recovery, inspection, testing

**Duration:** Approximately 512 hours (21+ days) for 3 complete cycles

### Step 11: Final Visual Inspection (45 minutes)

**Type:** Measurement
**Automated:** No

**Tasks:**
1. Comprehensive final visual inspection
2. High-resolution photography from all angles
3. Document all corrosion sites, edge seal condition, junction box integrity

**Data Fields:**
- Same as Step 8, with "final_" prefix

### Step 12: Final Electrical Characterization (60 minutes)

**Type:** Measurement
**Automated:** Yes

**Tasks:**
1. Complete electrical testing suite
2. IV curves, EL imaging, insulation resistance, ground continuity
3. Calculate all degradation metrics relative to baseline

**Data Fields:**
- Final Voc (V) - required
- Final Isc (A) - required
- Final Pmax (W) - required
- Final Fill Factor (%) - required
- Wet Leakage Current (mA) - required, min: 0
- Ground Continuity (boolean) - required

### Step 13: Data Analysis and Report Generation (120 minutes)

**Type:** Analysis
**Automated:** Yes

**Tasks:**
1. Analyze all collected data
2. Generate degradation curves
3. Create correlation plots
4. Prepare comprehensive test report

**Data Fields:**
- Test Result (required) - Options: Pass, Fail, Conditional Pass
- Notes

## Quality Control Criteria

### Critical QC Checks

| ID | Name | Type | Threshold | Severity |
|----|------|------|-----------|----------|
| qc_power_degradation | Maximum Power Degradation Limit | Threshold | ≤ 5% | Critical |
| qc_insulation_resistance | Minimum Insulation Resistance | Threshold | ≥ 40 MΩ | Critical |
| qc_visual_corrosion | Visual Corrosion Check | Pattern | Not "Severe" | Critical |
| qc_ground_continuity | Ground Continuity Required | Comparison | Must be True | Critical |

### Warning QC Checks

| ID | Name | Type | Range | Severity |
|----|------|------|-------|----------|
| qc_spray_temperature | Salt Spray Temperature Range | Range | 33-37°C | Warning |
| qc_humidity_temperature | Humidity Chamber Temperature Range | Range | 83-87°C | Warning |
| qc_solution_ph | Salt Solution pH Range | Range | 6.5-7.2 | Warning |

## Analysis and Calculations

### Automated Calculations

**Power Degradation (%):**
```
((baseline_pmax - final_pmax) / baseline_pmax) × 100
```

**Voc Degradation (%):**
```
((baseline_voc - final_voc) / baseline_voc) × 100
```

**Isc Degradation (%):**
```
((baseline_isc - final_isc) / baseline_isc) × 100
```

**Fill Factor Change (%):**
```
final_ff - baseline_ff
```

## Charts and Visualizations

1. **Power Degradation Curve** - Line chart showing Pmax vs cycle number
2. **IV Curve Comparison** - Baseline vs Final IV curves
3. **Temperature Profile** - Chamber temperature over time
4. **Insulation Resistance Trend** - Resistance vs cycle number

## Pass/Fail Criteria

### Pass Conditions

✅ Module passes if ALL of the following are true:
- Power degradation ≤ 5%
- Insulation resistance ≥ 40 MΩ·m²
- Visual corrosion not "Severe"
- Ground continuity maintained
- No critical QC check failures

### Fail Conditions

❌ Module fails if ANY of the following are true:
- Power degradation > 5%
- Insulation resistance < 40 MΩ·m²
- Visual corrosion rated as "Severe"
- Ground continuity lost
- Any critical QC check failure

## Report Generation

The protocol automatically generates comprehensive reports including:

### Report Sections

1. **Executive Summary** - Test result, key findings, pass/fail determination
2. **Test Parameters** - Environmental conditions, equipment used
3. **Baseline Measurements** - Initial electrical and visual state
4. **Exposure History** - Complete log of all exposure cycles
5. **Visual Inspection Results** - Photos and observations at each cycle
6. **Electrical Performance** - IV curves and degradation analysis
7. **Degradation Analysis** - Statistical analysis and trending
8. **QC Check Results** - All quality control check outcomes
9. **Conclusions and Recommendations** - Summary and next steps

### Report Formats

- **Markdown** - Human-readable text report
- **PDF** - Formatted document (coming soon)
- **JSON** - Machine-readable data export
- **CSV** - Tabular data export

## Usage Example

### Python API

```python
from protocols.implementations.corrosion.corrosion_protocol import CorrosionProtocol

# Load protocol
protocol = CorrosionProtocol()

# Create test run
test_run = protocol.create_test_run(
    run_id="CORR-001-2025-001",
    operator="John Doe"
)

# Execute steps
protocol.execute_step(1,
    sample_id="MODULE-12345",
    serial_number="SN-67890",
    operator="John Doe"
)

protocol.execute_step(2,
    baseline_voc=45.5,
    baseline_isc=9.2,
    baseline_pmax=350.0,
    baseline_ff=78.5
)

# ... continue with other steps ...

# Run QC checks
qc_results = protocol.run_qc_checks(protocol.test_run.data)

# Generate report
report = protocol.generate_report()
```

### Streamlit UI

1. Launch the application: `streamlit run ui/app.py`
2. Navigate to "Protocol Selection"
3. Select "CORR-001 - Corrosion Testing"
4. Click "Start New Test Run"
5. Enter run details and begin testing
6. Follow the step-by-step workflow in "Data Entry"
7. View results in "Analysis & Results"
8. Download reports from "Reports" page

## Best Practices

### Sample Handling

- Always wear appropriate PPE when handling samples
- Use clean, lint-free gloves to prevent contamination
- Store samples in controlled environment between steps
- Document any handling incidents immediately

### Data Collection

- Record data immediately after measurement
- Double-check all numerical entries for transcription errors
- Take photos from consistent angles for comparison
- Note any deviations from standard procedure

### Equipment Maintenance

- Calibrate all equipment before testing
- Verify chamber conditions before each exposure
- Clean chambers between test runs
- Maintain detailed equipment logs

### Safety Considerations

- Salt spray chambers operate at elevated temperatures
- Humidity chambers contain hot, moist environment
- Electrical testing requires proper isolation
- Follow all laboratory safety protocols

## Troubleshooting

### Common Issues

**Salt spray chamber not maintaining temperature:**
- Check heater function
- Verify ambient conditions
- Inspect chamber seals

**Humidity chamber condensing on samples:**
- Reduce ramp rate
- Check temperature uniformity
- Verify sample positioning

**Inconsistent IV measurements:**
- Allow adequate stabilization time
- Check light source calibration
- Verify temperature compensation

**High variability in visual inspection:**
- Use standardized lighting
- Employ multiple inspectors for consensus
- Reference comparison standards

## References

1. IEC 61701:2020 - Photovoltaic (PV) modules - Salt mist corrosion testing
2. ASTM B117-19 - Standard Practice for Operating Salt Spray (Fog) Apparatus
3. IEC 61215-2:2021 - Terrestrial photovoltaic (PV) modules - Design qualification and type approval
4. IEC 60904-1:2020 - Photovoltaic devices - Measurement of photovoltaic current-voltage characteristics

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-01-15 | Initial release |

## Contact

For questions or support regarding the CORR-001 protocol:
- Email: protocols@example.com
- GitHub Issues: https://github.com/ganeshgowri-ASA/test-protocols/issues
