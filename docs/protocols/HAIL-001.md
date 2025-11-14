# HAIL-001: Hail Impact Test Protocol

## Overview

**Protocol ID**: HAIL-001
**Version**: 1.0.0
**Category**: Mechanical
**Standard**: IEC 61215 MQT 17
**Reference**: IEC 61215-2:2021

## Purpose

The HAIL-001 protocol verifies that photovoltaic (PV) modules can withstand the impact of hailstones at specified velocities and temperatures, simulating real-world hail events.

## Test Scope

- **Application**: Crystalline silicon terrestrial photovoltaic (PV) modules
- **Test Type**: Destructive mechanical testing
- **Duration**: Approximately 2-3 hours

## Test Parameters

### Standard Test Conditions

| Parameter | Value | Tolerance |
|-----------|-------|-----------|
| Hailstone Diameter | 25 mm | ±0.5 mm |
| Hailstone Weight | 7.53 g | ±0.1 g |
| Impact Velocity | 80 km/h (23 m/s) | ±2 km/h |
| Hailstone Temperature | -4°C | ±2°C |
| Time Limit (retrieval to impact) | 60 seconds | Maximum |
| Number of Impact Locations | 11 | Exact |

### Extended Test (IEC TS 63397:2022)

For enhanced hail resistance testing:
- Hailstone diameter range: 25-80 mm in 5 mm increments
- Same velocity and temperature requirements

## Equipment Required

1. **Hail Impact Tester**
   - Pneumatic launcher with velocity control
   - Velocity range: 0-120 km/h
   - Accuracy: ±2 km/h

2. **Cold Storage Container**
   - Temperature: -20°C to 0°C
   - Stability: ±1°C

3. **IV Curve Tracer**
   - For Pmax measurements (STC conditions)
   - Accuracy: ±1%

4. **Insulation Resistance Tester (Megohmmeter)**
   - Test voltage: 1000V DC
   - Range: 0.1-1000 MΩ

5. **High-Speed Camera** (Optional)
   - For impact recording
   - Frame rate: ≥1000 fps

6. **Thermal Imaging Camera** (Optional)
   - For hotspot detection
   - Temperature range: -20°C to 150°C

## Test Procedure

### Phase 1: Pre-Test

1. **Visual Inspection**
   - Document any pre-existing defects
   - Take reference photographs

2. **Initial Electrical Measurements (STC)**
   - Measure Pmax, Voc, Isc, Vmp, Imp
   - Calculate fill factor
   - Record all values

3. **Insulation Resistance Test**
   - Apply 1000V DC
   - Measure resistance (must be ≥40 MΩ·m², typically ≥400 MΩ)

4. **Ice Ball Preparation**
   - Prepare ice balls to 25 mm diameter
   - Condition to -4°C ±2°C in cold storage

5. **Module Mounting**
   - Secure module in test fixture
   - Mark 11 impact locations

### Phase 2: Impact Test Execution

For each of the 11 impact locations:

1. Retrieve ice ball from cold storage
2. Launch ice ball at module surface
3. Ensure impact occurs within 60 seconds of retrieval
4. Verify velocity: 80 km/h ±2 km/h
5. Monitor for open-circuit conditions during impact
6. Document any visual damage
7. Optionally record with high-speed camera

**Impact Location Pattern:**
- 1 center location
- 4 corner locations
- 4 edge center locations
- 2 quarter locations

### Phase 3: Post-Test

1. **Visual Inspection**
   - Inspect for:
     - Front glass cracks
     - Cell cracks
     - Backsheet cracks
     - Delamination
     - Junction box damage
     - Frame damage
   - Document all observations with photographs

2. **Final Electrical Measurements (STC)**
   - Measure Pmax, Voc, Isc, Vmp, Imp
   - Calculate fill factor

3. **Insulation Resistance Test**
   - Repeat 1000V DC test
   - Compare to initial value

4. **Optional Tests**
   - Electroluminescence (EL) imaging for microcracks
   - Thermal imaging for hotspots

## Pass/Fail Criteria

The module **PASSES** if ALL of the following conditions are met:

### 1. Power Degradation
**Criterion**: Pmax degradation ≤ 5%
**Calculation**: `((Pmax_initial - Pmax_final) / Pmax_initial) × 100% ≤ 5%`

### 2. Visual Inspection
**Criterion**: No major visual defects
**Details**:
- ✅ No cracks in front glass that could allow water ingress
- ✅ No cracks in backsheet that could allow water ingress
- ✅ No delamination exceeding allowable limits
- ✅ No broken solder bonds visible
- ✅ No junction box damage

### 3. Insulation Resistance
**Criterion**: ≥40 MΩ·m² (typically ≥400 MΩ for standard module)
**Details**: No significant degradation from initial measurement

### 4. Open Circuit Test
**Criterion**: No intermittent open-circuit during impact test
**Details**: Continuous electrical monitoring during all 11 impacts

## Data Analysis

### Required Calculations

1. **Power Degradation Percentage**
   ```
   Degradation (%) = ((Pmax_initial - Pmax_final) / Pmax_initial) × 100
   ```

2. **Impact Time Compliance**
   ```
   Time Delta = Impact_time - Ice_ball_retrieval_time
   Compliant if ≤ 60 seconds
   ```

3. **Velocity Accuracy**
   ```
   Deviation = |Actual_velocity - Target_velocity|
   Compliant if ≤ 2 km/h
   ```

### Statistical Analysis

- Impact velocity mean and standard deviation
- Time compliance rate
- Correlation between impact location and damage severity

## Safety Considerations

⚠️ **Important Safety Requirements**:

1. **Eye Protection**: Required for all personnel during impact testing
2. **Safe Distance**: Maintain safe distance from impact zone (ice balls can ricochet)
3. **Electrical Safety**: Follow high voltage safety procedures for IV testing
4. **Pressure Vessel Safety**: Follow compressed air system safety protocols
5. **Cold Protection**: Use insulated gloves when handling ice balls

## Report Requirements

### Required Sections

1. Test Identification
2. Module Information
3. Equipment Used and Calibration
4. Test Conditions
5. Pre-test Measurements
6. Impact Test Data (all 11 locations)
7. Post-test Measurements
8. Visual Inspection Results
9. Pass/Fail Determination
10. Photographs and Videos
11. Deviations and Notes

### Required Data Tables

- Pre-test electrical parameters
- Impact test data (11 rows minimum)
- Post-test electrical parameters
- Pass/fail criteria evaluation

### Required Charts

- IV curves (pre vs post)
- Impact velocity distribution
- Power degradation visualization
- Impact location diagram

## References

1. **IEC 61215-2:2021** - Terrestrial photovoltaic (PV) modules - Design qualification and type approval - Part 2: Test procedures
2. **IEC TS 63397:2022** - Photovoltaic (PV) modules - Extended hail impact testing
3. **IEC 61730** - Photovoltaic (PV) module safety qualification

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-11-14 | Claude | Initial protocol implementation |

## Appendix A: Impact Location Coordinates

Standard 11 impact locations (normalized coordinates):

| ID | Location | X | Y | Description |
|----|----------|---|---|-------------|
| 1 | Center | 0.50 | 0.50 | Center of module |
| 2 | Corner | 0.10 | 0.10 | Top left corner |
| 3 | Corner | 0.90 | 0.10 | Top right corner |
| 4 | Corner | 0.10 | 0.90 | Bottom left corner |
| 5 | Corner | 0.90 | 0.90 | Bottom right corner |
| 6 | Edge | 0.50 | 0.10 | Top center edge |
| 7 | Edge | 0.50 | 0.90 | Bottom center edge |
| 8 | Edge | 0.10 | 0.50 | Left center edge |
| 9 | Edge | 0.90 | 0.50 | Right center edge |
| 10 | Quarter | 0.25 | 0.25 | Top left quarter |
| 11 | Quarter | 0.75 | 0.75 | Bottom right quarter |

## Appendix B: Common Issues and Troubleshooting

### Ice Ball Does Not Reach Target Velocity

- **Cause**: Insufficient launcher pressure
- **Solution**: Increase launcher pressure incrementally; recalibrate

### Ice Ball Melts Before Impact

- **Cause**: Ambient temperature too high or time delay too long
- **Solution**: Work in climate-controlled environment; reduce handling time

### Inconsistent Velocity Readings

- **Cause**: Launcher calibration drift
- **Solution**: Recalibrate launcher before each test session

### Module Shows Pre-existing Damage

- **Cause**: Damaged module received
- **Solution**: Document thoroughly; consider replacement; note in test report

## Contact

For questions about this protocol or test execution:
- Technical Support: [Contact Information]
- Standards Compliance: [Contact Information]
