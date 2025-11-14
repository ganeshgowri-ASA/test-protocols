"""
UV Preconditioning Protocol (UV-001)
IEC 61215 MQT 10 - UV Preconditioning Test

This module implements the UV preconditioning protocol for photovoltaic modules,
including real-time monitoring, dosage tracking, and spectral data logging.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import numpy as np


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestStatus(Enum):
    """Test execution status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


class ComplianceStatus(Enum):
    """Parameter compliance status"""
    COMPLIANT = "compliant"
    OUT_OF_SPEC = "out_of_spec"
    WARNING = "warning"


@dataclass
class SpectralData:
    """Spectral irradiance measurement data"""
    timestamp: datetime
    wavelengths: List[float]  # nm
    irradiance_values: List[float]  # W/m²/nm
    total_uv_irradiance: float  # W/m²
    uv_a_percentage: float  # %
    uv_b_percentage: float  # %
    peak_wavelength: float  # nm

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'wavelengths': self.wavelengths,
            'irradiance_values': self.irradiance_values,
            'total_uv_irradiance': self.total_uv_irradiance,
            'uv_a_percentage': self.uv_a_percentage,
            'uv_b_percentage': self.uv_b_percentage,
            'peak_wavelength': self.peak_wavelength
        }


@dataclass
class EnvironmentalData:
    """Environmental conditions measurement"""
    timestamp: datetime
    module_temperature: float  # °C
    ambient_temperature: float  # °C
    relative_humidity: float  # %
    air_velocity: Optional[float] = None  # m/s
    barometric_pressure: Optional[float] = None  # kPa

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class IrradianceData:
    """UV irradiance measurement data"""
    timestamp: datetime
    uv_irradiance: float  # W/m²
    sensor_temperature: Optional[float] = None  # °C
    uniformity_measurements: Optional[List[float]] = None  # W/m² at different points

    def calculate_uniformity(self) -> Optional[float]:
        """Calculate irradiance uniformity as percentage deviation"""
        if not self.uniformity_measurements or len(self.uniformity_measurements) < 2:
            return None
        mean = np.mean(self.uniformity_measurements)
        if mean == 0:
            return None
        max_deviation = max(abs(x - mean) for x in self.uniformity_measurements)
        return (max_deviation / mean) * 100

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['uniformity_deviation'] = self.calculate_uniformity()
        return data


@dataclass
class ElectricalParameters:
    """Module electrical characterization data"""
    timestamp: datetime
    open_circuit_voltage: float  # V (Voc)
    short_circuit_current: float  # A (Isc)
    maximum_power: float  # W (Pmax)
    fill_factor: float  # dimensionless (FF)
    efficiency: Optional[float] = None  # %
    series_resistance: Optional[float] = None  # Ω
    shunt_resistance: Optional[float] = None  # Ω
    iv_curve: Optional[List[Tuple[float, float]]] = None  # [(V, I), ...]

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class TestSession:
    """Test session data container"""
    session_id: str
    protocol_id: str = "UV-001"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: TestStatus = TestStatus.PENDING
    operator: str = ""
    sample_id: str = ""
    notes: str = ""

    # Test data collections
    irradiance_measurements: List[IrradianceData] = field(default_factory=list)
    environmental_measurements: List[EnvironmentalData] = field(default_factory=list)
    spectral_measurements: List[SpectralData] = field(default_factory=list)

    # Pre and post characterization
    pre_test_electrical: Optional[ElectricalParameters] = None
    post_test_electrical: Optional[ElectricalParameters] = None

    # Calculated metrics
    cumulative_uv_dose: float = 0.0  # kWh/m²
    total_exposure_time: float = 0.0  # hours
    average_irradiance: float = 0.0  # W/m²

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'session_id': self.session_id,
            'protocol_id': self.protocol_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status.value,
            'operator': self.operator,
            'sample_id': self.sample_id,
            'notes': self.notes,
            'cumulative_uv_dose': self.cumulative_uv_dose,
            'total_exposure_time': self.total_exposure_time,
            'average_irradiance': self.average_irradiance,
            'irradiance_measurements': [m.to_dict() for m in self.irradiance_measurements],
            'environmental_measurements': [m.to_dict() for m in self.environmental_measurements],
            'spectral_measurements': [m.to_dict() for m in self.spectral_measurements],
            'pre_test_electrical': self.pre_test_electrical.to_dict() if self.pre_test_electrical else None,
            'post_test_electrical': self.post_test_electrical.to_dict() if self.post_test_electrical else None
        }


class UVPreconditioningProtocol:
    """
    UV Preconditioning Protocol Implementation (IEC 61215 MQT 10)

    Manages UV exposure testing with real-time monitoring, dosage tracking,
    and spectral data logging for photovoltaic module qualification.
    """

    # Protocol specifications from IEC 61215 MQT 10
    TARGET_UV_DOSE = 15.0  # kWh/m²
    TARGET_UV_DOSE_TOLERANCE = 0.02  # ± 2%

    WAVELENGTH_MIN = 280  # nm
    WAVELENGTH_MAX = 400  # nm
    PEAK_WAVELENGTH_TARGET = 340  # nm
    PEAK_WAVELENGTH_TOLERANCE = 20  # ± nm

    IRRADIANCE_MIN = 250  # W/m²
    IRRADIANCE_MAX = 400  # W/m²
    IRRADIANCE_NOMINAL = 300  # W/m²

    MODULE_TEMP_TARGET = 60  # °C
    MODULE_TEMP_TOLERANCE = 5  # ± °C

    AMBIENT_TEMP_TARGET = 25  # °C
    AMBIENT_TEMP_TOLERANCE = 10  # ± °C

    HUMIDITY_MAX = 75  # %

    AIR_VELOCITY_MIN = 0.5  # m/s
    AIR_VELOCITY_MAX = 2.0  # m/s

    # Spectral distribution requirements
    UVB_PERCENTAGE_MIN = 5  # %
    UVB_PERCENTAGE_MAX = 10  # %
    UVA_PERCENTAGE_MIN = 90  # %
    UVA_PERCENTAGE_MAX = 95  # %

    # Acceptance criteria
    MAX_POWER_DEGRADATION = 5.0  # %
    MIN_INSULATION_RESISTANCE = 40  # MΩ

    def __init__(self, protocol_file: Optional[Path] = None):
        """
        Initialize UV Preconditioning Protocol

        Args:
            protocol_file: Path to protocol JSON configuration file
        """
        self.protocol_config = self._load_protocol_config(protocol_file)
        self.current_session: Optional[TestSession] = None
        self.last_measurement_time: Optional[datetime] = None

    def _load_protocol_config(self, protocol_file: Optional[Path]) -> Dict:
        """Load protocol configuration from JSON file"""
        if protocol_file and protocol_file.exists():
            with open(protocol_file, 'r') as f:
                return json.load(f)
        return {}

    def start_test_session(
        self,
        session_id: str,
        sample_id: str,
        operator: str,
        notes: str = ""
    ) -> TestSession:
        """
        Start a new UV preconditioning test session

        Args:
            session_id: Unique session identifier
            sample_id: Module/sample identifier
            operator: Test operator name
            notes: Optional test notes

        Returns:
            TestSession object
        """
        if self.current_session and self.current_session.status == TestStatus.IN_PROGRESS:
            raise ValueError("Cannot start new session while another is in progress")

        self.current_session = TestSession(
            session_id=session_id,
            start_time=datetime.now(),
            status=TestStatus.IN_PROGRESS,
            operator=operator,
            sample_id=sample_id,
            notes=notes
        )

        logger.info(f"Started UV-001 test session {session_id} for sample {sample_id}")
        return self.current_session

    def add_irradiance_measurement(
        self,
        uv_irradiance: float,
        sensor_temperature: Optional[float] = None,
        uniformity_measurements: Optional[List[float]] = None,
        timestamp: Optional[datetime] = None
    ) -> IrradianceData:
        """
        Add UV irradiance measurement and update cumulative dose

        Args:
            uv_irradiance: UV irradiance in W/m²
            sensor_temperature: Optional sensor temperature in °C
            uniformity_measurements: Optional list of irradiance at multiple points
            timestamp: Measurement timestamp (defaults to now)

        Returns:
            IrradianceData object

        Raises:
            ValueError: If no active test session
        """
        if not self.current_session:
            raise ValueError("No active test session")

        timestamp = timestamp or datetime.now()

        measurement = IrradianceData(
            timestamp=timestamp,
            uv_irradiance=uv_irradiance,
            sensor_temperature=sensor_temperature,
            uniformity_measurements=uniformity_measurements
        )

        self.current_session.irradiance_measurements.append(measurement)

        # Update cumulative dose
        if self.last_measurement_time:
            time_delta = (timestamp - self.last_measurement_time).total_seconds() / 3600  # hours
            # Use trapezoidal integration for dose calculation
            if len(self.current_session.irradiance_measurements) > 1:
                prev_irradiance = self.current_session.irradiance_measurements[-2].uv_irradiance
                avg_irradiance = (uv_irradiance + prev_irradiance) / 2
                dose_increment = (avg_irradiance * time_delta) / 1000  # kWh/m²
                self.current_session.cumulative_uv_dose += dose_increment

        self.last_measurement_time = timestamp

        # Update statistics
        self._update_session_statistics()

        # Check compliance
        compliance = self._check_irradiance_compliance(uv_irradiance)
        if compliance != ComplianceStatus.COMPLIANT:
            logger.warning(
                f"Irradiance {uv_irradiance:.1f} W/m² is {compliance.value} "
                f"(target: {self.IRRADIANCE_MIN}-{self.IRRADIANCE_MAX} W/m²)"
            )

        return measurement

    def add_environmental_measurement(
        self,
        module_temperature: float,
        ambient_temperature: float,
        relative_humidity: float,
        air_velocity: Optional[float] = None,
        barometric_pressure: Optional[float] = None,
        timestamp: Optional[datetime] = None
    ) -> EnvironmentalData:
        """
        Add environmental conditions measurement

        Args:
            module_temperature: Module surface temperature in °C
            ambient_temperature: Chamber ambient temperature in °C
            relative_humidity: Relative humidity in %
            air_velocity: Optional air velocity in m/s
            barometric_pressure: Optional pressure in kPa
            timestamp: Measurement timestamp (defaults to now)

        Returns:
            EnvironmentalData object
        """
        if not self.current_session:
            raise ValueError("No active test session")

        timestamp = timestamp or datetime.now()

        measurement = EnvironmentalData(
            timestamp=timestamp,
            module_temperature=module_temperature,
            ambient_temperature=ambient_temperature,
            relative_humidity=relative_humidity,
            air_velocity=air_velocity,
            barometric_pressure=barometric_pressure
        )

        self.current_session.environmental_measurements.append(measurement)

        # Check compliance
        temp_compliance = self._check_temperature_compliance(module_temperature, ambient_temperature)
        humidity_compliance = self._check_humidity_compliance(relative_humidity)

        if air_velocity:
            velocity_compliance = self._check_air_velocity_compliance(air_velocity)

        return measurement

    def add_spectral_measurement(
        self,
        wavelengths: List[float],
        irradiance_values: List[float],
        timestamp: Optional[datetime] = None
    ) -> SpectralData:
        """
        Add spectral irradiance measurement

        Args:
            wavelengths: List of wavelengths in nm
            irradiance_values: Corresponding irradiance values in W/m²/nm
            timestamp: Measurement timestamp (defaults to now)

        Returns:
            SpectralData object
        """
        if not self.current_session:
            raise ValueError("No active test session")

        timestamp = timestamp or datetime.now()

        # Calculate spectral metrics
        wavelengths_arr = np.array(wavelengths)
        irradiance_arr = np.array(irradiance_values)

        # Total UV irradiance (integrate over wavelength range)
        uv_mask = (wavelengths_arr >= self.WAVELENGTH_MIN) & (wavelengths_arr <= self.WAVELENGTH_MAX)
        total_uv_irradiance = np.trapz(irradiance_arr[uv_mask], wavelengths_arr[uv_mask])

        # UVA and UVB percentages
        uvb_mask = (wavelengths_arr >= 280) & (wavelengths_arr <= 320)
        uva_mask = (wavelengths_arr >= 320) & (wavelengths_arr <= 400)

        uvb_irradiance = np.trapz(irradiance_arr[uvb_mask], wavelengths_arr[uvb_mask])
        uva_irradiance = np.trapz(irradiance_arr[uva_mask], wavelengths_arr[uva_mask])

        if total_uv_irradiance > 0:
            uv_b_percentage = (uvb_irradiance / total_uv_irradiance) * 100
            uv_a_percentage = (uva_irradiance / total_uv_irradiance) * 100
        else:
            uv_b_percentage = 0
            uv_a_percentage = 0

        # Peak wavelength
        peak_idx = np.argmax(irradiance_arr)
        peak_wavelength = wavelengths_arr[peak_idx]

        measurement = SpectralData(
            timestamp=timestamp,
            wavelengths=wavelengths,
            irradiance_values=irradiance_values,
            total_uv_irradiance=total_uv_irradiance,
            uv_a_percentage=uv_a_percentage,
            uv_b_percentage=uv_b_percentage,
            peak_wavelength=peak_wavelength
        )

        self.current_session.spectral_measurements.append(measurement)

        # Check spectral compliance
        self._check_spectral_compliance(measurement)

        logger.info(
            f"Spectral measurement: Peak {peak_wavelength:.1f} nm, "
            f"UVA {uv_a_percentage:.1f}%, UVB {uv_b_percentage:.1f}%"
        )

        return measurement

    def add_electrical_characterization(
        self,
        voc: float,
        isc: float,
        pmax: float,
        ff: float,
        efficiency: Optional[float] = None,
        series_resistance: Optional[float] = None,
        shunt_resistance: Optional[float] = None,
        iv_curve: Optional[List[Tuple[float, float]]] = None,
        is_pre_test: bool = True,
        timestamp: Optional[datetime] = None
    ) -> ElectricalParameters:
        """
        Add electrical characterization data

        Args:
            voc: Open circuit voltage in V
            isc: Short circuit current in A
            pmax: Maximum power in W
            ff: Fill factor
            efficiency: Optional efficiency in %
            series_resistance: Optional series resistance in Ω
            shunt_resistance: Optional shunt resistance in Ω
            iv_curve: Optional I-V curve data
            is_pre_test: True for pre-test, False for post-test
            timestamp: Measurement timestamp (defaults to now)

        Returns:
            ElectricalParameters object
        """
        if not self.current_session:
            raise ValueError("No active test session")

        timestamp = timestamp or datetime.now()

        params = ElectricalParameters(
            timestamp=timestamp,
            open_circuit_voltage=voc,
            short_circuit_current=isc,
            maximum_power=pmax,
            fill_factor=ff,
            efficiency=efficiency,
            series_resistance=series_resistance,
            shunt_resistance=shunt_resistance,
            iv_curve=iv_curve
        )

        if is_pre_test:
            self.current_session.pre_test_electrical = params
            logger.info(f"Pre-test characterization: Pmax={pmax:.2f} W, FF={ff:.3f}")
        else:
            self.current_session.post_test_electrical = params
            logger.info(f"Post-test characterization: Pmax={pmax:.2f} W, FF={ff:.3f}")

            # Calculate degradation if both measurements exist
            if self.current_session.pre_test_electrical:
                degradation = self.calculate_power_degradation()
                logger.info(f"Power degradation: {degradation:.2f}%")

        return params

    def calculate_power_degradation(self) -> Optional[float]:
        """
        Calculate power degradation percentage

        Returns:
            Power degradation as percentage, or None if data not available
        """
        if not self.current_session:
            return None

        pre = self.current_session.pre_test_electrical
        post = self.current_session.post_test_electrical

        if not pre or not post:
            return None

        if pre.maximum_power == 0:
            return None

        degradation = ((pre.maximum_power - post.maximum_power) / pre.maximum_power) * 100
        return degradation

    def get_cumulative_dose(self) -> float:
        """Get current cumulative UV dose in kWh/m²"""
        if not self.current_session:
            return 0.0
        return self.current_session.cumulative_uv_dose

    def get_remaining_dose(self) -> float:
        """Get remaining UV dose to reach target in kWh/m²"""
        remaining = self.TARGET_UV_DOSE - self.get_cumulative_dose()
        return max(0.0, remaining)

    def get_dose_completion_percentage(self) -> float:
        """Get test completion percentage based on UV dose"""
        if self.TARGET_UV_DOSE == 0:
            return 0.0
        return (self.get_cumulative_dose() / self.TARGET_UV_DOSE) * 100

    def estimate_remaining_time(self) -> Optional[float]:
        """
        Estimate remaining exposure time in hours based on current irradiance

        Returns:
            Estimated hours remaining, or None if insufficient data
        """
        if not self.current_session or self.current_session.average_irradiance == 0:
            return None

        remaining_dose = self.get_remaining_dose()  # kWh/m²
        avg_irradiance = self.current_session.average_irradiance  # W/m²

        # Convert to hours: (kWh/m²) / (kW/m²) = hours
        estimated_hours = remaining_dose / (avg_irradiance / 1000)

        return estimated_hours

    def check_dose_target_reached(self) -> bool:
        """Check if target UV dose has been reached within tolerance"""
        dose = self.get_cumulative_dose()
        min_dose = self.TARGET_UV_DOSE * (1 - self.TARGET_UV_DOSE_TOLERANCE)
        max_dose = self.TARGET_UV_DOSE * (1 + self.TARGET_UV_DOSE_TOLERANCE)

        return min_dose <= dose <= max_dose

    def check_acceptance_criteria(self) -> Dict[str, Any]:
        """
        Check if test results meet acceptance criteria

        Returns:
            Dictionary with pass/fail status and details
        """
        results = {
            'overall_pass': True,
            'criteria': {}
        }

        # Check power degradation
        degradation = self.calculate_power_degradation()
        if degradation is not None:
            power_pass = degradation <= self.MAX_POWER_DEGRADATION
            results['criteria']['power_degradation'] = {
                'value': degradation,
                'limit': self.MAX_POWER_DEGRADATION,
                'unit': '%',
                'pass': power_pass
            }
            results['overall_pass'] &= power_pass

        # Check UV dose completion
        dose_pass = self.check_dose_target_reached()
        results['criteria']['uv_dose'] = {
            'value': self.get_cumulative_dose(),
            'target': self.TARGET_UV_DOSE,
            'unit': 'kWh/m²',
            'pass': dose_pass
        }
        results['overall_pass'] &= dose_pass

        return results

    def _update_session_statistics(self):
        """Update session-level statistics"""
        if not self.current_session:
            return

        # Calculate average irradiance
        if self.current_session.irradiance_measurements:
            irradiances = [m.uv_irradiance for m in self.current_session.irradiance_measurements]
            self.current_session.average_irradiance = np.mean(irradiances)

        # Calculate total exposure time
        if self.current_session.start_time and self.last_measurement_time:
            time_delta = self.last_measurement_time - self.current_session.start_time
            self.current_session.total_exposure_time = time_delta.total_seconds() / 3600

    def _check_irradiance_compliance(self, irradiance: float) -> ComplianceStatus:
        """Check if irradiance is within specification"""
        if self.IRRADIANCE_MIN <= irradiance <= self.IRRADIANCE_MAX:
            return ComplianceStatus.COMPLIANT
        return ComplianceStatus.OUT_OF_SPEC

    def _check_temperature_compliance(
        self,
        module_temp: float,
        ambient_temp: float
    ) -> Tuple[ComplianceStatus, ComplianceStatus]:
        """Check if temperatures are within specification"""
        module_min = self.MODULE_TEMP_TARGET - self.MODULE_TEMP_TOLERANCE
        module_max = self.MODULE_TEMP_TARGET + self.MODULE_TEMP_TOLERANCE

        ambient_min = self.AMBIENT_TEMP_TARGET - self.AMBIENT_TEMP_TOLERANCE
        ambient_max = self.AMBIENT_TEMP_TARGET + self.AMBIENT_TEMP_TOLERANCE

        module_status = (
            ComplianceStatus.COMPLIANT
            if module_min <= module_temp <= module_max
            else ComplianceStatus.OUT_OF_SPEC
        )

        ambient_status = (
            ComplianceStatus.COMPLIANT
            if ambient_min <= ambient_temp <= ambient_max
            else ComplianceStatus.OUT_OF_SPEC
        )

        if module_status != ComplianceStatus.COMPLIANT:
            logger.warning(
                f"Module temperature {module_temp:.1f}°C is out of spec "
                f"(target: {self.MODULE_TEMP_TARGET} ± {self.MODULE_TEMP_TOLERANCE}°C)"
            )

        return module_status, ambient_status

    def _check_humidity_compliance(self, humidity: float) -> ComplianceStatus:
        """Check if humidity is within specification"""
        if humidity <= self.HUMIDITY_MAX:
            return ComplianceStatus.COMPLIANT

        logger.warning(f"Humidity {humidity:.1f}% exceeds maximum {self.HUMIDITY_MAX}%")
        return ComplianceStatus.OUT_OF_SPEC

    def _check_air_velocity_compliance(self, velocity: float) -> ComplianceStatus:
        """Check if air velocity is within specification"""
        if self.AIR_VELOCITY_MIN <= velocity <= self.AIR_VELOCITY_MAX:
            return ComplianceStatus.COMPLIANT
        return ComplianceStatus.OUT_OF_SPEC

    def _check_spectral_compliance(self, spectral_data: SpectralData) -> bool:
        """Check if spectral distribution meets requirements"""
        compliant = True

        # Check peak wavelength
        peak_min = self.PEAK_WAVELENGTH_TARGET - self.PEAK_WAVELENGTH_TOLERANCE
        peak_max = self.PEAK_WAVELENGTH_TARGET + self.PEAK_WAVELENGTH_TOLERANCE

        if not (peak_min <= spectral_data.peak_wavelength <= peak_max):
            logger.warning(
                f"Peak wavelength {spectral_data.peak_wavelength:.1f} nm is out of spec "
                f"(target: {self.PEAK_WAVELENGTH_TARGET} ± {self.PEAK_WAVELENGTH_TOLERANCE} nm)"
            )
            compliant = False

        # Check UVB percentage
        if not (self.UVB_PERCENTAGE_MIN <= spectral_data.uv_b_percentage <= self.UVB_PERCENTAGE_MAX):
            logger.warning(
                f"UVB percentage {spectral_data.uv_b_percentage:.1f}% is out of spec "
                f"(target: {self.UVB_PERCENTAGE_MIN}-{self.UVB_PERCENTAGE_MAX}%)"
            )
            compliant = False

        # Check UVA percentage
        if not (self.UVA_PERCENTAGE_MIN <= spectral_data.uv_a_percentage <= self.UVA_PERCENTAGE_MAX):
            logger.warning(
                f"UVA percentage {spectral_data.uv_a_percentage:.1f}% is out of spec "
                f"(target: {self.UVA_PERCENTAGE_MIN}-{self.UVA_PERCENTAGE_MAX}%)"
            )
            compliant = False

        return compliant

    def complete_test_session(self) -> TestSession:
        """
        Complete the current test session

        Returns:
            Completed TestSession object
        """
        if not self.current_session:
            raise ValueError("No active test session")

        self.current_session.end_time = datetime.now()
        self.current_session.status = TestStatus.COMPLETED

        # Final statistics update
        self._update_session_statistics()

        logger.info(
            f"Completed session {self.current_session.session_id}: "
            f"{self.current_session.cumulative_uv_dose:.2f} kWh/m² "
            f"in {self.current_session.total_exposure_time:.1f} hours"
        )

        return self.current_session

    def abort_test_session(self, reason: str = "") -> TestSession:
        """
        Abort the current test session

        Args:
            reason: Reason for aborting

        Returns:
            Aborted TestSession object
        """
        if not self.current_session:
            raise ValueError("No active test session")

        self.current_session.end_time = datetime.now()
        self.current_session.status = TestStatus.ABORTED
        self.current_session.notes += f"\nAborted: {reason}"

        logger.warning(f"Aborted session {self.current_session.session_id}: {reason}")

        return self.current_session

    def export_session_data(self, output_path: Path) -> Path:
        """
        Export session data to JSON file

        Args:
            output_path: Path for output JSON file

        Returns:
            Path to created file
        """
        if not self.current_session:
            raise ValueError("No active test session")

        data = self.current_session.to_dict()

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Exported session data to {output_path}")
        return output_path

    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get summary of current test session

        Returns:
            Dictionary with session summary metrics
        """
        if not self.current_session:
            return {}

        summary = {
            'session_id': self.current_session.session_id,
            'sample_id': self.current_session.sample_id,
            'status': self.current_session.status.value,
            'cumulative_dose': self.current_session.cumulative_uv_dose,
            'target_dose': self.TARGET_UV_DOSE,
            'completion_percentage': self.get_dose_completion_percentage(),
            'remaining_dose': self.get_remaining_dose(),
            'total_exposure_time': self.current_session.total_exposure_time,
            'average_irradiance': self.current_session.average_irradiance,
            'estimated_remaining_time': self.estimate_remaining_time(),
            'measurement_counts': {
                'irradiance': len(self.current_session.irradiance_measurements),
                'environmental': len(self.current_session.environmental_measurements),
                'spectral': len(self.current_session.spectral_measurements)
            }
        }

        # Add degradation if post-test data exists
        degradation = self.calculate_power_degradation()
        if degradation is not None:
            summary['power_degradation'] = degradation
            summary['acceptance_criteria'] = self.check_acceptance_criteria()

        return summary
