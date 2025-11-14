"""Snow Load Testing Protocol Implementation - SNOW-001

Implementation of snow load testing according to IEC 61215-1:2016 Part 1
for photovoltaic modules.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
from datetime import datetime
import logging
import math

from protocols.base.protocol import BaseProtocol, Step, StepResult
from protocols.base.validators import validate_range, validate_positive, validate_non_negative


logger = logging.getLogger(__name__)


class LoadPhase(Enum):
    """Phases of snow load application"""
    BASELINE = "baseline"
    LOADING = "loading"
    HOLD = "hold"
    UNLOADING = "unloading"
    RECOVERY = "recovery"


class VisualCondition(Enum):
    """Visual inspection conditions"""
    NORMAL = "normal"
    MICRO_CRACK = "micro_crack"
    HAIRLINE_CRACK = "hairline_crack"
    VISIBLE_CRACK = "visible_crack"
    DELAMINATION = "delamination"
    FRAME_DAMAGE = "frame_damage"
    GLASS_BREAKAGE = "glass_breakage"


@dataclass
class ModuleSpecs:
    """PV Module specifications"""
    module_id: str
    length_mm: float
    width_mm: float
    thickness_mm: float
    mass_kg: float
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    frame_type: str = "aluminum"
    rated_power_w: Optional[float] = None

    def validate(self):
        """Validate module specifications"""
        validate_positive("length_mm", self.length_mm)
        validate_positive("width_mm", self.width_mm)
        validate_positive("thickness_mm", self.thickness_mm)
        validate_positive("mass_kg", self.mass_kg)
        if self.rated_power_w is not None:
            validate_positive("rated_power_w", self.rated_power_w)

    @property
    def area_m2(self) -> float:
        """Calculate module area in m²"""
        return (self.length_mm * self.width_mm) / 1_000_000


@dataclass
class SnowLoadTestConfig:
    """Configuration for snow load test"""
    snow_load_pa: float  # Target snow load in Pascals
    hold_duration_hours: float
    cycles: int = 1
    test_temperature_c: float = 23.0
    test_humidity_pct: float = 50.0
    load_application_rate: float = 10.0  # kg/m²/minute
    support_configuration: str = "4-point"

    # Acceptance criteria
    max_deflection_mm: float = 50.0
    max_permanent_deflection_mm: float = 5.0
    max_cracking: str = "none"
    min_performance_retention_pct: float = 95.0
    visual_inspection_required: bool = True
    electrical_test_required: bool = False

    def validate(self):
        """Validate configuration parameters"""
        validate_range("snow_load_pa", self.snow_load_pa, 0, 10000)
        validate_range("hold_duration_hours", self.hold_duration_hours, 0.5, 48)
        validate_range("cycles", self.cycles, 1, 10)
        validate_range("test_temperature_c", self.test_temperature_c, -70, 60)
        validate_range("test_humidity_pct", self.test_humidity_pct, 0, 100)
        validate_positive("load_application_rate", self.load_application_rate)
        validate_non_negative("max_deflection_mm", self.max_deflection_mm)
        validate_non_negative("max_permanent_deflection_mm", self.max_permanent_deflection_mm)
        validate_range("min_performance_retention_pct", self.min_performance_retention_pct, 0, 100)

    @property
    def snow_load_kg_m2(self) -> float:
        """Convert Pa to kg/m² (1 Pa ≈ 0.102 kg/m²)"""
        return self.snow_load_pa * 0.102


@dataclass
class MeasurementPoint:
    """Single measurement at a point in time"""
    timestamp: datetime
    phase: LoadPhase
    load_applied_pa: float
    deflection_mm: float
    visual_condition: VisualCondition = VisualCondition.NORMAL
    temperature_c: Optional[float] = None
    humidity_pct: Optional[float] = None
    electrical_power_w: Optional[float] = None
    notes: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "phase": self.phase.value,
            "load_applied_pa": self.load_applied_pa,
            "load_applied_kg_m2": self.load_applied_pa * 0.102,
            "deflection_mm": self.deflection_mm,
            "visual_condition": self.visual_condition.value,
            "temperature_c": self.temperature_c,
            "humidity_pct": self.humidity_pct,
            "electrical_power_w": self.electrical_power_w,
            "notes": self.notes
        }


class SnowLoadTestProtocol(BaseProtocol):
    """
    Implements snow load testing according to IEC 61215-1:2016 Part 1.

    Test procedure:
    1. Baseline measurement (no load)
    2. Apply snow load gradually
    3. Hold under load for specified duration
    4. Unload gradually
    5. Recovery measurement
    6. Visual inspection
    7. Optional electrical testing

    Repeat for specified number of cycles.
    """

    PROTOCOL_ID = "SNOW-001"
    STANDARD = "IEC 61215-1:2016, Part 1 - Mechanical Load Test"

    def __init__(self, config: SnowLoadTestConfig, module_specs: ModuleSpecs):
        """Initialize protocol with configuration and module specs"""
        super().__init__()

        # Validate inputs
        config.validate()
        module_specs.validate()

        self.config = config
        self.module_specs = module_specs
        self.measurements: List[MeasurementPoint] = []
        self.current_cycle = 0
        self.baseline_deflection = 0.0
        self.max_deflection_observed = 0.0

    def execute(self) -> bool:
        """Execute full test protocol"""
        try:
            logger.info(f"Starting snow load test SNOW-001 for module {self.module_specs.module_id}")
            logger.info(f"Target load: {self.config.snow_load_pa} Pa ({self.config.snow_load_kg_m2:.1f} kg/m²)")
            self.test_start_time = datetime.now()

            for cycle in range(self.config.cycles):
                self.current_cycle = cycle + 1
                logger.info(f"=== Cycle {self.current_cycle}/{self.config.cycles} ===")

                # Step 1: Baseline measurements
                self._baseline_measurement()

                # Step 2: Load application
                self._apply_load()

                # Step 3: Hold under load
                self._hold_under_load()

                # Step 4: Unload
                self._unload()

                # Step 5: Recovery measurement
                self._recovery_measurement()

                # Step 6: Visual inspection
                self._visual_inspection()

                # Optional: Electrical test
                if self.config.electrical_test_required:
                    self._electrical_test()

                # Wait between cycles if multiple
                if self.current_cycle < self.config.cycles:
                    self._wait_recovery_period()

            # Final evaluation
            self.test_end_time = datetime.now()
            self.test_result = self.evaluate_results()

            logger.info(f"Test completed. Result: {'PASS' if self.test_result else 'FAIL'}")
            return self.test_result

        except Exception as e:
            logger.error(f"Test execution failed: {e}", exc_info=True)
            self.test_result = False
            raise

    def _baseline_measurement(self) -> StepResult:
        """Record baseline measurements before load"""
        step = Step(
            name="Baseline Measurement",
            step_type="baseline_measurement",
            description="Record initial module condition before snow load application"
        )
        step.start()

        try:
            # Measure deflection with no load
            deflection = self._measure_deflection(load_pa=0)
            self.baseline_deflection = deflection

            self._record_measurement(
                load_applied_pa=0,
                deflection_mm=deflection,
                phase=LoadPhase.BASELINE,
                visual_condition=VisualCondition.NORMAL
            )

            step.mark_complete(success=True, data={
                "baseline_deflection_mm": deflection
            })
            logger.info(f"Baseline deflection: {deflection:.2f} mm")

        except Exception as e:
            logger.error(f"Baseline measurement failed: {e}")
            step.mark_complete(success=False, error=str(e))
            raise

        self.add_step(step)
        return step.result

    def _apply_load(self) -> StepResult:
        """Apply snow load at configured rate"""
        step = Step(
            name="Load Application",
            step_type="load_application",
            description=f"Apply {self.config.snow_load_pa} Pa at {self.config.load_application_rate} kg/m²/min"
        )
        step.start()

        try:
            # Calculate time to reach full load
            load_kg_m2 = self.config.snow_load_kg_m2
            load_time_minutes = load_kg_m2 / self.config.load_application_rate

            # Take measurements at intervals during loading
            num_measurement_points = max(int(load_time_minutes / 5), 3)  # At least 3 points

            for i in range(1, num_measurement_points + 1):
                progress = i / num_measurement_points
                current_load_pa = self.config.snow_load_pa * progress

                deflection = self._measure_deflection(load_pa=current_load_pa)
                self.max_deflection_observed = max(self.max_deflection_observed, deflection)

                self._record_measurement(
                    load_applied_pa=current_load_pa,
                    deflection_mm=deflection,
                    phase=LoadPhase.LOADING
                )

            step.mark_complete(success=True, data={
                "final_load_pa": self.config.snow_load_pa,
                "final_deflection_mm": deflection,
                "measurement_points": num_measurement_points
            })
            logger.info(f"Load applied: {self.config.snow_load_pa} Pa, deflection: {deflection:.2f} mm")

        except Exception as e:
            logger.error(f"Load application failed: {e}")
            step.mark_complete(success=False, error=str(e))
            raise

        self.add_step(step)
        return step.result

    def _hold_under_load(self) -> StepResult:
        """Hold module under full snow load"""
        step = Step(
            name="Hold Under Load",
            step_type="hold",
            description=f"Maintain {self.config.snow_load_pa} Pa for {self.config.hold_duration_hours} hours"
        )
        step.start()

        try:
            # Take measurements periodically during hold
            hold_intervals = max(int(self.config.hold_duration_hours), 1)

            for i in range(hold_intervals):
                deflection = self._measure_deflection(load_pa=self.config.snow_load_pa)
                self.max_deflection_observed = max(self.max_deflection_observed, deflection)

                self._record_measurement(
                    load_applied_pa=self.config.snow_load_pa,
                    deflection_mm=deflection,
                    phase=LoadPhase.HOLD
                )

            step.mark_complete(success=True, data={
                "hold_duration_hours": self.config.hold_duration_hours,
                "measurement_points": hold_intervals
            })
            logger.info(f"Held load for {self.config.hold_duration_hours} hours")

        except Exception as e:
            logger.error(f"Hold phase failed: {e}")
            step.mark_complete(success=False, error=str(e))
            raise

        self.add_step(step)
        return step.result

    def _unload(self) -> StepResult:
        """Gradually remove snow load"""
        step = Step(
            name="Unload",
            step_type="unload",
            description="Gradually remove applied snow load"
        )
        step.start()

        try:
            # Unload in steps
            num_steps = 5
            for i in range(1, num_steps + 1):
                progress = 1 - (i / num_steps)
                current_load_pa = self.config.snow_load_pa * progress

                deflection = self._measure_deflection(load_pa=current_load_pa)

                self._record_measurement(
                    load_applied_pa=current_load_pa,
                    deflection_mm=deflection,
                    phase=LoadPhase.UNLOADING
                )

            step.mark_complete(success=True, data={
                "unload_steps": num_steps
            })
            logger.info("Load removed")

        except Exception as e:
            logger.error(f"Unload failed: {e}")
            step.mark_complete(success=False, error=str(e))
            raise

        self.add_step(step)
        return step.result

    def _recovery_measurement(self) -> StepResult:
        """Record measurements after load removal"""
        step = Step(
            name="Recovery Measurement",
            step_type="recovery_measurement",
            description="Measure module condition after load removal"
        )
        step.start()

        try:
            deflection = self._measure_deflection(load_pa=0)
            permanent_deflection = deflection - self.baseline_deflection

            self._record_measurement(
                load_applied_pa=0,
                deflection_mm=deflection,
                phase=LoadPhase.RECOVERY,
                notes=f"Permanent deflection: {permanent_deflection:.2f} mm"
            )

            step.mark_complete(success=True, data={
                "recovery_deflection_mm": deflection,
                "permanent_deflection_mm": permanent_deflection,
                "baseline_deflection_mm": self.baseline_deflection
            })
            logger.info(f"Recovery deflection: {deflection:.2f} mm, permanent: {permanent_deflection:.2f} mm")

        except Exception as e:
            logger.error(f"Recovery measurement failed: {e}")
            step.mark_complete(success=False, error=str(e))
            raise

        self.add_step(step)
        return step.result

    def _visual_inspection(self) -> StepResult:
        """Perform visual inspection"""
        step = Step(
            name="Visual Inspection",
            step_type="visual_inspection",
            description="Inspect module for cracks, delamination, or other damage"
        )
        step.start()

        try:
            # Simulate visual inspection
            # In real implementation, this would be operator input
            visual_condition = self._perform_visual_inspection()

            # Record with current deflection
            current_deflection = self.measurements[-1].deflection_mm if self.measurements else 0

            self._record_measurement(
                load_applied_pa=0,
                deflection_mm=current_deflection,
                phase=LoadPhase.RECOVERY,
                visual_condition=visual_condition,
                notes="Visual inspection completed"
            )

            step.mark_complete(success=True, data={
                "visual_condition": visual_condition.value
            })
            logger.info(f"Visual inspection: {visual_condition.value}")

        except Exception as e:
            logger.error(f"Visual inspection failed: {e}")
            step.mark_complete(success=False, error=str(e))
            raise

        self.add_step(step)
        return step.result

    def _electrical_test(self) -> StepResult:
        """Perform electrical performance test"""
        step = Step(
            name="Electrical Test",
            step_type="electrical_test",
            description="Measure electrical performance"
        )
        step.start()

        try:
            # Simulate electrical test
            # In real implementation, this would measure IV curve
            power_retention = self._measure_electrical_performance()

            current_deflection = self.measurements[-1].deflection_mm if self.measurements else 0

            self._record_measurement(
                load_applied_pa=0,
                deflection_mm=current_deflection,
                phase=LoadPhase.RECOVERY,
                electrical_power_w=power_retention,
                notes="Electrical test completed"
            )

            step.mark_complete(success=True, data={
                "power_retention_pct": power_retention
            })
            logger.info(f"Power retention: {power_retention:.1f}%")

        except Exception as e:
            logger.error(f"Electrical test failed: {e}")
            step.mark_complete(success=False, error=str(e))
            raise

        self.add_step(step)
        return step.result

    def _wait_recovery_period(self):
        """Wait between cycles for recovery"""
        logger.info("Waiting recovery period between cycles (30 minutes)")
        # In real implementation, this would wait
        pass

    def _measure_deflection(self, load_pa: float) -> float:
        """
        Calculate expected deflection for given load.

        Uses simplified beam deflection theory:
        δ = (F * L³) / (48 * E * I)

        For real implementation, this would interface with actual sensors.
        """
        if load_pa == 0:
            # Small random variation for baseline
            import random
            return random.uniform(0, 0.5)

        # Module properties
        area_m2 = self.module_specs.area_m2
        length_m = self.module_specs.length_mm / 1000
        thickness_m = self.module_specs.thickness_mm / 1000

        # Calculate total force
        force_n = load_pa * area_m2

        # Estimate elastic modulus for glass+frame composite (simplified)
        E_glass = 70e9  # Pa for glass
        width_m = self.module_specs.width_mm / 1000

        # Second moment of area for rectangular cross-section
        I = (width_m * thickness_m ** 3) / 12

        # Deflection calculation (simplified 4-point bending)
        deflection_m = (force_n * length_m ** 3) / (48 * E_glass * I)
        deflection_mm = deflection_m * 1000

        # Add some realistic variation
        import random
        variation = random.uniform(-0.1, 0.1) * deflection_mm

        return max(0, deflection_mm + variation)

    def _perform_visual_inspection(self) -> VisualCondition:
        """
        Perform visual inspection.

        In real implementation, this would be operator input.
        For simulation, determines condition based on observed deflection.
        """
        if self.max_deflection_observed > self.config.max_deflection_mm * 1.5:
            return VisualCondition.VISIBLE_CRACK
        elif self.max_deflection_observed > self.config.max_deflection_mm * 1.2:
            return VisualCondition.HAIRLINE_CRACK
        elif self.max_deflection_observed > self.config.max_deflection_mm:
            return VisualCondition.MICRO_CRACK
        else:
            return VisualCondition.NORMAL

    def _measure_electrical_performance(self) -> float:
        """
        Measure electrical performance.

        In real implementation, this would measure IV curve.
        Returns power retention percentage.
        """
        # Simulate power degradation based on deflection
        if self.max_deflection_observed > self.config.max_deflection_mm * 1.5:
            return 85.0  # Significant degradation
        elif self.max_deflection_observed > self.config.max_deflection_mm:
            return 92.0  # Minor degradation
        else:
            return 98.5  # Minimal degradation

    def _record_measurement(
        self,
        load_applied_pa: float,
        deflection_mm: float,
        phase: LoadPhase,
        visual_condition: VisualCondition = VisualCondition.NORMAL,
        electrical_power_w: Optional[float] = None,
        notes: str = ""
    ):
        """Record a single measurement point"""
        measurement = MeasurementPoint(
            timestamp=datetime.now(),
            phase=phase,
            load_applied_pa=load_applied_pa,
            deflection_mm=deflection_mm,
            visual_condition=visual_condition,
            temperature_c=self.config.test_temperature_c,
            humidity_pct=self.config.test_humidity_pct,
            electrical_power_w=electrical_power_w,
            notes=notes
        )
        self.measurements.append(measurement)

    def evaluate_results(self) -> bool:
        """Evaluate if module passes test criteria"""
        logger.info("=== Evaluating Test Results ===")

        if not self.measurements:
            logger.warning("No measurements recorded")
            return False

        # Check maximum deflection
        max_deflection = max(m.deflection_mm for m in self.measurements)
        logger.info(f"Max deflection: {max_deflection:.2f} mm (limit: {self.config.max_deflection_mm} mm)")

        if max_deflection > self.config.max_deflection_mm:
            logger.error(f"FAIL: Max deflection {max_deflection:.2f} mm exceeds limit {self.config.max_deflection_mm} mm")
            return False

        # Check permanent deflection
        recovery_measurements = [m for m in self.measurements if m.phase == LoadPhase.RECOVERY]
        if recovery_measurements:
            final_deflection = recovery_measurements[-1].deflection_mm
            permanent_deflection = final_deflection - self.baseline_deflection
            logger.info(f"Permanent deflection: {permanent_deflection:.2f} mm (limit: {self.config.max_permanent_deflection_mm} mm)")

            if permanent_deflection > self.config.max_permanent_deflection_mm:
                logger.error(f"FAIL: Permanent deflection {permanent_deflection:.2f} mm exceeds limit")
                return False

        # Check visual condition
        visual_measurements = [m for m in self.measurements if m.visual_condition != VisualCondition.NORMAL]
        if visual_measurements:
            worst_condition = max(visual_measurements, key=lambda m: list(VisualCondition).index(m.visual_condition))
            logger.info(f"Visual condition: {worst_condition.visual_condition.value}")

            max_allowed = VisualCondition[self.config.max_cracking.upper().replace('-', '_')]
            if list(VisualCondition).index(worst_condition.visual_condition) > list(VisualCondition).index(max_allowed):
                logger.error(f"FAIL: Visual damage exceeds acceptable level")
                return False

        # Check electrical performance if required
        if self.config.electrical_test_required:
            power_measurements = [m for m in self.measurements if m.electrical_power_w is not None]
            if power_measurements:
                min_power = min(m.electrical_power_w for m in power_measurements)
                logger.info(f"Min power retention: {min_power:.1f}% (limit: {self.config.min_performance_retention_pct}%)")

                if min_power < self.config.min_performance_retention_pct:
                    logger.error(f"FAIL: Power retention {min_power:.1f}% below limit")
                    return False

        logger.info("PASS: All acceptance criteria met")
        return True

    def get_report_data(self) -> Dict:
        """Generate report data"""
        return {
            "protocol_id": self.PROTOCOL_ID,
            "protocol_name": "Snow Load Test",
            "standard": self.STANDARD,
            "module_id": self.module_specs.module_id,
            "module_specs": {
                "manufacturer": self.module_specs.manufacturer,
                "model": self.module_specs.model,
                "serial_number": self.module_specs.serial_number,
                "dimensions_mm": {
                    "length": self.module_specs.length_mm,
                    "width": self.module_specs.width_mm,
                    "thickness": self.module_specs.thickness_mm
                },
                "mass_kg": self.module_specs.mass_kg,
                "area_m2": self.module_specs.area_m2,
                "frame_type": self.module_specs.frame_type
            },
            "test_conditions": {
                "snow_load_pa": self.config.snow_load_pa,
                "snow_load_kg_m2": self.config.snow_load_kg_m2,
                "hold_duration_hours": self.config.hold_duration_hours,
                "temperature_c": self.config.test_temperature_c,
                "humidity_pct": self.config.test_humidity_pct,
                "cycles": self.config.cycles,
                "support_configuration": self.config.support_configuration
            },
            "test_execution": {
                "start_time": self.test_start_time.isoformat() if self.test_start_time else None,
                "end_time": self.test_end_time.isoformat() if self.test_end_time else None,
                "duration_hours": self.get_total_duration(),
                "cycles_completed": self.current_cycle
            },
            "results": {
                "test_result": "PASS" if self.test_result else "FAIL",
                "max_deflection_mm": max((m.deflection_mm for m in self.measurements), default=0),
                "permanent_deflection_mm": (
                    self.measurements[-1].deflection_mm - self.baseline_deflection
                    if self.measurements else 0
                ),
                "measurements_count": len(self.measurements)
            },
            "acceptance_criteria": {
                "max_deflection_mm": self.config.max_deflection_mm,
                "max_permanent_deflection_mm": self.config.max_permanent_deflection_mm,
                "max_cracking": self.config.max_cracking,
                "min_performance_retention_pct": self.config.min_performance_retention_pct
            },
            "measurements": [m.to_dict() for m in self.measurements],
            "steps": [
                {
                    "name": step.name,
                    "type": step.step_type,
                    "status": step.status.value,
                    "duration_seconds": step.duration_seconds,
                    "success": step.result.success if step.result else None
                }
                for step in self.steps
            ]
        }
