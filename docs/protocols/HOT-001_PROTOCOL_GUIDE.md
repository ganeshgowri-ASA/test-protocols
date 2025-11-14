# HOT-001: Hot Spot Endurance Test Protocol Guide

## Overview

**Protocol ID:** HOT-001
**Standard:** IEC 61215 MQT 09
**Category:** Safety Testing
**Version:** 1.0.0

### Purpose

The Hot Spot Endurance Test determines a photovoltaic (PV) module's ability to endure hot spot heating effects caused by:
- Non-uniform irradiance
- Cell cracking or damage
- Reverse bias conditions
- Shading or soiling

This test ensures that PV modules can withstand localized heating without catastrophic failure, fire hazard, or excessive degradation.

## Test Principle

Hot spots occur when one or more cells in a series string become reverse-biased due to shading, damage, or manufacturing defects. The reverse-biased cell dissipates power as heat rather than generating power, potentially reaching dangerous temperatures.

The test simulates worst-case hot spot conditions by:
1. Applying reverse bias voltage to selected cells
2. Limiting current to short-circuit current (Isc)
3. Monitoring temperature rise to target 85°C ±5°C
4. Maintaining conditions for 1 hour per cell
5. Testing minimum 3 cells per module

## Equipment Requirements

### Required Equipment

| Equipment | Specifications | Calibration Interval |
|-----------|---------------|---------------------|
| **Solar Simulator** | 1000 W/m², Class A spectral match, ±2% uniformity | 6 months |
| **I-V Curve Tracer** | ±0.5% V/I accuracy, >100 points/curve | 12 months |
| **Temperature Sensors** | Type K thermocouple, ±1°C accuracy | 12 months |
| **Power Supply** | 0 to 1.5×Voc, 0 to 2×Isc, ±0.1% regulation | 12 months |
| **Thermal Camera** | -20°C to +150°C range, ±2°C accuracy | 12 months |
| **Insulation Tester** | 500-1000V DC, 0.1-1000 MΩ range | 12 months |
| **Data Logger** | Minimum 8 channels, 1 Hz sampling | N/A |

### Safety Equipment

- Safety glasses with UV protection
- Insulated gloves (rated for test voltage)
- Heat-resistant gloves
- Anti-static wrist strap
- Fire extinguisher (Class C electrical)

## Test Procedure

### Step 1: Initial Visual Inspection

**Duration:** 15 minutes

1. Photograph module from multiple angles
2. Inspect for pre-existing defects:
   - Cell cracks or breakage
   - Discoloration or browning
   - Bubbles or delamination
   - Junction box damage
   - Frame deformation
3. Document all findings with photographs
4. Record in visual inspection log

**Acceptance Criteria:** Document all defects; no immediate disqualification

---

### Step 2: Initial I-V Curve Measurement

**Duration:** 30 minutes

1. **Setup:**
   - Mount module in solar simulator
   - Allow module to stabilize at 25°C ±2°C
   - Set irradiance to 1000 W/m² (STC conditions)
   - Connect I-V curve tracer

2. **Measurement:**
   - Capture complete I-V curve (>100 points)
   - Measure: Voc, Isc, Vmp, Imp, Pmax, FF
   - Repeat 3 times and average results
   - Record ambient conditions

3. **Data Recording:**
   ```
   Initial Measurements:
   - Voc: _____ V
   - Isc: _____ A
   - Pmax: _____ W
   - Fill Factor: _____
   - Irradiance: 1000 W/m²
   - Temperature: 25°C
   ```

**Acceptance Criteria:** Pmax within ±3% of nameplate rating

---

### Step 3: Initial Insulation Resistance Test

**Duration:** 15 minutes

1. Disconnect module from all equipment
2. Short all module terminals together
3. Apply test voltage: max(500V, 2×(Voc+50V))
4. Measure insulation resistance
5. Record result in MΩ

**Acceptance Criteria:** ≥ 400 MΩ

---

### Step 4: Cell Selection and Marking

**Duration:** 15 minutes

1. Select 3 cells for testing:
   - Cell 1: From first third of module
   - Cell 2: From middle third of module
   - Cell 3: From last third of module

2. Mark selected cells on backsheet (non-permanent marker)

3. Document cell locations with photograph

**Example Cell Selection:**
```
Module Grid (60-cell module):
[A1] [A2] [A3] ... [A10]  → Select Cell A5
[B1] [B2] [B3] ... [B10]
[C1] [C2] [C3] ... [C10]  → Select Cell C5
[D1] [D2] [D3] ... [D10]
[E1] [E2] [E3] ... [E10]
[F1] [F2] [F3] ... [F10]  → Select Cell F5
```

---

### Step 5: Bypass Diode Verification

**Duration:** 30 minutes

1. **For each selected cell:**
   - Shade only that cell completely
   - Illuminate rest of module at 1000 W/m²
   - Measure voltage across cell string
   - Verify bypass diode activates

2. **Expected Results:**
   - Bypass diode voltage drop: 0.4-0.7V
   - Activation current: near Isc
   - Module voltage: Voc minus one cell string

3. Record bypass diode activation for each cell

**Acceptance Criteria:** All bypass diodes must activate properly

---

### Step 6: Hot Spot Test Setup

**Duration:** 45 minutes

1. **Physical Setup:**
   - Mount module horizontally, backsheet facing up
   - Ensure adequate ventilation
   - Position fire extinguisher within reach

2. **Sensor Installation:**
   - Attach thermocouples to 3 test cell locations (backsheet)
   - Attach one thermocouple for ambient temperature
   - Secure sensors with heat-resistant tape

3. **Equipment Configuration:**
   - Connect power supply to module terminals
   - Set voltage limit: 1.25 × Voc
   - Set current limit: Isc
   - Configure data logger (30-second intervals)
   - Position thermal camera facing module backsheet

4. **Safety Checks:**
   - Verify all sensors connected
   - Test emergency shutdown procedure
   - Confirm ventilation active
   - Set temperature alarm at 120°C (abort limit)

---

### Steps 7-9: Hot Spot Generation (One Cell at a Time)

**Duration:** 1 hour per cell (3 hours total)

**For each selected cell:**

1. **Pre-Test:**
   - Verify safety systems active
   - Clear area of flammable materials
   - Begin data logging

2. **Apply Reverse Bias:**
   - Gradually increase voltage to 1.25 × Voc
   - Limit current to Isc
   - Monitor cell temperature

3. **Temperature Control:**
   - Target temperature: 85°C ±5°C
   - Adjust power to maintain temperature
   - Monitor continuously

4. **Duration:**
   - Maintain target temperature for 60 minutes
   - Record temperature every 30 seconds
   - Capture thermal image every 5 minutes

5. **Monitoring:**
   - Watch for smoke or unusual odors
   - Monitor temperature trend
   - Check thermal camera for hot spot location

6. **Safety Abort Conditions:**
   - Temperature exceeds 120°C
   - Visible smoke or fire
   - Strong burning odor
   - Sudden temperature spike (>10°C/min)
   - Open circuit condition

7. **Post-Cell Cool Down:**
   - Reduce voltage gradually to zero
   - Allow cell to cool to <40°C before next test
   - Minimum 30-minute cool down between cells

**Data Recording Per Cell:**
```
Cell: _____
Start Time: _____
Target Temp: 85°C
Max Temp Reached: _____ °C
Average Temp (last 30 min): _____ °C
Reverse Bias Voltage: _____ V
Current: _____ A
Duration: 60 minutes
Thermal Images: _____ files
Abort/Complete: _____
```

---

### Step 10: Cool Down Period

**Duration:** 30-60 minutes

1. Disconnect all power
2. Allow module to cool naturally
3. Monitor temperature until module ≤ ambient + 5°C
4. Visual inspection for immediate damage

---

### Step 11: Post-Test Visual Inspection

**Duration:** 30 minutes

**Detailed Inspection:**

1. **Backsheet Inspection:**
   - Discoloration at hot spot locations
   - Melting or deformation
   - Perforation or cracks
   - Measure discolored area (% of cell)

2. **Cell Inspection (front):**
   - Cell cracks (use EL imaging if available)
   - Solder joint damage
   - Discoloration or browning

3. **Encapsulant Inspection:**
   - Bubbling or delamination
   - Color change
   - Flow or distortion

4. **Junction Box Inspection:**
   - Melting or deformation
   - Connector damage
   - Internal damage (open if safe)

5. **Bypass Diode Check:**
   - Functionality test (repeat Step 5)
   - Resistance measurement

**Acceptable Minor Defects:**
- Discoloration < 10% of cell area at hot spot
- Slight encapsulant yellowing at hot spot
- Minor backsheet color change

**Unacceptable Major Defects:**
- Cell cracks or breakage
- Backsheet melting or perforation
- Junction box damage
- Bypass diode failure
- Encapsulant severe deformation
- Open circuit or ground fault

---

### Step 12: Final I-V Curve Measurement

**Duration:** 30 minutes

**Repeat Step 2 procedure exactly:**

1. Same STC conditions (1000 W/m², 25°C, AM1.5)
2. Same measurement technique
3. Same number of repetitions (3×)
4. Record all parameters

**Data Recording:**
```
Final Measurements:
- Voc: _____ V (Δ = _____ %)
- Isc: _____ A (Δ = _____ %)
- Pmax: _____ W (Δ = _____ %)
- Fill Factor: _____ (Δ = _____ %)
```

---

### Step 13: Final Insulation Resistance Test

**Duration:** 15 minutes

Repeat Step 3 procedure exactly.

**Acceptance Criteria:** ≥ 400 MΩ

---

### Step 14: Wet Leakage Current Test

**Duration:** 45 minutes

1. **Preparation:**
   - Prepare water solution (0.1% NaCl or distilled water)
   - Temperature: 20-30°C

2. **Test Setup:**
   - Immerse module edges in solution (frame submerged 2-5 cm)
   - Short all module terminals together
   - Connect to insulation tester

3. **Measurement:**
   - Apply test voltage for 60 seconds
   - Measure leakage current
   - Record in µA

4. **Cleanup:**
   - Remove module from solution
   - Dry thoroughly
   - Inspect for water ingress

**Acceptance Criteria:** ≤ 50 µA

---

## Pass/Fail Criteria

### Critical Parameters

| Parameter | Limit | Priority |
|-----------|-------|----------|
| **Power Degradation** | ≤ 5% | CRITICAL |
| **Insulation Resistance** | ≥ 400 MΩ | CRITICAL |
| **Wet Leakage Current** | ≤ 50 µA | CRITICAL |
| **Visual Defects** | No major defects | CRITICAL |
| **Bypass Diodes** | All functional | CRITICAL |

### Power Degradation Calculation

```
Degradation (%) = ((Pmax_initial - Pmax_final) / Pmax_initial) × 100
```

**Example:**
- Initial Pmax: 300.0 W
- Final Pmax: 291.0 W
- Degradation: ((300.0 - 291.0) / 300.0) × 100 = 3.0%
- **Result: PASS** (< 5%)

### Overall Pass/Fail Logic

Module **PASSES** if ALL of the following are true:
- ✓ Power degradation ≤ 5%
- ✓ Final insulation resistance ≥ 400 MΩ
- ✓ Wet leakage current ≤ 50 µA
- ✓ No major visual defects
- ✓ All 3 hot spot tests completed successfully
- ✓ All bypass diodes remain functional

Module **FAILS** if ANY of the following are true:
- ✗ Power degradation > 5%
- ✗ Final insulation resistance < 400 MΩ
- ✗ Wet leakage current > 50 µA
- ✗ Major visual defects present
- ✗ Fewer than 3 cells tested
- ✗ Any bypass diode failed
- ✗ Safety abort during hot spot test

---

## Data Management

### Required Data Collection

**Test Metadata:**
- Test ID
- Module serial number
- Module manufacturer and model
- Nameplate power rating
- Test date and time
- Operator name and certification
- Test facility

**Measurement Data:**
- Initial and final I-V curves (raw data + parameters)
- Temperature profiles for all 3 cells (30-second intervals)
- Thermal images (every 5 minutes during hot spot tests)
- Insulation resistance measurements
- Wet leakage current measurement
- Visual inspection photographs (before and after)

**Equipment Data:**
- Equipment IDs
- Calibration dates and certificates
- Calibration due dates

### Data Retention

**Requirement:** 25 years (per IEC 61215)

**Storage Format:**
- Primary: JSON (structured data + metadata)
- Secondary: PDF (formatted report)
- Raw data: CSV (measurements, temperature profiles)
- Images: JPEG (visual inspection, thermal images)

### Traceability

**QR Code Generation:**
- Encode: Test ID, Protocol ID, Module Serial, Date, Operator
- Print on test report and module label
- Link to database record

---

## Safety Procedures

### Pre-Test Safety Briefing

1. Review hot spot test hazards
2. Identify emergency shutdown procedures
3. Locate fire extinguisher and exits
4. Assign safety monitor (for critical tests)

### During Test

**Continuous Monitoring:**
- Temperature (automated alarm at 120°C)
- Visual observation (smoke, arcing)
- Thermal camera (hot spot migration)

**Abort Conditions:**
- Temperature > 120°C
- Smoke or fire
- Equipment malfunction
- Power outage

### Emergency Response

**If Fire Occurs:**
1. Press emergency shutdown button
2. Disconnect power supply
3. Use Class C fire extinguisher
4. Evacuate if fire not immediately controlled
5. Call emergency services

**If Excessive Temperature:**
1. Reduce power gradually
2. Increase ventilation
3. Monitor for 5 minutes
4. If temperature continues rising, abort test

---

## Troubleshooting

### Common Issues

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| Temperature won't reach 85°C | Insufficient power | Increase voltage (within 1.25×Voc limit) |
| | Excessive cooling | Reduce ventilation |
| Temperature too high | Excessive power | Reduce voltage |
| | Poor heat dissipation | Increase ventilation |
| Bypass diode not activating | Diode failure | Mark as major defect; fail module |
| | Incorrect shading | Re-check shading setup |
| Thermal runaway | Hot spot migration | Abort test immediately |
| | Encapsulant degradation | Document and abort |
| I-V curve measurement error | Poor contact | Clean and reconnect terminals |
| | Module not stabilized | Allow more temperature stabilization |

---

## Report Generation

### Required Report Sections

1. **Executive Summary**
   - Test ID and date
   - Module information
   - Pass/fail result
   - Key findings

2. **Module Information**
   - Manufacturer, model, serial number
   - Nameplate specifications
   - Manufacturing date (if available)

3. **Test Conditions**
   - Ambient temperature and humidity
   - Equipment used (with calibration dates)
   - Operator information

4. **Test Results Summary**
   - Initial and final I-V parameters
   - Power degradation percentage
   - Insulation resistance values
   - Visual inspection summary

5. **Hot Spot Test Details**
   - Cell IDs and locations
   - Temperature profiles (charts)
   - Thermal images
   - Maximum temperatures reached

6. **Analysis**
   - Pass/fail determination
   - Comparison to criteria
   - Failure analysis (if applicable)

7. **Appendices**
   - Raw measurement data
   - Calibration certificates
   - Photographs
   - QR code for traceability

### Report Formats

- **PDF:** Primary report format (with charts and images)
- **JSON:** Structured data for database storage
- **CSV:** Raw measurement data for analysis

---

## Standards References

1. **IEC 61215-1:2021** - Terrestrial photovoltaic (PV) modules - Design qualification and type approval - Part 1: Test requirements

2. **IEC 61215-2:2021** - Part 2: Test procedures (Section MQT 09)

3. **IEC 60904-1:2020** - Photovoltaic devices - Part 1: Measurement of photovoltaic current-voltage characteristics

4. **IEC 60904-9:2020** - Photovoltaic devices - Part 9: Solar simulator performance requirements

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2025-11-14 | Initial release | Test Protocols Team |

---

## Contact Information

For questions or issues with this protocol:
- Technical Support: support@testlabs.example.com
- Protocol Development: protocols@testlabs.example.com

---

*This document is part of the Modular PV Testing Protocol Framework*
