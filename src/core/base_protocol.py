"""
Base Protocol Module

This module defines the abstract base class for all test protocols in the framework.
All specific protocol implementations (e.g., YELLOW-001) must inherit from BaseProtocol.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional
import json
import logging
from pathlib import Path


class BaseProtocol(ABC):
    """
    Abstract base class for all test protocols.

    This class provides the common interface and functionality that all
    protocol implementations must support.

    Attributes:
        protocol_id (str): Unique identifier for the protocol (e.g., "YELLOW-001")
        protocol_data (Dict): Parsed JSON protocol definition
        test_session_id (Optional[str]): Current test session identifier
        measurements (List[Dict]): Collected measurement data
        qc_results (List[Dict]): Quality control check results
    """

    def __init__(self, protocol_id: str, protocol_path: str):
        """
        Initialize the base protocol.

        Args:
            protocol_id: Unique protocol identifier
            protocol_path: Path to the protocol JSON definition file
        """
        self.protocol_id = protocol_id
        self.protocol_path = Path(protocol_path)
        self.protocol_data = self._load_protocol(protocol_path)
        self.test_session_id: Optional[str] = None
        self.measurements: List[Dict[str, Any]] = []
        self.qc_results: List[Dict[str, Any]] = []
        self.logger = self._setup_logger()

    def _load_protocol(self, path: str) -> Dict[str, Any]:
        """
        Load and parse protocol JSON definition.

        Args:
            path: Path to the protocol JSON file

        Returns:
            Dict containing parsed protocol data

        Raises:
            FileNotFoundError: If protocol file doesn't exist
            json.JSONDecodeError: If protocol file is invalid JSON
        """
        protocol_file = Path(path)

        if not protocol_file.exists():
            raise FileNotFoundError(f"Protocol file not found: {path}")

        try:
            with open(protocol_file, 'r') as f:
                data = json.load(f)

            # Validate required fields
            required_fields = ['protocol_id', 'protocol_name', 'version', 'test_parameters']
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field in protocol: {field}")

            return data

        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON in protocol file: {e}", e.doc, e.pos)

    def _setup_logger(self) -> logging.Logger:
        """Set up protocol-specific logger."""
        logger = logging.getLogger(f"protocol.{self.protocol_id}")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    @abstractmethod
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """
        Validate input parameters for the test.

        Args:
            inputs: Dictionary of input parameters

        Returns:
            True if inputs are valid

        Raises:
            ValueError: If inputs are invalid
        """
        pass

    @abstractmethod
    def execute_test(self, samples: List[Any]) -> Dict[str, Any]:
        """
        Execute the test protocol.

        Args:
            samples: List of sample objects to test

        Returns:
            Dictionary containing test results
        """
        pass

    @abstractmethod
    def analyze_results(self) -> Dict[str, Any]:
        """
        Analyze test results and calculate derived metrics.

        Returns:
            Dictionary containing analysis results
        """
        pass

    def check_qc(self, qc_type: str, measurement_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform quality control check.

        Args:
            qc_type: Type of QC check to perform
            measurement_data: Current measurement data

        Returns:
            Dictionary with QC check results
        """
        qc_config = self._get_qc_config(qc_type)

        if not qc_config:
            self.logger.warning(f"QC type not found in protocol: {qc_type}")
            return {
                'qc_type': qc_type,
                'status': 'NOT_CONFIGURED',
                'timestamp': datetime.now().isoformat()
            }

        # QC implementation will be handled by specific protocols
        result = {
            'qc_type': qc_type,
            'qc_id': qc_config.get('qc_id'),
            'name': qc_config.get('name'),
            'status': 'PENDING',
            'timestamp': datetime.now().isoformat()
        }

        self.qc_results.append(result)
        return result

    def _get_qc_config(self, qc_type: str) -> Optional[Dict[str, Any]]:
        """Get QC configuration from protocol data."""
        qc_controls = self.protocol_data.get('quality_controls', [])
        for qc in qc_controls:
            if qc.get('type') == qc_type or qc.get('qc_id') == qc_type:
                return qc
        return None

    def evaluate_pass_fail(self, measurement_value: float, parameter: str) -> Dict[str, Any]:
        """
        Evaluate measurement against pass/fail criteria.

        Args:
            measurement_value: Measured value
            parameter: Parameter name (e.g., 'yellow_index')

        Returns:
            Dictionary with evaluation results
        """
        criteria_list = self.protocol_data.get('pass_fail_criteria', [])

        results = {
            'parameter': parameter,
            'value': measurement_value,
            'status': 'PASS',
            'failed_criteria': [],
            'warnings': []
        }

        for criteria in criteria_list:
            if criteria.get('parameter') != parameter:
                continue

            operator = criteria.get('operator')
            threshold = criteria.get('value')
            severity = criteria.get('severity', 'FAIL')

            # Evaluate based on operator
            passes = self._evaluate_criteria(measurement_value, operator, threshold)

            if not passes:
                if severity == 'FAIL':
                    results['status'] = 'FAIL'
                    results['failed_criteria'].append(criteria)
                elif severity == 'WARNING':
                    if results['status'] != 'FAIL':
                        results['status'] = 'WARNING'
                    results['warnings'].append(criteria)

        return results

    def _evaluate_criteria(self, value: float, operator: str, threshold: float) -> bool:
        """Evaluate a single criterion."""
        operators = {
            '<=': lambda v, t: v <= t,
            '<': lambda v, t: v < t,
            '>=': lambda v, t: v >= t,
            '>': lambda v, t: v > t,
            '==': lambda v, t: v == t,
            '!=': lambda v, t: v != t,
        }

        op_func = operators.get(operator)
        if not op_func:
            self.logger.error(f"Unknown operator: {operator}")
            return True  # Default to pass if operator unknown

        return op_func(value, threshold)

    def generate_report(self, output_format: str = 'JSON') -> str:
        """
        Generate test report.

        Args:
            output_format: Desired output format (JSON, PDF, XLSX, HTML)

        Returns:
            Report content or path to generated report file
        """
        report_data = {
            'protocol_id': self.protocol_id,
            'protocol_name': self.protocol_data.get('protocol_name'),
            'version': self.protocol_data.get('version'),
            'test_session_id': self.test_session_id,
            'generated_at': datetime.now().isoformat(),
            'measurements': self.measurements,
            'qc_results': self.qc_results,
            'analysis': self.analyze_results() if self.measurements else {}
        }

        if output_format.upper() == 'JSON':
            return json.dumps(report_data, indent=2)
        else:
            # Other formats would be implemented in subclasses
            self.logger.warning(f"Format {output_format} not implemented, returning JSON")
            return json.dumps(report_data, indent=2)

    def get_protocol_info(self) -> Dict[str, Any]:
        """
        Get protocol metadata and information.

        Returns:
            Dictionary with protocol information
        """
        return {
            'protocol_id': self.protocol_id,
            'protocol_name': self.protocol_data.get('protocol_name'),
            'version': self.protocol_data.get('version'),
            'description': self.protocol_data.get('description'),
            'category': self.protocol_data.get('category'),
            'test_duration_hours': self.protocol_data.get('test_parameters', {}).get('duration_hours'),
            'measurement_parameters': [m.get('name') for m in self.protocol_data.get('measurements', [])]
        }

    def _generate_session_id(self) -> str:
        """
        Generate unique test session ID.

        Returns:
            Unique session identifier
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{self.protocol_id}_{timestamp}"
