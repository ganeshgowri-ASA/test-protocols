"""pytest configuration and fixtures for test protocols"""

import pytest
from datetime import datetime


@pytest.fixture
def sample_module_specs():
    """Sample PV module specifications"""
    from protocols.mechanical.snow_load.protocol import ModuleSpecs

    return ModuleSpecs(
        module_id="TEST-MOD-001",
        length_mm=1650,
        width_mm=992,
        thickness_mm=35,
        mass_kg=18.5,
        manufacturer="Test Manufacturer",
        model="TEST-100W",
        serial_number="SN12345",
        frame_type="aluminum",
        rated_power_w=100.0
    )


@pytest.fixture
def sample_snow_load_config():
    """Sample snow load test configuration"""
    from protocols.mechanical.snow_load.protocol import SnowLoadTestConfig

    return SnowLoadTestConfig(
        snow_load_pa=2400,  # ~244 kg/m²
        hold_duration_hours=1.0,
        cycles=1,
        test_temperature_c=23.0,
        test_humidity_pct=50.0,
        load_application_rate=10.0,
        support_configuration="4-point",
        max_deflection_mm=50.0,
        max_permanent_deflection_mm=5.0,
        max_cracking="none",
        min_performance_retention_pct=95.0,
        visual_inspection_required=True,
        electrical_test_required=False
    )


@pytest.fixture
def snow_load_protocol(sample_snow_load_config, sample_module_specs):
    """Initialized snow load protocol"""
    from protocols.mechanical.snow_load.protocol import SnowLoadTestProtocol

    return SnowLoadTestProtocol(sample_snow_load_config, sample_module_specs)


@pytest.fixture
def sample_measurements():
    """Sample measurement data"""
    return [
        {
            "timestamp": datetime.now().isoformat(),
            "phase": "baseline",
            "load_applied_pa": 0,
            "deflection_mm": 0.2,
            "visual_condition": "normal"
        },
        {
            "timestamp": datetime.now().isoformat(),
            "phase": "loading",
            "load_applied_pa": 1200,
            "deflection_mm": 15.5,
            "visual_condition": "normal"
        },
        {
            "timestamp": datetime.now().isoformat(),
            "phase": "loading",
            "load_applied_pa": 2400,
            "deflection_mm": 28.3,
            "visual_condition": "normal"
        },
        {
            "timestamp": datetime.now().isoformat(),
            "phase": "hold",
            "load_applied_pa": 2400,
            "deflection_mm": 29.1,
            "visual_condition": "normal"
        },
        {
            "timestamp": datetime.now().isoformat(),
            "phase": "unloading",
            "load_applied_pa": 1200,
            "deflection_mm": 14.8,
            "visual_condition": "normal"
        },
        {
            "timestamp": datetime.now().isoformat(),
            "phase": "recovery",
            "load_applied_pa": 0,
            "deflection_mm": 1.5,
            "visual_condition": "normal"
        }
    ]
