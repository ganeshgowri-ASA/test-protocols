"""
Base Protocol Abstract Class
Defines the interface that all testing protocols must implement
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import jsonschema
from datetime import datetime
from pydantic import BaseModel, Field


class ProtocolConfig(BaseModel):
    """Pydantic model for protocol configuration"""
    protocol_id: str
    name: str
    category: str
    version: str
    description: str
    test_conditions: Dict[str, Any]
    input_parameters: List[Dict[str, Any]]
    measurements: List[Dict[str, Any]]
    qc_checks: List[Dict[str, Any]]
    output_format: str


class ProtocolResult(BaseModel):
    """Pydantic model for protocol execution results"""
    protocol_id: str
    run_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    status: str  # "running", "completed", "failed"
    input_data: Dict[str, Any]
    measurements: Dict[str, Any] = {}
    analysis_results: Dict[str, Any] = {}
    qc_passed: bool = False
    qc_details: Dict[str, Any] = {}
    errors: List[str] = []


class BaseProtocol(ABC):
    """
    Abstract base class for all testing protocols.

    All protocol implementations must inherit from this class and implement
    the required abstract methods.
    """

    def __init__(self, config_path: Path):
        """
        Initialize the protocol with configuration from JSON file.

        Args:
            config_path: Path to the protocol JSON configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.result: Optional[ProtocolResult] = None

    def _load_config(self) -> ProtocolConfig:
        """Load and validate protocol configuration from JSON file."""
        try:
            with open(self.config_path, 'r') as f:
                config_data = json.load(f)
            return ProtocolConfig(**config_data)
        except Exception as e:
            raise ValueError(f"Failed to load protocol configuration: {e}")

    def validate_input(self, input_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate input parameters against the protocol schema.

        Args:
            input_data: Dictionary of input parameters

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        for param in self.config.input_parameters:
            param_name = param.get('name')
            is_required = param.get('required', False)

            if is_required and param_name not in input_data:
                errors.append(f"Required parameter '{param_name}' is missing")

            if param_name in input_data:
                expected_type = param.get('type')
                actual_value = input_data[param_name]

                # Type validation
                type_mapping = {
                    'string': str,
                    'float': (float, int),
                    'integer': int,
                    'boolean': bool
                }

                if expected_type in type_mapping:
                    if not isinstance(actual_value, type_mapping[expected_type]):
                        errors.append(
                            f"Parameter '{param_name}' should be of type {expected_type}, "
                            f"got {type(actual_value).__name__}"
                        )

        return len(errors) == 0, errors

    @abstractmethod
    def run(self, test_data: Dict[str, Any]) -> ProtocolResult:
        """
        Execute the protocol with provided test data.

        Args:
            test_data: Dictionary containing all input parameters and measurements

        Returns:
            ProtocolResult object containing execution results
        """
        pass

    @abstractmethod
    def analyze_results(self) -> Dict[str, Any]:
        """
        Analyze the test results and generate statistics.

        Returns:
            Dictionary containing analysis results
        """
        pass

    @abstractmethod
    def perform_qc_checks(self) -> tuple[bool, Dict[str, Any]]:
        """
        Perform quality control checks on the results.

        Returns:
            Tuple of (qc_passed, qc_details)
        """
        pass

    @abstractmethod
    def generate_report(self, output_path: Path) -> Path:
        """
        Generate the final test report.

        Args:
            output_path: Directory path where the report should be saved

        Returns:
            Path to the generated report file
        """
        pass

    def get_protocol_info(self) -> Dict[str, Any]:
        """Get protocol metadata and configuration."""
        return {
            'protocol_id': self.config.protocol_id,
            'name': self.config.name,
            'category': self.config.category,
            'version': self.config.version,
            'description': self.config.description,
            'test_conditions': self.config.test_conditions
        }

    def save_results(self, output_path: Path) -> None:
        """Save protocol results to JSON file."""
        if self.result is None:
            raise ValueError("No results to save. Run the protocol first.")

        output_file = output_path / f"{self.result.run_id}_results.json"
        with open(output_file, 'w') as f:
            json.dump(self.result.model_dump(mode='json'), f, indent=2, default=str)
