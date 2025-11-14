# SALT-001: Salt Mist Corrosion Test

## Overview

- **Protocol Code**: SALT-001
- **Standard**: IEC 61701:2020
- **Category**: Environmental Testing
- **Version**: 1.0.0
- **Status**: Active

## Purpose

Evaluates the ability of photovoltaic (PV) modules to withstand exposure to salt mist corrosion, simulating coastal or marine environments. This test determines the resistance of module materials, coatings, and encapsulation to salt-induced degradation.

## Scope

### Applicable To

- Crystalline silicon PV modules
- Thin-film PV modules (CIGS, CdTe, etc.)
- All module frame materials and coatings
- Module mounting hardware and connectors
- Back contact and junction box assemblies

### Not Applicable To

- Cells without module assembly
- Modules larger than test chamber capacity
- Modules with active electrical connections during test

## Test Parameters

### Environmental Conditions (IEC 61701)

| Parameter | Min | Target | Max | Unit | Tolerance |
|-----------|-----|--------|-----|------|-----------|
| Salt Concentration | 4.5 | 5.0 | 5.5 | % NaCl | ±0.5% |
| Temperature | 34.0 | 35.0 | 36.0 | °C | ±1°C |
| Relative Humidity | 93.0 | 95.0 | 97.0 | % | ±2% |
| Spray Rate | 1.0 | 1.5 | 2.0 | mL/h/80cm² | - |
| Air Pressure | 0.7 | 1.0 | 1.3 | atm | - |

### Test Cycles

Each 24-hour cycle consists of:

1. **Spray Phase**: 2 hours
   - Salt mist spray active
   - Temperature: 35°C
   - Humidity: 95%

2. **Dry Phase**: 22 hours
   - No spray
   - Temperature: 35°C
   - Humidity: 95%

### Severity Levels

| Level | Duration | Cycles | Application |
|-------|----------|--------|-------------|
| 1 | 60 hours | 2.5 | Minimal corrosion risk |
| 2 | 120 hours | 5 | Low corrosion risk |
| 3 | 240 hours | 10 | Moderate corrosion risk (default) |
| 4 | 480 hours | 20 | High corrosion risk |
| 5 | 840 hours | 35 | Severe corrosion risk |

## Test Procedure

### 1. Pre-Test Preparation

1. **Specimen Documentation**
   - Record specimen ID, manufacturer, model number
   - Document rated power, dimensions, weight
   - Photograph module (all sides)
   - Record initial visual condition

2. **Initial Measurements**
   - Perform I-V curve measurement at STC
   - Record: Pmax, Voc, Isc, FF
   - Measure insulation resistance (>40 MΩ)
   - Verify no visual defects

3. **Salt Solution Preparation**
   - Dissolve 50 ± 5 g NaCl per liter of distilled water
   - Verify pH 6.5-7.2
   - Verify specific gravity 1.029-1.036 at 25°C
   - Filter to remove particulates

### 2. Test Execution

1. **Chamber Setup**
   - Set temperature to 35 ± 1°C
   - Set humidity to 95 ± 2%
   - Configure spray/dry cycle timing
   - Verify salt solution concentration

2. **Specimen Mounting**
   - Mount at 15-30° angle from vertical
   - Ensure no direct impingement of spray
   - Ensure adequate spacing between specimens
   - Front face should receive mist exposure

3. **Cycle Execution**
   - Start automated cycle control
   - Log environmental conditions hourly
   - Verify chamber conditions daily
   - Replenish salt solution as needed

4. **Intermediate Measurements** (per schedule)
   - Remove specimen from chamber
   - Rinse with distilled water
   - Dry at room temperature (24 hours)
   - Perform I-V measurement
   - Visual inspection and photography
   - Corrosion rating assessment
   - Return to chamber

### 3. Final Measurements

1. **Post-Test Conditioning**
   - Remove from chamber
   - Rinse thoroughly with distilled water
   - Dry at room temperature for 24 hours

2. **Final I-V Measurement**
   - Measure I-V curve at STC
   - Calculate power degradation
   - Compare to initial measurements

3. **Final Visual Inspection**
   - Comprehensive photography
   - Corrosion rating (0-5 scale)
   - Document affected areas
   - Note any delamination or damage

4. **Insulation Testing**
   - Measure insulation resistance
   - Verify >40 MΩ requirement
   - Document any failures

## Measurements and Data Collection

### 1. Environmental Monitoring

**Frequency**: Continuous (logged hourly)

- Chamber temperature (°C)
- Relative humidity (%)
- Salt concentration (% NaCl) - daily verification
- Spray rate (mL/h/80cm²) - daily verification

### 2. I-V Curve Measurements

**Standard Test Conditions (STC)**:
- Irradiance: 1000 W/m²
- Cell Temperature: 25°C
- Spectral Distribution: AM 1.5

**Measurement Points**:
| Time Point | Purpose |
|------------|---------|
| 0 hours | Initial baseline |
| 60 hours | Level 1 checkpoint |
| 120 hours | Level 2 checkpoint |
| 180 hours | Mid-test assessment |
| 240 hours | Level 3 final (default) |
| 480 hours | Level 4 final |
| 840 hours | Level 5 final |

**Recorded Parameters**:
- Complete I-V curve (voltage/current pairs)
- Maximum power (Pmax)
- Open circuit voltage (Voc)
- Short circuit current (Isc)
- Fill factor (FF)
- Power degradation (%)

### 3. Visual Inspection

**IEC 61701 Corrosion Rating Scale**:

| Rating | Description | Affected Area |
|--------|-------------|---------------|
| 0 | No corrosion | 0% |
| 1 | Slight corrosion | <1% |
| 2 | Light corrosion | 1-5% |
| 3 | Moderate corrosion | 5-25% |
| 4 | Heavy corrosion | 25-50% |
| 5 | Severe corrosion | >50% |

**Documentation**:
- High-resolution photographs (min 1920x1080)
- Corrosion location mapping
- Affected area percentage
- Notes on progression

## Quality Control

### Critical Parameters (Continuous Monitoring)

1. **Temperature**: 35 ± 1°C
   - **Action if OOR**: Adjust chamber setpoint
   - **Failure Criteria**: >2 hours outside range per cycle

2. **Humidity**: 95 ± 2%
   - **Action if OOR**: Check water supply and heating
   - **Failure Criteria**: >2 hours outside range per cycle

3. **Salt Concentration**: 5.0 ± 0.5% NaCl
   - **Action if OOR**: Prepare new solution
   - **Failure Criteria**: Daily verification outside range

### Quality Checks (Daily)

- Verify spray collector rate: 1.0-2.0 mL/h/80cm²
- Check solution pH: 6.5-7.2
- Inspect nozzles for clogging
- Review environmental data logs
- Verify chamber door seal integrity

### Data Quality

- I-V measurements within ±2% repeatability
- Image quality sufficient for corrosion assessment
- Complete environmental log (no gaps >1 hour)
- Traceability of all measurements

## Calculations

### 1. Power Degradation

```
Degradation (%) = ((Pmax_initial - Pmax_final) / Pmax_initial) × 100
```

### 2. Fill Factor

```
FF (%) = (Pmax / (Voc × Isc)) × 100
```

### 3. Corrosion Rate (if applicable)

```
CR = (Mass_initial - Mass_final) / (Area × Time)
```

## Pass/Fail Criteria (IEC 61701)

### Pass Requirements

✅ **All of the following must be met**:

1. **Power Degradation**: ≤ 5%
2. **Corrosion Rating**: ≤ 2 (light corrosion)
3. **No Delamination**: Encapsulant and backsheet intact
4. **No Electrical Failure**: Insulation resistance >40 MΩ
5. **No Broken Cells**: Visual inspection shows no cracked cells
6. **Environmental QC**: >95% of time within specifications

### Fail Criteria

❌ **Any of the following**:

1. Power degradation >5%
2. Corrosion rating >2
3. Delamination of encapsulant or backsheet
4. Insulation resistance <40 MΩ
5. Broken or cracked cells
6. Open circuit or ground fault
7. Major QC deviations (>5% time outside specs)

## Reporting Requirements

### Mandatory Report Sections

1. **Test Summary**
   - Specimen identification
   - Test parameters and severity level
   - Start/end dates
   - Operator information

2. **Environmental Conditions Log**
   - Time-series temperature data
   - Time-series humidity data
   - Salt concentration verification log
   - QC deviations and corrective actions

3. **I-V Curve Analysis**
   - Initial and final I-V curves (overlaid)
   - Power degradation progression chart
   - Voc, Isc, FF progression
   - Tabular summary of all measurements

4. **Visual Inspection Results**
   - Initial and final photographs
   - Intermediate inspection images
   - Corrosion rating progression
   - Affected area mapping

5. **Quality Control Summary**
   - Environmental stability statistics
   - QC check results
   - Deviations and resolutions

6. **Pass/Fail Determination**
   - Criteria evaluation
   - Final determination with justification
   - Recommendations

### Optional Report Sections

- Raw data tables
- Statistical analysis
- Comparison to previous tests
- Material composition analysis
- Cross-section microscopy (if performed)

## Safety Considerations

### Hazards

- **Chemical**: Salt solution (mild irritant)
- **Electrical**: High voltage from modules
- **Physical**: Chamber heat and humidity

### Precautions

- Wear safety glasses when handling salt solution
- Use insulated tools for electrical measurements
- Allow chamber to cool before opening
- Ensure proper ventilation
- Ground all equipment properly

### Emergency Procedures

- **Salt Solution Spill**: Rinse with water, neutralize if needed
- **Electrical Shock**: Disconnect power, render first aid
- **Chamber Malfunction**: Emergency stop, allow cooling

## Troubleshooting

| Issue | Possible Cause | Resolution |
|-------|----------------|------------|
| Temperature unstable | Heater malfunction | Check heater, verify thermostat |
| Low humidity | Water supply issue | Refill reservoir, check pump |
| Salt buildup on nozzles | Concentration too high | Flush system, verify solution |
| Inconsistent I-V data | Irradiance variation | Calibrate solar simulator |
| Chamber condensation | Poor sealing | Check door gasket, verify vents |

## References

### Standards

- **IEC 61701:2020**: Photovoltaic (PV) modules - Salt mist corrosion testing
- **ASTM B117-19**: Standard Practice for Operating Salt Spray (Fog) Apparatus
- **IEC 61215-2:2016**: Terrestrial photovoltaic (PV) modules - Design qualification and type approval
- **ISO 12944**: Paints and varnishes - Corrosion protection of steel structures by protective paint systems

### Related Documents

- IEC 61730: PV module safety qualification
- IEC 60068-2-52: Environmental testing - Salt mist
- ASTM G85: Modified salt spray testing

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-11-14 | ASA | Initial release |

## Appendices

### Appendix A: Salt Solution Preparation

1. Use distilled or deionized water
2. Dissolve 50 ± 5 g reagent grade NaCl per liter
3. Filter through 0.45 μm filter
4. Verify pH 6.5-7.2 (adjust with HCl or NaOH if needed)
5. Check specific gravity: 1.029-1.036 at 25°C
6. Prepare fresh solution weekly

### Appendix B: Chamber Calibration

- Temperature calibration: Annually
- Humidity sensor calibration: Semi-annually
- Spray rate verification: Monthly
- pH meter calibration: Before each test

### Appendix C: Data Management

- All data stored in SQLite/PostgreSQL database
- Automatic backup daily
- Image files stored with test ID reference
- Export capabilities: PDF, Excel, JSON, HTML
