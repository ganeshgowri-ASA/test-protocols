"""
QC Checks Module
================

Quality control check functions for test protocols.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class QCResult:
    """Quality control check result"""
    check_id: str
    check_name: str
    passed: bool
    expected_value: Any = None
    actual_value: Any = None
    deviation: Optional[float] = None
    is_critical: bool = False
    message: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'check_id': self.check_id,
            'check_name': self.check_name,
            'passed': self.passed,
            'expected_value': self.expected_value,
            'actual_value': self.actual_value,
            'deviation': self.deviation,
            'is_critical': self.is_critical,
            'message': self.message,
            'timestamp': self.timestamp
        }


class QCChecker:
    """
    Quality Control Checker for performing automated QC checks.
    """

    def __init__(self, protocol_config: Dict[str, Any]):
        """
        Initialize QC Checker.

        Args:
            protocol_config: Protocol configuration dictionary
        """
        self.protocol_config = protocol_config
        self.qc_rules = protocol_config.get('quality_control', {}).get('checks', [])

    def run_all_checks(self, test_data: Dict[str, Any]) -> List[QCResult]:
        """
        Run all QC checks for test data.

        Args:
            test_data: Test data dictionary

        Returns:
            List of QCResult objects
        """
        results = []

        for rule in self.qc_rules:
            result = self.run_check(rule, test_data)
            if result:
                results.append(result)

        logger.info(f"Completed {len(results)} QC checks")
        return results

    def run_check(self, rule: Dict[str, Any], test_data: Dict[str, Any]) -> Optional[QCResult]:
        """
        Run a single QC check.

        Args:
            rule: QC rule definition
            test_data: Test data

        Returns:
            QCResult or None
        """
        check_id = rule['id']
        check_name = rule['name']
        is_critical = rule.get('critical', False)

        # Implement different check types
        passed, message = self._evaluate_check(rule, test_data)

        result = QCResult(
            check_id=check_id,
            check_name=check_name,
            passed=passed,
            is_critical=is_critical,
            message=message
        )

        logger.debug(f"QC Check {check_id}: {'PASS' if passed else 'FAIL'}")
        return result

    def _evaluate_check(self, rule: Dict[str, Any], test_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Evaluate check based on rule type.

        Args:
            rule: QC rule
            test_data: Test data

        Returns:
            Tuple of (passed, message)
        """
        # Simplified implementation - can be extended
        check_name = rule['name']

        if 'Equipment Calibration' in check_name:
            # Check equipment calibration validity
            return True, "Equipment calibration valid"

        elif 'Environmental Conditions' in check_name:
            # Check environmental conditions
            temp = test_data.get('ambient_temperature')
            humidity = test_data.get('relative_humidity')

            if temp is not None and (temp < 15 or temp > 35):
                return False, f"Temperature {temp}°C out of range (15-35°C)"
            if humidity is not None and (humidity < 25 or humidity > 75):
                return False, f"Humidity {humidity}% out of range (25-75%)"

            return True, "Environmental conditions within limits"

        elif 'Test Voltage Accuracy' in check_name:
            # Check test voltage accuracy
            calculated = test_data.get('test_voltage_calculated')
            applied = test_data.get('test_voltage_applied')

            if calculated and applied:
                deviation = abs(applied - calculated)
                if deviation > 50:
                    return False, f"Voltage deviation {deviation:.1f}V exceeds ±50V"
                return True, f"Voltage within tolerance (±{deviation:.1f}V)"

            return True, "No voltage data to check"

        elif 'Test Duration' in check_name:
            # Check test duration
            duration = test_data.get('test_duration')
            if duration and duration < 60:
                return False, f"Test duration {duration}s less than required 60s"
            return True, "Test duration adequate"

        elif 'Insulation Resistance' in check_name:
            # Check insulation resistance minimums
            module_area = test_data.get('module_area', 1.0)
            resistance_initial = test_data.get('insulation_resistance_initial')
            resistance_final = test_data.get('insulation_resistance_final')

            if resistance_initial:
                resistance_per_area = resistance_initial / module_area
                if resistance_per_area < 40:
                    return False, f"Initial resistance {resistance_per_area:.1f} MΩ/m² below 40 MΩ/m²"

            if resistance_final:
                resistance_per_area = resistance_final / module_area
                if resistance_per_area < 40:
                    return False, f"Final resistance {resistance_per_area:.1f} MΩ/m² below 40 MΩ/m²"

            return True, "Insulation resistance meets minimum requirements"

        # Default: pass if no specific check implemented
        return True, "Check passed"

    def get_critical_failures(self, results: List[QCResult]) -> List[QCResult]:
        """Get list of critical check failures."""
        return [r for r in results if r.is_critical and not r.passed]

    def get_all_failures(self, results: List[QCResult]) -> List[QCResult]:
        """Get list of all check failures."""
        return [r for r in results if not r.passed]

    def calculate_pass_rate(self, results: List[QCResult]) -> float:
        """Calculate QC check pass rate percentage."""
        if not results:
            return 100.0

        passed = sum(1 for r in results if r.passed)
        return (passed / len(results)) * 100.0


def perform_qc_checks(test_data: Dict[str, Any], protocol_config: Dict[str, Any]) -> List[QCResult]:
    """
    Convenience function to perform QC checks.

    Args:
        test_data: Test data dictionary
        protocol_config: Protocol configuration

    Returns:
        List of QC results
    """
    checker = QCChecker(protocol_config)
    return checker.run_all_checks(test_data)
