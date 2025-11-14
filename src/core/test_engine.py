"""
Test Execution Engine
Manages test execution, monitoring, and data collection
"""
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import logging


class TestStatus(Enum):
    """Test execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


class TestEngine:
    """Execute and monitor test protocols"""

    def __init__(self, protocol: Dict[str, Any], test_id: str):
        """
        Initialize test engine

        Args:
            protocol: Protocol definition dictionary
            test_id: Unique test identifier
        """
        self.protocol = protocol
        self.test_id = test_id
        self.status = TestStatus.PENDING
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.current_step = 0
        self.current_cycle = 0
        self.measurements: List[Dict[str, Any]] = []
        self.alerts: List[Dict[str, Any]] = []
        self.deviations: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)

    def start_test(self, modules: List[str], operator: str) -> Dict[str, Any]:
        """
        Start test execution

        Args:
            modules: List of module serial numbers
            operator: Operator name

        Returns:
            Test initialization result
        """
        self.logger.info(f"Starting test {self.test_id} for protocol {self.protocol['protocol_id']}")

        # Validate sample size
        min_samples = self.protocol['test_requirements']['sample_size']['minimum']
        if len(modules) < min_samples:
            raise ValueError(
                f"Insufficient samples. Minimum {min_samples} required, got {len(modules)}"
            )

        self.status = TestStatus.RUNNING
        self.start_time = datetime.now()
        self.current_step = 0
        self.current_cycle = 0

        return {
            'test_id': self.test_id,
            'status': self.status.value,
            'start_time': self.start_time.isoformat(),
            'protocol_id': self.protocol['protocol_id'],
            'modules': modules,
            'operator': operator,
            'expected_end_time': self._calculate_end_time().isoformat()
        }

    def _calculate_end_time(self) -> datetime:
        """Calculate expected test end time"""
        total_duration = self.protocol['test_sequence']['total_test_duration']
        duration_unit = self.protocol['test_sequence']['total_test_duration_unit']

        if duration_unit == 'hours':
            delta = timedelta(hours=total_duration)
        elif duration_unit == 'minutes':
            delta = timedelta(minutes=total_duration)
        else:
            delta = timedelta(days=total_duration)

        return self.start_time + delta

    def record_measurement(
        self,
        parameter: str,
        value: float,
        unit: str,
        timestamp: Optional[datetime] = None,
        module_id: Optional[str] = None
    ) -> None:
        """
        Record a measurement

        Args:
            parameter: Parameter name
            value: Measured value
            unit: Unit of measurement
            timestamp: Measurement timestamp (defaults to now)
            module_id: Optional module identifier
        """
        if timestamp is None:
            timestamp = datetime.now()

        measurement = {
            'test_id': self.test_id,
            'timestamp': timestamp.isoformat(),
            'parameter': parameter,
            'value': value,
            'unit': unit,
            'step': self.current_step,
            'cycle': self.current_cycle,
            'module_id': module_id
        }

        self.measurements.append(measurement)

        # Check for alerts
        self._check_alerts(parameter, value)

    def _check_alerts(self, parameter: str, value: float) -> None:
        """
        Check if measurement triggers any alerts

        Args:
            parameter: Parameter name
            value: Measured value
        """
        monitoring_params = self.protocol.get('monitoring_parameters', {})

        # Check chamber conditions
        if parameter in ['temperature', 'relative_humidity']:
            chamber_params = monitoring_params.get('chamber_conditions', {})
            param_config = chamber_params.get(parameter, {})

            target = param_config.get('target')
            tolerance = param_config.get('tolerance')

            if target and tolerance:
                if abs(value - target) > tolerance:
                    self._create_alert(
                        severity='WARNING',
                        message=f"{parameter} out of tolerance: {value} (target: {target}±{tolerance})",
                        parameter=parameter,
                        value=value
                    )

    def _create_alert(
        self,
        severity: str,
        message: str,
        parameter: str,
        value: float
    ) -> None:
        """Create an alert"""
        alert = {
            'test_id': self.test_id,
            'timestamp': datetime.now().isoformat(),
            'severity': severity,
            'message': message,
            'parameter': parameter,
            'value': value,
            'step': self.current_step,
            'cycle': self.current_cycle
        }

        self.alerts.append(alert)
        self.logger.warning(f"Alert: {message}")

    def record_deviation(
        self,
        description: str,
        severity: str,
        corrective_action: str
    ) -> None:
        """
        Record a test deviation

        Args:
            description: Deviation description
            severity: Severity level (MINOR, MAJOR, CRITICAL)
            corrective_action: Action taken
        """
        deviation = {
            'test_id': self.test_id,
            'timestamp': datetime.now().isoformat(),
            'description': description,
            'severity': severity,
            'corrective_action': corrective_action,
            'step': self.current_step,
            'cycle': self.current_cycle
        }

        self.deviations.append(deviation)
        self.logger.warning(f"Deviation recorded: {description}")

    def advance_step(self) -> Dict[str, Any]:
        """
        Advance to next test step

        Returns:
            Current step information
        """
        steps = self.protocol['test_sequence']['steps']

        if self.current_step < len(steps):
            current_step_info = steps[self.current_step]

            # Check if this step repeats (cycles)
            repeat_count = current_step_info.get('repeat_count', 1)

            if self.current_cycle < repeat_count - 1:
                self.current_cycle += 1
            else:
                self.current_step += 1
                self.current_cycle = 0

            if self.current_step >= len(steps):
                # Test complete
                self.complete_test()
                return {'status': 'completed'}

            return {
                'step': self.current_step,
                'cycle': self.current_cycle,
                'step_info': steps[self.current_step] if self.current_step < len(steps) else None
            }

        return {'status': 'completed'}

    def complete_test(self) -> None:
        """Mark test as completed"""
        self.status = TestStatus.COMPLETED
        self.end_time = datetime.now()
        self.logger.info(f"Test {self.test_id} completed")

    def abort_test(self, reason: str) -> None:
        """
        Abort test execution

        Args:
            reason: Reason for abort
        """
        self.status = TestStatus.ABORTED
        self.end_time = datetime.now()
        self.record_deviation(
            description=f"Test aborted: {reason}",
            severity="CRITICAL",
            corrective_action="Test terminated"
        )
        self.logger.error(f"Test {self.test_id} aborted: {reason}")

    def get_status(self) -> Dict[str, Any]:
        """
        Get current test status

        Returns:
            Status information
        """
        progress = 0.0
        if self.status == TestStatus.RUNNING:
            total_cycles = self.protocol['test_sequence'].get('total_cycles', 1)
            steps = self.protocol['test_sequence']['steps']

            # Calculate progress
            if total_cycles > 0:
                progress = ((self.current_step * total_cycles) + self.current_cycle) / (
                    len(steps) * total_cycles
                ) * 100

        return {
            'test_id': self.test_id,
            'status': self.status.value,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'current_step': self.current_step,
            'current_cycle': self.current_cycle,
            'progress_percent': round(progress, 2),
            'total_measurements': len(self.measurements),
            'total_alerts': len(self.alerts),
            'total_deviations': len(self.deviations)
        }

    def evaluate_acceptance_criteria(
        self,
        pre_test_results: Dict[str, Any],
        post_test_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate acceptance criteria

        Args:
            pre_test_results: Pre-test measurement results
            post_test_results: Post-test measurement results

        Returns:
            Pass/fail determination with details
        """
        criteria = self.protocol['acceptance_criteria']
        results = {
            'overall_pass': True,
            'visual_pass': True,
            'electrical_pass': True,
            'details': []
        }

        # Evaluate electrical criteria
        if 'electrical' in criteria:
            elec_criteria = criteria['electrical']

            # Check power degradation
            if 'power_degradation' in elec_criteria:
                pre_power = pre_test_results.get('Pmax', 0)
                post_power = post_test_results.get('Pmax', 0)

                if pre_power > 0:
                    degradation = ((pre_power - post_power) / pre_power) * 100
                    max_degradation = elec_criteria['power_degradation']['max']

                    passed = degradation <= max_degradation

                    results['details'].append({
                        'criterion': 'Power Degradation',
                        'measured': round(degradation, 2),
                        'limit': max_degradation,
                        'unit': '%',
                        'pass': passed
                    })

                    if not passed:
                        results['electrical_pass'] = False
                        results['overall_pass'] = False

        # Overall result
        results['pass_fail'] = 'PASS' if results['overall_pass'] else 'FAIL'

        return results
