"""Base protocol class for all test protocols."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProtocolStep:
    """Represents a single protocol step."""
    step_id: str
    name: str
    type: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    measurements: List[Dict[str, Any]] = field(default_factory=list)
    qc_criteria: Optional[List[Dict[str, Any]]] = None
    duration: Optional[Dict[str, Any]] = None
    dependencies: List[str] = field(default_factory=list)


@dataclass
class TestResult:
    """Represents the result of executing a protocol step."""
    step_id: str
    timestamp: datetime
    measurements: Dict[str, Any]
    status: str  # 'pass', 'fail', 'warning'
    operator: str
    notes: Optional[str] = None


class BaseProtocol(ABC):
    """Base class for all test protocols.

    This class provides core functionality for:
    - Loading protocol definitions
    - Validating measurements
    - Executing protocol steps
    - Calculating derived results
    - Evaluating pass/fail criteria
    """

    def __init__(self, protocol_definition: Dict[str, Any]):
        """Initialize protocol with JSON definition.

        Args:
            protocol_definition: Dictionary containing protocol specification
        """
        self.protocol_id = protocol_definition['protocol_id']
        self.name = protocol_definition['name']
        self.version = protocol_definition['version']
        self.category = protocol_definition['category']
        self.definition = protocol_definition
        self.steps = self._load_steps()
        self.results: List[TestResult] = []

        logger.info(f"Initialized protocol {self.protocol_id} v{self.version}")

    def _load_steps(self) -> List[ProtocolStep]:
        """Load protocol steps from definition.

        Returns:
            List of ProtocolStep objects
        """
        return [
            ProtocolStep(
                step_id=step['step_id'],
                name=step['name'],
                type=step['type'],
                description=step['description'],
                parameters=step.get('parameters', {}),
                measurements=step.get('measurements', []),
                qc_criteria=step.get('qc_criteria'),
                duration=step.get('duration'),
                dependencies=step.get('dependencies', [])
            )
            for step in self.definition['steps']
        ]

    @abstractmethod
    def validate_equipment(self) -> bool:
        """Verify required equipment is available and calibrated.

        Returns:
            True if all equipment is ready, False otherwise
        """
        pass

    @abstractmethod
    def prepare_samples(self) -> bool:
        """Prepare samples according to requirements.

        Returns:
            True if samples are prepared successfully, False otherwise
        """
        pass

    def execute_step(
        self,
        step_id: str,
        measurements: Dict[str, Any],
        operator: str,
        notes: Optional[str] = None
    ) -> TestResult:
        """Execute a single protocol step.

        Args:
            step_id: Unique identifier for the step
            measurements: Dictionary of measurement name -> value
            operator: Name of person executing the step
            notes: Optional notes or comments

        Returns:
            TestResult object with execution status

        Raises:
            ValueError: If step not found or measurements invalid
        """
        step = self._get_step(step_id)

        logger.info(f"Executing step {step_id}: {step.name}")

        # Check dependencies
        self._check_dependencies(step)

        # Validate measurements
        validated = self._validate_measurements(step, measurements)

        # Check QC criteria
        qc_status = self._check_qc_criteria(step, validated)

        # Create result
        result = TestResult(
            step_id=step_id,
            timestamp=datetime.now(),
            measurements=validated,
            status=qc_status,
            operator=operator,
            notes=notes
        )

        self.results.append(result)

        logger.info(f"Step {step_id} completed with status: {qc_status}")

        return result

    def _get_step(self, step_id: str) -> ProtocolStep:
        """Get step by ID.

        Args:
            step_id: Step identifier

        Returns:
            ProtocolStep object

        Raises:
            ValueError: If step not found
        """
        for step in self.steps:
            if step.step_id == step_id:
                return step
        raise ValueError(f"Step {step_id} not found in protocol {self.protocol_id}")

    def _check_dependencies(self, step: ProtocolStep) -> None:
        """Check if dependent steps have been completed.

        Args:
            step: The step to check dependencies for

        Raises:
            ValueError: If dependencies not met
        """
        if not step.dependencies:
            return

        completed_steps = {result.step_id for result in self.results}

        for dep_id in step.dependencies:
            if dep_id not in completed_steps:
                raise ValueError(
                    f"Step {step.step_id} depends on {dep_id}, "
                    f"which has not been completed"
                )

    def _validate_measurements(
        self,
        step: ProtocolStep,
        measurements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate measurements against defined constraints.

        Args:
            step: Protocol step definition
            measurements: Measurement data to validate

        Returns:
            Validated measurements dictionary

        Raises:
            ValueError: If validation fails
        """
        validated = {}

        for measurement_def in step.measurements:
            name = measurement_def['name']
            value = measurements.get(name)
            validation = measurement_def.get('validation', {})

            # Check required
            if validation.get('required', False):
                if value is None:
                    raise ValueError(
                        f"Required measurement '{name}' missing in step {step.step_id}"
                    )

            # Skip further validation if value is None and not required
            if value is None:
                validated[name] = value
                continue

            # Validate numeric ranges
            if measurement_def['type'] == 'numeric':
                min_val = validation.get('min')
                max_val = validation.get('max')

                if min_val is not None and value < min_val:
                    raise ValueError(
                        f"{name} below minimum in step {step.step_id}: "
                        f"{value} < {min_val}"
                    )
                if max_val is not None and value > max_val:
                    raise ValueError(
                        f"{name} above maximum in step {step.step_id}: "
                        f"{value} > {max_val}"
                    )

                # Apply precision if specified
                precision = validation.get('precision')
                if precision is not None:
                    value = round(value, precision)

            validated[name] = value

        return validated

    def _check_qc_criteria(
        self,
        step: ProtocolStep,
        measurements: Dict[str, Any]
    ) -> str:
        """Check QC criteria and return status.

        Args:
            step: Protocol step definition
            measurements: Validated measurements

        Returns:
            Status string: 'pass', 'warning', or 'fail'
        """
        if not step.qc_criteria:
            return 'pass'

        status = 'pass'

        for criterion in step.qc_criteria:
            param = criterion['parameter']
            value = measurements.get(param)

            if value is None:
                continue

            threshold = criterion['threshold']
            action = criterion['action']

            # Check if condition is met
            if self._check_qc_condition(value, criterion['condition'], threshold):
                logger.warning(
                    f"QC criterion failed for {param} in step {step.step_id}: "
                    f"{criterion['condition']} threshold {threshold}"
                )

                if action == 'fail':
                    return 'fail'
                elif action == 'warn' and status == 'pass':
                    status = 'warning'

        return status

    def _check_qc_condition(
        self,
        value: Any,
        condition: str,
        threshold: float
    ) -> bool:
        """Check if a QC condition is met.

        Args:
            value: Measured value
            condition: Condition type
            threshold: Threshold value

        Returns:
            True if condition triggers action, False otherwise
        """
        if condition == 'deviation_from_target':
            return abs(value - threshold) > threshold * 0.1  # 10% deviation
        elif condition == 'greater_than':
            return value > threshold
        elif condition == 'less_than':
            return value < threshold

        return False

    def calculate_results(self) -> Dict[str, Any]:
        """Perform calculations defined in protocol.

        Returns:
            Dictionary of calculation name -> result
        """
        calculations = {}

        for calc in self.definition.get('calculations', []):
            try:
                # Extract variable values from results
                variables = {}
                for var_name, var_path in calc['variables'].items():
                    variables[var_name] = self._get_result_value(var_path)

                # Execute formula (safe evaluation)
                result = self._evaluate_formula(calc['formula'], variables)
                calculations[calc['name']] = result

                logger.info(
                    f"Calculated {calc['name']}: {result} {calc['output_unit']}"
                )

            except Exception as e:
                logger.error(f"Error calculating {calc['name']}: {e}")
                calculations[calc['name']] = None

        return calculations

    def _get_result_value(self, path: str) -> Any:
        """Extract value from results using dotted path.

        Args:
            path: Path in format "STEP_ID.measurement_name" or "calculated.calc_name"

        Returns:
            Measurement or calculated value
        """
        # Handle calculated values
        if path.startswith('calculated.'):
            calc_name = path.split('.', 1)[1]
            calculations = self.calculate_results()
            return calculations.get(calc_name)

        # Handle measurement values
        step_id, measurement = path.split('.', 1)

        for result in self.results:
            if result.step_id == step_id:
                return result.measurements.get(measurement)

        return None

    def _evaluate_formula(
        self,
        formula: str,
        variables: Dict[str, Any]
    ) -> float:
        """Safely evaluate a mathematical formula.

        Args:
            formula: Mathematical formula string
            variables: Variable values

        Returns:
            Calculated result
        """
        # Create safe namespace with only math operations
        import math

        safe_dict = {
            'abs': abs,
            'max': max,
            'min': min,
            'round': round,
            'sum': sum,
            'sqrt': math.sqrt,
            'pow': pow,
            **variables
        }

        # Evaluate formula
        try:
            result = eval(formula, {"__builtins__": {}}, safe_dict)
            return float(result)
        except Exception as e:
            logger.error(f"Error evaluating formula '{formula}': {e}")
            raise

    def evaluate_pass_fail(self) -> Dict[str, Any]:
        """Evaluate overall pass/fail criteria.

        Returns:
            Dictionary with overall pass status and individual criteria results
        """
        calculations = self.calculate_results()
        criteria_results = []
        overall_pass = True

        for criterion in self.definition.get('pass_criteria', []):
            param = criterion['parameter']

            # Get value from calculations or final measurements
            value = calculations.get(param)
            if value is None and self.results:
                value = self.results[-1].measurements.get(param)

            operator = criterion['operator']
            threshold = criterion['value']

            # Evaluate criterion
            passed = self._evaluate_criterion(value, operator, threshold)

            criteria_results.append({
                'parameter': param,
                'value': value,
                'threshold': threshold,
                'operator': operator,
                'passed': passed,
                'severity': criterion['severity'],
                'description': criterion.get('description', '')
            })

            if not passed and criterion['severity'] == 'critical':
                overall_pass = False

            logger.info(
                f"Criterion {param} {operator} {threshold}: "
                f"{'PASS' if passed else 'FAIL'} (value={value})"
            )

        return {
            'overall_pass': overall_pass,
            'criteria': criteria_results
        }

    def _evaluate_criterion(
        self,
        value: Any,
        operator: str,
        threshold: Any
    ) -> bool:
        """Evaluate a single pass/fail criterion.

        Args:
            value: Measured or calculated value
            operator: Comparison operator
            threshold: Threshold value

        Returns:
            True if criterion passes, False otherwise
        """
        if value is None:
            return False

        operators = {
            '<': lambda v, t: v < t,
            '>': lambda v, t: v > t,
            '<=': lambda v, t: v <= t,
            '>=': lambda v, t: v >= t,
            '==': lambda v, t: v == t,
            '!=': lambda v, t: v != t
        }

        try:
            return operators[operator](value, threshold)
        except (KeyError, TypeError) as e:
            logger.error(f"Error evaluating criterion: {e}")
            return False

    @abstractmethod
    def generate_report(self) -> Dict[str, Any]:
        """Generate test report.

        Returns:
            Dictionary containing report data
        """
        pass

    def get_summary(self) -> Dict[str, Any]:
        """Get protocol execution summary.

        Returns:
            Summary dictionary
        """
        return {
            'protocol': {
                'id': self.protocol_id,
                'name': self.name,
                'version': self.version,
                'category': self.category
            },
            'execution': {
                'total_steps': len(self.steps),
                'completed_steps': len(self.results),
                'start_time': self.results[0].timestamp.isoformat() if self.results else None,
                'end_time': self.results[-1].timestamp.isoformat() if self.results else None
            },
            'status': {
                'pass': sum(1 for r in self.results if r.status == 'pass'),
                'warning': sum(1 for r in self.results if r.status == 'warning'),
                'fail': sum(1 for r in self.results if r.status == 'fail')
            }
        }
