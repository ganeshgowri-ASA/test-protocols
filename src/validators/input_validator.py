"""
Input Validator
Validates protocol inputs and measurements
"""

from typing import Dict, List, Any, Optional, Tuple
import re
from datetime import datetime


class ValidationError(Exception):
    """Custom validation error"""
    pass


class InputValidator:
    """Validates protocol inputs and measurements"""

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""
        # Remove common separators
        cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)
        # Check if it's 10-15 digits
        return bool(re.match(r'^\+?\d{10,15}$', cleaned))

    @staticmethod
    def validate_power_measurement(pmax: float, voc: float, isc: float, ff: float) -> Tuple[bool, str]:
        """
        Validate power measurement values

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check ranges
        if pmax < 0 or pmax > 1000:
            return False, "Pmax must be between 0 and 1000 W"

        if voc < 0 or voc > 100:
            return False, "Voc must be between 0 and 100 V"

        if isc < 0 or isc > 20:
            return False, "Isc must be between 0 and 20 A"

        if ff < 0 or ff > 1:
            return False, "Fill Factor must be between 0 and 1"

        # Check consistency: Pmax should be approximately Voc * Isc * FF
        calculated_pmax = voc * isc * ff
        if abs(pmax - calculated_pmax) > calculated_pmax * 0.1:  # 10% tolerance
            return False, f"Pmax inconsistent with Voc*Isc*FF (calculated: {calculated_pmax:.2f}W)"

        return True, ""

    @staticmethod
    def validate_temperature(temp: float, min_val: float = -50, max_val: float = 150) -> Tuple[bool, str]:
        """Validate temperature value"""
        if temp < min_val or temp > max_val:
            return False, f"Temperature must be between {min_val} and {max_val}°C"
        return True, ""

    @staticmethod
    def validate_irradiance(irr: float) -> Tuple[bool, str]:
        """Validate irradiance value"""
        if irr < 0 or irr > 1500:
            return False, "Irradiance must be between 0 and 1500 W/m²"
        return True, ""

    @staticmethod
    def validate_humidity(rh: float) -> Tuple[bool, str]:
        """Validate relative humidity"""
        if rh < 0 or rh > 100:
            return False, "Relative humidity must be between 0 and 100%"
        return True, ""

    @staticmethod
    def validate_protocol_inputs(protocol_id: str, inputs: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate protocol-specific inputs

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Common validations
        if 'initial_pmax' in inputs:
            if inputs['initial_pmax'] <= 0:
                errors.append("Initial Pmax must be positive")

        if 'initial_voc' in inputs:
            if inputs['initial_voc'] <= 0:
                errors.append("Initial Voc must be positive")

        if 'initial_isc' in inputs:
            if inputs['initial_isc'] <= 0:
                errors.append("Initial Isc must be positive")

        # Protocol-specific validations
        if protocol_id == "PVTP-002":  # Thermal Cycling
            if 'num_cycles' in inputs:
                if inputs['num_cycles'] < 50 or inputs['num_cycles'] > 1000:
                    errors.append("Number of cycles must be between 50 and 1000")

            if 'min_temp' in inputs and 'max_temp' in inputs:
                if inputs['min_temp'] >= inputs['max_temp']:
                    errors.append("Min temperature must be less than max temperature")

        elif protocol_id == "PVTP-003":  # Damp Heat
            if 'duration_hours' in inputs:
                if inputs['duration_hours'] < 100 or inputs['duration_hours'] > 3000:
                    errors.append("Duration must be between 100 and 3000 hours")

        elif protocol_id == "PVTP-005":  # UV Preconditioning
            if 'uv_dose' in inputs:
                if inputs['uv_dose'] < 5 or inputs['uv_dose'] > 100:
                    errors.append("UV dose must be between 5 and 100 kWh/m²")

        return len(errors) == 0, errors

    @staticmethod
    def validate_degradation(initial: float, final: float, max_degradation_pct: float = 5.0) -> Tuple[bool, float]:
        """
        Validate degradation against acceptance criteria

        Returns:
            Tuple of (passes_criteria, degradation_percentage)
        """
        if initial <= 0:
            raise ValidationError("Initial value must be positive")

        degradation_pct = ((initial - final) / initial) * 100
        passes = degradation_pct <= max_degradation_pct

        return passes, degradation_pct

    @staticmethod
    def validate_date_range(start_date: datetime, end_date: datetime) -> Tuple[bool, str]:
        """Validate date range"""
        if end_date < start_date:
            return False, "End date must be after start date"

        if start_date > datetime.now():
            return False, "Start date cannot be in the future"

        return True, ""

    @staticmethod
    def validate_sample_id(sample_id: str) -> Tuple[bool, str]:
        """Validate sample ID format"""
        if not sample_id or len(sample_id) < 3:
            return False, "Sample ID must be at least 3 characters"

        # Check for valid characters
        if not re.match(r'^[A-Z0-9\-_]+$', sample_id):
            return False, "Sample ID can only contain uppercase letters, numbers, hyphens, and underscores"

        return True, ""
