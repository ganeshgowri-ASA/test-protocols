"""
ML-002 Mechanical Load Dynamic Test Implementation

This module implements the test execution logic for ML-002 protocol:
1000Pa cyclic mechanical load testing for photovoltaic modules.

Author: ganeshgowri-ASA
Date: 2025-11-14
Version: 1.0.0
"""

import json
import time
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
import numpy as np


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestStatus(Enum):
    """Test execution status"""
    INITIALIZED = "initialized"
    CALIBRATING = "calibrating"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class TestSample:
    """Represents a PV module test sample"""
    sample_id: str
    module_type: str
    serial_number: str
    manufacturer: str = ""
    manufacturing_date: str = ""
    rated_power_w: Optional[float] = None
    dimensions_mm: Dict[str, float] = field(default_factory=dict)
    weight_kg: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class SensorReading:
    """Single sensor reading"""
    sensor_id: str
    timestamp: float
    value: float
    unit: str
    cycle_number: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class CycleData:
    """Data for a single load cycle"""
    cycle_number: int
    start_time: float
    end_time: float
    max_load_pa: float
    min_load_pa: float
    max_deflection_mm: float
    min_deflection_mm: float
    peak_to_peak_deflection_mm: float
    sensor_readings: List[SensorReading] = field(default_factory=list)
    quality_flags: Dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['sensor_readings'] = [r.to_dict() for r in self.sensor_readings]
        return data


@dataclass
class EnvironmentalData:
    """Environmental conditions snapshot"""
    timestamp: float
    temperature_celsius: float
    humidity_percent: float
    atmospheric_pressure_kpa: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class TestResults:
    """Complete test results"""
    test_id: str
    sample: TestSample
    start_time: datetime
    end_time: Optional[datetime] = None
    status: TestStatus = TestStatus.INITIALIZED
    total_cycles: int = 0
    completed_cycles: int = 0
    cycle_data: List[CycleData] = field(default_factory=list)
    environmental_data: List[EnvironmentalData] = field(default_factory=list)
    quality_control_results: Dict[str, Any] = field(default_factory=dict)
    passed: Optional[bool] = None
    failure_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['start_time'] = self.start_time.isoformat()
        data['end_time'] = self.end_time.isoformat() if self.end_time else None
        data['status'] = self.status.value
        data['sample'] = self.sample.to_dict()
        data['cycle_data'] = [c.to_dict() for c in self.cycle_data]
        data['environmental_data'] = [e.to_dict() for e in self.environmental_data]
        return data


class EquipmentInterface(ABC):
    """Abstract base class for equipment control"""

    @abstractmethod
    def connect(self) -> bool:
        """Connect to equipment"""
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """Disconnect from equipment"""
        pass

    @abstractmethod
    def calibrate(self) -> bool:
        """Calibrate equipment"""
        pass

    @abstractmethod
    def is_ready(self) -> bool:
        """Check if equipment is ready"""
        pass


class LoadController(EquipmentInterface):
    """Load application system controller"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connected = False
        self.calibrated = False
        self.current_load_pa = 0.0

    def connect(self) -> bool:
        """Connect to load controller"""
        logger.info("Connecting to load controller...")
        # TODO: Implement actual equipment connection
        self.connected = True
        logger.info("Load controller connected")
        return True

    def disconnect(self) -> bool:
        """Disconnect from load controller"""
        logger.info("Disconnecting load controller...")
        self.connected = False
        return True

    def calibrate(self) -> bool:
        """Calibrate load controller"""
        logger.info("Calibrating load controller...")
        # TODO: Implement calibration procedure
        self.calibrated = True
        logger.info("Load controller calibrated")
        return True

    def is_ready(self) -> bool:
        """Check if ready"""
        return self.connected and self.calibrated

    def set_load(self, load_pa: float, rate_pa_per_sec: float = 100.0) -> bool:
        """
        Apply specified load at given rate

        Args:
            load_pa: Target load in Pascals
            rate_pa_per_sec: Rate of load change in Pa/sec

        Returns:
            Success status
        """
        if not self.is_ready():
            logger.error("Load controller not ready")
            return False

        # TODO: Implement actual load control
        # Simulate ramping
        duration = abs(load_pa - self.current_load_pa) / rate_pa_per_sec
        logger.debug(f"Ramping load from {self.current_load_pa:.1f} Pa to {load_pa:.1f} Pa over {duration:.2f}s")

        self.current_load_pa = load_pa
        return True

    def get_current_load(self) -> float:
        """Get current applied load"""
        return self.current_load_pa

    def emergency_stop(self) -> bool:
        """Emergency stop - remove load immediately"""
        logger.warning("EMERGENCY STOP - Removing load")
        self.current_load_pa = 0.0
        return True


class SensorArray:
    """Manages multiple sensors"""

    def __init__(self, sensor_configs: List[Dict[str, Any]]):
        self.sensors = sensor_configs
        self.connected = False

    def connect(self) -> bool:
        """Connect to all sensors"""
        logger.info(f"Connecting to {len(self.sensors)} sensors...")
        # TODO: Implement actual sensor connections
        self.connected = True
        logger.info("All sensors connected")
        return True

    def disconnect(self) -> bool:
        """Disconnect all sensors"""
        logger.info("Disconnecting sensors...")
        self.connected = False
        return True

    def read_all(self, cycle_number: Optional[int] = None) -> List[SensorReading]:
        """
        Read all sensors

        Args:
            cycle_number: Optional cycle number for data tagging

        Returns:
            List of sensor readings
        """
        if not self.connected:
            logger.error("Sensors not connected")
            return []

        timestamp = time.time()
        readings = []

        # TODO: Implement actual sensor reading
        # Simulated readings for now
        for sensor in self.sensors:
            sensor_id = sensor['sensor_id']
            unit = sensor['unit']

            # Simulate sensor values
            if 'load' in sensor_id:
                value = 0.0  # Will be set by load controller
            elif 'displacement' in sensor_id or 'deflection' in sensor_id:
                value = np.random.normal(0, 0.1)  # Simulated deflection
            elif 'temp' in sensor_id:
                value = np.random.normal(25, 0.5)  # Simulated temperature
            elif 'humidity' in sensor_id:
                value = np.random.normal(50, 2)  # Simulated humidity
            else:
                value = 0.0

            reading = SensorReading(
                sensor_id=sensor_id,
                timestamp=timestamp,
                value=value,
                unit=unit,
                cycle_number=cycle_number
            )
            readings.append(reading)

        return readings

    def read_sensor(self, sensor_id: str) -> Optional[SensorReading]:
        """Read a specific sensor"""
        readings = self.read_all()
        for reading in readings:
            if reading.sensor_id == sensor_id:
                return reading
        return None


class ML002MechanicalLoadTest:
    """
    Main class for executing ML-002 Mechanical Load Dynamic Test

    This class orchestrates the complete test execution including:
    - Equipment initialization and calibration
    - Cyclic load application
    - Data collection
    - Real-time monitoring
    - Quality control checks
    """

    def __init__(self, protocol_file: str):
        """
        Initialize test with protocol definition

        Args:
            protocol_file: Path to protocol.json file
        """
        self.protocol = self._load_protocol(protocol_file)
        self.protocol_file = protocol_file

        # Extract key parameters
        self.target_load_pa = self.protocol['parameters']['load_configuration']['test_load_pa']['value']
        self.max_load_pa = self.protocol['parameters']['load_configuration']['max_load_pa']['value']
        self.cycle_count = self.protocol['parameters']['cycle_parameters']['cycle_count']['value']
        self.cycle_duration = self.protocol['parameters']['cycle_parameters']['cycle_duration_seconds']['value']
        self.load_rate = self.protocol['parameters']['cycle_parameters']['load_rate_pa_per_sec']['value']
        self.unload_rate = self.protocol['parameters']['cycle_parameters']['unload_rate_pa_per_sec']['value']
        self.hold_time = self.protocol['parameters']['cycle_parameters']['hold_time_at_peak_seconds']['value']
        self.rest_time = self.protocol['parameters']['cycle_parameters']['rest_time_between_cycles_seconds']['value']

        # Initialize equipment
        self.load_controller = LoadController(self.protocol['parameters']['load_configuration'])
        self.sensors = SensorArray(self.protocol['data_collection']['sensor_mappings'])

        # Test state
        self.test_results: Optional[TestResults] = None
        self.status = TestStatus.INITIALIZED
        self.abort_flag = False
        self.pause_flag = False

        # Callbacks
        self.progress_callback: Optional[Callable] = None
        self.alert_callback: Optional[Callable] = None

        logger.info(f"ML-002 Test initialized: {self.cycle_count} cycles at {self.target_load_pa} Pa")

    def _load_protocol(self, protocol_file: str) -> Dict[str, Any]:
        """Load and parse protocol JSON file"""
        protocol_path = Path(protocol_file)
        if not protocol_path.exists():
            raise FileNotFoundError(f"Protocol file not found: {protocol_file}")

        with open(protocol_path, 'r') as f:
            protocol = json.load(f)

        logger.info(f"Protocol loaded: {protocol['metadata']['name']} v{protocol['metadata']['version']}")
        return protocol

    def set_progress_callback(self, callback: Callable[[int, int, Dict], None]):
        """
        Set callback for progress updates

        Args:
            callback: Function(cycle_number, total_cycles, current_data)
        """
        self.progress_callback = callback

    def set_alert_callback(self, callback: Callable[[AlertLevel, str], None]):
        """
        Set callback for alerts

        Args:
            callback: Function(alert_level, message)
        """
        self.alert_callback = callback

    def _emit_alert(self, level: AlertLevel, message: str):
        """Emit alert to callback if registered"""
        logger.log(
            logging.WARNING if level == AlertLevel.WARNING else
            logging.ERROR if level == AlertLevel.CRITICAL else
            logging.INFO,
            message
        )
        if self.alert_callback:
            self.alert_callback(level, message)

    def _emit_progress(self, cycle: int, data: Dict):
        """Emit progress update"""
        if self.progress_callback:
            self.progress_callback(cycle, self.cycle_count, data)

    def initialize_equipment(self) -> bool:
        """
        Initialize and calibrate all test equipment

        Returns:
            Success status
        """
        logger.info("Initializing test equipment...")
        self.status = TestStatus.CALIBRATING

        try:
            # Connect equipment
            if not self.load_controller.connect():
                raise RuntimeError("Failed to connect load controller")

            if not self.sensors.connect():
                raise RuntimeError("Failed to connect sensors")

            # Calibrate
            if not self.load_controller.calibrate():
                raise RuntimeError("Failed to calibrate load controller")

            # Verify zero load
            self.load_controller.set_load(0.0)
            time.sleep(1)

            # Read sensors to verify
            readings = self.sensors.read_all()
            logger.info(f"Initial sensor check: {len(readings)} sensors ready")

            logger.info("Equipment initialization complete")
            return True

        except Exception as e:
            logger.error(f"Equipment initialization failed: {e}")
            self._emit_alert(AlertLevel.CRITICAL, f"Equipment initialization failed: {e}")
            self.status = TestStatus.FAILED
            return False

    def execute_test(self, sample: TestSample) -> TestResults:
        """
        Execute complete test cycle

        Args:
            sample: Test sample information

        Returns:
            Test results
        """
        logger.info(f"Starting ML-002 test for sample: {sample.sample_id}")

        # Initialize results
        test_id = f"ML002-{sample.sample_id}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.test_results = TestResults(
            test_id=test_id,
            sample=sample,
            start_time=datetime.now(),
            total_cycles=self.cycle_count,
            status=TestStatus.RUNNING
        )

        # Initialize equipment
        if not self.initialize_equipment():
            self.test_results.status = TestStatus.FAILED
            self.test_results.failure_reason = "Equipment initialization failed"
            return self.test_results

        self.status = TestStatus.RUNNING
        self.abort_flag = False

        try:
            # Execute cycles
            for cycle_num in range(1, self.cycle_count + 1):
                if self.abort_flag:
                    logger.warning("Test aborted by user")
                    self.test_results.status = TestStatus.ABORTED
                    break

                # Execute single cycle
                cycle_data = self._execute_cycle(cycle_num)
                self.test_results.cycle_data.append(cycle_data)
                self.test_results.completed_cycles = cycle_num

                # Check for failure conditions
                if self._check_failure_conditions(cycle_data):
                    logger.error("Failure condition detected - stopping test")
                    self.test_results.status = TestStatus.FAILED
                    break

                # Record environmental data periodically
                if cycle_num % 10 == 0:
                    env_data = self._read_environmental_data()
                    self.test_results.environmental_data.append(env_data)

                # Emit progress
                progress_data = {
                    'cycle': cycle_num,
                    'max_deflection': cycle_data.max_deflection_mm,
                    'current_load': cycle_data.max_load_pa
                }
                self._emit_progress(cycle_num, progress_data)

                # Rest between cycles
                if cycle_num < self.cycle_count:
                    time.sleep(self.rest_time)

            # Test completed
            if self.test_results.status == TestStatus.RUNNING:
                self.test_results.status = TestStatus.COMPLETED
                logger.info(f"Test completed: {self.test_results.completed_cycles}/{self.cycle_count} cycles")

            # Perform quality control evaluation
            self._evaluate_quality_control()

        except Exception as e:
            logger.error(f"Test execution error: {e}", exc_info=True)
            self.test_results.status = TestStatus.FAILED
            self.test_results.failure_reason = str(e)
            self._emit_alert(AlertLevel.CRITICAL, f"Test failed: {e}")

        finally:
            # Cleanup
            self.load_controller.set_load(0.0)
            self.load_controller.disconnect()
            self.sensors.disconnect()
            self.test_results.end_time = datetime.now()

        return self.test_results

    def _execute_cycle(self, cycle_number: int) -> CycleData:
        """
        Execute a single load cycle

        Args:
            cycle_number: Current cycle number

        Returns:
            Cycle data
        """
        logger.debug(f"Executing cycle {cycle_number}/{self.cycle_count}")

        cycle_data = CycleData(
            cycle_number=cycle_number,
            start_time=time.time(),
            end_time=0.0,
            max_load_pa=0.0,
            min_load_pa=0.0,
            max_deflection_mm=0.0,
            min_deflection_mm=0.0,
            peak_to_peak_deflection_mm=0.0
        )

        # Apply load
        self.load_controller.set_load(self.target_load_pa, self.load_rate)
        ramp_time = self.target_load_pa / self.load_rate
        time.sleep(ramp_time)

        # Hold at peak
        time.sleep(self.hold_time)

        # Read sensors at peak load
        peak_readings = self.sensors.read_all(cycle_number)
        cycle_data.sensor_readings.extend(peak_readings)

        # Extract deflection
        deflection_readings = [r for r in peak_readings if 'deflection' in r.sensor_id or 'displacement' in r.sensor_id]
        if deflection_readings:
            cycle_data.max_deflection_mm = max(r.value for r in deflection_readings)

        # Extract load
        load_readings = [r for r in peak_readings if 'load' in r.sensor_id]
        if load_readings:
            cycle_data.max_load_pa = load_readings[0].value
        else:
            cycle_data.max_load_pa = self.target_load_pa

        # Unload
        self.load_controller.set_load(0.0, self.unload_rate)
        unload_time = self.target_load_pa / self.unload_rate
        time.sleep(unload_time)

        # Read sensors at zero load
        zero_readings = self.sensors.read_all(cycle_number)
        cycle_data.sensor_readings.extend(zero_readings)

        deflection_zero = [r for r in zero_readings if 'deflection' in r.sensor_id or 'displacement' in r.sensor_id]
        if deflection_zero:
            cycle_data.min_deflection_mm = max(r.value for r in deflection_zero)

        cycle_data.peak_to_peak_deflection_mm = cycle_data.max_deflection_mm - cycle_data.min_deflection_mm
        cycle_data.end_time = time.time()

        return cycle_data

    def _read_environmental_data(self) -> EnvironmentalData:
        """Read current environmental conditions"""
        readings = self.sensors.read_all()

        temp = 25.0
        humidity = 50.0
        pressure = None

        for reading in readings:
            if 'temp' in reading.sensor_id:
                temp = reading.value
            elif 'humidity' in reading.sensor_id:
                humidity = reading.value
            elif 'pressure' in reading.sensor_id:
                pressure = reading.value

        return EnvironmentalData(
            timestamp=time.time(),
            temperature_celsius=temp,
            humidity_percent=humidity,
            atmospheric_pressure_kpa=pressure
        )

    def _check_failure_conditions(self, cycle_data: CycleData) -> bool:
        """
        Check for failure conditions

        Args:
            cycle_data: Current cycle data

        Returns:
            True if failure detected
        """
        failure_conditions = self.protocol['quality_control']['failure_conditions']

        for condition in failure_conditions:
            condition_id = condition['condition_id']

            # Check excessive deflection
            if condition_id == 'excessive_deflection':
                threshold = condition.get('threshold_mm', 50)
                if cycle_data.max_deflection_mm > threshold:
                    self._emit_alert(
                        AlertLevel.CRITICAL,
                        f"Excessive deflection: {cycle_data.max_deflection_mm:.2f}mm > {threshold}mm"
                    )
                    if condition['stop_test']:
                        return True

            # Check load overshoot
            elif condition_id == 'load_overshoot':
                threshold = condition.get('threshold_pa', self.max_load_pa)
                if cycle_data.max_load_pa > threshold:
                    self._emit_alert(
                        AlertLevel.CRITICAL,
                        f"Load overshoot: {cycle_data.max_load_pa:.1f}Pa > {threshold}Pa"
                    )
                    if condition['stop_test']:
                        return True

        return False

    def _evaluate_quality_control(self):
        """Evaluate quality control criteria"""
        logger.info("Evaluating quality control criteria...")

        from .analyzer import ML002Analyzer

        # Perform analysis
        analyzer = ML002Analyzer(self.test_results, self.protocol)
        qc_results = analyzer.evaluate_acceptance_criteria()

        self.test_results.quality_control_results = qc_results
        self.test_results.passed = qc_results.get('overall_pass', False)

        if self.test_results.passed:
            logger.info("✓ Test PASSED all quality criteria")
        else:
            logger.warning("✗ Test FAILED quality criteria")
            failed_criteria = [k for k, v in qc_results.items() if isinstance(v, dict) and not v.get('passed', True)]
            logger.warning(f"Failed criteria: {failed_criteria}")

    def abort_test(self):
        """Abort the running test"""
        logger.warning("Test abort requested")
        self.abort_flag = True
        self.load_controller.emergency_stop()

    def pause_test(self):
        """Pause the test"""
        logger.info("Test pause requested")
        self.pause_flag = True
        self.status = TestStatus.PAUSED

    def resume_test(self):
        """Resume paused test"""
        logger.info("Resuming test")
        self.pause_flag = False
        self.status = TestStatus.RUNNING


if __name__ == "__main__":
    # Example usage
    protocol_path = Path(__file__).parent / "protocol.json"

    # Create test instance
    test = ML002MechanicalLoadTest(str(protocol_path))

    # Define sample
    sample = TestSample(
        sample_id="PV-MODULE-001",
        module_type="Crystalline Silicon",
        serial_number="SN123456789",
        manufacturer="Example Solar Inc.",
        rated_power_w=400.0
    )

    # Set callbacks
    def progress_callback(cycle, total, data):
        print(f"Progress: Cycle {cycle}/{total} - Deflection: {data.get('max_deflection', 0):.2f}mm")

    def alert_callback(level, message):
        print(f"[{level.value.upper()}] {message}")

    test.set_progress_callback(progress_callback)
    test.set_alert_callback(alert_callback)

    # Run test
    results = test.execute_test(sample)

    print(f"\nTest completed: {results.status.value}")
    print(f"Cycles completed: {results.completed_cycles}/{results.total_cycles}")
    print(f"Pass/Fail: {'PASS' if results.passed else 'FAIL'}")
