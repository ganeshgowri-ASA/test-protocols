"""
PVTP-049: Warranty Claim Testing & Documentation Validator
Data validation and evidence verification
"""

from typing import Dict, List, Tuple, Any
import numpy as np
import pandas as pd
from datetime import datetime


class WarrantyClaimValidator:
    """Validator for warranty claim testing and documentation"""

    def __init__(self, acceptance_criteria: Dict):
        self.criteria = acceptance_criteria
        self.violations = []
        self.warnings = []

    def validate_all(self, test_data: Dict) -> Tuple[bool, List[Dict]]:
        """Run all validation checks"""
        self.violations = []
        self.warnings = []

        # Documentation validation
        self.validate_documentation(test_data.get('documentation', {}))

        # Evidence validation
        self.validate_evidence(test_data.get('evidence', {}))

        # Testing completeness
        self.validate_test_completeness(test_data)

        # Root cause analysis validation
        self.validate_root_cause_analysis(test_data.get('root_cause_analysis', {}))

        # Chain of custody
        self.validate_chain_of_custody(test_data.get('custody', {}))

        is_valid = len(self.violations) == 0
        return is_valid, self.violations

    def validate_documentation(self, doc_data: Dict) -> bool:
        """Validate initial documentation completeness"""
        all_valid = True

        # Required fields
        required_fields = [
            'case_id',
            'module_info',
            'field_conditions',
            'receipt_condition'
        ]

        for field in required_fields:
            if field not in doc_data or not doc_data[field]:
                self.violations.append({
                    'parameter': f'documentation.{field}',
                    'severity': 'CRITICAL',
                    'message': f'Required documentation field {field} is missing',
                    'measured': None,
                    'expected': 'Required'
                })
                all_valid = False

        # Module information completeness
        module_info = doc_data.get('module_info', {})
        required_module_fields = ['serial_number', 'manufacturer', 'model', 'nameplate_power']

        for field in required_module_fields:
            if field not in module_info or not module_info[field]:
                self.violations.append({
                    'parameter': f'module_info.{field}',
                    'severity': 'CRITICAL',
                    'message': f'Required module information {field} is missing',
                    'measured': None,
                    'expected': 'Required'
                })
                all_valid = False

        # Age validation
        age_years = module_info.get('age_years', 0)
        if age_years < 0:
            self.violations.append({
                'parameter': 'module_age',
                'severity': 'CRITICAL',
                'message': 'Module age cannot be negative',
                'measured': age_years,
                'expected': '>=0'
            })
            all_valid = False
        elif age_years > 50:
            self.warnings.append({
                'parameter': 'module_age',
                'severity': 'WARNING',
                'message': 'Module age seems unusually high',
                'measured': age_years,
                'expected': '<50 years'
            })

        return all_valid

    def validate_evidence(self, evidence_data: Dict) -> bool:
        """Validate evidence collection requirements"""
        all_valid = True

        # Photography requirements
        photos = evidence_data.get('photos', {})
        required_photo_count = 6  # All 6 sides minimum

        if photos.get('count', 0) < required_photo_count:
            self.violations.append({
                'parameter': 'photographic_evidence',
                'severity': 'MAJOR',
                'message': f'Insufficient photos. Minimum {required_photo_count} required (all 6 sides)',
                'measured': photos.get('count', 0),
                'expected': required_photo_count
            })
            all_valid = False

        # Photo resolution check
        if photos.get('resolution_mp', 0) < 12:
            self.warnings.append({
                'parameter': 'photo_resolution',
                'severity': 'WARNING',
                'message': 'Photo resolution below recommended 12 MP',
                'measured': photos.get('resolution_mp', 0),
                'expected': '>=12 MP'
            })

        # EL imaging
        if not evidence_data.get('el_imaging_performed', False):
            self.warnings.append({
                'parameter': 'el_imaging',
                'severity': 'WARNING',
                'message': 'EL imaging not performed. Recommended for cell defect analysis',
                'measured': False,
                'expected': True
            })

        # IR thermography
        if not evidence_data.get('ir_imaging_performed', False):
            self.warnings.append({
                'parameter': 'ir_thermography',
                'severity': 'WARNING',
                'message': 'IR thermography not performed. Recommended for hotspot detection',
                'measured': False,
                'expected': True
            })

        return all_valid

    def validate_test_completeness(self, test_data: Dict) -> bool:
        """Validate that all required tests were performed"""
        all_valid = True

        # Core test requirements
        required_tests = [
            'visual_inspection',
            'electrical_performance'
        ]

        for test in required_tests:
            if test not in test_data or not test_data[test]:
                self.violations.append({
                    'parameter': f'test_{test}',
                    'severity': 'CRITICAL',
                    'message': f'Required test {test} not performed',
                    'measured': None,
                    'expected': 'Required'
                })
                all_valid = False

        # Visual inspection completeness
        visual = test_data.get('visual_inspection', {})
        if visual.get('defect_count', 0) == 0:
            self.warnings.append({
                'parameter': 'visual_inspection',
                'severity': 'WARNING',
                'message': 'No defects found in visual inspection. Verify thoroughness.',
                'measured': 0,
                'expected': '>0 for claimed failures'
            })

        # Electrical performance validation
        electrical = test_data.get('electrical_performance', {})
        if electrical:
            self.validate_electrical_measurements(electrical)

        return all_valid

    def validate_electrical_measurements(self, electrical_data: Dict) -> bool:
        """Validate electrical measurement data"""
        all_valid = True

        # Power measurement
        measured_power = electrical_data.get('measured_power', 0)
        nameplate_power = electrical_data.get('nameplate_power', 0)

        if measured_power <= 0:
            self.violations.append({
                'parameter': 'measured_power',
                'severity': 'CRITICAL',
                'message': 'Invalid measured power value',
                'measured': measured_power,
                'expected': '>0 W'
            })
            all_valid = False

        if nameplate_power <= 0:
            self.violations.append({
                'parameter': 'nameplate_power',
                'severity': 'CRITICAL',
                'message': 'Invalid nameplate power value',
                'measured': nameplate_power,
                'expected': '>0 W'
            })
            all_valid = False

        # Fill factor check
        ff = electrical_data.get('fill_factor', 0)
        if ff < 0.5 or ff > 0.85:
            self.warnings.append({
                'parameter': 'fill_factor',
                'severity': 'WARNING',
                'message': 'Fill factor outside typical range',
                'measured': ff,
                'expected': '0.70-0.82'
            })

        # Voc check (typical range)
        voc = electrical_data.get('voc', 0)
        if voc < 20 or voc > 100:
            self.warnings.append({
                'parameter': 'voc',
                'severity': 'WARNING',
                'message': 'Voc outside typical range for standard modules',
                'measured': voc,
                'expected': '30-50V for 60-cell, 35-60V for 72-cell'
            })

        # Isc check
        isc = electrical_data.get('isc', 0)
        if isc < 2 or isc > 15:
            self.warnings.append({
                'parameter': 'isc',
                'severity': 'WARNING',
                'message': 'Isc outside typical range',
                'measured': isc,
                'expected': '8-11A typical'
            })

        return all_valid

    def validate_root_cause_analysis(self, rca_data: Dict) -> bool:
        """Validate root cause analysis completeness and logic"""
        all_valid = True

        if not rca_data:
            self.violations.append({
                'parameter': 'root_cause_analysis',
                'severity': 'CRITICAL',
                'message': 'Root cause analysis not performed',
                'measured': None,
                'expected': 'Required'
            })
            return False

        # Primary root cause must be identified
        if not rca_data.get('primary_root_cause'):
            self.violations.append({
                'parameter': 'primary_root_cause',
                'severity': 'CRITICAL',
                'message': 'Primary root cause not identified',
                'measured': None,
                'expected': 'Required'
            })
            all_valid = False

        # Confidence level check
        confidence = rca_data.get('confidence_level', 0)
        if confidence < 0.5:
            self.warnings.append({
                'parameter': 'rca_confidence',
                'severity': 'WARNING',
                'message': 'Low confidence in root cause determination. Consider additional testing.',
                'measured': confidence,
                'expected': '>=0.7'
            })

        # Evidence support
        evidence = rca_data.get('evidence_summary', [])
        if len(evidence) < 2:
            self.warnings.append({
                'parameter': 'rca_evidence',
                'severity': 'WARNING',
                'message': 'Limited evidence for root cause. Multiple evidence sources recommended.',
                'measured': len(evidence),
                'expected': '>=2 sources'
            })

        # 5-Why analysis
        if not rca_data.get('five_why_analysis'):
            self.warnings.append({
                'parameter': 'five_why',
                'severity': 'WARNING',
                'message': '5-Why analysis not documented',
                'measured': None,
                'expected': 'Recommended'
            })

        return all_valid

    def validate_chain_of_custody(self, custody_data: Dict) -> bool:
        """Validate chain of custody documentation"""
        all_valid = True

        if not custody_data:
            self.violations.append({
                'parameter': 'chain_of_custody',
                'severity': 'MAJOR',
                'message': 'Chain of custody documentation missing',
                'measured': None,
                'expected': 'Required'
            })
            return False

        # Required custody events
        required_events = ['receipt', 'storage', 'testing']
        recorded_events = custody_data.get('events', [])

        for event in required_events:
            if not any(e.get('type') == event for e in recorded_events):
                self.violations.append({
                    'parameter': f'custody_event_{event}',
                    'severity': 'MAJOR',
                    'message': f'Missing chain of custody event: {event}',
                    'measured': None,
                    'expected': 'Required'
                })
                all_valid = False

        # Signatures
        for event in recorded_events:
            if not event.get('signature') or not event.get('timestamp'):
                self.warnings.append({
                    'parameter': 'custody_signature',
                    'severity': 'WARNING',
                    'message': f'Missing signature or timestamp for custody event',
                    'measured': event.get('type'),
                    'expected': 'Signature and timestamp required'
                })

        return all_valid

    def validate_warranty_determination(self, warranty_data: Dict,
                                       warranty_terms: Dict) -> bool:
        """Validate warranty determination logic"""
        all_valid = True

        if not warranty_data:
            self.violations.append({
                'parameter': 'warranty_determination',
                'severity': 'CRITICAL',
                'message': 'Warranty determination not completed',
                'measured': None,
                'expected': 'Required'
            })
            return False

        # Validity determination
        validity = warranty_data.get('validity')
        if not validity:
            self.violations.append({
                'parameter': 'warranty_validity',
                'severity': 'CRITICAL',
                'message': 'Warranty validity not determined',
                'measured': None,
                'expected': 'Required'
            })
            all_valid = False

        # Coverage type
        coverage = warranty_data.get('coverage_type')
        if not coverage:
            self.violations.append({
                'parameter': 'coverage_type',
                'severity': 'CRITICAL',
                'message': 'Coverage type not specified',
                'measured': None,
                'expected': 'Required'
            })
            all_valid = False

        # Consistency check
        root_cause = warranty_data.get('root_cause', '')
        if root_cause in ['manufacturing_defect', 'material_defect', 'design_defect']:
            if validity == 'invalid_excluded_cause':
                self.violations.append({
                    'parameter': 'warranty_logic',
                    'severity': 'CRITICAL',
                    'message': 'Inconsistent warranty determination. Manufacturing/material defects should be covered.',
                    'measured': f'{root_cause} -> {validity}',
                    'expected': 'valid for defects'
                })
                all_valid = False
        elif root_cause in ['installation_error', 'environmental_damage']:
            if validity == 'valid':
                self.violations.append({
                    'parameter': 'warranty_logic',
                    'severity': 'CRITICAL',
                    'message': 'Inconsistent warranty determination. Installation/environmental causes typically not covered.',
                    'measured': f'{root_cause} -> {validity}',
                    'expected': 'invalid for excluded causes'
                })
                all_valid = False

        # Recommendation check
        if not warranty_data.get('recommendation'):
            self.warnings.append({
                'parameter': 'warranty_recommendation',
                'severity': 'WARNING',
                'message': 'No recommendation provided',
                'measured': None,
                'expected': 'Recommended'
            })

        return all_valid

    def validate_safety_assessment(self, test_data: Dict) -> bool:
        """Validate safety assessment was performed"""
        all_valid = True

        visual = test_data.get('visual_inspection', {})
        safety_concern = visual.get('safety_concern', False)

        if safety_concern:
            # Safety concerns require immediate action
            if not test_data.get('safety_actions_taken'):
                self.violations.append({
                    'parameter': 'safety_actions',
                    'severity': 'CRITICAL',
                    'message': 'Safety concern identified but no actions documented',
                    'measured': None,
                    'expected': 'Immediate safety assessment and actions required'
                })
                all_valid = False

        # Insulation resistance check
        electrical = test_data.get('electrical_performance', {})
        # Note: Insulation resistance should be separate measurement
        # This is a placeholder for validation logic

        return all_valid

    def validate_measurement_uncertainty(self, test_data: Dict) -> bool:
        """Validate measurement uncertainties are documented"""
        all_valid = True

        electrical = test_data.get('electrical_performance', {})

        # Check if uncertainty is accounted for
        if electrical and not electrical.get('measurement_uncertainty'):
            self.warnings.append({
                'parameter': 'measurement_uncertainty',
                'severity': 'WARNING',
                'message': 'Measurement uncertainty not documented',
                'measured': None,
                'expected': 'Should be documented per ISO 17025'
            })

        return all_valid

    def validate_report_completeness(self, report_data: Dict) -> bool:
        """Validate report has all required sections"""
        all_valid = True

        required_sections = [
            'executive_summary',
            'module_identification',
            'visual_inspection',
            'electrical_tests',
            'root_cause_analysis',
            'warranty_determination'
        ]

        for section in required_sections:
            if section not in report_data or not report_data[section]:
                self.violations.append({
                    'parameter': f'report_section_{section}',
                    'severity': 'MAJOR',
                    'message': f'Required report section missing: {section}',
                    'measured': None,
                    'expected': 'Required'
                })
                all_valid = False

        return all_valid

    def get_violations_by_severity(self, severity: str) -> List[Dict]:
        """Get violations filtered by severity"""
        return [v for v in self.violations if v['severity'] == severity]

    def get_warnings(self) -> List[Dict]:
        """Get all warnings"""
        return self.warnings

    def get_violation_summary(self) -> Dict[str, int]:
        """Get summary of violations by severity"""
        return {
            'CRITICAL': len(self.get_violations_by_severity('CRITICAL')),
            'MAJOR': len(self.get_violations_by_severity('MAJOR')),
            'MINOR': len(self.get_violations_by_severity('MINOR')),
            'WARNINGS': len(self.warnings)
        }

    def is_ready_for_determination(self) -> bool:
        """Check if sufficient testing completed for warranty determination"""
        critical = len(self.get_violations_by_severity('CRITICAL'))
        major = len(self.get_violations_by_severity('MAJOR'))

        # No critical violations, max 1 major violation
        return critical == 0 and major <= 1

    def is_evidence_sufficient(self, test_data: Dict) -> Tuple[bool, str]:
        """Determine if evidence is sufficient for confident determination"""
        evidence_count = 0
        evidence_types = []

        if test_data.get('visual_inspection'):
            evidence_count += 1
            evidence_types.append('visual')

        if test_data.get('el_imaging'):
            evidence_count += 1
            evidence_types.append('EL')

        if test_data.get('ir_thermography'):
            evidence_count += 1
            evidence_types.append('IR')

        if test_data.get('electrical_performance'):
            evidence_count += 1
            evidence_types.append('electrical')

        if evidence_count >= 3:
            return True, f"Sufficient evidence ({', '.join(evidence_types)})"
        elif evidence_count >= 2:
            return True, f"Adequate evidence ({', '.join(evidence_types)}), additional testing recommended"
        else:
            return False, f"Insufficient evidence. Only {', '.join(evidence_types)} performed."
