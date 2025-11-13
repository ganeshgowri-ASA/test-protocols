"""
PERF-001 Validation and Quality Assurance Module

Comprehensive validation checks for temperature performance testing data
including IEC 61853 compliance verification.
"""

from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import numpy as np


class ValidationLevel(Enum):
    """Validation severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Single validation check result"""
    check_name: str
    passed: bool
    level: ValidationLevel
    message: str
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'check_name': self.check_name,
            'passed': self.passed,
            'level': self.level.value,
            'message': self.message,
            'details': self.details or {}
        }


@dataclass
class ValidationReport:
    """Complete validation report"""
    test_id: str
    overall_passed: bool
    results: List[ValidationResult] = field(default_factory=list)
    summary: Dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        """Calculate summary statistics"""
        self.summary = {
            'total_checks': len(self.results),
            'passed': sum(1 for r in self.results if r.passed),
            'failed': sum(1 for r in self.results if not r.passed),
            'errors': sum(1 for r in self.results if r.level == ValidationLevel.ERROR and not r.passed),
            'warnings': sum(1 for r in self.results if r.level == ValidationLevel.WARNING and not r.passed),
            'critical': sum(1 for r in self.results if r.level == ValidationLevel.CRITICAL and not r.passed)
        }
        self.overall_passed = self.summary['errors'] == 0 and self.summary['critical'] == 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'test_id': self.test_id,
            'overall_passed': self.overall_passed,
            'summary': self.summary,
            'results': [r.to_dict() for r in self.results]
        }

    def get_errors(self) -> List[ValidationResult]:
        """Get all error-level failures"""
        return [r for r in self.results
                if not r.passed and r.level in (ValidationLevel.ERROR, ValidationLevel.CRITICAL)]

    def get_warnings(self) -> List[ValidationResult]:
        """Get all warning-level failures"""
        return [r for r in self.results if not r.passed and r.level == ValidationLevel.WARNING]


class PERF001Validator:
    """
    Comprehensive validator for PERF-001 test data

    Performs IEC 61853 compliance checks, data quality validation,
    and physical constraint verification.
    """

    def __init__(self):
        self.results: List[ValidationResult] = []

    def validate_complete_test(self, test_data: Dict[str, Any]) -> ValidationReport:
        """
        Perform complete validation of test data

        Args:
            test_data: Complete test data dictionary

        Returns:
            ValidationReport with all check results
        """
        self.results = []

        # Extract test ID
        test_id = test_data.get('test_specimen', {}).get('module_id', 'UNKNOWN')

        # Run all validation checks
        self._validate_protocol_info(test_data.get('protocol_info', {}))
        self._validate_test_specimen(test_data.get('test_specimen', {}))
        self._validate_test_conditions(test_data.get('test_conditions', {}))
        self._validate_measurements(test_data.get('measurements', []))
        self._validate_calculated_results(test_data.get('calculated_results', {}))
        self._validate_metadata(test_data.get('metadata', {}))

        # Cross-validation checks
        self._validate_data_consistency(test_data)
        self._validate_iec61853_compliance(test_data)

        return ValidationReport(test_id=test_id, overall_passed=True, results=self.results)

    def _add_result(
        self,
        check_name: str,
        passed: bool,
        level: ValidationLevel,
        message: str,
        details: Optional[Dict] = None
    ):
        """Add a validation result"""
        self.results.append(ValidationResult(check_name, passed, level, message, details))

    def _validate_protocol_info(self, protocol_info: Dict[str, Any]):
        """Validate protocol information section"""
        # Check protocol ID
        if protocol_info.get('protocol_id') != 'PERF-001':
            self._add_result(
                'protocol_id',
                False,
                ValidationLevel.CRITICAL,
                f"Invalid protocol ID: {protocol_info.get('protocol_id')}"
            )
        else:
            self._add_result('protocol_id', True, ValidationLevel.INFO, "Valid protocol ID")

        # Check standard
        if 'IEC 61853' not in protocol_info.get('standard', ''):
            self._add_result(
                'standard',
                False,
                ValidationLevel.WARNING,
                f"Standard may not be IEC 61853: {protocol_info.get('standard')}"
            )
        else:
            self._add_result('standard', True, ValidationLevel.INFO, "Valid standard reference")

    def _validate_test_specimen(self, specimen: Dict[str, Any]):
        """Validate test specimen information"""
        required_fields = ['module_id', 'manufacturer', 'model', 'technology']

        for field in required_fields:
            if not specimen.get(field):
                self._add_result(
                    f'specimen_{field}',
                    False,
                    ValidationLevel.ERROR,
                    f"Missing required field: {field}"
                )
            else:
                self._add_result(
                    f'specimen_{field}',
                    True,
                    ValidationLevel.INFO,
                    f"Valid {field}"
                )

        # Validate rated power
        rated_power = specimen.get('rated_power_stc', 0)
        if rated_power <= 0:
            self._add_result(
                'rated_power',
                False,
                ValidationLevel.WARNING,
                "Rated power not specified or invalid"
            )
        elif rated_power < 10 or rated_power > 1000:
            self._add_result(
                'rated_power',
                False,
                ValidationLevel.WARNING,
                f"Unusual rated power: {rated_power}W (typical range: 10-1000W)"
            )

        # Validate module area
        area = specimen.get('area', 0)
        if area <= 0:
            self._add_result(
                'module_area',
                False,
                ValidationLevel.WARNING,
                "Module area not specified"
            )
        elif area < 0.5 or area > 5.0:
            self._add_result(
                'module_area',
                False,
                ValidationLevel.WARNING,
                f"Unusual module area: {area}m² (typical range: 0.5-5.0m²)"
            )

    def _validate_test_conditions(self, conditions: Dict[str, Any]):
        """Validate test conditions"""
        # Check irradiance
        irradiance = conditions.get('irradiance', 0)
        if irradiance != 1000:
            self._add_result(
                'irradiance',
                False,
                ValidationLevel.ERROR,
                f"PERF-001 requires 1000 W/m² irradiance, got {irradiance}"
            )
        else:
            self._add_result('irradiance', True, ValidationLevel.INFO, "Valid irradiance")

        # Check temperature points
        temp_points = conditions.get('temperature_points', [])
        if len(temp_points) < 4:
            self._add_result(
                'temperature_points_count',
                False,
                ValidationLevel.CRITICAL,
                f"IEC 61853 requires minimum 4 temperature points, got {len(temp_points)}"
            )
        else:
            self._add_result(
                'temperature_points_count',
                True,
                ValidationLevel.INFO,
                f"Valid number of temperature points: {len(temp_points)}"
            )

        # Check temperature range
        if temp_points:
            temp_range = max(temp_points) - min(temp_points)
            if temp_range < 30:
                self._add_result(
                    'temperature_range',
                    False,
                    ValidationLevel.WARNING,
                    f"Small temperature range ({temp_range}°C) may reduce accuracy. Recommended: >30°C"
                )
            elif temp_range < 40:
                self._add_result(
                    'temperature_range',
                    True,
                    ValidationLevel.INFO,
                    f"Adequate temperature range: {temp_range}°C"
                )
            else:
                self._add_result(
                    'temperature_range',
                    True,
                    ValidationLevel.INFO,
                    f"Excellent temperature range: {temp_range}°C"
                )

    def _validate_measurements(self, measurements: List[Dict[str, Any]]):
        """Validate measurement data"""
        if len(measurements) < 4:
            self._add_result(
                'measurements_count',
                False,
                ValidationLevel.CRITICAL,
                f"Insufficient measurements: {len(measurements)} (minimum 4 required)"
            )
            return

        self._add_result(
            'measurements_count',
            True,
            ValidationLevel.INFO,
            f"Valid measurement count: {len(measurements)}"
        )

        # Validate each measurement
        for i, m in enumerate(measurements):
            self._validate_single_measurement(m, i)

        # Check for duplicate temperatures
        temps = [m['temperature'] for m in measurements]
        if len(temps) != len(set(temps)):
            self._add_result(
                'duplicate_temperatures',
                False,
                ValidationLevel.WARNING,
                "Duplicate temperature points detected"
            )

    def _validate_single_measurement(self, measurement: Dict[str, Any], index: int):
        """Validate a single measurement"""
        # Check required parameters
        required = ['temperature', 'pmax', 'voc', 'isc', 'vmp', 'imp']
        for param in required:
            if param not in measurement or measurement[param] <= 0:
                self._add_result(
                    f'measurement_{index}_{param}',
                    False,
                    ValidationLevel.ERROR,
                    f"Measurement {index}: Invalid or missing {param}"
                )
                return

        # Validate power equation: Pmax ≈ Vmp × Imp
        pmax = measurement['pmax']
        vmp = measurement['vmp']
        imp = measurement['imp']
        calculated_pmax = vmp * imp

        if abs(pmax - calculated_pmax) / pmax > 0.05:  # 5% tolerance
            self._add_result(
                f'measurement_{index}_power_consistency',
                False,
                ValidationLevel.ERROR,
                f"Measurement {index}: Pmax inconsistency - "
                f"reported {pmax:.2f}W vs calculated {calculated_pmax:.2f}W",
                {'reported': pmax, 'calculated': calculated_pmax, 'error': abs(pmax - calculated_pmax)}
            )

        # Validate Vmp < Voc
        if measurement['vmp'] >= measurement['voc']:
            self._add_result(
                f'measurement_{index}_voltage_check',
                False,
                ValidationLevel.ERROR,
                f"Measurement {index}: Vmp must be less than Voc"
            )

        # Validate Imp < Isc
        if measurement['imp'] >= measurement['isc']:
            self._add_result(
                f'measurement_{index}_current_check',
                False,
                ValidationLevel.ERROR,
                f"Measurement {index}: Imp must be less than Isc"
            )

        # Validate fill factor range
        ff = measurement.get('fill_factor', 0)
        if ff:
            if ff < 0.5 or ff > 0.9:
                self._add_result(
                    f'measurement_{index}_fill_factor',
                    False,
                    ValidationLevel.WARNING,
                    f"Measurement {index}: Unusual fill factor {ff:.3f} (typical: 0.5-0.9)"
                )

        # Validate physical ranges
        self._validate_physical_ranges(measurement, index)

    def _validate_physical_ranges(self, measurement: Dict[str, Any], index: int):
        """Check if measurements are within physically reasonable ranges"""
        # Voltage: 0-100V typical
        voc = measurement.get('voc', 0)
        if voc > 100:
            self._add_result(
                f'measurement_{index}_voc_range',
                False,
                ValidationLevel.WARNING,
                f"Measurement {index}: Voc ({voc}V) exceeds typical range (0-100V)"
            )

        # Current: 0-50A typical
        isc = measurement.get('isc', 0)
        if isc > 50:
            self._add_result(
                f'measurement_{index}_isc_range',
                False,
                ValidationLevel.WARNING,
                f"Measurement {index}: Isc ({isc}A) exceeds typical range (0-50A)"
            )

        # Power: 0-1000W typical
        pmax = measurement.get('pmax', 0)
        if pmax > 1000:
            self._add_result(
                f'measurement_{index}_pmax_range',
                False,
                ValidationLevel.WARNING,
                f"Measurement {index}: Pmax ({pmax}W) exceeds typical range (0-1000W)"
            )

    def _validate_calculated_results(self, results: Dict[str, Any]):
        """Validate calculated temperature coefficients"""
        if not results:
            self._add_result(
                'calculated_results',
                False,
                ValidationLevel.ERROR,
                "No calculated results found"
            )
            return

        # Check Pmax coefficient
        coef_pmax = results.get('temp_coefficient_pmax', {})
        if coef_pmax:
            value = coef_pmax.get('value', 0)
            r_squared = coef_pmax.get('r_squared', 0)

            # Typical range for crystalline silicon: -0.3 to -0.5 %/°C
            if value > 0 or value < -1.0:
                self._add_result(
                    'temp_coef_pmax_value',
                    False,
                    ValidationLevel.WARNING,
                    f"Unusual Pmax temperature coefficient: {value:.4f} %/°C (typical: -0.3 to -0.5)"
                )

            # R² should be > 0.95 for good linearity
            if r_squared < 0.95:
                self._add_result(
                    'temp_coef_pmax_linearity',
                    False,
                    ValidationLevel.WARNING,
                    f"Poor linearity in Pmax coefficient: R²={r_squared:.4f} (should be >0.95)"
                )
            else:
                self._add_result(
                    'temp_coef_pmax_linearity',
                    True,
                    ValidationLevel.INFO,
                    f"Good linearity: R²={r_squared:.4f}"
                )

        # Check Voc coefficient
        coef_voc = results.get('temp_coefficient_voc', {})
        if coef_voc:
            value = coef_voc.get('value', 0)
            # Should be negative
            if value > 0:
                self._add_result(
                    'temp_coef_voc_value',
                    False,
                    ValidationLevel.WARNING,
                    f"Unusual Voc temperature coefficient: {value:.4f} (should be negative)"
                )

        # Check Isc coefficient
        coef_isc = results.get('temp_coefficient_isc', {})
        if coef_isc:
            value = coef_isc.get('value', 0)
            # Should be positive
            if value < 0:
                self._add_result(
                    'temp_coef_isc_value',
                    False,
                    ValidationLevel.WARNING,
                    f"Unusual Isc temperature coefficient: {value:.4f} (should be positive)"
                )

    def _validate_metadata(self, metadata: Dict[str, Any]):
        """Validate metadata section"""
        required_fields = ['test_date', 'test_facility', 'operator']

        for field in required_fields:
            if not metadata.get(field):
                self._add_result(
                    f'metadata_{field}',
                    False,
                    ValidationLevel.WARNING,
                    f"Missing metadata field: {field}"
                )

    def _validate_data_consistency(self, test_data: Dict[str, Any]):
        """Cross-validate data consistency"""
        measurements = test_data.get('measurements', [])
        conditions = test_data.get('test_conditions', {})

        # Check temperature points match
        temp_points = conditions.get('temperature_points', [])
        measured_temps = [m['temperature'] for m in measurements]

        if set(temp_points) != set(measured_temps):
            self._add_result(
                'temperature_consistency',
                False,
                ValidationLevel.WARNING,
                "Specified temperature points don't match measured temperatures",
                {'specified': temp_points, 'measured': measured_temps}
            )

    def _validate_iec61853_compliance(self, test_data: Dict[str, Any]):
        """Validate IEC 61853 specific requirements"""
        compliance_checks = []

        # Check 1: Minimum 4 temperature points
        measurements = test_data.get('measurements', [])
        if len(measurements) >= 4:
            compliance_checks.append("✓ Minimum 4 temperature points")
        else:
            compliance_checks.append("✗ Insufficient temperature points")

        # Check 2: Irradiance at 1000 W/m²
        irradiance = test_data.get('test_conditions', {}).get('irradiance', 0)
        if irradiance == 1000:
            compliance_checks.append("✓ Irradiance at 1000 W/m²")
        else:
            compliance_checks.append("✗ Incorrect irradiance")

        # Check 3: Data quality (R² > 0.95)
        r_squared = test_data.get('calculated_results', {}).get(
            'temp_coefficient_pmax', {}
        ).get('r_squared', 0)
        if r_squared >= 0.95:
            compliance_checks.append("✓ Good data quality (R² ≥ 0.95)")
        else:
            compliance_checks.append("✗ Poor data quality")

        # Overall compliance
        all_passed = all("✓" in check for check in compliance_checks)

        self._add_result(
            'iec61853_compliance',
            all_passed,
            ValidationLevel.INFO if all_passed else ValidationLevel.ERROR,
            f"IEC 61853 compliance: {'PASS' if all_passed else 'FAIL'}",
            {'checks': compliance_checks}
        )


def validate_test_data(test_data: Dict[str, Any]) -> ValidationReport:
    """
    Convenience function to validate test data

    Args:
        test_data: Complete test data dictionary

    Returns:
        ValidationReport
    """
    validator = PERF001Validator()
    return validator.validate_complete_test(test_data)
