# PID-002: Potential-Induced Degradation (Polarization) Test

## Protocol Overview

**Protocol ID:** PID-002
**Version:** 1.0.0
**Category:** Degradation Testing
**Standard Reference:** IEC 62804-1
**Estimated Duration:** 192 hours (8 days) + 96 hours recovery (4 days)

## Purpose

The PID-002 protocol evaluates the susceptibility of photovoltaic (PV) modules to potential-induced degradation (PID), a phenomenon where high voltage stress between the module frame and solar cells causes ion migration, leading to power loss and performance degradation.

## Test Principle

PID testing subjects PV modules to high voltage stress (typically -1000V for p-type cells) under elevated temperature (85°C) and humidity (85% RH) conditions. The combination of electrical stress and environmental conditions accelerates PID effects, allowing assessment of long-term field performance in a compressed timeframe.

## Key Parameters

- **Voltage Stress:** -1000V (configurable: -1500V, -1000V, -600V, +1000V)
- **Temperature:** 85°C ± 2°C
- **Relative Humidity:** 85% ± 5%
- **Test Duration:** 192 hours (configurable: 96, 192, 336, 672 hours)
- **Measurement Interval:** Every 24 hours
- **Recovery Period:** 96 hours post-stress

## Equipment Requirements

### Essential Equipment

1. **Climate Chamber**
   - Temperature range: 0-100°C
   - Humidity range: 10-95%
   - Temperature uniformity: ±2°C
   - Humidity uniformity: ±5%
   - Calibration: Required every 12 months

2. **High Voltage Power Supply**
   - Voltage range: 0-2000V
   - Current capability: 0-10A
   - Current limiting: Required for safety
   - Calibration: Required every 12 months

3. **I-V Curve Tracer / Solar Simulator**
   - Irradiance: 1000 W/m² (STC)
   - Spectral match: Class A
   - Uniformity: ±2%
   - Calibration: Required every 6 months

4. **Environmental Data Logger**
   - Temperature accuracy: ±0.5°C
   - Humidity accuracy: ±3%
   - Sampling rate: ≥1 per minute
   - Calibration: Required every 12 months

### Optional Equipment

5. **Electroluminescence (EL) Imaging System**
   - Resolution: ≥1 megapixel
   - Sensitivity: 850-1150 nm
   - For detailed defect analysis

## Sample Requirements

- **Sample Type:** PV modules
- **Minimum Samples:** 3 test samples + 2 control samples
- **Recommended:** 6 test samples + 2 control samples
- **Sample Preparation:**
  - Same production batch
  - Initial flash test to confirm power ratings
  - Visual inspection documentation
  - Serial number recording

## Test Procedure

### Phase 1: Initial Characterization (4 hours)

**Step 1.1: Visual Inspection**
- Document any visible defects
- Take photographs of module front and back
- Record in data entry form

**Step 1.2: I-V Curve Measurement**
- Conditions: 1000 W/m², 25°C module temperature
- Record:
  - Pmax (Maximum Power)
  - Voc (Open Circuit Voltage)
  - Isc (Short Circuit Current)
  - Vmpp (Voltage at Maximum Power Point)
  - Impp (Current at Maximum Power Point)
  - Fill Factor (calculated automatically)

**Step 1.3: Insulation Resistance Test**
- Measure insulation resistance (must be ≥40 MΩ)
- Record value

**Step 1.4: EL Imaging (Optional)**
- Capture baseline EL image
- Document any defects visible in EL

### Phase 2: Test Setup (2 hours)

**Step 2.1: Module Installation**
1. Mount modules in climate chamber
2. Ensure frame is electrically isolated
3. Connect high voltage supply:
   - Negative terminal to module frame (for p-type cells)
   - Positive terminal to chamber ground through current limiting resistor
4. Install temperature sensors on module backsheet
5. Connect environmental data logger

**Step 2.2: Chamber Conditioning**
1. Set chamber to 85°C, 85% RH
2. Allow stabilization for minimum 1 hour
3. Verify temperature and humidity uniformity

### Phase 3: Stress Application (192 hours)

**Step 3.1: Voltage Application**
1. Gradually ramp voltage to -1000V over 5 minutes
2. Monitor leakage current
3. Record initial voltage and current
4. Verify current limiting is active

**Step 3.2: Continuous Monitoring**
- Automated logging every minute:
  - Temperature (alert if <83°C or >87°C)
  - Humidity (alert if <80% or >90%)
  - Voltage (alert if deviation >5%)
  - Leakage current (alert if >100 mA)

**Step 3.3: Interim Measurements (Every 24 hours)**
1. Reduce voltage to zero
2. Remove modules from chamber
3. Allow modules to cool to 25°C (≈30 minutes)
4. Perform I-V curve measurement at STC
5. Calculate power degradation:
   ```
   Power Degradation (%) = ((Pmax_initial - Pmax_interim) / Pmax_initial) × 100
   ```
6. Return modules to chamber
7. Re-establish test conditions
8. Reapply voltage stress

### Phase 4: Post-Stress Measurement (2 hours)

**Step 4.1: Voltage Removal**
1. Gradually ramp voltage to zero over 5 minutes
2. Record final leakage current
3. Disconnect high voltage supply
4. Remove modules from chamber

**Step 4.2: Post-Stress I-V Measurement**
- Perform I-V curve measurement at STC
- Calculate immediate post-stress degradation

**Step 4.3: Post-Stress EL Imaging (Optional)**
- Capture EL image immediately after stress
- Compare with initial EL image

### Phase 5: Recovery Period (96 hours)

**Step 5.1: Recovery Storage**
- Store modules at standard conditions (25°C, 50% RH)
- Keep in dark or low light
- No electrical stress

**Step 5.2: Recovery Measurements (Every 24 hours)**
- Perform I-V measurements
- Track power recovery:
  ```
  Power Recovery (%) = ((Pmax_recovery - Pmax_post_stress) / (Pmax_initial - Pmax_post_stress)) × 100
  ```

### Phase 6: Final Characterization (2 hours)

**Step 6.1: Final I-V Measurement**
- Perform comprehensive I-V curve measurement
- Calculate final power degradation:
  ```
  Final Degradation (%) = ((Pmax_initial - Pmax_final) / Pmax_initial) × 100
  ```

**Step 6.2: Final Visual Inspection**
- Document any new visual defects
- Compare with initial inspection

**Step 6.3: Final Insulation Resistance**
- Measure and record final insulation resistance

**Step 6.4: Final EL Imaging (Optional)**
- Capture final EL image
- Comprehensive comparison with initial and post-stress images

## Pass/Fail Criteria

### Pass Conditions (per IEC 62804-1)

1. **Power Degradation:** ≤ 5% after recovery period
2. **Insulation Resistance:** ≥ 40 MΩ after testing

### Performance Grading

| Grade | Description | Final Power Degradation |
|-------|-------------|------------------------|
| **A** | PID-free | ≤ 0% |
| **B** | Low PID susceptibility | 0% to 2% |
| **C** | Moderate PID susceptibility | 2% to 5% |
| **D** | High PID susceptibility | 5% to 10% |
| **F** | Failed - Severe PID | > 10% |

## Safety Requirements

### Hazards

1. **High Voltage (CRITICAL)**
   - Use isolated power supply with current limiting
   - Implement emergency shutoff accessible from outside chamber
   - Post high voltage warning signs
   - Use proper lockout/tagout procedures
   - Ensure all personnel are trained on high voltage safety

2. **Electrical Shock (CRITICAL)**
   - Ensure all connections are properly insulated
   - Verify chamber door interlocks are functional
   - Discharge all capacitance before handling modules
   - Use insulated tools and PPE

3. **Module Damage (MODERATE)**
   - Handle modules with care
   - Inspect for cracks before testing
   - Use proper lifting techniques

### Required PPE

- Safety glasses
- Insulated gloves (for high voltage work)
- Lab coat
- Closed-toe shoes

### Required Training

- High voltage safety
- Climate chamber operation
- PV module handling
- Emergency procedures

## Data Analysis

### Key Metrics

1. **Power Degradation Rate**
   ```
   Rate (%/hour) = Power_Degradation_Post_Stress / Total_Stress_Hours
   ```

2. **Reversible Degradation**
   ```
   Reversible (%) = Power_Degradation_Post_Stress - Power_Degradation_Final
   ```

3. **Irreversible Degradation**
   ```
   Irreversible (%) = Power_Degradation_Final
   ```

### Charts and Visualizations

1. **Power Degradation Curve**
   - X-axis: Time (hours)
   - Y-axis: Power degradation (%)
   - Shows degradation progression during stress

2. **I-V Curve Comparison**
   - Overlay of initial, post-stress, and final I-V curves
   - Visualizes impact on electrical characteristics

3. **Recovery Curve**
   - X-axis: Recovery time (hours)
   - Y-axis: Power recovery (%)
   - Shows recovery dynamics

4. **Environmental Conditions**
   - Time-series plot of temperature and humidity
   - Verifies test conditions were maintained

## QC Rules and Alerts

### Automatic QC Checks

1. **QC001:** Initial power deviation >5% from nameplate → Review sample
2. **QC002:** Leakage current >100 mA → Abort test
3. **QC003:** Insulation resistance <40 MΩ → Review sample
4. **QC004:** Power degradation >10% → Flag high PID susceptibility
5. **QC005:** Temperature out of range → Review data
6. **QC006:** Humidity out of range → Review data
7. **QC007:** Incomplete recovery (>5% final degradation) → Note in report

## Report Generation

The system automatically generates a comprehensive test report including:

1. **Executive Summary**
   - Test objective and sample information
   - Key results and pass/fail status

2. **Test Setup and Conditions**
   - Equipment used and calibration status
   - Test parameters

3. **Results**
   - All measurements in tabular format
   - Interim measurements table
   - Recovery data

4. **Data Analysis**
   - Charts and visualizations
   - Statistical analysis
   - Degradation rates

5. **Visual and EL Inspection**
   - Image comparisons
   - Defect analysis

6. **Discussion**
   - Performance evaluation
   - Comparison to standards
   - Recommendations

7. **Conclusion**
   - Final verdict and grading

8. **Appendices**
   - Raw data
   - Calibration certificates
   - Complete monitoring logs

## Troubleshooting

### Common Issues

1. **High Leakage Current**
   - Check insulation of connections
   - Verify module insulation resistance
   - Inspect for moisture ingress

2. **Temperature/Humidity Instability**
   - Check chamber door seal
   - Verify chamber calibration
   - Reduce sample load if needed

3. **Inconsistent Measurements**
   - Verify simulator calibration
   - Check module temperature stabilization
   - Ensure consistent measurement conditions

4. **Power Supply Tripping**
   - Check current limit settings
   - Verify connection integrity
   - Inspect for short circuits

## References

1. IEC 62804-1:2015 - Photovoltaic (PV) modules - Test methods for the detection of potential-induced degradation - Part 1: Crystalline silicon
2. IEC 61215:2016 - Terrestrial photovoltaic (PV) modules - Design qualification and type approval
3. IEC 61730:2016 - Photovoltaic (PV) module safety qualification

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-11-14 | Test Protocols Team | Initial release |

---

**For technical support or questions, please contact your system administrator.**
