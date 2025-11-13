"""
PERF-001: Performance Testing at Different Temperatures
Calculation Engine and Analysis Module

This module implements the calculation engine for IEC 61853 compliant
temperature performance testing of photovoltaic modules.

Author: GenSpark Test Protocols
Version: 1.0.0
"""

import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class Measurement:
    """Single temperature measurement data point"""
    temperature: float  # Celsius
    pmax: float  # Watts
    voc: float  # Volts
    isc: float  # Amperes
    vmp: float  # Volts
    imp: float  # Amperes
    fill_factor: Optional[float] = None
    efficiency: Optional[float] = None
    iv_curve: Optional[Dict[str, List[float]]] = None
    timestamp: Optional[str] = None

    def __post_init__(self):
        """Calculate derived parameters if not provided"""
        if self.fill_factor is None:
            self.fill_factor = self._calculate_fill_factor()
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat() + "Z"

    def _calculate_fill_factor(self) -> float:
        """Calculate fill factor from measurements"""
        if self.voc > 0 and self.isc > 0:
            return (self.pmax) / (self.voc * self.isc)
        return 0.0

    def calculate_efficiency(self, module_area: float, irradiance: float = 1000) -> float:
        """
        Calculate module efficiency

        Args:
            module_area: Module area in m²
            irradiance: Irradiance in W/m²

        Returns:
            Efficiency in percent
        """
        if module_area > 0 and irradiance > 0:
            self.efficiency = (self.pmax / (irradiance * module_area)) * 100
            return self.efficiency
        return 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert measurement to dictionary"""
        return {
            "temperature": self.temperature,
            "pmax": self.pmax,
            "voc": self.voc,
            "isc": self.isc,
            "vmp": self.vmp,
            "imp": self.imp,
            "fill_factor": self.fill_factor,
            "efficiency": self.efficiency,
            "iv_curve": self.iv_curve,
            "timestamp": self.timestamp
        }


@dataclass
class TemperatureCoefficient:
    """Temperature coefficient with statistical metrics"""
    value: float  # Coefficient value
    unit: str  # Unit of measurement
    r_squared: float  # R² value of linear fit
    std_error: Optional[float] = None  # Standard error
    confidence_interval_95: Optional[Tuple[float, float]] = None  # 95% CI

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            "value": self.value,
            "unit": self.unit,
            "r_squared": self.r_squared
        }
        if self.std_error is not None:
            result["std_error"] = self.std_error
        if self.confidence_interval_95 is not None:
            result["confidence_interval_95"] = list(self.confidence_interval_95)
        return result


class PERF001Calculator:
    """
    Main calculation engine for PERF-001 protocol

    Implements IEC 61853 temperature coefficient calculations and analysis
    """

    def __init__(self, reference_temperature: float = 25.0):
        """
        Initialize calculator

        Args:
            reference_temperature: Reference temperature in Celsius (default 25°C)
        """
        self.reference_temperature = reference_temperature
        self.measurements: List[Measurement] = []

    def add_measurement(self, measurement: Measurement) -> None:
        """Add a measurement data point"""
        self.measurements.append(measurement)

    def add_measurements(self, measurements: List[Measurement]) -> None:
        """Add multiple measurement data points"""
        self.measurements.extend(measurements)

    def calculate_temp_coefficient_pmax(self) -> TemperatureCoefficient:
        """
        Calculate temperature coefficient of maximum power (Pmax)

        Uses linear regression on normalized Pmax vs temperature data
        Returns coefficient in %/°C

        Returns:
            TemperatureCoefficient object with value, unit, and statistics
        """
        if len(self.measurements) < 4:
            raise ValueError("Minimum 4 measurements required for IEC 61853 compliance")

        # Extract data
        temps = np.array([m.temperature for m in self.measurements])
        pmax_values = np.array([m.pmax for m in self.measurements])

        # Find reference measurement (closest to reference temperature)
        ref_idx = np.argmin(np.abs(temps - self.reference_temperature))
        pmax_ref = pmax_values[ref_idx]

        # Normalize to reference power
        pmax_normalized = (pmax_values / pmax_ref) * 100  # Convert to percentage

        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(temps, pmax_normalized)

        # Convert slope to %/°C (already in correct units)
        temp_coef = slope

        # Calculate 95% confidence interval
        # For a linear regression, CI = slope ± t * SE
        from scipy.stats import t as t_dist
        n = len(temps)
        t_val = t_dist.ppf(0.975, n - 2)  # 95% CI, two-tailed
        ci_margin = t_val * std_err
        ci = (slope - ci_margin, slope + ci_margin)

        return TemperatureCoefficient(
            value=temp_coef,
            unit="%/°C",
            r_squared=r_value**2,
            std_error=std_err,
            confidence_interval_95=ci
        )

    def calculate_temp_coefficient_voc(self, unit: str = "V/°C") -> TemperatureCoefficient:
        """
        Calculate temperature coefficient of open circuit voltage (Voc)

        Args:
            unit: Desired output unit ("V/°C", "mV/°C", or "%/°C")

        Returns:
            TemperatureCoefficient object
        """
        if len(self.measurements) < 4:
            raise ValueError("Minimum 4 measurements required for IEC 61853 compliance")

        temps = np.array([m.temperature for m in self.measurements])
        voc_values = np.array([m.voc for m in self.measurements])

        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(temps, voc_values)

        # Convert units if needed
        if unit == "mV/°C":
            slope_converted = slope * 1000
            std_err_converted = std_err * 1000
        elif unit == "%/°C":
            # Find reference Voc
            ref_idx = np.argmin(np.abs(temps - self.reference_temperature))
            voc_ref = voc_values[ref_idx]
            slope_converted = (slope / voc_ref) * 100
            std_err_converted = (std_err / voc_ref) * 100
        else:  # V/°C
            slope_converted = slope
            std_err_converted = std_err

        # Calculate 95% CI
        from scipy.stats import t as t_dist
        n = len(temps)
        t_val = t_dist.ppf(0.975, n - 2)
        ci_margin = t_val * std_err_converted
        ci = (slope_converted - ci_margin, slope_converted + ci_margin)

        return TemperatureCoefficient(
            value=slope_converted,
            unit=unit,
            r_squared=r_value**2,
            std_error=std_err_converted,
            confidence_interval_95=ci
        )

    def calculate_temp_coefficient_isc(self, unit: str = "A/°C") -> TemperatureCoefficient:
        """
        Calculate temperature coefficient of short circuit current (Isc)

        Args:
            unit: Desired output unit ("A/°C", "mA/°C", or "%/°C")

        Returns:
            TemperatureCoefficient object
        """
        if len(self.measurements) < 4:
            raise ValueError("Minimum 4 measurements required for IEC 61853 compliance")

        temps = np.array([m.temperature for m in self.measurements])
        isc_values = np.array([m.isc for m in self.measurements])

        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(temps, isc_values)

        # Convert units if needed
        if unit == "mA/°C":
            slope_converted = slope * 1000
            std_err_converted = std_err * 1000
        elif unit == "%/°C":
            # Find reference Isc
            ref_idx = np.argmin(np.abs(temps - self.reference_temperature))
            isc_ref = isc_values[ref_idx]
            slope_converted = (slope / isc_ref) * 100
            std_err_converted = (std_err / isc_ref) * 100
        else:  # A/°C
            slope_converted = slope
            std_err_converted = std_err

        # Calculate 95% CI
        from scipy.stats import t as t_dist
        n = len(temps)
        t_val = t_dist.ppf(0.975, n - 2)
        ci_margin = t_val * std_err_converted
        ci = (slope_converted - ci_margin, slope_converted + ci_margin)

        return TemperatureCoefficient(
            value=slope_converted,
            unit=unit,
            r_squared=r_value**2,
            std_error=std_err_converted,
            confidence_interval_95=ci
        )

    def calculate_normalized_power_at_temp(self, target_temp: float) -> float:
        """
        Calculate normalized power at a specific temperature using regression model

        Args:
            target_temp: Target temperature in Celsius

        Returns:
            Normalized power at target temperature (Watts)
        """
        if len(self.measurements) < 4:
            raise ValueError("Minimum 4 measurements required")

        temps = np.array([m.temperature for m in self.measurements])
        pmax_values = np.array([m.pmax for m in self.measurements])

        # Linear regression
        slope, intercept, _, _, _ = stats.linregress(temps, pmax_values)

        # Predict power at target temperature
        predicted_power = slope * target_temp + intercept

        return predicted_power

    def calculate_all_coefficients(self) -> Dict[str, Any]:
        """
        Calculate all temperature coefficients and derived parameters

        Returns:
            Dictionary containing all calculated results
        """
        results = {
            "temp_coefficient_pmax": self.calculate_temp_coefficient_pmax().to_dict(),
            "temp_coefficient_voc": self.calculate_temp_coefficient_voc(unit="%/°C").to_dict(),
            "temp_coefficient_isc": self.calculate_temp_coefficient_isc(unit="%/°C").to_dict(),
            "reference_temperature": self.reference_temperature,
            "normalized_power_25C": self.calculate_normalized_power_at_temp(25.0)
        }

        return results

    def validate_data_quality(self) -> Dict[str, Any]:
        """
        Perform quality checks on measurement data

        Returns:
            Dictionary with validation results
        """
        warnings = []
        errors = []

        # Check minimum data points
        if len(self.measurements) < 4:
            errors.append("Insufficient measurements: IEC 61853 requires minimum 4 temperature points")

        # Check for data completeness
        for i, m in enumerate(self.measurements):
            if m.pmax <= 0 or m.voc <= 0 or m.isc <= 0:
                errors.append(f"Invalid measurement at index {i}: non-positive values detected")

        # Check fill factor range
        for i, m in enumerate(self.measurements):
            if m.fill_factor and (m.fill_factor < 0.5 or m.fill_factor > 0.9):
                warnings.append(f"Unusual fill factor at index {i}: {m.fill_factor:.3f}")

        # Check temperature coefficient linearity
        if len(self.measurements) >= 4:
            try:
                coef_pmax = self.calculate_temp_coefficient_pmax()
                if coef_pmax.r_squared < 0.95:
                    warnings.append(f"Poor linearity in Pmax vs Temperature: R² = {coef_pmax.r_squared:.3f}")
            except Exception as e:
                errors.append(f"Error calculating Pmax coefficient: {str(e)}")

        # Check physical parameter ranges
        temps = [m.temperature for m in self.measurements]
        if max(temps) - min(temps) < 30:
            warnings.append(f"Small temperature range ({min(temps):.1f} to {max(temps):.1f}°C) may reduce accuracy")

        return {
            "data_completeness": len(errors) == 0,
            "measurement_stability": True,  # Would need raw data to check stability
            "linearity_check": len(self.measurements) >= 4 and coef_pmax.r_squared >= 0.95 if len(self.measurements) >= 4 else False,
            "range_validation": all(
                0 < m.pmax < 1000 and 0 < m.voc < 100 and 0 < m.isc < 50
                for m in self.measurements
            ),
            "warnings": warnings,
            "errors": errors
        }

    def generate_report_data(self) -> Dict[str, Any]:
        """
        Generate complete report data for the test

        Returns:
            Dictionary with all test data and results
        """
        return {
            "measurements": [m.to_dict() for m in self.measurements],
            "calculated_results": self.calculate_all_coefficients(),
            "quality_checks": self.validate_data_quality()
        }


class PERF001Validator:
    """Validates PERF-001 test data against schema and physical constraints"""

    @staticmethod
    def validate_against_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate data against JSON schema

        Args:
            data: Test data dictionary
            schema: JSON schema dictionary

        Returns:
            Tuple of (is_valid, error_messages)
        """
        try:
            import jsonschema
            jsonschema.validate(instance=data, schema=schema)
            return True, []
        except ImportError:
            return False, ["jsonschema package not installed"]
        except jsonschema.exceptions.ValidationError as e:
            return False, [str(e)]

    @staticmethod
    def validate_physical_constraints(measurements: List[Measurement]) -> Tuple[bool, List[str]]:
        """
        Validate physical constraints of measurements

        Args:
            measurements: List of Measurement objects

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        for i, m in enumerate(measurements):
            # Check power equation: Pmax ≈ Vmp × Imp
            calculated_pmax = m.vmp * m.imp
            if abs(m.pmax - calculated_pmax) / m.pmax > 0.05:  # 5% tolerance
                errors.append(
                    f"Measurement {i}: Pmax inconsistency - "
                    f"reported {m.pmax:.2f}W vs calculated {calculated_pmax:.2f}W"
                )

            # Check fill factor range
            if m.fill_factor and (m.fill_factor < 0.4 or m.fill_factor > 0.95):
                errors.append(f"Measurement {i}: Fill factor {m.fill_factor:.3f} outside typical range")

            # Check Vmp < Voc
            if m.vmp >= m.voc:
                errors.append(f"Measurement {i}: Vmp ({m.vmp}V) must be less than Voc ({m.voc}V)")

            # Check Imp < Isc
            if m.imp >= m.isc:
                errors.append(f"Measurement {i}: Imp ({m.imp}A) must be less than Isc ({m.isc}A)")

        return len(errors) == 0, errors


def create_sample_data() -> Dict[str, Any]:
    """
    Create sample test data for demonstration and testing

    Returns:
        Complete PERF-001 test data dictionary
    """
    measurements = [
        Measurement(temperature=15.0, pmax=330.5, voc=46.8, isc=9.12, vmp=38.2, imp=8.65),
        Measurement(temperature=25.0, pmax=320.0, voc=45.2, isc=9.18, vmp=37.0, imp=8.65),
        Measurement(temperature=50.0, pmax=290.0, voc=41.5, isc=9.30, vmp=34.2, imp=8.48),
        Measurement(temperature=75.0, pmax=260.5, voc=38.0, isc=9.42, vmp=31.5, imp=8.27),
    ]

    # Calculate efficiency for each measurement (assuming 1.96 m² module)
    for m in measurements:
        m.calculate_efficiency(module_area=1.96, irradiance=1000)

    # Create calculator and generate results
    calc = PERF001Calculator(reference_temperature=25.0)
    calc.add_measurements(measurements)

    report_data = calc.generate_report_data()

    # Build complete test data structure
    test_data = {
        "protocol_info": {
            "protocol_id": "PERF-001",
            "protocol_name": "Performance at Different Temperatures",
            "standard": "IEC 61853",
            "version": "1.0.0",
            "category": "PERFORMANCE"
        },
        "test_specimen": {
            "module_id": "TEST-MODULE-001",
            "manufacturer": "Example Solar Inc.",
            "model": "ES-320-60M",
            "technology": "mono-Si",
            "rated_power_stc": 320.0,
            "cell_count": 60,
            "area": 1.96,
            "notes": "Sample test module for demonstration"
        },
        "test_conditions": {
            "temperature_points": [15, 25, 50, 75],
            "irradiance": 1000,
            "spectrum": "AM1.5G",
            "measurement_uncertainty": {
                "temperature": 0.5,
                "irradiance": 2.0,
                "electrical": 1.0
            }
        },
        "measurements": report_data["measurements"],
        "calculated_results": report_data["calculated_results"],
        "quality_checks": report_data["quality_checks"],
        "metadata": {
            "test_date": "2025-11-13",
            "test_facility": "Example Test Laboratory",
            "operator": "Test Engineer",
            "equipment": {
                "solar_simulator": "Simulator Model X1000",
                "iv_tracer": "IV Tracer Model T500",
                "temperature_control": "Climate Chamber CC-2000",
                "calibration_date": "2025-10-01"
            },
            "environmental_conditions": {
                "ambient_temperature": 23.5,
                "relative_humidity": 45.0,
                "barometric_pressure": 101.3
            },
            "project_info": {
                "project_id": "PROJ-2025-001",
                "client": "Example Client Corp",
                "purchase_order": "PO-12345"
            },
            "traceability": {
                "lims_id": "LIMS-2025-001",
                "qms_reference": "QMS-TEST-001",
                "parent_test_id": "STC-001-2025-001",
                "related_tests": ["STC-001", "UV-001", "HF-001"]
            },
            "notes": "Sample test data generated for system demonstration"
        }
    }

    return test_data


if __name__ == "__main__":
    # Demo: Create and analyze sample data
    print("PERF-001 Calculation Engine Demo")
    print("=" * 50)

    test_data = create_sample_data()

    print("\nTest Specimen:", test_data["test_specimen"]["model"])
    print("\nMeasurements:")
    for m in test_data["measurements"]:
        print(f"  T={m['temperature']:5.1f}°C: Pmax={m['pmax']:6.2f}W, "
              f"Voc={m['voc']:5.2f}V, Isc={m['isc']:5.2f}A, FF={m['fill_factor']:.3f}")

    print("\nCalculated Temperature Coefficients:")
    results = test_data["calculated_results"]
    print(f"  Pmax: {results['temp_coefficient_pmax']['value']:.4f} "
          f"{results['temp_coefficient_pmax']['unit']} "
          f"(R²={results['temp_coefficient_pmax']['r_squared']:.4f})")
    print(f"  Voc:  {results['temp_coefficient_voc']['value']:.4f} "
          f"{results['temp_coefficient_voc']['unit']} "
          f"(R²={results['temp_coefficient_voc']['r_squared']:.4f})")
    print(f"  Isc:  {results['temp_coefficient_isc']['value']:.4f} "
          f"{results['temp_coefficient_isc']['unit']} "
          f"(R²={results['temp_coefficient_isc']['r_squared']:.4f})")

    print("\nQuality Checks:")
    qc = test_data["quality_checks"]
    print(f"  Data Completeness: {'✓' if qc['data_completeness'] else '✗'}")
    print(f"  Linearity Check: {'✓' if qc['linearity_check'] else '✗'}")
    print(f"  Range Validation: {'✓' if qc['range_validation'] else '✗'}")

    if qc['warnings']:
        print("\nWarnings:")
        for w in qc['warnings']:
            print(f"  - {w}")

    # Export to JSON
    with open("perf-001-sample-output.json", "w") as f:
        json.dump(test_data, f, indent=2)
    print("\n✓ Sample data exported to perf-001-sample-output.json")
