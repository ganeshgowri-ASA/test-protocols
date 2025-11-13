"""
Pytest configuration and fixtures
"""

import pytest
import numpy as np
from typing import Dict, Any, List


@pytest.fixture
def sample_iv_curve() -> Dict[str, List[float]]:
    """
    Generate a realistic I-V curve for testing

    Returns a typical mono-Si solar cell I-V curve
    """
    # Generate voltage points from 0 to Voc
    voltage = np.linspace(0, 0.6, 50)

    # Simplified I-V curve model
    # I = Isc * (1 - exp((V - Voc)/Vt))
    Isc = 8.5  # Short circuit current (A)
    Voc = 0.6  # Open circuit voltage (V)
    Vt = 0.026  # Thermal voltage at 25°C

    current = []
    for v in voltage:
        if v <= Voc:
            i = Isc * (1 - np.exp((v - Voc) / Vt))
            current.append(max(0, i))  # Current can't be negative
        else:
            current.append(0)

    return {
        "voltage": voltage.tolist(),
        "current": current
    }


@pytest.fixture
def sample_measurement(sample_iv_curve) -> Dict[str, Any]:
    """Generate a complete measurement for one irradiance level"""
    return {
        "actual_irradiance": 200.0,
        "actual_temperature": 25.0,
        "timestamp": "2024-01-15T10:30:00",
        "iv_curve": {
            "voltage": sample_iv_curve["voltage"],
            "current": sample_iv_curve["current"],
            "num_points": len(sample_iv_curve["voltage"])
        },
        "raw_measurements": {
            "voc": 0.6,
            "isc": 8.5
        }
    }


@pytest.fixture
def complete_measurements(sample_iv_curve) -> Dict[str, Any]:
    """Generate complete measurements for all irradiance levels"""
    measurements = {}

    # Generate scaled I-V curves for different irradiance levels
    irradiance_levels = [200, 400, 600, 800]

    for irradiance in irradiance_levels:
        # Scale current linearly with irradiance
        scale_factor = irradiance / 200.0
        scaled_current = [i * scale_factor for i in sample_iv_curve["current"]]

        measurements[str(irradiance)] = {
            "actual_irradiance": float(irradiance),
            "actual_temperature": 25.0,
            "timestamp": "2024-01-15T10:30:00",
            "iv_curve": {
                "voltage": sample_iv_curve["voltage"],
                "current": scaled_current,
                "num_points": len(sample_iv_curve["voltage"])
            },
            "raw_measurements": {
                "voc": 0.6,
                "isc": scaled_current[0] if scaled_current else 0
            }
        }

    return measurements


@pytest.fixture
def sample_info() -> Dict[str, Any]:
    """Generate sample information"""
    return {
        "sample_id": "TEST-001",
        "module_type": "Test Module 100W",
        "manufacturer": "Test Manufacturer",
        "serial_number": "SN123456",
        "batch_id": "BATCH-001",
        "cell_technology": "mono-Si",
        "rated_power": 100.0,
        "module_area": 0.65,  # m²
        "num_cells": 60
    }


@pytest.fixture
def test_conditions() -> Dict[str, Any]:
    """Generate test conditions"""
    return {
        "temperature": 25.0,
        "temperature_tolerance": 2.0,
        "spectrum": "AM1.5G",
        "irradiance_levels": [200, 400, 600, 800],
        "irradiance_tolerance": 10.0,
        "operator": "Test Operator",
        "equipment_id": "EQUIP-001",
        "lab_location": "Test Lab",
        "ambient_conditions": {
            "humidity": 50.0,
            "pressure": 101.325
        }
    }


@pytest.fixture
def complete_test_data(sample_info, test_conditions, complete_measurements) -> Dict[str, Any]:
    """Generate complete test data"""
    return {
        "protocol_info": {
            "protocol_id": "LIC-001",
            "version": "1.0.0",
            "standard": "IEC 61215-1:2021",
            "category": "PERFORMANCE",
            "test_date": "2024-01-15T10:00:00"
        },
        "sample_info": sample_info,
        "test_conditions": test_conditions,
        "measurements": complete_measurements,
        "metadata": {
            "run_id": "LIC-001_TEST-001_20240115_abcd1234",
            "created_at": "2024-01-15T10:00:00",
            "updated_at": "2024-01-15T12:00:00"
        }
    }
