"""Data Validation Utilities for PV Testing Protocols"""

from typing import Any, Dict, List, Optional, Union, Callable
from enum import Enum
import re
from datetime import datetime
import numpy as np
import pandas as pd


class ValidationType(Enum):
    """Types of validation checks"""
    REQUIRED = "required"
    RANGE = "range"
    TYPE = "type"
    PATTERN = "pattern"
    CUSTOM = "custom"
    DEPENDENCY = "dependency"


class FieldValidator:
    """Validator for individual fields"""

    @staticmethod
    def validate_required(value: Any, field_name: str) -> tuple[bool, Optional[str]]:
        """Validate that a field has a value"""
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return False, f"{field_name} is required"
        return True, None

    @staticmethod
    def validate_range(value: Union[int, float], min_val: Optional[float] = None,
                      max_val: Optional[float] = None, field_name: str = "") -> tuple[bool, Optional[str]]:
        """Validate that a numeric value is within range"""
        try:
            val = float(value)
            if min_val is not None and val < min_val:
                return False, f"{field_name} must be >= {min_val}, got {val}"
            if max_val is not None and val > max_val:
                return False, f"{field_name} must be <= {max_val}, got {val}"
            return True, None
        except (TypeError, ValueError):
            return False, f"{field_name} must be a number"

    @staticmethod
    def validate_type(value: Any, expected_type: type, field_name: str) -> tuple[bool, Optional[str]]:
        """Validate that a value is of expected type"""
        if not isinstance(value, expected_type):
            return False, f"{field_name} must be {expected_type.__name__}, got {type(value).__name__}"
        return True, None

    @staticmethod
    def validate_pattern(value: str, pattern: str, field_name: str) -> tuple[bool, Optional[str]]:
        """Validate that a string matches a regex pattern"""
        if not isinstance(value, str):
            return False, f"{field_name} must be a string"
        if not re.match(pattern, value):
            return False, f"{field_name} does not match required pattern: {pattern}"
        return True, None

    @staticmethod
    def validate_enum(value: Any, allowed_values: List[Any], field_name: str) -> tuple[bool, Optional[str]]:
        """Validate that a value is in allowed set"""
        if value not in allowed_values:
            return False, f"{field_name} must be one of {allowed_values}, got {value}"
        return True, None

    @staticmethod
    def validate_temperature(temp: float, field_name: str = "Temperature") -> tuple[bool, Optional[str]]:
        """Validate temperature value (in Celsius)"""
        return FieldValidator.validate_range(temp, -273.15, 150, field_name)

    @staticmethod
    def validate_irradiance(irr: float, field_name: str = "Irradiance") -> tuple[bool, Optional[str]]:
        """Validate irradiance value (in W/m²)"""
        return FieldValidator.validate_range(irr, 0, 1500, field_name)

    @staticmethod
    def validate_voltage(voltage: float, field_name: str = "Voltage") -> tuple[bool, Optional[str]]:
        """Validate voltage value"""
        return FieldValidator.validate_range(voltage, 0, 2000, field_name)

    @staticmethod
    def validate_current(current: float, field_name: str = "Current") -> tuple[bool, Optional[str]]:
        """Validate current value"""
        return FieldValidator.validate_range(current, 0, 50, field_name)

    @staticmethod
    def validate_power(power: float, field_name: str = "Power") -> tuple[bool, Optional[str]]:
        """Validate power value"""
        return FieldValidator.validate_range(power, 0, 1000, field_name)

    @staticmethod
    def validate_efficiency(eff: float, field_name: str = "Efficiency") -> tuple[bool, Optional[str]]:
        """Validate efficiency percentage"""
        return FieldValidator.validate_range(eff, 0, 100, field_name)


class DataValidator:
    """Comprehensive data validator for protocol execution"""

    def __init__(self):
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []

    def add_error(self, field: str, message: str, value: Any = None):
        """Add validation error"""
        self.errors.append({
            "field": field,
            "message": message,
            "value": value,
            "timestamp": datetime.now().isoformat()
        })

    def add_warning(self, field: str, message: str, value: Any = None):
        """Add validation warning"""
        self.warnings.append({
            "field": field,
            "message": message,
            "value": value,
            "timestamp": datetime.now().isoformat()
        })

    def has_errors(self) -> bool:
        """Check if there are any errors"""
        return len(self.errors) > 0

    def clear(self):
        """Clear all errors and warnings"""
        self.errors.clear()
        self.warnings.clear()

    def validate_dataframe(self, df: pd.DataFrame, required_columns: List[str]) -> bool:
        """Validate that DataFrame has required columns"""
        missing = set(required_columns) - set(df.columns)
        if missing:
            self.add_error("dataframe", f"Missing required columns: {missing}")
            return False
        return True

    def validate_dataframe_not_empty(self, df: pd.DataFrame, field_name: str = "data") -> bool:
        """Validate that DataFrame is not empty"""
        if df.empty:
            self.add_error(field_name, "DataFrame is empty")
            return False
        return True

    def validate_no_missing_values(self, df: pd.DataFrame, columns: List[str]) -> bool:
        """Validate that specified columns have no missing values"""
        valid = True
        for col in columns:
            if col in df.columns:
                missing_count = df[col].isna().sum()
                if missing_count > 0:
                    self.add_error(col, f"Column has {missing_count} missing values")
                    valid = False
        return valid

    def validate_numeric_column(self, df: pd.DataFrame, column: str,
                                min_val: Optional[float] = None,
                                max_val: Optional[float] = None) -> bool:
        """Validate that column is numeric and within range"""
        if column not in df.columns:
            self.add_error(column, f"Column not found in dataframe")
            return False

        if not pd.api.types.is_numeric_dtype(df[column]):
            self.add_error(column, f"Column must be numeric")
            return False

        valid = True
        if min_val is not None:
            below_min = (df[column] < min_val).sum()
            if below_min > 0:
                self.add_error(column, f"{below_min} values below minimum {min_val}")
                valid = False

        if max_val is not None:
            above_max = (df[column] > max_val).sum()
            if above_max > 0:
                self.add_error(column, f"{above_max} values above maximum {max_val}")
                valid = False

        return valid

    def validate_stc_conditions(self, irradiance: float, temperature: float,
                                airmass: float = 1.5) -> bool:
        """Validate Standard Test Conditions (STC)"""
        valid = True

        # Irradiance: 1000 W/m² ± 2%
        if not (980 <= irradiance <= 1020):
            self.add_warning("irradiance",
                           f"STC irradiance should be 1000±20 W/m², got {irradiance}")
            valid = False

        # Temperature: 25°C ± 2°C
        if not (23 <= temperature <= 27):
            self.add_warning("temperature",
                           f"STC temperature should be 25±2°C, got {temperature}")
            valid = False

        # Air mass: 1.5
        if not (1.4 <= airmass <= 1.6):
            self.add_warning("airmass",
                           f"STC air mass should be 1.5±0.1, got {airmass}")
            valid = False

        return valid

    def validate_measurement_uncertainty(self, value: float, uncertainty: float,
                                        max_uncertainty_pct: float = 5.0) -> bool:
        """Validate measurement uncertainty"""
        if value == 0:
            return True

        uncertainty_pct = abs(uncertainty / value) * 100
        if uncertainty_pct > max_uncertainty_pct:
            self.add_warning("uncertainty",
                           f"Measurement uncertainty {uncertainty_pct:.2f}% exceeds "
                           f"threshold {max_uncertainty_pct}%")
            return False
        return True

    def get_summary(self) -> Dict[str, Any]:
        """Get validation summary"""
        return {
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings,
            "is_valid": len(self.errors) == 0
        }
