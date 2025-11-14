"""
Environmental Protocol Implementation
Specialized implementation for environmental testing protocols
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging
import numpy as np
from collections import defaultdict

from ..base import BaseProtocol, ProtocolStatus, TestPhase

logger = logging.getLogger(__name__)


class EnvironmentalProtocol(BaseProtocol):
    """Base class for environmental testing protocols"""

    def __init__(self, protocol_file: Path):
        """Initialize environmental protocol"""
        super().__init__(protocol_file)
        self.data_storage: List[Dict[str, Any]] = []
        self.qc_results: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.current_cycle = 0
        self.cycle_data: Dict[int, List[Dict[str, Any]]] = defaultdict(list)

    def collect_data(self, data_point: Dict[str, Any]) -> None:
        """
        Collect environmental data point

        Args:
            data_point: Data to collect (temperature, humidity, etc.)
        """
        # Add timestamp if not present
        if 'timestamp' not in data_point:
            data_point['timestamp'] = datetime.utcnow()

        # Add cycle information
        data_point['cycle'] = self.current_cycle
        data_point['test_run_id'] = self.test_run_id

        # Store data
        self.data_storage.append(data_point)
        self.cycle_data[self.current_cycle].append(data_point)

        logger.debug(f"Collected data point: {data_point}")

    def run_qc_checks(self) -> Dict[str, bool]:
        """
        Run QC checks on collected data

        Returns:
            Dictionary of check results
        """
        results = {}
        qc_checks = self.get_qc_checks()

        for check in qc_checks:
            check_name = check.get("name")
            check_type = check.get("type")

            try:
                if check_type == "continuous":
                    result = self._run_continuous_qc_check(check)
                elif check_type == "periodic":
                    result = self._run_periodic_qc_check(check)
                else:
                    logger.warning(f"Unknown QC check type: {check_type}")
                    result = True

                results[check_name] = result

                # Store QC result
                self.qc_results[check_name].append({
                    'timestamp': datetime.utcnow(),
                    'passed': result,
                    'check': check
                })

                # Handle failures
                if not result:
                    action = check.get("action_on_fail", "alert")
                    self._handle_qc_failure(check_name, action)

            except Exception as e:
                logger.error(f"QC check {check_name} failed with error: {e}")
                results[check_name] = False

        return results

    def _run_continuous_qc_check(self, check: Dict[str, Any]) -> bool:
        """Run continuous QC check (e.g., stability)"""
        threshold = check.get("threshold")
        window = check.get("window", 600)  # Default 10 minutes

        # Get recent data within window
        cutoff_time = datetime.utcnow() - timedelta(seconds=window)
        recent_data = [
            d for d in self.data_storage
            if d.get('timestamp', datetime.min) >= cutoff_time
        ]

        if len(recent_data) < 2:
            return True  # Not enough data yet

        # Extract parameter values
        param_name = check.get("name").replace("_stability", "")
        values = [d.get(param_name) for d in recent_data if param_name in d]

        if not values:
            return True

        # Check stability (standard deviation or range)
        std_dev = np.std(values)
        value_range = max(values) - min(values)

        # Pass if variation is within threshold
        return std_dev <= threshold and value_range <= (threshold * 2)

    def _run_periodic_qc_check(self, check: Dict[str, Any]) -> bool:
        """Run periodic QC check"""
        check_name = check.get("name")

        if "power_degradation" in check_name:
            return self._check_power_degradation(check)
        elif "insulation_resistance" in check_name:
            return self._check_insulation_resistance(check)
        elif "data_completeness" in check_name:
            return self._check_data_completeness(check)

        return True

    def _check_power_degradation(self, check: Dict[str, Any]) -> bool:
        """Check power degradation limits"""
        max_degradation = check.get("max_degradation", 5.0)

        # Get initial and latest power measurements
        power_measurements = [
            d.get("power") for d in self.data_storage
            if "power" in d
        ]

        if len(power_measurements) < 2:
            return True

        initial_power = power_measurements[0]
        latest_power = power_measurements[-1]

        if initial_power == 0:
            return False

        degradation = ((initial_power - latest_power) / initial_power) * 100

        return degradation <= max_degradation

    def _check_insulation_resistance(self, check: Dict[str, Any]) -> bool:
        """Check insulation resistance minimum"""
        min_value = check.get("min_value", 40)

        # Get latest insulation resistance measurement
        ir_measurements = [
            d.get("insulation_resistance") for d in self.data_storage
            if "insulation_resistance" in d
        ]

        if not ir_measurements:
            return True

        latest_ir = ir_measurements[-1]
        return latest_ir >= min_value

    def _check_data_completeness(self, check: Dict[str, Any]) -> bool:
        """Check data collection completeness"""
        min_completeness = check.get("min_completeness", 95)

        # Calculate expected vs actual data points
        if self.start_time is None:
            return True

        elapsed_time = (datetime.utcnow() - self.start_time).total_seconds()

        # Get data collection config
        config = self.get_data_collection_config()
        continuous_monitoring = config.get("continuous_monitoring", [])

        if not continuous_monitoring:
            return True

        # Check first parameter as representative
        first_param = continuous_monitoring[0]
        interval = first_param.get("interval", 60)
        expected_points = elapsed_time / interval

        # Count actual data points
        param_name = first_param.get("parameter")
        actual_points = sum(
            1 for d in self.data_storage if param_name in d
        )

        if expected_points == 0:
            return True

        completeness = (actual_points / expected_points) * 100
        return completeness >= min_completeness

    def _handle_qc_failure(self, check_name: str, action: str) -> None:
        """Handle QC check failure"""
        logger.warning(f"QC check '{check_name}' failed. Action: {action}")

        if action == "abort":
            self.abort(f"QC check '{check_name}' failed")
        elif action == "alert":
            logger.error(f"ALERT: QC check '{check_name}' failed")
        elif action == "flag":
            logger.warning(f"FLAG: QC check '{check_name}' failed")

    def execute(self, parameters: Dict[str, Any]) -> bool:
        """
        Execute environmental protocol

        Args:
            parameters: Test parameter values

        Returns:
            True if execution successful
        """
        # Validate parameters
        is_valid, errors = self.validate_parameters(parameters)
        if not is_valid:
            logger.error(f"Parameter validation failed: {errors}")
            return False

        # Start protocol
        self.start()

        try:
            # Run test procedure
            self._execute_test_procedure(parameters)

            # Complete protocol
            self.complete()
            return True

        except Exception as e:
            logger.error(f"Protocol execution failed: {e}")
            self.fail(str(e))
            return False

    def _execute_test_procedure(self, parameters: Dict[str, Any]) -> None:
        """Execute test procedure (to be overridden by specific protocols)"""
        logger.info("Executing environmental test procedure")
        # This is a placeholder - specific protocols should override

    def generate_report(self) -> Dict[str, Any]:
        """
        Generate test report

        Returns:
            Report data dictionary
        """
        report = {
            'metadata': {
                'protocol_id': self.metadata.id,
                'protocol_name': self.metadata.name,
                'test_run_id': self.test_run_id,
                'start_time': self.start_time,
                'end_time': self.end_time,
                'status': self.status.value,
                'duration': (self.end_time - self.start_time) if self.end_time and self.start_time else None
            },
            'parameters': parameters if hasattr(self, 'parameters') else {},
            'data_summary': {
                'total_data_points': len(self.data_storage),
                'total_cycles': self.current_cycle
            },
            'qc_summary': self._generate_qc_summary(),
            'pass_fail_status': self._evaluate_pass_fail_criteria(),
            'data': self.data_storage
        }

        return report

    def _generate_qc_summary(self) -> Dict[str, Any]:
        """Generate QC summary"""
        summary = {}

        for check_name, results in self.qc_results.items():
            total_checks = len(results)
            passed_checks = sum(1 for r in results if r.get('passed', False))

            summary[check_name] = {
                'total_checks': total_checks,
                'passed': passed_checks,
                'failed': total_checks - passed_checks,
                'pass_rate': (passed_checks / total_checks * 100) if total_checks > 0 else 0
            }

        return summary

    def _evaluate_pass_fail_criteria(self) -> Dict[str, Any]:
        """Evaluate pass/fail criteria"""
        criteria = self.get_pass_fail_criteria()
        results = {}

        for criterion_name, criterion in criteria.items():
            try:
                passed = self._evaluate_criterion(criterion)
                results[criterion_name] = {
                    'passed': passed,
                    'severity': criterion.get('severity', 'major'),
                    'description': criterion.get('description', '')
                }
            except Exception as e:
                logger.error(f"Failed to evaluate criterion {criterion_name}: {e}")
                results[criterion_name] = {
                    'passed': False,
                    'severity': criterion.get('severity', 'major'),
                    'description': f"Evaluation error: {e}"
                }

        # Overall pass/fail
        critical_failures = [
            name for name, result in results.items()
            if not result['passed'] and result['severity'] == 'critical'
        ]

        results['overall'] = {
            'passed': len(critical_failures) == 0,
            'critical_failures': critical_failures
        }

        return results

    def _evaluate_criterion(self, criterion: Dict[str, Any]) -> bool:
        """Evaluate a single pass/fail criterion"""
        # This is a simplified implementation
        # Specific protocols should override for detailed evaluation
        return True


class DesertClimateProtocol(EnvironmentalProtocol):
    """Desert climate testing protocol (DESERT-001)"""

    def __init__(self):
        """Initialize DESERT-001 protocol"""
        protocol_file = Path(__file__).parent / "desert-001.json"
        super().__init__(protocol_file)
        self.total_cycles = 0
        self.daytime_duration = 12  # hours
        self.nighttime_duration = 8  # hours
        self.transition_duration = 2  # hours

    def _execute_test_procedure(self, parameters: Dict[str, Any]) -> None:
        """
        Execute desert climate test procedure

        Args:
            parameters: Test parameters including temperatures, humidity, cycles
        """
        self.total_cycles = parameters.get("total_cycles", 200)

        logger.info(f"Starting desert climate test with {self.total_cycles} cycles")

        # Pre-test phase
        self._run_pre_test()

        # Main test cycles
        for cycle in range(self.total_cycles):
            self.current_cycle = cycle + 1
            logger.info(f"Starting cycle {self.current_cycle}/{self.total_cycles}")

            # Run cycle
            self._run_desert_cycle(parameters)

            # Interim testing
            if self.current_cycle % parameters.get("interim_test_frequency", 50) == 0:
                self._run_interim_tests()

            # Run QC checks
            qc_results = self.run_qc_checks()
            if not all(qc_results.values()):
                logger.warning(f"QC checks failed in cycle {self.current_cycle}")

        # Post-test phase
        self._run_post_test()

    def _run_pre_test(self) -> None:
        """Run pre-test procedures"""
        logger.info("Running pre-test procedures")
        self.current_phase = TestPhase.PRE_TEST

        # Visual inspection
        self.collect_data({
            'phase': 'pre_test',
            'action': 'visual_inspection',
            'result': 'pass',
            'notes': 'No visible defects'
        })

        # Initial I-V curve measurement
        # (In real implementation, this would interface with measurement equipment)
        self.collect_data({
            'phase': 'pre_test',
            'action': 'iv_curve',
            'voc': 45.6,
            'isc': 9.8,
            'vmp': 37.2,
            'imp': 9.2,
            'pmax': 342.2
        })

    def _run_desert_cycle(self, parameters: Dict[str, Any]) -> None:
        """
        Run a single desert climate cycle

        Args:
            parameters: Test parameters
        """
        # Daytime phase
        self._run_daytime_phase(parameters)

        # Transition to night
        self._run_transition_phase(parameters, to_night=True)

        # Nighttime phase
        self._run_nighttime_phase(parameters)

        # Transition to day
        self._run_transition_phase(parameters, to_night=False)

    def _run_daytime_phase(self, parameters: Dict[str, Any]) -> None:
        """Run daytime desert conditions"""
        logger.debug(f"Cycle {self.current_cycle}: Daytime phase")

        # Simulate data collection during daytime
        # In real implementation, this would continuously collect data
        self.collect_data({
            'phase': 'daytime',
            'chamber_temperature': parameters.get('daytime_temperature', 65),
            'chamber_humidity': parameters.get('daytime_humidity', 15),
            'uv_irradiance': parameters.get('uv_irradiance', 1000),
            'module_temperature': parameters.get('daytime_temperature', 65) + 10,
            'voc': 42.1,
            'isc': 9.5
        })

    def _run_nighttime_phase(self, parameters: Dict[str, Any]) -> None:
        """Run nighttime desert conditions"""
        logger.debug(f"Cycle {self.current_cycle}: Nighttime phase")

        # Simulate data collection during nighttime
        self.collect_data({
            'phase': 'nighttime',
            'chamber_temperature': parameters.get('nighttime_temperature', 5),
            'chamber_humidity': parameters.get('nighttime_humidity', 40),
            'uv_irradiance': 0,
            'module_temperature': parameters.get('nighttime_temperature', 5) + 2
        })

    def _run_transition_phase(self, parameters: Dict[str, Any], to_night: bool) -> None:
        """Run transition between day and night"""
        phase_name = "transition_to_night" if to_night else "transition_to_day"
        logger.debug(f"Cycle {self.current_cycle}: {phase_name}")

        # Simulate transition data
        self.collect_data({
            'phase': phase_name,
            'note': 'Temperature and humidity ramping'
        })

    def _run_interim_tests(self) -> None:
        """Run interim tests at specified intervals"""
        logger.info(f"Running interim tests at cycle {self.current_cycle}")
        self.current_phase = TestPhase.INTERIM_TEST

        # Simulate interim measurements
        # In reality, this would measure actual module parameters
        degradation_factor = 1 - (self.current_cycle / self.total_cycles * 0.03)  # 3% total degradation

        self.collect_data({
            'phase': 'interim_test',
            'cycle': self.current_cycle,
            'action': 'iv_curve',
            'pmax': 342.2 * degradation_factor,
            'degradation_percent': (1 - degradation_factor) * 100
        })

        self.collect_data({
            'phase': 'interim_test',
            'cycle': self.current_cycle,
            'action': 'insulation_resistance',
            'insulation_resistance': 50.0  # MΩ
        })

    def _run_post_test(self) -> None:
        """Run post-test procedures"""
        logger.info("Running post-test procedures")
        self.current_phase = TestPhase.POST_TEST

        # Final measurements
        self.collect_data({
            'phase': 'post_test',
            'action': 'final_iv_curve',
            'voc': 44.8,
            'isc': 9.6,
            'vmp': 36.5,
            'imp': 9.0,
            'pmax': 328.5  # 4% degradation from initial
        })

        self.collect_data({
            'phase': 'post_test',
            'action': 'final_insulation_resistance',
            'insulation_resistance': 48.5  # MΩ
        })

        self.collect_data({
            'phase': 'post_test',
            'action': 'final_visual_inspection',
            'result': 'pass',
            'notes': 'Minor discoloration observed, no delamination or cracks'
        })
