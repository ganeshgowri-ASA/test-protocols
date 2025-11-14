"""
Data Validator for TEMP-001 Protocol

Validates measurement data and quality checks according to IEC 60891 requirements.

Author: ASA PV Testing
Date: 2025-11-14
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum
import re


class Severity(Enum):
    """Validation severity levels"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationResult:
    """Result of a validation check"""
    check_id: str
    check_name: str
    status: str  # 'pass', 'warning', 'fail'
    severity: Severity
    message: str
    details: Optional[Dict] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'check_id': self.check_id,
            'check_name': self.check_name,
            'status': self.status,
            'severity': self.severity.value,
            'message': self.message,
            'details': self.details
        }


@dataclass
class ValidationReport:
    """Complete validation report"""
    overall_status: str  # 'pass', 'warning', 'fail'
    num_critical_failures: int = 0
    num_warnings: int = 0
    num_passed: int = 0
    results: List[ValidationResult] = field(default_factory=list)

    def add_result(self, result: ValidationResult) -> None:
        """Add a validation result"""
        self.results.append(result)

        if result.status == 'fail' and result.severity == Severity.CRITICAL:
            self.num_critical_failures += 1
        elif result.status == 'warning':
            self.num_warnings += 1
        elif result.status == 'pass':
            self.num_passed += 1

    def update_overall_status(self) -> None:
        """Update overall status based on results"""
        if self.num_critical_failures > 0:
            self.overall_status = 'fail'
        elif self.num_warnings > 0:
            self.overall_status = 'warning'
        else:
            self.overall_status = 'pass'

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'overall_status': self.overall_status,
            'summary': {
                'total_checks': len(self.results),
                'passed': self.num_passed,
                'warnings': self.num_warnings,
                'critical_failures': self.num_critical_failures
            },
            'results': [r.to_dict() for r in self.results]
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent)


class TEMP001Validator:
    """
    Validator for TEMP-001 Temperature Coefficient Testing Protocol
    """

    def __init__(self, protocol_config_path: Optional[str] = None):
        """
        Initialize validator

        Args:
            protocol_config_path: Path to protocol.json configuration
        """
        self.config = self._load_config(protocol_config_path)
        self.data_fields = self._extract_data_fields()
        self.quality_checks = self._extract_quality_checks()

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load protocol configuration"""
        if config_path is None:
            current_dir = Path(__file__).parent.parent
            config_path = current_dir / "protocol.json"

        if Path(config_path).exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            return {}

    def _extract_data_fields(self) -> Dict:
        """Extract data field definitions from config"""
        if 'data_fields' not in self.config:
            return {}

        fields = {}
        for field in self.config['data_fields']:
            fields[field['id']] = field

        return fields

    def _extract_quality_checks(self) -> Dict:
        """Extract quality check definitions from config"""
        if 'quality_checks' not in self.config:
            return {}

        checks = {}
        for check in self.config['quality_checks']:
            checks[check['id']] = check

        return checks

    def validate_field_value(
        self,
        field_id: str,
        value: Any
    ) -> ValidationResult:
        """
        Validate a single field value

        Args:
            field_id: Field identifier
            value: Value to validate

        Returns:
            ValidationResult
        """
        if field_id not in self.data_fields:
            return ValidationResult(
                check_id=f"field_{field_id}",
                check_name=f"Field {field_id}",
                status='fail',
                severity=Severity.CRITICAL,
                message=f"Unknown field: {field_id}"
            )

        field_def = self.data_fields[field_id]

        # Check if required field is present
        if field_def.get('required', False) and (value is None or pd.isna(value)):
            return ValidationResult(
                check_id=f"field_{field_id}_required",
                check_name=field_def['name'],
                status='fail',
                severity=Severity.CRITICAL,
                message=f"Required field '{field_def['name']}' is missing"
            )

        # Skip validation if value is None and field is optional
        if value is None or pd.isna(value):
            return ValidationResult(
                check_id=f"field_{field_id}",
                check_name=field_def['name'],
                status='pass',
                severity=Severity.INFO,
                message="Optional field not provided"
            )

        # Validate type
        expected_type = field_def.get('type', 'string')
        if not self._validate_type(value, expected_type):
            return ValidationResult(
                check_id=f"field_{field_id}_type",
                check_name=field_def['name'],
                status='fail',
                severity=Severity.CRITICAL,
                message=f"Invalid type. Expected {expected_type}, got {type(value).__name__}"
            )

        # Validate range if applicable
        if 'validation' in field_def:
            validation = field_def['validation']

            if 'min' in validation and value < validation['min']:
                return ValidationResult(
                    check_id=f"field_{field_id}_min",
                    check_name=field_def['name'],
                    status='fail',
                    severity=Severity.WARNING,
                    message=f"Value {value} below minimum {validation['min']}",
                    details={'value': value, 'min': validation['min']}
                )

            if 'max' in validation and value > validation['max']:
                return ValidationResult(
                    check_id=f"field_{field_id}_max",
                    check_name=field_def['name'],
                    status='fail',
                    severity=Severity.WARNING,
                    message=f"Value {value} above maximum {validation['max']}",
                    details={'value': value, 'max': validation['max']}
                )

            if 'pattern' in validation:
                if not re.match(validation['pattern'], str(value)):
                    return ValidationResult(
                        check_id=f"field_{field_id}_pattern",
                        check_name=field_def['name'],
                        status='fail',
                        severity=Severity.WARNING,
                        message=f"Value does not match required pattern"
                    )

        return ValidationResult(
            check_id=f"field_{field_id}",
            check_name=field_def['name'],
            status='pass',
            severity=Severity.INFO,
            message="Valid"
        )

    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type"""
        type_map = {
            'float': (int, float, np.integer, np.floating),
            'int': (int, np.integer),
            'string': (str,),
            'datetime': (pd.Timestamp, str),
            'bool': (bool, np.bool_)
        }

        if expected_type not in type_map:
            return True  # Unknown type, skip validation

        return isinstance(value, type_map[expected_type])

    def validate_record(self, record: Dict) -> List[ValidationResult]:
        """
        Validate a single measurement record

        Args:
            record: Dictionary with measurement data

        Returns:
            List of ValidationResults
        """
        results = []

        for field_id in self.data_fields:
            value = record.get(field_id)
            result = self.validate_field_value(field_id, value)
            results.append(result)

        return results

    def validate_dataset(self, data: pd.DataFrame) -> ValidationReport:
        """
        Validate entire dataset

        Args:
            data: DataFrame with measurement data

        Returns:
            ValidationReport
        """
        report = ValidationReport(overall_status='pass')

        # 1. Data Completeness Check
        result = self._check_data_completeness(data)
        report.add_result(result)

        # 2. Temperature Range Check
        result = self._check_temperature_range(data)
        report.add_result(result)

        # 3. Measurement Count Check
        result = self._check_measurement_count(data)
        report.add_result(result)

        # 4. Irradiance Stability Check
        result = self._check_irradiance_stability(data)
        report.add_result(result)

        # 5. Field Validation
        for idx, row in data.iterrows():
            for field_id in ['module_temperature', 'pmax', 'voc', 'isc']:
                if field_id in row:
                    result = self.validate_field_value(field_id, row[field_id])
                    if result.status == 'fail':
                        report.add_result(result)

        report.update_overall_status()
        return report

    def _check_data_completeness(self, data: pd.DataFrame) -> ValidationResult:
        """Check if all required fields are present"""
        required_fields = [
            field['id'] for field in self.config.get('data_fields', [])
            if field.get('required', False)
        ]

        missing_fields = [f for f in required_fields if f not in data.columns]

        if missing_fields:
            return ValidationResult(
                check_id='qc_data_completeness',
                check_name='Data Completeness Check',
                status='fail',
                severity=Severity.CRITICAL,
                message=f"Missing required fields: {', '.join(missing_fields)}",
                details={'missing_fields': missing_fields}
            )

        # Check for missing values
        missing_counts = data[required_fields].isna().sum()
        if missing_counts.any():
            fields_with_missing = missing_counts[missing_counts > 0].to_dict()
            return ValidationResult(
                check_id='qc_data_completeness',
                check_name='Data Completeness Check',
                status='warning',
                severity=Severity.WARNING,
                message=f"Some required fields have missing values",
                details={'missing_counts': fields_with_missing}
            )

        return ValidationResult(
            check_id='qc_data_completeness',
            check_name='Data Completeness Check',
            status='pass',
            severity=Severity.INFO,
            message="All required fields present and complete"
        )

    def _check_temperature_range(self, data: pd.DataFrame) -> ValidationResult:
        """Check if temperature range meets IEC 60891 requirement (≥30°C)"""
        if 'module_temperature' not in data.columns:
            return ValidationResult(
                check_id='qc_temperature_range',
                check_name='Temperature Range Check',
                status='fail',
                severity=Severity.CRITICAL,
                message="Temperature data not found"
            )

        temps = data['module_temperature'].dropna()
        temp_range = temps.max() - temps.min()

        min_range = self.config.get('standard_requirements', {}).get(
            'iec_60891', {}
        ).get('minimum_temperature_range', {}).get('value', 30)

        if temp_range < min_range:
            return ValidationResult(
                check_id='qc_temperature_range',
                check_name='Temperature Range Check',
                status='fail',
                severity=Severity.CRITICAL,
                message=f"Temperature range {temp_range:.1f}°C is below minimum {min_range}°C (IEC 60891)",
                details={
                    'actual_range': temp_range,
                    'required_range': min_range,
                    'min_temp': temps.min(),
                    'max_temp': temps.max()
                }
            )

        return ValidationResult(
            check_id='qc_temperature_range',
            check_name='Temperature Range Check',
            status='pass',
            severity=Severity.INFO,
            message=f"Temperature range {temp_range:.1f}°C meets requirement (≥{min_range}°C)",
            details={
                'actual_range': temp_range,
                'min_temp': temps.min(),
                'max_temp': temps.max()
            }
        )

    def _check_measurement_count(self, data: pd.DataFrame) -> ValidationResult:
        """Check if minimum number of measurements acquired"""
        num_measurements = len(data)

        min_required = self.config.get('standard_requirements', {}).get(
            'iec_60891', {}
        ).get('required_measurement_points', {}).get('value', 5)

        if num_measurements < min_required:
            return ValidationResult(
                check_id='qc_measurement_count',
                check_name='Measurement Count Check',
                status='fail',
                severity=Severity.CRITICAL,
                message=f"Only {num_measurements} measurements, minimum {min_required} required",
                details={
                    'actual_count': num_measurements,
                    'required_count': min_required
                }
            )

        return ValidationResult(
            check_id='qc_measurement_count',
            check_name='Measurement Count Check',
            status='pass',
            severity=Severity.INFO,
            message=f"{num_measurements} measurements acquired (minimum: {min_required})",
            details={'actual_count': num_measurements}
        )

    def _check_irradiance_stability(self, data: pd.DataFrame) -> ValidationResult:
        """Check irradiance stability during test"""
        if 'irradiance' not in data.columns:
            return ValidationResult(
                check_id='qc_irradiance_stability',
                check_name='Irradiance Stability Check',
                status='info',
                severity=Severity.INFO,
                message="Irradiance data not available"
            )

        irrad = data['irradiance'].dropna()
        if len(irrad) == 0:
            return ValidationResult(
                check_id='qc_irradiance_stability',
                check_name='Irradiance Stability Check',
                status='warning',
                severity=Severity.WARNING,
                message="No irradiance data available"
            )

        mean_irrad = irrad.mean()
        std_irrad = irrad.std()
        variation_pct = (std_irrad / mean_irrad) * 100

        max_variation = 2.0  # 2% per IEC 60891

        if variation_pct > max_variation:
            return ValidationResult(
                check_id='qc_irradiance_stability',
                check_name='Irradiance Stability Check',
                status='warning',
                severity=Severity.WARNING,
                message=f"Irradiance variation {variation_pct:.2f}% exceeds {max_variation}%",
                details={
                    'mean_irradiance': mean_irrad,
                    'std_dev': std_irrad,
                    'variation_percent': variation_pct,
                    'threshold': max_variation
                }
            )

        return ValidationResult(
            check_id='qc_irradiance_stability',
            check_name='Irradiance Stability Check',
            status='pass',
            severity=Severity.INFO,
            message=f"Irradiance stable within {variation_pct:.2f}%",
            details={
                'mean_irradiance': mean_irrad,
                'variation_percent': variation_pct
            }
        )

    def validate_coefficients(
        self,
        alpha_pmp: float,
        beta_voc: float,
        alpha_isc: float,
        r_squared_pmp: float,
        r_squared_voc: float,
        r_squared_isc: float
    ) -> List[ValidationResult]:
        """
        Validate calculated temperature coefficients

        Args:
            alpha_pmp: Power temperature coefficient (%/°C)
            beta_voc: Voltage temperature coefficient (%/°C)
            alpha_isc: Current temperature coefficient (%/°C)
            r_squared_pmp: R² for power regression
            r_squared_voc: R² for voltage regression
            r_squared_isc: R² for current regression

        Returns:
            List of ValidationResults
        """
        results = []

        # 1. Linear fit quality check
        min_r_squared = 0.95
        for param, r2, name in [
            ('pmp', r_squared_pmp, 'Power'),
            ('voc', r_squared_voc, 'Voltage'),
            ('isc', r_squared_isc, 'Current')
        ]:
            if r2 < min_r_squared:
                results.append(ValidationResult(
                    check_id=f'qc_r_squared_{param}',
                    check_name=f'{name} Regression Quality',
                    status='warning',
                    severity=Severity.WARNING,
                    message=f"R² = {r2:.4f} is below recommended {min_r_squared}",
                    details={'r_squared': r2, 'threshold': min_r_squared}
                ))
            else:
                results.append(ValidationResult(
                    check_id=f'qc_r_squared_{param}',
                    check_name=f'{name} Regression Quality',
                    status='pass',
                    severity=Severity.INFO,
                    message=f"Excellent fit (R² = {r2:.4f})",
                    details={'r_squared': r2}
                ))

        # 2. Coefficient range checks (typical for crystalline silicon)
        coeff_checks = [
            ('alpha_pmp', alpha_pmp, -0.65, -0.25, 'Power Coefficient'),
            ('beta_voc', beta_voc, -0.50, -0.20, 'Voltage Coefficient'),
            ('alpha_isc', alpha_isc, 0.00, 0.10, 'Current Coefficient')
        ]

        for check_id, value, min_val, max_val, name in coeff_checks:
            if value < min_val or value > max_val:
                results.append(ValidationResult(
                    check_id=f'qc_coefficient_range_{check_id}',
                    check_name=f'{name} Range Check',
                    status='warning',
                    severity=Severity.WARNING,
                    message=f"Value {value:.4f}%/°C outside typical range [{min_val}, {max_val}]",
                    details={
                        'value': value,
                        'expected_min': min_val,
                        'expected_max': max_val
                    }
                ))
            else:
                results.append(ValidationResult(
                    check_id=f'qc_coefficient_range_{check_id}',
                    check_name=f'{name} Range Check',
                    status='pass',
                    severity=Severity.INFO,
                    message=f"Value {value:.4f}%/°C within typical range",
                    details={'value': value}
                ))

        return results


def main():
    """Example usage"""
    # Sample data
    sample_data = pd.DataFrame({
        'module_temperature': [20, 30, 40, 50, 60, 70],
        'pmax': [260, 252, 244, 236, 228, 220],
        'voc': [38.5, 37.8, 37.1, 36.4, 35.7, 35.0],
        'isc': [9.20, 9.25, 9.30, 9.35, 9.40, 9.45],
        'irradiance': [1000, 1005, 998, 1002, 997, 1001]
    })

    # Initialize validator
    validator = TEMP001Validator()

    # Validate dataset
    report = validator.validate_dataset(sample_data)

    print("Validation Report")
    print("=" * 50)
    print(report.to_json())

    # Validate coefficients
    coeff_results = validator.validate_coefficients(
        alpha_pmp=-0.40,
        beta_voc=-0.32,
        alpha_isc=0.05,
        r_squared_pmp=0.998,
        r_squared_voc=0.999,
        r_squared_isc=0.997
    )

    print("\nCoefficient Validation")
    print("=" * 50)
    for result in coeff_results:
        print(f"{result.check_name}: {result.status} - {result.message}")


if __name__ == "__main__":
    main()
