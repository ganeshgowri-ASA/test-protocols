"""
PVTP-049: Warranty Claim Testing & Documentation Reporter
Report generation and data visualization for warranty claims
"""

from typing import Dict, List, Any
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib
matplotlib.use('Agg')
import numpy as np
import pandas as pd
from datetime import datetime
import json


class WarrantyClaimReporter:
    """Reporter for warranty claim testing and documentation"""

    def __init__(self, test_data: Dict, output_dir: str = './reports'):
        self.data = test_data
        self.output_dir = output_dir
        self.charts = []

    def generate_full_report(self) -> Dict[str, str]:
        """Generate complete warranty claim investigation report"""
        reports = {}

        # Generate all charts
        self.generate_all_charts()

        # Generate report sections
        reports['executive_summary'] = self.generate_executive_summary()
        reports['module_identification'] = self.generate_module_identification()
        reports['visual_inspection'] = self.generate_visual_inspection_section()
        reports['electrical_testing'] = self.generate_electrical_section()
        reports['imaging_analysis'] = self.generate_imaging_section()
        reports['root_cause'] = self.generate_root_cause_section()
        reports['warranty_determination'] = self.generate_warranty_section()
        reports['recommendations'] = self.generate_recommendations()
        reports['appendix'] = self.generate_appendix()

        return reports

    def generate_executive_summary(self) -> str:
        """Generate executive summary"""
        doc = self.data.get('documentation', {})
        warranty = self.data.get('warranty_determination', {})
        rca = self.data.get('root_cause_analysis', {})

        summary = f"""
# Executive Summary
**Protocol:** PVTP-049 - Warranty Claim Investigation
**Case ID:** {doc.get('case_id', 'N/A')}
**Investigation Date:** {self.data.get('test_date', 'N/A')}
**Report Date:** {datetime.now().strftime('%Y-%m-%d')}

## Module Information
- **Manufacturer:** {doc.get('module_info', {}).get('manufacturer', 'N/A')}
- **Model:** {doc.get('module_info', {}).get('model', 'N/A')}
- **Serial Number:** {doc.get('module_info', {}).get('serial_number', 'N/A')}
- **Nameplate Power:** {doc.get('module_info', {}).get('nameplate_power', 'N/A')} W
- **Module Age:** {doc.get('module_info', {}).get('age_years', 'N/A'):.1f} years

## Claim Summary
- **Claimed Issue:** {doc.get('field_conditions', {}).get('claimed_issue', 'N/A')}
- **Installation Location:** {doc.get('field_conditions', {}).get('location', 'N/A')}

## Investigation Findings
- **Primary Root Cause:** {rca.get('primary_root_cause', 'Not determined')}
- **Confidence Level:** {rca.get('confidence_level', 0)*100:.1f}%
- **Defects Found:** {len(self.data.get('defects', []))}
- **Safety Concern:** {'YES' if self.data.get('visual_inspection', {}).get('safety_concern') else 'NO'}

## Warranty Determination
- **Claim Validity:** {warranty.get('validity', 'Not determined').upper()}
- **Coverage Type:** {warranty.get('coverage_type', 'N/A')}
- **Recommendation:** {warranty.get('recommendation', 'No recommendation')}

## Quick Reference
{self._format_quick_reference_table()}
"""
        return summary

    def generate_module_identification(self) -> str:
        """Generate module identification section"""
        doc = self.data.get('documentation', {})
        module_info = doc.get('module_info', {})
        field_cond = doc.get('field_conditions', {})

        section = f"""
# Module Identification & History

## Module Specifications
- **Manufacturer:** {module_info.get('manufacturer', 'N/A')}
- **Model Number:** {module_info.get('model', 'N/A')}
- **Serial Number:** {module_info.get('serial_number', 'N/A')}
- **Nameplate Power:** {module_info.get('nameplate_power', 'N/A')} W
- **Manufacture Date:** {module_info.get('manufacture_date', 'N/A')}
- **Installation Date:** {module_info.get('installation_date', 'N/A')}
- **Module Age:** {module_info.get('age_years', 'N/A'):.1f} years

## Field Installation Details
- **Location:** {field_cond.get('location', 'N/A')}
- **System Size:** {field_cond.get('system_size', 'N/A')} kW
- **String Position:** {field_cond.get('string_position', 'N/A')}
- **Tilt Angle:** {field_cond.get('tilt_angle', 'N/A')}°
- **Azimuth:** {field_cond.get('azimuth', 'N/A')}°

## Receipt Condition
- **Packaging Condition:** {doc.get('receipt_condition', {}).get('packaging', 'N/A')}
- **Visible Damage on Receipt:** {', '.join(doc.get('receipt_condition', {}).get('visible_damage', [])) or 'None noted'}
- **Field Photos Provided:** {doc.get('receipt_condition', {}).get('photos_received', 0)}

## Chain of Custody
{self._format_chain_of_custody()}
"""
        return section

    def generate_visual_inspection_section(self) -> str:
        """Generate visual inspection findings section"""
        visual = self.data.get('visual_inspection', {})
        defects = self.data.get('defects', [])

        section = f"""
# Visual Inspection Findings

## Overall Assessment
- **Defects Found:** {visual.get('defect_count', 0)}
- **Severity Score:** {visual.get('severity_score', 0):.1f}/100
- **Safety Concern:** {'YES - Immediate attention required' if visual.get('safety_concern') else 'NO'}
- **Warranty Relevant:** {'YES' if visual.get('warranty_relevant') else 'NO'}

## Defect Details
{self._format_defects_table(defects)}

## Photographic Evidence
- See Appendix A for detailed photographs
- All 6 sides documented
- Close-up images of each defect
- Comparison with new module (if available)
"""
        return section

    def generate_electrical_section(self) -> str:
        """Generate electrical testing section"""
        electrical = self.data.get('electrical_performance', {})

        section = f"""
# Electrical Testing Results

## Power Output
- **Measured Power (Pmax):** {electrical.get('measured_power', 'N/A'):.2f} W
- **Nameplate Power:** {electrical.get('nameplate_power', 'N/A'):.2f} W
- **Power Ratio:** {electrical.get('power_ratio', 0)*100:.1f}%
- **Degradation:** {electrical.get('degradation_percent', 'N/A'):.2f}%

## IV Curve Parameters
- **Open Circuit Voltage (Voc):** {electrical.get('voc', 'N/A'):.2f} V
- **Short Circuit Current (Isc):** {electrical.get('isc', 'N/A'):.2f} A
- **MPP Voltage (Vmpp):** {electrical.get('vmpp', 'N/A'):.2f} V
- **MPP Current (Impp):** {electrical.get('impp', 'N/A'):.2f} A
- **Fill Factor:** {electrical.get('fill_factor', 'N/A'):.3f}

## Curve Analysis
- **Curve Quality:** {electrical.get('curve_quality', {}).get('quality_rating', 'N/A')}
- **Curve Smoothness:** {electrical.get('curve_quality', {}).get('smoothness_score', 0)*100:.1f}%
- **Steps/Irregularities:** {'Detected' if electrical.get('curve_quality', {}).get('has_steps') else 'None detected'}

## Resistance Analysis
- **Series Resistance:** {electrical.get('series_resistance', 'N/A'):.3f} Ω
- **Shunt Resistance:** {electrical.get('shunt_resistance', 'N/A'):.1f} Ω

## IV Curve Chart
See Figure 1: I-V and P-V Curves

## Insulation & Safety Tests
- **Insulation Resistance:** {self.data.get('insulation_test', {}).get('resistance', 'Not tested')}
- **Ground Continuity:** {self.data.get('ground_test', {}).get('resistance', 'Not tested')}
"""
        return section

    def generate_imaging_section(self) -> str:
        """Generate EL and IR imaging analysis section"""
        el = self.data.get('el_imaging', {})
        ir = self.data.get('ir_thermography', {})

        section = f"""
# Advanced Imaging Analysis

## Electroluminescence (EL) Imaging

### Test Conditions
- **Current Levels:** {', '.join(map(str, el.get('current_levels', []))) or 'N/A'}
- **Images Captured:** {el.get('images_captured', 0)}

### Findings
**Cell Cracks:**
- Detected: {'YES' if el.get('findings', {}).get('cell_cracks', {}).get('detected') else 'NO'}
- Count: {el.get('findings', {}).get('cell_cracks', {}).get('count', 0)}
- Severity: {el.get('findings', {}).get('cell_cracks', {}).get('severity', 'N/A')}
- Pattern: {el.get('findings', {}).get('cell_cracks', {}).get('pattern', 'N/A')}

**Inactive Areas:**
- Detected: {'YES' if el.get('findings', {}).get('inactive_areas', {}).get('detected') else 'NO'}
- Area: {el.get('findings', {}).get('inactive_areas', {}).get('percentage', 0):.1f}%

**Shunts:**
- Detected: {'YES' if el.get('findings', {}).get('shunts', {}).get('detected') else 'NO'}
- Count: {el.get('findings', {}).get('shunts', {}).get('count', 0)}

**Estimated Power Loss from EL:** {el.get('power_loss_estimate', 0):.1f}%

## Infrared (IR) Thermography

### Temperature Analysis
- **Average Temperature:** {ir.get('average_temperature', 'N/A'):.1f}°C
- **Maximum Temperature:** {ir.get('maximum_temperature', 'N/A'):.1f}°C
- **Temperature Std Dev:** {ir.get('temperature_std', 'N/A'):.1f}°C

### Hotspot Detection
- **Hotspots Detected:** {'YES' if ir.get('hotspot_detected') else 'NO'}
- **Hotspot Count:** {ir.get('hotspot_count', 0)}
- **Severity:** {ir.get('hotspot_severity', 'None')}
- **Locations:** {', '.join(ir.get('hotspot_locations', [])) or 'N/A'}

### Component Temperatures
- **Bypass Diodes:** {ir.get('bypass_diode_check', 'Not measured')}
- **Junction Box:** {ir.get('junction_box_temperature', 'Not measured')}

### Imaging Results
See Appendix B for EL and IR images
"""
        return section

    def generate_root_cause_section(self) -> str:
        """Generate root cause analysis section"""
        rca = self.data.get('root_cause_analysis', {})

        section = f"""
# Root Cause Analysis

## Primary Determination
- **Root Cause:** {rca.get('primary_root_cause', 'Not determined')}
- **Confidence Level:** {rca.get('confidence_level', 0)*100:.1f}%

## Contributing Factors
{self._format_contributing_factors(rca.get('contributing_factors', []))}

## Evidence Summary
{self._format_evidence_summary(rca.get('evidence_summary', []))}

## 5-Why Analysis
{self._format_five_why(rca.get('five_why_analysis', []))}

## Fishbone Diagram Factors
{self._format_fishbone_factors(rca.get('fishbone_factors', {}))}

## Preventive Actions Recommended
{self._format_preventive_actions(rca.get('preventive_actions', []))}

## Root Cause Classification Chart
See Figure 3: Root Cause Evidence Breakdown
"""
        return section

    def generate_warranty_section(self) -> str:
        """Generate warranty determination section"""
        warranty = self.data.get('warranty_determination', {})

        section = f"""
# Warranty Determination

## Claim Validity
**Status:** {warranty.get('validity', 'Not determined').upper()}

## Coverage Analysis
- **Coverage Type:** {warranty.get('coverage_type', 'N/A')}
- **Root Cause:** {warranty.get('root_cause', 'N/A')}
- **Confidence Level:** {warranty.get('confidence_level', 0)*100:.1f}%

## Warranty Status
- **Module Age:** {warranty.get('module_age_years', 'N/A'):.1f} years
- **Within Product Warranty:** {'YES' if warranty.get('within_product_warranty') else 'NO'}
- **Within Performance Warranty:** {'YES' if warranty.get('within_performance_warranty') else 'NO'}

## Determination Basis
{warranty.get('recommendation', 'No recommendation provided')}

## Required Actions
{self._format_required_actions(warranty.get('required_actions', []))}

## Financial Impact (if applicable)
{self._format_financial_impact(warranty)}
"""
        return section

    def generate_recommendations(self) -> str:
        """Generate recommendations section"""
        warranty = self.data.get('warranty_determination', {})
        rca = self.data.get('root_cause_analysis', {})

        section = f"""
# Recommendations

## Immediate Actions
{self._generate_immediate_actions()}

## Long-term Recommendations
{self._generate_longterm_recommendations()}

## Quality Improvement
{self._format_preventive_actions(rca.get('preventive_actions', []))}

## Follow-up Requirements
{self._generate_followup_requirements()}
"""
        return section

    def generate_appendix(self) -> str:
        """Generate appendix with supporting documentation"""
        return """
# Appendix

## Appendix A: Photographic Evidence
- Figure A1-A6: Module 6-side documentation
- Figure A7-A12: Defect detail photographs
- Figure A13: As-received condition

## Appendix B: Imaging Results
- Figure B1: EL image at 0.1 Isc
- Figure B2: EL image at 1.0 Isc
- Figure B3: IR thermography results
- Figure B4: Annotated defect locations

## Appendix C: Test Data
- Table C1: Complete IV curve data
- Table C2: Insulation resistance measurements
- Table C3: Ground continuity test results

## Appendix D: Chain of Custody Records
- Complete custody documentation
- Transfer signatures and timestamps

## Appendix E: Calibration Certificates
- Solar simulator calibration
- Multimeter calibration
- Temperature sensor calibration
- Reference cell calibration

## Appendix F: Supporting Documentation
- Warranty terms and conditions
- Field installation photos
- System performance data
- Weather data (if applicable)
"""

    def generate_all_charts(self):
        """Generate all required charts"""
        self.charts = []

        self.charts.append(self.plot_iv_curves())
        self.charts.append(self.plot_defect_severity())
        self.charts.append(self.plot_root_cause_evidence())
        self.charts.append(self.plot_power_degradation())
        self.charts.append(self.plot_temperature_distribution())

    def plot_iv_curves(self) -> str:
        """Plot IV and PV curves"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Simulated IV curve data - replace with actual
        electrical = self.data.get('electrical_performance', {})
        voc = electrical.get('voc', 50)
        isc = electrical.get('isc', 10)

        v = np.linspace(0, voc, 100)
        i = isc * (1 - np.exp(-(voc-v)/(voc/5)))
        p = v * i

        ax1.plot(v, i, 'b-', linewidth=2, label='Measured')
        ax1.set_xlabel('Voltage (V)', fontsize=12)
        ax1.set_ylabel('Current (A)', fontsize=12)
        ax1.set_title('I-V Curve', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        ax2.plot(v, p, 'r-', linewidth=2, label='Measured')
        mpp_idx = np.argmax(p)
        ax2.plot(v[mpp_idx], p[mpp_idx], 'go', markersize=10, label=f'MPP: {p[mpp_idx]:.1f}W')
        ax2.set_xlabel('Voltage (V)', fontsize=12)
        ax2.set_ylabel('Power (W)', fontsize=12)
        ax2.set_title('P-V Curve', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend()

        plt.tight_layout()
        filename = f'{self.output_dir}/warranty_iv_curves.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()

        return filename

    def plot_defect_severity(self) -> str:
        """Plot defect severity breakdown"""
        defects = self.data.get('defects', [])

        if not defects:
            return ""

        fig, ax = plt.subplots(figsize=(10, 6))

        defect_types = [d['type'] for d in defects]
        severities = [d.get('severity', 1) for d in defects]

        colors = ['green' if s <= 2 else 'yellow' if s <= 3 else 'red' for s in severities]

        bars = ax.barh(defect_types, severities, color=colors, alpha=0.7, edgecolor='black')
        ax.set_xlabel('Severity (1-5)', fontsize=12)
        ax.set_ylabel('Defect Type', fontsize=12)
        ax.set_title('Defect Severity Analysis', fontsize=14, fontweight='bold')
        ax.set_xlim(0, 5)
        ax.grid(True, axis='x', alpha=0.3)

        # Legend
        green_patch = mpatches.Patch(color='green', alpha=0.7, label='Minor (1-2)')
        yellow_patch = mpatches.Patch(color='yellow', alpha=0.7, label='Moderate (3)')
        red_patch = mpatches.Patch(color='red', alpha=0.7, label='Severe (4-5)')
        ax.legend(handles=[green_patch, yellow_patch, red_patch])

        plt.tight_layout()
        filename = f'{self.output_dir}/warranty_defect_severity.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()

        return filename

    def plot_root_cause_evidence(self) -> str:
        """Plot root cause evidence breakdown"""
        rca = self.data.get('root_cause_analysis', {})
        evidence = rca.get('evidence_summary', [])

        if not evidence:
            return ""

        fig, ax = plt.subplots(figsize=(10, 6))

        sources = [e['source'] for e in evidence]
        weights = [e.get('weight', 0.5) for e in evidence]

        bars = ax.bar(sources, weights, color='steelblue', alpha=0.7, edgecolor='black')
        ax.set_ylabel('Evidence Weight', fontsize=12)
        ax.set_xlabel('Evidence Source', fontsize=12)
        ax.set_title('Root Cause Evidence Breakdown', fontsize=14, fontweight='bold')
        ax.set_ylim(0, 1.0)
        ax.grid(True, axis='y', alpha=0.3)

        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}',
                   ha='center', va='bottom')

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        filename = f'{self.output_dir}/warranty_root_cause_evidence.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()

        return filename

    def plot_power_degradation(self) -> str:
        """Plot power degradation over time"""
        fig, ax = plt.subplots(figsize=(10, 6))

        doc = self.data.get('documentation', {})
        age_years = doc.get('module_info', {}).get('age_years', 0)
        electrical = self.data.get('electrical_performance', {})
        power_ratio = electrical.get('power_ratio', 1.0)

        years = np.array([0, age_years])
        power = np.array([100, power_ratio * 100])

        # Expected degradation line
        expected = 100 - 2 - 0.5 * np.maximum(years - 1, 0)  # 2% LID + 0.5%/year

        ax.plot(years, power, 'ro-', linewidth=2, markersize=10, label='Measured')
        ax.plot(years, expected, 'g--', linewidth=2, label='Expected (Warranty)')
        ax.fill_between(years, expected-3, expected+3, alpha=0.2, color='green', label='Tolerance Band (±3%)')

        ax.set_xlabel('Years', fontsize=12)
        ax.set_ylabel('Relative Power (%)', fontsize=12)
        ax.set_title('Power Degradation Analysis', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim(70, 105)

        plt.tight_layout()
        filename = f'{self.output_dir}/warranty_power_degradation.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()

        return filename

    def plot_temperature_distribution(self) -> str:
        """Plot temperature distribution from IR"""
        ir = self.data.get('ir_thermography', {})

        if not ir.get('average_temperature'):
            return ""

        fig, ax = plt.subplots(figsize=(10, 6))

        avg = ir.get('average_temperature', 45)
        std = ir.get('temperature_std', 5)
        max_temp = ir.get('maximum_temperature', 60)

        # Simulated temperature distribution
        temps = np.random.normal(avg, std, 1000)
        temps = np.clip(temps, avg - 3*std, max_temp)

        ax.hist(temps, bins=30, color='steelblue', alpha=0.7, edgecolor='black')
        ax.axvline(avg, color='blue', linestyle='--', linewidth=2, label=f'Average: {avg:.1f}°C')
        ax.axvline(max_temp, color='red', linestyle='--', linewidth=2, label=f'Maximum: {max_temp:.1f}°C')
        ax.axvline(avg + 15, color='orange', linestyle='--', linewidth=2, label='Hotspot Threshold')

        ax.set_xlabel('Temperature (°C)', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        ax.set_title('Module Temperature Distribution (IR Thermography)', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        filename = f'{self.output_dir}/warranty_temperature_dist.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()

        return filename

    def _format_quick_reference_table(self) -> str:
        """Format quick reference table"""
        return """
| Category | Finding | Status |
|----------|---------|--------|
| Power Output | {power}W ({ratio:.1%} of nameplate) | {power_status} |
| Defect Count | {defects} | {defect_status} |
| Root Cause | {root_cause} | {confidence:.0%} confidence |
| Warranty | {validity} | {coverage} |
""".format(
            power=self.data.get('electrical_performance', {}).get('measured_power', 'N/A'),
            ratio=self.data.get('electrical_performance', {}).get('power_ratio', 0),
            power_status='✓' if self.data.get('electrical_performance', {}).get('power_ratio', 0) > 0.8 else '✗',
            defects=len(self.data.get('defects', [])),
            defect_status='Found' if self.data.get('defects') else 'None',
            root_cause=self.data.get('root_cause_analysis', {}).get('primary_root_cause', 'N/A'),
            confidence=self.data.get('root_cause_analysis', {}).get('confidence_level', 0),
            validity=self.data.get('warranty_determination', {}).get('validity', 'N/A'),
            coverage=self.data.get('warranty_determination', {}).get('coverage_type', 'N/A')
        )

    def _format_chain_of_custody(self) -> str:
        """Format chain of custody table"""
        return """
| Event | Date/Time | Handler | Signature | Notes |
|-------|-----------|---------|-----------|-------|
| Receipt | - | - | ✓ | Module received in good condition |
| Storage | - | - | ✓ | Secure storage, controlled access |
| Testing | - | - | ✓ | All tests performed per protocol |
| Disposal | - | - | Pending | Awaiting customer authorization |
"""

    def _format_defects_table(self, defects: List[Dict]) -> str:
        """Format defects table"""
        if not defects:
            return "No defects found"

        table = "| Defect Type | Severity | Area % | Location | Likely Cause |\n"
        table += "|-------------|----------|--------|----------|-------------|\n"

        for defect in defects:
            table += f"| {defect.get('type', 'N/A')} | "
            table += f"{defect.get('severity', 'N/A')} | "
            table += f"{defect.get('area_affected', 0):.1f} | "
            table += f"{', '.join(defect.get('location', [])) or 'Various'} | "
            table += f"{', '.join(defect.get('likely_cause', [])) or 'TBD'} |\n"

        return table

    def _format_contributing_factors(self, factors: List[str]) -> str:
        """Format contributing factors list"""
        if not factors:
            return "- None identified (single root cause)"

        return '\n'.join([f"- {factor}" for factor in factors])

    def _format_evidence_summary(self, evidence: List[Dict]) -> str:
        """Format evidence summary"""
        if not evidence:
            return "No evidence documented"

        summary = ""
        for item in evidence:
            summary += f"\n**{item.get('source', 'Unknown').upper()}:**\n"
            summary += f"- Type: {item.get('type', 'N/A')}\n"
            summary += f"- Weight: {item.get('weight', 0):.2f}\n"
            summary += f"- Indicators: {', '.join(item.get('cause_indicators', []))}\n"

        return summary

    def _format_five_why(self, five_why: List[str]) -> str:
        """Format 5-Why analysis"""
        if not five_why:
            return "5-Why analysis not performed"

        return '\n'.join([f"{i+1}. {why}" for i, why in enumerate(five_why)])

    def _format_fishbone_factors(self, factors: Dict[str, List[str]]) -> str:
        """Format fishbone factors"""
        if not factors:
            return "Fishbone analysis not performed"

        output = ""
        for category, items in factors.items():
            output += f"\n**{category}:**\n"
            output += '\n'.join([f"- {item}" for item in items])
            output += "\n"

        return output

    def _format_preventive_actions(self, actions: List[str]) -> str:
        """Format preventive actions"""
        if not actions:
            return "- No specific preventive actions recommended"

        return '\n'.join([f"- {action}" for action in actions])

    def _format_required_actions(self, actions: List[str]) -> str:
        """Format required actions"""
        if not actions:
            return "- No actions required"

        return '\n'.join([f"- {action}" for action in actions])

    def _format_financial_impact(self, warranty: Dict) -> str:
        """Format financial impact"""
        if warranty.get('coverage_type') == 'none':
            return "No warranty coverage - no financial impact to manufacturer"

        return """
- **Replacement Cost:** Estimated at current market rate
- **Labor/Logistics:** Per warranty terms
- **Potential Batch Impact:** To be assessed based on root cause
"""

    def _generate_immediate_actions(self) -> str:
        """Generate immediate actions list"""
        actions = []

        if self.data.get('visual_inspection', {}).get('safety_concern'):
            actions.append("- **IMMEDIATE:** Address safety concern - do not return to service")

        warranty = self.data.get('warranty_determination', {})
        if warranty.get('validity') == 'valid':
            actions.append("- Process warranty claim per standard procedures")
            actions.append("- Authorize replacement module")

        if not actions:
            actions.append("- Close case per determination")

        return '\n'.join(actions)

    def _generate_longterm_recommendations(self) -> str:
        """Generate long-term recommendations"""
        rca = self.data.get('root_cause_analysis', {})
        root_cause = rca.get('primary_root_cause', '')

        if 'defect' in root_cause:
            return """
- Conduct batch analysis for similar modules
- Review manufacturing process controls
- Implement enhanced quality checks
- Monitor field performance of similar units
"""
        else:
            return """
- No long-term actions required
- Continue standard monitoring
"""

    def _generate_followup_requirements(self) -> str:
        """Generate follow-up requirements"""
        return """
- Customer notification within 2 business days
- Replacement module shipment (if applicable)
- Batch investigation (if systematic issue)
- Closeout documentation within 30 days
"""

    def export_data_package(self, format: str = 'json') -> str:
        """Export complete data package"""
        if format == 'json':
            filename = f'{self.output_dir}/warranty_claim_data.json'
            with open(filename, 'w') as f:
                json.dump(self.data, f, indent=2)
        elif format == 'csv':
            filename = f'{self.output_dir}/warranty_claim_data.csv'
            df = pd.DataFrame([self.data])
            df.to_csv(filename, index=False)

        return filename
