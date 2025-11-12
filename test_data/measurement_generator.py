"""
Measurement data generator for creating synthetic measurement data.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import random
import numpy as np


class MeasurementGenerator:
    """Generates synthetic measurement data for testing."""

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize measurement generator.

        Args:
            seed: Random seed for reproducibility
        """
        if seed:
            random.seed(seed)
            np.random.seed(seed)

        self.measurement_types = {
            "voltage": {"unit": "V", "range": (0, 50), "precision": 2},
            "current": {"unit": "A", "range": (0, 12), "precision": 2},
            "power": {"unit": "W", "range": (0, 400), "precision": 1},
            "temperature": {"unit": "°C", "range": (-40, 150), "precision": 1},
            "irradiance": {"unit": "W/m²", "range": (0, 1200), "precision": 0},
            "efficiency": {"unit": "%", "range": (0, 25), "precision": 2},
            "fill_factor": {"unit": "", "range": (0.6, 0.85), "precision": 3},
            "resistance": {"unit": "Ω", "range": (0, 1000), "precision": 1},
            "capacitance": {"unit": "µF", "range": (0, 100), "precision": 2},
        }

    def generate_measurement(
        self,
        parameter: Optional[str] = None,
        value: Optional[float] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a single measurement.

        Args:
            parameter: Parameter name (random if None)
            value: Measurement value (random if None)
            status: Measurement status (random if None)

        Returns:
            Measurement dictionary
        """
        parameter = parameter or random.choice(list(self.measurement_types.keys()))
        spec = self.measurement_types[parameter]

        if value is None:
            min_val, max_val = spec["range"]
            value = round(random.uniform(min_val, max_val), spec["precision"])

        status = status or random.choice(["pass", "pass", "pass", "warning", "fail"])

        measurement = {
            "measurement_id": f"M{random.randint(1000, 9999)}",
            "parameter": parameter,
            "value": value,
            "unit": spec["unit"],
            "uncertainty": round(value * random.uniform(0.01, 0.05), spec["precision"]),
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "conditions": self._generate_conditions(),
        }

        return measurement

    def generate_iv_curve(
        self, num_points: int = 100, voc: float = 45, isc: float = 9.5
    ) -> List[Dict[str, Any]]:
        """
        Generate I-V curve measurement data.

        Args:
            num_points: Number of points in the curve
            voc: Open circuit voltage
            isc: Short circuit current

        Returns:
            List of measurement dictionaries
        """
        measurements = []
        voltages = np.linspace(0, voc, num_points)

        for i, voltage in enumerate(voltages):
            # Simple I-V curve model
            current = isc * (1 - (voltage / voc) ** 1.5) + np.random.normal(0, 0.05)
            current = max(0, current)  # No negative current
            power = voltage * current

            measurements.extend([
                {
                    "measurement_id": f"IV-V-{i:04d}",
                    "parameter": "voltage",
                    "value": round(voltage, 2),
                    "unit": "V",
                    "timestamp": (datetime.now() + timedelta(milliseconds=i*100)).isoformat(),
                    "status": "pass",
                },
                {
                    "measurement_id": f"IV-I-{i:04d}",
                    "parameter": "current",
                    "value": round(current, 2),
                    "unit": "A",
                    "timestamp": (datetime.now() + timedelta(milliseconds=i*100)).isoformat(),
                    "status": "pass",
                },
                {
                    "measurement_id": f"IV-P-{i:04d}",
                    "parameter": "power",
                    "value": round(power, 2),
                    "unit": "W",
                    "timestamp": (datetime.now() + timedelta(milliseconds=i*100)).isoformat(),
                    "status": "pass",
                }
            ])

        return measurements

    def generate_time_series(
        self,
        parameter: str,
        duration_seconds: int,
        interval_seconds: int = 60,
        base_value: Optional[float] = None,
        noise_level: float = 0.05,
    ) -> List[Dict[str, Any]]:
        """
        Generate time series measurement data.

        Args:
            parameter: Parameter to measure
            duration_seconds: Total duration
            interval_seconds: Interval between measurements
            base_value: Base value (random if None)
            noise_level: Relative noise level (0-1)

        Returns:
            List of measurements
        """
        if parameter not in self.measurement_types:
            raise ValueError(f"Unknown parameter: {parameter}")

        spec = self.measurement_types[parameter]

        if base_value is None:
            min_val, max_val = spec["range"]
            base_value = random.uniform(min_val, max_val)

        num_points = duration_seconds // interval_seconds
        measurements = []
        start_time = datetime.now()

        for i in range(num_points):
            # Add some drift and noise
            drift = np.sin(i / num_points * 2 * np.pi) * base_value * 0.1
            noise = np.random.normal(0, base_value * noise_level)
            value = base_value + drift + noise

            # Ensure within valid range
            min_val, max_val = spec["range"]
            value = np.clip(value, min_val, max_val)

            measurement = {
                "measurement_id": f"TS-{i:04d}",
                "parameter": parameter,
                "value": round(value, spec["precision"]),
                "unit": spec["unit"],
                "timestamp": (start_time + timedelta(seconds=i*interval_seconds)).isoformat(),
                "status": "pass",
            }
            measurements.append(measurement)

        return measurements

    def generate_batch(
        self, count: int, parameters: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple measurements.

        Args:
            count: Number of measurements
            parameters: List of parameters to use

        Returns:
            List of measurement dictionaries
        """
        measurements = []
        params_to_use = parameters or list(self.measurement_types.keys())

        for _ in range(count):
            parameter = random.choice(params_to_use)
            measurement = self.generate_measurement(parameter=parameter)
            measurements.append(measurement)

        return measurements

    def _generate_conditions(self) -> Dict[str, Any]:
        """Generate test conditions."""
        return {
            "ambient_temperature": round(random.uniform(20, 30), 1),
            "humidity": round(random.uniform(30, 70), 1),
            "irradiance": random.randint(800, 1200),
        }

    def generate_invalid_measurement(self) -> Dict[str, Any]:
        """
        Generate an intentionally invalid measurement.

        Returns:
            Invalid measurement data
        """
        invalid_choices = [
            # Missing required field
            {"parameter": "voltage", "value": 24.5},
            # Invalid value type
            {
                "measurement_id": "M001",
                "parameter": "voltage",
                "value": "invalid",
                "unit": "V",
            },
            # Out of range value
            {
                "measurement_id": "M002",
                "parameter": "temperature",
                "value": 999,
                "unit": "°C",
            },
        ]

        return random.choice(invalid_choices)

    def add_measurement_type(
        self, name: str, unit: str, value_range: tuple, precision: int
    ):
        """
        Add a custom measurement type.

        Args:
            name: Parameter name
            unit: Unit of measurement
            value_range: (min, max) tuple
            precision: Decimal precision
        """
        self.measurement_types[name] = {
            "unit": unit,
            "range": value_range,
            "precision": precision,
        }
