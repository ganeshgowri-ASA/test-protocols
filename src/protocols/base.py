"""
Base protocol class for all test protocols
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import json


class BaseProtocol(ABC):
    """Base class for all test protocols"""

    def __init__(self, protocol_data: Dict[str, Any]):
        """
        Initialize base protocol

        Args:
            protocol_data: Protocol definition dictionary
        """
        self.protocol_data = protocol_data
        self.protocol_id = protocol_data['protocol_id']
        self.version = protocol_data['version']
        self.title = protocol_data['title']
        self.category = protocol_data['category']
        self.standard = protocol_data['standard']
        self.test_parameters = protocol_data['test_parameters']
        self.test_procedure = protocol_data['test_procedure']
        self.pass_fail_criteria = protocol_data['pass_fail_criteria']

    @abstractmethod
    def validate_test_data(self, test_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate test data against protocol requirements

        Args:
            test_data: Test execution data

        Returns:
            Tuple of (is_valid, list of validation errors)
        """
        pass

    @abstractmethod
    def analyze_results(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze test results and calculate metrics

        Args:
            test_data: Test execution data

        Returns:
            Dictionary containing analysis results
        """
        pass

    @abstractmethod
    def evaluate_pass_fail(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate pass/fail criteria based on analysis results

        Args:
            analysis_results: Results from analyze_results()

        Returns:
            Dictionary containing pass/fail evaluation
        """
        pass

    def get_procedure_steps(self, phase: str) -> List[Dict[str, Any]]:
        """
        Get test procedure steps for a specific phase

        Args:
            phase: 'pre_test', 'test_execution', or 'post_test'

        Returns:
            List of procedure steps
        """
        return self.test_procedure.get(phase, [])

    def get_required_equipment(self) -> List[Dict[str, Any]]:
        """
        Get list of required equipment

        Returns:
            List of equipment dictionaries
        """
        return self.protocol_data.get('equipment_required', [])

    def get_safety_considerations(self) -> List[str]:
        """
        Get safety considerations for this protocol

        Returns:
            List of safety items
        """
        return self.protocol_data.get('safety_considerations', [])

    def generate_test_template(self) -> Dict[str, Any]:
        """
        Generate a template for test data collection

        Returns:
            Dictionary template for test execution
        """
        return {
            'protocol_id': self.protocol_id,
            'protocol_version': self.version,
            'test_date': datetime.now().isoformat(),
            'test_operator': '',
            'module_info': {
                'manufacturer': '',
                'model': '',
                'serial_number': '',
                'nameplate_power': 0,
                'dimensions': {}
            },
            'environmental_conditions': {},
            'pre_test_data': {},
            'test_execution_data': {},
            'post_test_data': {},
            'notes': ''
        }

    def export_protocol_summary(self, output_path: str) -> None:
        """
        Export protocol summary to JSON file

        Args:
            output_path: Path to output file
        """
        summary = {
            'protocol_id': self.protocol_id,
            'version': self.version,
            'title': self.title,
            'category': self.category,
            'standard': self.standard,
            'test_parameters': self.test_parameters,
            'pass_fail_criteria': self.pass_fail_criteria
        }

        with open(output_path, 'w') as f:
            json.dump(summary, f, indent=2)
