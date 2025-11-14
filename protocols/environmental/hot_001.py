"""HOT-001: Hot Spot Endurance Test Protocol

Implementation of IEC 61215 MQT 09 - Hot Spot Endurance Test.
Tests PV module ability to endure hot spot heating effects.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
import numpy as np
from dataclasses import dataclass

from protocols.base import BaseProtocol, TestResult, MeasurementPoint


@dataclass
class IVCurveData:
    """I-V curve measurement data"""
    timestamp: datetime
    voltage: np.ndarray  # V
    current: np.ndarray  # A
    voc: float  # V
    isc: float  # A
    vmp: float  # V
    imp: float  # A
    pmax: float  # W
    fill_factor: float
    irradiance: float  # W/m²
    temperature: float  # °C


@dataclass
class HotSpotTestData:
    """Data for single hot spot test on one cell"""
    cell_id: str
    start_time: datetime
    end_time: Optional[datetime]
    target_temperature: float  # °C
    reverse_bias_voltage: float  # V
    current_limit: float  # A
    temperature_profile: List[Tuple[datetime, float]]  # [(timestamp, temp)]
    thermal_images: List[str]  # List of thermal image paths
    max_temperature_reached: float  # °C
    completed: bool


@dataclass
class VisualInspection:
    """Visual inspection results"""
    timestamp: datetime
    inspector: str
    defects: List[Dict[str, str]]  # List of defect descriptions
    photographs: List[str]  # List of image paths
    severity: str  # "none", "minor", "major"
    notes: str


class HotSpotEnduranceProtocol(BaseProtocol):
    """Hot Spot Endurance Test Protocol (IEC 61215 MQT 09)

    This protocol tests a PV module's ability to withstand hot spot
    heating caused by reverse bias conditions.
    """

    def __init__(self, protocol_json_path: str = None):
        """Initialize Hot Spot Endurance Protocol

        Args:
            protocol_json_path: Path to protocol JSON. Defaults to standard location.
        """
        if protocol_json_path is None:
            protocol_json_path = Path(__file__).parent.parent.parent / \
                                'templates' / 'protocols' / 'hot-001.json'

        super().__init__(str(protocol_json_path))

        # Test-specific attributes
        self.initial_iv_curve: Optional[IVCurveData] = None
        self.final_iv_curve: Optional[IVCurveData] = None
        self.hot_spot_tests: List[HotSpotTestData] = []
        self.initial_inspection: Optional[VisualInspection] = None
        self.final_inspection: Optional[VisualInspection] = None
        self.initial_insulation_resistance: Optional[float] = None
        self.final_insulation_resistance: Optional[float] = None
        self.wet_leakage_current: Optional[float] = None

        # Module information
        self.module_info: Dict[str, str] = {}

    def validate_inputs(self, **kwargs) -> bool:
        """Validate input parameters for test execution

        Args:
            **kwargs: Test parameters including module_info, equipment_calibration, etc.

        Returns:
            True if inputs are valid
        """
        required_fields = [
            'module_serial_number',
            'module_manufacturer',
            'module_model',
            'operator_name',
            'test_facility'
        ]

        for field in required_fields:
            if field not in kwargs:
                raise ValueError(f"Missing required field: {field}")

        # Validate equipment calibration
        if 'equipment_calibration' in kwargs:
            for equipment_id, cal_data in kwargs['equipment_calibration'].items():
                if 'calibration_date' not in cal_data:
                    raise ValueError(f"Missing calibration date for {equipment_id}")
                if 'calibration_due_date' not in cal_data:
                    raise ValueError(f"Missing calibration due date for {equipment_id}")

        return True

    def execute(self, **kwargs) -> TestResult:
        """Execute the complete Hot Spot Endurance Test

        This is a high-level orchestration method. In practice, each step
        would be executed separately with operator interaction.

        Args:
            **kwargs: Test parameters

        Returns:
            TestResult object with complete test results
        """
        # Validate inputs
        self.validate_inputs(**kwargs)

        # Store module information
        self.module_info = {
            'serial_number': kwargs['module_serial_number'],
            'manufacturer': kwargs['module_manufacturer'],
            'model': kwargs['module_model'],
            'nameplate_power': kwargs.get('nameplate_power', 'Unknown'),
        }

        # Start test
        test_id = kwargs.get('test_id', f"HOT001_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.start_test(test_id)

        try:
            # Execute test sequence
            # In practice, these would be called separately with UI interaction
            pass_status = True
            failures = []

            # Note: Actual implementation would have operator interaction
            # between steps. This is a simplified flow.

            if not all([
                self.initial_iv_curve,
                self.final_iv_curve,
                len(self.hot_spot_tests) >= 3
            ]):
                pass_status = False
                failures.append("Incomplete test execution")

            self.complete_test(pass_status, notes="; ".join(failures) if failures else None)

        except Exception as e:
            self.abort_test(str(e))
            raise

        return self.current_test

    def perform_initial_visual_inspection(
        self,
        inspector: str,
        defects: List[Dict[str, str]] = None,
        photographs: List[str] = None,
        notes: str = ""
    ) -> VisualInspection:
        """Perform and record initial visual inspection (Step 1)

        Args:
            inspector: Name of inspector
            defects: List of observed defects
            photographs: List of photograph file paths
            notes: Additional notes

        Returns:
            VisualInspection object
        """
        self.initial_inspection = VisualInspection(
            timestamp=datetime.now(),
            inspector=inspector,
            defects=defects or [],
            photographs=photographs or [],
            severity=self._assess_defect_severity(defects or []),
            notes=notes
        )

        self.record_measurement(
            parameter="initial_visual_inspection",
            value=len(defects) if defects else 0,
            unit="defects",
            notes=f"Inspector: {inspector}"
        )

        return self.initial_inspection

    def measure_initial_iv_curve(
        self,
        voltage: np.ndarray,
        current: np.ndarray,
        irradiance: float,
        temperature: float
    ) -> IVCurveData:
        """Measure and record initial I-V curve (Step 2)

        Args:
            voltage: Array of voltage measurements (V)
            current: Array of current measurements (A)
            irradiance: Irradiance level (W/m²)
            temperature: Module temperature (°C)

        Returns:
            IVCurveData object
        """
        # Calculate I-V curve parameters
        power = voltage * current
        max_power_idx = np.argmax(power)

        self.initial_iv_curve = IVCurveData(
            timestamp=datetime.now(),
            voltage=voltage,
            current=current,
            voc=voltage[np.argmin(np.abs(current))],
            isc=current[np.argmin(np.abs(voltage))],
            vmp=voltage[max_power_idx],
            imp=current[max_power_idx],
            pmax=power[max_power_idx],
            fill_factor=power[max_power_idx] / (
                voltage[np.argmin(np.abs(current))] * current[np.argmin(np.abs(voltage))]
            ),
            irradiance=irradiance,
            temperature=temperature
        )

        # Record key parameters
        self.record_measurement("initial_voc", self.initial_iv_curve.voc, "V")
        self.record_measurement("initial_isc", self.initial_iv_curve.isc, "A")
        self.record_measurement("initial_pmax", self.initial_iv_curve.pmax, "W")
        self.record_measurement("initial_fill_factor", self.initial_iv_curve.fill_factor, "")

        return self.initial_iv_curve

    def measure_insulation_resistance(
        self,
        resistance: float,
        test_voltage: float,
        is_initial: bool = True
    ) -> float:
        """Measure and record insulation resistance (Steps 3 & 13)

        Args:
            resistance: Measured insulation resistance (MΩ)
            test_voltage: Test voltage used (V)
            is_initial: True for initial test, False for final

        Returns:
            Measured resistance value
        """
        prefix = "initial" if is_initial else "final"

        if is_initial:
            self.initial_insulation_resistance = resistance
        else:
            self.final_insulation_resistance = resistance

        self.record_measurement(
            f"{prefix}_insulation_resistance",
            resistance,
            "MΩ",
            notes=f"Test voltage: {test_voltage}V"
        )

        return resistance

    def select_test_cells(
        self,
        cell_ids: List[str]
    ) -> List[str]:
        """Select and mark cells for hot spot testing (Step 4)

        Args:
            cell_ids: List of cell identifiers (e.g., ["A1", "B5", "C9"])

        Returns:
            List of selected cell IDs
        """
        if len(cell_ids) < 3:
            raise ValueError("Must select at least 3 cells for testing")

        self.record_measurement(
            "cells_selected",
            len(cell_ids),
            "cells",
            notes=f"Cell IDs: {', '.join(cell_ids)}"
        )

        return cell_ids

    def verify_bypass_diode(
        self,
        cell_id: str,
        bypass_voltage_drop: float,
        activation_current: float
    ) -> bool:
        """Verify bypass diode functionality (Step 5)

        Args:
            cell_id: Cell identifier
            bypass_voltage_drop: Measured voltage drop across bypass diode (V)
            activation_current: Current at which diode activates (A)

        Returns:
            True if bypass diode is functional
        """
        # Typical bypass diode voltage drop is 0.4-0.7V for silicon diodes
        is_functional = 0.3 <= bypass_voltage_drop <= 1.0

        self.record_measurement(
            f"bypass_diode_{cell_id}_voltage",
            bypass_voltage_drop,
            "V",
            notes=f"Functional: {is_functional}"
        )

        self.record_measurement(
            f"bypass_diode_{cell_id}_current",
            activation_current,
            "A"
        )

        return is_functional

    def execute_hot_spot_test(
        self,
        cell_id: str,
        reverse_bias_voltage: float,
        current_limit: float,
        target_temperature: float = 85.0,
        duration_hours: float = 1.0,
        temperature_readings: List[Tuple[datetime, float]] = None,
        thermal_images: List[str] = None
    ) -> HotSpotTestData:
        """Execute hot spot test on single cell (Steps 7-9)

        Args:
            cell_id: Cell identifier
            reverse_bias_voltage: Applied reverse bias (V)
            current_limit: Current limit (A)
            target_temperature: Target hot spot temperature (°C)
            duration_hours: Test duration (hours)
            temperature_readings: List of (timestamp, temperature) tuples
            thermal_images: List of thermal image file paths

        Returns:
            HotSpotTestData object
        """
        start_time = datetime.now()

        test_data = HotSpotTestData(
            cell_id=cell_id,
            start_time=start_time,
            end_time=None,
            target_temperature=target_temperature,
            reverse_bias_voltage=reverse_bias_voltage,
            current_limit=current_limit,
            temperature_profile=temperature_readings or [],
            thermal_images=thermal_images or [],
            max_temperature_reached=max(
                [t[1] for t in temperature_readings]
            ) if temperature_readings else 0,
            completed=False
        )

        # Safety check
        if test_data.max_temperature_reached > 120:
            raise ValueError(
                f"Temperature exceeded safety limit: {test_data.max_temperature_reached}°C"
            )

        test_data.end_time = start_time + timedelta(hours=duration_hours)
        test_data.completed = True

        self.hot_spot_tests.append(test_data)

        # Record summary measurements
        self.record_measurement(
            f"hot_spot_{cell_id}_max_temp",
            test_data.max_temperature_reached,
            "°C"
        )

        self.record_measurement(
            f"hot_spot_{cell_id}_reverse_bias",
            reverse_bias_voltage,
            "V"
        )

        return test_data

    def perform_final_visual_inspection(
        self,
        inspector: str,
        defects: List[Dict[str, str]] = None,
        photographs: List[str] = None,
        notes: str = ""
    ) -> VisualInspection:
        """Perform and record final visual inspection (Step 11)

        Args:
            inspector: Name of inspector
            defects: List of observed defects
            photographs: List of photograph file paths
            notes: Additional notes

        Returns:
            VisualInspection object
        """
        self.final_inspection = VisualInspection(
            timestamp=datetime.now(),
            inspector=inspector,
            defects=defects or [],
            photographs=photographs or [],
            severity=self._assess_defect_severity(defects or []),
            notes=notes
        )

        self.record_measurement(
            parameter="final_visual_inspection",
            value=len(defects) if defects else 0,
            unit="defects",
            notes=f"Inspector: {inspector}"
        )

        return self.final_inspection

    def measure_final_iv_curve(
        self,
        voltage: np.ndarray,
        current: np.ndarray,
        irradiance: float,
        temperature: float
    ) -> IVCurveData:
        """Measure and record final I-V curve (Step 12)

        Args:
            voltage: Array of voltage measurements (V)
            current: Array of current measurements (A)
            irradiance: Irradiance level (W/m²)
            temperature: Module temperature (°C)

        Returns:
            IVCurveData object
        """
        # Calculate I-V curve parameters
        power = voltage * current
        max_power_idx = np.argmax(power)

        self.final_iv_curve = IVCurveData(
            timestamp=datetime.now(),
            voltage=voltage,
            current=current,
            voc=voltage[np.argmin(np.abs(current))],
            isc=current[np.argmin(np.abs(voltage))],
            vmp=voltage[max_power_idx],
            imp=current[max_power_idx],
            pmax=power[max_power_idx],
            fill_factor=power[max_power_idx] / (
                voltage[np.argmin(np.abs(current))] * current[np.argmin(np.abs(voltage))]
            ),
            irradiance=irradiance,
            temperature=temperature
        )

        # Record key parameters
        self.record_measurement("final_voc", self.final_iv_curve.voc, "V")
        self.record_measurement("final_isc", self.final_iv_curve.isc, "A")
        self.record_measurement("final_pmax", self.final_iv_curve.pmax, "W")
        self.record_measurement("final_fill_factor", self.final_iv_curve.fill_factor, "")

        return self.final_iv_curve

    def measure_wet_leakage_current(
        self,
        leakage_current: float,
        test_voltage: float
    ) -> float:
        """Measure wet leakage current (Step 14)

        Args:
            leakage_current: Measured leakage current (µA)
            test_voltage: Test voltage used (V)

        Returns:
            Measured leakage current
        """
        self.wet_leakage_current = leakage_current

        self.record_measurement(
            "wet_leakage_current",
            leakage_current,
            "µA",
            notes=f"Test voltage: {test_voltage}V"
        )

        return leakage_current

    def calculate_power_degradation(self) -> float:
        """Calculate power degradation percentage

        Returns:
            Power degradation as percentage
        """
        if not self.initial_iv_curve or not self.final_iv_curve:
            raise ValueError("Both initial and final I-V curves required")

        degradation = (
            (self.initial_iv_curve.pmax - self.final_iv_curve.pmax) /
            self.initial_iv_curve.pmax * 100
        )

        self.record_measurement(
            "power_degradation",
            degradation,
            "%",
            notes=f"Initial: {self.initial_iv_curve.pmax:.2f}W, Final: {self.final_iv_curve.pmax:.2f}W"
        )

        return degradation

    def determine_pass_fail(self) -> Tuple[bool, List[str]]:
        """Determine overall pass/fail status

        Returns:
            Tuple of (pass_status, list_of_failure_reasons)
        """
        failures = []

        # Check power degradation
        if self.initial_iv_curve and self.final_iv_curve:
            degradation = self.calculate_power_degradation()
            max_allowed = self.get_parameter_value('max_power_degradation')
            if degradation > max_allowed:
                failures.append(
                    f"Power degradation {degradation:.2f}% exceeds limit of {max_allowed}%"
                )

        # Check insulation resistance
        if self.final_insulation_resistance:
            min_resistance = self.get_parameter_value('insulation_resistance_min')
            if self.final_insulation_resistance < min_resistance:
                failures.append(
                    f"Insulation resistance {self.final_insulation_resistance:.0f}MΩ "
                    f"below minimum {min_resistance}MΩ"
                )

        # Check wet leakage current
        if self.wet_leakage_current:
            max_leakage = self.get_parameter_value('wet_leakage_current_max')
            if self.wet_leakage_current > max_leakage:
                failures.append(
                    f"Wet leakage current {self.wet_leakage_current:.1f}µA "
                    f"exceeds maximum {max_leakage}µA"
                )

        # Check visual inspection
        if self.final_inspection and self.final_inspection.severity == "major":
            failures.append("Major defects found in final visual inspection")

        # Check hot spot tests completed
        if len(self.hot_spot_tests) < 3:
            failures.append(f"Only {len(self.hot_spot_tests)} cells tested, minimum 3 required")

        return len(failures) == 0, failures

    def _assess_defect_severity(self, defects: List[Dict[str, str]]) -> str:
        """Assess severity of defects

        Args:
            defects: List of defect descriptions

        Returns:
            "none", "minor", or "major"
        """
        if not defects:
            return "none"

        major_keywords = [
            'crack', 'breakage', 'melting', 'perforation',
            'open circuit', 'ground fault', 'failure'
        ]

        for defect in defects:
            description = defect.get('description', '').lower()
            if any(keyword in description for keyword in major_keywords):
                return "major"

        return "minor"

    def generate_test_report(self) -> Dict:
        """Generate comprehensive test report

        Returns:
            Dictionary containing complete test report data
        """
        if not self.current_test:
            raise ValueError("No test to report on")

        degradation = self.calculate_power_degradation() if \
            (self.initial_iv_curve and self.final_iv_curve) else None

        pass_status, failures = self.determine_pass_fail()

        report = {
            'test_info': {
                'test_id': self.current_test.test_id,
                'protocol_id': self.metadata.protocol_id,
                'protocol_name': self.metadata.name,
                'protocol_version': self.metadata.version,
                'standard': self.metadata.standard,
                'start_time': self.current_test.start_time.isoformat(),
                'end_time': self.current_test.end_time.isoformat() if self.current_test.end_time else None,
                'status': self.current_test.status,
            },
            'module_info': self.module_info,
            'initial_measurements': {
                'iv_curve': {
                    'voc': self.initial_iv_curve.voc if self.initial_iv_curve else None,
                    'isc': self.initial_iv_curve.isc if self.initial_iv_curve else None,
                    'pmax': self.initial_iv_curve.pmax if self.initial_iv_curve else None,
                    'fill_factor': self.initial_iv_curve.fill_factor if self.initial_iv_curve else None,
                },
                'insulation_resistance': self.initial_insulation_resistance,
                'visual_inspection': {
                    'defects': self.initial_inspection.defects if self.initial_inspection else [],
                    'severity': self.initial_inspection.severity if self.initial_inspection else None,
                }
            },
            'hot_spot_tests': [
                {
                    'cell_id': test.cell_id,
                    'start_time': test.start_time.isoformat(),
                    'end_time': test.end_time.isoformat() if test.end_time else None,
                    'max_temperature': test.max_temperature_reached,
                    'reverse_bias_voltage': test.reverse_bias_voltage,
                    'completed': test.completed,
                }
                for test in self.hot_spot_tests
            ],
            'final_measurements': {
                'iv_curve': {
                    'voc': self.final_iv_curve.voc if self.final_iv_curve else None,
                    'isc': self.final_iv_curve.isc if self.final_iv_curve else None,
                    'pmax': self.final_iv_curve.pmax if self.final_iv_curve else None,
                    'fill_factor': self.final_iv_curve.fill_factor if self.final_iv_curve else None,
                },
                'insulation_resistance': self.final_insulation_resistance,
                'wet_leakage_current': self.wet_leakage_current,
                'visual_inspection': {
                    'defects': self.final_inspection.defects if self.final_inspection else [],
                    'severity': self.final_inspection.severity if self.final_inspection else None,
                }
            },
            'analysis': {
                'power_degradation_percent': degradation,
                'pass_fail': pass_status,
                'failures': failures,
            },
            'measurements': [m.dict() for m in self.measurements],
        }

        return report

    def export_report_to_json(self, filepath: str) -> str:
        """Export test report to JSON file

        Args:
            filepath: Path to save JSON file

        Returns:
            Path to saved file
        """
        report = self.generate_test_report()

        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        return filepath
