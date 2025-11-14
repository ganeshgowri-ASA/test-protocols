"""
Data Models for Test Protocol Framework
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum


class ModuleType(Enum):
    """PV Module types"""
    CRYSTALLINE_SILICON = "Crystalline Silicon"
    THIN_FILM = "Thin Film"
    BIFACIAL = "Bifacial"
    BIPV = "BIPV"


class TestPhase(Enum):
    """Test phases"""
    PRE_TEST = "pre_test"
    IN_TEST = "in_test"
    POST_TEST = "post_test"


@dataclass
class Module:
    """PV Module information"""
    serial_number: str
    manufacturer: str
    model: str
    module_type: ModuleType
    rated_power: float  # Watts
    technology: str
    manufacture_date: Optional[datetime] = None
    notes: Optional[str] = None


@dataclass
class ElectricalMeasurement:
    """Electrical measurement data"""
    timestamp: datetime
    module_id: str
    test_id: str
    phase: TestPhase

    # I-V curve parameters
    pmax: float  # Maximum power (W)
    voc: float  # Open circuit voltage (V)
    isc: float  # Short circuit current (A)
    vmpp: float  # Voltage at maximum power point (V)
    impp: float  # Current at maximum power point (A)
    fill_factor: float  # Fill factor (%)

    # Test conditions
    irradiance: float = 1000.0  # W/m²
    temperature: float = 25.0  # °C
    spectrum: str = "AM 1.5"

    notes: Optional[str] = None


@dataclass
class EnvironmentalMeasurement:
    """Environmental chamber measurement"""
    timestamp: datetime
    test_id: str
    step: int
    cycle: int

    temperature: float  # °C
    relative_humidity: float  # %
    sensor_id: str

    target_temperature: Optional[float] = None
    target_humidity: Optional[float] = None


@dataclass
class VisualInspection:
    """Visual inspection record"""
    timestamp: datetime
    module_id: str
    test_id: str
    phase: TestPhase
    inspector: str

    # Defect categories
    delamination: bool = False
    corrosion: bool = False
    broken_cells: bool = False
    bubbles: bool = False
    discoloration: bool = False
    mechanical_damage: bool = False

    # Severity
    major_defects: int = 0
    minor_defects: int = 0

    observations: Optional[str] = None
    photos: List[str] = field(default_factory=list)


@dataclass
class InsulationTest:
    """Insulation resistance test"""
    timestamp: datetime
    module_id: str
    test_id: str
    phase: TestPhase

    test_voltage: float  # V
    resistance: float  # MΩ
    duration: int  # seconds
    temperature: float  # °C
    humidity: float  # %

    passed: bool = True
    notes: Optional[str] = None


@dataclass
class TestSession:
    """Complete test session"""
    test_id: str
    protocol_id: str
    protocol_version: str

    modules: List[Module]
    operator: str
    start_time: datetime
    end_time: Optional[datetime] = None

    # Test equipment
    chamber_id: str = ""
    solar_simulator_id: str = ""
    data_logger_id: str = ""

    # Calibration dates
    chamber_calibration_date: Optional[datetime] = None
    simulator_calibration_date: Optional[datetime] = None

    # Results
    pre_test_electrical: List[ElectricalMeasurement] = field(default_factory=list)
    post_test_electrical: List[ElectricalMeasurement] = field(default_factory=list)
    environmental_data: List[EnvironmentalMeasurement] = field(default_factory=list)
    visual_inspections: List[VisualInspection] = field(default_factory=list)
    insulation_tests: List[InsulationTest] = field(default_factory=list)

    # Test status
    status: str = "pending"
    deviations: List[Dict[str, Any]] = field(default_factory=list)
    alerts: List[Dict[str, Any]] = field(default_factory=list)

    # Results
    pass_fail: Optional[str] = None
    final_report_path: Optional[str] = None

    notes: Optional[str] = None


@dataclass
class TestResult:
    """Test result summary"""
    test_id: str
    protocol_id: str
    module_id: str

    # Performance metrics
    initial_power: float  # W
    final_power: float  # W
    power_degradation: float  # %

    # Acceptance
    visual_pass: bool
    electrical_pass: bool
    insulation_pass: bool
    overall_pass: bool

    # Test conditions
    test_duration: float  # hours
    total_cycles: int
    deviations_count: int
    alerts_count: int

    completion_date: datetime

    notes: Optional[str] = None


def calculate_power_degradation(
    initial_power: float,
    final_power: float
) -> float:
    """
    Calculate power degradation percentage

    Args:
        initial_power: Initial Pmax (W)
        final_power: Final Pmax (W)

    Returns:
        Degradation percentage
    """
    if initial_power <= 0:
        return 0.0

    return ((initial_power - final_power) / initial_power) * 100


def calculate_fill_factor(voc: float, isc: float, vmpp: float, impp: float) -> float:
    """
    Calculate fill factor

    Args:
        voc: Open circuit voltage
        isc: Short circuit current
        vmpp: Voltage at MPP
        impp: Current at MPP

    Returns:
        Fill factor percentage
    """
    if voc <= 0 or isc <= 0:
        return 0.0

    return (vmpp * impp) / (voc * isc) * 100
