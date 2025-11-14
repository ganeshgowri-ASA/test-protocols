"""
PVTP-049: Warranty Claim Testing & Documentation Handler
Data processing and analysis for warranty claim validation
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
import json
from enum import Enum


class FailureMode(Enum):
    """Enumeration of common PV module failure modes"""
    CELL_CRACK = "cell_crack"
    DISCOLORATION = "discoloration"
    DELAMINATION = "delamination"
    HOTSPOT = "hotspot"
    JUNCTION_BOX = "junction_box_failure"
    BACKSHEET_DAMAGE = "backsheet_damage"
    FRAME_DAMAGE = "frame_damage"
    GLASS_BREAKAGE = "glass_breakage"
    PID = "potential_induced_degradation"
    SOLDER_BOND = "solder_bond_failure"
    BYPASS_DIODE = "bypass_diode_failure"


class RootCause(Enum):
    """Root cause classification"""
    MANUFACTURING_DEFECT = "manufacturing_defect"
    MATERIAL_DEFECT = "material_defect"
    DESIGN_DEFECT = "design_defect"
    INSTALLATION_ERROR = "installation_error"
    ENVIRONMENTAL_DAMAGE = "environmental_damage"
    NORMAL_WEAR = "normal_wear"
    ELECTRICAL_OVERSTRESS = "electrical_overstress"
    MECHANICAL_STRESS = "mechanical_stress"


class WarrantyClaimHandler:
    """Handler for warranty claim testing and documentation"""

    def __init__(self, protocol_config: Dict):
        self.config = protocol_config
        self.results = {}
        self.defects = []
        self.evidence = []

    def process_initial_documentation(self, module_info: Dict,
                                     field_data: Dict) -> Dict[str, Any]:
        """Process initial module documentation and field data"""
        doc_record = {
            'timestamp': datetime.now().isoformat(),
            'case_id': self._generate_case_id(module_info),
            'module_info': {
                'serial_number': module_info.get('serial_number'),
                'manufacturer': module_info.get('manufacturer'),
                'model': module_info.get('model'),
                'nameplate_power': module_info.get('nameplate_power'),
                'manufacture_date': module_info.get('manufacture_date'),
                'installation_date': field_data.get('installation_date'),
                'age_years': self._calculate_age(
                    field_data.get('installation_date')
                )
            },
            'field_conditions': {
                'location': field_data.get('location'),
                'system_size': field_data.get('system_size'),
                'string_position': field_data.get('string_position'),
                'tilt_angle': field_data.get('tilt_angle'),
                'azimuth': field_data.get('azimuth'),
                'claimed_issue': field_data.get('claimed_issue')
            },
            'receipt_condition': {
                'packaging': field_data.get('packaging_condition'),
                'visible_damage': field_data.get('visible_damage', []),
                'photos_received': field_data.get('photos_count', 0)
            }
        }

        self.results['documentation'] = doc_record
        return doc_record

    def analyze_visual_inspection(self, inspection_data: Dict) -> Dict[str, Any]:
        """Analyze visual inspection findings"""
        defects_found = []

        # Process each defect type
        for defect_type, findings in inspection_data.items():
            if findings.get('present', False):
                defect = {
                    'type': defect_type,
                    'severity': findings.get('severity', 1),
                    'location': findings.get('location', []),
                    'area_affected': findings.get('area_percent', 0),
                    'description': findings.get('description', ''),
                    'likely_cause': self._assess_defect_cause(
                        defect_type, findings
                    )
                }
                defects_found.append(defect)

        # Calculate overall severity score
        severity_score = self._calculate_severity_score(defects_found)

        analysis = {
            'defects_found': defects_found,
            'defect_count': len(defects_found),
            'severity_score': severity_score,
            'safety_concern': self._check_safety_concern(defects_found),
            'warranty_relevant': self._check_warranty_relevance(defects_found)
        }

        self.defects = defects_found
        self.results['visual_inspection'] = analysis
        return analysis

    def process_el_imaging(self, el_images: Dict) -> Dict[str, Any]:
        """Process electroluminescence imaging data"""
        analysis = {
            'images_captured': len(el_images.get('images', [])),
            'current_levels': el_images.get('current_levels', []),
            'findings': {
                'cell_cracks': {
                    'detected': el_images.get('cracks_detected', False),
                    'count': el_images.get('crack_count', 0),
                    'severity': el_images.get('crack_severity', 'None'),
                    'pattern': el_images.get('crack_pattern', 'N/A')
                },
                'inactive_areas': {
                    'detected': el_images.get('inactive_areas', False),
                    'percentage': el_images.get('inactive_percent', 0)
                },
                'shunts': {
                    'detected': el_images.get('shunts_detected', False),
                    'count': el_images.get('shunt_count', 0)
                },
                'cell_mismatch': {
                    'detected': el_images.get('mismatch_detected', False),
                    'variation': el_images.get('brightness_variation', 0)
                }
            },
            'power_loss_estimate': self._estimate_power_loss_from_el(
                el_images
            )
        }

        self.results['el_imaging'] = analysis
        return analysis

    def process_ir_thermography(self, ir_data: Dict) -> Dict[str, Any]:
        """Process infrared thermography data"""
        temp_profile = ir_data.get('temperature_data', [])

        if temp_profile:
            temps = np.array(temp_profile)
            avg_temp = np.mean(temps)
            max_temp = np.max(temps)
            std_temp = np.std(temps)

            # Detect hotspots (>15°C above average)
            hotspot_threshold = avg_temp + 15
            hotspots = temps[temps > hotspot_threshold]

            analysis = {
                'average_temperature': float(avg_temp),
                'maximum_temperature': float(max_temp),
                'temperature_std': float(std_temp),
                'hotspot_detected': len(hotspots) > 0,
                'hotspot_count': len(hotspots),
                'hotspot_severity': self._classify_hotspot_severity(
                    max_temp - avg_temp
                ),
                'hotspot_locations': ir_data.get('hotspot_locations', []),
                'bypass_diode_check': ir_data.get('diode_temperature', None),
                'junction_box_temperature': ir_data.get('jbox_temperature', None)
            }
        else:
            analysis = {
                'error': 'No temperature data available'
            }

        self.results['ir_thermography'] = analysis
        return analysis

    def analyze_electrical_performance(self, iv_data: pd.DataFrame,
                                      nameplate_power: float) -> Dict[str, Any]:
        """Analyze electrical performance from IV curve"""
        # Extract key parameters
        pmax = iv_data['power'].max()
        voc = iv_data['voltage'].max()
        isc = iv_data['current'].max()

        # Find MPP
        mpp_idx = iv_data['power'].idxmax()
        vmpp = iv_data.loc[mpp_idx, 'voltage']
        impp = iv_data.loc[mpp_idx, 'current']

        # Calculate fill factor
        ff = (vmpp * impp) / (voc * isc) if (voc * isc) > 0 else 0

        # Calculate degradation
        degradation_percent = ((nameplate_power - pmax) / nameplate_power) * 100

        # Analyze curve shape
        curve_quality = self._analyze_curve_quality(iv_data)

        analysis = {
            'measured_power': float(pmax),
            'nameplate_power': float(nameplate_power),
            'power_ratio': float(pmax / nameplate_power) if nameplate_power > 0 else 0,
            'degradation_percent': float(degradation_percent),
            'voc': float(voc),
            'isc': float(isc),
            'vmpp': float(vmpp),
            'impp': float(impp),
            'fill_factor': float(ff),
            'curve_quality': curve_quality,
            'series_resistance': self._estimate_series_resistance(iv_data),
            'shunt_resistance': self._estimate_shunt_resistance(iv_data)
        }

        self.results['electrical_performance'] = analysis
        return analysis

    def perform_root_cause_analysis(self) -> Dict[str, Any]:
        """Perform comprehensive root cause analysis"""
        # Collect all evidence
        evidence_items = []

        # Visual defects
        if self.defects:
            for defect in self.defects:
                evidence_items.append({
                    'source': 'visual_inspection',
                    'type': defect['type'],
                    'weight': 0.8,
                    'cause_indicators': defect.get('likely_cause', [])
                })

        # EL imaging findings
        if 'el_imaging' in self.results:
            el_findings = self.results['el_imaging']['findings']
            if el_findings['cell_cracks']['detected']:
                evidence_items.append({
                    'source': 'el_imaging',
                    'type': 'cell_cracks',
                    'weight': 0.9,
                    'cause_indicators': self._interpret_crack_pattern(
                        el_findings['cell_cracks']['pattern']
                    )
                })

        # IR hotspots
        if 'ir_thermography' in self.results:
            if self.results['ir_thermography'].get('hotspot_detected'):
                evidence_items.append({
                    'source': 'ir_thermography',
                    'type': 'hotspot',
                    'weight': 0.85,
                    'cause_indicators': ['bypass_diode_failure', 'cell_mismatch']
                })

        # Electrical performance
        if 'electrical_performance' in self.results:
            perf = self.results['electrical_performance']
            if perf['fill_factor'] < 0.70:
                evidence_items.append({
                    'source': 'electrical',
                    'type': 'low_fill_factor',
                    'weight': 0.75,
                    'cause_indicators': ['series_resistance', 'shunt_paths']
                })

        # Determine most likely root cause
        root_cause_scores = self._score_root_causes(evidence_items)
        primary_root_cause = max(root_cause_scores, key=root_cause_scores.get)

        # Build 5-Why analysis
        five_why = self._generate_five_why(primary_root_cause, evidence_items)

        rca = {
            'primary_root_cause': primary_root_cause,
            'confidence_level': root_cause_scores[primary_root_cause],
            'contributing_factors': [
                cause for cause, score in root_cause_scores.items()
                if score > 0.3 and cause != primary_root_cause
            ],
            'evidence_summary': evidence_items,
            'five_why_analysis': five_why,
            'fishbone_factors': self._generate_fishbone_factors(evidence_items),
            'preventive_actions': self._recommend_preventive_actions(
                primary_root_cause
            )
        }

        self.results['root_cause_analysis'] = rca
        return rca

    def determine_warranty_validity(self, warranty_terms: Dict) -> Dict[str, Any]:
        """Determine warranty claim validity"""
        if 'root_cause_analysis' not in self.results:
            self.perform_root_cause_analysis()

        root_cause = self.results['root_cause_analysis']['primary_root_cause']
        confidence = self.results['root_cause_analysis']['confidence_level']

        # Check if within warranty period
        module_age = self.results['documentation']['module_info']['age_years']
        product_warranty_years = warranty_terms.get('product_warranty_years', 12)
        performance_warranty_years = warranty_terms.get('performance_warranty_years', 25)

        # Determine coverage type
        if root_cause in ['manufacturing_defect', 'material_defect', 'design_defect']:
            if module_age <= product_warranty_years:
                coverage = 'full_product_warranty'
                validity = 'valid'
            else:
                coverage = 'none'
                validity = 'invalid_out_of_warranty'
        elif root_cause == 'normal_wear':
            # Check performance warranty
            if 'electrical_performance' in self.results:
                degradation = self.results['electrical_performance']['degradation_percent']
                expected_degradation = self._calculate_expected_degradation(
                    module_age, warranty_terms.get('degradation_rate', 0.5)
                )

                if degradation > expected_degradation + 3:  # +3% tolerance
                    if module_age <= performance_warranty_years:
                        coverage = 'performance_warranty'
                        validity = 'valid'
                    else:
                        coverage = 'none'
                        validity = 'invalid_out_of_warranty'
                else:
                    coverage = 'none'
                    validity = 'invalid_within_spec'
            else:
                coverage = 'unknown'
                validity = 'requires_further_testing'
        else:
            # Installation error, environmental damage, etc.
            coverage = 'none'
            validity = 'invalid_excluded_cause'

        determination = {
            'validity': validity,
            'coverage_type': coverage,
            'confidence_level': confidence,
            'root_cause': root_cause,
            'module_age_years': module_age,
            'within_product_warranty': module_age <= product_warranty_years,
            'within_performance_warranty': module_age <= performance_warranty_years,
            'recommendation': self._generate_warranty_recommendation(
                validity, coverage, confidence, root_cause
            ),
            'required_actions': self._determine_required_actions(
                validity, coverage
            )
        }

        self.results['warranty_determination'] = determination
        return determination

    def _generate_case_id(self, module_info: Dict) -> str:
        """Generate unique case ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        serial = module_info.get('serial_number', 'UNKNOWN')[:8]
        return f"WC-{timestamp}-{serial}"

    def _calculate_age(self, installation_date: str) -> float:
        """Calculate module age in years"""
        if not installation_date:
            return 0.0

        try:
            install_dt = datetime.fromisoformat(installation_date)
            age_days = (datetime.now() - install_dt).days
            return age_days / 365.25
        except:
            return 0.0

    def _assess_defect_cause(self, defect_type: str,
                            findings: Dict) -> List[str]:
        """Assess likely causes for a defect"""
        cause_map = {
            'cell_cracks': ['mechanical_stress', 'thermal_cycling', 'manufacturing_defect'],
            'discoloration': ['UV_exposure', 'moisture_ingress', 'EVA_degradation'],
            'delamination': ['adhesion_failure', 'moisture_ingress', 'material_defect'],
            'hotspot': ['bypass_diode_failure', 'cell_mismatch', 'partial_shading'],
            'junction_box_failure': ['water_ingress', 'connector_issue', 'manufacturing_defect'],
            'backsheet_damage': ['UV_degradation', 'mechanical_damage', 'material_defect']
        }

        return cause_map.get(defect_type, ['unknown'])

    def _calculate_severity_score(self, defects: List[Dict]) -> float:
        """Calculate overall severity score (0-100)"""
        if not defects:
            return 0.0

        total_score = 0
        for defect in defects:
            severity = defect.get('severity', 1)
            area = defect.get('area_affected', 0)

            # Weight by severity and area
            defect_score = (severity * 10) + (area * 0.5)
            total_score += defect_score

        # Normalize to 0-100 scale
        return min(total_score / len(defects), 100)

    def _check_safety_concern(self, defects: List[Dict]) -> bool:
        """Check if any defects pose safety concerns"""
        safety_critical = [
            'delamination',
            'backsheet_damage',
            'junction_box_failure',
            'glass_breakage'
        ]

        for defect in defects:
            if defect['type'] in safety_critical:
                if defect.get('severity', 0) >= 3:
                    return True

        return False

    def _check_warranty_relevance(self, defects: List[Dict]) -> bool:
        """Check if defects are warranty-relevant"""
        for defect in defects:
            if defect.get('likely_cause'):
                causes = defect['likely_cause']
                if any('defect' in cause for cause in causes):
                    return True

        return False

    def _estimate_power_loss_from_el(self, el_data: Dict) -> float:
        """Estimate power loss from EL imaging"""
        power_loss = 0.0

        # Inactive areas
        inactive_percent = el_data.get('inactive_percent', 0)
        power_loss += inactive_percent

        # Cell cracks (estimated impact)
        crack_count = el_data.get('crack_count', 0)
        crack_severity = el_data.get('crack_severity', 'None')

        if crack_severity == 'Severe':
            power_loss += crack_count * 0.5
        elif crack_severity == 'Moderate':
            power_loss += crack_count * 0.2
        elif crack_severity == 'Minor':
            power_loss += crack_count * 0.05

        return min(power_loss, 100)

    def _classify_hotspot_severity(self, temp_diff: float) -> str:
        """Classify hotspot severity"""
        if temp_diff > 30:
            return 'Severe'
        elif temp_diff > 20:
            return 'Moderate'
        elif temp_diff > 15:
            return 'Minor'
        else:
            return 'None'

    def _analyze_curve_quality(self, iv_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze IV curve quality"""
        # Check for steps or irregularities
        power = iv_data['power'].values
        voltage = iv_data['voltage'].values

        # Calculate smoothness
        power_diff = np.diff(power)
        smoothness = 1 - (np.std(power_diff) / np.mean(np.abs(power_diff)))

        return {
            'smoothness_score': float(smoothness),
            'has_steps': bool(np.any(np.abs(power_diff) > np.std(power_diff) * 3)),
            'quality_rating': 'Good' if smoothness > 0.8 else 'Fair' if smoothness > 0.6 else 'Poor'
        }

    def _estimate_series_resistance(self, iv_data: pd.DataFrame) -> float:
        """Estimate series resistance from IV curve"""
        # Simplified estimation from slope near Voc
        near_voc = iv_data[iv_data['voltage'] > iv_data['voltage'].max() * 0.9]
        if len(near_voc) > 2:
            v = near_voc['voltage'].values
            i = near_voc['current'].values
            rs = -np.polyfit(i, v, 1)[0]
            return float(max(rs, 0))
        return 0.0

    def _estimate_shunt_resistance(self, iv_data: pd.DataFrame) -> float:
        """Estimate shunt resistance from IV curve"""
        # Simplified estimation from slope near Isc
        near_isc = iv_data[iv_data['voltage'] < iv_data['voltage'].max() * 0.1]
        if len(near_isc) > 2:
            v = near_isc['voltage'].values
            i = near_isc['current'].values
            rsh = np.polyfit(v, i, 1)[0]
            return float(1/rsh if rsh > 0 else float('inf'))
        return float('inf')

    def _interpret_crack_pattern(self, pattern: str) -> List[str]:
        """Interpret crack pattern to determine likely cause"""
        pattern_causes = {
            'parallel': ['thermal_cycling', 'manufacturing_stress'],
            'dendritic': ['mechanical_impact', 'shipping_damage'],
            'random': ['thermal_cycling', 'normal_aging'],
            'grid_aligned': ['soldering_stress', 'manufacturing_defect']
        }

        return pattern_causes.get(pattern.lower(), ['unknown'])

    def _score_root_causes(self, evidence_items: List[Dict]) -> Dict[str, float]:
        """Score potential root causes based on evidence"""
        scores = {cause.value: 0.0 for cause in RootCause}

        for evidence in evidence_items:
            weight = evidence.get('weight', 0.5)
            causes = evidence.get('cause_indicators', [])

            for cause in causes:
                if cause in scores:
                    scores[cause] += weight

        # Normalize scores
        max_score = max(scores.values()) if scores.values() else 1.0
        if max_score > 0:
            scores = {k: v/max_score for k, v in scores.items()}

        return scores

    def _generate_five_why(self, root_cause: str,
                          evidence: List[Dict]) -> List[str]:
        """Generate 5-Why analysis"""
        # Simplified 5-Why generator
        why_templates = {
            'manufacturing_defect': [
                f"Why did the module fail? {root_cause}",
                "Why was there a manufacturing defect? Process control issue",
                "Why was there a process control issue? Insufficient quality checks",
                "Why were quality checks insufficient? Lack of standardization",
                "Why was there lack of standardization? Inadequate procedures"
            ],
            'material_defect': [
                f"Why did the module fail? {root_cause}",
                "Why was there a material defect? Supplier material issue",
                "Why was there a supplier issue? Inadequate incoming inspection",
                "Why was inspection inadequate? Missing material specifications",
                "Why were specifications missing? Poor supplier management"
            ]
        }

        return why_templates.get(root_cause, [f"Analysis required for {root_cause}"])

    def _generate_fishbone_factors(self, evidence: List[Dict]) -> Dict[str, List[str]]:
        """Generate fishbone diagram factors"""
        return {
            'Materials': ['Cell quality', 'Encapsulant', 'Backsheet', 'Solder'],
            'Methods': ['Manufacturing process', 'Quality control', 'Testing'],
            'Machines': ['Laminator', 'Soldering equipment', 'Handling'],
            'Environment': ['Temperature', 'Humidity', 'UV exposure'],
            'Measurement': ['Test accuracy', 'Calibration', 'Procedures'],
            'People': ['Training', 'Experience', 'Procedures']
        }

    def _recommend_preventive_actions(self, root_cause: str) -> List[str]:
        """Recommend preventive actions"""
        actions = {
            'manufacturing_defect': [
                'Review manufacturing process controls',
                'Enhance quality inspection procedures',
                'Implement statistical process control',
                'Conduct operator training'
            ],
            'material_defect': [
                'Review supplier qualification',
                'Enhance incoming material inspection',
                'Implement material traceability',
                'Conduct supplier audits'
            ],
            'design_defect': [
                'Review module design',
                'Conduct design FMEA',
                'Implement design changes',
                'Validate with accelerated testing'
            ]
        }

        return actions.get(root_cause, ['Conduct further investigation'])

    def _calculate_expected_degradation(self, age_years: float,
                                       degradation_rate: float) -> float:
        """Calculate expected degradation"""
        # Year 1 LID
        lid = 2.0

        if age_years <= 1:
            return lid * age_years
        else:
            return lid + (degradation_rate * (age_years - 1))

    def _generate_warranty_recommendation(self, validity: str, coverage: str,
                                         confidence: float, root_cause: str) -> str:
        """Generate warranty recommendation"""
        if validity == 'valid':
            if confidence > 0.8:
                return f"Approve warranty claim. Clear evidence of {root_cause}."
            else:
                return f"Approve warranty claim with reservation. Additional verification recommended."
        elif validity == 'invalid_out_of_warranty':
            return "Deny claim. Module is outside warranty period."
        elif validity == 'invalid_within_spec':
            return "Deny claim. Module performance is within warranty specifications."
        elif validity == 'invalid_excluded_cause':
            return f"Deny claim. Failure cause ({root_cause}) is excluded from warranty coverage."
        else:
            return "Cannot determine validity. Additional testing required."

    def _determine_required_actions(self, validity: str,
                                   coverage: str) -> List[str]:
        """Determine required actions"""
        if validity == 'valid':
            if coverage == 'full_product_warranty':
                return ['Authorize module replacement', 'Issue RMA', 'Investigate batch']
            elif coverage == 'performance_warranty':
                return ['Authorize prorated replacement', 'Issue credit', 'Monitor fleet']
        elif validity.startswith('invalid'):
            return ['Notify customer of denial', 'Provide detailed explanation']

        return ['Conduct additional testing', 'Request more information']

    def generate_report_data(self) -> Dict[str, Any]:
        """Compile all data for report generation"""
        return {
            'protocol_id': 'PVTP-049',
            'test_date': datetime.now().isoformat(),
            'case_id': self.results.get('documentation', {}).get('case_id'),
            'results': self.results,
            'summary': self._generate_summary()
        }

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate executive summary"""
        warranty_det = self.results.get('warranty_determination', {})

        return {
            'case_id': self.results.get('documentation', {}).get('case_id'),
            'validity': warranty_det.get('validity', 'Unknown'),
            'root_cause': warranty_det.get('root_cause', 'Unknown'),
            'recommendation': warranty_det.get('recommendation', 'No recommendation'),
            'defect_count': len(self.defects),
            'safety_concern': self._check_safety_concern(self.defects)
        }
