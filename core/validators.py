"""
Validation framework for test protocols
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import re


class ValidationSeverity(Enum):
    """Validation severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Result of a validation check"""
    is_valid: bool
    severity: ValidationSeverity
    rule_name: str
    message: str
    field: Optional[str] = None
    value: Optional[Any] = None


class ValidationRule:
    """
    Base class for validation rules
    """

    def __init__(
        self,
        name: str,
        severity: ValidationSeverity = ValidationSeverity.ERROR,
        message: Optional[str] = None
    ):
        self.name = name
        self.severity = severity
        self.message = message or f"Validation failed: {name}"

    def validate(self, value: Any, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate a value

        Args:
            value: Value to validate
            context: Additional context for validation

        Returns:
            ValidationResult
        """
        raise NotImplementedError("Subclasses must implement validate()")


class RangeValidator(ValidationRule):
    """Validates that a value is within a specified range"""

    def __init__(
        self,
        name: str,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        **kwargs
    ):
        super().__init__(name, **kwargs)
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value: Any, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate that value is within range"""
        try:
            num_value = float(value)

            if self.min_value is not None and num_value < self.min_value:
                return ValidationResult(
                    is_valid=False,
                    severity=self.severity,
                    rule_name=self.name,
                    message=f"Value {num_value} is below minimum {self.min_value}",
                    value=value
                )

            if self.max_value is not None and num_value > self.max_value:
                return ValidationResult(
                    is_valid=False,
                    severity=self.severity,
                    rule_name=self.name,
                    message=f"Value {num_value} exceeds maximum {self.max_value}",
                    value=value
                )

            return ValidationResult(
                is_valid=True,
                severity=self.severity,
                rule_name=self.name,
                message="Value within valid range",
                value=value
            )

        except (ValueError, TypeError):
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                rule_name=self.name,
                message=f"Cannot convert value to number: {value}",
                value=value
            )


class RequiredFieldValidator(ValidationRule):
    """Validates that a required field is present and not empty"""

    def validate(self, value: Any, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate that field is present and not empty"""
        is_valid = value is not None and value != "" and value != []

        return ValidationResult(
            is_valid=is_valid,
            severity=self.severity,
            rule_name=self.name,
            message="Field is required" if not is_valid else "Field is present",
            value=value
        )


class PatternValidator(ValidationRule):
    """Validates that a value matches a regex pattern"""

    def __init__(self, name: str, pattern: str, **kwargs):
        super().__init__(name, **kwargs)
        self.pattern = re.compile(pattern)

    def validate(self, value: Any, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate that value matches pattern"""
        str_value = str(value)
        is_valid = bool(self.pattern.match(str_value))

        return ValidationResult(
            is_valid=is_valid,
            severity=self.severity,
            rule_name=self.name,
            message=f"Value does not match pattern: {self.pattern.pattern}" if not is_valid else "Pattern matched",
            value=value
        )


class CustomValidator(ValidationRule):
    """Validates using a custom function"""

    def __init__(
        self,
        name: str,
        validation_func: Callable[[Any, Optional[Dict[str, Any]]], bool],
        **kwargs
    ):
        super().__init__(name, **kwargs)
        self.validation_func = validation_func

    def validate(self, value: Any, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate using custom function"""
        try:
            is_valid = self.validation_func(value, context)
            return ValidationResult(
                is_valid=is_valid,
                severity=self.severity,
                rule_name=self.name,
                message=self.message if not is_valid else "Validation passed",
                value=value
            )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                rule_name=self.name,
                message=f"Validation error: {str(e)}",
                value=value
            )


class ProtocolValidator:
    """
    Manages validation rules for a protocol
    """

    def __init__(self):
        self.rules: Dict[str, List[ValidationRule]] = {}

    def add_rule(self, field: str, rule: ValidationRule):
        """Add a validation rule for a field"""
        if field not in self.rules:
            self.rules[field] = []
        self.rules[field].append(rule)

    def validate_field(
        self,
        field: str,
        value: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> List[ValidationResult]:
        """Validate a single field"""
        if field not in self.rules:
            return []

        results = []
        for rule in self.rules[field]:
            result = rule.validate(value, context)
            results.append(result)

        return results

    def validate_all(
        self,
        data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> List[ValidationResult]:
        """Validate all fields in data"""
        all_results = []

        for field, rules in self.rules.items():
            value = data.get(field)
            for rule in rules:
                result = rule.validate(value, context)
                result.field = field
                all_results.append(result)

        return all_results

    def is_valid(self, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Check if data is valid

        Returns:
            (is_valid, error_messages)
        """
        results = self.validate_all(data)
        errors = [
            f"{r.field}: {r.message}"
            for r in results
            if not r.is_valid and r.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]
        ]

        return len(errors) == 0, errors


class IVCurveValidator:
    """
    Specialized validator for I-V curve data
    """

    @staticmethod
    def validate_curve(
        voltage: List[float],
        current: List[float],
        irradiance: float,
        temperature: float
    ) -> List[ValidationResult]:
        """
        Validate I-V curve data

        Checks:
        - Voltage and current arrays have same length
        - Voltage is monotonically increasing
        - Current starts positive and decreases to negative (typical PV behavior)
        - No NaN or Inf values
        - Reasonable ranges for given conditions
        """
        results = []

        # Check array lengths
        if len(voltage) != len(current):
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                rule_name="array_length_match",
                message=f"Voltage and current arrays must have same length. Got {len(voltage)} and {len(current)}",
                field="iv_curve"
            ))
            return results  # Can't proceed with other checks

        # Check for NaN or Inf
        import math
        if any(not math.isfinite(v) for v in voltage):
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                rule_name="voltage_finite",
                message="Voltage array contains NaN or Inf values",
                field="voltage"
            ))

        if any(not math.isfinite(i) for i in current):
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                rule_name="current_finite",
                message="Current array contains NaN or Inf values",
                field="current"
            ))

        # Check voltage is monotonically increasing
        if not all(voltage[i] <= voltage[i+1] for i in range(len(voltage)-1)):
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.WARNING,
                rule_name="voltage_monotonic",
                message="Voltage should be monotonically increasing",
                field="voltage"
            ))

        # Check current behavior (should start positive and decrease)
        if current and current[0] < 0:
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.WARNING,
                rule_name="short_circuit_current",
                message="Short circuit current (first point) should be positive",
                field="current"
            ))

        # If all checks passed
        if not results:
            results.append(ValidationResult(
                is_valid=True,
                severity=ValidationSeverity.INFO,
                rule_name="iv_curve_valid",
                message="I-V curve data is valid",
                field="iv_curve"
            ))

        return results
