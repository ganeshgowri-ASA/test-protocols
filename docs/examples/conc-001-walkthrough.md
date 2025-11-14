# CONC-001 Concentration Testing - Complete Walkthrough

This guide provides a step-by-step walkthrough of executing a CONC-001 concentration test using the Test Protocols Framework.

## Prerequisites

- Test Protocols Framework installed
- Equipment calibrated and ready
- Sample prepared for testing

## Step 1: Launch the Application

```bash
streamlit run src/ui/streamlit_app.py
```

The GenSpark UI will open in your browser.

## Step 2: Select Protocol

1. Navigate to "Protocol Selection" in the sidebar
2. Select "conc-001" from the dropdown
3. Review protocol details:
   - Equipment requirements
   - Safety requirements
   - QC criteria
4. Click "Load Protocol"

## Step 3: Prepare Test Setup

### Required Equipment
- Solar simulator (Class AAA)
- Reference cell (NIST traceable)
- Temperature chamber
- Data acquisition system

### Verification Checklist
- [ ] Equipment calibration current (within last 180-365 days)
- [ ] Sample properly mounted
- [ ] Temperature sensors connected
- [ ] Data acquisition configured

## Step 4: Enter Test Information

Navigate to "Data Entry" page.

### Test Information Fields
```
Test Run ID: CONC-001-20251114-0001 (auto-generated format)
Sample ID: PV-SAMPLE-001
Operator Name: John Smith
Test Date: 2025-11-14 10:30:00 (auto-filled)
```

### Equipment Information
```
Solar Simulator: SIM-001-ClassAAA
Reference Cell: REF-CELL-001
Last Calibration Date: 2025-06-01
```

### Environmental Conditions
```
Ambient Temperature: 22.5 °C
Humidity: 45 %
Atmospheric Pressure: 101.3 kPa
```

## Step 5: Perform Measurements

For each concentration level (1, 10, 25, 50, 100, 200, 300, 400, 500 suns):

### Measurement Procedure
1. Set concentration level on solar simulator
2. Verify with reference cell
3. Wait for temperature stabilization (5 minutes)
4. Record I-V curve
5. Extract parameters

### Example Measurement at 1 Sun
```
Concentration: 1.0 suns
Cell Temperature: 25.0 °C
Voc: 0.650 V
Isc: 8.5 A
Vmp: 0.550 V
Imp: 8.0 A
Fill Factor: 0.846 (calculated: Vmp*Imp/(Voc*Isc))
Efficiency: 22.5 %
```

Click "Add Measurement" to add each data point.

## Step 6: Validate Data

Before saving, click "Validate Data" to check:
- Data completeness
- Value ranges
- QC criteria
- Calibration status

### Validation Results
```
✓ All required fields present
✓ Values within acceptable ranges
⚠ Warning: Fill factor at 100 suns slightly below typical
✓ Equipment calibration current
```

## Step 7: Save and Review

1. Click "Save Data" to store the test data
2. Navigate to "Test Results" page
3. Review:
   - Summary metrics
   - Data table
   - Performance plots
   - Statistical analysis

### Expected Plots
- **Efficiency vs Concentration:** Shows how efficiency changes with intensity
- **Fill Factor vs Concentration:** Indicates series resistance effects
- **Power Output vs Concentration:** Linear relationship expected

## Step 8: QC Dashboard

Navigate to "QC Dashboard" to verify:

### QC Checks
- ✓ Temperature stability: ±2°C
- ✓ Measurement repeatability: CV < 5%
- ✓ Fill factor minimum: ≥ 0.65
- ⚠ Spectral mismatch: 0.03 (acceptable < 0.05)

### Data Quality
- Outlier detection
- Equipment calibration status
- Recommendations

## Step 9: Generate Report

Navigate to "Report Generation" to create final report.

### Report Contents
1. **Executive Summary**
   - Test identification
   - Date and operator
   - Overall results

2. **Data Summary**
   - Total measurements: 9
   - Concentration range: 1.0 - 500.0 suns
   - Temperature range: 25.0 °C

3. **Statistical Analysis**
   - Mean efficiency: 26.8 %
   - Std deviation: 3.2 %
   - Temperature coefficient: -0.045 %/°C

4. **Quality Indicators**
   - No efficiency outliers detected
   - No fill factor outliers detected

### Export Options
- Download JSON Report
- Download Text Report
- Download CSV Data

## Step 10: Data Export

Export options:
```
- CSV: For Excel/analysis tools
- JSON: For programmatic access
- Text Report: For documentation
```

## Example Complete Dataset

```json
{
  "test_run_id": "CONC-001-20251114-0001",
  "sample_id": "PV-SAMPLE-001",
  "operator": "John Smith",
  "timestamp": "2025-11-14T10:30:00",
  "measurements": [
    {
      "concentration_suns": 1.0,
      "temperature_c": 25.0,
      "voc": 0.650,
      "isc": 8.5,
      "vmp": 0.550,
      "imp": 8.0,
      "fill_factor": 0.846,
      "efficiency": 22.5
    },
    {
      "concentration_suns": 10.0,
      "temperature_c": 25.0,
      "voc": 0.750,
      "isc": 85.0,
      "vmp": 0.650,
      "imp": 80.0,
      "fill_factor": 0.815,
      "efficiency": 26.8
    },
    // ... more measurements
  ]
}
```

## Troubleshooting

### Common Issues

**Issue: Validation fails on test run ID**
- Solution: Ensure format is CONC-001-YYYYMMDD-####

**Issue: Fill factor warning**
- Solution: Check connections and verify I-V curve quality

**Issue: Temperature out of range**
- Solution: Allow more stabilization time

**Issue: Equipment calibration expired**
- Solution: Re-calibrate equipment before testing

## Best Practices

1. **Always verify equipment calibration before testing**
2. **Allow sufficient stabilization time at each setpoint**
3. **Record environmental conditions**
4. **Document any anomalies in notes field**
5. **Save data frequently during long tests**
6. **Export data for backup**

## Next Steps

After completing CONC-001:
- Review results with team
- Compare with historical data
- Archive test data
- Schedule follow-up tests if needed

## Support

For questions or issues:
- Refer to protocol documentation: `protocols/conc-001/README.md`
- Check QC criteria: Protocol schema
- Contact test engineering team
