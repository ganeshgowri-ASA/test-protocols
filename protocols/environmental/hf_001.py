"""HF-001 Humidity Freeze Test Protocol

Implementation of IEC 61215 MQT 12 Humidity Freeze test protocol
for photovoltaic module qualification testing.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import logging

import numpy as np
import pandas as pd
from pydantic import BaseModel, Field

from protocols.base import BaseProtocol, MeasurementPoint, TestResult


logger = logging.getLogger(__name__)


class IVCurveData(BaseModel):
    """I-V Curve measurement data"""
    timestamp: datetime
    irradiance: float = Field(description="W/m²")
    module_temp: float = Field(description="°C")
    voltage: List[float] = Field(description="Voltage points (V)")
    current: List[float] = Field(description="Current points (A)")
    Voc: float = Field(description="Open circuit voltage (V)")
    Isc: float = Field(description="Short circuit current (A)")
    Vmp: float = Field(description="Max power point voltage (V)")
    Imp: float = Field(description="Max power point current (A)")
    Pmax: float = Field(description="Maximum power (W)")
    FF: float = Field(description="Fill factor")


class CycleData(BaseModel):
    """Single cycle monitoring data"""
    cycle_number: int
    start_time: datetime
    end_time: Optional[datetime] = None
    temperature_log: List[Tuple[datetime, float]] = []
    humidity_log: List[Tuple[datetime, float]] = []
    excursions: List[Dict[str, Any]] = []
    status: str = "running"  # running, completed, failed, aborted


class HumidityFreezeTestData(BaseModel):
    """Complete test data container"""
    test_id: str
    module_serial: str
    operator_id: str
    start_time: datetime
    end_time: Optional[datetime] = None

    # Pre-test data
    initial_visual_inspection: Dict[str, Any] = {}
    initial_iv_curve: Optional[IVCurveData] = None
    initial_insulation_resistance: Optional[float] = None

    # Cycle data
    cycles: List[CycleData] = []

    # Post-test data
    final_visual_inspection: Dict[str, Any] = {}
    final_iv_curve: Optional[IVCurveData] = None
    final_insulation_resistance: Optional[float] = None

    # Results
    power_degradation: Optional[float] = None
    pass_fail: Optional[bool] = None
    failure_modes: List[str] = []


class HumidityFreezeProtocol(BaseProtocol):
    """IEC 61215 MQT 12 Humidity Freeze Test Protocol Implementation

    This protocol executes thermal cycling with humidity stress testing
    on photovoltaic modules to evaluate durability and reliability.
    """

    def __init__(self, template_path: Optional[Path] = None):
        """Initialize Humidity Freeze Protocol

        Args:
            template_path: Path to JSON template. If None, uses default template.
        """
        if template_path is None:
            template_path = Path(__file__).parent.parent.parent / "templates" / "protocols" / "hf-001.json"

        super().__init__(template_path)
        self.test_data: Optional[HumidityFreezeTestData] = None
        logger.info(f"Initialized {self.metadata.name} v{self.metadata.version}")

    def validate_equipment(self) -> bool:
        """Validate all required equipment is available and calibrated

        Returns:
            True if all equipment is valid, False otherwise
        """
        required_equipment = self.template['equipment']

        # In a real implementation, this would check actual equipment status
        # For now, we'll return a structure for validation
        logger.info("Validating equipment configuration...")

        for equipment_name, specs in required_equipment.items():
            if specs.get('required', False):
                logger.info(f"  - {equipment_name}: Required")
                if specs.get('calibration_required', False):
                    logger.info(f"    Calibration interval: {specs.get('calibration_interval', 'N/A')}")

        # This would integrate with equipment management system
        return True

    def validate_sample(self, sample_data: Dict[str, Any]) -> bool:
        """Validate sample meets protocol requirements

        Args:
            sample_data: Dictionary containing sample information

        Returns:
            True if sample is valid, False otherwise
        """
        required_fields = ['module_serial', 'manufacturer', 'model']

        for field in required_fields:
            if field not in sample_data:
                logger.error(f"Missing required sample field: {field}")
                return False

        logger.info(f"Sample validation passed for module {sample_data['module_serial']}")
        return True

    def measure_iv_curve(
        self,
        module_temp: float = 25.0,
        irradiance: float = 1000.0
    ) -> IVCurveData:
        """Measure I-V curve at specified conditions

        Args:
            module_temp: Module temperature in °C
            irradiance: Irradiance in W/m²

        Returns:
            IVCurveData object containing measurement results
        """
        logger.info(f"Measuring I-V curve at {module_temp}°C, {irradiance} W/m²")

        # In real implementation, this would interface with I-V curve tracer
        # For demonstration, generate realistic synthetic data

        # Realistic PV module parameters
        Voc_ref = 45.5  # V
        Isc_ref = 9.2   # A
        Vmp_ref = 37.2  # V
        Imp_ref = 8.7   # A

        # Temperature coefficients (typical for c-Si)
        alpha = 0.0005  # A/°C (Isc)
        beta = -0.0031  # V/°C (Voc)

        # Adjust for temperature
        dT = module_temp - 25.0
        Voc = Voc_ref * (1 + beta * dT)
        Isc = Isc_ref * (1 + alpha * dT) * (irradiance / 1000.0)

        # Generate I-V curve
        voltage = np.linspace(0, Voc, 100)
        # Simplified single-diode model
        current = Isc * (1 - np.exp((voltage / Voc - 1) / 0.06))

        # Find maximum power point
        power = voltage * current
        max_idx = np.argmax(power)
        Vmp = voltage[max_idx]
        Imp = current[max_idx]
        Pmax = power[max_idx]
        FF = Pmax / (Voc * Isc)

        return IVCurveData(
            timestamp=datetime.now(),
            irradiance=irradiance,
            module_temp=module_temp,
            voltage=voltage.tolist(),
            current=current.tolist(),
            Voc=float(Voc),
            Isc=float(Isc),
            Vmp=float(Vmp),
            Imp=float(Imp),
            Pmax=float(Pmax),
            FF=float(FF)
        )

    def measure_insulation_resistance(self, test_voltage: float = 1000.0) -> float:
        """Measure insulation resistance

        Args:
            test_voltage: Test voltage in VDC

        Returns:
            Insulation resistance in MΩ
        """
        logger.info(f"Measuring insulation resistance at {test_voltage}V DC")

        # In real implementation, interface with insulation tester
        # For demonstration, return typical value
        resistance = 150.0  # MΩ

        logger.info(f"Insulation resistance: {resistance} MΩ")
        return resistance

    def execute_cycle(
        self,
        cycle_number: int,
        duration_minutes: int = 360
    ) -> CycleData:
        """Execute a single humidity-freeze cycle

        Args:
            cycle_number: Cycle number (1-10)
            duration_minutes: Expected cycle duration in minutes

        Returns:
            CycleData object with cycle monitoring data
        """
        logger.info(f"Starting cycle {cycle_number}/10")

        cycle = CycleData(
            cycle_number=cycle_number,
            start_time=datetime.now()
        )

        # Cycle profile from template
        profile = self.template['test_steps'][5]['cycle_profile']

        # Phase 1: High temperature with humidity (4 hours)
        logger.info("  Phase 1: High temperature with humidity (85°C, 85% RH, 4h)")
        phase1_duration = self.get_parameter('dwell_time_high')['value'] * 60  # minutes

        # Phase 2: Transition to low temperature
        logger.info("  Phase 2: Transition to low temperature (85°C → -40°C)")
        temp_range = 85 - (-40)  # 125°C
        ramp_rate = self.get_parameter('transition_rate')['value']  # °C/hour
        phase2_duration = (temp_range / ramp_rate) * 60  # minutes

        # Phase 3: Low temperature dwell (1 hour)
        logger.info("  Phase 3: Low temperature dwell (-40°C, 1h)")
        phase3_duration = self.get_parameter('dwell_time_low')['value'] * 60  # minutes

        # Phase 4: Transition back to high temperature
        logger.info("  Phase 4: Transition to high temperature (-40°C → 85°C)")
        phase4_duration = phase2_duration  # Same ramp rate

        # In real implementation, this would monitor actual chamber data
        # For demonstration, generate synthetic monitoring data
        total_duration = phase1_duration + phase2_duration + phase3_duration + phase4_duration

        # Simulate temperature and humidity logs
        current_time = cycle.start_time
        time_step = 1  # minute

        for minute in range(0, int(total_duration), time_step):
            timestamp = current_time + timedelta(minutes=minute)

            # Determine current phase and setpoints
            if minute < phase1_duration:
                temp_setpoint = 85.0
                humidity_setpoint = 85.0
            elif minute < phase1_duration + phase2_duration:
                # Ramping down
                progress = (minute - phase1_duration) / phase2_duration
                temp_setpoint = 85.0 - (125.0 * progress)
                humidity_setpoint = None  # Uncontrolled
            elif minute < phase1_duration + phase2_duration + phase3_duration:
                temp_setpoint = -40.0
                humidity_setpoint = None  # Uncontrolled
            else:
                # Ramping up
                progress = (minute - phase1_duration - phase2_duration - phase3_duration) / phase4_duration
                temp_setpoint = -40.0 + (125.0 * progress)
                if temp_setpoint > 60:
                    humidity_setpoint = 85.0
                else:
                    humidity_setpoint = None

            # Add realistic noise
            temp_actual = temp_setpoint + np.random.normal(0, 0.5)
            cycle.temperature_log.append((timestamp, temp_actual))

            if humidity_setpoint is not None:
                humidity_actual = humidity_setpoint + np.random.normal(0, 1.5)
                cycle.humidity_log.append((timestamp, humidity_actual))

        cycle.end_time = current_time + timedelta(minutes=total_duration)
        cycle.status = "completed"

        logger.info(f"Cycle {cycle_number} completed in {total_duration/60:.1f} hours")
        return cycle

    def run_test(
        self,
        sample_id: str,
        operator_id: str = "OPERATOR001",
        **kwargs
    ) -> TestResult:
        """Execute complete HF-001 test protocol

        Args:
            sample_id: Module serial number
            operator_id: Operator identification
            **kwargs: Additional test parameters

        Returns:
            TestResult object with test outcome
        """
        logger.info(f"Starting HF-001 test for module {sample_id}")

        # Initialize test data
        self.test_data = HumidityFreezeTestData(
            test_id=f"HF001_{sample_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            module_serial=sample_id,
            operator_id=operator_id,
            start_time=datetime.now()
        )

        # Step 1-2: Documentation and Visual Inspection
        logger.info("Step 1-2: Pre-test documentation and visual inspection")
        self.test_data.initial_visual_inspection = {
            'broken_cells': 0,
            'delamination': False,
            'junction_box_intact': True,
            'discoloration': False,
            'bubbles': 0,
            'inspection_passed': True
        }

        # Step 3: Initial I-V Curve
        logger.info("Step 3: Initial I-V curve measurement")
        self.test_data.initial_iv_curve = self.measure_iv_curve()

        # Step 4: Initial Insulation Resistance
        logger.info("Step 4: Initial insulation resistance test")
        self.test_data.initial_insulation_resistance = self.measure_insulation_resistance()

        # Step 5: Chamber setup (logged only)
        logger.info("Step 5: Chamber setup and pre-conditioning")

        # Step 6: Execute 10 cycles
        logger.info("Step 6: Executing 10 humidity-freeze cycles")
        num_cycles = self.get_parameter('total_cycles')['value']

        for cycle_num in range(1, num_cycles + 1):
            cycle_data = self.execute_cycle(cycle_num)
            self.test_data.cycles.append(cycle_data)

        # Step 7: Stabilization
        logger.info("Step 7: Post-cycle stabilization (2 hours)")

        # Step 8: Final Visual Inspection
        logger.info("Step 8: Final visual inspection")
        self.test_data.final_visual_inspection = {
            'broken_cells': 0,
            'delamination': False,
            'junction_box_intact': True,
            'discoloration': False,
            'bubbles': 1,  # Minor bubble appeared
            'inspection_passed': True,
            'notes': 'One small bubble (5mm) observed - within acceptable limits'
        }

        # Step 9: Final I-V Curve
        logger.info("Step 9: Final I-V curve measurement")
        # Simulate small degradation (2-3%)
        degradation_factor = 0.97  # 3% degradation
        self.test_data.final_iv_curve = self.measure_iv_curve()
        # Apply degradation to Pmax
        self.test_data.final_iv_curve.Pmax *= degradation_factor

        # Step 10: Final Insulation Resistance
        logger.info("Step 10: Final insulation resistance test")
        self.test_data.final_insulation_resistance = self.measure_insulation_resistance()

        # Step 11: Analysis
        logger.info("Step 11: Data analysis and pass/fail determination")
        analysis_results = self.analyze_results_internal()

        self.test_data.power_degradation = analysis_results['power_degradation']
        self.test_data.pass_fail = analysis_results['pass_fail']
        self.test_data.failure_modes = analysis_results['failure_modes']
        self.test_data.end_time = datetime.now()

        # Create TestResult
        result = TestResult(
            test_id=self.test_data.test_id,
            protocol_id=self.metadata.protocol_id,
            start_time=self.test_data.start_time,
            end_time=self.test_data.end_time,
            status="completed",
            pass_fail=self.test_data.pass_fail
        )

        logger.info(f"Test completed: {'PASS' if result.pass_fail else 'FAIL'}")
        return result

    def analyze_results_internal(self) -> Dict[str, Any]:
        """Internal analysis method for test data

        Returns:
            Dictionary with analysis results
        """
        if self.test_data is None:
            raise ValueError("No test data available for analysis")

        analysis = {
            'power_degradation': 0.0,
            'pass_fail': True,
            'failure_modes': []
        }

        # Calculate power degradation
        if self.test_data.initial_iv_curve and self.test_data.final_iv_curve:
            P_initial = self.test_data.initial_iv_curve.Pmax
            P_final = self.test_data.final_iv_curve.Pmax
            degradation = ((P_initial - P_final) / P_initial) * 100
            analysis['power_degradation'] = round(degradation, 2)

            # Check against limit (5%)
            limit = self.get_qc_criteria()['power_degradation']['limit']
            if degradation > limit:
                analysis['pass_fail'] = False
                analysis['failure_modes'].append(
                    f"Power degradation ({degradation:.2f}%) exceeds limit ({limit}%)"
                )

        # Check insulation resistance
        if self.test_data.final_insulation_resistance:
            min_resistance = self.get_qc_criteria()['insulation_resistance']['final_min']
            if self.test_data.final_insulation_resistance < min_resistance:
                analysis['pass_fail'] = False
                analysis['failure_modes'].append(
                    f"Insulation resistance ({self.test_data.final_insulation_resistance} MΩ) below minimum ({min_resistance} MΩ)"
                )

        # Check visual inspection
        if not self.test_data.final_visual_inspection.get('inspection_passed', False):
            analysis['pass_fail'] = False
            analysis['failure_modes'].append("Visual inspection failed")

        # Check cycle completion
        completed_cycles = len([c for c in self.test_data.cycles if c.status == 'completed'])
        required_cycles = self.get_parameter('total_cycles')['value']
        if completed_cycles < required_cycles:
            analysis['pass_fail'] = False
            analysis['failure_modes'].append(
                f"Incomplete cycles: {completed_cycles}/{required_cycles}"
            )

        return analysis

    def analyze_results(self, test_result: TestResult) -> Dict[str, Any]:
        """Analyze test results and generate summary

        Args:
            test_result: TestResult object from test execution

        Returns:
            Dictionary with detailed analysis
        """
        if self.test_data is None:
            return {'error': 'No test data available'}

        analysis = self.analyze_results_internal()

        # Add detailed metrics
        analysis['initial_performance'] = {
            'Pmax': self.test_data.initial_iv_curve.Pmax if self.test_data.initial_iv_curve else None,
            'Voc': self.test_data.initial_iv_curve.Voc if self.test_data.initial_iv_curve else None,
            'Isc': self.test_data.initial_iv_curve.Isc if self.test_data.initial_iv_curve else None,
            'FF': self.test_data.initial_iv_curve.FF if self.test_data.initial_iv_curve else None,
        }

        analysis['final_performance'] = {
            'Pmax': self.test_data.final_iv_curve.Pmax if self.test_data.final_iv_curve else None,
            'Voc': self.test_data.final_iv_curve.Voc if self.test_data.final_iv_curve else None,
            'Isc': self.test_data.final_iv_curve.Isc if self.test_data.final_iv_curve else None,
            'FF': self.test_data.final_iv_curve.FF if self.test_data.final_iv_curve else None,
        }

        analysis['cycles_completed'] = len(self.test_data.cycles)
        analysis['test_duration_hours'] = (
            (self.test_data.end_time - self.test_data.start_time).total_seconds() / 3600
            if self.test_data.end_time else None
        )

        return analysis

    def export_cycle_data(self, output_path: Path) -> Path:
        """Export cycle temperature and humidity data to CSV

        Args:
            output_path: Directory for output files

        Returns:
            Path to exported CSV file
        """
        if self.test_data is None:
            raise ValueError("No test data available")

        # Combine all cycle data
        all_data = []
        for cycle in self.test_data.cycles:
            for timestamp, temp in cycle.temperature_log:
                all_data.append({
                    'cycle': cycle.cycle_number,
                    'timestamp': timestamp,
                    'parameter': 'temperature',
                    'value': temp,
                    'unit': '°C'
                })
            for timestamp, humidity in cycle.humidity_log:
                all_data.append({
                    'cycle': cycle.cycle_number,
                    'timestamp': timestamp,
                    'parameter': 'humidity',
                    'value': humidity,
                    'unit': '%RH'
                })

        df = pd.DataFrame(all_data)
        csv_path = output_path / f"{self.test_data.test_id}_cycle_data.csv"
        df.to_csv(csv_path, index=False)

        logger.info(f"Cycle data exported to {csv_path}")
        return csv_path

    def generate_qr_code(self) -> str:
        """Generate QR code content for traceability

        Returns:
            QR code content string
        """
        if self.test_data is None:
            raise ValueError("No test data available")

        qr_config = self.template['data_traceability']['qr_code']
        content_template = qr_config['content']

        qr_content = content_template.format(
            protocol_id=self.metadata.protocol_id,
            module_serial=self.test_data.module_serial,
            test_date=self.test_data.start_time.strftime('%Y%m%d'),
            test_id=self.test_data.test_id
        )

        return qr_content
