"""SALT-001: Salt Mist Corrosion Test Protocol (IEC 61701)."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from test_protocols.constants import (
    IEC_61701_HUMIDITY_MAX,
    IEC_61701_HUMIDITY_MIN,
    IEC_61701_SALT_CONCENTRATION_MAX,
    IEC_61701_SALT_CONCENTRATION_MIN,
    IEC_61701_SEVERITY_LEVEL_1,
    IEC_61701_SEVERITY_LEVEL_2,
    IEC_61701_SEVERITY_LEVEL_3,
    IEC_61701_SEVERITY_LEVEL_4,
    IEC_61701_SEVERITY_LEVEL_5,
    IEC_61701_TEMP_MAX,
    IEC_61701_TEMP_MIN,
    IV_MEASUREMENT_TOLERANCE,
    MAX_DEGRADATION_THRESHOLD,
    SALT_MIST_CYCLE_DRY_DURATION,
    SALT_MIST_CYCLE_SPRAY_DURATION,
    CorrosionRating,
    ProtocolCategory,
    QCStatus,
)
from test_protocols.logger import setup_logger
from test_protocols.protocols.base import (
    BaseProtocol,
    ProtocolMetadata,
    QualityCheckResult,
    ValidationError,
)

logger = setup_logger(__name__)


class SALT001Protocol(BaseProtocol):
    """SALT-001: Salt Mist Corrosion Test Protocol.

    Implementation of IEC 61701 standard for photovoltaic module salt mist
    corrosion testing. This protocol includes:
    - Automated cycle management (spray/dry cycles)
    - Corrosion progression tracking
    - Visual inspection logging with image capture
    - I-V curve measurements and degradation analysis
    - Real-time environmental monitoring
    """

    # Severity level mapping (hours)
    SEVERITY_LEVELS = {
        "Level 1 - 60 hours": IEC_61701_SEVERITY_LEVEL_1,
        "Level 2 - 120 hours": IEC_61701_SEVERITY_LEVEL_2,
        "Level 3 - 240 hours": IEC_61701_SEVERITY_LEVEL_3,
        "Level 4 - 480 hours": IEC_61701_SEVERITY_LEVEL_4,
        "Level 5 - 840 hours": IEC_61701_SEVERITY_LEVEL_5,
    }

    def __init__(self):
        """Initialize SALT-001 protocol."""
        metadata = ProtocolMetadata(
            code="SALT-001",
            name="Salt Mist Corrosion Test",
            version="1.0.0",
            description=(
                "IEC 61701 - Photovoltaic (PV) modules - Salt mist corrosion testing. "
                "Evaluates the ability of PV modules to withstand exposure to salt mist corrosion."
            ),
            category=ProtocolCategory.ENVIRONMENTAL,
            standard="IEC 61701:2020",
        )
        super().__init__(metadata)

        self.cycle_log: List[Dict[str, Any]] = []
        self.iv_measurements: List[Dict[str, Any]] = []
        self.visual_inspections: List[Dict[str, Any]] = []
        self.environmental_log: List[Dict[str, Any]] = []

    def validate_inputs(self, data: Dict[str, Any]) -> bool:
        """Validate protocol input parameters.

        Args:
            data: Input parameters including:
                - specimen_id: Unique specimen identifier
                - severity_level: IEC 61701 severity level
                - salt_concentration: NaCl concentration (%)
                - chamber_temperature: Chamber temp (°C)
                - relative_humidity: Humidity (%)
                - spray_duration: Spray phase duration (hours)
                - dry_duration: Dry phase duration (hours)

        Returns:
            bool: True if all validations pass
        """
        self.validation_errors.clear()

        # Required fields
        required_fields = [
            "specimen_id",
            "severity_level",
            "salt_concentration",
            "chamber_temperature",
            "relative_humidity",
        ]

        for field in required_fields:
            if field not in data or data[field] is None:
                self.validation_errors.append(
                    ValidationError(
                        field=field,
                        value=None,
                        message=f"Required field '{field}' is missing",
                        code="REQUIRED_FIELD",
                    )
                )

        if self.validation_errors:
            return False

        # Validate specimen ID format
        specimen_id = data.get("specimen_id", "")
        if not isinstance(specimen_id, str) or len(specimen_id) == 0:
            self.validation_errors.append(
                ValidationError(
                    field="specimen_id",
                    value=specimen_id,
                    message="Specimen ID must be a non-empty string",
                    code="INVALID_FORMAT",
                )
            )

        # Validate severity level
        severity_level = data.get("severity_level", "")
        if severity_level not in self.SEVERITY_LEVELS:
            self.validation_errors.append(
                ValidationError(
                    field="severity_level",
                    value=severity_level,
                    message=f"Invalid severity level. Must be one of: {list(self.SEVERITY_LEVELS.keys())}",
                    code="INVALID_VALUE",
                )
            )

        # Validate salt concentration (IEC 61701: 5.0 ± 0.5%)
        salt_conc = data.get("salt_concentration", 0)
        if not (IEC_61701_SALT_CONCENTRATION_MIN <= salt_conc <= IEC_61701_SALT_CONCENTRATION_MAX):
            self.validation_errors.append(
                ValidationError(
                    field="salt_concentration",
                    value=salt_conc,
                    message=(
                        f"Salt concentration must be between "
                        f"{IEC_61701_SALT_CONCENTRATION_MIN}% and "
                        f"{IEC_61701_SALT_CONCENTRATION_MAX}% (IEC 61701)"
                    ),
                    code="OUT_OF_RANGE",
                )
            )

        # Validate chamber temperature (IEC 61701: 35 ± 1°C)
        temp = data.get("chamber_temperature", 0)
        if not (IEC_61701_TEMP_MIN <= temp <= IEC_61701_TEMP_MAX):
            self.validation_errors.append(
                ValidationError(
                    field="chamber_temperature",
                    value=temp,
                    message=(
                        f"Chamber temperature must be between "
                        f"{IEC_61701_TEMP_MIN}°C and {IEC_61701_TEMP_MAX}°C (IEC 61701)"
                    ),
                    code="OUT_OF_RANGE",
                )
            )

        # Validate relative humidity (IEC 61701: 95 ± 2%)
        humidity = data.get("relative_humidity", 0)
        if not (IEC_61701_HUMIDITY_MIN <= humidity <= IEC_61701_HUMIDITY_MAX):
            self.validation_errors.append(
                ValidationError(
                    field="relative_humidity",
                    value=humidity,
                    message=(
                        f"Relative humidity must be between "
                        f"{IEC_61701_HUMIDITY_MIN}% and {IEC_61701_HUMIDITY_MAX}% (IEC 61701)"
                    ),
                    code="OUT_OF_RANGE",
                )
            )

        # Validate spray and dry durations
        spray_duration = data.get("spray_duration", SALT_MIST_CYCLE_SPRAY_DURATION)
        dry_duration = data.get("dry_duration", SALT_MIST_CYCLE_DRY_DURATION)

        if spray_duration + dry_duration != 24.0:
            self.validation_errors.append(
                ValidationError(
                    field="cycle_duration",
                    value=spray_duration + dry_duration,
                    message="Total cycle duration (spray + dry) must equal 24 hours",
                    code="INVALID_CYCLE",
                )
            )

        return len(self.validation_errors) == 0

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute SALT-001 protocol.

        This method sets up the test parameters and initializes tracking
        structures. Actual test execution is managed through cycle updates.

        Args:
            data: Protocol execution parameters

        Returns:
            Dict[str, Any]: Execution setup results

        Raises:
            ValueError: If input validation fails
        """
        # Validate inputs
        if not self.validate_inputs(data):
            raise ValueError(f"Input validation failed:\n{self.get_validation_summary()}")

        logger.info(f"Executing SALT-001 protocol for specimen: {data['specimen_id']}")

        # Calculate total duration based on severity level
        severity_level = data["severity_level"]
        total_hours = self.SEVERITY_LEVELS[severity_level]
        total_cycles = int(total_hours / 24)

        # Initialize test
        self.results = {
            "specimen_id": data["specimen_id"],
            "module_type": data.get("module_type", "Unknown"),
            "manufacturer": data.get("manufacturer", "Unknown"),
            "rated_power": data.get("rated_power"),
            "severity_level": severity_level,
            "total_duration_hours": total_hours,
            "total_cycles": total_cycles,
            "parameters": {
                "salt_concentration": data["salt_concentration"],
                "chamber_temperature": data["chamber_temperature"],
                "relative_humidity": data["relative_humidity"],
                "spray_duration": data.get("spray_duration", SALT_MIST_CYCLE_SPRAY_DURATION),
                "dry_duration": data.get("dry_duration", SALT_MIST_CYCLE_DRY_DURATION),
            },
            "iv_measurement_intervals": data.get("iv_measurement_intervals", [0, 60, 120, 180, 240]),
            "visual_inspection_intervals": data.get(
                "visual_inspection_intervals", [0, 24, 48, 96, 144, 192, 240]
            ),
            "start_time": datetime.now().isoformat(),
            "status": "initialized",
        }

        logger.info(
            f"Test initialized: {total_cycles} cycles ({total_hours} hours), "
            f"Severity Level: {severity_level}"
        )

        return self.results

    def update_cycle(
        self,
        cycle_number: int,
        phase: str,
        temperature: float,
        humidity: float,
        salt_concentration: Optional[float] = None,
        spray_rate: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Update cycle progress with environmental measurements.

        Args:
            cycle_number: Current cycle number (1-indexed)
            phase: Current phase ('spray' or 'dry')
            temperature: Measured chamber temperature (°C)
            humidity: Measured relative humidity (%)
            salt_concentration: Measured salt concentration (%, optional)
            spray_rate: Measured spray rate (mL/h/80cm², optional)

        Returns:
            Dict[str, Any]: Cycle update result with QC status
        """
        cycle_data = {
            "cycle_number": cycle_number,
            "phase": phase,
            "timestamp": datetime.now().isoformat(),
            "temperature": temperature,
            "humidity": humidity,
            "salt_concentration": salt_concentration,
            "spray_rate": spray_rate,
        }

        # Perform real-time QC checks
        qc_checks = self._check_environmental_conditions(
            temperature, humidity, salt_concentration, spray_rate
        )
        cycle_data["qc_status"] = qc_checks["status"]
        cycle_data["qc_messages"] = qc_checks["messages"]

        self.cycle_log.append(cycle_data)
        self.environmental_log.append(cycle_data)

        logger.info(
            f"Cycle {cycle_number} ({phase}): "
            f"T={temperature}°C, RH={humidity}%, QC={qc_checks['status']}"
        )

        return cycle_data

    def record_iv_measurement(
        self,
        elapsed_hours: float,
        voltage: List[float],
        current: List[float],
        irradiance: float = 1000.0,
        temperature: float = 25.0,
    ) -> Dict[str, Any]:
        """Record I-V curve measurement.

        Args:
            elapsed_hours: Hours elapsed since test start
            voltage: Voltage points (V)
            current: Current points (A)
            irradiance: Irradiance level (W/m²), default 1000
            temperature: Module temperature (°C), default 25

        Returns:
            Dict[str, Any]: I-V measurement results including calculated parameters
        """
        voltage_array = np.array(voltage)
        current_array = np.array(current)
        power_array = voltage_array * current_array

        # Calculate key parameters
        max_power_idx = np.argmax(power_array)
        max_power = power_array[max_power_idx]
        voc = voltage_array[-1]  # Open circuit voltage (last point)
        isc = current_array[0]  # Short circuit current (first point)
        fill_factor = (max_power / (voc * isc)) * 100 if (voc * isc) > 0 else 0

        # Calculate degradation if initial measurement exists
        degradation = 0.0
        if self.iv_measurements:
            initial_power = self.iv_measurements[0]["max_power"]
            degradation = ((initial_power - max_power) / initial_power) * 100 if initial_power > 0 else 0

        iv_data = {
            "elapsed_hours": elapsed_hours,
            "timestamp": datetime.now().isoformat(),
            "voltage": voltage,
            "current": current,
            "power": power_array.tolist(),
            "max_power": float(max_power),
            "voc": float(voc),
            "isc": float(isc),
            "fill_factor": float(fill_factor),
            "degradation_percent": float(degradation),
            "irradiance": irradiance,
            "temperature": temperature,
        }

        self.iv_measurements.append(iv_data)

        logger.info(
            f"I-V measurement at {elapsed_hours}h: "
            f"Pmax={max_power:.2f}W, Degradation={degradation:.2f}%"
        )

        return iv_data

    def record_visual_inspection(
        self,
        elapsed_hours: float,
        corrosion_rating: str,
        image_path: Optional[str] = None,
        notes: Optional[str] = None,
        affected_area_percent: float = 0.0,
    ) -> Dict[str, Any]:
        """Record visual inspection results.

        Args:
            elapsed_hours: Hours elapsed since test start
            corrosion_rating: IEC 61701 corrosion rating (0-5)
            image_path: Path to inspection image
            notes: Inspection notes
            affected_area_percent: Percentage of area affected by corrosion

        Returns:
            Dict[str, Any]: Visual inspection record
        """
        inspection_data = {
            "elapsed_hours": elapsed_hours,
            "timestamp": datetime.now().isoformat(),
            "corrosion_rating": corrosion_rating,
            "affected_area_percent": affected_area_percent,
            "image_path": image_path,
            "notes": notes or "",
        }

        self.visual_inspections.append(inspection_data)

        logger.info(
            f"Visual inspection at {elapsed_hours}h: "
            f"Rating={corrosion_rating}, Affected={affected_area_percent:.1f}%"
        )

        return inspection_data

    def quality_check(self, results: Dict[str, Any]) -> QCStatus:
        """Perform comprehensive quality control checks.

        Args:
            results: Test results to check

        Returns:
            QCStatus: Overall QC status
        """
        self.qc_results.clear()

        # Check if we have environmental data
        if not self.environmental_log:
            logger.warning("No environmental data available for QC checks")
            return QCStatus.PENDING

        # Aggregate environmental data
        temperatures = [log["temperature"] for log in self.environmental_log]
        humidities = [log["humidity"] for log in self.environmental_log]
        salt_concs = [
            log["salt_concentration"]
            for log in self.environmental_log
            if log.get("salt_concentration") is not None
        ]

        # Temperature QC
        avg_temp = np.mean(temperatures)
        temp_check = QualityCheckResult(
            check_name="chamber_temperature",
            parameter="temperature",
            expected_range=[IEC_61701_TEMP_MIN, IEC_61701_TEMP_MAX],
            actual_value=avg_temp,
            passed=(IEC_61701_TEMP_MIN <= avg_temp <= IEC_61701_TEMP_MAX),
            tolerance=1.0,
            unit="°C",
            message=f"Average temperature: {avg_temp:.2f}°C",
        )
        self.qc_results.append(temp_check)

        # Humidity QC
        avg_humidity = np.mean(humidities)
        humidity_check = QualityCheckResult(
            check_name="relative_humidity",
            parameter="humidity",
            expected_range=[IEC_61701_HUMIDITY_MIN, IEC_61701_HUMIDITY_MAX],
            actual_value=avg_humidity,
            passed=(IEC_61701_HUMIDITY_MIN <= avg_humidity <= IEC_61701_HUMIDITY_MAX),
            tolerance=2.0,
            unit="%",
            message=f"Average humidity: {avg_humidity:.2f}%",
        )
        self.qc_results.append(humidity_check)

        # Salt concentration QC
        if salt_concs:
            avg_salt = np.mean(salt_concs)
            salt_check = QualityCheckResult(
                check_name="salt_concentration",
                parameter="salt_concentration",
                expected_range=[
                    IEC_61701_SALT_CONCENTRATION_MIN,
                    IEC_61701_SALT_CONCENTRATION_MAX,
                ],
                actual_value=avg_salt,
                passed=(
                    IEC_61701_SALT_CONCENTRATION_MIN
                    <= avg_salt
                    <= IEC_61701_SALT_CONCENTRATION_MAX
                ),
                tolerance=0.5,
                unit="%",
                message=f"Average salt concentration: {avg_salt:.2f}%",
            )
            self.qc_results.append(salt_check)

        # Power degradation QC
        if self.iv_measurements and len(self.iv_measurements) > 1:
            final_degradation = self.iv_measurements[-1]["degradation_percent"]
            degradation_check = QualityCheckResult(
                check_name="power_degradation",
                parameter="degradation",
                expected_range=[0, MAX_DEGRADATION_THRESHOLD],
                actual_value=final_degradation,
                passed=(final_degradation <= MAX_DEGRADATION_THRESHOLD),
                tolerance=1.0,
                unit="%",
                message=f"Power degradation: {final_degradation:.2f}%",
            )
            self.qc_results.append(degradation_check)

        # Determine overall status
        all_passed = all(qc.passed for qc in self.qc_results)
        critical_failed = any(
            not qc.passed for qc in self.qc_results if qc.check_name in ["chamber_temperature", "relative_humidity"]
        )

        if all_passed:
            return QCStatus.PASS
        elif critical_failed:
            return QCStatus.FAIL
        else:
            return QCStatus.WARNING

    def calculate_metrics(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate derived metrics from test data.

        Args:
            data: Test data

        Returns:
            Dict[str, float]: Calculated metrics
        """
        metrics = {}

        if self.iv_measurements:
            # Initial and final power
            initial_power = self.iv_measurements[0]["max_power"]
            final_power = self.iv_measurements[-1]["max_power"]

            metrics["initial_power_w"] = initial_power
            metrics["final_power_w"] = final_power
            metrics["power_loss_w"] = initial_power - final_power
            metrics["power_degradation_percent"] = (
                ((initial_power - final_power) / initial_power * 100) if initial_power > 0 else 0
            )

            # Average fill factor
            fill_factors = [iv["fill_factor"] for iv in self.iv_measurements]
            metrics["avg_fill_factor_percent"] = np.mean(fill_factors)

        if self.visual_inspections:
            # Final corrosion rating
            final_inspection = self.visual_inspections[-1]
            metrics["final_corrosion_rating"] = int(
                final_inspection["corrosion_rating"].split(" - ")[0]
            )
            metrics["final_affected_area_percent"] = final_inspection["affected_area_percent"]

        if self.environmental_log:
            # Environmental stability
            temperatures = [log["temperature"] for log in self.environmental_log]
            humidities = [log["humidity"] for log in self.environmental_log]

            metrics["avg_temperature_c"] = np.mean(temperatures)
            metrics["temp_std_dev"] = np.std(temperatures)
            metrics["avg_humidity_percent"] = np.mean(humidities)
            metrics["humidity_std_dev"] = np.std(humidities)

        return metrics

    def _check_environmental_conditions(
        self,
        temperature: float,
        humidity: float,
        salt_concentration: Optional[float],
        spray_rate: Optional[float],
    ) -> Dict[str, Any]:
        """Check environmental conditions against IEC 61701 limits.

        Args:
            temperature: Chamber temperature (°C)
            humidity: Relative humidity (%)
            salt_concentration: Salt concentration (%)
            spray_rate: Spray rate (mL/h/80cm²)

        Returns:
            Dict[str, Any]: QC check results
        """
        messages = []
        status = "PASS"

        # Temperature check
        if not (IEC_61701_TEMP_MIN <= temperature <= IEC_61701_TEMP_MAX):
            messages.append(
                f"Temperature {temperature}°C out of range "
                f"[{IEC_61701_TEMP_MIN}, {IEC_61701_TEMP_MAX}]"
            )
            status = "FAIL"

        # Humidity check
        if not (IEC_61701_HUMIDITY_MIN <= humidity <= IEC_61701_HUMIDITY_MAX):
            messages.append(
                f"Humidity {humidity}% out of range "
                f"[{IEC_61701_HUMIDITY_MIN}, {IEC_61701_HUMIDITY_MAX}]"
            )
            status = "FAIL"

        # Salt concentration check
        if salt_concentration is not None:
            if not (
                IEC_61701_SALT_CONCENTRATION_MIN
                <= salt_concentration
                <= IEC_61701_SALT_CONCENTRATION_MAX
            ):
                messages.append(
                    f"Salt concentration {salt_concentration}% out of range "
                    f"[{IEC_61701_SALT_CONCENTRATION_MIN}, "
                    f"{IEC_61701_SALT_CONCENTRATION_MAX}]"
                )
                status = "WARNING"

        # Spray rate check (typical range: 1.0-2.0 mL/h/80cm²)
        if spray_rate is not None:
            if not (1.0 <= spray_rate <= 2.0):
                messages.append(f"Spray rate {spray_rate} mL/h/80cm² out of typical range [1.0, 2.0]")
                status = "WARNING" if status == "PASS" else status

        if not messages:
            messages.append("All environmental conditions within specifications")

        return {"status": status, "messages": messages}

    def get_test_summary(self) -> Dict[str, Any]:
        """Get comprehensive test summary.

        Returns:
            Dict[str, Any]: Test summary with all key metrics
        """
        return {
            "metadata": self.metadata.__dict__,
            "results": self.results,
            "metrics": self.calculate_metrics(self.results),
            "qc_status": self.quality_check(self.results).value,
            "qc_summary": self.get_qc_summary(),
            "total_cycles": len(self.cycle_log),
            "total_iv_measurements": len(self.iv_measurements),
            "total_visual_inspections": len(self.visual_inspections),
            "environmental_data_points": len(self.environmental_log),
        }


def load_protocol_template() -> Dict[str, Any]:
    """Load SALT-001 protocol template from JSON file.

    Returns:
        Dict[str, Any]: Protocol template
    """
    template_path = Path(__file__).parent.parent.parent.parent / "templates" / "protocols" / "salt-001.json"

    if not template_path.exists():
        logger.warning(f"Template file not found: {template_path}")
        return {}

    with open(template_path, "r") as f:
        return json.load(f)
